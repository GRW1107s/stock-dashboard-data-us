# stock-dashboard-data-us

US screener snapshot archive for
[stock-dashboard-public](https://grw1107s.github.io/stock-dashboard-public/),
covering **1996-11-25 .. 2016-11-24** (US rows only). The main
repository keeps the snapshots from 2016-11-25 on; this repository
holds the older era so each repository stays within GitHub's size
guidance.

Files:

- `screener-archive/<date>.json` — one daily snapshot (columnar,
  same format as the main repository), `screener-archive/index.json`
  lists the dates.
- `scripts/backfill_us_old.py` — the backfill driver run by this
  repository's workflow; it fills up to 150 missing dates per run
  from a deep Yahoo price cache (`deep-series-us-*.json`, built once).
- Snapshots are reconstructed from today's universe and
  classifications with prices recomputed as of each date; earnings
  fields are empty, as in the main repository's backfill.

Served via GitHub Pages at
https://grw1107s.github.io/stock-dashboard-data-us/
