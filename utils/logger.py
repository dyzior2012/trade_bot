# utils/logger.py
import csv
import os
from datetime import datetime

LOG_FILE = 'logs/signal_log.csv'

def log_signal(symbol, strategy, price, signal_type):
    first_write = not os.path.exists(LOG_FILE)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if first_write:
            writer.writerow(['timestamp', 'symbol', 'strategy', 'signal_type', 'price'])

        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            symbol,
            strategy,
            signal_type,
            price
        ])

def log_trailing_update(symbol, new_sl):
    first_write = not os.path.exists(LOG_FILE)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        if first_write:
            writer.writerow(['timestamp', 'symbol', 'strategy', 'signal_type', 'price'])

        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            symbol,
            'trailing_stop',
            'update_sl',
            new_sl
        ])
