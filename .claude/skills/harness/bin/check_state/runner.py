"""Row selection, the repo and feature passes, collation, reporting and the CLI. (FEAT-69)"""
import os, re, sys
from check_state.ctx import Ctx
from check_state.table import INVARIANTS, RETIRED
_INV_NAME = re.compile(r"^(?:INV-\d+|[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)$")


def _rows():
    return [row for group in INVARIANTS for row in group.rows]


def _list_rows():
    for group in INVARIANTS:
        for row in group.rows:
            print(f"{row.name:9} {row.scope:8} {' '.join(row.reads)}")
            print(f"{'':9} {row.authority:8} {row.contract}")
    for name, why in RETIRED.items():
        print(f"{name:9} retired  {why}")


def _select_names(only):
    """The row names --only selects, or a (message, exit) refusal."""
    names = [n.strip() for n in only.split(",") if n.strip()]
    active = {row.name for row in _rows()}
    for n in names:
        if n in RETIRED:
            print(f"check-state.py: {n} is retired — {RETIRED[n]}. Nothing runs for it.")
            return None, 0
        if n not in active:
            print(f"check-state.py: no invariant named {n!r}; run --list to see the table.",
                  file=sys.stderr)
            return None, 2
    return set(names), None


# --- --changed: the join between dirty paths and declared reads --------------------------------
_FEATURE_IN_PATH = re.compile(r"^\.harness/[^/]+/features/([^/]+)(?:/|$)")


def _dirty_toplevel(ctx):
    """The real path of root's work-tree top (the context's ONE rev-parse), or of root itself
    when git cannot say."""
    return os.path.realpath(ctx.git_top if ctx.git_top else ctx.root)


def _dirty_records(fields):
    """The paths named by a `status --porcelain=v1 -z` record stream, both sides of a rename."""
    paths, i = [], 0
    while i < len(fields):
        entry = fields[i]
        i += 1
        if len(entry) < 4:
            continue
        code, p = entry[:2], entry[3:]
        paths.append(p)
        if code[0] in "RC" and i < len(fields):
            # A rename record is followed by the ORIGINAL path in its own field; both sides count.
            paths.append(fields[i])
            i += 1
    return paths


def _dirty_paths(ctx):
    """Repo-relative POSIX paths of every dirty, staged, untracked or renamed file, or None
    when git cannot answer (no work tree)."""
    root = ctx.root
    r = ctx.spawn(["git", "-C", root, "status", "--porcelain=v1", "-z", "--untracked-files=all"],
                  capture_output=True)
    if r is None or r.returncode != 0:
        return None
    top = _dirty_toplevel(ctx)
    real_root = os.path.realpath(root)
    paths = _dirty_records(r.stdout.decode("utf-8", errors="replace").split("\0"))
    out = []
    for p in paths:
        absolute = os.path.join(top, p)
        rel = os.path.relpath(absolute, real_root).replace(os.sep, "/")
        if not rel.startswith("../"):
            out.append(rel)
    return out


def _path_changed(p, pat):
    """True when dirty path `p` matches the `path:` pattern `pat` or lies beneath it."""
    from fnmatch import fnmatchcase
    return fnmatchcase(p, pat) or p.startswith(pat.rstrip("*") + "/")


def _pattern_changed(pat, dirty, feats):
    """(hit, everywhere) of one `path:` pattern against the dirty paths; the features the
    matching paths belong to are added to `feats`, a path outside the feature tree sets
    `everywhere`."""
    hit = everywhere = False
    for p in dirty:
        if _path_changed(p, pat):
            hit = True
            m = _FEATURE_IN_PATH.match(p)
            if m:
                feats.add(m.group(1))
            else:
                everywhere = True
    return hit, everywhere


def _row_changed(row, dirty):
    """(hit, feats, everywhere) of one row against the dirty paths: whether any declared read
    is touched, the features whose paths touched it, and whether an input no path can map
    makes it run for every feature."""
    feats, everywhere, hit = set(), False, False
    for r in row.reads:
        if not r.startswith("path:"):
            hit = everywhere = True      # git:/gh: inputs cannot be mapped to a path
            continue
        pat = r[len("path:"):]
        h, e = _pattern_changed(pat, dirty, feats)
        hit = hit or h
        everywhere = everywhere or e
    return hit, feats, everywhere


def _changed_selection(ctx):
    """{row name: feature names or None} selected by the dirty tree, or None when the tree
    cannot be read -- which runs EVERYTHING, the conservative direction. A row selected
    through a `path:` declaration is narrowed to the features those paths belong to; a row
    selected through an input no path can map (`git:`, `gh:`, a path outside the feature
    tree) runs for every feature."""
    dirty = _dirty_paths(ctx)
    if dirty is None:
        return None
    selection = {}
    for row in _rows():
        hit, feats, everywhere = _row_changed(row, dirty)
        if hit:
            selection[row.name] = None if everywhere else feats
    return selection


