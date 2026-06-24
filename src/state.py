import json
from pathlib import Path

STATE_FILE = Path("state.json")


def load_state():
    if not STATE_FILE.exists():
        return {}

    text = STATE_FILE.read_text().strip()
    if not text:
        return {}

    return json.loads(text)


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))