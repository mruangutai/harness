#!/usr/bin/env python3
"""Tests for check-domain.sh's path decisions (DEC-110/DEC-151).

WHY: this is the hook that enforces write domains. It had no test, and it
disagreed with its Bash-side sibling about paths OUTSIDE the repo — a scratch
file in /tmp was blocked by the Write hook and allowed by bash-write-guard, so
an agent learned to work around a hook whose own message says not to.

Exit codes are asserted EXACTLY (2 blocks, 0 passes — DEC-100: only exit 2
blocks, so "nonzero" would let a crash read as a rejection).

Both halves must stay green: the out-of-repo carve-out must not become a hole
that lets a repo path through by dressing it up.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
HOOK = os.environ.get("CHECK_DOMAIN_BIN") or os.path.join(HERE, "check-domain.sh")
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

CASES = []

def case(name, path, want, agent="harness-documentor", tool="Write"):
    CASES.append((name, path, want, agent, tool))

# ---------------- MUST PASS: outside the repo is not a domain question --------
# bash-write-guard.sh:211 already says so ("outside repo — not this hook's
# problem"). The Write hook must agree, or the same scratch file is legal via
# Bash and illegal via Write.
case("a scratch script in /tmp", "/tmp/backfill_t04.py", 0)
case("/var/folders temp dir (macOS mktemp)", "/var/folders/ab/cd/T/x.py", 0)
case("an absolute path in another checkout", "/Users/someone/other-repo/x.py", 0)

# ---------------- MUST PASS: inside its own domain ----------------
case("documentor writing docs/", f"{ROOT}/docs/harness/guide.md", 0)
case("documentor writing its own expertise",
     f"{ROOT}/.harness/expertise/harness-documentor.md", 0)
case("a shared path is allowed and serialized", f"{ROOT}/package.json", 0)

# ---------------- MUST BLOCK: repo paths outside its domain ----------------
case("documentor may not write source", f"{ROOT}/src/main.py", 2)
case("documentor may not write another agent's expertise",
     f"{ROOT}/.harness/expertise/harness-qa.md", 2)
case("documentor may not write bin/", f"{ROOT}/.claude/skills/harness/bin/x.py", 2)
# The carve-out must key on being outside the repo, NOT on the string "..".
case("a repo path reached via .. still blocks",
     f"{ROOT}/docs/../src/main.py", 2)
case("a repo path reached via a long .. chain still blocks",
     f"{ROOT}/docs/harness/../../src/main.py", 2)


# ================= T-12: the manifest is PARSED, not skimmed ==================
# These use a FIXTURE repo rather than the live one, so a malformed manifest can be
# exercised without touching the manifest that governs this session.

import shutil
import tempfile

FIXTURE_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: allowed/**, upsert: true }
          - { path: .harness/features/*/runs/*/state.yaml, upsert: true }
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


def fire(root, path, content="x", agent="harness-documentor"):
    payload = {"agent_type": agent, "tool_name": "Write",
               "tool_input": {"file_path": os.path.join(root, path), "content": content}}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=root))


T12 = []


def t12(name, ok, detail=""):
    T12.append((name, ok, detail))


def run_t12():
    # SC-05's PAIRED assertion, in ONE invocation context. Either outcome alone is
    # also what a broken hook produces — an allow-all escape passes the permitted
    # write, a block-all fail-closed blocks the forbidden one. Only a manifest that
    # actually parsed produces BOTH from the same fixture.
    root = fixture(FIXTURE_MANIFEST)
    allowed = fire(root, "allowed/thing.md")
    denied = fire(root, "forbidden/thing.md")
    t12("SC-05 pair: permitted allowed AND forbidden blocked, one manifest",
        allowed.returncode == 0 and denied.returncode == 2,
        f"permitted got {allowed.returncode} (want 0), forbidden got "
        f"{denied.returncode} (want 2)")

    # FAIL CLOSED on a malformed manifest (user ruling, 2026-08-03). NOT the
    # absent-manifest case, which still fails OPEN: an unconfigured project has
    # nothing to enforce, whereas this project IS configured and one action fixes it.
    # No deadlock — the manifest is in no agent's domain and the main session is
    # exempt, so the only party who can repair it is the one this guard never governs.
    bad = fixture('teams: [ {name: x ## eaten\nnext_key: 1\n')
    r = fire(bad, "allowed/thing.md")
    t12("a MALFORMED manifest blocks the write (fail closed, not half-enforced)",
        r.returncode == 2 and "does not parse" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    # A duplicate key in the RULEBOOK: which of two domain lists wins is not a thing
    # to guess at while holding a write guard.
    dup = fixture(FIXTURE_MANIFEST + "\nshared:\n  - { path: other.json }\n")
    r = fire(dup, "allowed/thing.md")
    t12("a DUPLICATE key in the manifest blocks the write",
        r.returncode == 2 and "duplicate key" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    # The manifest still ABSENT fails OPEN, loudly — DEC-101 unchanged. Asserted so
    # the new fail-closed paths cannot quietly swallow this deliberate carve-out.
    #
    # This needs an ISOLATED COPY of the hook, not merely an empty CLAUDE_PROJECT_DIR:
    # `root` falls back to `_derived`, computed from BASH_SOURCE, so a hook running
    # from the real bin/ finds the REAL manifest no matter what the env var says. A
    # first draft of this case pointed the env var at an empty dir, got exit 0, and
    # passed — but the 0 came from "outside repo, not this hook's problem" and the
    # absent-manifest branch never ran. Vacuous, and it looked green.
    iso = tempfile.mkdtemp()
    isobin = os.path.join(iso, ".claude", "skills", "harness", "bin")
    os.makedirs(isobin)
    shutil.copy(HOOK, os.path.join(isobin, "check-domain.sh"))
    payload = {"agent_type": "harness-documentor", "tool_name": "Write",
               "tool_input": {"file_path": os.path.join(iso, "anything.md"), "content": "x"}}
    r = subprocess.run([os.path.join(isobin, "check-domain.sh")], input=json.dumps(payload),
                       capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=iso))
    t12("an ABSENT manifest still fails OPEN, loudly (DEC-101 carve-out intact)",
        r.returncode == 0 and "enforcement OFF" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    # --- the state.yaml shape gate, now loader-driven (D-02) ---
    root = fixture(FIXTURE_MANIFEST)
    sp = ".harness/features/FEAT-01/runs/r1/state.yaml"

    r = fire(root, sp, "run_id: r1\nstatus: complete\n")
    t12("a well-formed state.yaml with checkpoint keys passes",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    r = fire(root, sp, "run_id: r1\ncost: 1\ncost: 2\n")
    t12("a DUPLICATE top-level key is blocked with the DEC-156 message",
        r.returncode == 2 and "DEC-156" in r.stderr and "duplicate key" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    # The genuinely NEW behaviour. The regex this replaced was anchored at column 0
    # (`^([A-Za-z_]...):` under re.M), so a duplicate NESTED inside a block was
    # invisible — `cost:` appearing twice under `steps:` silently shadowed, which is
    # the FEAT-02 audit's finding one level down. The loader raises at any depth.
    r = fire(root, sp, "run_id: r1\nsteps:\n  - id: s1\n    cost: 1\n    cost: 2\n")
    t12("a NESTED duplicate key is blocked (column-0 regex could not see it)",
        r.returncode == 2 and "duplicate key" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    # NEW blocking outcome: the regex this replaced found no keys in a malformed
    # file and therefore reported nothing wrong — it wrote a broken checkpoint and
    # said it was fine.
    r = fire(root, sp, "run_id: [unclosed\nstatus: complete\n")
    t12("MALFORMED state.yaml is blocked with a parse-error message",
        r.returncode == 2 and "not valid YAML" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    r = fire(root, sp, "run_id: r1\nfindings: lots of prose\n")
    t12("a non-checkpoint top-level key is still blocked (DEC-154 vocabulary intact)",
        r.returncode == 2 and "non-checkpoint" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    fails = 0
    for name, ok, detail in T12:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(T12) - fails}/{len(T12)} T-12 cases passed.")
    return fails


def main():
    fails = 0
    for name, path, want, agent, tool in CASES:
        payload = {"agent_type": agent, "tool_name": tool,
                   "tool_input": {"file_path": path, "content": "x"}}
        r = subprocess.run([HOOK], input=json.dumps(payload),
                           capture_output=True, text=True,
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
        if r.returncode != want:
            fails += 1
            verb = "should have BLOCKED (2)" if want == 2 else "should have PASSED (0)"
            print(f"FAIL  {name}\n        {verb}, got {r.returncode}")
            for l in (r.stdout + r.stderr).strip().splitlines()[:2]:
                print(f"      | {l}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} cases passed.\n")
    fails += run_t12()
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
