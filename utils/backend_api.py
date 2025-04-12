from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import csv
from datetime import datetime
import os
from alpaca_trade_api.rest import REST
from config import API_KEY, API_SECRET, BASE_URL

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE_FILE = "state/positions.json"
LOG_FILE = "logs/position_log.csv"

class Position(BaseModel):
    symbol: str
    qty: int
    entry_price: float
    sl: float
    tp: float
    time: str

@app.get("/api/positions")
def get_positions():
    if not os.path.exists(STATE_FILE):
        return []
    with open(STATE_FILE, "r") as f:
        raw = json.load(f)
        return [{"symbol": k, **v} for k, v in raw.items()]

@app.get("/api/logs")
def get_logs():
    if not os.path.exists(LOG_FILE):
        return []
    balance = 0
    data = []
    with open(LOG_FILE, "r") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            timestamp = row[0]
            pnl = float(row[6]) if len(row) > 6 else 0
            balance += pnl
            data.append({"timestamp": timestamp, "balance": round(balance, 2)})
    return data[-100:]  # ostatnie 100 punktów

@app.get("/api/market")
def get_market_status():
    try:
        api = REST(API_KEY, API_SECRET, BASE_URL)
        clock = api.get_clock()
        return {
            "is_open": clock.is_open,
            "timestamp": clock.timestamp.isoformat()
        }
    except Exception as e:
        return {"is_open": False, "timestamp": str(datetime.utcnow())}

@app.get("/api/pnl")
def get_live_pnl():
    try:
        from alpaca_trade_api.rest import REST
        api = REST(API_KEY, API_SECRET, BASE_URL)

        if not os.path.exists(STATE_FILE):
            return []

        with open(STATE_FILE, "r") as f:
            raw = json.load(f)

        result = []
        for symbol, pos in raw.items():
            latest = api.get_latest_trade(symbol)
            current_price = latest.price
            entry_price = float(pos["entry_price"])
            qty = int(pos["qty"])
            pnl = round((current_price - entry_price) * qty, 2) if pos["side"] == "buy" else round((entry_price - current_price) * qty, 2)

            result.append({
                "symbol": symbol,
                "entry": entry_price,
                "current": current_price,
                "qty": qty,
                "side": pos["side"],
                "live_pnl": pnl
            })

        return result

    except Exception as e:
        return {"error": str(e)}
