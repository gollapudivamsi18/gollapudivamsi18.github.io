# Runbook: Orders API p95 latency high

**Alert:** `OrdersLatencyP95High` (p95 above 500 ms for 10 minutes) · **Severity:** ticket

Latency alone does not page here. It becomes a page only if it starts causing errors
(timeouts show up as 5xx and trigger the burn-rate alerts).

1. Check whether traffic increased (requests per second panel). If yes, check HPA:
   `kubectl get hpa orders` — is it at max replicas?
2. Check CPU throttling and memory on the pods. Throttling often shows as p95/p99 growth
   while p50 stays flat.
3. Check the slowest dependency (database, downstream API). Compare p50 vs p95: a flat p50
   with a rising p95 points to a subset of slow calls, not a general slowdown.
4. If a recent release changed query patterns or added synchronous calls, roll back.
5. Raise the ticket's priority if p95 stays above 500 ms for more than 4 hours.
