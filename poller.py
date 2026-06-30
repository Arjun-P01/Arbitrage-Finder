import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from odds_api import fetch_all_odds, find_arbitrage_from_api
from telegram_bot import send_alert

load_dotenv()

ODDS_API_KEY = os.getenv("ODDS_API_KEY")
TOTAL_BUDGET = 100
POLL_INTERVAL_SECONDS = 20 * 60  # 20 minutes
ACTIVE_HOURS = (9, 23)  # 9am to 11pm local time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

request_count = 0


def is_active_hours():
    hour = datetime.now().hour
    return ACTIVE_HOURS[0] <= hour < ACTIVE_HOURS[1]


def poll():
    global request_count
    logging.info("Polling odds API...")
    data = fetch_all_odds(ODDS_API_KEY)
    request_count += len(data)  # each sport key = 1 request
    logging.info(f"Requests used this session: {request_count}")

    opportunities = find_arbitrage_from_api(data, TOTAL_BUDGET)

    if opportunities:
        logging.info(f"Found {len(opportunities)} arbitrage opportunity(s) — sending alerts.")
        for opp in opportunities:
            send_alert(opp, TOTAL_BUDGET)
    else:
        logging.info("No arbitrage opportunities found.")


def run():
    logging.info("Poller started. Active hours: %d:00 – %d:00." % ACTIVE_HOURS)
    while True:
        if is_active_hours():
            poll()
        else:
            logging.info("Outside active hours, sleeping...")

        time.sleep(POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
