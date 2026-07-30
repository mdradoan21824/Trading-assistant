import pandas as pd

from market.forex_provider import get_forex_candles
from core.response import success, error


def get_forex_indicators(symbol, timeframe="D"):
    result = get_forex_candles(symbol, timeframe, outputsize=100)

    if not result["success"]:
        return result

    data = result["data"]
    candles = data["candles"]

    if len(candles) < 30:
        return error(f"Not enough historical data for {data['symbol']}.")

    close = pd.Series([float(c["close"]) for c in candles])

    # RSI (14) with EMA smoothing
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1 / 14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / 14, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi_ema9 = rsi.ewm(span=9, adjust=False).mean()

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    # Recent range for price-action stage (last 10 candles, excluding current)
    recent_low = float(close.iloc[-11:-1].min())
    recent_high = float(close.iloc[-11:-1].max())

    return success(
        f"Indicators for {data['symbol']}",
        {
            "symbol": data["symbol"],
            "timeframe": data["interval"],
            "close": round(float(close.iloc[-1]), 5),
            "recent_low": round(recent_low, 5),
            "recent_high": round(recent_high, 5),
            "rsi": round(float(rsi.iloc[-1]), 2),
            "rsi_ema9": round(float(rsi_ema9.iloc[-1]), 2),
            "macd": round(float(macd_line.iloc[-1]), 5),
            "macd_signal": round(float(signal_line.iloc[-1]), 5),
            "macd_histogram": round(float(histogram.iloc[-1]), 5),
            "histogram_series": [round(float(x), 5) for x in histogram.tail(5)],
            "candles": candles,
        },
    )
