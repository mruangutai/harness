"""worktree_terminal.py — the shared eligibility predicate over standing worktrees (FEAT-34 T-01).

A library with NO SIDE EFFECTS and NO ARGV HANDLING. It is imported by check-state.sh's INV-29
and by post-merge-sweep.sh; nothing else may duplicate this logic (D-02) — one predicate the gate
and the hook cross, so they can never disagree about what is eligible.

Public surface, and nothing wider: `CLASSES`, `classify(root)` and `classify_all(root)` (D-10).
`classify` covers ONE repository at `root`; `classify_all` is the cross-repository entry point
check-state.sh's INV-29 calls — it returns `classify(root)` for the harness checkout plus
`classify(owner_root)` for every repository declared in fleet.yaml. Everything else here is
implementation detail that stays private.
"""
import importlib.util
import json
import os
import subprocess
import sys

CLASSES = ("terminal", "exempt_absent", "unresolved")

_BIN_DIR = os.path.dirname(os.path.abspath(__file__))


def _import_harness_boundary():
    if _BIN_DIR not in sys.path:
        sys.path.insert(0, _BIN_DIR)
    import harness_boundary
    return harness_boundary


def _import_factory_config():
    if _BIN_DIR not in sys.path:
        sys.path.insert(0, _BIN_DIR)
    import factory_config
    return factory_config


def _import_feature_worktree():
    # The filename has a hyphen, so a plain `import` cannot reach it — loaded by path instead,
    # per T-01's intent, rather than re-deriving resolve_repo's logic here.
    path = os.path.join(_BIN_DIR, "feature-worktree.py")
    spec = importlib.util.spec_from_file_location("_worktree_terminal_feature_worktree", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_git(args, cwd, timeout=None):
    try:
        return subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                               timeout=timeout)
    except Exception:
        return None


def _worktree_list_raw(root):
    """Run `git worktree list --porcelain` with cwd=root, timeout 10. Returns (ok, stdout).
    `ok` is False when the subprocess could not be run, timed out, returned non-zero, or
    produced no output (git worktree list always reports at least the main checkout, so empty
    output signals a failure too). This is the PRIVATE enumeration-success signal classify_all
    needs to tell "enumeration failed" apart from "enumerated, found nothing" — classify()'s own
    public return shape never exposes it; that shape is fixed by T-02's nineteen green cases."""
    try:
        r = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root,
                            capture_output=True, text=True, timeout=10)
    except Exception:
        return False, ""
    if r.returncode != 0 or not r.stdout:
        return False, ""
    return True, r.stdout


def _worktree_paths(root):
    """Enumerate worktrees of the repository at `root`. Reuses the exact parsing shape
    check-state.sh already uses at :1117-:1135 — blank-line separated porcelain records,
    `worktree <path>` opens each — rather than a second parser."""
    ok, stdout = _worktree_list_raw(root)
    if not ok:
        return []
    paths = []
    for rec in stdout.split("\n\n"):
        path = None
        for line in rec.splitlines():
            if line.startswith("worktree "):
                path = line[len("worktree "):].strip()
        if path:
            paths.append(path)
    return paths


def _split_owner_segment_id(path, worktrees_segment):
    """Split an absolute worktree path into (owner_root, repo_segment, worktree_id) per
    DEC-193's <owner_root>/<WORKTREES_SEGMENT>/<repo>/<id> shape. None if `path` is not under
    WORKTREES_SEGMENT at all."""
    marker = os.sep + worktrees_segment.replace("/", os.sep) + os.sep
    idx = path.find(marker)
    if idx == -1:
        return None
    owner_root = path[:idx]
    rest = path[idx + len(marker):]
    parts = [p for p in rest.split(os.sep) if p]
    if len(parts) < 2:
        return None
    return owner_root, parts[0], parts[1]


def _repo_arg_for_segment(repo_segment, factory_config):
    """The `--repo` string feature-worktree.py's resolve_repo accepts for a worktree's repo
    segment — "harness" (the literal segment feature-worktree.py itself uses), or the
    owner/repo fleet.yaml name whose trailing segment matches. None if no repo matches.

    Matched by SEGMENT NAME, never by comparing owner_root against the resolved harness root.
    That comparison is the CWD trap: the root resolver derives from the calling script's own
    file location, so when this module is imported from a worktree's own copy it resolves to
    that worktree, not the main checkout, and would never match a real worktree's true
    owner_root. Segment matching sidesteps it — and resolve_repo's own default_branch
    never depends on owner_root being correct: "harness" hardcodes "main", and the fleet case
    reads default_branch straight from the fleet entry."""
    if repo_segment == "harness":
        return "harness"
    try:
        fleet = factory_config.load_fleet()
    except Exception:
        return None
    for entry in fleet.get("repos", []):
        name = entry.get("name")
        if name and name.split("/", 1)[-1] == repo_segment:
            return name
    return None


