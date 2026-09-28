"""plan.yaml is a well-formed, approved record: INV-35/3/4/5/34/32/44.

FEAT-69: split out of check-state.py by declared reads; bodies and comments moved byte-for-byte.
"""
import os, re
from check_state.ctx import approved, has_approval_block, read
# --- INV-35 (issue #251): a plan.yaml plain scalar carrying a space then a `#` immediately
# followed by a digit truncates SILENTLY under YAML's plain-scalar comment rule -- `#217`
# embedded in `title: close out the fix for #217` stops the scalar exactly at the `#` and the
# loss is invisible: the file still parses, `artifact_accessors.load_plan` returns cleanly, and
# nothing downstream can tell a truncated value from one that never mentioned the number.
#
# THIS WALKS THE RAW SOURCE, NEVER THE PARSED DOC. The parsed doc is the wrong side of the
# loss to look from -- by the time safe_load has run, the deleted text is already gone, so a
# check keyed on plan_docs above cannot see what it exists to catch.
#
# EVERY CHECK IS ANCHORED TO THE VALUE, NEVER THE RAW LINE. `_line_value` strips the leading
# indentation, an optional sequence dash and an optional `key: ` prefix, and every downstream
# decision -- block-scalar-open, quoted-vs-plain -- is made against what remains. A validator
# review of an earlier cut of this invariant found TWO live false negatives from skipping this
# step and matching against the raw line instead, both reproduced against this repo's own
# tree before the fix:
#   (1) `_BLOCK_SCALAR_OPEN.search(line)` matched a coincidental `key:>value` substring
#       anywhere in the line -- e.g. `title: fix #217 for the ratio:>5` -- misreading an
#       ordinary line as a block-scalar opener and skipping the real truncation earlier on
#       it. A `.fullmatch` against the isolated value cannot be fooled by a substring.
#   (2) The prior quote tracker toggled `in_quote` on EVERY `'`/`"` character anywhere on the
#       line, so a plain scalar with an odd count of apostrophes before the truncation point
#       (`the operator's design note for #806`, live in
#       FEAT-34-worktree-act3-enforced/plan.yaml D-03 at review time) flipped the scanner into
#       treating the real ` #806` as quoted and reported nothing.
#
# THE FIX RESTS ON ONE YAML FACT: only the FIRST character of a value can open a quoted
# scalar. If it is not `'`/`"`, the value is plain for its ENTIRE remaining length and no
# quote character appearing later has any special meaning at all -- it is literal text, full
# stop. So a plain value needs no quote-tracking whatsoever; it needs only the first
# whitespace-preceded (or value-initial) `#`, which is where YAML's comment actually starts.
# A quoted value tracks its own delimiter to the close (a doubled quote is YAML's escape for
# a literal one), and nothing after that close can be lost data -- a proper quoted scalar's
# close ends the value; what follows is comment or malformed, never truncated content.
#
# BLOCK SCALARS ARE EXEMPT BY THE YAML SPEC ITSELF: a `|`/`>` block's content is literal, and a
# `#` inside it is data, never a comment. `_block_indent` tracks the opening key's indentation
# and skips every more-indented (or blank) line that follows, so a `verify: |` body can freely
# quote an issue number without tripping this.
#
# STOPS AT THE FIRST UNQUOTED `#` in a plain value, never scans past it. That hash is where
# YAML's comment actually starts, whether or not a digit follows it -- everything after it is
# already comment text, so a second `#<digit>` deeper in an ordinary trailing comment
# (`# see issue #217`) must not be mistaken for a second truncation point.
#
# MULTI-LINE QUOTED SCALARS KEEP THEIR QUOTE STATE ACROSS PHYSICAL LINES. YAML folds those
# lines into one scalar, so a `#<digit>` on a continuation line is still quoted data. The
# scanner therefore suppresses every continuation line through the closing delimiter, then
# resumes ordinary line scanning. Single quotes escape a quote by doubling it; double quotes
# escape with a backslash.
#
# THE KEY ITSELF CAN BE QUOTED OR HYPHENATED, and `_KEY_PREFIX` must recognise both or the
# strip fails silently in the dangerous direction. A validator's second pass (cycle 2, PR
# #1145) proved this live: an earlier cut matched only a bare identifier key, so a quoted key
# (`"my-key": value #217`) fell through the optional key group entirely, and
# `_unquoted_hash_digit` then read the key's OWN opening quote as `value[0]`, tracked to the
# key's own closing quote, and returned None -- silently swallowing the real truncation that
# followed. `_KEY_PREFIX` now recognises three key shapes: a bare identifier (now including
# `-`, since a hyphenated unquoted key hit the same fall-through in the block-scalar-open
# direction, a false POSITIVE rather than a silence but the same root cause), a
# double-quoted key, or a single-quoted key.
_KEY_PREFIX = re.compile(
    r'^\s*(?:-\s+)?(?:(?:[A-Za-z_][A-Za-z0-9_-]*|"[^"]*"|\'[^\']*\'):\s+)?'
)
_BLOCK_SCALAR_VALUE = re.compile(r"^[|>][+\-]?\d*\s*(#.*)?$")


