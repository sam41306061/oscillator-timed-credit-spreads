# Config Thresholds

**Source:** `config.py`
**Load when:** implementing handlers, writing tests, or verifying strategy parameters.

All strategy thresholds are `Final` typed constants in `config.py`. Never hardcode these
values in handlers or tests — always import by name.

> ⚠️ **Template file.** The rows below mirror the placeholder values shipped in
> `config.py`. Update this table whenever you change a constant — and update
> `docs/STRATEGY_OVERVIEW.md` in the same commit. A drift between the spec, `config.py`,
> and this table is a silent failure mode (see `architecture-rules.md` → *Source-of-Truth
> Hierarchy*).

---

## Universe

| Parameter | Value | Constant | Handler(s) |
|---|---|---|---|
| Candidate CSV path | `universe/candidates.csv` | `UNIVERSE_CSV_PATH` | `universe_filter.py` |
| Min market cap | $10B | `MIN_MARKET_CAP` | `universe_filter.py` |
| Min avg daily volume | 1,000,000 | `MIN_AVG_VOLUME` | `universe_filter.py` |
| Max universe size | 500 | `MAX_UNIVERSE_SIZE` | `universe_filter.py` |

## Event timing (if event-driven)

| Parameter | Value | Constant | Handler(s) |
|---|---|---|---|
| Min days to event | 7 | `MIN_DAYS_TO_EVENT` | `setup_checker.py` |
| Max days to event | 30 | `MAX_DAYS_TO_EVENT` | `setup_checker.py` |

## Indicators

| Parameter | Value | Constant | Handler(s) |
|---|---|---|---|
| Long SMA | 50 | `SMA_LONG_PERIOD` | `data_handler.py`, `technical_validator.py` |
| Short EMA | 8 | `EMA_SHORT_PERIOD` | `data_handler.py` |
| Mid EMA | 21 | `EMA_MID_PERIOD` | `data_handler.py` |
| Long EMA | 34 | `EMA_LONG_PERIOD` | `data_handler.py` |
| ATR | 14 | `ATR_PERIOD` | `data_handler.py` |

## Entry criteria

| Parameter | Value | Constant | Handler(s) |
|---|---|---|---|
| Price > long SMA required | True | `PRICE_ABOVE_SMA_REQUIRED` | `technical_validator.py` |
| Max ATR extension | 2.0× | `MAX_ATR_EXTENSION` | `technical_validator.py` |
| Entry-zone EMAs | [8, 21, 34] | `ENTRY_ZONE_EMAS` | `setup_checker.py` |
| Entry-zone tolerance | 2.0% | `ENTRY_ZONE_TOLERANCE_PCT` | `setup_checker.py` |

## Market regime

| Parameter | Value | Constant | Handler(s) |
|---|---|---|---|
| Regime EMA | 21 | `MARKET_REGIME_EMA` | `data_handler.py` |
| Regime SMA | 50 | `MARKET_REGIME_SMA` | `data_handler.py` |
| Restrict in downtrend | True | `RESTRICT_TRADES_IN_DOWNTREND` | `setup_checker.py` |

## Options (delete section if equities-only)

| Parameter | Value | Constant | Handler(s) |
|---|---|---|---|
| Target delta | 0.30 | `TARGET_DELTA` | `instrument_selector.py` |
| Delta tolerance | 0.05 | `DELTA_TOLERANCE` | `instrument_selector.py` |
| Min OI multiplier | 100 | `MIN_OPEN_INTEREST_MULTIPLIER` | `instrument_selector.py` |

<!-- TODO: Add rows for position sizing, risk, exit, and pyramiding constants
     as your strategy adopts them. -->
