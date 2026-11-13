# Rollback instructions: Transaction API

> Independent portfolio demo. Fictional environments.

**Goal:** return production to the last good version in under 15 minutes.

## When to roll back
- Post-deployment smoke test fails, or
- Error rate or latency alerts fire within 30 minutes of a release, or
- The change owner or incident lead asks for it.

## Option A - redeploy the previous package (preferred)
1. In Azure DevOps, open **Pipelines > Environments > txn-api-prod** and note the last successful run before the current one.
2. Open that run and choose **Rerun stage** on the `Prod` stage. The same versioned package from Azure Artifacts is deployed again, so nothing is rebuilt.
3. Approve the run (the approval check still applies).
4. Run the smoke test and confirm the version: `GET /health` returns the previous build number.

## Option B - revert and roll forward
Use when the previous package is not safe (for example, a config change has already gone out).
1. Revert the merge commit on `main` through a pull request (`git revert -m 1 <merge-sha>`).
2. Let the pipeline promote it through Dev and UAT with the normal checks.

## Database changes
- Schema changes must be backward compatible for one release (expand, then contract).
- Never roll back a schema in a hurry; roll back the application first.

## After rollback
- Update the change record and the incident channel.
- Create a Bug in Azure Boards linked to the failed release.
