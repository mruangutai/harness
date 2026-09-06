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
over the whole document -- load it, set the `factory` key, json.dump the whole thing back --
preserving every other top-level key (a `github:` block from gh-sync.py included) unchanged.
plan.yaml and BRIEF.md are read-only inputs and are never written (D-01, SC-03, SC-20).

That read-modify-write goes through feature_json_write.write_feature_json (DEC-199,
stale-anchor-write-hazard), the same locked, schema-ratcheted entry point gh-sync.py's three
call sites already share: the fcntl lock on feature.json's sibling `.lock` file, the
same-directory tempfile, fsync and atomic rename this module's own `write_factory` used to
carry as a private, unlocked, unvalidated copy. `write_factory` may legitimately be the
FIRST writer of a feature's feature.json (T-c4) -- this tool is a standalone CLI entry point,
never guaranteed the orchestrator has instantiated one first -- so every internal call below
passes the plan's own `feature:` id, and an absent file is created fresh rather than refused.
See the feature's receipt for the fuller argument.
"""
import argparse
import json
import os
import re
import sys

import factory_cli
import factory_config
import factory_gh
import feature_json_write
import gh_issue_types
import harness_merge
import harness_yaml

# DEC-138, applied mechanically per task - but ONLY in compatibility mode (T-08, FEAT-55).
# Where the target repository declares native GitHub Issue Types, an issue's type comes
# from gh_issue_types.py's mapping instead, applied via factory_gh.apply_issue_type after
# create, and neither of these two labels is added. This label pair is what a repository
# with no Issue Types declared still gets.
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
        "issues": {},
        "items": {},
        "edges": {"parent": [], "blocked_by": {}},
        "typed": {},
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

    # T-08: provenance is positive and absence means unknown (D-20) - only the three
    # legal recorded values survive the read, so a corrupt or hand-edited entry is
    # treated the same as absent rather than typed on a later run.
    typed = f.get("typed")
    if isinstance(typed, dict):
        for k, v in typed.items():
            if v is True or (isinstance(v, str) and v in ("created", "adopted")):
                factory["typed"][str(k)] = v

    return factory


# feat_dir is a plain CLI positional argument (factory_decompose is a general-purpose tool
# pointed at ANY feature directory, not just one nested under .harness/*/features/*/ -- see
# test-factory-integration.py's own decompose fixtures at :635-636 and :708-709, which run
# the standalone CLI against a bare tmp dir). write_factory therefore enforces only that the
# resolved path is named feature.json, never the canonical harness layout gh-sync.py's own
# callers stay constrained to (feature_json_write.FEATURE_JSON_TAIL, unchanged by this).
FEATURE_JSON_BASENAME_TAIL = re.compile(r"(?:^|/)feature\.json$")


def _factory_block(factory):
    """Build the `factory:` dict written into feature.json (pure extraction from
    `write_factory`'s `transform` closure; see that function for context)."""
    return {
        "repo": factory["repo"],
        "parent": factory["parent"],
        "issues": dict(sorted(factory["issues"].items())),
        "items": dict(sorted(factory["items"].items())),
        "edges": {
            "parent": list(factory["edges"]["parent"]),
            "blocked_by": {k: list(v)
                           for k, v in sorted(factory["edges"]["blocked_by"].items())},
        },
        "typed": dict(sorted(factory.get("typed", {}).items())),
    }


def write_factory(feat_dir, factory, feat_id=None):
    """Write the `factory:` key into feature.json through
    feature_json_write.write_feature_json (DEC-199, stale-anchor-write-hazard cycle 3): the
    same fcntl lock on feature.json's sibling `.lock` file, same-directory tempfile, fsync
    and atomic rename this function's own private `_atomic_write`-shaped primitive gave it,
    now shared with gh-sync.py's three call sites instead of duplicated a third time. Every
    other top-level key (a `github:` block from gh-sync.py included) round-trips unchanged.
    A candidate that would introduce a schema problem the base did not already carry is
    refused by write_feature_json itself (feature_schema.py, monotonic non-regression) and
    leaves feature.json byte-for-byte unchanged.

    CREATION IS AN EXPLICIT OPT-IN (stale-anchor-write-hazard T-c4, replacing cycle 3's
    hand-copied never-create refusal). Cycle 3's docstring argued "no caller of write_factory
    ... is ever legitimately the FIRST writer" because "the orchestrator instantiates it ...
    well before decompose ever runs" -- FALSE, and test-factory-integration.py is the counter-
    evidence: factory_decompose is a standalone CLI entry point, and its own fixtures run
    `decompose` against a feature dir holding only plan.yaml, with no feature.json ever
    created first (see the module docstring above and this feature's receipt).

    `feat_id` is that opt-in: `_main` always has one by this point (step 2b validates
    `plan.yaml`'s top-level `feature:` key before any write_factory call), so every one of
    this module's five internal call sites passes it, and creation succeeds. A caller that
    omits it -- the shape every gh-sync.py call site uses for the SAME absent-file decision
    (save_recorded, _record_status, _record_pr all refuse before ever calling
    write_feature_json) -- still gets the old refusal: nothing here can accidentally mint a
    document with only a `factory` key and none of feature-schema.json's other seven required
    keys, because without a feature_id there is no way to build a schema-clean one.
    """
    path = os.path.join(feat_dir, "feature.json")
    absent_message = (
        f"{path}: feature.json is absent and no feature id was given to create one. "
        f"Pass feat_id (this module's own `_main` derives it from plan.yaml's `feature:` "
        f"key) or run this feature through the orchestrator's normal cycle first."
    )

    def transform(base):
        if base is None:
            if feat_id is None:
                raise harness_merge.MergeRefusal(9, [absent_message])
            # NO `status` KEY (FEAT-41 T-07). This wrote the plan station into feature.json,
            # which the schema's additionalProperties now REFUSES — so the seven keys below are
            # the whole required set. The new feature's station is recorded in plan.yaml, by
            # `plan-merge.py set-feature-station`, and this function never writes it: it is
            # reached from the factory lane with a plan already on disk, and inventing a station
            # here would be a second writer of the one field that must have exactly one.
            doc = {
                "feature_id": feat_id,
                "branch": "none",
                "pr": None,
                "review_sha": "none",
                "cycles_used": 0,
                "max_total_cycles": 10,
                "runs": [],
            }
        else:
            doc = json.loads(base.decode("utf-8"))
            if not isinstance(doc, dict):
                doc = {}
        doc["factory"] = _factory_block(factory)
        return json.dumps(doc, indent=2) + "\n"

    feature_json_write.write_feature_json(path, transform, tail_regex=FEATURE_JSON_BASENAME_TAIL)


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
    """Validate every declared station against the board's real field options before anything is
    created. Two failure modes of factory_gh.project_field_options: the FIELD itself missing (it
    raises GhError naming the field, propagated unchanged) and an OPTION missing (it returns a
    list and this function produces the message, naming the offending station, the COLUMN it
    requires, and the board's real options).

    `stations` is now a SEQUENCE of lowercase station names, not a mapping of names to
    operator-chosen columns (FEAT-41 T-02), so the column each one requires is derived here by
    factory_config.station_column rather than read out of the declaration."""
    options = factory_gh.project_field_options(owner, board_number, station_field)
    for name in stations:
        column = factory_config.station_column(name)
        if column not in options:
            factory_cli.refuse(
                TOOL, "station option not offered by the board", f"{name}={column!r}",
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


def _task_labels(task, feat_id, state):
    labels = ["harness", f"feature:{feat_id}"]
    if state != "available":
        ct = task["change_type"]
        if ct in CHORE_TYPES:
            labels.append("chore")
        elif ct in BUG_TYPES:
            labels.append("bug")
    return labels


# --------------------------------------------------------------------------
# Issue Types (T-08, FEAT-55). D-18: a task issue's type is ALWAYS resolved through
# type_for_change_type and a parent's ALWAYS through type_for_parent - no task issue on any
# route ever carries the parent's type. D-20: factory["typed"] is positive provenance;
# absence is UNKNOWN and is never typed, this run or any later one.
# --------------------------------------------------------------------------

def _issue_type_overrides(fleet, repo):
    """The target repository's OWN github.issue_types overrides. Capability is per target
    repository and is never inherited; a FleetError (the repo's harness.json is unreadable
    or invalid) yields {} so the defaults apply rather than aborting the run."""
    try:
        return gh_issue_types.overrides_from_config(factory_config.product_config(fleet, repo))
    except factory_config.FleetError:
        return {}


def _print_issue_types_state(repo, state, message):
    """Exactly one diagnostic line when native Issue Types are not usable - printed
    unconditionally, even on a run that creates nothing (T-07 case G)."""
    if state == "absent":
        print(f"factory: issue types unavailable on {repo} - labels only", file=sys.stderr)
    elif state == "query_failed":
        print(
            f"factory: issue types could not be determined on {repo} ({message}) - "
            f"labels only",
            file=sys.stderr,
        )


def _task_issue_type(task, overrides):
    """(type name, canonical config key) for one task's issue. An UnknownWorkNature is a
    caller error - print it and exit 2, never let it propagate as an unhandled failure."""
    change_type = task["change_type"]
    try:
        type_name = gh_issue_types.type_for_change_type(change_type, overrides)
    except gh_issue_types.UnknownWorkNature as e:
        print(f"factory: {TOOL}: {e}", file=sys.stderr)
        sys.exit(factory_cli.EXIT_REFUSED)
    return type_name, gh_issue_types.DEFAULT_TYPE_BY_CHANGE_TYPE[change_type]


def _required_issue_types(tasks, dispositions, factory, overrides, need_parent_create):
    """Every (type name, config key) this run must have declared before any create or
    backfill apply - the issues about to be created AND the backfill set step 8 will apply
    (T-07 case J: the backfill alone can be what triggers the refusal)."""
    typed = factory.get("typed", {})
    required = []
    if need_parent_create or typed.get("parent") == "created":
        required.append((gh_issue_types.type_for_parent(overrides), gh_issue_types.PARENT_KEY))
    for t in tasks:
        tid = str(t["id"])
        if dispositions[tid] == "new" or typed.get(tid) == "created":
            required.append(_task_issue_type(t, overrides))
    return required


def _refuse_on_missing_types(required, declared, repo):
    """REQ-07: refuse before ANY create or apply-type call, the parent's create and the
    step-8 backfill included, when the required set is not fully declared."""
    missing = gh_issue_types.missing_types([name for name, _ in required], declared)
    if not missing:
        return
    for name, key in required:
        if name in missing:
            print(f"factory: {TOOL}: {gh_issue_types.refusal_text(repo, name, key)}",
                  file=sys.stderr)
            sys.exit(factory_cli.EXIT_REFUSED)


def _apply_and_promote(feat_dir, factory, feat_id, repo, number, key, type_id):
    """Apply the type to an already-"created" number, then promote its provenance to True
    in its own write_factory call - the receipt ordering that survives a crash between the
    two remote calls (T-07 case E)."""
    factory_gh.apply_issue_type(repo, number, type_id)
    factory["typed"][key] = True
    write_factory(feat_dir, factory, feat_id=feat_id)


def _backfill_issue_types(feat_dir, factory, tasks, overrides, declared, feat_id, repo):
    """Apply the type for every already-recorded key whose provenance is exactly the string
    "created" - never search GitHub, never touch "adopted" or an absent entry (D-20). Every
    name resolved here was already proven present in `declared` by _refuse_on_missing_types,
    which covers this exact set."""
    typed = factory.setdefault("typed", {})
    if factory["parent"] is not None and typed.get("parent") == "created":
        type_name = gh_issue_types.type_for_parent(overrides)
        _apply_and_promote(feat_dir, factory, feat_id, repo, factory["parent"], "parent",
                            declared[type_name])
    for t in tasks:
        tid = str(t["id"])
        num = factory["issues"].get(tid)
        if num is not None and typed.get(tid) == "created":
            type_name = gh_issue_types.type_for_change_type(t["change_type"], overrides)
            _apply_and_promote(feat_dir, factory, feat_id, repo, num, tid, declared[type_name])


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
    # ensure_labels (step 5, the point of no return). The board resolved here is the one
    # governing args.repo specifically (factory_config.board_for), never a fleet-level block;
    # reads used to sit inside step 7 alone (issue: T-04 defect fix); hoisted here rather than
    # duplicated.
    board = factory_config.board_for(fleet, args.repo)
    owner = board["owner"]
    board_number = board["number"]
    station_field = board["station_field"]
    _validate_stations(owner, board_number, station_field, board["stations"])

    # 4. load the ledger and sort every task into a disposition.
    factory = load_factory(feat_dir)
    factory["repo"] = args.repo
    tasks = plan["tasks"]
    dispositions = sort_dispositions(tasks, factory)

    # 4b. issue types (T-08). Detection is UNCONDITIONAL and runs exactly once, before the
    # step-5 parent branch and the step-6 task loop, and not inside either - a run that
    # creates nothing still reports its state (T-07 case G).
    overrides = _issue_type_overrides(fleet, args.repo)
    state, declared, detect_message = factory_gh.detect_issue_types(args.repo)
    _print_issue_types_state(args.repo, state, detect_message)
    need_parent_create = factory["parent"] is None and args.parent is None
    if state == "available":
        required = _required_issue_types(tasks, dispositions, factory, overrides,
                                          need_parent_create)
        _refuse_on_missing_types(required, declared, args.repo)
        _backfill_issue_types(feat_dir, factory, tasks, overrides, declared, feat_id, args.repo)

    edges_drawn = 0
    edges_skipped = 0

    need_step5 = any(d == "new" for d in dispositions.values()) or factory["parent"] is None
    if need_step5:
        # THE POINT OF NO RETURN. The first remote write this tool makes.
        ensured = ["harness", f"feature:{feat_id}"]
        if state != "available":
            ensured += ["chore", "bug"]
        ensured.append("factory:claimed")
        factory_gh.ensure_labels(args.repo, ensured)

        # 5b. the parent — adopt or create.
        if factory["parent"] is not None:
            print(
                f"factory: {TOOL}: parent #{factory['parent']} already recorded — skipping",
                file=sys.stderr,
            )
        elif args.parent is not None:
            factory["parent"] = args.parent
            factory.setdefault("typed", {})["parent"] = "adopted"
            write_factory(feat_dir, factory, feat_id=feat_id)
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
            factory.setdefault("typed", {})["parent"] = "created"
            write_factory(feat_dir, factory, feat_id=feat_id)

    # 6. create an issue for every task in the third disposition (new).
    for t in tasks:
        tid = str(t["id"])
        if dispositions[tid] != "new":
            continue
        title = f"{tid} {t['title']}"
        num = factory_gh.create_issue(
            args.repo, title, _issue_body(t), _task_labels(t, feat_id, state),
        )
        factory["issues"][tid] = num
        factory.setdefault("typed", {})[tid] = "created"
        write_factory(feat_dir, factory, feat_id=feat_id)

    # 6b. the SAME run's own creates are typed here, not inline per-create - reusing the
    # backfill pass right after the genesis run that creates the parent (need_parent_create),
    # so a fresh feature is fully typed in one shot (T-07 case A). A run that finds the
    # parent already recorded defers every fresh task's typing to the ordinary pre-create
    # backfill on a LATER run instead (T-07 case H) - the same reconciliation path recovery
    # already uses, rather than a second, parallel typing mechanism.
    if need_parent_create and state == "available":
        _backfill_issue_types(feat_dir, factory, tasks, overrides, declared, feat_id, args.repo)

    # 7. add every task issue with no recorded item id to the board. The parent is NEVER added.
    # The item id is recorded ONLY after project_field_set returns (T-04 defect fix): recording
    # it the moment project_item_add returns left an orphan permanently invisible to
    # sort_dispositions whenever the station-set that follows raised — the ledger said "done"
    # while no agent could ever claim the task (fleet.yaml's `stations.ready` need only be one
    # character wrong for the board add to succeed and the station-set to fail forever).
    ready_option = factory_config.board_station(fleet, args.repo, "ready")
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
        write_factory(feat_dir, factory, feat_id=feat_id)

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
            write_factory(feat_dir, factory, feat_id=feat_id)
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
            write_factory(feat_dir, factory, feat_id=feat_id)
            edges_drawn += 1

    # 8. the single stdout payload.
    factory_cli.payload({
        "repo": args.repo,
        "feature": feat_id,
        "parent": factory["parent"],
        "issues": dict(factory["issues"]),
        "edges_drawn": edges_drawn,
        "edges_skipped": edges_skipped,
    })


if __name__ == "__main__":
    factory_cli.run(TOOL, _main, expected=(factory_config.FleetError, factory_gh.GhError))
