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
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import json, os, re, shutil, subprocess, sys, yaml

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
sys.path.insert(0, HERE)
from isolated_bin import isolated_bin
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
case("documentor writing the moved harness docs", f"{ROOT}/.harness/harness/docs/guide.md", 0)
case("documentor writing its own expertise",
     f"{ROOT}/.harness/expertise/harness-documentor.md", 0)
# EXPECTATION CHANGED by FEAT-15 T-02, and it is the only one in this file that moved.
# All eight entries in the manifest's `shared:` block are dependency manifests and
# lockfiles — package.json, pyproject.toml, uv.lock and the rest. None has a
# control-plane first segment and none is among the explicit Harness entries, so in
# the HARNESS base every one of them is a product-shaped target and stops being
# serialized-allow. No such file exists in this repo today, so nothing live changed —
# but the rule did, and the assertion says so rather than being quietly deleted.
# Serialized-allow survives where those files actually live: a product checkout.
case("a shared path in the harness base is now REFUSED (product-shaped target)",
     f"{ROOT}/package.json", 2)

# ---------------- MUST BLOCK: repo paths outside its domain ----------------
case("documentor may not write source", f"{ROOT}/src/main.py", 2)
case("documentor may not write another agent's expertise",
     f"{ROOT}/.harness/expertise/harness-qa.md", 2)
case("documentor may not write bin/", f"{ROOT}/.agents/skills/harness/bin/x.py", 2)
# The carve-out must key on being outside the repo, NOT on the string "..".
case("a repo path reached via .. still blocks",
     f"{ROOT}/docs/../src/main.py", 2)
case("a repo path reached via a long .. chain still blocks",
     f"{ROOT}/.harness/harness/docs/../../../src/main.py", 2)
# THE REFUSED DIRECTION (FEAT-22): the OLD docs location is no longer granted to
# anybody — a writer still aimed at the pre-move path must be told no, loudly,
# not silently landed in a directory nothing reads any more.
case("the pre-move docs path is REFUSED after the migration",
     f"{ROOT}/docs/harness/guide.md", 2)


# ================= T-12: the manifest is PARSED, not skimmed ==================
# These use a FIXTURE repo rather than the live one, so a malformed manifest can be
# exercised without touching the manifest that governs this session.

import errno
import shutil
import tempfile
import time

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


T12 = []


def t12(name, ok, detail=""):
    T12.append((name, ok, detail))


def run_t12():
    # SC-05's PAIRED assertion, in ONE invocation context. Either outcome alone is
    # also what a broken hook produces — an allow-all escape passes the permitted
    # write, a block-all fail-closed blocks the forbidden one. Only a manifest that
    # actually parsed produces BOTH from the same fixture.
    root = fixture(FIXTURE_MANIFEST)
    # The ALLOW half is a control-plane path (FEAT-15 T-01). Under T-02's rule an
    # in-root product-shaped target stops being owned, so `allowed/thing.md` would
    # flip to exit 2 — and this pair's whole point is that a block-all guard cannot
    # pass it. The forbidden half stays product-shaped and stays refused.
    allowed = fire(root, ".harness/allowed/thing.md")
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
                       env=_env(iso))
    t12("an ABSENT manifest still fails OPEN, loudly (DEC-101 carve-out intact)",
        r.returncode == 0 and "enforcement OFF" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    # F-01, found by the review panel and reproduced live before the fix. load_str
    # caught only yaml.YAMLError and load_file's open()/read() sat outside any try, so
    # a manifest that is not valid UTF-8 — or a directory where a file was expected —
    # raised past every caller's `except YamlParseError`, killed the subprocess with
    # exit 1, and exit 1 is NON-BLOCKING (DEC-100). The write then proceeded UNGOVERNED.
    #
    # This is the ONE way a fail-closed guard fails open, it is the same crash pattern
    # T-17's receipt documents, and it was fixed once in the escape path and missed here
    # in the module both hooks call. Asserted at HOOK level, not module level: the panel
    # showed module tests can exercise a path production never takes.
    bad_utf8 = tempfile.mkdtemp()
    os.makedirs(os.path.join(bad_utf8, ".harness"))
    with open(os.path.join(bad_utf8, ".harness", "team-config.yaml"), "wb") as f:
        f.write(b"schema_version: 1\nteams: [{name: b}]\n\xff\xfe not utf-8\n")
    r = fire(bad_utf8, "allowed/thing.md")
    t12("F-01: a manifest that is not valid UTF-8 BLOCKS (was exit 1 = fail open)",
        r.returncode == 2 and "does not parse" in r.stderr,
        f"exit {r.returncode} (2 blocks, 1 fails OPEN): {r.stderr.strip()[:200]}")

    # M-02, found by the re-review panel and PRE-EXISTING at both SHAs. F-01 widened
    # load_str's except, but these inputs PARSE SUCCESSFULLY — an empty file yields
    # None, a bare scalar a str, a bare list a list — so no exception is ever raised
    # and manifest_domains' `parsed.get("shared")` raised AttributeError straight past
    # both hooks' `except YamlParseError`. Exit 1, non-blocking (DEC-100), write
    # allowed. An EMPTY team-config.yaml was enough to disable both write guards.
    #
    # The shape is worth remembering: walk() immediately above guards every branch with
    # isinstance and the very next statement did not. F-01's fix was scoped to the two
    # shapes cycle 0 happened to name; this was a third route to the same fail-open.
    for label, body in (("empty", ""), ("bare scalar", "just text\n"), ("bare list", "- a\n- b\n")):
        m2 = tempfile.mkdtemp()
        os.makedirs(os.path.join(m2, ".harness"))
        with open(os.path.join(m2, ".harness", "team-config.yaml"), "w") as f:
            f.write(body)
        r = fire(m2, "allowed/thing.md")
        t12(f"M-02: a manifest that parses to a non-mapping ({label}) BLOCKS, not crashes",
            r.returncode == 2 and "Traceback" not in r.stderr,
            f"exit {r.returncode} (2 blocks, 1 fails OPEN): {r.stderr.strip()[:180]}")

    as_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(as_dir, ".harness", "team-config.yaml"))
    r = fire(as_dir, "allowed/thing.md")
    t12("F-01: a manifest that is a DIRECTORY does not crash the guard",
        r.returncode in (0, 2) and "Traceback" not in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- the state.yaml shape gate, now loader-driven (D-02) ---
    root = fixture(FIXTURE_MANIFEST)
    sp = ".harness/harness/features/FEAT-01/runs/r1/state.yaml"

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

    # T-17 / D-08: test_yaml_truthy_top_level_key_is_reported_by_name.
    #
    # `on:` is NOT the string "on" after parsing — YAML 1.1 resolves it to True. Without
    # str() on both sides, `k not in ALLOWED` compares a bool against a set of strings
    # and the resulting `sorted()` gets a MIXED set.
    #
    # THE FIXTURE NEEDS TWO UNKNOWN KEYS, one bool-resolved and one string, and that is
    # not incidental: a first draft used `on:` alone, whose unknown set is the single
    # element {True}, which sorts fine. It passed against a deliberately un-coerced copy
    # — a non-discriminating test that looked like proof. Mixed types are what raise
    # TypeError, and in a fail-closed hook a raise is a BLOCK ON EVERY WRITE, not a
    # wrong answer.
    r = fire(root, sp, "run_id: r1\non: something\nfindings: prose\n")
    t12("a YAML-truthy key (`on:`) beside a string key denies cleanly, no raise",
        r.returncode == 2 and "non-checkpoint" in r.stderr and "Traceback" not in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:200]}")
    t12("...and the denial explains the unquoted-key cause, not just 'True'",
        "UNQUOTED key" in r.stderr and "YAML 1.1" in r.stderr,
        f"stderr lacked the cause hint: {r.stderr.strip()[:200]}")

    # --- SC-08: the bootstrap escape, driven through the REAL HOOK -------------
    #
    # SC-08 says "the first HOOK INVOCATION permits the write and emits the install
    # command". test-harness-yaml.py already covers require_or_bootstrap's state
    # machine, but at MODULE level and via payload={"session_id": ...} — which the
    # resolution probe showed is a DEAD entry in production, where identity comes from
    # the CLAUDE_CODE_SESSION_ID environment variable. A module test cannot see whether
    # the hook acts on the return value at all.
    #
    # It could not, and this caught it: both hooks called require_or_bootstrap(root)
    # and DISCARDED the result, so the escape printed an install command and then let
    # every write through — REQ-04's fail-closed and SC-09's expiry were inert.
    #
    # PyYAML is hidden portably: a fake yaml.py that raises ImportError, on a PYTHONPATH
    # entry the hook appends after its own bin/. harness_yaml.py:18-20 is the single
    # `try: import yaml / except ImportError: yaml = None` in the tree (D-12), so this
    # reproduces a machine that genuinely lacks the package without uninstalling it.
    fake = tempfile.mkdtemp()
    with open(os.path.join(fake, "yaml.py"), "w") as f:
        f.write('raise ImportError("simulated: no PyYAML")\n')

    def fire_noyaml(root, path, session, content="x"):
        payload = {"agent_type": "harness-documentor", "tool_name": "Write",
                   "tool_input": {"file_path": os.path.join(root, path), "content": content}}
        env = _env(root, PYTHONPATH=fake,
                   CLAUDE_CODE_SESSION_ID=session)
        env.pop("CLAUDE_CODE_BRIDGE_SESSION_ID", None)
        return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                              text=True, env=env)

    root = fixture(FIXTURE_MANIFEST)
    marker = os.path.join(root, ".harness", ".pyyaml-bootstrap")

    r1 = fire_noyaml(root, "allowed/a.md", "sess-A")
    t12("SC-08: with PyYAML missing, the FIRST hook invocation PERMITS the write",
        r1.returncode == 0, f"exit {r1.returncode}: {r1.stderr.strip()[:200]}")
    # NOT SC-08's full clause, and the name says so. SC-08 requires the command on "a
    # channel the user sees" (BRIEF:106); this asserts only that it reaches stderr.
    # The 2026-08-03 hand-run proved those are different things — Claude Code does not
    # surface hook stderr when the hook ALLOWS (exit 0), so this assertion passed while
    # the criterion it traces to FAILED, and the tester saw nothing. That is the
    # verify-method defect this feature keeps finding, here in my own test. D-14b tracks
    # the real fix; renamed so nobody reads a green tick as SC-08 being met.
    t12("[partial SC-08] the install command reaches stderr (NOT proof the user sees it — D-14b)",
        "pip install" in r1.stderr and "pyyaml" in r1.stderr.lower(),
        f"stderr: {r1.stderr.strip()[:200]}")

    # SC-08's ACTUAL clause: "a channel the user sees". stderr is not that on an allow —
    # measured, not assumed. `systemMessage` on stdout is the PreToolUse contract's
    # user-visible channel, already live in this repo via branch-create-gate.sh:82,111.
    # Parsed rather than substring-matched: malformed JSON on a hook's stdout is worse
    # than none, so this fails if the payload is not loadable.
    def _sysmsg(res):
        try:
            return json.loads(res.stdout.strip()).get("systemMessage", "")
        except Exception:
            return None
    msg = _sysmsg(r1)
    t12("SC-08: the install command reaches a channel the user SEES (systemMessage)",
        isinstance(msg, str) and "pip install" in msg,
        f"stdout was {r1.stdout.strip()[:200]!r}")
    t12("SC-08: ...and records the marker",
        os.path.exists(marker), f"no marker at {marker}")

    r2 = fire_noyaml(root, "allowed/b.md", "sess-A")
    t12("SC-08: a SECOND write in the SAME session is permitted, silently",
        r2.returncode == 0 and "pip install" not in r2.stderr,
        f"exit {r2.returncode}: {r2.stderr.strip()[:200]}")

    # The SC-09 MECHANISM. The criterion itself is verify: uat, because only a real
    # session boundary proves it honestly — but the identity comparison the boundary
    # relies on is testable here, and without it SC-09 could not pass in principle.
    r3 = fire_noyaml(root, "allowed/c.md", "sess-B")
    t12("SC-09 mechanism: a DIFFERENT session is BLOCKED while PyYAML is missing",
        r3.returncode == 2, f"exit {r3.returncode}: {r3.stderr.strip()[:200]}")

    # D-14a, found by the SC-09 hand-run: the block was SILENT. require_or_bootstrap
    # returned False without writing anything on three branches while both callers
    # assumed it had printed, so an expired grant refused every Write AND every Bash
    # command with zero bytes of explanation — the agent saw "PreToolUse:Write hook
    # error: No stderr output" and had no way to learn why. Unlike the grant path
    # (D-14b), stderr on a BLOCK does reach the agent, because exit 2 surfaces it
    # (DEC-100) — so this channel is the right one here and the fix is complete.
    t12("D-14a: the block SAYS WHY and carries the install command",
        r3.stderr.strip() != "" and "pip install" in r3.stderr
        and "EARLIER session" in r3.stderr,
        f"stderr was {len(r3.stderr)} bytes: {r3.stderr.strip()[:200]}")

    # THE SHAPE GATE DOES NOT RUN DURING A BOOTSTRAP GRANT, and that is the ruling,
    # not an oversight.
    #
    # Review finding 1 (5th pass) said the grant skipped the DEC-154 shape gate, and I
    # closed it with a line-scan fallback. The GOAL-CHECK then found that fallback
    # violates the signed BRIEF outright — Goal :20-21 "no second code path anywhere,
    # so the brittle regex leaves the tree instead of living on as a fallback nobody
    # exercises", Constraint :48-49 "no line-scan alternative, no degraded mode in any
    # converted script". The user ruled: REMOVE IT, honour the signature.
    #
    # What that costs is EARLIER detection, not correctness — measured before deciding:
    # a malformed state.yaml written during a grant is still refused by check-state.sh
    # at the next /harness entry, naming the same keys, by a session that can read it.
    # One bad file to delete, against a crude reader living on forever in a write guard.
    #
    # These two cases pin the RULED behaviour so nobody "fixes" it back: during a grant
    # the write is allowed, and the entry gate is the backstop.
    grant = fixture(FIXTURE_MANIFEST)
    sp2 = ".harness/harness/features/FEAT-01/runs/r1/state.yaml"
    rbad = fire_noyaml(grant, sp2, "sess-shape",
                       content="run_id: r1\nfindings: a notebook of prose\n")
    t12("grant: a malformed state.yaml is ALLOWED (no fallback — BRIEF Goal :20-21)",
        rbad.returncode == 0,
        f"exit {rbad.returncode}: {rbad.stderr.strip()[:200]}")

    grant_ok = fixture(FIXTURE_MANIFEST)
    rok = fire_noyaml(grant_ok, sp2, "sess-shape-ok",
                      content="run_id: r1\nstatus: complete\n")
    t12("grant: a well-formed state.yaml is allowed too (the grant is not selective)",
        rok.returncode == 0, f"exit {rok.returncode}: {rok.stderr.strip()[:200]}")

    # And WITH a parser the gate is unchanged — this is what makes the pair meaningful
    # rather than "the hook allows everything".
    withyaml = fixture(FIXTURE_MANIFEST)
    rgated = fire(withyaml, sp2, content="run_id: r1\nfindings: prose\n")
    t12("with a parser, the shape gate still BLOCKS the same content",
        rgated.returncode == 2 and "DEC-154" in rgated.stderr,
        f"exit {rgated.returncode}: {rgated.stderr.strip()[:200]}")

    # Self-cleaning: once yaml imports again the marker is removed, so a machine that
    # gets fixed does not carry a spent grant forever.
    # Control-plane target, for T-01's reason: this is an allow assertion, and an
    # in-root product-shaped path stops being owned once T-02 lands.
    r4 = fire(root, ".harness/allowed/d.md")
    t12("the marker self-unlinks once PyYAML imports again",
        r4.returncode == 0 and not os.path.exists(marker),
        f"exit {r4.returncode}, marker present: {os.path.exists(marker)}")

    fails = 0
    for name, ok, detail in T12:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(T12) - fails}/{len(T12)} T-12 cases passed.")
    return fails


FLEET = []


def fleet_case(name, ok, detail=""):
    FLEET.append((name, ok, detail))


def run_fleet():
    # FEAT-15 T-01 — REQ-03 and REQ-04. The fleet declaration resolves once per
    # invocation, and ABSENT is a different answer from UNREADABLE: a project with no
    # factory keeps today's behaviour, while a project whose factory declaration cannot
    # be read refuses EVERY governed write, not only writes to workspace paths. The
    # value that identifies a product path is the one that failed, so enforcing "the
    # parts we can still read" would mean classifying paths with the classifier missing.
    #
    # Every ALLOW assertion below targets .harness/allowed/x.md and never allowed/x.md.
    # An in-root product-shaped path stops being owned at T-02, so a product-shaped
    # allow here would flip to exit 2 then — collapsing case (a) and case (b) into
    # both-halves-refuse, which is exactly the degenerate pair these cases exist to
    # rule out.
    # A fleet that load_fleet actually ACCEPTS. The board no longer lives here (T-02/T-03) — a
    # fleet member's board is read remotely, through factory_config.product_config, and never
    # from a repos[] entry. This fixture exercises the write guard through resolve_fleet, which
    # reads name and workspace_root only, so nothing about it needs a board at all.
    good_repos = ("schema: factory-fleet/1\n"
                  "workspace_root: /tmp/harness-fixture-workspaces\n"
                  "repos:\n"
                  "  - name: nobody/example\n"
                  "    default_branch: main\n")

    # (a) NO fleet file — the no-factory project. Paired with (b) below, because an
    # allow-all guard passes (a) alone and a block-all guard passes (b) alone.
    none_root = fixture_fleet(FIXTURE_MANIFEST, None)
    a_in = fire(none_root, ".harness/allowed/x.md")
    a_out = subprocess.run(
        [HOOK],
        input=json.dumps({"agent_type": "harness-documentor", "tool_name": "Write",
                          "tool_input": {"file_path": "/tmp/uat-no-fleet-scratch.py",
                                         "content": "x"}}),
        capture_output=True, text=True,
        env=_env(none_root))

    # (b) fleet.yaml is BROKEN YAML — the same write the agent owns, inside the same
    # fixture root, must now be refused.
    bad_root = fixture_fleet(FIXTURE_MANIFEST, "schema: [unclosed\n")
    b = fire(bad_root, ".harness/allowed/x.md")

    fleet_case(
        "(a)+(b) PAIR: with no fleet the owned write passes; with a broken fleet the "
        "SAME write is refused",
        a_in.returncode == 0 and b.returncode == 2 and "fleet.yaml" in b.stderr,
        f"no-fleet got {a_in.returncode} (want 0); broken got {b.returncode} (want 2), "
        f"stderr={b.stderr.strip()[:160]!r}")

    fleet_case(
        "(a) with no fleet, a scratch path outside the root still gets no verdict",
        a_out.returncode == 0,
        f"got {a_out.returncode} (want 0), stderr={a_out.stderr.strip()[:160]!r}")

    # (c) fleet.yaml PARSES but omits workspace_root. Distinct from (b): the file is
    # valid YAML and the failure is a missing key, so a check that only guards the
    # parser would let this through with workspace_root unset.
    nows_root = fixture_fleet(
        FIXTURE_MANIFEST,
        "schema: factory-fleet/1\n"
        "repos:\n"
        "  - { name: nobody/example, default_branch: main }\n")
    c = fire(nows_root, ".harness/allowed/x.md")
    fleet_case(
        "(c) a fleet that parses but omits workspace_root refuses the owned write",
        c.returncode == 2,
        f"got {c.returncode} (want 2), stderr={c.stderr.strip()[:160]!r}")

    # (d) a WELL-FORMED fleet changes no existing verdict. T-01 resolves the names and
    # hands them to T-02; on its own it must be invisible.
    ok_root = fixture_fleet(FIXTURE_MANIFEST, good_repos)
    d_allow = fire(ok_root, ".harness/allowed/x.md")
    d_deny = fire(ok_root, "forbidden/thing.md")
    fleet_case(
        "(d) PAIR: a well-formed fleet leaves both verdicts unchanged",
        d_allow.returncode == 0 and d_deny.returncode == 2,
        f"owned got {d_allow.returncode} (want 0), forbidden got {d_deny.returncode} "
        f"(want 2)")

    # (e) the muzzle. factory_config's import prints a discard notice to stderr under a
    # fixture root that holds no .harness/harness/docs/SPEC.md probe. It must not reach the agent on a
    # write that PASSES — noise on an exit-0 path is indistinguishable from a verdict.
    fleet_case(
        "(e) the lazy factory_config import leaks nothing to stderr on a passing write",
        d_allow.returncode == 0 and d_allow.stderr.strip() == "",
        f"exit {d_allow.returncode}, stderr={d_allow.stderr.strip()[:200]!r}")

    # ---- T-02: the two bases, asserted as pairs in both directions ----
    #
    # A fixture whose fleet declares a repo that is NOT harness, with workspace_root
    # inside the same tempdir. Nothing needs to exist on disk under the workspace: the
    # branch is a path comparison, not a stat.
    ws = tempfile.mkdtemp()
    two_base_manifest = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain:
          - { path: src/**, upsert: true }
      - name: harness-documentor
        domain:
          - { path: .harness/allowed/**, upsert: true }
shared:
  - { path: package.json }
"""
    two_base_fleet = ("schema: factory-fleet/1\n"
                      f"workspace_root: {ws}\n"
                      "repos:\n"
                      "  - name: acme/widget\n"
                      "    default_branch: main\n")
    tb = fixture_fleet(two_base_manifest, two_base_fleet)
    prod_src = os.path.join(ws, "widget", "src", "main.py")

    def fire_abs(root, abspath, agent):
        return subprocess.run(
            [HOOK],
            input=json.dumps({"agent_type": agent, "tool_name": "Write",
                              "tool_input": {"file_path": abspath, "content": "x"}}),
            capture_output=True, text=True,
            env=_env(root))

    # (f) THE PRODUCT BASE, as a discriminating pair from ONE fixture. Either half
    # alone is what a broken guard produces: an allow-all passes the granted write, a
    # block-all refuses the ungranted one.
    f_yes = fire_abs(tb, prod_src, "harness-backend-dev")
    f_no = fire_abs(tb, prod_src, "harness-documentor")
    fleet_case(
        "(f) PAIR: in a product checkout, src/** grants the owner and refuses a "
        "persona without it",
        f_yes.returncode == 0 and f_no.returncode == 2,
        f"granted got {f_yes.returncode} (want 0), ungranted got {f_no.returncode} "
        f"(want 2)")

    # (g) THE MIRROR-IMAGE BUG, both directions, from the same fixture. This is the
    # defect the feature exists to close: the same logical path was blocked inside
    # harness and permitted outside it.
    g_in_root = fire_abs(tb, os.path.join(tb, "src", "main.py"), "harness-backend-dev")
    fleet_case(
        "(g) PAIR: src/** refuses <root>/src/main.py and permits "
        "<workspace>/widget/src/main.py",
        g_in_root.returncode == 2 and f_yes.returncode == 0,
        f"in-root got {g_in_root.returncode} (want 2), in-product got "
        f"{f_yes.returncode} (want 0)")

    # (h) THE OTHER DIRECTION: a control-plane grant must not reach a product
    # checkout's own .harness/. Paired with its in-root twin so neither an allow-all
    # nor a block-all guard passes.
    h_in = fire_abs(tb, os.path.join(tb, ".harness", "allowed", "x.md"),
                    "harness-documentor")
    h_out = fire_abs(tb, os.path.join(ws, "widget", ".harness", "allowed", "x.md"),
                     "harness-documentor")
    fleet_case(
        "(h) PAIR: a .harness/** grant permits it in root and refuses it in a product "
        "checkout",
        h_in.returncode == 0 and h_out.returncode == 2,
        f"in-root got {h_in.returncode} (want 0), in-product got {h_out.returncode} "
        f"(want 2)")

    # (i) UNDER workspace_root, BELONGING TO NO DECLARED REPO — refused, and the
    # message must name the fleet file so the operator knows which file to edit.
    i = fire_abs(tb, os.path.join(ws, "undeclared", "src", "main.py"),
                 "harness-backend-dev")
    fleet_case(
        "(i) a path under workspace_root for an undeclared repo is refused, naming "
        "the fleet",
        i.returncode == 2 and "fleet" in i.stderr,
        f"got {i.returncode} (want 2), stderr={i.stderr.strip()[:180]!r}")

    # (j) SCRATCH IS STILL NOT A DOMAIN QUESTION (REQ-05). Asserted from the SAME
    # fixture that refuses (i), so this is not an allow-all passing by accident.
    j = fire_abs(tb, "/tmp/feat15-scratch-probe.py", "harness-backend-dev")
    fleet_case(
        "(j) a scratch path outside both bases still gets no verdict",
        j.returncode == 0,
        f"got {j.returncode} (want 0), stderr={j.stderr.strip()[:180]!r}")

    # ---- T-03: the mirror image, both directions, and explicit Harness entries ----
    #
    # Every group below is a PAIR asserted from ONE fixture and ONE manifest. Either
    # half alone is what a broken guard produces: a guard that widened both bases
    # passes the product half and fails the harness half; a guard that refused
    # everything outside the root passes the harness half and fails the product half.
    # Each assertion is named for the direction it protects, so a failure says which
    # half of the mirror broke.

    def two_base_fleet_for(workspace):
        return ("schema: factory-fleet/1\n"
                f"workspace_root: {workspace}\n"
                "repos:\n"
                "  - name: acme/widget\n"
                "    default_branch: main\n")

    # PAIR A — the PRODUCT half. One persona, exactly one writable glob, product-shaped.
    ws_a = tempfile.mkdtemp()
    a_root = fixture_fleet("""schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: src/**, upsert: true }
""", two_base_fleet_for(ws_a))
    a_in = fire_abs(a_root, os.path.join(a_root, "src", "main.py"), "harness-documentor")
    a_out = fire_abs(a_root, os.path.join(ws_a, "widget", "src", "main.py"),
                     "harness-documentor")
    fleet_case(
        "A PAIR: a product-shaped glob is REFUSED in the harness root and PERMITTED in "
        "the product checkout",
        a_in.returncode == 2 and a_out.returncode == 0,
        f"harness-base got {a_in.returncode} (want 2 — a src/** grant must not reach "
        f"this repo), product-base got {a_out.returncode} (want 0)")

    # PAIR B — the CONTROL-PLANE half. A product repository can perfectly well contain a
    # directory called .harness/; a control-plane grant must still not reach it.
    ws_b = tempfile.mkdtemp()
    b_root = fixture_fleet("""schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/expertise/**, upsert: true }
""", two_base_fleet_for(ws_b))
    b_in = fire_abs(b_root, os.path.join(b_root, ".harness", "expertise", "x.md"),
                    "harness-documentor")
    b_out = fire_abs(b_root, os.path.join(ws_b, "widget", ".harness", "expertise", "x.md"),
                     "harness-documentor")
    fleet_case(
        "B PAIR: a control-plane glob is PERMITTED in the harness root and REFUSED in "
        "the product checkout",
        b_in.returncode == 0 and b_out.returncode == 2,
        f"harness-base got {b_in.returncode} (want 0), product-base got "
        f"{b_out.returncode} (want 2 — a .harness/** grant must not reach a product's "
        f"own control plane)")

    # PAIR C — EXPLICIT HARNESS ENTRIES. These are target-side exceptions for paths
    # whose names are otherwise product-shaped. Hidden control roots are also
    # filtered from product checkouts by `is_control_plane_glob`.
    #
    # Its own manifest, because neither fixture above carries these globs. Two
    # personas: documentor holds docs, shared instructions and neutral OMP roots;
    # dev-ops holds `.github/**`.
    ws_c = tempfile.mkdtemp()
    c_root = fixture_fleet("""schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: docs/**, upsert: true }
          - { path: .harness/*/docs/**, upsert: true }
          - { path: README.md, upsert: true }
          - { path: AGENTS.md, upsert: true }
          - { path: .agents/**, upsert: true }
          - { path: .omp/**, upsert: true }
      - name: harness-dev-ops
        domain:
          - { path: .github/**, upsert: true }
""", two_base_fleet_for(ws_c))
    DOC, OPS = "harness-documentor", "harness-dev-ops"
    c_h_docs = fire_abs(c_root, os.path.join(c_root, ".harness", "harness", "docs", "guide.md"), DOC)
    c_h_prin = fire_abs(c_root, os.path.join(c_root, "docs", "PRINCIPLES.md"), DOC)
    c_h_read = fire_abs(c_root, os.path.join(c_root, "README.md"), DOC)
    c_h_gh = fire_abs(c_root, os.path.join(c_root, ".github", "workflows", "tests.yml"), OPS)
    c_h_agents_doc = fire_abs(c_root, os.path.join(c_root, "AGENTS.md"), DOC)
    c_h_agents_root = fire_abs(c_root, os.path.join(c_root, ".agents", "skills", "x", "SKILL.md"), DOC)
    c_h_omp = fire_abs(c_root, os.path.join(c_root, ".omp", "agents", "x.md"), DOC)
    fleet_case(
        "C harness base: explicit Harness entries resolve, including AGENTS.md, "
        ".agents/** and .omp/**",
        all(r.returncode == 0 for r in (
            c_h_docs, c_h_prin, c_h_read, c_h_agents_doc, c_h_agents_root, c_h_omp, c_h_gh)),
        f".harness/*/docs {c_h_docs.returncode}, PRINCIPLES {c_h_prin.returncode}, "
        f"README {c_h_read.returncode}, AGENTS {c_h_agents_doc.returncode}, "
        f".agents {c_h_agents_root.returncode}, .omp {c_h_omp.returncode}, "
        f".github {c_h_gh.returncode} (all want 0)")

    # THE NOT-WIDENED ASSERTION, and the persona is part of it. Fired against a persona
    # never granted docs/**, this exits 2 for the wrong reason and would pass under
    # exactly the rule it exists to catch. It must be the SAME persona that is permitted
    # the granted docs path above.
    c_h_bare = fire_abs(c_root, os.path.join(c_root, "docs", "guide.md"), DOC)
    fleet_case(
        "C harness base: .harness/*/docs/** was NOT widened to docs/** — the same persona "
        "permitted .harness/harness/docs/guide.md is REFUSED docs/guide.md",
        c_h_docs.returncode == 0 and c_h_bare.returncode == 2,
        f".harness/harness/docs/guide.md got {c_h_docs.returncode} (want 0), docs/guide.md got "
        f"{c_h_bare.returncode} (want 2), same persona {DOC}")

    c_p_read = fire_abs(c_root, os.path.join(ws_c, "widget", "README.md"), DOC)
    c_p_docs = fire_abs(c_root, os.path.join(ws_c, "widget", "docs", "guide.md"), DOC)
    c_p_gh = fire_abs(c_root, os.path.join(ws_c, "widget", ".github", "workflows", "ci.yml"), OPS)
    c_p_agents = fire_abs(c_root, os.path.join(ws_c, "widget", ".agents", "skills", "x", "SKILL.md"), DOC)
    c_p_omp = fire_abs(c_root, os.path.join(ws_c, "widget", ".omp", "agents", "x.md"), DOC)
    fleet_case(
        "C product base: product README.md, docs/ and .github/ remain writable, "
        "while Harness grants to .agents/ and .omp/ stay checkout-local",
        all(r.returncode == 0 for r in (c_p_read, c_p_docs, c_p_gh))
        and c_p_agents.returncode == 2 and c_p_omp.returncode == 2,
        f"README {c_p_read.returncode}, docs/guide.md {c_p_docs.returncode}, "
        f".github {c_p_gh.returncode} (want 0); .agents {c_p_agents.returncode}, "
        f".omp {c_p_omp.returncode} (want 2)")

    # ---- T-04: the RESOLVE path gets the same base treatment (REQ-07) ----
    #
    # The --resolve branch exits before domain_check() and carries its own root
    # derivation and its own manifest load, so T-02's change does not reach it by
    # inheritance. A resolver that named an owner for a path the hook refuses is the
    # build-time discovery check-plan-routes.py exists to prevent — a plan signed on a
    # route the build rejects. Asserted on the exact stdout TOKENS, never on exit code
    # alone: this branch exits 0 in every case, so the code proves nothing.
    ws_r = tempfile.mkdtemp()
    r_root = fixture_fleet("""schema_version: 1
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain:
          - { path: src/**, upsert: true }
""", two_base_fleet_for(ws_r))

    def resolve_in(root, path):
        return subprocess.run([HOOK, "--resolve", path], capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=20,
                              env=_env(root))

    r_prod = resolve_in(r_root, os.path.join(ws_r, "widget", "src", "main.py"))
    r_harn = resolve_in(r_root, os.path.join(r_root, "src", "main.py"))
    r_undec = resolve_in(r_root, os.path.join(ws_r, "undeclared", "src", "main.py"))
    fleet_case(
        "T-04 resolve PAIR: a product path names the src/** owner, the SAME path in "
        "the harness root resolves to NOBODY",
        "harness-backend-dev" in r_prod.stdout.split()
        and r_harn.stdout.strip() == "NOBODY",
        f"product stdout={r_prod.stdout.strip()!r} (want harness-backend-dev), "
        f"harness stdout={r_harn.stdout.strip()!r} (want NOBODY)")
    fleet_case(
        "T-04 resolve: a path under workspace_root for an undeclared repo resolves to "
        "NOBODY, never silence",
        r_undec.stdout.strip() == "NOBODY" or r_undec.returncode == 2,
        f"stdout={r_undec.stdout.strip()!r}, exit {r_undec.returncode}")

    # Against the LIVE root, not a fixture — this is what guards the tree-wide
    # check-plan-routes.py run that CI requires on main.
    # Since FEAT-22's T-02 the documentor holds `.harness/*/docs/**`, so the moved
    # SPEC resolves through a real grant; the named-entry half of the rule is
    # exercised by the fleet cases above.
    r_live = subprocess.run([HOOK, "--resolve", ".harness/harness/docs/SPEC.md"],
                            capture_output=True, text=True, stdin=subprocess.DEVNULL,
                            timeout=20, env=_env(ROOT))
    fleet_case(
        "T-04 resolve, LIVE tree: .harness/harness/docs/SPEC.md names harness-documentor — the "
        "named entries hold target-side",
        "harness-documentor" in r_live.stdout.split(),
        f"stdout={r_live.stdout.strip()!r} (want harness-documentor, NOBODY means the "
        f"rule was built glob-keyed)")

    # ---- THE SYMLINK ESCAPE, surfaced by the review panel 2026-08-11 ----
    #
    # A link inside a granted directory pointing OUT of it: <granted docs>/<link> ->
    # ../../.claude let harness-documentor write .claude/agents/*. Reproduced against
    # the live tree before the fix — through the link exit 0, the same file named
    # directly exit 2.
    #
    # PRE-EXISTING, not a regression from the two-base rule: before that change
    # `docs/**` matched any docs/… path with no target-side test, so the same link
    # granted the same write. Fixed here because the panel found it and it is live.
    #
    # Asserted as a PAIR from ONE fixture. A guard that refused everything would pass
    # the escape half alone, so the legitimate write is part of the assertion.
    esc_root = fixture("""schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/*/docs/**, upsert: true }
""")
    os.makedirs(os.path.join(esc_root, ".harness", "harness", "docs"))
    os.makedirs(os.path.join(esc_root, ".claude", "agents"))
    os.symlink(os.path.join(esc_root, ".claude"),
               os.path.join(esc_root, ".harness", "harness", "docs", "esc"))
    esc = fire_abs(esc_root, os.path.join(esc_root, ".harness", "harness", "docs", "esc",
                                          "agents", "pwned.md"), "harness-documentor")
    legit = fire_abs(esc_root, os.path.join(esc_root, ".harness", "harness", "docs", "guide.md"),
                     "harness-documentor")
    fleet_case(
        "SYMLINK PAIR: a link out of a granted directory is REFUSED at its real "
        "target, and the ordinary granted write still PASSES",
        esc.returncode == 2 and legit.returncode == 0,
        f"escape got {esc.returncode} (want 2 — the write lands in .claude/agents/), "
        f"legitimate got {legit.returncode} (want 0)")
    fleet_case(
        "SYMLINK: the refusal names the REAL target, not the link path — an agent "
        "told it may not write the docs path would file a bug against the wrong file",
        ".claude/agents/pwned.md" in esc.stderr,
        f"stderr={esc.stderr.strip()[:200]!r}")

    print("--- FEAT-15 T-01..T-04 + symlink escape: fleet, bases, mirror, resolve ---")
    fails = 0
    for name, ok, detail in FLEET:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(FLEET) - fails}/{len(FLEET)} fleet cases passed.\n")
    return fails


