"""The boundary rule — one implementation, read by every guard that needs it.

Extracted from `check-domain.sh`'s embedded Python (FEAT-17 T-01). The rule was
reachable only from inside that heredoc, so `bash-write-guard.sh` could not consult it
and enforced a second, weaker version of the same question — the split issue #261
reports. A heredoc cannot be imported, so the rule moves here and both guards import it.

NO BEHAVIOUR CHANGES IN THIS MOVE. Every function below is the `check-domain.sh` text
verbatim, with exactly two edits, both stated in T-01's intent: `resolve_fleet` and
`select_base` take the hook `label` as a parameter and emit it, so a second caller
cannot print a verdict naming the wrong hook; and the DEC-143 worktree prefix is built
from `WORKTREES_SEGMENT` rather than spelled again.

`check-domain.sh` keeps printing the agent-facing BLOCKED lines. `classify` RETURNS a
verdict and prints nothing: a module shared by two hooks must not decide whose wording
the agent sees.
"""

import os
import re
import sys

# THE LEGITIMATE WORKTREE LOCATION, named once. Every rule in this module that needs
# it reads this constant, so mutating it here changes the rule everywhere it applies
# — which is what T-03 mutates by name to prove there is one implementation and not
# two agreeing copies.
#
# Two literals survive in check-domain.sh and are deliberately NOT rewired: the
# stripping regex in `_norm` and the prefixes in SWEEP_GLOBS. Both belong to the shape
# phase, whose import of this module is absorbing rather than fail-closed, so reading
# this constant from there would hand the shape gate a dependency the fail-closed rule
# then blocks the main session on.
WORKTREES_SEGMENT = ".claude/worktrees"

# The DEC-143 rel-stripping pattern, built from the constant above rather than spelled
# again. `<segment>/<id>/<path>` -> group(1) is the in-worktree path.
WORKTREE_REL_RE = re.compile(r"^" + re.escape(WORKTREES_SEGMENT) + r"/[^/]+/(.+)$")


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
# The operator's verbatim four, and the list is CLOSED. `docs/harness/**` is not
# widened to `docs/**` and no fifth entry is added. The accepted risk, signed: a
# future harness-owned path starting with neither `.harness/` nor `.claude/` must be
# added here or it silently becomes a product path. No machinery detects the
# omission — that was ruled out deliberately. This is one more place to remember.
HARNESS_CONTROL_PLANE = [
    "docs/harness/**",
    "docs/PRINCIPLES.md",
    "README.md",
    ".github/**",
]


def is_control_plane_glob(pat):
    """First segment is `.harness` or `.claude`. Used to FILTER GLOBS on the product
    side — a `.harness/expertise/**` grant must not reach a product checkout's own
    `.harness/`."""
    p = pat.lstrip("/")
    if p.startswith("./"):
        p = p[2:]
    return p.split("/", 1)[0] in (".harness", ".claude")


def real(path):
    """Absolute AND symlink-resolved.

    `abspath` alone normalises `..` textually but follows no link, so
    `docs/harness/<link>/agents/x.md` with `<link> -> ../../.claude` stayed inside
    `docs/` for every comparison while the write landed in `.claude/agents/`.
    Reproduced before this fix: through the link exit 0, the same file named directly
    exit 2. The gap predates the two-base rule — `docs/**` matched with no target-side
    test — so this closes a live escape rather than a regression.

    `realpath` resolves the existing prefix of a path that does not exist yet, which is
    the normal case for a Write. Applied to BOTH sides of every comparison: resolving
    only the target would break any checkout reached through a link (`/var` on macOS is
    itself a link to `/private/var`).
    """
    return os.path.realpath(os.path.abspath(path))


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
        # LAZY, and stderr-muzzled for the import statement ONLY. Measured: under a root
        # holding no docs/harness/SPEC.md, importing factory_config prints a discard
        # notice to stderr — which would reach the agent on every governed write from a
        # fixture root, as noise indistinguishable from a real verdict.
        import io
        import contextlib
        with contextlib.redirect_stderr(io.StringIO()):
            import factory_config
        # The EXPLICIT path, never factory_config.FLEET_PATH: that constant is computed
        # at import time from that module's own root probe (docs/harness/SPEC.md), which
        # is not this hook's probe (.harness/team-config.yaml). Under a fixture root the
        # two disagree and the constant names the live repository.
        fleet = factory_config.load_fleet(fleet_path)
        bases = [real(factory_config.workspace_path(fleet, e["name"]))
                 for e in fleet["repos"]]
        return fleet["workspace_root"], bases, fleet_path
    except Exception as e:
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

    def inside(child, parent):
        try:
            return os.path.commonpath([child, parent]) == parent
        except ValueError:      # different drives / unrelated roots
            return False

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

    Target-keyed, not glob-keyed, and that is load-bearing: team-config.yaml grants
    `docs/**` and holds no `docs/harness/**` entry anywhere, so a glob-keyed
    classifier would have literally nothing to match two of the four named entries
    against. Anchored through the same `matches` idiom, so `README.md` means the
    repository-root readme and never `docs/README.md`, and `.github/**` never matches
    `vendor/.github/x`.
    """
    if is_control_plane_glob(rel):
        return True
    return any(matches(rel, e) for e in HARNESS_CONTROL_PLANE)


def classify(abs_target, root, globs, shared, label):
    """Decide whether `globs`/`shared` reach `abs_target`, and return the verdict.

    Moved verbatim from `check-domain.sh`'s `domain_check` (FEAT-17 T-01) — the block
    that ran from THE FLEET AND THE BASE to the actionable rejection. It RETURNS rather
    than prints or exits, because two hooks now ask this question and the module must
    not decide whose wording the agent reads. `check-domain.sh` prints exactly what it
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
        # NOT A DOMAIN QUESTION, unchanged. bash-write-guard.sh already said so
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
    # directory still works — none exist today, but the edge is real), then strip the
    # worktree prefix and match the in-worktree path against the same globs. This is NOT
    # a widen: identical globs, anchored to the checkout the agent is standing in.
    _wt = WORKTREE_REL_RE.match(rel)
    rel_candidates = [rel] + ([_wt.group(1)] if _wt else [])

    # A match is accepted only where the base's target-side test passes. In the product
    # base that test is constant-True and the filtering already happened on the globs;
    # in the harness base every glob is live but only a control-plane target may be
    # granted by one. Discarding the match here rather than filtering globs above is
    # what makes `docs/**` grant <harness>/docs/harness/guide.md AND <product>/docs/x.md
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
