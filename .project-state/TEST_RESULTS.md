# Test results

## 13 Nov 2026 — portfolio-v2 (local, before push)
| Check | Result |
| --- | --- |
| Existing demo Python tests (4 suites) | pass |
| sre-observability: `slo` (7) + `app` (4) | pass |
| github-actions-devsecops: app tests (8, incl. real HTTP) | pass |
| server-ops-toolkit: Linux script tests (7) | pass |
| Assistant engine + knowledge base (`node tests/assistant.test.js`, 8 groups) | pass |
| Responsive check, 3 pages x 320/375/390/768/1024/1440/1920 px: no horizontal overflow | pass (21/21) |
| Assistant in browser at all 7 widths: answers a question and a follow-up; no JS errors | pass |
| View-only checks (no download links, no resume files, no phone/email on resume page) | pass |
| Secret / client-name / phone scan of all files | clean |

## Not run here (needs CI or real infrastructure)
- ShellCheck, PSScriptAnalyzer, Pester, promtool, amtool, Trivy, Gitleaks, Ruff, Bandit, pip-audit:
  run in GitHub Actions once `ci/workflows/` is copied into `.github/workflows/`.
- Docker Compose stack, real AKS/Azure deployments: not run (no registry access / no subscription).
- Voice input and spoken replies: browser feature; checked for graceful fallback only (headless browser has no microphone).

## 13 Nov 2026 — baseline (before changes)
- Python unit tests, all four existing demos: pass (local).
- CI `Validate demos` on c9c35e2: pass (GitHub Actions).
