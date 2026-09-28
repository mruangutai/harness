"""The GitHub mirror agrees with disk: INV-13/21/24/26/28/30/37. (FEAT-69)"""
import os, re
import artifact_accessors
import harness_boundary
from check_state.ctx import FINISHED_STATIONS
# --- INV-21 (D-05): a mirrored feature whose task issues are recorded but whose
# container (parent) never was — `ship`/`abandon` cannot close it and `open` will not
# re-derive it (the mirror is write-only, DEC-138). Warn, not violation (D-05): the
# GitHub Issues sync is never a gate, and a re-run of `open` fixes it. Vacuous
# when github.sync is off — the check costs nothing then.
def _inv21_feature_doc(ctx, feat):
    """The feature's feature.json document behind the github.sync gate: (doc, findings).
    The doc is None when sync is off, the file is absent, or it does not parse — only the
    last of those is a finding."""
    bad = []
    fpath = ctx.fpath
    cj = ctx.cj
    if not (cj and (cj.get("github") or {}).get("sync")):
        return None, bad
    fy = ctx.path(feat, 'feature.json')
    if not os.path.isfile(fy):
        return None, bad
    e = ctx.record_error(feat)
    if e is not None:
        bad.append(f"{fpath(feat, 'feature.json')} does not parse, so INV-21 cannot be "
                   f"checked for it: {e}")
        return None, bad
    return ctx.record(feat)[0] or {}, bad


def _inv21_has_task_issue(gblk):
    """Whether the github block records at least one numeric issue under a T-NN key."""
    _issues = gblk.get("issues")
    return bool(isinstance(_issues, dict) and any(
        re.fullmatch(r"T-\d+", str(k).strip()) and str(v).strip().isdigit()
        for k, v in _issues.items()))


def _inv21_orphan_issues(feat, gdoc):
    """The finding for a feature whose github block records task issues but no numeric
    parent, if any."""
    gblk = gdoc.get("github") if isinstance(gdoc, dict) else None
    if not isinstance(gblk, dict):
        return []
    has_issue = _inv21_has_task_issue(gblk)
    has_parent = str(gblk.get("parent", "")).strip().isdigit()
    if has_issue and not has_parent:
        return [f"INV-21: {feat} has recorded task issues but no numeric "
                f"parent — ship/abandon cannot close the container and open "
                f"will not re-derive it (D-05). Re-run `open` to record it."]
    return []


