from flask import Flask, request, jsonify
import MetaTrader5 as mt5
from datetime import datetime, timedelta

app = Flask(__name__)

mt5.initialize()

@app.route("/price/<symbol>")
def price(symbol):

    tick = mt5.symbol_info_tick(symbol)

    return jsonify({
        "bid": tick.bid,
        "ask": tick.ask,
        "time": tick.time
    })


@app.route("/buy", methods=["POST"])
def buy():
    data = request.json
    symbol = data["symbol"]
    lot = data["lot"]

    price = mt5.symbol_info_tick(symbol).ask

    request_order = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY,
        "price": price,
        "deviation": 20,
        "magic": 100,
        "comment": "node_bot"
    }

    result = mt5.order_send(request_order)

    return jsonify({
        "retcode": result.retcode
    })


@app.route("/sell", methods=["POST"])
def sell():
    data = request.json
    symbol = data["symbol"]
    lot = data["lot"]

    price = mt5.symbol_info_tick(symbol).bid

    request_order = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL,
        "price": price,
        "deviation": 20,
        "magic": 100,
        "comment": "node_bot"
    }

    result = mt5.order_send(request_order)

    return jsonify({
        "retcode": result.retcode
    })


@app.route("/buy-limit", methods=["POST"])
def buy_limit():

    data = request.json

    symbol = data["symbol"]
    lot = float(data["lot"])
    price = float(data["price"])
    sl = float(data["sl"])
    tp = float(data["tp"])

    mt5.symbol_select(symbol, True)

    request_order = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY_LIMIT,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "node_bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN
    }

    result = mt5.order_send(request_order)

    if result is None:
        return jsonify({
            "error": "order_send failed",
            "last_error": mt5.last_error()
        }), 400

    return jsonify({
        "retcode": result.retcode,
        "order": result.order
    })

@app.route("/sell-limit", methods=["POST"])
def sell_limit():

    data = request.json

    symbol = data["symbol"]
    lot = float(data["lot"])
    price = float(data["price"])
    sl = float(data["sl"])
    tp = float(data["tp"])

    mt5.symbol_select(symbol, True)

    request_order = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": lot,
        "type": mt5.ORDER_TYPE_SELL_LIMIT,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "node_bot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_RETURN
    }

    result = mt5.order_send(request_order)

    if result is None:
        return jsonify({
            "error": "order_send failed",
            "last_error": mt5.last_error()
        }), 400

    return jsonify({
        "retcode": result.retcode,
        "order": result.order
    })

@app.route("/balance", methods=["GET"])
def balance():
    account = mt5.account_info()

    return jsonify({
        "balance": account.balance,
        "equity": account.equity
    })

@app.route("/positions")
def positions():

    pos = mt5.positions_get()

    result = []

    if pos is not None:
        for p in pos:
            result.append({
                "ticket": p.ticket,
                "price_open": p.price_open,
                "sl": p.sl,
                "tp": p.tp,
                "profit": p.profit,
                "symbol": p.symbol,
                "type": p.type
            })

    return jsonify(result)

@app.route("/orders")
def orders():

    try:
        orders = mt5.orders_get()

        result = []

        if orders is not None and len(orders) > 0:
            for o in orders:
                result.append({
                    "ticket": o.ticket,
                    "symbol": o.symbol,
                    "type": o.type,
                    "price_open": o.price_open,
                    "sl": o.sl,
                    "tp": o.tp,
                    "volume_initial": o.volume_initial,
                    "time_setup": o.time_setup,
                    "comment": o.comment
                })

        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "orders": []
        }), 500

@app.route("/modify-sl")
def modify_sl():

    try:
        ticket = int(request.args.get("ticket"))
        sl = float(request.args.get("sl"))

        positions = mt5.positions_get(ticket=ticket)
        
        if positions is None or len(positions) == 0:
            return jsonify({
                "error": "Position not found",
                "retcode": -1
            }), 404

        pos = positions[0]

        request_data = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": ticket,
            "sl": sl,
            "tp": pos.tp
        }

        result = mt5.order_send(request_data)

        if result is None:
            error = mt5.last_error()
            return jsonify({
                "error": error,
                "retcode": -1
            }), 500

        return jsonify({
            "retcode": result.retcode
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "retcode": -1
        }), 500

@app.route("/check-price-touched")
def check_price_touched():
    symbol = request.args.get("symbol")
    target_price = float(request.args.get("price"))
    hours = int(request.args.get("hours", 4))
    
    now = datetime.now()
    past = now - timedelta(hours=hours)
    
    rates = mt5.copy_rates_range(symbol, mt5.TIMEFRAME_M1, past, now)
    
    for r in rates:
        if r["low"] <= target_price <= r["high"]:
            return jsonify({
                "touched": True,
                "time": datetime.fromtimestamp(r["time"]).isoformat()
            })
    
    return jsonify({"touched": False})

app.run(port=5001)