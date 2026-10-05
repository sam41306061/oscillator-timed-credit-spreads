---
name: run-backtest-analysis
description: |
  Interpret QuantConnect backtest results. Classify performance, flag overfitting signals,
  and route to the correct diagnostic skill.
  Trigger phrases: "analyze backtest", "interpret backtest results", "backtest output",
  "Sharpe ratio", "PSR", "drawdown metrics", "evaluate backtest", "interpret results"
argument-hint: "Paste the QC backtest statistics output or describe the metrics you want analyzed"
---

# Run Backtest Analysis

## Philosophy

Backtests are hypotheses, not proofs. A passing backtest is necessary but not sufficient.
Overfit strategies show high in-sample Sharpe but fail live. This skill guides structured
interpretation of QC output and flags overfitting signals before any config tuning.

**Hard boundaries:**
- Do not change `config.py` thresholds based on a single backtest run.
- Do not interpret Sharpe in isolation — always check PSR and drawdown together.
- Do not run more than 5 parameter variants without documenting the hypothesis first.

---

## Phase 1 — Collect Output

Paste or load the QC backtest statistics. Minimum required metrics:

- CAGR
- Sharpe Ratio
- Probabilistic Sharpe Ratio (PSR)
- Maximum Drawdown
- Win Rate
- Trade Count
- Net Profit
- Beta to benchmark (if available)

---

## Phase 1.5 — Sanity Checks (BEFORE scoring)

Stop and surface a blocker if **any** of these fire — the result is unreliable noise,
not edge:

| Check | Threshold | Why |
|---|---|---|
| **Order count vs. expected** | `total_orders > MAX_POSITIONS_OPEN × trading_days × 1.5` | Capacity guard is broken; entries spamming each day. See `architecture-rules.md` → *Decisions vs. Settled State* |
| **"Insufficient buying power" in logs** | any occurrence | Aggregate exposure cap violated, or async-order capacity bug |
| **Beta to benchmark** | `|beta| > 1.3` or close to leverage cap | Strategy is just leveraged drift, not stock selection |
| **Win rate + net profit sign mismatch** | win rate < 20% AND net profit > 0 | Almost certainly a beta-driven survivorship effect, not a tradable edge |
| **Duplicate tickers in trade log** | same `Symbol.value` appearing in adjacent rows daily | `PositionManager` keyed on raw `Symbol`. See *Symbol Identity* |
| **Order count spike on first regime-up day** | day-1 orders > `MAX_POSITIONS_OPEN` | Same capacity bug as row 1 |

If any check fires: do not proceed to Phase 2. Route to `debugging` and fix the root
cause before re-running.

---

## Phase 2 — Score Against Benchmarks

| Metric | Target | Concern | Action if Concern |
|---|---|---|---|
| Sharpe Ratio | > 1.0 | < 0.5 | Investigate entry / regime filter activation rate |
| PSR | > 95% | < 80% | Sample size too small; extend date range |
| Max Drawdown | < 20% | > 30% | Review exit priority order and stop loss level |
| CAGR | > 15% | < 8% | Review universe quality and position sizing |
| Win Rate | 45–65% | > 75% | Possible data snooping; check hold-period distribution |
| Trade Count | ≥ 50 | < 20 | Filters may be too restrictive; check threshold counters |

---

## Phase 3 — Overfitting Checks

- [ ] Date range spans at least one full market cycle (bull + correction + recovery).
- [ ] Fewer than 5 free parameters tuned to this dataset.
- [ ] Trade count ≥ 50 (statistical significance floor).
- [ ] Out-of-sample segment held out (e.g. most recent 2 years).
- [ ] Filter / regime activation rate is reasonable — not always on or always off.
- [ ] Walk-forward or Monte Carlo test does not show performance collapse.

---

## Phase 4 — Diagnose Underperformance

Route to the correct diagnostic skill based on symptom:

| Symptom | Likely Cause | Next Skill / Reference |
|---|---|---|
| Very few trades, low CAGR | Filter rarely activates | `debugging` → Phase 1 (gate check) |
| High drawdown, low win rate | Exit logic firing too late | strategy `trading/exit-rules` skill (if defined) |
| Good Sharpe but low CAGR | Position sizing too conservative | strategy `trading/sizing-rules` skill (if defined) |
| Stale indicators / cache misses | Cache key or warm-up bug | `.github/skills/indicators/indicator_readiness_gates.md` |
| Untracked fills / re-entry loops | Order-event plumbing | `debugging` → Phase 5 (fill plumbing) |

---

## Handoff Menu

| Next Step | Trigger | Skill |
|---|---|---|
| Investigate a specific handler | "why isn't it trading", "wrong exits" | `debugging` |
| Create a PR for the backtest branch | "create PR" | `lifecycle-workflows/create-pr` |
| Add a new handler before re-running | "implement handler" | `lifecycle-workflows/implement-handler` |

---

## Reference Files

- [Config thresholds](../../_shared/references/config-thresholds.md)
- [Architecture rules](../../_shared/references/architecture-rules.md)
- [Results interpretation reference](../../backtesting/results_interpretation.md)
- [Overfitting prevention reference](../../backtesting/overfitting_prevention.md)
- [Deployment constraints reference](../../backtesting/deployment_constraints.md)
