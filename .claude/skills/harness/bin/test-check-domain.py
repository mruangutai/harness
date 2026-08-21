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
case("documentor writing the moved harness docs", f"{ROOT}/.harness/harness/docs/guide.md", 0)
case("documentor writing its own expertise",
     f"{ROOT}/.harness/expertise/harness-documentor.md", 0)
# EXPECTATION CHANGED by FEAT-15 T-02, and it is the only one in this file that moved.
# All eight entries in the manifest's `shared:` block are dependency manifests and
# lockfiles — package.json, pyproject.toml, uv.lock and the rest. None has a
# control-plane first segment and none is among the four named harness entries, so in
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
case("documentor may not write bin/", f"{ROOT}/.claude/skills/harness/bin/x.py", 2)
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
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=iso))
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
        env = dict(os.environ, CLAUDE_PROJECT_DIR=root, PYTHONPATH=fake,
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
        env=dict(os.environ, CLAUDE_PROJECT_DIR=none_root))

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
            env=dict(os.environ, CLAUDE_PROJECT_DIR=root))

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

    # ---- T-03: the mirror image, both directions, and the four named entries ----
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

    # PAIR C — THE FOUR NAMED ENTRIES, which are the only paths that resolve in BOTH
    # bases, and the only place the PRODUCT side of the operator's ruling is checked at
    # all. The routing measurement behind the ruling models in-harness resolution only
    # and is structurally blind to a product-side regression.
    #
    # Its own manifest, because neither of the two above carries these globs. Two
    # personas: one holds docs/** and README.md, the other .github/**.
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
      - name: harness-dev-ops
        domain:
          - { path: .github/**, upsert: true }
""", two_base_fleet_for(ws_c))
    DOC, OPS = "harness-documentor", "harness-dev-ops"
    c_h_docs = fire_abs(c_root, os.path.join(c_root, ".harness", "harness", "docs", "guide.md"), DOC)
    c_h_prin = fire_abs(c_root, os.path.join(c_root, "docs", "PRINCIPLES.md"), DOC)
    c_h_read = fire_abs(c_root, os.path.join(c_root, "README.md"), DOC)
    c_h_gh = fire_abs(c_root, os.path.join(c_root, ".github", "workflows", "tests.yml"), OPS)
    fleet_case(
        "C harness base: all four named entries resolve — .harness/*/docs/**, "
        "docs/PRINCIPLES.md, README.md, .github/**",
        all(r.returncode == 0 for r in (c_h_docs, c_h_prin, c_h_read, c_h_gh)),
        f".harness/*/docs {c_h_docs.returncode}, PRINCIPLES {c_h_prin.returncode}, "
        f"README {c_h_read.returncode}, .github {c_h_gh.returncode} (all want 0)")

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
    fleet_case(
        "C product base: a product checkout keeps its OWN README.md, docs/ and .github/ "
        "— the named entries are target-side only and must not refuse them",
        all(r.returncode == 0 for r in (c_p_read, c_p_docs, c_p_gh)),
        f"README {c_p_read.returncode}, docs/guide.md {c_p_docs.returncode}, "
        f".github {c_p_gh.returncode} (all want 0)")

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
                              env=dict(os.environ, CLAUDE_PROJECT_DIR=root))

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
                            timeout=20, env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
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
                           timeout=timeout, env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT), **kw)
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
    r = resolve(".claude/skills/harness/bin/run-unit-tests.sh")
    check("(b) --resolve: a doubly-granted path returns both grantees",
          sorted(r.stdout.split()) == ["harness-backend-dev", "harness-dev-ops"],
          f"got {r.stdout.split()!r}")

    # (c) NOBODY is a LITERAL EMITTED TOKEN, not silence
    r_nobody = resolve(".claude/skills/harness-spec-driven/SKILL.md")
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
                              text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT))
    r = hook(".claude/skills/harness/bin/check-domain.sh", "harness-documentor")
    check("(g) no --resolve: an out-of-domain Write still exits 2",
          r.returncode == 2, f"got {r.returncode}")
    r = hook(".harness/harness/docs/SPEC.md", "harness-documentor")
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
                              text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=ROOT,
                                                  HARNESS_RESOLVE_PATH=resolve_value))
    # EXIT 2 ALONE IS NOT ENOUGH, and the delta review caught this. There are five distinct
    # exit-2 sites in this script and FOUR of them are inside the resolve branch (missing
    # manifest, duplicate key, parse error, unreadable root). A reimplementation that still
    # leaked the env var but happened to exit 2 from one of those would pass a returncode-only
    # assertion while VF-1 was wide open. Assert the DENIAL TEXT, which only the hook path
    # emits — the same convention cases (c)/(d) already use.
    def denied(r):
        return r.returncode == 2 and "may not write" in (r.stderr or "")
    r = hook_env(".claude/skills/harness/bin/check-domain.sh", "harness-documentor",
                 ".harness/harness.json")
    check("(i) VF-1: HARNESS_RESOLVE_PATH set in the env does NOT disable the hook",
          denied(r), f"got {r.returncode}, stderr={r.stderr!r}")
    r = hook_env(".claude/skills/harness/bin/check-domain.sh", "harness-documentor", "")
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
                          text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=root))



