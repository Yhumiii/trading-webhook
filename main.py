# main.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

CAPITAL_COM_API_URL = "https://api-capital.backend-capital.com"
API_KEY = "your_capital_com_api_key_here"
ACCOUNT_ID = "your_account_id_here"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    signal = data.get("signal")
    symbol = data.get("symbol")

    if not signal or not symbol:
        return jsonify({"error": "Missing signal or symbol"}), 400

    # Example: place a mock market order
    headers = {
        "X-CAP-API-KEY": API_KEY,
        "Content-Type": "application/json",
    }

    payload = {
        "marketId": symbol,
        "direction": "BUY" if signal == "buy" else "SELL",
        "orderType": "MARKET",
        "size": 1,
        "currencyCode": "USD",
        "forceOpen": True,
        "guaranteedStop": False,
        "stopDistance": "10",
        "limitDistance": "20"
    }

    response = requests.post(f"{CAPITAL_COM_API_URL}/api/v1/orders", json=payload, headers=headers)

    return jsonify({
        "status": "ok",
        "order_response": response.json()
    })

if __name__ == '__main__':
    app.run()
