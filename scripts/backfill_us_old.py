"""Backfill US screener snapshots for 1996-11-25 .. 2016-11-24.

Runs in the stock-dashboard-data-us repository (its own workflow).
The main repo (stock-dashboard-public) keeps US snapshots from
2016-11-25 on; this repo holds the older era so each repository
stays within GitHub's size guidance. Snapshots are US-only (the jp
list is empty) and are built exactly like the main repo's backfill:
today's universe and classifications, prices recomputed as of each
date from a deep Yahoo cache (deep-series-us-*.json shards at the
repo root, ~11,300 days, eight files so each stays well under
GitHub's 100 MB file limit).

The current US rows (universe, classifications, market cap) are read
from the main site's latest published snapshot.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

import backfill_snapshots as bf
from history_store import write_snapshot_rows

OLD_START = os.environ.get("BACKFILL_OLD_START", "1996-11-25")
OLD_END = os.environ.get("BACKFILL_OLD_END", "2016-11-25")  # exclusive
MAX_DATES = int(os.environ.get("BACKFILL_OLD_MAX", "150"))
MAIN_SITE = "https://grw1107s.github.io/stock-dashboard-public"
SHARDS = 8

bf.DEEP_DAYS = {"jp": 1500, "us": 11300}
bf.DEEP_CACHE_FILES = {
    "jp": ["deep-series-jp.json"],
    "us": [f"deep-series-us-{i}.json" for i in range(1, SHARDS + 1)],
}


def fetch_json(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (backfill-us-old)"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def latest_us_rows():
    idx = fetch_json(f"{MAIN_SITE}/screener-archive/index.json")
    day = idx["dates"][0]
    snap = fetch_json(f"{MAIN_SITE}/screener-archive/{day}.json")
    fields = snap["fields"]
    return [dict(zip(fields, vals)) for vals in snap.get("us") or []]


def main():
    root = Path(__file__).resolve().parent.parent
    archive = root / "screener-archive"
    archive.mkdir(exist_ok=True)
    rows_now = latest_us_rows()
    tickers = [r["ticker"] for r in rows_now if r.get("ticker")]
    cache = bf._load_or_build_cache(root, "us", tickers)
    bench_series = bf._merge_series(cache.get("^GSPC"), None)
    bench = bf._bench_from_series(bench_series)
    file_dates = {p.stem for p in archive.glob("*.json")
                  if len(p.stem) == 10 and p.stem[4] == "-" and p.stem[7] == "-"}
    calendar = [r[0] for r in bench["series"] if OLD_START <= r[0] < OLD_END]
    targets = [d for d in calendar if d not in file_dates][-MAX_DATES:]
    if not targets:
        print("BACKFILL_OLD none", flush=True)
        return 0
    merged = {t: bf._merge_series(rows, None) for t, rows in cache.items()}
    built = bf._build_market(rows_now, merged, bench, "us", targets)
    for d in targets:
        write_snapshot_rows(root, d, [], built[d])
        print("BACKFILL_OLD_SNAPSHOT", d, len(built[d]), flush=True)
    print("BACKFILL_OLD_DONE", len(targets), flush=True)
    return len(targets)


if __name__ == "__main__":
    main()
