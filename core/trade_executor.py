# core/trade_executor.py

import datetime
import json
import os
import time
from pytz import timezone
from alpaca_trade_api.rest import REST, TimeFrame

from config import (
    API_KEY, API_SECRET, BASE_URL, CAPITAL, RISK_PER_TRADE,
    MAX_POSITIONS, TICKER_SECTOR, MAX_SECTOR_EXPOSURE, DEFAULT_SL_PCT
)
from core.position_manager import close_position
from core.trailing_stop import update_trailing_sl
from indicators.ta_wrapper import calculate_indicators
from core.risk_manager import calculate_position_size
from utils.logger import log_trailing_update
from state.position_tracker import log_position
from core.signal_strength import is_extremely_strong_signal  # <- ważne
from config import DEBUG

api = REST(API_KEY, API_SECRET, BASE_URL)
positions = {}
cooldown_tracker = {}

POSITIONS_FILE = 'state/positions.json'
MAX_RETRIES = 3
COOLDOWN = datetime.timedelta(minutes=2)
MAX_POSITION_AGE = datetime.timedelta(hours=6)

def is_market_near_close(minutes=15):
    now = datetime.datetime.now(timezone("US/Eastern"))
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_close - now <= datetime.timedelta(minutes=minutes)

def safe_submit_order(**kwargs):
    for attempt in range(MAX_RETRIES):
        try:
            return api.submit_order(**kwargs)
        except Exception as e:
            print(f"[ORDER RETRY {attempt+1}] {kwargs['symbol']} — {e}")
            time.sleep(2)
    raise Exception(f"FAILED ORDER: {kwargs['symbol']}")

def get_sector_exposure(sector):
    exposure = 0
    for sym, pos in positions.items():
        if TICKER_SECTOR.get(sym) == sector:
            exposure += pos['qty'] * pos['entry_price']
    return exposure / CAPITAL

def execute_trade(symbol, side, df):
    if symbol in positions:
        print(f"[SKIP] {symbol} already in position.")
        return

    if len(positions) >= MAX_POSITIONS:
        print(f"[LIMIT] Maksymalna liczba pozycji ({MAX_POSITIONS}) osiągnięta.")
        return

    now = datetime.datetime.now()
    if symbol in cooldown_tracker and now - cooldown_tracker[symbol] < COOLDOWN:
        print(f"[COOLDOWN] {symbol} pominięty (niedawny sygnał)")
        return
    cooldown_tracker[symbol] = now

    if is_market_near_close(minutes=15):
        if not is_extremely_strong_signal(df):
            print(f"[MARKET CLOSE BLOCK] {symbol} pominięty — blisko końca sesji.")
            return
        else:
            print(f"[FORCE TRADE] {symbol} — ekstremalny sygnał, mimo bliskości zamknięcia.")

    sector = TICKER_SECTOR.get(symbol)
    if sector and get_sector_exposure(sector) > MAX_SECTOR_EXPOSURE:
        print(f"[SECTOR LIMIT] {symbol} nie otwarty — sektor '{sector}' przekroczył limit ekspozycji.")
        return

    last_price = df.iloc[-1]['close']
    qty, sl_distance = calculate_position_size(last_price, custom_sl_pct=DEFAULT_SL_PCT)

    try:
        safe_submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )

        sl = last_price - sl_distance if side == 'buy' else last_price + sl_distance
        tp = last_price + 2 * sl_distance if side == 'buy' else last_price - 2 * sl_distance

        positions[symbol] = {
            'qty': qty,
            'entry_price': last_price,
            'side': side,
            'sl': sl,
            'tp': tp,
            'time': now
        }

        log_position(symbol, qty, last_price, side, sl, tp)
        print(f"[ORDER] {side.upper()} {qty}x {symbol} @ {last_price:.2f}")

    except Exception as e:
        print(f"[ORDER ERROR] {symbol}: {e}")

    save_positions()

def check_positions():
    if not positions:
        print("[INFO] Brak otwartych pozycji – check_positions pominięte.")
        return

    for symbol, pos in list(positions.items()):
        try:
            bars = api.get_bars(symbol, TimeFrame.Minute, limit=50)
            if bars is None or bars.df is None or bars.df.empty or len(bars.df) < 5:
                print(f"[DATA WARNING] {symbol} — zbyt mało danych do analizy.")
                continue

            df = calculate_indicators(bars.df)
            if df.empty:
                print(f"[WAIT] {symbol} — wskaźniki usunęły wszystkie świece.")
                continue

            current_price = df.iloc[-1]['close']
            atr = df['atr'].iloc[-1]

            if is_market_near_close(minutes=5) and (datetime.datetime.now() - pos['time'] > datetime.timedelta(hours=1)):
                print(f"[AUTO CLOSE] {symbol} – stara pozycja zamknięta przed końcem sesji.")
                exit_side = 'sell' if pos['side'] == 'buy' else 'buy'
                close_position(api, symbol, pos['qty'], exit_side)
                del positions[symbol]
                continue

            if update_trailing_sl(pos, current_price, atr):
                log_trailing_update(symbol, pos['sl'])
                print(f"[TRAILING UPDATE] {symbol} new SL: {pos['sl']:.2f}")

            hit_tp = current_price >= pos['tp'] if pos['side'] == 'buy' else current_price <= pos['tp']
            hit_sl = current_price <= pos['sl'] if pos['side'] == 'buy' else current_price >= pos['sl']

            if hit_tp or hit_sl:
                exit_side = 'sell' if pos['side'] == 'buy' else 'buy'
                close_position(api, symbol, pos['qty'], exit_side)
                print(f"[CLOSE] {symbol} @ {current_price:.2f} (TP/SL HIT)")
                del positions[symbol]

            elif datetime.datetime.now() - pos['time'] > MAX_POSITION_AGE:
                print(f"[AUTO EXIT] {symbol} zbyt długo otwarty. Zamykam pozycję.")
                exit_side = 'sell' if pos['side'] == 'buy' else 'buy'
                close_position(api, symbol, pos['qty'], exit_side)
                del positions[symbol]

        except Exception as e:
            if DEBUG:
                print(f"[CHECK ERROR] {symbol}: {e}")

    save_positions()

def save_positions():
    try:
        os.makedirs(os.path.dirname(POSITIONS_FILE), exist_ok=True)
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(positions, f, default=str)
    except Exception as e:
        print(f"[SAVE ERROR] {e}")

def load_positions():
    global positions
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'r') as f:
            raw = json.load(f)
            for sym in raw:
                if not raw[sym] or 'time' not in raw[sym]:
                    continue
                raw[sym]['time'] = datetime.datetime.fromisoformat(raw[sym]['time'])
            positions = raw
