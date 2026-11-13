#!/usr/bin/env bash
# health-check.sh - read-only health report for a RHEL/Ubuntu server.
# Independent portfolio demo. Makes no changes to the system.
#
# Usage: health-check.sh [--json] [--disk-warn 80] [--disk-crit 90] [--mem-warn 90] [--load-warn 1.5]
# Exit codes: 0 OK, 1 WARNING, 2 CRITICAL (Nagios-style, so it can feed a monitor).
#
# Paths can be overridden for testing: PROC_ROOT (default /proc).
set -euo pipefail

PROC_ROOT="${PROC_ROOT:-/proc}"
DISK_WARN=80; DISK_CRIT=90; MEM_WARN=90; LOAD_WARN=1.5; JSON=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON=1 ;;
    --disk-warn) DISK_WARN="$2"; shift ;;
    --disk-crit) DISK_CRIT="$2"; shift ;;
    --mem-warn) MEM_WARN="$2"; shift ;;
    --load-warn) LOAD_WARN="$2"; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 64 ;;
  esac
  shift
done

status=0                 # worst status seen
checks=()                # "name|state|detail" entries

record() {               # record <name> <OK|WARNING|CRITICAL> <detail>
  checks+=("$1|$2|$3")
  case "$2" in
    CRITICAL) status=2 ;;
    WARNING) [[ $status -lt 1 ]] && status=1 ;;
  esac
  return 0
}

# --- CPU load relative to core count -------------------------------------
cores=$(grep -c '^processor' "$PROC_ROOT/cpuinfo" || echo 1)
read -r load1 _ < "$PROC_ROOT/loadavg"
per_core=$(awk -v l="$load1" -v c="$cores" 'BEGIN { printf "%.2f", l / c }')
if awk -v p="$per_core" -v w="$LOAD_WARN" 'BEGIN { exit !(p > w) }'; then
  record cpu_load WARNING "load1=$load1 on $cores cores (${per_core}/core > $LOAD_WARN)"
else
  record cpu_load OK "load1=$load1 on $cores cores (${per_core}/core)"
fi

# --- Memory (MemAvailable is the right number, not MemFree) --------------
mem_total=$(awk '/^MemTotal:/ {print $2}' "$PROC_ROOT/meminfo")
mem_avail=$(awk '/^MemAvailable:/ {print $2}' "$PROC_ROOT/meminfo")
mem_used_pct=$(( (mem_total - mem_avail) * 100 / mem_total ))
if (( mem_used_pct >= MEM_WARN )); then
  record memory WARNING "${mem_used_pct}% used"
else
  record memory OK "${mem_used_pct}% used"
fi

# --- Disk usage per real filesystem ---------------------------------------
while read -r use mount; do
  pct=${use%\%}
  if (( pct >= DISK_CRIT )); then
    record "disk:$mount" CRITICAL "${pct}% used"
  elif (( pct >= DISK_WARN )); then
    record "disk:$mount" WARNING "${pct}% used"
  else
    record "disk:$mount" OK "${pct}% used"
  fi
done < <(df -P -x tmpfs -x devtmpfs -x overlay -x squashfs 2>/dev/null | awk 'NR>1 {print $5, $6}')

# --- Failed systemd units (skipped where systemd is not PID 1) ------------
if [[ -d /run/systemd/system ]] && command -v systemctl >/dev/null; then
  failed=$(systemctl --failed --no-legend --plain 2>/dev/null | awk '{print $1}' | paste -sd, -)
  if [[ -n "$failed" ]]; then
    record systemd WARNING "failed units: $failed"
  else
    record systemd OK "no failed units"
  fi
else
  record systemd OK "systemd not running here; check skipped"
fi

# --- Output -----------------------------------------------------------------
names=(OK WARNING CRITICAL)
if (( JSON )); then
  printf '{"host":"%s","status":"%s","checks":[' "$(hostname)" "${names[$status]}"
  sep=""
  for c in "${checks[@]}"; do
    IFS='|' read -r n s d <<< "$c"
    d=${d//\"/\\\"}
    printf '%s{"name":"%s","state":"%s","detail":"%s"}' "$sep" "$n" "$s" "$d"
    sep=","
  done
  printf ']}\n'
else
  printf 'Health check on %s: %s\n' "$(hostname)" "${names[$status]}"
  for c in "${checks[@]}"; do
    IFS='|' read -r n s d <<< "$c"
    printf '  %-9s %-22s %s\n' "$s" "$n" "$d"
  done
fi
exit "$status"
