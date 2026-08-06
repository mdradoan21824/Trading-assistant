from storage.json_store import load, save

FILE = "storage/simulation.json"

STARTING_BALANCE = 100.0
POSITION_SIZE_PCT = 0.10


def _default_state():
    return {
        "balance": STARTING_BALANCE,
        "open_positions": [],
        "closed_trades": [],
    }


def get_simulation_state():
    return load(FILE, _default_state())


def save_simulation_state(state):
    save(FILE, state)


def reset_simulation():
    state = _default_state()
    save(FILE, state)
    return state
