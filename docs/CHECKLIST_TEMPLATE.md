# <!-- TODO: Strategy Name --> — Operational Checklist

> Replace this template with a step-by-step checklist for your strategy's setup and
> trade management workflow. This serves as a quick-reference for the rules encoded
> in your handlers.

---

## 1) Identify Candidates

<!-- TODO: Describe how candidates enter the universe -->

- How are symbols selected? (CSV, screener, fundamental filter)
- What is the lookback or event window?
- What must be confirmed before a symbol is eligible?

---

## 2) Confirm Trend / Regime

<!-- TODO: Describe your trend or regime filters -->

- What indicators confirm the right market environment?
- Is there a broad market filter (e.g., SPY above its moving average)?
- Is there a per-symbol trend filter (e.g., price above SMA-50)?

---

## 3) Validate Entry Setup

<!-- TODO: Describe the conditions that must all be true for entry -->

- What are the mandatory (hard gate) conditions?
- What are the preferred (soft) conditions?
- Is there a two-phase validation (scan-time vs. entry-time)?

---

## 4) Select Instrument

<!-- TODO: Describe how you pick the specific contract or instrument -->

- Equity, option, future, or other?
- If options: target delta, expiry selection, OI/liquidity filters
- If equity: position sizing method

---

## 5) Execute Entry

<!-- TODO: Describe order type and sizing -->

- Market order or limit order?
- Fixed contracts/shares or risk-based sizing?
- Maximum concurrent positions?

---

## 6) Manage Position

<!-- TODO: Describe ongoing position management -->

- Stop loss rules (hard stop, trailing, time-based)
- Profit target rules
- Delta/position rolling criteria
- Any conditions that trigger early exit

---

## 7) Execute Exit

<!-- TODO: Describe exit triggers and priority -->

- What is the mandatory exit condition? (event-based, time-based, etc.)
- What is the exit priority order?
- How do you determine the latest acceptable exit time?
