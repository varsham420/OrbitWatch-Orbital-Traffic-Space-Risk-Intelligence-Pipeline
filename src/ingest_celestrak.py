import logging
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

URL = "https://celestrak.org/NORAD/elements/gp.php"
BRONZE_DIR = Path("data/bronze/celestrak")
GROUPS = ["stations"]  # more groups can be added later
MIN_HOURS_BETWEEN_FETCHES = 2
MAX_RETRIES = 3
REQUIRED_FIELDS = {"NORAD_CAT_ID", "OBJECT_NAME", "EPOCH"}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("ingest_celestrak")


def last_fetch_time(group):
    """Newest fetch time for this group, read from the Bronze filenames."""
    newest = None
    for f in BRONZE_DIR.glob(f"{group}_*.json"):
        stamp = f.stem.split("_")[-1]
        try:
            t = datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if newest is None or t > newest:
            newest = t
    return newest


def fetched_recently(group):
    last = last_fetch_time(group)
    if last is None:
        return False
    age = datetime.now(timezone.utc) - last
    return age < timedelta(hours=MIN_HOURS_BETWEEN_FETCHES)


def fetch(group):
    """Download one group, retrying with increasing waits."""
    params = {"GROUP": group, "FORMAT": "json"}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(URL, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as err:
            log.warning("Attempt %d/%d failed for %s: %s", attempt, MAX_RETRIES, group, err)
            if attempt == MAX_RETRIES:
                raise
            time.sleep(2 ** attempt)


def validate(records):
    if not isinstance(records, list) or not records:
        raise ValueError("Response is not a non-empty list")
    for i, rec in enumerate(records):
        missing = REQUIRED_FIELDS - rec.keys()
        if missing:
            raise ValueError(f"Record {i} is missing fields: {sorted(missing)}")


def ingest_group(group):
    if fetched_recently(group):
        log.info("Skipping %s: fetched within the last %d hours", group, MIN_HOURS_BETWEEN_FETCHES)
        return
    response = fetch(group)
    records = response.json()
    validate(records)

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = BRONZE_DIR / f"{group}_{stamp}.json"
    out_file.write_bytes(response.content)  # raw, untouched
    log.info("Saved %d records for %s to %s", len(records), group, out_file)


def main():
    failures = 0
    for group in GROUPS:
        try:
            ingest_group(group)
        except Exception as err:
            failures += 1
            log.error("Group %s failed: %s", group, err)
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()