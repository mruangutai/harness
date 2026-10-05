"""feature_corpus.py — where feature records live, and which one a checkout is working on.

FEAT-1559 (#1559). Operator ruling, 2026-09-09: "The feature corpus is never materialised inside a
worktree. It remains fully available to the active feature from outside the worktree." Ruling B,
2026-10-04: other features are read from the MAIN CORPUS only — the owner root's ordinary files —
and in-progress features in sibling worktrees are never read.

So this module answers three questions and nothing else:

  * landed population  — which feature directories the owner root holds (`landed_dirs`,
                         `records`), compared by NAME against the structure git tracks there, so a
                         missing directory refuses instead of shrinking the population silently;
  * branch claims      — which landed features claim which branch (`branch_collisions`),
                         computed on demand every call: no index file, no cache (FEAT-58 D-01);
  * active selection   — which feature a checkout is working on and which directories its sparse
                         cone holds (`select`, `derive_cone`).

There is no provider hierarchy, no symlink, and no read of record CONTENT through git: content is
read from ordinary files at the owner root. Git is asked only for STRUCTURE — which directories
are tracked, which branch is checked out.

Every failure to establish the population raises CorpusError, never an empty list: an empty list
is what a fail-open caller reads as "nothing to check".
"""
import os
import re
import subprocess
import sys

_BIN = os.path.dirname(os.path.abspath(__file__))
if _BIN not in sys.path:
    sys.path.insert(0, _BIN)

import harness_boundary  # noqa: E402

# The flow-id form `feature-worktree.py` accepts (its `_ID_RE`); a worktree whose directory
# name does not match it is not a feature worktree.
ID_RE = re.compile(r"^(FEAT|BUG)-[0-9]+[a-z0-9-]*$")
FEATURES_ROOT_RE = re.compile(r"^\.harness/([^/]+)/features$")
PIN_SEPARATOR = "--"
RECORD_FILE = "feature.json"
BRANCH_SENTINELS = frozenset({"", "none"})

# Classes of checkout `select` recognises.
PLAIN_CLONE = "plain-clone"
PROBE = "probe"
PLANNING = "planning-worktree"
PIN = "pin"


class CorpusError(Exception):
    """The population could not be established. Callers turn this into their own established
    refusal (a deny payload, a non-zero exit); none may treat it as an empty corpus."""


# ---------------------------------------------------------------------------------------------
# Structure, from git
# ---------------------------------------------------------------------------------------------

def git(checkout, *args):
    """Run a STRUCTURAL git query in `checkout`; stdout on success, CorpusError otherwise.
    `--no-optional-locks` so a read never refreshes the index behind a verify."""
    try:
        proc = subprocess.run(["git", "--no-optional-locks", *args], cwd=checkout,
                              capture_output=True, text=True)
    except OSError as exc:
        raise CorpusError(f"git {' '.join(args)}: {exc}") from exc
    if proc.returncode != 0:
        raise CorpusError(f"git {' '.join(args)} in {checkout} exited {proc.returncode}: "
                          f"{proc.stderr.strip()}")
    return proc.stdout


def tracked_dirs(checkout, ref="HEAD"):
    """Every directory tracked at `ref`, as sorted repository-relative paths. A repository
    whose HEAD is unborn — no commit yet — tracks nothing and has landed nothing: that is an
    empty structure, not an unreadable one."""
    if ref == "HEAD":
        probe = subprocess.run(["git", "--no-optional-locks", "rev-parse", "-q", "--verify",
                                "HEAD^{commit}"], cwd=checkout, capture_output=True, text=True)
        if probe.returncode == 1 and subprocess.run(
                ["git", "--no-optional-locks", "rev-parse", "--git-dir"], cwd=checkout,
                capture_output=True).returncode == 0:
            return []
    out = git(checkout, "ls-tree", "-d", "-r", "-t", "-z", "--name-only", ref)
    return sorted(p for p in out.split("\0") if p)


def tracks(checkout, rel, ref="HEAD"):
    """Does `ref` track the path `rel`? Structural only."""
    out = git(checkout, "ls-tree", "-z", "--name-only", ref, "--", rel)
    return rel in out.split("\0")


def current_branch(checkout):
    """The checked-out branch's short name, or None when HEAD is detached."""
    try:
        proc = subprocess.run(["git", "symbolic-ref", "-q", "--short", "HEAD"], cwd=checkout,
                              capture_output=True, text=True)
    except OSError as exc:
        raise CorpusError(f"git symbolic-ref: {exc}") from exc
    if proc.returncode == 0:
        return proc.stdout.strip() or None
    if proc.returncode == 1:        # detached HEAD: a fact, not an error
        return None
    raise CorpusError(f"git symbolic-ref in {checkout} exited {proc.returncode}: "
                      f"{proc.stderr.strip()}")


