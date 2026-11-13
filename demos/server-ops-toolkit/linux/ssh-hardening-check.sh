#!/usr/bin/env bash
# ssh-hardening-check.sh - audit sshd settings against a small baseline.
# Independent portfolio demo. Read-only: it reports, it never edits sshd_config.
#
# Usage: ssh-hardening-check.sh [path/to/sshd_config]
# Prefers `sshd -T` (effective config, includes Include files) when run as root;
# otherwise parses the given file. Exit 1 if any check fails.
set -euo pipefail

CONFIG="${1:-/etc/ssh/sshd_config}"

effective_config() {
  if [[ $EUID -eq 0 ]] && command -v sshd >/dev/null && [[ "$CONFIG" == /etc/ssh/sshd_config ]]; then
    sshd -T 2>/dev/null
  else
    # First occurrence wins in sshd_config, so keep only the first value per key.
    grep -Ev '^\s*(#|$)' "$CONFIG" | awk '{ k=tolower($1); if (!(k in seen)) { seen[k]=1; $1=""; sub(/^ /,""); print k, $0 } }'
  fi
}

declare -A cfg
while read -r key value; do
  cfg["$key"]="$value"
done < <(effective_config)

fails=0
check() {             # check <key> <expected regex> <default if unset> <why>
  local key=$1 want=$2 default=$3 why=$4
  local got="${cfg[$key]:-$default}"
  if [[ "${got,,}" =~ ^($want)$ ]]; then
    printf 'PASS  %-24s %-18s\n' "$key" "$got"
  else
    printf 'FAIL  %-24s %-18s want: %s  (%s)\n' "$key" "$got" "$want" "$why"
    fails=$((fails + 1))
  fi
}

echo "Checking $CONFIG"
check permitrootlogin        'no|prohibit-password' 'prohibit-password' 'no password logins as root'
check passwordauthentication 'no'                   'yes'               'keys only'
check pubkeyauthentication   'yes'                  'yes'               'keys only'
check permitemptypasswords   'no'                   'no'                'never'
check x11forwarding          'no'                   'no'                'not needed on servers'
check maxauthtries           '[1-4]'                '6'                 'slow down brute force'
check clientaliveinterval    '[1-9][0-9]*'          '0'                 'drop dead sessions'

if (( fails )); then
  echo "$fails check(s) failed."
  exit 1
fi
echo "All checks passed."
