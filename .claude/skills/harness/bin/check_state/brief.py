"""BRIEF.md's perspectives and SCs are dischargeable: INV-38/41/49. (FEAT-69)"""
import re
# --- INV-38..41 (FEAT-59 proportional flow; SC-10, SC-15, SC-16, SC-21; DEC-174 direct work).
# Four invariants over the FEAT-59 record shapes, sharing ONE era predicate defined once here.
#
# THE ERA PREDICATE. A record is graded under the FEAT-59 contract when its feature.json
# carries any key that contract introduced -- `mission`, `judgements`, `budget_decisions`,
# `rework` -- or its BRIEF is the by-perspective shape (heading `## Done when — by
# perspective`, C5). A record carrying none of those predates the contract and CANNOT pass a
# ledger check, because nothing that wrote it knew a ledger existed. INV-32's lesson
# (BUG-1071) applies verbatim: measured at this commit, 16 features carry `max_total_cycles`
# above the harness.json default with no `budget_decisions` (the key did not exist) and
# BUG-1309 records cycles_used 18 against max 17. An invariant that fires on all of them and
# admits nothing enforces no rule; it trains its reader to ignore the gate. So a pre-era
# record is NOTED where a check WOULD have fired, and only there: a legacy feature with
# nothing to say gets no line, and a wrongly granted exemption stays visible.
#
# THE PREDICATE ONLY WIDENS GRADING. Any one FEAT-59 key is enough, and so is the BRIEF shape
# on its own; `judgements: []` is an in-era record with an empty ledger, not a legacy one.
# Retroactive grading of existing BRIEFs, plans and notes is out of scope by the brief.
_BY_PERSPECTIVE_HEADING = re.compile(r"^##\s+Done when\s*[—–-]+\s*by perspective\s*$", re.M | re.I)
_FEAT59_KEYS = ("mission", "judgements", "budget_decisions", "rework")
SC_LINE_RE = re.compile(
    r"^[^\S\r\n]*-[^\S\r\n]*(SC-\d+)(?:[^\S\r\n]*\(([^)\r\n]*)\))?"
    r"[^\S\r\n]*:(.*)$", re.M)


def _brief_is_by_perspective(txt):
    return bool(txt) and _BY_PERSPECTIVE_HEADING.search(txt) is not None


def _perspective_key(name):
    """`**reader (reviewer / qa / panel)**` declares `reader`: a trailing parenthetical is a
    gloss on the name, and the SC tag carries the bare name. Case and inner whitespace are
    normalised so `(Code Maintainer)` discharges `**code maintainer**`."""
    return re.sub(r"\s+", " ", re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()).lower()


def _brief_perspectives(txt):
    """The `**name**` lines under the by-perspective heading, up to the next `## `, in order."""
    m = _BY_PERSPECTIVE_HEADING.search(txt)
    body = txt[m.end():]
    nxt = re.search(r"^##\s", body, re.M)
    if nxt:
        body = body[:nxt.start()]
    return [pm.group(1).strip() for pm in re.finditer(r"^\*\*([^*\n]+?)\*\*", body, re.M)]


def brief_scs_with_lines(txt):
    """(id, tag or None, body lines) bounded by each SC's continuation block."""
    out, lines, i = [], txt.splitlines(), 0
    while i < len(lines):
        m = SC_LINE_RE.match(lines[i])
        i += 1
        if not m:
            continue
        body = [m.group(3)]
        while (i < len(lines) and lines[i].strip() and lines[i][:1].isspace()
               and not re.match(r"^\s*-\s*SC-\d+", lines[i])):
            body.append(lines[i])
            i += 1
        out.append((m.group(1), m.group(2), body))
    return out


def _brief_scs(txt):
    """SC bodies flattened for prose invariants, using the same criterion boundaries."""
    return [(sid, tag, " ".join(line.strip() for line in body))
            for sid, tag, body in brief_scs_with_lines(txt)]