def _line_value(line):
    return line[_KEY_PREFIX.match(line).end():]


def _quoted_escape(value, quote, i):
    """FEAT-69: the length of the escape at `i` -- a backslash in a double-quoted scalar, a doubled
    quote in a single-quoted one -- or 0 when `value[i]` is not an escape."""
    if quote == '"' and value[i] == "\\":
        return 2
    if quote == "'" and value[i] == quote and i + 1 < len(value) and value[i + 1] == quote:
        return 2
    return 0


def _quoted_scalar_closed(value, quote, start):
    i = start
    while i < len(value):
        skip = _quoted_escape(value, quote, i)
        if skip:
            i += skip
            continue
        if value[i] == quote:
            return True
        i += 1
    return False


def _comment_hash_at(value, i):
    """FEAT-69: True when `value[i]` is a `#` that opens a plain-scalar comment -- at the start or
    after whitespace."""
    return value[i] == "#" and (i == 0 or value[i - 1].isspace())


def _unquoted_hash_digit(value):
    for i in range(len(value)):
        if _comment_hash_at(value, i):
            return i if value[i + 1:i + 2].isdigit() else None
    return None


def _inv35_quoted_after(_line, _quoted_scalar):
    """The quote a continued quoted scalar still holds open after `_line`, or None once it
    closes on this line."""
    if _quoted_scalar_closed(_line, _quoted_scalar, 0):
        return None
    return _quoted_scalar


def _inv35_scan_value(_value, _indent):
    """The scanner state after a plain line's value: ((block_indent, quoted_scalar), hit),
    where hit is the issue number an unquoted ` #NN` would truncate, or None."""
    if _BLOCK_SCALAR_VALUE.fullmatch(_value.rstrip()):
        return (_indent, None), None
    if _value[:1] in ("'", '"'):
        if not _quoted_scalar_closed(_value, _value[0], 1):
            return (None, _value[0]), None
        return (None, None), None
    _hit = _unquoted_hash_digit(_value)
    if _hit is None:
        return (None, None), None
    return (None, None), re.match(r"\d+", _value[_hit + 1:]).group(0)


def _inv35_scan_line(_line, _state):
    """One step of INV-35's line scanner: the next (block_indent, quoted_scalar) state and
    the hit `_inv35_scan_value` reports for a plain line, or None for a line the scanner
    skips (inside an open quoted or block scalar, blank, or a comment)."""
    _block_indent, _quoted_scalar = _state
    if _quoted_scalar is not None:
        return (_block_indent, _inv35_quoted_after(_line, _quoted_scalar)), None
    _stripped = _line.strip()
    _indent = len(_line) - len(_line.lstrip(" "))
    if _block_indent is not None and (_stripped == "" or _indent > _block_indent):
        return (_block_indent, _quoted_scalar), None
    if not _stripped or _stripped.startswith("#"):
        return (None, _quoted_scalar), None
    return _inv35_scan_value(_line_value(_line), _indent)


