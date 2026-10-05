# Handler Responsibilities

**Source:** `docs/FILE_MAP.md`, `.github/copilot-instructions.md`
**Load when:** asked which handler owns a behavior; before implementing a new handler to
avoid overlap; before modifying routing logic in `main.py`.

> ⚠️ **Template file.** The rows below describe the *scaffolded* handlers shipped with
> this template. Update this table as you delete unused handlers and implement your
> strategy. Keep it in lock-step with `docs/FILE_MAP.md` and the handlers actually
> wired into `main.py`.

---

| Handler Class | File | Responsibility |
|---|---|---|
| `UniverseFilter` | `handlers/universe_filter.py` | Return the symbol list to trade. Default: static load from `universe/candidates.csv`. Replace with QC coarse/fine selectors when you need dynamic universes. |
| `DataHandler` | `handlers/data_handler.py` | Compute + cache indicators keyed by `(symbol, date)`. Reads exclusively from `algorithm.history(...)` or registered indicators. |
| `TechnicalValidator` | `handlers/technical_validator.py` | Pure technical-filter pass/fail (SMA, EMA, ATR alignment). No side effects. |
| `SetupChecker` | `handlers/setup_checker.py` | Two-phase validation: Phase 1 (scan-time) builds candidate set; Phase 2 (entry-time) confirms tradability just before order placement. |
| `InstrumentSelector` | `handlers/instrument_selector.py` | Pick the specific contract/instrument to trade (e.g. option contract from a chain). Drop this handler for equity-only strategies. |
| `PositionManager` | `handlers/position_manager.py` | Entry/exit state, multi-leg avg-cost tracking, realized + unrealized P&L per symbol. |
| `OptionAnalytics` | `handlers/option_analytics.py` | IV / delta / theta / Greeks tracking. Drop for non-options strategies. |

---

## Data Flow Sketch

```
main.py (scheduled @ DAILY_EVAL_TIME)
  → UniverseFilter.symbols()                          # today's universe
  → DataHandler.get_indicators(symbol, today)         # cache per (symbol, date)
  → TechnicalValidator.passes(indicators)             # technical gate
  → SetupChecker.phase_1_passes(symbol, indicators)   # candidacy
  → SetupChecker.phase_2_passes(symbol, ...)          # final entry gate
  → InstrumentSelector.pick(symbol, ...)              # contract selection (optional)
  → PositionManager.open(...) / .close(...)           # state + order plumbing
  → OptionAnalytics.update(...)                       # Greeks tracking (optional)
```

---

## Deleting Handlers

The template ships handlers that may not apply to your strategy. Delete them rather
than leaving them un-wired:

| Handler | Delete when… |
|---|---|
| `instrument_selector.py` | Equities-only strategy |
| `option_analytics.py` | Equities-only strategy |
| `setup_checker.py` | Single-phase validation is sufficient |
| `technical_validator.py` | Validation lives entirely inside `setup_checker.py` |

When you delete a handler, also delete its row above, its tests under `tests/unit/`,
and any references in `docs/FILE_MAP.md` and `main.py`.
