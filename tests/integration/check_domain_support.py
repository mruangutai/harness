#!/usr/bin/env python3
"""Shared fixtures and the block driver for the test-check-domain-*.py family.

WHY (inherited verbatim in intent from the former test-check-domain.py): this is the
hook that enforces write domains. It had no test, and it disagreed with its Bash-side
sibling about paths OUTSIDE the repo — a scratch file in /tmp was blocked by the Write
hook and allowed by bash-write-guard, so an agent learned to work around a hook whose
own message says not to.

Exit codes are asserted EXACTLY (2 blocks, 0 passes — DEC-100: only exit 2 blocks, so
"nonzero" would let a crash read as a rejection).

Issue #1527 split that one 5370-line file into six by surface, because run-unit-tests.sh
parallelises by FILE and a single serial run of subprocess cases set the suite's floor.
Everything here is used by two or more of those six; a fixture used by one lives with it.
Nothing in this module runs a case: `drive()` IS the former main(), parameterised on the
calling module's namespace so each file still DISCOVERS its own module-level run_* blocks
rather than hand-maintaining a list.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import contextlib, json, os, subprocess, sys, tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
sys.path.insert(0, HERE)
HOOK = os.environ.get("CHECK_DOMAIN_BIN") or os.path.join(HERE, "check-domain.sh")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def _env(root, **kw):
    """The hook's environment for a fixture rooted at `root` — BOTH names, one value.

    FEAT-42 T-10. check-domain.sh resolves its root through harness_boundary.resolve_root,
    which reads HARNESS_PROJECT_DIR and no other name. The reverted sha-3952814 copy this
    suite is diffed against reads HARNESS_PROJECT_DIR first and CLAUDE_PROJECT_DIR second.
    Setting both to the same value is therefore the ONE spelling under which the two copies
    resolve the same root, which is what makes the identical-violation-set proof mean
    anything. Setting only the host-owned name — what every call here did before — points
    the new copy at the live checkout instead, and 20 cases failed exactly that way.

    resolve_root honours the override only when `.harness/team-config.yaml` is readable
    underneath it. A fixture without that marker gets the override discarded and falls back
    to the derived root, which is the same answer the deleted chain gave it.
    """
    return dict(os.environ, CLAUDE_PROJECT_DIR=root, HARNESS_PROJECT_DIR=root, **kw)


FIXTURE_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: allowed/**, upsert: true }
          - { path: .harness/allowed/**, upsert: true }
          - { path: .harness/*/features/*/runs/*/state.yaml, upsert: true }
          - { path: ".", read: true }
shared:
  - { path: package.json }
"""


def fixture(manifest_text):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write(manifest_text)
    return d


def fixture_fleet(manifest_text, fleet_text):
    """A fixture root that ALSO carries .harness/factory/fleet.yaml. Passing
    fleet_text=None gives a root with no fleet file at all, which is the no-factory
    case and must behave exactly as it did before FEAT-15."""
    d = fixture(manifest_text)
    if fleet_text is not None:
        os.makedirs(os.path.join(d, ".harness", "factory"))
        with open(os.path.join(d, ".harness", "factory", "fleet.yaml"), "w") as f:
            f.write(fleet_text)
    return d


def make_linked_worktree(root, wt_path, wt_id):
    """Turn `wt_path` into a REAL linked worktree of `root`. No git subprocess.

    Both sides of the pointer pair, per D-09, and both are load-bearing for different
    consumers: the worktree-side `.git` FILE is what `checkout_relative` reads, and the
    owner-side `.git/worktrees/<id>/gitdir` file is what `linked_worktrees` enumerates.
    A `.git` file alone leaves the sweep blind to the checkout; a bare directory
    exercises neither.

    NO `.harness/team-config.yaml` inside the worktree: callers root their session at
    `root`, and a nearer manifest would move the base out from under the assertion.
    """
    os.makedirs(os.path.join(root, ".git", "worktrees", wt_id), exist_ok=True)
    os.makedirs(wt_path, exist_ok=True)
    entry = os.path.join(root, ".git", "worktrees", wt_id)
    with open(os.path.join(wt_path, ".git"), "w") as f:
        f.write("gitdir: %s\n" % entry)
    with open(os.path.join(entry, "gitdir"), "w") as f:
        f.write("%s\n" % os.path.join(wt_path, ".git"))
    return wt_path


