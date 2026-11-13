# Runbook: Orders API error-budget burn

**Alerts:** `OrdersErrorBudgetFastBurn`, `OrdersErrorBudgetSlowBurn`, `OrdersTargetDown`
**Severity:** page
**Service:** orders (fictional demo service)

## What the alert means
More than 0.5% of `/api/orders` requests are failing, at a rate that would spend
a meaningful share of the 30-day error budget:

| Alert | Condition | Budget spent if it continues |
| --- | --- | --- |
| Fast burn | 14.4x over 1h and 5m | 2% per hour |
| Slow burn | 6x over 6h and 30m | 5% per 6 hours |

## First 5 minutes
1. Acknowledge the page and post in the incident channel: "Investigating orders error-budget burn."
2. Open the Grafana dashboard **Orders service — SLO and health**. Check:
   - Is the error ratio still rising, flat, or falling?
   - Is it all requests or one status code?
   - Did latency change at the same time?
3. Check what changed in the last 2 hours: deployments, config changes, certificate renewals,
   upstream dependencies.

## Decide
- **A deployment lines up with the start of errors** → roll back first, investigate after.
  (Helm: `helm rollback orders <previous-revision>`; Azure Pipelines: re-run the last good release.)
- **Upstream dependency failing** → enable the fallback or degrade gracefully; contact the owning team.
- **Target down (`up == 0`)** → check pods (`kubectl get pods -l app=orders`), recent restarts,
  OOMKilled events, and readiness probe failures.
- **Cause unclear after 15 minutes** → escalate to the secondary on-call and open a bridge.

## Useful queries
```promql
# Error ratio by status code, last 15 minutes
sum by (code) (rate(http_requests_total{route="/api/orders"}[5m]))

# Remaining budget estimate over 30 days (needs 30 days of data)
1 - (
  sum(increase(http_requests_total{route="/api/orders",code=~"5.."}[30d]))
  / (sum(increase(http_requests_total{route="/api/orders"}[30d])) * 0.005)
)
```

## Close out
- Confirm the burn rate is back under 1x for 30 minutes before resolving.
- Record timeline, impact (failed requests, minutes affected) and budget consumed.
- Schedule a blameless review within 3 working days if more than 5% of budget was used.
  Template: [../incidents/rca-template.md](../incidents/rca-template.md).