# --- FEAT-09 / DEC-179: `--resolve <path>`. Eight cases, one per clause of T-01's
# intent. The two stdin cases are the reason this mode exists at all: both were
# MEASURED on the pre-change tree — an open pipe blocked indefinitely, and closed
# stdin exited 0 printing nothing, which is a fail-open answer indistinguishable
# from a clean resolve.
def run_resolve():
    fails = 0

    def resolve(path, stdin_mode="closed", timeout=10):
        kw = {"stdin": subprocess.DEVNULL} if stdin_mode == "closed" else {"stdin": os.pipe()[0]}
        r = subprocess.run([HOOK, "--resolve", path], capture_output=True, text=True,
                           timeout=timeout, env=_env(ROOT), **kw)
        return r

    def check(name, ok, detail=""):
        nonlocal fails
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}" + (f"\n        {detail}" if detail else ""))

    # (a) a singly-granted path resolves to exactly one name
    r = resolve(".harness/harness.json")
    check("(a) --resolve: a singly-granted path returns exactly one agent",
          r.stdout.split() == ["harness-dev-ops"], f"got {r.stdout.split()!r}")

    # (b) a doubly-granted path returns BOTH, sorted
    r = resolve(".agents/skills/harness/bin/run-unit-tests.sh")
    check("(b) --resolve: a doubly-granted path returns both grantees",
          sorted(r.stdout.split()) == ["harness-backend-dev", "harness-dev-ops"],
          f"got {r.stdout.split()!r}")

    # (c) NOBODY is a LITERAL EMITTED TOKEN, not silence
    r_nobody = resolve(".agents/skills/harness-spec-driven/SKILL.md")
    check("(c) --resolve: an ungranted path prints the literal NOBODY",
          r_nobody.stdout.split() == ["NOBODY"], f"got {r_nobody.stdout!r}")

    # (d) ...and that same call exits 0 with NON-EMPTY stdout. Separate from (c) on
    # purpose: an exit-0-with-empty-stdout resolver passes any check that only reads
    # the exit code, and that is precisely the fail-open shape.
    check("(d) --resolve: the ungranted call exits 0 and stdout is not empty",
          r_nobody.returncode == 0 and r_nobody.stdout.strip() != "",
          f"exit={r_nobody.returncode} stdout={r_nobody.stdout!r}")

    # (e) an OPEN PIPE nobody writes to must not hang. Pre-change this blocked forever.
    try:
        r_pipe = resolve(".harness/harness.json", stdin_mode="pipe", timeout=10)
        ok_e = r_pipe.stdout.split() == ["harness-dev-ops"]
        detail_e = f"got {r_pipe.stdout.split()!r}"
    except subprocess.TimeoutExpired:
        r_pipe, ok_e, detail_e = None, False, "TIMED OUT — the branch read stdin"
    check("(e) --resolve: an open pipe on stdin still answers within 10s", ok_e, detail_e)

    # (f) closed stdin gives the BYTE-IDENTICAL answer. The two stdin shapes failed
    # differently before (hang vs silent exit 0), so equality across them is the
    # assertion that matters, not either one alone.
    r_closed = resolve(".harness/harness.json", stdin_mode="closed")
    check("(f) --resolve: closed stdin is byte-identical to an open pipe",
          r_pipe is not None and r_closed.stdout == r_pipe.stdout,
          f"closed={r_closed.stdout!r} pipe={(r_pipe.stdout if r_pipe else None)!r}")

    # (g)+(h) THE HOOK PATH IS UNCHANGED. Without these two the whole mode could have
    # been added by breaking enforcement and nothing here would notice.
    def hook(path, agent):
        payload = {"agent_type": agent, "tool_name": "Write",
                   "tool_input": {"file_path": path, "content": "x"}}
        return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                              text=True, env=_env(ROOT))
    # ABSOLUTE, like every other case in this file. These two were the only relative
    # paths in the suite, and the gate resolves a relative target with os.path.abspath —
    # against the CWD, not the root — so (h) read out-of-domain whenever the runner was
    # launched from anywhere but the repository root. That is the other half of #556.
    # Claude Code sends an absolute file_path; these now say what production sends.
    r = hook(f"{ROOT}/.agents/skills/harness/bin/check-domain.sh", "harness-documentor")
    check("(g) no --resolve: an out-of-domain Write still exits 2",
          r.returncode == 2, f"got {r.returncode}")
    r = hook(f"{ROOT}/.harness/harness/docs/SPEC.md", "harness-documentor")
    check("(h) no --resolve: an in-domain Write still exits 0",
          r.returncode == 0, f"got {r.returncode}")

    # (i)+(j) VF-1 REGRESSION. (g) and (h) above assert the right thing and CANNOT SEE this:
    # they inherit the runner's environment, which happens to be clean. Mode was selected by
    # os.environ, not argv, so a HARNESS_RESOLVE_PATH inherited from the caller turned the
    # whole guard off — exit 0, no stderr, nothing logged. These two set it EXPLICITLY in the
    # subprocess env, which is the only way to reach the branch that was broken.
    # (j) uses the EMPTY STRING on purpose: the selector is `is not None`, so "" qualified.
    def hook_env(path, agent, resolve_value):
        payload = {"agent_type": agent, "tool_name": "Write",
                   "tool_input": {"file_path": path, "content": "x"}}
        return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                              text=True, env=_env(ROOT,
                                                  HARNESS_RESOLVE_PATH=resolve_value))
    # EXIT 2 ALONE IS NOT ENOUGH, and the delta review caught this. There are five distinct
    # exit-2 sites in this script and FOUR of them are inside the resolve branch (missing
    # manifest, duplicate key, parse error, unreadable root). A reimplementation that still
    # leaked the env var but happened to exit 2 from one of those would pass a returncode-only
    # assertion while VF-1 was wide open. Assert the DENIAL TEXT, which only the hook path
    # emits — the same convention cases (c)/(d) already use.
    def denied(r):
        return r.returncode == 2 and "may not write" in (r.stderr or "")
    r = hook_env(".agents/skills/harness/bin/check-domain.sh", "harness-documentor",
                 ".harness/harness.json")
    check("(i) VF-1: HARNESS_RESOLVE_PATH set in the env does NOT disable the hook",
          denied(r), f"got {r.returncode}, stderr={r.stderr!r}")
    r = hook_env(".agents/skills/harness/bin/check-domain.sh", "harness-documentor", "")
    check("(j) VF-1: an EMPTY HARNESS_RESOLVE_PATH does NOT disable the hook",
          denied(r), f"got {r.returncode}, stderr={r.stderr!r}")

    print(f"\n{10 - fails}/10 --resolve cases passed.\n")
    return fails


# ============ #132: the shape gate on the routes PreToolUse cannot reach ============
# Measured before the fix, ONE 400-line feature.yaml against a 200-line budget:
#   Write/harness-orchestrator exit 2 · Edit exit 0 · Bash exit 0 · Write/MAIN exit 0.
# One route of four. Each case below is one of those routes, run against a REAL file in a
# fixture repo, because the whole point of the post mode is that it reads the disk rather
# than a payload it could have been handed.

POST = []


def post(name, ok, detail=""):
    POST.append((name, ok, detail))


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


def _write_while_sweep_reads_fifo(root, payload, fifo_path, mid_write):
    """Block the sweep after its start mark, then perform one write it already walked past."""
    process = subprocess.Popen(
        [HOOK, "--post"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, env=_env(root))
    process.stdin.write(json.dumps(payload))
    process.stdin.close()
    process.stdin = None
    writer = None
    deadline = time.monotonic() + 30
    try:
        while writer is None:
            try:
                writer = os.open(fifo_path, os.O_WRONLY | os.O_NONBLOCK)
            except OSError as error:
                if error.errno != errno.ENXIO:
                    raise
                if process.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError("sweep never opened the FIFO — sync premise broke")
                time.sleep(0.005)
        os.unlink(fifo_path)
        mid_write()
        os.close(writer)
        writer = None
        return process.communicate(timeout=30)
    finally:
        if writer is not None:
            os.close(writer)
        if process.poll() is None:
            process.kill()
            process.communicate()


def run_post():
    d = fixture(FIXTURE_MANIFEST)
    fdir = os.path.join(d, ".harness", "harness", "features", "FEAT-X")
    os.makedirs(fdir)
    fy = os.path.join(fdir, "feature.json")
    rel_fy = ".harness/harness/features/FEAT-X/feature.json"

    def write(nlines):
        # A LEGAL ten-key document, padded with blank lines to an exact length.
        # T-06 put the schema on this path, so a fixture meant to be judged on its LINE
        # COUNT must be schema-clean or it is denied for a reason its case never intended
        # — a green-looking test asserting the wrong cause. Trailing whitespace is
        # insignificant to a JSON parser, so padding this way changes the line count and
        # nothing else.
        import json as _json
        doc = _json.dumps({"feature_id": "FEAT-X", "branch": "none", "pr": None, "review_sha": "none", "cycles_used": 0,
                           "max_total_cycles": 10, "runs": []}, indent=2)
        body = doc.splitlines()
        with open(fy, "w") as f:
            f.write("\n".join(body + [""] * max(0, nlines - len(body))) + "\n")

    def edit_payload(agent="harness-orchestrator"):
        p = {"tool_name": "Edit", "hook_event_name": "PostToolUse",
             "tool_input": {"file_path": fy, "old_string": "a", "new_string": "b"}}
        if agent:
            p["agent_type"] = agent
        return p

    bash_payload = {"agent_type": "harness-orchestrator", "tool_name": "Bash",
                    "hook_event_name": "PostToolUse",
                    "tool_input": {"command": "sed -i '' s/a/b/ " + fy}}

    # --- ROUTE 2: Edit. Its payload carries old_string/new_string and NO whole-file
    # content, which is exactly why the pre hook cannot judge it and exits 0.
    write(400)
    r = fire_post(d, edit_payload())
    post("route 2 — post Edit on an over-budget file exits 2",
         r.returncode == 2 and "budget is 300" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip().splitlines()[:1]}")

    pre = subprocess.run([HOOK], input=json.dumps({
        "agent_type": "harness-orchestrator", "tool_name": "Edit",
        "tool_input": {"file_path": fy, "old_string": "a", "new_string": "b"}}),
        capture_output=True, text=True, env=_env(d))
    # The claim is about the SHAPE finding, not the exit code, and the difference is not
    # pedantry: harness-orchestrator has no domain in FIXTURE_MANIFEST, so the pre hook
    # exits 2 here for a DOMAIN reason. A first draft asserted `returncode == 0` and
    # failed — reading, wrongly, as the pre hook having gained shape coverage on Edit.
    post("route 2 — the PRE hook reports NO shape finding on that same Edit",
         "budget is 300" not in pre.stderr,
         f"exit {pre.returncode}: {pre.stderr.strip()[:120]}")

    # --- ROUTE 3: Bash. No file_path in the payload at all, so this exercises the sweep.
    r = fire_post(d, bash_payload)
    post("route 3 — post Bash sweeps and finds the over-budget file",
         r.returncode == 2 and "budget is 300" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip().splitlines()[:1]}")

    # --- ROUTE 4: the MAIN SESSION, which has no agent_type and was exempted from the
    # shape gate by the DOMAIN carve-out sitting above it.
    r = subprocess.run([HOOK], input=json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": fy, "content": "\n".join(["x: 1"] * 400)}}),
        capture_output=True, text=True, env=_env(d))
    post("route 4 — the MAIN SESSION is no longer exempt from the shape gate",
         r.returncode == 2 and "budget is 300" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip().splitlines()[:1]}")

    # --- THE ENFORCED BUDGET, AT ITS BOUNDARY (review F-02). 400-vs-10 passes against
    # `> 250` and `> 350` and against every `>` flipped to `>=`, because nothing between
    # 200 and 400 is ever probed. Cross each budget by exactly ONE line, in both
    # directions, so the comparison itself is bound and not merely the message text.
    for _n, _want in ((301, True), (300, False)):
        write(_n)
        r = fire_post(d, edit_payload())
        post(f"feature.json at {_n} lines {'IS' if _want else 'is NOT'} over the 300 budget",
             (r.returncode == 2 and "budget is 300" in r.stderr) == _want,
             f"exit {r.returncode}: {r.stderr.strip()[:100]}")

    # THE COMMENT BUDGET CASE IS DELETED, not rewritten. T-06 removed the check from both
    # check-domain.sh and check-state.sh because JSON has no comments, so it could never
    # fire — and a check that cannot fire is a check a reader trusts. A case asserting a
    # budget that no longer exists would pass by never triggering it, which is the
    # vacuous-assertion shape this suite exists to catch.

    # --- THE OTHER THREE GATES, IN POST MODE (review F-03). The handoff branch and the
    # state.yaml checkpoint branch could each be replaced with `if False:` and both suites
    # stayed green; three of the four sweep globs could be deleted unnoticed. Each file
    # below is written under a DIFFERENT glob and reached through the Bash SWEEP, so this
    # binds the branch and its glob at once.
    os.makedirs(os.path.join(fdir, "notes"), exist_ok=True)
    os.makedirs(os.path.join(fdir, "runs", "r1"), exist_ok=True)
    write(10)
    for label, relpath, body, needle in (
        ("handoff cap (DEC-159)", "notes/handoff-plan.md",
         "\n".join(["## Next", "## Trust", "## Dead ends", "## Working set"] + ["x"] * 70),
         "cap is 60"),
        ("handoff missing sections", "notes/handoff-build.md", "## Next\nonly one\n",
         "missing required section"),
        ("state.yaml checkpoint keys (DEC-154)", "runs/r1/state.yaml",
         "schema_version: 1\nrun_id: r1\nfindings: a notebook entry\n", "non-checkpoint top-level key"),
        ("STATE.md sections (SPEC 2)", "STATE.md", "## Current\n## Not A Section\n",
         "illegal section"),
    ):
        _p = os.path.join(fdir, relpath)
        with open(_p, "w") as f:
            f.write(body)
        r = fire_post(d, bash_payload)
        post(f"the SWEEP reaches and enforces {label}",
             r.returncode == 2 and needle in r.stderr,
             f"exit {r.returncode}: {r.stderr.strip()[:140]}")
        os.remove(_p)

    # --- F-06: `_norm`'s worktree strip is load-bearing, and the sweep's worktree tier
    # with it. A live agent worktree in this repo held 38 files matching the sweep globs
    # and the sweep reached NONE of them before this. Every harness agent works in one.
    # CONVERTED to a real linked worktree (FEAT-30 T-04, D-09). It was a bare directory,
    # which reached the shape regexes only through the fixed-segment strip this task
    # deletes. NO ASSERTION BELOW CHANGES — the fixture is what was wrong, not the claim.
    # wt1 is still exactly one segment deep, so this conversion also passes against the
    # eeabc59 guard and does not weaken T-04's red proof.
    make_linked_worktree(d, os.path.join(d, ".claude", "worktrees", "wt1"), "wt1")
    wt = os.path.join(d, ".claude", "worktrees", "wt1", ".harness", "harness", "features", "FEAT-W")
    os.makedirs(wt, exist_ok=True)
    write(10)
    fire_post(d, bash_payload)                      # advance the stamp past everything
    r0 = fire_post(d, bash_payload)                 # nothing fresh -> silence
    with open(os.path.join(wt, "feature.json"), "w") as f:
        f.write(_legal_feature_json(400))
    r1 = fire_post(d, bash_payload)
    post("the sweep reaches a file inside .claude/worktrees/ (and was silent before it)",
         r0.returncode == 0 and r1.returncode == 2 and "budget is 300" in r1.stderr,
         f"baseline exit {r0.returncode}, after exit {r1.returncode}")

    # --- THE HIGH-WATER MARK. Two review findings in one: no dedup (five unrelated Bash
    # calls re-reported one bad file five times) and bulk mtime refresh (`git checkout --`
    # resets mtime to now, dragging the whole tree into a fixed window at once).
    r_rep = [fire_post(d, bash_payload).returncode for _ in range(4)]
    post("a reported file is NOT re-reported on the next sweep",
         r_rep == [0, 0, 0, 0], f"got {r_rep} (want all 0 after the first report)")

    # --- CLAUDE.md (issue #139), on the routes that matter for it. It is edited by the
    # MAIN SESSION, which #132 had exempted entirely, and by Edit far more than by Write —
    # so a Write-only gate would have bound the one route nobody uses for this file.
    _cm = os.path.join(d, "CLAUDE.md")
    for _n, _want in ((81, True), (80, False)):
        with open(_cm, "w") as f:
            f.write("\n".join(f"line {i}" for i in range(_n)) + "\n")
        # route 1: main-session Write, measured on the payload
        rw = subprocess.run([HOOK], input=json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": _cm,
                           "content": "\n".join(f"line {i}" for i in range(_n))}}),
            capture_output=True, text=True, env=_env(d))
        # route 2: main-session Edit, measured on disk
        os.utime(_cm, None)
        re_ = fire_post(d, {"tool_name": "Edit", "hook_event_name": "PostToolUse",
                            "tool_input": {"file_path": _cm, "old_string": "a",
                                           "new_string": "b"}})
        hit_w = rw.returncode == 2 and "budget is 80" in rw.stderr
        hit_e = re_.returncode == 2 and "budget is 80" in re_.stderr
        post(f"CLAUDE.md at {_n} lines {'IS' if _want else 'is NOT'} over the 80 budget, "
             f"on Write AND Edit",
             hit_w == _want and hit_e == _want,
             f"Write exit {rw.returncode}, Edit exit {re_.returncode}")

    # route 3: Bash, via the sweep — the route that has no path in its payload at all.
    with open(_cm, "w") as f:
        f.write("\n".join(f"line {i}" for i in range(81)) + "\n")
    fire_post(d, bash_payload)                       # settle
    os.utime(_cm, None)
    r = fire_post(d, bash_payload)
    post("the SWEEP reaches CLAUDE.md (route 3)",
         r.returncode == 2 and "budget is 80" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip()[:120]}")
    os.remove(_cm)

    # --- ATTRIBUTION ON EVERY ROUTE, not just the sweep (review of PR #152, round 2).
    # The first fix threaded the display path through the Bash sweep alone and left the
    # named-target routes printing a bare "CLAUDE.md". Measured: an agent told its file was
    # 81 lines opened the 74-line root copy and concluded the gate was stale. All three
    # mutations of the threading — `_head` using `rel`, the sweep back to 2-tuples, the
    # call site forcing display=None — survived every gate, because NOTHING bound it.
    #
    # A state file is checked too. The comment justifying the original fix claimed the
    # stripped form "still carries FEAT-NN, enough to tell two checkouts apart"; a reviewer
    # falsified that against this repo the same day, with two live worktrees emitting
    # findings naming identical FEAT strings. Stripping collapses every checkout onto one
    # name for state files as much as for CLAUDE.md.
    # CONVERTED, same reason and same rule as the F-06 fixture above: real linked
    # worktree, both pointer sides, and not one assertion below is adjusted.
    _wt = make_linked_worktree(d, os.path.join(d, ".claude", "worktrees", "wt1"), "wt1")
    os.makedirs(os.path.join(_wt, ".harness", "harness", "features", "FEAT-W"), exist_ok=True)
    _wcm = os.path.join(_wt, "CLAUDE.md")
    _wfy = os.path.join(_wt, ".harness", "harness", "features", "FEAT-W", "feature.json")
    with open(_wcm, "w") as f:
        f.write("\n".join(f"x{i}" for i in range(81)) + "\n")
    with open(_wfy, "w") as f:
        f.write(_legal_feature_json(400))

    for label, path, payload_maker in (
        ("post Edit", _wcm, lambda p: {"hook_event_name": "PostToolUse", "tool_name": "Edit",
                                       "tool_input": {"file_path": p, "old_string": "a",
                                                      "new_string": "b"}}),
        ("post Edit (state file)", _wfy,
         lambda p: {"hook_event_name": "PostToolUse", "tool_name": "Edit",
                    "tool_input": {"file_path": p, "old_string": "a", "new_string": "b"}}),
    ):
        os.utime(path, None)
        r = fire_post(d, payload_maker(path))
        post(f"{label} on a worktree file names the WORKTREE it came from",
             r.returncode == 2 and ".claude/worktrees/wt1" in r.stderr,
             f"exit {r.returncode}: {r.stderr.strip().splitlines()[:1]}")

    # The PRE route too — it measures a payload, and it printed the same bare name.
    rw = subprocess.run([HOOK], input=json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": _wcm,
                       "content": "\n".join(f"x{i}" for i in range(81))}}),
        capture_output=True, text=True, env=_env(d))
    post("pre Write on a worktree file names the WORKTREE it came from",
         rw.returncode == 2 and ".claude/worktrees/wt1" in rw.stderr,
         f"exit {rw.returncode}: {rw.stderr.strip().splitlines()[:1]}")

    # And the SWEEP, which was the only route the first fix covered — kept so a regression
    # there is caught too, not assumed.
    fire_post(d, bash_payload)
    os.utime(_wcm, None)
    rs = fire_post(d, bash_payload)
    post("the sweep still names the worktree it came from",
         rs.returncode == 2 and ".claude/worktrees/wt1" in rs.stderr,
         f"exit {rs.returncode}: {rs.stderr.strip().splitlines()[:1]}")
    shutil.rmtree(_wt, ignore_errors=True)

    # --- DISCRIMINATION. Every case above passes against a gate that exits 2 always.
    write(10)
    for label, payload in (("Edit", edit_payload()), ("Bash", bash_payload)):
        r = fire_post(d, payload)
        post(f"a WITHIN-budget file exits 0 on post {label}",
             r.returncode == 0 and not r.stderr.strip(),
             f"exit {r.returncode}: {r.stderr.strip()[:120]}")

    # --- THE DOMAIN PHASE MUST NOT RUN POST-HOC. The write already landed, so a denial is
    # noise duplicating the pre verdict — and require_or_bootstrap would SPEND the
    # session's single bootstrap grant on a question whose answer can no longer matter.
    # Measured before `_domain_phase` existed: this exited 2 with the domain message.
    ungranted = os.path.join(d, "forbidden", "x.md")
    os.makedirs(os.path.dirname(ungranted))
    open(ungranted, "w").write("x\n")
    r = fire_post(d, {"agent_type": "harness-documentor", "tool_name": "Write",
                      "hook_event_name": "PostToolUse",
                      "tool_input": {"file_path": ungranted}})
    post("post mode does NOT re-run the domain check",
         r.returncode == 0 and "may not write" not in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip()[:120]}")
    # ...and the PRE hook on that same path still blocks, or the line above is only
    # measuring a manifest that grants everything.
    r = fire(d, "forbidden/x.md")
    post("the PRE hook still blocks that same ungranted path",
         r.returncode == 2, f"exit {r.returncode}")

    # --- THE MTIME WINDOW. It is what keeps the sweep off the 515 ms path, so a file
    # older than the window must NOT be re-reported on every subsequent Bash call.
    write(400)
    old = time.time() - 7200
    os.utime(fy, (old, old))
    r = fire_post(d, bash_payload)
    post("the sweep skips an over-budget file older than SWEEP_WINDOW_S",
         r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:120]}")
    # ...and the SAME file, touched, is found again — so the line above is the window
    # working, not the sweep being broken.
    os.utime(fy, None)
    r = fire_post(d, bash_payload)
    post("the same file, freshly touched, IS found",
         r.returncode == 2 and "budget is 300" in r.stderr, f"exit {r.returncode}")

    # --- THE RACE, ASSERTED AS ORDERED BEHAVIOUR (review HIGH-1). A FIFO under the
    # runs/state.yaml glob blocks the sweep after `_now` was captured. feature.json is
    # globbed earlier, so writing it while the FIFO is open is provably mid-walk and too
    # late for this pass. A start-stamped sweep must find it on the NEXT pass; an
    # end-stamped sweep advances beyond the write and loses it permanently.
    write(10)
    fire_post(d, bash_payload)                        # settle: nothing fresh
    fifo_dir = os.path.join(fdir, "runs", "fifo")
    fifo_path = os.path.join(fifo_dir, "state.yaml")
    os.makedirs(fifo_dir, exist_ok=True)
    os.mkfifo(fifo_path)
    sync_error = ""
    blocked_stderr = ""
    try:
        _stdout, blocked_stderr = _write_while_sweep_reads_fifo(
            d, bash_payload, fifo_path, lambda: write(400))
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        sync_error = str(error)
    finally:
        if os.path.exists(fifo_path):
            os.remove(fifo_path)
        os.rmdir(fifo_dir)
    following = fire_post(d, bash_payload)
    kept_visible = (
        not sync_error
        and "budget is 300" not in blocked_stderr
        and following.returncode == 2
        and "budget is 300" in following.stderr
        and rel_fy in following.stderr
    )
    post("a write made during the sweep remains visible to the next sweep",
         kept_visible,
         sync_error or
         f"blocked sweep stderr={blocked_stderr[:120]!r}; next exit "
         f"{following.returncode}: {following.stderr[:160]!r}")

    # --- AN UNREADABLE CANDIDATE MUST NOT ADVANCE THE MARK PAST ITSELF, or a transient
    # permission blip becomes a permanent blind spot by the same mechanism.
    write(400)
    _bad = os.path.join(fdir, "runs", "r2")
    os.makedirs(_bad, exist_ok=True)
    _sy = os.path.join(_bad, "state.yaml")
    with open(_sy, "w") as f:
        f.write("schema_version: 1\n")
    os.chmod(_sy, 0o000)
    try:
        fire_post(d, bash_payload)                   # one candidate unreadable
        os.chmod(_sy, 0o644)
        r = fire_post(d, bash_payload)
        post("an unreadable candidate leaves the mark unadvanced (no permanent blind spot)",
             r.returncode == 2 and "budget is 300" in r.stderr,
             f"exit {r.returncode}: {r.stderr.strip()[:120]}")
    finally:
        os.chmod(_sy, 0o644)
        os.remove(_sy)

    # --- EVERY FINDING NAMES ITS FILE. The sweep walks up to 234 candidates across a main
    # checkout and every worktree; without the path, one logical file present in five
    # checkouts produced five byte-identical findings and zero way to tell them apart.
    write(400)
    os.utime(fy, None)
    r = fire_post(d, bash_payload)
    post("a sweep finding names the file it is about",
         rel_fy in r.stderr, f"stderr lacked {rel_fy}: {r.stderr.strip()[:160]}")

    # --- A POST PAYLOAD WITH NO agent_type still gets the shape gate. That is the shape
    # every Bash and main-session post invocation has, and it is the path argv position 2
    # feeds, so it is the one that would break if the mode flag were read as an identity.
    #
    # NOT a test of the argv blanking itself: mutation showed the suite stays green with
    # that line removed, because "--post" is not `harness-`-prefixed and lands on the same
    # ungoverned branch. The blanking is defensive and this case does not pretend to cover
    # it — a case named for something it cannot detect is worse than no case.
    write(400)
    r = fire_post(d, {"tool_name": "Edit", "tool_input": {"file_path": fy,
                                                          "old_string": "a", "new_string": "b"}})
    post("a post payload with NO agent_type still gets the shape gate",
         r.returncode == 2 and "budget is 300" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip()[:120]}")

    # --- TWO SIGNALS, EITHER SUFFICIENT. The platform's hook_event_name alone must work,
    # or a registration that omits the flag silently degrades to pre-mode.
    r = fire_post(d, edit_payload(), flag=None)
    post("hook_event_name alone selects post mode (no --post flag)",
         r.returncode == 2 and "budget is 300" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip()[:120]}")

    shutil.rmtree(d, ignore_errors=True)

    fails = 0
    print("--- #132: shape coverage on all four write routes ---")
    for name, ok, detail in POST:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(POST) - fails}/{len(POST)} post-mode cases passed.\n")
    return fails


