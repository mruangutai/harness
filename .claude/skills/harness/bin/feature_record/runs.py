"""feature_record/runs.py — the runs[] ledger: run-start, run-end, record-history,
stamp-tokens and close-run, with the owed-judgement checks a run open composes.
"""
import argparse
import json
import os
import re
import sys

import digest_record
from harness_boundary import CONTRACT_REFUSAL_CODE
from feature_record import evidence
from feature_record.judgements import JUDGEMENT_KINDS, _append_judgement, _judgement, _kind_count, now_iso
from feature_record.read import _read_doc, _runs
from feature_record.write import _apply, _exit_refused, _refuse


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
    from digest_destination import LEAD_SQUADS
    expected_squad = LEAD_SQUADS.get(args.agent)
    if expected_squad is not None and args.squad != expected_squad:
        _exit_refused([f"REFUSED: {args.agent} requires --squad {expected_squad!r}; "
                       f"got {args.squad!r}."])
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


def _history_evidence(doc, entry, args, effect):
    """Authenticate a requested historical effect without deriving claims from prose."""
    directory = os.path.dirname(os.path.abspath(args.file))
    try:
        digest = evidence.resolve_evidence_ref(directory, args.digest)
        authorization = evidence.resolve_evidence_ref(directory, args.evidence)
        subject = {"feature_id": doc["feature_id"], "run_id": entry["id"],
                   "digest": digest, "effect": effect}
        if effect == "record-cycle-evidence":
            subject["cycles_used"] = entry["cycles_used"]
        evidence.verify_evidence_ref(directory, authorization, subject)
        if effect == "record-cycle-evidence":
            evidence.verify_historical_cycle_count(
                os.path.join(directory, digest["path"]), entry["cycles_used"])
        if not args.yes or not args.by.strip():
            raise ValueError("historical recovery requires --by and --yes")
        return digest, authorization
    except (OSError, ValueError, KeyError, TypeError) as error:
        _refuse([f"REFUSED: {error}"])


def _history_run(doc, args):
    """The closed run a historical effect is recorded on, once the effect may apply to it."""
    entry = _find_run(_runs(doc), args.id)
    if entry is None or not entry.get("ended_at"):
        _refuse(["REFUSED: historical recovery requires an existing closed run."])
    if args.cmd == "record-refusal":
        _check_refusal_history(entry)
    else:
        _cycle_count(entry.get("cycles_used"), f"run {args.id!r}")
    return entry


def _check_refusal_history(entry):
    if entry.get("verdict") != "BLOCKED":
        _refuse(["REFUSED: refusal provenance requires a historical BLOCKED run."])
    if "return_disposition" in entry:
        _refuse(["REFUSED: the run already carries the frozen legacy refused marker; "
                 "an entry never holds both it and refusal provenance."])


def _history_conflicts(existing, field, ref, authorization, args):
    """A recorded historical receipt that differs from the one requested now."""
    expected = {"digest": ref} if field == "refusal" else ref
    return (existing.get("source") != "operator-history"
            or existing.get("authorization") != authorization
            or existing.get("by") != args.by
            or any(existing.get(key) != value for key, value in expected.items())
            or (field == "refusal" and existing.get("reason") != args.reason))


def _history_receipt(field, ref, authorization, args):
    receipt = {"source": "operator-history", "by": args.by,
               "at": now_iso(), "authorization": authorization}
    if field == "refusal":
        receipt.update(digest=ref, run_id=args.id, reason=args.reason)
    else:
        receipt.update(ref)
    return receipt


def cmd_record_history(args):
    def mutate(doc):
        entry = _history_run(doc, args)
        effect = args.cmd
        ref, authorization = _history_evidence(doc, entry, args, effect)
        field = "refusal" if effect == "record-refusal" else "cycle_evidence"
        existing = entry.get(field)
        if existing:
            if _history_conflicts(existing, field, ref, authorization, args):
                _refuse(["REFUSED: historical evidence conflicts with the recorded receipt."])
            return doc
        entry[field] = _history_receipt(field, ref, authorization, args)
        return doc
    _apply(args.file, mutate)
    print(f"RECORDED {args.cmd} run {args.id!r}")
    sys.exit(0)


