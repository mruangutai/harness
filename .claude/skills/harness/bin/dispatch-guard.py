#!/usr/bin/env python3
"""OMP task preflight — enforce governed dispatch contracts.

Registered in `.omp/extensions/harness-hooks.ts`. The guard rejects model
overrides, validates feature/run-directory routing, and records single-flight claims.

WAS A .sh (issue #1674). The Python policy previously ran behind two shell-launched
interpreters: one derived run-directory grants with user site-packages available and
one applied policy with an isolated import path. This native entry point preserves both
import contracts in one process, making the policy visible to Python tooling.
"""
import io as _bootstrap_io
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys

if __name__ == "__main__":
    _bootstrap_bin = _bootstrap_os.path.dirname(_bootstrap_os.path.abspath(__file__))
    _bootstrap_payload = _bootstrap_sys.stdin.read().rstrip("\n")


    def _bootstrap_run_dir_globs():
        """Return the former helper interpreter's captured stdout and exit status."""
        captured_out = _bootstrap_io.StringIO()
        captured_err = _bootstrap_io.StringIO()
        prior_out, prior_err = _bootstrap_sys.stdout, _bootstrap_sys.stderr
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        try:
            _bootstrap_sys.stdout, _bootstrap_sys.stderr = captured_out, captured_err
            import artifact_accessors as bootstrap_artifacts
            import harness_boundary as bootstrap_boundary
            import harness_yaml as bootstrap_yaml

            bootstrap_root = bootstrap_boundary.resolve_root(_bootstrap_bin, strict=False)
            manifest_path = _bootstrap_os.path.join(
                bootstrap_root, ".harness", "team-config.yaml")
            bootstrap_artifacts.manifest_domains(manifest_path, agent=None)
            for grant in bootstrap_boundary.run_dir_grant_globs(bootstrap_root):
                print(grant)
            status = "0"
        except ImportError:
            status = "1"
        except (bootstrap_artifacts.ArtifactAccessError, bootstrap_yaml.YamlParseError,
                OSError, ValueError):
            # The manifest unreadable or unparseable, PyYAML unavailable to this python3
            # (MissingDependency is a YamlParseError), the fleet file bad (FEAT-65).
            status = "1"
        finally:
            _bootstrap_sys.stdout, _bootstrap_sys.stderr = prior_out, prior_err
            _bootstrap_sys.path.pop(0)
        return captured_out.getvalue().rstrip("\n"), status


    _bootstrap_globs, _bootstrap_derived = _bootstrap_run_dir_globs()

    # The policy interpreter formerly used `python3 -I`. Drop the invoking directory,
    # PYTHONPATH and user-site entries before its imports, then let the unchanged body add
    # the trusted bin directory at its original boundary.
    _bootstrap_pythonpath = {
        _bootstrap_os.path.realpath(entry)
        for entry in (_bootstrap_os.environ.get("PYTHONPATH") or "").split(_bootstrap_os.pathsep)
        if entry
    }
    _bootstrap_user_sites = _bootstrap_site.getusersitepackages()
    if isinstance(_bootstrap_user_sites, str):
        _bootstrap_user_sites = [_bootstrap_user_sites]
    _bootstrap_unsafe = _bootstrap_pythonpath | {
        _bootstrap_os.path.realpath(_bootstrap_bin),
        _bootstrap_os.path.realpath(_bootstrap_os.getcwd()),
        *(_bootstrap_os.path.realpath(entry) for entry in _bootstrap_user_sites),
    }
    _bootstrap_sys.path[:] = [
        entry for entry in _bootstrap_sys.path
        if entry and _bootstrap_os.path.realpath(entry) not in _bootstrap_unsafe
    ]

    # The helper was a separate interpreter. Do not leak its project or YAML modules into
    # the isolated policy phase.
    for _bootstrap_name, _bootstrap_module in list(_bootstrap_sys.modules.items()):
        if _bootstrap_name == "__main__":
            continue
        _bootstrap_file = getattr(_bootstrap_module, "__file__", None)
        if (_bootstrap_name == "yaml" or _bootstrap_name.startswith("yaml.")
                or (_bootstrap_file and _bootstrap_os.path.commonpath([
                    _bootstrap_os.path.realpath(_bootstrap_file),
                    _bootstrap_os.path.realpath(_bootstrap_bin),
                ]) == _bootstrap_os.path.realpath(_bootstrap_bin))):
            _bootstrap_sys.modules.pop(_bootstrap_name, None)

    _bootstrap_os.environ["HARNESS_GUARD_BIN_DIR"] = _bootstrap_bin
    _bootstrap_os.environ["HARNESS_RUN_DIR_GLOBS"] = _bootstrap_globs
    _bootstrap_os.environ["HARNESS_RUN_DIR_DERIVED"] = _bootstrap_derived
    _bootstrap_sys.stdin = _bootstrap_io.StringIO(_bootstrap_payload)

    # THE HOOK'S OWN-FAILURE POSTURE IS harness_boundary.hook_guard (FEAT-65), wired as
    # check-domain.py wires it — see the note there. The policy body below is module-level
    # flow, so the guard wraps its EXECUTION: this process runs the bootstrap once (including
    # the import-path isolation above), then re-runs this file as module
    # `dispatch_guard_body`, under whose name the bootstrap is skipped and the body reads
    # the environment and stdin the bootstrap fixed. The guard module is imported from the
    # same declared bin directory the body imports from. A tree without it runs unguarded.
    _bootstrap_sys.path.insert(0, _bootstrap_os.environ["HARNESS_GUARD_BIN_DIR"])
    try:
        import harness_boundary as _bootstrap_boundary
    except (ImportError, SyntaxError):
        _bootstrap_boundary = None
    if _bootstrap_boundary is not None:
        _bootstrap_sys.exit(_bootstrap_boundary.run_hook_body(__file__, "dispatch-guard", "dispatch_guard_body"))