# INV-41's notion of INVOKING a gate script, as distinct from naming one. A code span that
# is a command line -- the script with a path or interpreter before it, or arguments after
# it -- is an invocation. A bare `check-state.py` span is a mention (FEAT-59's own SC-10
# reads "`check-state.py` refuses a new BRIEF") UNLESS the sentence runs it ("the reviewer
# runs `check-state.py`") or grades its result ("`check-state.py` exits 0"), which is the
# FEAT-54 SC-04 shape this invariant exists to refuse. A `check-state.py:1868` citation is
# neither: the name is followed by `:`, not by an argument boundary.
_INV41_SCRIPTS = ("check-state.py", "check-domain.py")
_INV41_RUNS_BEFORE = re.compile(r"\b(?:run|runs|running|ran|execute|executes|invoke|invokes|call|calls)\s*$")
_INV41_GRADES_AFTER = re.compile(r"(?:exits?\b|exit\s+code|passes|is\s+green|reports|prints|returns)")


def _inv41_span_invokes(text, m, span, s):
    """FEAT-69: True when the backticked `span` (match `m` in `text`) invokes gate script `s` --
    as a word inside a longer command, or bare with a runs-before / grades-after context."""
    if span != s:
        return re.search(r"(?:^|[\s/(=])%s(?:\s|$|[);|])" % re.escape(s), span) is not None
    before = text[:m.start()].rstrip().lower()
    after = text[m.end():].lstrip().lower()
    return bool(_INV41_RUNS_BEFORE.search(before) or _INV41_GRADES_AFTER.match(after))


def _inv41_span_script(text, m, span):
    """FEAT-69: the gate script the backticked `span` invokes, or None."""
    for s in _INV41_SCRIPTS:
        if s in span and _inv41_span_invokes(text, m, span, s):
            return s
    return None


def _inv41_invocation(text):
    """The gate script `text` invokes, or None."""
    for m in re.finditer(r"`([^`\n]*)`", text):
        s = _inv41_span_script(text, m, m.group(1).strip())
        if s:
            return s
    return None


def _inv41_scoped(text, feat):
    """A `--feature` flag, the feature's own directory, or its id anywhere in the SC text
    scopes the invocation to this feature (SC-16)."""
    if "--feature" in text or f"features/{feat}" in text:
        return True
    if re.search(r"\b%s\b" % re.escape(feat), text):
        return True
    fid = re.match(r"^[A-Za-z]+-\d+", feat)
    return fid is not None and re.search(r"\b%s\b" % re.escape(fid.group(0)), text) is not None

# INV-38 (SC-10): in a by-perspective BRIEF, every declared perspective is discharged by at
# least one SC tagged with it, and every SC is tagged with a declared perspective. The old
# shape is untouched; an abandoned feature's BRIEF is skipped for INV-1/2's reason.
#
# NO `## Requirements`/REQ-NN GRADING EXISTS IN THIS SCRIPT TO SCOPE. The brief asked that a
# by-perspective BRIEF not be graded for a missing Requirements section; the only BRIEF
# checks here are INV-1/2 (the `## Approval` block), which apply to both shapes unchanged.
# Said here so nobody goes looking for a REQ check that was never written.
# INV-41 (SC-16) runs in the same loop because it reads the same SC list: an SC whose text
# invokes check-state.py or check-domain.py with no feature-scoped argument grades the whole
# repository -- other features' debris reddens it (FEAT-54 SC-04, three of six review cycles).
# INV-38 (SC-10): in a by-perspective BRIEF, every declared perspective is discharged by at
# least one SC tagged with it, and every SC is tagged with a declared perspective. The old
# shape is untouched; an abandoned feature's BRIEF is skipped for INV-1/2's reason.
#
# NO `## Requirements`/REQ-NN GRADING EXISTS IN THIS SCRIPT TO SCOPE. The brief asked that a
# by-perspective BRIEF not be graded for a missing Requirements section; the only BRIEF
# checks here are INV-1/2 (the `## Approval` block), which apply to both shapes unchanged.
# Said here so nobody goes looking for a REQ check that was never written.
# INV-41 (SC-16) runs in the same loop because it reads the same SC list: an SC whose text
# invokes check-state.py or check-domain.py with no feature-scoped argument grades the whole
# repository -- other features' debris reddens it (FEAT-54 SC-04, three of six review cycles).
def _inv38_sc_tag(feat, _persp, _pkeys, _discharged, _sid, _tag):
    bad = []
    if _tag is None or not _tag.strip():
        bad.append(f"INV-38 {feat}: BRIEF.md {_sid} carries no perspective tag — write it "
                   f"`- {_sid} (<perspective>): ...` so a declared perspective discharges it "
                   f"(SC-10).")
    elif _perspective_key(_tag) not in _pkeys:
        bad.append(f"INV-38 {feat}: BRIEF.md {_sid} is tagged ({_tag.strip()}), which names no "
                   f"declared perspective ({', '.join(_persp) or 'none declared'}) — every SC "
                   f"discharges a perspective the block declares (SC-10).")
    else:
        _discharged.add(_perspective_key(_tag))
    return bad