def inv_35(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    _feat, _p = feat, ctx.path(feat, 'plan.yaml')
    _txt = read(_p)
    if _txt is None:
        return bad, warn
    _state = (None, None)
    for _lineno, _line in enumerate(_txt.splitlines(), start=1):
        _state, _num = _inv35_scan_line(_line, _state)
        if _num is None:
            continue
        bad.append(
            f"INV-35: {fpath(_feat, 'plan.yaml')}:{_lineno} carries an unquoted scalar with "
            f"` #{_num}` -- YAML's plain-scalar comment rule truncates everything from that "
            f"`#` onward, silently, even though the file still parses. Quote the value so "
            f"the issue number stays in the data: {_line.strip()!r}."
        )
    return bad, warn

# --- INV-3/4/5 on plan.yaml (DEC-182). Same three invariants, read from a mapping
# instead of scraped out of prose. load_plan has already guaranteed every task carries the
# fields REQUIRED_TASK_FIELDS names, so INV-4's "no change_type" case cannot reach here —
# it is a load error now, caught above. What remains is what the loader does not police:
# the approval block, and STATE.md pointing at a task the plan does not contain.
# A STATION-ONLY RECORD IS OUT OF SCOPE FOR BOTH (FEAT-41 T-19). Neither question applies to it:
# it declares a station and no tasks, so it HAS no goal to sign and no task ids for STATE.md to
# name. Backfilling twelve of them made these two checks visible for directories that had been
# skipped for as long as they carried no plan at all -- 31 lines, none of them a real finding.
#
# THIS IS SCOPING, NOT A FAIL-OPEN, and the alternative shows why: the only way to satisfy the
# approval check here would be to write an `approval:` block into each of the twelve, which would
# FABRICATE twelve signatures nobody gave. A check that can only be passed by inventing a record
# is measuring the wrong thing.
#
# KEYED ON THE POSITIVE DECLARATION, NEVER ON THE ABSENCE OF TASKS (FEAT-41 MF-3). The first
# version tested `if not doc["tasks"]`, and cycle 3 proved end to end what that cost: a Bash write
# emptied a SIGNED plan's `tasks:` while keeping its `approval:` and `status:`, the document
# inherited this exemption, and a real dangling-STATE.md-task violation went SILENT. An emptied
# plan carries no `station_only:` marker, so it now fails to LOAD -- which is already a violation,
# so the forged state is louder than the check it was escaping.
#
# AN ABSENCE CANNOT BE A CREDENTIAL. A checker must be TOLD a fact, never infer one from a missing
# field; that is the same shape as the B-7 fail-open the loader's own comment records.
#
# THE EXEMPTION CANNOT WIDEN SILENTLY, and the guarantee is that the MARKER IS NOT MINTABLE: a
# plan carrying tasks cannot wear it, enforced at `artifact_accessors.load_plan` because that is
# chokepoint every reader passes through -- a writer-side guard would leave the unmediated Bash
# route open, which the BRIEF itself discloses.
#
# THIS COMMENT PREVIOUSLY CITED case (inv34.d) AS ASSERTING THAT, AND IT DID NOT (FEAT-41 HIGH-1).
# Two of cycle 4's reviewers checked at source: (inv34.d)'s fixture carries no marker, so the test
# named here never tested the guarantee claimed here. A false citation is worse than a missing test
# -- it stops the next reader looking. Cases (inv34.e) and (inv34.f) cover the two forgeries.
def _inv3_plan_yaml(ctx, feat, doc):
    """The plan.yaml (DEC-182) branch of INV-3: the loaded mapping's approval block."""
    bad, warn = [], []
    fpath = ctx.fpath
    if doc.get("station_only") is True:
        return bad, warn
    _appr = doc.get("approval")
    if not isinstance(_appr, dict):
        bad.append(f"{fpath(feat, 'plan.yaml')} has no `approval:` block — cannot tell if the goal "
                   f"is signed.")
    elif str(_appr.get("status", "")).strip().lower() != "approved":
        warn.append(f"{fpath(feat, 'plan.yaml')} approval is pending — awaiting the user.")
    return bad, warn


def _inv3_plan_md(ctx, feat, plan):
    """The PLAN.md-era branch of INV-3: the prose record's '## Approval' section."""
    bad, warn = [], []
    fpath = ctx.fpath
    if not has_approval_block(plan):
        bad.append(f"{fpath(feat, 'PLAN.md')} has no '## Approval' section.")
    elif not approved(plan):
        warn.append(f"{fpath(feat, 'PLAN.md')} approval is pending — awaiting the user.")
    return bad, warn


def inv_3(ctx, feat):
    """INV-3: the plan is signed too, and re-planning resets that signature. plan.yaml
    (DEC-182) when the feature carries one, else the PLAN.md-era record."""
    doc = ctx.plan_docs.get(feat)
    if doc is not None:
        return _inv3_plan_yaml(ctx, feat, doc)
    plan = ctx.plans.get(feat)
    if plan is None:
        return [], []
    return _inv3_plan_md(ctx, feat, plan)


def _plan_md_tasks(plan):
    # Tasks may be list items (`- T-01:`) or headings (`### T-01 —`) — the smoke's pm
    # wrote headings and the list-only regex made this check silently vacuous (DEC-129).
    return re.findall(r"^(?:-\s*|#+\s*)(T-\d+)\b(.*?)(?=^(?:-\s*|#+\s*)T-\d+\b|\Z)",
                      plan, re.M | re.S)


def inv_4(ctx, feat):
    """INV-4: every PLAN.md task carries change_type, or the qa gate cannot apply. On
    plan.yaml this is a LOAD error (REQUIRED_TASK_FIELDS) and never reaches here."""
    bad, warn = [], []
    fpath = ctx.fpath
    if feat in ctx.plan_docs:
        return bad, warn
    plan = ctx.plans.get(feat)
    if plan is None:
        return bad, warn
    tasks = _plan_md_tasks(plan)
    if not tasks and re.search(r"\bT-\d+\b", plan):
        bad.append(f"{fpath(feat, 'PLAN.md')} mentions T-NN ids but none parse as tasks — "
                   f"INV-4/5 would be vacuous. Fix the task format.")
    for tid, body in tasks:
        if "change_type:" not in body:
            bad.append(f"{feat}: {tid} has no change_type: — the qa gate cannot be applied to it.")
    return bad, warn


def _inv5_plan_yaml(ctx, feat, doc, _state):
    """The plan.yaml branch: every T-id STATE.md names is a task the plan declares. A
    station-only record is out of scope (see the INV-3/4/5 note above)."""
    bad, warn = [], []
    fpath = ctx.fpath
    if doc.get("station_only") is True:
        return bad, warn
    _plan_ids = {str(t["id"]) for t in doc["tasks"]}
    for _tid in set(re.findall(r"\bT-[0-9A-Za-z]+\b", _state)):
        if _tid not in _plan_ids:
            bad.append(f"{fpath(feat, 'STATE.md')} references {_tid}, which is absent from its "
                       f"plan.yaml.")
    return bad, warn


def _inv5_plan_md(ctx, feat, plan, _state):
    """The PLAN.md branch: every T-NN STATE.md names is a task the prose plan parses."""
    bad, warn = [], []
    fpath = ctx.fpath
    plan_ids = {tid for tid, _ in _plan_md_tasks(plan)}
    for tid in set(re.findall(r"\bT-\d+\b", _state)):
        if tid not in plan_ids:
            bad.append(f"{fpath(feat, 'STATE.md')} references {tid}, which is absent from its PLAN.md.")
    return bad, warn


def inv_5(ctx, feat):
    """INV-5: no flow's STATE.md points at a task its plan does not contain."""
    bad, warn = [], []
    _state = ctx.states.get(feat)
    if not _state:
        return bad, warn
    doc = ctx.plan_docs.get(feat)
    if doc is not None:
        return _inv5_plan_yaml(ctx, feat, doc, _state)
    plan = ctx.plans.get(feat)
    if plan is None:
        return bad, warn
    return _inv5_plan_md(ctx, feat, plan, _state)

# INV-32 ERA RESOLUTION BEGIN (BUG-1071)
# WHY AN ERA GUARD EXISTS AT ALL. FEAT-45 T-07 shipped INV-32 with no era boundary, so it
# graded every plan ever signed: all 32 approved plans in this tree failed it, and NONE
# could pass, because a plan signed before the adversarial panel existed cannot carry a
# record of it. FEAT-45's own plan was among the 32. An invariant that fires on 100% of a
# corpus and admits nothing does not enforce a rule -- it only trains its reader to ignore
# the gate, which is the failure mode this file exists to prevent (see the INV-10 note at
# the foot of this script on the cost of a dead invariant). The rule was right; its
# retroactive reach was the defect.
#
# THE BOUNDARY IS PER-PROJECT CONFIG, NOT A LITERAL (panel finding F2). One
# control-plane clone runs this script against MANY product repositories, each
# carrying its own `.harness/harness.json`, read from that repository's own default
# branch, so a hardcoded date would still export one repository's history as another's
# gate: a project whose plans predate 2026-08-31 would have every one of them silently
# exempted, for a reason belonging to somebody else's git log. `panel_era_start` is
# stamped per project and merged into an existing config additively by
# upgrade-config.py, whose whole contract is "template fills gaps, project values
# win".
#
# RESOLVED ONCE, ABOVE THE LOOP. The first cut assigned the boundary inside the per-plan
# loop, which re-derived it 32 times and would have reported a single config defect once
# per plan. A config defect is one finding.
# A signed plan must carry the adversarial panel record the operator reviewed. The FEAT-45 T-07
# mutation markers wrap this invariant's TABLE ROW below: removing the row unregisters the check,
# which is what the mutant needs; the function itself may stay defined.
def _inv32_signed_plan(ctx, feat):
    """The feature's plan document and its approval block, or (None, None) when there is no
    plan or it is not signed approved — INV-32 grades approved plans only."""
    doc = ctx.plan_docs.get(feat)
    if doc is None:
        return None, None
    approval = doc.get("approval")
    if not isinstance(approval, dict) or str(approval.get("status", "")).strip().lower() != "approved":
        return None, None
    return doc, approval


def _inv32_patch_mission(ctx, feat, doc):
    """The patch-mission exemption: a note (exempt) or a violation (a patch record over a
    larger plan); both empty means the plan is graded."""
    bad, warn = [], []
    fpath = ctx.fpath
    # FEAT-59 SC-02: a `patch` mission runs no pre-build panel by design — its diff is
    # reviewed by the validate run instead (DEC-139 as amended). The mission is read from
    # the sibling feature.json's own key, never inferred from the plan's shape: a one-task
    # plan under `mission: plan` is still graded. Absent or unreadable feature.json, or any
    # mission other than `patch`, exempts nothing. And the exemption rests on the plan
    # BEING one task — that is what makes one validate-run review a sufficient substitute
    # for the panel — so a patch record over a larger plan is graded as the mismatch it is
    # rather than exempted on the strength of a key.
    _mission = str((ctx.record(feat)[0] or {}).get("mission", "")).strip()
    if _mission == "patch":
        _tasks = doc.get("tasks")
        _ntasks = len(_tasks) if isinstance(_tasks, list) else 0
        if _ntasks == 1:
            warn.append(f"INV-32: {feat} is a patch mission, which runs no pre-build panel; "
                        f"its diff is graded by the validate run instead. Not graded.")
            return bad, warn
        bad.append(f"INV-32: {feat} feature.json says mission: patch but its approved plan "
                   f"carries {_ntasks} tasks, not one — a patch is a one-task plan (SC-02), "
                   f"so the panel exemption does not apply. Set the mission to plan "
                   f"(feature-record.py set-mission) and run the panel, or cut the plan to "
                   f"one task.")
    return bad, warn


def _inv32_era_placement(ctx, feat, approval):
    """Where the signature falls against the project's panel era: a violation (unplaceable),
    a note (pre-era, exempt), or both empty (graded). Called ONLY from between the INV-32 ERA
    markers in inv_32 below; the era mutant excises that call, and this function may stay
    defined, as the table-row mutant leaves inv_32 defined."""
    bad, warn = [], []
    _era_start = ctx.era_start
    # The boundary itself is resolved ONCE from `panel_era_start`, above this loop; see
    # the ERA RESOLUTION block for why it is config rather than a literal. `_era_start` is
    # either a YYYY-MM-DD string or None, and None means THIS PROJECT HAS NO PRE-PANEL
    # ERA, so nothing below exempts anything.
    #
    # THE PER-PLAN KEY IS approval.date -- the only durable signature timestamp in the
    # document. Lexicographic comparison on YYYY-MM-DD is chronological, which is why the
    # format is validated rather than parsed.
    signed = str(approval.get("date", "")).strip()
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", signed):
        # AN UNPLACEABLE ERA IS A VIOLATION (panel finding F1, closed at the operator's
        # ruling). This branch WARNED in the first cut of this guard, and that was a
        # fail-open on a fail-closed invariant: an approved plan with no `approval.date`
        # was never graded, the exemption never expired, and nothing else in this file or
        # in harness_yaml requires the key -- INV-3/4/5 check `approval.status` only. So
        # omitting one line bought permanent silence from INV-32.
        #
        # It is safe to fail here because the tree has no undated approval left:
        # FEAT-40-harness-writes-done was the only one, and BUG-1071 backfilled it from
        # the commit that signed it (2938a5c, 2026-08-25) rather than from memory. Fixing
        # the data BEFORE closing the hole is what keeps this from re-reddening the gate.
        #
        # IT FIRES EVEN WHEN _era_start IS None. An undated signature is a record defect
        # in its own right, not merely an obstacle to placing an era, so a project with no
        # pre-panel era still owes the date.
        # The recovery command NAMES THE FILE (cycle-1 ui finding). It printed a literal
        # `<this plan.yaml>` placeholder, which is the one thing an operator cannot paste:
        # a diagnostic whose remedy has to be hand-edited before it runs is a diagnostic
        # that will be retyped wrong. The glob matches the tree's real layout,
        # `.harness/*/features/*/`, so it resolves in a served repository too.
        bad.append(f"INV-32: {feat} is approved but approval.date is missing or "
                   f"malformed ({signed!r}), so its panel era cannot be placed. "
                   f"Add the signature date; recover it with "
                   f"git log -S'status: approved' -- "
                   f".harness/*/features/{feat}/plan.yaml")
        return bad, warn
    if _era_start is not None and signed < _era_start:
        warn.append(f"INV-32: {feat} was signed {signed}, before the adversarial panel "
                    f"became available here ({_era_start}, harness.json "
                    f"panel_era_start); not graded. A plan signed before the panel "
                    f"existed cannot carry a record of it.")
    return bad, warn


def _inv32_panel_presence(feat, panel):
    """The violation for an approved plan with no complete panel result, else empty."""
    bad = []
    if not isinstance(panel, dict) or not str(panel.get("last_run", "")).strip() or not isinstance(panel.get("findings"), list):
        # THE MESSAGE NAMES THE ERA KEY (cycle-1 Q1/Q2). This is the line a migrating
        # legacy project sees, once per historical plan, the first time it upgrades: the
        # template merges `panel_era_start: null`, null means "no pre-panel era", and every
        # plan signed before that project's panel arrived is suddenly graded. The finding
        # is correct and fail-closed, but WITHOUT this sentence its cause is invisible --
        # the operator reads "no panel result recorded" against a plan signed months before
        # the panel existed and has no reason to look at config. Naming the key here is
        # what makes the residual self-diagnosing rather than merely reversible.
        bad.append(f"INV-32: {feat} plan is approved with no complete panel result "
                   f"recorded. If this plan predates the adversarial panel in this "
                   f"project, set harness.json `panel_era_start` to the date the panel "
                   f"became available here instead of recording one.")
    return bad


def _inv32_ruling_complete(ruling):
    """A ruling's finding id, and whether it carries finding, who, a valid date and a reason."""
    fid = str(ruling.get("finding", "")).strip()
    who = str(ruling.get("who", "")).strip()
    date = str(ruling.get("date", "")).strip()
    reason = str(ruling.get("reason", "")).strip()
    complete = bool(fid and who and reason and re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date
    ))
    return fid, complete


