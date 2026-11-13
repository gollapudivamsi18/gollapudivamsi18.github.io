# Decisions

## D1 — Keep a static site (no React/Vite build)
The existing site is static HTML/CSS/JS, deploys from `main` with no build, and passes CI.
A framework would add a build pipeline and dependencies for little gain on a
content site. Shared CSS/JS move to `assets/` so pages stay consistent.

## D2 — Keep demos in the portfolio repository
One repository keeps CI, diagrams and site links in one place, and the existing five demos
already live there. Each demo is self-contained under `demos/<name>/` and can be split into
its own repository later without changes.

## D3 — Assistant runs entirely in the browser
No LLM API is called, so no keys, backend or cost. The assistant answers from a curated
knowledge base (`assets/data/knowledge.json`) built from the resume and demo READMEs, with
keyword/topic retrieval and conversation context for follow-ups. Speech uses the browser's
Web Speech API (supported in Chrome/Edge/Safari; text works everywhere).
Trade-off: it cannot answer questions outside the knowledge base — it says so instead of
guessing. An optional LLM backend (e.g. a serverless proxy holding the key) is listed as a
future option that needs the owner's approval and budget.

## D4 — No transcripts or audio stored
Chat history lives in page memory only and is cleared on reload. Speech recognition is
started only after a click on the microphone button, which triggers the browser's own
permission prompt. Note: in Chrome, speech recognition audio is processed by the browser
vendor's service; the page says so.

## D5 — Naukri link omitted
Naukri has no verified public profile URL for this account. The site says profiles are
available on request instead of linking to a guessed URL.

## D6 — Remote-only wording
Past roles are not described as remote. Only the job preference is stated as remote-only.

## D7 — Recovery files live in the public repo
They contain only requirements, plans and test results — no secrets or private data —
so a separate private repository is not needed.

## D8 — Workflow files are pushed by the owner
The GitHub connector used by Claude can write repository contents but not files under
`.github/workflows/` (GitHub requires a separate "workflows" permission). Workflow changes
are kept under `ci/workflows/` and the owner copies them into `.github/workflows/`
(instructions in `ci/README.md`).
