# Architecture Rules & Coding Guidelines

**Source:** `.github/copilot-instructions.md`, `docs/DEVELOPMENT_GUIDE.md`
**Load when:** implementing or modifying any handler; reviewing PRs; setting up a new handler

---

## Core Architecture Constraints

1. **LEAN isolation** — `main.py` is the *only* file that imports the LEAN SDK
   (`AlgorithmImports`). All business logic lives in `handlers/` as pure Python, fully
   testable without LEAN.

2. **Dependency injection** — Every handler receives `algorithm` (the `QCAlgorithm` reference)
   in its `__init__(self, algorithm)` constructor. Never import LEAN types inside handlers.

3. **Single source of truth for config** — All strategy thresholds belong in `config.py` as
   `Final` typed constants. Never hardcode values in handlers or tests.

4. **Test doubles** — `type_stubs.py` provides stub implementations of all LEAN types used in
   tests. Add new stubs there when a handler needs a new LEAN type reference.

5. **Platform adapters** — To run handlers against a non-LEAN platform (Backtrader, VectorBT,
   paper-trading shells), wrap the platform API in an adapter that exposes the same
   `algorithm` interface handlers expect. See `adapters/_example_adapter.py` and
   `docs/PLATFORM_ADAPTERS.md`.

---

## Handler Constructor Pattern

```python
class MyHandler:
    def __init__(self, algorithm) -> None:
        self._algorithm = algorithm
        # import constants from config — never hardcode
```

---

## Coding Standards

| Rule | Detail |
|---|---|
| Line length | 100 characters (Black-enforced via `pyproject.toml`) |
| Formatter | `poetry run black .` |
| Linter | `poetry run pylint handlers/` |
| Test coverage | ≥ 80% per handler — `poetry run pytest tests/unit/ -v --cov` |
| No LEAN imports in handlers | Any `from QuantConnect` / `from AlgorithmImports` in a handler file is a bug |
| No hardcoded thresholds | All constants must reference `config.py` by name |

---

## Test File Pattern

```python
from handlers.my_handler import MyHandler
from config import CONSTANT_A


def test_something(mock_algorithm):
    handler = MyHandler(mock_algorithm)
    # assert behavior
```

`mock_algorithm` fixture lives in `tests/conftest.py`.

---

## Type Hint Pattern for LEAN Types

```python
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from type_stubs import QCAlgorithm  # type hints only — never imported at runtime
```

The `TYPE_CHECKING` guard ensures stubs never load in a running LEAN environment.

---

## Source-of-Truth Hierarchy

When the same fact appears in multiple places, this is the authoritative order:

1. **`docs/STRATEGY_OVERVIEW.md`** — the human-authored spec (intent + Gherkin contract).
2. **`config.py`** — machine-enforced constants. Must match the spec exactly.
3. **`.github/skills/_shared/references/config-thresholds.md`** — quick lookup table.
   Mirrors `config.py`; never invents new values.
4. **Per-skill `SKILL.md`** — pedagogy and worked examples. Numbers cited here must
   match the table above. **Never** invent thresholds for illustration.

**When editing any threshold, update all four in the same commit.** A bare-number drift
between spec and config is a silent failure mode the test suite cannot catch.

CI/PR sanity: `grep -r "<CONSTANT_NAME>" .github/ docs/ config.py` must yield a single
consistent value.

---

## Decisions vs. Settled State (async order lifecycle)

LEAN's order lifecycle is asynchronous: `MarketOrder()` returns immediately; the
position only appears in `PositionManager`'s state after `on_order_event` fires with
`Filled` status.

**Anti-pattern (silently broken):**

```python
for symbol in universe:
    if positions.can_add_position():        # reads settled count
        decisions.append(EntryDecision(...))  # appends pending — count not updated
```

On the first allowed day, `can_add_position()` is `True` for the entire loop, so the
engine queues hundreds of decisions for a cap of N.

**Required pattern:** track *pending* decisions locally within the loop and break when
`settled + pending >= cap`:

```python
pending = 0
settled = len(positions.active_trades)
for symbol in universe:
    if settled + pending >= config.MAX_POSITIONS_OPEN:
        break
    ...
    decisions.append(EntryDecision(...))
    pending += 1
```

Applies to every batch producing side effects with an async feedback path (entries,
scale-outs, hedges). When unsure, ask: *"if I called this function 100 times in a row
with no fills in between, would the guard still hold?"*

---

## Symbol Identity

QC `Symbol` objects are **not** stable across universe refreshes. Two `Symbol` instances
for the same ticker (e.g. `"AAPL"`) can be unequal under `==` / `hash`. Keying any dict
on raw `Symbol` leaks identity into business logic.

**Canonical key** for every handler-owned mapping (positions, indicator caches,
cooldowns, seen-set deduplication):

```python
def _symbol_key(symbol) -> str:
    val = getattr(symbol, "value", None)
    if val is not None:
        return str(val).upper()                # QC Symbol → "AAPL"
    return str(symbol).split()[0].upper()      # test stub or bare string
```

Rules:
- Store the original `Symbol` on the value side (e.g. `TradeRecord.symbol`) for
  downstream order placement.
- Iterate `.values()` when callers need the original `Symbol`; iterate `.items()`
  only when the canonical ticker string is what you want.
- Never compare `symbol_a == symbol_b` for equality of "same ticker." Compare keys.

Symptom of violation: identical ticker re-enters daily; `has_position()` returns
`False` for a symbol you just opened; the closed-trade ledger contains duplicate
rows for one name.
