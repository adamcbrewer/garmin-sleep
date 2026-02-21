import json
import logging
import os
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from garminconnect import Garmin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
SLEEP_DIR = DATA_DIR / "sleep"
TOKEN_DIR = DATA_DIR / ".garminconnect"
BACKFILL_DAYS = int(os.getenv("BACKFILL_DAYS", "180"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "1.0"))
MAX_RETRIES = 3


def authenticate() -> Garmin:
    email = os.environ["GARMIN_EMAIL"]
    password = os.environ["GARMIN_PASSWORD"]

    client = Garmin(email, password)
    token_dir = str(TOKEN_DIR)

    try:
        client.login(token_dir)
        log.info("Authenticated using saved tokens")
    except Exception:
        log.info("Saved tokens invalid or missing, logging in with credentials")
        client.login()
        client.garth.dump(token_dir)
        log.info("Tokens saved to %s", token_dir)

    return client


def fetch_sleep(client: Garmin, target_date: date) -> dict | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            data = client.get_sleep_data(target_date.isoformat())
            return data
        except Exception as e:
            wait = 2**attempt
            log.warning(
                "Attempt %d/%d failed for %s: %s — retrying in %ds",
                attempt, MAX_RETRIES, target_date, e, wait,
            )
            time.sleep(wait)

    log.error("Failed to fetch sleep data for %s after %d attempts", target_date, MAX_RETRIES)
    return None


def main():
    log.info("Starting Garmin sleep data extraction")
    log.info("Backfill: %d days | Delay: %.1fs", BACKFILL_DAYS, REQUEST_DELAY)

    SLEEP_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)

    client = authenticate()

    today = date.today()
    fetched = 0
    skipped = 0
    failed = 0

    for days_ago in range(BACKFILL_DAYS):
        target = today - timedelta(days=days_ago)
        out_file = SLEEP_DIR / f"{target.isoformat()}.json"

        if out_file.exists():
            skipped += 1
            continue

        data = fetch_sleep(client, target)
        if data is None:
            failed += 1
            continue

        out_file.write_text(json.dumps(data, indent=2))
        fetched += 1
        log.info("Saved %s", out_file.name)

        time.sleep(REQUEST_DELAY)

    log.info(
        "Done — fetched: %d, skipped (existing): %d, failed: %d",
        fetched, skipped, failed,
    )

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
