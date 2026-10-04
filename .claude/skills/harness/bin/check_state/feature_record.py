"""feature.json is internally consistent and matches disk: INV-1/2/6/7/8/12/18/22/23/33 and the ledger INV-39/40/43/47. (FEAT-69)"""
import glob, os, re
import harness_boundary
import harness_yaml
from check_state.brief import _FEAT59_KEYS, _brief_is_by_perspective
from check_state.ctx import FINISHED_STATIONS, _int_field, _iso_instant, approved, has_approval_block, read
from check_state.run_state import _inv15_digest_verdict
def inv_1(ctx, feat):
    """INV-1: the feature's goal of record (BRIEF.md) is signed before its flows run."""
    bad, warn = [], []
    fpath = ctx.fpath
    brief = ctx.briefs.get(feat)
    if brief is None or feat in ctx.abandoned:
        return bad, warn
    if not has_approval_block(brief):
        bad.append(f"{fpath(feat, 'BRIEF.md')} has no '## Approval' section — cannot tell if the goal is signed.")
    elif not approved(brief):
        bad.append(f"{fpath(feat, 'BRIEF.md')} is NOT approved — halt that flow and surface to the user.")
    return bad, warn


def inv_2(ctx, feat):
    """INV-2: a flow with a STATE.md has a BRIEF.md — no flow runs with no goal of record."""
    bad, warn = [], []
    if feat in ctx.states and feat not in ctx.briefs:
        bad.append(f"{feat} has STATE.md but no BRIEF.md — a flow is running with no goal of record.")
    return bad, warn


# --- INV-6..8: per-feature execution facts.
def inv_6(ctx, feat):
    """INV-6: reviewers diff a pinned SHA, never a moving HEAD (DEC-50). Also the row that
    reports a feature.json the family cannot read at all."""
    bad, warn = [], []
    doc, runs, code_reviewing_runs, _errors = ctx.record(feat)
    bad.extend(_errors)
    if doc is None:
        return bad, warn
    def val(k):
        v = doc.get(k)
        return None if v is None else str(v)
    # INV-6: reviewers must diff a pinned SHA, never a moving HEAD (DEC-50).
    # A placeholder is not a pin: val() returns str(v), so `review_sha: none` is a
    # truthy string and only an ABSENT key used to trip this (issue #16).
    #
    # The exemption is keyed on the RUN, never on approval.status (BUG-1080). Keying it
    # on a pending approval would turn green at signature and red again for the whole
    # build: the plan-phase runs stay in runs: while review_sha is unpinned until the
    # Building -> Review seam. One exempt run never silences a code-reviewing sibling.
    _sha = (val("review_sha") or "").strip().lower()
    if code_reviewing_runs and (
            _sha == "" or _sha in harness_yaml.PLACEHOLDER_UNSET):
        bad.append(f"{feat}: a validator run reviewed code but review_sha is not pinned "
                   f"— reviewers would diff HEAD (the GAP-7 failure). A run that graded a "
                   f"plan and no code carries `code_grade: n_a` and needs no pin (DEC-207).")
    return bad, warn

def _inv33_plan_path(fy):
    """The plan file beside feature.json: plan.yaml, else the PLAN.md path."""
    _pf = os.path.join(os.path.dirname(fy), "plan.yaml")
    if not os.path.isfile(_pf):
        _pf = os.path.join(os.path.dirname(fy), "PLAN.md")
    return _pf

def _inv33_stale_relpath(ctx, _git_top, _sha, _pf):
    """The plan's path relative to the work tree when its bytes at the pin differ from
    the bytes on disk, else None."""
    # REALPATH BOTH SIDES. `git rev-parse --show-toplevel` returns the resolved
    # path, and on macOS the temp dir every fixture uses is a symlink
    # (/var -> /private/var). Mixing the two makes relpath emit a
    # `../../..`-prefixed path, `git show` fail, and this invariant go SILENT —
    # measured, and the same mismatch T-07 hit in worktree_terminal.
    _prel = os.path.relpath(os.path.realpath(_pf), os.path.realpath(_git_top))
    _shown = ctx.spawn(["git", "-C", ctx.root, "show", f"{_sha}:{_prel}"],
                       capture_output=True)
    try:
        with open(_pf, "rb") as _pfh:
            _disk = _pfh.read()
    except OSError:
        _disk = None
    # BOTH reads must succeed. See the path-absent paragraph above — this one clause is
    # what keeps 19 honest pins quiet.
    if _shown is not None and _shown.returncode == 0 and _disk is not None and _shown.stdout != _disk:
        return _prel
    return None

def _inv33_finding(ctx, feat, _sha, _pf, _prel):
    """The stale-pin finding, naming the last commit to touch the plan."""
    # THE FINDING NAMES THREE THINGS: the feature, the pinned sha, and the last
    # commit to touch that plan. A finding that says only "stale" makes the reader
    # redo the measurement.
    _last = ctx.spawn(
        ["git", "-C", ctx.root, "log", "-1", "--format=%h", "--", _prel],
        capture_output=True, text=True)
    _lastsha = (_last.stdout.strip() if _last is not None else "") or "(unknown)"
    return (f"{feat}: review_sha {_sha} is STALE — {os.path.basename(_pf)} has "
            f"changed since it was pinned, last at {_lastsha}, so the review "
            f"claim covers text that is no longer there (INV-33).")

def _inv33_stale(ctx, _git_top, feat, fy, _sha):
    """The stale-pin finding for the feature's plan file, as a list."""
    bad = []
    _pf = _inv33_plan_path(fy)
    if os.path.isfile(_pf):
        _prel = _inv33_stale_relpath(ctx, _git_top, _sha, _pf)
        if _prel is not None:
            bad.append(_inv33_finding(ctx, feat, _sha, _pf, _prel))
    return bad