def feature_roots(dirs):
    """The `.harness/<segment>/features` directories among `dirs`, sorted."""
    return sorted(d for d in dirs if FEATURES_ROOT_RE.match(d))


def segments(dirs):
    """Artifact segments: every `<segment>` with a tracked `.harness/<segment>/features`."""
    return [FEATURES_ROOT_RE.match(d).group(1) for d in feature_roots(dirs)]


def expected_feature_dirs(dirs):
    """Feature directories `dirs` tracks, as sorted `<segment>/<id>` names — record-bearing and
    record-less alike, because a directory is the unit of the population, not a feature.json."""
    names = []
    for d in dirs:
        parts = d.split("/")
        if len(parts) == 4 and parts[0] == ".harness" and parts[2] == "features":
            names.append(f"{parts[1]}/{parts[3]}")
    return sorted(names)


# ---------------------------------------------------------------------------------------------
# The landed population, at the owner root
# ---------------------------------------------------------------------------------------------

def owner_root(start):
    """The main checkout `start` belongs to. A linked worktree resolves to its owner; the main
    checkout resolves to itself. Not-a-checkout and an unparseable `.git` pointer both raise."""
    found = harness_boundary.worktree_owner(start)
    if found is None:
        raise CorpusError(f"{start} is not inside a git checkout, so no owner root resolves")
    checkout, owner, _legitimate = found
    if owner is None:
        raise CorpusError(f"{checkout}/.git could not be parsed, so its owner root is unknown")
    if not os.path.isfile(os.path.join(owner, harness_boundary.MARKER)):
        raise CorpusError(f"owner root {owner} has no {harness_boundary.MARKER}, so it is not a "
                          f"harness root")
    return owner


def reached_feature_dirs(root):
    """Feature directories present on disk under `root`, as sorted `<segment>/<id>` names. A root
    with no `.harness` at all reaches none — callers that EXPECT directories compare names and
    refuse the shortfall (`landed_dirs`); an unreadable `.harness` raises."""
    found = []
    harness = os.path.join(root, ".harness")
    try:
        segment_names = sorted(os.listdir(harness))
    except FileNotFoundError:
        return found
    except OSError as exc:
        raise CorpusError(f"{harness}: {exc.strerror or exc}") from exc
    for segment in segment_names:
        features = os.path.join(harness, segment, "features")
        if not os.path.isdir(features):
            continue
        try:
            entries = sorted(os.listdir(features))
        except OSError as exc:
            raise CorpusError(f"{features}: {exc.strerror or exc}") from exc
        found.extend(f"{segment}/{name}" for name in entries
                     if os.path.isdir(os.path.join(features, name)))
    return found


def compare_names(expected, reached):
    """`(missing, unexpected)`: expected names not reached, reached names not expected."""
    expected, reached = set(expected), set(reached)
    return sorted(expected - reached), sorted(reached - expected)


def landed_dirs(owner):
    """`[(segment, id, abs_path)]` for every feature directory the owner root's HEAD tracks.

    A tracked directory missing on disk raises CorpusError naming it: the population this
    returns is either the whole landed corpus or nothing at all. A directory present on disk but
    untracked is not landed and is left out. An owner tracking no feature directory at all — a
    plain clone of a project with no features yet — legitimately returns []."""
    expected = expected_feature_dirs(tracked_dirs(owner))
    missing, _unexpected = compare_names(expected, reached_feature_dirs(owner))
    if missing:
        raise CorpusError(
            f"main corpus at {owner} reaches {len(expected) - len(missing)} of {len(expected)} "
            f"tracked feature directories; missing: {', '.join(missing)}")
    out = []
    for name in expected:
        segment, fid = name.split("/", 1)
        out.append((segment, fid, os.path.join(owner, ".harness", segment, "features", fid)))
    return out


def records(owner):
    """One mapping per landed feature directory: segment, id, path, record (path of its
    feature.json or None), document (parsed mapping or None) and error (why it would not parse,
    or None). A directory without a record stays in the list — the consuming invariant decides
    what a missing record means; this census never erases it."""
    import artifact_accessors

    out = []
    for segment, fid, path in landed_dirs(owner):
        record = os.path.join(path, RECORD_FILE)
        entry = {"segment": segment, "id": fid, "path": path, "record": None,
                 "document": None, "error": None}
        if os.path.isfile(record):
            entry["record"] = record
            try:
                entry["document"] = artifact_accessors.load_feature_json(record)
            except artifact_accessors.FeatureJsonError as exc:
                entry["error"] = str(exc)
        out.append(entry)
    return out


