from core.command_router import execute
from core.commands import (
    execute_price,
    execute_watchlist,
    execute_market,
    execute_signal,
    execute_overview,
    execute_analyze,
    execute_recap,
    execute_forex_test,
    execute_forex_watchlist,
    execute_forex_overview,
    execute_simulation_status,
    execute_simulation_history,
)


def process_message(text, user=None):
    text = text.strip()

    if text.startswith("/"):
        text = text[1:]

    parts = text.split(maxsplit=2)

    command = parts[0].lower()

    if command == "price":
        if len(parts) < 2:
            return {
                "success": False,
                "message": "Usage: /price SYMBOL",
                "data": {},
            }

        return execute_price(parts[1])

    if command == "market":
        return execute_market()

    if command == "signal":
        if len(parts) < 2:
            return {
                "success": False,
                "message": "Usage: /signal SYMBOL [timeframe]",
                "data": {},
            }
        timeframe = parts[2] if len(parts) > 2 else None
        return execute_signal(parts[1], timeframe)

    if command == "forex":
        if len(parts) < 2:
            return {
                "success": False,
                "message": "Usage: /forex watchlist | /forex overview",
                "data": {},
            }

        subcommand = parts[1].lower()

        if subcommand == "overview":
            return execute_forex_overview()

        if subcommand == "watchlist":
            rest = parts[2] if len(parts) > 2 else "list"
            rest_parts = rest.split(maxsplit=1)
            action = rest_parts[0].lower()
            symbol = rest_parts[1] if len(rest_parts) > 1 else None
            return execute_forex_watchlist(action, symbol)

        return {
            "success": False,
            "message": "Usage: /forex watchlist | /forex overview",
            "data": {},
        }

    if command == "simulation":
        subcommand = parts[1].lower() if len(parts) > 1 else "status"

        if subcommand == "history":
            return execute_simulation_history()

        return execute_simulation_status()

    if command == "overview":
        return execute_overview()

    if command == "analyze":
        if len(parts) < 2:
            return {
                "success": False,
                "message": "Usage: /analyze SYMBOL",
                "data": {},
            }
        return execute_analyze(parts[1])

    if command == "recap":
        return execute_recap()

    if command == "forextest":
        if len(parts) < 2:
            return {
                "success": False,
                "message": "Usage: /forextest SYMBOL [timeframe]",
                "data": {},
            }
        timeframe = parts[2] if len(parts) > 2 else "D"
        return execute_forex_test(parts[1], timeframe)

    if command == "watchlist":
        if len(parts) == 1:
            return execute_watchlist("list")

        action = parts[1].lower()
        symbol = parts[2] if len(parts) > 2 else None

        return execute_watchlist(action, symbol)

    return execute(command, user=user)