SCHEMA_MANIFEST = FIXTURE_MANIFEST.replace(
    "- { path: .harness/allowed/**, upsert: true }",
    "- { path: .harness/allowed/**, upsert: true }\n"
    "          - { path: .harness/*/features/*/feature.json, upsert: true }")


def _schema_case(name, got, want, extra_ok=True, detail=""):
    ok = got == want and extra_ok
    if ok:
        print(f"ok    schema/{name}")
        return 0
    print(f"FAIL  schema/{name}\n        wanted exit {want}, got {got}. {detail}")
    return 1


def _inject_schema_crash(copied_fs):
    source = open(copied_fs, encoding="utf-8").read()
    start = source.index("def problems_for_text(")
    end = source.index("\n", source.index(":", source.index(")", start)))
    injected = (source[:end + 1]
                + '    raise ValueError("injected: checker is broken")\n'
                + source[end + 1:])
    with open(copied_fs, "w", encoding="utf-8") as copied_file:
        copied_file.write(injected)


def _schema_copy_control(root, rel, illegal, copied_hook):
    result = fire(root, rel, content=illegal, hook=copied_hook)
    detail = " ".join((result.stderr or "").split())[:160]
    return _schema_case(
        "the copied unbroken hook DENIES the illegal document",
        result.returncode, 2, "invented_key" in (result.stderr or ""), detail)


def _schema_crash_control(root, rel, illegal, copied_hook):
    result = fire(root, rel, content=illegal, hook=copied_hook)
    detail = " ".join((result.stderr or "").split())[:160]
    return _schema_case(
        "a CRASHING schema module DENIES the write rather than letting it through",
        result.returncode, 2, "CRASHED" in (result.stderr or ""), detail)


def _schema_crash_cases(root, rel, illegal):
    live_fs = os.path.join(HERE, "feature_schema.py")
    live_before = open(live_fs, "rb").read()
    live_mtime = os.stat(live_fs).st_mtime_ns
    iso = isolated_bin(root)
    copied_hook = os.path.join(iso, "check-domain.sh")
    fails = _schema_copy_control(root, rel, illegal, copied_hook)
    _inject_schema_crash(os.path.join(iso, "feature_schema.py"))
    fails += _schema_crash_control(root, rel, illegal, copied_hook)
    unchanged = (open(live_fs, "rb").read() == live_before
                 and os.stat(live_fs).st_mtime_ns == live_mtime)
    fails += _schema_case(
        "the live feature_schema.py was never written (bytes and mtime unchanged)",
        unchanged, True)
    return fails

def run_schema():
    """Exercise legal, illegal, and crashing feature-schema write checks.

    The manifest grants the path so every result reaches the schema phase. The crashing
    private-copy case proves exceptions block rather than escaping with fail-open exit 1.
    """
    root = fixture(SCHEMA_MANIFEST)
    os.makedirs(os.path.join(root, ".harness", "harness", "features", "FEAT-X"), exist_ok=True)
    rel = ".harness/harness/features/FEAT-X/feature.json"
    legal = _legal_feature_json(0)
    illegal = json.dumps({"feature_id": "FEAT-X", "invented_key": 1}, indent=2)
    allowed = fire(root, rel, content=legal)
    fails = _schema_case(
        "a legal ten-key document is ALLOWED", allowed.returncode, 0,
        detail=" ".join((allowed.stderr or "").split())[:160])
    denied = fire(root, rel, content=illegal)
    fails += _schema_case(
        "an illegal document is DENIED and the offending key is NAMED",
        denied.returncode, 2, "invented_key" in (denied.stderr or ""),
        " ".join((denied.stderr or "").split())[:160])
    fails += _schema_crash_cases(root, rel, illegal)
    shutil.rmtree(root, ignore_errors=True)
    return fails


WT = []


def wt(name, ok, detail=""):
    WT.append((name, ok, detail))