def _legal_feature_json(nlines):
    """A schema-clean eleven-key feature.json padded to exactly `nlines` lines.

    T-06 put the schema on this path, so any fixture judged on its LINE COUNT must be
    schema-clean or it is denied for a reason its case never named — a green-looking test
    asserting the wrong cause. Trailing whitespace is insignificant to a JSON parser, so
    padding this way changes the line count and nothing else.
    """
    import json as _json
    body = _json.dumps({"feature_id": "FEAT-X", "branch": "none", "pr": None,
                        "status": "Building", "review_sha": "none", "cycles_used": 0,
                        "max_total_cycles": 10, "runs": []}, indent=2).splitlines()
    return "\n".join(body + [""] * max(0, nlines - len(body))) + "\n"


def run_post():
    d = fixture(FIXTURE_MANIFEST)
    fdir = os.path.join(d, ".harness", "harness", "features", "FEAT-X")
    os.makedirs(fdir)
    fy = os.path.join(fdir, "feature.json")
    rel_fy = ".harness/harness/features/FEAT-X/feature.json"

    def write(nlines):
        # A LEGAL eleven-key document, padded with blank lines to an exact length.
        # T-06 put the schema on this path, so a fixture meant to be judged on its LINE
        # COUNT must be schema-clean or it is denied for a reason its case never intended
        # — a green-looking test asserting the wrong cause. Trailing whitespace is
        # insignificant to a JSON parser, so padding this way changes the line count and
        # nothing else.
        import json as _json
        doc = _json.dumps({"feature_id": "FEAT-X", "branch": "none", "pr": None,
                           "status": "Building", "review_sha": "none", "cycles_used": 0,
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
        capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=d))
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
        capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=d))
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
         "schema_version: 1\nfindings: a notebook entry\n", "non-checkpoint top-level key"),
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
            capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=d))
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
        capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=d))
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

    # --- THE RACE, ASSERTED AS A PROPERTY (review HIGH-1). Round 2's stamp advanced to the
    # moment the sweep FINISHED, so a file another agent wrote DURING the walk landed before
    # the new mark and was reported by nobody — reproduced 40/40 at a 40 ms offset, and
    # PERMANENT, because the stamp is global and shared. Worse than the repeat-reporting it
    # replaced.
    #
    # A first draft of this case tried to stage the race with a backdated mtime and PASSED
    # AGAINST THE DEFECT — the backdate was relative to the previous sweep's mark, which is
    # exactly the quantity the bug moves, so both versions found the file. Assert the
    # invariant itself instead: THE MARK IS THE SWEEP'S START. Padding makes the walk long
    # enough that start and finish are far apart, which is what gives the assertion teeth.
    _pad = os.path.join(fdir, "runs")
    for _i in range(800):
        _rd = os.path.join(_pad, f"pad{_i}")
        os.makedirs(_rd, exist_ok=True)
        with open(os.path.join(_rd, "state.yaml"), "w") as f:
            f.write("schema_version: 1\nrun_id: pad\nstatus: complete\n")
    write(10)
    fire_post(d, bash_payload)                        # settle: nothing fresh

    # INTERPRETER START-UP IS MEASURED AND SUBTRACTED, because it dominates. `_now` is
    # captured inside the Python body, so wall-clock from process launch to the stamp
    # includes ~38 ms of start-up that has nothing to do with the walk. A first draft
    # compared the mark against total process time and FAILED on correct code, reporting a
    # 37 ms offset against a 53 ms total — measuring start-up, not the race window.
    _t0i = time.time()
    fire_post(d, bash_payload)                        # idle: start-up only
    _idle = time.time() - _t0i

    for _i in range(800):                             # make every pad file fresh again
        os.utime(os.path.join(_pad, f"pad{_i}", "state.yaml"), None)
    _t0 = time.time()
    fire_post(d, bash_payload)
    _loaded = time.time() - _t0
    _mark = os.stat(os.path.join(d, ".harness", ".shape-sweep-stamp")).st_mtime
    _walk = _loaded - _idle                           # the part that is actually the sweep
    _offset = _mark - _t0                             # where the mark landed in the process
    # Start-stamping puts the mark at ~_idle; end-stamping puts it at ~_idle + _walk.
    # IS THE MARK NEARER THE START OF THE WALK OR ITS END? A fixed threshold discriminated
    # by one millisecond and was luck, not a test; this compares the two hypotheses directly.
    ok_mark = _walk > 0.015 and abs(_offset - _idle) < abs(_offset - _loaded)
    post("the mark records the sweep's START, not its finish (the race window)",
         ok_mark,
         f"start-up {_idle*1000:.0f} ms, walk {_walk*1000:.0f} ms, mark at "
         f"{_offset*1000:.0f} ms — distance to start {abs(_offset-_idle)*1000:.0f} ms vs "
         f"to finish {abs(_offset-_loaded)*1000:.0f} ms (a walk under 15 ms means the case "
         f"proved nothing and fails on purpose)")
    for _i in range(800):
        shutil.rmtree(os.path.join(_pad, f"pad{_i}"), ignore_errors=True)

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


