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
  run-end       stamp ended_at, verdict, the lead-reported run cycles, and optionally tokens /
                code_grade on an existing entry; refuses (exit 2) when there is none.
  stamp-tokens  write the host-measured tokens onto the ONE open run (started_at set, ended_at
                absent); refuses (exit 2) when no run or more than one is open (BUG-1724).
  close-run     ONE close-out (BUG-1723): validate-digest.py <run's agent> <digest>, then
                run-end, then plan-merge.py set-task-station when --task/--station are given,
                then judgement (as harness-orchestrator) when --judgement is given, then spend;
                --cycles-used is forwarded to run-end
                — composed as subprocesses so each keeps its own refusal; the first refusal
                stops the sequence naming its stage, earlier durable writes stay. Prints ONE
                line on success. Never takes --tokens: the host hook stamps those.
  judgement     append one {at, by, kind, decision, reason} to judgements[] (SC-21).
  set-rework    write the operator's one rework ruling (SC-15); --decision must be a file
                under the feature's own directory (refuses exit 2 otherwise).
  raise-cycles  write max_total_cycles AND append the budget_decisions[] record the raise rests
                on (DEC-157); refuses (exit 2) a value that does not raise it, or a --decision
                that is not a file under the feature's own directory.
  set-mission   write mission: patch | plan (SC-01) AND append the `kind: mission` judgement
                deciding it, from --by / --reason, in the same locked write — so a mission
                never exists without the entry check-state.py INV-40 demands (SC-21).
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

TOKENS ARE MEASURED BY THE HOST, OR NULL — THIS TOOL NEVER ESTIMATES (SC-18). Under OMP the
harness hook reads the figure off the orchestrator's task result and runs `stamp-tokens` on the
open run before that run is closed; a bare `run-end` then preserves it (BUG-1724). `run-end
--tokens N` remains the explicit override for a host that reported nothing. A run that reaches
run-end with no figure is written null, and `spend` prints null when no run carries an integer,
so a reader can always tell "unmeasured" from "zero". Wall-clock minutes are likewise a sum of
recorded ended_at - started_at spans, floored to whole minutes; an open run, or one predating
FEAT-59, contributes zero rather than a guess.

CYCLES ARE REPORTED BY THE LEAD, NEVER INFERRED. `run-end --cycles-used C` records C on the
run and adjusts the feature-level total by the difference from that run's prior value. Repeating
the same cycle report leaves the total unchanged while preserving legacy unattributed cycles.

EXIT CODES: 0 on success; 2 for this CLI's own refusals (unknown id, duplicate id, non-raise,
argparse); feature_json_write / harness_merge codes propagate unchanged (11 schema or missing
file, 9 destination, 6 lock). python3 stdlib only.
"""
import argparse
import json
import artifact_accessors
import os
import re
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import feature_json_write  # noqa: E402  (local import, after sys.path fix-up)
import harness_merge  # noqa: E402  (local import, after sys.path fix-up)
import harness_yaml  # noqa: E402  (local import, after sys.path fix-up)

JUDGEMENT_KINDS = ("mission", "finding_kind", "regate", "continue", "succession", "amendment", "reject")
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


def _cycle_count(value, label):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _refuse([f"REFUSED: {label} must be a non-negative integer, got {value!r}."])
    return value


def _attributed_cycles(runs):
    total = 0
    for index, entry in enumerate(runs):
        if not isinstance(entry, dict):
            _refuse([f"REFUSED: runs[{index}] must be a mapping, got {type(entry).__name__}."])
        label = f"run {entry.get('id', index)!r} cycles_used"
        total += _cycle_count(entry.get("cycles_used", 0), label)
    return total


def _kind_count(doc, kind):
    return sum(1 for e in (doc.get("judgements") or [])
               if isinstance(e, dict) and str(e.get("kind", "")).strip() == kind)


def _owed_regate(doc, runs):
    """The FAIL run the new run re-gates with no regate entry yet, or None. INV-40 (b)'s own
    matching: the k-th FAIL run a later run follows takes the k-th regate entry."""
    followed = [str(e.get("id", "")).strip() for e in runs
                if isinstance(e, dict) and str(e.get("verdict", "")).strip().upper() == "FAIL"]
    have = _kind_count(doc, "regate")
    return followed[have] if len(followed) > have else None


def _handoff_seq(path):
    """The `seq-N` a handoff note's first line names, or None (unmarked or unreadable)."""
    try:
        with open(path, encoding="utf-8") as fh:
            m = re.search(r"\bseq-(\d+)\b", fh.readline())
    except (OSError, UnicodeDecodeError):
        return None
    return int(m.group(1)) if m else None


