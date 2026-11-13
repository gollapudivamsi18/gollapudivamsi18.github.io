# Rollback runbook (per wave)

> Independent portfolio demo. Fictional servers and applications.

## Decision rule
Roll back if, at the go/no-go checkpoint, any **high-criticality** application fails its smoke test and cannot be fixed within 60 minutes, or if data integrity is in doubt. The migration lead makes the call and logs it.

## Steps
1. **Freeze:** announce rollback in the bridge; stop users from writing to the Azure copies (stop app services in Azure).
2. **Capture:** note any data written in Azure after cutover. If writes happened, the app owner decides how to replay them.
3. **DNS:** point records back to the source IPs. Confirm with `nslookup` from a client subnet.
4. **Power on source** servers in dependency order: database -> application -> web.
5. **Verify source:** services running, application smoke test passed, users can log in.
6. **Azure side:** shut down (do not delete) the migrated VMs so they can be examined; keep replication disabled until the root cause is known.
7. **Communicate:** send the rollback notice with the reason and the next steps.

## After rollback
- Root-cause review within 2 working days.
- Fix, re-test in the isolated test VNet, and plan the wave again.

## Rollback readiness checklist (before every cutover)
- [ ] Source servers will only be powered off, never deleted, during the window.
- [ ] Old DNS values recorded.
- [ ] Final source backups verified.
- [ ] Contact list for app owners and network team available.
