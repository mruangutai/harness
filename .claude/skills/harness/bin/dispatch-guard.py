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

# A named subagent is a persistent, addressable peer; the org runs plain subagents whose
# only identity is the persona and the feature line (DEC-233). The playbook says never to
# pass `name:`, and until now nothing checked. Same shape as the `model:` refusal above.
name_param = ti.get("name")
if name_param and not omp_main:
    print(f"dispatch-guard: BLOCKED — {agent} passed name: {name_param!r} in a dispatch.",
          file=sys.stderr)
    print("  Every governed dispatch is a plain subagent addressed by persona and feature",
          file=sys.stderr)
    print("  line; a named peer outlives the tool call and escapes single-flight. Re-dispatch",
          file=sys.stderr)
    print("  without the name parameter.", file=sys.stderr)
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

forbidden_lineage_fields = {
    "agent_id", "parent_agent_id", "harness_agent_id", "harness_parent_agent_id",
}
authored_lineage = sorted(forbidden_lineage_fields.intersection(ti))
if authored_lineage:
    print(
        "dispatch-guard: BLOCKED — task input may not author runtime-lineage fields: %s."
        % (", ".join(authored_lineage),),
        file=sys.stderr,
    )
    sys.exit(2)




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
    # #2010: OMP's task tool hands this gate each task's own `task` text; a batch's shared
    # `context` block never reaches it, so a marker placed only there reads as absent.
    print("  On OMP it goes in EACH task's own `task` text; a shared `context` block is not "
          "read.", file=sys.stderr)
    sys.exit(2)

repository_lines = [
    line[len("HARNESS-REPOSITORY: "):]
    for line in prompt.splitlines()
    if line.startswith("HARNESS-REPOSITORY: ")
]
REPOSITORY_RE = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+")
if (
    len(repository_lines) > 1
    or (repository_lines and not REPOSITORY_RE.fullmatch(repository_lines[0]))
):
    print(
        "dispatch-guard: BLOCKED — HARNESS-REPOSITORY must appear at most once "
        "as an owner-qualified fleet repository.",
        file=sys.stderr,
    )
    sys.exit(2)
declared_repository = repository_lines[0] if repository_lines else None



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


# THE ALLOWLIST. A persona may dispatch only what its own frontmatter `spawns:` names.
# Until now that list was org documentation the playbooks restated as prose ("delegate to a
# lead, never a member"; "no lead is in another lead's spawns"; a task outside your squad
# escalates); the reviewer≠author independence of DEC-175 rests on it. Read from the
# DISPATCHER's file at the owner root. Fails OPEN when that file or its key cannot be read
# (a checkout without the persona is not a violation), loudly; only a persona present in
# the file and absent from its list blocks (DEC-100). `spawns: []` is a real, empty list.
if not omp_main:
    try:
        _owner_root = hb.resolve_root(os.environ.get("HARNESS_GUARD_BIN_DIR") or os.getcwd(),
                                      strict=False)
        _dispatcher_file = os.path.join(_owner_root, ".omp", "agents", agent + ".md")
        _fm = open(_dispatcher_file, encoding="utf-8").read().split("---", 2)[1]
        _m = re.search(r"(?m)^spawns:[ \t]*(\[[^\]\n]*\])?[ \t]*$((?:\n[ \t]*-[^\n]*)*)", _fm)
        if _m is None:
            raise ValueError("no spawns key")
        if _m.group(1) is not None:
            _allowed = [s.strip().strip("'\"") for s in _m.group(1)[1:-1].split(",")
                        if s.strip()]
        else:
            _allowed = [ln.strip()[1:].strip().strip("'\"")
                        for ln in _m.group(2).splitlines() if ln.strip()]
    except (hb.AmbiguousWorktree, OSError, IndexError, ValueError) as exc:
        print("dispatch-guard: spawns allowlist unreadable for %s (%s) -- passing through."
              % (agent, exc), file=sys.stderr)
    else:
        if dispatched not in _allowed:
            print("dispatch-guard: BLOCKED -- %s may not dispatch %s; its spawns: list is %s."
                  % (agent, dispatched, ", ".join(_allowed) or "empty"), file=sys.stderr)
            print("  A persona dispatches only what its frontmatter names. A task owned by",
                  file=sys.stderr)
            print("  another squad is an ESCALATE to the orchestrator, which routes it to the",
                  file=sys.stderr)
            print("  owning lead; a member is reached through its lead, never directly.",
                  file=sys.stderr)
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


