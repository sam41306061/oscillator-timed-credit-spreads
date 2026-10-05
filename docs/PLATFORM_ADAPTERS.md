# Platform Adapters — Running Handlers Outside QuantConnect

This document describes how to reuse the handler layer (`handlers/`) with platforms
other than QuantConnect LEAN that have similar quant/backtest capabilities.

---

## Architecture Review

The template enforces a strict separation:

```
┌─────────────────────────────────┐
│  Platform Layer (main.py)       │  ← Only file that imports LEAN SDK
│  - Lifecycle callbacks          │
│  - Data subscriptions           │
│  - Order routing                │
│  - Scheduling                   │
├─────────────────────────────────┤
│  Handler Layer (handlers/)      │  ← Pure Python, no platform imports
│  - Business logic               │
│  - Indicator computation        │
│  - Entry/exit validation        │
│  - Position state management    │
├─────────────────────────────────┤
│  Config Layer (config.py)       │  ← Shared constants, no imports
└─────────────────────────────────┘
```

Because handlers never import platform types, you can swap the platform layer
without touching any business logic.

---

## Adapter Pattern

To port to a new platform, create an adapter that translates the platform's API
into the `algorithm` interface that handlers expect:

```python
# adapters/my_platform_adapter.py

class MyPlatformAdapter:
    """Wraps <Platform>'s API to match the algorithm interface handlers expect."""

    def __init__(self, platform_context):
        self._ctx = platform_context

    @property
    def Time(self):
        """Return current simulation/live datetime."""
        return self._ctx.get_current_time()

    @property
    def Portfolio(self):
        """Return portfolio state (positions, cash, value)."""
        return self._ctx.get_portfolio()

    def History(self, symbol, periods, resolution):
        """Return historical bars as list of TradeBar-like objects."""
        raw = self._ctx.get_history(symbol, periods, resolution)
        return [TradeBar(r.open, r.high, r.low, r.close, r.volume, r.time)
                for r in raw]

    def Log(self, message: str):
        self._ctx.log(message)

    def Debug(self, message: str):
        self._ctx.debug(message)

    def Error(self, message: str):
        self._ctx.error(message)

    def MarketOrder(self, symbol, quantity):
        """Place a market order; return an order-ticket-like object."""
        return self._ctx.submit_market_order(symbol, quantity)
```

Then in your platform's entry point:

```python
adapter = MyPlatformAdapter(platform_context)

# All handlers work unchanged
data_handler = DataHandler(adapter)
validator = TechnicalValidator(adapter)
position_mgr = PositionManager(adapter)
```

---

## Algorithm Interface Contract

Handlers rely on the following attributes and methods of the `algorithm` object.
Any adapter must provide these:

### Properties

| Property | Type | Description |
|---|---|---|
| `Time` | `datetime` | Current simulation time |
| `Portfolio` | dict-like | Portfolio positions and values |
| `Securities` | dict-like | Subscribed securities data |

### Methods

| Method | Signature | Description |
|---|---|---|
| `Log(msg)` | `str → None` | Info-level logging |
| `Debug(msg)` | `str → None` | Debug-level logging |
| `Error(msg)` | `str → None` | Error-level logging |
| `History(symbol, periods, resolution)` | `→ list[TradeBar]` | Historical price bars |
| `MarketOrder(symbol, quantity)` | `→ OrderTicket` | Place market order |

### Optional (strategy-dependent)

| Method | When needed |
|---|---|
| `AddEquity(ticker, resolution)` | Universe management |
| `AddOption(underlying, resolution)` | Options strategies |
| `OptionChainProvider.GetOptionContractList(symbol, date)` | Options chain access |
| `ObjectStore` | Persistent state across restarts |

---

## Platform Compatibility Notes

### Zipline / QuantLib
- Map `History()` to `data.history()`
- Map `MarketOrder()` to `order()`
- Scheduling: use Zipline's `schedule_function()`

### Backtrader
- Map `History()` to data feed access via `self.datas[n]`
- Map `MarketOrder()` to `self.buy()` / `self.sell()`
- Scheduling: use `next()` with time checks

### Custom / In-House
- Implement the adapter protocol above
- Use `type_stubs.py` as a reference for the expected object shapes

---

## Testing Adapters

Adapter tests should verify the interface contract without needing the live platform:

```python
def test_adapter_has_required_interface():
    adapter = MyPlatformAdapter(mock_context)
    assert hasattr(adapter, 'Time')
    assert hasattr(adapter, 'Portfolio')
    assert callable(adapter.History)
    assert callable(adapter.MarketOrder)
    assert callable(adapter.Log)
```

The existing `conftest.py` fixtures (`mock_algorithm`) already implement this
interface — use them as the reference implementation.