def _owed_succession(feature_json, doc, runs):
    """The handoff note the new run succeeds with no succession entry yet, or None. INV-40
    (c)'s own matching: handoff notes with a `seq-N` below the new run's ordinal, in seq
    order, take succession entries in ledger order. A note with no marker is INV-40's own
    finding and is never counted here."""
    notes_dir = os.path.join(os.path.dirname(os.path.abspath(feature_json)), "notes")
    names = sorted(os.listdir(notes_dir)) if os.path.isdir(notes_dir) else []
    seqs = [(_handoff_seq(os.path.join(notes_dir, name)), name) for name in names
            if name.startswith("handoff-") and name.endswith(".md")]
    owed = sorted((seq, name) for seq, name in seqs if seq is not None and seq <= len(runs))
    have = _kind_count(doc, "succession")
    return owed[have][1] if len(owed) > have else None


def _reconcile_owed(kind, owed_to, decision):
    """Refuse a mismatch between what the open owes and what the caller supplied."""
    if owed_to and not decision:
        what = (f"run {owed_to!r} has verdict FAIL and this run follows it" if kind == "regate"
                else f"notes/{owed_to} is a handoff this run succeeds")
        _refuse([f"REFUSED: {what}, and judgements[] carries no {kind} for it.",
                 f"  The open owes that judgement (INV-40); supply --by, --reason and "
                 f"--{kind} <decision> to record it and start the run in one write."])
    if decision and not owed_to:
        _refuse([f"REFUSED: --{kind} given, but this run owes no {kind}: "
                 f"the ledger records decisions that happened."])


