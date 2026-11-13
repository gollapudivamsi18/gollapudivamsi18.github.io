# Progress

## Done (all on branch `portfolio-v2`)
- [x] Phase 1 — Resume read; facts in MASTER_REQUIREMENTS.md.
- [x] Phase 2 — Repository audit (REPOSITORY_AUDIT.md). One repository; nothing to archive or delete.
- [x] Phase 3 — Recovery files.
- [x] Phase 4 — Existing five demos kept as they are (sound, tested in CI).
- [x] Phase 5 — New demos: `sre-observability`, `github-actions-devsecops`, `server-ops-toolkit`.
- [x] Phase 6 — Site redesign: `index.html`, `projects.html`, shared `assets/css/site.css`, `sitemap.xml`, `robots.txt`.
- [x] Phase 7 — Diagrams for the three new demos (`tools/make_diagrams.py`); existing diagrams reused.
- [x] Phase 8 — `resume.html` restyled; same verified content; no contact details, files or print.
- [x] Phase 9 — AI assistant: `assets/js/assistant-core.js`, `assistant-ui.js`, `assets/data/knowledge.json` (36 topics).
- [x] Phase 10 — LinkedIn and GitHub links. Naukri: "profile shared on request" (no verified public URL).
- [x] Phase 12 — Tests (see TEST_RESULTS.md).

## Open
- Phase 11 — GitHub profile README (`gollapudivamsi18/gollapudivamsi18` repository) not created yet.
- Workflows: owner copies `ci/workflows/*.yml` into `.github/workflows/` (connector cannot write workflows).
- Phase 13–14 — Merge PR into `main` after owner review; verify live site.

## Known limitations
- Assistant answers from a fixed knowledge base (no LLM). Voice needs a browser with the Web Speech API (Chrome, Edge, Safari).
- Demos are not deployed to Azure.
