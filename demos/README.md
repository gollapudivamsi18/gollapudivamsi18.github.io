# Projects

Four independent portfolio projects. Each folder has its own README with an architecture
diagram, the source files and the steps to run or validate it. They use fictional systems
and synthetic data; they are not client work and are not deployed to a live Azure subscription.

- [aks-helm-sre](aks-helm-sre/) — AKS + Helm delivery with SRE guardrails (Azure Pipelines, ACR, Helm, SLO burn-rate alerts)
- [github-actions-devsecops](github-actions-devsecops/) — GitHub Actions DevSecOps pipeline (SAST, secrets, dependencies, Trivy, SBOM)
- [terraform-hub-spoke](terraform-hub-spoke/) — Terraform hub-and-spoke network on Azure
- [sre-observability](sre-observability/) — SLO burn-rate alerting and incident flow (Prometheus, Alertmanager, Grafana)

Earlier demos (Azure Pipelines banking API, migration plan, server ops toolkit, patching lab)
were retired in November 2026 to keep the portfolio focused. They are preserved on the
`archive/portfolio-v2-all-demos` branch.
