"""Build projects.html from the project list below.

Run: python3 tools/build_projects.py
Keeping the content as data makes every project section follow the same
structure: purpose, stack, what it shows, how it was tested, limitations.
"""
from html import escape
from pathlib import Path

REPO = "https://github.com/gollapudivamsi18/gollapudivamsi18.github.io/tree/main/demos/"
PROJECTS = [
    dict(id="devsecops", folder="github-actions-devsecops", title="GitHub Actions DevSecOps pipeline",
         area="Azure DevOps and SRE", diagram="devsecops-pipeline.svg",
         purpose="A pull-request pipeline that checks code, dependencies, secrets and the container image before anything moves toward an environment.",
         stack=["GitHub Actions", "Python", "Docker", "Ruff", "Bandit", "Gitleaks", "pip-audit", "Trivy", "CycloneDX"],
         shows=["Five parallel quality and security jobs, then a container job that only runs if all five pass.",
                "Container smoke test, non-root check, Trivy gate on fixable critical CVEs and an SBOM as a build artifact.",
                "A manual promotion step into a protected environment, plus a written guide to OIDC login to Azure without stored secrets."],
         tested="8 unit and HTTP tests pass locally. The workflow file is ready in the repository and runs on GitHub-hosted runners once enabled.",
         limits="No registry push or real deployment; actions pinned to release tags rather than commit SHAs."),
    dict(id="banking-pipeline", folder="banking-pipeline", title="Azure Pipelines for a Transaction API",
         area="Azure DevOps and SRE", diagram="banking-pipeline.svg",
         purpose="A multi-stage Azure Pipelines workflow for a fictional bank's transfer API, built around audit-friendly promotion.",
         stack=["Azure Pipelines YAML", "Azure Repos branch policies", "Python"],
         shows=["Pull-request checks: unit tests, syntax check and a quality-gate step.",
                "One versioned package promoted Dev → UAT → Prod, with an approval and business-hours check before production.",
                "A documented rollback to the last good package in under 15 minutes, and idempotent transfer logic."],
         tested="Python unit tests and YAML parsing run in GitHub Actions on every push.",
         limits="The pipeline YAML is validated for syntax, not run against a real Azure DevOps organisation."),
    dict(id="sre-observability", folder="sre-observability", title="SRE observability and incident management",
         area="Azure DevOps and SRE", diagram="sre-observability.svg",
         purpose="SLO-based monitoring for a small service: alert on error-budget burn, route pages and tickets differently, and close the loop with a runbook and review.",
         stack=["Prometheus", "Alertmanager", "Grafana", "Python", "Docker Compose"],
         shows=["Recording rules and multi-window burn-rate alerts (14.4x over 1h and 5m, 6x over 6h and 30m) with promtool unit tests.",
                "An error-budget calculator: on the synthetic incident it reports 47.4% of the budget used and a page at 34x burn.",
                "A Grafana dashboard, two runbooks, a fictional RCA and a reusable RCA template."],
         tested="11 Python tests pass locally. Rule tests use promtool in CI once the updated workflow is enabled.",
         limits="Single service and SLI; synthetic traffic only; no long-term metrics storage."),
    dict(id="aks-helm-sre", folder="aks-helm-sre", title="AKS + Helm delivery with SRE practices",
         area="Azure DevOps and SRE", diagram="aks-sre-architecture.svg",
         purpose="A containerised API packaged for AKS and delivered through a staged pipeline with an SLO and an incident runbook.",
         stack=["AKS", "Helm", "Docker", "Azure Pipelines", "Prometheus"],
         shows=["Helm chart with liveness and readiness probes, non-root user, HPA and PodDisruptionBudget.",
                "CI with unit tests, helm lint and image scan; staging deploy with helm upgrade --atomic; approval before production.",
                "A 99.5% availability SLO over 28 days with burn-rate alerts and an on-call runbook."],
         tested="helm lint, helm template, unit tests and a local smoke test of the API run in GitHub Actions.",
         limits="Not deployed to a real AKS cluster; ingress and cluster provisioning are described, not built."),
    dict(id="terraform-hub-spoke", folder="terraform-hub-spoke", title="Terraform hub-and-spoke network",
         area="Azure cloud infrastructure", diagram="hub-spoke.svg",
         purpose="Hub-and-spoke Azure networking for a fictional asset-management platform, written as Terraform.",
         stack=["Terraform", "Azure VNet", "NSG", "Private DNS", "Recovery Services vault", "Log Analytics"],
         shows=["Hub with firewall, gateway and shared-services subnets; two spokes peered only with the hub; deny-by-default NSGs.",
                "One tag block applied to every resource.",
                "Backup policy, optional DR vault, and a cost and RTO/RPO discussion."],
         tested="terraform fmt and terraform validate run in GitHub Actions.",
         limits="Not applied to a real subscription; remote state is documented rather than configured."),
    dict(id="migration-plan", folder="migration-plan", title="Windows and Linux migration plan to Azure",
         area="Azure cloud infrastructure", diagram="migration-waves.svg",
         purpose="How I plan a lift-and-shift: inventory, dependencies, waves, cutover and rollback, shown on 12 fictional servers.",
         stack=["Azure Migrate", "Azure Site Recovery", "Python", "CSV"],
         shows=["A sample inventory and a port-level dependency map.",
                "A script that groups dependent servers into waves, with shared services first and critical systems last.",
                "Cutover checks for Windows, Linux, Azure and the application, plus a rollback runbook with a clear decision rule."],
         tested="The wave planner's unit tests run in GitHub Actions.",
         limits="Planning artefacts only; no Azure Migrate project or replication is set up."),
    dict(id="server-ops-toolkit", folder="server-ops-toolkit", title="Windows and Linux server ops toolkit",
         area="Windows Server and Linux administration", diagram="server-ops-toolkit.svg",
         purpose="Day-to-day fleet checks: health, patch status, Active Directory hygiene, SSH baseline and user audit.",
         stack=["PowerShell", "Pester", "Bash", "CIM/WinRM", "Active Directory module"],
         shows=["Read-only PowerShell reports with JSON/CSV output and 0/1/2 exit codes for monitoring.",
                "Bash health check, SSH hardening check (first value wins, as in sshd) and user audit.",
                "One state-changing script that only restarts allow-listed services and confirms each restart by default."],
         tested="7 Bash tests against fixture files pass locally; Pester and ShellCheck run in CI once the updated workflow is enabled.",
         limits="Calls that need a real Windows Server or Active Directory were not run; the SSH baseline is a short list, not a full benchmark."),
    dict(id="patching-lab", folder="patching-lab", title="Patching and OS upgrade lab",
         area="Windows Server and Linux administration", diagram="patching-flow.svg",
         purpose="A safe patching routine for Windows and Linux: snapshot, patch, compare, report.",
         stack=["PowerShell", "Bash", "dnf/yum/apt", "Python"],
         shows=["Pre-checks that snapshot OS build, free space, services, ports and pending reboot.",
                "Linux patching with --security-only and --dry-run; post-checks that flag anything that did not come back.",
                "A compliance report built from the results, and an OS upgrade checklist."],
         tested="ShellCheck, PSScriptAnalyzer, a dry-run of the Linux scripts and the report tests run in GitHub Actions.",
         limits="Lab hosts are synthetic; Windows patching itself is described rather than scripted."),
]