def run_schema():
    """The write-time schema gate on feature.json, and the fail-open it used to have.

    The manifest GRANTS the path deliberately. Without that grant every case here exits 2
    for a DOMAIN reason and the schema phase is never reached — three green cases proving
    nothing, which is the vacuous shape this feature kept turning up.

    Case 3 is the regression. `except ImportError:` alone let any OTHER exception out of
    problems_for_text escape the hook: measured before the fix, an ILLEGAL document exited
    **1 with a traceback** instead of 2, and exit 1 is NON-BLOCKING (line 14), so the bad
    write landed. A schema loader raises far more than ImportError — a malformed
    feature-schema.json is JSONDecodeError, an unreadable one OSError, a jsonschema
    version drift SchemaError — and every one of them meant "written anyway".
    """
    import shutil
    fails = 0
    root = fixture(SCHEMA_MANIFEST)
    os.makedirs(os.path.join(root, ".harness", "harness", "features", "FEAT-X"), exist_ok=True)
    rel = ".harness/harness/features/FEAT-X/feature.json"
    legal = _legal_feature_json(0)
    illegal = json.dumps({"feature_id": "FEAT-X", "invented_key": 1}, indent=2)

    def case(name, got, want, extra_ok=True, detail=""):
        nonlocal fails
        ok = got == want and extra_ok
        if not ok:
            fails += 1
            print(f"FAIL  schema/{name}\n        wanted exit {want}, got {got}. {detail}")
        else:
            print(f"ok    schema/{name}")

    r = fire(root, rel, content=legal)
    case("a legal eleven-key document is ALLOWED", r.returncode, 0,
         detail=" ".join((r.stderr or "").split())[:160])

    r = fire(root, rel, content=illegal)
    case("an illegal document is DENIED and the offending key is NAMED", r.returncode, 2,
         "invented_key" in r.stderr,
         detail="stderr did not name invented_key: " + " ".join((r.stderr or "").split())[:160])

    # Case 3: break the checker itself. Restored byte-identically, and the restore is
    # ASSERTED — a probe that silently failed to restore would leave the tree mutated and
    # every later case measuring the wrong file.
    fs = os.path.join(os.path.dirname(os.path.realpath(__file__)), "feature_schema.py")
    before = open(fs, "rb").read()
    try:
        src = before.decode()
        marker = "def problems_for_text("
        i = src.index(marker)
        j = src.index("\n", src.index(":", src.index(")", i)))
        open(fs, "w").write(src[:j + 1] + '    raise ValueError("injected: checker is broken")\n' + src[j + 1:])
        r = fire(root, rel, content=illegal)
        case("a CRASHING schema module DENIES the write rather than letting it through",
             r.returncode, 2, "CRASHED" in r.stderr,
             detail="fail-open: exit 1 is non-blocking, so this write would have landed. "
                    + " ".join((r.stderr or "").split())[:160])
    finally:
        with open(fs, "wb") as f:
            f.write(before)
    if open(fs, "rb").read() != before:
        fails += 1
        print("FAIL  schema/probe restored feature_schema.py byte-identically")
    else:
        print("ok    schema/probe restored feature_schema.py byte-identically")
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
                              env=dict(os.environ, CLAUDE_PROJECT_DIR=session_root))

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
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=iso))
    wt("a MISSING harness_boundary.py blocks the write and NAMES the module",
       r.returncode == 2 and "harness_boundary" in r.stderr,
       f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # The other half: without it the case above is satisfied by a guard that blocks
    # everything. The manifest is removed, so DEC-101's deliberate fail-open must still
    # fire — the module being absent must not convert it into a refusal.
    os.remove(os.path.join(iso, ".harness", "team-config.yaml"))
    r = subprocess.run([os.path.join(isobin, "check-domain.sh")], input=json.dumps(payload),
                       capture_output=True, text=True,
                       env=dict(os.environ, CLAUDE_PROJECT_DIR=iso))
    wt("with the module absent AND no manifest, DEC-101 still fails OPEN, loudly",
       r.returncode == 0 and "enforcement OFF" in r.stderr,
       f"exit {r.returncode}: {r.stderr.strip()[:200]}")

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
       an agent whose first entry is product code — `src/**`, `docs/**`, `tests/**`,
       `web/src/**`, `supabase/migrations/**` — resolves to NOBODY at BOTH paths.
       Measured directly before writing this: `src/zz/zz/main.py` and
       `.claude/worktrees/wt1/src/zz/zz/main.py` both return NOBODY. Two equal EMPTY
       sets, which is exactly the vacuity this test exists to exclude. The first entry
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
                           env=dict(os.environ, CLAUDE_PROJECT_DIR=root))
        return set(r.stdout.split())

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
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
