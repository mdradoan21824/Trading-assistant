import requests

from config.settings import TWELVEDATA_API_KEY
from core.response import success, error
from utils.logger import logger

BASE_URL = "https://api.twelvedata.com/time_series"

FRIENDLY_ERROR = "Forex data service is temporarily unavailable. Please try again in a few minutes."


def normalize_forex_symbol(raw_symbol):
    symbol = raw_symbol.upper().replace(" ", "")

    if "/" in symbol:
        return symbol

    if len(symbol) == 6:
        return f"{symbol[:3]}/{symbol[3:]}"

    return symbol


TIMEFRAME_MAP = {
    "D": "1day",
    "DAY": "1day",
    "H1": "1h",
    "H4": "4h",
}


def get_forex_candles(symbol, timeframe="D", outputsize=100):
    if not TWELVEDATA_API_KEY:
        return error("TwelveData API key not configured.")

    normalized_symbol = normalize_forex_symbol(symbol)
    interval = TIMEFRAME_MAP.get(timeframe.upper(), "1day")

    try:
        params = {
            "symbol": normalized_symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": TWELVEDATA_API_KEY,
        }

        response = requests.get(BASE_URL, params=params, timeout=15)

        if response.status_code != 200:
            logger.error(f"TwelveData HTTP error for {normalized_symbol}: {response.status_code}")
            return error(FRIENDLY_ERROR)

        data = response.json()

        if data.get("status") == "error":
            logger.error(f"TwelveData API error for {normalized_symbol}: {data.get('message')}")
            return error(f"Could not find data for {normalized_symbol}. Please check the symbol.")

        values = data.get("values")

        if not values:
            return error(f"No historical data found for {normalized_symbol}.")

        values = list(reversed(values))

        return success(
            f"Candles for {normalized_symbol}",
            {
                "symbol": normalized_symbol,
                "interval": interval,
                "candles": values,
            },
        )

    except requests.exceptions.Timeout:
        logger.error(f"TwelveData timeout for {normalized_symbol}")
        return error(FRIENDLY_ERROR)
    except Exception as e:
        logger.error(f"TwelveData error for {normalized_symbol}: {e}")
        return error(FRIENDLY_ERROR)