def inv_33(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    doc, runs, code_reviewing_runs, _errors = ctx.record(feat)
    if doc is None:
        return bad, warn
    fy = ctx.path(feat, 'feature.json')
    def val(k):
        """A scalar field as a string, or None. JSON returns typed values, so
        consumers that compare textual placeholders normalize them here."""
        v = doc.get(k)
        return None if v is None else str(v)
    _git_top = ctx.git_top
    _sha = (val("review_sha") or "").strip().lower()
    # INV-33: a pin that is STALE, not merely absent (FEAT-41 T-14, closing issue #867).
    #
    # INV-6 above asserts a pin EXISTS. This asserts the pin is CURRENT. An absent pin is
    # honest — it says nobody reviewed this. A stale pin makes a CLAIM, that this text was
    # reviewed at this commit, and once the text has moved that claim is false while looking
    # byte-identical to a true one. Measured live on FEAT-41 itself: feature.json read one sha
    # while plan.yaml had been committed later, and a full run reported no INV-6 line for it.
    #
    # WHY A SEPARATE NUMBER, not a second INV-6 finding. The two have different PRECONDITIONS —
    # INV-6 needs only feature.json, this needs a git work tree and a plan file — and therefore
    # different silences, so folding them together would put two fail-open surfaces behind one
    # grep-able string. Six existing cases assert INV-6's exact text; a distinct number leaves
    # them untouched and makes each invariant separately searchable.
    #
    # A BYTE COMPARISON, NEVER A COMMIT COMPARISON. Comparing the pin to the last commit that
    # touched the plan reports a plan changed and changed back, and reports any feature reviewed
    # before an unrelated commit landed on that path. The bytes are what the pin actually
    # claims. Case (inv32.b) exists to kill the commit-equality implementation.
    #
    # SILENT, DELIBERATELY, ON FIVE STATES, four of which this invariant simply cannot speak to:
    # no git work tree; a pin that does not resolve; no plan file on disk; THE PLAN FILE EXISTS
    # BUT NOT AT THAT PATH IN THE PINNED COMMIT; and a TERMINAL station.
    #
    #   THE PATH-ABSENT SILENCE IS THE LARGEST IN THE TREE. Re-measured at execution time: 19 of
    #   44 feature directories sit in it, from layout history — the docs-layout migration and the
    #   PLAN.md-to-plan.yaml move each changed where a plan lives, and every one of those pins
    #   was honest about the path that existed when it was taken. The ONLY thing silencing it is
    #   the both-reads-succeed clause below, so an implementation that reads an absent object at
    #   the pin as evidence of staleness reds all nineteen at once. All nineteen are also
    #   terminal today, so live exposure is ZERO — which is exactly why case (inv32.d) pins the
    #   clause with a NON-TERMINAL fixture. Nothing in the tree can currently make it fail.
    #
    #   THE TERMINAL SCOPE IS LOAD-BEARING FOR FOUR SHIPPED FEATURES (operator answer Q6): a
    #   shipped plan is a record rather than a contract, and shipped history stays unrepaired.
    #   Without it this goes red on four of them the moment it lands.
    #
    # A VALIDATOR RUN IS NOT ONE OF THE SILENCES. That precondition was dropped deliberately: a
    # recorded run is a LAGGING indicator that can only fire after a panel has already read the
    # wrong text, which is how this feature's own divergence survived.
    if _git_top and _sha and _sha not in harness_yaml.PLACEHOLDER_UNSET \
            and ctx.station(feat) not in FINISHED_STATIONS:
        bad.extend(_inv33_stale(ctx, _git_top, feat, fy, _sha))
    return bad, warn

def inv_7(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    doc, runs, code_reviewing_runs, _errors = ctx.record(feat)
    if doc is None:
        return bad, warn
    fy = ctx.path(feat, 'feature.json')
    def val(k):
        """A scalar field as a string, or None. JSON returns typed values, so
        consumers that compare textual placeholders normalize them here."""
        v = doc.get(k)
        return None if v is None else str(v)

    # INV-7: the fix-loop bound must actually count the failures it bounds.
    fails = sum(1 for _, _, v in runs if v.upper() == "FAIL")
    cu = val("cycles_used")
    if cu is not None and cu.isdigit() and int(cu) < fails:
        bad.append(f"{feat}: cycles_used={cu} but {fails} FAIL run(s) recorded "
                   f"— the fix loop is no longer bounded.")
    return bad, warn

# A BUDGET THIS INVARIANT CANNOT RESOLVE IS REPORTED, NEVER SILENTLY DROPPED.
# First cut read the key and fell through on anything unexpected, so a harness.json
# that PARSES FINE but has no `budgets.max_total_runs` disabled INV-22 with no
# diagnostic — and a shipped template example once omitted the budgets block in exactly
# that shape, so a project onboarded from it got a check that never ran. DEC-160
# records the identical config lag for max_total_cycles. Worse, `true` satisfied
# isinstance(x, int) — bool subclasses int in Python — so it "worked" while "20"
# and 20.0 did not.
def _inv22_int_budget(v):
    """An int budget: non-negative, or None with a reason."""
    return (v, None) if v >= 0 else (None, f"{v} is negative")

def _inv22_float_budget(v):
    """A float budget: a non-negative whole number, or None with a reason."""
    return (int(v), None) if v.is_integer() and v >= 0 else (None, f"{v!r} is not a whole number")

def _inv22_as_budget(v):
    """int, or None with a reason. bool is rejected BEFORE the int check."""
    if isinstance(v, bool):
        return None, f"{v!r} is a boolean"
    if isinstance(v, int):
        return _inv22_int_budget(v)
    if isinstance(v, float):
        return _inv22_float_budget(v)
    if isinstance(v, str) and v.strip().isdigit():
        return int(v.strip()), None
    return None, ("absent" if v is None else f"{v!r} is not a number")

def _inv22_default_budget(ctx):
    """harness.json's budgets.max_total_runs as (int, None), or (None, why)."""
    if not ctx.cj_valid:
        return None, "harness.json could not be read"
    return _inv22_as_budget((ctx.cj.get("budgets") or {}).get("max_total_runs"))

def _inv22_budget(ctx, feat, val, warn):
    """The run budget in force — the feature's own outranking the harness.json default —
    as (int, None), or (None, why). An unusable per-feature value is noted in `warn`."""
    _budget, _why = _inv22_default_budget(ctx)
    _declared = val("max_total_runs")
    if _declared is not None:                 # a per-feature value outranks the default
        _d, _dwhy = _inv22_as_budget(_declared.strip() if isinstance(_declared, str) else _declared)
        if _d is None:
            warn.append(f"INV-22 {feat}: its own max_total_runs is unusable ({_dwhy}) — "
                        f"falling back to the harness.json default.")
        else:
            _budget, _why = _d, None
    return _budget, _why

def _inv22_count(feat, runs, val, _budget, _why):
    """The note on the run count against the budget, as a list."""
    warn = []
    if _budget is None:
        warn.append(f"INV-22 {feat}: run counting is INACTIVE — budgets.max_total_runs "
                    f"{_why}. {len(runs)} runs recorded and nothing is watching them. "
                    f"Set it in .harness/harness.json (default 20).")
    elif len(runs) > _budget:
        warn.append(f"INV-22 {feat}: {len(runs)} runs recorded against a {_budget}-run budget "
                    f"(cycles_used={val('cycles_used')} counts REWORK only, DEC-157, so it "
                    f"does not see this). Not a defect by itself — check each run is "
                    f"efficient, is resolving issues, and is advancing the SCs. The count "
                    f"is a FLOOR: main-session-direct segments are not runs.")
    return warn

def inv_22(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    doc, runs, code_reviewing_runs, _errors = ctx.record(feat)
    if doc is None:
        return bad, warn
    fy = ctx.path(feat, 'feature.json')
    def val(k):
        """A scalar field as a string, or None. JSON returns typed values, so
        consumers that compare textual placeholders normalize them here."""
        v = doc.get(k)
        return None if v is None else str(v)

    # INV-22: RUNS are counted, because cycles do not count them (issue #79).
    # DEC-157 makes a cycle REWORK ONLY, so a first-pass run contributes zero however
    # many steps it has. That is right for what the cycle budget guards, and it left
    # total runs unbounded AND uncounted: FEAT-03 ran 19 times against a 6-cycle count
    # and tripped nothing. Cost was the other long-feature signal and DEC-178 deleted
    # it, so without this nothing at all notices a feature running long.
    #
    # DELIBERATELY A NOTE, NOT A VIOLATION. A high run count is not itself a defect —
    # a long feature is fine when each run is efficient, resolves issues and advances
    # the SCs. A third HARD budget that stops work needs a much stronger case than one
    # that flags, so this one flags and names those three questions.
    #
    # THE COUNT IS A FLOOR, not a total: a main-session-direct segment is not a run and
    # never appears in runs: — on FEAT-07 that hid eight of ten tasks. Said in the
    # message so nobody reads the number as complete. (#1895: since FEAT-64 the main
    # session MAY record its direct segment as a run with `--agent main-session`; a recorded
    # one is counted like any other, an unrecorded one still is not — the floor stands.)
    _budget, _why = _inv22_budget(ctx, feat, val, warn)
    warn.extend(_inv22_count(feat, runs, val, _budget, _why))
    return bad, warn

def inv_8(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    doc, runs, code_reviewing_runs, _errors = ctx.record(feat)
    if doc is None:
        return bad, warn
    fy = ctx.path(feat, 'feature.json')
    def val(k):
        """A scalar field as a string, or None. JSON returns typed values, so
        consumers that compare textual placeholders normalize them here."""
        v = doc.get(k)
        return None if v is None else str(v)

    # INV-8: a referenced run dir must exist, or resume has nothing to read.
    recorded = set()
    for rid, _, _ in runs:
        recorded.add(rid)
        d = os.path.join(os.path.dirname(fy), "runs", rid)
        if not os.path.isdir(d):
            warn.append(f"{feat}: run {rid} is referenced but its dir is absent "
                        f"(pruned, or never created).")
    return bad, warn

def inv_12(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    doc, runs, code_reviewing_runs, _errors = ctx.record(feat)
    if doc is None:
        return bad, warn
    fy = ctx.path(feat, 'feature.json')
    def val(k):
        """A scalar field as a string, or None. JSON returns typed values, so
        consumers that compare textual placeholders normalize them here."""
        v = doc.get(k)
        return None if v is None else str(v)
    recorded = {rid for rid, _, _ in runs}
    # INV-12: the INVERSE — a run dir nothing records. Observed live (DEC-131): an
    # interrupt killed the orchestrator's view while its orphaned subtree ran on and
    # wrote a whole run. Work on disk that no orchestrator knows about is invisible
    # to resume unless something surfaces it.
    for d in glob.glob(os.path.join(os.path.dirname(fy), "runs", "*")):
        rid = os.path.basename(d)
        if os.path.isdir(d) and rid not in recorded:
            warn.append(f"{feat}: run dir {rid} exists on disk but feature.json does not "
                        f"record it — orphaned work (interrupted flow?). A resume must "
                        f"reconcile it, not rediscover it by luck.")
    return bad, warn

# --- INV-18 (DEC-160): a feature with run dirs but no feature.json is invisible to
# every feature-keyed invariant (INV-8/12/17) — a whole phase can run unchecked.
# Observed live: FEAT-03's plan phase ran to completion before feature.json existed.
def inv_18(ctx, feat):
    bad, warn = [], []
    rd = ctx.path(feat, 'runs')
    fdir = ctx.feature_dir(feat)
    # isdir FIRST: glob matches a plain file named `runs` too, and os.listdir on it raises
    # NotADirectoryError — exit 1, empty stdout, every later invariant skipped.
    if os.path.isdir(rd) and os.listdir(rd) and not os.path.isfile(os.path.join(fdir, "feature.json")):
        bad.append(f"{os.path.basename(fdir)}: has runs/ but no feature.json — the feature is "
                   f"invisible to run reconciliation and phase checks; instantiate it from "
                   f".agents/skills/harness/templates/feature.json (the playbook's first-cycle "
                   f"duty).")
    return bad, warn

# --- INV-23 (DEC-150, mechanized — issue #132): the feature.json and STATE.md budgets,
# swept from DISK. check-domain.py enforces the same numbers on a WRITE payload, which is
# where they can still be prevented; this reads the file as it actually is, so no tool and
# no author identity can route around it.
#
# WARN, not bad, and the reason is measured rather than tidy: run against this tree the
# day it landed, it found FEAT-05/STATE.md at 165 lines against a 120 budget and five
# illegal sections, and FEAT-02/STATE.md with five more — both predating the gate. Making
# them halt /harness entry would convert a reporting backstop into an unrelated cleanup
# that has to land first. The write-time gate is the one with teeth; this one's job is
# that the drift reaches a human.
#
# VOCABULARY stays in sync with check-domain.py; the MECHANISM deliberately does not
# (D-02) — that one measures a payload, this one measures a file.
def _inv23_feature_json(ctx, feat):
    """The finding for one feature's feature.json over its line budget, if any. A feature
    with no feature.json contributes nothing."""
    fpath = ctx.fpath
    fy = ctx.path(feat, 'feature.json')
    if not os.path.isfile(fy):
        return []
    _ftext = read(fy) or ""
    # 300, not 200: FEAT-10 measures 173 lines with 32 runs, roughly 5 lines per run.
    #
    # THE COUNT EXCLUDES `runs:` (FEAT-54 backlog B-4), through the SAME helper the
    # write-time gate uses — the vocabulary sync this block's header promises now covers the
    # definition of a counted line, not only the wording of the message.
    # An unimportable feature_schema is CANNOT RUN (FEAT-63 T-02, ruled 2026-09-21). It used to
    # fall back to grading the whole file against a hard-coded 300 — a budget nobody
    # maintained, applied silently, which is the fail-open shape this wave removes.
    try:
        _fs_inv23 = harness_boundary.load_repo_module("feature_schema")
    except harness_boundary.RepoModuleError as _fse:
        return [f"INV-23 CANNOT RUN for {fpath(feat, 'feature.json')}: feature_schema.py did not "
                f"import ({type(_fse.cause).__name__}: {_fse.cause}), so its line budget cannot be "
                f"graded. The module ships with this repository."]
    _inv23_budget = _fs_inv23.FEATURE_JSON_LINE_BUDGET
    _inv23_count = _fs_inv23.journal_lines(_ftext)
    _inv23_basis = "excluding the runs ledger"
    if _inv23_count > _inv23_budget:
        return [f"INV-23 {fpath(feat, 'feature.json')} is {_inv23_count} lines "
                f"({_inv23_basis}) — budget is {_inv23_budget}. It is "
                f"data a script parses, not a journal (DEC-150)."]
    return []


def _inv23_claude_md(root):
    """The finding for a CLAUDE.md over its line budget, if any."""
    # CLAUDE.md (issue #139), swept from disk like its peers. The write-time gate in
    # check-domain.py is the one with teeth; this is the backstop for a session where the
    # PostToolUse half was never registered, exactly as for the four state files below.
    _cm = os.path.join(root, "CLAUDE.md")
    _cml = (read(_cm) or "").splitlines()
    if _cml and len(_cml) > 80:
        return [f"INV-23 CLAUDE.md is {len(_cml)} lines — budget is 80 (DEC-181). It is "
                f"preloaded into EVERY session, so a line here costs more than a line "
                f"anywhere else; rationale belongs in .harness/harness/docs/DECISIONS.md."]
    return []


def _inv23_state_md(ctx, feat):
    """The findings for one feature's STATE.md — over its line budget, and carrying sections
    other than the two it may hold. A feature with no STATE.md contributes nothing."""
    warn = []
    fpath = ctx.fpath
    sm = ctx.path(feat, 'STATE.md')
    if not os.path.isfile(sm):
        return warn
    sl = (read(sm) or "").splitlines()
    if len(sl) > 120:
        warn.append(f"INV-23 {fpath(feat, 'STATE.md')} is {len(sl)} lines — budget is 120. It holds no "
                    f"history: ## Current is replaced, never appended (DEC-150).")
    illegal = [l.strip() for l in sl
               if l.startswith("## ") and l.strip() not in ("## Current", "## Open Questions")]
    if illegal:
        warn.append(f"INV-23 {fpath(feat, 'STATE.md')} has illegal section(s) {illegal} — STATE.md is "
                    f"`## Current` + `## Open Questions` and nothing else (SPEC §2).")
    return warn


def inv_23(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    for feat in ctx.features:
        warn.extend(_inv23_feature_json(ctx, feat))
    warn.extend(_inv23_claude_md(root))
    for feat in ctx.features:
        warn.extend(_inv23_state_md(ctx, feat))
    return bad, warn

# INV-47 (#1884): a validate run recorded PASS is graded against the member notes of ITS
# cycle. FEAT-63's c2 was recorded PASS while notes/review-harness-qa-c2.md said BLOCKED —
# the integration runner's exit 1 was real and CI caught it after the PASS. issue #919's
# re-run fires only on a qa PASS, and INV-46 compares the run's digest with feature.json;
# nothing compared the lead's verdict with what its members returned. The note IS the
# member's record (overwritten per cycle), so a FAIL or BLOCKED there under a PASS run means
# the lead passed over a member it did not get to re-return. Cycle mapping is the run id's
# own: `validate-validator` is c0, `validate-cN-validator` is cN; `-plan-cN` notes belong to
# plan runs and are not members of a validate run.
_VALIDATE_RUN_RE = re.compile(r"^validate(?:-c(\d+))?-validator$")
# The lookahead keeps `-plan-cN` names out: plan-review notes are not members of a validate run.
_MEMBER_NOTE_RE = re.compile(r"^review-harness-(?!.*-plan-c)[a-z-]+-c(\d+)\.md$")


def _note_cycle(name):
    """The cycle a member review note belongs to, or None for a non-member name."""
    _nm = _MEMBER_NOTE_RE.match(name)
    return int(_nm.group(1)) if _nm else None


def _note_verdict(path):
    """The note's tail VERDICT, upper-cased, or None when it carries none."""
    _vm = _inv15_digest_verdict(read(path) or "")
    return _vm.group(1).strip().upper() if _vm else None


def _inv47_member_notes(ctx, feat, cycle):
    """(name, verdict) for every member review note of `cycle`."""
    _paths = sorted(glob.glob(os.path.join(ctx.feature_dir(feat), "notes", "review-harness-*.md")))
    return [(os.path.basename(_np), _note_verdict(_np)) for _np in _paths
            if _note_cycle(os.path.basename(_np)) == cycle]


def _passed_validate_cycle(_entry):
    """(run id, cycle) when `_entry` is a validate run at PASS, else None."""
    if not isinstance(_entry, dict):
        return None
    _rid = str(_entry.get("id", "")).strip()
    _rm = _VALIDATE_RUN_RE.match(_rid)
    if not _rm or str(_entry.get("verdict", "")).strip().upper() != "PASS":
        return None
    return _rid, int(_rm.group(1) or 0)


def _passed_validate_cycles(_doc):
    """(run id, cycle) for every validate run the record has at PASS."""
    _found = (_passed_validate_cycle(_entry) for _entry in (_doc.get("runs") or []))
    return [_hit for _hit in _found if _hit is not None]


def _inv47_hit(_rid, _name, _verdict):
    return ("INV-47", f"run {_rid} PASS over notes/{_name} {_verdict}",
            f"run {_rid} is recorded PASS but its member note notes/{_name} says VERDICT: "
            f"{_verdict} — a lead does not pass over a member's {_verdict}; the member "
            f"returns again, or the run is FAIL (#1884)")


def inv_47(ctx, feat):
    _doc, _era = _feat59_record(ctx, feat)
    if _doc is None:
        return [], [], []
    _hits = [_inv47_hit(_rid, _name, _verdict)
             for _rid, _cycle in _passed_validate_cycles(_doc)
             for _name, _verdict in _inv47_member_notes(ctx, feat, _cycle)
             if _verdict in ("FAIL", "BLOCKED")]
    return [], [], _hits


# INV-39 (SC-15, DEC-157): the cycle budget is a bound, and a raise is a recorded decision.
#
# TODAY NOTHING ENFORCES `cycles_used <= max_total_cycles`. INV-7 bounds cycles_used from
# BELOW (it must count the FAIL runs) and INV-22 counts runs against a budget that is
# informational by design; no invariant reads max_total_cycles at all. FEAT-43 raised it
# seven times and "it always followed cycles_used, never led" (the FEAT-59 brief) -- a
# ceiling that moves whenever it is reached is not a ceiling. DEC-157 made a raise a recorded
# user decision in prose; `budget_decisions[]` (C1) is where the record now lives, written by
# feature-record.py raise-cycles, and a raise with no entry recording the CURRENT value is
# the unrecorded decision this refuses. An entry recording an earlier value covers only that
# raise; the current one is still undecided.
#
# INV-40 (SC-21, SC-20): every autonomous judgement leaves a judgements[] entry. Four
# INDEPENDENT checks, each on its own trigger, so one record can fail all four and each line
# names its own remedy: (a) a `mission` whose LAST entry of kind mission is absent or decided
# a different value -- set-mission ran without the ledger hearing of it; (b) a run with verdict
# FAIL that a later run follows -- a re-gate happened -- with no entry of kind regate; (c) a
# handoff note with at least one run recorded after its `seq-N` -- a successor woke -- with no
# entry of kind succession; (d) BUG-1716: a task whose current {files, intent, verify} hash
# differs from the hash `sign-approval` recorded in `signed_task_hashes` -- the signed text
# changed -- with no entry of kind amendment whose decision is that task's `T-NN.<field>`.
# Entries are appended in order and the ledger is one flat list, so (b) and (c) match by
# COUNT: k re-gates need k regate entries and the first uncovered run or note is the one
# named. `seq-N` is the note's own first-line marker (templates/HANDOFF.md), read as the
# ordinal of the run that wrote it; run N+1 onward is the successor's. An in-era note with no
# marker is refused rather than skipped, because a note that cannot be placed cannot be
# matched -- the same posture INV-32 takes on an undated approval. (d) recomputes with the
# hash plan-merge.py owns (`signed_task_hash`), never a re-spelling of it; an overruled
# amendment still covers -- the ledger is the historical record whatever the operator ruled;
# a record with no `signed_task_hashes` (signed before BUG-1716) and a pending approval are
# not graded; malformed hash data is the schema gate's finding, not this one's.
#
# INV-43 (BUG-1723 SC-03, D-02): the succession judgement for a handoff at seq-N is recorded
# NO LATER than run N+1 started. INV-40(c) asks whether it exists; this asks WHEN. A
# succession whose `at` postdates the successor's first run is a retrospective correction --
# the shape #1713 measured twice on BUG-285-canonical-reader, where one context ran plan,
# build and validate and wrote "seam correction" judgements after the fact. Matching is
# INV-40's own: the k-th qualifying handoff (by seq) takes the k-th succession entry (by
# ledger order). A timestamp that is present but unreadable is CANNOT VERIFY naming the
# field, never a silent pass; a missing succession is INV-40's finding and is not repeated.
# Chronology is compared on ISO-8601 instants, so `Z` and `+00:00` agree.
def _signed_hashes_to_grade(ctx, doc, plan_doc):
    """The signed_task_hashes mapping when INV-40 (d) applies, else None: the hash module
    imported, the record carries hashes, and the plan's approval is `approved`."""
    signed = doc.get("signed_task_hashes")
    approval = plan_doc.get("approval") if isinstance(plan_doc, dict) else None
    approved = isinstance(approval, dict) and str(approval.get("status", "")).strip() == "approved"
    if ctx.signed_task_hash is None or not isinstance(signed, dict) or not approved:
        return None
    return signed


def _amended_task_ids(doc):
    """Every task id an amendment judgement names, overruled or not."""
    return {str(e.get("decision", "")).split(".", 1)[0]
            for e in (doc.get("judgements") or [])
            if isinstance(e, dict) and str(e.get("kind", "")).strip() == "amendment"}


def _unledgered_edit_hit(tid, current, signed):
    return ("INV-40", f"{tid}'s signed text changed with no amendment judgement",
            f"{tid}'s intent/files/verify hash to {current[:12]}… but were signed as "
            f"{str(signed)[:12]}…, and judgements[] carries no entry of kind amendment for "
            f"{tid} — the signed text was edited outside the ledger (SC-21, DEC-229); record "
            f"it with plan-merge.py record-amendments --file plan.yaml --digest "
            f"<engineering-lead digest>, or restore the signed text")


def _unledgered_task_edits(ctx, doc, plan_doc):
    """INV-40 (d): one (short, full) hit per task whose current hash differs from its signed
    hash with no amendment judgement naming that task."""
    signed = _signed_hashes_to_grade(ctx, doc, plan_doc)
    if signed is None:
        return []
    graded = {str(t.get("id", "")): t for t in (plan_doc.get("tasks") or [])
              if isinstance(t, dict)}
    unledgered = set(signed) & set(graded) - _amended_task_ids(doc)
    changed = [(tid, ctx.signed_task_hash(graded[tid])) for tid in sorted(unledgered)]
    return [_unledgered_edit_hit(tid, current, signed[tid])
            for tid, current in changed if current != signed[tid]]



def _feat59_record(ctx, feat):
    """(doc, era) for the FEAT-59 family, or (None, None) when the record is absent or
    unreadable -- INV-6..8 already reports an unparseable feature.json; restating it is noise."""
    _doc59 = ctx.record(feat)[0]
    if _doc59 is None:
        return None, None
    if not isinstance(_doc59, dict):
        return None, None
    _era59 = (any(k in _doc59 for k in _FEAT59_KEYS)
              or _brief_is_by_perspective(ctx.briefs.get(feat)))
    return _doc59, _era59


def _inv39_bound_hit(_doc59, _cu59, _mtc59, _default_cycles):
    """The (a) hit -- cycles_used above the record's bound -- or None."""
    # The schema lets a record OMIT max_total_cycles to inherit harness.json's default, so
    # the BOUND is the explicit key when present and the default otherwise; a feature that
    # inherits its ceiling still has one. The raise check below stays on the explicit key —
    # an inherited value cannot have been raised.
    if "max_total_cycles" in _doc59:
        _bound59, _bound_src = _mtc59, "max_total_cycles"
    else:
        _bound59, _bound_src = _default_cycles, "the inherited harness.json default max_total_cycles"
    # Each hit is (invariant, short form, full form): the full form is the violation an in-era
    # record gets, the short form is what a pre-era record's single note lists. Measured at
    # this commit, all 69 legacy feature.json files trip (b) or (c) below -- one line each
    # with the full text would be the wall INV-32 taught this file not to build.
    if _cu59 is not None and _bound59 is not None and _cu59 > _bound59:
        return ("INV-39", f"cycles_used {_cu59} > {_bound_src} {_bound59}",
                f"cycles_used={_cu59} exceeds {_bound_src}={_bound59} — the rework "
                f"budget is spent; raise it through feature-record.py raise-cycles, which "
                f"records the decision (DEC-157), or stop (SC-15)")
    return None


def _inv39_recorded_raises(_doc59):
    """The max_total_cycles values the record's budget_decisions entries carry."""
    _decs59 = _doc59.get("budget_decisions")
    return ({_int_field(d.get("max_total_cycles")) for d in _decs59 if isinstance(d, dict)}
            if isinstance(_decs59, list) else set())


def _inv39_raise_check(_feat59, _doc59, _era59, _mtc59, _default_cycles):
    """The (b) raise check on the explicit max_total_cycles: the hit when it is raised above
    the default with no budget_decisions entry, the in-era warn when the default is unreadable,
    or neither -- as (hits, warn)."""
    _hits59, warn = [], []
    if _mtc59 is None:
        return _hits59, warn
    if _default_cycles is None:
        if _era59:
            warn.append(f"INV-39 {_feat59}: the raise check is INACTIVE — harness.json "
                        f"budgets.max_total_cycles is absent or not a whole number, so "
                        f"max_total_cycles={_mtc59} cannot be compared with the default.")
    elif _mtc59 > _default_cycles:
        if _mtc59 not in _inv39_recorded_raises(_doc59):
            _hits59.append(("INV-39",
                            f"max_total_cycles {_mtc59} raised above the default "
                            f"{_default_cycles} with no budget_decisions entry",
                            f"max_total_cycles={_mtc59} is above the harness.json default "
                            f"{_default_cycles} and no budget_decisions entry records "
                            f"max_total_cycles: {_mtc59} — a raise is a recorded user decision "
                            f"(DEC-157); write it with feature-record.py raise-cycles --to "
                            f"{_mtc59} --decision <path> (SC-15)"))
    return _hits59, warn


def inv_39(ctx, feat):
    bad, warn, _hits59 = [], [], []
    _feat59 = feat
    _default_cycles = ctx.default_cycles
    _doc59, _era59 = _feat59_record(ctx, feat)
    if _doc59 is None:
        return bad, warn, _hits59
    _cu59 = _int_field(_doc59.get("cycles_used"))
    _mtc59 = _int_field(_doc59.get("max_total_cycles"))
    _bound_hit = _inv39_bound_hit(_doc59, _cu59, _mtc59, _default_cycles)
    if _bound_hit is not None:
        _hits59.append(_bound_hit)
    _raise_hits, _raise_warn = _inv39_raise_check(_feat59, _doc59, _era59, _mtc59, _default_cycles)
    _hits59.extend(_raise_hits)
    warn.extend(_raise_warn)
    return bad, warn, _hits59


def _inv40_judgements(_feat59, _doc59, _era59):
    """The judgements list INV-40 reads and the kind of each of its entries; an unreadable
    ledger is the in-era violation and reads as empty."""
    bad = []
    _j59 = _doc59.get("judgements")
    if _j59 is None:
        _j59 = []
    if not isinstance(_j59, list):
        if _era59:
            bad.append(f"INV-40 {_feat59}: judgements is {type(_j59).__name__}, not a list — the "
                       f"ledger cannot be read, so no judgement can be matched.")
        _j59 = []
    _kinds59 = [str(e.get("kind", "")).strip() for e in _j59 if isinstance(e, dict)]
    return bad, _j59, _kinds59


def _inv40_mission(_doc59, _j59):
    """(a) the mission key against the ledger's last judgement of kind mission."""
    _hits59 = []
    if "mission" not in _doc59:
        return _hits59
    # (a) is a MATCH, not a presence check: set-mission may run twice (the SC-03 downgrade
    # is exactly that), and a second write with no new judgement leaves the ledger's last
    # word on the mission disagreeing with the key. The last entry of kind mission is the
    # ledger's current ruling; anything else is an unrecorded change.
    _mission59 = str(_doc59.get("mission")).strip()
    _mj59 = [e for e in _j59 if isinstance(e, dict) and str(e.get("kind", "")).strip() == "mission"]
    if not _mj59:
        _hits59.append(("INV-40", f"no mission judgement for mission '{_mission59}'",
                        f"mission '{_mission59}' is recorded but judgements[] carries "
                        f"no entry of kind mission — the mission choice is an unrecorded "
                        f"judgement (SC-21)"))
    else:
        _last59 = str(_mj59[-1].get("decision", "")).strip()
        if _last59 != _mission59:
            _hits59.append(("INV-40",
                            f"mission '{_mission59}' but the last mission judgement decided "
                            f"'{_last59}'",
                            f"mission is '{_mission59}' but the last judgements[] entry of kind "
                            f"mission decided '{_last59}' — the mission was changed with no "
                            f"judgement recording the change (SC-21); record it with "
                            f"feature-record.py set-mission --by <persona> --reason <why>"))
    return _hits59


def _inv40_regates(_kinds59, _runs59):
    """(b) one regate judgement per FAIL run that a later run follows."""
    _hits59 = []
    _regates59 = _kinds59.count("regate")
    _need_regate = [str(e.get("id", "")).strip() for e in _runs59[:-1]
                    if str(e.get("verdict", "")).strip().upper() == "FAIL"]
    if len(_need_regate) > _regates59:
        _hits59.append(("INV-40", f"no regate judgement for FAIL run {_need_regate[_regates59]}",
                        f"run {_need_regate[_regates59]} has verdict FAIL and a later run follows "
                        f"it, but judgements[] carries no matching entry of kind regate "
                        f"({_regates59} recorded for {len(_need_regate)} re-gate(s)) — the "
                        f"re-gate decision is unrecorded (SC-21)"))
    return _hits59


def _inv40_handoff_need(_feat59, _hp59, _runs59, _era59):
    """One handoff note's (seq, note, runs-after) entry for (c), or None when no run
    follows it; a note with no `seq-N` is the in-era violation and is never counted."""
    bad = []
    _first59 = ((read(_hp59) or "").splitlines() or [""])[0]
    _sm59 = re.search(r"\bseq-(\d+)\b", _first59)
    if _sm59 is None:
        if _era59:
            bad.append(f"INV-40 {_feat59}: notes/{os.path.basename(_hp59)} carries no `seq-N` "
                       f"on its first line, so the runs after it cannot be counted and no "
                       f"succession can be matched to it — add it (templates/HANDOFF.md).")
        return bad, None
    _after59 = len(_runs59) - int(_sm59.group(1))
    if _after59 > 0:
        return bad, (int(_sm59.group(1)), os.path.basename(_hp59), _after59)
    return bad, None


def _inv40_successions(ctx, feat, _era59, _kinds59, _runs59):
    """(c) one succession judgement per handoff note a later run follows, in seq order."""
    bad, _hits59 = [], []
    _fy59 = ctx.path(feat, "feature.json")
    _succ59 = _kinds59.count("succession")
    _need_succ = []
    for _hp59 in glob.glob(os.path.join(os.path.dirname(_fy59), "notes", "handoff-*.md")):
        _bad59, _need59 = _inv40_handoff_need(feat, _hp59, _runs59, _era59)
        bad.extend(_bad59)
        if _need59 is not None:
            _need_succ.append(_need59)
    _need_succ.sort()
    if len(_need_succ) > _succ59:
        _seq, _note, _after = _need_succ[_succ59]
        _hits59.append(("INV-40",
                        f"no succession judgement for notes/{_note} (seq-{_seq}, {_after} "
                        f"run(s) after it)",
                        f"notes/{_note} was written at seq-{_seq} and {_after} run(s) are recorded "
                        f"after it, but judgements[] carries no matching entry of kind succession "
                        f"({_succ59} recorded for {len(_need_succ)} handoff(s) with a successor "
                        f"run) — the successor's continue/downgrade/stop decision is unrecorded "
                        f"(SC-20/SC-21)"))
    return bad, _hits59


def inv_40(ctx, feat):
    bad, warn, _hits59 = [], [], []
    _doc59, _era59 = _feat59_record(ctx, feat)
    if _doc59 is None:
        return bad, warn, _hits59
    bad, _j59, _kinds59 = _inv40_judgements(feat, _doc59, _era59)
    _runs59 = [e for e in (_doc59.get("runs") or []) if isinstance(e, dict)]
    _hits59.extend(_inv40_mission(_doc59, _j59))
    _hits59.extend(_unledgered_task_edits(ctx, _doc59, ctx.plan_docs.get(feat) or {}))
    _hits59.extend(_inv40_regates(_kinds59, _runs59))
    _sbad59, _shits59 = _inv40_successions(ctx, feat, _era59, _kinds59, _runs59)
    return bad + _sbad59, warn, _hits59 + _shits59


def _feat59_note_seq(_hp59):
    """The seq-N a handoff note's first line names, or None when it names none."""
    _first59 = ((read(_hp59) or "").splitlines() or [""])[0]
    _sm59 = re.search(r"\bseq-(\d+)\b", _first59)
    return None if _sm59 is None else int(_sm59.group(1))


def _feat59_succession_entries(_doc59):
    """The succession entries the ledger carries; an unreadable ledger carries none."""
    _j59 = _doc59.get("judgements")
    _j59 = _j59 if isinstance(_j59, list) else []
    return [e for e in _j59 if isinstance(e, dict)
            and str(e.get("kind", "")).strip() == "succession"]


def _feat59_successions(ctx, feat, _doc59, _era59):
    """The (seq, note, runs-after) handoffs INV-40 (c) counts, in seq order, and the
    succession entries the ledger carries -- shared by INV-40 and INV-43."""
    _runs59 = [e for e in (_doc59.get("runs") or []) if isinstance(e, dict)]
    _need_succ = []
    for _hp59 in glob.glob(os.path.join(ctx.feature_dir(feat), "notes", "handoff-*.md")):
        _seq59 = _feat59_note_seq(_hp59)
        if _seq59 is None:
            continue
        _after59 = len(_runs59) - _seq59
        if _after59 > 0:
            _need_succ.append((_seq59, os.path.basename(_hp59), _after59))
    _need_succ.sort()
    return _runs59, _need_succ, _feat59_succession_entries(_doc59)


def _inv43_run(_runs59, _seq43):
    """The run at seq -- the first run after the note -- or an empty record when the ledger
    has no readable run there."""
    return _runs59[_seq43] if _seq43 < len(_runs59) and isinstance(_runs59[_seq43], dict) else {}


def _inv43_placement(_feat59, _seam_era_start, _seq43, _note43, _run43, _entry43):
    """One succession's placement against the first run after its note: the two CANNOT
    VERIFY hits, the retrospective hit, or that hit's pre-era warn -- as (hits, warn)."""
    _hits59, warn = [], []
    _rid43 = _run43.get("id", f"runs[{_seq43}]")
    _at43 = _iso_instant(_entry43.get("at"))
    _st43 = _iso_instant(_run43.get("started_at"))
    if _at43 is None:
        _hits59.append(("INV-43", f"succession for notes/{_note43}: `at` unreadable",
                        f"CANNOT VERIFY the seam for notes/{_note43}: the matching succession "
                        f"judgement's `at` ({_entry43.get('at')!r}) is not an "
                        f"ISO-8601 instant, so it cannot be placed against run {_rid43}"))
        return _hits59, warn
    if _st43 is None:
        _hits59.append(("INV-43", f"run {_rid43}: started_at unreadable",
                        f"CANNOT VERIFY the seam for notes/{_note43}: run {_rid43} — the first "
                        f"run after seq-{_seq43} — has no readable `started_at` "
                        f"({_run43.get('started_at')!r}), so the succession cannot be placed "
                        f"against it"))
        return _hits59, warn
    if _at43 > _st43:
        _full43 = (f"the succession judgement for notes/{_note43} (seq-{_seq43}) is "
                   f"recorded at {_entry43.get('at')}, AFTER run {_rid43} "
                   f"started at {_run43.get('started_at')} — a retrospective seam "
                   f"correction: the successor must append its succession no later "
                   f"than its first run (DEC-159, BUG-1723)")
        if _seam_era_start and _at43.date().isoformat() < _seam_era_start:
            # BEFORE THE SEAM WAS GRADED (BUG-1071's rule for INV-32, same reason):
            # the record cannot be re-recorded to satisfy a rule that did not exist
            # when it was written (DEC-227). A note, so the exemption is visible.
            warn.append(f"INV-43 {_feat59}: predates seam_era_start {_seam_era_start}; "
                        f"not graded — would fail: {_full43}.")
            return _hits59, warn
        _hits59.append(("INV-43", f"retrospective succession for notes/{_note43}", _full43))
    return _hits59, warn


def inv_43(ctx, feat):
    bad, warn, _hits59 = [], [], []
    _feat59 = feat
    _seam_era_start = ctx.seam_era_start
    _doc59, _era59 = _feat59_record(ctx, feat)
    if _doc59 is None:
        return bad, warn, _hits59
    _runs59, _need_succ, _succ_entries = _feat59_successions(ctx, feat, _doc59, _era59)
    for _k43, (_seq43, _note43, _) in enumerate(_need_succ):
        if _k43 >= len(_succ_entries):
            break  # INV-40 names the missing one
        _hits43, _warn43 = _inv43_placement(_feat59, _seam_era_start, _seq43, _note43,
                                            _inv43_run(_runs59, _seq43), _succ_entries[_k43])
        _hits59.extend(_hits43)
        warn.extend(_warn43)
    return bad, warn, _hits59


def _collate59_in_era(feat, _hits59):
    """An in-era record: one violation per hit, the full form."""
    bad = []
    _feat59 = feat
    # INV-43 gates on a terminal feature too (SC-03/D-02): a retrospective succession is
    # the record of work that crossed the seam unhanded, and shipping does not change what
    # the ledger says happened. Validate c0 struck the terminal downgrade this branch first
    # carried; the boundary above is by DATE, not by station.
    for _inv, _short, _full in _hits59:
        bad.append(f"{_inv} {_feat59}: {_full}.")
    return bad


def _collate59_legacy_note(feat, _hits59):
    """A pre-era record: the ONE note listing every short form."""
    _feat59 = feat
    # ONE note per legacy feature, both invariants together, short forms only. It says
    # what was not graded so a wrongly granted exemption is visible (INV-17's rule), and
    # no more, so sixty of them do not bury the violations above them.
    _invs = "/".join(sorted({_inv for _inv, _, _ in _hits59}))
    return (f"{_invs} {_feat59}: predates the FEAT-59 ledger (no mission, judgements, "
            f"budget_decisions or rework key; no by-perspective BRIEF); not graded — "
            f"would fail: " + "; ".join(_s for _, _s, _ in _hits59) + ".")


def collate_feat59(ctx, feat, results):
    """The FEAT-59 family's joint emission: an in-era record gets one violation per hit; a
    pre-era record gets ONE note listing every short form, so sixty of them do not bury the
    violations above them (INV-32's lesson)."""
    bad, warn, _hits59 = [], [], []
    for _b, _w, _h in results:
        bad.extend(_b)
        warn.extend(_w)
        _hits59.extend(_h)
    if not _hits59:
        return bad, warn
    _doc59, _era59 = _feat59_record(ctx, feat)
    if _era59:
        bad.extend(_collate59_in_era(feat, _hits59))
    else:
        warn.append(_collate59_legacy_note(feat, _hits59))
    return bad, warn
