# RCA example: orders API returned 5xx for 40 minutes

> **Fictional.** This write-up uses the synthetic data from `../data/generate.py`.
> It shows the format I use for blameless reviews; it describes no real system or employer.

| Field | Value |
| --- | --- |
| Date | 3 Nov 2026 (synthetic) |
| Duration | 23:20 – 00:00 UTC, 40 minutes of elevated errors |
| Impact | ~25% of `/api/orders` requests failed; about 3,500 failed requests |
| Error budget | 47% of the 30-day budget used by end of the data window (`error_budget.py`) |
| Detection | `OrdersErrorBudgetFastBurn` paged after the 2-minute `for` period |
| Severity | SEV-2 |

## Timeline (UTC)
- **23:20** — Release 1.8.0 rolled out; new connection-pool limit reduced from 50 to 5 by a typo in `values-prod.yaml`.
- **23:22** — Error ratio crosses 14.4x burn on both 5m and 1h windows; page fires.
- **23:26** — On-call acknowledges, sees errors start with the rollout in the dashboard annotations.
- **23:31** — Decision to roll back instead of patching forward.
- **23:38** — Rollback complete in staging validation; production rollback starts.
- **00:00** — Data window ends during recovery; error ratio falling.

## Root cause
A configuration value was changed in the production Helm values file without a matching change
in staging, so staging tests never exercised the lower pool size. Under production load,
requests queued for a connection and timed out.

## What went well
- Burn-rate alerting paged within 2 minutes; no alert noise from the slow-burn rule.
- The runbook's "deployment lines up → roll back first" rule avoided a long debugging session.

## What went wrong
- Production and staging values diverged without review.
- No canary step; 100% of traffic received the change at once.

## Actions
| Action | Owner | Due |
| --- | --- | --- |
| CI check that diffs prod vs staging values and requires approval for differences | Platform | +7 days |
| Add a 10% canary stage with automatic rollback on burn rate > 6x | Platform | +14 days |
| Add a connection-pool saturation metric and dashboard panel | Orders team | +14 days |
