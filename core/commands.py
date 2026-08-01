from core.health import status, health
from core.user import whoami
from core.portfolio import portfolio
from core.connection import connection
from core.analyze import analyze_symbol
from core.price import price
from core.watchlist import add, remove, show
from core.market import market
from core.signal import signal
from core.overview import build_overview

COMMANDS = {
    "status": status,
    "health": health,
    "whoami": whoami,
    "portfolio": portfolio,
    "connection": connection,
}


def execute_analysis(symbol):
    return analyze_symbol(symbol)


def execute_price(symbol):
    return price(symbol)


def execute_market():
    return market()


def execute_signal(symbol, timeframe=None):
    from market.forex_provider import is_forex_symbol

    if is_forex_symbol(symbol):
        from core.forex_signal import forex_signal
        return forex_signal(symbol, timeframe or "D")

    return signal(symbol)


def execute_overview():
    return build_overview()


def execute_watchlist(action, symbol=None):
    action = action.lower()

    if action == "list":
        return show()

    if action == "add":
        if not symbol:
            return {
                "success": False,
                "message": "Usage: /watchlist add SYMBOL",
                "data": {},
            }
        return add(symbol)

    if action == "remove":
        if not symbol:
            return {
                "success": False,
                "message": "Usage: /watchlist remove SYMBOL",
                "data": {},
            }
        return remove(symbol)

    return {
        "success": False,
        "message": "Usage: /watchlist | add SYMBOL | remove SYMBOL",
        "data": {},
    }


def execute_analyze(symbol):
    from core.analyze import analyze_symbol
    return analyze_symbol(symbol)


def execute_recap():
    from core.recap import build_recap
    return build_recap()


def execute_forex_test(symbol, timeframe="D"):
    from strategies.forex_indicators import get_forex_indicators
    return get_forex_indicators(symbol, timeframe)


def execute_forex_watchlist(action, symbol=None):
    from core.forex_watchlist import add, remove, show

    action = action.lower()

    if action == "list" or action == "":
        return show()

    if action == "add":
        if not symbol:
            return {
                "success": False,
                "message": "Usage: /forex watchlist add SYMBOL",
                "data": {},
            }
        return add(symbol)

    if action == "remove":
        if not symbol:
            return {
                "success": False,
                "message": "Usage: /forex watchlist remove SYMBOL",
                "data": {},
            }
        return remove(symbol)

    return {
        "success": False,
        "message": "Usage: /forex watchlist | add SYMBOL | remove SYMBOL",
        "data": {},
    }


def execute_forex_overview():
    from core.forex_overview import build_forex_overview
    return build_forex_overview()
