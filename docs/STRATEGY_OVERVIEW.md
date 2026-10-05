# Strategy Overview

<!-- TODO: Replace all placeholder content with your strategy specifics -->

## What This Strategy Does

**Core Concept:** <!-- Describe the edge thesis in 1-2 sentences -->

**Position:** <!-- What instrument, direction, and structure (e.g., "Long weekly call options") -->

**Holding period:** <!-- Entry to exit window (e.g., "7-30 days") -->

**Why it works:** <!-- The 2-3 edge factors your strategy exploits -->

**What kills it:** <!-- Primary risk factor (e.g., "Adverse gap", "IV crush", "Mean reversion failure") -->

---

## System Flow

<!-- Describe the phased pipeline your strategy follows -->

### Phase 1: Universe Scan (SCAN_SCHEDULE_TIME)

1. Filter universe for candidates matching criteria
2. Validate technical conditions
3. Queue passing symbols for Phase 2

### Phase 2: Entry Trigger (ENTRY_TRIGGER_TIME)

1. Re-validate conditions with intraday data
2. Check position capacity
3. Select instrument and place order

### Phase 3: Position Management (EXIT_CHECK_TIMES)

1. Evaluate exit conditions in priority order
2. Execute exits as needed

---

## Entry Criteria — Gate by Gate

<!-- List each validation gate your strategy requires -->

### Gate 1: Universe Filter

- Candidates loaded from `universe/candidates.csv`

### Gate 2: Technical Validation

- <!-- e.g., Price above SMA(50) -->
- <!-- e.g., EMA stack aligned (short > mid > long) -->
- <!-- e.g., Not overextended (< 2 ATR above mean) -->

### Gate 3: Market Regime

- <!-- e.g., SPY EMA(21) > SMA(50) for uptrend confirmation -->

### Gate 4: Setup Validation

- <!-- e.g., Event within target window -->
- <!-- e.g., Historical pattern confirmation -->

### Gate 5: Instrument Selection

- <!-- e.g., Option contract with target delta, sufficient OI -->

---

## Exit Rules

### Mandatory Exits

- <!-- e.g., Event proximity — exit 1 day before catalyst -->
- Stop loss at `STOP_LOSS_PCT`

### Optional Exits

- Profit target at `PROFIT_TARGET_PCT`
- Time limit at `MAX_HOLDING_DAYS`

---

## Risk Management

| Rule | Detail |
|---|---|
| Max positions | `MAX_POSITIONS_OPEN` |
| Risk per trade | `POSITION_RISK_PCT` of portfolio |
| Contracts per trade | `FIXED_CONTRACTS` |
| Stop loss | `STOP_LOSS_PCT` |
| Market regime gate | Trade only in uptrend |