def _repository_identity(feature_root, control_root):
    """Validate a repository dispatch against its one fleet-owned feature artifact.

    The artifact is read in `feature_root`, the checkout this dispatch's claim resolves to: a
    new fleet feature's record exists only in its own worktree until it merges, so reading it
    in the main checkout refused every first dispatch (#2104). The fleet declaration is
    control-plane configuration and is read in `control_root`."""
    # GRADE-2 REASON: one preflight keeps the artifact, header and fleet correspondence in
    # one place; splitting it would hide which of the three disagreed.
    harness_dir = os.path.join(feature_root, ".harness")
    artifacts = []
    try:
        segments = os.listdir(harness_dir)
    except OSError:
        segments = []
    for segment in segments:
        if segment in ("harness", "factory"):
            continue
        feature_path = os.path.join(
            harness_dir, segment, "features", declared, "feature.json")
        if not os.path.isfile(feature_path):
            continue
        feature_doc = artifact_accessors.load_feature_json(feature_path)
        if not isinstance(feature_doc, dict):
            raise ValueError("repository-tier feature artifact is not a mapping")
        factory = feature_doc.get("factory")
        repo_name = factory.get("repo") if isinstance(factory, dict) else None
        if feature_doc.get("feature_id") != declared or not isinstance(repo_name, str):
            raise ValueError(
                "repository-tier feature artifact does not bind its feature and factory repo")
        artifacts.append((segment, repo_name))

    if not artifacts:
        if declared_repository:
            raise ValueError(
                "HARNESS-REPOSITORY names no repository-tier feature artifact")
        return None
    if len(artifacts) != 1:
        raise ValueError(
            "repository feature is ambiguous across %d artifacts" % (len(artifacts),))

    segment, artifact_repository = artifacts[0]
    if declared_repository is None:
        raise ValueError(
            "repository-tier feature requires HARNESS-REPOSITORY: %s"
            % (artifact_repository,))
    if declared_repository != artifact_repository:
        raise ValueError(
            "HARNESS-REPOSITORY %s disagrees with feature artifact %s"
            % (declared_repository, artifact_repository))

    import factory_config
    fleet_path = os.path.join(control_root, ".harness", "factory", "fleet.yaml")
    fleet = artifact_accessors.load_fleet(fleet_path)
    factory_config.repo_entry(fleet, declared_repository)
    if factory_config.segment_of(declared_repository) != segment:
        raise ValueError(
            "repository segment %s disagrees with fleet repository %s"
            % (segment, declared_repository))
    return segment


try:
    repository = _repository_identity(root, owner_root)
except (ValueError, OSError, artifact_accessors.FeatureJsonError,
        artifact_accessors.FleetError) as exc:
    print(
        "dispatch-guard: BLOCKED — repository dispatch identity is invalid (%s)."
        % (exc,),
        file=sys.stderr,
    )
    sys.exit(2)



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

# ---------------------------------------------------------------------------
# BUG-2110 (#2110, #2097) — A START WHOSE RETURN CANNOT SUCCEED IS REFUSED HERE, BEFORE ANY
# CLAIM. A lead's digest is bound at run start to exactly one open registered run, and a plan
# reader's review is accepted only while its plan is pending; both used to fail first at the
# return, after the whole run's work. This block asks the SAME questions the return asks —
# digest_destination.registered_destination and validate-digest.py's
# _pending_plan_status_error — never a copy of either. It cannot see runtime identities that
# do not exist yet, and it is not race-free: a run closed or a plan signed after this check
# is still refused at the return, which stays authoritative.
#
# Mission applicability (DEC-228, D-01): a product-lead or validator-lead start, and the plan
# team's scope reader, declares exactly one `HARNESS-MISSION:` line in its own task text — the
# host's marker spelling. An engineering-lead start needs none; its registered run does.
# ---------------------------------------------------------------------------
MISSION_PREFIX = "HARNESS-MISSION:"
MISSION_LINE_RE = re.compile(r"HARNESS-MISSION: ([a-z]+)")
MISSION_LEADS = ("harness-product-lead", "harness-validator-lead")
PLAN_READER = "harness-code-reviewer"
PLAN_TEAM_LEAD = "harness-product-lead"


