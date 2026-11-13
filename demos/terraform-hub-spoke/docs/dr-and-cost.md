# Backup, disaster recovery and cost considerations

> Independent portfolio demo. Targets and figures are examples, not client values.

## Recovery targets (example)
| Tier | Example workload | RTO | RPO | Method |
|---|---|---|---|---|
| 1 | Portfolio valuation API | 4 hours | 15 minutes | Azure Site Recovery to `southindia` |
| 2 | Reporting VMs | 24 hours | 24 hours | Daily Azure Backup, geo-redundant vault, cross-region restore |
| 3 | Dev/test | Best effort | 24 hours | Daily backup, locally redundant |

## Backup design
- Daily VM backup at 01:00 IST, 14 daily, 12 weekly and 12 monthly recovery points (`backup.tf`).
- Soft delete kept on so that a deleted backup can be recovered for 14 days.
- Vault access through RBAC only; backup operators cannot delete vaults.

## DR design
- Set `enable_dr = true` to create the secondary resource group and ASR vault.
- Replicate tier-1 VMs with ASR; keep a matching spoke address space in the DR region so routes and NSG rules stay the same.
- Run a **test failover** twice a year into an isolated VNet and record the actual RTO/RPO.
- DR runbook outline: declare, fail over tier 1, update DNS, verify, communicate, fail back after root cause is fixed.

## Cost considerations
| Area | Lever used in this example |
|---|---|
| Log Analytics | 30-day retention and a 2 GB daily cap in dev (`log_daily_cap_gb`) |
| Backup storage | GeoRedundant only where cross-region restore is needed; LRS for dev |
| DR | ASR is off by default; you pay for replication only for tier-1 VMs |
| Networking | Spokes peer only with the hub; avoid unnecessary cross-region peering and egress |
| Firewall/gateway | Subnets are reserved, but the paid firewall and gateway are not created in this demo |
| Tagging | `cost_centre`, `owner` and `environment` tags for cost reports and budgets |
| Compute | Right-size from utilisation data, shut down non-prod at night, consider reserved instances for steady prod VMs |
