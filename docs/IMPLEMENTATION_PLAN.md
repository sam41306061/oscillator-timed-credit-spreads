# <!-- TODO: Strategy Name --> — Implementation Plan

> Read alongside `FILE_MAP.md` (architecture), `DEVELOPMENT_GUIDE.md` (build sequence),
> and `STRATEGY_OVERVIEW.md` (trading logic).

---

## Current State Assessment

<!-- TODO: Fill in status for your strategy's modules -->

| File | Status |
|---|---|
| `config.py` | 🔲 Template — needs strategy parameters |
| `type_stubs.py` | ✅ Complete |
| `main.py` | 🔲 Skeleton — wiring and callbacks need strategy logic |
| `handlers/universe_filter.py` | 🔲 Template — ready to populate |
| `handlers/data_handler.py` | 🔲 Template — ready to populate |
| `handlers/technical_validator.py` | 🔲 Template — ready to populate |
| `handlers/setup_checker.py` | 🔲 Template — ready to populate |
| `handlers/instrument_selector.py` | 🔲 Template — ready to populate |
| `handlers/position_manager.py` | 🔲 Template — TradeRecord done, methods need logic |
| `handlers/option_analytics.py` | 🔲 Template — ready to populate |
| `tests/conftest.py` | ✅ Complete |
| All `tests/unit/test_*.py` | 🔲 Template — test patterns shown, need strategy cases |

---

## Architecture Rules (Non-Negotiable)

1. **Only `main.py` imports `AlgorithmImports` / LEAN SDK.** All handlers are pure Python.
2. **`type_stubs.py` + `conftest.py` injection** enables full unit testing without LEAN.
3. **Never build the next layer until the current layer's tests pass.**

---

## Summary Build Order

<!-- TODO: Update steps to match your strategy's handler dependencies -->

| Step | File | Depends On |
|---|---|---|
| 0 | `type_stubs.py` + `conftest.py` | — |
| 1 | `config.py` | — |
| 2 | `universe_filter.py` | `config.py` |
| 3 | `data_handler.py` | `config.py`, stubs |
| 4 | `technical_validator.py` | `data_handler` output dict |
| 5 | `setup_checker.py` | 3, 4 |
| 6 | `instrument_selector.py` | stubs |
| 7 | `position_manager.py` | `config.py`, stubs |
| 8 | `test_order_lifecycle.py` | all handlers complete |
| 9 | `main.py` | all handlers + unit tests green |
| 10 | Cloud integration | `main.py` complete |
| 11 | Production backtest | Integration clean |

---

## Phase 0 — Foundation Hardening

**Files:** `type_stubs.py`, `tests/conftest.py`

These are already provided by the template. Verify they work:

```bash
python -c "import type_stubs; print(type_stubs.__all__)"
poetry run pytest tests/ --co  # collect tests, don't run
```

If your strategy needs additional LEAN types, add stubs to `type_stubs.py`.

---

## Phase 1 — Core Handlers

Build each handler following the patterns in `handlers/_example_handler.py`:

1. Implement the handler class with `__init__(self, algorithm)` constructor
2. Write unit tests using fixtures from `conftest.py`
3. Verify: `poetry run pytest tests/unit/test_<handler>.py -v`
4. Move to the next handler only when tests pass

### Handler Implementation Template

For each handler, define:

| Method | Logic |
|---|---|
| `__init__(self, algorithm)` | Store `self._algo`, initialize caches/state |
| Core methods | <!-- TODO: define per handler --> |
| `clear_cache()` / `reset()` | State cleanup for new scan cycles |

### Test Template

For each handler test file:

| Test | Technique | Assertion |
|---|---|---|
| Happy path | ECP | Expected output for valid input |
| Edge case | BVA | Boundary values produce correct results |
| Error case | Error Guessing | None/empty inputs handled gracefully |
| State reset | State Transition | Cache/state clears correctly |

---

## Phase 2 — Integration Test

**File:** `tests/unit/test_order_lifecycle.py`

Stitch all handlers together through a mock algorithm to validate the full
order cycle without LEAN.

### Scenarios to cover

- Full scan → signal → entry → exit (happy path)
- Full scan → no signal (each gate fails independently)
- Double entry prevention (same underlying, second trade rejected)

```bash
poetry run pytest tests/unit/ -v --cov=handlers --cov-report=html
```

Target: **≥ 80% coverage**, critical paths **100%**

---

## Phase 3 — `main.py` Wiring

**Only after all handlers pass unit tests.**

| Section | Logic |
|---|---|
| `initialize()` | Set dates, cash, benchmark; instantiate handlers; schedule events |
| `on_data(slice)` | Update prices; check exits |
| `on_order_event(event)` | On FILLED → update position_manager |
| Scheduled scans | Run handler pipeline phases |

---

## Phase 4 — Cloud Integration

```bash
lean cloud push --project-id <PROJECT_ID>
lean cloud backtest --project-id <PROJECT_ID>
```

### Acceptance criteria

- Universe loads without errors
- No `KeyError` / `AttributeError` runtime exceptions
- At least one full trade cycle (entry + exit) completes
- Strategy-specific invariants hold

---

## Phase 5 — Production Backtest

```bash
lean cloud backtest --project-id <PROJECT_ID> \
  --from-date YYYY-MM-DD --to-date YYYY-MM-DD
```

### Acceptance criteria

<!-- TODO: Define your strategy's target metrics -->

| Metric | Target |
|---|---|
| Sharpe ratio | > ? |
| Max drawdown | < ?% |
| Win rate | > ?% |
| Strategy invariants | ✅ |

---

## Developer Commands

```bash
# Install dependencies
poetry install

# Run all unit tests with coverage
poetry run pytest tests/unit/ -v --cov=handlers --cov-report=html

# Run a single handler's tests
poetry run pytest tests/unit/test_data_handler.py -v

# Type check
poetry run mypy handlers/

# Format
poetry run black .

# Push to LEAN Cloud
lean cloud push --project-id <PROJECT_ID>
```
