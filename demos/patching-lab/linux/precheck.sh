#!/usr/bin/env bash
# Pre-patch checks for RHEL/Ubuntu lab servers. Independent portfolio demo.
# Usage: sudo ./precheck.sh [output_dir]
# Writes a key=value snapshot that postcheck.sh compares against.
set -euo pipefail

OUT_DIR="${1:-/var/tmp/patchlab}"
mkdir -p "$OUT_DIR"
SNAP="$OUT_DIR/pre-$(hostname -s).env"
status=0

root_free_mb=$(df -Pm / | awk 'NR==2 {print $4}')
boot_free_mb=$(df -Pm /boot 2>/dev/null | awk 'NR==2 {print $4}')
boot_free_mb=${boot_free_mb:-$root_free_mb}

if command -v dnf >/dev/null 2>&1; then
  pkg_mgr=dnf
  pending=$(dnf -q check-update 2>/dev/null | grep -c '^[[:alnum:]]' || true)
elif command -v yum >/dev/null 2>&1; then
  pkg_mgr=yum
  pending=$(yum -q check-update 2>/dev/null | grep -c '^[[:alnum:]]' || true)
else
  pkg_mgr=apt
  pending=$(apt list --upgradable 2>/dev/null | grep -c 'upgradable' || true)
fi

{
  echo "host=$(hostname -s)"
  echo "taken_at=$(date -u +%FT%TZ)"
  echo "kernel=$(uname -r)"
  # shellcheck source=/dev/null
  echo "os=$(. /etc/os-release && echo "$PRETTY_NAME")"
  echo "pkg_mgr=$pkg_mgr"
  echo "pending_updates=$pending"
  echo "root_free_mb=$root_free_mb"
  echo "boot_free_mb=$boot_free_mb"
  echo "failed_units=$(systemctl --failed --no-legend 2>/dev/null | wc -l)"
  echo "running_services=$(systemctl list-units --type=service --state=running --no-legend 2>/dev/null | awk '{print $1}' | sort | tr '\n' ',')"
  echo "listening_ports=$(ss -Hltn 2>/dev/null | awk '{print $4}' | sed 's/.*://' | sort -un | tr '\n' ',')"
} > "$SNAP"

echo "Snapshot written to $SNAP"

if (( root_free_mb < 2048 )); then echo "FAIL: less than 2 GB free on /"; status=1; fi
if (( boot_free_mb < 200 )); then echo "FAIL: less than 200 MB free on /boot"; status=1; fi
if grep -q '^failed_units=[1-9]' "$SNAP"; then
  echo "WARN: failed systemd units exist before patching (record them, do not block)"
fi
echo "Pending updates: $pending"
exit "$status"