def _parse_valued(argv, i):
    """(flag, value, tokens consumed) when argv[i] is `--only`/`--feature` with its value in
    the next token or after `=`, else None. A flag missing its value stops the run."""
    a = argv[i]
    if a in ("--only", "--feature"):
        if i + 1 >= len(argv):
            print(f"check-state.py: {a} needs a value", file=sys.stderr)
            sys.exit(2)
        return a, argv[i + 1], 2
    if a.startswith("--only=") or a.startswith("--feature="):
        k, v = a.split("=", 1)
        return k, v, 1
    return None


def _parse_args(argv):
    """The four verbs. Everything the baseline ignored (stray user arguments) is still ignored:
    only the flags below are read."""
    values = {"--only": None, "--feature": None}
    list_mode = changed = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--list":
            list_mode = True
        elif a == "--changed":
            changed = True
        else:
            valued = _parse_valued(argv, i)
            if valued is not None:
                k, v, n = valued
                values[k] = v
                i += n - 1
        i += 1
    return values["--only"], values["--feature"], list_mode, changed


def _table_repo_pass(ctx, rows):
    """(bad, warn) of one group's repo-scoped rows, in table order."""
    bad, warn = [], []
    for row in [r for r in rows if r.scope == "repo"]:
        b, w = row.run(ctx)
        bad.extend(b)
        warn.extend(w)
    return bad, warn


def _table_rows_for(feat_rows, feat, selection):
    """The feature-scoped rows the selection runs for `feat`."""
    return [r for r in feat_rows
            if selection is None or selection[r.name] is None or feat in selection[r.name]]


def _table_collate(ctx, group, feat, results):
    """(bad, warn) of one feature's row results, collated when the group asks for it."""
    if group.collate is not None:
        return group.collate(ctx, feat, results)
    return ([x for res in results for x in res[0]],
            [x for res in results for x in res[1]])


def _table_feature_pass(ctx, group, rows, selection):
    """(bad, warn) of one group's feature-scoped rows, `for feature: for row`."""
    feat_rows = [r for r in rows if r.scope == "feature"]
    if not feat_rows:
        return [], []
    bad, warn = [], []
    for feat in ctx.features:
        feat_rows_here = _table_rows_for(feat_rows, feat, selection)
        if not feat_rows_here:
            continue
        results = [row.run(ctx, feat) for row in feat_rows_here]
        b, w = _table_collate(ctx, group, feat, results)
        bad.extend(b)
        warn.extend(w)
    return bad, warn


def run_table(ctx, selection=None):
    """Every selected row, in table order: `for group: for feature: for row`. `selection`
    maps a row name to the feature names it runs for (None: every feature in ctx.features);
    a None selection runs the whole table."""
    bad, warn = list(ctx.bad), list(ctx.warn)
    for group in INVARIANTS:
        rows = [r for r in group.rows if selection is None or r.name in selection]
        if not rows:
            continue
        b, w = _table_repo_pass(ctx, rows)
        bad.extend(b)
        warn.extend(w)
        b, w = _table_feature_pass(ctx, group, rows, selection)
        bad.extend(b)
        warn.extend(w)
    return bad, warn


def _main_list():
    """`--list`: print the table, tolerant of a closed pipe."""
    try:
        _list_rows()
    except BrokenPipeError:
        pass
    return 0


def _main_changed(ctx, selection):
    """`--changed` narrowing of `selection`: (selection, None) to run it, or (None, 0) when
    nothing selected reads anything that changed."""
    changed_sel = _changed_selection(ctx)
    if changed_sel is None:
        return selection, None
    if selection is None:
        selection = changed_sel
    else:
        selection = {n: f for n, f in changed_sel.items() if n in selection}
    if not selection:
        return None, 0            # nothing selected reads anything that changed: silent
    return selection, None


def _main_selection(ctx, only, changed):
    """The row selection `--only`/`--changed` ask for: (selection, None) to run it, or
    (None, exit status) when the run stops here."""
    selection = None
    if only is not None:
        names, code = _select_names(only)
        if names is None:
            return None, code
        selection = {n: None for n in names}
    if changed:
        return _main_changed(ctx, selection)
    return selection, None


def _main_report(bad, warn, changed):
    """Print the findings and return the exit status."""
    if changed and not bad and not warn:
        return 0                    # a clean selective run is SILENT: hooks forward only rows
    for m in bad:  print(f"  VIOLATION  {m}")
    for m in warn: print(f"  note       {m}")
    if not bad and not warn:
        print("  all state invariants hold.")
    return 1 if bad else 0


def main(root, argv):
    H = os.path.join(root, ".harness")
    only, feature, list_mode, changed = _parse_args(argv)
    if list_mode:
        return _main_list()
    if not os.path.isdir(H):
        print("harness: no .harness/ here — this clone is not an onboarded harness control plane. Run /harness-init in the control-plane clone.")
        return 1
    keep = None if feature is None else {feature}
    # The context is built BEFORE the selection is resolved (FEAT-63 T-01): `--changed` reads
    # the dirty tree through the context's one process boundary and its one git top level.
    # Building it prints nothing, so a selector error still exits before any finding.
    ctx = Ctx(root, keep=keep)
    selection, code = _main_selection(ctx, only, changed)
    if code is not None:
        return code
    bad, warn = run_table(ctx, selection)
    return _main_report(bad, warn, changed)
