# main.py
import time
from datetime import datetime
from config import TICKERS, DEBUG, BACKTEST
from core.engine_manager import process_ticker
from core.trade_executor import check_positions, load_positions
from utils.market_status import is_market_open

def run_bot():
    print(f"\n[INIT] Bot uruchomiony {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    load_positions()

    while True:
        if not BACKTEST and not is_market_open():
            print("[INFO] Rynek zamknięty, bot nyny...")
            time.sleep(300)
            continue

        for symbol in TICKERS:
            try:
                process_ticker(symbol)
            except Exception as e:
                if DEBUG:
                    print(f"[ERROR] {symbol}: {e}")

        try:
            check_positions()
        except Exception as e:
            if DEBUG:
                print(f"[CHECK_POSITIONS ERROR]: {e}")

        time.sleep(60 if not BACKTEST else 0.5)

if __name__ == '__main__':
    run_bot()
