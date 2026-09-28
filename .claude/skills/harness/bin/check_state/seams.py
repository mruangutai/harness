"""Every phase seam left a well-formed handoff note: INV-17.

FEAT-69: split out of check-state.py by declared reads; bodies and comments moved byte-for-byte.
"""
import glob, os
import handoff_policy
import harness_boundary
from check_state.ctx import SEAM_NOTES, STATUS_ORDER, read
try:
    handoff_done_when = harness_boundary.load_repo_module("handoff_done_when")
except harness_boundary.RepoModuleError as _hdw_error:
    handoff_done_when, _handoff_done_when_error = None, _hdw_error.cause
HANDOFF_SECTIONS = ["## next", "## trust", "## dead ends", "## working set", "## done when"]
HANDOFF_NARRATIVE_HEADINGS = HANDOFF_SECTIONS[:4]

# The literal exemption set. FEAT-01 and FEAT-02 are Done, carry zero handoff notes, and
# finished before DEC-159 existed: no seam was crossed, so no honest handoff note can be
# written for them and none will be fabricated (PRINCIPLES rule 15). A finite list, not an
# inferred rule — no future feature can join it.
#
# Matched by PREFIX because a feature directory is FEAT-01-<slug>, and FEAT-01's happens to
# be bare today. Exact equality would pass every fixture and still raise three violations
# on the live corpus the moment either directory gained a slug.
#
# This one is a SILENT skip, unlike the plan-keyed exemption below, which reports. The
# difference is deliberate: reporting exists so a WRONGLY granted exemption is visible, and
# a two-element list that cannot grow has nothing to grant wrongly.
HANDOFF_EXEMPT_LITERAL = ("FEAT-01", "FEAT-02")

# --- INV-17 (DEC-159): squad seams hand off through notes/handoff-<stem>.md.
# A feature whose status: sits past a seam with no handoff note for the crossing lost the
# predecessor's working memory — recoverable (disk-only is supported) but never silent.
#
# This block was keyed on a `phase` field until DEC-150/D-12 (FEAT-14). phase and status
# collapsed into ONE field whose values are the GitHub board's six columns, and phase was
# deleted from every feature file. The old constant — named PHASE_ORDER, holding
# plan/build/validate/ship — is recorded here because leaving it standing was the actual
# hazard: with phase gone from the corpus the read returns the empty string on every
# feature, the membership test fails on every feature, and the loop `continue`s on every
# feature. INV-17 would stop examining anything at all while check-state.py went on exiting
# exactly as it does today. A gate that examines nothing reports nothing wrong.
#
def _inv17_station(ctx, feat, fy):
    """(station, bad) — station is falsy when the seam invariants cannot or need not run."""
    bad = []
    fpath = ctx.fpath
    _status = ctx.station(feat)
    if not _status:
        # NO STATION AT ALL is still a skip, and deliberately so: a feature directory with no
        # plan.yaml is a PLAN.md-era record, and INV-3 already reports a plan that should exist
        # and does not. Reporting it here too would double every such line.
        return None, bad
    if _status not in STATUS_ORDER:
        # LOUD, per A-03: nothing denies this value at write time any more. See the comment
        # above STATUS_ORDER for why the old silent skip's justification no longer holds.
        bad.append(f"{fpath(feat, 'plan.yaml')} records station '{_status}', which is not in "
                   f"the station vocabulary ({', '.join(STATUS_ORDER)}), so its seam "
                   f"invariants cannot be checked. Set it with `plan-merge.py "
                   f"set-feature-station`, which validates the station before it writes.")
        return None, bad
    return _status, bad

def _inv17_owed_stems(feat, fy, _status):
    """Seam stems whose handoff note is absent, minus the literal exemption."""
    _lit = feat.startswith(HANDOFF_EXEMPT_LITERAL)
    owed = []
    for prev in SEAM_NOTES[_status]:
        hp = os.path.join(os.path.dirname(fy), "notes", f"handoff-{prev}.md")
        if not os.path.isfile(hp):
            if _lit:
                continue
            owed.append(prev)
    return owed

