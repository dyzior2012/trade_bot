# strategies/short_trend.py
from utils.debug_logger import log_strategy_debug

def short_trend_strategy(df):
    if len(df) < 20:
        return False

    latest = df.iloc[-1]

    is_downtrend = latest['ema20'] < latest['ema50'] < latest['ema200']
    adx_strong = latest['adx'] > 20
    rsi_confirm = latest['rsi'] < 50
    bearish_candle = latest['close'] < latest['open']
    below_ema20 = latest['close'] < latest['ema20']

    log_strategy_debug(
        df.name if hasattr(df, 'name') else "UNKNOWN",
        'short_trend',
        latest['ema20'],
        latest['ema50'],
        latest['ema200'],
        latest['close'],
        latest['adx'],
        latest['rsi'],
        0
    )

    return is_downtrend and adx_strong and rsi_confirm and bearish_candle and below_ema20
