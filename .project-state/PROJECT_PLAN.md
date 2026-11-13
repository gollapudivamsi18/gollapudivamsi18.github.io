# Project plan

Work happens on branch `portfolio-v2`, merged to `main` through a pull request once tests pass.

| # | Phase | Output | Depends on |
| --- | --- | --- | --- |
| 1 | Resume analysis | Facts in MASTER_REQUIREMENTS | — |
| 2 | Repository audit | REPOSITORY_AUDIT.md | — |
| 3 | Recovery system | `.project-state/` files | 1, 2 |
| 4 | Improve existing demos | Small fixes only; they are sound | 2 |
| 5 | New demos | `demos/github-actions-devsecops`, `demos/sre-observability`, `demos/server-ops-toolkit` with tests and CI | 3 |
| 6 | Site redesign | `index.html`, `projects.html`, shared `assets/css/site.css` | 5 |
| 7 | Diagrams | SVGs in `assets/img/` for new demos; existing diagrams reused | 5 |
| 8 | Resume page | `resume.html` restyled, same verified content | 6 |
| 9 | AI assistant | `assets/js/assistant.js`, `assets/data/knowledge.json`, tests | 6 |
| 10 | Links | LinkedIn, GitHub; Naukri pending a verified URL | 6 |
| 11 | GitHub profile README | New repo `gollapudivamsi18/gollapudivamsi18` (needs GitHub access) | 6 |
| 12 | Testing | Playwright at 7 widths, unit tests, link + secret checks | 6–9 |
| 13 | Deployment | Merge PR to `main`; Pages redeploys | 12, GitHub access |
| 14 | Verification | Check live site | 13 |
| 15 | Final checkpoint | Update all state files, push | 14 |
