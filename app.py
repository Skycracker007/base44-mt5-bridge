import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for the latest signal
latest_signal = {"signal": "HOLD", "symbol": "XAUUSD", "lot": 0.1}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "Base44 MT5 Bridge Active"}), 200

# Base44 posts new signals here
@app.route('/webhook', methods=['POST'])
def webhook():
    global latest_signal
    data = request.json or {}
    latest_signal = {
        "signal": data.get("action", "HOLD"),
        "symbol": data.get("symbol", "XAUUSD"),
        "lot": data.get("volume", 0.1)
    }
    return jsonify({"status": "received", "signal": latest_signal}), 200

# MT5 EA calls this endpoint to get the trade order
@app.route('/signal', methods=['GET'])
def get_signal():
    return jsonify(latest_signal), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
  