def _run_end_digest(args, entry, changed, runs):
    """Verify immutable, durably run-owned evidence and the claimed count."""
    try:
        directory = os.path.dirname(args.file)
        ref = evidence.resolve_evidence_ref(directory, args.digest)
        evidence.verify_run_digest_owner(entry["id"], ref["path"], runs)
        previous = _prior_digest_claims(directory, entry, ref, changed, runs)
        _check_digest_record(directory, ref, args)
        if previous:
            ref["previous"] = previous
        return ref
    except (OSError, ValueError, KeyError, TypeError, digest_record.DigestRecordError) as error:
        _refuse([f"REFUSED: {error}"])


def _prior_digest_claims(directory, entry, ref, changed, runs):
    """The run's earlier digest claims other than `ref`, each still authentic and run-owned."""
    existing = entry.get("cycle_evidence")
    if not existing:
        return []
    claims = [*existing.get("previous", []),
              {key: existing[key] for key in ("path", "sha256")}]
    _verify_claims(directory, entry, claims, runs)
    previous = [claim for claim in claims if claim["path"] != ref["path"]]
    if not changed and any(existing[key] != ref[key] for key in ("path", "sha256")):
        raise ValueError("replay evidence conflicts with the recorded receipt")
    return previous


def _check_digest_record(directory, ref, args):
    record = digest_record.load_record(os.path.join(directory, ref["path"]))
    digest = record.get("DIGEST")
    count = digest.get("cycles_used") if isinstance(digest, dict) else None
    if type(count) is not int or count != args.cycles_used:
        raise ValueError("cycles_used disagrees with authentic digest evidence")
    if record.get("VERDICT") != args.verdict or "artifact" not in record:
        raise ValueError("digest verdict/record does not match the requested close")


def _verify_claims(directory, entry, claims, runs):
    for claim in claims:
        evidence.verify_evidence_ref(directory, claim)
        evidence.verify_run_digest_owner(entry["id"], claim["path"], runs)


def _is_refused(entry):
    """Typed refusal provenance, or the frozen legacy marker no writer produces any more."""
    return bool(entry.get("refusal")) or entry.get("return_disposition") == "refused"


def _replay_refused(entry, args):
    """An already-refused run keeps its terminal record: BLOCKED, its count and its tokens."""
    if args.verdict != "BLOCKED":
        _refuse(["REFUSED: a refused return cannot be upgraded to an accepted verdict."])
    if args.cycles_used != entry.get("cycles_used", 0):
        _refuse(["REFUSED: a refused run's recorded cycles_used cannot be rewritten."])
    if getattr(args, "tokens", None) is not None and args.tokens != entry.get("tokens"):
        _refuse(["REFUSED: a refused run's measured tokens cannot be rewritten."])


def _ledger_cycles(doc, runs):
    """The feature's cycles_used, refused when the runs already attribute more than it."""
    feature_cycles = _cycle_count(doc.get("cycles_used"), "feature cycles_used")
    attributed_cycles = _attributed_cycles(runs)
    if attributed_cycles > feature_cycles:
        _refuse([
            f"REFUSED: attributed cycles_used={attributed_cycles} exceeds "
            f"feature cycles_used={feature_cycles}.",
            "  repair the inconsistent ledger before recording another run result.",
        ])
    return feature_cycles


def _record_attribution(entry, args, runs, previous_cycles):
    changed = "cycles_used" not in entry or previous_cycles != args.cycles_used
    if changed and not args.digest:
        _refuse(["REFUSED: new/changed cycle attribution requires --digest evidence."])
    if args.digest:
        _attach_digest(entry, args, runs, changed)
    entry["cycles_used"] = args.cycles_used
    # A measured figure is never overwritten with null; null is written only when
    # the entry has no figure at all, so "unmeasured" is recorded rather than implied.
    if args.tokens is not None or "tokens" not in entry:
        entry["tokens"] = args.tokens