def fire(root, path, content="x", agent="harness-documentor", hook=HOOK):
    payload = {"agent_type": agent, "tool_name": "Write",
               "tool_input": {"file_path": os.path.join(root, path), "content": content}}
    return subprocess.run([hook], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def fire_post(root, payload, flag="--post"):
    argv = [HOOK] + ([flag] if flag else [])
    return subprocess.run(argv, input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def _legal_feature_json(nlines):
    """A schema-clean ten-key feature.json padded to exactly `nlines` lines.

    T-06 put the schema on this path, so any fixture judged on its LINE COUNT must be
    schema-clean or it is denied for a reason its case never named — a green-looking test
    asserting the wrong cause. Trailing whitespace is insignificant to a JSON parser, so
    padding this way changes the line count and nothing else.
    """
    import json as _json
    body = _json.dumps({"feature_id": "FEAT-X", "branch": "none", "pr": None, "review_sha": "none", "cycles_used": 0,
                        "max_total_cycles": 10, "runs": []}, indent=2).splitlines()
    return "\n".join(body + [""] * max(0, nlines - len(body))) + "\n"


def _fire_edit(root, full, old_s, new_s, agent="harness-pm", replace_all=False):
    ti = {"file_path": full, "old_string": old_s, "new_string": new_s}
    if replace_all:
        ti["replace_all"] = True
    payload = {"agent_type": agent, "tool_name": "Edit", "tool_input": ti}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def _handoff_text(body, trust_lines=1):
    lines = ["## Next", "next", "## Trust"]
    lines += [f"trust {n}" for n in range(trust_lines)]
    lines += ["## Dead ends", "none", "## Working set", "set", "## Done when"]
    lines += body.splitlines()
    return "\n".join(lines) + "\n"


def _handoff_done_when_fixture(root):
    os.makedirs(os.path.join(root, ".harness"), exist_ok=True)
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    feat = os.path.join(root, ".harness", "harness", "features", "FEAT-90-fixture")
    notes = os.path.join(feat, "notes")
    os.makedirs(notes, exist_ok=True)
    with open(os.path.join(feat, "plan.yaml"), "w") as f:
        f.write("tasks:\n  - id: T-03\n    verify: python3 test.py\n")
    with open(os.path.join(feat, "BRIEF.md"), "w") as f:
        f.write("# BRIEF\n\n- SC-04: observable\n\n## Approval\n")
    with open(os.path.join(notes, "review-fixture.md"), "w") as f:
        f.write("Finding F-02 remains.\n")
    return notes, os.path.join(notes, "handoff-build.md")


class _AggTee:
    """Captures written text while still writing through to the real stream, so a
    human watching the run live still sees verdicts as they print.
    """

    def __init__(self, real):
        self.real = real
        self.parts = []

    def write(self, s):
        self.parts.append(s)
        return self.real.write(s)

    def flush(self):
        self.real.flush()

    def text(self):
        return "".join(self.parts)


def _aggregation_verdict(label, captured_text, total):
    """None when a block's printed column-0 FAIL lines agree with its returned total
    on ZERONESS (D-01): the diagnostic fires only when one side is zero and the other
    is not. Strict equality of the printed count against total is NOT the predicate.
    """
    printed = sum(1 for line in captured_text.splitlines() if line.startswith("FAIL"))
    if bool(printed) == bool(total):
        return None
    return f"{label}: {printed} printed column-0 FAIL line(s) vs total={total}"


def _run_block_captured(block_fn, label, stream=None):
    """Runs block_fn() under a live-tee capture of stdout and returns
    (total, verdict): the same tee-construction + redirect_stdout + call +
    _aggregation_verdict sequence main()'s discovery loop uses for every
    discovered "run_*" block (D-02). `stream` is the passthrough target the
    tee also writes through to; it defaults to the real sys.stdout so
    main()'s on-screen behaviour is unchanged when it calls this helper.
    """
    tee = _AggTee(stream if stream is not None else sys.stdout)
    with contextlib.redirect_stdout(tee):
        total = block_fn()
    return total, _aggregation_verdict(label, tee.text(), total)



def drive(namespace, cases=()):
    """The former main(): the CASES loop, then every module-level run_* block.

    `namespace` is the calling test module's globals(). The block list is
    DISCOVERED, never hand-maintained: every module-level "run_*" callable, in
    definition order, runs under _run_block_captured() (D-02), the same
    tee-capture + _aggregation_verdict safeguard as the CASES loop. A block whose
    printed column-0 FAIL lines disagree on zeroness with its returned total trips
    the safeguard (D-01), and a trip alone fails the suite even when every block's
    own total was 0.
    """
    fails = 0
    problems = []

    if cases:
        cases_tee = _AggTee(sys.stdout)
        with contextlib.redirect_stdout(cases_tee):
            for name, path, want, agent, tool in cases:
                payload = {"agent_type": agent, "tool_name": tool,
                           "tool_input": {"file_path": path, "content": "x"}}
                r = subprocess.run([HOOK], input=json.dumps(payload),
                                   capture_output=True, text=True,
                                   env=_env(ROOT))
                if r.returncode != want:
                    fails += 1
                    verb = "should have BLOCKED (2)" if want == 2 else "should have PASSED (0)"
                    print(f"FAIL  {name}\n        {verb}, got {r.returncode}")
                    for l in (r.stdout + r.stderr).strip().splitlines()[:2]:
                        print(f"      | {l}")
                else:
                    print(f"ok    {name}")
            print(f"\n{len(cases) - fails}/{len(cases)} cases passed.\n")
        cases_verdict = _aggregation_verdict("CASES", cases_tee.text(), fails)
        if cases_verdict is not None:
            problems.append(cases_verdict)

    for block_name, block_fn in list(namespace.items()):
        if not block_name.startswith("run_") or not callable(block_fn):
            continue
        total, block_verdict = _run_block_captured(block_fn, block_name)
        fails += total
        if block_verdict is not None:
            problems.append(block_verdict)

    for problem in problems:
        print(f"FAIL  aggregation safeguard: {problem}")
    return fails + len(problems)
