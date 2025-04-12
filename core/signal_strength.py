# core/singal_strenght.py

from datetime import datetime, timedelta

def is_extremely_strong_signal(df):
    if len(df) < 2:
        return False
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    jump = (latest['close'] - prev['close']) / prev['close']
    body = abs(latest['close'] - latest['open'])
    candle = latest['high'] - latest['low']
    volume_avg = df['volume'].rolling(10).mean().iloc[-2] if 'volume' in df else 0

    return (
        jump > 0.01 and
        latest['volume'] > 2 * volume_avg and
        candle > 0 and
        (body / candle) > 0.7 and
        latest.get('rsi', 0) > 65
    )
