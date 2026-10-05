---
name: debugging
description: |
  Diagnose why a handler-based QC algorithm is not trading, or identify silent failure modes.
  Trigger phrases: "why isn't my algo trading", "diagnose no orders", "algo not placing orders",
  "silent failure", "debug algo", "no trades", "why no entries", "not trading", "spec drift",
  "untracked fill"
argument-hint: "Paste the LEAN debug log output, or describe the symptom (no entries / wrong exits / stale indicators / re-entry loops)"
---

# Debugging

## Philosophy

Silent failures are the most dangerous bugs in algorithmic trading: the algo runs without
errors but produces no (or wrong) trades. This skill provides a phase-gated diagnostic
workflow. Work phases in order — a failure at an earlier phase makes later phases
irrelevant.

**Hard boundaries:**
- Do not modify handler logic as part of diagnosis — only read and log.
- Always confirm gates (market regime, warm-up, scheduling) before investigating per-symbol
  entry logic.
- Config constants are never wrong by themselves — verify the *value* against `config.py`
  before concluding a threshold is misconfigured. Mismatch between `config.py` and
  `docs/STRATEGY_OVERVIEW.md` is a spec-drift bug; see
  [architecture-rules.md](../_shared/references/architecture-rules.md) →
  *Source-of-Truth Hierarchy*.

---

## Phase 1 — Confirm the Scheduled Eval Fired

**Goal:** prove the daily evaluation callback ran at the expected wall-clock time.

Add at the top of the eval callback:

```python
self.debug(f"[EVAL] time={self.time}  tz={self.time_zone}")
```

If the log line is missing → schedule never fired. If the timestamp is wrong (e.g.
05:35 ET on a 09:35 ET schedule) → timezone bug. Load the `qc-timezone-scheduling`
skill.

---

## Phase 2 — Verify Indicator / Data Readiness

**Goal:** confirm indicators are warmed up and returning valid values.

```python
data = self._data_handler.get_indicators(symbol, today)
self.debug(f"[DATA] {symbol} {data}")
```

If any value is `None` or `0.0`:
- Check warm-up period (`set_warm_up`) covers the longest indicator.
- Check the symbol is actually in the universe today.
- Check the cache is keyed on the canonical string (see *Symbol Identity*), not raw
  `Symbol`.
- See [indicator_readiness_gates.md](../indicators/indicator_readiness_gates.md).

---

## Phase 3 — Walk the Per-Symbol Gates

**Goal:** identify which gate is filtering out every candidate.

For each candidate, log the boolean of every gate in order. The first gate to return
`False` for every name is the culprit.

```python
for s in candidates:
    self.debug(
        f"[GATES] {s} regime={self._regime.allowed()} "
        f"tech={self._tech.passes(s)} setup={self._setup.passes(s)}"
    )
```

Cross-reference each gate's threshold against
[config-thresholds.md](../_shared/references/config-thresholds.md). If a counter or
threshold value is off by one, the bug is usually in `config.py`, not the handler.

---

## Phase 4 — Capacity / Risk Suspension

**Goal:** rule out position-cap or drawdown gating.

```python
self.debug(
    f"[CAP] open={len(self._positions.active_trades)} "
    f"cap={config.MAX_POSITIONS_OPEN}"
)
```

Async-fill capacity bug: if `MarketOrder` queues 100+ entries on a single day under a
cap of N, the loop is reading the *settled* count and never the *pending* count. See
[architecture-rules.md](../_shared/references/architecture-rules.md) →
*Decisions vs. Settled State*.

---

## Phase 5 — Fill / Lifecycle Plumbing (catches silent state-loss bugs)

If `[ORDER ENTRY ...]` log lines fire but the portfolio still misbehaves (re-entry
spam, missing add-ons, runaway position count), the fill path is broken — orders are
being submitted but `PositionManager` is never written to. Run these log-count
assertions:

```bash
grep -c "\[ORDER ENTRY"   logs.txt   # orders submitted
grep -c "\[POSITION\] OPEN" logs.txt # filled and recorded — should ≈ above
grep -c "\[FILL UNTRACKED\]" logs.txt # > 0 is a red flag (QC liquidated behind your back)
```

| Pattern | Cause | Fix |
|---|---|---|
| `[ORDER ENTRY]` lines exist but zero `[POSITION] OPEN` | `on_order_event` status comparison wrong (e.g. `OrderStatus.FILLED` vs `OrderStatus.Filled`) | Compare via `.name.lower() == "filled"`. See `main.py:on_order_event` |
| broker orders >> strategy orders (10×+) | QC auto-liquidates symbols dropped from universe; bypasses exit logic | Override `on_securities_changed` to retain held positions in the universe |
| `[FILL UNTRACKED]` lines present | Same as above, or stale order_id from a prior session | If recurring + position is held: same retention fix |
| Identical ticker re-enters daily | `_trades` keyed on raw `Symbol` (refresh yields fresh instance) | See *Symbol Identity* |

Full catalogue: [silent_failure_modes.md](silent_failure_modes.md).

---

## Handoff Menu

| Next Step | Trigger | Skill |
|---|---|---|
| Schedule fired at wrong wall-clock | "timezone", "DST", "fires before open" | `quantconnect/timezone-and-scheduling` |
| Apply a code fix | "apply fix", "fix the issue" | `lifecycle-workflows/implement-handler` |
| Add a regression test for the bug | "write tests" | `lifecycle-workflows/write-unit-tests` |
| Open a PR with the fix | "create PR" | `lifecycle-workflows/create-pr` |

---

## Reference Files

- [Why didn't my algo trade?](why_didnt_my_algo_trade.md) — Phase 1/2 checklist detail
- [Silent failure modes catalogue](silent_failure_modes.md)
- [Architecture rules](../_shared/references/architecture-rules.md)
- [Config thresholds](../_shared/references/config-thresholds.md)
- [Handler responsibilities](../_shared/references/handler-responsibilities.md)