AREAS = ["Azure DevOps and SRE", "Azure cloud infrastructure", "Windows Server and Linux administration"]


def section(p):
    li = "".join(f"<li>{escape(x)}</li>" for x in p["shows"])
    tags = "".join(f"<li>{escape(x)}</li>" for x in p["stack"])
    return f"""
<article class="project" id="{p['id']}" aria-labelledby="{p['id']}-title">
  <p class="eyebrow">{escape(p['area'])}</p>
  <h2 id="{p['id']}-title">{escape(p['title'])}</h2>
  <div class="project-grid">
    <div>
      <p>{escape(p['purpose'])}</p>
      <h3>What it shows</h3>
      <ul>{li}</ul>
      <dl class="meta">
        <dt>Tested</dt><dd>{escape(p['tested'])}</dd>
        <dt>Limits</dt><dd>{escape(p['limits'])}</dd>
      </dl>
      <ul class="tags" aria-label="Technology">{tags}</ul>
      <p style="margin-top:14px"><a class="btn ghost" href="{REPO}{p['folder']}" target="_blank" rel="noopener">Code and README on GitHub</a></p>
    </div>
    <figure class="diagram">
      <a href="assets/img/{p['diagram']}" target="_blank" rel="noopener"><img src="assets/img/{p['diagram']}" alt="Architecture diagram: {escape(p['title'])}" loading="lazy" width="560" height="600"></a>
      <figcaption>Diagram of the demo as built. Open it full size for detail; the text description is in the image's accessible title.</figcaption>
    </figure>
  </div>
</article>"""


