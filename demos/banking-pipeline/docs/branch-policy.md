# Branch policy, pull requests and work items

> Independent portfolio demo. Fictional project and team names.

## Branching
- `main` is always releasable. Short-lived `feature/<work-item-id>-short-name` branches.
- `release/<version>` branches are cut only when a hotfix must go out without other changes.
- Versions follow semantic versioning: `MAJOR.MINOR.PATCH`.

## Policy on `main` (Azure Repos > Branches > Branch policies)
| Setting | Value |
|---|---|
| Minimum reviewers | 2, and the author cannot approve their own change |
| Reset votes on new pushes | On |
| Check for linked work items | Required |
| Check for comment resolution | Required |
| Build validation | This pipeline, required, expires after 12 hours |
| Merge type | Squash merge only |
| Automatically included reviewers | `Payments-Leads` group for `demos/banking-pipeline/src/*` |

## Work-item flow (Azure Boards)
1. Every change starts from a User Story or Bug, e.g. `AB#1234`.
2. The branch and commit messages mention the ID, which links the commit to the work item.
3. The pull request is linked to the work item; the policy blocks merging without one.
4. When the PR completes, the work item moves to **Resolved** automatically.
5. The release record shows which work items went into each deployment, which gives audit traceability.

## Pull-request checklist
- [ ] Linked work item
- [ ] Unit tests added or updated
- [ ] Pipeline green on the PR
- [ ] Rollback note added if the change touches the database or configuration