def run_worktree():
    """Issue #103 — an out-of-place git worktree is a mistake, not a supported shape.

    NO GIT IS INVOKED, here or in the guard. Every fixture is built by hand from
    directories and a `.git` FILE holding the `gitdir:` pointer, which is exactly the
    on-disk shape `git worktree add` leaves. Standing up a real worktree would mean the
    suite creating the shape the guard now forbids.

    The manifest is FIXTURE_MANIFEST rather than a fresh one naming harness-backend-dev:
    same `.harness/allowed/**` grant, and `fire` already defaults to the persona it
    names. The persona is not what any of these cases discriminate.

    Every path asserted in-root is under `.harness/`, and that is load-bearing. In the
    harness base a glob match is accepted only when the TARGET passes
    is_control_plane_target, so a grant of `allowed/**` cannot permit `<root>/allowed/x`
    — it exits 2 for the same reason `<root>/src/main.py` does. A shorter path would make
    the paired ALLOW cases fail against correct code.
    """
    fails = 0
    tmp = tempfile.mkdtemp()

    # THE MAIN CHECKOUT. `.git` is a DIRECTORY, which is what makes it the owner.
    root = os.path.join(tmp, "root")
    os.makedirs(os.path.join(root, ".harness"))
    os.makedirs(os.path.join(root, ".git", "worktrees", "sib"))
    os.makedirs(os.path.join(root, ".git", "worktrees", "wt"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)

    def _linked(path, wt_id):
        """A linked worktree, by hand: a `.git` FILE pointing at the owner's entry."""
        os.makedirs(os.path.join(path, ".harness"), exist_ok=True)
        with open(os.path.join(path, ".git"), "w") as f:
            f.write("gitdir: %s\n" % os.path.join(root, ".git", "worktrees", wt_id))
        # ITS OWN MANIFEST, because each of these is used as a session root below and a
        # root with no readable manifest falls to the DEC-101 fail-open — which exits 0
        # for a reason that has nothing to do with worktrees, and proves nothing.
        with open(os.path.join(path, ".harness", "team-config.yaml"), "w") as f:
            f.write(FIXTURE_MANIFEST)

    sib = os.path.join(tmp, "sib")                                    # OUT OF PLACE
    legit = os.path.join(root, ".claude", "worktrees", "wt")          # legitimate
    _linked(sib, "sib")
    _linked(legit, "wt")

    def _fire(session_root, abs_target):
        payload = {"agent_type": "harness-documentor", "tool_name": "Write",
                   "tool_input": {"file_path": abs_target, "content": "x"}}
        return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                              text=True,
                              env=_env(session_root))

    # --- TARGET-SIDE: a write INTO the sibling, from a session rooted in the checkout.
    # The sibling is outside root, so select_base returns None and no grant can reach
    # it — this case discriminates whatever the manifest says.
    r = _fire(root, os.path.join(sib, "allowed", "x.txt"))
    wt("a write INTO an out-of-place worktree is REFUSED, and the verdict names where "
       "worktrees belong",
       r.returncode == 2 and ".claude/worktrees" in r.stderr,
       f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # The PAIRED ALLOW, same fixture and same session. Without it the case above is
    # satisfied by a guard that refuses everything.
    r = _fire(root, os.path.join(root, ".harness", "allowed", "x.txt"))
    wt("the same session's in-domain write still PASSES",
       r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- ROOT-SIDE: the session is STANDING IN the out-of-place tree. The target is
    # deliberately control-plane and in-domain FOR THAT ROOT, so it exits 0 if the
    # root-side rule is absent and 2 only because of it. A target of sib/allowed/x.txt
    # would exit 2 from the ordinary glob rule with the root-side rule deleted, and
    # would prove nothing.
    r = _fire(sib, os.path.join(sib, ".harness", "allowed", "x.txt"))
    wt("a session ROOTED in an out-of-place worktree is REFUSED its own in-domain write",
       r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # BOTH HALVES OF THE WORDING, on the SAME captured stderr. Presence alone passes
    # unchanged if the destructive sentence is re-added beside the location line, which
    # is the regression being guarded; absence alone passes for a verdict that says
    # nothing at all. Measured by visual-designer: `git worktree remove` SUCCEEDS from
    # inside the tree it removes, so that guidance printed to a session whose cwd IS
    # that tree is an instruction to delete the ground it is standing on.
    #
    # Scoped to THIS case's stderr. The target-side verdict keeps the removal guidance,
    # so a file-wide or tree-wide grep for the string would fail against correct code.
    wt("the ROOT-SIDE verdict names .claude/worktrees and does NOT say `git worktree remove`",
       ".claude/worktrees" in r.stderr and "git worktree remove" not in r.stderr,
       f"stderr: {r.stderr.strip()[:300]}")

    # The PAIRED ALLOW for the root-side rule: same shape, legitimate location.
    r = _fire(legit, os.path.join(legit, ".harness", "allowed", "x.txt"))
    wt("a session rooted in a LEGITIMATE worktree is unaffected",
       r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # SC-07, AND IT WAS OWED — the goal-check found every fixture using `legit` as the
    # SESSION ROOT, where no stripping happens, so DEC-143's worktree-prefix rule was
    # exercised by nothing. This reaches the same file FROM OUTSIDE the worktree.
    #
    # It discriminates: relative to `root` the path is
    # .claude/worktrees/wt/.harness/allowed/x.txt, which NO glob in the fixture matches.
    # It is granted only because the prefix is stripped to .harness/allowed/x.txt first.
    # Delete the stripping and this case exits 2.
    r = _fire(root, os.path.join(legit, ".harness", "allowed", "x.txt"))
    wt("SC-07: the legitimate worktree is writable FROM OUTSIDE it, through DEC-143's "
       "prefix stripping",
       r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # Ordinary scratch, outside any worktree — the change must not have widened.
    scratch = tempfile.mkdtemp()
    r = _fire(root, os.path.join(scratch, "x.txt"))
    wt("a scratch path outside any worktree still PASSES",
       r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- F-A, THE PANEL'S `high`: A POINTER THAT DOES NOT PARSE MUST REFUSE, NOT ALLOW.
    # Reproduced end to end before the fix: appending ONE 0xff byte to an otherwise valid
    # pointer turned this identical write from exit 2 into a silent exit 0, because every
    # parse failure returned None and every caller read None as not-a-worktree. That is
    # issue #103's own failure direction inside issue #103's fix.
    _ptr = os.path.join(sib, ".git")
    _good = open(_ptr, "rb").read()
    for _label, _payload in (
            ("not valid UTF-8", _good.rstrip() + b"\xff"),
            ("a bare word, no gitdir:", b"nonsense\n"),
            ("a gitdir: that is not a worktrees entry", b"gitdir: /tmp/elsewhere/.git\n"),
            ("an empty file", b""),
    ):
        with open(_ptr, "wb") as _f:
            _f.write(_payload)
        r = _fire(root, os.path.join(sib, "allowed", "x.txt"))
        wt(f"F-A: a .git pointer that is {_label} REFUSES the write (it must not read as "
           "not-a-worktree)",
           r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")
    # THE PAIRED ALLOW, restoring the valid pointer — without it every case above is
    # satisfied by a guard that refuses everything in this fixture.
    with open(_ptr, "wb") as _f:
        _f.write(_good)
    r = _fire(root, os.path.join(root, ".harness", "allowed", "x.txt"))
    wt("F-A: with the pointer restored, the in-domain write still PASSES",
       r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- THE FAIL-CLOSED PAIR for the shared module (D-06). An isolated copy carrying
    # check-domain.sh and harness_yaml.py but NOT harness_boundary.py.
    iso = tempfile.mkdtemp()
    isobin = os.path.join(iso, ".claude", "skills", "harness", "bin")
    os.makedirs(isobin)
    shutil.copy(HOOK, os.path.join(isobin, "check-domain.sh"))
    shutil.copy(os.path.join(HERE, "harness_yaml.py"), os.path.join(isobin, "harness_yaml.py"))
    os.makedirs(os.path.join(iso, ".harness"))
    with open(os.path.join(iso, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    payload = {"agent_type": "harness-documentor", "tool_name": "Write",
               "tool_input": {"file_path": os.path.join(iso, ".harness", "allowed", "x.txt"),
                              "content": "x"}}
    r = subprocess.run([os.path.join(isobin, "check-domain.sh")], input=json.dumps(payload),
                       capture_output=True, text=True,
                       env=_env(iso))
    wt("a MISSING harness_boundary.py blocks the write and NAMES the module",
       r.returncode == 2 and "harness_boundary" in r.stderr,
       f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # The other half: without it the case above is satisfied by a guard that blocks
    # everything. The manifest is removed, so DEC-101's deliberate fail-open must still
    # fire — the module being absent must not convert it into a refusal.
    os.remove(os.path.join(iso, ".harness", "team-config.yaml"))
    r = subprocess.run([os.path.join(isobin, "check-domain.sh")], input=json.dumps(payload),
                       capture_output=True, text=True,
                       env=_env(iso))
    wt("with the module absent AND no manifest, DEC-101 still fails OPEN, loudly",
       r.returncode == 0 and "enforcement OFF" in r.stderr,
       f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- #556: THE CWD MUST NOT SUPPLY THE BOUNDARY RULE. Python puts the invoking
    # directory at sys.path[0] AHEAD of PYTHONPATH, so before the safe-path bootstrap a
    # harness_boundary.py sitting in the agent's cwd WAS the resolver this gate consulted.
    # Measured on 2026-08-27 at sha 7179095: a module returning a bogus root turned a
    # refusal (exit 2) into "enforcement OFF" (exit 0) — the domain gate switched off
    # entirely by a file the governed agent controls. Both halves are asserted: the clean
    # cwd must refuse, and the hostile cwd must return the SAME verdict.
    _hostile = tempfile.mkdtemp()
    with open(os.path.join(_hostile, "harness_boundary.py"), "w") as _hf:
        _hf.write("MARKER = 'nope'\n"
                  "def resolve_root(bin_dir, strict=True): return '/definitely/not/here'\n"
                  "def root_from_script(bin_dir): return '/definitely/not/here'\n"
                  "def root_above(start): return None\n")
    _p556 = {"agent_type": "harness-backend-dev", "tool_name": "Write",
             "tool_input": {"file_path": os.path.join(ROOT, ".harness", "harness",
                                                      "docs", "SPEC.md"),
                            "content": "x"}}
    _clean = subprocess.run([HOOK], input=json.dumps(_p556), capture_output=True,
                            text=True, env=_env(ROOT), cwd=tempfile.gettempdir())
    wt("#556 control: from a clean cwd the out-of-domain write is REFUSED",
       _clean.returncode == 2, f"exit {_clean.returncode}: {_clean.stderr.strip()[:200]}")
    _hijack = subprocess.run([HOOK], input=json.dumps(_p556), capture_output=True,
                             text=True, env=_env(ROOT), cwd=_hostile)
    wt("#556: a harness_boundary.py in the CWD does not become the gate's resolver",
       _hijack.returncode == 2 and _hijack.returncode == _clean.returncode
       and "enforcement OFF" not in _hijack.stderr,
       f"clean={_clean.returncode} hijacked={_hijack.returncode}: "
       f"{_hijack.stderr.strip()[:200]}")

    fails = 0
    for name, ok, detail in WT:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(WT) - fails}/{len(WT)} worktree-boundary cases passed.\n")
    return fails


WTG = []


def wtg(name, ok, detail=""):
    WTG.append((name, ok, detail))


def run_worktree_grant_parity():
    """T-03 (FEAT-30, SC-05) — the grant an agent has inside a worktree is the grant it
    has at the checkout root, for ALL SIXTEEN agents, one assertion each.

    THIS PINS TODAY'S LAYOUT ON PURPOSE: exactly one segment after WORKTREES_SEGMENT.
    T-04 replaces the fixed-segment strip with a mechanism that reads the git pointer,
    and these sixteen cases are the baseline it must leave green. Do NOT extend this to
    the repo-and-id layout here — T-04 owns that.

    THE ROSTER IS WALKED, NOT LISTED. Every node carrying both a `name` and a
    list-valued `domain`, at every nesting level: members inside each team's `members`,
    leads under `leads`, and harness-orchestrator as a bare top-level key. The length is
    asserted to be exactly 16 and reports the names it found when it is not — a roster
    that silently shrinks would make every following assertion vacuous rather than red.

    TWO DEVIATIONS FROM THE SIGNED INTENT, both forced by measurement, both disclosed
    rather than smoothed over:

    1. The intent says instantiate by "replacing each single-star segment" with a token.
       Replacing the whole SEGMENT destroys literal prefixes — the reviewers' grant
       `notes/review-harness-code-reviewer-*.md` becomes `notes/zz`, which their own
       glob cannot match. Measured: 7 of 16 agents resolved to harness-orchestrator
       instead of themselves. The star is replaced WITHIN its segment, keeping literals.

    2. The intent says take "the first entry of its own domain list". In the harness base
       a glob match is accepted only when the TARGET passes is_control_plane_target, so
       an agent whose first entry is product code — `src/**`, `docs/**`, `web/src/**`,
       `supabase/migrations/**` — resolves to NOBODY at BOTH paths. `tests/**` is now a
       target-side control-plane entry, so harness-qa's first domain entry is selected
       rather than falling through. For agents without such an entry, the first entry
       that is a control-plane target is used instead, and an agent with none at all is
       a reported FAILURE, never a skip.

    The membership assertion is not decoration. Equality alone is satisfied by two empty
    sets, so each case also asserts the agent is IN both sets. T-03's verify mutates
    WORKTREES_SEGMENT by name in a copied module and requires this file to FAIL, which is
    only reachable if the in-worktree half of every pair really traverses the worktree
    path.
    """
    import harness_yaml as _hy
    import harness_boundary as _hb

    fails = 0
    tmp = tempfile.mkdtemp()

    manifest_src = os.path.join(ROOT, ".harness", "team-config.yaml")
    with open(manifest_src, encoding="utf-8") as f:
        manifest_text = f.read()

    # THE REAL MANIFEST, not FIXTURE_MANIFEST. The roster and the grants under test are
    # the shipped ones; a fixture manifest would assert parity for personas that do not
    # exist and would never notice a real grant losing its worktree parity.
    root = fixture(manifest_text)

    # A REAL LINKED WORKTREE, both sides of the pointer pair, per D-09. A bare directory
    # made with os.makedirs resolves identically under today's fixed-segment strip, so
    # these cases would pass now and go red the moment T-04 lands — sixteen false
    # failures attributed to T-04 instead of to the fixture.
    wt_id = "wt1"
    owner_entry = os.path.join(root, ".git", "worktrees", wt_id)
    os.makedirs(owner_entry)
    os.makedirs(os.path.join(root, ".git", "refs"), exist_ok=True)
    wt_path = os.path.join(root, ".claude", "worktrees", wt_id)
    os.makedirs(wt_path)
    # the worktree side
    with open(os.path.join(wt_path, ".git"), "w") as f:
        f.write("gitdir: %s\n" % owner_entry)
    # the owner side, naming the worktree's own .git file
    with open(os.path.join(owner_entry, "gitdir"), "w") as f:
        f.write("%s\n" % os.path.join(wt_path, ".git"))
    # NO .harness/team-config.yaml inside wt1, deliberately: these cases root the session
    # at the fixture root, and a nearer manifest would move the base out from under the
    # assertion.

    # THE OWNER MUST BE A REAL CHECKOUT for worktree_owner to name it: it walks up to the
    # first `.git` entry, and a DIRECTORY is what makes a root the owner.
    parsed = _hb.worktree_owner(wt_path)
    wtg("the fixture worktree is a REAL linked worktree, parsed and legitimate",
        parsed is not None and parsed[1] is not None and parsed[2] is True,
        f"worktree_owner({wt_path}) = {parsed!r} — a bare directory or an unparsed "
        f"pointer here makes all sixteen cases below prove nothing")

    def instantiate(pat):
        """A glob to a concrete relative path, replacing the star INSIDE its segment."""
        out = []
        for seg in pat.strip("/").split("/"):
            out.append("zz/zz" if seg == "**" else seg.replace("*", "zz"))
        return "/".join(out)

    roster = []

    def walk(node):
        if isinstance(node, dict):
            nm, dom = node.get("name"), node.get("domain")
            if isinstance(nm, str) and isinstance(dom, list):
                roster.append((nm, dom))
            for k, v in node.items():
                if k not in ("name", "domain"):
                    walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(_hy.yaml.safe_load(manifest_text))
    names = sorted(n for n, _ in roster)
    wtg("the roster walk finds exactly 16 agents carrying a name and a list domain",
        len(roster) == 16,
        f"found {len(roster)}: {names!r} — every case below is vacuous if this is wrong")

    def resolve(path):
        r = subprocess.run([HOOK, "--resolve", path], capture_output=True, text=True,
                           stdin=subprocess.DEVNULL, timeout=20,
                           env=_env(root))
        return set(r.stdout.split())

    unit_path = os.path.join(root, "tests", "unit", "test-zz.py")
    integration_path = os.path.join(root, "tests", "integration", "test-zz.py")
    unit_grants = resolve(unit_path)
    integration_grants = resolve(integration_path)
    expected_test_writers = {
        "harness-qa", "harness-backend-dev", "harness-dev-ops"}
    for agent in sorted(expected_test_writers):
        wtg(f"tests/unit grants {agent}", agent in unit_grants,
            f"resolved {sorted(unit_grants)!r}")
        wtg(f"tests/integration grants {agent}", agent in integration_grants,
            f"resolved {sorted(integration_grants)!r}")
    for agent in ("harness-frontend-dev", "harness-ai-dev", "harness-data-engineer"):
        wtg(f"tests/unit denies {agent}", agent not in unit_grants,
            f"resolved {sorted(unit_grants)!r}")
    bin_grants = resolve(os.path.join(
        root, ".claude", "skills", "harness", "bin", "zz.sh"))
    wtg("harness-qa cannot write governed bin shell",
        "harness-qa" not in bin_grants, f"resolved {sorted(bin_grants)!r}")
    wt_unit_grants = resolve(os.path.join(wt_path, "tests", "unit", "test-zz.py"))
    wtg("tests/unit grants are identical in a linked worktree",
        wt_unit_grants == unit_grants,
        f"root={sorted(unit_grants)!r}, worktree={sorted(wt_unit_grants)!r}")

    for agent, domain in sorted(roster):
        chosen = None
        for entry in domain:
            pat = entry.get("path") if isinstance(entry, dict) else entry
            if not isinstance(pat, str):
                continue
            rel = instantiate(pat)
            if _hb.is_control_plane_target(rel):
                chosen = (pat, rel)
                break
        if chosen is None:
            wtg(f"{agent}: in-worktree grant equals root grant",
                False,
                "no domain entry instantiates to a control-plane target, so no path in "
                "this agent's domain can be granted in the harness base. Reported as a "
                "failure rather than skipped: a skip here is a silent hole.")
            continue
        pat, rel = chosen
        at_root = resolve(os.path.join(root, rel))
        in_wt = resolve(os.path.join(wt_path, rel))
        wtg(f"{agent}: in-worktree grant equals root grant, and names {agent}",
            at_root == in_wt and agent in at_root,
            f"glob {pat!r} -> {rel!r}; at root {sorted(at_root)!r}, in worktree "
            f"{sorted(in_wt)!r}; equal={at_root == in_wt}, "
            f"contains-self={agent in at_root}")

    # ================= T-04: THE DEEP LAYOUT =================
    # Everything above pins the ONE-level shape and must stay green (SC-09). Everything
    # below is what NO path could reach before T-04: the fixed-segment strip left the
    # repository segment in the path, so the second candidate matched no glob.

    deep = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "harness", "FEAT-90"), "FEAT-90")

    # SC-02c — one case per agent at <segment>/<repo>/<id>/, all sixteen.
    for agent, domain in sorted(roster):
        chosen = None
        for entry in domain:
            pat = entry.get("path") if isinstance(entry, dict) else entry
            if not isinstance(pat, str):
                continue
            rel = instantiate(pat)
            if _hb.is_control_plane_target(rel):
                chosen = (pat, rel)
                break
        if chosen is None:
            wtg(f"SC-02c {agent}: DEEP-layout grant equals root grant", False,
                "no domain entry instantiates to a control-plane target")
            continue
        pat, rel = chosen
        at_root = resolve(os.path.join(root, rel))
        in_deep = resolve(os.path.join(deep, rel))
        wtg(f"SC-02c {agent}: DEEP-layout grant equals root grant, and names {agent}",
            at_root == in_deep and agent in at_root,
            f"glob {pat!r} -> {rel!r}; root {sorted(at_root)!r}, deep "
            f"{sorted(in_deep)!r}; equal={at_root == in_deep}, self={agent in at_root}")

    # THE DEPTH IS NOT LOAD-BEARING. A rule that asks which checkout it stands in does
    # not care how deep the path is; a rule with a segment count does. Four levels.
    very_deep = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "a", "b", "c", "FEAT-90"), "abcFEAT90")
    _probe = ".harness/zz/features/zz/BRIEF.md"
    wtg("the depth is not load-bearing: <segment>/a/b/c/<id> resolves like the root",
        resolve(os.path.join(very_deep, _probe)) == resolve(os.path.join(root, _probe))
        and "harness-pm" in resolve(os.path.join(very_deep, _probe)),
        f"deep-4 {sorted(resolve(os.path.join(very_deep, _probe)))!r} vs root "
        f"{sorted(resolve(os.path.join(root, _probe)))!r}")

    # THE OLD MECHANISM IS GONE, not left standing beside its replacement. A dead regex
    # kept "for reference" is what leaves a segment count load-bearing for the next reader.
    wtg("WORKTREE_REL_RE no longer exists on harness_boundary",
        not hasattr(_hb, "WORKTREE_REL_RE"),
        "the fixed-segment strip is still importable, so a caller can still use it")

    # linked_worktrees: exactly the registered checkouts, and empty when there are none.
    lw_root = fixture(manifest_text)
    os.makedirs(os.path.join(lw_root, ".git"))
    wtg("linked_worktrees returns [] for a checkout with no worktrees",
        _hb.linked_worktrees(lw_root) == [],
        f"got {_hb.linked_worktrees(lw_root)!r}")
    a = make_linked_worktree(
        lw_root, os.path.join(lw_root, ".claude", "worktrees", "harness", "FEAT-90"), "FEAT-90")
    b = make_linked_worktree(
        lw_root, os.path.join(lw_root, ".claude", "worktrees", "harness", "FEAT-91"), "FEAT-91")
    wtg("linked_worktrees returns exactly the two registered checkouts, as realpaths",
        _hb.linked_worktrees(lw_root) == sorted([_hb.real(a), _hb.real(b)]),
        f"got {_hb.linked_worktrees(lw_root)!r}, want {sorted([_hb.real(a), _hb.real(b)])!r}")

    for name, ok, detail in WTG:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(WTG) - fails}/{len(WTG)} worktree grant-parity cases passed.\n")
    shutil.rmtree(tmp, ignore_errors=True)
    return fails


WDS = []


def wds(name, ok, detail=""):
    WDS.append((name, ok, detail))


def run_worktree_deep_shape():
    """T-04 PART 3 — DEC-150's shape caps under a two-level worktree layout.

    THIS IS THE HALF THAT WAS SILENTLY DARK, and the measurement is why PART 3 was not
    optional. At `eeabc59`, harness-orchestrator writing a 204-line STATE.md against a
    120-line budget at the same repo-relative path in three places: the main checkout
    refused with the SHAPE reason naming DEC-150; one-level `.claude/worktrees/WT1` also
    refused with that shape reason; two-level `.claude/worktrees/harness/WT1` refused with
    the DOMAIN reason instead, and NEVER REACHED the shape gate at all. Fixing only
    classify and the resolve path would have lifted the domain refusal that was masking
    it — writes succeed, budgets unenforced, suite green.

    EVERY ASSERTION HERE IS ON THE WORDING, never on the exit code. The domain refusal and
    the shape refusal BOTH exit 2, so an exit-code assertion passes against the masked
    state and keeps passing after the domain half is fixed while the caps stay off. That
    is the whole trap.
    """
    import harness_boundary as _hbd

    def _hb_where(owner_root):
        """The one spelling of where worktrees belong, from the module, never re-typed."""
        return _hbd.worktree_refusal_location(_hbd.real(owner_root))

    fails = 0
    manifest_src = os.path.join(ROOT, ".harness", "team-config.yaml")
    with open(manifest_src, encoding="utf-8") as f:
        manifest_text = f.read()

    over = "\n".join(f"x{i}" for i in range(204)) + "\n"
    state_rel = os.path.join(".harness", "harness", "features", "FEAT-W", "STATE.md")

    def shape_refusal(root, abs_target):
        os.makedirs(os.path.dirname(abs_target), exist_ok=True)
        payload = {"agent_type": "harness-orchestrator", "tool_name": "Write",
                   "tool_input": {"file_path": abs_target, "content": over}}
        return fire_post(root, payload, flag=None)

    # --- THE PAIR THAT DISCRIMINATES: one-level must KEEP refusing on shape (it did at
    # eeabc59), two-level must START refusing on shape (it did not).
    d = fixture(manifest_text)
    os.makedirs(os.path.join(d, ".git"))
    one = make_linked_worktree(d, os.path.join(d, ".claude", "worktrees", "wt1"), "wt1")
    two = make_linked_worktree(
        d, os.path.join(d, ".claude", "worktrees", "harness", "FEAT-90"), "FEAT-90")

    r_root = shape_refusal(d, os.path.join(d, state_rel))
    wds("baseline: the main checkout refuses an over-budget STATE.md with the SHAPE "
        "reason naming DEC-150",
        r_root.returncode == 2 and "DEC-150" in r_root.stderr,
        f"exit {r_root.returncode}: {r_root.stderr.strip()[:200]}")

    r_one = shape_refusal(d, os.path.join(one, state_rel))
    wds("SC-09: at ONE level the shape refusal still names DEC-150 (it did at eeabc59 "
        "and must not regress)",
        r_one.returncode == 2 and "DEC-150" in r_one.stderr,
        f"exit {r_one.returncode}: {r_one.stderr.strip()[:200]}")

    r_two = shape_refusal(d, os.path.join(two, state_rel))
    wds("at TWO levels the write route refuses on SHAPE, naming DEC-150 — asserted on "
        "the WORDING, because the domain refusal also exits 2",
        r_two.returncode == 2 and "DEC-150" in r_two.stderr,
        f"exit {r_two.returncode}: {r_two.stderr.strip()[:200]} — a refusal without "
        f"DEC-150 is the DOMAIN refusal masking a dark shape gate")

    # --- THE POST-WRITE SWEEP AT DEPTH, paired against a BARE directory. D-09 accepts
    # that a directory under the segment with no pointer pair stops being swept; that cost
    # must be asserted, not left silent. A single-direction assertion here also passes
    # against a sweep that reaches nothing at all, which is why both halves are here.
    d2 = fixture(manifest_text)
    os.makedirs(os.path.join(d2, ".git"))
    swept = make_linked_worktree(
        d2, os.path.join(d2, ".claude", "worktrees", "harness", "FEAT-90"), "FEAT-90")
    bare = os.path.join(d2, ".claude", "worktrees", "harness", "FEAT-BARE")
    os.makedirs(os.path.join(bare, ".harness", "harness", "features", "FEAT-W"))

    bash_payload = {"agent_type": "harness-orchestrator", "tool_name": "Bash",
                    "tool_input": {"command": "echo hi"}}
    fire_post(d2, bash_payload)                      # advance the stamp past everything
    r0 = fire_post(d2, bash_payload)                 # nothing fresh -> silence
    reg = os.path.join(swept, ".harness", "harness", "features", "FEAT-W", "feature.json")
    os.makedirs(os.path.dirname(reg), exist_ok=True)
    with open(reg, "w") as f:
        f.write(_legal_feature_json(400))
    r1 = fire_post(d2, bash_payload)
    wds("the sweep reaches a file inside a TWO-LEVEL registered worktree (invisible at "
        "eeabc59, and invisible SILENTLY)",
        r0.returncode == 0 and r1.returncode == 2 and "budget is 300" in r1.stderr,
        f"baseline exit {r0.returncode}, after exit {r1.returncode}: "
        f"{r1.stderr.strip()[:200]}")
    wds("...and the finding names the WORKTREE it came from, not the stripped path",
        "FEAT-90" in r1.stderr,
        f"stderr does not name the checkout: {r1.stderr.strip()[:200]}")

    fire_post(d2, bash_payload)                      # re-advance the stamp
    r2 = fire_post(d2, bash_payload)
    bare_f = os.path.join(bare, ".harness", "harness", "features", "FEAT-W", "feature.json")
    with open(bare_f, "w") as f:
        f.write(_legal_feature_json(400))
    r3 = fire_post(d2, bash_payload)
    wds("D-09's ACCEPTED COST, asserted: a directory under the segment with NO pointer "
        "pair is not swept",
        r2.returncode == 0 and r3.returncode == 0,
        f"expected silence both times, got {r2.returncode} then {r3.returncode}: "
        f"{r3.stderr.strip()[:200]}")

    # --- SC-02b, BOTH DIRECTIONS FROM ONE FIXTURE. The accept half alone is what an
    # allow-all escape produces; the refuse half alone is what a fail-closed guard
    # produces. Only the pair distinguishes them.
    d3 = fixture(manifest_text)
    os.makedirs(os.path.join(d3, ".git"))
    inside = make_linked_worktree(
        d3, os.path.join(d3, ".claude", "worktrees", "harness", "FEAT-90"), "FEAT-90")
    granted = os.path.join(inside, ".harness", "harness", "features", "FEAT-W", "BRIEF.md")
    os.makedirs(os.path.dirname(granted), exist_ok=True)
    r_ok = fire_post(d3, {"agent_type": "harness-pm", "tool_name": "Write",
                          "tool_input": {"file_path": granted, "content": "x"}}, flag=None)
    wds("SC-02b accept: a governed write inside <segment>/<repo>/<id> exits 0",
        r_ok.returncode == 0,
        f"exit {r_ok.returncode}: {r_ok.stderr.strip()[:200]}")

    # The sibling is a REAL linked worktree of the same root, in the wrong place.
    sib = os.path.join(os.path.dirname(d3), os.path.basename(d3) + "-sib")
    make_linked_worktree(d3, sib, "sib")
    sib_target = os.path.join(sib, ".harness", "harness", "features", "FEAT-W", "BRIEF.md")
    os.makedirs(os.path.dirname(sib_target), exist_ok=True)
    r_sib = fire_post(d3, {"agent_type": "harness-pm", "tool_name": "Write",
                           "tool_input": {"file_path": sib_target, "content": "x"}}, flag=None)
    _expected = _hb_where(d3)
    wds("SC-02b refuse: a linked worktree OUTSIDE the layout is refused, and the message "
        "NAMES where worktrees belong",
        r_sib.returncode == 2 and _expected in r_sib.stderr,
        f"exit {r_sib.returncode}, want the text {_expected!r} in: "
        f"{r_sib.stderr.strip()[:240]}")

    for name, ok, detail in WDS:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(WDS) - fails}/{len(WDS)} deep-layout shape cases passed.\n")
    return fails



def run_sweep_clean_tracked():
    """The post-sweep must not report a file `git worktree add` merely materialised.

    THE DEFECT, measured 2026-08-21. `feature-worktree.py create` runs `git worktree add`,
    which writes a fresh copy of every tracked file, so all 126 files matching SWEEP_GLOBS
    in the new checkout carried an mtime of that second. The sweep asked only
    `st_mtime > _since`, so it shape-checked all 126 — including 25 features whose status
    is Done — and reported the two long-standing malformed STATE.md files as
    `OVER BUDGET (already written)` against the agent that cut the tree. False in the one
    field an agent acts on: authorship. Both files sit outside any ordinary agent's domain,
    so an agent obeying that message is DENIED by this same hook.

    A REAL GIT REPOSITORY IS REQUIRED HERE, unlike `make_linked_worktree`'s pointer-pair
    fixture. The skip asks git whether a candidate differs from HEAD; against a fake
    pointer pair that call fails, `_dirty_set` is None, and the sweep falls back to its old
    behaviour. That fallback is deliberate (it fails OPEN), and it is why every pre-existing
    worktree case in this file stays green — but it also means only a real repo can
    exercise the skip at all.
    """
    fails = 0
    d = tempfile.mkdtemp()
    try:
        root = os.path.join(d, "owner")
        os.makedirs(root)

        def git(cwd, args):
            r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr))
            return r

        git(root, ["init", "-q"])
        git(root, ["symbolic-ref", "HEAD", "refs/heads/main"])
        git(root, ["config", "user.email", "t@example.com"])
        git(root, ["config", "user.name", "T"])
        os.makedirs(os.path.join(root, ".harness"))
        with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
            f.write(FIXTURE_MANIFEST)

        # A MALFORMED STATE.md, COMMITTED. This stands in for FEAT-02's real file: an old,
        # shipped feature carrying an illegal section that nothing in this run wrote.
        fdir = os.path.join(root, ".harness", "harness", "features", "FEAT-OLD")
        os.makedirs(os.path.join(fdir, "notes"))
        rel_state = ".harness/harness/features/FEAT-OLD/STATE.md"
        with open(os.path.join(root, rel_state), "w") as f:
            f.write("# FEAT-OLD — STATE\n\n## Current\nshipped\n\n"
                    "## Illegal Section\nhistory that DEC-150 forbids\n")
        git(root, ["add", "-A"])
        git(root, ["commit", "-q", "-m", "the malformed file, committed"])

        wt = os.path.join(root, ".claude", "worktrees", "harness", "FEAT-NEW")
        git(root, ["worktree", "add", "-q", "-b", "feat/FEAT-NEW", wt])

        # Every file in `wt` now carries a fresh mtime. Assert that, rather than trusting
        # it: if git ever stopped rewriting mtimes, this whole case would pass vacuously
        # and prove nothing about the skip.
        wt_state = os.path.join(wt, rel_state)
        stamp_floor = time.time() - 5
        if not os.path.isfile(wt_state):
            print("FAIL  sweep/clean-tracked: git worktree add did not materialise %s"
                  % rel_state)
            return fails + 1
        if os.stat(wt_state).st_mtime <= stamp_floor:
            print("FAIL  sweep/clean-tracked: PRECONDITION DEAD — the worktree copy's "
                  "mtime is not fresh, so the sweep would skip it on mtime alone and "
                  "this case could not distinguish the fix from its absence.")
            return fails + 1

        bash_payload = {"agent_type": "harness-orchestrator", "tool_name": "Bash",
                        "hook_event_name": "PostToolUse",
                        "tool_input": {"command": "true"}}

        def sweep(hook_path=None):
            argv = [hook_path or HOOK, "--post"]
            return subprocess.run(argv, input=json.dumps(bash_payload),
                                  capture_output=True, text=True,
                                  env=_env(root))

        def inv_lines(r):
            return [l for l in (r.stdout + r.stderr).splitlines()
                    if "FEAT-OLD" in l and "STATE.md" in l]

        def clear_stamp():
            # The sweep advances a high-water mark on every run, so a second sweep in the
            # same second sees nothing. Each case below removes the stamp first, or the
            # ordering of the cases would decide their results.
            try:
                os.remove(os.path.join(root, ".harness", ".shape-sweep-stamp"))
            except OSError:
                pass

        # CASE A — the committed file, materialised by `git worktree add`, is NOT reported.
        clear_stamp()
        r = sweep()
        got = inv_lines(r)
        if got:
            fails += 1
            print("FAIL  sweep/clean-tracked A: a clean-tracked file the checkout merely "
                  "materialised was reported as `already written`")
            for l in got[:2]:
                print("      | %s" % l.strip())
        else:
            print("ok    sweep/clean-tracked A: worktree creation reports nothing")

        # CASE B — a REAL Bash-route write in the worktree IS still reported. Without this
        # the fix is indistinguishable from deleting the sweep.
        with open(wt_state, "a") as f:
            f.write("\n## Second Illegal Section\nwritten by this run\n")
        clear_stamp()
        r = sweep()
        got = inv_lines(r)
        if not got:
            fails += 1
            print("FAIL  sweep/clean-tracked B: a modified STATE.md in the worktree was "
                  "NOT reported — the skip is swallowing real writes")
        elif r.returncode != 2:
            fails += 1
            print("FAIL  sweep/clean-tracked B: reported the file but exited %d, not 2"
                  % r.returncode)
        else:
            print("ok    sweep/clean-tracked B: a modified file is still caught, exit 2")

        # CASE C — an UNTRACKED state file in the worktree IS reported. `diff HEAD` alone
        # would miss this; the skip needs `ls-files --others` too, and a fix that dropped
        # it would leave every newly created run/state file unswept.
        newdir = os.path.join(wt, ".harness", "harness", "features", "FEAT-BRANDNEW")
        os.makedirs(newdir)
        with open(os.path.join(newdir, "STATE.md"), "w") as f:
            f.write("# x\n\n## Current\nok\n\n## Nope\nillegal\n")
        clear_stamp()
        r = sweep()
        if not [l for l in (r.stdout + r.stderr).splitlines() if "FEAT-BRANDNEW" in l]:
            fails += 1
            print("FAIL  sweep/clean-tracked C: an UNTRACKED malformed STATE.md in the "
                  "worktree was not reported — the skip is treating untracked as clean")
        else:
            print("ok    sweep/clean-tracked C: an untracked file is still caught")

        # RED PROOF — a mutant copy with SWEEP_SKIP_CLEAN_TRACKED flipped to False must
        # report case A's file. An exit status is never the proof: a crash on the way in is
        # also non-zero, so this compares the COUNT of FEAT-OLD lines.
        with open(HOOK) as f:
            original = f.read()
        mutant_text = original.replace("SWEEP_SKIP_CLEAN_TRACKED = True",
                                       "SWEEP_SKIP_CLEAN_TRACKED = False", 1)
        if mutant_text == original:
            fails += 1
            print("FAIL  sweep/clean-tracked RED: INCONCLUSIVE — the mutation did not "
                  "apply, so no claim is made about the assertions above. Has "
                  "SWEEP_SKIP_CLEAN_TRACKED been renamed?")
        else:
            mutant = os.path.join(d, "check-domain-mutant.sh")
            with open(mutant, "w") as f:
                f.write(mutant_text)
            os.chmod(mutant, 0o755)
            # THE MUTANT NEEDS THE RESOLVER BESIDE IT (FEAT-42 T-10). The hook prepends its
            # OWN directory to PYTHONPATH, and this copy sits in a bare tmpdir, so without
            # this the import of harness_boundary fails, the root falls back to the wrapper's
            # BASH_SOURCE walk out of that tmpdir, no manifest is found, and the mutant
            # prints "enforcement OFF" and sweeps nothing — reporting 0 lines for a reason
            # that has nothing to do with the mutation. An inconclusive red proof reads
            # exactly like a surviving mutant, which is why this is not left to chance.
            shutil.copy(os.path.join(HERE, "harness_boundary.py"),
                        os.path.join(d, "harness_boundary.py"))
            shutil.copy(os.path.join(HERE, "run_identity.py"),
                        os.path.join(d, "run_identity.py"))
            # Restore case A's exact state: the committed file clean again, nothing else
            # of FEAT-OLD's on disk changed.
            git(wt, ["checkout", "--", rel_state])
            clear_stamp()
            base = len(inv_lines(sweep()))
            clear_stamp()
            mut = len(inv_lines(sweep(mutant)))
            print("      red proof: original reported %d FEAT-OLD line(s), mutant %d"
                  % (base, mut))
            if mut <= base:
                fails += 1
                print("FAIL  sweep/clean-tracked RED: the mutant reported no more than "
                      "the original, so case A does not discriminate the fix from its "
                      "absence.")
            else:
                print("ok    sweep/clean-tracked RED: removing the skip makes case A red")
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return fails


def run_runs_agent_write_path():
    """FEAT-31 T-15 case F — the half that makes "the WRITE PATH refuses" true rather
    than "the module refuses". SC-07's positional rule is enforced through the same
    import check-domain.sh already has, so this drives the real hook as a subprocess
    on its PRE Write route and asserts on the process, not on a function return.

    THE MUTANT RUNS FROM A COPY OF THE WHOLE BIN DIRECTORY, and that is forced rather
    than chosen. check-domain.sh puts its OWN directory first on PYTHONPATH (`:96`), so
    an external PYTHONPATH cannot shadow feature_schema.py — the trick run_t12 uses for
    a module that is not in bin/ does not work here. Overwriting the real
    bin/feature_schema.py and restoring it in a finally was the alternative, and it
    leaves the enforcement layer broken if the process dies between the two. Copying
    bin/ into a tmpdir touches nothing real: `_derived` is only a fallback for
    CLAUDE_PROJECT_DIR, which every call here sets explicitly.
    """
    fails = 0
    local = []

    def t(name, ok, detail=""):
        nonlocal fails
        local.append((name, ok, detail))
        if not ok:
            fails += 1

    # A feature name deliberately ABSENT from the frozen map, so its exempt count is 0
    # and its very first runs entry must carry `agent`. Asserted, not assumed.
    import feature_schema as _fs
    feat = "FEAT-Z-absent-from-the-frozen-map"
    t("SC-07 write path: the fixture feature is absent from the frozen exempt map",
      feat not in _fs.RUNS_AGENT_EXEMPT,
      "the fixture name is in the map, so this block would prove nothing")

    doc_bad = json.dumps({"feature_id": feat, "branch": "none", "pr": None, "review_sha": "none", "cycles_used": 0,
                          "max_total_cycles": 10,
                          "runs": [{"id": "r1", "squad": "eng", "verdict": "PASS"}]},
                         indent=2)
    doc_ok = json.dumps({"feature_id": feat, "branch": "none", "pr": None, "review_sha": "none", "cycles_used": 0,
                         "max_total_cycles": 10,
                         "runs": [{"id": "r1", "squad": "eng", "verdict": "PASS",
                                   "agent": "harness-backend-dev"}]},
                        indent=2)
    rel = f".harness/harness/features/{feat}/feature.json"

    def fire_json(hook, root, content):
        payload = {"agent_type": "harness-orchestrator", "tool_name": "Write",
                   "tool_input": {"file_path": os.path.join(root, rel),
                                  "content": content}}
        return subprocess.run([hook], input=json.dumps(payload), capture_output=True,
                              text=True, env=_env(root))

    # A MANIFEST THAT GRANTS THE PATH, and this is the whole difference between a real
    # case and a green-looking one. FIXTURE_MANIFEST grants harness-orchestrator
    # nothing, so under it the PRE hook exits 2 for a DOMAIN reason and every assertion
    # below would pass while measuring nothing — the trap this file already records at
    # run_post's "route 2" case. Granting feature.json explicitly leaves the schema rule
    # as the only thing that can deny.
    grant = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-orchestrator
        domain:
          - { path: .harness/*/features/*/feature.json, upsert: true }
          - { path: ".", read: true }
"""
    root = fixture(grant)
    os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)

    r_bad = fire_json(HOOK, root, doc_bad)
    t("SC-07 write path: a Write whose runs entry omits agent exits 2",
      r_bad.returncode == 2, f"exit {r_bad.returncode}: {r_bad.stderr.strip()[:200]}")
    t("SC-07 write path: the denial names the key 'agent'",
      "agent" in r_bad.stderr, r_bad.stderr.strip()[:200])
    t("SC-07 write path: the denial names the offending index",
      "runs[0]" in r_bad.stderr, r_bad.stderr.strip()[:200])

    # THE DISCRIMINATING HALF. Without it an allow-nothing guard passes every assertion
    # above: the same write CARRYING the field must be permitted.
    r_ok = fire_json(HOOK, root, doc_ok)
    t("SC-07 write path: the same Write CARRYING agent is permitted",
      r_ok.returncode == 0, f"exit {r_ok.returncode}: {r_ok.stderr.strip()[:200]}")

    # RED PROOF — an exit status is never the proof (D-08). Counts on both sides.
    bin_dir = os.path.dirname(os.path.realpath(HOOK))
    src = open(os.path.join(bin_dir, "feature_schema.py")).read()
    needle = "    problems.extend(_runs_agent_problems(doc, display))\n"
    if needle not in src:
        t("SC-07 write path RED: the rule's call site was found", False,
          "feature_schema.py does not contain the call site")
    else:
        mutant_text = src.replace(needle, "")
        if mutant_text == src:
            t("SC-07 write path RED: the mutation changed the source", False,
              "INCONCLUSIVE — replace() was a no-op")
        else:
            mtmp = tempfile.mkdtemp()
            try:
                mbin = os.path.join(mtmp, "bin")
                shutil.copytree(bin_dir, mbin)
                with open(os.path.join(mbin, "feature_schema.py"), "w") as f:
                    f.write(mutant_text)
                mhook = os.path.join(mbin, os.path.basename(HOOK))
                r_mut = fire_json(mhook, root, doc_bad)
                n_real = 1 if r_bad.returncode == 2 else 0
                n_mut = 1 if r_mut.returncode == 2 else 0
                print(f"      red proof: original denials {n_real}, mutant {n_mut} "
                      f"(exit {r_bad.returncode} vs {r_mut.returncode})")
                t("SC-07 write path RED: the positional rule is load-bearing at the hook",
                  n_mut < n_real,
                  f"INCONCLUSIVE — original {n_real}, mutant {n_mut}")
            finally:
                shutil.rmtree(mtmp, ignore_errors=True)

    shutil.rmtree(root, ignore_errors=True)
    for name, ok, detail in local:
        if ok:
            print(f"ok    {name}")
        else:
            print(f"FAIL  {name}")
            if detail:
                print(f"      | {detail}")
    return fails

# ---------------------------------------------------------------------------
# T-14 — the approval exclusion, sourced from main_session.writes (D-10).
# Every case gets its OWN fixture root. Each asserts the exit code AND a
# distinguishing string, so a crash cannot satisfy it.
# ---------------------------------------------------------------------------

T14 = []


def t14(name, ok, detail=""):
    T14.append((name, ok, detail))


# harness-pm and harness-orchestrator must be GRANTED these paths, or every case below
# is an ordinary DOMAIN denial that never reaches the approval guard and the suite reports
# exit 2 for the wrong reason. FEAT-31 T-15 hit this exact trap with this exact fixture.
APPROVAL_MANIFEST = FIXTURE_MANIFEST.replace(
    "shared:\n",
    "  - name: plan\n"
    "    members:\n"
    "      - name: harness-pm\n"
    "        domain:\n"
    "          - { path: .harness/*/features/*/plan.yaml, upsert: true }\n"
    "          - { path: .harness/*/features/*/BRIEF.md, upsert: true }\n"
    "          - { path: .harness/*/features/*/PLAN.md, upsert: true }\n"
    "      - name: harness-orchestrator\n"
    "        domain:\n"
    "          - { path: .harness/*/features/**, upsert: true }\n"
    "          - { path: .harness/logs/**, upsert: true }\n"
    "main_session:\n"
    "  writes:\n"
    '    - ".harness/*/features/*/BRIEF.md ## Approval"\n'
    '    - ".harness/*/features/*/PLAN.md ## Approval"\n'
    '    - ".harness/*/features/*/plan.yaml approval:"\n'
    '    - ".harness/logs/**"\n'
    "shared:\n"
    "  - { path: .harness/*/features/*/quarantine/** }\n")

PLAN_ON_DISK = (
    "schema: plan/1\n"
    "feature: FEAT-99-fixture\n"
    "\n"
    "approval:\n"
    "  status: pending\n"
    "  approved_by: <name>\n"
    "  date: <YYYY-MM-DD>\n"
    "\n"
    "tasks:\n"
    "  - id: T-01\n"
    "    change_type: logic\n"
    "    status: pending\n"
    "  - id: T-02\n"
    "    change_type: logic\n"
    "    status: pending\n")

BRIEF_ON_DISK = (
    "# Brief\n"
    "\n"
    "## Goal\n"
    "\n"
    "Do the thing.\n"
    "\n"
    "## Approval\n"
    "\n"
    "status: pending\n"
    "approved-by: <name>\n")

REL_PLAN = ".harness/harness/features/FEAT-99-fixture/plan.yaml"
REL_BRIEF = ".harness/harness/features/FEAT-99-fixture/BRIEF.md"
REL_PLANMD = ".harness/harness/features/FEAT-99-fixture/PLAN.md"
MARK = "may not change"


def _approval_root(manifest_text=None, rel=REL_PLAN, body=PLAN_ON_DISK):
    root = fixture(APPROVAL_MANIFEST if manifest_text is None else manifest_text)
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(body)
    return root, full


def _fire_write(root, full, content, agent="harness-pm"):
    payload = {"agent_type": agent, "tool_name": "Write",
               "tool_input": {"file_path": full, "content": content}}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def _fire_edit(root, full, old_s, new_s, agent="harness-pm", replace_all=False):
    ti = {"file_path": full, "old_string": old_s, "new_string": new_s}
    if replace_all:
        ti["replace_all"] = True
    payload = {"agent_type": agent, "tool_name": "Edit", "tool_input": ti}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def t09(name, ok, detail=""):
    global _T09_FAILS
    if ok:
        print(f"ok    {name}")
    else:
        _T09_FAILS += 1
        print(f"FAIL  {name}\n      {detail}")
    return ok


_T09_FAILS = 0

# The station value a legal plan carries, and one that is not in the vocabulary at all. The
# LEGAL word is read from factory_config rather than typed, so this fixture cannot drift from
# the declaration the way a six-key mapping once did (FEAT-41 T-01).
import factory_config as _fc09

_PLAN_LEGAL = (
    "schema: plan/1\n"
    "feature: FEAT-99-fixture\n"
    f"status: {_fc09.MANDATED_STATIONS[3]}\n"
    "tasks:\n"
    "  - id: T-01\n"
    f"    status: {_fc09.MANDATED_STATIONS[5]}\n"
    "    verify: python3 test.py\n"
    # T-02 IS DELIBERATELY NOT TERMINAL. T-01 is `done`, and under FEAT-54's B-1 satisfaction
    # rule a handoff whose every authority is already satisfied binds nothing and is refused —
    # so a fixture handoff citing T-01 alone reds for a reason its own case never names. Any
    # case here that needs a LEGAL handoff body cites T-02.
    "  - id: T-02\n"
    f"    status: {_fc09.MANDATED_STATIONS[3]}\n"
    "    verify: python3 test.py\n"
)
_PLAN_ILLEGAL = _PLAN_LEGAL.replace(
    f"    status: {_fc09.MANDATED_STATIONS[5]}", "    status: Sideways")
# A plan with NO top-level status at all — the UN-MIGRATED shape the sweep meets while T-07 is
# pending. T-09 and T-07 are unordered, so this must be LEGAL or the sweep reports every plan
# that has not been migrated yet.
_PLAN_NO_TOP = "\n".join(l for l in _PLAN_LEGAL.splitlines()
                          if not l.startswith("status:")) + "\n"


# FEAT-41 T-09's cases, SPLIT BY CASE GROUP (FEAT-41 F-05). This began as one `run_t09` and grew
# a case group per finding until it graded 1 against a test bar of 3, driven by ABC alone — 61.1
# worth of fixture calls in one body, with cyclomatic at 7 and cognitive at 6. Nothing here was
# hard to read line by line; there was simply too much of it in one place. The groups are the
# ones the numbered comments already named, so the split follows a boundary the file had.
#
# THEY SHARE `t09()`, which counts into the module-level tally, so each group asserts freely and
# only the aggregator resets and reports.
def _t09_edit_denial():
    """1. THE EDIT ROUTE IS DENIED, and the message routes the reader to the verb."""

    # ---- 1. THE EDIT ROUTE IS DENIED, and the message routes the reader to the verb -------
    root, full = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    r = _fire_edit(root, full, "T-01", "T-02", agent="harness-orchestrator")
    t09("T-09 1: an AGENT's Edit of plan.yaml is DENIED", r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")
    err = r.stderr
    t09("T-09 1: the denial names set-task-station — the write an agent will actually attempt",
        "set-task-station" in err, f"stderr={err[:400]!r}")

    # THE REASON CLAUSE IS LOAD-BEARING, NOT DECORATION. A denial that says only what to use
    # instead is indistinguishable from a stuck or over-broad gate, and a reader who takes it
    # for a harness malfunction routes around it through a shell write of a legal value — the
    # one channel the sweep admits it cannot attribute to an author.
    t09("T-09 1: the denial STATES THE REASON — one writer, because stations are validated "
        "before they land",
        "one writer" in err.lower() and "validate" in err.lower(),
        f"stderr={err[:400]!r}")

    # THE BASENAME IS THE ONE ON DISK, read from the bin directory rather than retyped.
    t09("T-09 1: the denial names the writer script by the basename that EXISTS on disk",
        "plan-merge.py" in err and os.path.isfile(os.path.join(HERE, "plan-merge.py")),
        f"stderr={err[:400]!r}")

    # ONE ROUTING SENTENCE PER FINDING. deny() appends the module-level ROUTING constant,
    # which speaks about STATE.md, digests and notes/ — a different file class entirely.
    # Emitting it beside a plan.yaml refusal puts two contradictory routing sentences in one
    # stderr stream. Asserted by a distinctive substring of that constant.
    t09("T-09 1: the denial does NOT carry the STATE.md ROUTING sentence",
        "STATE.md" not in err, f"stderr={err[:400]!r}")


def _t09_binds_every_author():
    """2-4. Every author is bound, both write routes are denied, and a sibling is not."""

    # ---- 2. THE MAIN SESSION IS DENIED TOO ------------------------------------------------
    # DEC-180 makes the shape gate independent of domain and binding on EVERY author. The
    # domain region would have been the wrong home precisely because check-domain exits 0 for
    # a payload with no agent_type, which would exempt the one author most likely to hand-edit.
    root2, full2 = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    r2 = _fire_edit(root2, full2, "T-01", "T-02", agent=None)
    t09("T-09 2: an Edit with NO agent_type is denied too — the shape gate binds every author",
        r2.returncode == 2, f"exit {r2.returncode}, stderr={r2.stderr.strip()[:300]!r}")

    # ---- 3. THE WRITE ROUTE IS DENIED -----------------------------------------------------
    root3, full3 = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    r3 = _fire_write(root3, full3, _PLAN_LEGAL, agent="harness-orchestrator")
    t09("T-09 3: a Write of plan.yaml is DENIED", r3.returncode == 2,
        f"exit {r3.returncode}, stderr={r3.stderr.strip()[:300]!r}")

    # ---- 4. NEGATIVE CONTROL: a SIBLING file in the same directory is untouched -----------
    # Without this the whole group passes against a gate that denies the feature directory.
    root4, _ = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
    brief = os.path.join(root4, REL_BRIEF)
    os.makedirs(os.path.dirname(brief), exist_ok=True)
    with open(brief, "w") as f:
        f.write(BRIEF_ON_DISK)
    r4 = _fire_edit(root4, brief, "Goal", "Goal", agent="harness-orchestrator")
    t09("T-09 4: NEGATIVE CONTROL — BRIEF.md beside it is NOT denied by this rule",
        r4.returncode != 2 or "set-task-station" not in r4.stderr,
        f"exit {r4.returncode}, stderr={r4.stderr.strip()[:300]!r}")


def _t09_post_sweep():
    """5-7. What a shell write LANDS is read after the fact, and an un-migrated plan is legal."""

    # ---- 5. THE POST SWEEP'S VOCABULARY RULE ----------------------------------------------
    # A shell write cannot be denied before the fact, so the sweep reads what LANDED. It
    # catches a dead word or a broken file; it CANNOT catch a shell write of a legal value,
    # because it reads disk and cannot attribute an author.
    def _bash_sweep(body):
        root_s, full_s = _approval_root(rel=REL_PLAN, body=body)
        payload = {"agent_type": "harness-orchestrator", "tool_name": "Bash",
                   "hook_event_name": "PostToolUse",
                   "tool_input": {"command": "sed -i '' s/a/b/ " + full_s}}
        return fire_post(root_s, payload)

    r5 = _bash_sweep(_PLAN_ILLEGAL)
    t09("T-09 5: a Bash write landing an ILLEGAL station value is REPORTED by the post sweep",
        r5.returncode == 2 and "Sideways" in r5.stderr,
        f"exit {r5.returncode}, stderr={r5.stderr.strip()[:400]!r}")
    t09("T-09 5: and the report names the FILE as well as the offending value",
        "plan.yaml" in r5.stderr, f"stderr={r5.stderr.strip()[:400]!r}")

    r6 = _bash_sweep(_PLAN_LEGAL)
    t09("T-09 6: NEGATIVE CONTROL — a Bash write landing a LEGAL station value is NOT reported",
        r6.returncode == 0, f"exit {r6.returncode}, stderr={r6.stderr.strip()[:400]!r}")

    # ---- 7. AN UN-MIGRATED PLAN IS LEGAL --------------------------------------------------
    # T-07 adds the top-level key and is NOT a dependency of T-09, so the two are unordered.
    # A rule that REQUIRED the key would report a violation on every plan the sweep meets
    # before T-07 lands. An absent TASK status is legal for the same reason: T-04 leaves it
    # out of REQUIRED_TASK_FIELDS and an absent one reads as the not-started station.
    r7 = _bash_sweep(_PLAN_NO_TOP)
    t09("T-09 7: a plan.yaml carrying NO top-level status is NOT reported — the un-migrated "
        "shape is legal",
        r7.returncode == 0, f"exit {r7.returncode}, stderr={r7.stderr.strip()[:400]!r}")


def _t09_spelling():
    """8. The spelling of the filename is not a route (FEAT-41 F-04)."""

    # ---- 8. THE SPELLING OF THE FILENAME IS NOT A ROUTE (FEAT-41 F-04) --------------------
    # Panel finding F-04, high. RE_PLAN_YAML matched lowercase only, and this workstation's
    # filesystem is case-INSENSITIVE: measured, `echo x > Plan.yaml` overwrites plan.yaml and
    # reports the SAME INODE. So `Plan.yaml` was a write to the real plan that the route denial
    # did not see, and it exited 0 with no stderr at all.
    #
    # HALF OF THE FINDING DID NOT REPRODUCE, and this paragraph WAS TOO WIDE WHEN FIRST WRITTEN
    # -- cycle 1's panel found the hole it had talked past, so it is corrected here rather than
    # deleted, because the wrong version is what a reader would otherwise trust.
    #
    # STILL TRUE: replacing shape-matching WITH realpath would WEAKEN the gate. `./` prefix, a
    # `notes/..` traversal, a doubled slash, an absolute path and a SYMLINKED FEATURE DIRECTORY
    # are all denied already, because the path as written still ends `[^/]+/plan.yaml` and the
    # pattern matches SHAPE. Where such a path resolves is irrelevant.
    #
    # WHAT WAS WRONG: "even a symlinked feature directory" was read as covering symlinks in
    # general, and it does not. A symlinked FILE is the opposite shape -- `notes/innocent.md ->
    # plan.yaml` is innocent at every component, so no pattern matches what was typed, while the
    # write lands in the plan. Case 9 below closes that, by ADDING resolved candidates to the
    # shape test rather than substituting resolution for it.
    #
    # THE FIX DENIES ON A CASE-SENSITIVE FILESYSTEM TOO, where `Plan.yaml` is a genuinely
    # different file. That asymmetry is deliberate: a loud refusal of a file nobody legitimately
    # writes is a far better error than a silent bypass of the one write denial in this gate.
    for spelling in ("Plan.yaml", "PLAN.YAML", "plan.YAML"):
        rel8 = f".harness/harness/features/FEAT-99-fixture/{spelling}"
        root8, full8 = _approval_root(rel=rel8, body=_PLAN_LEGAL)
        r8 = _fire_write(root8, full8, _PLAN_LEGAL, agent="harness-orchestrator")
        t09(f"T-09 8 / F-04: a Write of {spelling} is DENIED — on a case-insensitive "
            f"filesystem it lands on the same inode as plan.yaml",
            r8.returncode == 2, f"exit {r8.returncode}, stderr={r8.stderr.strip()[:300]!r}")

    # NEGATIVE CONTROL. Case-folding the plan pattern must not swallow a sibling whose name
    # merely contains it -- `plan.yaml.bak` and `myplan.yaml` are not the plan.
    for benign in ("plan.yaml.bak", "myplan.yaml"):
        rel8b = f".harness/harness/features/FEAT-99-fixture/{benign}"
        root8b, full8b = _approval_root(rel=rel8b, body=_PLAN_LEGAL)
        r8b = _fire_write(root8b, full8b, _PLAN_LEGAL, agent="harness-orchestrator")
        t09(f"T-09 8 NEGATIVE CONTROL: {benign} is still ALLOWED — the rule is anchored, not "
            f"a substring match",
            r8b.returncode == 0, f"exit {r8b.returncode}, stderr={r8b.stderr.strip()[:300]!r}")


def _t09_symlink():
    """9. A symlink is a route, and its name is not (FEAT-41 H-01)."""

    # ---- 9. A SYMLINK IS A ROUTE, AND ITS NAME IS NOT (FEAT-41 H-01) ----------------------
    # Cycle 1's panel, high, and it is the half of F-04 that case 8 above dismissed TOO WIDELY.
    # Case 8 says a symlinked feature DIRECTORY is already denied, which is true and stays
    # true: the written path still ends `<something>/plan.yaml`, so the shape match sees it.
    #
    # A SYMLINKED FILE IS THE OPPOSITE SHAPE. `notes/innocent.md -> plan.yaml` is a path whose
    # spelling is innocent at every component, so no pattern can match it, while the write
    # lands in plan.yaml. MEASURED BOTH HALVES before fixing:
    #   this runtime's Write tool follows a symlink -- the link stayed a link and the TARGET's
    #     bytes changed, so the route is real and not theoretical
    #   plan.yaml -> exit 2 DENIED; innocent.md -> exit 0 ALLOWED
    # That is a forged approval through a path every squad member is already granted.
    #
    # WHY SHAPE-MATCHING THE TARGET IS NOT THE REALPATH FIX CASE 8 REFUSED. Case 8 refused to
    # replace shape-matching WITH realpath, because resolution would have weakened `./`, `..`,
    # doubled slashes and absolute paths, all of which the shape already denies. This ADDS the
    # resolved target as a second thing to shape-match. Nothing denied today becomes allowed.
    root9, full9 = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                  body=_PLAN_LEGAL)
    link_abs = os.path.join(root9, ".harness", "harness", "features", "FEAT-99-fixture",
                            "notes", "innocent.md")
    os.makedirs(os.path.dirname(link_abs), exist_ok=True)
    os.symlink(os.path.join("..", "plan.yaml"), link_abs)

    r9 = _fire_write(root9, link_abs, _PLAN_LEGAL, agent="harness-orchestrator")
    t09("T-09 9: a Write to a SYMLINK whose name is not plan.yaml is DENIED — the write lands "
        "in the plan, so the link is a route",
        r9.returncode == 2, f"exit {r9.returncode}, stderr={r9.stderr.strip()[:300]!r}")
    # AND THE REFUSAL NAMES THE REAL FILE, not only the link the author typed. A denial that
    # says `innocent.md` is not a route would read as a malfunction -- the exact failure the
    # reason clause in the production denial exists to prevent.
    #
    # ASSERTED ON THE RESOLVED PATH, NOT THE WORD `plan.yaml`. The denial's own prose contains
    # "plan.yaml has exactly ONE writer" whatever it refuses, so a bare substring check would
    # have passed vacuously -- it would have gone green against a message naming only the link.
    t09("T-09 9: the refusal names the feature's plan.yaml, the file the write would reach",
        ".harness/harness/features/FEAT-99-fixture/plan.yaml" in r9.stderr,
        f"stderr={r9.stderr.strip()[:300]!r}")
    # NEGATIVE CONTROL. A symlink pointing at something that is NOT the plan stays allowed --
    # the rule follows the link to a shape test, it does not refuse links as a class.
    root9b, _full9b = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                     body=_PLAN_LEGAL)
    ord_abs = os.path.join(root9b, ".harness", "harness", "features", "FEAT-99-fixture",
                           "notes", "ordinary.md")
    os.makedirs(os.path.dirname(ord_abs), exist_ok=True)
    # THE TARGET CARRIES NO RULES OF ITS OWN, deliberately. Pointing it outside the feature
    # trips the DOMAIN rule and pointing it at BRIEF.md trips that file's `## Approval` shape
    # rule — either way the case would pass for a reason that has nothing to do with routes.
    real_abs = os.path.join(root9b, ".harness", "harness", "features", "FEAT-99-fixture",
                            "notes", "real.md")
    with open(real_abs, "w") as _f:
        _f.write("# note\n")
    os.symlink("real.md", ord_abs)
    r9b = _fire_write(root9b, ord_abs, "# note\n", agent="harness-orchestrator")
    t09("T-09 9 NEGATIVE CONTROL: a symlink to a file that is not the plan is still ALLOWED — "
        "links are followed to a shape test, not refused as a class",
        r9b.returncode == 0, f"exit {r9b.returncode}, stderr={r9b.stderr.strip()[:300]!r}")

    # AND THE POST REPORTER CLASSIFIES BY WHERE THE WRITE LANDED. POST opens the path, which
    # follows the link, so it read the plan's bytes and then looked up rules under the link's
    # innocent name and found none. PRE now refuses this route for every editor tool, so this
    # case defends the REPORTING side against drifting away from the denial beside it.
    root9c, _f9c = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                  body=_PLAN_LEGAL)
    post_link = os.path.join(root9c, ".harness", "harness", "features", "FEAT-99-fixture",
                             "notes", "innocent.md")
    os.makedirs(os.path.dirname(post_link), exist_ok=True)
    os.symlink(os.path.join("..", "plan.yaml"), post_link)
    # An ILLEGAL station value, landed through the link, is what the vocabulary net must see.
    _plan9c = os.path.join(root9c, ".harness", "harness", "features", "FEAT-99-fixture",
                           "plan.yaml")
    with open(_plan9c, "w") as _f:
        _f.write(_PLAN_LEGAL.replace("status: building", "status: Sideways"))
    # THE NAMED-FILE POST BRANCH, not the Bash glob sweep. The sweep finds plan.yaml by GLOB, so
    # it catches a landed illegal value whatever route reached it; this branch is the one that
    # looked up rules by the path it was HANDED, and so exited 0 on the link.
    r9c = fire_post(root9c, {"agent_type": "harness-orchestrator", "tool_name": "Write",
                             "hook_event_name": "PostToolUse",
                             "tool_input": {"file_path": post_link, "content": "x"}})
    t09("T-09 9: the POST reporter follows the link and the vocabulary net speaks — a landed "
        "illegal station is reported even though the path written carries no rules",
        r9c.returncode == 2 and "Sideways" in r9c.stderr,
        f"exit {r9c.returncode}, stderr={r9c.stderr.strip()[:300]!r}")


def _t09_other_routes():
    """11. Hardlink, linked parent directory, and a chain too long (FEAT-41 C2-02)."""

    # ---- 11. THE THREE ROUTES H-01's FIRST FIX STILL LEFT OPEN (FEAT-41 C2-02) ------------
    # Cycle 2's panel, high, all three reproduced live by its security reviewer. H-01 closed the
    # symlinked-FILE case it was shown and stopped there, which is the same mistake in kind that
    # F-04's record made -- fixing the demonstrated instance and reading it as the class.
    #
    #   (a) HARDLINK. `os.path.islink` is False for one, so the hop loop broke immediately and
    #       only the as-typed spelling was matched. A hardlink has NO target to read: it IS the
    #       file, under another name, so no amount of path resolution can see it. Identity can.
    #   (b) LINKED PARENT DIRECTORY. Only the full path was resolved, never an intermediate
    #       component, so `notes-link/innocent.md` where `notes-link -> ../notes` was invisible.
    #   (c) A CHAIN LONGER THAN THE HOP CAP FAILED **OPEN** -- the worst of the three. The real
    #       plan.yaml never entered the candidate list, so the shape test found nothing and the
    #       write was PERMITTED. A cap that runs out must refuse, not shrug.
    #
    # ONE MECHANISM PER QUESTION, and that is why the fix is not three patches: resolution
    # answers "what path does this become" (b, c), and inode identity answers "is this the same
    # file" (a). A hardlink is unanswerable by the first and trivial for the second.
    base9 = ".harness/harness/features/FEAT-99-fixture"
    for label, build, expect in (
        ("a hardlink to plan.yaml", "hardlink", 2),
        ("an innocent file under a LINKED parent directory", "dirlink", 2),
        ("a symlink chain longer than the hop cap", "deepchain", 2),
        ("a hardlink to a file that is NOT the plan", "hardlink_benign", 0),
    ):
        root, plan = _approval_root(rel=f"{base9}/plan.yaml", body=_PLAN_LEGAL)
        featd = os.path.join(root, ".harness", "harness", "features", "FEAT-99-fixture")
        notes = os.path.join(featd, "notes")
        os.makedirs(notes, exist_ok=True)
        if build == "hardlink":
            target = os.path.join(notes, "innocent.md")
            os.link(plan, target)
        elif build == "dirlink":
            # THE LINK ADDS A SEGMENT, and that is what defeats the pattern. `RE_PLAN_YAML`
            # anchors on `features/<one segment>/plan.yaml`, so
            # `features/FEAT-99-fixture/alias/plan.yaml` matches NOTHING even though its final
            # component is spelled plan.yaml and the write lands in another feature's real plan.
            #
            # MY FIRST FIXTURE HERE WAS WRONG and passed for the wrong reason: I made the final
            # component a symlink too, so the existing hop walk resolved it and the case went
            # green while the directory route was still open. A linked DIRECTORY needs the
            # innocent segment to be the directory, never the file.
            other = os.path.join(root, ".harness", "harness", "features", "FEAT-98-other")
            os.makedirs(other, exist_ok=True)
            with open(os.path.join(other, "plan.yaml"), "w") as _f:
                _f.write(_PLAN_LEGAL)
            os.symlink(os.path.join("..", "FEAT-98-other"), os.path.join(featd, "alias"))
            target = os.path.join(featd, "alias", "plan.yaml")
        elif build == "deepchain":
            prev = os.path.join("..", "plan.yaml")
            for i in range(12):
                link = os.path.join(notes, f"hop{i}.md")
                os.symlink(prev, link)
                prev = f"hop{i}.md"
            target = os.path.join(notes, "hop11.md")
        else:
            other = os.path.join(featd, "BRIEF.md")
            with open(other, "w") as _f:
                _f.write("# BRIEF\n")
            target = os.path.join(notes, "innocent2.md")
            os.link(other, target)
        r = _fire_write(root, target, _PLAN_LEGAL, agent="harness-orchestrator")
        verb = "DENIED" if expect == 2 else "still ALLOWED"
        t09(f"T-09 11: a Write through {label} is {verb} — identity and resolution are "
            f"different questions and the plan needs both answered",
            r.returncode == expect,
            f"exit {r.returncode} (want {expect}), stderr={r.stderr.strip()[:300]!r}")


# Path, over-budget body, and the word the refusal must carry. ONE ROW PER `_I`-WIDENED PATTERN
# except RE_PLAN_YAML, which case 8 above already covers with its own case-fold case.
_FOLD_ROWS = (
    ("features/FEAT-99-fixture/{}", "Feature.json", "feature.json", 301, "{}\n", "300"),
    ("features/FEAT-99-fixture/notes/{}", "Handoff-Build.md", "handoff-build.md", 61,
     "# h\n", "60"),
    ("features/FEAT-99-fixture/{}", "State.md", "STATE.md", 121, "# s\n", "120"),
)


def _t09_case_fold():
    """10. Every `_I`-widened pattern is tested, not only the one F-04 fixed."""

    # ---- 10. THE OTHER FOUR `_I` PATTERNS ARE TESTED TOO ----------------------------------
    # Cycle 1's QA, med, and MUTATION-PROVEN by them: removing `_I` from RE_FEATURE_JSON alone
    # produced zero failures across this whole suite. F-04 widened six patterns and only
    # RE_PLAN_YAML -- the one the finding was about -- got a case-fold case. The other five were
    # defence-in-depth that the suite could not tell from dead code.
    #
    # THE DISCRIMINATOR IS THE PAIR, and it is why both spellings are asserted rather than only
    # the folded one: the canonical path proves the BODY genuinely violates the budget, so when
    # the folded path is also refused, the refusal is attributable to `_I` and to nothing else.
    # Drop `_I` from any row's pattern and exactly that row's folded case reds while its
    # canonical case stays green.
    for tmpl, folded, canonical, nlines, unit, budget in _FOLD_ROWS:
        body = unit * nlines
        for spelling, folded_case in ((canonical, False), (folded, True)):
            rel = ".harness/harness/" + tmpl.format(spelling)
            root, full = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
            abs_p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(abs_p), exist_ok=True)
            r = _fire_write(root, abs_p, body, agent="harness-orchestrator")
            t09(f"T-09 10: {spelling} over budget is DENIED"
                + (" — the SPELLING is not a way past a budget" if folded_case else
                   " — the canonical control, proving the body really violates it"),
                r.returncode == 2 and budget in r.stderr,
                f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")

    # NEGATIVE CONTROL, ONE PER FOLDED SPELLING. A case-folded path carrying a LEGAL body is
    # still allowed, so `_I` widened WHICH PATHS ARE MEASURED and did not turn a spelling into a
    # denial of its own.
    #
    # EACH BODY IS LEGAL FOR ITS OWN FILE, and getting that wrong is how these first failed:
    # `{}` repeated is over-budget-free but SCHEMA-invalid for feature.json, and three heading
    # lines are within 60 but violate the handoff's five-section rule. Both refusals were real
    # and had nothing to do with the fold, so the controls would have gone red for a reason that
    # could not distinguish the fix from its absence.
    _legal_bodies = {
        "Feature.json": _legal_feature_json(20),
        "Handoff-Build.md": "\n".join(
            ["## Next", "## Trust"] + ["x"] * 10 + ["## Dead ends", "## Working set",
             "## Done when", "Scope: fixture", "Authority: plan-task:T-02.verify"]) + "\n",
        "State.md": "## Current\n" + "x" * 3 + "\n",
    }
    for tmpl, folded, _canon, _n, _unit, _b in _FOLD_ROWS:
        rel = ".harness/harness/" + tmpl.format(folded)
        root, _full = _approval_root(rel=REL_PLAN, body=_PLAN_LEGAL)
        abs_p = os.path.join(root, rel)
        os.makedirs(os.path.dirname(abs_p), exist_ok=True)
        r = _fire_write(root, abs_p, _legal_bodies[folded], agent="harness-orchestrator")
        t09(f"T-09 10 NEGATIVE CONTROL: {folded} within budget is still ALLOWED — the fold "
            f"widened what is measured, not what is refused",
            r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")



def _t09_unresolvable():
    """12. An unresolvable path refuses, and does not take the hook down (FEAT-41 MF-2/MF-5)."""

    # ---- 12. UNRESOLVABLE MEANS REFUSE, NOT CRASH AND NOT SHRUG (FEAT-41 MF-2 + MF-5) -----
    # Cycle 3's panel, two findings that are one bug, and the panel saw a coupling neither of its
    # own reviewers could: the obvious fix for the crash lands inside the dead branch.
    #
    #   MF-2: `os.path.realpath` raises ValueError -- NOT OSError -- on an embedded NUL, so it
    #         escaped `_resolved_rel`'s except and propagated out of the whole Python body. By
    #         this file's own header, exit 1 is NON-blocking, so the write PROCEEDS. And
    #         `_plan_route` is called unconditionally, so a NUL took budgets and domain grants
    #         down with it, not only the plan route.
    #   MF-5: the `islink` fail-closed branch was DEAD, and the docstring's claim that realpath
    #         "raises on a loop" was FALSE. MEASURED both: realpath on a symlink loop RETURNS
    #         (`/private/tmp/loopt/a`, non-strict), and `os.path.islink` on a NUL path is False.
    #         So widening the except to return None would have routed to a branch that never
    #         fires -- the hole reopening two lines away from its own fix.
    #
    # THE FIX IS THAT UNRESOLVABLE IS ITS OWN ANSWER. Not None, which means "not the plan", but a
    # refusal. Non-strict realpath succeeds for paths that merely do not exist, so the only ways
    # to be unresolvable are pathological -- a NUL, or an OS-level path error. Ordinary work never
    # produces one, which is what makes refusing safe rather than obstructive.
    root12, _p12 = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                  body=_PLAN_LEGAL)
    nul = os.path.join(root12, ".harness", "harness", "features", "FEAT-99-fixture",
                       "innocent\x00.md")
    payload = {"agent_type": "harness-orchestrator", "tool_name": "Write",
               "tool_input": {"file_path": nul, "content": _PLAN_LEGAL}}
    r12 = subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                         text=True, env=_env(root12))
    t09("T-09 12: a NUL-bearing path is REFUSED at exit 2, not exit 1 — exit 1 is non-blocking "
        "here, so a crash is a fail-OPEN",
        r12.returncode == 2, f"exit {r12.returncode}, stderr={r12.stderr.strip()[:300]!r}")
    t09("T-09 12: and it does not crash — no traceback reaches the operator",
        "Traceback" not in r12.stderr, f"stderr={r12.stderr.strip()[:300]!r}")

    # NEGATIVE CONTROL. A path that simply DOES NOT EXIST is resolvable (realpath is non-strict)
    # and must stay allowed, or every first write of a new note would be refused.
    root12b, _p12b = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                    body=_PLAN_LEGAL)
    fresh = os.path.join(root12b, ".harness", "harness", "features", "FEAT-99-fixture",
                         "notes", "brand-new.md")
    os.makedirs(os.path.dirname(fresh), exist_ok=True)
    r12b = _fire_write(root12b, fresh, "# new\n", agent="harness-orchestrator")
    t09("T-09 12 NEGATIVE CONTROL: a path that does not exist yet is still ALLOWED — realpath is "
        "non-strict, so absence is not unresolvable",
        r12b.returncode == 0, f"exit {r12b.returncode}, stderr={r12b.stderr.strip()[:300]!r}")

    # AND A SYMLINK LOOP, which the docstring wrongly claimed realpath raises on. It RESOLVES,
    # so the loop is not the unresolvable case and must not be reported as one.
    root12c, _p12c = _approval_root(rel=".harness/harness/features/FEAT-99-fixture/plan.yaml",
                                    body=_PLAN_LEGAL)
    featc = os.path.join(root12c, ".harness", "harness", "features", "FEAT-99-fixture")
    os.makedirs(os.path.join(featc, "notes"), exist_ok=True)
    os.symlink("loop-b.md", os.path.join(featc, "notes", "loop-a.md"))
    os.symlink("loop-a.md", os.path.join(featc, "notes", "loop-b.md"))
    r12c = _fire_write(root12c, os.path.join(featc, "notes", "loop-a.md"), "x\n",
                       agent="harness-orchestrator")
    t09("T-09 12: a symlink LOOP is allowed, not refused — realpath resolves it rather than "
        "raising, which the old docstring had backwards",
        r12c.returncode == 0, f"exit {r12c.returncode}, stderr={r12c.stderr.strip()[:300]!r}")


def run_t09():
    """FEAT-41 T-09: plan.yaml has exactly ONE writer, and the editor routes are refused."""
    global _T09_FAILS
    _T09_FAILS = 0
    _t09_edit_denial()
    _t09_binds_every_author()
    _t09_post_sweep()
    _t09_spelling()
    _t09_symlink()
    _t09_other_routes()
    _t09_case_fold()
    _t09_unresolvable()
    return _T09_FAILS


def run_t14():
    APPROVED = PLAN_ON_DISK.replace("status: pending\n  approved_by",
                                    "status: approved\n  approved_by")

    # 1. the flip is DENIED, and the message names the fragment and the route
    root, full = _approval_root()
    r = _fire_write(root, full, APPROVED)
    t14("1: a governed agent flipping approval.status is DENIED", r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t14("1: the denial names the approval mapping", MARK in r.stderr and "approval:" in r.stderr,
        r.stderr.strip()[:200])
    t14("1: the denial names the plan-merge route", "plan-merge.py" in r.stderr,
        r.stderr.strip()[:200])

    # FEAT-41 T-09 CLOSED THE EDITOR ROUTE, so every ALLOW below is INVERTED rather than
    # deleted, and this paragraph is why. This group was written when plan.yaml had no shape
    # rule (DEC-182) and the approval_guard was the only thing standing between an agent and
    # the approval mapping — so the guard's ALLOW direction was observable through Write and
    # Edit, and cases 2, 4, 5e, 6, 7, 8, 9, 10a and 10b measured exactly that.
    #
    # T-09 gives plan.yaml exactly ONE writer. The shape gate now refuses Write, Edit and
    # NotebookEdit on that path for EVERY author, including the main session (DEC-180), so no
    # editor write of a plan can be allowed by anything downstream of it. The approval_guard
    # itself is UNCHANGED and still first in line — cases 1, 3 and 5a-5d still see its own
    # message, which is why they still assert MARK.
    #
    # NOTHING LEGITIMATE LOST, and this was verified rather than assumed: `plan-merge.py apply`
    # CREATES a plan.yaml whole when the base does not exist (its step 3), so case 6's route was
    # redundant, not load-bearing. Run at execution time against a fresh legal path: APPLIED,
    # file created.
    #
    # THEY ARE KEPT BECAUSE THE ALLOW DIRECTION STILL MATTERS, just at a different gate: each
    # one now proves the shape denial reaches a case the approval_guard would have permitted,
    # which is the only remaining way to tell "denied by the route rule" from "denied by the
    # approval rule". A deleted case proves neither.

    # 2. INVERTED (T-09). The approval mapping is byte-identical, so the approval_guard has
    # nothing to say — and the ROUTE rule denies it anyway. The assertion that it is NOT the
    # approval message is what distinguishes the two gates.
    root, full = _approval_root()
    added = PLAN_ON_DISK + "  - id: T-03\n    change_type: logic\n    status: pending\n"
    r = _fire_write(root, full, added)
    t14("2 (T-09): adding a task through Write is DENIED BY THE ROUTE RULE, not the approval "
        "guard — plan.yaml has one writer",
        r.returncode == 2 and MARK not in r.stderr and "set-task-station" in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")

    # 3. the ORCHESTRATOR is governed too, and is not the signer (D-10)
    root, full = _approval_root()
    r = _fire_write(root, full, APPROVED, agent="harness-orchestrator")
    t14("3: the orchestrator flipping approval is DENIED too",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 4. THE CASE THE WHOLE DESIGN TURNS ON. No agent_type -> the main session -> allowed.
    root, full = _approval_root()
    payload = {"tool_name": "Write", "tool_input": {"file_path": full, "content": APPROVED}}
    r = subprocess.run([HOOK], input=json.dumps(payload), capture_output=True, text=True,
                       env=_env(root))
    # INVERTED (T-09), AND THIS IS THE CASE THE DESIGN NOW TURNS ON THE OTHER WAY. The main
    # session is still ungoverned by the DOMAIN region — that mechanism is untouched — but the
    # SHAPE gate binds every author by design (DEC-180), because exempting the one author most
    # likely to hand-edit a plan is exactly what T-09 exists to prevent. The main session signs
    # through `plan-merge.py sign-approval`, which T-08 gates on identity so that only it can.
    t14("4 (T-09): the MAIN SESSION's editor write is DENIED TOO — the shape gate binds every "
        "author, and signing is a verb now",
        r.returncode == 2, f"exit {r.returncode}, stderr={r.stderr.strip()[:300]!r}")

    # 5a. TARGETED
    root, full = _approval_root()
    r = _fire_edit(root, full, "  status: pending", "  status: approved")
    t14("5a: a targeted Edit of the signature is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5b. THE MID-LINE-START EVASION. Its FIRST line carries ZERO leading spaces, so any
    # rule anchored on a two-space line start is blind to it. The obvious implementation
    # ALLOWS this, which is why the case exists.
    root, full = _approval_root()
    r = _fire_edit(root, full, "status: pending\n  approved_by:", "status: approved\n  approved_by:")
    t14("5b: the mid-line-start evasion is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5c. THE ACCIDENTAL SWEEP. replace_all over a substring that occurs several times,
    # one of them the signature. Also invisible to an indent rule.
    root, full = _approval_root()
    r = _fire_edit(root, full, "status: pending", "status: approved", replace_all=True)
    t14("5c: the accidental replace_all sweep is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5d. LIMB B: INTRODUCING a block rather than replacing one.
    root, full = _approval_root()
    r = _fire_edit(root, full, "tasks:", "approval:\n  status: approved\ntasks:")
    t14("5d: an Edit INTRODUCING an approval block at column zero is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 5e. THE ALLOW DIRECTION for Edit, and it is the case a deny-everything build fails.
    root, full = _approval_root()
    r = _fire_edit(root, full, "    change_type: logic\n    status: pending",
                   "    change_type: docs\n    status: done")
    t14("5e (T-09): an Edit touching only a task body is DENIED by the route rule",
        r.returncode == 2 and "set-task-station" in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 6. no file on disk -> no signature to destroy
    root = fixture(APPROVAL_MANIFEST)
    full = os.path.join(root, REL_PLAN)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    r = _fire_write(root, full, APPROVED)
    # INVERTED (T-09). Creation does not go through an editor: `plan-merge.py apply` writes a
    # plan whole when the base does not exist, which was measured at execution time.
    t14("6 (T-09): a plan.yaml that does not exist yet is DENIED too — creation goes through "
        "apply, not Write",
        r.returncode == 2,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 7. an unparseable proposal is ALLOWED and SAYS SO. A silent allow and a reported
    # allow are different gates.
    root, full = _approval_root()
    r = _fire_write(root, full, "approval:\n  status: [unclosed\n")
    t14("7 (T-09): an unparseable proposal is DENIED by the route rule — the shape gate never "
        "parses, so unparseable and legal are refused alike",
        r.returncode == 2, f"exit {r.returncode}")
    t14("7: and stderr SAYS the parse failed",
        "could not parse" in r.stderr, r.stderr.strip()[:200])

    # 8. a whitespace-only reflow loads to the same value. A text-comparing build fails here.
    root, full = _approval_root()
    reflowed = PLAN_ON_DISK.replace("  status: pending\n", "  status:   pending\n")
    r = _fire_write(root, full, reflowed)
    t14("8 (T-09): a whitespace-only reflow is DENIED by the route rule, though still NOT by "
        "the approval guard",
        r.returncode == 2 and MARK not in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 9. THE ONLY CASE THAT DISCRIMINATES READING THE RECORD FROM REIMPLEMENTING IT.
    # A hardcoded plan.yaml pattern passes 1-8 and fails this.
    dropped = APPROVAL_MANIFEST.replace(
        '    - ".harness/*/features/*/plan.yaml approval:"\n', "")
    assert dropped != APPROVAL_MANIFEST
    root, full = _approval_root(manifest_text=dropped)
    r = _fire_write(root, full, APPROVED)
    # INVERTED (T-09). Dropping the list entry still disarms the APPROVAL guard — that is the
    # property the intent protects by leaving the entry in place — but the ROUTE rule does not
    # read that list, so the write is refused regardless. Asserted by the message, not the code.
    t14("9 (T-09): dropping the entry from main_session.writes stops the APPROVAL denial but "
        "not the ROUTE denial",
        r.returncode == 2 and MARK not in r.stderr and "one writer" in r.stderr.lower(),
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 10. THE LOUD FAIL-OPEN, both shapes.
    # Derived from APPROVAL_MANIFEST, NOT from FIXTURE_MANIFEST: the grants must stay so
    # the write reaches the guard. Built from the bare fixture it is an ordinary domain
    # denial and this case reports exit 2 for entirely the wrong reason.
    import re as _re
    no_ms = _re.sub(r"main_session:\n(?:  .*\n|    .*\n)+", "", APPROVAL_MANIFEST)
    assert "main_session" not in no_ms, "the main_session stanza was not removed"
    root, full = _approval_root(manifest_text=no_ms)
    r = _fire_write(root, full, APPROVED)
    t14("10a (T-09): no main_session key at all -> still DENIED by the route rule",
        r.returncode == 2 and MARK not in r.stderr, f"exit {r.returncode}")
    t14("10a: and stderr says the exclusion list was unreadable",
        "exclusion list was unreadable" in r.stderr, r.stderr.strip()[:200])
    empty = no_ms.replace("shared:\n", "main_session:\n  writes: []\nshared:\n")
    root, full = _approval_root(manifest_text=empty)
    r = _fire_write(root, full, APPROVED)
    t14("10b (T-09): an empty writes list -> still DENIED by the route rule",
        r.returncode == 2 and MARK not in r.stderr, f"exit {r.returncode}")
    t14("10b: and stderr says the exclusion list was unreadable",
        "exclusion list was unreadable" in r.stderr, r.stderr.strip()[:200])

    # 11. A FRAGMENT-LESS ENTRY CONTRIBUTES NO DENIAL. Assert the ABSENCE of the fragment
    # marker rather than exit 0 -- that path may be refused by ordinary domain rules for
    # unrelated reasons, and a bare exit assertion would pass for the wrong reason.
    root = fixture(APPROVAL_MANIFEST)
    full = os.path.join(root, ".harness", "logs", "2026-01-01.md")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write("# log\n")
    r = _fire_write(root, full, "# log\nchanged\n")
    t14("11: a fragment-less entry (.harness/logs/**) contributes NO fragment denial",
        MARK not in r.stderr, r.stderr.strip()[:200])

    # 12. THE GENERALISATION, BRIEF.md, BOTH DIRECTIONS. This is the half that FAILS before
    # the task: team-config granted pm BRIEF.md whole and "except ## Approval" was a comment.
    root, full = _approval_root(rel=REL_BRIEF, body=BRIEF_ON_DISK)
    flipped = BRIEF_ON_DISK.replace("status: pending", "status: approved")
    r = _fire_write(root, full, flipped)
    t14("12: flipping BRIEF.md's ## Approval body is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")
    t14("12: the denial names the ## Approval heading", "## Approval" in r.stderr,
        r.stderr.strip()[:200])
    root, full = _approval_root(rel=REL_BRIEF, body=BRIEF_ON_DISK)
    goal_only = BRIEF_ON_DISK.replace("Do the thing.", "Do the other thing.")
    r = _fire_write(root, full, goal_only)
    t14("12: changing only ## Goal, leaving ## Approval identical, is ALLOWED",
        r.returncode == 0, f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 13. THE GENERALISATION, PLAN.md. Same hole as case 12.
    root, full = _approval_root(rel=REL_PLANMD, body=BRIEF_ON_DISK)
    r = _fire_write(root, full, BRIEF_ON_DISK.replace("status: pending", "status: approved"))
    t14("13: flipping PLAN.md's ## Approval body is DENIED",
        r.returncode == 2 and MARK in r.stderr,
        f"exit {r.returncode}, stderr={r.stderr.strip()[:200]!r}")

    # 14. THE REPOSITORY'S OWN RECORD, not a fixture. This is why T-14 depends_on T-15:
    # T-15 SUPPLIES the entry. It runs here as well as in T-15's verify because this file
    # runs in the integration kind on every CI run, so it is what keeps noticing if the
    # entry is ever deleted.
    # ROOT, NOT THE ENVIRONMENT. What stood here was the retired two-name chain falling
    # through to "." — the cwd — so this case read a different file depending on where the
    # runner was launched from, and reported the repository's own record missing when it
    # was not. That is half of #556. ROOT comes from __file__ and cannot move (FEAT-42).
    real = os.path.join(ROOT, ".harness", "team-config.yaml")
    try:
        import yaml as _y
        w = (_y.safe_load(open(real)) or {}).get("main_session", {}).get("writes") or []
    except Exception as exc:
        w = []
        t14("14: the real team-config.yaml is readable", False, repr(exc))
    t14("14: the real record carries the plan.yaml approval: entry",
        any(g.endswith("plan.yaml approval:") for g in w), repr(w))
    t14("14: and still carries the BRIEF.md ## Approval entry",
        any(g.endswith("BRIEF.md ## Approval") for g in w), repr(w))
    t14("14: and still carries the PLAN.md ## Approval entry",
        any(g.endswith("PLAN.md ## Approval") for g in w), repr(w))

    fails = 0
    for name, ok, detail in T14:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print("FAIL  %s" % (name,))
            print("      | %s" % (detail,))
    print("\n%d/%d T-14 cases passed." % (len(T14) - fails, len(T14)))
    return fails


FEAT50_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/*/features/*/BRIEF.md, upsert: true }
"""
FEAT50_FEATURE = "FEAT-X-thing"
FEAT50_REL = f".harness/harness/features/{FEAT50_FEATURE}/BRIEF.md"


def _feat50_feature_fixture(wt_id=None):
    root = fixture(FEAT50_MANIFEST)
    if wt_id is None:
        return root, None
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", wt_id), wt_id)
    return root, worktree


def _feat50_binding_case(name, wt_id):
    root, worktree = _feat50_feature_fixture(wt_id)
    target = os.path.join(root, FEAT50_REL)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    result = fire(root, FEAT50_REL)
    ok = result.returncode == 2 and target in result.stderr and worktree in result.stderr
    return (name, ok, f"{result.returncode}: {result.stderr}"), root, worktree, target, result


def _feat50_inside_case(root, worktree):
    rel = os.path.join(os.path.relpath(worktree, root), FEAT50_REL)
    os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
    result = fire(root, rel)
    ok = result.returncode == 0 and "belongs in worktree" not in result.stderr
    return ("feature-checkout-inside binding skipped after worktree strip", ok,
            f"{result.returncode}: {result.stderr}")


def _feat50_absent_case():
    root, _worktree = _feat50_feature_fixture()
    os.makedirs(os.path.dirname(os.path.join(root, FEAT50_REL)), exist_ok=True)
    result = fire(root, FEAT50_REL)
    return ("feature-checkout-absent", result.returncode == 0,
            f"{result.returncode}: {result.stderr}")


def _feat50_mutant_between(start, end, iso):
    with open(HOOK, encoding="utf-8") as source_file:
        source = source_file.read()
    begin = source.find(start)
    finish = source.find(end, begin + len(start))
    if begin < 0 or finish < 0:
        raise AssertionError("INCONCLUSIVE: mutant anchors absent")
    changed = source[:begin] + source[finish:]
    if changed == source:
        raise AssertionError("INCONCLUSIVE: mutant is byte-identical")
    path = os.path.join(iso, "check-domain.sh")
    with open(path, "w", encoding="utf-8") as mutant_file:
        mutant_file.write(changed)
    os.chmod(path, os.stat(HOOK).st_mode)
    return path


def _feat50_binding_red_case(root, target, refused):
    iso = isolated_bin(root)
    mutant = _feat50_mutant_between(
        '        feature_checkout_guard(_verdict["rel"], target)\n',
        '        approval_guard(rel, agent)\n', iso)
    payload = {"agent_type": "harness-documentor", "tool_name": "Write",
               "tool_input": {"file_path": target, "content": "x"}}
    muted = subprocess.run([mutant], input=json.dumps(payload), capture_output=True,
                           text=True, env=_env(root))
    ok = refused.returncode == 2 and muted.returncode == 0 and "Traceback" not in muted.stderr
    return ("feature-checkout-red", ok,
            f"real={refused.returncode}, mutant={muted.returncode}: {muted.stderr}")


def _feat50_digest_fixture():
    root = fixture("schema_version: 1\nteams: []\n")
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-D"), "FEAT-D")
    rel = ".harness/harness/features/FEAT-D-thing/runs/r1/digest.md"
    path = os.path.join(worktree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return root, path


def _feat50_digest_fire(root, path, content, *flags, hook=HOOK):
    payload = {"tool_name": "Write",
               "tool_input": {"file_path": path, "content": content}}
    return subprocess.run([hook, *flags], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def _feat50_write_text(path, content):
    with open(path, "w", encoding="utf-8") as digest_file:
        digest_file.write(content)


def _feat50_digest_clobber_case(root, path, prior):
    _feat50_write_text(path, prior)
    result = _feat50_digest_fire(root, path, "wholly different digest\n")
    ok = (result.returncode == 2
          and "replace rather than extend" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("digest-clobber", ok, f"{result.returncode}: {result.stderr}"), result


def _feat50_digest_append_case(root, path, prior):
    append = _feat50_digest_fire(root, path, prior + "and more\n")
    _feat50_write_text(path, " \n")
    whitespace = _feat50_digest_fire(root, path, "first digest\n")
    os.unlink(path)
    new_file = _feat50_digest_fire(root, path, "first digest\n")
    ok = append.returncode == 0 and whitespace.returncode == 0 and new_file.returncode == 0
    detail = (f"append={append.returncode}, whitespace={whitespace.returncode}, "
              f"new={new_file.returncode}")
    return "digest-append", ok, detail


def _feat50_digest_unreadable_case(root, path):
    os.makedirs(path)
    result = _feat50_digest_fire(root, path, "replacement\n")
    os.rmdir(path)
    ok = result.returncode == 2 and "cannot be read safely" in result.stderr
    return "digest-unreadable", ok, f"{result.returncode}: {result.stderr}"


def _feat50_digest_post_case(root, path, prior):
    _feat50_write_text(path, prior)
    result = _feat50_digest_fire(root, path, "wholly different digest\n", "--post")
    ok = result.returncode == 0 and "recorded digest" not in result.stderr
    return "digest rule is PRE-Write-only", ok, f"{result.returncode}: {result.stderr}"


def _feat50_digest_red_case(root, path, clobber):
    iso = isolated_bin(root)
    mutant = _feat50_mutant_between(
        "    # Issue #1058: a lead reused a cycle's run directory",
        "    if RE_FEATURE_JSON.match(rel):", iso)
    muted = _feat50_digest_fire(root, path, "wholly different digest\n", hook=mutant)
    ok = clobber.returncode == 2 and muted.returncode == 0 and "Traceback" not in muted.stderr
    return ("digest-clobber-red", ok,
            f"real={clobber.returncode}, mutant={muted.returncode}: {muted.stderr}")


def _report_feat50_artifact_results(results):
    failures = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    {name}")
            continue
        failures += 1
        print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(results) - failures}/{len(results)} FEAT-50 artifact-integrity cases passed.")
    return failures


def _bug1124_state_fixture():
    root = fixture("schema_version: 1\nteams: []\n")
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-S"), "FEAT-S")
    rel = ".harness/harness/features/FEAT-S-thing/runs/r1/state.yaml"
    path = os.path.join(worktree, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return root, path


def _bug1124_state_fire(root, path, content, *flags, hook=HOOK):
    payload = {"tool_name": "Write",
               "tool_input": {"file_path": path, "content": content}}
    return subprocess.run([hook, *flags], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def _bug1124_collision_case(root, path):
    """Issue #1124: a slug reused for a DIFFERENT run's state.yaml is refused."""
    _feat50_write_text(path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    result = _bug1124_state_fire(root, path, "schema_version: 1\nrun_id: run-beta\nstatus: building\n")
    ok = (result.returncode == 2
          and "different run's state" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("state-run-id-collision", ok, f"{result.returncode}: {result.stderr}"), result


def _bug1124_upsert_case(root, path):
    """The SAME run_id may be rewritten any number of times — the checkpoint upsert (DEC-154)."""
    _feat50_write_text(path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    first = _bug1124_state_fire(root, path, "schema_version: 1\nrun_id: run-alpha\nstatus: reviewing\n")
    second = _bug1124_state_fire(root, path, "schema_version: 1\nrun_id: run-alpha\ncycles_used: 3\n")
    ok = first.returncode == 0 and second.returncode == 0
    return ("state-run-id-upsert-allowed", ok,
            f"first={first.returncode}:{first.stderr}, second={second.returncode}:{second.stderr}")


def _bug1124_no_run_id_case(root, path):
    """Issue #1106, gap (b): a prior file with no run_id used to be silently allowed through
    unchanged — the write could not be shown to be the same run, and "cannot verify" was
    treated as "allow". Now it is refused: the identity cannot be verified, so a Write that
    could silently replace the prior checkpoint is denied."""
    _feat50_write_text(path, "schema_version: 1\nstatus: building\n")
    result = _bug1124_state_fire(root, path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    ok = (result.returncode == 2
          and "no run_id" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("state-no-prior-run-id-refused", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_no_incoming_run_id_case(root, path):
    """The symmetric case: a prior WITH run_id, and an incoming write that carries none.
    Also refused — the incoming write cannot be shown to be an upsert of that run either."""
    _feat50_write_text(path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    result = _bug1124_state_fire(root, path, "schema_version: 1\nstatus: reviewing\n")
    ok = (result.returncode == 2
          and "carries no run_id" in result.stderr
          and "run directory of its own" in result.stderr)
    return ("state-no-incoming-run-id-refused", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_prior_unparseable_case(root, path):
    """Issue #1106, gap (b): a prior that exists with content but is not valid YAML — a
    genuinely different failure mode from an UNREADABLE prior (permission denied, a
    directory) already covered by `_bug1124_unreadable_case`. Must also refuse."""
    _feat50_write_text(path, "status: [unterminated flow seq\n")
    result = _bug1124_state_fire(root, path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    ok = (result.returncode == 2
          and "does not parse" in result.stderr
          and "silently replace" in result.stderr)
    return ("state-prior-unparseable-refused", ok, f"{result.returncode}: {result.stderr}")



def _bug1124_new_file_case(root, path):
    result = _bug1124_state_fire(root, path, "schema_version: 1\nrun_id: run-gamma\nstatus: building\n")
    ok = result.returncode == 0
    return ("state-new-file-allowed", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_unreadable_case(root, path):
    """Code review finding: a prior state.yaml that lexists but cannot be OPENED (here, a
    directory sitting at the path) must deny, mirroring the sibling #1058 digest guard —
    not fail open by treating an unreadable prior as "nothing to compare"."""
    os.makedirs(path)
    result = _bug1124_state_fire(root, path, "schema_version: 1\nrun_id: run-delta\n")
    os.rmdir(path)
    ok = result.returncode == 2 and "cannot be read safely" in result.stderr
    return ("state-unreadable-prior-denied", ok, f"{result.returncode}: {result.stderr}")


def _bug1124_red_case(root, path, collision):
    iso = isolated_bin(root)
    mutant = _feat50_mutant_between(
        "        # Issue #1124: the digest guard above (#1058) fires only on digest.md",
        "        # T-17 / D-08: str() BOTH sides.", iso)
    muted = _bug1124_state_fire(root, path,
                                "schema_version: 1\nrun_id: run-beta\nstatus: building\n",
                                hook=mutant)
    ok = collision.returncode == 2 and muted.returncode == 0 and "Traceback" not in muted.stderr
    return ("state-run-id-collision-red", ok,
            f"real={collision.returncode}, mutant={muted.returncode}: {muted.stderr}")


def _bug895_fixture():
    root = fixture("""schema_version: 1
teams:
  - name: harness-documentor
    domain:
      - { path: .harness/allowed/**, upsert: true }
""")
    os.makedirs(os.path.join(root, ".harness", "allowed"), exist_ok=True)
    wt = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "OTHER"), "OTHER")
    os.makedirs(os.path.join(wt, ".harness", "allowed"), exist_ok=True)
    # A session can only ROOT at wt (via HARNESS_PROJECT_DIR) if wt itself carries
    # the MARKER harness_boundary.resolve_root checks for — unlike
    # make_linked_worktree's usual callers, this test roots its session AT the
    # worktree, not at `root`, so the worktree needs its own copy of the same grant.
    # `.harness/allowed/**`, not a bare `allowed/**`: only a control-plane-shaped
    # target (first segment `.harness`/`.claude`/`.agents`/`.omp`) can be granted at
    # all on a bare harness base with no product workspace configured.
    with open(os.path.join(wt, ".harness", "team-config.yaml"), "w") as f:
        f.write("""schema_version: 1
teams:
  - name: harness-documentor
    domain:
      - { path: .harness/allowed/**, upsert: true }
""")
    return root, wt


def _bug895_fire(session_root, abs_target):
    payload = {"agent_type": "harness-documentor", "tool_name": "Write",
               "tool_input": {"file_path": abs_target, "content": "x"}}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(session_root))


def _bug895_wrong_checkout_case(root, wt):
    """Issue #895: a session rooted in a worktree, writing into its own main
    checkout's copy of an identically-shaped allowed path, is refused by identity —
    not waved through as 'not our problem', which is how FEAT-40's ship write-back
    (commit 3952814) landed in main from a worktree session."""
    r = _bug895_fire(wt, os.path.join(root, ".harness", "allowed", "x.txt"))
    ok = (r.returncode == 2 and "BLOCKED" in r.stderr and "is rooted in" in r.stderr
          and wt in r.stderr)
    return ("wrong-checkout: worktree session writing into main is refused",
            ok, f"{r.returncode}: {r.stderr}")


def _bug895_own_checkout_case(wt):
    """NEGATIVE CONTROL: the identical grant, written into the session's OWN
    checkout, still works — this is a checkout-identity check, not a new denial on
    the domain grant itself."""
    r = _bug895_fire(wt, os.path.join(wt, ".harness", "allowed", "x.txt"))
    return ("wrong-checkout NEGATIVE CONTROL: same session, own checkout, still allowed",
            r.returncode == 0, f"{r.returncode}: {r.stderr}")


def _bug895_scratch_case(wt):
    """NEGATIVE CONTROL: an unrelated path outside any checkout of this repository
    (e.g. /tmp) stays a not-a-domain-question, exit 0 — this only governs writes
    that land in a REAL checkout of the SAME repository."""
    scratch = os.path.join(tempfile.mkdtemp(), "scratch.txt")
    r = _bug895_fire(wt, scratch)
    return ("wrong-checkout NEGATIVE CONTROL: an unrelated scratch path is untouched",
            r.returncode == 0, f"{r.returncode}: {r.stderr}")


def _bug895_mutant_hook():
    """A full copy of bin/ with harness_boundary.py's WRONG CHECKOUT detection block
    removed, so `import harness_boundary` inside the copy's own check-domain.sh
    resolves to the mutant — `sys.path.insert(0, _bin_dir)` makes the copy's own
    directory win regardless of PYTHONPATH, so only a real sibling copy shadows it."""
    with open(os.path.join(HERE, "harness_boundary.py"), encoding="utf-8") as f:
        source = f.read()
    start = source.find(
        '        # WRONG CHECKOUT, SAME REPOSITORY (issue #895).')
    end = source.find(
        '        # NOT A DOMAIN QUESTION, unchanged.')
    if start < 0 or end < 0 or end <= start:
        return None
    mutated = source[:start] + source[end:]
    if mutated == source:
        return None
    mbin = tempfile.mkdtemp(prefix="bug895-boundary-mutant-")
    shutil.copytree(HERE, mbin, dirs_exist_ok=True)
    with open(os.path.join(mbin, "harness_boundary.py"), "w", encoding="utf-8") as f:
        f.write(mutated)
    return os.path.join(mbin, os.path.basename(HOOK))


def _bug895_red_case(root, wt, real_result):
    mutant_hook = _bug895_mutant_hook()
    if mutant_hook is None:
        return ("wrong-checkout-red", False,
                "INCONCLUSIVE: the wrong-checkout block anchors were not found by "
                "their source text")
    payload = {"agent_type": "harness-documentor", "tool_name": "Write",
               "tool_input": {"file_path": os.path.join(root, ".harness", "allowed", "x.txt"),
                              "content": "x"}}
    muted = subprocess.run([mutant_hook], input=json.dumps(payload),
                           capture_output=True, text=True, env=_env(wt))
    ok = (real_result.returncode == 2 and muted.returncode == 0
          and "Traceback" not in muted.stderr)
    return ("wrong-checkout-red", ok,
            f"real={real_result.returncode} mutant={muted.returncode}: {muted.stderr}")


def run_bug895_wrong_checkout_cases():
    """Issue #895: path-shape authorization now sees WHICH checkout a write lands
    in, not just whether the relative path shape matches a grant."""
    root, wt = _bug895_fixture()
    wrong = _bug895_wrong_checkout_case(root, wt)
    results = [
        wrong,
        _bug895_own_checkout_case(wt),
        _bug895_scratch_case(wt),
        _bug895_red_case(root, wt, _bug895_fire(
            wt, os.path.join(root, ".harness", "allowed", "x.txt"))),
    ]
    fails = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    [bug895] {name}")
        else:
            fails += 1
            print(f"FAIL  [bug895] {name}\n      | {detail}")
    print(f"\n{len(results) - fails}/{len(results)} bug895 wrong-checkout cases passed.")
    return fails

def _feat52_foreign_cwd_receipt_pair():
    workspace = tempfile.mkdtemp()
    root = fixture_fleet(
        """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/*/features/*/runs/**, upsert: true }
""",
        ("schema: factory-fleet/1\n"
         f"workspace_root: {workspace}\n"
         "repos:\n"
         "  - name: acme/widget\n"
         "    default_branch: main\n"),
    )
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-90"), "FEAT-90"
    )
    rel = ".harness/harness/features/FEAT-90-alpha/runs/r1/receipt.md"
    receipt = os.path.join(worktree, rel)
    product_cwd = os.path.join(workspace, "widget")
    os.makedirs(os.path.dirname(receipt), exist_ok=True)
    os.makedirs(product_cwd, exist_ok=True)

    def invoke(path):
        payload = {"agent_type": "harness-documentor", "tool_name": "Write",
                   "tool_input": {"file_path": path, "content": "x"}}
        return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                              text=True, env=_env(root), cwd=product_cwd)

    allowed = invoke(receipt)
    refused = invoke(os.path.join(product_cwd, rel))
    return (
        "SC-15 PAIR: foreign product cwd allows its feature-worktree receipt and refuses its product twin",
        allowed.returncode == 0 and refused.returncode == 2,
        f"allow={allowed.returncode}: {allowed.stderr}; refuse={refused.returncode}: {refused.stderr}",
    )


def run_feat50_artifact_integrity():
    """Issues #1057/#1058: bind feature writes and preserve recorded digests."""
    main, root, worktree, target, refused = _feat50_binding_case(
        "feature-checkout-main", FEAT50_FEATURE)
    short, _short_root, _short_worktree, _short_target, _short_result = (
        _feat50_binding_case("feature-checkout-main short prefix", "FEAT-X"))
    digest_root, digest_path = _feat50_digest_fixture()
    prior = "recorded cycle-0 text\n"
    clobber_case, clobber = _feat50_digest_clobber_case(digest_root, digest_path, prior)
    state_root1, state_path1 = _bug1124_state_fixture()
    collision_case, collision = _bug1124_collision_case(state_root1, state_path1)
    state_root2, state_path2 = _bug1124_state_fixture()
    state_root3, state_path3 = _bug1124_state_fixture()
    state_root4, state_path4 = _bug1124_state_fixture()
    state_root5, state_path5 = _bug1124_state_fixture()
    state_root6, state_path6 = _bug1124_state_fixture()
    state_root7, state_path7 = _bug1124_state_fixture()
    results = [
        main,
        short,
        _feat50_inside_case(root, worktree),
        _feat50_absent_case(),
        _feat50_binding_red_case(root, target, refused),
        clobber_case,
        _feat50_digest_append_case(digest_root, digest_path, prior),
        _feat50_digest_unreadable_case(digest_root, digest_path),
        _feat50_digest_post_case(digest_root, digest_path, prior),
        _feat50_digest_red_case(digest_root, digest_path, clobber),
        collision_case,
        _bug1124_upsert_case(state_root2, state_path2),
        _bug1124_no_run_id_case(state_root3, state_path3),
        _bug1124_new_file_case(state_root4, state_path4),
        _bug1124_red_case(state_root1, state_path1, collision),
        _bug1124_unreadable_case(state_root5, state_path5),
        _bug1124_no_incoming_run_id_case(state_root6, state_path6),
        _bug1124_prior_unparseable_case(state_root7, state_path7),
        _feat52_foreign_cwd_receipt_pair(),
    ]
    return _report_feat50_artifact_results(results)


def _fire_digest_edit(root, path, old_s, new_s, replace_all=False):
    # NO agent_type, matching _feat50_digest_fire/_bug1124_state_fire's payload shape:
    # these cases test the SHAPE gate (DEC-180, domain-independent), not the domain
    # phase, and check-domain.sh exempts a payload with no agent_type from the domain
    # phase entirely so the shape-only behaviour can be isolated.
    return _fire_edit(root, path, old_s, new_s, agent=None, replace_all=replace_all)


def run_bug1106_edit_route_cases():
    """Issue #1106, gap (a): an Edit targeting a run's digest.md or state.yaml is now
    intercepted PRE-write, by reconstructing the full resulting content from the on-disk
    prior and old_string/new_string, then running it through the SAME content guards the
    Write route already uses (issue #1058's digest prefix test, issues #1124/#1106's
    state.yaml run-identity test)."""
    results = []

    # --- digest.md: a REPLACE-shaped Edit (old_string spans the whole prior text) must
    # be refused exactly like a Write that would replace it.
    digest_root, digest_path = _feat50_digest_fixture()
    prior = "recorded cycle-0 text\n"
    _feat50_write_text(digest_path, prior)
    r = _fire_digest_edit(digest_root, digest_path, prior, "wholly different digest\n")
    results.append(("bug1106 Edit route: replacing a run's digest.md via Edit is REFUSED",
                    r.returncode == 2 and "replace rather than extend" in r.stderr,
                    f"exit {r.returncode}: {r.stderr.strip()[:250]}"))
    on_disk = open(digest_path, encoding="utf-8").read()
    results.append(("bug1106 Edit route: the refused digest Edit left the file untouched",
                    on_disk == prior, repr((prior, on_disk))))

    # --- digest.md: a genuine APPEND-shaped Edit (old_string is a true prefix, new_string
    # extends it) is allowed — this is not a blanket "no Edit on digest.md" rule.
    digest_root2, digest_path2 = _feat50_digest_fixture()
    _feat50_write_text(digest_path2, prior)
    r = _fire_digest_edit(digest_root2, digest_path2, prior, prior + "and more\n")
    results.append(("bug1106 Edit route NEGATIVE CONTROL: a genuine append via Edit is "
                    "ALLOWED", r.returncode == 0, f"exit {r.returncode}: {r.stderr[:200]}"))

    # --- state.yaml: an Edit that changes run_id to a DIFFERENT run is refused exactly
    # like the equivalent Write.
    state_root, state_path = _bug1124_state_fixture()
    _feat50_write_text(state_path, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    r = _fire_digest_edit(state_root, state_path, "run_id: run-alpha", "run_id: run-beta")
    results.append(("bug1106 Edit route: a state.yaml run_id collision via Edit is "
                    "REFUSED",
                    r.returncode == 2 and "different run's state" in r.stderr,
                    f"exit {r.returncode}: {r.stderr.strip()[:250]}"))
    on_disk = open(state_path, encoding="utf-8").read()
    results.append(("bug1106 Edit route: the refused state.yaml Edit left the file "
                    "untouched", "run-alpha" in on_disk, on_disk))

    # --- state.yaml: the SAME run_id, a legitimate checkpoint upsert via Edit, is
    # allowed.
    state_root2, state_path2 = _bug1124_state_fixture()
    _feat50_write_text(state_path2, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    r = _fire_digest_edit(state_root2, state_path2, "status: building", "status: reviewing")
    results.append(("bug1106 Edit route NEGATIVE CONTROL: a same-run_id checkpoint "
                    "upsert via Edit is ALLOWED",
                    r.returncode == 0, f"exit {r.returncode}: {r.stderr[:200]}"))

    # --- An ambiguous or unmatched Edit payload cannot describe the candidate bytes.
    # Governed artifacts fail closed and route the caller to a whole-file Write rather
    # than assuming the editor will reject the operation before this hook matters.
    state_root3, state_path3 = _bug1124_state_fixture()
    _feat50_write_text(state_path3, "schema_version: 1\nrun_id: run-alpha\nstatus: building\n")
    r = _fire_digest_edit(state_root3, state_path3, "no-such-text-in-file", "replacement")
    results.append(("bug1106 Edit route: an unmatched old_string fails closed",
                    r.returncode == 2
                    and "Write the complete file instead" in r.stderr,
                    f"exit {r.returncode}: {r.stderr[:200]}"))

    state_root4, state_path4 = _bug1124_state_fixture()
    _feat50_write_text(
        state_path4, "schema_version: 1\nrun_id: run-alpha\nstatus: x\nnote: x\n")
    r = _fire_digest_edit(state_root4, state_path4, "x", "y")
    results.append(("bug1106 Edit route: a non-unique old_string fails closed",
                    r.returncode == 2
                    and "Write the complete file instead" in r.stderr,
                    f"exit {r.returncode}: {r.stderr[:200]}"))

    # --- An Edit to an UNRELATED file (not digest.md/state.yaml) is completely
    # unaffected by this widening — the PRE route stays Write-only for everything else.
    other_root, other_path = _feat50_digest_fixture()
    other_path = other_path.replace("digest.md", "notes.md")
    _feat50_write_text(other_path, "some notes\n")
    r = _fire_digest_edit(other_root, other_path, "some notes", "different notes entirely")
    results.append(("bug1106 Edit route NEGATIVE CONTROL: an unrelated file's Edit is "
                    "still unaffected (no PRE check runs at all for it)",
                    r.returncode == 0, f"exit {r.returncode}: {r.stderr[:200]}"))

    fails = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(results) - fails}/{len(results)} bug1106 Edit-route cases passed.")
    return fails
def _bug1305_digest_write(root, path, content):
    payload = {"tool_name": "Write",
               "tool_input": {"file_path": path, "content": content}}
    return subprocess.run(
        [HOOK], input=json.dumps(payload), capture_output=True, text=True,
        env=_env(root))


def run_bug1305_digest_repair_cases():
    """BUG-1305 SC-05: legal append repair and actionable refusal wording."""
    prior = "VERDICT: PASS\nDIGEST:\n  headline: recorded\n"
    artifact = "  artifact: notes/x.md\n"
    results = []

    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    response = _fire_digest_edit(
        root, path, "  headline: recorded\n",
        "  headline: recorded\n" + artifact)
    results.append(("digest Edit append repair remains allowed",
                    response.returncode == 0, response.stderr))

    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    response = _fire_digest_edit(
        root, path, "VERDICT: PASS\n", artifact + "VERDICT: PASS\n")
    results.append(("digest Edit insertion is refused with append-at-end route",
                    response.returncode == 2 and "appended at the end" in response.stderr,
                    response.stderr))

    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    response = _bug1305_digest_write(root, path, "wholly different digest\n")
    results.append(("cross-run digest replacement remains refused",
                    response.returncode == 2, response.stderr))

    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    response = _bug1305_digest_write(root, path, prior + artifact)
    results.append(("digest Write append remains allowed",
                    response.returncode == 0, response.stderr))

    root, path = _feat50_digest_fixture()
    _feat50_write_text(path, prior)
    _bug1305_write_marker(path)
    response = _bug1305_digest_write(root, path, prior + artifact)
    results.append(("digest Write append remains allowed beside identity witness",
                    response.returncode == 0, response.stderr))

    failures = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    [bug1305-digest] {name}")
        else:
            failures += 1
            print(f"FAIL  [bug1305-digest] {name}\n      | {str(detail).strip()[:300]}")
    print(f"\n{len(results) - failures}/{len(results)} BUG-1305 digest cases passed.")
    return failures




def run_bug1106_shared_pattern_consistency():
    """The digest.md/state.yaml patterns are respelled, not shared, between
    check-domain.sh (whose shape-phase import of harness_boundary must stay ABSORBING —
    see the comment beside RE_STATE_YAML there) and harness_boundary.py (which
    bash-write-guard.sh imports safely). Assert the two copies are byte-identical so this
    respelling cannot silently drift (issue #1106)."""
    with open(HOOK, encoding="utf-8") as f:
        cd_source = f.read()
    with open(os.path.join(HERE, "harness_boundary.py"), encoding="utf-8") as f:
        hb_source = f.read()

    def _pattern_literal(source, varname):
        marker = varname + " "
        idx = source.find("\n" + marker)
        if idx < 0:
            return None
        line = source[idx + 1:source.index("\n", idx + 1)]
        if "re.compile(r" not in line:
            return None
        start = line.index('r"') + 1
        end = line.index('"', start + 1)
        return line[start:end + 1]

    cd_digest = _pattern_literal(cd_source, "RE_RUN_DIGEST  ")
    hb_digest = _pattern_literal(hb_source, "RE_RUN_DIGEST =")
    cd_state = _pattern_literal(cd_source, "RE_STATE_YAML  ")
    hb_state = _pattern_literal(hb_source, "RE_STATE_YAML =")

    results = [
        ("bug1106: RE_RUN_DIGEST is found in both check-domain.sh and harness_boundary.py",
         cd_digest is not None and hb_digest is not None,
         f"check-domain={cd_digest!r} harness_boundary={hb_digest!r}"),
        ("bug1106: RE_RUN_DIGEST's pattern text is byte-identical in both files",
         cd_digest == hb_digest, f"{cd_digest!r} != {hb_digest!r}"),
        ("bug1106: RE_STATE_YAML is found in both check-domain.sh and harness_boundary.py",
         cd_state is not None and hb_state is not None,
         f"check-domain={cd_state!r} harness_boundary={hb_state!r}"),
        ("bug1106: RE_STATE_YAML's pattern text is byte-identical in both files",
         cd_state == hb_state, f"{cd_state!r} != {hb_state!r}"),
    ]
    fails = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(results) - fails}/{len(results)} bug1106 pattern-consistency cases "
          "passed.")
    return fails



def _feat51_root(reg, agent=None, runtime=None, supervisor_pid=None):
    root, _ = _approval_root(rel=REL_BRIEF, body=BRIEF_ON_DISK)
    if agent:
        reg.claim_with_receipt(
            root, agent, "harness-product-lead", root,
            feature="FEAT-99-fixture",
            session=("feat51-writer" if agent == "harness-orchestrator"
                     else "other-session"),
            runtime=runtime,
            supervisor_pid=supervisor_pid,
        )
    return root


def _feat51_fire(root, rel, hook=None):
    content = BRIEF_ON_DISK if rel == REL_BRIEF else "replacement\n"
    payload = {
        "agent_type": "harness-orchestrator",
        "session_id": "feat51-writer",
        "tool_name": "Write",
        "tool_input": {"file_path": os.path.join(root, rel), "content": content},
    }
    return subprocess.run(
        [hook or HOOK], input=json.dumps(payload), capture_output=True,
        text=True, env=_env(root),
    )


def _feat51_result(name, result, want, mention=None):
    ok = result.returncode == want and (mention is None or mention in result.stderr)
    return name, ok, f"exit {result.returncode}: {result.stderr}"


def _feat51_refusal_cases(reg, quarantine):
    root = _feat51_root(reg, "harness-qa")
    brief_path = os.path.join(root, REL_BRIEF)
    before = open(brief_path, "rb").read()
    refused = _feat51_fire(root, REL_BRIEF)
    after = open(brief_path, "rb").read()
    return [
        _feat51_result("an orphan canonical write is quarantined",
                       refused, 2, quarantine),
        ("the refused orphan write does not modify the canonical artifact",
         before == after, "canonical BRIEF.md changed"),
        _feat51_result(
            "NEGATIVE CONTROL: with the registry healthy an orphan canonical write is still refused",
            _feat51_fire(root, REL_BRIEF), 2, quarantine),
    ], root


def _feat51_fail_open_cases(reg, root):
    registry_path = os.path.join(root, reg.REGISTRY_REL)
    os.remove(registry_path)
    os.mkdir(registry_path)
    fired = _feat51_fire(root, REL_BRIEF)
    raising = _feat51_result(
        "an existing-but-unreadable registry (a directory) is refused fail-closed at the "
        "BUG-1304 claim boundary before the quarantine branch (REQ-05/SC-10 supersede this "
        "FEAT-51 fixture; quarantine fail-open stays pinned by the unimportable case below "
        "and by test-plan-sign-gate.py)",
        fired, 2, "claim registries are unreadable")
    names_file = (
        "the unreadable-registry refusal names the registry file to repair (REQ-05)",
        reg.REGISTRY_REL in fired.stderr, fired.stderr)

    root = _feat51_root(reg, "harness-qa")
    copybin = tempfile.mkdtemp()
    shutil.copytree(HERE, copybin, dirs_exist_ok=True)
    os.remove(os.path.join(copybin, "inflight_registry.py"))
    unimportable = _feat51_result(
        "an unimportable inflight_registry fails OPEN at the check-domain.sh quarantine branch",
        _feat51_fire(root, REL_BRIEF, hook=os.path.join(copybin, "check-domain.sh")),
        0, "boundary was not enforced")
    return [raising, names_file, unimportable]


def _feat51_omp_case(reg):
    supervisor = subprocess.Popen(
        [sys.executable, "-c", "import time; time.sleep(60)"]
    )
    try:
        root = _feat51_root(
            reg, "harness-qa", runtime="omp", supervisor_pid=supervisor.pid
        )
        return _feat51_result(
            "an omp-runtime writer is never quarantined",
            _feat51_fire(root, REL_BRIEF), 0)
    finally:
        supervisor.terminate()
        supervisor.wait()


def _feat51_allow_cases(reg, quarantine):
    own = _feat51_root(reg, "harness-orchestrator")
    empty = _feat51_root(reg)
    orphan = _feat51_root(reg, "harness-qa")
    notes = ".harness/harness/features/FEAT-99-fixture/notes/report.txt"
    return [
        _feat51_result("the writer own live claim allows the canonical write",
                       _feat51_fire(own, REL_BRIEF), 0),
        _feat51_result("a feature with no live claim allows the canonical write",
                       _feat51_fire(empty, REL_BRIEF), 0),
        _feat51_omp_case(reg),
        _feat51_result("an orphan write to notes is allowed",
                       _feat51_fire(orphan, notes), 0),
        _feat51_result("an orphan write to the quarantine path is allowed",
                       _feat51_fire(orphan, quarantine), 0),
    ], orphan


def _feat51_route_cases(root):
    result = _feat51_fire(root, REL_PLAN)
    return [
        _feat51_result("an orphan Write of plan.yaml keeps the FEAT-41 route denial",
                       result, 2, "exactly ONE writer"),
        ("the plan.yaml route denial does not mention quarantine",
         "quarantine" not in result.stderr, result.stderr),
    ]


def _report_feat51_results(results):
    fails = 0
    for name, ok, detail in results:
        print(("ok    " if ok else "FAIL  ") + name)
        if not ok:
            fails += 1
            print("      " + detail[:500])
    return fails


def run_feat51_orphan_write():
    sys.path.insert(0, HERE)
    import inflight_registry as reg

    quarantine = (
        ".harness/harness/features/FEAT-99-fixture/quarantine/"
        "harness-orchestrator-feat51-w/BRIEF.md"
    )
    refusal, refused_root = _feat51_refusal_cases(reg, quarantine)
    allowed, orphan_root = _feat51_allow_cases(reg, quarantine)
    results = refusal + _feat51_fail_open_cases(reg, refused_root) + allowed
    results += _feat51_route_cases(orphan_root)
    return _report_feat51_results(results)


def _record_handoff_result(results, name, result, want, needles=None):
    needles = () if needles is None else (
        needles if isinstance(needles, tuple) else (needles,))
    stderr = result.stderr.lower()
    ok = result.returncode == want and all(needle.lower() in stderr for needle in needles)
    results.append((name, ok, f"exit {result.returncode}: {result.stderr.strip()[:180]}"))


def _handoff_text(body, trust_lines=1):
    lines = ["## Next", "next", "## Trust"]
    lines += [f"trust {n}" for n in range(trust_lines)]
    lines += ["## Dead ends", "none", "## Working set", "set", "## Done when"]
    lines += body.splitlines()
    return "\n".join(lines) + "\n"


def _invoke_handoff(root, target, content):
    payload = {"tool_name": "Write",
               "tool_input": {"file_path": target, "content": content}}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


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


def _handoff_grammar_cases(results, root, target, valid):
    missing = "\n".join(["## Next", "next", "## Trust", "trust",
                         "## Dead ends", "none", "## Working set", "set"]) + "\n"
    _record_handoff_result(
        results, "handoff Done when missing",
        _invoke_handoff(root, target, missing), 2,
        ("## Done when", "templates/HANDOFF.md"))
    _record_handoff_result(
        results, "handoff Done when valid",
        _invoke_handoff(root, target, _handoff_text(valid)), 0)
    malformed = [
        ("zero Scope", "Authority: plan-task:T-03.verify", "has 0 Scope: lines"),
        ("two Scope", "Scope: one\nScope: two\nAuthority: plan-task:T-03.verify",
         "has 2 Scope: lines"),
        ("blank Scope", "Scope:   \nAuthority: plan-task:T-03.verify", "non-empty"),
        ("Scope after Authority", "Authority: plan-task:T-03.verify\nScope: only",
         "before every Authority"),
        ("zero Authority", "Scope: only", "has 0 Authority: lines"),
        ("five Authority", "Scope: only\n" + "\n".join(
            ["Authority: plan-task:T-03.verify"] * 5), "has 5 Authority: lines"),
        ("stray prose", valid + "\nstray prose", "stray prose"),
        ("nested heading cannot truncate",
         valid + "\n### hidden\nstray prose\nAuthority: plan-task:T-99.verify",
         "unexpected line"),
        ("duplicate heading cannot truncate",
         valid + "\n## Done when\nScope: hidden\nAuthority: plan-task:T-99.verify",
         "expected exactly 1"),
    ]
    for name, body, needle in malformed:
        _record_handoff_result(
            results, f"handoff {name}",
            _invoke_handoff(root, target, _handoff_text(body)), 2, needle)


def _handoff_pointer_cases(results, root, target):
    pointers = [
        ("plan", "plan-task:T-03.verify", "plan-task:T-99.verify"),
        ("brief", "brief-sc:SC-04", "brief-sc:SC-99"),
        ("finding",
         "finding:.harness/harness/features/FEAT-90-fixture/notes/review-fixture.md#F-02",
         "finding:.harness/harness/features/FEAT-90-fixture/notes/review-fixture.md#F-99"),
        ("approval", "approval:.harness/harness/features/FEAT-90-fixture/BRIEF.md#Approval",
         "approval:.harness/harness/features/FEAT-90-fixture/BRIEF.md#Missing"),
    ]
    for name, good, bad in pointers:
        _record_handoff_result(
            results, f"handoff {name} resolves",
            _invoke_handoff(root, target, _handoff_text(
                f"Scope: done\nAuthority: {good}")), 0)
        _record_handoff_result(
            results, f"handoff {name} unresolved",
            _invoke_handoff(root, target, _handoff_text(
                f"Scope: done\nAuthority: {bad}")), 2, bad)
    legal_prefixes = ("plan-task:", "brief-sc:", "finding:", "approval:")
    for value in ("docs:whatever", "check-domain.sh:1523"):
        _record_handoff_result(
            results, f"handoff unknown authority {value}",
            _invoke_handoff(root, target, _handoff_text(
                f"Scope: done\nAuthority: {value}")), 2, legal_prefixes)
    feat = os.path.dirname(os.path.dirname(target))
    invalid_headings = {
        "bad-nospace.md": "#Approval\n",
        "bad-seven.md": "####### Approval\n",
    }
    for name, content in invalid_headings.items():
        path = os.path.join(feat, name)
        with open(path, "w") as f:
            f.write(content)
        pointer = f"approval:{os.path.relpath(path, root)}#Approval"
        _record_handoff_result(
            results, f"handoff approval rejects invalid ATX {name}",
            _invoke_handoff(root, target, _handoff_text(
                f"Scope: done\nAuthority: {pointer}")), 2, pointer)


def _handoff_unsafe_cases(results, root, notes, target):
    for value in (
        "finding:/tmp/review.md#F-02",
        "finding:../review.md#F-02",
        "finding:.harness/harness/features/FEAT-90-fixture/notes/\x00review.md#F-02",
        "approval:/tmp/review.md#Approval",
        "approval:../review.md#Approval",
    ):
        _record_handoff_result(
            results, f"handoff unsafe authority {value!r}",
            _invoke_handoff(root, target, _handoff_text(
                f"Scope: done\nAuthority: {value}")), 2, "unsafe")
    outside = os.path.join(os.path.dirname(root), os.path.basename(root) + "-outside.md")
    with open(outside, "w") as f:
        f.write("F-02\n# Approval\n")
    escape = os.path.join(notes, "escape.md")
    os.symlink(outside, escape)
    special = os.path.join(notes, "special.md")
    os.mkfifo(special)
    for name, path in (("symlink escape", escape), ("special target", special)):
        rel_pointer = os.path.relpath(path, root)
        for kind, suffix in (("finding", "F-02"), ("approval", "Approval")):
            _record_handoff_result(
                results, f"handoff {kind} {name}",
                _invoke_handoff(root, target, _handoff_text(
                    f"Scope: done\nAuthority: {kind}:{rel_pointer}#{suffix}")),
                2, "unsafe")
    return outside


def _handoff_valid_pre_edit_cases(results, root, target, valid):
    with open(target, "w") as f:
        f.write(_handoff_text(valid))
    before = open(target, "rb").read()
    permitted_edit = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": target,
            "old_string": "Scope: build complete",
            "new_string": "Scope: build complete and verified",
        },
    }
    _record_handoff_result(
        results, "handoff valid reconstructable PRE-Edit remains allowed",
        subprocess.run(
            [HOOK], input=json.dumps(permitted_edit), capture_output=True,
            text=True, env=_env(root)),
        0)
    pre_edit = {"tool_name": "Edit",
                "tool_input": {"file_path": target,
                               "old_string": "Scope: build complete",
                               "new_string": "Scope:   "}}
    pre_result = subprocess.run(
        [HOOK], input=json.dumps(pre_edit), capture_output=True, text=True, env=_env(root))
    _record_handoff_result(
        results, "handoff pre-Edit blocks invalid candidate",
        pre_result, 2, "non-empty")
    results.append(("handoff blocked pre-Edit leaves file unchanged",
                    open(target, "rb").read() == before, "file bytes changed"))
    return before


def _handoff_invalid_utf8_pre_edit_case(results, root, target, before):
    unreadable = b"\xff\xfehandoff\n"
    with open(target, "wb") as f:
        f.write(unreadable)
    unreadable_edit = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": target,
            "old_string": "handoff",
            "new_string": "changed",
        },
    }
    try:
        unreadable_result = subprocess.run(
            [HOOK], input=json.dumps(unreadable_edit), capture_output=True,
            text=True, env=_env(root))
        combined = unreadable_result.stderr + unreadable_result.stdout
        unchanged = open(target, "rb").read() == unreadable
        results.append((
            "handoff pre-Edit unreadable existing file fails closed",
            unreadable_result.returncode == 2
            and "cannot be reconstructed" in combined.lower()
            and unchanged,
            f"exit {unreadable_result.returncode}: {combined.strip()[:180]}; "
            f"bytes unchanged: {unchanged}",
        ))
    finally:
        with open(target, "wb") as f:
            f.write(before)


def _handoff_pre_edit_cases(results, root, target, outside, valid):
    os.unlink(outside)
    before = _handoff_valid_pre_edit_cases(results, root, target, valid)
    _handoff_invalid_utf8_pre_edit_case(results, root, target, before)


def _handoff_validator_exception_case(results, root, valid):
    isolated = os.path.join(root, "isolated")
    isolated_bin = os.path.join(isolated, ".agents", "skills", "harness", "bin")
    os.makedirs(isolated_bin)
    isolated_hook = os.path.join(isolated_bin, "check-domain.sh")
    shutil.copy2(HOOK, isolated_hook)
    with open(os.path.join(isolated_bin, "handoff_done_when.py"), "w") as f:
        f.write("def problems(*args, **kwargs):\n    raise RuntimeError('injected failure')\n")
    isolated_target = os.path.join(
        isolated, ".harness", "harness", "features", "FEAT-90-fixture",
        "notes", "handoff-build.md")
    os.makedirs(os.path.dirname(isolated_target), exist_ok=True)
    isolated_payload = {
        "tool_name": "Write",
        "tool_input": {"file_path": isolated_target, "content": _handoff_text(valid)},
    }
    _record_handoff_result(
        results, "handoff validator exception fails closed",
        subprocess.run([isolated_hook], input=json.dumps(isolated_payload),
                       capture_output=True, text=True, env=_env(isolated)),
        2, ("injected failure", "REFUSING"))


def _handoff_existing_edit_cases(results, root, target, missing, valid):
    # The existing-note edit route is the post-write sweep, not a second parser.
    with open(target, "w") as f:
        f.write(missing)
    edit_payload = {"tool_name": "Edit", "hook_event_name": "PostToolUse",
                    "tool_input": {"file_path": target, "old_string": "old",
                                   "new_string": "new"}}
    _record_handoff_result(
        results, "handoff edit without Done when",
        subprocess.run([HOOK], input=json.dumps(edit_payload), capture_output=True,
                       text=True, env=_env(root)), 2, "## Done when")
    with open(target, "w") as f:
        f.write(_handoff_text(valid))
    _record_handoff_result(
        results, "handoff edit with Done when",
        subprocess.run([HOOK], input=json.dumps(edit_payload), capture_output=True,
                       text=True, env=_env(root)), 0)


def _handoff_line_cap_cases(results, root, target, valid):
    sixty = _handoff_text(valid, trust_lines=50)
    sixty_one = _handoff_text(valid, trust_lines=51)
    assert len(sixty.splitlines()) == 60 and len(sixty_one.splitlines()) == 61
    _record_handoff_result(
        results, "handoff 60-line boundary",
        _invoke_handoff(root, target, sixty), 0)
    _record_handoff_result(
        results, "handoff 61-line boundary",
        _invoke_handoff(root, target, sixty_one), 2, "cap is 60")
    _record_handoff_result(
        results, "handoff no per-section cap",
        _invoke_handoff(root, target, sixty), 0)

def _handoff_worktree_cases(results, root):
    wt_path = os.path.join(
        root, ".claude", "worktrees", "harness", "BUG-1480-wt")
    make_linked_worktree(root, wt_path, "bug1480")
    feat = os.path.join(
        wt_path, ".harness", "harness", "features", "BUG-1480-wt-fixture")
    notes = os.path.join(feat, "notes")
    os.makedirs(notes)
    with open(os.path.join(feat, "plan.yaml"), "w") as f:
        f.write("tasks:\n  - id: T-03\n    verify: python3 test.py\n")
    with open(os.path.join(feat, "BRIEF.md"), "w") as f:
        f.write("# BRIEF\n\n- SC-04: observable\n\n## Approval\n")
    target = os.path.join(notes, "handoff-build.md")
    main_feat = os.path.join(
        root, ".harness", "harness", "features", "BUG-1480-wt-fixture")
    results.append((
        "handoff worktree-only main root has no feature dir",
        not os.path.exists(main_feat), main_feat))
    _record_handoff_result(
        results, "handoff worktree-only feature dir resolves",
        _invoke_handoff(
            root, target,
            _handoff_text("Scope: build complete\nAuthority: plan-task:T-03.verify")),
        0)
    _record_handoff_result(
        results, "handoff worktree-only unresolvable pointer refused",
        _invoke_handoff(
            root, target,
            _handoff_text("Scope: build complete\nAuthority: plan-task:T-99.verify")),
        2, ("T-99",))
    _record_handoff_result(
        results, "handoff worktree-only brief-sc pointer refused",
        _invoke_handoff(
            root, target, _handoff_text("Scope: build complete\nAuthority: brief-sc:SC-99")),
        2, (
            "SC-99",
            os.path.join(
                "BUG-1480-wt", ".harness", "harness", "features",
                "BUG-1480-wt-fixture", "BRIEF.md"),
        ))


def _report_handoff_results(results):
    fails = 0
    for name, ok, detail in results:
        print(("ok   " if ok else "FAIL "), name, "" if ok else detail)
        fails += not ok
    return fails


def run_handoff_done_when():
    results = []
    with tempfile.TemporaryDirectory() as root:
        notes, target = _handoff_done_when_fixture(root)
        valid = "Scope: build complete\nAuthority: plan-task:T-03.verify"
        missing = "\n".join(["## Next", "next", "## Trust", "trust",
                             "## Dead ends", "none", "## Working set", "set"]) + "\n"
        _handoff_grammar_cases(results, root, target, valid)
        _handoff_pointer_cases(results, root, target)
        outside = _handoff_unsafe_cases(results, root, notes, target)
        _handoff_pre_edit_cases(results, root, target, outside, valid)
        _handoff_validator_exception_case(results, root, valid)
        _handoff_existing_edit_cases(results, root, target, missing, valid)
        _handoff_line_cap_cases(results, root, target, valid)
        _handoff_worktree_cases(results, root)
    return _report_handoff_results(results)


# ---------------------------------------------------------------------------
# B-2: THE HOOK'S CWD IS NOT THE PROJECT ROOT, AND A CLAIMED PATH MAY BE RELATIVE.
#
# Every case below fires the SAME payload from two working directories and asserts
# ONE verdict. That pairing is the whole point: before `_claimed_abs`, the relative
# spelling from outside the tree exited 0 on a note the gate never opened, while the
# absolute spelling refused — so a suite that fired only from the repo root, as every
# other suite in this file does, could not see either hole.
#
# TWO INDEPENDENT HOLES, and the pair below covers one each. The SHAPE phase resolved
# the claimed path with `os.path.abspath`; the DOMAIN phase handed the raw claimed path
# to `harness_boundary.classify`, whose parameter is named `abs_target` and which calls
# `real()` on it. Fixing either alone leaves the other open, which is why the domain
# case is not merely a duplicate of the shape case with a different agent.
B2_OUTSIDE_CWD = "/tmp"


def _b2_fire(payload, cwd, root):
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, cwd=cwd, env=_env(root)).returncode


def _b2_case(results, name, payload, want, root, rel_path):
    """Assert one verdict from BOTH cwds, for the absolute and relative spelling."""
    for cwd_label, cwd in (("repo root", root), ("outside", B2_OUTSIDE_CWD)):
        for spelling, path in (("absolute", os.path.join(root, rel_path)),
                               ("relative", rel_path)):
            got = _b2_fire({**payload, "tool_input": {**payload["tool_input"],
                                                      "file_path": path}}, cwd, root)
            results.append((f"{name} — {spelling} claimed path, cwd {cwd_label}",
                            got == want, f"wanted exit {want}, got {got}"))


def _b2_fixture(root):
    """A governed tree with a handoff note path and a blank-`Scope:` candidate."""
    shutil.copytree(os.path.join(ROOT, ".harness"), os.path.join(root, ".harness"),
                    ignore=shutil.ignore_patterns("worktrees", "*.lock"))
    feature = os.path.join(".harness", "harness", "features", "FEAT-B2", "notes")
    os.makedirs(os.path.join(root, feature), exist_ok=True)
    return os.path.join(feature, "handoff-validate.md").replace(os.sep, "/")


_B2_BLANK_SCOPE = "\n".join([
    "## Next", "next", "## Trust", "- a — b — verified-at 0000000",
    "## Dead ends", "- a — b — verified-at 0000000", "## Working set", "- x",
    "## Done when", "Scope:", "Authority: brief-sc:SC-01"]) + "\n"


def run_b2_cwd_independence():
    """B-2: neither phase may depend on the hook's working directory."""
    results = []
    with tempfile.TemporaryDirectory() as root:
        handoff_rel = _b2_fixture(root)
        # SHAPE phase: a blank `Scope:` is refused wherever the gate is standing.
        _b2_case(results, "blank Scope: in a handoff note",
                 {"tool_name": "Write", "agent_type": "harness-orchestrator",
                  "tool_input": {"content": _B2_BLANK_SCOPE}}, 2, root, handoff_rel)
        # DOMAIN phase: an ungranted write is refused, and a granted one is not.
        spec_rel = ".harness/harness/docs/SPEC.md"
        _b2_case(results, "ungranted agent writing harness docs",
                 {"tool_name": "Write", "agent_type": "harness-frontend-dev",
                  "tool_input": {"content": "x"}}, 2, root, spec_rel)
        _b2_case(results, "granted agent writing harness docs",
                 {"tool_name": "Write", "agent_type": "harness-documentor",
                  "tool_input": {"content": "x"}}, 0, root, spec_rel)
    fails = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    [b2] {name}")
        else:
            fails += 1
            print(f"FAIL  [b2] {name}\n      | {detail}")
    print(f"\n{len(results) - fails}/{len(results)} b2 cwd-independence cases passed.")
    return fails


def bug1304_pre_change_hook(dest):
    copied_bin = isolated_bin(dest)
    hook = os.path.join(copied_bin, "check-domain.sh")
    fixture_path = os.path.join(
        TESTS_DIR, "fixtures", "prior-check-domain.sh.fixture")
    shutil.copyfile(fixture_path, hook)
    os.chmod(hook, 0o755)
    return hook


def _bug1304_fire(root, destination, agent, hook=HOOK, tool="Write"):
    absolute = destination if os.path.isabs(destination) else os.path.join(root, destination)
    os.makedirs(os.path.dirname(absolute), exist_ok=True)
    if tool == "Edit":
        with open(absolute, "a", encoding="utf-8"):
            pass
        tool_input = {"file_path": absolute, "old_string": "before", "new_string": "after"}
    else:
        tool_input = {"file_path": absolute, "content": "after"}
    payload = {"agent_type": agent, "tool_name": tool, "tool_input": tool_input}
    return subprocess.run([hook], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


def bug1304_assert_pre_change_allows(results, name, root, destination, agent):
    isolated = tempfile.mkdtemp()
    prior = bug1304_pre_change_hook(isolated)
    allowed = _bug1304_fire(root, destination, agent, hook=prior)
    stderr = allowed.stderr or ""
    quiet = not any(marker in stderr for marker in (
        "enforcement OFF", "was not enforced", "passing through"))
    control = _bug1304_fire(
        root, ".harness/forbidden/positive-control.md", agent, hook=prior)
    results.append((
        name + " is allowed by the frozen pre-change hook",
        allowed.returncode == 0 and quiet and control.returncode == 2,
        f"allow={allowed.returncode} control={control.returncode} stderr={stderr[:160]!r}",
    ))
    shutil.rmtree(isolated, ignore_errors=True)


def _bug1304_domain_expect(results, root, agent, name, destination, want,
                           contains=None, tool="Write"):
    response = _bug1304_fire(root, destination, agent, tool=tool)
    text = response.stdout + response.stderr
    ok = response.returncode == want and (contains is None or contains in text)
    results.append((name, ok, f"exit={response.returncode} output={text[:180]!r}"))
    return response


def _bug1304_domain_context(agent, inflight_registry):
    manifest = FIXTURE_MANIFEST.replace(
        '          - { path: ".", read: true }',
        '          - { path: ".claude/worktrees/**", upsert: true }\n'
        '          - { path: ".", read: true }',
    )
    root = fixture(manifest)
    first = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-1304-A"), "A")
    second = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-1304-B"), "B")
    inflight_registry.claim(
        first, agent, "harness-product-lead", first,
        feature="FEAT-1304-A-claim-guard")
    return {
        "manifest": manifest, "root": root, "first": first, "second": second,
        "agent": agent, "main": ".harness/allowed/main.md",
    }


def _bug1304_domain_main_routes(results, context):
    root = context["root"]
    agent = context["agent"]
    first = context["first"]
    main = context["main"]
    cases = (
        ("relative main", main),
        ("absolute main", os.path.join(root, main)),
        ("sibling", os.path.join(context["second"], ".harness", "allowed", "sibling.md")),
    )
    for label, destination in cases:
        _bug1304_domain_expect(
            results, root, agent, f"{label}-checkout write is refused",
            destination, 2, first)
        bug1304_assert_pre_change_allows(
            results, label, root, destination, agent)

    _bug1304_domain_expect(
        results, root, agent, "relative held-worktree write is allowed",
        os.path.relpath(os.path.join(first, ".harness", "allowed", "own.md"), root), 0)
    _bug1304_domain_expect(
        results, root, agent, "absolute held-worktree write is allowed",
        os.path.join(first, ".harness", "allowed", "own-absolute.md"), 0)


def _bug1304_domain_unbound_routes(results, context):
    agent = context["agent"]
    root = fixture(context["manifest"])
    response = _bug1304_fire(root, context["main"], agent)
    results.append(("unbound agent remains allowed", response.returncode == 0,
                    f"exit={response.returncode}"))
    scratch = os.path.join(tempfile.mkdtemp(), "scratch.md")
    _bug1304_domain_expect(
        results, context["root"], agent, "scratch write remains allowed", scratch, 0)


def _bug1304_domain_owner_claim(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    matching = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-1304-C"), "C")
    inflight_registry.claim(
        root, agent, "harness-product-lead", root, feature="FEAT-404-no-worktree")
    destination = ".harness/allowed/unmatched.md"
    response = _bug1304_fire(root, destination, agent)
    results.append(("unresolved owner-root claim remains unbound",
                    response.returncode == 0, f"exit={response.returncode}"))
    inflight_registry.claim(
        root, agent, "harness-product-lead", root, feature="FEAT-1304-C-linked")
    _bug1304_domain_expect(
        results, root, agent, "owner-root matching claim refuses main write",
        destination, 2, matching)
    bug1304_assert_pre_change_allows(
        results, "owner-root matching claim", root, destination, agent)


def _bug1304_domain_multi_and_malformed(results, context, inflight_registry):
    agent = context["agent"]
    inflight_registry.claim(
        context["second"], agent, "harness-product-lead", context["second"],
        feature="FEAT-1304-B-claim-guard")
    _bug1304_domain_expect(
        results, context["root"], agent, "two claims still allow either held worktree",
        os.path.join(context["second"], ".harness", "allowed", "own.md"), 0)

    malformed = os.path.join(context["root"], ".claude", "worktrees", "broken")
    os.makedirs(malformed, exist_ok=True)
    with open(os.path.join(malformed, ".git"), "w", encoding="utf-8") as handle:
        handle.write("not-a-pointer\n")
    destination = os.path.join(malformed, ".harness", "allowed", "x.md")
    _bug1304_domain_expect(
        results, context["root"], agent,
        "malformed checkout pointer refuses with a nonempty claim set",
        destination, 2, context["first"])
    bug1304_assert_pre_change_allows(
        results, "malformed checkout", context["root"], destination, agent)


def _bug1304_domain_ambiguous(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT"), "AMB1")
    make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-X"), "AMB2")
    inflight_registry.claim(
        root, agent, "harness-product-lead", root, feature="FEAT-X-ambiguous")
    _bug1304_domain_expect(
        results, root, agent, "ambiguous claim refuses and names candidates",
        context["main"], 2, "FEAT, FEAT-X")
    bug1304_assert_pre_change_allows(
        results, "ambiguous claim", root, context["main"], agent)


def _bug1304_domain_short_claim(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    short = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "BUG-1304"), "SHORT")
    inflight_registry.claim(
        short, agent, "harness-product-lead", short,
        feature="BUG-1304-worktree-relative-path-guard")
    _bug1304_domain_expect(
        results, root, agent, "short-form worktree claim refuses main write",
        context["main"], 2)
    bug1304_assert_pre_change_allows(
        results, "short-form", root, context["main"], agent)


def _bug1304_domain_aged_claim(results, context, inflight_registry):
    registry = os.path.join(context["first"], inflight_registry.REGISTRY_REL)
    data = json.load(open(registry, encoding="utf-8"))
    data["claims"][0]["started_at"] = (
        __import__("time").time() - inflight_registry.CLAIM_TTL_SECONDS - 5)
    with open(registry, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    _bug1304_domain_expect(
        results, context["root"], context["agent"],
        "aged compatibility claim still refuses",
        context["main"], 2, context["first"])
    bug1304_assert_pre_change_allows(
        results, "aged claim", context["root"], context["main"], context["agent"])


def _bug1304_domain_unreadable(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    worktree = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-BAD"), "BAD")
    inflight_registry.claim(
        worktree, agent, "harness-product-lead", worktree,
        feature="FEAT-BAD-unreadable")
    registry = os.path.join(worktree, inflight_registry.REGISTRY_REL)
    with open(registry, "w", encoding="utf-8") as handle:
        handle.write("{")
    _bug1304_domain_expect(
        results, root, agent, "unreadable registry refuses and names file",
        context["main"], 2, registry)
    bug1304_assert_pre_change_allows(
        results, "unreadable registry", root, context["main"], agent)
    with open(registry, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 2, "claims": []}, handle)
    response = _bug1304_fire(root, context["main"], agent)
    results.append(("readable empty registry remains allowed",
                    response.returncode == 0, f"exit={response.returncode}"))


def _bug1304_domain_partial_registry(results, context, inflight_registry):
    agent = context["agent"]
    root = fixture(context["manifest"])
    own = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-OWN"), "OWN")
    corrupt = make_linked_worktree(
        root, os.path.join(root, ".claude", "worktrees", "FEAT-CORRUPT"), "CORRUPT")
    inflight_registry.claim(
        own, agent, "harness-product-lead", own, feature="FEAT-OWN-readable")
    registry = os.path.join(corrupt, inflight_registry.REGISTRY_REL)
    os.makedirs(os.path.dirname(registry), exist_ok=True)
    with open(registry, "w", encoding="utf-8") as handle:
        handle.write("{")
    response = _bug1304_fire(
        root, os.path.join(own, ".harness", "allowed", "inside.md"), agent)
    results.append(("readable member allows despite unrelated unreadable registry",
                    response.returncode == 0, f"exit={response.returncode}"))
    _bug1304_domain_expect(
        results, root, agent, "outside partial claim set refuses unreadable registry",
        context["main"], 2, registry)
    bug1304_assert_pre_change_allows(
        results, "partial unreadable", root, context["main"], agent)


def run_bug1304_claim_set():
    """Issue #1304 claim-set cases; frozen guard provenance: a4e8ecf7."""
    import inflight_registry

    results = []
    context = _bug1304_domain_context("harness-documentor", inflight_registry)
    _bug1304_domain_main_routes(results, context)
    _bug1304_domain_unbound_routes(results, context)
    _bug1304_domain_owner_claim(results, context, inflight_registry)
    _bug1304_domain_multi_and_malformed(results, context, inflight_registry)
    _bug1304_domain_ambiguous(results, context, inflight_registry)
    _bug1304_domain_short_claim(results, context, inflight_registry)
    _bug1304_domain_aged_claim(results, context, inflight_registry)
    _bug1304_domain_unreadable(results, context, inflight_registry)
    _bug1304_domain_partial_registry(results, context, inflight_registry)

    failures = 0
    for name, ok, detail in results:
        print(("PASS " if ok else "FAIL "), "[bug1304]", name)
        if not ok:
            failures += 1
            print("      " + detail)
    return failures


def _bug1305_marker_path(state_path):
    return os.path.join(os.path.dirname(state_path), ".run-identity.json")


def _bug1305_write_marker(state_path, run_id="A", run_uid=None):
    marker = {
        "run_id": run_id, "feature": "FEAT-S-thing", "squad": "eng",
        "host": "omp", "identity": "session", "run_uid": run_uid,
        "created_at": "2026-09-05T00:00:00+00:00",
    }
    with open(_bug1305_marker_path(state_path), "w", encoding="utf-8") as fh:
        json.dump(marker, fh)


def _bug1305_unverifiable_edit_result(name, response):
    refused = (
        response.returncode == 2
        and "run identity" in response.stderr
        and "witness" in response.stderr
        and "Write the complete file instead" in response.stderr
    )
    return name, refused, response.stderr


def _bug1305_absent_prior_edit_case():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    response = _fire_digest_edit(
        root, state, "run_id: A", "run_id: B")
    return _bug1305_unverifiable_edit_result(
        "absent-prior Edit refuses unverifiable witness identity", response)


def _bug1305_unmatched_edit_case():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(
        state, "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\n"
        "squad: eng\nhost: omp\n")
    response = _fire_digest_edit(
        root, state, "run_id: missing", "run_id: B")
    return _bug1305_unverifiable_edit_result(
        "unmatched state Edit refuses unverifiable witness identity", response)


def _bug1305_omp_edit_cases():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(
        state, "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\n"
        "squad: eng\nhost: omp\nstatus: building\n")
    payload = {"tool_name": "Edit", "tool_input": {"file_path": state}}
    response = subprocess.run(
        [HOOK], input=json.dumps(payload), capture_output=True, text=True,
        env=_env(root))
    refused = _bug1305_unverifiable_edit_result(
        "omp file-path-only state Edit fails closed", response)

    permitted = _fire_digest_edit(
        root, state, "status: building", "status: review")
    allowed = (
        "uniquely reconstructable state Edit remains allowed",
        permitted.returncode == 0,
        permitted.stderr,
    )
    return [refused, allowed]


def _bug1305_edit_reconstruction_cases():
    return [
        _bug1305_absent_prior_edit_case(),
        _bug1305_unmatched_edit_case(),
        *_bug1305_omp_edit_cases(),
    ]


def _bug1305_unreconstructable_artifact_cases(label, root, path, prior):
    absent = _fire_digest_edit(root, path, "missing", "replacement")
    _feat50_write_text(path, prior)
    unmatched = _fire_digest_edit(root, path, "missing", "replacement")
    payload = {"tool_name": "Edit", "tool_input": {"file_path": path}}
    omp_edit = subprocess.run(
        [HOOK], input=json.dumps(payload), capture_output=True, text=True,
        env=_env(root))
    results = []
    for shape, response in (
        ("absent-prior", absent),
        ("unmatched", unmatched),
        ("omp file-path-only", omp_edit),
    ):
        allowed_route = "Write the complete file instead" in response.stderr
        results.append((
            f"{label} {shape} Edit fails closed",
            response.returncode == 2 and allowed_route,
            response.stderr,
        ))
    return results


def _bug1305_nonstate_edit_reconstruction_cases():
    digest_root, digest_path = _feat50_digest_fixture()
    results = _bug1305_unreconstructable_artifact_cases(
        "digest", digest_root, digest_path, "recorded digest\n")
    with tempfile.TemporaryDirectory() as handoff_root:
        _, handoff_path = _handoff_done_when_fixture(handoff_root)
        results.extend(_bug1305_unreconstructable_artifact_cases(
            "handoff", handoff_root, handoff_path,
            _handoff_text("Scope: done\nAuthority: plan-task:T-03.verify")))
    return results


def _bug1305_marker_foreign_refusals():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    write = _bug1124_state_fire(
        root, state,
        "schema_version: 1\nrun_id: B\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n")

    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(
        state, "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n")
    edit = _fire_digest_edit(root, state, "run_id: A", "run_id: B")
    return [
        ("foreign first Write is refused by witness", write.returncode == 2
         and "Issue 1305" in write.stderr and "A" in write.stderr
         and "B" in write.stderr, write.stderr),
        ("foreign Edit is refused by witness", edit.returncode == 2
         and "Issue 1305" in edit.stderr and "A" in edit.stderr
         and "B" in edit.stderr, edit.stderr),
    ]


def _bug1305_marker_witness_precedence():
    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(state, "{")
    unparseable = _bug1124_state_fire(root, state, "schema_version: 1\nrun_id: B\n")

    root, state = _bug1124_state_fixture()
    _bug1305_write_marker(state)
    _feat50_write_text(state, "schema_version: 1\nrun_id: A\n")
    legacy = _bug1124_state_fire(root, state, "schema_version: 1\nrun_id: B\n")
    return [
        ("witness outranks an unparseable prior", unparseable.returncode == 2
         and "Issue 1305" in unparseable.stderr
         and "does not parse" not in unparseable.stderr, unparseable.stderr),
        ("witness outranks legacy run_id ladder", legacy.returncode == 2
         and "Issue 1305" in legacy.stderr
         and "Issue 1124" not in legacy.stderr, legacy.stderr),
    ]


def _bug1305_marker_recovery_cases():
    results = []
    for label, prior in (("absent", None), ("zero-byte", "")):
        root, state = _bug1124_state_fixture()
        _bug1305_write_marker(state)
        if prior is not None:
            _feat50_write_text(state, prior)
        response = _bug1124_state_fire(
            root, state,
            "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n")
        results.append((
            f"recovering owner with {label} prior is allowed",
            response.returncode == 0, response.stderr))

    root, state = _bug1124_state_fixture()
    with open(_bug1305_marker_path(state), "w", encoding="utf-8") as fh:
        fh.write("{")
    response = _bug1124_state_fire(root, state, "schema_version: 1\nrun_id: A\n")
    results.append((
        "unreadable witness fails closed", response.returncode == 2
        and "cannot be read" in response.stderr
        and "Issue 1305" in response.stderr, response.stderr))
    return results


def _bug1305_marker_file_protection():
    root, state = _bug1124_state_fixture()
    identity = _bug1305_marker_path(state)
    with open(identity, "w", encoding="utf-8") as fh:
        fh.write("{}\n")
    write = _bug1124_state_fire(root, identity, '{"run_id": "forged"}\n')
    edit = _fire_digest_edit(root, identity, "{}", '{"run_id": "forged"}')
    unmatched_edit = _fire_digest_edit(
        root, identity, "not present", '{"run_id": "forged"}')
    legal = _bug1124_state_fire(
        root, state, "schema_version: 1\nrun_id: A\nrun_uid: U\n")
    os.unlink(identity)
    create = _bug1124_state_fire(root, identity, '{"run_id": "forged"}\n')
    create_edit = _fire_digest_edit(
        root, identity, "not present", '{"run_id": "forged"}')
    return [
        ("Write of existing witness is refused", write.returncode == 2
         and "identity witness" in write.stderr, write.stderr),
        ("Edit of existing witness is refused", edit.returncode == 2
         and "identity witness" in edit.stderr, edit.stderr),
        ("unmatched Edit of existing witness is refused",
         unmatched_edit.returncode == 2
         and "identity witness" in unmatched_edit.stderr, unmatched_edit.stderr),
        ("run_uid is a legal checkpoint key beside identity witness",
         legal.returncode == 0, legal.stderr),
        ("Write creating false witness is refused", create.returncode == 2
         and "identity witness" in create.stderr, create.stderr),
        ("Edit creating false witness is refused", create_edit.returncode == 2
         and "identity witness" in create_edit.stderr, create_edit.stderr),
    ]


def _bug1305_post_landing(root, state):
    payload = {
        "tool_name": "Write", "hook_event_name": "PostToolUse",
        "tool_input": {"file_path": state},
    }
    response = fire_post(root, payload)
    after_first = open(state, "rb").read()
    marker_path = _bug1305_marker_path(state)
    marker_first = open(marker_path, "rb").read() if os.path.isfile(marker_path) else b""
    parsed = yaml.safe_load(after_first.decode("utf-8"))
    marker_doc = json.loads(marker_first) if marker_first else {}
    uid = parsed.get("run_uid") if isinstance(parsed, dict) else None
    return response, payload, after_first, marker_first, marker_doc, uid


def _bug1305_marker_post_mint_cases():
    root, state = _bug1124_state_fixture()
    landed = "schema_version: 1\nrun_id: A\nfeature: FEAT-S-thing\nsquad: eng\nhost: omp\n"
    _feat50_write_text(state, landed)
    response, payload, after_first, marker_first, marker_doc, uid = (
        _bug1305_post_landing(root, state))
    fire_post(root, payload)
    marker_path = _bug1305_marker_path(state)
    marker_second = open(marker_path, "rb").read() if os.path.isfile(marker_path) else b""
    return [
        ("POST mints uid and matching witness", response.returncode == 0
         and re.fullmatch(r"[0-9a-f]{32}", str(uid or ""))
         and marker_doc.get("run_uid") == uid, response.stderr),
        ("second POST is byte stable", open(state, "rb").read() == after_first
         and marker_second == marker_first and bool(marker_first), ""),
    ]


def _bug1305_marker_post_preservation_cases():
    root, state = _bug1124_state_fixture()
    explicit = "schema_version: 1\nrun_id: A\nrun_uid: fixed\n"
    _feat50_write_text(state, explicit)
    before = open(state, "rb").read()
    fire_post(root, {
        "tool_name": "Write", "hook_event_name": "PostToolUse",
        "tool_input": {"file_path": state},
    })
    preserved = open(state, "rb").read() == before

    root, state = _bug1124_state_fixture()
    _feat50_write_text(state, "{")
    fire_post(root, {
        "tool_name": "Write", "hook_event_name": "PostToolUse",
        "tool_input": {"file_path": state},
    })
    malformed = (
        open(state, encoding="utf-8").read() == "{"
        and not os.path.exists(_bug1305_marker_path(state)))
    return [
        ("POST preserves supplied uid bytes", preserved, ""),
        ("POST leaves malformed checkpoint untouched", malformed, ""),
    ]


def run_bug1305_marker_cases():
    """BUG-1305 SC-01/10: guard, seed-field precedence, and POST minting."""
    results = (
        _bug1305_edit_reconstruction_cases()
        + _bug1305_nonstate_edit_reconstruction_cases()
        + _bug1305_marker_foreign_refusals()
        + _bug1305_marker_witness_precedence()
        + _bug1305_marker_recovery_cases()
        + _bug1305_marker_file_protection()
        + _bug1305_marker_post_mint_cases()
        + _bug1305_marker_post_preservation_cases()
    )
    failures = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    [bug1305] {name}")
        else:
            failures += 1
            print(f"FAIL  [bug1305] {name}\n      | {str(detail).strip()[:300]}")
    print(f"\n{len(results) - failures}/{len(results)} BUG-1305 marker cases passed.")
    return failures


def _bug1305_identity_doc(run_id="A", run_uid=None, include_uid=True):
    text = (
        f"schema_version: 1\nrun_id: {run_id}\nfeature: FEAT-S-thing\n"
        "squad: eng\nhost: omp\nstatus: building\n")
    if include_uid and run_uid is not None:
        text += f"run_uid: {run_uid}\n"
    return text


def _bug1305_write_identity_marker(state, run_id="A", run_uid="U1"):
    marker = {
        "run_id": run_id, "feature": "FEAT-S-thing", "squad": "eng",
        "host": "omp", "identity": "session", "run_uid": run_uid,
        "created_at": "2026-09-05T00:00:00+00:00",
    }
    with open(os.path.join(os.path.dirname(state), ".run-identity.json"),
              "w", encoding="utf-8") as handle:
        json.dump(marker, handle)


def _bug1305_identity_write(prior, incoming, marker=False, session_id=None):
    root, state = _bug1124_state_fixture()
    if prior is not None:
        _feat50_write_text(state, prior)
    if marker:
        _bug1305_write_identity_marker(state)
    payload = {"tool_name": "Write",
               "tool_input": {"file_path": state, "content": incoming}}
    if session_id is not None:
        payload["session_id"] = session_id
    return subprocess.run(
        [HOOK], input=json.dumps(payload), capture_output=True, text=True,
        env=_env(root))


def _bug1305_identity_edit(new_string=""):
    root, state = _bug1124_state_fixture()
    _feat50_write_text(state, _bug1305_identity_doc(run_uid="U1"))
    payload = {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": state, "old_string": "run_uid: U1\n", "new_string": new_string,
        },
    }
    return subprocess.run(
        [HOOK], input=json.dumps(payload), capture_output=True, text=True,
        env=_env(root))


def _bug1305_identity_refusal_cases():
    prior = _bug1305_identity_doc(run_uid="U1")
    missing = _bug1305_identity_write(
        prior, _bug1305_identity_doc(include_uid=False))
    edit = _bug1305_identity_edit()
    different_edit = _bug1305_identity_edit("run_uid: U2\n")
    different = _bug1305_identity_write(
        prior, _bug1305_identity_doc(run_uid="U2"))
    precedence = _bug1305_identity_write(
        prior, _bug1305_identity_doc(run_id="B", run_uid="U1"), marker=True)
    return [
        ("modal collision Write omitting uid is refused",
         missing.returncode == 2 and "U1" in missing.stderr
         and "run identity" in missing.stderr and "field disagreement" not in missing.stderr,
         missing.stderr),
        ("modal collision Edit removing uid is refused",
         edit.returncode == 2 and "U1" in edit.stderr
         and "run identity" in edit.stderr
         and "field disagreement" not in edit.stderr, edit.stderr),
        ("different minted uid is refused",
         different.returncode == 2 and "U1" in different.stderr
         and "U2" in different.stderr, different.stderr),
        ("different minted uid Edit is refused",
         different_edit.returncode == 2 and "U1" in different_edit.stderr
         and "U2" in different_edit.stderr, different_edit.stderr),
        ("run_id disagreement keeps Issue 1124 precedence",
         precedence.returncode == 2 and "Issue #1124" in precedence.stderr
         and "Issue 1305" not in precedence.stderr, precedence.stderr),
    ]


def _bug1305_identity_allow_cases():
    prior = _bug1305_identity_doc(run_uid="U1")
    incoming = _bug1305_identity_doc(run_uid="U1")
    resumed = _bug1305_identity_write(prior, incoming, session_id="S2")
    # D-01 forbids session-keyed ownership: this same-uid S2 update catches it.
    absent = _bug1305_identity_write(
        None, _bug1305_identity_doc(include_uid=False), marker=True)
    zeroed = _bug1305_identity_write(
        "", _bug1305_identity_doc(include_uid=False), marker=True)
    legacy = _bug1305_identity_doc(include_uid=False)
    legacy_same = _bug1305_identity_write(legacy, legacy)
    legacy_new = _bug1305_identity_write(
        legacy, _bug1305_identity_doc(run_uid="U2"))
    return [
        ("DEC-154 resumed owner with same uid remains allowed across sessions",
         resumed.returncode == 0, resumed.stderr),
        ("recovering owner with absent checkpoint remains allowed",
         absent.returncode == 0, absent.stderr),
        ("recovering owner with zero-byte checkpoint remains allowed",
         zeroed.returncode == 0, zeroed.stderr),
        ("legacy checkpoint without uid remains allowed",
         legacy_same.returncode == 0, legacy_same.stderr),
        ("legacy checkpoint accepts incoming uid",
         legacy_new.returncode == 0, legacy_new.stderr),
    ]


def run_bug1305_identity_cases():
    """BUG-1305 SC-01: prior checkpoint uid owns resumed-write admission."""
    results = _bug1305_identity_refusal_cases() + _bug1305_identity_allow_cases()
    failures = 0
    for name, ok, detail in results:
        if ok:
            print(f"ok    [bug1305-identity] {name}")
        else:
            failures += 1
            print(f"FAIL  [bug1305-identity] {name}\n      | {str(detail).strip()[:300]}")
    print(f"\n{len(results) - failures}/{len(results)} BUG-1305 identity cases passed.")
    return failures


def run_bug1305_cases():
    return (
        run_bug1305_digest_repair_cases()
        + run_bug1305_marker_cases()
        + run_bug1305_identity_cases()
    )


def main():
    fails = 0
    for name, path, want, agent, tool in CASES:
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
    print(f"\n{len(CASES) - fails}/{len(CASES)} cases passed.\n")
    # EACH `fails +=` IS ITSELF THE REACHABILITY OF ITS BLOCK. Dropping seven characters
    # from any one of these leaves the block running and printing while its result is
    # discarded — the suite goes green with the cases visibly FAILing on screen. The
    # aggregate below is asserted non-negative so the shape of this line stays deliberate.
    fails += run_t12()
    fails += run_fleet()
    fails += run_resolve()
    fails += run_post()
    fails += run_schema()
    fails += run_worktree()
    fails += run_worktree_grant_parity()
    fails += run_worktree_deep_shape()
    fails += run_sweep_clean_tracked()
    fails += run_runs_agent_write_path()
    fails += run_t14()
    fails += run_feat50_artifact_integrity()
    fails += run_bug895_wrong_checkout_cases()
    fails += run_t09()
    fails += run_feat51_orphan_write()
    fails += run_bug1106_edit_route_cases()
    fails += run_bug1106_shared_pattern_consistency()
    fails += run_handoff_done_when()
    fails += run_b2_cwd_independence()
    fails += run_bug1304_claim_set()
    return fails + run_bug1305_cases()


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