def main():
    toc = "".join(f'<li><a href="#{p["id"]}">{escape(p["title"])}</a></li>' for p in PROJECTS)
    body = "".join(section(p) for a in AREAS for p in PROJECTS if p["area"] == a)
    html = f"""<!DOCTYPE html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Portfolio Projects | Vamsikrishna Gollapudi</title>
<meta name="description" content="Eight independent Azure DevOps, SRE, Azure infrastructure, Windows and Linux demos with architecture diagrams, tests and honest limits.">
<link rel="canonical" href="https://gollapudivamsi18.github.io/projects.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://gollapudivamsi18.github.io/projects.html">
<meta property="og:title" content="Portfolio Projects | Vamsikrishna Gollapudi">
<meta property="og:description" content="Azure DevOps, SRE and Azure infrastructure demos with architecture diagrams and tests.">
<meta name="theme-color" content="#13213d">
<link rel="stylesheet" href="assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="./">Vamsikrishna Gollapudi</a>
    <button class="menu-btn ghost" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
    <nav class="nav" id="site-nav" aria-label="Main">
      <a href="./#expertise">Expertise</a>
      <a href="./#experience">Experience</a>
      <a href="projects.html" aria-current="page">Projects</a>
      <a href="./#certifications">Certifications</a>
      <a href="./#assistant-section">Assistant</a>
      <a href="resume.html">Resume</a>
      <a href="./#contact">Contact</a>
    </nav>
  </div>
</header>
<main id="main">
<section class="block">
  <div class="wrap">
    <p class="eyebrow">Projects</p>
    <h1>Eight demos, with diagrams and tests</h1>
    <p class="lead">These are independent demos I built on fictional systems and synthetic data. They are not client or employer work, and none runs in a real Azure subscription. Each section says how it was tested and where it stops. Grouped by my focus areas: Azure DevOps and SRE first, then Azure infrastructure, then Windows and Linux.</p>
    <ul class="toc">{toc}</ul>
  </div>
</section>
<section class="block">
  <div class="wrap">{body}
  </div>
</section>
</main>
<footer class="site-footer">
  <div class="wrap">
    <span>© Vamsikrishna Gollapudi. Demos use fictional systems and synthetic data. Open to 100% remote roles.</span>
    <a href="https://github.com/gollapudivamsi18/gollapudivamsi18.github.io">Source on GitHub</a>
  </div>
</footer>
<script src="assets/js/site.js" defer></script>
</body>
</html>
"""
    Path(__file__).resolve().parent.parent.joinpath("projects.html").write_text(html, encoding="utf-8")
    print("wrote projects.html")


if __name__ == "__main__":
    main()
