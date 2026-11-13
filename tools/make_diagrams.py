"""Generate the SVG architecture diagrams for the three newer demos.

Run: python3 tools/make_diagrams.py   (writes assets/img/*.svg)
Kept as code so labels stay in sync with the demos and the style stays consistent
with the existing hand-drawn SVGs (navy #1A2A4E, slate text, Azure-blue accents).
"""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"
STYLE = ("text{font-family:'Segoe UI',Roboto,'Noto Sans',Arial,sans-serif;fill:#14213D}"
         ".t{font-size:16px;font-weight:700}.s{font-size:13px;fill:#4A5568}"
         ".w{font-size:14px;font-weight:700;fill:#fff}.h{font-size:13px;font-weight:700;fill:#0B5CAD;letter-spacing:.04em}")
FILL = {"navy": ("#1A2A4E", "#1A2A4E"), "azure": ("#E8F2FC", "#0B5CAD"), "plain": ("#FFFFFF", "#A0AEC0"),
        "green": ("#E6F4EA", "#2F7D4F"), "amber": ("#FFF5E5", "#B7791F"), "red": ("#FDECEC", "#C0392B")}


class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h, self.parts = w, h, []
        self.head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="t d">'
                     f'<title id="t">{escape(title)}</title><desc id="d">{escape(desc)}</desc><style>{STYLE}</style>'
                     '<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                     'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#1A2A4E"/></marker></defs>'
                     f'<rect width="{w}" height="{h}" fill="#fff"/>')

    def box(self, x, y, w, h, title, sub=None, kind="azure", dashed=False):
        fill, stroke = FILL[kind]
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"{dash}/>')
        cls = "w" if kind == "navy" else "t"
        lines = [title] + ([sub] if isinstance(sub, str) else (sub or []))
        ty = y + h / 2 - (len(lines) - 1) * 9 + 5
        self.parts.append(f'<text class="{cls}" x="{x + w / 2}" y="{ty}" text-anchor="middle">{escape(title)}</text>')
        for i, line in enumerate(lines[1:], 1):
            c = 's' if kind != "navy" else 'w" style="font-weight:400;font-size:12.5px'
            self.parts.append(f'<text class="{c}" x="{x + w / 2}" y="{ty + i * 18}" text-anchor="middle">{escape(line)}</text>')

    def arrow(self, x1, y1, x2, y2, label=None, dashed=False):
        dash = ' stroke-dasharray="6 4"' if dashed else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1A2A4E" stroke-width="2" marker-end="url(#a)"{dash}/>')
        if label:
            self.parts.append(f'<text class="s" x="{(x1 + x2) / 2 + 8}" y="{(y1 + y2) / 2 + 4}">{escape(label)}</text>')

    def label(self, x, y, text, cls="h", anchor="start"):
        self.parts.append(f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{escape(text)}</text>')

    def save(self, name):
        (OUT / name).write_text(self.head + "".join(self.parts) + "</svg>\n", encoding="utf-8")
        print("wrote", name)


def sre():
    s = Svg(560, 600, "SRE observability demo architecture",
            "A load generator calls the orders service. Prometheus scrapes its metrics every 15 seconds, evaluates "
            "SLO recording rules and multi-window burn-rate alerts, and sends alerts to Alertmanager. Alertmanager "
            "routes pages to the on-call receiver and tickets to a queue; both link to runbooks. Grafana reads from "
            "Prometheus. Separately, error_budget.py computes budget and burn rate from exported request counts. "
            "Runs locally with Docker Compose; nothing is deployed to Azure.")
    s.label(20, 26, "LOCAL DOCKER COMPOSE STACK · SYNTHETIC TRAFFIC")
    s.box(20, 40, 160, 60, "Load generator", "curl every 100 ms", "plain")
    s.box(220, 40, 320, 60, "orders service", "/api/orders · /metrics · probes", "navy")
    s.arrow(180, 70, 218, 70)
    s.arrow(380, 100, 380, 146, "scrape 15s")
    s.box(140, 148, 400, 92, "Prometheus", ["recording rules: error ratio 5m / 30m / 1h / 6h, p95",
                                               "alerts: 14.4x (1h+5m), 6x (6h+30m), latency, target down"], "azure")
    s.arrow(250, 240, 150, 300, "alerts")
    s.arrow(430, 240, 430, 298, "query")
    s.box(20, 300, 250, 74, "Alertmanager", ["group, route, inhibit", "page vs ticket"], "azure")
    s.box(310, 300, 230, 74, "Grafana", ["availability, burn rate,", "p95, scrape status"], "azure")
    s.arrow(80, 374, 80, 420)
    s.arrow(210, 374, 210, 420)
    s.box(20, 422, 120, 58, "On-call", "severity=page", "red")
    s.box(150, 422, 120, 58, "Ticket queue", "severity=ticket", "amber")
    s.arrow(145, 480, 145, 516)
    s.box(20, 518, 250, 62, "Runbook → RCA", "blameless review, actions", "green")
    s.box(310, 420, 230, 160, "error_budget.py", ["offline calculator", "budget used / remaining", "burn rate per window",
                                                    "exit 2 when a page fires", "→ release gate"], "plain", dashed=True)
    s.save("sre-observability.svg")


def devsecops():
    s = Svg(560, 640, "GitHub Actions DevSecOps pipeline",
            "A pull request triggers five parallel jobs: Ruff lint, unit and HTTP tests with an 80 percent coverage "
            "gate, Bandit static analysis, Gitleaks secret scan, and pip-audit plus dependency review. When all pass, "
            "the container job builds the image, smoke-tests it, checks it runs as a non-root user, scans it with "
            "Trivy and produces a CycloneDX SBOM. Image and SBOM are stored as build artifacts. A manual run on main "
            "reaches the demo-staging environment, which only prints what it would deploy.")
    s.label(20, 26, "GITHUB-HOSTED RUNNERS · NO CLOUD CREDENTIALS")
    s.box(130, 40, 300, 56, "Pull request / push", "demos/github-actions-devsecops/**", "navy")
    xs = [20, 128, 236, 344, 452]
    names = [("lint", "Ruff"), ("test", "≥ 80% cov."), ("sast", "Bandit"), ("secrets", "Gitleaks"), ("deps", "pip-audit")]
    for x, (n, sub) in zip(xs, names):
        s.arrow(280, 96, x + 44, 138)
        s.box(x, 140, 88, 72, n, sub, "azure")
        s.arrow(x + 44, 212, 280, 262)
    s.label(352, 254, "all five must pass", "s", "start")
    s.box(110, 264, 340, 150, "container", ["docker build", "smoke test /healthz + /api/items",
                                            "assert non-root user (10001)", "Trivy: fail on fixable CRITICAL",
                                            "CycloneDX SBOM"], "navy")
    s.arrow(280, 414, 280, 452)
    s.box(110, 454, 340, 56, "Build artifacts (7 days)", "image tarball · SBOM · coverage.xml", "plain")
    s.arrow(280, 510, 280, 548, "manual run on main", dashed=True)
    s.box(110, 550, 340, 70, "environment: demo-staging", ["prints what it would deploy", "real path: OIDC → Azure (docs)"],
          "green", dashed=True)
    s.save("devsecops-pipeline.svg")


def serverops():
    s = Svg(560, 600, "Windows and Linux server operations toolkit",
            "A scheduler (Task Scheduler on Windows, cron on Linux) runs read-only checks. Windows: Get-ServerHealth, "
            "Get-PatchReport and Get-ADAccountReport using the shared ServerOps module. Linux: health-check, "
            "ssh-hardening-check and user-audit. Results go out as text, JSON or CSV with exit codes 0, 1 or 2 for a "
            "monitoring agent. The only state-changing script, Restart-StoppedAutoService, needs an allow-list and "
            "asks for confirmation.")
    s.box(20, 20, 250, 56, "Task Scheduler", "Windows Server", "navy")
    s.box(290, 20, 250, 56, "cron", "RHEL / Ubuntu", "navy")
    s.arrow(145, 76, 145, 108)
    s.arrow(415, 76, 415, 108)
    s.box(20, 110, 250, 150, "PowerShell (read-only)", ["Get-ServerHealth", "Get-PatchReport", "Get-ADAccountReport",
                                                         "ServerOps.psm1 (tested)"], "azure")
    s.box(290, 110, 250, 150, "Bash (read-only)", ["health-check.sh", "ssh-hardening-check.sh", "user-audit.sh",
                                                    "logrotate + crontab examples"], "azure")
    s.arrow(145, 260, 250, 318)
    s.arrow(415, 260, 310, 318)
    s.box(110, 320, 340, 70, "Results", ["text · JSON · CSV", "exit 0 OK · 1 WARNING · 2 CRITICAL"], "plain")
    s.arrow(280, 390, 280, 424)
    s.box(110, 426, 340, 56, "Monitoring agent / log shipper", "e.g. Azure Monitor Agent → Log Analytics", "green", dashed=True)
    s.box(20, 506, 520, 74, "Changes state: Restart-StoppedAutoService.ps1",
          ["allow-listed services only · -WhatIf · confirms each restart by default"], "amber")
    s.save("server-ops-toolkit.svg")


if __name__ == "__main__":
    sre()
    devsecops()
    serverops()
