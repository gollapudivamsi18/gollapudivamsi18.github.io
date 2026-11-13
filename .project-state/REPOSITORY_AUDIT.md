# Repository audit — 13 Nov 2026

GitHub account checked in the owner's browser session: **gollapudivamsi18**.
Repositories visible: **1** (`gollapudivamsi18.github.io`, public). No profile README
repository (`gollapudivamsi18/gollapudivamsi18`) exists yet.

## gollapudivamsi18.github.io — KEEP and IMPROVE

| Area | Finding |
| --- | --- |
| Hosting | GitHub Pages from `main` (branch deploy), `.nojekyll` present. Latest Pages build succeeded. |
| CI | `Validate demos` workflow: Python unit tests, YAML parse, helm lint/template, local smoke test, terraform fmt/validate, ShellCheck, PSScriptAnalyzer. Last run (c9c35e2) passed; 4 of 8 earlier runs failed and were fixed. |
| Site | Static `index.html` + `resume.html`, inline CSS/JS, no build step, no external scripts. Accessible basics (skip link, landmarks, focus styles). |
| Voice | One-way voice introduction (Web Speech API, en-IN). Not conversational. |
| Resume page | Accurate to the resume. Omits contact details and client names. Print disabled via CSS. No download links. |
| Secrets / client data | None found (grep for client names, password, token, secret). |
| Contact | README still publishes the email address while the resume page hides it. Owner to decide. |

### Demos inside the repository

| Demo | Status | Notes |
| --- | --- | --- |
| `demos/aks-helm-sre` | KEEP | Flask-free stdlib app with tests, Helm chart (probes, HPA, PDB), SLO + burn-rate rules, runbook, smoke test. Ingress not included. |
| `demos/banking-pipeline` | KEEP | Multi-stage Azure Pipelines YAML, deploy template, rollback and branch-policy docs, tested Python API. "Banking" label is an experience area, not client work — wording is already clear. |
| `demos/terraform-hub-spoke` | KEEP | Hub-and-spoke VNets, NSGs, backup, DR/cost doc; validated in CI. No remote-state backend block (documented only). |
| `demos/migration-plan` | KEEP | Inventory, dependency CSV, tested wave planner, cutover and rollback runbooks. |
| `demos/patching-lab` | KEEP | PowerShell + Bash pre/post checks, patch script with dry run, tested report builder. Covers part of the Windows and Linux brief. |

Local test run (13 Nov 2026): all four Python test suites pass.

## Gaps against the new brief
- No GitHub Actions DevSecOps project (SAST, dependency and container scanning).
- No Prometheus/Grafana observability stack or error-budget calculator.
- Windows and Linux coverage limited to patching; no general health-check / AD reporting toolkit.
- No conversational assistant, certifications section, project detail pages, sitemap.
- Skill order on the site does not follow the required priority.

## Proposed destructive actions
None. Nothing is recommended for archiving or deletion.
