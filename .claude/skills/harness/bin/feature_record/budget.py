"""feature_record/budget.py — the operator's rulings and the review pin: set-rework,
raise-cycles, set-mission, pin-review and propose-rework.
"""
import json
import os
import sys

import artifact_accessors
import harness_merge
import harness_yaml
from harness_boundary import root_above
from feature_record.judgements import _append_judgement, _judgement, now_iso
from feature_record.read import _read_doc
from feature_record.write import REFUSAL_CODE, _apply, _exit_refused, _refuse


MISSIONS = ("patch", "plan")


def _require_decision_file(feature_json, decision, verb):
    """Refuse (exit 2) unless `decision`, less any `#fragment`, is an existing FILE under the
    feature directory. Resolved as given (absolute or cwd-relative) first, then relative to
    the feature directory — so the main session can pass either the path it copy-pastes from
    the repo root or the short form the ledger prints. Realpath on both sides, so a symlink
    that escapes the directory is refused as the outside path it is."""
    feature_dir = os.path.realpath(os.path.dirname(os.path.abspath(feature_json)))
    target = decision.split("#", 1)[0]
    candidates = [target] if os.path.isabs(target) else [target, os.path.join(feature_dir, target)]
    for candidate in candidates:
        resolved = os.path.realpath(candidate)
        if os.path.isfile(resolved) and os.path.commonpath([feature_dir, resolved]) == feature_dir:
            return
    _refuse([f"REFUSED: --decision {decision!r} is not a file under {feature_dir}.",
             f"  {verb} records the OPERATOR'S ruling (SC-15, DEC-157); its record must be a "
             "document in the feature's own directory, not a bare id or a path elsewhere."])


def cmd_set_rework(args):
    ruling = {"rounds": args.rounds, "wall_clock_minutes": args.minutes,
              "decision": args.decision}

    def mutate(doc):
        _require_decision_file(args.file, args.decision, "set-rework")
        doc["rework"] = ruling
        return doc

    _apply(args.file, mutate)
    print(f"SET rework = {json.dumps(ruling)}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def cmd_raise_cycles(args):
    def mutate(doc):
        _require_decision_file(args.file, args.decision, "raise-cycles")
        current = doc.get("max_total_cycles")
        if isinstance(current, int) and args.to <= current:
            _refuse([f"REFUSED: max_total_cycles is {current} and --to {args.to} does not "
                     "raise it.",
                     "  raise-cycles records a RAISE (DEC-157); lowering is not a budget "
                     "decision this tool takes."])
        doc["max_total_cycles"] = args.to
        decisions = doc.get("budget_decisions")
        decisions = list(decisions) if isinstance(decisions, list) else []
        decisions.append({"at": now_iso(), "max_total_cycles": args.to,
                          "decision": args.decision})
        doc["budget_decisions"] = decisions
        return doc

    _apply(args.file, mutate)
    print(f"RAISED max_total_cycles to {args.to} per {args.decision}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def cmd_set_mission(args):
    # THE MISSION AND ITS JUDGEMENT ARE ONE WRITE. check-state.py INV-40 refuses a `mission`
    # whose last `kind: mission` entry decides something else; writing the two separately
    # would let this CLI produce exactly that state between its own two calls.
    record = _judgement(args.by, "mission", args.mission, args.reason)

    def mutate(doc):
        doc["mission"] = args.mission
        return _append_judgement(doc, record)

    _apply(args.file, mutate)
    print(f"SET mission = {args.mission}")
    print(f"RECORDED judgement mission: {args.mission}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def _commit_id(path, sha):
    """`sha` resolved to a full commit id in the repository holding `path`, or the exit-2
    refusal. A tree, a blob or an unresolved name is refused: readers diff a commit."""
    import code_grade
    repo = os.path.dirname(os.path.abspath(path))
    try:
        # The one resolver: validate-digest.py resolves the recorded pin through it too.
        return code_grade.commit_oid(repo, sha)
    except ValueError:
        _exit_refused([f"REFUSED: {sha!r} does not resolve to a commit in {repo}.",
                       "  review_sha pins the commit the readers diff; nothing was written."])


def cmd_pin_review(args):
    """#2167: the pin is a ledger write like every other, never a hand edit of feature.json."""
    full = _commit_id(args.file, args.sha)

    def mutate(doc):
        doc["review_sha"] = full
        return doc

    _apply(args.file, mutate)
    print(f"APPLIED pin-review {full}")
    sys.exit(0)


def _budgets_for(feature_json):
    """`budgets` from the validated harness.json of the checkout holding the feature (the
    manifest probe, never a bare `.harness` directory — B-7). A missing or invalid config
    refuses with its diagnosis (FEAT-2297) — never empty budgets."""
    root = root_above(os.path.dirname(os.path.abspath(feature_json)))
    if root is None:
        sys.exit(f"feature-record: no harness checkout above {feature_json}, so no budgets")
    try:
        return artifact_accessors.load_harness_json(os.path.join(root, ".harness", "harness.json"))["budgets"]
    except artifact_accessors.ArtifactAccessError as error:
        sys.exit(f"feature-record: {error}")


DEFAULT_REWORK_ROUND_MINUTES = 45


TASKS_PER_ROUND = 3


def propose_rework(doc, task_count, budgets):
    """The baseline rework ruling the main session shows the operator at signature (SC-15).

    Deterministic from disk so the operator confirms or changes a number rather than
    inventing one (SC-22): `patch` is one round; `plan` is one round per TASKS_PER_ROUND
    tasks, never fewer than two, never more than `max_total_cycles`; minutes are rounds
    times `budgets.rework_round_minutes`. When five shipped features carry `rework_rounds`,
    the measured median belongs here instead of the constant — that is the KPI's job.
    """
    mission = doc.get("mission")
    if mission not in ("patch", "plan"):
        _refuse(["REFUSED: no mission recorded; propose-rework reads `mission` (patch | plan).",
                 "  Write it first: feature-record.py set-mission --mission <patch|plan> "
                 "--by <persona> --reason <one line>."])
    per_round = budgets.get("rework_round_minutes", DEFAULT_REWORK_ROUND_MINUTES)
    caps = [c for c in (doc.get("max_total_cycles"), budgets.get("max_total_cycles"))
            if isinstance(c, int) and not isinstance(c, bool)]
    cap = min(caps) if caps else 10
    if mission == "patch":
        rounds = 1
        basis = f"patch mission: 1 round"
    else:
        rounds = min(max(2, -(-task_count // TASKS_PER_ROUND)), cap)
        basis = (f"plan mission: {task_count} tasks / {TASKS_PER_ROUND} per round, floor 2, "
                 f"cap max_total_cycles {cap} -> {rounds} rounds")
    return {"rounds": rounds, "minutes": rounds * per_round,
            "basis": f"{basis}; {per_round} min per round (budgets.rework_round_minutes)"}


def cmd_propose_rework(args):
    doc = _read_doc(args.file)
    plan_path = os.path.join(os.path.dirname(os.path.abspath(args.file)), "plan.yaml")
    try:
        tasks = artifact_accessors.load_plan(plan_path).get("tasks") or []
        proposal = propose_rework(doc, len(tasks), _budgets_for(args.file))
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    except harness_yaml.YamlParseError as exc:  # a plan that does not load proposes nothing
        print(f"REFUSED: {plan_path} does not load: {exc}", file=sys.stderr)
        sys.exit(REFUSAL_CODE)
    print(json.dumps(proposal))
    sys.exit(0)