def _attach_digest(entry, args, runs, changed):
    ref = _run_end_digest(args, entry, changed, runs)
    if changed or "cycle_evidence" not in entry:
        entry["cycle_evidence"] = dict(source="lead-digest", **ref)


def _record_run_end(args):
    def mutate(doc):
        runs = _runs(doc)
        entry = _find_run(runs, args.id)
        if entry is None:
            _refuse([f"REFUSED: runs[] carries no entry with id {args.id!r}.",
                     "  run-end closes an entry run-start opened; start it first."])
        feature_cycles = _ledger_cycles(doc, runs)
        previous_cycles = entry.get("cycles_used", 0)
        if _is_refused(entry):
            _replay_refused(entry, args)
        else:
            _record_attribution(entry, args, runs, previous_cycles)
        entry["verdict"] = args.verdict
        entry.setdefault("ended_at", now_iso())
        if args.code_grade:
            entry["code_grade"] = args.code_grade
        doc["cycles_used"] = feature_cycles - previous_cycles + entry.get("cycles_used", 0)
        doc["runs"] = runs
        return doc

    _apply(args.file, mutate)


def cmd_run_end(args):
    _record_run_end(args)
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


# close-run (BUG-1723 T-01, D-01): ONE command for the close-out the orchestrator used to spend
# ~11 model calls on. It COMPOSES the existing authorities — validate-digest.py, the shared
# atomic run-end transaction, plan-merge.py set-task-station, feature-record.py's judgement and spend —
# so each keeps its own validation, lock and refusal text. The first refusal
# stops the sequence, names its stage, and leaves every earlier durable write in place (no
# rollback: a closed run is a fact, and hiding it would be worse than a half-finished close-out).
_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ENTRY = os.path.join(_HERE, "feature-record.py")


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


def _stage(name, argv, refuse_on_success=None):
    """Run one composed authority; on refusal print its stderr under the stage name and exit
    with ITS code, so the orchestrator reads the same refusal it would have read by hand.
    With `refuse_on_success`, the stage is INVERTED: the authority's success is the refusal,
    worded by that line, and its refusal is the pass."""
    import subprocess
    proc = subprocess.run([sys.executable, *argv], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True)
    inverted = refuse_on_success is not None
    expected = CONTRACT_REFUSAL_CODE if inverted else 0
    if inverted and proc.returncode == 0:
        _exit_refused([f"REFUSED at stage {name}: later stages were not run.",
                       refuse_on_success])
    if proc.returncode != expected:
        print(f"REFUSED at stage {name}: later stages were not run.", file=sys.stderr)
        sys.stderr.write(proc.stderr or proc.stdout)
        sys.exit(proc.returncode)
    return "" if inverted else proc.stdout


def _close_run_options(args):
    """Reject invalid close intent before resolving a run or touching its artifacts."""
    judgement = _parse_judgement(args.judgement) if args.judgement else None
    if (args.task is None) != (args.station is None):
        _exit_refused(["REFUSED: --task and --station are a pair; give both or neither."])
    if args.refused_return and args.verdict != "BLOCKED":
        _exit_refused([f"REFUSED: --refused-return closes a run as BLOCKED only — got "
                       f"--verdict {args.verdict!r}. No digest was validated, so no other "
                       "verdict has a record to rest on."])
    if args.judgement and judgement is None:
        _exit_refused([f"REFUSED: --judgement must read kind=<{'|'.join(JUDGEMENT_KINDS)}>,"
                       "decision=...,reason=... — got " + repr(args.judgement)])
    return judgement


