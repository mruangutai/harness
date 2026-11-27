"""feature_record/judgements.py — the judgements[] ledger (SC-21): the `judgement` and
`overrule-amendment` verbs and the helpers every verb uses to append one judgement.
"""
import sys
from datetime import datetime, timezone
from feature_record.write import _apply, _refuse


JUDGEMENT_KINDS = ("mission", "finding_kind", "regate", "continue", "succession", "amendment", "reject")


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _judgements_of(doc, kind):
    """Every judgement entry of `kind` (the stored kind compared stripped), in ledger order."""
    return [e for e in (doc.get("judgements") or [])
            if isinstance(e, dict) and str(e.get("kind", "")).strip() == kind]


def _kind_count(doc, kind):
    return len(_judgements_of(doc, kind))


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
