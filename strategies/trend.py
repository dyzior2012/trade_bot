# strategies/trend.py
from utils.debug_logger import log_strategy_debug


def trend_strategy(df):
    if len(df) < 4:
        return False

    latest = df.iloc[-1]
    prev1 = df.iloc[-2]
    prev3 = df.iloc[-4]

    adx_rising = latest['adx'] > prev3['adx']
    ema50_up = latest['ema50'] > prev1['ema50']

    trend_valid = (
            latest['ema20'] > latest['ema50'] > latest['ema200'] and
            latest['close'] > latest['ema20'] and
            latest['adx'] > 25 and
            latest['rsi'] > 60 and
            adx_rising and
            ema50_up
    )

    log_strategy_debug(
        df.name if hasattr(df, 'name') else "UNKNOWN",
        'trend',
        latest['ema20'],
        latest['ema50'],
        latest['ema200'],
        latest['close'],
        latest['adx'],
        latest['rsi'],
        int(adx_rising)
    )

    return trend_valid
