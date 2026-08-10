"""factory_claim.py — the polling and claiming tool (T-05, D-05).

It is how an agent takes work, and it is the only thing standing between two agents and the
same issue.

THE CLAIM IS A REF CREATION, NOT AN ASSIGNMENT (D-05). `factory_gh.create_ref` is a
create-if-absent decided by the server: exactly one concurrent creator can receive a create, so
its return value is the ONLY thing this tool trusts to decide ownership. The label
`factory:claimed`, the assignee and the `building` station are written only by the winner, are
purely operator-visible bookkeeping, and never decide anything (DESIGN.md C-2).

C-3's stream split is absolute here: the single JSON payload on success is the ONLY thing this
tool ever writes to stdout. Every diagnostic — no work available, a skip and its reason, a lost
race, a warning — goes to stderr.

THE BLOCKER GATE (DESIGN.md C-2's amendment, D-01 as amended 2026-08-08) sits after the
self-ownership branch and before `create_ref`: a candidate whose plan dependencies are unfinished
is never claimed, but a candidate this agent already owns is never re-gated. The DAG authority is
`plan.yaml`'s `depends_on` — read-only, never GitHub's rendered `blocked_by` edge — resolved to an
issue number through that feature's `feature.yaml` `factory.issues` map, and finished-ness is
that issue's state. An issue with no resolvable `feature:` label has no plan task and is not
gated at all (D-09's tolerant read); a `feature:` label that resolves but whose title yields no
matching plan task is edge (i) and counts as blocked.

FEATURES_ROOT is resolved under `factory_config.harness_root()`, never the current working
directory — this tool runs from inside a workspace checkout of ANOTHER repository (T-06), and a
cwd-relative path would silently read the wrong DAG or none at all (R-03).
"""
import argparse
import os
import re
import sys

import factory_cli
import factory_config
import factory_gh
import harness_yaml

TOOL = "claim"

# Overridable for tests — read as a module global inside _main/_BlockerCache, never bound as a
# default argument value, so a test monkeypatching this attribute after import is honoured.
FEATURES_ROOT = os.path.join(factory_config.harness_root(), ".harness", "features")

_TASK_ID_RE = re.compile(r"(T-\d+)")


def _feature_of(labels):
    """Return (feature_id_or_None, warnings) from an issue's `labels` list of {"name": str}.
    The first `feature:` label in sorted order wins; every other one is reported as a warning
    string (unprefixed — the caller adds the "factory: claim:" prefix)."""
    names = sorted(l.get("name", "") for l in labels if isinstance(l, dict))
    feats = [n[len("feature:"):] for n in names if n.startswith("feature:")]
    if not feats:
        return None, []
    warnings = []
    if len(feats) > 1:
        warnings.append(
            f"issue carries multiple feature: labels {feats!r} — using {feats[0]!r}"
        )
    return feats[0], warnings


def _task_id_from_title(title):
    m = _TASK_ID_RE.search(title or "")
    return m.group(1) if m else None


def _repo_name_of(item):
    """TAKE THE REPOSITORY FROM content.repository, NOT the item's `repository` key — the URL
    and the owner/name form name the same repository but only the latter matches the fleet."""
    content = item.get("content") or {}
    repo = content.get("repository")
    if repo:
        return repo
    url = item.get("repository") or ""
    parts = url.rstrip("/").split("/")
    normalised = "/".join(parts[-2:]) if len(parts) >= 2 else url
    print(
        f"factory: {TOOL}: item #{content.get('number')} carries no content.repository — "
        f"normalised {url!r} to {normalised!r}",
        file=sys.stderr,
    )
    return normalised


