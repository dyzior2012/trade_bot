from indicators.ta_wrapper import calculate_indicators
from utils.debug_logger import log_strategy_debug
from config import (
    BREAKOUT_LOOKBACK,
    BREAKOUT_EMA_THRESHOLD,
    BREAKOUT_VOLUME_MULT_UP,
    BREAKOUT_VOLUME_MULT_DOWN,
    BREAKOUT_CONFIRM_PERCENT
)

def breakout_strategy(df):
    df = calculate_indicators(df)
    if len(df) < BREAKOUT_LOOKBACK + 5:
        return None  # za mało danych

    latest = df.iloc[-1]
    lookback = BREAKOUT_LOOKBACK
    threshold = BREAKOUT_EMA_THRESHOLD
    atr_threshold = df['atr'].rolling(30).mean().iloc[-1]

    local_high = df['high'].iloc[-lookback:-1].max()
    local_low = df['low'].iloc[-lookback:-1].min()
    atr = df['atr'].iloc[-1]
    volume_avg = df['volume'].rolling(10).mean().iloc[-1]

    ema20 = latest['ema20']
    ema50 = latest['ema50']
    ema200 = latest['ema200']
    close = latest['close']
    volume = latest['volume']

    ema_close = abs(ema20 - ema50) < threshold and abs(ema50 - ema200) < threshold
    is_consolidating = atr < atr_threshold and ema_close

    breakout_up = (
        close > local_high * (1 + BREAKOUT_CONFIRM_PERCENT) and
        volume > BREAKOUT_VOLUME_MULT_UP * volume_avg
    )
    breakout_down = (
        close < local_low * (1 - BREAKOUT_CONFIRM_PERCENT) and
        volume > BREAKOUT_VOLUME_MULT_DOWN * volume_avg
    )

    log_strategy_debug(
        df.name if hasattr(df, 'name') else "UNKNOWN",
        'breakout',
        ema20, ema50, ema200, close, atr, 0, 0  # brak RSI i ADX
    )

    if is_consolidating and breakout_up:
        return 'buy'
    elif is_consolidating and breakout_down:
        return 'sell'
    else:
        return None