def _resolve_default_branch(repo_segment, feature_worktree_mod, factory_config):
    """The repository's default_branch, via feature-worktree.py's own resolve_repo — never
    re-derived here. None on any failure to resolve."""
    repo_arg = _repo_arg_for_segment(repo_segment, factory_config)
    if repo_arg is None:
        return None
    try:
        _owner_root, _segment, default_branch = feature_worktree_mod.resolve_repo(repo_arg)
    except SystemExit:
        return None
    except Exception:
        return None
    return default_branch


def _landed_dir_names(owner_root, default_branch, features_rel):
    """Names present in the default branch's features directory. None if the `git ls-tree`
    lookup itself errored — that failure is never folded into "absent"."""
    r = _run_git(["ls-tree", "--name-only", f"{default_branch}:{features_rel}"], owner_root)
    if r is None or r.returncode != 0:
        return None
    return [line for line in r.stdout.splitlines() if line]


def _read_landed_feature_json(owner_root, default_branch, feature_json_rel):
    """The LANDED copy of feature.json: git rev-parse <default_branch>:<rel> then git cat-file,
    exactly as feature-worktree.py:287 reads a landed blob. Never the working tree's copy.
    Returns (data, error) — error is None only on a successfully parsed dict."""
    r = _run_git(["rev-parse", f"{default_branch}:{feature_json_rel}"], owner_root)
    if r is None or r.returncode != 0:
        return None, "missing"
    blob = r.stdout.strip()
    if not blob:
        return None, "missing"
    c = _run_git(["cat-file", "blob", blob], owner_root)
    if c is None or c.returncode != 0:
        return None, "unreadable"
    try:
        data = json.loads(c.stdout)
    except Exception:
        return None, "unparseable"
    if not isinstance(data, dict):
        return None, "unparseable"
    return data, None


def _is_dirty(worktree_path):
    r = _run_git(["status", "--porcelain"], worktree_path)
    if r is None or r.returncode != 0:
        return False
    return bool(r.stdout.strip())