class _BlockerCache:
    """Caches each feature's plan.yaml and feature.yaml so a single poll reads each file once —
    the cost model is per-blocker `issue_view` reads, not per-file reads (DESIGN.md C-2
    amendment)."""

    def __init__(self, features_root):
        self._features_root = features_root
        self._plans = {}
        self._issue_maps = {}

    def task(self, feature, task_id):
        """The plan task dict for (feature, task_id), or None when the feature's plan.yaml
        cannot be read, or contains no task with that id."""
        if feature not in self._plans:
            path = os.path.join(self._features_root, feature, "plan.yaml")
            try:
                plan = harness_yaml.load_plan(path)
            except harness_yaml.YamlParseError:
                plan = None
            self._plans[feature] = plan
        plan = self._plans[feature]
        if plan is None or task_id is None:
            return None
        for t in plan["tasks"]:
            if str(t["id"]) == task_id:
                return t
        return None

    def issue_number(self, feature, task_id):
        """The blocker's issue number from that feature's feature.yaml `factory.issues` map, or
        None when it is unresolvable."""
        if feature not in self._issue_maps:
            path = os.path.join(self._features_root, feature, "feature.yaml")
            try:
                doc = harness_yaml.load_file(path)
            except harness_yaml.YamlParseError:
                doc = None
            issues = {}
            if isinstance(doc, dict):
                f = doc.get("factory")
                if isinstance(f, dict) and isinstance(f.get("issues"), dict):
                    issues = {str(k): v for k, v in f["issues"].items()}
            self._issue_maps[feature] = issues
        return self._issue_maps[feature].get(task_id)


def _blocker_gate(cache, repo, feature, task_id):
    """Return None when the candidate is clear, or a tuple describing why it is blocked:
    ("edge_i", task_id) — the feature resolves but the title yields no matching plan task;
    ("unresolvable", dep) — a depends_on entry has no feature.yaml issue-map entry;
    ("open", dep, blocker_num) — the LAST depends_on entry (in order) whose blocker issue is
    still open — scanning every entry, never stopping at the first, is what MIXED BLOCKER SET
    requires (T-05 intent, SC-22)."""
    task = cache.task(feature, task_id)
    if task is None:
        return ("edge_i", task_id)
    depends_on = [str(d) for d in (task.get("depends_on") or [])]
    if not depends_on:
        return None

    for dep in depends_on:
        if cache.issue_number(feature, dep) is None:
            return ("unresolvable", dep)

    open_blocker = None
    for dep in depends_on:
        blocker_num = cache.issue_number(feature, dep)
        state = factory_gh.issue_view(repo, blocker_num, ["state"]).get("state")
        if state != "CLOSED":
            open_blocker = (dep, blocker_num)
    if open_blocker is not None:
        return ("open",) + open_blocker
    return None


def _blocker_reason_text(gate, num):
    kind = gate[0]
    if kind == "edge_i":
        return (
            f"issue #{num} carries a feature: label that resolves, but its title yields no "
            f"matching plan task (edge (i), lost task identity)"
        )
    if kind == "unresolvable":
        dep = gate[1]
        return (
            f"issue #{num} depends_on {dep}, which has no recorded issue in feature.yaml "
            f"(unresolvable blocker)"
        )
    dep, blocker_num = gate[1], gate[2]
    return f"issue #{num} is blocked by {dep} (issue #{blocker_num}), which is still open"


def _emit(repo, num, issue):
    labels = issue.get("labels") or []
    feature, warnings = _feature_of(labels)
    for w in warnings:
        print(f"factory: {TOOL}: {w}", file=sys.stderr)
    factory_cli.payload({
        "repo": repo,
        "issue": num,
        "title": issue.get("title"),
        "branch": f"factory/issue-{num}",
        "feature": feature,
    })


