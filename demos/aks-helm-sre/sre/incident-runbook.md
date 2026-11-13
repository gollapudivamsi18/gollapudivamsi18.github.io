# Incident runbook: Clinic Slots API error-budget burn

> Independent portfolio demo. Fictional service, synthetic data.

**Alerts covered:** `ClinicSlotsFastBurn` (page), `ClinicSlotsSlowBurn` (ticket)
**SLO:** 99.5% of requests succeed over 28 days ([slo.yaml](slo.yaml))

## 1. Acknowledge (first 5 minutes)
1. Acknowledge the page and open an incident channel, e.g. `#inc-clinic-slots-<date>`.
2. Assign roles: incident lead, communications, scribe. For a small team, one person can hold two roles.
3. Post the first update: what is affected, when it started, next update time.

## 2. Triage (5-15 minutes)
| Check | Command / query | What to look for |
|---|---|---|
| Recent deployments | `helm history clinic-slots -n clinic-prod` | A release in the last 2 hours |
| Pod health | `kubectl get pods -n clinic-prod -o wide` | CrashLoopBackOff, Pending, restarts |
| Events | `kubectl get events -n clinic-prod --sort-by=.lastTimestamp` | OOMKilled, failed probes, scheduling |
| Error ratio | `clinic_slots:error_ratio:rate5m` in Grafana | Is it still rising? |
| Node pressure | `kubectl top nodes` | CPU or memory near limits |
| Logs (KQL) | `ContainerLogV2 \| where PodNamespace == "clinic-prod" \| where LogMessage has "error"` | Repeating error messages |

## 3. Mitigate (restore service first, investigate later)
- **Bad release:** `helm rollback clinic-slots <previous-revision> -n clinic-prod --wait`
- **Capacity:** `kubectl scale deploy/clinic-slots -n clinic-prod --replicas=6` (HPA will settle it later)
- **Bad node:** `kubectl cordon <node>` then `kubectl drain <node> --ignore-daemonsets --delete-emptydir-data`
- **Dependency outage:** confirm on the dependency's status page, switch to the degraded mode if available, and update stakeholders.

## 4. Verify
1. Run `bash sre/smoke-test.sh https://clinic.example.internal`.
2. Watch the 5-minute error ratio return below 0.5% for at least 15 minutes.
3. Post the resolution update with the time of recovery.

## 5. After the incident
- Hold a blameless review within 5 working days.
- Record timeline, impact (requests failed, error budget used), contributing factors and actions.
- Each action has an owner and a due date; track it on the team board.
