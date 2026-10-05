---
name: implement-handler
description: |
  Scaffold or implement a new handler following the architecture rules of this template.
  Trigger phrases: "implement handler", "scaffold handler", "build handler", "write handler",
  "create handler", "new handler"
argument-hint: "Name of the handler to implement (e.g., regime_filter, signal_engine) and a brief description of its responsibility"
---

# Implement Handler

## Philosophy

Every handler in this codebase is pure Python — no LEAN SDK imports. The dependency-injection
pattern means handlers are fully unit-testable without a running `QCAlgorithm`. Following the
structural pattern is non-negotiable; deviation breaks the test suite and violates the LEAN
isolation guarantee.

**Hard boundaries:**
- No `from QuantConnect import ...` or `from AlgorithmImports import ...` inside any handler file
- All thresholds must come from `config.py` — never hardcode numbers
- Constructor signature is always `__init__(self, algorithm) -> None`
- Return types must be Python primitives or dataclasses — no LEAN types in return values

---

## Phase 1 — Load Context

Before writing code:

1. Read [architecture-rules.md](../../_shared/references/architecture-rules.md) — confirm
   constructor pattern and LEAN isolation rules.
2. Read [handler-responsibilities.md](../../_shared/references/handler-responsibilities.md) —
   confirm which handler owns which behavior so the new one does not overlap with existing
   ones.
3. Read [config-thresholds.md](../../_shared/references/config-thresholds.md) — identify
   which constants this handler will consume; add any missing ones to `config.py`.
4. Read `handlers/_example_handler.py` — the canonical structural template.
5. Read `type_stubs.py` — identify any LEAN type stubs needed (e.g. `Symbol`, `TradeBar`)
   and add new stubs there if missing.

---

## Phase 2 — Scaffold the Handler File

Create `handlers/<handler_name>.py` with this structure:

```python
"""<HandlerName> — <one-line responsibility>.

Source handler: handlers/<handler_name>.py
Config constants used: CONSTANT_A, CONSTANT_B
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from config import CONSTANT_A, CONSTANT_B

if TYPE_CHECKING:
    from type_stubs import QCAlgorithm  # type hints only — never imported at runtime


class HandlerName:
    def __init__(self, algorithm) -> None:
        self._algorithm = algorithm
        # initialise internal state here
```

**Checklist:**
- [ ] No LEAN SDK import at module level
- [ ] All thresholds imported from `config.py` by constant name
- [ ] `TYPE_CHECKING` guard used for any type hint imports from `type_stubs.py`
- [ ] Constructor stores `algorithm` as `self._algorithm`

---

## Phase 3 — Implement Business Logic

Implement handler methods following these rules:

- Use `self._algorithm.debug(...)` for logging — never `print()`.
- Cache expensive computations keyed by `(symbol, date)` — see `DataHandler` for the
  canonical cache pattern.
- Check `IsReady` on any indicator before reading `.current.value`.
- Access other handlers via references passed into `__init__`, not via `self._algorithm`.
- Key dicts on the canonical ticker string, not raw `Symbol` (see
  [architecture-rules.md](../../_shared/references/architecture-rules.md) → *Symbol Identity*).
- For batched decisions with async fill feedback, track *pending* count in the loop
  (see *Decisions vs. Settled State*).

---

## Phase 4 — Register in `main.py`

1. Import the handler class at the top of `main.py` (the only file that may hold LEAN
   and handler imports together).
2. Instantiate in `initialize()`:
   ```python
   self._handler = HandlerName(self)
   ```
3. Wire into the daily evaluation scheduled event at the appropriate time slot.

---

## Phase 5 — Update Reference Docs

Same commit that adds the handler must update:
- `docs/FILE_MAP.md` — row for the new file.
- `.github/skills/_shared/references/handler-responsibilities.md` — row for the new
  handler.
- `.github/skills/_shared/references/config-thresholds.md` — rows for any new constants.

---

## Handoff Menu

| Next Step | Trigger | Skill |
|---|---|---|
| Write tests for this handler | "write tests", "unit tests" | `lifecycle-workflows/write-unit-tests` |
| Run the backtest and interpret results | "analyze backtest" | `lifecycle-workflows/run-backtest-analysis` |
| Create a PR | "create PR", "ready to merge" | `lifecycle-workflows/create-pr` |
| Diagnose handler not running | "why isn't it trading" | `debugging` |

---

## Reference Files

- [Architecture rules](../../_shared/references/architecture-rules.md)
- [Handler responsibilities](../../_shared/references/handler-responsibilities.md)
- [Config thresholds](../../_shared/references/config-thresholds.md)
- `handlers/_example_handler.py`
- `type_stubs.py`
