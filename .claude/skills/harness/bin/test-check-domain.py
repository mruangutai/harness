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
import time

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
    sp2 = ".harness/features/FEAT-01/runs/r1/state.yaml"
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
    r4 = fire(root, "allowed/d.md")
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
    r = hook("docs/harness/SPEC.md", "harness-documentor")
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


def run_post():
    d = fixture(FIXTURE_MANIFEST)
    fdir = os.path.join(d, ".harness", "features", "FEAT-X")
    os.makedirs(fdir)
    fy = os.path.join(fdir, "feature.yaml")
    rel_fy = ".harness/features/FEAT-X/feature.yaml"

    def write(nlines):
        with open(fy, "w") as f:
            f.write("\n".join(f"k{i}: v" for i in range(nlines)) + "\n")

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
         r.returncode == 2 and "budget is 200" in r.stderr,
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
         "budget is 200" not in pre.stderr,
         f"exit {pre.returncode}: {pre.stderr.strip()[:120]}")

    # --- ROUTE 3: Bash. No file_path in the payload at all, so this exercises the sweep.
    r = fire_post(d, bash_payload)
    post("route 3 — post Bash sweeps and finds the over-budget file",
         r.returncode == 2 and "budget is 200" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip().splitlines()[:1]}")

    # --- ROUTE 4: the MAIN SESSION, which has no agent_type and was exempted from the
    # shape gate by the DOMAIN carve-out sitting above it.
    r = subprocess.run([HOOK], input=json.dumps({
        "tool_name": "Write",
        "tool_input": {"file_path": fy, "content": "\n".join(["x: 1"] * 400)}}),
        capture_output=True, text=True, env=dict(os.environ, CLAUDE_PROJECT_DIR=d))
    post("route 4 — the MAIN SESSION is no longer exempt from the shape gate",
         r.returncode == 2 and "budget is 200" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip().splitlines()[:1]}")

    # --- THE ENFORCED BUDGET, AT ITS BOUNDARY (review F-02). 400-vs-10 passes against
    # `> 250` and `> 350` and against every `>` flipped to `>=`, because nothing between
    # 200 and 400 is ever probed. Cross each budget by exactly ONE line, in both
    # directions, so the comparison itself is bound and not merely the message text.
    for _n, _want in ((201, True), (200, False)):
        write(_n)
        r = fire_post(d, edit_payload())
        post(f"feature.yaml at {_n} lines {'IS' if _want else 'is NOT'} over the 200 budget",
             (r.returncode == 2 and "budget is 200" in r.stderr) == _want,
             f"exit {r.returncode}: {r.stderr.strip()[:100]}")

    # The COMMENT budget is a second, independent number in the same branch — a fixture
    # that only ever crosses the line budget leaves it entirely unbound.
    for _c, _want in ((21, True), (20, False)):
        with open(fy, "w") as f:
            f.write("\n".join(["# c"] * _c + ["k: v"] * 5) + "\n")
        r = fire_post(d, edit_payload())
        post(f"feature.yaml with {_c} comment lines {'IS' if _want else 'is NOT'} over 20",
             (r.returncode == 2 and "budget is 20" in r.stderr) == _want,
             f"exit {r.returncode}: {r.stderr.strip()[:100]}")

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
    wt = os.path.join(d, ".claude", "worktrees", "wt1", ".harness", "features", "FEAT-W")
    os.makedirs(wt, exist_ok=True)
    write(10)
    fire_post(d, bash_payload)                      # advance the stamp past everything
    r0 = fire_post(d, bash_payload)                 # nothing fresh -> silence
    with open(os.path.join(wt, "feature.yaml"), "w") as f:
        f.write("\n".join(f"k{i}: v" for i in range(400)) + "\n")
    r1 = fire_post(d, bash_payload)
    post("the sweep reaches a file inside .claude/worktrees/ (and was silent before it)",
         r0.returncode == 0 and r1.returncode == 2 and "budget is 200" in r1.stderr,
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
         r.returncode == 2 and "budget is 200" in r.stderr, f"exit {r.returncode}")

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
             r.returncode == 2 and "budget is 200" in r.stderr,
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
         r.returncode == 2 and "budget is 200" in r.stderr,
         f"exit {r.returncode}: {r.stderr.strip()[:120]}")

    # --- TWO SIGNALS, EITHER SUFFICIENT. The platform's hook_event_name alone must work,
    # or a registration that omits the flag silently degrades to pre-mode.
    r = fire_post(d, edit_payload(), flag=None)
    post("hook_event_name alone selects post mode (no --post flag)",
         r.returncode == 2 and "budget is 200" in r.stderr,
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
    fails += run_resolve()
    fails += run_post()
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
