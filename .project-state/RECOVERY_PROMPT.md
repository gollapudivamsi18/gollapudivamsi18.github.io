# Recovery prompt

Paste the block below into a new Claude session (with GitHub access to this repository) to continue.

---

You are continuing an existing GitHub portfolio implementation for Vamsikrishna Gollapudi.

Repository: https://github.com/gollapudivamsi18/gollapudivamsi18.github.io
Live site: https://gollapudivamsi18.github.io (GitHub Pages, deployed from `main`)
Working branch: `portfolio-v2` (check whether it exists on the remote; if not, the last
session could not push and work may need to be redone from NEXT_SESSION.md).

1. Clone the repository and check out `portfolio-v2` if it exists.
2. Read, in order: `.project-state/MASTER_REQUIREMENTS.md`, `PROJECT_PLAN.md`, `PROGRESS.md`,
   `NEXT_SESSION.md`, `DECISIONS.md`, `TEST_RESULTS.md`, `DEPLOYMENT_STATUS.md`,
   `REPOSITORY_AUDIT.md`.
3. Run `git status` and `git log --oneline -15`; confirm which commit is on the remote.
4. Do not restart from scratch. Do not overwrite working components.
5. Continue from the first unchecked item in NEXT_SESSION.md.
6. Keep every original requirement: 100% remote-only positioning, genuine demos clearly
   labelled as independent and synthetic, natural professional English, responsive design,
   view-only HTML resume, accurate architecture diagrams, and the conversational
   AI assistant with voice.
7. Validate (`python3 tools/run_checks.py` and the Playwright test in `tests/`), update the
   state files, commit, push, and record the commit hash before moving on.

The owner's resume (`vamsikrishna_Resume.docx`) is not in the repository. Ask the owner to
attach it if a fact needs re-checking; the verified facts are in MASTER_REQUIREMENTS.md and
`resume.html`.