def _inv32_ruling(feat, ruling, finding_ids):
    """One risk acceptance: its findings, and the finding id it accepts (None when it
    accepts nothing — malformed, incomplete, or stale)."""
    bad = []
    if not isinstance(ruling, dict):
        bad.append(f"INV-32: {feat} has a malformed approval ruling.")
        return bad, None
    fid, complete = _inv32_ruling_complete(ruling)
    if not complete:
        bad.append(
            f"INV-32: {feat} risk acceptance for {fid or '<missing>'} must carry "
            "finding, who, a valid date, and a non-empty reason."
        )
    accepted = None
    if fid not in finding_ids:
        bad.append(f"INV-32: {feat} STALE RISK ACCEPTANCE {fid or '<missing>'}: a reworded "
                   f"finding gets a NEW content-hash id, so the old acceptance stopped "
                   f"applying and the operator is asked again.")
    elif complete:
        accepted = fid
    return bad, accepted


def _inv32_rulings(feat, approval, findings):
    """The rulings pass: its findings, and the set of finding ids with a complete, current
    risk acceptance."""
    bad = []
    finding_ids = {
        str(item.get("id", "")).strip()
        for item in findings if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    rulings = approval.get("rulings", [])
    if not isinstance(rulings, list):
        bad.append(f"INV-32: {feat} approval.rulings is malformed; expected a list.")
        rulings = []
    accepted_risks = set()
    for ruling in rulings:
        r_bad, accepted = _inv32_ruling(feat, ruling, finding_ids)
        bad.extend(r_bad)
        if accepted is not None:
            accepted_risks.add(accepted)
    return bad, accepted_risks


def _inv32_finding(feat, item, accepted_risks):
    """One panel finding's disposition against the accepted risks: its findings."""
    bad, warn = [], []
    if not isinstance(item, dict):
        bad.append(f"INV-32: {feat} has a malformed panel finding.")
        return bad, warn
    fid = str(item.get("id", "")).strip() or "<missing>"
    severity = str(item.get("severity", "")).strip().lower()
    disposition = str(item.get("disposition", "")).strip().lower()
    if disposition == "resolved":
        warn.append(f"INV-32: {feat} finding {fid} disposition resolved.")
    elif fid in accepted_risks:
        warn.append(f"INV-32: {feat} operator accepted risk for finding {fid}.")
    elif severity not in {"info", "low", "med"}:
        bad.append(f"INV-32: {feat} finding {fid} is {severity or 'unrated'} and remains "
                   "open without operator risk acceptance.")
    return bad, warn


def _inv32_findings(feat, findings, accepted_risks):
    """The findings pass: each finding's disposition against the accepted risks."""
    bad, warn = [], []
    for item in findings:
        f_bad, f_warn = _inv32_finding(feat, item, accepted_risks)
        bad.extend(f_bad)
        warn.extend(f_warn)
    return bad, warn


def _inv32_reader_skipped(feat, reader, item):
    """A skipped reader's record: a note naming persona and reason, or the violation for
    a skip that cannot show why it never ran."""
    bad, warn = [], []
    persona = str(item.get("persona", "")).strip()
    reason = str(item.get("reason", "")).strip()
    if not persona or not reason:
        bad.append(f"INV-32: {feat} reader {reader} was skipped without persona and reason; "
                   f"the record cannot show why it never ran.")
    else:
        warn.append(f"INV-32: {feat} reader {reader} skipped persona {persona}: {reason}")
    return bad, warn


def _inv32_reader(feat, reader, item):
    """One expected reader's record (`item` may be absent): its findings."""
    status = str(item.get("status", "")).strip().lower() if isinstance(item, dict) else ""
    if status not in {"ran", "skipped"}:
        return [f"INV-32: {feat} reader {reader} never ran or was not recorded; an unrecorded "
                f"reader is not a clean reader."], []
    if status == "skipped":
        return _inv32_reader_skipped(feat, reader, item)
    return [], []


def _inv32_readers(feat, panel):
    """The readers pass: every expected reader ran, or was skipped on the record."""
    bad, warn = [], []
    expected_readers = {"should-not-exist", "scope", "goalcheck"}
    readers = panel.get("readers")
    if not isinstance(readers, list):
        readers = []
    by_reader = {
        str(item.get("reader", "")).strip(): item
        for item in readers if isinstance(item, dict) and str(item.get("reader", "")).strip()
    }
    for reader in sorted(expected_readers):
        r_bad, r_warn = _inv32_reader(feat, reader, by_reader.get(reader))
        bad.extend(r_bad)
        warn.extend(r_warn)
    return bad, warn


def _inv32_panel_record(feat, approval, panel):
    """The rulings, findings and readers passes over a complete panel record, in that order."""
    findings = panel.get("findings", [])
    r_bad, accepted_risks = _inv32_rulings(feat, approval, findings)
    f_bad, f_warn = _inv32_findings(feat, findings, accepted_risks)
    rd_bad, rd_warn = _inv32_readers(feat, panel)
    return r_bad + f_bad + rd_bad, f_warn + rd_warn


def inv_32(ctx, feat):
    doc, approval = _inv32_signed_plan(ctx, feat)
    if doc is None:
        return [], []
    bad, warn = _inv32_patch_mission(ctx, feat, doc)
    if bad or warn:
        return bad, warn
# INV-32 ERA BEGIN (BUG-1071)
    bad, warn = _inv32_era_placement(ctx, feat, approval)
    if bad or warn:
        return bad, warn
# INV-32 ERA END (BUG-1071)
    panel = doc.get("panel")
    bad = _inv32_panel_presence(feat, panel)
    if bad:
        return bad, warn
    return _inv32_panel_record(feat, approval, panel)

# --- INV-34 (FEAT-41 T-19): every feature directory carries a plan.yaml, because that is the
# ONLY place a station may be recorded and a feature without one cannot record its own.
#
# OPERATOR-DIRECTED, after this feature proved the hole by falling into it. T-07 deleted
# `status: Review` from BUG-1030 -- plan-less and non-terminal -- and it could not be put back:
# feature.json refuses the key (undeclared, exit 11) and, before T-19, plan.yaml refused to exist
# without tasks. The record was representable NOWHERE. Twelve directories were backfilled with
# station-only plans; this is what stops the thirteenth reintroducing the hole in silence.
#
# A STATION-ONLY PLAN SATISFIES IT. The check is that the record EXISTS, not that it carries
# tasks: a feature that predates the format, or a bug fix opened without a plan, honestly has no
# tasks to record and inventing some to pass a schema would be fabrication.
def inv_34(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    fy = ctx.path(feat, 'feature.json')
    if not os.path.isfile(fy):
        return bad, warn
    _fdir = os.path.dirname(fy)
    if not os.path.isfile(os.path.join(_fdir, "plan.yaml")):
        bad.append(f"INV-34: {os.path.basename(_fdir)} has no plan.yaml, so it has nowhere to "
                   f"record its station — feature.json cannot hold one (the schema declares no "
                   f"`status` key). Create a station-only record: `schema: plan/1`, `feature:`, "
                   f"`status: <station>`, `station_only: true`, `tasks: []`, written through "
                   f"plan-merge.py apply. The marker is REQUIRED and is not inferred from an "
                   f"empty `tasks:` — an emptied plan is not a station-only record.\n"
                   f"    FIRST CHECK WHETHER A REAL PLAN WAS DELETED: `git log --diff-filter=D "
                   f"-- {os.path.join(os.path.relpath(_fdir, root), 'plan.yaml')}`. If this "
                   f"feature HAD tasks, restore that plan instead — a station-only stub would "
                   f"record the station and silently discard the task history.")
    return bad, warn

# --- INV-44 (FEAT-1714 T-03): a REJECTED record has exactly one shape. `rejected` is the
# orchestrator's first-run verdict that the ticket is wrong or superseded — one run, zero
# cycles, one reject judgement, nothing signed, no panel. Each dimension is its own line
# with its own remedy, because a rejection that spent cycles, ran a lead, or sits under a
# signature is not a rejection but an abandoned build wearing the wrong station; and a
# conforming rejected record is exempt from the approval and plan-panel demands ONLY by
# being at this station (INV-32 keys on an approved plan; the approval gate skips terminal
# stations), never by weakening those demands elsewhere.
def _inv44_cycles(_feat44, _doc44):
    """The zero-cycles dimension of the rejected shape."""
    bad = []
    _cu44 = _doc44.get("cycles_used")
    if not (isinstance(_cu44, int) and not isinstance(_cu44, bool) and _cu44 == 0):
        bad.append(f"INV-44 {_feat44}: rejected with cycles_used={_cu44!r} — a rejection is "
                   f"decided at first-run intake before any gate and costs zero cycles; a record "
                   f"that spent cycles was built, not rejected (set the honest station).")
    return bad


def _inv44_runs(_feat44, _doc44):
    """The one-orchestrator-run dimension of the rejected shape."""
    bad = []
    _runs44 = [e for e in (_doc44.get("runs") or []) if isinstance(e, dict)]
    if len(_runs44) != 1:
        bad.append(f"INV-44 {_feat44}: rejected with {len(_runs44)} run(s) recorded — a "
                   f"rejection is ONE orchestrator-owned run; {'none ran' if not _runs44 else 'more than one means a lead was dispatched'}, "
                   f"so either the station or the ledger is wrong.")
    else:
        _agent44 = _runs44[0].get("agent")
        if _agent44 != "harness-orchestrator":
            bad.append(f"INV-44 {_feat44}: the one run is owned by {_agent44!r}, not "
                       f"harness-orchestrator — a rejection dispatches no lead; the orchestrator "
                       f"reads the ticket and returns.")
    return bad


def _inv44_judgement(_feat44, _doc44):
    """The recorded-reject-judgement dimension of the rejected shape."""
    bad = []
    _js44 = [j for j in (_doc44.get("judgements") or []) if isinstance(j, dict)]
    if not any(j.get("kind") == "reject" for j in _js44):
        bad.append(f"INV-44 {_feat44}: rejected with no judgements[] entry of kind reject — an "
                   f"unrecorded rejection is an unrecorded judgement (DEC-230); record it with "
                   f"feature-record.py judgement --kind reject --decision <issue|none>.")
    return bad


def _inv44_plan_approval(_feat44, _pdoc44):
    """The nothing-signed dimension of the rejected shape: plan.yaml's approval."""
    bad = []
    _appr44 = _pdoc44.get("approval") if isinstance(_pdoc44, dict) else None
    if isinstance(_appr44, dict) and str(_appr44.get("status", "")).strip() == "approved":
        bad.append(f"INV-44 {_feat44}: rejected but plan.yaml's approval is approved — a "
                   f"rejection happens BEFORE signature; a signed plan that is then refused is "
                   f"abandoned, not rejected.")
    return bad


def _inv44_brief_approval(_feat44, briefs):
    """The nothing-signed dimension of the rejected shape: BRIEF.md's ## Approval."""
    bad = []
    _brief44 = briefs.get(_feat44)
    if _brief44 and re.search(r"(?m)^status:\s*approved\b", _brief44):
        bad.append(f"INV-44 {_feat44}: rejected but BRIEF.md's ## Approval reads approved — "
                   f"nothing is signed on a rejected feature.")
    return bad


def _inv44_panel(_feat44, _pdoc44):
    """The no-panel dimension of the rejected shape."""
    bad = []
    if "panel" in _pdoc44:
        bad.append(f"INV-44 {_feat44}: rejected but plan.yaml carries a panel mapping — no "
                   f"panel runs on a rejected feature; its presence means the plan phase ran.")
    return bad


def _inv44_dimensions(_feat44, _doc44, _pdoc44, briefs):
    """Every dimension of the one rejected shape, each its own line, in report order."""
    return (_inv44_cycles(_feat44, _doc44)
            + _inv44_runs(_feat44, _doc44)
            + _inv44_judgement(_feat44, _doc44)
            + _inv44_plan_approval(_feat44, _pdoc44)
            + _inv44_brief_approval(_feat44, briefs)
            + _inv44_panel(_feat44, _pdoc44))


def inv_44(ctx, feat):
    bad, warn = [], []
    briefs, plan_docs = ctx.briefs, ctx.plan_docs
    _fd44 = ctx.feature_dir(feat)
    if ctx.station(feat) != 'rejected':
        return bad, warn
    _feat44 = feat
    if ctx.record_error(feat) is not None:
        bad.append(f"INV-44 {_feat44}: station is rejected but feature.json is unreadable, so "
                   f"the rejection's one-run/zero-cycle shape cannot be verified.")
        return bad, warn
    _doc44 = ctx.record(feat)[0] or {}
    _pdoc44 = plan_docs.get(_feat44) or {}
    bad.extend(_inv44_dimensions(_feat44, _doc44, _pdoc44, briefs))
    return bad, warn
