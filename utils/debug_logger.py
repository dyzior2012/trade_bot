from datetime import datetime
import csv
import os

DEBUG_LOG_FILE = 'logs/strategy_debug.csv'

HEADERS = [
    "timestamp", "symbol", "strategy",
    "ema20", "ema50", "ema200",
    "close", "adx", "rsi", "adx_rising"
]

def initialize_debug_log():
    os.makedirs(os.path.dirname(DEBUG_LOG_FILE), exist_ok=True)
    if not os.path.exists(DEBUG_LOG_FILE):
        with open(DEBUG_LOG_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

def log_strategy_debug(symbol, strategy, ema20, ema50, ema200, close, adx, rsi, adx_rising):
    initialize_debug_log()
    with open(DEBUG_LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            symbol,
            strategy,
            round(ema20, 2), round(ema50, 2), round(ema200, 2),
            round(close, 2), round(adx, 2), round(rsi, 2),
            int(adx_rising)
        ])