def _close_run_preflight(args):
    """Resolve argument shape, run persona, judgement and one digest before any stage."""
    judgement = _close_run_options(args)
    entry = _find_run(_runs(_read_doc(args.file)), args.id)
    if entry is None:
        _exit_refused([f"REFUSED at stage run-end: runs[] carries no entry with id {args.id!r}.",
                       "  close-run closes an entry run-start opened; later stages were not run."])
    agent = entry.get("agent")
    if not isinstance(agent, str) or not agent:
        _exit_refused([f"REFUSED at stage digest: run {args.id!r} records no agent, so no "
                       "persona can validate its digest."])
    _resolve_close_digest(args)
    return agent, judgement


def _resolve_close_digest(args):
    """Validation, refusal recording and run-end must address the same target-local file."""
    directory = os.path.dirname(os.path.abspath(args.file))
    try:
        ref = evidence.resolve_evidence_ref(directory, args.digest)
        args.digest = evidence.verify_evidence_ref(directory, ref)
        if args.refused_return:
            with open(args.digest, encoding="utf-8") as source:
                source.read()
            args._refusal_digest = ref
    except (OSError, ValueError, UnicodeError, TypeError) as error:
        stage = "refused-return" if args.refused_return else "digest"
        _exit_refused([f"REFUSED at stage {stage}: {error}"])


def _close_run_stages(args, agent, judgement):
    """The ordered (name, argv, summary-fragment, refuse-on-success) plan, D-01's order:
    digest, run-end, station, judgement, spend. Optional stages are simply absent.

    --refused-return (#2068) INVERTS the digest stage: the host refused the lead's final
    return, so its digest.md never received a valid record and the normal close could never
    pass. The stage then demands that the digest does NOT validate — a digest that does is a
    return that landed, and must close through the normal stage under its own verdict."""
    grade = ["--code-grade", args.code_grade] if args.code_grade else []
    plan_yaml = os.path.join(os.path.dirname(os.path.abspath(args.file)), "plan.yaml")
    digest = [os.path.join(_HERE, "validate-digest.py")]
    if args.refused_return:
        digest.extend(["--contract-refusal-code", str(CONTRACT_REFUSAL_CODE)])
    digest.extend(["--", agent, args.digest])
    if args.refused_return:
        first = ("refused-return", digest, "refused-return",
                 f"  {args.digest} validates for {agent}: the lead's return landed, so close "
                 "it without --refused-return under the verdict its digest reports.")
    else:
        first = ("digest", digest, None, None)
    stages = [
        first,
        ("run-end", [_ENTRY, "run-end", "--file", args.file, "--id", args.id,
                     "--verdict", args.verdict, "--cycles-used", str(args.cycles_used),
                     "--digest", args.digest, *grade],
         None, None),
    ]
    if args.task is not None:
        stages.append(("station", [os.path.join(_HERE, "plan-merge.py"), "set-task-station",
                                   "--file", plan_yaml, "--task", args.task,
                                   "--station", args.station],
                       f"{args.task}={args.station}", None))
    if judgement:
        stages.append(("judgement", [_ENTRY, "judgement", "--file", args.file,
                                     "--by", "harness-orchestrator", "--kind", judgement["kind"],
                                     "--decision", judgement["decision"],
                                     "--reason", judgement["reason"]],
                       f"judgement={judgement['kind']}:{judgement['decision']}", None))
    stages.append(("spend", [_ENTRY, "spend", "--file", args.file], None, None))
    return stages