def inv_21(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    gdoc, bad = _inv21_feature_doc(ctx, feat)
    if gdoc is None:
        return bad, warn
    warn.extend(_inv21_orphan_issues(feat, gdoc))
    return bad, warn

# --- INV-24 (DEC-203): a feature that records factory state must name a repository the
# fleet declares, and no two features may claim one issue. The factory writes exactly one
# harness file — a feature's own `factory` block — so that block is the only place the
# harness can disagree with the board about what is in flight.
# The parent is counted alongside the task issues, not separately: gh-sync.py's `open`
# ALSO adopts or creates a container for the same feature in the same repository, so a
# container published beside one the factory created is D-12's collision, and comparing
# parents and issues in one list is the only place in this increment it becomes visible.
# A feature.json with no `factory` block contributes nothing and is not a violation.
def _inv24_factory_blocks(ctx):
    """Each feature's `factory` block, in feature order. A feature with no feature.json, an
    unreadable one, or no block contributes nothing (a generator, so the unreadable case keeps
    its `continue`)."""
    for feat in ctx.features:
        # (FEAT-63: `None` is also an ABSENT record, which an isfile check used to skip here.)
        fdoc = ctx.record(feat)[0]
        if fdoc is None:
            continue  # the parse failure is already a violation elsewhere; do not double-report
        fac = fdoc.get("factory")
        if not isinstance(fac, dict):
            continue
        yield feat, fac


def _inv24_fleet_names(fleet):
    """The repository names the fleet declares."""
    # TYPES ARE VALIDATED, NOT ASSUMED (panel2 C1). A missing repository name must
    # not enter the allow-list, and invalid issue numbers are refused at the shared
    # feature reader before collision checks run.
    return [r["name"] for r in (fleet.get("repos") or [])
            if isinstance(r, dict) and isinstance(r.get("name"), str) and r["name"]]


def _inv24_repo(feat, fac, fleet):
    """The block's repository name when the fleet declares it, else (None, the finding)."""
    names = _inv24_fleet_names(fleet)
    repo = fac.get("repo")
    if not isinstance(repo, str) or not repo:
        return None, [f"INV-24 {feat}: factory.repo is {repo!r}, not a repository name — "
                      f"set it to an owner/name string the fleet declares, or remove the "
                      f"factory block if this feature claims no work."]
    if repo not in names:
        return None, [f"INV-24 {feat}: records factory repo {repo!r}, which the fleet does not "
                      f"declare — fleet names: {', '.join(names) or '(none)'}. Add it to "
                      f".harness/factory/fleet.yaml, or correct the feature's factory.repo."]
    return repo, []


def _inv24_numbers(feat, fac):
    """The (number, where-it-came-from) pairs a factory block records, and the finding for a
    container of the wrong type."""
    # Each number carries WHERE IT CAME FROM. Re-deriving the label later from
    # `n == fac.get("parent")` renders the duplicate message as "(parent and parent)" in
    # the exact container-equals-task case this check exists for, because both sides of
    # the comparison are then true.
    bad, nums = [], []
    issues = fac.get("issues")
    if isinstance(issues, dict):
        nums.extend((v, f"task {k}") for k, v in issues.items())
    elif isinstance(issues, list):
        nums.extend((v, "a task") for v in issues)
    elif issues is not None:
        # The CONTAINER type was assumed while its contents were validated: `issues: 42`
        # left nums empty, so no collision check ran and nothing was reported at all.
        bad.append(f"INV-24 {feat}: factory.issues is {issues!r}, which is neither a "
                   f"T-NN-to-number mapping nor a list of numbers — no issue in this "
                   f"block can be checked for collision. Re-run `factory publish` to "
                   f"rewrite it, or correct it by hand.")
    if fac.get("parent") is not None:
        nums.append((fac.get("parent"), "the parent"))
    return bad, nums


def _inv24_issue_number(n):
    """`n` as an int, or None when it is not an integer or a digit string."""
    # A DIGIT STRING IS A NUMBER HERE. INV-21 thirty lines above accepts `parent: "40"`
    # deliberately — gh-sync.py's reader was widened to it because bare-digits-only
    # read a quoted number as absent. Rejecting the same shape here would make one
    # legal feature.json pass one invariant and hard-block on its twin (D-03).
    if isinstance(n, bool) or not (isinstance(n, int) or str(n).strip().isdigit()):
        return None
    return int(n)


def _inv24_collision(feat, repo, n, _src, _seen_here, _fac_pairs):
    """One recorded number against the feature's own block (`_seen_here`) and the
    cross-feature ledger (`_fac_pairs`); both are extended here."""
    num = _inv24_issue_number(n)
    if num is None:
        return [f"INV-24 {feat}: records issue number {n!r} for {repo}, which is not "
                f"an integer — re-run `factory publish` to rewrite the block, or "
                f"correct it by hand."]
    key = (repo, num)
    if key in _seen_here:
        return [f"INV-24 {feat}: records {repo} issue {num} twice within its own factory "
                f"block ({_seen_here[key]} and {_src}) — a container that is also a "
                f"task issue is D-12's collision. "
                f"Re-run `factory publish` after correcting the block."]
    _seen_here[key] = _src
    if key in _fac_pairs and _fac_pairs[key] != feat:
        return [f"INV-24: {_fac_pairs[key]} and {feat} both record {repo} issue {num} — "
                f"two features claiming one issue means the board and the harness "
                f"disagree about what is in flight. Decide which feature owns it and "
                f"clear the other's factory block."]
    _fac_pairs[key] = feat
    return []


def _inv24_collisions(feat, repo, nums, _fac_pairs):
    """Every number the block records, checked for collision."""
    # WITHIN a feature as well as across features (panel2 C2). The comparison used to be
    # `!= feat`, so a feature whose own parent equalled one of its own task issues never
    # fired — which is exactly D-12's container collision, in the one shape this check
    # was written to make visible.
    bad = []
    _seen_here = {}
    for n, _src in nums:
        bad.extend(_inv24_collision(feat, repo, n, _src, _seen_here, _fac_pairs))
    return bad


def _inv24_feature(feat, fac, fleet, _fac_pairs):
    """One feature's factory block against the fleet: the repository check, then the
    collision check of every issue number it records."""
    repo, bad = _inv24_repo(feat, fac, fleet)
    if repo is None:
        return bad
    bad, nums = _inv24_numbers(feat, fac)
    bad.extend(_inv24_collisions(feat, repo, nums, _fac_pairs))
    return bad


def inv_24(ctx):
    bad, warn = [], []
    H, root = ctx.H, ctx.root
    _fac_pairs = {}
    for feat, fac in _inv24_factory_blocks(ctx):
        fleet_p = os.path.join(H, "factory", "fleet.yaml")
        if not os.path.isfile(fleet_p):
            bad.append(f"INV-24 {feat}: records factory state but {os.path.relpath(fleet_p, root)} "
                       f"is absent — no fleet declares the repository it claims work in. "
                       f"Write the fleet declaration, or clear the feature's factory block.")
            continue
        try:
            fleet = artifact_accessors.load_fleet(fleet_p) or {}
        except artifact_accessors.FleetError as _e:
            bad.append(f"INV-24 {feat}: records factory state but the fleet file does not parse: "
                       f"{_e} — fix .harness/factory/fleet.yaml before any factory run.")
            continue
        bad.extend(_inv24_feature(feat, fac, fleet, _fac_pairs))
    return bad, warn

# --- INV-28 (FEAT-26 T-05, REQ-04): a feature that shipped but whose pull request
# number was never recorded. WARN, not violation: the mirror is never a gate (DEC-138),
# and the remedy is one command that can be run at any time.
#
# THE FAILURE THIS MAKES VISIBLE IS A HABIT DECAYING, NOT A BUG. `feature.json`'s `pr`
# was filled by hand for thirteen features and then the hand stopped; five ran null before
# anyone noticed (#492). Nothing checked, so nothing complained.
#
# ONE LINE PER FEATURE, never an aggregate count. A per-feature check that reports a
# single total cannot tell the operator WHICH feature to run the remedy on, which makes
# the report unactionable at exactly the moment it matters.
#
# GATED ON github.sync, like INV-21 above: a repository with no mirror has no pull
# requests to record, and the remedy needs a working `gh`.
#
# THE TERMINAL MARKER IS TERMINAL AND IS SILENT HERE, deliberately. It asserts that no seam was
# crossed and nothing shipped, so there is no pull request to have missed. Only the `done`
# station is checked, read from plan.yaml (FEAT-41 T-07) — the feature.json read below stays,
# because this invariant is ABOUT that document's `pr` key.
def _inv28_feature_doc(ctx, feat):
    """The feature's feature.json path and document behind the github.sync gate:
    (path, doc, findings). The doc is None when sync is off, the file is absent, or it
    does not parse — only the last of those is a finding."""
    bad = []
    fpath = ctx.fpath
    cj = ctx.cj
    if not (cj and (cj.get("github") or {}).get("sync")):
        return None, None, bad
    fy = ctx.path(feat, 'feature.json')
    if not os.path.isfile(fy):
        return fy, None, bad
    e = ctx.record_error(feat)
    if e is not None:
        bad.append(f"{fpath(feat, 'feature.json')} does not parse, so INV-28 cannot be "
                   f"checked for it: {e}")
        return fy, None, bad
    return fy, ctx.record(feat)[0] or {}, bad


def _inv28_missing_pr(ctx, feat, fy, pdoc):
    """The finding for a Done feature whose `pr` key holds no pull request number, if any."""
    root = ctx.root
    if not isinstance(pdoc, dict):
        return []
    if ctx.station(feat) != "done":
        return []
    _pr = pdoc.get("pr")
    # `isinstance(True, int)` is True in Python, so the bool exclusion is load-bearing:
    # `pr: true` is not a pull request number and must not read as one.
    if isinstance(_pr, int) and not isinstance(_pr, bool):
        return []
    return [f"INV-28: {feat} is Done but its pull request number was never "
            f"recorded — the linkage from the feature to the change that shipped "
            f"it is missing. Record it with `gh-sync.py record-pr "
            f"{os.path.relpath(os.path.dirname(fy), root)}`."]


def inv_28(ctx, feat):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    fy, pdoc, bad = _inv28_feature_doc(ctx, feat)
    if pdoc is None:
        return bad, warn
    warn.extend(_inv28_missing_pr(ctx, feat, fy, pdoc))
    return bad, warn

# --- INV-37 (BUG-1309): an enabled mirror must leave a Build-entry receipt.
# This deliberately runs regardless of station and task state. INV-26 correctly skips
# terminal and all-ready plans for board placement; neither condition proves a mirror ran.
# --- INV-37 (BUG-1309): an enabled mirror must leave a Build-entry receipt.
# This deliberately runs regardless of station and task state. INV-26 correctly skips
# terminal and all-ready plans for board placement; neither condition proves a mirror ran.
def _inv37_import():
    bad = []
    try:
        _fs37 = harness_boundary.load_repo_module("feature_schema")
    except harness_boundary.RepoModuleError as _fs37e:
        _fs37, _fs37e = None, _fs37e.cause
        bad.append("INV-37 CANNOT RUN: feature_schema.py did not import (%s: %s), so a missing "
                   "Build-entry receipt would go unreported." % (type(_fs37e).__name__, _fs37e))
    return bad, _fs37

def _inv37_sync(ctx):
    return bool((ctx.cj.get("github") or {}).get("sync"))

def _inv37_receipted(ctx, _feat37):
    _doc37 = ctx.record(_feat37)[0] or {}
    return bool((_doc37.get("factory") or {}).get("issues")
                or (_doc37.get("github") or {}).get("build_entry") is not None)

def _inv37_finding(_fs37, _feat37, _fp37):
    _cmd37 = _fs37.recovery_command_for(_fp37)
    if _cmd37 == "open":
        return (f"INV-37 {_feat37}: github.sync is enabled but feature.json records no "
                f"github.build_entry, so no Build entry outcome was ever recorded and "
                f"the board cannot be telling the truth about this feature - run "
                f"gh-sync.py open {_fp37}.")
    return (f"INV-37 {_feat37}: github.sync is enabled but feature.json records no "
            f"github.build_entry, and the feature's own record says the work is "
            f"already under way or finished, so creating the mirror now would mean "
            f"task sub-issues for completed work - run gh-sync.py recover-terminal "
            f"{_fp37} --yes.")

def _inv37_feature(ctx, _fs37, plan_docs, _feat37):
    bad = []
    _fp37 = ctx.feature_dir(_feat37)
    if _feat37 in _fs37.BUILD_ENTRY_ERA_EXEMPT or _feat37 not in plan_docs:
        return bad
    if _inv37_receipted(ctx, _feat37):
        return bad
    bad.append(_inv37_finding(_fs37, _feat37, _fp37))
    return bad

def inv_37(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    plan_docs = ctx.plan_docs
    _import_bad37, _fs37 = _inv37_import()
    bad.extend(_import_bad37)

    _sync37 = _inv37_sync(ctx)

    if _fs37 is None or not _sync37:
        return bad, warn
    for _feat37 in ctx.features:
        bad.extend(_inv37_feature(ctx, _fs37, plan_docs, _feat37))
    return bad, warn

# --- INV-26 BEGINS — the marker T-05's verify slices on. Without it the slice is EMPTY and
# every literal-absence grep below trivially passes, which is the vacuous-grep failure this
# feature exists to remove. The verify's positive control requires derive_station INSIDE the
# slice for exactly that reason.
# --- INV-26 (issue #277): the board must agree with the plan on disk.
#
# THIS INVARIANT CARRIES THE GUARANTEE. A failed station write is loud only on stderr, and
# the operator accepted that stderr inside a subagent run is not something they read — so a
# board that drifted is caught HERE or it is not caught at all. Every finding goes to `bad`:
# the operator's view of the factory being wrong is the condition the ticket opens with, and
# a warning is the same silence in a quieter font.
#
# THE IMPORT IS A VIOLATION WHEN IT FAILS — INV-25's precedent, and for its reason: gh_board
# ships with the repository, so being unimportable is a defect in the tree, never a property
# of the environment. Everything else below records NOTHING, because an offline or
# unconfigured environment must never become a red gate.
def _inv26_import():
    bad = []
    try:
        _gb = harness_boundary.load_repo_module("gh_board")
        # artifact_accessors owns FleetError, so INV-26 can classify the error without importing
        # another domain module. gh_board still imports factory_config for board validation.
    except harness_boundary.RepoModuleError as _gbe:
        _gb, _gbe = None, _gbe.cause
        bad.append("INV-26 CANNOT RUN: gh_board.py did not import (%s: %s), so a board that "
                   "disagrees with the plan would go unreported. The module ships with this "
                   "repository — restore .agents/skills/harness/bin/gh_board.py."
                   % (type(_gbe).__name__, _gbe))
    return bad, _gb


def _inv26_repo(cj):
    _g26 = cj.get("github") if isinstance(cj, dict) else None
    _repo26 = (_g26 or {}).get("repo")
    return _g26, _repo26


def _inv26_load_board(_gb, root):
    # AN UNUSABLE BOARD IS A VIOLATION, NOT SILENCE — the exact inverse of the behaviour
    # this task removes. load_board used to return None for both "no board declared" and
    # "board declared and broken", so a typo made INV-26 vacuous and left the gate GREEN.
    # It now raises for everything except an explicit null, and the gate must COMPLETE
    # and report rather than abort: one entry, then the rest of INV-26 is skipped.
    bad = []
    try:
        _inv26_board = _gb.load_board(root)
    except artifact_accessors.FleetError as _be26:
        _inv26_board = None
        bad.append("INV-26 CANNOT RUN: %s — the board declaration is unusable, so a "
                   "card that disagrees with the plan would go unreported." % _be26)
    return bad, _inv26_board


def _inv26_declared_board(_gb, cj, root):
    bad = []
    _inv26_board = None
    _repo26 = None
    if _gb is not None:
        _g26, _repo26 = _inv26_repo(cj)
        if isinstance(_g26, dict) and _g26.get("sync") is True and _repo26:
            bad, _inv26_board = _inv26_load_board(_gb, root)
    return bad, _inv26_board, _repo26



def _inv26_github_numbers(_gblk26, _issues26):
    _numbers26 = set()
    if isinstance(_gblk26.get("parent"), int):
        _numbers26.add(_gblk26["parent"])
    for _n26 in _issues26.values():
        if isinstance(_n26, int):
            _numbers26.add(_n26)
    for _n26 in (_gblk26.get("source_issues") or []):
        if isinstance(_n26, int):
            _numbers26.add(_n26)
    return _numbers26


def _inv26_feature_numbers(ctx, _feat26, plan_docs):
    if not plan_docs.get(_feat26):
        return set()
    if ctx.station(_feat26) in FINISHED_STATIONS:
        return set()
    _fj26 = ctx.record(_feat26)[0] or {}
    _gblk26 = _fj26.get("github") or {}
    _issues26 = _gblk26.get("issues") or {}
    if not _issues26:
        return set()
    return _inv26_github_numbers(_gblk26, _issues26)


def _inv26_numbers(ctx, plan_docs):
    # THE CANDIDATE SET IS BUILT FROM DISK FIRST, so the network is touched only if there is
    # something to ask about. That is INV-30's posture one screen below, and it is the one this
    # invariant was missing (issue #1541): the whole-board read downloaded every card the board
    # has ever held — 918 items over ten sequential `gh` processes, 11.25s of this script's
    # 14.3s — to answer questions about the handful of features actually in flight. Measured
    # 2026-09-09, that handful was FOURTEEN features carrying ZERO mirrored issues, so the
    # entire download was compared against nothing.
    #
    # The skip conditions here are a SUPERSET of the loop's below, deliberately: an extra issue
    # number costs one alias in a batched query, while a missing one would make the loop report
    # CANNOT VERIFY for a card that is on the board. Over-asking is cheap; under-asking lies.
    _numbers26 = set()
    for _feat26 in ctx.features:
        _numbers26 |= _inv26_feature_numbers(ctx, _feat26, plan_docs)
    return _numbers26


def _inv26_stations(_gb, _inv26_board, _repo26, _numbers26, _gh_bin):
    # A FAILED BOARD READ RECORDS NOTHING. board_stations_for already refuses a truncated
    # read by raising, which is what keeps a partial read from being reported as an empty
    # column — but the remedy here is silence, not a red gate, because the network is not
    # the tree.
    #
    # AN EMPTY CANDIDATE SET IS AN EMPTY MAP, NOT None. None skips the whole comparison
    # block below, and that block carries findings that need no board at all — the
    # mirror-never-ran clause among them. Nothing to look up is not the same as nothing
    # to check.
    try:
        os.environ["FACTORY_GH"] = _gh_bin
        _stations = _gb.board_stations_for(_inv26_board, _repo26, _numbers26)
    except _gb.BoardError:
        _stations = None
    return _stations



def _inv26_task_status_entry(_tstat, _t):
    if isinstance(_t, dict) and _t.get("id"):
        _tstat[_t["id"]] = _t.get("status") or "ready"


def _inv26_task_status(_pdoc):
    _tstat = {}
    for _t in (_pdoc.get("tasks") or []):
        _inv26_task_status_entry(_tstat, _t)
    return _tstat


def _inv26_projected(_gb, _feat, _pdoc, _fj, _issues):
    # ONE CALL, INSIDE THE TRY THAT ALREADY TREATS A gh_board FAILURE AS A VIOLATION.
    # `rec` is the shape gh-sync.load_recorded returns, built from the feature.json this
    # loop already has. source_issues is empty because this invariant compares TASK
    # cards and the parent, and a source issue's card is the parent's station — already
    # covered by the parent claim above.
    bad = []
    try:
        _projected = _gb.project(
            _pdoc, {"issues": _issues,
                    "parent": (_fj.get("github") or {}).get("parent"),
                    "source_issues": (_fj.get("github") or {}).get("source_issues") or []})
    except artifact_accessors.FleetError as _pe26:
        # A VOCABULARY MISS IS A VIOLATION, NOT A SKIP. project raises FleetError
        # naming the task and the value, which is the defect this feature exists to
        # end — reporting it as silence would be the fail-open D-11 removes.
        bad.append(f"INV-26 {_feat}: the plan carries a station the vocabulary does not "
                   f"contain, so no card can be checked against it — {_pe26}")
        _projected = None
    return bad, _projected


def _inv26_accepted(_want, _tstat, _tid, _station):
    # D-24, on the operator's ruling 4 of 2026-08-23 (FEAT-33 T-22). Under
    # D-23 a done task's sub-issue is deliberately left OPEN so it can hold its
    # column through the whole Review phase.
    #
    # THE ORIGINAL JUSTIFICATION HERE WAS FALSE and is corrected rather than
    # deleted. It argued that GitHub's native `Item closed` workflow lands a
    # closed issue's card in the done column by itself, and cited board 3 never
    # having held a card at Review as the measurement. Measured 2026-08-25:
    # FEAT-34's thirteen sub-issues #818 through #830 are ALL CLOSED and ALL sit
    # at Review. A closed issue's card stays where it is.
    #
    # What is actually true, and what this widening rests on now: `ship` — not a
    # close — is what writes the done station (DEC-203). So while a feature's own
    # station is review, a done task's card may legitimately read the done, review
    # OR building station: done if ship has already run, and review or building
    # because those are what the review phase itself leaves behind.
    #
    # BOUNDED ON THAT STATION ON PURPOSE, unchanged in force: an unconditional
    # widening would silence the mis-columned done card the invariant was
    # extended to catch. The station is read from plan.yaml now (FEAT-41 T-07),
    # the same file `_pdoc` came from.
    _accept = {_want}
    if _tstat.get(_tid) == "done" and _station == "review":
        _accept |= {"review", "building"}
    _wanttxt = (_want if len(_accept) == 1
                else ", ".join(sorted(_accept)[:-1]) + " or " + sorted(_accept)[-1])
    return _accept, _wanttxt


def _inv26_task_card(_gb, _stations, _station, _feat, _tid, _num, _projected, _tstat):
    bad = []
    # THE FAIL-OPEN IS DELETED (D-11). This read `if _want is None: continue`, so a
    # recorded sub-issue that the placement rule did not place went unexamined. A
    # card project declines to place is now a violation naming the feature, the task
    # and the station the plan carries.
    _want = _projected.get(_num)
    if _want is None:
        bad.append(f"INV-26 {_feat} {_tid} (issue #{_num}): the plan carries station "
                   f"{_tstat.get(_tid, 'ready')!r} and no card placement follows from "
                   f"it, so the board cannot be checked against the plan.")
        return bad
    _accept, _wanttxt = _inv26_accepted(_want, _tstat, _tid, _station)
    _found, _reason = _gb.read_station(_stations, _num)
    if _reason:
        # CANNOT VERIFY, NOT CLEAN. A lookup that misses leaves both sides of
        # the comparison empty and every record then compares equal — which is
        # precisely the silence this invariant exists to break.
        bad.append(f"INV-26 CANNOT VERIFY {_feat} {_tid} (issue #{_num}): "
                   f"{_reason}. The plan says {_tstat.get(_tid, 'pending')}, so "
                   f"the card should read {_wanttxt}.")
    elif _found not in _accept:
        bad.append(f"INV-26 {_feat} {_tid} (issue #{_num}): plan says "
                   f"{_tstat.get(_tid, 'pending')}, so the card should read "
                   f"{_wanttxt} — the board reads {_found}.")
    return bad


def _inv26_task_cards(_gb, _stations, _station, _feat, _issues, _projected, _tstat):
    bad = []
    for _tid in sorted(_issues):
        _num = _issues[_tid]
        bad += _inv26_task_card(_gb, _stations, _station, _feat, _tid, _num, _projected, _tstat)
    return bad


def _inv26_parent_card(_gb, _stations, _feat, _fj, _projected):
    bad = []
    _parent = (_fj.get("github") or {}).get("parent")
    if isinstance(_parent, int):
        _parent_want = _projected.get(_parent)
        if _parent_want is not None:
            _pfound, _preason = _gb.read_station(_stations, _parent)
            if _preason:
                bad.append(f"INV-26 CANNOT VERIFY {_feat} parent (issue #{_parent}): "
                           f"{_preason}. The plan projects {_parent_want}.")
            elif _pfound != _parent_want:
                bad.append(f"INV-26 {_feat} parent (issue #{_parent}): the plan projects "
                           f"{_parent_want} — the board reads {_pfound}.")
    return bad


def _inv26_source_card(_gb, _stations, _feat, _source, _projected):
    bad = []
    if not isinstance(_source, int):
        return bad
    _source_want = _projected.get(_source)
    if _source_want is None:
        return bad
    _sfound, _sreason = _gb.read_station(_stations, _source)
    if _sreason:
        bad.append(f"INV-26 CANNOT VERIFY {_feat} source (issue #{_source}): "
                   f"{_sreason}. The plan projects {_source_want}.")
    elif _sfound != _source_want:
        bad.append(f"INV-26 {_feat} source (issue #{_source}): the plan projects "
                   f"{_source_want} — the board reads {_sfound}.")
    return bad


def _inv26_source_cards(_gb, _stations, _feat, _fj, _projected):
    bad = []
    for _source in (_fj.get("github") or {}).get("source_issues") or []:
        bad += _inv26_source_card(_gb, _stations, _feat, _source, _projected)
    return bad


def _inv26_feature(ctx, _gb, _stations, plan_docs, _feat):
    bad = []
    _station = ctx.station(_feat)
    _pdoc = plan_docs.get(_feat)
    if not _pdoc:
        # No plan.yaml, or one that did not load. Other invariants own both — the
        # load failure is already a violation above, and restating it here would
        # report one defect twice.
        return bad

    # THE FEATURE.JSON READ STAYS — this block reads `github.issues`, `github.parent`
    # and `factory.issues` off `_fj` further down. Only the STATION moved to plan.yaml.
    _fj = ctx.record(_feat)[0] or {}

    # THE TERMINAL EXEMPTION. `ship` writes the parent's card to the done station and
    # records the terminal station, while the plan-derived station would still say
    # review — so without this every shipped feature is a permanent false violation.
    #
    # THE CONDITION NOW KEYS ON plan.yaml's STATION (FEAT-41 T-07) rather than
    # feature.json's status, which is the only change here: one file records the station.
    if _station in FINISHED_STATIONS:
        return bad


    # INV-26 only compares cards recorded by the GitHub mirror. A feature with no
    # mirrored task issue has no board projection to verify; mirror opening owns its
    # separate lifecycle obligation.
    _issues = ((_fj.get("github") or {}).get("issues") or {})
    if not _issues:
        return bad

    _tstat = _inv26_task_status(_pdoc)

    _pbad, _projected = _inv26_projected(_gb, _feat, _pdoc, _fj, _issues)
    bad += _pbad
    if _projected is None:
        return bad

    bad += _inv26_task_cards(_gb, _stations, _station, _feat, _issues, _projected, _tstat)

    # Parent and source cards are compared through the same projection as task cards.
    bad += _inv26_parent_card(_gb, _stations, _feat, _fj, _projected)
    bad += _inv26_source_cards(_gb, _stations, _feat, _fj, _projected)
    return bad


def _inv26_compare(ctx, _gb, _stations, plan_docs):
    # THE PLACEMENT RULE IS NOT HERE ANY MORE (FEAT-41 T-06, D-11). The two lookup tables
    # that stood here are DELETED, not lowercased: the rule they encoded — which card
    # belongs at which station, and when — now lives in gh_board.project and nowhere else,
    # so this file holds the COMPARE side only. It asks project where a card belongs and
    # reports the cards that disagree.
    #
    # What went with them: a status-to-COLUMN mapping, which was the last thing in this file
    # translating between two vocabularies, and a three-key lookup whose ready-to-backlog
    # exception D-11 removed outright. plan.yaml and the board now carry the same word with
    # the same meaning and nothing is derived between them.
    #
    # Their names are deliberately not written here. This task's verify greps the whole file
    # for both identifiers and fails on a COMMENT as readily as on code — a dead name in
    # prose is still a reader's next false lead.
    bad = []
    for _feat in ctx.features:
        bad += _inv26_feature(ctx, _gb, _stations, plan_docs, _feat)
    return bad


def _inv26_check(ctx, _gb, _inv26_board, _repo26, _gh_bin, plan_docs):
    bad = []
    _gh_ok = ctx.gh_ok(_gh_bin)
    _numbers26 = _inv26_numbers(ctx, plan_docs)

    _stations = None
    if _gh_ok:
        _stations = _inv26_stations(_gb, _inv26_board, _repo26, _numbers26, _gh_bin)

    if _stations is not None:
        bad += _inv26_compare(ctx, _gb, _stations, plan_docs)
    return bad


def inv_26(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    cj, plan_docs = ctx.cj, ctx.plan_docs
    _ibad, _gb = _inv26_import()
    bad += _ibad

    # THE BINARY IS OVERRIDABLE OR THIS CANNOT BE TESTED. FACTORY_GH is the variable factory_gh
    # already honours, so ONE fake serves both the module and this invariant. A third variable
    # name would be a third thing to get wrong.
    _gh_bin = os.environ.get("FACTORY_GH") or "gh"

    _bbad, _inv26_board, _repo26 = _inv26_declared_board(_gb, cj, root)
    bad += _bbad

    if _inv26_board:
        bad += _inv26_check(ctx, _gb, _inv26_board, _repo26, _gh_bin, plan_docs)
    return bad, warn

# --- INV-30 (FEAT-34 T-08, REQ-12): a feature recorded `Done` whose milestone is still OPEN.
#
# IT KEYS ON THE MILESTONE, NEVER ON THE STATUS AGREEING WITH ITSELF. `status: Done` has more
# than one path that can write it — the 2026-08-24 repair wrote ten by hand — so a Done status
# corroborating a Done status proves nothing. The milestone has exactly ONE writer,
# `gh-sync.py`'s `cmd_ship`, which PATCHes it closed unconditionally once entered. So an OPEN
# milestone on a Done feature is proof that `ship` never ran.
#
# THE OFFLINE POSTURE IS INV-26's, NOT A NEW ONE. The IMPORT failing is a violation, because
# the module ships with this repository. Everything else — `gh` absent, unauthenticated, the
# network unreachable, a milestone that 404s — records NOTHING. `check-state.py` runs before
# every commit, and an offline environment must never become a red gate.
#
# ONE `gh` CALL, NOT ONE PER FEATURE. 24 features carry a recorded milestone at 9165162; a
# request each would make the pre-commit gate pay 24 round trips for a check that one paginated
# list answers. The whole milestone list is fetched once and matched by number in memory.
def _inv30_import():
    bad = []
    try:
        harness_boundary.load_repo_module("gh_board")
        _inv30_import_ok = True
    except harness_boundary.RepoModuleError as _gbe30:
        _inv30_import_ok, _gbe30 = False, _gbe30.cause
        bad.append("INV-30 CANNOT RUN: gh_board.py did not import (%s: %s), so a feature recorded "
                   "Done whose milestone is still open would go unreported. The module ships with "
                   "this repository — restore .agents/skills/harness/bin/gh_board.py."
                   % (type(_gbe30).__name__, _gbe30))
    return bad, _inv30_import_ok


def _inv30_repo(cj):
    _g30 = cj.get("github") if isinstance(cj, dict) else None
    _repo30 = (_g30 or {}).get("repo")
    return _g30, _repo30


def _inv30_feature_doc(ctx, _feat30):
    _doc30 = ctx.record(_feat30)[0]
    if _doc30 is None:
        # INV-28 above already reports an unparseable feature.json. Restating it here would
        # report one defect twice.
        return None
    if not isinstance(_doc30, dict):
        return None
    return _doc30


def _inv30_candidate(ctx, _feat30):
    _fy30 = ctx.path(_feat30, 'feature.json')
    _doc30 = _inv30_feature_doc(ctx, _feat30)
    if _doc30 is None:
        return None
    # The `done` station and nothing else, read from plan.yaml (FEAT-41 T-07). The terminal
    # marker is terminal and silent here for INV-28's reason: nothing shipped, so there is
    # no milestone that ship should have closed. The feature.json read above stays — this
    # invariant needs `github.milestone` off that document.
    if ctx.station(_feat30) != "done":
        return None
    _ms30 = (_doc30.get("github") or {}).get("milestone")
    if _ms30 is None:
        # A Done feature with no recorded milestone is outside this invariant's reach, not a
        # finding. Eight features are in that state at 9165162 and none of them is a defect
        # INV-30 can speak to.
        return None
    try:
        return (_feat30, int(_ms30))
    except (TypeError, ValueError):
        return None


def _inv30_candidates(ctx):
    # THE CANDIDATE SET IS BUILT FROM DISK FIRST, so the network is touched only if there is
    # something to ask about. A tree with no Done-and-milestoned feature makes no gh call at all.
    _cand30 = []
    for _feat30 in ctx.features:
        _c30 = _inv30_candidate(ctx, _feat30)
        if _c30 is not None:
            _cand30.append(_c30)
    return _cand30



def _inv30_open_milestones(ctx, _gh_bin30, _repo30):
    # `--paginate` rather than a bare per_page: the list is small today and silently
    # truncating it later would make this invariant quietly stop firing on the oldest
    # features, which is the decay shape INV-28 was written to catch.
    _r30 = ctx.spawn(
        [_gh_bin30, "api", "--paginate",
         "repos/%s/milestones?state=open&per_page=100" % _repo30,
         "-q", ".[].number"],
        capture_output=True, text=True, timeout=60)
    if _r30 is None or _r30.returncode != 0:
        return None
    return {int(x) for x in _r30.stdout.split() if x.strip().isdigit()}


def _inv30_compare(_cand30, _open30, fpath):
    bad = []
    for _feat30, _num30 in _cand30:
        if _num30 not in _open30:
            continue
        bad.append(
            "INV-30 %s: status is Done but milestone #%d is still OPEN, so "
            "`gh-sync.py ship` never ran for it. The status is not evidence — it has "
            "several writers and the milestone has one. Close it with `python3 "
            ".agents/skills/harness/bin/gh-sync.py ship %s`."
            % (_feat30, _num30, fpath(_feat30)))
    return bad


def _inv30_check(ctx, _cand30, _repo30, fpath):
    # SAME RESOLUTION AS INV-26 at :1371 — FACTORY_GH first. A fixture that stubs
    # `gh` through that variable must reach this invariant too, or INV-30 would be
    # untestable offline while claiming an offline posture.
    _gh_bin30 = os.environ.get("FACTORY_GH") or "gh"
    _open30 = None
    _gh_ok30 = ctx.gh_ok(_gh_bin30)

    if _gh_ok30:
        _open30 = _inv30_open_milestones(ctx, _gh_bin30, _repo30)

    # None means "we could not ask", which is NOT the same as "nothing is open" and must
    # never be treated as one. Silence here is the whole offline posture.
    bad = []
    if _open30 is not None:
        bad += _inv30_compare(_cand30, _open30, fpath)
    return bad


def inv_30(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath
    cj = ctx.cj
    _ibad, _inv30_import_ok = _inv30_import()
    bad += _ibad

    _g30, _repo30 = _inv30_repo(cj)

    if _inv30_import_ok and (_g30 or {}).get("sync") and _repo30:
        _cand30 = _inv30_candidates(ctx)

        if _cand30:
            bad += _inv30_check(ctx, _cand30, _repo30, fpath)
    return bad, warn

# --- INV-13: the GitHub mirror is either configured or explicitly off — never limbo
# (DEC-138). `sync: true` with no pinned repo would make every gh-sync call skip
# silently, which reads exactly like a working mirror to anyone not tailing logs.
# A missing `github` block means the project predates the feature: surface it once.
def inv_13(ctx):
    bad, warn = [], []
    cj = ctx.cj
    if cj:
        gh_ = cj.get("github")
        if gh_ is None:
            warn.append("harness.json has no `github` block — predates DEC-138. Run "
                        "/harness-init --upgrade to decide the Issues mirror once (sync on/off).")
        elif gh_.get("sync") and not gh_.get("repo"):
            bad.append("github.sync is ON but github.repo is not pinned — every sync will "
                       "silently SKIP. Pin the repo (from `gh repo view`) or turn sync off.")
    return bad, warn
