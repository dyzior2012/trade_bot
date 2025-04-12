# utils/time_filter.py
from datetime import datetime, time

# Godziny otwarcia sesji w USA (czas lokalny bota, np. CET)
STRATEGY_SCHEDULE = {
    'scalper': (time(15, 30), time(17, 30)),
    'trend': (time(15, 30), time(22, 0)),
    'reversion': (time(15, 30), time(22, 0)),
}

def is_strategy_allowed(strategy_name):
    now = datetime.now().time()
    if strategy_name not in STRATEGY_SCHEDULE:
        return True
    start, end = STRATEGY_SCHEDULE[strategy_name]
    return start <= now <= end

def get_allowed_strategies(all_strategies):
    now = datetime.now().time()
    return [
        strategy for strategy in all_strategies
        if strategy not in STRATEGY_SCHEDULE or
           STRATEGY_SCHEDULE[strategy][0] <= now <= STRATEGY_SCHEDULE[strategy][1]
    ]
