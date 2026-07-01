import os
import json
import logging
from dotenv import load_dotenv
from odds_api import fetch_all_odds, find_arbitrage_from_api, SPORT_KEYS
from telegram_bot import send_alert, mark_gone

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
TOTAL_BUDGET = 100
STATE_FILE = "state.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def opportunity_key(opp):
    return f"{opp['away_team']}|{opp['home_team']}|{opp['league']}|{opp['market']}"


def poll():
    logging.info("Polling odds API...")
    data = fetch_all_odds(ODDS_API_KEY)
    logging.info(f"Fetched {len(data)} games across {len(SPORT_KEYS)} sports.")

    current_opps = find_arbitrage_from_api(data, TOTAL_BUDGET)
    current_keys = {opportunity_key(o): o for o in current_opps}

    state = load_state()

    # Mark gone opportunities
    for key, entry in list(state.items()):
        if key not in current_keys:
            logging.info(f"Gone: {key}")
            mark_gone(entry["message_id"], entry["text"])
            del state[key]

    # Send alerts for new opportunities
    for key, opp in current_keys.items():
        if key not in state:
            margin = round((1 - opp["total_inverse_odds"]) * 100, 2)
            logging.info(f"New opportunity: {key} — {margin}% margin")
            message_id, text = send_alert(opp, TOTAL_BUDGET)
            if message_id:
                state[key] = {"message_id": message_id, "text": text}
        else:
            logging.info(f"Still active: {key}")

    save_state(state)
    logging.info(f"Active opportunities tracked: {len(state)}")


if __name__ == "__main__":
    poll()
