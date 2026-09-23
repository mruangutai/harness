"""The boundary rule — one implementation, read by every guard that needs it.

Extracted from `check-domain.py`'s embedded Python (FEAT-17 T-01). The rule was
reachable only from inside that heredoc, so `bash-write-guard.py` could not consult it
and enforced a second, weaker version of the same question — the split issue #261
reports. A heredoc cannot be imported, so the rule moves here and both guards import it.

NO BEHAVIOUR CHANGES IN THIS MOVE. Every function below is the `check-domain.py` text
verbatim, with exactly two edits, both stated in T-01's intent: `resolve_fleet` and
`select_base` take the hook `label` as a parameter and emit it, so a second caller
cannot print a verdict naming the wrong hook; and the DEC-143 worktree prefix is built
from `WORKTREES_SEGMENT` rather than spelled again.

`check-domain.py` keeps printing the agent-facing BLOCKED lines. `classify` RETURNS a
verdict and prints nothing: a module shared by two hooks must not decide whose wording
the agent sees.
"""

import os
import re
import subprocess
import sys
import artifact_accessors
import harness_yaml
from run_identity import MARKER_NAME as _RUN_IDENTITY_MARKER

# THE LEGITIMATE WORKTREE LOCATION, named once. Every rule in this module that needs
# it reads this constant, so mutating it here changes the rule everywhere it applies
# — which is what T-03 mutates by name to prove there is one implementation and not
# two agreeing copies.
#
# Two literals survive in check-domain.py and are deliberately NOT rewired: the
# stripping regex in `_norm` and the prefixes in SWEEP_GLOBS. Both belong to the shape
# phase, whose import of this module is absorbing rather than fail-closed, so reading
# this constant from there would hand the shape gate a dependency the fail-closed rule
# then blocks the main session on.
WORKTREES_SEGMENT = ".claude/worktrees"

# THE RUN-ARTIFACT PATTERNS, shared between check-domain.py (content or route
# guards on Write/Edit) and bash-write-guard.py (route-only refusal on Bash).
# One definition keeps both write surfaces from silently disagreeing.
RE_RUN_DIGEST = re.compile(r"^\.harness/[^/]+/features/[^/]+/runs/[^/]+/digest\.md$",
                            re.IGNORECASE)
RE_STATE_YAML = re.compile(r"^\.harness/[^/]+/features/[^/]+/runs/[^/]+/state\.yaml$",
                            re.IGNORECASE)
RE_RUN_IDENTITY = re.compile(
    r"^\.harness/[^/]+/features/[^/]+/runs/[^/]+/"
    + re.escape(_RUN_IDENTITY_MARKER) + r"$",
    re.IGNORECASE)

# A directory is a harness checkout when it contains MARKER. Never a caller-supplied
# parameter (FEAT-42 T-01): a parameter is what let each caller invent its own
# definition — check-plan-routes.py probed team-config.yaml, factory_config.py probed
# SPEC.md, wayfind.py probed the bare .harness DIRECTORY, and that last probe is the
# fail-open recorded at check-plan-routes.py:489-495: $HOME/.harness holds two backup
# tarballs and no team-config.yaml, so the bare-directory probe resolved $HOME as a root.
MARKER = os.path.join(".harness", "team-config.yaml")
PROJECT_DIR_ENV = "HARNESS_PROJECT_DIR"


def root_from_script(bin_dir):
    """The root implied by `bin_dir`'s location, by pure arithmetic. ZERO filesystem
    access and ZERO environment reads — for callers that must not touch cwd or disk.

    `bin_dir` is `<root>/.claude/skills/harness/bin`, so four levels up is `<root>`.
    """
    return os.path.abspath(os.path.join(bin_dir, "..", "..", "..", ".."))


def resolve_root(bin_dir, strict=True):
    """The root: environment-aware, the only one of the three that reads os.environ.

    Reads HARNESS_PROJECT_DIR ONLY — never CLAUDE_PROJECT_DIR, which is host-owned,
    always names the session project root, and is one of the three spellings of a
    single value this feature exists to delete. If the override is set and carries
    MARKER, it wins. If it is set and does NOT carry MARKER, the override is
    discarded — reported on stderr naming both candidates — and resolution falls
    through to the derived root. If nothing carries MARKER: raise ValueError naming
    both candidates when `strict`, else return the derived root anyway.
    """
    derived = root_from_script(bin_dir)
    override = os.environ.get(PROJECT_DIR_ENV)
    if override:
        if os.path.isfile(os.path.join(override, MARKER)):
            return os.path.abspath(override)
        print(
            f"harness_boundary: discarding {PROJECT_DIR_ENV}={override!r} — it does "
            f"not carry {MARKER}. Falling back to the derived root {derived!r}.",
            file=sys.stderr,
        )
    if os.path.isfile(os.path.join(derived, MARKER)):
        return derived
    if strict:
        raise ValueError(
            f"no harness root found: neither HARNESS_PROJECT_DIR ({override!r}) nor "
            f"the derived root ({derived!r}) carries {MARKER}"
        )
    return derived


def root_above(start):
    """Walk up from `start`, returning the first directory at or above it that
    carries MARKER, or None at the filesystem root. No environment read — the only
    one of the three permitted to see a cwd, and only because a caller hands one in.

    Answers "which checkout is this PATH in". A directory merely NAMED `.harness`
    with no `team-config.yaml` inside it does not satisfy this — that bare-directory
    probe is the $HOME/.harness fail-open this function exists to close.
    """
    cur = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(cur, MARKER)):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent

def checkout_relative(abs_path):
    """Return `(checkout_dir, path relative to that checkout)`, or None.

    REPLACES `WORKTREE_REL_RE` (FEAT-30 T-04), which stripped a FIXED number of path
    segments after `WORKTREES_SEGMENT` and so answered "how deep am I" when the real
    question is "which checkout am I standing in". One mechanism for one mechanism: no
    segment is added, widened, or parameterised anywhere.

    Why the fixed strip had to go rather than gain a segment: under a
    `<segment>/<repo>/<id>/` layout it left the repository segment in the path, so the
    stripped candidate matched no glob. It also made the depth load-bearing — a rule that
    asks which checkout a path is in does not care how deep the path is.

    Three outcomes, and the None cases are deliberate:
      not in any worktree     -> None. The caller keeps its base-relative path.
      a parsed worktree       -> (checkout_dir, relpath of realpath against it)
      an UNPARSED `.git`      -> None. Do NOT invent a checkout here. That branch is
                                 already refused by its own callers, and a second,
                                 quieter answer is how a refusal becomes a fall-through.

    No git subprocess, no segment counting, no regex. `worktree_owner` already answers
    the whole question from the pointer file.

    Cost is measured and settled, recorded so it is not re-litigated: over 2000
    iterations the deleted regex took 0.3 ms in TOTAL against 46.8 ms in total here —
    0.023 ms per write, against a guard that already reads files.
    """
    owner = worktree_owner(abs_path)
    if owner is None:
        return None
    checkout_dir, owner_root, _legitimate = owner
    if owner_root is None:
        return None
    return checkout_dir, os.path.relpath(real(abs_path), checkout_dir)