def _inv17_missing_notes(feat, fy, _status):
    bad = []
    # Evaluated LAZILY — only when a required note is actually found missing, never for
    # every feature on every run — and cached, so a feature owing three notes reads its
    # plan once and emits ONE line rather than three near-identical ones.
    _ex_why, _ex_detail, _ex_stems = None, "", []
    for prev in _inv17_owed_stems(feat, fy, _status):
        if _ex_why is None:
            _ex_why, _ex_detail = handoff_policy.exempt_reason(os.path.dirname(fy))
        if _ex_why:
            _ex_stems.append(prev)
            continue
        # M-01: this said `pm_.group(1)` — a leftover from the regex the F-02
        # conversion deleted when it renamed the parsed value. Used once, assigned
        # nowhere, so it raised NameError on the ONE condition INV-17 exists to
        # detect, aborting INV-13/15/16/18/21 and INV-10 with no "could not run"
        # message. A crash exits 1, which is what a real violation exits, so
        # /harness entry reported "violations found" for a typo. Introduced by the
        # fix for F-02 and caught by the re-review, not by any gate.
        bad.append(f"{feat}: status is '{_status}' but notes/handoff-{prev}.md is "
                   f"missing — the {prev} seam was crossed without a handoff; the "
                   f"successor is on the disk-only path (DEC-159).{_ex_detail}")
        continue
    return bad, _ex_why, _ex_stems

def _inv17_missing_headings(ctx, hl, _rel_handoff):
    miss = [h for h in HANDOFF_NARRATIVE_HEADINGS if h not in hl]
    if "## done when" not in hl and _rel_handoff not in ctx.handoff_baseline:
        miss.append("## done when")
    return miss

def _inv17_section_body(hl, _i):
    _body = []
    for _n in hl[_i + 1:]:
        if _n.startswith("##"):
            break
        _body.append(_n)
    return _body

def _inv17_empty_sections(hl):
    _empty = []
    for _i, _l in enumerate(hl):
        if _l not in HANDOFF_NARRATIVE_HEADINGS:
            continue
        _body = _inv17_section_body(hl, _i)
        if not any(_b for _b in _body):
            _empty.append(_l)
    return _empty

def _inv17_done_when_problems(ctx, hl, _rel_handoff, _text):
    root = ctx.root
    _done_when_problems = []
    if "## done when" in hl:
        if handoff_done_when is None:
            _done_when_problems.append(
                "handoff_done_when.py could not be imported: "
                f"{type(_handoff_done_when_error).__name__}: {_handoff_done_when_error}")
        else:
            _done_when_problems.extend(
                handoff_done_when.problems(_rel_handoff, _text, root, resolve=False))
    return _done_when_problems

def _inv17_why(miss, hl, _empty, _done_when_problems):
    """The assembled reasons; empty exactly when the note passes the shape."""
    why = []
    if miss:
        why.append(f"missing section(s) {miss}; follow templates/HANDOFF.md")
    if len(hl) > 60: why.append(f"{len(hl)} lines vs cap 60")
    if _empty: why.append(f"empty section(s) {_empty}")
    why.extend(_done_when_problems)
    return why

def _inv17_note_shape(ctx, feat, hp):
    _text = read(hp) or ""
    hl = [l.strip().lower() for l in _text.splitlines()]
    _rel_handoff = os.path.normpath(os.path.relpath(hp, ctx.root)).replace(os.sep, "/")
    miss = _inv17_missing_headings(ctx, hl, _rel_handoff)
    # INV-17 empty-body check (FEAT-31 T-10)
    # SC-15 requires the relay be SHOWN TO FAIL when "## Next" is emptied. Until now it
    # could not be: `miss` tests only that the HEADING is present, so a note carrying all
    # four headings and nothing under any of them passed. A heading with no body is the
    # shape of a handoff that satisfies the gate and tells the successor nothing.
    #
    # A body runs from its heading to the next line whose stripped form starts with two
    # hash characters, or end of file, and is EMPTY when every one of those lines is blank
    # after stripping. Only headings actually PRESENT are examined — an absent heading is
    # already `miss`'s finding and must not be reported twice under a second name.
    #
    # MIGRATION, re-measured at 1929774 in the FEAT-31 worktree rather than copied from
    # the plan: 74 notes match, and ZERO have an empty required section. The three
    # non-seam stems T-14's glob newly reaches carry 13, 6 and 8 non-blank lines under
    # "## Next" (FEAT-09/handoff-ship.md, FEAT-22/handoff-t09-rotation.md,
    # FEAT-24/handoff-ship.md) — the same figures the plan measured at 7299669. So this
    # adds zero violations.
    _empty = _inv17_empty_sections(hl)
    _done_when_problems = _inv17_done_when_problems(ctx, hl, _rel_handoff, _text)
    if miss or len(hl) > 60 or _empty or _done_when_problems:
        why = _inv17_why(miss, hl, _empty, _done_when_problems)
        return [f"{feat}: notes/{os.path.basename(hp)} fails the shape "
                f"({'; '.join(why)}) — a freeform handoff drifts like an "
                f"unvalidated digest did (DEC-159/160)."]
    return []

