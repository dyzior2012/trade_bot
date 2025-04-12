from indicators.ta_wrapper import calculate_indicators
from utils.debug_logger import log_strategy_debug

def squeeze_breakout_strategy(df):
    if len(df) < 30:
        return False

    df = calculate_indicators(df)
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # Kompresja wstęg Bollingera
    bb_width = df['bb_high'] - df['bb_low']
    avg_bb_width = bb_width.rolling(window=20).mean()
    is_squeeze = bb_width.iloc[-1] < avg_bb_width.iloc[-1] * 0.8

    # Spadające ATR (niskie zmienności)
    atr_falling = df['atr'].iloc[-1] < df['atr'].rolling(20).mean().iloc[-1]

    # Świeca breakout
    breakout_candle = (
        latest['close'] > latest['open'] and
        latest['close'] > df['bb_high'].iloc[-2] and
        latest['volume'] > df['volume'].rolling(10).mean().iloc[-1]
    )

    # RSI w strefie neutralnej – bez skrajnego wykupienia
    neutral_rsi = 40 < latest['rsi'] < 60

    passed = is_squeeze and atr_falling and breakout_candle and neutral_rsi

    log_strategy_debug(
        df.name if hasattr(df, 'name') else "UNKNOWN",
        'squeeze_breakout',
        latest['ema20'],
        latest['ema50'],
        latest['ema200'],
        latest['close'],
        df['atr'].iloc[-1],
        latest['rsi'],
        int(passed)
    )

    return passed