import sys, json, os

sys.path.insert(0, os.environ.get("HARNESS_GUARD_BIN_DIR") or ".")
import artifact_accessors
try:
    d = artifact_accessors.read_hook_payload(
        sys.stdin.read(), "dispatch-guard hook payload")
except artifact_accessors.ArtifactAccessError as e:
    detail = e.__cause__ if isinstance(
        e.__cause__, json.JSONDecodeError) else e
    print(f"dispatch-guard: unreadable hook payload ({detail}) — passing through.",
          file=sys.stderr)
    sys.exit(0)

agent = d.get("agent_type") or ""
runtime = d.get("harness_runtime") or "claude"
omp_main = (
    agent == "Main"
    and runtime == "omp"
    and d.get("harness_agent_id") == "Main"
    and not d.get("harness_parent_agent_id")
)
if not agent.startswith("harness-") and not omp_main:
    sys.exit(0)  # ungoverned host session or a non-harness agent.

ti = d.get("tool_input") or {}
model = ti.get("model")
if model and not omp_main:
    print(f"dispatch-guard: BLOCKED — {agent} passed model: {model!r} in a dispatch.",
          file=sys.stderr)
    print("  A member runs on the model pinned in its agent frontmatter — that pin is org design",
          file=sys.stderr)
    print("  (DEC-152 tiers), not a dispatch option. If this task genuinely needs a stronger model,",
          file=sys.stderr)
    print("  that is an ESCALATION: raise it in open_questions with the evidence and let it be",
          file=sys.stderr)
    print("  decided above you and recorded (DEC-155). Re-dispatch without the model parameter.",
          file=sys.stderr)
    sys.exit(2)

# ---------------------------------------------------------------------------
# T-08 — the single-flight claim (issue #551). EVERY branch below fails OPEN.
#
# ---------------------------------------------------------------------------
dispatched = ti.get("subagent_type") or ti.get("agent") or ""
if not dispatched.startswith("harness-"):
    # A gap of OURS, said out loud rather than swallowed — the precedent this file already
    # sets above, and that validate-digest.py sets again in its own pass-through line.
    if dispatched:
        print("dispatch-guard: dispatched persona %r is not a harness agent — no claim recorded."
              % (dispatched,), file=sys.stderr)
    else:
        print("dispatch-guard: no dispatched persona on this payload — no claim recorded.",
              file=sys.stderr)
    sys.exit(0)


# ---------------------------------------------------------------------------
# THE DISPATCH DECLARES ITS FEATURE (FEAT-42 T-18, issue #742). This is the ONE site in the
# whole system that can see a dispatch prompt: measured in
# FEAT-31/notes/probe-hook-payload-identity.md, a PreToolUse payload carries eleven keys and
# tool_input.prompt exists only on the DISPATCH payload. So this field fixes this gate and
# reaches no other hook.
#
# THIS IS THE ONE BRANCH HERE THAT FAILS CLOSED. Everything below passes through on its own
# failure, because a guard that blocks every spawn the moment a payload shape changes is
# worse than no guard. This one cannot: the declared feature is the only signal that says
# which checkout an agent was ASSIGNED to, and the agent process working directory does not
# follow its assignment. That is the defect, and a missing declaration is not a degraded
# answer -- it is no answer.
# ---------------------------------------------------------------------------
import re

