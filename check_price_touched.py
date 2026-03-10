import MetaTrader5 as mt5
from datetime import datetime, timedelta

symbol = "XAUUSDm"
target_price = 5162

mt5.initialize()

now = datetime.now()
past = now - timedelta(hours=8)

rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, past, now)

found = False

for r in rates:
    if r["low"] <= target_price <= r["high"]:
        found = True
        print("Price touched in candle:", datetime.fromtimestamp(r["time"]))
        break

if not found:
    print("Price never touched", target_price)
