# state/position_tracker.py
import csv
import os
from datetime import datetime

POSITION_LOG = 'logs/position_log.csv'

def log_position(symbol, qty, entry_price, side, sl, tp, strategy='N/A'):
    first_write = not os.path.exists(POSITION_LOG)
    os.makedirs(os.path.dirname(POSITION_LOG), exist_ok=True)

    with open(POSITION_LOG, mode='a', newline='') as file:
        writer = csv.writer(file)
        if first_write:
            writer.writerow(['timestamp', 'symbol', 'qty', 'entry_price', 'side', 'sl', 'tp', 'strategy'])

        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            symbol,
            qty,
            entry_price,
            side,
            sl,
            tp,
            strategy
        ])
