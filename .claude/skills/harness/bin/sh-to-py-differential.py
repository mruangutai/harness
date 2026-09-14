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
    if tool == "post-merge-sweep":
        return post_merge_sweep_corpus(scratch)
    if tool == "check-domain":
        return domain_corpus(scratch)
    if tool == "bash-write-guard":
        return bash_guard_corpus(scratch)
    if tool == "dispatch-guard":
        return dispatch_guard_corpus(scratch)
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
