import json
from collections import Counter
from pathlib import Path

files = sorted(Path("data/bronze/celestrak").glob("stations_*.json"))
latest = files[-1]
records = json.loads(latest.read_text(encoding="utf-8"))

print("File:", latest.name)
print("Records:", len(records))

ids = [r["NORAD_CAT_ID"] for r in records]
print("Unique NORAD_CAT_ID:", len(set(ids)))

layouts = Counter(tuple(sorted(r.keys())) for r in records)
print("Distinct field layouts:", len(layouts))

nulls = {k: sum(1 for r in records if r.get(k) is None) for k in records[0]}
print("Fields containing nulls:", {k: v for k, v in nulls.items() if v})

print("\nObjects in this file:")
for r in records:
    print(r["NORAD_CAT_ID"], r["OBJECT_NAME"], r["EPOCH"][:10])