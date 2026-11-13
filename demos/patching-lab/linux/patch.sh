#!/usr/bin/env bash
# Apply OS updates on a lab server. Independent portfolio demo.
# Usage: sudo ./patch.sh [--security-only] [--dry-run]
set -euo pipefail

SECURITY_ONLY=false
DRY_RUN=false
for arg in "$@"; do
  case "$arg" in
    --security-only) SECURITY_ONLY=true ;;
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown option: $arg" >&2; exit 2 ;;
  esac
done

run() {
  echo "+ $*"
  if [[ "$DRY_RUN" == false ]]; then "$@"; fi
}

if command -v dnf >/dev/null 2>&1 || command -v yum >/dev/null 2>&1; then
  PM=$(command -v dnf >/dev/null 2>&1 && echo dnf || echo yum)
  if [[ "$SECURITY_ONLY" == true ]]; then
    run "$PM" -y update --security
  else
    run "$PM" -y update
  fi
  needs_reboot=$( (needs-restarting -r >/dev/null 2>&1 && echo no) || echo yes )
else
  export DEBIAN_FRONTEND=noninteractive
  run apt-get update -q
  if [[ "$SECURITY_ONLY" == true ]]; then
    run unattended-upgrade -v
  else
    run apt-get -y -o Dpkg::Options::=--force-confold upgrade
  fi
  needs_reboot=$([[ -f /var/run/reboot-required ]] && echo yes || echo no)
fi

echo "Reboot required: $needs_reboot"
echo "Next: reboot in the agreed window, then run ./postcheck.sh"