def _refuse(*lines):
    for line in lines:
        print(line, file=sys.stderr)
    sys.exit(2)


def _declared_mission():
    """This task's own mission declaration as (value, problem)."""
    lines = [line for line in prompt.splitlines() if line.startswith(MISSION_PREFIX)]
    if not lines:
        return None, "has no HARNESS-MISSION line"
    match = MISSION_LINE_RE.fullmatch(lines[0])
    if len(lines) > 1 or match is None:
        return None, ("has conflicting or malformed HARNESS-MISSION lines (%s)"
                      % "; ".join(repr(line) for line in lines))
    return match.group(1), None


def _mission_refusal(problem):
    _refuse(
        "dispatch-guard: BLOCKED — the %s dispatch for %s %s." % (dispatched, declared, problem),
        "  A harness-product-lead or harness-validator-lead start, and the plan team's scope",
        "  reader, carries exactly one line in its own task text, spelled",
        "    HARNESS-MISSION: <phase>",
        "  naming the phase actually dispatched (plan, patch, validate, fix, distill, ...): never a",
        "  phase guessed from the prompt, never a review relabelled to pass. Engineering-lead",
        "  starts need none. Authority: harness-zero-micro-management, the dispatch header.")


def _mission_scope():
    """(must this start declare a mission, is it the plan team's scope-reader route). A code
    reviewer outside that route is held to a mission line only when it carries one."""
    plan_route = dispatched == PLAN_READER and agent == PLAN_TEAM_LEAD
    declares = dispatched == PLAN_READER and any(
        line.startswith(MISSION_PREFIX) for line in prompt.splitlines())
    return dispatched in MISSION_LEADS or plan_route or declares, plan_route


def _start_mission():
    """The declared mission where this start must (or does) declare one, else None."""
    applies, plan_route = _mission_scope()
    if not applies:
        return None
    mission, problem = _declared_mission()
    if problem:
        _mission_refusal(problem)
    if plan_route and mission != "plan":
        _mission_refusal("declares %r; the plan team's scope reader declares plan" % (mission,))
    return mission


def _destinations():
    """digest_destination and the read failures its preflight can raise, or exit 2."""
    try:
        import digest_destination
        import harness_yaml
    except ImportError as exc:
        _refuse("dispatch-guard: BLOCKED — %s cannot start for %s: digest_destination.py, which "
                "establishes its registered run, is unavailable (%s)." % (dispatched, declared, exc))
    return digest_destination, (OSError, ValueError, TypeError, harness_yaml.YamlParseError,
                                artifact_accessors.ArtifactAccessError,
                                artifact_accessors.FeatureJsonError)


def _feature_record(destinations, lead, errors):
    try:
        return os.path.join(destinations._registered_feature(root, declared, lead)[1],
                            "feature.json")
    except errors:
        return "<the feature.json of %s>" % (declared,)


def _run_refusal(destinations, lead, exc, errors):
    squad = destinations.LEAD_SQUADS[lead]
    record = _feature_record(destinations, lead, errors)
    _refuse(
        "dispatch-guard: BLOCKED — %s cannot start for %s: %s." % (lead, declared, exc),
        "  Its return could never be authorized: the hook binds a lead's digest only to exactly",
        "  one matching open registered run (agent %s, squad %s, verdict PENDING, no ended_at)."
        % (lead, squad),
        "  No matching open run: register it before dispatching, with a run id the lead's run-dir",
        "  grant covers —",
        "    feature-record.py run-start --file %s --id <run-id> --squad %s --agent %s"
        % (record, squad, lead),
        "  More than one: inspect runs[] in %s and close each surplus open run with" % (record,),
        "  its real outcome (feature-record.py close-run, or run-end) so exactly one matching",
        "  open run remains. Deleting runs[] entries or freeing in-flight claims is no substitute.")


def _registered_digest(destinations, lead, errors):
    """The lead's registered run digest, or exit 2 with the failure and its remedy."""
    try:
        return destinations.registered_destination(root, declared, lead)[1]
    except destinations.AuthorizationError as exc:
        _run_refusal(destinations, lead, exc, errors)
    except errors as exc:
        _refuse("dispatch-guard: BLOCKED — %s cannot start for %s: its registered run could not "
                "be established (%s: %s)." % (lead, declared, type(exc).__name__, exc),
                "  The feature.json record and the team-config.yaml grants must be readable "
                "before a lead starts; repair the named file, then re-dispatch.")


