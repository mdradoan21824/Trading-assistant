STAGE_LABELS = {
    0: "⚪ No Signal",
    1: "👀 Watch (Bullish)",
    2: "🟡 Setup (Bullish)",
    3: "🟠 Almost Ready (Bullish)",
    4: "🟢 BUY SIGNAL",
}

SELL_STAGE_LABELS = {
    0: "⚪ No Signal",
    1: "👀 Watch (Bearish)",
    2: "🟡 Setup (Bearish)",
    3: "🟠 Almost Ready (Bearish)",
    4: "🔴 SELL SIGNAL",
}


def _price_action_tag(price_action, direction):
    if not price_action:
        return ""

    if price_action["direction"] != direction:
        return ""

    name = price_action["name"]

    if price_action["confirmed"]:
        return f" ({name} \u2014 Confirmed \u2705)"

    return f" ({name} \u2014 pending confirmation)"


def _evaluate_bull_stage(data):
    close = data["close"]
    recent_low = data["recent_low"]
    rsi = data["rsi"]
    rsi_ema9 = data["rsi_ema9"]
    macd = data["macd"]
    macd_signal = data["macd_signal"]
    hist = data["histogram_series"]

    checks = []

    stage1 = close > recent_low * 1.005
    checks.append(("Price bounced from recent low", stage1))
    if not stage1:
        return 0, checks

    stage2 = rsi > rsi_ema9
    checks.append(("RSI crossed above RSI-EMA9", stage2))
    if not stage2:
        return 1, checks

    stage3 = len(hist) >= 3 and hist[-3] < hist[-2] < hist[-1]
    checks.append(("MACD histogram momentum improving", stage3))
    if not stage3:
        return 2, checks

    stage4 = macd > macd_signal
    checks.append(("MACD line crossed above Signal", stage4))
    if not stage4:
        return 3, checks

    return 4, checks


def _evaluate_bear_stage(data):
    close = data["close"]
    recent_high = data["recent_high"]
    rsi = data["rsi"]
    rsi_ema9 = data["rsi_ema9"]
    macd = data["macd"]
    macd_signal = data["macd_signal"]
    hist = data["histogram_series"]

    checks = []

    stage1 = close < recent_high * 0.995
    checks.append(("Price dropped from recent high", stage1))
    if not stage1:
        return 0, checks

    stage2 = rsi < rsi_ema9
    checks.append(("RSI crossed below RSI-EMA9", stage2))
    if not stage2:
        return 1, checks

    stage3 = len(hist) >= 3 and hist[-3] > hist[-2] > hist[-1]
    checks.append(("MACD histogram momentum weakening", stage3))
    if not stage3:
        return 2, checks

    stage4 = macd < macd_signal
    checks.append(("MACD line crossed below Signal", stage4))
    if not stage4:
        return 3, checks

    return 4, checks


def _check_established_trend(data):
    macd = data["macd"]
    macd_signal = data["macd_signal"]
    hist = data["histogram_series"]

    if len(hist) < 3:
        return None

    momentum_improving = hist[-3] < hist[-2] < hist[-1]
    momentum_weakening = hist[-3] > hist[-2] > hist[-1]

    if macd > macd_signal and momentum_weakening:
        return {
            "direction": "BUY",
            "stage": 3.5,
            "label": "🟡 Bullish Trend (Momentum weakening \u2014 possible pullback/correction)",
            "checks": [],
        }

    if macd < macd_signal and momentum_improving:
        return {
            "direction": "SELL",
            "stage": 3.5,
            "label": "🟡 Bearish Trend (Momentum weakening \u2014 possible bounce/correction)",
            "checks": [],
        }

    return None


def evaluate_forex_stage(data):
    bull_stage, bull_checks = _evaluate_bull_stage(data)
    bear_stage, bear_checks = _evaluate_bear_stage(data)
    price_action = data.get("price_action")

    if bull_stage < 4 and bear_stage < 4:
        trend_warning = _check_established_trend(data)
        if trend_warning:
            return trend_warning

    if bull_stage >= bear_stage and bull_stage > 0:
        label = STAGE_LABELS[bull_stage]
        if bull_stage == 4:
            label += _price_action_tag(price_action, "BUY")
        return {
            "direction": "BUY",
            "stage": bull_stage,
            "label": label,
            "checks": bull_checks,
        }

    if bear_stage > 0:
        label = SELL_STAGE_LABELS[bear_stage]
        if bear_stage == 4:
            label += _price_action_tag(price_action, "SELL")
        return {
            "direction": "SELL",
            "stage": bear_stage,
            "label": label,
            "checks": bear_checks,
        }

    return {
        "direction": "NONE",
        "stage": 0,
        "label": "⚪ No Signal",
        "checks": [],
    }
