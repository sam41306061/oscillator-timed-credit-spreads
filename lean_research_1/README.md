
## Summary of Sharpened Research Plan

## Core thesis kept faithful, made specific

Sell SPY 7-DTE call spreads when StochRSI(14,21) ≥ 95 and put spreads when ≤ 5, only when the tape is measurably sideways (ADX(14) < 25, one number, ablated 20/25/30).
Short strike at ~18 delta, 5-point width, entry skipped unless net credit ≥ 1/3 of width (penny credits are friction fodder).

Exits in priority order: buy back at ≤15% of credit → underlying crosses short strike (close immediately, never wait out max loss) → expiry. No rolls in v1.
Economic rationale

Weekly option buyers (retail lottery tickets + hedgers rolling protection) overpay for tails in quiet ranges; the oscillator proxies for "one probe side is crowded and exhausted." The predictable loser is the discretionary buyer chasing determinism in a chop tape — and on the breakdown side, the strategy's own loser is the breakout, which is exactly why the regime gate is load-bearing, not decorative.
Honest backtest protocol (pre-registered)

Instrument: SPY options, 2014 → present via QC US Equity Options data; QQQ only as OOS extension if SPY passes. Classic event-driven LEAN API fits best (single symbol, daily logic, OptionStrategies.SellingCallSpread/SellingPutSpread).
Primary kill gate is the random-day control, not absolute returns: sell the identical structure on random days within the same sideways regime; the oscillator timing must beat the control's 75th percentile (bootstrap). Plus a pre-registered decomposition table isolating edge from (a) regime gate alone, (b) oscillator alone, (c) both — because if the control sits inside the signal's CI, the truth is "sell spreads sideways, oscillator irrelevant," and the plan says so up front.
Conservative fills: mid-plus + ~$1.30/contract surcharge; risk-stop exits filled at the worse of close price vs gap fill.
Kill criteria: expectancy ≤ 0 net; no edge vs control; no regime split; <3 of 6 years positive; or sign flips at adjacent width/delta settings.
Weaknesses flagged before the backtest

The transcript's own stats (≈50-60% win rate at ≈1:1 payoff) imply a razor-thin gross edge — friction is the most likely first killer.
Lump loss profile: one breakout day erases ~10 wins; expect max-loss clusters around vol explosions (Feb-2018-type) right as the sideways gate relaxes.
Chain breadth/thin mids pre-2016, and the "60% of time sideways" claim is unverified folklore here — deliberately not load-bearing.
Fair framing: this is a smoothing overlay alongside trend models (as the transcript itself presents it), not a standalone alpha engine; capacity is bounded by SPY option liquidity (roughly low-8-figures) far above what the edge can support comfortably.