FEATURE_RE = re.compile(r"(?:FEAT|BUG)-[0-9]+(?:-[a-z0-9]+)+")
prompt = ti.get("prompt") or ti.get("task") or ""
first_line = prompt.splitlines()[0] if prompt.splitlines() else ""
prefix = "HARNESS-FEATURE: "
declared = first_line[len(prefix):] if first_line.startswith(prefix) else ""
if not declared or not FEATURE_RE.fullmatch(declared):
    print("dispatch-guard: BLOCKED — this governed dispatch has no valid first-line feature.",
          file=sys.stderr)
    print("  The FIRST line of the prompt must be, spelled exactly:", file=sys.stderr)
    print("    HARNESS-FEATURE: FEAT-42-one-root-resolver", file=sys.stderr)
    print("  BUG-NN-slug is also valid. A later line or another id form is refused.",
          file=sys.stderr)
    sys.exit(2)

try:
    import harness_boundary as hb
    import inflight_registry as reg
except ImportError as exc:
    print("dispatch-guard: registry libraries unavailable (%s) — passing through." % (exc,),
          file=sys.stderr)
    sys.exit(0)

# BUG-124 T-02 — the run-dir shape check. MUST sit here: it needs hb.run_dir_refs,
# hb.run_dir_slug_ok and hb.run_dir_forms, and it MUST run before the checkout
# resolution and the single-flight claim below — a refusal recorded after a claim
# strands that claim in the registry (D-04). Fails OPEN on its own breakage (no
# vocabulary, unparseable manifest, an exception) — only a POSITIVE finding
# blocks (DEC-100).
#
# NO LOCAL CATCH (FEAT-65): the vocabulary helpers raise nothing of their own, so the
# absorbing `except` here was for defects only; those reach hook_guard, which is the same
# fail-open, said once.
globs = [line for line in (os.environ.get("HARNESS_RUN_DIR_GLOBS") or "").splitlines()
         if line.strip()]
refs = hb.run_dir_refs(prompt)
if refs:
    if not globs:
        if os.environ.get("HARNESS_RUN_DIR_DERIVED") == "0":
            print("dispatch-guard: run-dir shape check SKIPPED -- the manifest declares no "
                  "run-dir write grant, so the slug vocabulary is empty.", file=sys.stderr)
        else:
            print("dispatch-guard: run-dir shape check SKIPPED -- the run-dir vocabulary "
                  "derivation failed (manifest unreadable, unparseable, or PyYAML unavailable "
                  "to that python3).", file=sys.stderr)
    else:
        bad = [ref for ref in refs if not hb.run_dir_slug_ok(ref, globs)]
        if bad:
            forms = hb.run_dir_forms(globs)
            for repo, feature_id, slug in bad:
                tail = ".harness/%s/features/%s/runs/%s" % (repo, feature_id, slug)
                print("dispatch-guard: BLOCKED -- run-dir slug %r cannot be written by any "
                      "squad lead." % (slug,), file=sys.stderr)
                print("  %s" % (tail.replace(".harness/", "[.]harness/"),), file=sys.stderr)
            print("  compliant forms: %s" % (", ".join(forms),), file=sys.stderr)
            print("  the squad suffix trails the purpose -- the parent directory already "
                  "carries the feature id.", file=sys.stderr)
            print("  a run-dir path being quoted rather than directed is spelled with "
                  "[.]harness/ in place of .harness/; the paths above are already in that "
                  "form.", file=sys.stderr)
            sys.exit(2)


# The checkout whose registry holds this dispatch's claims — the one resolver every reader
# uses. BUG-1898: this once matched a linked worktree's basename by EQUALITY, so a
# short-form worktree (`BUG-97` for `BUG-97-short-form`) sent the claim to the owner
# checkout while authorize and validate-digest, which prefix-match through feature_root,
# looked in the worktree. One resolver, one registry.
owner_root = hb.resolve_root(os.environ.get("HARNESS_GUARD_BIN_DIR") or os.getcwd(),
                             strict=False)
root = reg.feature_root(owner_root, declared) if owner_root else None
if not root:
    print("dispatch-guard: no checkout root for this dispatch — no claim recorded.",
          file=sys.stderr)
    sys.exit(0)

