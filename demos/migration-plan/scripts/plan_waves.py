"""Group servers into migration waves from an inventory and dependency map.

Independent portfolio demo (synthetic data). Standard library only.

Rules used:
  1. Servers that talk to each other (directly or indirectly) form one
     "move group" and migrate in the same wave, so no cross-site latency
     appears between dependent tiers during cutover.
  2. Shared services (here: domain controllers) are excluded from grouping and
     go first in wave 0, because almost everything depends on them.
  3. Wave order: shared services, then dev/test pilots, then groups by rising
     criticality (low -> medium -> high), so lessons are learnt on safer moves.

Usage:
  python3 plan_waves.py inventory/servers.csv inventory/dependencies.csv > waves.md
"""
import csv
import sys
from collections import defaultdict

SHARED_ROLES = {"Domain controller"}
RANK = {"low": 0, "medium": 1, "high": 2}


def load(servers_path, deps_path):
    with open(servers_path, newline="") as f:
        servers = {row["server"]: row for row in csv.DictReader(f)}
    with open(deps_path, newline="") as f:
        deps = list(csv.DictReader(f))
    return servers, deps


def validate(servers, deps):
    """Return a list of problems found in the inputs."""
    problems = []
    for d in deps:
        for side in ("source", "target"):
            if d[side] not in servers:
                problems.append(f"dependency references unknown server {d[side]}")
    for name, s in servers.items():
        if s["criticality"] not in RANK:
            problems.append(f"{name}: unknown criticality {s['criticality']}")
        if not s["target_size"]:
            problems.append(f"{name}: missing target VM size")
    return problems


def move_groups(servers, deps):
    """Union-find over dependencies, ignoring shared services."""
    parent = {s: s for s in servers}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    shared = {n for n, s in servers.items() if s["role"] in SHARED_ROLES}
    for d in deps:
        a, b = d["source"], d["target"]
        if a in shared or b in shared:
            continue
        parent[find(a)] = find(b)

    groups = defaultdict(list)
    for n in servers:
        if n not in shared:
            groups[find(n)].append(n)
    return sorted(shared), [sorted(g) for g in groups.values()]


def plan(servers, deps):
    shared, groups = move_groups(servers, deps)
    waves = [("Wave 0 - shared services", shared)] if shared else []

    def key(group):
        is_dev = all(servers[s]["env"] != "prod" for s in group)
        crit = max(RANK[servers[s]["criticality"]] for s in group)
        return (0 if is_dev else 1, crit, group[0])

    for i, g in enumerate(sorted(groups, key=key), start=1):
        apps = sorted({servers[s]["app"] for s in g})
        waves.append((f"Wave {i} - {', '.join(apps)}", g))
    return waves


def to_markdown(servers, waves):
    out = ["# Migration waves (generated)", "",
           "> Independent portfolio demo. Synthetic inventory.", ""]
    for title, members in waves:
        out += [f"## {title}", "", "| Server | OS | Role | Criticality | Target size |",
                "|---|---|---|---|---|"]
        for s in members:
            r = servers[s]
            out.append(f"| {s} | {r['os']} | {r['role']} | {r['criticality']} | {r['target_size']} |")
        out.append("")
    return "\n".join(out)


def main(argv):
    servers, deps = load(argv[1], argv[2])
    problems = validate(servers, deps)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 1
    print(to_markdown(servers, plan(servers, deps)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
