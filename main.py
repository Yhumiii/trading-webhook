from flask import Flask, request, jsonify
import requests
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Environment variables from Render dashboard
CAPITAL_API_KEY = os.getenv("CAPITAL_API_KEY")
CAPITAL_USERNAME = os.getenv("CAPITAL_USERNAME")
CAPITAL_PASSWORD = os.getenv("CAPITAL_PASSWORD")

BASE_URL = "https://api-capital.backend-capital.com"
SESSION_URL = f"{BASE_URL}/session"
ORDERS_URL = f"{BASE_URL}/positions"

def get_auth_headers():
    headers = {
        "X-CAP-API-KEY": CAPITAL_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "identifier": CAPITAL_USERNAME,
        "password": CAPITAL_PASSWORD
    }
    response = requests.post(SESSION_URL, headers=headers, json=payload)
    auth_headers = headers.copy()
    auth_headers["X-SECURITY-TOKEN"] = response.headers.get("X-SECURITY-TOKEN")
    auth_headers["CST"] = response.headers.get("CST")
    return auth_headers

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Webhook received:", data)

    symbol = data.get("symbol")
    direction = data.get("side")  # BUY or SELL
    size = data.get("size", 1)
    order_type = data.get("order_type", "MARKET")

    headers = get_auth_headers()
    
    order_data = {
        "epic": symbol,
        "direction": direction,
        "size": size,
        "orderType": order_type,
        "guaranteedStop": False
    }

    response = requests.post(ORDERS_URL, headers=headers, json=order_data)
    if response.status_code in [200, 201]:
        log_trade(symbol, direction, size)
        return jsonify({"status": "success", "response": response.json()})
    else:
        return jsonify({"status": "error", "details": response.text}), 400

def log_trade(symbol, direction, size):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_data = {
        "timestamp": now,
        "symbol": symbol,
        "direction": direction,
        "size": size
    }
    df = pd.DataFrame([log_data])
    try:
        df.to_csv("trade_log.csv", mode='a', header=not os.path.exists("trade_log.csv"), index=False)
    except Exception as e:
        print("Logging error:", e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
