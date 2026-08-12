#!/usr/bin/env python3
"""factory_decompose.py — turn one approved plan into work items on the board (T-04, D-14).

Command line: factory_decompose.py <feature-dir> --repo <owner/name> [--fleet <path>]
[--parent <n>].

Behaviour is documented step-by-step in plan.yaml T-04's intent and in DESIGN.md C-3/C-4/C-5.
In short: load and validate the fleet and the signed plan, ensure the factory's label
vocabulary, validate the fleet's declared stations against the board's real field options
(step 3b), adopt-or-create a parent issue, create one issue per not-yet-published task, add
each to the board, then draw the DAG (sub-issue + blocked_by edges) in a second pass so edge
correctness never depends on plan task order. Every receipt (issue number, item id, edge) is
written back into <feature-dir>/feature.json's `factory` block ATOMICALLY, so an interrupted
run resumes instead of duplicating (D-14). The item id specifically is written back only after
`project_field_set` returns (T-04 defect fix) — not immediately after the board add — so the
ledger never claims a task is ready to claim when the station-set that makes it claimable has
in fact failed.

The only harness file this tool writes is feature.json, and the write is a read-modify-write
over the whole document: load it, set the `factory` key, json.dump the whole thing back —
preserving every other top-level key (a `github:` block from gh-sync.py included) unchanged.
plan.yaml and BRIEF.md are read-only inputs and are never written (D-01, SC-03, SC-20).
"""
import argparse
import json
import os
import re
import sys
import tempfile

import factory_cli
import factory_config
import factory_gh
import harness_yaml

# DEC-138 amendment 3, applied mechanically per task.
CHORE_TYPES = {"config", "scaffolding", "infra", "ci"}
BUG_TYPES = {"bugfix"}

TOOL = "decompose"


# --------------------------------------------------------------------------
# BRIEF.md extraction — a READ ONLY, guarded extraction. Any failure, for any
# reason, yields (None, None); nothing here ever raises, and nothing here
# ever invents text.
# --------------------------------------------------------------------------

def _section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return None
    body = m.group(1).strip()
    return body or None


def _first_sentence(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)
    return parts[0].strip() if parts and parts[0].strip() else text.strip()


def extract_brief(feat_dir):
    """Return (problem, goal) or (None, None) on ANY extraction failure — a missing file, a
    misspelled or mis-cased heading, an empty section, an unreadable or malformed file. Never
    invents text and never raises: a publish must not be blocked by prose the operator can
    edit afterwards (T-04 step 5b)."""
    try:
        path = os.path.join(feat_dir, "BRIEF.md")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        problem = _section(text, "Problem")
        goal = _section(text, "Goal")
        if problem is None or goal is None:
            return None, None
        return problem, goal
    except Exception:
        return None, None


# --------------------------------------------------------------------------
# The factory block — load, normalize, atomically write.
# --------------------------------------------------------------------------

def _empty_factory():
    return {
        "repo": None,
        "parent": None,
        "parent_origin": None,
        "issues": {},
        "items": {},
        "edges": {"parent": [], "blocked_by": {}},
    }


def load_factory(feat_dir):
    path = os.path.join(feat_dir, "feature.json")
    factory = _empty_factory()
    if not os.path.exists(path):
        return factory
    doc = harness_yaml.load_file(path)
    if not isinstance(doc, dict):
        return factory
    f = doc.get("factory")
    if not isinstance(f, dict):
        return factory

    repo = f.get("repo")
    factory["repo"] = repo if isinstance(repo, str) and repo else None

    parent = f.get("parent")
    if isinstance(parent, int) and not isinstance(parent, bool):
        factory["parent"] = parent

    po = f.get("parent_origin")
    factory["parent_origin"] = po if po in ("adopted", "created") else None

    issues = f.get("issues")
    if isinstance(issues, dict):
        for k, v in issues.items():
            if isinstance(v, int) and not isinstance(v, bool):
                factory["issues"][str(k)] = v

    items = f.get("items")
    if isinstance(items, dict):
        for k, v in items.items():
            factory["items"][str(k)] = v

    edges = f.get("edges")
    if isinstance(edges, dict):
        parent_edges = edges.get("parent")
        if isinstance(parent_edges, list):
            factory["edges"]["parent"] = [str(x) for x in parent_edges]
        blocked = edges.get("blocked_by")
        if isinstance(blocked, dict):
            for k, v in blocked.items():
                if isinstance(v, list):
                    factory["edges"]["blocked_by"][str(k)] = [str(x) for x in v]

    return factory