def _inv17_shape_pass(ctx, feat, fy):
    bad = []
    for hp in sorted(glob.glob(os.path.join(os.path.dirname(fy), "notes", "handoff-*.md"))):
        bad.extend(_inv17_note_shape(ctx, feat, hp))
    return bad

def _inv17_record_gate(ctx, feat, fy):
    """(proceed, findings): the record must exist and parse before any seam is graded."""
    if not os.path.isfile(fy):
        return False, []
    e = ctx.record_error(feat)
    if e is not None:
        return False, [f"{ctx.fpath(feat, 'feature.json')} does not parse, so its seam invariants "
                       f"cannot be checked: {e}"]
    return True, []

def inv_17(ctx, feat):
    bad, warn = [], []
    fy = ctx.path(feat, 'feature.json')
    proceed, bad = _inv17_record_gate(ctx, feat, fy)
    if not proceed:
        return bad, warn
    _status, _gate = _inv17_station(ctx, feat, fy)
    bad.extend(_gate)
    if not _status:
        return bad, warn
    _missing, _ex_why, _ex_stems = _inv17_missing_notes(feat, fy, _status)
    bad.extend(_missing)
    # INV-17 handoff shape pass, all stems (FEAT-31 T-14)
    # ONE call site for the shape check, by STRUCTURE and not by an ordering rule: the loop
    # above now owns only the missing-note question, and this glob owns only the shape
    # question. Because the glob finds every note including the seam stems, no file can be
    # reported twice — there is no second place that could report it.
    #
    # WHY A GLOB. check-domain.py's RE_HANDOFF already accepts handoff-[a-z0-9-]+.md, so a
    # mid-phase note is already legal to write and was, until now, never opened. Measured at
    # cf51dce in the FEAT-31 worktree: 74 notes match, 71 on seam stems and THREE on
    # non-seam stems newly in reach — FEAT-09/handoff-ship.md (56 lines),
    # FEAT-22/handoff-t09-rotation.md (50), FEAT-24/handoff-ship.md (60, exactly on the cap
    # with no headroom). All 74 carry the four headings and are within the cap, so this pass
    # adds ZERO violations at that sha. The plan measured 69 at 7299669; the five-note gap
    # reconciles exactly — FEAT-30's three notes plus FEAT-29's handoff-validate.md plus
    # FEAT-31's own handoff-build.md all landed after that reading.
    #
    # EXEMPTIONS DO NOT REACH HERE, deliberately. HANDOFF_EXEMPT_LITERAL and
    # handoff_policy.exempt_reason gate the missing-note branch above only: they answer whether a note is
    # OWED. Once a file exists its shape is checked whoever wrote it and whatever the
    # feature's status.
    bad.extend(_inv17_shape_pass(ctx, feat, fy))
    if _ex_stems:
        # Reported, never silent: a wrongly granted exemption must be VISIBLE rather than
        # look like a pass. It goes through warn and its text must NOT carry the word that
        # marks a violation — the shipping gate builds a baseline from those lines, and a
        # note worded as one would pollute that diff.
        warn.append(f"INV-17 {feat}: exempt from handoff notes — {_ex_why}. Suppressed "
                    + ", ".join(f"handoff-{s}" for s in _ex_stems) + ".")
    return bad, warn