def cmd_run_start(args):
    # THE RUN AND WHAT ITS OPEN OWES ARE ONE WRITE (#1881), the posture set-mission takes for
    # the mission and close-run takes for the close. What the open owes is DERIVED from the
    # record — a FAIL run this one follows owes a regate (INV-40 b); a handoff note this one
    # succeeds owes a succession (INV-40 c, INV-43 no later than this run starts) — and is
    # refused unless supplied, so a successor cannot wake without the ledger hearing of it.
    # A reason for a judgement the open does not owe is refused too: the ledger records
    # decisions that happened, and an unowed regate or succession did not.
    # `--regate <decision>` and `--succession continue|downgrade|stop` are the decisions the
    # ledger already spells (references/ledger.md); `--reason` is the one line both share.
    supplied = {"regate": args.regate, "succession": args.succession}
    if any(supplied.values()) and not (args.by and args.reason):
        _refuse(["REFUSED: --regate/--succession record a judgement and need --by and --reason."])
    judgements = []

    def mutate(doc):
        judgements.clear()
        runs = _runs(doc)
        if _find_run(runs, args.id) is not None:
            _refuse([f"REFUSED: runs[] already carries an entry with id {args.id!r}.",
                     "  run-start appends a NEW run; close the existing one with run-end."])
        owed = {"regate": _owed_regate(doc, runs),
                "succession": _owed_succession(args.file, doc, runs)}
        for kind, owed_to in owed.items():
            _reconcile_owed(kind, owed_to, supplied[kind])
            if owed_to:
                judgements.append(_judgement(args.by, kind, supplied[kind], args.reason))
        entry = {"id": args.id, "squad": args.squad}
        if args.agent:
            entry["agent"] = args.agent
        entry["verdict"] = "PENDING"
        entry["started_at"] = now_iso()
        runs.append(entry)
        doc["runs"] = runs
        for record in judgements:
            _append_judgement(doc, record)
        return doc

    _apply(args.file, mutate)
    print(f"STARTED run {args.id!r}")
    for record in judgements:
        print(f"RECORDED judgement {record['kind']}: {record['decision']}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def cmd_run_end(args):
    def mutate(doc):
        runs = _runs(doc)
        entry = _find_run(runs, args.id)
        if entry is None:
            _refuse([f"REFUSED: runs[] carries no entry with id {args.id!r}.",
                     "  run-end closes an entry run-start opened; start it first."])
        feature_cycles = _cycle_count(doc.get("cycles_used"), "feature cycles_used")
        attributed_cycles = _attributed_cycles(runs)
        if attributed_cycles > feature_cycles:
            _refuse([
                f"REFUSED: attributed cycles_used={attributed_cycles} exceeds "
                f"feature cycles_used={feature_cycles}.",
                "  repair the inconsistent ledger before recording another run result.",
            ])
        previous_cycles = entry.get("cycles_used", 0)
        entry["verdict"] = args.verdict
        entry["ended_at"] = now_iso()
        entry["cycles_used"] = args.cycles_used
        # A measured figure is never overwritten with null; null is written only when
        # the entry has no figure at all, so "unmeasured" is recorded rather than implied.
        if args.tokens is not None or "tokens" not in entry:
            entry["tokens"] = args.tokens
        if args.code_grade:
            entry["code_grade"] = args.code_grade
        doc["cycles_used"] = feature_cycles - previous_cycles + args.cycles_used
        doc["runs"] = runs
        return doc

    _apply(args.file, mutate)
    print(f"ENDED run {args.id!r} verdict={args.verdict} "
          f"cycles_used={args.cycles_used} tokens={json.dumps(args.tokens)}")
    print(f"APPLIED {args.file}")
    sys.exit(0)


def _open_runs(runs):
    """Open = started and not ended. An entry with no started_at predates FEAT-59's timing
    and is not a run any host is measuring now."""
    return [entry for entry in runs
            if isinstance(entry, dict) and entry.get("started_at") and not entry.get("ended_at")]


def cmd_stamp_tokens(args):
    """BUG-1724: the HOST stamps the figure it measured onto the one open run, before that run
    is closed, so the orchestrator never transcribes it. Refuses anything but exactly one open
    run — with none there is nothing being measured; with several the figure is ambiguous."""
    def mutate(doc):
        runs = _runs(doc)
        open_runs = _open_runs(runs)
        if not open_runs:
            _refuse(["REFUSED: no run is open (started_at set, ended_at absent).",
                     "  stamp-tokens writes the host's figure onto the run being measured;",
                     "  run-start one first, or use `run-end --tokens N` on a closed run."])
        if len(open_runs) > 1:
            ids = ", ".join(repr(entry.get("id")) for entry in open_runs)
            _refuse([f"REFUSED: {len(open_runs)} runs are open at once: {ids}.",
                     "  The figure cannot be attributed; close all but one with run-end."])
        open_runs[0]["tokens"] = args.tokens
        doc["runs"] = runs
        return doc

    _apply(args.file, mutate)
    print(f"STAMPED tokens={args.tokens}")
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


def _sole_judgement_at(ledger, at):
    """The index of the ONE judgement stamped `at`. Selection is by the exact timestamp
    because two amendments on one task field are individually selectable only by when they
    were made; every other dimension can repeat."""
    hits = [i for i, e in enumerate(ledger) if isinstance(e, dict) and e.get("at") == at]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        _refuse([f"REFUSED: no judgement is recorded at {at!r}.",
                 "  overrule-amendment selects by the entry's exact `at`; copy it from the ledger."])
    _refuse([f"REFUSED: {len(hits)} judgements share at={at!r}; the selection is ambiguous.",
             "  " + "; ".join(f"[{i}] {ledger[i].get('kind')}: {ledger[i].get('decision')}"
                              for i in hits)])


def _refuse_unless_live_amendment(entry, at):
    """BUG-1716 D-05: only a live (not yet overruled) amendment can be overruled."""
    if entry.get("kind") != "amendment":
        _refuse([f"REFUSED: the judgement at {at!r} is kind {entry.get('kind')!r}, not an "
                 "amendment.", "  Only an amendment can be overruled (DEC-230); other kinds "
                 "are answered by a new judgement, never rewritten."])
    if "overruled" in entry:
        _refuse([f"REFUSED: the amendment at {at!r} ({entry.get('decision')}) is already "
                 "overruled.", "  The ledger is append-only; there is nothing further to record."])


def _select_amendment(ledger, at):
    """The index of the ONE live amendment judgement stamped `at`, or a refusal."""
    index = _sole_judgement_at(ledger, at)
    _refuse_unless_live_amendment(ledger[index], at)
    return index


def cmd_overrule_amendment(args):
    """The operator's ship-time rejection of one in-build amendment (BUG-1716 T-03). Adds
    `overruled: true` to exactly that entry, preserving every other value and the ledger's
    order; every refusal leaves the file byte-identical (the write happens under `_apply`'s
    lock only after selection succeeds)."""
    selected = {}

    def mutate(doc):
        ledger = doc.get("judgements")
        ledger = list(ledger) if isinstance(ledger, list) else []
        index = _select_amendment(ledger, args.at)
        ledger[index] = {**ledger[index], "overruled": True}
        doc["judgements"] = ledger
        selected["decision"] = ledger[index].get("decision")
        return doc

    _apply(args.file, mutate)
    print(f"OVERRULED amendment {selected['decision']} at {args.at}")
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


# close-run (BUG-1723 T-01, D-01): ONE command for the close-out the orchestrator used to spend
# ~11 model calls on. It COMPOSES the existing authorities as subprocesses — validate-digest.py,
# this file's run-end and judgement, plan-merge.py set-task-station, this file's spend — so each
# keeps its own validation, lock and refusal text. Stages run in that order; the first refusal
# stops the sequence, names its stage, and leaves every earlier durable write in place (no
# rollback: a closed run is a fact, and hiding it would be worse than a half-finished close-out).
_HERE = os.path.dirname(os.path.abspath(__file__))


def _parse_judgement(text):
    """`kind=K,decision=D,reason=R` -> dict, else None. `reason` is last and may hold commas."""
    parts = text.split(",", 2)
    if len(parts) != 3:
        return None
    pairs = {}
    for expected, part in zip(("kind", "decision", "reason"), parts):
        key, sep, value = part.partition("=")
        if not sep or key.strip() != expected or not value.strip():
            return None
        pairs[expected] = value.strip()
    return pairs if pairs["kind"] in JUDGEMENT_KINDS else None


def _exit_refused(lines):
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(REFUSAL_CODE)


def _stage(name, argv):
    """Run one composed authority; on refusal print its stderr under the stage name and exit
    with ITS code, so the orchestrator reads the same refusal it would have read by hand."""
    import subprocess
    proc = subprocess.run([sys.executable, *argv], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        print(f"REFUSED at stage {name}: later stages were not run.", file=sys.stderr)
        sys.stderr.write(proc.stderr or proc.stdout)
        sys.exit(proc.returncode or REFUSAL_CODE)
    return proc.stdout


def _close_run_agent(args, judgement):
    """Every refusal that needs no stage: argument shape, unknown run, run with no agent.
    Returns the run's recorded agent — the persona whose digest contract applies."""
    if (args.task is None) != (args.station is None):
        _exit_refused(["REFUSED: --task and --station are a pair; give both or neither."])
    if args.judgement and judgement is None:
        _exit_refused([f"REFUSED: --judgement must read kind=<{'|'.join(JUDGEMENT_KINDS)}>,"
                       "decision=...,reason=... — got " + repr(args.judgement)])
    entry = _find_run(_runs(_read_doc(args.file)), args.id)
    if entry is None:
        _exit_refused([f"REFUSED at stage run-end: runs[] carries no entry with id {args.id!r}.",
                       "  close-run closes an entry run-start opened; later stages were not run."])
    agent = entry.get("agent")
    if not isinstance(agent, str) or not agent:
        _exit_refused([f"REFUSED at stage digest: run {args.id!r} records no agent, so no "
                       "persona can validate its digest."])
    return agent


def _close_run_stages(args, agent, judgement):
    """The ordered (name, argv, summary-fragment) plan, D-01's order: digest, run-end,
    station, judgement, spend. Optional stages are simply absent from the list."""
    grade = ["--code-grade", args.code_grade] if args.code_grade else []
    plan_yaml = os.path.join(os.path.dirname(os.path.abspath(args.file)), "plan.yaml")
    stages = [
        ("digest", [os.path.join(_HERE, "validate-digest.py"), agent, args.digest], None),
        ("run-end", [__file__, "run-end", "--file", args.file, "--id", args.id,
                     "--verdict", args.verdict, "--cycles-used", str(args.cycles_used), *grade],
         None),
    ]
    if args.task is not None:
        stages.append(("station", [os.path.join(_HERE, "plan-merge.py"), "set-task-station",
                                   "--file", plan_yaml, "--task", args.task,
                                   "--station", args.station],
                       f"{args.task}={args.station}"))
    if judgement:
        stages.append(("judgement", [__file__, "judgement", "--file", args.file,
                                     "--by", "harness-orchestrator", "--kind", judgement["kind"],
                                     "--decision", judgement["decision"],
                                     "--reason", judgement["reason"]],
                       f"judgement={judgement['kind']}:{judgement['decision']}"))
    stages.append(("spend", [__file__, "spend", "--file", args.file], None))
    return stages


def cmd_close_run(args):
    judgement = _parse_judgement(args.judgement) if args.judgement else None
    agent = _close_run_agent(args, judgement)
    summary = [f"CLOSED run {args.id!r} verdict={args.verdict}"]
    spend = ""
    for name, argv, fragment in _close_run_stages(args, agent, judgement):
        out = _stage(name, argv)
        if fragment:
            summary.append(fragment)
        if name == "spend":
            spend = out.strip()
    print(" ".join(summary) + f" spend={spend}")
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
                doc = artifact_accessors.load_harness_json(candidate)
                budgets = doc.get("budgets")
                return budgets if isinstance(budgets, dict) else {}
            except artifact_accessors.ArtifactAccessError:
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
    p.add_argument("--by", help="the persona judging what this open owes (with --reason)")
    p.add_argument("--reason", help="one line, at most 240 characters, shared by the judgement(s) below")
    p.add_argument("--regate", help="the re-gate decision when the run this one follows is a FAIL "
                                    "(INV-40 b), e.g. 'validate cycle 2'")
    p.add_argument("--succession", choices=("continue", "downgrade", "stop"),
                   help="the decision on the handoff this run succeeds (INV-40 c, INV-43)")
    p.set_defaults(func=cmd_run_start)

    p = with_file(sub.add_parser("run-end", help="close a runs[] entry"))
    p.add_argument("--id", required=True)
    p.add_argument("--verdict", required=True)
    p.add_argument("--cycles-used", required=True, type=_int_at_least(0),
                   help="send-backs REPORTED by this run's lead; never inferred")
    p.add_argument("--tokens", type=_int_at_least(0),
                   help="tokens MEASURED from the transcript; omit when unmeasured (null)")
    p.add_argument("--code-grade", choices=["n_a"], dest="code_grade")
    p.set_defaults(func=cmd_run_end)

    p = with_file(sub.add_parser("stamp-tokens",
                                 help="write the host-measured tokens onto the ONE open run"))
    p.add_argument("--tokens", required=True, type=_int_at_least(0),
                   help="tokens the host reported for the dispatch this run records")
    p.set_defaults(func=cmd_stamp_tokens)
    p = with_file(sub.add_parser("close-run",
                                 help="ONE close-out: validate the digest, run-end, optional "
                                      "task station, optional judgement, then print spend"))
    p.add_argument("--id", required=True, help="the run to close")
    p.add_argument("--digest", required=True, help="the lead's digest.md for that run")
    p.add_argument("--verdict", required=True)
    p.add_argument("--cycles-used", required=True, type=_int_at_least(0),
                   help="the lead DIGEST's reported send-back count for this run, forwarded to run-end")
    p.add_argument("--task", help="with --station: the task whose station to set")
    p.add_argument("--station", help="with --task: the station to set")
    p.add_argument("--judgement", help="kind=<kind>,decision=<d>,reason=<r>, recorded as "
                                       "harness-orchestrator")
    p.add_argument("--code-grade", choices=["n_a"], dest="code_grade")
    p.set_defaults(func=cmd_close_run)

    p = with_file(sub.add_parser("judgement", help="append one judgement to the ledger"))
    p.add_argument("--by", required=True)
    p.add_argument("--kind", required=True, choices=JUDGEMENT_KINDS)
    p.add_argument("--decision", required=True)
    p.add_argument("--reason", required=True, help="one line, at most 240 characters")
    p.set_defaults(func=cmd_judgement)

    p = with_file(sub.add_parser("overrule-amendment",
                                 help="mark ONE amendment judgement overruled by the operator"))
    p.add_argument("--at", required=True,
                   help="the amendment's exact `at` timestamp, copied from the ledger")
    p.set_defaults(func=cmd_overrule_amendment)

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