def _inv38_undischarged(feat, _pkeys, _discharged):
    bad = []
    for _k, _p in _pkeys.items():
        if _k not in _discharged:
            bad.append(f"INV-38 {feat}: BRIEF.md declares perspective '{_p}' and no SC is tagged "
                       f"({_k}) — a perspective no criterion discharges is a promise nothing "
                       f"grades (SC-10).")
    return bad

def inv_38(ctx, feat):
    bad, warn = [], []
    brief = ctx.briefs.get(feat)
    if brief is None or feat in ctx.abandoned or not _brief_is_by_perspective(brief):
        return bad, warn
    _persp = _brief_perspectives(brief)
    _pkeys = {_perspective_key(p): p for p in _persp}
    _scs = _brief_scs(brief)
    if not _persp:
        bad.append(f"INV-38 {feat}: BRIEF.md carries '## Done when — by perspective' but declares "
                   f"no perspective under it (a line beginning **name**) — an empty block states "
                   f"no done (SC-10).")
    _discharged = set()
    for _sid, _tag, _text in _scs:
        bad.extend(_inv38_sc_tag(feat, _persp, _pkeys, _discharged, _sid, _tag))
    bad.extend(_inv38_undischarged(feat, _pkeys, _discharged))
    return bad, warn


def inv_41(ctx, feat):
    bad, warn = [], []
    brief = ctx.briefs.get(feat)
    if brief is None or feat in ctx.abandoned or not _brief_is_by_perspective(brief):
        return bad, warn
    for _sid, _tag, _text in _brief_scs(brief):
        _script = _inv41_invocation(_text)
        if _script and not _inv41_scoped(_text, feat):
            bad.append(f"INV-41 {feat}: BRIEF.md {_sid} invokes {_script} with no feature-scoped "
                       f"argument (--feature, the feature directory, or {feat}) — repository-wide "
                       f"state is a merge-time check, not a feature criterion (SC-16).")
    return bad, warn

# INV-49 (DEC-163): harness-brief's own rule ("Record the gap where the user signs") had no
# mechanical check -- DEC-163 names it explicitly as one of three surfacings and marks only the
# other two (check-state's own gap note and the init interview) as built; the BRIEF-authoring half
# stayed prose. An SC resting on `verify: automated` whose named evidence kind harness.json does
# not declare runnable (`cmd: null` or `status: excluded`), or whose method is `manual`/spelled
# `MANUAL --`, is a promise nothing proves -- DEC-163 requires that gap named in prose, at the
# signature, or it is silently absorbed exactly as #1033's config-shape gap was. Runs in the same
# by-perspective SC loop as INV-38/41 and shares their scope: an old-shape or abandoned feature's
# BRIEF is skipped for INV-1/2's reason. Violation-class, matching INV-41's own posture.
_INV49_VERIFY_RE = re.compile(r"\bverify:\s*([A-Za-z][A-Za-z0-9_-]*)")
_INV49_EVIDENCE_RE = re.compile(r"\bevidence:\s*([A-Za-z0-9_]+(?:\s*,\s*[A-Za-z0-9_]+)*)", re.I)
_INV49_MANUAL_DASH_RE = re.compile(r"MANUAL\s*[—–-]")
_VERIFICATION_GAPS_HEADING = re.compile(r"^##\s+Verification.*\bgaps\b", re.M | re.I)


