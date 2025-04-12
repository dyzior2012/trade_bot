# engine_manager.py

from config import STRATEGIES
from strategies.trend import trend_strategy
from strategies.reversion import reversion_strategy
from strategies.scalper import scalper_strategy
from strategies.short_trend import short_trend_strategy
from data.market_fetcher import get_latest_data
from core.trade_executor import execute_trade
from utils.time_filter import is_strategy_allowed
from indicators.ta_wrapper import calculate_indicators
from strategies.squeeze_breakout import squeeze_breakout_strategy
from strategies.breakout import breakout_strategy
from config import ALLOW_BREAKOUT_LONG
from config import ALLOW_BREAKOUT_SHORT


def process_ticker(symbol):
    df = get_latest_data(symbol)
    if df is None:
        return

    df.name = symbol  # <- TO MUSI BYĆ PRZED calculate_indicators
    df = calculate_indicators(df)

    print(f"[ENGINE] Analizuję {symbol}...")

    if 'trend' in STRATEGIES and is_strategy_allowed('trend') and trend_strategy(df):
        execute_trade(symbol, 'buy', df)

    elif 'reversion' in STRATEGIES and is_strategy_allowed('reversion') and reversion_strategy(df):
        execute_trade(symbol, 'buy', df)

    elif 'scalper' in STRATEGIES and is_strategy_allowed('scalper') and scalper_strategy(df):
        execute_trade(symbol, 'buy', df)

    elif 'short_trend' in STRATEGIES and is_strategy_allowed('trend') and short_trend_strategy(df):
        print(
            f"[SHORT DEBUG] {df.iloc[-1]['ema20']:.2f} < {df.iloc[-1]['ema50']:.2f} < {df.iloc[-1]['ema200']:.2f} | ADX: {df.iloc[-1]['adx']:.2f} | RSI: {df.iloc[-1]['rsi']:.2f}")
        execute_trade(symbol, 'sell', df)

    elif 'squeeze_breakout' in STRATEGIES and is_strategy_allowed('squeeze_breakout') and squeeze_breakout_strategy(df):
        execute_trade(symbol, 'buy', df)

    if 'breakout' in STRATEGIES and is_strategy_allowed('breakout'):
        direction = breakout_strategy(df)
        if direction == 'buy' and ALLOW_BREAKOUT_LONG:
            execute_trade(symbol, 'buy', df)
        elif direction == 'sell' and ALLOW_BREAKOUT_SHORT:
            execute_trade(symbol, 'sell', df)

