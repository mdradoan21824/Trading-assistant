def _to_float(candle):
    return {
        "open": float(candle["open"]),
        "high": float(candle["high"]),
        "low": float(candle["low"]),
        "close": float(candle["close"]),
    }


def _classify_single_candle(candle):
    c = _to_float(candle)
    body = abs(c["close"] - c["open"])
    candle_range = c["high"] - c["low"]

    if candle_range == 0:
        return None

    upper_wick = c["high"] - max(c["open"], c["close"])
    lower_wick = min(c["open"], c["close"]) - c["low"]
    is_bullish = c["close"] > c["open"]

    small_body = body <= candle_range * 0.35

    # Hammer: small body, long lower wick, small upper wick
    if small_body and lower_wick >= body * 2 and upper_wick <= body * 0.5:
        return {"name": "Hammer", "direction": "BUY"}

    # Shooting Star / Bearish Pin Bar: small body, long upper wick, small lower wick
    if small_body and upper_wick >= body * 2 and lower_wick <= body * 0.5:
        return {"name": "Shooting Star", "direction": "SELL"}

    return None


def _classify_engulfing(prev_candle, current_candle):
    prev = _to_float(prev_candle)
    curr = _to_float(current_candle)

    prev_bullish = prev["close"] > prev["open"]
    curr_bullish = curr["close"] > curr["open"]

    prev_body_top = max(prev["open"], prev["close"])
    prev_body_bottom = min(prev["open"], prev["close"])
    curr_body_top = max(curr["open"], curr["close"])
    curr_body_bottom = min(curr["open"], curr["close"])

    # Bullish Engulfing: prev bearish, curr bullish, curr body engulfs prev body
    if not prev_bullish and curr_bullish:
        if curr_body_top >= prev_body_top and curr_body_bottom <= prev_body_bottom:
            return {"name": "Bullish Engulfing", "direction": "BUY"}

    # Bearish Engulfing: prev bullish, curr bearish, curr body engulfs prev body
    if prev_bullish and not curr_bullish:
        if curr_body_top >= prev_body_top and curr_body_bottom <= prev_body_bottom:
            return {"name": "Bearish Engulfing", "direction": "SELL"}

    return None


def _check_confirmation(pattern, pattern_candle, confirmation_candle):
    p = _to_float(pattern_candle)
    conf = _to_float(confirmation_candle)

    if pattern["direction"] == "BUY":
        return conf["close"] > p["high"]

    if pattern["direction"] == "SELL":
        return conf["close"] < p["low"]

    return False


def detect_price_action(candles):
    if len(candles) < 3:
        return None

    prev_candle = candles[-3]
    pattern_candle = candles[-2]
    confirmation_candle = candles[-1]

    pattern = _classify_engulfing(prev_candle, pattern_candle)

    if pattern is None:
        pattern = _classify_single_candle(pattern_candle)

    if pattern is None:
        return None

    confirmed = _check_confirmation(pattern, pattern_candle, confirmation_candle)

    return {
        "name": pattern["name"],
        "direction": pattern["direction"],
        "confirmed": confirmed,
    }