def linked_worktrees(owner_root):
    """Absolute checkout directories of `owner_root`'s linked worktrees, sorted.

    Standard library only. For each directory under `owner_root/.git/worktrees`, read its
    `gitdir` pointer file, take the directory it names, drop a trailing `.git` component,
    and keep the realpath if it exists. A missing `.git/worktrees` returns `[]`.

    NO GIT SUBPROCESS: DEC-193 forbids one on the governed-write path, and a hook that
    shells out is both slow and a new failure surface.

    Used by `check-domain.py`'s post-write sweep, which at `eeabc59` joined the segment to
    a single star and therefore reached no file in any worktree deeper than one level — a
    glob that matches nothing reports nothing, so that was a SILENT regression rather than
    a refusal.

    Cost, measured on a fixture with five linked worktrees over 2000 iterations: 0.371 ms
    per call against 0.147 ms before, so +0.22 ms per governed write, scaling linearly
    with worktree count, against the ~38 ms of interpreter start-up the hook already pays.
    """
    wt_dir = os.path.join(owner_root, ".git", "worktrees")
    try:
        entries = sorted(os.listdir(wt_dir))
    except OSError:
        return []
    out = []
    for name in entries:
        pointer = os.path.join(wt_dir, name, "gitdir")
        try:
            with open(pointer, "r", encoding="utf-8", errors="strict") as fh:
                named = fh.read().strip()
        except (OSError, UnicodeError):
            # An unreadable or non-UTF-8 pointer is skipped, not guessed at. The sweep is
            # a REPORT, so a checkout it cannot place is one it cannot honestly name.
            continue
        if not named:
            continue
        if not os.path.isabs(named):
            named = os.path.join(wt_dir, name, named)
        # The pointer names the worktree's own `.git` FILE; the checkout is its parent.
        if os.path.basename(named) == ".git":
            named = os.path.dirname(named)
        named = os.path.normpath(named)
        if os.path.isdir(named):
            out.append(real(named))
    return sorted(set(out))


class AmbiguousWorktree(Exception):
    """Two or more of `owner_root`'s linked worktrees prefix-match one feature id.

    Raised by `worktree_for_feature` instead of guessing. `str(exc)` names every
    candidate basename, sorted, so the caller's refusal is one an operator can act on.
    """


def worktree_for_feature(owner_root, feature_id):
    """Which of `owner_root`'s linked worktrees belongs to `feature_id`?

    Enumerates `linked_worktrees(owner_root)` and keeps every checkout whose basename
    either EQUALS `feature_id` or is a prefix of it followed by a hyphen --
    `feature_id.startswith(basename + "-")`. Exactly one candidate: return it, already
    realpath-resolved by `linked_worktrees`. No candidate: return None. Two or more:
    raise `AmbiguousWorktree` naming every candidate basename, sorted. Never guess and
    never prefer the longest match.

    PREFIX, NOT EQUALITY, because this repository measured the equality premise false
    in its own source: feature-worktree.py:236-239 recorded that all four live
    worktrees were named FEAT-32 while every feature directory was
    FEAT-32-concurrent-write-merge, and :244-248 resolved that by prefix, refusing on
    ambiguity, because a coin flip is strictly worse than a refusal the operator can
    act on. Both spellings are legal input, so equality alone leaves every short-form
    worktree unmatched and silently unbound.

    COST: this runs on the PreToolUse path and adds no I/O beyond the
    `linked_worktrees` call the caller already makes, which is measured at 0.371 ms
    per call over five worktrees, against the hook's own ~38 ms interpreter-startup
    floor.
    """
    candidates = [
        checkout for checkout in linked_worktrees(owner_root)
        if os.path.basename(checkout) == feature_id
        or feature_id.startswith(os.path.basename(checkout) + "-")
    ]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    names = sorted(os.path.basename(checkout) for checkout in candidates)
    raise AmbiguousWorktree(
        "feature %r matches %d linked worktrees: %s"
        % (feature_id, len(names), ", ".join(names))
    )


# A governed feature artifact: `.harness/<segment>/features/<feature-id>/...`. Owned here
# (FEAT-61 T-01) because both write routes — check-domain's tool route and bash-write-guard's
# Bash route — ask the same checkout question of it; two copies of this regex let a fix to
# the binding rule land on one route and leave the other permissive (the FEAT-45 shape).
RE_FEATURE_ARTIFACT = re.compile(r"^\.harness/[^/]+/features/([^/]+)/")


def feature_artifact_id(raw_rel):
    """The feature id a governed artifact path belongs to, or None when it is not one."""
    match = RE_FEATURE_ARTIFACT.match(raw_rel)
    return None if match is None else match.group(1)


def feature_artifact_checkout_mismatch(owner_root, raw_rel, target_path):
    """Does a write to `raw_rel` (resolved at `target_path`) land outside the worktree its
    feature is linked to? None when the path is not a feature artifact, when the feature has
    no linked worktree, or when the write is already inside it; otherwise
    `(feature_id, expected_worktree)` for the adapter to refuse in its own voice.

    THE ADAPTERS OWN THE RESPONSE. `AmbiguousWorktree` and any unexpected failure propagate:
    each route decides its refusal channel and whether to absorb, because an exit code one
    host treats as a refusal the other treats as non-blocking. This function decides only the
    path question, so the binding rule has one home and cannot drift between the routes.
    """
    feature_id = feature_artifact_id(raw_rel)
    if feature_id is None:
        return None
    expected = worktree_for_feature(owner_root, feature_id)
    if expected is None:
        return None
    checkout = checkout_relative(target_path)
    if checkout is not None and real(checkout[0]) == real(expected):
        return None
    return feature_id, expected


