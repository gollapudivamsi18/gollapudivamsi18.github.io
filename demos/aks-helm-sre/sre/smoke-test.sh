#!/usr/bin/env bash
# Smoke test for the Clinic Slots API. Usage: ./smoke-test.sh http://localhost:8080
set -euo pipefail

BASE_URL="${1:-http://localhost:8080}"
fail=0

check() {
  local path="$1" expect="$2"
  local code
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 5 "${BASE_URL}${path}" || echo "000")
  if [[ "$code" == "$expect" ]]; then
    echo "PASS ${path} -> ${code}"
  else
    echo "FAIL ${path} -> ${code} (expected ${expect})"
    fail=1
  fi
}

check /healthz 200
check /api/slots 200
check /metrics 200
exit "$fail"
