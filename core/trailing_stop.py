# core/trailing_stop.py
from config import TRAILING_SL_RATIO  # dodaj w config.py np. TRAILING_SL_RATIO = 0.8

def update_trailing_sl(position, current_price, atr):
    """
    Aktualizuje SL pozycji, jeśli można go przesunąć w bardziej korzystne miejsce.
    """
    new_sl = current_price - atr * TRAILING_SL_RATIO if position['side'] == 'buy' else current_price + atr * TRAILING_SL_RATIO

    if position['side'] == 'buy' and new_sl > position['sl']:
        position['sl'] = new_sl
        return True
    elif position['side'] == 'sell' and new_sl < position['sl']:
        position['sl'] = new_sl
        return True
    return False
