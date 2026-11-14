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
were staged under `ci/workflows/`. Resolved 13 Nov 2026: with the owner's permission they were moved
into `.github/workflows/` through the GitHub web editor in the owner's browser.

## D9 — Third-party actions pinned by commit SHA where tags proved unsafe
`aquasecurity/trivy-action` is pinned to the v0.36.0 commit SHA. Its unprefixed tags were hijacked
in March 2026 and later removed, so a tag reference is neither stable nor trustworthy.

## D10 — v3 redesign keeps four projects (14 Nov 2026)
At the owner's request the portfolio keeps only the four strongest projects (aks-helm-sre,
github-actions-devsecops, terraform-hub-spoke, sre-observability). The other four demos were removed
from `main`; they remain on branch `archive/portfolio-v2-all-demos`. See `PROJECT_PROGRESS.md`.

## D11 — Assistant is a floating widget
The large assistant section was replaced by a small bottom-right widget on every page. Same
in-browser engine and knowledge base; the knowledge base loads on first open.

## D12 — Final polish pass (14 Nov 2026)
Diagrams describe only what each project's code does; the platform diagram uses resume wording only.
Each project shows verification badges. The assistant is described as rule-based (no AI service). Older
`.project-state/` notes were removed because they described the retired eight-demo version; history is in git.
