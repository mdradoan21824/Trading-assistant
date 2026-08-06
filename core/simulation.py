from datetime import datetime
from zoneinfo import ZoneInfo

from core.response import success
from storage.simulation import get_simulation_state, save_simulation_state, POSITION_SIZE_PCT


def _find_open_position(state, symbol):
    for pos in state["open_positions"]:
        if pos["symbol"] == symbol:
            return pos
    return None


def process_signal(symbol, direction, price):
    state = get_simulation_state()
    now = datetime.now(ZoneInfo("Asia/Dubai")).strftime("%Y-%m-%d")

    existing = _find_open_position(state, symbol)

    if direction == "BUY":
        if existing:
            return

        invest_amount = state["balance"] * POSITION_SIZE_PCT

        if invest_amount <= 0 or invest_amount > state["balance"]:
            return

        quantity = invest_amount / price

        state["balance"] -= invest_amount
        state["open_positions"].append({
            "symbol": symbol,
            "entry_price": round(price, 2),
            "quantity": round(quantity, 6),
            "entry_date": now,
        })

        save_simulation_state(state)
        return

    if direction == "SELL":
        if not existing:
            return

        proceeds = existing["quantity"] * price
        profit = proceeds - (existing["quantity"] * existing["entry_price"])
        profit_pct = (price - existing["entry_price"]) / existing["entry_price"] * 100

        state["balance"] += proceeds
        state["open_positions"].remove(existing)
        state["closed_trades"].append({
            "symbol": symbol,
            "entry_price": existing["entry_price"],
            "exit_price": round(price, 2),
            "quantity": existing["quantity"],
            "profit": round(profit, 2),
            "profit_pct": round(profit_pct, 2),
            "entry_date": existing["entry_date"],
            "exit_date": now,
        })

        state["closed_trades"] = state["closed_trades"][-100:]

        save_simulation_state(state)
        return


def get_simulation_status():
    state = get_simulation_state()

    return success(
        "Simulation Status",
        {
            "balance": round(state["balance"], 2),
            "open_positions": state["open_positions"],
        },
    )


def get_simulation_history():
    state = get_simulation_state()
    trades = state["closed_trades"]

    if not trades:
        return success("Simulation History", {"has_data": False})

    wins = sum(1 for t in trades if t["profit"] > 0)
    total_profit = sum(t["profit"] for t in trades)
    win_rate = (wins / len(trades)) * 100

    return success(
        "Simulation History",
        {
            "has_data": True,
            "total_trades": len(trades),
            "wins": wins,
            "win_rate": round(win_rate, 1),
            "total_profit": round(total_profit, 2),
            "recent_trades": trades[-10:],
        },
    )
