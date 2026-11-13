"""Error-budget and burn-rate calculator for the SRE observability demo.

Independent portfolio demo. Works on synthetic request counts (see
../data/sample-requests.csv); the numbers are not from any real system.

Usage
  python3 error_budget.py ../data/sample-requests.csv --slo 99.5
  python3 error_budget.py ../data/sample-requests.csv --slo 99.5 --json

The CSV has one row per minute: timestamp (ISO 8601, UTC), total, errors.

Alerting follows the multi-window, multi-burn-rate pattern from the Google SRE
Workbook: page when both a long and a short window burn fast, open a ticket
when burn is slower but sustained. Thresholds below assume a 30-day window.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# (severity, long window, short window, burn-rate threshold)
# 14.4x for 1h spends 2% of a 30-day budget; 6x for 6h spends 5%;
# 1x for 3 days spends 10%.
ALERT_POLICIES = [
    ("page", timedelta(hours=1), timedelta(minutes=5), 14.4),
    ("page", timedelta(hours=6), timedelta(minutes=30), 6.0),
    ("ticket", timedelta(days=3), timedelta(hours=6), 1.0),
]


@dataclass
class Sample:
    ts: datetime
    total: int
    errors: int


@dataclass
class Report:
    slo_percent: float
    window_start: str
    window_end: str
    total_requests: int
    failed_requests: int
    availability_percent: float
    budget_requests: float
    budget_used_percent: float
    budget_remaining_percent: float
    alerts: list


def load_samples(path: str) -> list[Sample]:
    samples = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            total = int(row["total"])
            errors = int(row["errors"])
            if total < 0 or errors < 0 or errors > total:
                raise ValueError(f"bad row at {row['timestamp']}: total={total} errors={errors}")
            ts = datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00"))
            samples.append(Sample(ts, total, errors))
    samples.sort(key=lambda s: s.ts)
    if not samples:
        raise ValueError("no samples in file")
    return samples


def error_ratio(samples: list[Sample]) -> float:
    total = sum(s.total for s in samples)
    return 0.0 if total == 0 else sum(s.errors for s in samples) / total


def burn_rate(samples: list[Sample], end: datetime, window: timedelta, slo: float) -> float:
    """Burn rate = observed error ratio / allowed error ratio over the window."""
    allowed = 1 - slo / 100
    in_window = [s for s in samples if end - window < s.ts <= end]
    return error_ratio(in_window) / allowed if allowed > 0 else float("inf")


def evaluate_alerts(samples: list[Sample], slo: float) -> list[dict]:
    end = samples[-1].ts
    fired = []
    for severity, long_w, short_w, threshold in ALERT_POLICIES:
        long_rate = burn_rate(samples, end, long_w, slo)
        short_rate = burn_rate(samples, end, short_w, slo)
        if long_rate >= threshold and short_rate >= threshold:
            fired.append({
                "severity": severity,
                "long_window": str(long_w),
                "short_window": str(short_w),
                "threshold": threshold,
                "long_burn_rate": round(long_rate, 2),
                "short_burn_rate": round(short_rate, 2),
            })
    return fired


def build_report(samples: list[Sample], slo: float) -> Report:
    if not 0 < slo < 100:
        raise ValueError("SLO must be between 0 and 100 (exclusive)")
    total = sum(s.total for s in samples)
    failed = sum(s.errors for s in samples)
    budget = total * (1 - slo / 100)
    used = 100.0 if budget == 0 and failed else (failed / budget * 100 if budget else 0.0)
    return Report(
        slo_percent=slo,
        window_start=samples[0].ts.isoformat(),
        window_end=samples[-1].ts.isoformat(),
        total_requests=total,
        failed_requests=failed,
        availability_percent=round(100 * (1 - failed / total), 4) if total else 100.0,
        budget_requests=round(budget, 1),
        budget_used_percent=round(used, 1),
        budget_remaining_percent=round(100 - used, 1),
        alerts=evaluate_alerts(samples, slo),
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv_path")
    parser.add_argument("--slo", type=float, default=99.5, help="availability SLO in percent")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args(argv)

    report = build_report(load_samples(args.csv_path), args.slo)
    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"SLO target:        {report.slo_percent}%")
        print(f"Window:            {report.window_start} -> {report.window_end}")
        print(f"Requests:          {report.total_requests} ({report.failed_requests} failed)")
        print(f"Availability:      {report.availability_percent}%")
        print(f"Error budget:      {report.budget_requests} failed requests allowed")
        print(f"Budget used:       {report.budget_used_percent}%  (remaining {report.budget_remaining_percent}%)")
        if report.alerts:
            for a in report.alerts:
                print(f"ALERT [{a['severity']}] burn {a['long_burn_rate']}x over {a['long_window']} "
                      f"and {a['short_burn_rate']}x over {a['short_window']} (threshold {a['threshold']}x)")
        else:
            print("Alerts:            none firing")
    # Exit 2 when a page-level alert fires so the script can gate a pipeline.
    return 2 if any(a["severity"] == "page" for a in report.alerts) else 0


if __name__ == "__main__":
    sys.exit(main())
