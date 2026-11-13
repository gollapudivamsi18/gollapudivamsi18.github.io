# CI workflows waiting to be enabled

GitHub only runs workflows stored in `.github/workflows/`. The tool that pushed this branch
can write repository files but is not allowed to change workflows (GitHub keeps that behind
a separate "workflows" permission), so the updated workflows are kept here.

| File | What it does |
| --- | --- |
| `workflows/validate.yml` | Replaces `.github/workflows/validate.yml`. Adds tests for the three new demos, ShellCheck and PSScriptAnalyzer for the new scripts, Pester, `promtool` rule tests, `amtool` and `docker compose config`, and the portfolio site checks. |
| `workflows/devsecops-demo.yml` | New. The DevSecOps pipeline for `demos/github-actions-devsecops`. |

## Enable them (about 2 minutes, in the browser)
1. Open the `portfolio-v2` branch on GitHub.
2. For each file above: open it, copy the raw content, then go to `.github/workflows/`,
   choose **Add file → Create new file** (or edit `validate.yml`), paste, and commit to
   `portfolio-v2`.
3. The workflows run on the pull request automatically.

Or from a terminal with your own credentials:
```bash
git checkout portfolio-v2
cp ci/workflows/*.yml .github/workflows/
git commit -am "Enable updated CI workflows" && git push
```
After that, this folder can be deleted.
