"""Generate the architecture diagrams used on the portfolio (assets/img/*.svg).

Run: python3 tools/make_diagrams.py
One visual language for every diagram: dark navy canvas, Azure-blue flow lines,
teal for healthy/delivery, amber for alerting, violet for security gates.
Animated dashes respect prefers-reduced-motion.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "img"

C = {
    "bg1": "#0c1a33", "bg2": "#081226", "node": "#11264a", "stroke": "#26497d",
    "title": "#eaf2ff", "sub": "#93abd0", "azure": "#3b9cff", "teal": "#2dd4bf",
    "amber": "#f5b84b", "violet": "#a78bfa", "group": "#2c5288", "muted": "#5f7aa3",
}
FONT = "'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif"
MONO = "ui-monospace,'Cascadia Code',Consolas,Menlo,monospace"


class Svg:
    def __init__(self, w, h, title, desc):
        self.w, self.h = w, h
        self.parts = []
        self.title, self.desc = title, desc
        self.used = set()

    def add(self, s):
        self.parts.append(s)

    def group(self, x, y, w, h, label, color=None):
        color = color or C["group"]
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" fill-opacity=".07" '
                 f'stroke="{color}" stroke-dasharray="4 5" stroke-width="1.2"/>')
        self.add(f'<text x="{x+12}" y="{y+18}" class="gl" fill="{color}">{escape(label.upper())}</text>')

    def node(self, x, y, w, h, title, sub=None, accent=None, dashed=False, lines=None, mono=False):
        accent = accent or C["azure"]
        dash = ' stroke-dasharray="5 4"' if dashed else ""
        self.add(f'<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="n"{dash}/>'
                 f'<rect x="{x}" y="{y+8}" width="3" height="{h-16}" rx="1.5" fill="{accent}"/>')
        ty = y + (20 if (sub or lines) else h / 2 + 4.5)
        self.add(f'<text x="{x+13}" y="{ty}" class="t">{escape(title)}</text>')
        if sub:
            cls = "m" if mono else "s"
            self.add(f'<text x="{x+13}" y="{ty+16}" class="{cls}">{escape(sub)}</text>')
        for i, line in enumerate(lines or []):
            self.add(f'<text x="{x+13}" y="{ty+16+(i*15)+(16 if sub else 0)}" class="s">{escape(line)}</text>')
        self.add("</g>")

    def arrow(self, pts, color=None, anim=True, label=None, lx=None, ly=None, dashed=False, both=False):
        color = color or C["azure"]
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        mid = {"#3b9cff": "a", "#2dd4bf": "t", "#f5b84b": "w", "#a78bfa": "v", "#5f7aa3": "g"}[color]
        cls = "flow" if anim else ""
        extra = ' stroke-dasharray="4 4"' if dashed and not anim else ""
        start = f' marker-start="url(#s{mid})"' if both else ""
        self.used.add(mid)
        if both:
            self.used.add("s" + mid)
        klass = ("ln " + cls).strip()
        self.add(f'<path d="{d}" stroke="{color}" class="{klass}"{extra}'
                 f' marker-end="url(#{mid})"{start}/>')
        if label:
            self.add(f'<text x="{lx}" y="{ly}" class="lbl" fill="{color}">{escape(label)}</text>')

    def text(self, x, y, s, cls="s", fill=None, anchor="start"):
        f = f' fill="{fill}"' if fill else ""
        self.add(f'<text x="{x}" y="{y}" class="{cls}"{f} text-anchor="{anchor}">{escape(s)}</text>')

    def render(self):
        markers = ""
        for k, col in (("a", C["azure"]), ("t", C["teal"]), ("w", C["amber"]), ("v", C["violet"]), ("g", C["muted"])):
            if k not in self.used:
                continue
            markers += (f'<marker id="{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                        f'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{col}"/></marker>')
            if "s" + k not in self.used:
                continue
            markers += (f'<marker id="s{k}" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="7" markerHeight="7" '
                        f'orient="auto-start-reverse"><path d="M0,1 L9,5 L0,9 z" fill="{col}"/></marker>')
        style = (
            f"svg{{font-family:{FONT}}}"
            f".n{{fill:{C['node']};stroke:{C['stroke']}}}"
            ".ln{fill:none;stroke-width:1.6;stroke-linejoin:round}"
            f".t{{font-size:12.5px;font-weight:600;fill:{C['title']}}}"
            f".s{{font-size:10.5px;fill:{C['sub']}}}"
            f".m{{font:10px {MONO};fill:{C['sub']};white-space:pre}}"
            ".gl{font-size:9.5px;font-weight:700;letter-spacing:.09em}"
            ".lbl{font-size:9.5px;font-weight:600}"
            ".flow{stroke-dasharray:5 5;animation:f 1.4s linear infinite}"
            "@keyframes f{to{stroke-dashoffset:-20}}"
            "@media (prefers-reduced-motion:reduce){.flow{animation:none}}"
        )
        bg = (f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">'
              f'<stop offset="0" stop-color="{C["bg1"]}"/><stop offset="1" stop-color="{C["bg2"]}"/></linearGradient>'
              f'<pattern id="dots" width="18" height="18" patternUnits="userSpaceOnUse">'
              f'<circle cx="1" cy="1" r="1" fill="#1d3560"/></pattern>{markers}</defs>'
              f'<rect width="{self.w}" height="{self.h}" rx="14" fill="url(#bg)"/>'
              f'<rect width="{self.w}" height="{self.h}" rx="14" fill="url(#dots)" opacity=".55"/>')
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-labelledby="ttl dsc"><title id="ttl">{escape(self.title)}</title>'
                f'<desc id="dsc">{escape(self.desc)}</desc><style>{style}</style>{bg}'
                + "".join(self.parts) + "</svg>\n")


def hero():
    s = Svg(720, 440, "Azure platform delivery and operations flow",
            "Pull requests in GitHub Enterprise run CI in GitHub Actions and Azure Pipelines with security gates, "
            "images go to Azure Container Registry and deploy with Helm to AKS inside an Azure landing zone "
            "provisioned by Terraform and Bicep. Prometheus, Grafana and Azure Monitor feed SLO burn-rate alerts, "
            "on-call runbooks and incident reviews, whose actions return to the backlog.")
    y = 34
    s.node(18, y, 150, 56, "GitHub Enterprise", "PRs · CODEOWNERS")
    s.node(196, y, 150, 56, "CI/CD pipelines", "Actions · Azure Pipelines")
    s.node(374, y, 150, 56, "Security gates", "SAST · secrets · Trivy", accent=C["violet"])
    s.node(552, y, 150, 56, "Container registry", "ACR · versioned images")
    for x in (168, 346, 524):
        s.arrow([(x, y + 28), (x + 27, y + 28)])
    s.group(18, 132, 500, 214, "Azure landing zone · 8 subscriptions · 600+ resources")
    s.node(34, 164, 140, 56, "Terraform · Bicep", "modules · drift checks", accent=C["teal"])
    s.node(196, 164, 148, 56, "Hub-and-spoke", "VNet · NSG · VPN · DNS")
    s.node(362, 164, 140, 56, "AKS · 6 clusters", "Helm · Ingress · HPA", accent=C["teal"])
    s.node(34, 240, 230, 56, "Identity and governance", "Entra ID · RBAC · Azure Policy", accent=C["violet"])
    s.node(282, 240, 220, 56, "Key Vault · Defender", "secrets · Secure Score 62→85%", accent=C["violet"])
    s.arrow([(174, 192), (195, 192)], C["teal"])
    s.arrow([(627, 90), (627, 116), (432, 116), (432, 163)], C["teal"], label="helm upgrade --atomic", lx=470, ly=110)
    s.text(34, 330, "Remote state · nightly drift detection · 98% tagging compliance", "s")
    s.group(530, 132, 178, 292, "Observability · SRE", C["amber"])
    s.node(541, 160, 156, 50, "Prometheus · Grafana", "150+ alert rules", accent=C["amber"])
    s.node(541, 222, 156, 50, "Azure Monitor", "Log Analytics · KQL", accent=C["amber"])
    s.node(541, 284, 156, 50, "SLO · error budget", "burn-rate paging", accent=C["amber"])
    s.node(541, 346, 156, 50, "On-call · runbooks", "40+ runbooks · RCA", accent=C["amber"])
    s.arrow([(502, 185), (540, 185)], C["amber"])
    for y2 in (210, 272, 334):
        s.arrow([(619, y2), (619, y2 + 11)], C["amber"], anim=False)
    s.arrow([(541, 371), (8, 371), (8, 62), (17, 62)], C["muted"], label="post-incident actions → backlog",
            lx=200, ly=364)
    s.text(18, 418, "MTTR ↓ ~35%  ·  alert noise ↓ 40%  ·  99.95% platform availability", "lbl", C["teal"])
    return s


def devsecops():
    s = Svg(720, 350, "GitHub Actions DevSecOps pipeline",
            "A pull request fans out to five parallel jobs: Ruff lint, tests with an 80 percent coverage gate, "
            "Bandit SAST, Gitleaks secret scanning and pip-audit. A container job then builds, smoke-tests and "
            "scans the image with Trivy and produces an SBOM before an environment approval gate.")
    s.node(16, 140, 128, 60, "Pull request", "or push to main")
    jobs = [("Lint", "Ruff · bandit rules"), ("Test", "unittest · coverage ≥ 80%"),
            ("SAST", "Bandit · medium+ fails"), ("Secrets", "Gitleaks · full tree"),
            ("Dependencies", "pip-audit · dep. review")]
    for i, (t, sub) in enumerate(jobs):
        y = 30 + i * 58
        s.node(196, y, 166, 46, t, sub, accent=C["violet"])
        s.arrow([(144, 170), (170, 170), (170, y + 23), (195, y + 23)], C["violet"])
        s.arrow([(362, y + 23), (388, y + 23), (388, 170), (411, 170)], C["violet"], anim=False)
    s.text(196, 22, "5 JOBS IN PARALLEL", "gl", C["violet"])
    s.node(412, 106, 152, 128, "Container job", None, accent=C["teal"],
           lines=["docker build", "smoke test /healthz", "non-root check", "Trivy · CRITICAL fails", "CycloneDX SBOM"])
    s.node(586, 90, 120, 56, "Approval gate", "GitHub environment", accent=C["amber"])
    s.node(586, 196, 120, 56, "demo-staging", "pattern only", accent=C["teal"], dashed=True)
    s.arrow([(564, 150), (575, 150), (575, 118), (585, 118)], C["teal"])
    s.arrow([(646, 146), (646, 195)], C["amber"])
    s.text(586, 274, "OIDC to Azure,", "s")
    s.text(586, 288, "no stored secrets", "s")
    s.text(16, 330, "Fails on: lint finding · coverage < 80% · medium+ SAST · leaked secret · vulnerable "
           "dependency · fixable CRITICAL CVE · root container", "s")
    return s


def aks():
    s = Svg(720, 330, "AKS and Helm delivery with SRE practices",
            "Azure Pipelines runs tests, helm lint and an image scan, pushes to ACR, deploys to AKS staging with an "
            "atomic Helm upgrade and smoke test, waits for approval, then deploys to production with HPA, PDB and "
            "probes. Prometheus and Azure Monitor feed burn-rate alerts and an incident runbook; the error-budget "
            "policy can freeze releases.")
    s.text(16, 26, "DELIVERY", "gl", C["teal"])
    top = [(16, "Azure Pipelines", "tests · helm lint · scan", C["azure"]),
           (158, "ACR", "image:<git-sha>", C["azure"]),
           (300, "AKS staging", "--atomic · smoke test", C["teal"]),
           (442, "Approval", "environment check", C["amber"]),
           (584, "AKS production", "HPA · PDB · probes", C["teal"])]
    for x, t, sub, col in top:
        s.node(x, 40, 124, 58, t, sub, accent=col, mono=(t == "ACR"))
    for x in (140, 282, 424, 566):
        s.arrow([(x, 69), (x + 17, 69)], C["teal"])
    s.text(16, 168, "SRE LOOP", "gl", C["amber"])
    bottom = [(442, "Prometheus", "Azure Monitor · SLIs"), (300, "Burn-rate alert", "14.4x over 1h and 5m"),
              (158, "Incident runbook", "triage · rollback"), (16, "Error budget", "SLO 99.5% · 28 days")]
    for x, t, sub in bottom:
        s.node(x, 182, 124, 58, t, sub, accent=C["amber"])
    s.arrow([(646, 98), (646, 211), (567, 211)], C["amber"], label="metrics", lx=652, ly=160)
    for x in (442, 300, 158):
        s.arrow([(x, 211), (x - 17, 211)], C["amber"])
    s.arrow([(78, 182), (78, 99)], C["muted"], anim=False, dashed=True,
            label="budget spent → freeze releases", lx=86, ly=150)
    s.text(16, 286, "Validated with helm lint, helm template and a local smoke test in CI. "
           "Not deployed to a real AKS cluster.", "s")
    s.text(16, 304, "Chart: non-root container · liveness/readiness probes · HorizontalPodAutoscaler · "
           "PodDisruptionBudget", "s")
    return s


def hub_spoke():
    s = Svg(720, 380, "Terraform hub-and-spoke network on Azure",
            "Terraform provisions a hub VNet with firewall, gateway and shared-services subnets, Log Analytics and a "
            "Recovery Services vault. Two spoke VNets peer only with the hub and use default-deny NSGs, with a "
            "private DNS zone linked to the spokes. An optional VPN connects on-premises and an optional DR region "
            "uses Azure Site Recovery.")
    s.node(16, 40, 136, 104, "Terraform", None, accent=C["teal"],
           lines=["fmt · validate in CI", "locals.tags on all", "input validation", "safe defaults"])
    s.arrow([(152, 92), (189, 92)], C["teal"], label="provisions", lx=152, ly=84)
    s.group(190, 30, 262, 246, "Hub VNet · 10.10.0.0/22")
    s.node(206, 58, 230, 36, "AzureFirewallSubnet")
    s.node(206, 102, 230, 36, "GatewaySubnet")
    s.node(206, 146, 230, 36, "Shared services")
    s.node(206, 198, 110, 58, "Log Analytics", "retention cap", accent=C["amber"])
    s.node(326, 198, 110, 58, "Backup vault", "daily policy", accent=C["teal"])
    s.group(506, 30, 198, 104, "Spoke · 10.11.0.0/24", C["teal"])
    s.node(520, 62, 170, 56, "Portfolio app", "subnet · NSG default deny", accent=C["violet"])
    s.group(506, 150, 198, 104, "Spoke · 10.12.0.0/24", C["teal"])
    s.node(520, 182, 170, 56, "Reporting", "subnet · NSG default deny", accent=C["violet"])
    s.arrow([(453, 82), (505, 82)], both=True, anim=False, label="peering", lx=458, ly=74)
    s.arrow([(453, 202), (505, 202)], both=True, anim=False, label="peering", lx=458, ly=194)
    s.node(506, 276, 198, 50, "Private DNS zone", "linked to both spokes", accent=C["azure"])
    s.node(16, 178, 136, 56, "On-premises", "optional S2S VPN", dashed=True, accent=C["muted"])
    s.arrow([(152, 206), (170, 206), (170, 120), (205, 120)], C["muted"], anim=False, dashed=True)
    s.node(190, 304, 262, 50, "DR region (optional)", "secondary vault · Site Recovery", dashed=True,
           accent=C["muted"])
    s.arrow([(381, 257), (381, 303)], C["muted"], anim=False, dashed=True)
    s.text(16, 300, "Spokes reach each", "s")
    s.text(16, 314, "other only via hub", "s")
    s.text(16, 344, "Firewall and VPN", "s")
    s.text(16, 358, "gateway not created", "s")
    s.text(16, 372, "(cost control)", "s")
    return s


def sre_obs():
    s = Svg(720, 350, "SRE observability: SLO burn-rate alerting and incident flow",
            "An instrumented orders service is scraped by Prometheus, which computes error ratios and multi-window "
            "burn-rate alerts tested with promtool. Alertmanager routes pages and tickets; runbooks and a blameless "
            "RCA close the loop. Grafana shows the SLO dashboard, and an offline error-budget calculator can gate "
            "releases.")
    s.node(16, 40, 132, 58, "Orders service", "/metrics · fault inject")
    s.node(170, 40, 132, 58, "Prometheus", "rules 5m · 30m · 1h · 6h", accent=C["amber"])
    s.node(324, 40, 132, 58, "Burn-rate alerts", "promtool unit-tested", accent=C["amber"])
    s.node(478, 40, 120, 58, "Alertmanager", "inhibit · grouping", accent=C["amber"])
    s.node(618, 22, 88, 42, "Page", "on-call", accent="#f87171")
    s.node(618, 76, 88, 42, "Ticket", "backlog", accent=C["azure"])
    for x in (148, 302, 456):
        s.arrow([(x, 69), (x + 21, 69)], C["amber"])
    s.arrow([(598, 60), (608, 60), (608, 43), (617, 43)], C["amber"], anim=False)
    s.arrow([(598, 78), (608, 78), (608, 97), (617, 97)], C["amber"], anim=False)
    s.node(170, 150, 132, 58, "Grafana", "availability · burn · p95", accent=C["teal"])
    s.arrow([(236, 98), (236, 149)], C["teal"])
    s.node(478, 150, 120, 58, "Runbooks", "burn · latency", accent=C["teal"])
    s.node(324, 150, 132, 58, "Blameless RCA", "template + example", accent=C["teal"])
    s.arrow([(538, 98), (538, 149)], C["teal"])
    s.arrow([(478, 179), (457, 179)], C["teal"])
    s.text(16, 248, "OFFLINE GATE", "gl", C["violet"])
    s.node(16, 260, 132, 58, "Synthetic traffic", "3 days + incident", accent=C["muted"])
    s.node(170, 260, 132, 58, "error_budget.py", "budget used · alerts", accent=C["violet"], mono=False)
    s.node(324, 260, 132, 58, "Release gate", "exit 2 blocks release", accent=C["violet"])
    s.arrow([(148, 289), (169, 289)], C["violet"])
    s.arrow([(302, 289), (323, 289)], C["violet"])
    s.group(478, 236, 228, 100, "SLO 99.5% · 30 days", C["amber"])
    s.text(490, 274, "page    14.4x   1h + 5m", "m")
    s.text(490, 292, "page    6x      6h + 30m", "m")
    s.text(490, 310, "ticket  1x      3d + 6h", "m")
    return s


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in (("platform-architecture", hero), ("devsecops-pipeline", devsecops),
                     ("aks-sre-architecture", aks), ("hub-spoke", hub_spoke),
                     ("sre-observability", sre_obs)):
        (OUT / f"{name}.svg").write_text(fn().render(), encoding="utf-8")
        print("wrote", name)


if __name__ == "__main__":
    main()
