# File Map — Modular Architecture Reference

> Maps every module to its responsibility, data flow, and contracts.

---

## Directory Structure

```
lean-algo-template/
├── main.py                         # Platform orchestrator (ONLY LEAN imports)
├── config.py                       # Single source of truth for all parameters
├── type_stubs.py                   # LEAN type stubs for local testing
├── pyproject.toml                  # Dependencies and tool configuration
├── Makefile                        # Common commands (test, lint, rag)
├── handlers/                       # Business logic (pure Python, no LEAN imports)
│   ├── _example_handler.py         # Handler pattern reference
│   ├── _example_event_handler.py   # Event-driven handler pattern
│   ├── universe_filter.py          # Static universe from CSV
│   ├── data_handler.py             # Indicator computation + caching
│   ├── technical_validator.py      # Technical filter validation
│   ├── setup_checker.py            # Two-phase entry validation
│   ├── instrument_selector.py      # Contract/instrument selection
│   ├── position_manager.py         # Position state machine + exit logic
│   └── option_analytics.py         # Greeks + IV tracking (optional)
├── tests/
│   ├── conftest.py                 # Module injection + shared fixtures
│   └── unit/
│       ├── test_example_handler.py
│       ├── test_universe_filter.py
│       ├── test_data_handler.py
│       └── test_position_manager.py
├── docs/
│   ├── STRATEGY_OVERVIEW.md        # Strategy thesis and system flow
│   ├── FILE_MAP.md                 # This file
│   ├── DEVELOPMENT_GUIDE.md        # Build sequence and testing conventions
│   ├── IMPLEMENTATION_PLAN.md      # Phase-by-phase implementation
│   ├── AI_RAG_STRUCTURE.md         # RAG pipeline architecture
│   ├── PLATFORM_ADAPTERS.md        # Non-QC platform adapter guidance
│   ├── CHECKLIST_TEMPLATE.md       # Operational checklist template
│   └── skills/                     # Behavioral invariant skill files
├── rag/                            # Documentation RAG pipeline
│   ├── inject_context.py           # CLI: query corpus → RAG_CONTEXT.md
│   ├── crawler/                    # Playwright-based docs crawler
│   ├── processing/                 # HTML → Markdown → chunks
│   ├── storage/                    # DocStore + BM25 index
│   └── pipelines/                  # Ingest orchestration
├── universe/
│   └── candidates.csv              # Static candidate symbol list
├── adapters/
│   └── _example_adapter.py         # Platform adapter protocol reference
└── .github/
    └── copilot-instructions.md     # AI assistant context
```

---

## Core Data Flow

### Phase 1: Universe Scan (SCAN_SCHEDULE_TIME)

```
universe_filter.get_universe()
    → list[str] (ticker symbols)
    ↓
data_handler.get_indicators(symbol)
    → dict {price, sma_long, ema_short, ema_mid, ema_long, atr, atr_mean}
    ↓
technical_validator.validate_daily_technicals(symbol, price, indicators)
    → dict {filter_name: bool}
    ↓
setup_checker.validate_setup(symbol, price)
    → dict {valid: bool, details: dict}
    ↓
instrument_selector.select_instrument(symbol)
    → OptionContract | None
    ↓
_pending_entry_signals[symbol] = signal_dict
```

### Phase 2: Entry Trigger (ENTRY_TRIGGER_TIME)

```
For each pending signal:
    setup_checker.check_entry_trigger(symbol, price)
        → bool
    ↓
    position_manager.can_add_position()
        → bool
    ↓
    MarketOrder(instrument, FIXED_CONTRACTS)
        → OrderTicket → _pending_orders[order_id]
```

### Phase 3: Exit Check (EXIT_CHECK_TIMES)

```
For each active position:
    position_manager.check_exit_conditions(instrument, price)
        → (should_exit: bool, reason: str)
    ↓
    If exit: _execute_exit(instrument, reason)
        → MarketOrder(instrument, -quantity)
```

---

## Module Responsibilities

<!-- TODO: Update as you implement handlers -->

| Module | Responsibility |
|---|---|
| `main.py` | Platform orchestration, LEAN lifecycle callbacks, scheduling |
| `config.py` | All strategy parameters as `Final[...]` typed constants |
| `type_stubs.py` | LEAN type mocks for local testing |
| `universe_filter.py` | Load candidates from CSV |
| `data_handler.py` | Compute + cache indicators by (symbol, date) |
| `technical_validator.py` | Validate entry conditions, return {filter: bool} dict |
| `setup_checker.py` | Two-phase validation (scan-time + entry-time) |
| `instrument_selector.py` | Select optimal contract by delta, OI, spread |
| `position_manager.py` | Track trades, evaluate exits in priority order |
| `option_analytics.py` | IV elevation check, Greeks tracking |
