import MetaTrader5 as mt5
import time

symbol = "XAUUSDm"

mt5.initialize()

mt5.symbol_select(symbol, True)

while True:

    tick = mt5.symbol_info_tick(symbol)

    if tick:
        print(
            "TIME:", tick.time,
            "BID:", tick.bid,
            "ASK:", tick.ask
        )

    time.sleep(0.2)
