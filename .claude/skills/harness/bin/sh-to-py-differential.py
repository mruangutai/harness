#!/usr/bin/env python3
"""Prove a .sh -> .py conversion changed no observable behaviour (issue #1674).

WHY THIS EXISTS AND WHY IT IS A SCRIPT, NOT A TEST. The conversion moves ~6,600
lines of Python out of `.sh` heredocs where no Python tool can read them. Every
one of those files is a gate, a validator or a CLI whose exit code routes control
flow, so "it still works" is not a judgement anyone should make by reading a diff.
This captures what a caller can observe -- exit status, stdout, stderr -- across a
corpus of real inputs BEFORE the move, replays it after, and requires the two to
be identical byte for byte.

It is deliberately a throwaway proof rather than a permanent suite. A test that
asserts "the old and new implementations agree" has no meaning once the old one is
deleted, and keeping it would be exactly the parity-harness mistake BUG-285 made:
policing two implementations instead of having one.

USAGE
  capture:  sh-to-py-differential.py capture <tool> <baseline.json>
  verify:   sh-to-py-differential.py verify  <tool> <baseline.json>

`<tool>` is a bare name such as `check-expertise`; the runner resolves
`<tool>.sh` when capturing and `<tool>.py` when verifying, so the SAME corpus
runs against both. A corpus case that crashes the runner is a FAILED case, never
a skipped one -- a proof that can silently cover nothing is worse than no proof.
"""
import json
import os
import shutil
import subprocess
import re
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(BIN, "..", "..", "..", ".."))


