# StochRSI Sideways-Regime Credit Spreads on Sector SPDR ETFs
#
# G2-style sequence-verification backtest of the transcribed idea from the research
# program: after a StochRSI(14,14) extreme inside a sideways regime (ADX(14) < 25),
# sell a credit spread in the fear direction:
#   - oversold episode entry (stoch crosses below 0.20)  -> put credit spread
#   - overbought episode entry (stoch crosses above 0.80) -> call credit spread
# Note: the underlying-only risk test (G1) for this trigger FAILED (the oversold
# trigger raises the 5-day down-cross rate vs the in-regime baseline). This backtest
# verifies the full trading sequence on the option side; it is NOT evidence of edge.
#
# Entry: 1 contract, short strike ~2% OTM, long leg ~2% further OTM, nearest expiry
#        to 35 DTE (filter 30-45 DTE). Combo market orders (no sequential legging).
# Exit:  50% of entry credit profit take; otherwise hold to expiration.
#        Shares left by assignment/auto-exercise of expired legs are flattened
#        on the next bar (one cleanup mechanism: residual flatten in on_data).

from AlgorithmImports import *


class EtfState:
    """Per-ETF signal and position state."""

    def __init__(self, underlying: Symbol, option: Symbol, rsi: object, adx: object) -> None:
        self.underlying = underlying
        self.option = option
        self.rsi = rsi
        self.adx = adx
        self.rsi_win = RollingWindow[float](14)
        self.prev_stoch = None
        self.signal = ''
        self.short_leg = None
        self.long_leg = None
        self.entry_credit = 0.0


