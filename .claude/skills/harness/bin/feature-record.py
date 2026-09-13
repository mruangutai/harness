#!/usr/bin/env python3
"""feature-record.py — the thin CLI that writes FEAT-59's judgement and spend ledger into
feature.json (SC-15, SC-18, SC-19, SC-21), mirroring feature-json-merge.py's own split over
feature_json_write.py: every verb loads the current document, applies exactly its one
structured op, and hands the result to feature_json_write.write_feature_json, which locks,
schema-validates the candidate and atomically replaces the file — or refuses, leaving it
byte-for-byte unchanged, and this CLI prints the refusal lines and exits its code.

VERBS
  run-start     append a runs[] entry with started_at and verdict PENDING; refuses (exit 2)
                when an entry with that id already exists.
  run-end       stamp ended_at, verdict and optionally tokens / code_grade on the entry with
                that id; refuses (exit 2) when there is none.
  judgement     append one {at, by, kind, decision, reason} to judgements[] (SC-21).
  set-rework    write the operator's one rework ruling (SC-15); --decision must be a file
                under the feature's own directory (refuses exit 2 otherwise).
  raise-cycles  write max_total_cycles AND append the budget_decisions[] record the raise rests
                on (DEC-157); refuses (exit 2) a value that does not raise it, or a --decision
                that is not a file under the feature's own directory.
  set-mission   write mission: patch | plan (SC-01) AND append the `kind: mission` judgement
                deciding it, from --by / --reason, in the same locked write — so a mission
                never exists without the entry check-state.sh INV-40 demands (SC-21).
  propose-rework read-only: print {rounds, minutes, basis} — the baseline ruling the main
                session shows the operator at signature (patch: 1 round; plan: tasks/3,
                floor 2, cap max_total_cycles; minutes = rounds x budgets.rework_round_minutes).
  spend         read-only: print one JSON object {runs, wall_clock_minutes, tokens, phase,
                rework_minutes, rework_rounds} — the last two are the rework window, from
                the first validate run; the ruling is compared to those, never the whole.

THE OPERATOR'S RULINGS ARE MAIN-SESSION-ONLY. set-rework and raise-cycles are gated by
plan-sign-gate.py the way plan-merge.py sign-approval is: an agent's call is refused before it
runs. This CLI adds the second half — `--decision` must resolve to an existing file under the
feature directory — so the record a ruling rests on is a document, not a string INV-39 would
accept on the strength of its own syntax.

TOKENS ARE MEASURED BY THE CALLER, OR NULL — THIS TOOL NEVER ESTIMATES (SC-18). `run-end
--tokens N` records a figure the caller read off the OMP transcript on disk; a run-end that
carries none writes null, and `spend` prints null when no run carries an integer, so a reader
can always tell "unmeasured" from "zero". Wall-clock minutes are likewise a sum of recorded
ended_at - started_at spans, floored to whole minutes; an open run, or one predating FEAT-59,
contributes zero rather than a guess.

EXIT CODES: 0 on success; 2 for this CLI's own refusals (unknown id, duplicate id, non-raise,
argparse); feature_json_write / harness_merge codes propagate unchanged (11 schema or missing
file, 9 destination, 6 lock). python3 stdlib only.
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feature_json_write  # noqa: E402  (local import, after sys.path fix-up)
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)

JUDGEMENT_KINDS = ("mission", "finding_kind", "regate", "continue", "succession")
MISSIONS = ("patch", "plan")
REFUSAL_CODE = 2


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _refuse(lines):
    raise harness_merge.MergeRefusal(REFUSAL_CODE, lines)


def _apply(path, mutate):
    """Load `path`'s document, apply `mutate(doc) -> doc`, and write the result under the
    lock. A `path` whose document does not exist is refused: this CLI records onto an
    existing feature.json only — it is never the tool that instantiates one."""

    def transform(base):
        doc = feature_json_write.parse_doc(base, path)
        if doc is None:
            raise harness_merge.MergeRefusal(
                feature_json_write.SCHEMA_REFUSAL_CODE,
                [f"REFUSED: {path} does not exist.",
                 "  this tool records onto an existing feature.json only."],
            )
        return json.dumps(mutate(doc), indent=2) + "\n"

    try:
        feature_json_write.write_feature_json(path, transform)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def _runs(doc):
    runs = doc.get("runs")
    return list(runs) if isinstance(runs, list) else []


def _find_run(runs, run_id):
    for entry in runs:
        if isinstance(entry, dict) and entry.get("id") == run_id:
            return entry
    return None


def cmd_run_start(args):
    def mutate(doc):
        runs = _runs(doc)
        if _find_run(runs, args.id) is not None:
            _refuse([f"REFUSED: runs[] already carries an entry with id {args.id!r}.",
                     "  run-start appends a NEW run; close the existing one with run-end."])
        entry = {"id": args.id, "squad": args.squad}
        if args.agent:
            entry["agent"] = args.agent
        entry["verdict"] = "PENDING"
        entry["started_at"] = now_iso()
        runs.append(entry)
        doc["runs"] = runs
        return doc

    _apply(args.file, mutate)
    print(f"STARTED run {args.id!r}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def cmd_run_end(args):
    def mutate(doc):
        runs = _runs(doc)
        entry = _find_run(runs, args.id)
        if entry is None:
            _refuse([f"REFUSED: runs[] carries no entry with id {args.id!r}.",
                     "  run-end closes an entry run-start opened; start it first."])
        entry["verdict"] = args.verdict
        entry["ended_at"] = now_iso()
        # A measured figure is never overwritten with null; null is written only when
        # the entry has no figure at all, so "unmeasured" is recorded rather than implied.
        if args.tokens is not None or "tokens" not in entry:
            entry["tokens"] = args.tokens
        if args.code_grade:
            entry["code_grade"] = args.code_grade
        doc["runs"] = runs
        return doc

    _apply(args.file, mutate)
    print(f"ENDED run {args.id!r} verdict={args.verdict} tokens={json.dumps(args.tokens)}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def _judgement(by, kind, decision, reason):
    return {"at": now_iso(), "by": by, "kind": kind, "decision": decision, "reason": reason}


def _append_judgement(doc, record):
    ledger = doc.get("judgements")
    ledger = list(ledger) if isinstance(ledger, list) else []
    ledger.append(record)
    doc["judgements"] = ledger
    return doc


def cmd_judgement(args):
    record = _judgement(args.by, args.kind, args.decision, args.reason)
    _apply(args.file, lambda doc: _append_judgement(doc, record))
    print(f"RECORDED judgement {args.kind}: {args.decision}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


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
    # THE MISSION AND ITS JUDGEMENT ARE ONE WRITE. check-state.sh INV-40 refuses a `mission`
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


def _parse_iso(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _run_seconds(entry):
    """Whole seconds a closed run took, or 0 for one still open or unstamped."""
    started = _parse_iso(entry.get("started_at"))
    ended = _parse_iso(entry.get("ended_at"))
    if started is None or ended is None or ended <= started:
        return 0
    return int((ended - started).total_seconds())


# A run is a validate run when its id carries the `validate-` token at the start or after a
# `-`, and a fix run likewise for `fix-`. Real ids are date-prefixed run-dir slugs
# (`2026-09-11-05-validate-validator`; the corpus holds 181 of that shape against 1 bare
# `validate-validator`), and the first draft's `startswith("validate-")` never opened the
# window on any of them — so the build-phase SPEND advisory (SC-19) never fired and the
# rework-ratio KPI read 0, silently. Token-bounded, not substring: `postfix-eng` is no fix.
VALIDATE_RUN = re.compile(r"(?:^|-)validate-")
FIX_RUN = re.compile(r"(?:^|-)fix-")


def spend_for(doc):
    """The spend summary for a parsed feature.json (pure; used by `spend`).

    `wall_clock_minutes` is the whole feature — the lagging figure the briefing reports.
    `rework_minutes` and `rework_rounds` are the REWORK WINDOW: every run from the first
    validate run onward, and the count of fix runs in it. The operator's
    `rework.wall_clock_minutes` ruling is a budget for rework, so the hook compares it to
    the window, never to the whole — before this split a 60-minute plan run and a 40-minute
    build ate 100 of a 120-minute ruling before the first fix round existed.
    """
    runs = [entry for entry in _runs(doc) if isinstance(entry, dict)]
    seconds = sum(_run_seconds(entry) for entry in runs)
    measured = [entry["tokens"] for entry in runs
                if isinstance(entry.get("tokens"), int) and not isinstance(entry.get("tokens"), bool)]
    tokens = sum(measured) if measured else None
    first_validate = next((i for i, entry in enumerate(runs)
                           if VALIDATE_RUN.search(str(entry.get("id", "")))), None)
    window = runs[first_validate:] if first_validate is not None else []
    github = doc.get("github")
    has_build_entry = isinstance(github, dict) and "build_entry" in github
    return {"runs": len(runs), "wall_clock_minutes": seconds // 60, "tokens": tokens,
            "phase": "build" if has_build_entry else "plan",
            "rework_minutes": sum(_run_seconds(entry) for entry in window) // 60,
            "rework_rounds": sum(1 for entry in window
                                 if FIX_RUN.search(str(entry.get("id", ""))))}


def cmd_spend(args):
    print(json.dumps(spend_for(_read_doc(args.file))))
    sys.exit(0)


def _read_doc(path):
    """The parsed feature.json, or a refusal — shared by the read-only verbs."""
    try:
        with open(path, "rb") as handle:
            return feature_json_write.parse_doc(handle.read(), path)
    except FileNotFoundError:
        print(f"REFUSED: {path} does not exist.", file=sys.stderr)
        sys.exit(feature_json_write.SCHEMA_REFUSAL_CODE)
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)


def _budgets_for(feature_json):
    """`budgets` from the nearest `.harness/harness.json` above the feature dir, else {}."""
    here = os.path.dirname(os.path.abspath(feature_json))
    while True:
        candidate = os.path.join(here, ".harness", "harness.json")
        if os.path.isfile(candidate):
            try:
                with open(candidate, encoding="utf-8") as handle:
                    budgets = (json.load(handle) or {}).get("budgets")
                return budgets if isinstance(budgets, dict) else {}
            except (OSError, ValueError):
                return {}
        parent = os.path.dirname(here)
        if parent == here:
            return {}
        here = parent


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
        import harness_yaml
        tasks = harness_yaml.load_plan(plan_path).get("tasks") or []
        proposal = propose_rework(doc, len(tasks), _budgets_for(args.file))
    except harness_merge.MergeRefusal as refusal:
        for line in refusal.lines:
            print(line, file=sys.stderr)
        sys.exit(refusal.code)
    except Exception as exc:  # a plan that does not load proposes nothing
        print(f"REFUSED: {plan_path} does not load: {exc}", file=sys.stderr)
        sys.exit(REFUSAL_CODE)
    print(json.dumps(proposal))
    sys.exit(0)


def _int_at_least(minimum):
    def parse(raw):
        value = int(raw)
        if value < minimum:
            raise argparse.ArgumentTypeError(f"must be >= {minimum}, got {value}")
        return value
    return parse


def main():
    parser = argparse.ArgumentParser(prog="feature-record.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def with_file(p):
        p.add_argument("--file", required=True, help="path to feature.json")
        return p

    p = with_file(sub.add_parser("run-start", help="append a PENDING runs[] entry"))
    p.add_argument("--id", required=True)
    p.add_argument("--squad", required=True)
    p.add_argument("--agent", help="the agent executing the run (required for new features)")
    p.set_defaults(func=cmd_run_start)

    p = with_file(sub.add_parser("run-end", help="close a runs[] entry"))
    p.add_argument("--id", required=True)
    p.add_argument("--verdict", required=True)
    p.add_argument("--tokens", type=_int_at_least(0),
                   help="tokens MEASURED from the transcript; omit when unmeasured (null)")
    p.add_argument("--code-grade", choices=["n_a"], dest="code_grade")
    p.set_defaults(func=cmd_run_end)

    p = with_file(sub.add_parser("judgement", help="append one judgement to the ledger"))
    p.add_argument("--by", required=True)
    p.add_argument("--kind", required=True, choices=JUDGEMENT_KINDS)
    p.add_argument("--decision", required=True)
    p.add_argument("--reason", required=True, help="one line, at most 240 characters")
    p.set_defaults(func=cmd_judgement)

    p = with_file(sub.add_parser("set-rework", help="write the operator's rework ruling"))
    p.add_argument("--rounds", required=True, type=_int_at_least(0))
    p.add_argument("--minutes", required=True, type=_int_at_least(0))
    p.add_argument("--decision", required=True,
                   help="where the ruling is recorded: a file under the feature directory, "
                        "optionally with a #fragment")
    p.set_defaults(func=cmd_set_rework)

    p = with_file(sub.add_parser("raise-cycles", help="raise max_total_cycles with its record"))
    p.add_argument("--to", required=True, type=_int_at_least(1))
    p.add_argument("--decision", required=True,
                   help="the recorded user decision: a file under the feature directory, "
                        "optionally with a #fragment")
    p.set_defaults(func=cmd_raise_cycles)

    p = with_file(sub.add_parser("set-mission",
                                 help="write the mission and the judgement deciding it"))
    p.add_argument("--mission", required=True, choices=MISSIONS)
    p.add_argument("--by", required=True, help="the persona that judged the mission")
    p.add_argument("--reason", required=True, help="one line, at most 240 characters")
    p.set_defaults(func=cmd_set_mission)

    p = with_file(sub.add_parser("spend", help="print the feature's measured spend as JSON"))
    p.set_defaults(func=cmd_spend)

    p = with_file(sub.add_parser("propose-rework",
                                 help="print the baseline rework ruling for signature as JSON"))
    p.set_defaults(func=cmd_propose_rework)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