def _validator_path():
    """sys.path for loading validate-digest.py: the policy path plus user-site entries LAST.

    The policy phase drops user-site entries (the former `python3 -I`) so nothing there can
    shadow a trusted module, but validate-digest.py imports digest_schema, whose jsonschema
    may be installed only in user site — where the hook that runs validate-digest.py finds it.
    Appended after every trusted entry, a user-site package can only supply a module nothing
    earlier provides; the caller restores the policy path afterwards."""
    import site
    sites = site.getusersitepackages() if site.ENABLE_USER_SITE else []
    sites = [sites] if isinstance(sites, str) else list(sites)
    return list(sys.path) + [entry for entry in sites if entry not in sys.path]


def _plan_status_error(target):
    """validate-digest.py's own pending-plan answer for `target`, loaded once, or exit 2."""
    script = os.path.join(os.environ.get("HARNESS_GUARD_BIN_DIR") or ".", "validate-digest.py")
    policy_path = list(sys.path)
    sys.path[:] = _validator_path()
    try:
        validator = hb.load_repo_module("validate_digest", script, register=True)
        return validator._pending_plan_status_error(target)
    except (hb.RepoModuleError, OSError, ValueError) as exc:
        _refuse("dispatch-guard: BLOCKED — the approval status of %s could not be established: "
                "validate-digest.py is unavailable or failed (%s)." % (target, exc))
    finally:
        sys.path[:] = policy_path


def _plan_preflight(destination):
    """Refuse a plan panel whose canonical plan.yaml (beside the registered feature.json) is
    not pending; only the product plan team may start before the plan exists, to draft it."""
    feature_dir = os.path.dirname(os.path.dirname(os.path.dirname(destination)))
    target = os.path.realpath(os.path.join(feature_dir, "plan.yaml"))
    if not os.path.exists(target):
        if dispatched == PLAN_TEAM_LEAD:
            return
        _refuse("dispatch-guard: BLOCKED — %s plan-panel start for %s: no plan exists at %s."
                % (dispatched, declared, target),
                "  A standalone plan panel or scope reader reviews an existing pending plan; the "
                "product plan team drafts it first.")
    error = _plan_status_error(target)
    if error:
        _refuse(
            "dispatch-guard: BLOCKED — %s plan-panel start for %s refused before any work: %s"
            % (dispatched, declared, error),
            "  Target: %s, the canonical plan.yaml beside the registered feature.json." % (target,),
            "  Plan panels run before signature: a plan review is accepted only while its plan is",
            "  pending, so every return of this panel would be refused at yield. Return to the",
            "  legitimate pending-plan phase: a signed plan that genuinely needs changes takes the",
            "  DEC-229 task-set amendment, whose plan-merge.py receipt returns approval to pending,",
            "  and the panel runs before the renewed signature.")


def _reader_preflight(destinations, errors, _mission):
    """A plan scope reader's target is named by its dispatching lead's registered run."""
    if agent not in destinations.LEAD_SQUADS:
        _refuse("dispatch-guard: BLOCKED — a plan scope reader for %s is dispatched by the "
                "lead hosting the panel, whose registered run names the plan; %s is not one."
                % (declared, agent))
    _plan_preflight(_registered_digest(destinations, agent, errors))


def _lead_preflight(destinations, errors, mission):
    """Every lead needs its registered run; a product or validator plan panel, a pending plan."""
    if dispatched not in destinations.LEAD_SQUADS:
        return
    destination = _registered_digest(destinations, dispatched, errors)
    if mission == "plan" and dispatched in MISSION_LEADS:
        _plan_preflight(destination)


def _start_preflight():
    """BUG-2110: refuse, before any claim, a lead or plan-reader start whose return the
    return-time gates would refuse for a reason already true now."""
    reader = dispatched == PLAN_READER
    if not (dispatched.endswith("-lead") or reader):
        return
    mission = _start_mission()
    if reader and mission != "plan":
        return
    destinations, errors = _destinations()
    (_reader_preflight if reader else _lead_preflight)(destinations, errors, mission)


_start_preflight()

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
        repository=repository,
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
