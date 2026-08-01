from core.response import success
from strategies.forex_indicators import get_forex_indicators
from strategies.forex_stage_engine import evaluate_forex_stage


def forex_signal(symbol, timeframe="D"):
    result = get_forex_indicators(symbol, timeframe)

    if not result["success"]:
        return result

    data = result["data"]
    stage_info = evaluate_forex_stage(data)

    data["stage"] = stage_info["stage"]
    data["stage_label"] = stage_info["label"]
    data["direction"] = stage_info["direction"]
    data["checks"] = stage_info["checks"]

    return success(f"Signal for {data['symbol']}", data)
