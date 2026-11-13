# Next session

State at end of session 1 (13 Nov 2026): PR #1 merged; the new site is live (main @ b7ad5e3 plus
this notes update). Both workflows are enabled and green. The profile README is live.

Remaining, all optional and owner-decided:
1. [ ] Pin `gollapudivamsi18.github.io` on the GitHub profile (Customize your pins).
2. [ ] Turn on Settings > Code security > Dependency graph, then remove `continue-on-error: true`
       from the dependency-review step in `.github/workflows/devsecops-demo.yml` so it gates PRs.
3. [ ] Add a Naukri link only if the owner provides a verified public URL.
4. [ ] Review the About wording and the B.Sc. line (REPOSITORY_AUDIT.md notes the discrepancy).
5. [ ] Optional, needs owner approval and budget: an LLM-backed assistant through a small
       serverless proxy that holds the API key (see DECISIONS.md D3).
