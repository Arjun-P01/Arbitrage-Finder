import time
import logging
from datetime import datetime

from poll_once import poll

POLL_INTERVAL_SECONDS = 60 * 60  # 1 hour
ACTIVE_HOURS = (9, 23)  # 9am to 11pm local time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def is_active_hours():
    hour = datetime.now().hour
    return ACTIVE_HOURS[0] <= hour < ACTIVE_HOURS[1]


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