def classify(root):
    """Classify every standing worktree of the repository at `root`. See the module docstring
    and FEAT-34 T-01's intent for the full contract."""
    hb = _import_harness_boundary()
    factory_config = _import_factory_config()
    feature_worktree_mod = _import_feature_worktree()

    records = []

    # The first porcelain entry is always the main checkout, even when `root` is itself a
    # linked worktree — a repository with no linked worktrees returns itself, so the
    # derivation is total (check-state.sh:1138-1143, INV-25's precedent). Skipping it by
    # comparing realpath(path) against realpath(root) is WRONG when root IS a linked
    # worktree: the main checkout still appears in the porcelain output and would never be
    # skipped, so it would be misclassified as an unresolved linked worktree instead. Index
    # 0 plays two roles that must not be fused — it is skipped as the main checkout here, and
    # it is what makes `root` itself become a genuine classified record when root is a linked
    # worktree, which is correct and required (D-10/T-01 rework).
    for i, path in enumerate(_worktree_paths(root)):
        if i == 0:
            continue  # the main checkout, never a linked worktree

        dirty = _is_dirty(path)

        split = _split_owner_segment_id(path, hb.WORKTREES_SEGMENT)
        if split is None:
            records.append({
                "path": path, "feature_id": None, "klass": "unresolved", "dirty": dirty,
                "reason": "worktree path is not under WORKTREES_SEGMENT", "repo": None,
            })
            continue
        owner_root, repo_segment, wt_id = split

        default_branch = _resolve_default_branch(repo_segment, feature_worktree_mod, factory_config)
        if default_branch is None:
            records.append({
                "path": path, "feature_id": wt_id, "klass": "unresolved", "dirty": dirty,
                "reason": "could not resolve the repository's default_branch",
                "repo": repo_segment,
            })
            continue

        features_rel = os.path.join(".harness", repo_segment, "features")
        names = _landed_dir_names(owner_root, default_branch, features_rel)
        if names is None:
            records.append({
                "path": path, "feature_id": wt_id, "klass": "unresolved", "dirty": dirty,
                "reason": "git ls-tree of the landed features directory errored",
                "repo": repo_segment,
            })
            continue

        exact = wt_id in names
        prefix_matches = [n for n in names if n.startswith(wt_id)]

        if not exact and not prefix_matches:
            records.append({
                "path": path, "feature_id": None, "klass": "exempt_absent", "dirty": dirty,
                "reason": f"{wt_id} is absent from {default_branch}'s features directory",
                "repo": repo_segment,
            })
            continue

        if exact:
            resolved_id = wt_id
        elif len(prefix_matches) == 1:
            resolved_id = prefix_matches[0]
        else:
            records.append({
                "path": path, "feature_id": wt_id, "klass": "unresolved", "dirty": dirty,
                "reason": (f"{wt_id} is an ambiguous prefix of {len(prefix_matches)} landed "
                           f"feature directories"),
                "repo": repo_segment,
            })
            continue

        feature_json_rel = os.path.join(features_rel, resolved_id, "feature.json")
        data, err = _read_landed_feature_json(owner_root, default_branch, feature_json_rel)
        if err is not None:
            records.append({
                "path": path, "feature_id": resolved_id, "klass": "unresolved", "dirty": dirty,
                "reason": f"landed feature.json for {resolved_id} is {err}",
                "repo": repo_segment,
            })
            continue

        status = data.get("status")
        if status == "Done":
            records.append({
                "path": path, "feature_id": resolved_id, "klass": "terminal", "dirty": dirty,
                "reason": f"landed status is Done on {default_branch}",
                "repo": repo_segment,
            })
        # else: the lookup resolved and the landed status is anything else -> omitted entirely.

    records.sort(key=lambda r: r["path"])
    return records


def classify_all(root):
    """Cross-repository entry point, D-10. THIS is what REQ-04 needs and classify(root) cannot
    give it: classify runs ONE `git worktree list` with cwd=root, and feature-worktree.py's
    dest_for joins WORKTREES_SEGMENT only to a resolved owner_root, so a served repository's
    worktrees live inside a DIFFERENT git repository that a git worktree list in the harness
    checkout can never report. classify_all is the only function check-state.sh's INV-29 calls.

    Returns classify(root) for the harness checkout, plus classify(owner_root) for every
    repository declared in fleet.yaml, one combined list sorted by path. See the module
    docstring and FEAT-34 T-01's intent (D-10 a-e) for the full three-way failure posture:
    fleet.yaml failing to load is ONE blocking repository-level "unresolved" record, ALONGSIDE
    the harness's own records (never swallowed, never a harness-only return); a declared
    repository whose checkout directory is absent emits nothing (decidable, not unknown); a
    declared repository whose checkout exists but cannot be enumerated emits ONE
    repository-level "unresolved" record.

    `root` is the checkout actually being graded, which may itself be a worktree. Never
    substitute the resolved harness root for it — the CWD trap this module already
    documents at _repo_arg_for_segment applies here too.
    """
    factory_config = _import_factory_config()

    records = list(classify(root))

    try:
        fleet = factory_config.load_fleet()
    except Exception as exc:
        records.append({
            "path": factory_config.FLEET_PATH, "feature_id": None, "klass": "unresolved",
            "dirty": False, "reason": f"fleet.yaml failed to load: {exc}", "repo": None,
        })
        records.sort(key=lambda r: r["path"])
        return records

    for entry in fleet.get("repos", []):
        name = entry.get("name")
        owner_root = factory_config.workspace_path(fleet, name)

        if not os.path.isdir(owner_root):
            # Absent checkout -> emit nothing for this repo. Decidable, not unknown: a
            # directory that does not exist holds no worktrees. One rule for every declared
            # repo, not the per-repository exception REQ-04 forbids.
            continue

        ok, _stdout = _worktree_list_raw(owner_root)
        if not ok:
            repo_segment = name.split("/", 1)[-1] if name else None
            records.append({
                "path": owner_root, "feature_id": None, "klass": "unresolved", "dirty": False,
                "reason": "git worktree list could not be run or failed for this repository",
                "repo": repo_segment,
            })
            continue

        records.extend(classify(owner_root))

    records.sort(key=lambda r: r["path"])
    return records
