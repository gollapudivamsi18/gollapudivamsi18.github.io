"""Generate synthetic per-minute request counts for the SRE demo.

Deterministic (fixed seed) so tests and the README numbers stay stable.
Scenario: 3 days of normal traffic at ~0.1% errors, then an incident at
~25% errors that is still ongoing when the data ends (the last 40 minutes).

  python3 generate.py > sample-requests.csv
"""
import csv
import random
import sys
from datetime import datetime, timedelta, timezone

START = datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc)
MINUTES = 3 * 24 * 60
INCIDENT_START = MINUTES - 40   # incident begins 40 minutes before the end
INCIDENT_END = MINUTES          # not yet mitigated when the data ends


def rows(seed=42):
    rng = random.Random(seed)
    for m in range(MINUTES):
        ts = START + timedelta(minutes=m)
        # Daily traffic curve: busier during IST working hours.
        hour_ist = (ts.hour + 5) % 24
        base = 900 if 9 <= hour_ist < 19 else 350
        total = max(0, int(rng.gauss(base, base * 0.08)))
        if INCIDENT_START <= m < INCIDENT_END:
            rate = 0.25
        else:
            rate = 0.001
        errors = sum(1 for _ in range(total) if rng.random() < rate)
        yield ts.strftime("%Y-%m-%dT%H:%M:%SZ"), total, errors


def main():
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["timestamp", "total", "errors"])
    for r in rows():
        w.writerow(r)


if __name__ == "__main__":
    main()
