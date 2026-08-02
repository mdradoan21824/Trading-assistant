import time

from core.response import success
from storage.forex_watchlist import get_forex_watchlist
from core.forex_signal import forex_signal


def build_forex_overview():
    symbols = get_forex_watchlist()

    watchlist_items = []

    for i, sym in enumerate(symbols):
        if i > 0:
            time.sleep(2)

        result = forex_signal(sym, "D")

        if not result["success"]:
            continue

        data = result["data"]

        watchlist_items.append({
            "symbol": sym,
            "close": data["close"],
            "stage_label": data["stage_label"],
            "direction": data["direction"],
        })

    return success("Forex Overview", {"watchlist": watchlist_items})