def write_factory(feat_dir, factory):
    """Write the `factory:` key into feature.json by read-modify-write, ATOMICALLY.

    Load the document (or start from an empty one when the file does not exist yet) -> set
    its `factory` key to the mapping below -> json.dump the whole document back to a temp
    file created in the SAME DIRECTORY -> fsync -> os.replace onto feature.json. Every other
    top-level key (a `github:` block from gh-sync.py included) round-trips unchanged.
    feature.json itself is opened only for reading, never in a truncating mode: every
    observer sees either the previous complete file or the next one, never a partial one
    (T-04 step 8, carried forward by FEAT-14 T-05)."""
    path = os.path.join(feat_dir, "feature.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            doc = json.load(f)
        if not isinstance(doc, dict):
            doc = {}
    else:
        doc = {}
    doc["factory"] = {
        "repo": factory["repo"],
        "parent": factory["parent"],
        "parent_origin": factory["parent_origin"],
        "issues": dict(sorted(factory["issues"].items())),
        "items": dict(sorted(factory["items"].items())),
        "edges": {
            "parent": list(factory["edges"]["parent"]),
            "blocked_by": {k: list(v) for k, v in sorted(factory["edges"]["blocked_by"].items())},
        },
    }
    text = json.dumps(doc, indent=2) + "\n"

    dirpath = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(prefix=".feature.json.", suffix=".tmp", dir=dirpath)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# --------------------------------------------------------------------------
# Disposition sorting (T-04 step 4).
# --------------------------------------------------------------------------

def _owes_edges(task, factory):
    tid = str(task["id"])
    if tid not in factory["edges"]["parent"]:
        return True
    recorded = set(factory["edges"]["blocked_by"].get(tid, []))
    for d in (task.get("depends_on") or []):
        if str(d) not in recorded:
            return True
    return False


def sort_dispositions(tasks, factory):
    """Return {task_id: 'full'|'partial'|'new'|'edges_unwritten'}."""
    out = {}
    for t in tasks:
        tid = str(t["id"])
        has_issue = tid in factory["issues"]
        has_item = tid in factory["items"]
        if has_issue and has_item:
            out[tid] = "edges_unwritten" if _owes_edges(t, factory) else "full"
        elif has_issue and not has_item:
            out[tid] = "partial"
        else:
            out[tid] = "new"
    return out


# --------------------------------------------------------------------------
# Station validation (T-04 defect fix, deliverable 4 — a declared widening beyond the signed
# plan). Called at step 3/4, before ensure_labels (step 5, THE POINT OF NO RETURN per
# plan.yaml:818-830). Deliberately NOT inside preflight() — plan.yaml:412 signs preflight() as
# `auth status` only and plan.yaml:1270 tests a monkeypatched preflight raising GhError; widening
# that signature would break a signed test for no gain.
# --------------------------------------------------------------------------

def _validate_stations(owner, board_number, station_field, stations):
    """Validate every fleet station name against the board's real field options before anything
    is created. Two failure modes of factory_gh.project_field_options: the FIELD itself missing
    (it raises GhError naming the field, propagated unchanged) and an OPTION missing (it returns
    a list and this function produces the message, naming the offending station key, its
    configured value, and the board's real options)."""
    options = factory_gh.project_field_options(owner, board_number, station_field)
    for key, value in stations.items():
        if value not in options:
            factory_cli.refuse(
                TOOL, "station option not offered by the board", f"{key}={value!r}",
                f"field {station_field!r} on {owner} project {board_number} offers: "
                + ", ".join(options),
            )


# --------------------------------------------------------------------------
# Re-add resolution (T-04 defect fix, deliverable 3, option ii). On the `partial` recovery path
# only: resolve an already-added board item before calling project_item_add again, since
# `gh project item-add` on an already-added issue is UNVERIFIED to be idempotent. The resolution
# is one targeted, repository-scoped GraphQL lookup through factory_gh.issue_board_item_id,
# which needs no client-side repository matching.
# --------------------------------------------------------------------------

def _find_existing_item_id(board_number, repo, issue_number):
    """Deliberately unscoped by issue STATE, by construction: this looks up whether ONE
    SPECIFIC issue already has a board item, not whether it is currently claimable —
    factory_claim.py's `is:open` scoping serves a different purpose (polling for open work) and
    would silently miss the issue if it were closed between the failed run and this recovery
    run, which would re-trigger the exact re-add this function exists to avoid. The new query is
    scoped to a repository and an issue number with no state filter at all. Confirmed live on
    2026-08-10, read-only, against board 3: the targeted repository.issue.projectItems query
    returned the board item for an issue in the CLOSED state — that observation is the property
    this whole feature rests on. The truncation guard now lives in
    factory_gh.issue_board_item_id, which raises when the issue is on more projects than the
    query returns."""
    return factory_gh.issue_board_item_id(repo, issue_number, board_number)


# --------------------------------------------------------------------------
# The publish itself.
# --------------------------------------------------------------------------

def _issue_body(task):
    ct = task["change_type"]
    traces = ", ".join(str(t) for t in (task.get("traces") or []))
    return f"{task['intent'].strip()}\n\nchange_type: {ct}\ntraces: {traces}"


def _task_labels(task, feat_id):
    labels = ["harness", f"feature:{feat_id}"]
    ct = task["change_type"]
    if ct in CHORE_TYPES:
        labels.append("chore")
    elif ct in BUG_TYPES:
        labels.append("bug")
    return labels


def _main():
    parser = argparse.ArgumentParser(prog="factory_decompose")
    parser.add_argument("feature_dir")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--fleet", default=None)
    parser.add_argument("--parent", type=int, default=None)
    args = parser.parse_args()

    feat_dir = args.feature_dir

    # 1. fleet + repo.
    fleet = factory_config.load_fleet(args.fleet) if args.fleet else factory_config.load_fleet()
    factory_config.repo_entry(fleet, args.repo)

    # 2. the signed plan.
    plan_path = os.path.join(feat_dir, "plan.yaml")
    plan = harness_yaml.load_plan(plan_path)
    approval = plan.get("approval") or {}
    if approval.get("status") != "approved":
        factory_cli.refuse(
            TOOL, "plan not signed", plan_path,
            "get the plan approved before publishing",
        )

    # 2b. a usable feature id — before preflight, so a bad plan costs zero remote calls.
    feat_id = plan.get("feature")
    if not isinstance(feat_id, str) or not feat_id.strip():
        factory_cli.refuse(
            TOOL, "plan has no usable feature id", plan_path,
            "add a top-level `feature: <FEAT-id>` key to the plan before publishing",
        )

    # 3. preflight.
    factory_gh.preflight()

    # 3b. hoisted board reads + station validation (T-04 defect fix, deliverable 4 — a declared
    # widening beyond the signed plan). Everything through step 4 mutates nothing
    # (plan.yaml:818-830), so validating here costs one field-list READ and stops a typo before
    # ensure_labels (step 5, the point of no return). fleet["board"] reads used to sit inside
    # step 7 alone (issue: T-04 defect fix); hoisted here rather than duplicated.
    owner = fleet["board"]["owner"]
    board_number = fleet["board"]["number"]
    station_field = fleet["board"]["station_field"]
    _validate_stations(owner, board_number, station_field, fleet["board"]["stations"])

    # 4. load the ledger and sort every task into a disposition.
    factory = load_factory(feat_dir)
    factory["repo"] = args.repo
    tasks = plan["tasks"]
    dispositions = sort_dispositions(tasks, factory)

    edges_drawn = 0
    edges_skipped = 0

    need_step5 = any(d == "new" for d in dispositions.values()) or factory["parent"] is None
    if need_step5:
        # THE POINT OF NO RETURN. The first remote write this tool makes.
        ensured = ["harness", f"feature:{feat_id}", "chore", "bug", "factory:claimed"]
        factory_gh.ensure_labels(args.repo, ensured)

        # 5b. the parent — adopt or create.
        if factory["parent"] is not None:
            print(
                f"factory: {TOOL}: parent #{factory['parent']} already recorded — skipping",
                file=sys.stderr,
            )
        elif args.parent is not None:
            factory["parent"] = args.parent
            factory["parent_origin"] = "adopted"
            write_factory(feat_dir, factory)
            factory_gh.add_label(args.repo, args.parent, f"feature:{feat_id}")
        else:
            problem, goal = extract_brief(feat_dir)
            if problem is None or goal is None:
                title = str(feat_id)
                body = ""
                print(
                    f"factory: {TOOL}: could not extract a problem/goal statement from "
                    f"BRIEF.md — creating the parent titled with the feature id alone",
                    file=sys.stderr,
                )
            else:
                title = f"{feat_id} — {_first_sentence(goal)}"
                body = f"{problem}\n\n**Goal:** {goal}"
            num = factory_gh.create_issue(
                args.repo, title, body, ["harness", f"feature:{feat_id}"],
            )
            factory["parent"] = num
            factory["parent_origin"] = "created"
            write_factory(feat_dir, factory)

    # 6. create an issue for every task in the third disposition (new).
    for t in tasks:
        tid = str(t["id"])
        if dispositions[tid] != "new":
            continue
        title = f"{tid} {t['title']}"
        num = factory_gh.create_issue(
            args.repo, title, _issue_body(t), _task_labels(t, feat_id),
        )
        factory["issues"][tid] = num
        write_factory(feat_dir, factory)

    # 7. add every task issue with no recorded item id to the board. The parent is NEVER added.
    # The item id is recorded ONLY after project_field_set returns (T-04 defect fix): recording
    # it the moment project_item_add returns left an orphan permanently invisible to
    # sort_dispositions whenever the station-set that follows raised — the ledger said "done"
    # while no agent could ever claim the task (fleet.yaml's `stations.ready` need only be one
    # character wrong for the board add to succeed and the station-set to fail forever).
    ready_option = factory_config.station(fleet, "ready")
    for t in tasks:
        tid = str(t["id"])
        disp = dispositions[tid]
        if disp not in ("new", "partial"):
            continue
        num = factory["issues"][tid]
        item_id = None
        if disp == "partial":
            # The board add may already have succeeded on an earlier, interrupted run whose
            # station-set then failed — resolve it rather than re-adding (deliverable 3).
            item_id = _find_existing_item_id(board_number, args.repo, num)
        if item_id is None:
            url = f"https://github.com/{args.repo}/issues/{num}"
            item_id = factory_gh.project_item_add(owner, board_number, url)
        factory_gh.project_field_set(owner, board_number, item_id, station_field, ready_option)
        factory["items"][tid] = item_id
        write_factory(feat_dir, factory)

    # 7b. the edge pass — a second pass, run after every issue in this publish exists.
    id_cache = {}

    def internal_id(num):
        if num not in id_cache:
            id_cache[num] = factory_gh.internal_id(args.repo, num)
        return id_cache[num]

    for t in tasks:
        tid = str(t["id"])
        if dispositions[tid] == "full":
            continue
        num = factory["issues"].get(tid)
        if num is None:
            continue

        if tid not in factory["edges"]["parent"]:
            child_id = internal_id(num)
            factory_gh.attach_sub_issue(args.repo, factory["parent"], child_id)
            factory["edges"]["parent"].append(tid)
            write_factory(feat_dir, factory)
            edges_drawn += 1

        recorded = factory["edges"]["blocked_by"].setdefault(tid, [])
        for dep in (t.get("depends_on") or []):
            dep = str(dep)
            if dep in recorded:
                continue
            blocker_num = factory["issues"].get(dep)
            if blocker_num is None:
                print(
                    f"factory: {TOOL}: {tid} blocked_by {dep} skipped — {dep} has no "
                    f"recorded issue yet",
                    file=sys.stderr,
                )
                edges_skipped += 1
                continue
            blocker_id = internal_id(blocker_num)
            try:
                factory_gh.blocked_by(args.repo, num, blocker_id)
            except factory_gh.GhError as e:
                combined = f"{e.stdout or ''}\n{e.stderr or ''}".lower()
                if "422" in combined and "already been taken" in combined:
                    print(
                        f"factory: {TOOL}: {tid} blocked_by {dep} already existed on "
                        f"GitHub — recording it",
                        file=sys.stderr,
                    )
                else:
                    raise
            recorded.append(dep)
            factory["edges"]["blocked_by"][tid] = recorded
            write_factory(feat_dir, factory)
            edges_drawn += 1

    # 8. the single stdout payload.
    factory_cli.payload({
        "repo": args.repo,
        "feature": feat_id,
        "parent": factory["parent"],
        "parent_origin": factory["parent_origin"],
        "issues": dict(factory["issues"]),
        "edges_drawn": edges_drawn,
        "edges_skipped": edges_skipped,
    })


if __name__ == "__main__":
    factory_cli.run(TOOL, _main, expected=(factory_config.FleetError, factory_gh.GhError))
