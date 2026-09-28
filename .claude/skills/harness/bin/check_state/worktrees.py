"""git worktrees live where and as long as the layout says: INV-25/27/29/31. (FEAT-69)"""
import os
import harness_boundary
_HOOKS_REL = os.path.join(".claude", "skills", "harness", "hooks")

# --- INV-25 (issue #103): the environment itself must not contain an out-of-place
# worktree. The write guards now REFUSE writes into such a tree and refuse a session
# rooted in one, so an environment holding one is broken rather than merely unusual —
# which is why every branch below goes to `bad` and not to `warn`. A warning is the same
# silence in a quieter font.
#
# THE ONE PLACE A GIT SUBPROCESS IS ACCEPTABLE. The cost objection that kept this out of
# both hooks was that they run on EVERY governed write; check-state runs once per
# session. If git is absent or the command fails, record nothing: this invariant must
# never turn an unrelated environment into a red gate.
# THE IMPORT IS A VIOLATION WHEN IT FAILS, NOT A SILENT SKIP. Found by the review panel:
# this absorbed the ImportError into `_wt_seg = None`, `if _wt_seg:` then skipped every
# INV-25 branch, and a session holding a pre-existing out-of-place worktree printed
# "all state invariants hold" and exited 0. That is the fourth import route — the three
# in the two write guards fail closed, this one did not.
#
# It is a VIOLATION rather than a note because the module ships with the repository: it
# being unimportable is a defect in the tree, never a property of the environment. That
# is the opposite of the git-absent case below, which correctly records nothing.
def _inv25_import():
    bad = []
    try:
        _wt_seg = harness_boundary.WORKTREES_SEGMENT
    except AttributeError as _hbe:
        # The module is imported at the top of this file; a copy that lost the constant is
        # the one shape left that this row cannot run over.
        _wt_seg = None
        bad.append("INV-25 CANNOT RUN: harness_boundary.py did not import (%s: %s), so a "
                   "pre-existing out-of-place worktree would go unreported. The module ships "
                   "with this repository — restore "
                   ".agents/skills/harness/bin/harness_boundary.py."
                   % (type(_hbe).__name__, _hbe))
    return _wt_seg, bad

def _inv25_porcelain(ctx):
    _wtp = ctx.spawn(["git", "worktree", "list", "--porcelain"], cwd=ctx.root,
                     capture_output=True, text=True, timeout=10)
    return _wtp.stdout if _wtp is not None and _wtp.returncode == 0 else None

def _inv25_parse_record(rec):
    _path, _prunable = None, False
    for _line in rec.splitlines():
        if _line.startswith("worktree "):
            _path = _line[len("worktree "):].strip()
        elif _line.strip() == "prunable" or _line.startswith("prunable "):
            _prunable = True
    return _path, _prunable

def _inv25_parse_entries(wt_out):
    # Porcelain records are blank-line separated; `worktree <path>` opens each one and
    # `prunable` appears on its own, with no --verbose flag needed.
    _entries = []
    for _rec in wt_out.split("\n\n"):
        _path, _prunable = _inv25_parse_record(_rec)
        if _path:
            _entries.append((_path, _prunable))
    return _entries

def _inv25_inside_legal(p, legal_home):
    try:
        return os.path.commonpath([p, legal_home]) == legal_home
    except ValueError:      # different drives / unrelated roots
        return False

def _inv25_classify_entry(wpath, prunable, legal_home, real_root):
    bad = []
    _rp = os.path.realpath(wpath)
    if _inv25_inside_legal(_rp, legal_home):
        return bad
    _where = (f"INV-25: {wpath} is a git worktree outside {legal_home}{os.sep}, "
              f"where worktrees belong. A worktree elsewhere silently disables "
              f"the harness machinery for every session opened in it.")
    if _rp == real_root:
        # THIS BRANCH TESTS AGAINST THE SESSION ROOT, not against the legitimate
        # location above. They answer different questions — am I standing in
        # this tree, versus does this tree belong where it is — and they stay
        # two comparisons.
        #
        # NO REMOVAL GUIDANCE HERE. `git worktree remove` exits 0 when run from
        # inside the tree it removes, so telling this session to remove this
        # entry is telling it, at session entry, to delete the ground it is
        # standing on.
        bad.append(_where + " This session is rooted in it: start the session "
                            "from the main checkout, or from a checkout under "
                            "that location, instead.")
    elif prunable:
        # A prunable entry is a stale administrative record whose tree is
        # already gone from disk, so it can never be a live cwd.
        bad.append(_where + " The entry is stale — clear it with "
                            "`git worktree prune`.")
    else:
        # The session is not standing in it, so removal guidance is correct
        # here and it STAYS. Deleting it everywhere would be the opposite
        # defect.
        bad.append(_where + f" Remove it with `git worktree remove {wpath}`.")
    return bad

