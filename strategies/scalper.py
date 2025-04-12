# strategies/scalper.py
from utils.debug_logger import log_strategy_debug

def scalper_strategy(df):
    if len(df) < 20:
        return False

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # Wolumen
    volume_avg = df['volume'].rolling(10).mean().iloc[-2]
    volume_spike = latest['volume'] > 1.3 * volume_avg

    # Ciało świecy / breakout bar
    body = abs(latest['close'] - latest['open'])
    candle_range = latest['high'] - latest['low']
    small_wick = candle_range > 0 and (body / candle_range > 0.65)

    # Skok ceny względem poprzedniej świecy
    price_jump = (latest['close'] - prev['close']) / prev['close'] > 0.002

    # Nowy warunek: wybicie lokalnego szczytu z ostatnich 5 świec
    local_high = df['high'].iloc[-6:-1].max()
    breakout_high = latest['high'] > local_high

    # RSI jako filtr kierunkowy
    rsi_filter = latest['rsi'] > 50 if 'rsi' in latest else True

    # Logowanie debugowe
    log_strategy_debug(
        df.name if hasattr(df, 'name') else "UNKNOWN",
        'scalper',
        0, 0, 0,
        latest['close'],
        0,
        latest['rsi'] if 'rsi' in latest else 0,
        0
    )

    return volume_spike and price_jump and small_wick and breakout_high and rsi_filter
