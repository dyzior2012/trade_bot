# utils/market_status.py
from alpaca_trade_api.rest import REST
from config import API_KEY, API_SECRET, BASE_URL

def is_market_open():
    api = REST(API_KEY, API_SECRET, BASE_URL)
    clock = api.get_clock()
    return clock.is_open