def _inv25_classify_entries(root, wt_seg, entries):
    bad = []
    # THE BASE IS DERIVED ONCE, FROM THE MAIN CHECKOUT, AND USED FOR BOTH THE
    # COMPARISON AND THE MESSAGE. The first porcelain entry is always the main
    # checkout, even when the command runs from inside a linked worktree, and a
    # repository with no linked worktrees returns itself — so the derivation is
    # total.
    #
    # NEVER <root>/.claude/worktrees/. `root` is CLAUDE_PROJECT_DIR or the cwd, so
    # in exactly the session this invariant exists to catch — one whose root IS an
    # out-of-place worktree — that base would mark every LEGITIMATE worktree under
    # the main checkout as out of place and hand it destructive removal guidance.
    _main = os.path.realpath(entries[0][0])
    _legal_home = os.path.realpath(os.path.join(_main, wt_seg))
    _real_root = os.path.realpath(root)

    # The first entry plays two SEPARATE parts and they must not be fused: it is
    # skipped as the main checkout, and it supplied the base above.
    for _wpath, _prunable in entries[1:]:
        bad.extend(_inv25_classify_entry(_wpath, _prunable, _legal_home, _real_root))
    return bad

def inv_25(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    _wt_seg, _import_bad = _inv25_import()
    bad.extend(_import_bad)

    if _wt_seg:
        _wt_out = _inv25_porcelain(ctx)

        if _wt_out:
            _entries = _inv25_parse_entries(_wt_out)

            if _entries:
                bad.extend(_inv25_classify_entries(root, _wt_seg, _entries))
    return bad, warn

# --- INV-29 (FEAT-34 T-06, REQ-01..REQ-06): a worktree must not survive its feature
# reaching a terminal state. INV-25's SIBLING, deliberately placed next to it: INV-25 asks
# whether a worktree belongs where it is, INV-29 asks whether it should still exist at all.
# Two different questions, so INV-25 above is untouched — the brief lists its enumeration
# under "already built — do not strike, do not rebuild".
#
# THE ENUMERATION IS NOT REPEATED HERE. `git worktree list` is run by worktree_terminal, the
# single shared predicate this gate and post-merge-sweep.py both cross (D-02), so the gate and
# the hook can never disagree about what is eligible. A second copy of the walk in this file
# is exactly what D-02 exists to prevent.
#
# classify_all, NEVER classify (D-10). classify covers ONE repository — it runs one
# `git worktree list` with cwd=root, and feature-worktree.py joins WORKTREES_SEGMENT only to a
# resolved owner_root, so a served repository's worktrees live inside a DIFFERENT git
# repository that a list in this checkout can never report. An INV-29 built on classify would
# satisfy every other criterion and fail SC-04, which grades an INV-29 line for a SECOND
# repository produced by ONE run of this script.
#
# THE IMPORT FAILING IS ITSELF A VIOLATION, exactly as INV-25 at :1109 and INV-26 at :1203.
# The module ships with this repository, so being unimportable is a defect in the tree and
# never a property of the environment.
def _inv29_import():
    bad = []
    try:
        _wt29 = harness_boundary.load_repo_module("worktree_terminal")
    except harness_boundary.RepoModuleError as _wt29e:
        _wt29, _wt29e = None, _wt29e.cause
        bad.append("INV-29 CANNOT RUN: worktree_terminal.py did not import (%s: %s), so a "
                   "worktree surviving its feature's terminal state would go unreported. The "
                   "module ships with this repository — restore "
                   ".agents/skills/harness/bin/worktree_terminal.py."
                   % (type(_wt29e).__name__, _wt29e))
    return _wt29, bad

def _inv29_fleet_path():
    # The fleet path is read as a CONSTANT, not re-derived. It is one of the two things that
    # tells a repository-level record apart from a worktree record — see the discriminator
    # below — and reading it here duplicates none of classify_all's resolution logic.
    try:
        _fleet_path29 = os.path.realpath(harness_boundary.load_repo_module("factory_config").FLEET_PATH)
    except harness_boundary.RepoModuleError:
        _fleet_path29 = None
    return _fleet_path29

def _inv29_classify_all(wt29, root):
    bad = []
    # A raise here is caught rather than allowed to abort the interpreter. classify_all
    # already handles the three failure shapes D-10 specifies; an unexpected exception is a
    # defect, and letting it propagate would take EVERY other invariant's findings down with
    # it — the gate would print a traceback and report nothing at all.
    try:
        _recs29 = harness_boundary.call_repo_module(wt29, "classify_all", root)
    except harness_boundary.RepoModuleError as _ce29:
        _recs29, _ce29 = [], _ce29.cause
        bad.append("INV-29 CANNOT RUN: worktree_terminal.classify_all raised (%s: %s), so a "
                   "worktree surviving its feature's terminal state would go unreported."
                   % (type(_ce29).__name__, _ce29))
    return _recs29, bad

def _inv29_root_is_inside(real_root, worktree_path):
    """Is this session standing inside the worktree the record describes?"""
    try:
        return os.path.commonpath([real_root, os.path.realpath(worktree_path)]) == \
               os.path.realpath(worktree_path)
    except ValueError:      # different drives / unrelated roots
        return False

def _inv29_repo_level(r29, fleet_path):
    # THE DISCRIMINATOR KEYS ON MORE THAN feature_id, AND IT HAS TO. A worktree whose path
    # is not under WORKTREES_SEGMENT emits feature_id None / repo None / unresolved
    # (worktree_terminal.py:202-206) — identical on class AND on feature_id to the
    # fleet-load record (:303-306). Keying on feature_id alone would classify a REAL
    # worktree as a repository-level failure and withhold the removal command from it.
    # What separates them: a repository-level record either names a declared repository
    # (repo is set) or IS the fleet file itself.
    return (
        r29["feature_id"] is None
        and (r29["repo"] is not None
             or (fleet_path is not None
                 and os.path.realpath(r29["path"]) == fleet_path))
    )

def _inv29_repo_level_finding(r29, fleet_path):
    # D-10's repository-level shape. BLOCKING for D-10's reason — the enumeration
    # failed there, so a terminal worktree could be standing and unreported.
    #
    # NO REMOVAL COMMAND, EVER, ON THIS BRANCH. The path is a repository root or the
    # fleet declaration, not a worktree. A removal command pointed at a repository
    # root would be actively dangerous, and there is nothing there to remove.
    _what29 = ("the fleet declaration"
               if fleet_path is not None
               and os.path.realpath(r29["path"]) == fleet_path
               else "repository %s" % r29["repo"])
    return ("INV-29: cross-repository enumeration failed at %s (%s) — %s. A "
            "worktree surviving its feature's terminal state could be standing "
            "there and unreported. No removal command is given: this path is not "
            "a worktree."
            % (r29["path"], _what29, r29["reason"]))

def _inv29_head(r29):
    # From here every record describes an actual worktree.
    if r29["klass"] == "terminal":
        _head29 = ("INV-29: %s is a standing worktree whose feature %s reached a terminal "
                   "state on the default branch. Act 3 is not optional — the checkout is "
                   "removed once the work has landed."
                   % (r29["path"], r29["feature_id"]))
    else:
        # unresolved, at the worktree level. THE FAILED LOOKUP IS NOT AN EXEMPTION, and
        # the message says so outright: a reader who mistook this for the abandoned-flow
        # case would treat the loudest branch as the quietest one.
        _head29 = ("INV-29: %s is a standing worktree whose terminal status could not be "
                   "determined — %s. A lookup that FAILED is not an exemption; the "
                   "worktree is reported rather than passed over."
                   % (r29["path"], r29["reason"]))

    # THE DIRTY CLAUSE IS ITS OWN SENTENCE, not folded into the command line. SC-03 grades
    # the two claims one at a time: that the tree is dirty, and that remove will decline.
    if r29["dirty"]:
        _head29 += (" The tree is dirty: `remove` will DECLINE until those changes are "
                    "committed, landed or discarded.")
    return _head29

def _inv29_guidance(r29, head29, real_root):
    if _inv29_root_is_inside(real_root, r29["path"]):
        # INV-25's precedent at :1173, for the same mechanical reason: `git worktree
        # remove` exits 0 from inside the tree it deletes, so handing this session that
        # command is telling it to delete the ground it is standing on. The finding still
        # prints; only the guidance is withheld.
        return (head29 + " This session is rooted in it, so no removal command is "
                         "given here: run it from the main checkout instead.")
    elif r29["repo"] is not None and r29["feature_id"] is not None:
        # THE COMMAND CARRIES THIS WORKTREE'S OWN IDENTITY, composed from this record's
        # own repo segment and id — never a bare command, and never another worktree's.
        # feature-worktree.py remove is named rather than `git worktree remove` because it
        # declines a dirty tree at exit 4 and an unlanded artifact directory at exit 5,
        # and it has no force flag. Raw git would take --force.
        # THE --id IS THE WORKTREE DIRECTORY'S OWN NAME, never the record's feature_id.
        # They differ for a SHORT-NAMED worktree: feature_id is the LANDED directory on the
        # default branch, which is the full name, while `remove` matches the checkout. Printing
        # feature_id there gives a command that exits "not a linked worktree" for a directory
        # plainly sitting in front of the reader. post-merge-sweep.py:150 already derives it
        # this way; this is the same derivation, not a second rule.
        return (head29 + " Remove it with `python3 "
                         ".agents/skills/harness/bin/feature-worktree.py remove "
                         "--repo %s --id %s` (path: %s)."
                         % (r29["repo"],
                            os.path.basename(r29["path"].rstrip(os.sep)),
                            r29["path"]))
    else:
        # An out-of-segment worktree: there is no repo/id pair to build the command from,
        # because the path never resolved to one. INV-25 above reports the same tree with
        # its own removal guidance, so nothing is lost by withholding it here.
        return (head29 + " Its path did not resolve to a repository and id, so no "
                         "removal command can be composed for it.")

def _inv29_record(r29, fleet_path, real_root):
    bad = []
    if r29["klass"] == "exempt_absent":
        # The feature directory is genuinely absent from the default branch. Nothing to
        # report: that is the abandoned-flow case, and it is silence by design.
        return bad

    _repo_level29 = _inv29_repo_level(r29, fleet_path)

    if _repo_level29:
        bad.append(_inv29_repo_level_finding(r29, fleet_path))
        return bad

    _head29 = _inv29_head(r29)
    bad.append(_inv29_guidance(r29, _head29, real_root))
    return bad

def inv_29(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    _wt29, _import_bad29 = _inv29_import()
    bad.extend(_import_bad29)

    if _wt29 is not None:
        _fleet_path29 = _inv29_fleet_path()

        _recs29, _classify_bad29 = _inv29_classify_all(_wt29, root)
        bad.extend(_classify_bad29)

        _real_root29 = os.path.realpath(root)

        for _r29 in _recs29:
            bad.extend(_inv29_record(_r29, _fleet_path29, _real_root29))
    return bad, warn

# --- INV-27 (FEAT-20): every layout surface speaks one language. The detector is
# layout_migration.py; this block composes findings from its STRUCTURED RESULT and
# never re-parses its CLI text. A NOT APPLICABLE root (no control-plane marker —
# a product checkout, or a test fixture) appends nothing, and a clean result appends
# nothing. The verdict is computed by the module, which is a DEC-174 carve-out by
# content for exactly that reason.
#
# THE IMPORT IS A VIOLATION WHEN IT FAILS — INV-25's precedent, and for its reason:
# the module ships with the repository, so it being unimportable is a defect in the
# tree, never a property of the environment.
# --- INV-27 (FEAT-20): every layout surface speaks one language. The detector is
# layout_migration.py; this block composes findings from its STRUCTURED RESULT and
# never re-parses its CLI text. A NOT APPLICABLE root (no control-plane marker —
# a product checkout, or a test fixture) appends nothing, and a clean result appends
# nothing. The verdict is computed by the module, which is a DEC-174 carve-out by
# content for exactly that reason.
#
# THE IMPORT IS A VIOLATION WHEN IT FAILS — INV-25's precedent, and for its reason:
# the module ships with the repository, so it being unimportable is a defect in the
# tree, never a property of the environment.
def _inv27_import():
    bad = []
    try:
        _lmod = harness_boundary.load_repo_module("layout_migration")
    except harness_boundary.RepoModuleError as _lme:
        _lmod, _lme = None, _lme.cause
        bad.append("INV-27 CANNOT RUN: layout_migration.py did not import (%s: %s), so a "
                   "half-migrated layout would go unreported. The module ships with this "
                   "repository — restore .agents/skills/harness/bin/layout_migration.py."
                   % (type(_lme).__name__, _lme))
    return bad, _lmod

def _inv27_scan(_lmod, root):
    bad = []
    try:
        _lres = harness_boundary.call_repo_module(_lmod, "scan", root)
    except _lmod.LayoutTableError as _lse:
        _lres = None
    except harness_boundary.RepoModuleError as _lse:
        _lres, _lse = None, _lse.cause
        bad.append("INV-27 CANNOT RUN: the layout scan raised (%s: %s) — fix "
                   "layout_migration.py or its reader table before trusting this gate."
                   % (type(_lse).__name__, _lse))
    return bad, _lres

def _inv27_surface(_lmod, root, _lrem, _sname, _srep):
    bad = []
    if _srep.verdict == "MIXED":
        _ev = "+".join(sorted(_srep.evidence)) if _srep.evidence else "none"
        bad.append(f"INV-27 {_sname}: layout is MIXED — evidence {_ev}; "
                   f"readers {_lmod.blame_text(_srep)}. {_lrem}")
    elif _srep.verdict == "CANNOT_VERIFY":
        _named = _lmod.blame_text(_srep)
        _suffix = f"; readers: {_named}" if _named else ""
        bad.append(f"INV-27 CANNOT VERIFY {_sname}: "
                   f"{_lmod.cause_text(_srep, root)}{_suffix}. {_lrem}")
    return bad

def inv_27(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    _import_bad27, _lmod = _inv27_import()
    bad.extend(_import_bad27)

    if _lmod is not None:
        _scan_bad27, _lres = _inv27_scan(_lmod, root)
        bad.extend(_scan_bad27)
        if _lres is not None and _lres.applicable:
            # Every entry ends with a remedy — house style; a finding an operator cannot
            # act on is a finding they will learn to skip. The form-set tag on each reader
            # path is load-bearing: [legacy] on a migrated tree means FINISH the reader,
            # [migrated] on a legacy tree means REVERT it, and the paths are identical
            # without the tag.
            _lrem = ("Finish or revert this surface inside one atomic commit; the form "
                     "rows are data in layout_migration.py.")
            # THE CAUSE TABLE IS CLOSED AND THE LOOKUP FAILS LOUD (code-review finding:
            # the earlier if/elif chain had no else, so a fifth cause value would have
            # appended nothing and this gate — the surface operators actually see —
            # would have passed clean while CI stayed red).
            # Wording and blame both come from the module — cause_text/blame_text are
            # the single owners (see layout_migration.blame, #379); this block adds only
            # the INV-27 framing and the remedy.
            for _sname in sorted(_lres.surfaces):
                bad.extend(_inv27_surface(_lmod, root, _lrem, _sname, _lres.surfaces[_sname]))
    return bad, warn

# --- INV-31 (FEAT-40 T-08, REQ-02/REQ-09): this clone's merge hook is not installed.
#
# WHY IT EXISTS AT ALL. The setup step lives in `.claude/skills/harness-init/SKILL.md`, whose
# subject is the control-plane clone, and an already-onboarded clone NEVER RE-RUNS IT. A doc
# step reaches a clone once; an invariant
# reaches every clone, every run. Measured at cc84b29 on this very checkout,
# `core.hooksPath` read `/Users/molchairuangutai/GitHub/harness/.git/hooks`, a directory
# holding fourteen files every one of which is a `.sample` — so `gh-sync.py ship` never ran at
# a merge, and NOTHING SAID SO. After this feature `ship` is the only thing that closes
# tickets and the post-merge sweep is the only thing that runs `ship`, so a clone without the
# hook silently stops closing tickets altogether.
#
# BOTH FINDINGS APPEND TO `bad`, NEVER `warn`, and that is a deliberate departure from INV-28,
# which warns on the stated ground that the mirror is never a gate. This is not a mirror fact.
# It is whether THIS MACHINE runs the hook that runs ship.
#
# SCOPE, decided rather than omitted: this invariant does NOT check whether a card is closed
# but away from the done station. `board_lifecycle.py`'s audit already reports exactly that as
# its STATION finding class, and a second detector for one fact is two rules that will drift.
# What was missing there was a RUNNER, not a detector, and that runner now sits inside `ship`,
# once per feature (DEC-203 item 8) — deliberately not here, where the audit's four network
# calls would fall on every run of the state checker.
def _inv31_post_merge(want_abs):
    bad = []
    # A SECOND FINDING WITH A DIFFERENT SUBJECT, never a variable tail on the first. One
    # is a misconfigured clone; this one is a damaged checkout. They have different fixes,
    # so they are different lines.
    _pm = os.path.join(want_abs, "post-merge")
    if not os.path.isfile(_pm):
        bad.append("INV-31: %s/post-merge is missing — the hook path resolves but the "
                   "merge sweep cannot run. Fix: restore it" % _HOOKS_REL)
    elif not os.access(_pm, os.X_OK):
        bad.append("INV-31: %s/post-merge is not executable (mode %o) — the hook path "
                   "resolves but the merge sweep cannot run. Fix: chmod +x it"
                   % (_HOOKS_REL, os.stat(_pm).st_mode & 0o777))
    return bad

def _inv31_hooks_path(root, hp):
    bad = []
    _found_hp = hp.stdout.strip() if hp.returncode == 0 else ""
    _want_abs = os.path.realpath(os.path.join(root, _HOOKS_REL))
    # RESOLVED AND COMPARED AS REAL PATHS, so an ABSOLUTE value naming the same directory
    # passes and a RELATIVE one naming a different directory fails. Comparing the strings
    # would report a working clone as broken and vice versa.
    _found_abs = os.path.realpath(os.path.join(root, _found_hp)) if _found_hp else ""
    if _found_abs != _want_abs:
        _shown = "unset" if not _found_hp else '"%s"' % _found_hp
        bad.append("INV-31: core.hooksPath is %s, not %s — no harness hook runs on this "
                   "clone. Fix: git config core.hooksPath %s"
                   % (_shown, _HOOKS_REL, _HOOKS_REL))
    else:
        bad.extend(_inv31_post_merge(_want_abs))
    return bad

def inv_31(ctx):
    bad, warn = [], []
    H, root, fpath = ctx.H, ctx.root, ctx.fpath

    _hp = ctx.spawn(["git", "config", "--get", "core.hooksPath"],
                    cwd=root, capture_output=True, text=True)
    if _hp is None:
        _hpe = ctx.spawn_error
        # CANNOT RUN IS A VIOLATION, NOT A PASS — the same posture INV-25, INV-26 and INV-29 take
        # for an import failure. An unreadable git config is not evidence the hook is installed.
        bad.append("INV-31 CANNOT RUN: git config could not be read (%s: %s), so an uninstalled "
                   "merge hook would go unreported. Fix: make git runnable in this checkout."
                   % (type(_hpe).__name__, _hpe))
    else:
        bad.extend(_inv31_hooks_path(root, _hp))
    return bad, warn