# ---------------------------------------------------------------------------------------------
# Branch claims, computed on demand
# ---------------------------------------------------------------------------------------------

# FEAT-58 D-06 (operator, cycle 3): FEAT-02 and FEAT-03-subissue-mirror both record
# feat/harness-native-foundation. That is what happened — two features shared a foundation branch
# — and both are terminal, so correcting either record would invent a value. The exemption is the
# EXACT id set: a third claimant on that branch still collides, and an empty reason stops the
# entry matching, so it cannot become a habit.
BRANCH_ERA_EXEMPT = {
    frozenset({"FEAT-02", "FEAT-03-subissue-mirror"}):
        "shared foundation branch of the harness-native era; both features are terminal, and "
        "correcting either record would write a branch value that never existed",
}


def branch_claims(entries):
    """`{branch: sorted ids}` over parsed records. Missing, empty and literal `none` branches are
    sentinels and claim nothing."""
    claims = {}
    for entry in entries:
        document = entry.get("document")
        if not isinstance(document, dict):
            continue
        branch = document.get("branch")
        if not isinstance(branch, str) or branch.strip() in BRANCH_SENTINELS:
            continue
        claims.setdefault(branch.strip(), []).append(entry["id"])
    return {branch: sorted(ids) for branch, ids in claims.items()}


def branch_collisions(entries, exempt=None):
    """`[(branch, ids)]` for every branch claimed by more than one feature, sorted by branch,
    except an exact exempt id set whose reason is non-empty."""
    exempt = BRANCH_ERA_EXEMPT if exempt is None else exempt
    out = []
    for branch, ids in sorted(branch_claims(entries).items()):
        if len(ids) < 2:
            continue
        reason = exempt.get(frozenset(ids))
        if isinstance(reason, str) and reason.strip():
            continue
        out.append((branch, ids))
    return out


# ---------------------------------------------------------------------------------------------
# Active selection: which feature a checkout works on, and its sparse cone
# ---------------------------------------------------------------------------------------------

def parse_pin(name):
    """`<feature>--<run-id>--<persona>` (pinned-checkout.py `_pin_name`) → feature id, or None
    when the name is not exactly that shape around a flow id."""
    parts = name.split(PIN_SEPARATOR)
    if len(parts) != 3 or not all(parts) or not ID_RE.match(parts[0]):
        return None
    return parts[0]


def identity(kind, name, branch):
    """The active id a checkout's IDENTITY names, as `(id, refusal)`.

    A pin is named by its directory alone. A planning worktree is named by its directory id and
    by a `feat/<id>` branch; when both name an id they must agree. `(None, None)` means the
    checkout names no feature at all — an arbitrary worktree, a no-op subject."""
    if kind == PIN:
        fid = parse_pin(name)
        if fid is None:
            return None, (f"pin directory {name!r} is not <feature>--<run-id>--<persona> "
                          f"around a flow id, so its active feature cannot be derived")
        return fid, None
    by_name = name if ID_RE.match(name) else None
    by_branch = None
    if branch and branch.startswith("feat/") and ID_RE.match(branch[len("feat/"):]):
        by_branch = branch[len("feat/"):]
    if by_name and by_branch and by_name != by_branch:
        return None, (f"directory names {by_name} but branch {branch} names {by_branch}; "
                      f"the active feature is ambiguous")
    return by_name or by_branch, None


def claiming_segments(fid, dirs, roots):
    """Segments holding a `.harness/<segment>/features/<fid>` directory — tracked in `dirs`, or
    present on disk under any of `roots` (the checkout, the owner)."""
    found = set()
    for d in dirs:
        parts = d.split("/")
        if len(parts) == 4 and parts[0] == ".harness" and parts[2] == "features" \
                and parts[3] == fid:
            found.add(parts[1])
    for root in roots:
        harness = os.path.join(root, ".harness")
        if not os.path.isdir(harness):
            continue
        for segment in os.listdir(harness):
            if os.path.isdir(os.path.join(harness, segment, "features", fid)):
                found.add(segment)
    return sorted(found)


def _related(d, roots):
    return any(d == r or d.startswith(r + "/") or r.startswith(d + "/") for r in roots)


def derive_cone(dirs, active):
    """The sparse cone: directories only, derived — never a literal list (FEAT-58 D-08).

      (a) every top-level tracked directory except `.harness`;
      (b) every MAXIMAL tracked directory under `.harness` disjoint from every
          `.harness/<segment>/features` — neither it, beneath it, nor above it;
      (c) the active feature's directory paths.

    Files directly in `.harness` and `.harness/<segment>` need no entry: cone mode materialises
    the files held directly by every ancestor of a listed directory."""
    roots = feature_roots(dirs)
    top = {d for d in dirs if "/" not in d and d != ".harness"}
    under = [d for d in dirs if d.startswith(".harness/") and not _related(d, roots)]
    kept = set(under)
    maximal = {d for d in under if not any(p in kept for p in _ancestors(d))}
    return sorted(top | maximal | set(active))


