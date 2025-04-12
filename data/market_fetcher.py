# data/market_fetcher.py
import pandas as pd
from alpaca_trade_api.rest import REST, TimeFrame
from config import API_KEY, API_SECRET, BASE_URL, TIMEFRAME, BACKTEST

api = REST(API_KEY, API_SECRET, BASE_URL)

# Zamiana TIMEFRAME na dynamiczny obiekt TimeFrame
def parse_timeframe(tf_str):
    if tf_str == '1Min':
        return TimeFrame.Minute
    elif tf_str == '5Min':
        return TimeFrame(5, TimeFrame.Unit.Minute)
    elif tf_str == '1H':
        return TimeFrame.Hour
    elif tf_str == '1D':
        return TimeFrame.Day
    else:
        raise ValueError(f"Unsupported TIMEFRAME: {tf_str}")

def get_latest_data(symbol, limit=300):
    try:
        if BACKTEST:
            path = f"backtest_data/{symbol}.csv"
            df = pd.read_csv(path, parse_dates=['timestamp'], index_col='timestamp')
            df = df.tail(limit)
            df.index = df.index.tz_localize(None)
            df.name = symbol
            print(f"[BACKTEST FETCH] {symbol} — {len(df)} świec z CSV")
            return df

        tf = parse_timeframe(TIMEFRAME)
        bars = api.get_bars(symbol, tf, limit=limit)
        df = bars.df
        if df.empty:
            print(f"[FETCH EMPTY] {symbol} — brak świec.")
            return None
        df.index = df.index.tz_localize(None)
        df.name = symbol
        print(f"[FETCH DEBUG] {symbol} — {len(df)} świec")
        return df

    except Exception as e:
        print(f"[FETCH ERROR] {symbol}: {e}")
        return None
