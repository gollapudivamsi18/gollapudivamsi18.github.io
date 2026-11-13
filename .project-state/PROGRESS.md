# Progress

## Done (merged to `main` via PR #1, live)
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

## Done in the final step
- [x] Workflows moved into `.github/workflows/` through the GitHub web editor (owner granted control).
- [x] CI fixes: Ruff config for the DevSecOps demo, `SKIP_SYSTEMD` so the runner's own failed units
      don't leak into fixture tests, trivy-action pinned to the v0.36.0 commit SHA (the old 0.28.0 tag
      was removed after the March 2026 tag-hijack incident), dependency review informational until the
      Dependency graph is enabled.
- [x] Phase 11 — Profile README repository `gollapudivamsi18` created and populated.
- [x] Phase 13–14 — PR #1 merged (b7ad5e3); live site verified.

## Known limitations
- Assistant answers from a fixed knowledge base (no LLM). Voice needs a browser with the Web Speech API (Chrome, Edge, Safari).
- Demos are not deployed to Azure.
