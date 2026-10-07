"""Layout preflight, audit subject, and INV-52 branch claims. (FEAT-1559, #1559)

THE PREFLIGHT RUNS BEFORE THE CONTEXT IS BUILT, so a checkout whose view of the tree is not the
tree is refused before a single invariant judges it. In a record-bearing linked worktree it
calls `worktree-state.py --verify --json` — never `--repair`; the hook tier is repair's only
caller — and reads EVERY finding the report carries:

  cone 3, skip-bits 4, materialisation 7   refuse, naming the break and the repair command;
  dirty 8                                   a note, and the audit runs: a dirty tree is the
                                            ordinary mid-task state, and refusing on it would
                                            refuse ahead of the very commit that clears it.

A structural finding refuses even when the report's own exit is 8: dirty outranks the structural
codes in the exit, so a caller that read only the exit would let a broken cone through.

THE SUBJECT IS SETTLED HERE TOO. A record-bearing worktree audits its one active feature by
default; `--feature` must name a feature directory present in this checkout. A plain clone
with no selector audits every feature it holds, as before. Then expected feature-directory NAMES
are compared with the names on disk — record-less directories included — and a missing expected
name refuses before any invariant runs, because an audit over a smaller population than it was
meant to see is the silent shrink this feature exists to stop.
"""
import feature_corpus
import harness_boundary


class Preflight:
    """What the runner needs before it builds the context: the subject (`keep`), whether this
    is a sparse record-bearing worktree (`scoped`) with its `active` feature and `owner` root,
    notes to carry into the report, and the refusal lines that stop the run (empty: proceed)."""

    def __init__(self):
        self.keep = None
        self.scoped = False
        self.active = None
        self.owner = None
        self.notes = []
        self.refusal = []


# --- pure diagnostics (unit-tested) ---------------------------------------------------------

def name_set_findings(expected, reached, remedy):
    """`(refusal, notes)` comparing expected and reached `<segment>/<id>` names. Missing
    expected names refuse with N of M and the sorted shortfall; unexpected-only names are a
    note, never a refusal."""
    missing, unexpected = feature_corpus.compare_names(expected, reached)
    refusal, notes = [], []
    if missing:
        refusal.append(
            f"FEATURE SET: this checkout reaches {len(expected) - len(missing)} of "
            f"{len(expected)} expected feature directories — missing: {', '.join(missing)}"
            + (f"; unexpected: {', '.join(unexpected)}" if unexpected else "")
            + f". No invariant ran: an audit over fewer features than expected would report "
            f"clean about the ones it never saw. {remedy}")
    elif unexpected:
        notes.append(f"FEATURE SET: {len(unexpected)} feature director(y/ies) on disk that "
                     f"HEAD does not track: {', '.join(unexpected)} (not gating).")
    return refusal, notes


def subject_refusal(feature, local_names):
    """A refusal line when an explicit `--feature` names no feature directory in this checkout,
    else None — a narrowed audit over nothing would print 'all invariants hold'."""
    if feature is None:
        return None
    if feature in {name.split("/", 1)[1] for name in local_names}:
        return None
    return (f"--feature {feature} names no feature directory in this checkout, so there is "
            f"nothing to audit. Feature directories here: "
            f"{', '.join(sorted(local_names)) or 'none'}.")


# --- the preflight ----------------------------------------------------------------------------

def _layout(pre, root, bin_dir):
    """Verify a record-bearing linked worktree; fill `pre`. Returns the selection (or None)."""
    doc, error = feature_corpus.verify_layout(root, bin_dir)
    if error is None:
        structural, dirty, error = feature_corpus.verify_report_findings(doc)
    if error is not None:
        pre.refusal.append(f"LAYOUT: {error}. The audit refuses rather than judging a tree it "
                           f"cannot see.")
        return None
    if doc.get("noop"):
        return None
    repair = (f"python3 .claude/skills/harness/bin/worktree-state.py --repair --checkout "
              f"{doc.get('checkout', root)}")
    for f in structural:
        shown = ", ".join(f.get("paths", [])[:6])
        pre.refusal.append(f"LAYOUT {f['label']} ({f['code']}): {f.get('detail', '')}"
                           + (f" [{shown}]" if shown else ""))
    if structural:
        pre.refusal.append(f"LAYOUT: no invariant ran — this checkout's view of the tree is not "
                           f"the tree. Repair: {repair}")
    if dirty is not None:
        pre.notes.append(f"LAYOUT dirty (8): {dirty.get('detail', '')} — reported, not gating; "
                         f"repair runs once the work is committed or stashed.")
    return doc


def preflight(root, feature, bin_dir):
    """Settle the audit's subject and refuse a broken layout, before any invariant runs."""
    pre = Preflight()
    found = harness_boundary.worktree_owner(root)
    local = feature_corpus.reached_feature_dirs(root)
    doc = None
    if found is not None and found[1] is not None and found[0] != found[1]:
        doc = _layout(pre, root, bin_dir)
        if pre.refusal:
            return pre
    if doc is not None:
        pre.scoped, pre.active, pre.owner = True, doc.get("active_feature"), found[1]
        pre.keep = {feature} if feature is not None else {pre.active}
    elif feature is not None:
        pre.keep = {feature}
    refusal = subject_refusal(feature, local)
    if refusal:
        pre.refusal.append(refusal)
        return pre
    # Expected names: in a sparse worktree, the active directory wherever HEAD tracks it; in a
    # plain clone, every directory HEAD tracks. Outside git there is no structure to compare.
    if found is None:
        return pre
    try:
        tracked = feature_corpus.expected_feature_dirs(feature_corpus.tracked_dirs(root))
    except feature_corpus.CorpusError:
        return pre                  # no commit yet: nothing is tracked, nothing can be missing
    if pre.scoped:
        expected = [n for n in tracked if n.split("/", 1)[1] == pre.active]
        reached = [n for n in local if n.split("/", 1)[1] == pre.active]
    else:
        expected, reached = tracked, local
    remedy = ("Restore the directory (`git checkout -- <path>`) or, in a linked worktree, run "
              "worktree-state.py --repair.")
    refusal, notes = name_set_findings(expected, reached, remedy)
    pre.refusal.extend(refusal)
    pre.notes.extend(notes)
    return pre


# --- INV-52 -----------------------------------------------------------------------------------

def inv_52(ctx):
    """INV-52: no two LANDED features claim one branch, read from the main corpus on demand —
    a sparse checkout's one local record cannot see a collision between two others. No git work
    tree is a state this cannot speak to (INV-33's silence); every other failure to establish
    the population is reported, never read as 'no collision'."""
    bad, warn = [], []
    if ctx.git_top is None:
        return bad, warn
    try:
        owner = ctx.owner or feature_corpus.owner_root(ctx.root)
        entries = feature_corpus.records(owner)
    except feature_corpus.CorpusError as exc:
        bad.append(f"INV-52 CANNOT VERIFY branch claims: {exc}. A population that could not be "
                   f"read is not one without collisions.")
        return bad, warn
    for branch, ids in feature_corpus.branch_collisions(entries):
        bad.append(f"INV-52: branch {branch} is claimed by {len(ids)} landed features "
                   f"({', '.join(ids)}); merge-gate cannot tell which one a merge of it ships. "
                   f"Give each feature its own branch.")
    return bad, warn
