# core/position_manager.py

def close_position(api, symbol, qty, side):
    """
    Zamknięcie pozycji przez złożenie przeciwnego zlecenia rynkowego.
    """
    try:
        api.submit_order(
            symbol=symbol,
            qty=qty,
            side=side,
            type='market',
            time_in_force='gtc'
        )
        print(f"[CLOSE ORDER] {side.upper()} {qty}x {symbol}")
    except Exception as e:
        print(f"[CLOSE ERROR] {symbol}: {e}")