def domain_corpus(scratch):
    """Representative route, mode, stdin, environment and cwd cases."""
    root = os.path.join(scratch, "domain-root")
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    manifest = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: allowed/**, upsert: true }
shared:
  - { path: package.json }
"""
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w", encoding="utf-8") as fh:
        fh.write(manifest)

    allowed = os.path.join(root, "allowed", "note.md")
    denied = os.path.join(root, "src", "app.py")
    state = os.path.join(root, ".harness", "harness", "features", "FEAT-X", "STATE.md")
    os.makedirs(os.path.dirname(state), exist_ok=True)
    with open(state, "w", encoding="utf-8") as fh:
        fh.write("## Current\nok\n## Illegal\nno\n")

    project_override = "HARNESS" + "_PROJECT_DIR"
    root_env = {project_override: root}

    def hook_payload(path, *, agent="harness-documentor", event=None, content="ok\n"):
        payload = {"tool_name": "Write",
                   "tool_input": {"file_path": path, "content": content}}
        if agent is not None:
            payload["agent_type"] = agent
        if event is not None:
            payload["hook_event_name"] = event
        return json.dumps(payload)

    denied_payload = hook_payload(denied)
    invalid_state = hook_payload(
        state, agent=None, content="## Current\nok\n## Illegal\nno\n")
    post_state = hook_payload(state, event="PostToolUse")
    return [
        {"label": "resolve granted path", "argv": ["--resolve", allowed],
         "env": root_env},
        {"label": "resolve path outside every base",
         "argv": ["--resolve", os.path.join(scratch, "outside.txt")],
         "env": root_env},
        {"label": "pre-hook allowed write", "stdin": hook_payload(allowed),
         "env": root_env},
        {"label": "pre-hook denied write", "stdin": denied_payload,
         "env": root_env},
        {"label": "pre-hook clears inherited resolve mode", "stdin": denied_payload,
         "env": {**root_env, "HARNESS_RESOLVE_PATH": ""}},
        {"label": "legacy argv agent fallback", "argv": ["harness-documentor"],
         "stdin": hook_payload(denied, agent=None), "env": root_env},
        {"label": "main-session shape refusal", "stdin": invalid_state,
         "env": root_env},
        {"label": "post mode selected by argv", "argv": ["--post"],
         "stdin": hook_payload(state), "env": root_env},
        {"label": "post mode selected by event", "stdin": post_state,
         "env": root_env},
        {"label": "malformed hook payload", "stdin": "{not json",
         "env": root_env},
        {"label": "cwd-independent denied write", "stdin": denied_payload,
         "cwd": scratch, "env": root_env},
        {"label": "unconfigured isolated copy", "stdin": denied_payload,
         "isolate": True,
         "env": {project_override: None}},
    ]


def bash_guard_corpus(scratch):
    """Representative identity, command, domain, parser and cwd cases."""
    root = os.path.join(scratch, "bash-root")
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    manifest = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain:
          - { path: allowed/**, upsert: true }
shared:
  - { path: package.json }
"""
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w",
              encoding="utf-8") as fh:
        fh.write(manifest)

    malformed_root = os.path.join(scratch, "malformed-root")
    os.makedirs(os.path.join(malformed_root, ".harness"), exist_ok=True)
    with open(os.path.join(malformed_root, ".harness", "team-config.yaml"), "w",
              encoding="utf-8") as fh:
        fh.write("teams: [ {name: broken ## eaten\nnext_key: 1\n")

    allowed = os.path.join(root, "allowed", "note.md")
    denied = os.path.join(root, "src", "app.py")
    shared = os.path.join(root, "package.json")
    project_override = "HARNESS" + "_PROJECT_DIR"
    root_env = {project_override: root}

    def payload(command, agent="harness-backend-dev"):
        data = {"tool_name": "Bash", "tool_input": {"command": command}}
        if agent is not None:
            data["agent_type"] = agent
        return json.dumps(data)

    denied_command = f"printf changed > {denied}"
    return [
        {"label": "malformed hook payload", "stdin": "{not json", "env": root_env},
        {"label": "main session is ungoverned", "stdin": payload(denied_command, None),
         "env": root_env},
        {"label": "non-harness agent is ungoverned",
         "stdin": payload(denied_command, "custom-agent"), "env": root_env},
        {"label": "read-only command has no finding",
         "stdin": payload(f"cat {denied}"), "env": root_env},
        {"label": "governed in-domain redirect",
         "stdin": payload(f"printf changed > {allowed}"), "env": root_env},
        {"label": "governed out-of-domain redirect",
         "stdin": payload(denied_command), "env": root_env},
        {"label": "reviewer write refusal",
         "stdin": payload(denied_command, "harness-code-reviewer"), "env": root_env},
        {"label": "shared-path write warning",
         "stdin": payload(f"printf changed > {shared}"), "env": root_env},
        {"label": "literal Python open write",
         "stdin": payload(f"python3 -c 'open({denied!r}, \"w\").write(\"x\")'"),
         "env": root_env},
        {"label": "dev-ops write exemption",
         "stdin": payload(denied_command, "harness-dev-ops"), "env": root_env},
        {"label": "dev-ops still cannot move HEAD",
         "stdin": payload("git checkout main", "harness-dev-ops"), "env": root_env},
        {"label": "malformed manifest refuses",
         "stdin": payload(f"printf changed > {os.path.join(malformed_root, 'x.txt')}"),
         "env": {project_override: malformed_root}},
        {"label": "cwd-independent denial", "stdin": payload(denied_command),
         "cwd": scratch, "env": root_env},
        {"label": "unconfigured isolated copy", "stdin": payload(denied_command),
         "isolate": True, "env": {project_override: None}},
    ]


def dispatch_guard_corpus(scratch):
    """Representative parse, identity, model, feature and run-dir cases."""
    project_override = "HARNESS" + "_PROJECT_DIR"
    root_env = {project_override: ROOT}
    feature_line = "HARNESS-FEATURE: BUG-1674-sh-to-py"
    with open(os.path.join(scratch, "harness_boundary.py"), "w",
              encoding="utf-8") as fh:
        fh.write("raise RuntimeError('cwd shadow imported')\n")

    def payload(*, agent="harness-eng-lead", dispatched="harness-backend-dev",
                model=None, prompt=feature_line, runtime=None, supervisor_pid=None):
        tool_input = {"subagent_type": dispatched, "prompt": prompt}
        if model is not None:
            tool_input["model"] = model
        data = {"tool_name": "Task", "tool_input": tool_input}
        if agent is not None:
            data["agent_type"] = agent
        if runtime is not None:
            data["harness_runtime"] = runtime
        if supervisor_pid is not None:
            data["supervisor_pid"] = supervisor_pid
        return json.dumps(data)

    invalid_run = (
        feature_line + "\nwrite .harness/harness/features/BUG-1674-sh-to-py/"
        "runs/eng-t01/digest.md")
    return [
        {"label": "malformed hook payload", "stdin": "{not json", "env": root_env},
        {"label": "main session model is ungoverned",
         "stdin": payload(agent=None, model="opus"), "env": root_env},
        {"label": "non-harness dispatcher is ungoverned",
         "stdin": payload(agent="custom-agent", model="opus"), "env": root_env},
        {"label": "governed model override refusal",
         "stdin": payload(model="opus"), "env": root_env},
        {"label": "missing dispatched persona passes through",
         "stdin": payload(dispatched=""), "env": root_env},
        {"label": "missing feature declaration refuses",
         "stdin": payload(prompt="build it"), "env": root_env},
        {"label": "invalid run-dir slug refuses",
         "stdin": payload(agent="harness-orchestrator",
                          dispatched="harness-eng-lead", prompt=invalid_run),
         "env": root_env},
        {"label": "OMP dispatch without supervisor passes through",
         "stdin": payload(runtime="omp"), "env": root_env},
        {"label": "stray argv remains ignored", "argv": ["unexpected"],
         "stdin": payload(model="opus"), "env": root_env},
        {"label": "cwd-independent model refusal", "stdin": payload(model="opus"),
         "cwd": scratch, "env": root_env},
        {"label": "cwd module shadow is ignored",
         "stdin": payload(runtime="omp"), "cwd": scratch, "env": root_env},
        {"label": "unconfigured isolated copy",
         "stdin": payload(runtime="omp"), "isolate": True,
         "env": {project_override: None}},
    ]


def branch_create_gate_corpus(scratch):
    """Representative config, parser, branch grammar and GitHub cases."""
    project_override = "HARNESS" + "_PROJECT_DIR"

    def make_root(name, github):
        root = os.path.join(scratch, name)
        harness = os.path.join(root, ".harness")
        os.makedirs(harness, exist_ok=True)
        with open(os.path.join(harness, "team-config.yaml"), "w",
                  encoding="utf-8") as fh:
            fh.write("agents: {}\n")
        document = {} if github is None else {"github": github}
        with open(os.path.join(harness, "harness.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(document, fh)
        return root

    enabled = make_root(
        "branch-enabled", {"sync": True, "repo": "owner/repo"})
    os.makedirs(os.path.join(
        enabled, ".harness", "harness", "features",
        "FEAT-1674-existing"), exist_ok=True)
    disabled = make_root("branch-disabled", {"sync": False, "repo": "owner/repo"})
    absent = make_root("branch-absent", None)
    unpinned = make_root("branch-unpinned", {"sync": True})
    malformed = make_root("branch-malformed", None)
    with open(os.path.join(malformed, ".harness", "harness.json"), "w",
              encoding="utf-8") as fh:
        fh.write("{not json")
    invalid_shape = make_root("branch-invalid-shape", "not-a-mapping")
    with open(os.path.join(scratch, "harness_boundary.py"), "w",
              encoding="utf-8") as fh:
        fh.write("raise RuntimeError('cwd shadow imported')\n")

    def gh_mock(name, state, auth_ok):
        path = os.path.join(scratch, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(
                "#!/usr/bin/env python3\n"
                "import sys\n"
                f"state = {state!r}\n"
                "if sys.argv[1:3] == ['issue', 'view']:\n"
                "    if state:\n"
                "        print(state)\n"
                "    raise SystemExit(0)\n"
                "if sys.argv[1:3] == ['auth', 'status']:\n"
                f"    raise SystemExit({0 if auth_ok else 1})\n"
                "raise SystemExit(2)\n")
        os.chmod(path, 0o755)
        return path

    gh_open = gh_mock("gh-open", "OPEN", True)
    gh_closed = gh_mock("gh-closed", "CLOSED", True)
    gh_missing = gh_mock("gh-missing", "", True)
    gh_unauthenticated = gh_mock("gh-unauthenticated", "", False)

    def payload(command):
        return json.dumps({"tool_name": "Bash",
                           "tool_input": {"command": command}})

    def env(root, gh=None):
        return {project_override: root, "GH_BIN": gh}

    enabled_env = env(enabled)
    flow_missing = payload("git checkout -b feat/FEAT-1674-missing")
    return [
        {"label": "sync absent passes through",
         "stdin": flow_missing, "env": env(absent)},
        {"label": "sync false passes through",
         "stdin": flow_missing, "env": env(disabled)},
        {"label": "sync enabled without pinned repo passes through",
         "stdin": flow_missing, "env": env(unpinned)},
        {"label": "malformed config passes through",
         "stdin": flow_missing, "env": env(malformed)},
        {"label": "invalid github shape preserves helper failure",
         "stdin": flow_missing, "env": env(invalid_shape)},
        {"label": "malformed hook payload",
         "stdin": "{not json", "env": enabled_env},
        {"label": "non-branch command passes through",
         "stdin": payload("git status --short"), "env": enabled_env},
        {"label": "missing flow denies",
         "stdin": flow_missing, "env": enabled_env},
        {"label": "existing flow allows",
         "stdin": payload("git checkout -b feat/FEAT-1674-existing"),
         "env": enabled_env},
        {"label": "switch create flow allows",
         "stdin": payload("git -C /tmp switch --create=feat/FEAT-1674-existing"),
         "env": enabled_env},
        {"label": "worktree add flow allows",
         "stdin": payload(
             "git worktree add /tmp/branch-proof -B feat/FEAT-1674-existing"),
         "env": enabled_env},
        {"label": "branch command flow allows",
         "stdin": payload("git branch feat/FEAT-1674-existing"),
         "env": enabled_env},
        {"label": "untracked branch name denies",
         "stdin": payload("git checkout -b scratch/no-ticket"),
         "env": enabled_env},
        {"label": "issue branch without gh denies",
         "stdin": payload("git checkout -b fix/123-typo"),
         "env": env(enabled, "/no/such/gh")},
        {"label": "open issue branch allows",
         "stdin": payload("git checkout -b fix/123-typo"),
         "env": env(enabled, gh_open)},
        {"label": "closed issue branch denies",
         "stdin": payload("git checkout -b fix/123-typo"),
         "env": env(enabled, gh_closed)},
        {"label": "missing issue denies",
         "stdin": payload("git checkout -b fix/123-typo"),
         "env": env(enabled, gh_missing)},
        {"label": "unauthenticated gh denies",
         "stdin": payload("git checkout -b fix/123-typo"),
         "env": env(enabled, gh_unauthenticated)},
        {"label": "stray argv remains ignored", "argv": ["unexpected"],
         "stdin": flow_missing, "env": enabled_env},
        {"label": "cwd-independent flow denial",
         "stdin": flow_missing, "cwd": scratch, "env": enabled_env},
        {"label": "unconfigured isolated copy", "stdin": flow_missing,
         "isolate": True, "env": {project_override: None, "GH_BIN": None}},
    ]


def plan_sign_gate_corpus(scratch):
    """Representative identity, gated verb, parser, root and isolation cases."""
    project_override = "HARNESS" + "_PROJECT_DIR"
    root = os.path.join(scratch, "plan-sign-root")
    os.makedirs(os.path.join(root, ".harness"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w",
              encoding="utf-8") as fh:
        fh.write("agents: {}\n")
    with open(os.path.join(root, ".harness", "harness.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"schema_version": 1}, fh)
    shadow = os.path.join(scratch, "shadow")
    os.makedirs(shadow)
    with open(os.path.join(shadow, "harness_boundary.py"), "w",
              encoding="utf-8") as fh:
        fh.write("raise RuntimeError('PYTHONPATH shadow imported')\n")
    root_env = {project_override: root}

    def payload(command, agent=None):
        data = {"tool_name": "Bash", "tool_input": {"command": command}}
        if agent is not None:
            data["agent_type"] = agent
        return json.dumps(data)

    sign = (
        "python3 .claude/skills/harness/bin/plan-merge.py "
        "sign-approval --file p.yaml")
    return [
        {"label": "malformed hook payload", "stdin": "{not json",
         "env": root_env},
        {"label": "main session may sign", "stdin": payload(sign),
         "env": root_env},
        {"label": "agent sign approval denies",
         "stdin": payload(sign, "harness-orchestrator"), "env": root_env},
        {"label": "operator cycle raise denies",
         "stdin": payload(
             "python3 feature-record.py raise-cycles --file feature.json",
             "harness-orchestrator"), "env": root_env},
        {"label": "ordinary command allows",
         "stdin": payload("git status --short", "harness-orchestrator"),
         "env": root_env},
        {"label": "open plan mutation allows",
         "stdin": payload(
             "python3 plan-merge.py set-task-station --file p.yaml",
             "harness-orchestrator"), "env": root_env},
        {"label": "nested sign command denies",
         "stdin": payload(
             f"bash -c '{sign}'", "harness-orchestrator"),
         "env": root_env},
        {"label": "unlexable sign fallback denies",
         "stdin": payload(
             f"echo it's fine; {sign}", "harness-orchestrator"),
         "env": root_env},
        {"label": "stray argv remains ignored", "argv": ["unexpected"],
         "stdin": payload(sign, "harness-orchestrator"), "env": root_env},
        {"label": "cwd-independent denial ignores module shadow",
         "stdin": payload(sign, "harness-orchestrator"), "cwd": scratch,
         "env": {**root_env, "PYTHONPATH": shadow}},
        {"label": "unconfigured isolated copy refuses",
         "stdin": payload(sign, "harness-orchestrator"), "isolate": True,
         "env": {project_override: None, "PYTHONPATH": shadow}},
    ]


def _gh_close_denial_cases(payload, enabled_env, direct_close):
    return [
        {"label": "malformed hook payload", "stdin": "{not json",
         "env": enabled_env},
        {"label": "direct issue close denies", "stdin": direct_close,
         "env": enabled_env},
        {"label": "REST state close denies",
         "stdin": payload(
             "gh api -X PATCH repos/owner/repo/issues/1674 -f state=closed"),
         "env": enabled_env},
        {"label": "GraphQL close mutation denies",
         "stdin": payload(
             "gh api graphql -f query='mutation{closeIssue(input:{issueId:\"x\"}){clientMutationId}}'"),
         "env": enabled_env},
        {"label": "opaque REST mutation denies",
         "stdin": payload(
             "gh api --method PATCH repos/owner/repo/issues/1674 --input -"),
         "env": enabled_env},
        {"label": "nested close command denies",
         "stdin": payload("bash -c 'gh issue close 1674'"),
         "env": enabled_env},
        {"label": "unlexable close fallback denies",
         "stdin": payload("echo it's here; gh issue close 1674"),
         "env": enabled_env},
        {"label": "unlexable ordinary command allows",
         "stdin": payload("echo it's fine"), "env": enabled_env},
        {"label": "ordinary command allows",
         "stdin": payload("git status --short"), "env": enabled_env},
    ]


def _gh_close_config_cases(direct_close, env, disabled, absent, malformed,
                           invalid_shape):
    return [
        {"label": "sync false allows close", "stdin": direct_close,
         "env": env(disabled)},
        {"label": "missing config allows close", "stdin": direct_close,
         "env": env(absent)},
        {"label": "malformed config allows close", "stdin": direct_close,
         "env": env(malformed)},
        {"label": "invalid github shape preserves failure",
         "stdin": direct_close, "env": env(invalid_shape)},
    ]


def _gh_close_boundary_cases(direct_close, payload, env, enabled, scratch,
                             shadow, project_override):
    return [
        {"label": "stray argv remains ignored", "argv": ["unexpected"],
         "stdin": direct_close, "env": env(enabled)},
        {"label": "cwd-independent denial ignores module shadow",
         "stdin": direct_close, "cwd": scratch,
         "env": env(enabled, PYTHONPATH=shadow)},
        {"label": "unconfigured isolated copy refuses",
         "stdin": direct_close, "isolate": True,
         "env": {project_override: None, "PYTHONPATH": shadow}},
    ]


def gh_close_gate_corpus(scratch):
    """Representative config, close parser, root and isolation cases."""
    project_override = "HARNESS" + "_PROJECT_DIR"

    def make_root(name, github=None, *, config=True, raw=None):
        root = os.path.join(scratch, name)
        harness = os.path.join(root, ".harness")
        os.makedirs(harness)
        with open(os.path.join(harness, "team-config.yaml"), "w",
                  encoding="utf-8") as fh:
            fh.write("agents: {}\n")
        if config:
            with open(os.path.join(harness, "harness.json"), "w",
                      encoding="utf-8") as fh:
                if raw is None:
                    json.dump({"github": github}, fh)
                else:
                    fh.write(raw)
        return root

    enabled = make_root(
        "gh-close-enabled", {"sync": True, "repo": "owner/repo"})
    disabled = make_root(
        "gh-close-disabled", {"sync": False, "repo": "owner/repo"})
    absent = make_root("gh-close-absent", config=False)
    malformed = make_root("gh-close-malformed", raw="{not json")
    invalid_shape = make_root("gh-close-invalid-shape", "not-a-mapping")
    shadow = os.path.join(scratch, "shadow")
    os.makedirs(shadow)
    with open(os.path.join(shadow, "harness_boundary.py"), "w",
              encoding="utf-8") as fh:
        fh.write("raise RuntimeError('PYTHONPATH shadow imported')\n")

    def payload(command):
        return json.dumps({"tool_name": "Bash",
                           "tool_input": {"command": command}})

    def env(root, **extra):
        return {project_override: root, **extra}

    direct_close = payload("gh issue close 1674 --repo owner/repo")
    enabled_env = env(enabled)
    return (
        _gh_close_denial_cases(payload, enabled_env, direct_close)
        + _gh_close_config_cases(
            direct_close, env, disabled, absent, malformed, invalid_shape)
        + _gh_close_boundary_cases(
            direct_close, payload, env, enabled, scratch, shadow,
            project_override)
    )


def merge_gate_corpus(scratch):
    """Representative merge parsing, receipt, root and isolation cases."""
    project_override = "HARNESS" + "_PROJECT_DIR"

    def make_root(name, *, entry=None, repo="acme/widgets", sync=True,
                  feature="FEAT-9001-fixture-non-era"):
        root = os.path.join(scratch, name)
        harness = os.path.join(root, ".harness")
        os.makedirs(harness, exist_ok=True)
        with open(os.path.join(harness, "team-config.yaml"), "w",
                  encoding="utf-8") as fh:
            fh.write("agents: {}\n")
        with open(os.path.join(harness, "harness.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"github": {"sync": sync, "repo": repo}}, fh)
        feat_dir = os.path.join(
            harness, "harness", "features", feature)
        os.makedirs(feat_dir)
        github = {} if entry is None else {"build_entry": entry}
        with open(os.path.join(feat_dir, "feature.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"feature_id": feature, "branch": "feature/test",
                       "github": github}, fh)
        with open(os.path.join(feat_dir, "plan.yaml"), "w",
                  encoding="utf-8") as fh:
            fh.write("status: plan\ntasks: []\n")
        return root

    recovery = make_root("merge-recovery", entry="recovery-required")
    absent = make_root("merge-absent")
    opened = make_root("merge-opened", entry="opened")
    disabled = make_root("merge-disabled", sync=False)
    unpinned = make_root("merge-unpinned", repo=None)
    era = make_root(
        "merge-era", feature="BUG-1030-stale-anchor-write-hazard")
    shadow = os.path.join(scratch, "shadow")
    os.makedirs(shadow)
    with open(os.path.join(shadow, "harness_boundary.py"), "w",
              encoding="utf-8") as fh:
        fh.write("raise RuntimeError('PYTHONPATH shadow imported')\n")

    def payload(command):
        return json.dumps({"tool_name": "Bash",
                           "tool_input": {"command": command}})

    def env(root, **extra):
        return {project_override: root, **extra}

    merge = payload("git merge feature/test")
    return [
        {"label": "malformed hook payload", "stdin": "{not json",
         "env": env(recovery)},
        {"label": "non-merge command passes through",
         "stdin": payload("git status --short"), "env": env(recovery)},
        {"label": "recovery-required receipt denies",
         "stdin": merge, "env": env(recovery)},
        {"label": "absent receipt denies", "stdin": merge,
         "env": env(absent)},
        {"label": "opened receipt allows", "stdin": merge,
         "env": env(opened)},
        {"label": "sync false allows", "stdin": merge,
         "env": env(disabled)},
        {"label": "unpinned repository denies", "stdin": merge,
         "env": env(unpinned)},
        {"label": "era-exempt feature allows with notice", "stdin": merge,
         "env": env(era)},
        {"label": "nested merge command denies",
         "stdin": payload("bash -c 'git merge feature/test'"),
         "env": env(recovery)},
        {"label": "stray argv remains ignored", "argv": ["unexpected"],
         "stdin": merge, "env": env(recovery)},
        {"label": "cwd-independent denial ignores module shadow",
         "stdin": merge, "cwd": scratch,
         "env": env(recovery, PYTHONPATH=shadow)},
        {"label": "unconfigured isolated copy refuses", "stdin": merge,
         "isolate": True,
         "env": {project_override: None, "PYTHONPATH": shadow}},
    ]


def _write_runner_modules(bin_dir):
    with open(os.path.join(bin_dir, "suite_layout.py"), "w",
              encoding="utf-8") as fh:
        fh.write(
            "import os\n"
            "def violations(root):\n"
            "    return ['unit layout broken', 'integration layout broken'] "
            "if os.environ.get('LAYOUT_MODE') == 'bad' else []\n")
    with open(os.path.join(bin_dir, "run_pool.py"), "w",
              encoding="utf-8") as fh:
        fh.write(
            "import json, os, sys\n"
            "def main(argv=None):\n"
            "    args = sys.argv[1:] if argv is None else argv\n"
            "    print(json.dumps(args))\n"
            "    return int(os.environ.get('POOL_EXIT', '0'))\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n")


def _write_runner_tests(root):
    for kind, names in (
            ("unit", ("test-alpha.py", "test-zeta.py")),
            ("integration", ("test-beta.py",))):
        directory = os.path.join(root, "tests", kind)
        os.makedirs(directory)
        for name in names:
            with open(os.path.join(directory, name), "w",
                      encoding="utf-8") as fh:
                fh.write("raise SystemExit(0)\n")


def _run_unit_fixture(scratch):
    root = os.path.join(scratch, "run-unit-root")
    harness = os.path.join(root, ".harness")
    bin_dir = os.path.join(root, ".claude", "skills", "harness", "bin")
    os.makedirs(harness)
    os.makedirs(bin_dir)
    with open(os.path.join(harness, "team-config.yaml"), "w",
              encoding="utf-8") as fh:
        fh.write("teams: []\n")
    _write_runner_modules(bin_dir)
    _write_runner_tests(root)
    return root


def run_unit_tests_corpus(scratch):
    """Argument, layout, selection, pool and root cases for the suite runner."""
    project_override = "HARNESS" + "_PROJECT_DIR"
    root = _run_unit_fixture(scratch)
    root_env = {project_override: root}
    return [
        {"label": "default runs both kinds", "env": root_env},
        {"label": "unit kind selects unit scripts",
         "argv": ["--kind", "unit"], "env": root_env},
        {"label": "integration kind selects integration scripts",
         "argv": ["--kind", "integration"], "env": root_env},
        {"label": "missing kind value defaults to all",
         "argv": ["--kind"], "env": root_env},
        {"label": "extra kind arguments remain ignored",
         "argv": ["--kind", "unit", "unexpected"], "env": root_env},
        {"label": "layout-only exits without pool",
         "argv": ["--check-layout"], "env": root_env},
        {"label": "layout findings refuse before pool",
         "argv": ["--kind", "unit"],
         "env": {**root_env, "LAYOUT_MODE": "bad"}},
        {"label": "unknown kind refuses",
         "argv": ["--kind", "functional"], "env": root_env},
        {"label": "unexpected first argument refuses",
         "argv": ["unexpected"], "env": root_env},
        {"label": "pool exit status is preserved",
         "argv": ["--kind", "integration"],
         "env": {**root_env, "POOL_EXIT": "7"}},
        {"label": "cwd-independent suite selection",
         "argv": ["--kind", "unit"], "cwd": scratch, "env": root_env},
        {"label": "unconfigured isolated copy refuses",
         "argv": ["--check-layout"], "isolate": True,
         "env": {project_override: None}},
    ]


def _write_expertise_fixture(path, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)


def _expertise_root(scratch, name, config="agents: {}\n"):
    root = os.path.join(scratch, name)
    _write_expertise_fixture(
        os.path.join(root, ".harness", "team-config.yaml"), config)
    return root


def _write_instruction_checker(root):
    checker = os.path.join(
        root, ".claude", "skills", "harness", "bin",
        "check-instruction-paths.py")
    _write_expertise_fixture(
        checker,
        "#!/usr/bin/env python3\n"
        "import os\n"
        "mode = os.environ.get('CHECKER_MODE', 'clean')\n"
        "if mode == 'clean':\n"
        "    print('scanned 4 file(s), 0 violation(s)')\n"
        "    raise SystemExit(0)\n"
        "if mode == 'drift':\n"
        "    for n in range(1, 8):\n"
        "        print(f'VIOLATION .omp/agents/harness-qa.md:{n}: bad')\n"
        "    raise SystemExit(1)\n"
        "print('checker unavailable')\n"
        "raise SystemExit(3)\n")


def _tiered_expertise_root(scratch, agent):
    root = _expertise_root(scratch, "expertise-tiers")
    _write_expertise_fixture(
        os.path.join(root, ".harness", "expertise", f"{agent}.md"),
        "PROJECT BODY\n")
    for segment, body in (
            ("zeta", "ZETA BODY\n"), ("alpha", "ALPHA BODY\n"),
            ("Not-Valid", "MUST NOT APPEAR\n")):
        _write_expertise_fixture(
            os.path.join(root, ".harness", segment, "expertise", f"{agent}.md"),
            body)
    dangling = os.path.join(
        root, ".harness", "broken", "expertise", f"{agent}.md")
    os.makedirs(os.path.dirname(dangling))
    os.symlink(os.path.join(scratch, "missing-expertise.md"), dangling)
    return root


def _capped_expertise_root(scratch, agent):
    root = _expertise_root(scratch, "expertise-caps")
    bodies = (
        ("", "".join(f"craft line {number}\n" for number in range(1, 152))),
        ("repo", "".join(f"repo line {number}\n" for number in range(1, 42))),
        ("nonewline", "\n".join(
            f"partial line {number}" for number in range(1, 42))),
    )
    for segment, body in bodies:
        middle = [segment] if segment else []
        _write_expertise_fixture(
            os.path.join(
                root, ".harness", *middle, "expertise", f"{agent}.md"),
            body)
    return root


def _expertise_fixtures(scratch, agent):
    home = os.path.join(scratch, "home")
    os.makedirs(home)
    _write_expertise_fixture(
        os.path.join(home, ".harness", "expertise", f"{agent}.md"),
        "GLOBAL BODY\n")
    empty = _expertise_root(scratch, "expertise-empty")
    tiers = _tiered_expertise_root(scratch, agent)
    caps = _capped_expertise_root(scratch, agent)
    malformed = _expertise_root(
        scratch, "expertise-malformed", 'broken: "unterminated\n\tbad\n')
    _write_expertise_fixture(
        os.path.join(malformed, ".harness", "expertise", f"{agent}.md"),
        "MALFORMED CONFIG STILL INJECTS\n")
    checker = _expertise_root(scratch, "expertise-checker")
    _write_instruction_checker(checker)
    return home, empty, tiers, caps, malformed, checker


def _expertise_payload_cases(env, empty):
    return [
        {"label": "malformed payload is ignored", "stdin": "{not json",
         "env": env(empty)},
        {"label": "missing agent type is ignored", "stdin": "{}",
         "env": env(empty)},
        {"label": "non-harness agent is ignored",
         "stdin": json.dumps({"agent_type": "custom-agent"}),
         "env": env(empty)},
        {"label": "unsafe harness agent is ignored",
         "stdin": json.dumps({"agent_type": "harness-qa/../../etc"}),
         "env": env(empty)},
    ]


def _expertise_content_cases(payload, env, empty, tiers, caps, malformed):
    return [
        {"label": "empty expertise emits control plane",
         "stdin": payload, "env": env(empty)},
        {"label": "all tiers preserve order and segment filtering",
         "stdin": payload, "env": env(tiers)},
        {"label": "tier caps preserve truncation behavior",
         "stdin": payload, "env": env(caps)},
        {"label": "malformed team config remains unread",
         "stdin": payload, "env": env(malformed)},
    ]


def _expertise_checker_cases(payload, env, checker):
    return [
        {"label": "instruction checker clean branch",
         "stdin": payload, "env": env(checker, CHECKER_MODE="clean")},
        {"label": "instruction checker drift branch caps locations",
         "stdin": payload, "env": env(checker, CHECKER_MODE="drift")},
        {"label": "instruction checker failure stays unknown",
         "stdin": payload, "env": env(checker, CHECKER_MODE="failed")},
    ]


def _expertise_boundary_cases(payload, env, empty, tiers, home, project_override,
                               scratch):
    return [
        {"label": "stray arguments remain ignored",
         "argv": ["unexpected"], "stdin": payload, "env": env(empty)},
        {"label": "cwd-independent injection",
         "stdin": payload, "cwd": scratch, "env": env(tiers)},
        {"label": "unconfigured isolated copy remains non-blocking",
         "stdin": payload, "isolate": True,
         "env": {project_override: None, "HOME": home}},
    ]


def inject_expertise_corpus(scratch):
    """Payload, tier, cap, checker, cwd and root cases for the spawn hook."""
    project_override = "HARNESS" + "_PROJECT_DIR"
    agent = "harness-qa"
    payload = json.dumps({"agent_type": agent})
    fixtures = _expertise_fixtures(scratch, agent)
    home, empty, tiers, caps, malformed, checker = fixtures

    def env(root, **extra):
        return {project_override: root, "HOME": home, **extra}

    return (
        _expertise_payload_cases(env, empty)
        + _expertise_content_cases(
            payload, env, empty, tiers, caps, malformed)
        + _expertise_checker_cases(payload, env, checker)
        + _expertise_boundary_cases(
            payload, env, empty, tiers, home, project_override, scratch)
    )


def _gitignore_root(scratch, name, body=None):
    root = os.path.join(scratch, name)
    os.makedirs(root)
    if body is not None:
        with open(os.path.join(root, ".gitignore"), "wb") as fh:
            fh.write(body)
    return root


def _gitignore_rules():
    snippet = os.path.join(BIN, "..", "templates", "gitignore.snippet")
    with open(snippet, "r", encoding="utf-8") as fh:
        return [
            line for line in fh.read().splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]


def _gitignore_fixtures(scratch):
    rules = _gitignore_rules()
    complete = _gitignore_root(
        scratch, "gitignore-complete",
        ("existing\n" + "\n".join(rules) + "\n").encode())
    partial = _gitignore_root(
        scratch, "gitignore-partial",
        ("existing\n" + rules[0] + "\n").encode())
    absent = _gitignore_root(scratch, "gitignore-absent")
    no_newline = _gitignore_root(
        scratch, "gitignore-no-newline", b"existing-without-newline")
    unexpected = _gitignore_root(scratch, "gitignore-unexpected-mode")
    expanded = _gitignore_root(scratch, "gitignore-expanded-output")
    expanded_cwd = os.path.join(scratch, "gitignore-expanded-cwd")
    os.makedirs(expanded_cwd)
    open(os.path.join(expanded_cwd, "visible.pyc"), "w").close()
    return complete, partial, absent, no_newline, unexpected, expanded, expanded_cwd


def _gitignore_cases(scratch, fixtures):
    complete, partial, absent, no_newline, unexpected, expanded, expanded_cwd = fixtures
    return [
        {"label": "missing root prints usage"},
        {"label": "nonexistent root prints usage",
         "argv": [os.path.join(scratch, "missing-root")]},
        {"label": "complete check is read-only",
         "argv": [complete, "--check"]},
        {"label": "partial check reports each missing rule",
         "argv": [partial, "--check"]},
        {"label": "absent target receives rules", "argv": [absent]},
        {"label": "nonempty target without newline preserves append bytes",
         "argv": [no_newline]},
        {"label": "unexpected mode still performs merge",
         "argv": [unexpected, "--unexpected", "ignored"]},
        {"label": "unquoted success diagnostics preserve glob expansion",
         "argv": [expanded], "cwd": expanded_cwd},
        {"label": "missing snippet reports its resolved path",
         "argv": [absent], "isolate": True},
    ]


def merge_gitignore_corpus(scratch):
    """Usage, check, append, idempotence-input, cwd and snippet cases."""
    return _gitignore_cases(scratch, _gitignore_fixtures(scratch))


def post_merge_sweep_corpus(scratch):
    """Safe dry-run, argument, cwd and broken-installation sweep cases."""
    with open(os.path.join(scratch, "harness_boundary.py"), "w",
              encoding="utf-8") as fh:
        fh.write("raise RuntimeError('cwd shadow imported')\n")
    return [
        {"label": "dry run from repository root", "argv": ["--dry-run"]},
        {"label": "git non-squash flag remains ignored",
         "argv": ["0", "--dry-run"]},
        {"label": "git squash flag and stray args remain ignored",
         "argv": ["1", "unexpected", "--dry-run"]},
        {"label": "cwd-independent dry run ignores module shadow",
         "argv": ["--dry-run"], "cwd": scratch},
        {"label": "unconfigured isolated copy stays non-fatal",
         "argv": ["--dry-run"], "isolate": True},
    ]







def corpus(tool, scratch, impl):
    """Cases to run. Real repository inputs plus the edge cases.

    A case is `{"argv": [...], "cwd": <dir>, "isolate": bool}`. Edge cases are not
    decoration: argument handling and root resolution are the parts that move from
    shell into Python, so usage errors, working directory and the refusal path are
    precisely where a conversion goes wrong. Exit 2 paths matter as much as exit 0.

    `isolate` copies bin/ to a scratch tree with NO harness marker above it and runs
    the copy there. That is the only way to reach the "no root could be resolved"
    branch, which is a refusal the real tree can never produce.
    """
    if tool == "check-expertise":
        exp = os.path.join(ROOT, ".harness", "expertise")
        cases = [
            [],                                            # no args -> usage, exit 2
            ["/nonexistent/path.md"],                      # missing -> exit 2
            [scratch],                                     # empty dir -> "nothing to check"
            [exp],                                         # real dir, expanded and sorted
        ]
        if os.path.isdir(exp):
            mds = sorted(f for f in os.listdir(exp) if f.endswith(".md"))
            cases += [[os.path.join(exp, m)] for m in mds]          # each real file
            if len(mds) >= 2:                                        # multi-file argv
                cases.append([os.path.join(exp, mds[0]), os.path.join(exp, mds[1])])
        for seg in sorted(os.listdir(os.path.join(ROOT, ".harness"))):
            d = os.path.join(ROOT, ".harness", seg, "expertise")
            if os.path.isdir(d):
                cases.append([d])                                    # repository tier
        # synthetic violations: the failing path must be proven too, not just the clean one
        bad = os.path.join(scratch, "bad.md")
        with open(bad, "w", encoding="utf-8") as fh:
            fh.write("## Patterns\n- P-01: " + "word " * 80 + "\n## Bogus\n- X-01: FEAT-12 T-03 #55\n")
        cases.append([bad])
        empty = os.path.join(scratch, "empty.md")
        open(empty, "w", encoding="utf-8").close()
        cases.append([empty])
        return [{"argv": a} for a in cases]
    if tool == "merge-gitignore":
        return merge_gitignore_corpus(scratch)
    if tool == "check-state":
        # Takes NO arguments: the shell wrapper passes only $root and $_selfdir to
        # the interpreter and never forwards "$@". Stray args must stay ignored.
        # The wrapper also cd's to the root, so the answer must not depend on cwd --
        # that is the property most likely to break when the cd moves into Python.
        return [
            {"argv": []},
            {"argv": [], "cwd": os.path.join(ROOT, ".claude", "skills", "harness", "bin")},
            {"argv": [], "cwd": os.path.join(ROOT, ".harness")},
            {"argv": [], "cwd": scratch},                       # outside the repo entirely
            {"argv": ["--nonsense", "extra"]},                  # ignored, not an error
            {"argv": [], "isolate": True},                      # no root -> refuse, exit 2
        ]
    if tool == "check-domain":
        return domain_corpus(scratch)
    if tool == "bash-write-guard":
        return bash_guard_corpus(scratch)
    if tool == "dispatch-guard":
        return dispatch_guard_corpus(scratch)
    if tool == "branch-create-gate":
        return branch_create_gate_corpus(scratch)
    if tool == "plan-sign-gate":
        return plan_sign_gate_corpus(scratch)
    if tool == "gh-close-gate":
        return gh_close_gate_corpus(scratch)
    if tool == "merge-gate":
        return merge_gate_corpus(scratch)
    if tool == "run-unit-tests":
        return run_unit_tests_corpus(scratch)
    if tool == "post-merge-sweep":
        return post_merge_sweep_corpus(scratch)
    if tool == "inject-expertise":
        return inject_expertise_corpus(scratch)
    raise SystemExit(f"no corpus defined for {tool!r} -- add one before converting it")


def run(impl, case, scratch):
    argv, cwd = case.get("argv", []), case.get("cwd", ROOT)
    if case.get("isolate"):
        # Copy the bin dir somewhere with no harness marker above it. shutil.copytree
        # keeps the relative layout the script resolves its siblings through.
        iso = os.path.join(scratch, "isolated")
        if not os.path.exists(iso):
            shutil.copytree(BIN, iso)
        impl, cwd = os.path.join(iso, os.path.basename(impl)), iso

    child_env = dict(os.environ)
    for key, value in case.get("env", {}).items():
        if value is None:
            child_env.pop(key, None)
        else:
            child_env[key] = value
    p = subprocess.run([impl] + argv, input=case.get("stdin"),
                       capture_output=True, text=True, cwd=cwd, env=child_env)
    # Absolute paths leak roots that differ between capture and verify: the checkout
    # (harmless but noisy) and the scratch dir (a fresh mkdtemp each run). Two source
    # coordinates intentionally move: the executable's suffix, and the first traceback
    # frame from heredoc `<stdin>` to the installed module. Normalize only those locations;
    # the exit code, downstream frames, exception type/message and all ordinary output
    # remain byte-for-byte requirements.
    impl_stem = os.path.splitext(os.path.basename(impl))[0]
    def scrub(s):
        normalized = (s.replace(ROOT, "<ROOT>").replace(scratch, "<SCRATCH>")
                      .replace(impl_stem + ".sh", "<IMPL>")
                      .replace(impl_stem + ".py", "<IMPL>"))
        return re.sub(
            r'  File "(?:<stdin>|[^"\n]*<IMPL>)", line \d+, in <module>\n'
            r'(?:    [^\n]+\n(?:    [~^ ]+\n)?)?',
            '  File "<IMPL>", in <module>\n',
            normalized,
        )
    return {"case": {"label": case.get("label", ""),
                     "argv": [scrub(a) for a in argv], "cwd": scrub(cwd),
                     "isolate": bool(case.get("isolate"))},
            "exit": p.returncode, "stdout": scrub(p.stdout), "stderr": scrub(p.stderr)}


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("capture", "verify"):
        raise SystemExit(__doc__)
    mode, tool, store = sys.argv[1], sys.argv[2], sys.argv[3]
    impl = os.path.join(BIN, f"{tool}.sh" if mode == "capture" else f"{tool}.py")
    if not os.path.exists(impl):
        raise SystemExit(f"{impl} does not exist")

    with tempfile.TemporaryDirectory() as scratch:
        results = [run(impl, case, scratch) for case in corpus(tool, scratch, impl)]

    if mode == "capture":
        with open(store, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"captured {len(results)} cases from {os.path.basename(impl)} -> {store}")
        codes = sorted({r["exit"] for r in results})
        print(f"exit codes observed: {codes}")
        if codes == [0]:
            # A corpus that only ever succeeds cannot detect a conversion that
            # breaks failure handling -- which is most of what argument parsing does.
            print("WARNING: no non-zero exit in the corpus; failure paths are unproven")
        return 0

    baseline = json.load(open(store, encoding="utf-8"))
    if len(baseline) != len(results):
        print(f"FAIL: corpus size changed ({len(baseline)} -> {len(results)})")
        return 1
    bad = 0
    for b, a in zip(baseline, results):
        diffs = [k for k in ("exit", "stdout", "stderr") if b[k] != a[k]]
        if diffs:
            bad += 1
            desc = b["case"].get("label") or (' '.join(b["case"]["argv"]) or '<no args>')
            if b["case"].get("isolate"):
                desc += " [isolated: no harness root]"
            desc += f" (cwd {b['case']['cwd']})"
            print(f"FAIL {desc}: differs in {', '.join(diffs)}")
            for k in diffs:
                print(f"  --- {k} before ---\n{b[k]!r}\n  --- {k} after ---\n{a[k]!r}")
    print(f"{len(results) - bad}/{len(results)} cases byte-identical")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
