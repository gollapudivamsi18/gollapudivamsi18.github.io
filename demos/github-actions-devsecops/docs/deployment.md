# Deploying from GitHub Actions to Azure without stored secrets

The demo's `deploy-example` job stops before any real deployment. This page shows
how the same job would deploy to Azure in a real setup.

## Use OpenID Connect (federated credentials), not client secrets
1. Create an Entra ID app registration (or a user-assigned managed identity).
2. Add a **federated credential** for this repository and the `staging` environment:
   - Issuer: `https://token.actions.githubusercontent.com`
   - Subject: `repo:<owner>/<repo>:environment:staging`
3. Grant the identity the smallest role it needs on the target resource group
   (for example `AcrPush` on the registry and a custom deploy role on the AKS cluster).
4. Store only non-secret IDs as GitHub variables: `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`,
   `AZURE_SUBSCRIPTION_ID`.

```yaml
deploy-staging:
  environment: staging          # required reviewers configured on the environment
  permissions:
    id-token: write             # lets the job request an OIDC token
    contents: read
  steps:
    - uses: azure/login@v2
      with:
        client-id: ${{ vars.AZURE_CLIENT_ID }}
        tenant-id: ${{ vars.AZURE_TENANT_ID }}
        subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}
    - run: az acr login --name <registry>
    - run: |
        docker load < inventory-api.tar.gz
        docker tag inventory-api:${{ github.sha }} <registry>.azurecr.io/inventory-api:${{ github.sha }}
        docker push <registry>.azurecr.io/inventory-api:${{ github.sha }}
```

The token is short-lived and scoped to that environment, so there is nothing to
rotate or leak.

## Other secret-handling rules this demo follows
- No secrets in code, Dockerfiles or workflow files; Gitleaks scans every run.
- Application secrets come from Azure Key Vault at runtime (CSI driver on AKS or
  Key Vault references on App Service), not from pipeline variables.
- `permissions: contents: read` at the workflow level; jobs ask for more only when needed.
- Third-party actions are pinned to a release tag. For stricter supply-chain control,
  pin to a full commit SHA and let Dependabot propose updates.

## Promotion and approvals
- `main` is protected: pull request required, CI checks required, one reviewer, no force pushes.
- The `staging` and `production` environments have required reviewers and a wait timer.
- The same image digest moves from staging to production; nothing is rebuilt between stages.
- Rollback: redeploy the previous image tag (kept in the registry), or `helm rollback`
  on AKS.