# --- FEAT-62 T-03: the changed-state feedback loop behind every canonical structured write.
#
# `--changed` is the edit-loop verb (grilling artefact, SC-06): it exists so an agent sees the
# invariants its write just touched WITHOUT knowing the flag exists. The primary path is
# therefore not a rule an agent must remember but this adapter, run by the two canonical
# writers -- plan-merge.py after each successful mutating plan write, feature_json_write
# after each successful feature.json write -- once the write's own lock has been released.
#
# THE CHECKOUT IS DERIVED FROM THE WRITTEN PATH ALONE. `resolve_root` reads the environment
# (HARNESS_PROJECT_DIR) and answers "which tree is this SESSION about"; that is the wrong
# question here. A write to `<X>/.harness/<repo>/features/<FEAT>/plan.yaml` is feedback
# about `<X>` and nothing else -- so a test fixture under /tmp derives /tmp/<fixture>, finds no
# checker there, and is silent, rather than reaching into the developer's checkout because an
# env var pointed at it (panel finding PF-e27f2ac2). A path that is not canonical -- a scratch
# file, a plain CLI positional -- derives no root at all.
#
# ADVISORY, NEVER A ROLLBACK. The write has already landed; what the checker says is stderr
# feedback for the caller to relay. A clean selective run prints nothing at the checker
# source (check-state.py's own `--changed` contract), so this forwards whatever arrives
# without matching any exact string (panel finding PF-db8324a6). The writer's stdout receipt,
# refusal paths, durable bytes and exit status are untouched by construction: this runs after
# all of them and touches none.
#
# NEVER RECURSIVE. The checker spawns gate scripts of its own; none of them writes a plan or a
# feature.json, and the env marker below stops a nested writer from re-entering here.
# HARNESS_PROJECT_DIR is DROPPED from the child's environment for the same reason the root is
# derived from the path: the checker then resolves its root from its own location, which IS
# the derived checkout, and a stale session override cannot redirect the feedback.
_CHANGED_FEEDBACK_ENV = "HARNESS_CHANGED_FEEDBACK"
# The union of plan-merge.py's PLAN_TAIL and feature_json_write's FEATURE_JSON_TAIL, anchored
# at the checkout: the tree segment is optional, exactly as the writers accept it.
RE_CANONICAL_STRUCTURED_WRITE = re.compile(
    r"^(?P<root>.*?)/\.harness/(?:[^/]+/)?features/(?:FEAT|BUG)-[^/]+/(?:plan\.yaml|feature\.json)$")
CHECKER_REL = os.path.join(".claude", "skills", "harness", "bin", "check-state.py")


def changed_state_root(target_path):
    """The checkout a canonical plan.yaml/feature.json write belongs to, from the PATH alone;
    None for any other path."""
    posix = os.path.abspath(target_path).replace(os.sep, "/")
    match = RE_CANONICAL_STRUCTURED_WRITE.match(posix)
    return None if match is None else (match.group("root") or "/")


def _changed_state_checker(target_path):
    """The checker to run for a write to `target_path`, or None: the path must be canonical,
    the derived checkout must carry MARKER and the checker, and this process must not itself
    be inside a feedback run."""
    root = changed_state_root(target_path)
    if root is None or os.environ.get(_CHANGED_FEEDBACK_ENV):
        return None
    checker = os.path.join(root, CHECKER_REL)
    if os.path.isfile(checker) and os.path.isfile(os.path.join(root, MARKER)):
        return root, checker
    return None