def _main():
    parser = argparse.ArgumentParser(prog="factory_claim")
    parser.add_argument("--as", dest="as_login", required=True)
    parser.add_argument("--repo", default=None)
    parser.add_argument("--issue", type=int, default=None)
    parser.add_argument("--fleet", default=None)
    args = parser.parse_args()

    fleet_path = args.fleet if args.fleet else factory_config.FLEET_PATH
    fleet = factory_config.load_fleet(args.fleet) if args.fleet else factory_config.load_fleet()

    # 1. preflight — a missing or unauthenticated gh raises GhError, exits 2 via the wrapper.
    factory_gh.preflight()

    owner = fleet["board"]["owner"]
    board_number = fleet["board"]["number"]
    station_field = fleet["board"]["station_field"]
    stations = fleet["board"]["stations"]

    # 2. validate the fleet's three station option names against the board, BEFORE any board
    # read — a mismatch here is otherwise indistinguishable from an empty queue forever.
    options = factory_gh.project_field_options(owner, board_number, station_field)
    for key in ("ready", "building", "review"):
        opt = stations[key]
        if opt not in options:
            factory_cli.refuse(
                TOOL, "station option not offered by the board", opt,
                f"field {station_field!r} on {owner} project {board_number} does not offer it "
                f"— check {fleet_path}",
            )

    # 3. read the board.
    ready_option = stations["ready"]
    if args.issue is not None:
        raw_items = factory_gh.project_items(owner, board_number, query="is:open")
        raw_items = [
            it for it in raw_items if (it.get("content") or {}).get("number") == args.issue
        ]
        if not raw_items:
            factory_cli.refuse(
                TOOL, "issue not found on the board", args.issue,
                f"board {owner}/{board_number}",
            )
    else:
        query = f'{station_field}:"{ready_option}" is:open'
        raw_items = factory_gh.project_items(owner, board_number, query=query)

    # 4. keep candidates whose repository is listed in the fleet, filtered to --repo, sorted.
    repo_names = {e["name"] for e in fleet["repos"]}
    candidates = []
    for it in raw_items:
        repo_name = _repo_name_of(it)
        if repo_name not in repo_names:
            continue
        if args.repo and repo_name != args.repo:
            continue
        num = (it.get("content") or {}).get("number")
        if num is None:
            continue
        candidates.append((num, repo_name, it))
    candidates.sort(key=lambda c: c[0])

    if not candidates:
        factory_cli.nothing_to_do(TOOL, "no work available")

    # 5. the candidate loop.
    cache = _BlockerCache(FEATURES_ROOT)
    winner = None
    for num, repo_name, item in candidates:
        issue = factory_gh.issue_view(
            repo_name, num, ["number", "title", "state", "assignees", "labels"],
        )
        labels = [l.get("name", "") for l in (issue.get("labels") or [])]
        assignees = issue.get("assignees") or []

        # 5a. self-ownership FIRST, and only under --issue — must precede every skip below,
        # or an issue this agent owns (which satisfies every skip condition) is unreachable.
        if args.issue is not None and "factory:claimed" in labels and any(
            a.get("login") == args.as_login for a in assignees
        ):
            _emit(repo_name, num, issue)
            sys.exit(0)

        if issue.get("state") != "OPEN":
            print(f"factory: {TOOL}: skip #{num} — issue is not open", file=sys.stderr)
            continue
        if "factory:claimed" in labels:
            print(
                f"factory: {TOOL}: skip #{num} — already carries factory:claimed",
                file=sys.stderr,
            )
            continue
        if assignees:
            print(f"factory: {TOOL}: skip #{num} — already assigned", file=sys.stderr)
            continue

        # 5a-bis. THE BLOCKER GATE — after self-ownership, before create_ref.
        feature, feature_warnings = _feature_of(issue.get("labels") or [])
        for w in feature_warnings:
            print(f"factory: {TOOL}: {w}", file=sys.stderr)
        if feature is not None:
            task_id = _task_id_from_title(issue.get("title") or "")
            gate = _blocker_gate(cache, repo_name, feature, task_id)
            if gate is not None:
                reason = _blocker_reason_text(gate, num)
                if args.issue is not None:
                    factory_cli.refuse(
                        TOOL, "blocked by an unfinished dependency", num, reason,
                    )
                print(f"factory: {TOOL}: skip #{num} — {reason}", file=sys.stderr)
                continue

        # 5b. THE POINT OF NO RETURN. The return value of create_ref decides ownership.
        entry = factory_config.repo_entry(fleet, repo_name)
        sha = factory_gh.default_branch_sha(repo_name, entry["default_branch"])
        ref = f"refs/heads/factory/issue-{num}"
        ok = factory_gh.create_ref(repo_name, ref, sha)
        if not ok:
            if args.issue is not None:
                factory_cli.lost_race(
                    TOOL, "claim ref already exists", num, f"{ref} already exists",
                )
            print(f"factory: {TOOL}: skip #{num} — {ref} already exists", file=sys.stderr)
            continue

        winner = (num, repo_name, item, issue)
        break

    # 5c. exhausted without a win.
    if winner is None:
        factory_cli.nothing_to_do(TOOL, "no claimable work")

    # 6. winner only — bookkeeping, in order, after ownership is already decided.
    num, repo_name, item, issue = winner
    item_id = item.get("id")
    factory_gh.add_label(repo_name, num, "factory:claimed")
    factory_gh.assign(repo_name, num, args.as_login)
    factory_gh.project_field_set(owner, board_number, item_id, station_field, stations["building"])

    # 7. the single stdout payload.
    _emit(repo_name, num, issue)


if __name__ == "__main__":
    factory_cli.run(TOOL, _main, expected=(factory_config.FleetError, factory_gh.GhError))
