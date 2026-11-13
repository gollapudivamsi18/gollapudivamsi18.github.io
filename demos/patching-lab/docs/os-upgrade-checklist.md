# OS upgrade checklist (lab)

> Independent portfolio demo. Lab servers only.

## Windows Server in-place upgrade (e.g. 2016 -> 2022)
1. Confirm the upgrade path is supported and the application vendor supports the target version.
2. Run `Invoke-PreCheck.ps1`; at least 30 GB free on C:, no pending reboot.
3. Take a VM snapshot or full backup and test that it can be restored.
4. Remove or update agents that block upgrades (old antivirus, backup agents).
5. Mount the media and run `setup.exe /auto upgrade /dynamicupdate enable /eula accept`.
6. After the upgrade: run `Invoke-PostCheck.ps1`, check roles and features, activation, domain trust, and the application smoke test.
7. Keep the snapshot for 7 days, then remove it.

## RHEL major upgrade (e.g. 8 -> 9 with Leapp)
1. `dnf install leapp-upgrade` and update the system to the latest minor release.
2. Run `./precheck.sh`, then `leapp preupgrade` and fix every inhibitor in `/var/log/leapp/leapp-report.txt`.
3. Snapshot or back up, then `leapp upgrade` and reboot.
4. Run `./postcheck.sh`, confirm `cat /etc/redhat-release`, SELinux mode and application health.

## Ubuntu LTS upgrade (e.g. 20.04 -> 22.04)
1. Patch fully on the current release; run `./precheck.sh`.
2. Snapshot, then `do-release-upgrade` from a screen/tmux session.
3. Reboot, run `./postcheck.sh`, review `/var/log/dist-upgrade/`.

## Rollback
Restore the snapshot or backup taken in the steps above, then repeat the post-checks.