def _close_refused_run(args, agent):
    """Persist observed rejection before any later close stage, without a fake accepted record.

    Only an open run takes new close-run provenance. An already-refused run (typed refusal or
    the frozen legacy marker) replays unchanged; a closed BLOCKED run without provenance is
    historical and takes it through record-refusal, never here."""
    def mutate(doc):
        runs = _runs(doc)
        entry, total, previous = _refused_close_entry(doc, runs, args)
        ref = _observed_refusal_digest(args)
        _check_refusal_closable(entry, ref, args)
        if _is_refused(entry):
            _replay_refused(entry, args)
            return doc
        if entry.get("verdict") == "BLOCKED" or entry.get("ended_at"):
            _refuse(["REFUSED: this run is already closed BLOCKED; record historical refusal "
                     "provenance with record-refusal, not close-run."])
        _refused_cycle_evidence(doc, entry, args, previous)
        _stamp_refusal(entry, ref, args, agent)
        doc["cycles_used"] = total - previous + args.cycles_used
        return doc
    _apply(args.file, mutate)
    return ""


def _refused_close_entry(doc, runs, args):
    """(entry, feature total, the run's prior count) for a refused close, refusing a missing
    run or an over-attributed ledger."""
    entry = _find_run(runs, args.id)
    if entry is None:
        _refuse(["REFUSED: the run disappeared before recording its refusal."])
    total = _cycle_count(doc.get("cycles_used"), "feature cycles_used")
    if _attributed_cycles(runs) > total:
        _refuse(["REFUSED: cycle attribution exceeds the feature total."])
    previous = _cycle_count(entry.get("cycles_used", 0), f"run {args.id!r}")
    return entry, total, previous


def _observed_refusal_digest(args):
    """The digest's reference, refused when its bytes changed since the observed rejection."""
    try:
        directory = os.path.dirname(os.path.abspath(args.file))
        ref = evidence.resolve_evidence_ref(directory, args.digest)
        if ref != args._refusal_digest:
            raise ValueError("digest bytes changed after the observed contract rejection")
    except (OSError, ValueError, TypeError) as error:
        _refuse([f"REFUSED: {error}"])
    return ref


def _check_refusal_closable(entry, ref, args):
    if entry.get("verdict") not in ("PENDING", "BLOCKED"):
        _refuse(["REFUSED: a refused closure cannot rewrite an existing terminal verdict."])
    existing = entry.get("refusal")
    if existing and (existing["digest"] != ref or existing["run_id"] != args.id):
        _refuse(["REFUSED: refusal conflicts with the recorded provenance."])


def _refused_cycle_evidence(doc, entry, args, previous):
    """New or changed refused attribution carries operator-authorized cycle evidence."""
    if "cycles_used" in entry and previous == args.cycles_used:
        return
    if not args.evidence or not args.by:
        _refuse(["REFUSED: new/changed refused attribution requires --evidence and --by."])
    proof = argparse.Namespace(**vars(args), yes=True)
    counted = dict(entry, cycles_used=args.cycles_used)
    digest, authorization = _history_evidence(doc, counted, proof, "record-cycle-evidence")
    entry["cycle_evidence"] = dict(
        source="operator-history", by=args.by, at=now_iso(),
        authorization=authorization, **digest)


def _stamp_refusal(entry, ref, args, agent):
    entry["refusal"] = {
        "source": "close-run", "digest": ref, "run_id": args.id,
        "reason": "validator rejected the return with deliberate contract-refusal "
                  f"status {CONTRACT_REFUSAL_CODE}",
        "by": args.by or agent, "at": now_iso()}
    entry["verdict"] = "BLOCKED"
    entry["ended_at"] = now_iso()
    entry.setdefault("tokens", None)
    entry["cycles_used"] = args.cycles_used
    if args.code_grade:
        entry["code_grade"] = args.code_grade


def cmd_close_run(args):
    agent, judgement = _close_run_preflight(args)
    summary = [f"CLOSED run {args.id!r} verdict={args.verdict}"]
    spend = ""
    for name, argv, fragment, refuse_on_success in _close_run_stages(args, agent, judgement):
        out = (_close_refused_run(args, agent) if name == "run-end" and args.refused_return
               else _stage(name, argv, refuse_on_success))
        if fragment:
            summary.append(fragment)
        if name == "spend":
            spend = out.strip()
    print(" ".join(summary) + f" spend={spend}")
    sys.exit(0)