def _ancestors(path):
    parts = path.split("/")
    return ["/".join(parts[:i]) for i in range(1, len(parts))]


def in_cone(path, cone):
    """Does cone mode materialise the FILE `path` for this cone? Top-level files always; a file
    under a listed directory; a file directly inside any ancestor of a listed directory."""
    parent = os.path.dirname(path)
    if not parent:
        return True
    for entry in cone:
        if path.startswith(entry + "/"):
            return True
        if entry.startswith(parent + "/"):
            return True
    return False


def active_paths(fid, dirs, roots):
    """`(paths, artifact_segment, refusal, every_segment)` for the active feature's cone entries.

    An existing record selects its exact segment — never the worktree's own segment, which for a
    fleet planning worktree differs. An id no segment holds yet (a worktree cut before its record
    is written) is included in EVERY segment, so the record lands inside the cone wherever it is
    created. More than one claiming segment refuses. `every_segment` is that all-segment form,
    returned in both cases: once the record exists, a cone still in that form hides exactly what
    the exact form hides, so a caller may accept it as converged."""
    claims = claiming_segments(fid, dirs, roots)
    known = set(segments(dirs))
    for root in roots:
        harness = os.path.join(root, ".harness")
        if os.path.isdir(harness):
            known.update(s for s in os.listdir(harness)
                         if os.path.isdir(os.path.join(harness, s, "features")))
    every = [f".harness/{s}/features/{fid}" for s in sorted(known)]
    if len(claims) > 1:
        return [], None, (f"{fid} is claimed by segments {', '.join(claims)}; the active "
                          f"record's segment is ambiguous"), every
    if claims:
        return [f".harness/{claims[0]}/features/{fid}"], claims[0], None, every
    return every, None, None, every


def select(checkout):
    """What `checkout` is, and — when it bears records — its active feature and target cone.

    Returns a mapping: checkout, owner, checkout_class, active_feature, artifact_segment,
    active_paths, cone, pre_record (the every-segment form of the active entries and its cone —
    what a worktree cut before its record was written still holds), noop (a reason string when
    the checkout is not record-bearing, else None) and refusal (a reason string when identity or
    segment is ambiguous, else None)."""
    found = harness_boundary.worktree_owner(checkout)
    if found is None:
        raise CorpusError(f"{checkout} is not inside a git checkout")
    top, owner, legitimate = found
    if owner is None:
        raise CorpusError(f"{top}/.git could not be parsed, so its owner root is unknown")
    out = {"checkout": top, "owner": owner, "checkout_class": None, "active_feature": None,
           "artifact_segment": None, "active_paths": [], "cone": [],
           "pre_record": {"active_paths": [], "cone": []}, "noop": None, "refusal": None}
    if top == owner:
        out.update(checkout_class=PLAIN_CLONE,
                   noop="not a linked worktree; a plain clone keeps the full corpus")
        return out
    rel = os.path.relpath(top, os.path.join(owner, harness_boundary.WORKTREES_SEGMENT))
    parts = rel.split(os.sep)
    if not legitimate or len(parts) != 2:
        out.update(checkout_class=PROBE,
                   noop=f"linked worktree outside {harness_boundary.WORKTREES_SEGMENT}/<segment>/"
                        f"<id>; not record-bearing")
        return out
    kind = PIN if parts[0] == harness_boundary.PINS_SEGMENT else PLANNING
    out["checkout_class"] = kind
    if not tracks(top, harness_boundary.MARKER.replace(os.sep, "/")):
        out.update(checkout_class=PROBE,
                   noop=f"HEAD does not track {harness_boundary.MARKER}; a code-only checkout")
        return out
    fid, refusal = identity(kind, parts[1], current_branch(top) if kind == PLANNING else None)
    if refusal:
        out["refusal"] = refusal
        return out
    if fid is None:
        out.update(checkout_class=PROBE,
                   noop=f"{parts[1]!r} names no feature; an arbitrary worktree is not "
                        f"record-bearing")
        return out
    dirs = tracked_dirs(top)
    paths, segment, refusal, every = active_paths(fid, dirs, [top, owner])
    out.update(active_feature=fid, artifact_segment=segment, active_paths=paths)
    if refusal:
        out["refusal"] = refusal
        return out
    out["cone"] = derive_cone(dirs, paths)
    out["pre_record"] = {"active_paths": every, "cone": derive_cone(dirs, every)}
    return out