# T-09 -- a shell-less persona cannot resolve the feature tree itself. The
# dispatcher supplies the resolved value and this block checks it before claim.
try:
    # owner_root is set: a dispatch with no checkout root exited above.
    tools_file = os.path.join(owner_root, ".omp", "agents", dispatched + ".md")
    raw_agent = open(tools_file, encoding="utf-8").read()
    frontmatter = raw_agent.split("---", 2)[1]
    tools_match = re.search(r"(?ms)^tools:\s*\n(.*?)(?=^[A-Za-z_-]+:|\Z)", frontmatter)
    if tools_match is None:
        raise ValueError("no tools key")
    has_bash = bool(re.search(r"(?m)^\s*-\s*bash\s*$", tools_match.group(1)))
except (OSError, ValueError, IndexError) as exc:
    print("dispatch-guard: could not read tool grants for %s (%s) -- passing through."
          % (dispatched, exc), file=sys.stderr)
    has_bash = True

if not has_bash:
    declared_root = None
    for prompt_line in prompt.splitlines():
        stripped = prompt_line.strip()
        if stripped.startswith("HARNESS-FEATURE-TREE-ROOT: "):
            declared_root = stripped[len("HARNESS-FEATURE-TREE-ROOT: "):]
            break
    if not declared_root:
        print("dispatch-guard: BLOCKED -- %s holds no shell and requires "
              "HARNESS-FEATURE-TREE-ROOT: from inflight_registry.py feature-root --feature %s."
              % (dispatched, declared), file=sys.stderr)
        sys.exit(2)
    if not os.path.isabs(declared_root):
        print("dispatch-guard: BLOCKED -- HARNESS-FEATURE-TREE-ROOT value must be absolute: %r"
              % (declared_root,), file=sys.stderr)
        sys.exit(2)
    try:
        expected_root = hb.worktree_for_feature(owner_root, declared) or owner_root
    except hb.AmbiguousWorktree as exc:
        print("dispatch-guard: BLOCKED -- feature tree for %s is ambiguous (%s)."
              % (declared, exc), file=sys.stderr)
        sys.exit(2)
    else:
        if os.path.realpath(declared_root) != os.path.realpath(expected_root):
            print("dispatch-guard: BLOCKED -- declared feature-tree root %s disagrees with resolver %s."
                  % (declared_root, expected_root), file=sys.stderr)
            sys.exit(2)

# OMP is the only host (DEC-233). A dispatch that does not identify itself as OMP-supervised,
# or carries no supervisor pid, cannot be claimed and so cannot be tracked: single-flight and
# child liveness would be silently off for it. Refuse rather than pass through.
if d.get("harness_runtime") != "omp":
    print("dispatch-guard: BLOCKED — dispatch payload carries no `harness_runtime: omp`; "
          "only the OMP host may dispatch a governed persona (DEC-233).", file=sys.stderr)
    sys.exit(2)
supervisor_pid = d.get("supervisor_pid")
if not isinstance(supervisor_pid, int) or isinstance(supervisor_pid, bool) or supervisor_pid <= 0:
    print("dispatch-guard: BLOCKED — OMP dispatch has no valid supervisor pid, so its claim "
          "could never be verified live (DEC-204).", file=sys.stderr)
    sys.exit(2)

try:
    existing, expired = reg.live_claim(root, dispatched, feature=declared)
    if expired:
        print("dispatch-guard: expired %d stale claim(s) for %s."
              % (expired, dispatched), file=sys.stderr)
    if reg.is_single_flight(dispatched) and existing:
        command = reg.release_cmd(root, dispatched, feature=declared)
        for line in reg.refusal_lines(dispatched, existing, command):
            print(line, file=sys.stderr)
        sys.exit(2)
    receipt = reg.claim_with_receipt(
        root,
        dispatched,
        agent,
        d.get("cwd") or "",
        feature=declared,
        supervisor_pid=supervisor_pid,
    )
    if receipt is None:
        print("dispatch-guard: BLOCKED — single-flight claim raced for %s in %s."
              % (dispatched, declared), file=sys.stderr)
        sys.exit(2)
    print(json.dumps({
        "harness_claim": {
            "root": root,
            "feature": declared,
            "agent": dispatched,
            "claim_id": receipt.get("claim_id"),
        }
    }, sort_keys=True))
except (reg.UnreadableRegistry, reg.harness_merge.MergeRefusal, OSError) as exc:
    # The registry's own failure classes (FEAT-65): unreadable, lock refused, unwritable.
    print("dispatch-guard: claim step failed (%s: %s) — passing through, the dispatch is NOT "
          "blocked." % (type(exc).__name__, exc), file=sys.stderr)
    sys.exit(0)

sys.exit(0)
