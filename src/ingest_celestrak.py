import requests
from datetime import datetime, timezone
from pathlib import Path

URL = "https://celestrak.org/NORAD/elements/gp.php"
PARAMS = {"GROUP": "stations", "FORMAT": "json"}
BRONZE_DIR = Path("data/bronze/celestrak")


def main():
    response = requests.get(URL, params=PARAMS, timeout=30)
    response.raise_for_status()

    records = response.json()
    if not isinstance(records, list) or len(records) == 0:
        raise ValueError(f"Unexpected response: {response.text[:200]}")

    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = BRONZE_DIR / f"stations_{stamp}.json"
    out_file.write_bytes(response.content)

    print(f"Saved {len(records)} records to {out_file}")


if __name__ == "__main__":
    main()