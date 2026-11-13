# Cutover checklist (per wave)

> Independent portfolio demo. Fictional servers and applications.

## T-5 days
- [ ] Wave scope frozen; change request approved; application owners confirmed for the cutover window.
- [ ] Replication healthy in Azure Migrate / ASR for every server in the wave (no critical health warnings).
- [ ] Test migration done into an isolated test VNet; owners signed off on the test results.
- [ ] Target VM sizes, disks, IPs, NSG rules and backup policy confirmed.
- [ ] DNS TTLs lowered to 300 seconds for the wave's records.
- [ ] Rollback runbook reviewed with the team ([rollback-runbook.md](rollback-runbook.md)).

## T-0 (cutover window)
| # | Step | Owner | Check |
|---|---|---|---|
| 1 | Announce start in the bridge and channel | Migration lead | Message posted |
| 2 | Stop application services on source servers | App owner | Services stopped, no active sessions |
| 3 | Take final backups / snapshots of source | Infra | Backup job succeeded |
| 4 | Final replication sync, then **Migrate** | Infra | Azure VMs running |
| 5 | Keep source VMs **powered off, not deleted** | Infra | Source state recorded |
| 6 | Update DNS records to Azure IPs | Network | `nslookup` returns new IP |
| 7 | Start services in dependency order (DB -> app -> web) | App owner | Health endpoints green |
| 8 | Post-migration checks (below) | Infra + App | All pass |
| 9 | Go / no-go decision at the agreed checkpoint | Migration lead | Decision logged |

## Post-migration checks
**Windows:** domain join and `nltest /sc_verify:<domain>`, services set to Automatic are running, Event Viewer has no new critical errors, SQL connectivity from app tier, file share access, time sync.
**Linux:** `systemctl --failed` is empty, `/etc/fstab` mounts present, `chronyc tracking` OK, application port listening (`ss -ltnp`), SELinux mode unchanged.
**Azure:** VM agent ready, Azure Backup protected, Azure Monitor agent reporting, NSG flow as expected, tags applied.
**Application:** owner smoke test passed, a test user completes the main journey.

## T+1 to T+14
- [ ] Hypercare: daily check with application owners.
- [ ] Restore DNS TTLs.
- [ ] After 14 clean days, approve decommissioning of source servers.
