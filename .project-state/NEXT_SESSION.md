# Next session

State at end of session 1 (13 Nov 2026): all work is on `portfolio-v2` and in
PR #1 (https://github.com/gollapudivamsi18/gollapudivamsi18.github.io/pull/1), not merged.
The live site is still the old version (main @ c9c35e2). Every test passed on a fresh clone
of the branch (see TEST_RESULTS.md).

1. [ ] Owner copies `ci/workflows/*.yml` into `.github/workflows/` on `portfolio-v2`
       (the Claude GitHub connector has no workflows permission). Then check CI on PR #1 and
       fix any failures (ShellCheck, PSScriptAnalyzer, Pester, promtool, amtool, Trivy, Ruff, Bandit).
2. [ ] Owner reviews PR #1 (About wording, B.Sc. line) and approves the merge.
3. [ ] Merge PR #1; confirm the Pages build; open https://gollapudivamsi18.github.io and
       record the live commit in DEPLOYMENT_STATUS.md.
4. [ ] Owner creates the public repo `gollapudivamsi18` and pastes `ci/profile-README.md`
       (the connector cannot create repositories). Pin `gollapudivamsi18.github.io`.
5. [ ] Add a Naukri link only if the owner provides a verified public URL.
6. [ ] Optional, needs owner approval and budget: an LLM-backed assistant through a small
       serverless proxy that holds the API key (see DECISIONS.md D3).