class StochRsiSectorCreditSpreads(QCAlgorithm):

    _TICKERS = ('XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY')
    _ADX_GATE = 25.0
    _OB_BAND = 0.80
    _OS_BAND = 0.20
    _TARGET_DTE = 35
    _OTM = 0.02
    _PROFIT_TAKE = 0.5

    def initialize(self) -> None:
        self.set_start_date(2023, 1, 1)
        self.set_cash(100_000)

        # diagnostics for the 0-trade verification run
        self._dbg = {'days': 0, 'ready': 0, 'crossings': 0, 'gate_blocked': 0,
                     'signals': 0, 'chain_none': 0, 'no_shorts': 0,
                     'no_farther': 0, 'credit_le0': 0}
        self._dbg_logged = 0

        self._states = []
        for ticker in self._TICKERS:
            equity = self.add_equity(ticker, Resolution.DAILY)
            option = self.add_option(ticker, Resolution.DAILY)
            option.set_filter(lambda u: u.include_weeklys().strikes(-15, 15).expiration(30, 45))
            rsi = self.rsi(equity.symbol, 14, MovingAverageType.WILDERS, Resolution.DAILY)
            adx = AverageDirectionalIndex(14)
            self.register_indicator(equity.symbol, adx, Resolution.DAILY)
            self._states.append(EtfState(equity.symbol, option.symbol, rsi, adx))

        self.set_warm_up(60, Resolution.DAILY)

    def on_data(self, data: Slice) -> None:
        if self.is_warming_up:
            return

        for state in self._states:
            if state.short_leg is None:
                # expired legs can leave underlying shares via auto-exercise or
                # assignment; flatten them before the next entry
                shares = self.portfolio[state.underlying].quantity
                if shares != 0:
                    self.market_order(state.underlying, -shares, tag='Assignment cleanup')
                    self.log('Assignment cleanup: %s, %d shares' % (state.underlying, -shares))
            if state.short_leg is not None:
                self._manage(state, data)
            bar = data.bars.get(state.underlying)
            if bar is None:
                continue
            signal = self._signal(state)
            if signal and state.short_leg is None:
                self._enter(state, signal, bar.close, data)

        self._dbg['days'] += 1
        if self._dbg['days'] % 63 == 0:
            self.log('DBG summary day %d: %s' % (self._dbg['days'], self._dbg))

    def _dbg_log(self, event: str, detail: str) -> None:
        """Log the first 25 occurrences of each diagnostic event, then just count."""
        self._dbg[event] += 1
        if self._dbg[event] <= 25:
            self._dbg_logged += 1
            self.log('DBG %s #%d: %s' % (event, self._dbg[event], detail))

    def _signal(self, state: EtfState) -> str:
        if not state.rsi.is_ready or not state.adx.is_ready or not state.rsi_win.is_ready:
            # keep the window in sync even before it is full
            if state.rsi.is_ready:
                state.rsi_win.add(state.rsi.current.value)
            state.prev_stoch = None
            return ''
        self._dbg['ready'] += 1
        state.rsi_win.add(state.rsi.current.value)
        values = list(state.rsi_win)
        hi, lo = max(values), min(values)
        if hi <= lo:
            state.prev_stoch = None
            return ''
        stoch = (state.rsi.current.value - lo) / (hi - lo)
        signal = ''
        gate_open = state.adx.current.value < self._ADX_GATE
        if state.prev_stoch is not None:
            if stoch < self._OS_BAND <= state.prev_stoch:
                self._dbg_log('crossings', '%s os cross stoch %.2f prev %.2f adx %.1f gate %s'
                              % (state.underlying, stoch, state.prev_stoch,
                                 state.adx.current.value, gate_open))
                if gate_open:
                    signal = 'os'
                else:
                    self._dbg_log('gate_blocked', '%s adx %.1f' % (state.underlying, state.adx.current.value))
            elif stoch > self._OB_BAND >= state.prev_stoch:
                self._dbg_log('crossings', '%s ob cross stoch %.2f prev %.2f adx %.1f gate %s'
                              % (state.underlying, stoch, state.prev_stoch,
                                 state.adx.current.value, gate_open))
                if gate_open:
                    signal = 'ob'
                else:
                    self._dbg_log('gate_blocked', '%s adx %.1f' % (state.underlying, state.adx.current.value))
        state.prev_stoch = stoch
        return signal

    def _pick_expiry(self, chain: OptionChain) -> datetime:
        today = self.time.date()
        return min((c.expiry.date() for c in chain),
                   key=lambda d: abs((d - today).days - self._TARGET_DTE))

    def _enter(self, state: EtfState, signal: str, spot: float, data: Slice) -> None:
        self._dbg['signals'] += 1
        chain = data.option_chains.get(state.option)
        if chain is None:
            self._dbg_log('chain_none', '%s %s spot %.2f' % (state.underlying, signal, spot))
            return
        self._dbg_log('signals', '%s %s spot %.2f chain %d contracts' % (state.underlying, signal, spot, len(list(chain))))
        expiry = self._pick_expiry(chain)
        contracts = [c for c in chain if c.expiry.date() == expiry]
        if signal == 'os':
            short_side = OptionRight.PUT
            shorts = sorted((c for c in contracts if c.right == short_side
                             and c.strike <= spot * (1.0 - self._OTM)),
                            key=lambda c: c.strike)
        else:
            short_side = OptionRight.CALL
            shorts = sorted((c for c in contracts if c.right == short_side
                             and c.strike >= spot * (1.0 + self._OTM)),
                            key=lambda c: c.strike)
        if not shorts:
            self._dbg_log('no_shorts', '%s %s expiry %s spot %.2f, %d contracts that day'
                          % (state.underlying, signal, expiry, spot, len(contracts)))
            return
        short_c = shorts[-1] if signal == 'os' else shorts[0]
        farther = [c for c in contracts
                   if c.right == short_side
                   and ((c.strike < short_c.strike) if signal == 'os' else (c.strike > short_c.strike))]
        if not farther:
            self._dbg_log('no_farther', '%s short strike %.2f' % (state.underlying, short_c.strike))
            return
        long_c = (max(farther, key=lambda c: c.strike) if signal == 'os'
                  else min(farther, key=lambda c: c.strike))
        credit = short_c.bid_price - long_c.ask_price
        if credit <= 0:
            self._dbg_log('credit_le0', '%s short %.2f bid %.2f, long %.2f ask %.2f'
                          % (state.underlying, short_c.strike, short_c.bid_price,
                             long_c.strike, long_c.ask_price))
            return

        legs = [Leg.create(short_c.symbol, -1), Leg.create(long_c.symbol, 1)]
        self.combo_market_order(legs, 1, tag='%s %s credit spread' % (state.underlying, signal))
        state.signal = signal
        state.short_leg = short_c.symbol
        state.long_leg = long_c.symbol
        state.entry_credit = credit
        self.log('%s %s signal: spot %.2f, short %s, long %s, est credit %.2f'
                 % (state.underlying, signal, spot, short_c.symbol.id, long_c.symbol.id, credit))

    def _manage(self, state: EtfState, data: Slice) -> None:
        short_q = self.portfolio[state.short_leg].quantity
        long_q = self.portfolio[state.long_leg].quantity
        if short_q == 0 and long_q == 0:
            # fully closed (expiry or fills) - clear state so the ETF can re-enter
            self.log('%s position closed, state cleared' % state.underlying)
            state.short_leg = None
            state.long_leg = None
            state.entry_credit = 0.0
            state.signal = ''
            return
        if short_q == 0 or long_q == 0:
            return  # partial (assignment edge) - handled in on_assignment_order_event
        chain = data.option_chains.get(state.option)
        if chain is None:
            return
        quotes = {c.symbol: c for c in chain}
        if state.short_leg not in quotes or state.long_leg not in quotes:
            return
        cost = quotes[state.short_leg].ask_price - quotes[state.long_leg].bid_price
        if cost <= self._PROFIT_TAKE * state.entry_credit:
            legs = [Leg.create(state.short_leg, 1), Leg.create(state.long_leg, -1)]
            self.combo_market_order(legs, 1, tag='%s profit take' % state.underlying)
            self.log('%s profit take: entry credit %.2f, close cost %.2f'
                     % (state.underlying, state.entry_credit, cost))
