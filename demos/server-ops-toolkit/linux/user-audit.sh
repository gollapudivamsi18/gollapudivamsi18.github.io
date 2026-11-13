#!/usr/bin/env bash
# user-audit.sh - list interactive users, sudo rights and accounts without passwords.
# Independent portfolio demo. Read-only. Needs root to read /etc/shadow;
# without root that column shows "n/a".
#
# Usage: user-audit.sh
# Paths can be overridden for testing: PASSWD_FILE, SHADOW_FILE, GROUP_FILE.
set -euo pipefail

PASSWD_FILE="${PASSWD_FILE:-/etc/passwd}"
SHADOW_FILE="${SHADOW_FILE:-/etc/shadow}"
GROUP_FILE="${GROUP_FILE:-/etc/group}"
UID_MIN=$(awk '/^UID_MIN/ {print $2}' /etc/login.defs 2>/dev/null || true)
UID_MIN=${UID_MIN:-1000}

sudo_members=$(awk -F: '$1=="sudo" || $1=="wheel" {print $4}' "$GROUP_FILE" | paste -sd, -)

printf '%-16s %-6s %-20s %-6s %s\n' USER UID SHELL SUDO PASSWORD
awk -F: -v min="$UID_MIN" '($3 >= min && $3 != 65534) || $3 == 0 {print $1, $3, $7}' "$PASSWD_FILE" |
while read -r user uid shell; do
  case "$shell" in */nologin|*/false) continue ;; esac
  sudo="no"
  [[ ",$sudo_members," == *",$user,"* ]] && sudo="yes"
  [[ "$uid" == 0 ]] && sudo="root"
  if [[ -r "$SHADOW_FILE" ]]; then
    hash=$(awk -F: -v u="$user" '$1==u {print $2}' "$SHADOW_FILE")
    case "$hash" in
      "") pw="EMPTY (fix now)" ;;
      '!'*|'*'*) pw="locked" ;;
      *) pw="set" ;;
    esac
  else
    pw="n/a"
  fi
  printf '%-16s %-6s %-20s %-6s %s\n' "$user" "$uid" "$shell" "$sudo" "$pw"
done
