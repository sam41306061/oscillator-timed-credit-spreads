# <!-- TODO: Strategy Name --> — Development Guide

> Step-by-step build sequence for the QuantConnect LEAN implementation.
> Covers project setup, module build order, testing approach, and LEAN integration.

---

## Prerequisites

### Environment

```bash
# Python 3.11+ required (see pyproject.toml)
python --version

# Install dependencies via Poetry
poetry install

# Verify LEAN CLI is available
lean --version
```

### Key dependencies (from `pyproject.toml`)

| Package | Purpose |
|---|---|
| `lean` | LEAN CLI for local backtesting |
| `quantconnect-stubs` | Type stubs for IDE support (no runtime dependency) |
| `pandas`, `numpy` | Data manipulation (handlers only — not in main.py) |
| `pytest`, `pytest-cov` | Unit testing and coverage |
| `black`, `isort` | Code formatting |
| `mypy` | Static type checking |

---

## Architecture Constraint — Platform Isolation

> **This is the most important design rule in the entire codebase.**

Only `main.py` may import anything from the LEAN SDK (`QuantConnect.*`).

All handler modules (`handlers/*.py`) must be **pure Python**. They receive the algorithm
object as a dependency-injected parameter, but they never import it.

```python
# CORRECT — in main.py only
from QuantConnect import *
from QuantConnect.Algorithm import QCAlgorithm

# CORRECT — in any handler
class MyHandler:
    def __init__(self, algorithm):   # algorithm is injected, not imported
        self._algo = algorithm

# WRONG — never do this in a handler
from QuantConnect import Resolution   # ← breaks local testing
```

**Why this matters:** Pure Python handlers can be unit-tested locally without a LEAN
runtime. Breaking this rule means your tests require a live LEAN container — slow,
brittle, and hard to debug.

---

## Build Sequence

Follow this order. Each step builds on the previous.
**Never build the next layer until the current layer's tests pass.**

### Step 0 — Foundation (`type_stubs.py` + `conftest.py`)

Verify the stubs and test fixtures are working:

```bash
python -c "import type_stubs; print(type_stubs.__all__)"
poetry run pytest tests/ --co  # collect tests without running
```

### Step 1 — `config.py`

Review every constant and adjust for your strategy's parameters and risk tolerance.

**Validate:**
- All required constants are present and typed correctly.
- No hardcoded values remain in any other module.

### Step 2 — Core Handlers

Build handlers in dependency order. Typical sequence:

<!-- TODO: Replace with your strategy's handler build order -->

| Step | File | Depends On |
|---|---|---|
| 2a | `universe_filter.py` | `config.py` |
| 2b | `data_handler.py` | `config.py`, stubs |
| 2c | `technical_validator.py` | `data_handler` output dict |
| 2d | `setup_checker.py` | 2b, 2c |
| 2e | `instrument_selector.py` | stubs |
| 2f | `position_manager.py` | `config.py`, stubs |

### Step 3 — Integration Test

Create `tests/unit/test_order_lifecycle.py` to stitch all handlers together
through a mock algorithm. Validate the full cycle without LEAN.

### Step 4 — `main.py` Wiring

**Only after all handlers pass unit tests.**

Wire handlers into LEAN lifecycle callbacks:

| Section | Logic |
|---|---|
| `initialize()` | Set dates, cash, benchmark; instantiate handlers; schedule events |
| `on_data(slice)` | Update prices; check exit conditions |
| `on_order_event(event)` | On FILLED → update position_manager |
| Scheduled scan | Phase 1: universe → indicators → validate → signal |
| Scheduled entry | Phase 2: re-validate → place orders |
| Scheduled exit | Check exits → place close orders |

---

## Testing Conventions

```bash
# Run all unit tests with coverage
poetry run pytest tests/unit/ -v --cov=handlers --cov-report=html

# Run a single handler's tests
poetry run pytest tests/unit/test_data_handler.py -v

# Type check
poetry run mypy handlers/

# Format
poetry run black .
```

**Coverage target:** ≥ 80% on all handlers; critical paths 100%.

### Testing Technique Reference

| Abbreviation | Technique | When to use |
|---|---|---|
| ECP | Equivalence Class Partitioning | Valid vs. invalid input classes |
| BVA | Boundary Value Analysis | Min/max/edge values for a condition |
| State Transition | State Transition Testing | Cache, position states, open → closed |
| Pairwise | Pairwise / Combinatorial | Multiple interacting boolean conditions |
| Error Guessing | Error Guessing | Missing data, None inputs, empty lists |

---

## Common Pitfalls

1. **Importing LEAN in a handler** — instant test failure, impossible to debug locally.
2. **Forgetting cache invalidation** — stale indicators across scan cycles.
3. **Hardcoding thresholds** — breaks when you tune parameters. Use `config.py`.
4. **Not mocking `algorithm.History()`** — tests that pass locally but fail with real data shapes.
5. **Skipping boundary tests** — off-by-one errors in date windows and numeric thresholds.

---

## LEAN Cloud Integration

Once all unit tests pass:

```bash
# Push to cloud
lean cloud push --project-id <PROJECT_ID>

# Run backtest
lean cloud backtest --project-id <PROJECT_ID>
```

### Acceptance Criteria

- Universe loads without errors
- No `KeyError` / `AttributeError` runtime exceptions
- At least one full trade cycle (entry + exit) completes
- Strategy-specific invariants hold (define these before backtesting)
