# Skill: QuantConnect Timezone & Scheduling

Diagnose and prevent schedule misfires caused by timezone/DST mismatches between
the algorithm timezone, `time_rules.at()`, and US market wall-clock hours.

**Trigger phrases:** "schedule time", "timezone", "DST", "time_rules", "set_time_zone",
"why didn't my schedule fire", "fires before open", "fires after close",
"daylight saving", "wall-clock", "ET vs UTC".

---

## Core Rule

`self.time`, `time_rules.at(h, m)`, and every logged timestamp are interpreted in
the **algorithm timezone** set by `self.set_time_zone(...)`. Change the timezone
and the meaning of every existing `time_rules.at()` call shifts with it.

US equity market hours are 09:30–16:00 **Eastern Time** with DST. There are three
valid patterns and one anti-pattern.

---

## Pattern A — Algo in ET (preferred for US equities)

```python
def initialize(self):
    self.set_time_zone(TimeZones.NEW_YORK)
    self.schedule.on(
        self.date_rules.every_day("SPY"),
        self.time_rules.at(9, 35),   # 09:35 ET, DST-safe
        self._on_open,
    )
```

- `self.time` reads in ET — logs and date math match what a trader expects.
- QC handles EST↔EDT transitions automatically.

## Pattern B — Algo in UTC, schedule pinned to ET

```python
def initialize(self):
    self.set_time_zone(TimeZones.UTC)
    self.schedule.on(
        self.date_rules.every_day("SPY"),
        self.time_rules.at(9, 35, TimeZones.NEW_YORK),  # explicit tz arg
        self._on_open,
    )
```

- Use only if you need UTC for cross-asset alignment or external system sync.
- Logged `self.time` is UTC — add an ET conversion to log lines if reading them.

## Pattern C — Universal market-open helpers

```python
self.time_rules.after_market_open("SPY", minutes=5)
self.time_rules.before_market_close("SPY", minutes=5)
```

- Always anchored to the security's exchange hours. Timezone-independent.
- Preferred when "X minutes around the bell" is the actual intent.

---

## Anti-Pattern (DO NOT USE)

```python
self.set_time_zone(TimeZones.UTC)
self.time_rules.at(9, 35)   # fires at 09:35 UTC = 05:35 ET (pre-market!)
```

**Symptom:** algo "isn't trading", schedule fires but no market data has ticked,
indicators return None, regime stays `NO_TREND` forever. The log timestamp on the
eval line reads several hours off from the expected market time.

Hardcoded UTC offsets like `13:35` (winter) or `14:35` (summer) are equally bad —
they break twice a year at DST transitions.

---

## Diagnostic Checklist

When a scheduled callback "isn't working":

1. **Print `self.time` in the callback.** Does it match the expected wall-clock time?
2. **Check `set_time_zone`.** What timezone is the algo running in?
3. **Inspect every `time_rules.at(...)` call.** Is the hour/minute in the same
   timezone you think it is?
4. **Look for indicators returning `None`** — a callback firing pre-market gets
   empty `history()` results.
5. **Cross-reference market hours** — US equities trade 09:30–16:00 ET; futures,
   FX, crypto have different schedules.

---

## Related Skills

- [debugging/SKILL.md](../../debugging/SKILL.md) — silent failure diagnosis
- [trading/regime-filter-rules/SKILL.md](../../trading/regime-filter-rules/SKILL.md) —
  regime updates depend on a correctly-timed daily eval

---

## References

- QC docs: <https://www.quantconnect.com/docs/v2/writing-algorithms/scheduled-events>
- QC docs: <https://www.quantconnect.com/docs/v2/writing-algorithms/initialization#06-Set-Time-Zone>
