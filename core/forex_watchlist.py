from core.response import success, error
from storage.forex_watchlist import get_forex_watchlist, save_forex_watchlist
from market.forex_provider import normalize_forex_symbol, get_forex_candles


def _parse_symbols(raw_input):
    parts = raw_input.split(",")
    return [normalize_forex_symbol(p.strip()) for p in parts if p.strip()]


def add(symbol):
    requested = _parse_symbols(symbol)

    symbols = get_forex_watchlist()

    added = []
    skipped = []

    for sym in requested:
        if sym in symbols:
            skipped.append(sym)
            continue
        symbols.append(sym)
        added.append(sym)

    save_forex_watchlist(symbols)

    if not added:
        return error(f"Already in forex watchlist: {', '.join(skipped)}")

    message = f"Added: {', '.join(added)}"
    if skipped:
        message += f"\nAlready exists: {', '.join(skipped)}"

    return success(message, {"watchlist": symbols})


def remove(symbol):
    requested = _parse_symbols(symbol)

    symbols = get_forex_watchlist()

    removed = []
    not_found = []

    for sym in requested:
        if sym not in symbols:
            not_found.append(sym)
            continue
        symbols.remove(sym)
        removed.append(sym)

    save_forex_watchlist(symbols)

    if not removed:
        return error(f"Not found: {', '.join(not_found)}")

    message = f"Removed: {', '.join(removed)}"
    if not_found:
        message += f"\nNot found: {', '.join(not_found)}"

    return success(message, {"watchlist": symbols})


def show():
    symbols = get_forex_watchlist()

    if not symbols:
        return success("Forex Watchlist", {"watchlist": [], "prices": []})

    prices = []

    for sym in symbols:
        result = get_forex_candles(sym, "D", outputsize=2)

        if not result["success"]:
            prices.append({"symbol": sym, "price": None, "change_pct": None})
            continue

        candles = result["data"]["candles"]

        if len(candles) < 2:
            prices.append({"symbol": sym, "price": None, "change_pct": None})
            continue

        prev_close = float(candles[-2]["close"])
        curr_close = float(candles[-1]["close"])
        change_pct = (curr_close - prev_close) / prev_close * 100

        prices.append({
            "symbol": sym,
            "price": round(curr_close, 5),
            "change_pct": round(change_pct, 2),
        })

    return success("Forex Watchlist", {"watchlist": symbols, "prices": prices})
