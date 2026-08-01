from storage.json_store import load, save

FILE = "storage/forex_watchlist.json"

DEFAULT_MAJORS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CHF", "USD/CAD", "NZD/USD"]


def get_forex_watchlist():
    data = load(FILE, {"symbols": DEFAULT_MAJORS.copy()})
    return data["symbols"]


def save_forex_watchlist(symbols):
    save(FILE, {"symbols": symbols})
