# Strategy Overview

## Strategy 1: Oscillator-Timed Credit Spreads (Sideways Market)

> Use an overbought/oversold oscillator to sell short-dated, defined-risk credit spreads on a stock index, collecting premium while the market chops sideways.
>
> **Status: hypothesis.** Details marked [RESEARCH] were not given in the transcript. Not financial advice.

### 1. Idea

Roughly 60% of the time over 58 years, stocks have gone sideways. Trend-following strategies whipsaw in those periods. A short-dated credit spread profits if the index stays in a range, and the oscillator tells you which side to sell. The speaker uses it to smooth the equity curve alongside trend-following models, not as a standalone system.

### 2. Rules

**Universe**

- A stock index (the example uses an index trading around 425, likely an index ETF) [RESEARCH: which instruments]
- Used only when the market is sideways, a regime filter the transcript implies but does not define [RESEARCH]

**Signal**

- Oscillator: stochastic RSI (any normalized 0–100 oscillator is said to work similarly)
- The yen futures example uses a 21-day lookback [RESEARCH: the period used for the index spreads]
- Overbought (near 100): sell a **call** credit spread
- Oversold (near 0): sell a **put** credit spread
- Possible trigger (from the yen futures example): price exceeds the prior day's extreme in the direction of the reversal [RESEARCH: whether this applies to the spreads]

**Option selection**

- Expiry: 6–8 days out
- Spread width: about 5 points in the example (sell the 425 put, buy the 420 put)
- Short strike at or near the current index price in the example [RESEARCH: delta and strike rules]

**Exits**

1. Close for pennies once the credit has mostly decayed, then re-enter if the oscillator signals again
2. Hold to expiry if the market stays sideways and keep the full credit
3. Max loss is predefined by the spread width minus the credit; the speaker mentions a loss if the index moves 4–5 points against the position [RESEARCH: any stop before max loss]

**Size**

- Not specified [RESEARCH]
- Time: a few minutes once or twice a week

### 3. What to Expect (from the transcript)

- Reliability above 50% with an average win about equal to the average loss (about 1:1), unlike trend following (under 40% reliability with large winners).
- Example payoff profile: max loss −2.22 points, max gain +2.78 points. The gain implies a credit of about 2.78 on a 5-wide spread.
- Strong trending markets produce a steady stream of losers, so it should not be traded alone.
- The speaker reports it has picked up profits when trend strategies struggle, but gives no hard statistics.

### 4. One Test Before Trading

1. **Regime check:** does the oscillator signal work better in sideways regimes than in trends? Define "sideways" objectively.

- Fail: no meaningful difference in win rate between regimes.
2. **Simulation:** backtest on real option chain prices with realistic fills, comparing oscillator-timed spreads to spreads sold on random days. Check short-strike delta choices, spread widths and oscillator lookbacks.

- Fail: net return after slippage ≤ 0, or no better than the random-day control.

### 5. Log for Each Trade

Oscillator reading at entry, side sold, credit received, width, DTE, exit reason, P/L, and whether the market was in a sideways or trending regime.

---

## Strategy 2: Mean-Reversion Pullback in Strong Uptrends (Bensdorp Example)

> Buy a deep intraday-style dip in a very strong, volatile uptrending stock, and sell when it reverts about 1 ATR or after 6 days.
>
> **Status: hypothesis.** Example strategy from Lawrence Bensdorp's *Automated Stock Trading Systems* (the transcript spells the name "Benzdoorp"), presented to show the basics of a mean-reversion system. The speaker does not trade it. Not financial advice.

### 1. Idea

Strong stocks that take a breather tend to resume the uptrend. Buy the pullback at a discount and exit when price snaps back toward its recent norm. It is low expectancy, so it needs a large universe to generate enough trades.

### 2. Rules

**Universe**

- All stocks on NYSE, Amex and Nasdaq
- 50-day average volume ≥ 500,000 shares
- 50-day average dollar volume ≥ $2.5M
- ATR% > 4% (fast movers revert quickly)

**Signal**

- Trend filter: close > 100-day SMA + 1 × ATR(10)
- Strength filter: 7-day ADX > 55
- Ranking: highest 7-day ADX first
- Entry: limit order 3% below the previous close

**Option selection**

- N/A (stock strategy)

**Exits (any one)**

1. Profit target: 1 × ATR(10) [RESEARCH: measured from the execution price, presumably above entry]
2. Stop loss: 3 × ATR(10) below the execution price (wide, to give the stock room to revert)
3. Time stop: after 6 days with no stop or target hit, exit at the next open at market

**Size**

- Not specified [RESEARCH: position sizing and max concurrent positions]

### 3. What to Expect (from the transcript)

- Described as low expectancy, with a very large universe needed for enough trades.
- Wide stop (3 ATR) against a 1 ATR target implies a high win rate is needed to be profitable. [RESEARCH: reported win rate and average win/loss]
- The speaker says it can help reduce drawdowns from trend-following systems in sideways markets, though he does not run it himself.
- Time exit signals the trade is "not working" and should be cut.

### 4. One Test Before Trading

1. **Filter check:** how many stocks pass the ADX > 55 and ATR% > 4% filters each day? Confirm enough signals exist.

- Fail: too few signals for the strategy to be diversified.
2. **Simulation:** backtest on survivorship-bias-free data with slippage and the unfilled-limit-order problem (entries 3% below the close may not fill). Compare against buying on non-pullback days.

- Fail: mean return after costs ≤ 0, or no edge versus the control.

### 5. Log for Each Trade

Ticker, ADX rank, ATR%, entry fill vs prior close, days held, exit reason (target / stop / time), and return in ATR units.
