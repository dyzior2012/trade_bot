# strategies/reversion.py
from utils.debug_logger import log_strategy_debug

def reversion_strategy(df):
    if len(df) < 20:
        return False

    latest = df.iloc[-1]
    prev = df.iloc[-2]
    prev_volume_avg = df['volume'].rolling(10).mean().iloc[-2]

    # Sygnał odwrócenia: RSI niskie, cena mocno pod BB, świeca wzrostowa
    strong_down_move = latest['close'] < latest['bb_low'] and latest['rsi'] < 40
    reversal_candle = (
        latest['close'] > latest['open'] and
        latest['low'] < prev['low'] and
        latest['close'] > prev['close']
    )
    volume_confirm = latest['volume'] > 0.8 * prev_volume_avg
    ema_filter = latest['close'] < latest['ema20']

    signal = strong_down_move and reversal_candle and volume_confirm and ema_filter

    log_strategy_debug(
        df.name if hasattr(df, 'name') else "UNKNOWN",
        'reversion',
        latest['ema20'],
        latest['ema50'],
        latest['ema200'],
        latest['close'],
        latest['adx'] if 'adx' in latest else 0,
        latest['rsi'] if 'rsi' in latest else 0,
        0
    )

    return signal
