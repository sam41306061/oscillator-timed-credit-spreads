---
name: write-unit-tests
description: |
  Write pytest unit tests for a handler in tests/unit/.
  Trigger phrases: "write tests", "unit tests for", "test coverage", "write unit tests",
  "add tests", "test this handler"
argument-hint: "Name of the handler to test (e.g., data_handler, position_manager) and the behaviors to cover"
---

# Write Unit Tests

## Philosophy

Handlers are pure Python — tests never need a running LEAN instance. The `type_stubs.py`
module provides all necessary LEAN type doubles. Tests must achieve ≥ 80% coverage per
handler. Each test verifies a single behavioral invariant: one scenario, one assertion.

**Hard boundaries:**
- Never instantiate `QCAlgorithm` directly — use the `mock_algorithm` fixture from
  `tests/conftest.py`.
- Never call the real LEAN history API in tests — inject synthetic data dictionaries.
- Tests live in `tests/unit/test_<handler_name>.py` only.
- No magic numbers — all thresholds referenced by `config` constant name.

---

## Phase 1 — Load Context

1. Read `tests/conftest.py` — understand the `mock_algorithm` fixture and any shared
   helpers.
2. Read the handler source file in full — identify every public method and state
   transition.
3. Read [config-thresholds.md](../../_shared/references/config-thresholds.md) — note
   which constants affect branching behaviour. These become boundary-value test
   parameters.
4. Skim an existing test file (e.g. [test_position_manager.py](../../../../tests/unit/test_position_manager.py))
   for the project's preferred style.

---

## Phase 2 — Derive Test Cases

For each public method, walk this invariant matrix:

| Condition class | Happy path | Boundary (n vs n−1) | Sad path |
|---|---|---|---|
| Threshold compare | Value above threshold | Value exactly at threshold | Value below threshold |
| Counter / state machine | Counter reaches target | Counter at target − 1 | Counter resets mid-run |
| Cache | Hit returns cached | First call computes | Stale key invalidates |
| Input shape | Full data dict | Missing optional field | `None` / empty dict |

Always test:
- Exact boundary value (e.g. `counter == THRESHOLD` vs `counter == THRESHOLD - 1`).
- State after a reset.
- `None` / missing data inputs (cache miss, indicator not ready).

---

## Phase 3 — Write the Test File

Create `tests/unit/test_<handler_name>.py`:

```python
import pytest

from config import CONSTANT_A, CONSTANT_B
from handlers.<handler_name> import HandlerName


@pytest.fixture
def handler(mock_algorithm):
    return HandlerName(mock_algorithm)


def test_<behavior>_when_<condition>(handler):
    # Arrange — minimal data dict the handler needs
    data = {"close": 100.0, "EMA21": 98.0, "SMA50": 95.0}
    # Act
    result = handler.method(data)
    # Assert
    assert result == expected
```

**Checklist:**
- [ ] One assertion per test function (single responsibility).
- [ ] Test names follow `test_<behavior>_when_<condition>` pattern.
- [ ] All config constants referenced by name, not magic number.
- [ ] Both sides of every threshold tested.
- [ ] Sad-path / `None`-input cases covered.

---

## Phase 4 — Verify Coverage

```bash
poetry run pytest tests/unit/test_<handler_name>.py -v \
    --cov=handlers.<handler_name> \
    --cov-report=term-missing
```

- Coverage must be ≥ 80% for the handler under test.
- Review the "missing" column — add tests for uncovered branches.
- Full-suite sanity check: `poetry run pytest tests/unit/ -v`.

---

## Handoff Menu

| Next Step | Trigger | Skill |
|---|---|---|
| Run a backtest with the implemented handler | "analyze backtest" | `lifecycle-workflows/run-backtest-analysis` |
| Create a PR | "create PR", "ready to merge" | `lifecycle-workflows/create-pr` |
| Debug a failing test | "test failing", "assertion error" | `debugging` |

---

## Reference Files

- [Architecture rules](../../_shared/references/architecture-rules.md)
- [Config thresholds](../../_shared/references/config-thresholds.md)
- `tests/conftest.py`
- `type_stubs.py`
