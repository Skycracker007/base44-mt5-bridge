import time
from flask import Flask, request, jsonify
import MetaTrader5 as mt5

app = Flask(__name__)

# 1. Login to MT5 Account
def initialize_mt5(account, password, server):
    if not mt5.initialize():
        return False
    authorized = mt5.login(int(account), password=password, server=server)
    return authorized

@app.route('/connect', methods=['POST'])
def connect_account():
    data = request.json
    success = initialize_mt5(data['account'], data['password'], data['server'])
    if success:
        return jsonify({"status": "connected", "account": data['account']}), 200
    return jsonify({"status": "failed", "error": "Invalid MT5 credentials"}), 400

@app.route('/trade', methods=['POST'])
def execute_trade():
    data = request.json
    action = data.get('action') # "BUY" or "SELL"
    symbol = data.get('symbol', 'EURUSD')
    volume = float(data.get('volume', 0.1))
    
    symbol_info = mt5.symbol_info(symbol)
    if not symbol_info:
        return jsonify({"error": "Symbol not found"}), 400
        
    price = mt5.symbol_info_tick(symbol).ask if action == "BUY" else mt5.symbol_info_tick(symbol).bid
    order_type = mt5.ORDER_TYPE_BUY if action == "BUY" else mt5.ORDER_TYPE_SELL
    
    request_data = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": order_type,
        "price": price,
        "deviation": 20,
        "magic": 123456,
        "comment": "Base44 AutoBot Trade",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    
    result = mt5.order_send(request_data)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        return jsonify({"status": "error", "code": result.retcode}), 400
        
    return jsonify({"status": "success", "ticket": result.order}), 200

if __name__ == '__main__':
    app.run(port=5000)
  