def changed_state_feedback(target_path, timeout=120):
    """Run that checkout's `check-state.py --changed` after a successful structured write and
    return its non-clean rows (both streams, in order) for the caller's stderr. Empty when
    there is no checker to run (`_changed_state_checker`) or it cannot be spawned -- feedback
    is never a failure."""
    found = _changed_state_checker(target_path)
    if found is None:
        return []
    root, checker = found
    env = {k: v for k, v in os.environ.items() if k != PROJECT_DIR_ENV}
    env[_CHANGED_FEEDBACK_ENV] = "1"
    try:
        result = subprocess.run([sys.executable, checker, "--changed"], cwd=root, env=env,
                                capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return []
    return [line for line in (result.stdout + result.stderr).splitlines() if line.strip()]


def relay_changed_state_feedback(target_path):
    """`changed_state_feedback`, printed to stderr under one header — the writers' one call."""
    rows = changed_state_feedback(target_path)
    if rows:
        print(f"check-state --changed after {target_path}:", file=sys.stderr)
        for row in rows:
            print(row, file=sys.stderr)


class RepoModuleError(Exception):
    """A repo-local script could not be loaded as a module (FEAT-63 T-01, D-02). ONE type for
    every failure of the load itself — no spec, the loader's own I/O error, an exception raised
    while the module body executes — so a caller can name the boundary it guards instead of
    guessing which of `ImportError`, `OSError`, `SyntaxError` or the script's own bug will
    arrive. The original exception is kept as `cause` (and chained), because the CANNOT RUN
    lines check-state.py prints render its type and text."""

    def __init__(self, module_name, path, cause):
        self.module_name = module_name
        self.path = path
        self.cause = cause
        super().__init__(f"cannot load {module_name!r} from {path}: {type(cause).__name__}: {cause}")


def load_repo_module(module_name, path=None, register=False):
    """Load a repo-local script as a module — by path, THE sole `spec_from_file_location` in
    bin/ (FEAT-61 T-01); or, with no `path`, by name through the ordinary import machinery
    (FEAT-63 T-02: `import gh_board` inside an invariant used to sit in its own broad catch,
    because a sibling that fails while its body executes raises whatever it raises; this is
    the one place that failure is given a type). The kebab-case gate scripts cannot be
    imported by name, and six hand-written copies of this sequence disagreed on two
    decisions this function now owns:

    - `register=True` binds the module in `sys.modules` BEFORE exec. A script that declares
      dataclasses needs it (check-skill-weight.py: dataclasses resolve their module by name
      during class creation); a script that does not is left out so a failed load leaves no
      half-initialised entry behind.
    - A failed exec raises RepoModuleError carrying the ORIGINAL exception (FEAT-63: it used to
      re-raise it bare, which left every caller catching `Exception` to be safe) and removes
      only the registration this call made, restoring whatever was bound under the name before.

    A path that yields no spec or loader (missing file, a directory) is RepoModuleError over an
    ImportError naming the path, never an AttributeError on None three lines later.
    KeyboardInterrupt and SystemExit are process control, not load failures: they propagate
    unchanged (the registration is still undone).
    """
    return _as_repo_module_failure(module_name, path, _load_repo_module, module_name, path, register)


def _load_repo_module(module_name, path, register):
    import importlib
    import importlib.util
    if path is None:
        return importlib.import_module(module_name)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {module_name!r} from {path}: no module spec or loader")
    module = importlib.util.module_from_spec(spec)
    if not register:
        spec.loader.exec_module(module)
        return module
    previous = sys.modules.get(module_name)
    sys.modules[module_name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        _restore_registration(module_name, previous)
        raise
    return module


def _as_repo_module_failure(module_name, path, fn, *args):
    """Run `fn(*args)` and give anything it raises the type of a repo-module failure. THE ONE
    broad catch of the load/call boundary (FEAT-64): `load_repo_module` and `call_repo_module`
    each spelled it before. The cause, its chain and the path travel on RepoModuleError;
    process control (KeyboardInterrupt, SystemExit) passes through untouched."""
    try:
        return fn(*args)
    except Exception as error:
        raise RepoModuleError(module_name, path, error) from error


def hook_guard(main, name, fail="open"):
    """A hook's own-failure posture, spelled ONCE (FEAT-64; wired by FEAT-65). Runs `main()`
    and returns its result unchanged. An Exception escaping main is the hook's OWN defect —
    an unreadable payload shape, a missing sibling, a bug — never the agent's contract
    violation, and the verdict on it is fixed at the call site: `fail="open"` prints the
    pass-through line and returns 0 (DEC-100: only exit 2 blocks; check-domain.py set the
    precedent that a hook must not wedge every agent on its own bug); `fail="closed"` prints
    BLOCKED and returns 2 for the one hook whose safety layer cannot run without the module
    that failed. KeyboardInterrupt and SystemExit are BaseException, not Exception, and are
    never caught here: a hook that exits deliberately keeps its own exit code."""
    try:
        return main()
    except Exception as error:
        detail = f"{type(error).__name__}: {error}"
        if fail == "closed":
            print(f"{name}: BLOCKED — the hook failed internally ({detail}); enforcement is "
                  f"CLOSED rather than partial.", file=sys.stderr)
            return 2
        print(f"{name}: the hook failed internally ({detail}) — passing through; this is not "
              f"a pass, nothing was checked.", file=sys.stderr)
        return 0


def call_repo_module(module, attr, *args, **kwargs):
    """Call `module.<attr>(*args, **kwargs)` and give anything it raises the type of a repo-
    module failure (FEAT-63 T-02). The sibling's own exported error class is the caller's to
    catch FIRST; this is for the siblings whose contract is "never raises" (worktree_terminal
    .classify_all, check-skill-weight.scan, validate-digest.validate) — an exception out of
    one of those is a defect in the sibling, and a defect that took every other invariant's
    findings down with it (a traceback, and nothing else printed) would be the worse gate.
    Process control passes through."""
    return _as_repo_module_failure(module.__name__, getattr(module, "__file__", None),
                                   lambda: getattr(module, attr)(*args, **kwargs))


def _restore_registration(module_name, previous):
    """Undo one `load_repo_module(register=True)` binding after a failed exec: drop the entry
    this call made, or put back whatever was bound under the name before it."""
    if previous is None:
        sys.modules.pop(module_name, None)
    else:
        sys.modules[module_name] = previous


def inside(child, parent):
    """Whether one resolved absolute path is contained by another."""
    try:
        return os.path.commonpath([child, parent]) == parent
    except ValueError:
        return False


def _registry_claim_worktrees(owner_root, registry_root, agent_type,
                              agent_id=None, parent_agent_id=None):
    """Resolve one registry's live claims to linked worktrees."""
    import inflight_registry

    result = set()
    for claim in inflight_registry.live_claims(
            registry_root,
            agent_type,
            agent_id=agent_id,
            parent_agent_id=parent_agent_id):
        worktree = worktree_for_feature(owner_root, claim.get("feature"))
        if worktree is not None:
            result.add(worktree)
    return result


def claim_worktrees(owner_root, agent_type, destination,
                    agent_id=None, parent_agent_id=None):
    """Return linked worktrees bound to the matching agent runtime's live claims."""
    import inflight_registry

    owner_root = real(owner_root)
    destination = real(destination)
    claim_set = set()
    unreadable = set()
    for registry_root in [owner_root] + linked_worktrees(owner_root):
        try:
            claim_set.update(
                _registry_claim_worktrees(
                    owner_root,
                    registry_root,
                    agent_type,
                    agent_id=agent_id,
                    parent_agent_id=parent_agent_id,
                ))
        except inflight_registry.UnreadableRegistry as error:
            unreadable.update(error.paths)

    result = sorted(claim_set)
    if any(inside(destination, worktree) for worktree in result):
        return result
    if unreadable:
        raise inflight_registry.UnreadableRegistry(unreadable)
    return result


def claim_set_refusal(agent_type, claim_set, destination, unreadable_paths=None):
    """Build the single actionable refusal used by every governed write route."""
    destination = real(destination)
    if unreadable_paths:
        files = ", ".join(sorted(set(unreadable_paths)))
        return (
            f"{agent_type} binding cannot be determined for destination {destination}; "
            f"the write is refused because these claim registries are unreadable: {files}. "
            "Repair or remove those registry files, then retry."
        )

    held = ", ".join(sorted(set(claim_set)))
    expertise_segment = os.sep + os.path.join(".harness", "expertise") + os.sep
    if expertise_segment in destination:
        return (
            f"{agent_type} holds worktree claim(s): {held}. Destination {destination} "
            "belongs to the control-plane expertise route. Use the sanctioned "
            "python3 expertise-merge.py apply command."
        )

    home = root_above(os.path.dirname(destination)) or os.path.dirname(destination)
    return (
        f"{agent_type} holds worktree claim(s): {held}. Destination {destination} "
        f"belongs in its proper checkout at {home}; write it from a bound worktree."
    )


def glob_to_re(pat):
    """Translate a glob to a regex. `**` crosses separators, `*` does not.

    fnmatch cannot do this: its `*` matches `/` too, so `web/*/x` would match
    `web/a/b/x`. And a literal prefix comparison cannot do it either — the bug
    this replaced used str.startswith on the text before `/**`, which silently
    failed for any pattern with a wildcard earlier in the path, e.g.
    `features/*/runs/*-eng/**`. That blocked every lead from its own run dir.
    """
    out, i = [], 0
    while i < len(pat):
        c = pat[i]
        if pat.startswith("**", i):
            out.append(".*"); i += 2
            if pat.startswith("/", i):      # `**/` also matches zero segments
                out.append("/?"); i += 1
        elif c == "*":
            out.append("[^/]*"); i += 1
        elif c == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(c)); i += 1
    return re.compile("^" + "".join(out) + "$")


def matches(path, pat):
    pat = pat.rstrip("/")
    if pat in (".", ""):            # "." means read-anything; never a write grant
        return False
    if pat.endswith("/**"):
        # the directory itself, or anything beneath it
        base = pat[:-3]
        return bool(glob_to_re(base).match(path) or glob_to_re(base + "/**").match(path))
    if glob_to_re(pat).match(path):
        return True
    # a bare dir pattern grants everything under it
    return bool(glob_to_re(pat + "/**").match(path))


# THE CONTROL-PLANE CLASSIFIER (FEAT-15 T-02). Defined at module scope beside
# glob_to_re/matches so the hook path and the --resolve path reach the SAME rule —
# a resolver that granted a base the hook refuses is the build-time discovery
# check-plan-routes.py exists to prevent.
#
# Harness-owned paths with product-shaped names must be explicit. Hidden
# control-plane roots are additionally recognized by `is_control_plane_glob`
# below so their grants never bleed into a product checkout. Provider-neutral
# OMP adds `.agents`, `.omp`, and `AGENTS.md`; `.claude` holds the authored
# skills tree and the development worktrees.
HARNESS_CONTROL_PLANE = [
    ".harness/*/docs/**",
    "docs/PRINCIPLES.md",
    "README.md",
    "AGENTS.md",
    ".agents/**",
    ".omp/**",
    ".github/**",
    "tests/**",
]


def is_control_plane_glob(pat):
    """Whether a grant belongs only to the Harness checkout.

    Hidden Harness roots must not reach a product checkout's same-named
    directory. `.claude` holds the authored skills and worktrees; `.agents`
    and `.omp` are the provider-neutral OMP surfaces.
    """
    p = pat.lstrip("/")
    if p.startswith("./"):
        p = p[2:]
    return p.split("/", 1)[0] in (".harness", ".claude", ".agents", ".omp")


def real(path):
    """Absolute AND symlink-resolved.

    `abspath` alone normalises `..` textually but follows no link, so
    `.harness/harness/docs/<link>/agents/x.md` with `<link> -> ../../../.omp` stayed inside
    `.harness/` for every comparison while the write landed in `.omp/agents/`.
    Reproduced before this fix: through the link exit 0, the same file named directly
    exit 2. The gap predates the two-base rule — `docs/**` matched with no target-side
    test — so this closes a live escape rather than a regression.

    `realpath` resolves the existing prefix of a path that does not exist yet, which is
    the normal case for a Write. Applied to BOTH sides of every comparison: resolving
    only the target would break any checkout reached through a link (`/var` on macOS is
    itself a link to `/private/var`).

    AN UNRESOLVABLE PATH RETURNS ITS ABSOLUTE FORM RATHER THAN RAISING (FEAT-41 MF-2). realpath
    raises ValueError -- not OSError -- on an embedded NUL, and this function is called from
    `classify`, which runs inside check-domain.py's Python body. That ValueError propagated all
    the way out, and by that hook's own header exit 1 is NON-BLOCKING, so a single NUL in
    `tool_input.file_path` disabled EVERY domain grant, budget and route denial at once and the
    write proceeded.

    MEASURED, AND THE ATTRIBUTION CORRECTED: cycle 3's panel reported this as introduced by
    FEAT-41's own `_resolved_rel`. Running the identical fixture against `origin/main` reproduces
    it at exit 1, so it is PRE-EXISTING and lives here. The finding was right; its blame was not.

    Returning the absolute form keeps this function total. Callers that need to REFUSE an
    unresolvable path do so on their own terms -- check-domain.py's route denial treats one as a
    refusal -- rather than depending on an exception from a path-normalising helper.

    AND THE FALLBACK RESOLVES AS FAR AS IT SAFELY CAN, rather than returning a bare `abspath`
    (FEAT-41 HIGH-3). Every caller COMPARES two `real()` results, so both must be in the same
    spelling namespace. A bare abspath is not: when the checkout root is reached through a symlink,
    `real(root)` is fully resolved while an unresolvable target was not, the two shared no prefix,
    and `select_base`/`inside` classified an IN-BASE target as `not_a_domain_question` --
    bash-write-guard.py then exited 0 with empty stderr.

    MEASURED before the fix, on a symlinked root:
        real('/tmp/h3/link')                   -> /private/tmp/h3/actual
        real('/tmp/h3/link/sub/<unresolvable>') -> /tmp/h3/link/sub/<unresolvable>
        target.startswith(root)                 -> False

    THE PERMIT ITSELF IS PRE-EXISTING: origin/main crashes fail-open on the same input, so the
    write proceeded there too. What the earlier fix changed is that it became SILENT rather than
    loud, and for a guard that is worse. Resolving the longest resolvable ancestor and rejoining
    the remainder keeps one namespace without reintroducing the raise.
    """
    try:
        return os.path.realpath(os.path.abspath(path))
    except (OSError, ValueError):
        pass
    absolute = os.path.abspath(path)
    head, tail = absolute, []
    while True:
        parent = os.path.dirname(head)
        if parent == head:
            # Reached the filesystem root without resolving anything. Nothing is left to
            # normalise, so the absolute form IS the answer.
            return absolute
        tail.append(os.path.basename(head))
        head = parent
        try:
            resolved_head = os.path.realpath(head)
        except (OSError, ValueError):
            continue
        return os.path.join(resolved_head, *reversed(tail))


def resolve_fleet(root, label):
    """Resolve the fleet declaration for `root`, returning (workspace_root, bases).

    ONE function called from both the hook path and the --resolve path (FEAT-15 T-04).
    Written twice it would drift, and the two halves disagreeing is precisely the
    build-time discovery check-plan-routes.py exists to prevent: a resolver that grants
    a base the hook refuses lets a plan be signed on a route the build will reject.

    Absent is not unreadable. No file at all means no second base and today's behaviour
    exactly, with nothing imported. A file that will not load exits 2 — the value that
    identifies product paths is the one that failed, so enforcing the readable parts
    would mean classifying paths with the classifier missing.
    """
    fleet_path = os.path.join(root, ".harness", "factory", "fleet.yaml")
    if not os.path.exists(fleet_path):
        return None, [], fleet_path
    try:
        # LAZY, and stderr-muzzled for the import statement ONLY. factory_config's own
        # FLEET_PATH resolves at import time from ITS OWN on-disk location, never from
        # `root` below — so importing it can still print a discard notice to stderr if
        # the caller's HARNESS_PROJECT_DIR happens to be set without carrying MARKER.
        # Muzzled so that noise never reaches the agent on a governed write, indistinguishable
        # from a real verdict.
        import io
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()):
            import factory_config
        # The EXPLICIT path, never factory_config.FLEET_PATH: that constant is computed
        # at import time from resolve_root(factory_config's own bin dir) — always the LIVE
        # checkout's fleet.yaml, never this hook's `root` argument. Under a fixture root the
        # two disagree and the constant names the live repository.
        fleet = artifact_accessors.load_fleet(fleet_path)
        bases = [real(factory_config.workspace_path(fleet, e["name"]))
                 for e in fleet["repos"]]
        return fleet["workspace_root"], bases, fleet_path
    except (artifact_accessors.FleetError, KeyError, TypeError, ValueError) as e:
        print(f"{label}: BLOCKED — the fleet declaration does not load, so no "
              "product path can be identified.", file=sys.stderr)
        print(f"  {fleet_path}", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        print("  Enforcement is CLOSED rather than partial: the value that identifies "
              "product paths is the one that failed. Fix the file (the main session "
              "owns it — it is in no agent's domain), then retry.", file=sys.stderr)
        sys.exit(2)


def select_base(abs_target, root, workspace_root, workspace_bases, fleet_path, label):
    """Pick the base a target resolves against, and say how to match in it.

    Returns (base, filter_globs, target_side_test). Shared by the hook path and the
    --resolve path so the two can never disagree. Exits 2 for a target under the
    workspace belonging to no declared repository; returns None for a target in
    neither base, which stays not-a-domain-question.

    Containment is commonpath over abspaths throughout, never a string prefix, so a
    path reached via docs/../src/main.py resolves back inside and lands in the right
    base — and /workspaces/widget-other is not read as inside /workspaces/widget.
    """
    abs_root = real(root)

    # All containment decisions use the module-level primitive shared with
    # claim_worktrees, so path membership cannot drift between the guard and seam.

    if inside(abs_target, abs_root):
        # THE HARNESS BASE. Every glob is applicable — nothing is filtered on the glob
        # side — but a match is accepted only for a control-plane TARGET. That is what
        # stops a src/** grant from reaching this repository's own src/.
        return abs_root, (lambda _g: True), is_control_plane_target
    if workspace_bases and any(inside(abs_target, b) for b in workspace_bases):
        # A PRODUCT BASE. Longest match wins, so a repo checked out beneath another's
        # path resolves against its own base rather than its parent's. Filtering happens
        # on the GLOBS here: a control-plane grant must not reach a product checkout's
        # .harness/ or .claude/. HARNESS_CONTROL_PLANE plays NO part on this side — it is
        # target-side only, and consulting it here would refuse a product checkout's own
        # README.md, the very file its documentor exists to write.
        base = max((b for b in workspace_bases if inside(abs_target, b)), key=len)
        return base, (lambda g: not is_control_plane_glob(g)), (lambda _r: True)
    if workspace_root is not None and inside(abs_target, real(workspace_root)):
        # UNDER THE WORKSPACE, BELONGING TO NO DECLARED REPO. Refused rather than
        # ignored: a checkout there for an unlisted repository is stale or a mistake,
        # and treating it as scratch would reopen the hole for exactly the paths the
        # factory writes to.
        print(f"{label}: BLOCKED — {abs_target} is under the factory workspace but "
              f"belongs to no repository declared in {fleet_path}.", file=sys.stderr)
        print("  A checkout there for an unlisted repository is stale or a mistake. "
              "Add the repository to `repos` in that file, or remove the directory.",
              file=sys.stderr)
        sys.exit(2)
    return None, None, None


def is_control_plane_target(rel):
    """The TARGET-side test, used only in the harness base.

    Target-keyed, not glob-keyed, and that is load-bearing: named entries may appear
    in no team-config grant, so a glob-keyed classifier would have nothing to match
    them against. `tests/**` is intentionally target-side only: keeping
    `is_control_plane_glob("tests/**")` false leaves a product checkout's own tests in
    its product base. Anchored through the same `matches` idiom, so `README.md` means
    the repository-root readme and never `docs/README.md`, and `.github/**` never
    matches `vendor/.github/x`.
    """
    if is_control_plane_glob(rel):
        return True
    return any(matches(rel, e) for e in HARNESS_CONTROL_PLANE)


def classify(abs_target, root, globs, shared, label):
    """Decide whether `globs`/`shared` reach `abs_target`, and return the verdict.

    Moved verbatim from `check-domain.py`'s `domain_check` (FEAT-17 T-01) — the block
    that ran from THE FLEET AND THE BASE to the actionable rejection. It RETURNS rather
    than prints or exits, because two hooks now ask this question and the module must
    not decide whose wording the agent reads. `check-domain.py` prints exactly what it
    printed before, from these fields.

    The verdict is a dict:
      outcome           one of not_a_domain_question, allow, shared, deny
      rel               the base-relative path (None when not a domain question)
      base              the base the target resolved against (likewise)
      advertise         the globs the `Permitted for you` line may honestly offer
      shared_advertise  the same for shared paths

    Note what is NOT returned and never was: `resolve_fleet` and `select_base` still
    exit 2 themselves for an unloadable fleet file and for a path under the workspace
    belonging to no declared repository. Those are refusals to answer, not verdicts,
    and turning them into a returned outcome would let a caller ignore them.
    """
    # THE FLEET AND THE BASE (FEAT-15 T-01/T-02, REQ-01 through REQ-06). Both steps go
    # through the SAME functions the --resolve path calls, so the resolver can never
    # grant a base a hook refuses — a plan signed on a route the build rejects is the
    # build-time discovery check-plan-routes.py exists to prevent.
    #
    # Resolution runs for EVERY governed write, whatever the target looks like. A
    # resolution that only ran for paths already shaped like product paths would be
    # deciding the question it exists to answer.
    workspace_root, workspace_bases, fleet_path = resolve_fleet(root, label)
    _abs_target = real(abs_target)
    base, _glob_filter, target_side_test = select_base(
        _abs_target, root, workspace_root, workspace_bases, fleet_path, label)
    if base is None:
        # OUT-OF-PLACE WORKTREE (issue #103), checked BEFORE the fall-through below.
        # A sibling worktree of this repository is outside both bases, so it lands here
        # and no grant can reach it — which is exactly why it used to be waved through
        # as "not our problem". It is not a scratch path: it is a checkout of this
        # repository in a place nobody merges from.
        _wt_owner = worktree_owner(real(abs_target))
        if _wt_owner is not None and not _wt_owner[2]:
            # owner_root None means the pointer did not PARSE. Refused either way — a
            # checkout this code cannot place is not a checkout it may write into — but
            # the caller says which, because "unparseable" and "in the wrong place" want
            # different remedies from a human.
            return {"outcome": "out_of_place_worktree", "rel": None, "base": None,
                    "advertise": [], "shared_advertise": [],
                    "checkout": _wt_owner[0], "owner_root": _wt_owner[1],
                    "unparsed": _wt_owner[1] is None,
                    "expected": worktree_refusal_location(_wt_owner[1])}

        # WRONG CHECKOUT, SAME REPOSITORY (issue #895). abs_target can be outside
        # BOTH bases and still be a real mistake rather than a scratch path: the main
        # checkout, seen from a session rooted in one of its own worktrees, or a
        # sibling worktree either way. Domain grants are declared once and matched by
        # relative path SHAPE — the identical path exists, unrefused, in every
        # checkout of the family — which is exactly what let FEAT-40's ship
        # write-back land in main from a worktree session (commit 3952814). Checked
        # AFTER out-of-place-worktree (an illegitimate placement is refused on that
        # ground first) and BEFORE the not-a-domain-question fall-through, because
        # /tmp and an unrelated repository are not this: this is the SAME repository,
        # just the wrong tree of it.
        _target_owner = _wt_owner[1] if _wt_owner is not None else None
        _root_owner = worktree_owner(real(root))
        _root_owner_root = _root_owner[1] if _root_owner is not None else None
        if (_target_owner is not None and _root_owner_root is not None
                and real(_target_owner) == real(_root_owner_root)):
            return {"outcome": "wrong_checkout", "rel": None, "base": None,
                    "advertise": [], "shared_advertise": [],
                    "checkout": _wt_owner[0], "root": real(root)}

        # NOT A DOMAIN QUESTION, unchanged. bash-write-guard.py already said so
        # ("outside repo — not this hook's problem"), and check-domain did not: a
        # scratch script at /tmp/x.py was legal via Bash and blocked via Write, so an
        # agent learned to route around a hook whose own message said not to. /tmp,
        # /var/folders and unrelated checkouts keep exactly today's behaviour.
        return {"outcome": "not_a_domain_question", "rel": None, "base": None,
                "advertise": [], "shared_advertise": []}

    _abs_root = real(root)
    applicable_globs = [g for g in globs if _glob_filter(g)]
    applicable_shared = [s for s in shared if _glob_filter(s)]

    # Compare base-relative, so an absolute tool path and a relative glob still meet.
    rel = os.path.relpath(_abs_target, base)

    # WORKTREES (DEC-143). A git worktree under `<WORKTREES_SEGMENT>/<name>/` is a full
    # checkout, but to this rule it was just a subdirectory: the same repo-relative path
    # that globs ALLOW in the main checkout arrived prefixed and matched nothing — so in
    # a worktree-per-session project, NO doer could write source at all. Found in kaya-ai
    # at the first build dispatch after plan approval, the most expensive possible place.
    #
    # Fix: match the RAW path first (so a glob that deliberately targets the worktree
    # directory still works — none exist today, but the edge is real), then match the
    # path relative to THE CHECKOUT IT STANDS IN against the same globs. This is NOT a
    # widen: identical globs, anchored to that checkout.
    #
    # The second candidate came from a fixed-segment strip until FEAT-30 T-04. It now
    # comes from `checkout_relative`, which asks the containing checkout via its git
    # pointer. The ordering and the meaning are unchanged; only the source of the second
    # candidate is, and with it the depth-independence — `<segment>/<repo>/<id>/` and
    # `<segment>/<id>/` both resolve, because neither is counted.
    _ck = checkout_relative(_abs_target)
    rel_candidates = [rel]
    if _ck is not None and real(_ck[0]) != real(base):
        # `!= base`, not `!= root`: when the target resolves against a product base the
        # checkout IS that base, and adding an identical second candidate would be noise.
        rel_candidates.append(_ck[1])

    # A match is accepted only where the base's target-side test passes. In the product
    # base that test is constant-True and the filtering already happened on the globs;
    # in the harness base every glob is live but only a control-plane target may be
    # granted by one. Discarding the match here rather than filtering globs above is
    # what makes `.harness/*/docs/**` grant <harness>/.harness/harness/docs/guide.md
    # while refusing <harness>/src/main.py under a `src/**` grant.
    if any(matches(r, g) for r in rel_candidates for g in applicable_globs
           if target_side_test(r)):
        return {"outcome": "allow", "rel": rel, "base": base,
                "advertise": [], "shared_advertise": []}

    if any(matches(r, g) for r in rel_candidates for g in applicable_shared
           if target_side_test(r)):
        # Shared paths are owned by nobody and always serialized (DEC-85). Allow the
        # write, but the caller says so — an unnoticed shared-file edit is how two
        # agents collide.
        return {"outcome": "shared", "rel": rel, "base": base,
                "advertise": [], "shared_advertise": []}

    # ACTIONABLE REJECTION (DEC-100b). A probe confirmed that naming only the rejected
    # path leaves an agent with no basis for choosing a valid alternative, so the caller
    # always prints what it MAY write — and these are the lists it prints.
    #
    # The line must not advertise globs that cannot grant anything in the base that was
    # selected — an agent told it may write `src/**` here, when here is the harness
    # base, is being sent round a loop it cannot exit. In the product base that is the
    # non-control-plane globs; in the harness base, the globs some control-plane target
    # could actually satisfy.
    if base == _abs_root:
        _advertise = [g for g in applicable_globs
                      if is_control_plane_glob(g) or any(
                          matches(e.rstrip("*").rstrip("/"), g) or matches(g.rstrip("*").rstrip("/"), e)
                          for e in HARNESS_CONTROL_PLANE)]
        _shared_advertise = [s for s in applicable_shared if is_control_plane_glob(s)]
    else:
        _advertise = list(applicable_globs)
        _shared_advertise = list(applicable_shared)

    return {"outcome": "deny", "rel": rel, "base": base,
            "advertise": _advertise, "shared_advertise": _shared_advertise}


def worktree_owner(path):
    """Which checkout does `path` stand in, and is that checkout in a legal place?

    Returns `(checkout_dir, owner_root, legitimate)`. Issue #103: a linked git worktree
    of this repository that does not live under `WORKTREES_SEGMENT` silently disables
    the harness machinery, so it is a mistake rather than a supported shape.

    THREE OUTCOMES, AND THE THIRD EXISTS BECAUSE ITS ABSENCE WAS A FAIL-OPEN. The review
    panel found it and it was reproduced end to end before this fix: every parse failure
    returned None, every caller read None as not-a-worktree, and a single appended
    `\xff` byte on an otherwise valid pointer turned an identical write from exit 2 into
    a silent exit 0. That is issue #103's own failure direction, installed inside issue
    #103's fix.

      None                     NO `.git` entry found walking up. Genuinely not in a
                               worktree — /tmp, an unrelated directory. Callers ALLOW.
      (dir, root, True/False)  A pointer was found AND parsed. `legitimate` says whether
                               the checkout sits under the owner's WORKTREES_SEGMENT.
      (dir, None, False)       A `.git` FILE was found and could NOT be parsed. UNKNOWN,
                               and `owner_root is None` is how a caller tells it apart.
                               Callers must REFUSE: something claims to be a linked
                               worktree and this code cannot say where it belongs.

    NO GIT SUBPROCESS. The guard runs on every governed write, and a hook that shells
    out is both slow and a new failure surface — it would also be answering a question
    about the filesystem by asking a program that reads the filesystem. Walk up to the
    first `.git` entry and read it:

      a DIRECTORY  the main checkout. owner_root is the checkout, legitimate is True.
      a FILE       a linked worktree. Its single line is `gitdir: <abs>/.git/worktrees/<id>`,
                   so the owning repository is the parent of the `.git` directory named
                   in that pointer.

    Legitimacy is commonpath over realpath-resolved absolutes, never a string prefix:
    `<root>/.claude/worktrees-old/wt` must not read as inside `<root>/.claude/worktrees`.
    """
    cur = real(path)
    if not os.path.isdir(cur):
        cur = os.path.dirname(cur)
    seen_root = None
    while True:
        dot = os.path.join(cur, ".git")
        if os.path.isdir(dot):
            return (cur, cur, True)
        if os.path.isfile(dot):
            try:
                with open(dot, "r", encoding="utf-8", errors="strict") as fh:
                    line = fh.read().strip()
            except (OSError, UnicodeError):
                # Unreadable, or not UTF-8. UNKNOWN, never "not a worktree".
                return (cur, None, False)
            # MULTILINE, because a pointer carrying any second line is still a pointer
            # this code can read. Before the fix `$` anchored at end-of-string, so one
            # trailing line failed the whole match and the write was allowed.
            m = re.match(r"^gitdir:\s*(.+?)\s*$", line, re.MULTILINE)
            if not m:
                return (cur, None, False)
            entry = m.group(1).strip()
            if not os.path.isabs(entry):
                # A relative pointer is legal git, but it resolves against the checkout
                # rather than against this process's cwd — which is what makes writing
                # `os.path.abspath` here a bug rather than a shortcut.
                entry = os.path.join(cur, entry)
            entry = os.path.normpath(entry)
            worktrees_dir = os.path.dirname(entry)          # <abs>/.git/worktrees
            git_dir = os.path.dirname(worktrees_dir)        # <abs>/.git
            if os.path.basename(worktrees_dir) != "worktrees" or os.path.basename(git_dir) != ".git":
                return (cur, None, False)
            owner_root = real(os.path.dirname(git_dir))     # <abs>
            legal_home = real(os.path.join(owner_root, WORKTREES_SEGMENT))
            try:
                legitimate = os.path.commonpath([real(cur), legal_home]) == legal_home
            except ValueError:      # different drives / unrelated roots
                legitimate = False
            return (cur, owner_root, legitimate)
        parent = os.path.dirname(cur)
        if parent == cur or parent == seen_root:
            return None
        seen_root, cur = cur, parent


def worktree_refusal_location(owner_root):
    """Where worktrees belong, for the caller's verdict. One spelling, from the constant.

    `owner_root` is None in the UNKNOWN case, where the pointer did not parse and no
    owning repository could be named. Returning the bare segment there is deliberate:
    formatting None into a path raises, and an unhandled raise in a guard exits 1, which
    is NON-BLOCKING — the fail-open this whole fix is closing.
    """
    if owner_root is None:
        return WORKTREES_SEGMENT + os.sep
    return os.path.join(owner_root, WORKTREES_SEGMENT) + os.sep


# THE RUN-DIR GRANT VOCABULARY (BUG-124 T-01). A dispatcher can name a run-dir path
# a governed callee provably cannot write — an inverted slug such as `eng-t01` instead
# of `t01-eng` resolves to no lead's grant. These four helpers are the mechanism that
# lets dispatch-guard.py (T-02) catch that at dispatch time instead of at write time;
# nothing here spells a squad name literally, so a renamed or added squad needs no
# second edit (D-02).

def run_dir_grant_globs(root):
    """Return all declared write grants for run directories, or [] on manifest failure.

    `manifest_domains(..., agent=None)` aggregates named-role write grants separately
    from shared write grants. Both can authorize a dispatcher run directory. Manifest
    access remains fail-open because dispatch-guard decides what an empty vocabulary
    means when the manifest cannot be read.
    """
    manifest_path = os.path.join(root, ".harness", "team-config.yaml")
    try:
        all_roles, shared = artifact_accessors.manifest_domains(manifest_path, agent=None)
    except (artifact_accessors.ArtifactAccessError, artifact_accessors.FleetError,
            harness_yaml.YamlParseError, OSError, UnicodeError, KeyError, TypeError,
            ValueError):
        return []
    return sorted({glob for glob in (*all_roles, *shared) if "/runs/" in glob})


# Anchored on the literal `.harness/` segment (not `checkout_relative()`): a dispatch
# prompt legitimately names an absolute path in another checkout that may not exist
# yet, and this must read the tail with zero filesystem access. This is also what
# makes the D-05 `[.]harness/` quoting spelling invisible here — the escaped form
# never contains the literal substring `.harness/`.
_RUN_DIR_REF_RE = re.compile(
    r"\.harness/([^/\s]+)/features/([^/\s]+)/runs/([A-Za-z0-9._-]+)")


def run_dir_refs(text):
    """Every `.harness/<repo>/features/<feature>/runs/<slug>` reference in `text`,
    as `(repo, feature, slug)` tuples, in order of first appearance, de-duplicated.
    """
    seen = set()
    out = []
    for m in _RUN_DIR_REF_RE.finditer(text):
        ref = (m.group(1), m.group(2), m.group(3).rstrip(".,"))
        if ref not in seen:
            seen.add(ref)
            out.append(ref)
    return out


def run_dir_slug_ok(ref, globs):
    """Whether `ref = (repo, feature, slug)` names a run directory at least one of
    `globs` can write. Synthesizes the run-dir's leaf — `.../runs/<slug>/x` — so a
    bare directory reference is gradeable against a grant glob ending in `/**`.
    `globs` empty means "cannot check", which is the CALLER's call, not this one's:
    it returns False, never True.
    """
    if not globs:
        return False
    repo, feature, slug = ref
    candidate = f".harness/{repo}/features/{feature}/runs/{slug}/x"
    return any(matches(candidate, g) for g in globs)


def run_dir_forms(globs):
    """The compliant example form for each glob in `globs`, sorted and de-duplicated:
    `.harness/*/features/*/runs/*-eng/**` yields `<task-or-purpose>-eng`. Takes the
    last path segment before a trailing `/**`, replaces a leading `*` with the literal
    text `<task-or-purpose>`, and skips any glob whose run-dir segment carries no
    suffix (a bare `*`) or names a fixed literal instead of a wildcard suffix.
    """
    out = set()
    for g in globs:
        base = g[:-3] if g.endswith("/**") else g
        segment = base.rsplit("/", 1)[-1]
        if not segment.startswith("*") or segment == "*":
            continue
        out.add("<task-or-purpose>" + segment[1:])
    return sorted(out)
