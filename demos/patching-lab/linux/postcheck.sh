#!/usr/bin/env bash
# Post-patch checks: compare with the pre-check snapshot. Independent portfolio demo.
# Usage: sudo ./postcheck.sh [output_dir]
set -euo pipefail

OUT_DIR="${1:-/var/tmp/patchlab}"
HOST=$(hostname -s)
PRE="$OUT_DIR/pre-$HOST.env"
[[ -f "$PRE" ]] || { echo "No pre-check snapshot at $PRE"; exit 2; }

get() { grep "^$1=" "$PRE" | cut -d= -f2-; }
status=0

pre_kernel=$(get kernel)
now_kernel=$(uname -r)
echo "Kernel: $pre_kernel -> $now_kernel"

failed_now=$( (systemctl --failed --no-legend 2>/dev/null || true) | wc -l)
if (( failed_now > $(get failed_units) )); then
  echo "FAIL: new failed systemd units:"; systemctl --failed --no-legend; status=1
fi

IFS=',' read -r -a services <<< "$(get running_services)"
for svc in "${services[@]}"; do
  [[ -z "$svc" ]] && continue
  if ! systemctl is-active --quiet "$svc"; then
    echo "FAIL: $svc was running before patching and is not running now"; status=1
  fi
done

IFS=',' read -r -a ports <<< "$(get listening_ports)"
now_ports=",$( (ss -Hltn 2>/dev/null || true) | awk '{print $4}' | sed 's/.*://' | sort -un | tr '\n' ','),"
for p in "${ports[@]}"; do
  [[ -z "$p" ]] && continue
  if [[ "$now_ports" != *",$p,"* ]]; then
    echo "FAIL: port $p was listening before patching and is not now"; status=1
  fi
done

result=$([[ $status -eq 0 ]] && echo compliant || echo needs-attention)
echo "$HOST,$(date -u +%F),$(get os),$pre_kernel,$now_kernel,$result" | tee -a "$OUT_DIR/results.csv"
exit "$status"