def _brief_verification_gaps(txt):
    """The body of the `## Verification gaps` section (through the next `## `), or None when
    the BRIEF carries no such heading at all."""
    m = _VERIFICATION_GAPS_HEADING.search(txt)
    if not m:
        return None
    body = txt[m.end():]
    nxt = re.search(r"^##\s", body, re.M)
    return body[:nxt.start()] if nxt else body


def _kind_unrunnable(cj, kind):
    """A test_kinds entry harness.json does NOT declare runnable: absent, `cmd: null`, or
    `status: excluded` -- the two shapes DEC-163 names, plus a kind nobody declared at all."""
    info = ((cj or {}).get("test_kinds") or {}).get(kind)
    if not isinstance(info, dict):
        return True
    if info.get("cmd") is None:
        return True
    return str(info.get("status", "")).strip().lower() == "excluded"


def _inv49_verify_method(text):
    m = _INV49_VERIFY_RE.search(text)
    return m.group(1).strip().lower() if m else None


def _inv49_evidence_kinds(text):
    m = _INV49_EVIDENCE_RE.search(text)
    return [k.strip() for k in m.group(1).split(",") if k.strip()] if m else []


def _inv49_gap_reason(cj, text):
    """Why `text`'s SC needs a `## Verification gaps` line, or None when it needs none."""
    method = _inv49_verify_method(text)
    if method == "manual" or _INV49_MANUAL_DASH_RE.search(text):
        return "verify: manual"
    if method != "automated":
        return None
    unrunnable = [k for k in _inv49_evidence_kinds(text) if _kind_unrunnable(cj, k)]
    return f"evidence kind {', '.join(unrunnable)} with no runner" if unrunnable else None


def _inv49_sc_hit(feat, sid, reason):
    return (f"INV-49 {feat}: BRIEF.md {sid} rests on {reason} but '## Verification gaps' names "
            f"no line for {sid} — record the gap where the user signs (DEC-163).")


def _inv49_graded(ctx, feat, brief):
    """FEAT-69: the record INV-49 grades -- a live by-perspective BRIEF with a plan.yaml."""
    # A record with no plan.yaml has no station and no signature: a DEC-174 direct build
    # (FEAT-59) that predates test_kinds. It is outside the planned flow this rule grades.
    return not (brief is None or feat in ctx.abandoned or not _brief_is_by_perspective(brief)
                or ctx.plan_docs.get(feat) is None)


def _inv49_hits(ctx, feat, brief):
    """FEAT-69: one finding per SC resting on an unrunnable kind that `## Verification gaps` does
    not name."""
    cj = ctx.cj if isinstance(ctx.cj, dict) else {}
    gaps = _brief_verification_gaps(brief)
    hits = []
    for _sid, _tag, _text in _brief_scs(brief):
        _reason = _inv49_gap_reason(cj, _text)
        if _reason and _inv49_unnamed(gaps, _sid):
            hits.append(_inv49_sc_hit(feat, _sid, _reason))
    return hits


def _inv49_unnamed(gaps, sid):
    """FEAT-69: True when no `## Verification gaps` section names `sid` (an absent section names
    nothing)."""
    return gaps is None or sid not in gaps


def inv_49(ctx, feat):
    bad, warn = [], []
    brief = ctx.briefs.get(feat)
    if not _inv49_graded(ctx, feat, brief):
        return bad, warn
    bad.extend(_inv49_hits(ctx, feat, brief))
    return bad, warn
