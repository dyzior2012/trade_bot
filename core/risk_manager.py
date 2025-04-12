# core/risk_manager.py
from config import CAPITAL, RISK_PER_TRADE

def calculate_position_size(price, custom_sl_pct=0.01):
    """
    price: cena instrumentu
    custom_sl_pct: procent odległości SL (np. 0.01 to 1%)
    """
    risk_amount = CAPITAL * RISK_PER_TRADE
    sl_distance = price * custom_sl_pct
    qty = int(risk_amount / sl_distance)
    return qty, sl_distance
