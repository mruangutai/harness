"""feature_record/spend.py — the read-only spend measurement: wall-clock minutes, tokens and
the rework window a ruling is compared to.
"""
import json
import re
import sys
from datetime import datetime
from feature_record.judgements import _judgements_of
from feature_record.read import _read_doc, _runs


def _parse_iso(value):
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _run_interval(entry):
    """(start, end) of a closed run, or None for one still open, unstamped or inverted."""
    started = _parse_iso(entry.get("started_at"))
    ended = _parse_iso(entry.get("ended_at"))
    if started is None or ended is None or ended <= started:
        return None
    return started, ended


def _elapsed_seconds(entries):
    """Whole seconds covered by at least one closed run: the union of their intervals (#2034).

    Concurrent runs share their clock. Summing durations counted BUG-1016's three distill
    squads, 24 minutes side by side, as 72."""
    total, reach = 0, None
    for start, end in sorted(filter(None, map(_run_interval, entries))):
        if reach is None or start > reach:
            total += (end - start).total_seconds()
            reach = end
        elif end > reach:
            total += (end - reach).total_seconds()
            reach = end
    return int(total)


# A run is a validate run when its id carries the `validate-` token at the start or after a
# `-`, and a fix run likewise for `fix-`. Real ids are date-prefixed run-dir slugs
# (`2026-09-11-05-validate-validator`; the corpus holds 181 of that shape against 1 bare
# `validate-validator`), and the first draft's `startswith("validate-")` never opened the
# window on any of them — so the build-phase SPEND advisory (SC-19) never fired and the
# rework-ratio KPI read 0, silently. Token-bounded, not substring: `postfix-eng` is no fix.
VALIDATE_RUN = re.compile(r"(?:^|-)validate-")


FIX_RUN = re.compile(r"(?:^|-)fix-")


# #2032: feature-close distillation (DEC-145) runs after the merge and is never rework. Same
# token rule: `redistill-eng` is not a distill run.
DISTILL_RUN = re.compile(r"(?:^|-)distill-")


def _regate_stamps(doc):
    """The parsed `at` of every `regate` judgement; an unparsable stamp is left out."""
    stamps = (_parse_iso(j.get("at")) for j in _judgements_of(doc, "regate"))
    return [at for at in stamps if at is not None]


def _not_before(at, opened):
    """`at >= opened`, False when one is naive and the other aware: they do not compare, and a
    hand-written naive stamp must not crash `spend`, which the hook calls."""
    return (at.tzinfo is None) == (opened.tzinfo is None) and at >= opened


def _window_opened(runs, first_validate):
    """The first validate run's start, or None when there is no validate run or no start."""
    return _parse_iso(runs[first_validate].get("started_at")) if first_validate is not None else None


def _regate_rounds(doc, opened):
    """The `regate` judgements recorded at or after `opened`, or None when the window has no
    start (no validate run, or one with no `started_at`) or holds no regate (#2222)."""
    if opened is None:
        return None
    return sum(1 for at in _regate_stamps(doc) if _not_before(at, opened)) or None


def spend_for(doc):
    """The spend summary for a parsed feature.json (pure; used by `spend`).

    `wall_clock_minutes` is the whole feature — the lagging figure the briefing reports.
    `rework_minutes` and `rework_rounds` are the REWORK WINDOW: every run from the first
    validate run onward except feature-close distill runs, and the rounds within it.
    Minutes are elapsed time, the union of the runs' intervals; tokens are a sum. The operator's
    `rework.wall_clock_minutes` ruling is a budget for rework, so the hook compares it to
    the window, never to the whole — before this split a 60-minute plan run and a 40-minute
    build ate 100 of a 120-minute ruling before the first fix round existed.

    A round is one `regate` judgement in the window ("each round is one cycles_used and one
    regate judgement", build-phase.md), so a fix the main session builds directly, which has no
    `fix-` run, still counts (#2222). A window holding no regate — a ledger from before regates
    were recorded — keeps the count of its `fix-` runs. The two are never summed.
    """
    runs = [entry for entry in _runs(doc) if isinstance(entry, dict)]
    seconds = _elapsed_seconds(runs)
    first_validate = next((i for i, entry in enumerate(runs)
                           if VALIDATE_RUN.search(str(entry.get("id", "")))), None)
    window = _rework_window(runs, first_validate)
    github = doc.get("github")
    has_build_entry = isinstance(github, dict) and "build_entry" in github
    return {"runs": len(runs), "wall_clock_minutes": seconds // 60, "tokens": _tokens(runs),
            "phase": "build" if has_build_entry else "plan",
            "rework_minutes": _elapsed_seconds(window) // 60,
            "rework_rounds": _rework_rounds(doc, runs, first_validate, window)}


def _rework_rounds(doc, runs, first_validate, window):
    """The window's regate judgements, else (none recorded) the count of its `fix-` runs."""
    rounds = _regate_rounds(doc, _window_opened(runs, first_validate))
    if rounds is None:
        rounds = sum(1 for entry in window if FIX_RUN.search(str(entry.get("id", ""))))
    return rounds


def _tokens(runs):
    """The sum of every measured integer `tokens`, or None when no run carries one."""
    measured = [entry["tokens"] for entry in runs
                if isinstance(entry.get("tokens"), int) and not isinstance(entry.get("tokens"), bool)]
    return sum(measured) if measured else None


def _rework_window(runs, first_validate):
    """Every run from the first validate run onward, feature-close distill runs excluded."""
    return [entry for entry in (runs[first_validate:] if first_validate is not None else [])
            if not DISTILL_RUN.search(str(entry.get("id", "")))]


def cmd_spend(args):
    print(json.dumps(spend_for(_read_doc(args.file))))
    sys.exit(0)
