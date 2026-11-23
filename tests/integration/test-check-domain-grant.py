#!/usr/bin/env python3
"""check-domain.py: the domain grant path and the manifest that feeds it.

Slice of the former test-check-domain.py (issue #1527) — the live-repo grant cases,
T-12's manifest parsing, FEAT-15's fleet/base resolution, `--resolve`, and the
feature-schema crash controls. Siblings: test-check-domain-worktree.py,
-worktree-parity.py, -post.py, -approval.py, -artifact.py. Shared fixtures and the
block driver live in check_domain_support.py, which also carries the family's WHY.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json, os, re, shutil, subprocess, sys, tempfile
from isolated_bin import isolated_bin
from check_domain_support import (FIXTURE_MANIFEST, HERE, HOOK, ROOT, _env,
    _legal_feature_json, _run_block_captured, drive, fire, fixture, fixture_fleet,
    make_linked_worktree)
import inflight_registry


_anchor_sys.path.insert(0, _anchor_bin)


sys.path.insert(0, HERE)


CASES = []


def case(name, path, want, agent="harness-documentor", tool="Write"):
    CASES.append((name, path, want, agent, tool))


# ---------------- MUST PASS: outside the repo is not a domain question --------
# bash-write-guard.py:211 already says so ("outside repo — not this hook's
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


T12 = []


def t12(name, ok, detail=""):
    T12.append((name, ok, detail))


def _t12_sc05_pair():
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


# FAIL CLOSED on a malformed manifest (user ruling, 2026-08-03). NOT the absent-manifest
# case, which still fails OPEN: an unconfigured project has nothing to enforce, whereas
# this project IS configured and one action fixes it. No deadlock — the manifest is in no
# agent's domain and the main session is exempt, so the only party who can repair it is
# the one this guard never governs. A duplicate key in the RULEBOOK: which of two domain
# lists wins is not a thing to guess at while holding a write guard.
BAD_MANIFESTS = (
    ("a MALFORMED manifest blocks the write (fail closed, not half-enforced)",
     'teams: [ {name: x ## eaten\nnext_key: 1\n', "does not parse"),
    ("a DUPLICATE key in the manifest blocks the write",
     FIXTURE_MANIFEST + "\nshared:\n  - { path: other.json }\n", "duplicate key"),
)


def _t12_bad_manifests_fail_closed():
    for label, manifest, needle in BAD_MANIFESTS:
        r = fire(fixture(manifest), "allowed/thing.md")
        t12(label, r.returncode == 2 and needle in r.stderr,
            f"exit {r.returncode}: {r.stderr.strip()[:160]}")


def _t12_absent_manifest_fails_open():
    # The manifest still ABSENT fails OPEN, loudly — DEC-101 unchanged. Asserted so
    # the new fail-closed paths cannot quietly swallow this deliberate carve-out.
    #
    # This needs an ISOLATED COPY of the hook, not merely an empty project-root override:
    # `root` falls back to `_derived`, computed from BASH_SOURCE, so a hook running
    # from the real bin/ finds the REAL manifest no matter what the env var says. A
    # first draft of this case pointed the env var at an empty dir, got exit 0, and
    # passed — but the 0 came from "outside repo, not this hook's problem" and the
    # absent-manifest branch never ran. Vacuous, and it looked green.
    iso = tempfile.mkdtemp()
    isobin = os.path.join(iso, ".claude", "skills", "harness", "bin")
    os.makedirs(isobin)
    shutil.copy(HOOK, os.path.join(isobin, "check-domain.py"))
    shutil.copy(
        os.path.join(HERE, "artifact_accessors.py"),
        os.path.join(isobin, "artifact_accessors.py"))
    payload = {"agent_type": "harness-documentor", "tool_name": "Write",
               "tool_input": {"file_path": os.path.join(iso, "anything.md"), "content": "x"}}
    r = subprocess.run([os.path.join(isobin, "check-domain.py")], input=json.dumps(payload),
                       capture_output=True, text=True,
                       env=_env(iso))
    t12("an ABSENT manifest still fails OPEN, loudly (DEC-101 carve-out intact)",
        r.returncode == 0 and "enforcement OFF" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:160]}")


def _manifest_root(body, mode="w"):
    root = tempfile.mkdtemp()
    os.makedirs(os.path.join(root, ".harness"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), mode) as f:
        f.write(body)
    return root


# F-01, found by the review panel and reproduced live before the fix. load_str caught only
# yaml.YAMLError and load_file's open()/read() sat outside any try, so a manifest that is
# not valid UTF-8 — or a directory where a file was expected — raised past every caller's
# `except YamlParseError`, killed the subprocess with exit 1, and exit 1 is NON-BLOCKING
# (DEC-100). The write then proceeded UNGOVERNED. This is the ONE way a fail-closed guard
# fails open, it is the same crash pattern T-17's receipt documents, and it was fixed once
# in the escape path and missed here in the module both hooks call. Asserted at HOOK level,
# not module level: the panel showed module tests can exercise a path production never takes.
#
# M-02, found by the re-review panel and PRE-EXISTING at both SHAs. F-01 widened load_str's
# except, but these inputs PARSE SUCCESSFULLY — an empty file yields None, a bare scalar a
# str, a bare list a list — so no exception is ever raised and manifest_domains'
# `parsed.get("shared")` raised AttributeError straight past both hooks' `except
# YamlParseError`. Exit 1, non-blocking (DEC-100), write allowed. An EMPTY team-config.yaml
# was enough to disable both write guards. The shape is worth remembering: walk()
# immediately above guards every branch with isinstance and the very next statement did
# not. F-01's fix was scoped to the two shapes cycle 0 happened to name; this was a third
# route to the same fail-open.
UNREADABLE_MANIFESTS = (
    ("F-01: a manifest that is not valid UTF-8 BLOCKS (was exit 1 = fail open)",
     b"schema_version: 1\nteams: [{name: b}]\n\xff\xfe not utf-8\n", "wb", "does not parse"),
    ("M-02: a manifest that parses to a non-mapping (empty) BLOCKS, not crashes", "", "w", ""),
    ("M-02: a manifest that parses to a non-mapping (bare scalar) BLOCKS, not crashes",
     "just text\n", "w", ""),
    ("M-02: a manifest that parses to a non-mapping (bare list) BLOCKS, not crashes",
     "- a\n- b\n", "w", ""),
)


def _t12_unreadable_manifests_block():
    for label, body, mode, needle in UNREADABLE_MANIFESTS:
        r = fire(_manifest_root(body, mode), "allowed/thing.md")
        t12(label, r.returncode == 2 and needle in r.stderr and "Traceback" not in r.stderr,
            f"exit {r.returncode} (2 blocks, 1 fails OPEN): {r.stderr.strip()[:200]}")
    as_dir = tempfile.mkdtemp()
    os.makedirs(os.path.join(as_dir, ".harness", "team-config.yaml"))
    r = fire(as_dir, "allowed/thing.md")
    t12("F-01: a manifest that is a DIRECTORY does not crash the guard",
        r.returncode in (0, 2) and "Traceback" not in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:200]}")


STATE_PATH = ".harness/harness/features/FEAT-90-fixture/runs/r1/state.yaml"
# --- the state.yaml shape gate, now loader-driven (D-02) ---
# The NESTED duplicate is the genuinely NEW behaviour: the regex this replaced was anchored
# at column 0 (`^([A-Za-z_]...):` under re.M), so a duplicate nested inside a block was
# invisible — the FEAT-02 audit's finding one level down. MALFORMED is a NEW blocking
# outcome: the regex found no keys in a malformed file and reported nothing wrong.
#
# T-17 / D-08: `on:` is NOT the string "on" after parsing — YAML 1.1 resolves it to True.
# Without str() on both sides, `k not in ALLOWED` compares a bool against a set of strings
# and `sorted()` gets a MIXED set. THE FIXTURE NEEDS TWO UNKNOWN KEYS, one bool-resolved and
# one string: `on:` alone sorts fine and passed against a deliberately un-coerced copy.
# Mixed types are what raise TypeError, and in a fail-closed hook a raise is a BLOCK ON
# EVERY WRITE, not a wrong answer; the denial must also explain the unquoted-key cause.
SHAPE_GATE_ROWS = (
    ("a newly created, well-formed version-2 state.yaml with checkpoint keys passes",
     "schema_version: 2\nrun_id: r1\nstatus: complete\n", 0, ()),
    ("a DUPLICATE top-level key is blocked with the DEC-156 message",
     "run_id: r1\ncost: 1\ncost: 2\n", 2, ("DEC-156", "duplicate key")),
    ("a NESTED duplicate key is blocked (column-0 regex could not see it)",
     "run_id: r1\nsteps:\n  - id: s1\n    cost: 1\n    cost: 2\n", 2, ("duplicate key",)),
    ("MALFORMED state.yaml is blocked with a parse-error message",
     "run_id: [unclosed\nstatus: complete\n", 2, ("not valid YAML",)),
    ("a non-checkpoint top-level key is still blocked (DEC-154 vocabulary intact)",
     "run_id: r1\nfindings: lots of prose\n", 2, ("non-checkpoint",)),
    ("a YAML-truthy key (`on:`) beside a string key denies cleanly, naming the unquoted cause",
     "run_id: r1\non: something\nfindings: prose\n", 2,
     ("non-checkpoint", "UNQUOTED key", "YAML 1.1")),
)


def _t12_state_shape_gate():
    root = fixture(FIXTURE_MANIFEST)
    for label, content, code, needles in SHAPE_GATE_ROWS:
        r = fire(root, STATE_PATH, content)
        t12(label, r.returncode == code and all(n in r.stderr for n in needles)
            and "Traceback" not in r.stderr, f"exit {r.returncode}: {r.stderr.strip()[:200]}")


# --- SC-08: the bootstrap escape, driven through the REAL HOOK -------------------------
#
# SC-08 says "the first HOOK INVOCATION permits the write and emits the install command".
# test-harness-yaml.py covers require_or_bootstrap's state machine at MODULE level; a module
# test cannot see whether the hook acts on the return value at all. It could not, and this
# caught it: both hooks called require_or_bootstrap(root) and DISCARDED the result, so the
# escape printed an install command and then let every write through — REQ-04's fail-closed
# and SC-09's expiry were inert.
#
# PyYAML is hidden portably: a fake yaml.py that raises ImportError, on a PYTHONPATH entry
# the hook appends after its own bin/. harness_yaml.py:18-20 is the single `try: import yaml
# / except ImportError: yaml = None` in the tree (D-12), so this reproduces a machine that
# genuinely lacks the package without uninstalling it.
#
# FEAT-2397 (#10): the session identity rides in the REAL hook payload (session_id, or the
# transcript_path stem; the hook hands it on as HOOK_PAYLOAD). The retired Claude
# CLAUDE_CODE_SESSION_ID / CLAUDE_CODE_BRIDGE_SESSION_ID arms are gone, so those names are
# scrubbed from the inherited environment and only set where a case asserts they are inert.
LEGACY_IDENTITY_ENV = ("CLAUDE_CODE_SESSION_ID", "CLAUDE_CODE_BRIDGE_SESSION_ID")


def _fake_yaml():
    fake = tempfile.mkdtemp()
    with open(os.path.join(fake, "yaml.py"), "w") as f:
        f.write('raise ImportError("simulated: no PyYAML")\n')
    return fake


def fire_noyaml(fake, root, path, identity, content="x", env=None):
    payload = {"agent_type": "harness-documentor", "tool_name": "Write",
               "tool_input": {"file_path": os.path.join(root, path), "content": content},
               **identity}
    hook_env = _env(root, PYTHONPATH=fake)
    for name in LEGACY_IDENTITY_ENV:
        hook_env.pop(name, None)
    hook_env.update(env or {})
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=hook_env)


def _install_advice():
    # BUG-2169: the advice is per platform (apt on Debian/Ubuntu's system python3, pip
    # elsewhere), so the assertion is that one of harness_yaml's real install commands
    # arrives, not that the word "pip" does.
    import harness_yaml
    return {harness_yaml.install_command(homebrew=brew, debian_system=debian).splitlines()[0]
            for brew in (True, False) for debian in (True, False)}


def _sysmsg(res):
    """The hook's stdout systemMessage, parsed rather than substring-matched: malformed JSON
    on a hook's stdout is worse than none, so an unloadable payload is None."""
    try:
        return json.loads(res.stdout.strip()).get("systemMessage", "")
    except (ValueError, AttributeError):
        return None


def _t12_bootstrap_first_session(fake):
    root = fixture(FIXTURE_MANIFEST)
    marker = os.path.join(root, ".harness", ".pyyaml-bootstrap")
    advice = _install_advice()
    r1 = fire_noyaml(fake, root, "allowed/a.md", {"session_id": "sess-A"})
    t12("SC-08: with PyYAML missing, the FIRST hook invocation PERMITS the write",
        r1.returncode == 0, f"exit {r1.returncode}: {r1.stderr.strip()[:200]}")
    # NOT SC-08's full clause, and the name says so: stderr on an ALLOW is not a channel the
    # user sees (the 2026-08-03 hand-run measured it). D-14b tracks the real fix.
    t12("[partial SC-08] the install command reaches stderr (NOT proof the user sees it — D-14b)",
        any(command in r1.stderr for command in advice),
        f"stderr: {r1.stderr.strip()[:200]}")
    # SC-08's ACTUAL clause: "a channel the user sees" — `systemMessage` on stdout.
    msg = _sysmsg(r1)
    t12("SC-08: the install command reaches a channel the user SEES (systemMessage)",
        isinstance(msg, str) and any(command in msg for command in advice),
        f"stdout was {r1.stdout.strip()[:200]!r}")
    t12("SC-08: ...and records the marker",
        os.path.exists(marker), f"no marker at {marker}")
    r2 = fire_noyaml(fake, root, "allowed/b.md", {"session_id": "sess-A"})
    t12("SC-08: a SECOND write in the SAME session is permitted, silently",
        r2.returncode == 0 and not any(command in r2.stderr for command in advice),
        f"exit {r2.returncode}: {r2.stderr.strip()[:200]}")


def _t12_bootstrap_other_session_and_cleanup(fake):
    # The SC-09 MECHANISM. The criterion itself is verify: uat, because only a real session
    # boundary proves it honestly — but the identity comparison the boundary relies on is
    # testable here, and without it SC-09 could not pass in principle.
    root = fixture(FIXTURE_MANIFEST)
    marker = os.path.join(root, ".harness", ".pyyaml-bootstrap")
    fire_noyaml(fake, root, "allowed/a.md", {"session_id": "sess-A"})
    r3 = fire_noyaml(fake, root, "allowed/c.md", {"session_id": "sess-B"})
    t12("SC-09 mechanism: a DIFFERENT session is BLOCKED while PyYAML is missing",
        r3.returncode == 2, f"exit {r3.returncode}: {r3.stderr.strip()[:200]}")
    # D-14a, found by the SC-09 hand-run: the block was SILENT. Unlike the grant path
    # (D-14b), stderr on a BLOCK does reach the agent, because exit 2 surfaces it (DEC-100).
    t12("D-14a: the block SAYS WHY and carries the install command",
        r3.stderr.strip() != "" and any(command in r3.stderr for command in _install_advice())
        and "EARLIER session" in r3.stderr,
        f"stderr was {len(r3.stderr)} bytes: {r3.stderr.strip()[:200]}")
    # Self-cleaning: once yaml imports again the marker is removed, so a machine that gets
    # fixed does not carry a spent grant forever. Control-plane target, for T-01's reason:
    # this is an allow assertion, and an in-root product-shaped path stops being owned.
    r4 = fire(root, ".harness/allowed/d.md")
    t12("the marker self-unlinks once PyYAML imports again",
        r4.returncode == 0 and not os.path.exists(marker),
        f"exit {r4.returncode}, marker present: {os.path.exists(marker)}")


def _t12_grant_skips_shape_gate(fake):
    # THE SHAPE GATE DOES NOT RUN DURING A BOOTSTRAP GRANT, and that is the ruling, not an
    # oversight: a line-scan fallback violated the signed BRIEF (Goal :20-21, Constraint
    # :48-49) and the user ruled REMOVE IT. What that costs is EARLIER detection, not
    # correctness: check-state.py refuses a malformed state.yaml at the next /harness entry.
    # These cases pin the RULED behaviour so nobody "fixes" it back.
    rbad = fire_noyaml(fake, fixture(FIXTURE_MANIFEST), STATE_PATH, {"session_id": "sess-shape"},
                       content="run_id: r1\nfindings: a notebook of prose\n")
    t12("grant: a malformed state.yaml is ALLOWED (no fallback — BRIEF Goal :20-21)",
        rbad.returncode == 0,
        f"exit {rbad.returncode}: {rbad.stderr.strip()[:200]}")
    rok = fire_noyaml(fake, fixture(FIXTURE_MANIFEST), STATE_PATH, {"session_id": "sess-shape-ok"},
                      content="run_id: r1\nstatus: complete\n")
    t12("grant: a well-formed state.yaml is allowed too (the grant is not selective)",
        rok.returncode == 0, f"exit {rok.returncode}: {rok.stderr.strip()[:200]}")
    # And WITH a parser the gate is unchanged — this is what makes the pair meaningful
    # rather than "the hook allows everything".
    rgated = fire(fixture(FIXTURE_MANIFEST), STATE_PATH, content="run_id: r1\nfindings: prose\n")
    t12("with a parser, the shape gate still BLOCKS the same content",
        rgated.returncode == 2 and "DEC-154" in rgated.stderr,
        f"exit {rgated.returncode}: {rgated.stderr.strip()[:200]}")


# FEAT-2397 (#10): which inputs name the session for the bootstrap grant. The payload's
# session_id and transcript stem do; the retired CLAUDE_CODE_* variables alone do not, so a
# grant asked for with only those fails CLOSED (no identity, D-06), never opens.
IDENTITY_SOURCES = (
    ("a payload session_id", {"session_id": "sess-P"}, {}, 0),
    ("a payload transcript_path stem", {"transcript_path": "/t/sess-T.jsonl"}, {}, 0),
    ("CLAUDE_CODE_SESSION_ID alone", {}, {"CLAUDE_CODE_SESSION_ID": "sess-E"}, 2),
    ("CLAUDE_CODE_BRIDGE_SESSION_ID alone", {}, {"CLAUDE_CODE_BRIDGE_SESSION_ID": "sess-B"}, 2),
)


def _t12_identity_sources(fake):
    for label, identity, env, code in IDENTITY_SOURCES:
        r = fire_noyaml(fake, fixture(FIXTURE_MANIFEST), "allowed/a.md", identity, env=env)
        t12(f"FEAT-2397 identity: {label} -> exit {code} with PyYAML missing",
            r.returncode == code and "Traceback" not in r.stderr,
            f"exit {r.returncode}: {r.stderr.strip()[:200]}")


T12_SCENARIOS = (_t12_sc05_pair, _t12_bad_manifests_fail_closed, _t12_absent_manifest_fails_open,
                 _t12_unreadable_manifests_block, _t12_state_shape_gate)
T12_NOYAML_SCENARIOS = (_t12_bootstrap_first_session, _t12_bootstrap_other_session_and_cleanup,
                        _t12_grant_skips_shape_gate, _t12_identity_sources)


def run_t12():
    for scenario in T12_SCENARIOS:
        scenario()
    fake = _fake_yaml()
    for scenario in T12_NOYAML_SCENARIOS:
        scenario(fake)
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

    repository_identities = {}

    def fire_abs(root, abspath, agent):
        key = (root, agent)
        if key not in repository_identities:
            child = f"child-{len(repository_identities)}"
            parent = "fleet-test-parent"
            receipt = inflight_registry.claim_with_receipt(
                root, agent, "task", root, feature="FEAT-fleet-test",
                supervisor_pid=os.getpid(), repository="widget",
            )
            assert receipt is not None
            assert inflight_registry.attach_runtime_identity(
                root, agent, "FEAT-fleet-test", agent_id=child,
                parent_agent_id=parent, claim_id=receipt["claim_id"],
            )
            repository_identities[key] = (child, parent)
        child, parent = repository_identities[key]
        return subprocess.run(
            [HOOK],
            input=json.dumps({
                "agent_type": agent,
                "harness_feature": "FEAT-fleet-test",
                "harness_agent_id": child,
                "harness_parent_agent_id": parent,
                "tool_name": "Write",
                "tool_input": {"file_path": abspath, "content": "x"},
            }),
            capture_output=True, text=True,
            env=_env(root),
        )

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
        f"(want 2), granted stderr={f_yes.stderr.strip()[:180]!r}")

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
    # ../../.omp let harness-documentor write .omp/agents/*. Reproduced against
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
    os.makedirs(os.path.join(esc_root, ".omp", "agents"))
    os.symlink(os.path.join(esc_root, ".omp"),
               os.path.join(esc_root, ".harness", "harness", "docs", "esc"))
    esc = fire_abs(esc_root, os.path.join(esc_root, ".harness", "harness", "docs", "esc",
                                          "agents", "pwned.md"), "harness-documentor")
    legit = fire_abs(esc_root, os.path.join(esc_root, ".harness", "harness", "docs", "guide.md"),
                     "harness-documentor")
    fleet_case(
        "SYMLINK PAIR: a link out of a granted directory is REFUSED at its real "
        "target, and the ordinary granted write still PASSES",
        esc.returncode == 2 and legit.returncode == 0,
        f"escape got {esc.returncode} (want 2 — the write lands in .omp/agents/), "
        f"legitimate got {legit.returncode} (want 0)")
    fleet_case(
        "SYMLINK: the refusal names the REAL target, not the link path — an agent "
        "told it may not write the docs path would file a bug against the wrong file",
        ".omp/agents/pwned.md" in esc.stderr,
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


def _assert_typed_view_resolution():
    root = fixture("""schema_version: 1
teams:
  - name: fixture
    members:
      - name: harness-zeta
        domain:
          - { path: .harness/typed/**, upsert: true }
      - name: harness-alpha
        domain:
          - { path: .harness/typed/**, upsert: true }
      - name: harness-flattened-trap
        domain:
          - { path: .harness/elsewhere/**, upsert: true }
shared:
  - { path: .harness/typed/** }
""")
    result = subprocess.run(
        [HOOK, "--resolve", ".harness/typed/owned.txt"],
        capture_output=True, text=True, timeout=10, env=_env(root),
        stdin=subprocess.DEVNULL)
    expected = [
        "harness-alpha",
        "harness-zeta",
        "SHARED .harness/typed/**",
    ]
    if result.stdout.splitlines() != expected:
        raise AssertionError(
            "typed view did not preserve owner association and shared order: "
            f"{result.stdout.splitlines()!r}")


# --- FEAT-09 / DEC-179: `--resolve <path>`. Eight cases, one per clause of T-01's
# intent. The two stdin cases are the reason this mode exists at all: both were
# MEASURED on the pre-change tree — an open pipe blocked indefinitely, and closed
# stdin exited 0 printing nothing, which is a fail-open answer indistinguishable
# from a clean resolve.
# GRADE-2 REASON: run_resolve keeps the existing ordered resolver and stdin parity
# contract together; the new typed-view assertion is isolated to avoid adding branches.
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
    r = resolve(".agents/skills/harness/bin/run-unit-tests.py")
    check("(b) --resolve: a doubly-granted path returns both grantees",
          sorted(r.stdout.split()) == ["harness-backend-dev", "harness-dev-ops"],
          f"got {r.stdout.split()!r}")

    _assert_typed_view_resolution()

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
    r = hook(f"{ROOT}/.agents/skills/harness/bin/check-domain.py", "harness-documentor")
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
    r = hook_env(".agents/skills/harness/bin/check-domain.py", "harness-documentor",
                 ".harness/harness.json")
    check("(i) VF-1: HARNESS_RESOLVE_PATH set in the env does NOT disable the hook",
          denied(r), f"got {r.returncode}, stderr={r.stderr!r}")
    r = hook_env(".agents/skills/harness/bin/check-domain.py", "harness-documentor", "")
    check("(j) VF-1: an EMPTY HARNESS_RESOLVE_PATH does NOT disable the hook",
          denied(r), f"got {r.returncode}, stderr={r.stderr!r}")

    print(f"\n{10 - fails}/10 --resolve cases passed.\n")
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
    copied_hook = os.path.join(iso, "check-domain.py")
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


# ---------------------------------------------------------------------------
# shadowless-P triage rows 5, 85/102, 94 — three narrow check-domain refusals that
# replace prose nothing enforced. Each plants the defect AND its honest counterpart.
# ---------------------------------------------------------------------------
SHADOW_MANIFEST = FIXTURE_MANIFEST.replace(
    "- { path: .harness/*/features/*/runs/*/state.yaml, upsert: true }",
    "- { path: .harness/*/features/*/runs/*/state.yaml, upsert: true }\n"
    "          - { path: .harness/*/features/*/observations/*.md, upsert: true }\n"
    "          - { path: .harness/*/features/*/plan.yaml, upsert: true }\n"
    "          - { path: .harness/*/features/*/BRIEF.md, upsert: true }\n"
    "          - { path: .harness/*/features/*/notes/*.md, upsert: true }")

SHADOW = []


def shadow(name, ok, detail=""):
    SHADOW.append((name, ok, detail))


def _run_observations_log_cases(root):
    # ROW 5 — the observations log has exactly one writer (observations-merge.py, Bash).
    obs_defect = fire(root, ".harness/repo/features/FEAT-1-thing/observations/harness-documentor.md")
    shadow("Write to the observations log is BLOCKED — only observations-merge.py may write it",
           obs_defect.returncode == 2 and "observations-merge.py" in obs_defect.stderr,
           f"exit {obs_defect.returncode}: {obs_defect.stderr.strip()[:200]}")

    obs_honest = fire(root, ".harness/repo/features/FEAT-1-thing/notes/observations-mention.md")
    shadow("a path that merely mentions 'observations', outside observations/, still writes",
           obs_honest.returncode == 0,
           f"exit {obs_honest.returncode}: {obs_honest.stderr.strip()[:200]}")


def _run_plan_conversion_cases(root):
    # ROWS 85/102 — a PLAN.md-era feature is never CONVERTED to plan.yaml.
    legacy_dir = os.path.join(root, ".harness", "repo", "features", "FEAT-2-legacy")
    os.makedirs(legacy_dir)
    with open(os.path.join(legacy_dir, "PLAN.md"), "w", encoding="utf-8") as f:
        f.write("# legacy plan\n")
    conversion = fire(root, ".harness/repo/features/FEAT-2-legacy/plan.yaml")
    shadow("creating plan.yaml beside a shipped PLAN.md is BLOCKED (DEC-182: never converted)",
           conversion.returncode == 2 and "PLAN.md already ships" in conversion.stderr,
           f"exit {conversion.returncode}: {conversion.stderr.strip()[:200]}")

    fresh_conversion = fire(root, ".harness/repo/features/FEAT-3-fresh/plan.yaml")
    shadow("a FRESH feature's first plan.yaml write is not the legacy-conversion denial "
           "(only plan.yaml's own single-writer route denial fires)",
           fresh_conversion.returncode == 2
           and "PLAN.md already ships" not in fresh_conversion.stderr,
           f"exit {fresh_conversion.returncode}: {fresh_conversion.stderr.strip()[:200]}")


def _run_feature_dir_name_cases(root):
    # ROW 94 — the feature id is coined once, in the shape dispatch-guard.py already
    # enforces at spawn.
    bad_name = fire(root, ".harness/repo/features/not-a-feature-id/BRIEF.md")
    shadow("a first write into a malformed feature dir name is BLOCKED",
           bad_name.returncode == 2 and "not a valid feature id" in bad_name.stderr,
           f"exit {bad_name.returncode}: {bad_name.stderr.strip()[:200]}")

    good_name = fire(root, ".harness/repo/features/FEAT-4-good-name/BRIEF.md")
    shadow("a first write into a well-formed feature dir name writes",
           good_name.returncode == 0,
           f"exit {good_name.returncode}: {good_name.stderr.strip()[:200]}")

    grandfathered_dir = os.path.join(root, ".harness", "repo", "features", "legacy-no-regex")
    os.makedirs(grandfathered_dir)
    grandfathered = fire(root, ".harness/repo/features/legacy-no-regex/BRIEF.md")
    shadow("an EXISTING malformed-name feature dir is grandfathered — only the first "
           "write is checked",
           grandfathered.returncode == 0,
           f"exit {grandfathered.returncode}: {grandfathered.stderr.strip()[:200]}")


def run_shadow_checks():
    root = fixture(SHADOW_MANIFEST)
    _run_observations_log_cases(root)
    _run_plan_conversion_cases(root)
    _run_feature_dir_name_cases(root)
    shutil.rmtree(root, ignore_errors=True)
    fails = 0
    for name, ok, detail in SHADOW:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(SHADOW) - fails}/{len(SHADOW)} shadow-check cases passed.")
    return fails


def run_feature_id_regex_parity():
    """check-domain's `_FEATURE_ID_RE` is a COPY of dispatch-guard.py's `FEATURE_RE`
    (row 94) — copied rather than imported so this hook never depends on that file's own
    bootstrap. A copy that drifts silently stops meaning what its comment says, so the
    two literal pattern strings are compared here rather than trusted to stay in sync.
    """
    domain_src = open(os.path.join(HERE, "check-domain.py"), encoding="utf-8").read()
    dispatch_src = open(os.path.join(HERE, "dispatch-guard.py"), encoding="utf-8").read()
    domain_m = re.search(r'_FEATURE_ID_RE = re\.compile\(r"(.+)"\)', domain_src)
    dispatch_m = re.search(r'FEATURE_RE = re\.compile\(r"(.+)"\)', dispatch_src)
    fails = 0
    if not (domain_m and dispatch_m):
        print("FAIL  feature-id regex parity\n      | one of the two literals could not "
              f"be found (domain={bool(domain_m)}, dispatch={bool(dispatch_m)})")
        return 1
    if domain_m.group(1) != dispatch_m.group(1):
        print("FAIL  feature-id regex parity\n      | check-domain._FEATURE_ID_RE "
              f"{domain_m.group(1)!r} != dispatch-guard.FEATURE_RE {dispatch_m.group(1)!r}")
        fails += 1
    else:
        print("ok    feature-id regex parity: check-domain._FEATURE_ID_RE == "
              "dispatch-guard.FEATURE_RE")
    return fails


# ================= FEAT-2337: QA's runner-receipt grant (SC-06, DEC-255) =================
# QA writes `runs/<run-id>/qa/manifest-<kind>.json` through the production runner and
# nothing else under a run: not the lead's state.yaml or digest.md, not a log, not another
# directory level. Each row fires the CANDIDATE hook at a throwaway copy of the REAL authored
# manifest (or the real template, in its own unsegmented layout), so the grant under test is
# the one that ships and the live checkout is never a fixture.
FEAT2337_CONVENTIONS = {
    "authored": (os.path.join(ROOT, ".harness", "team-config.yaml"),
                 ".harness/harness/features/FEAT-9-receipt/runs"),
    "template": (os.path.join(ROOT, ".claude", "skills", "harness", "templates",
                              "team-config.yaml"),
                 ".harness/features/FEAT-9-receipt/runs"),
}

# (convention, case, path under the feature's runs/, agent, expected exit)
FEAT2337_GRANT_ROWS = (
    ("authored", "QA writes its own unit receipt", "r-1-validator/qa/manifest-unit.json",
     "harness-qa", 0),
    ("authored", "QA writes its own integration receipt",
     "r-1-validator/qa/manifest-integration.json", "harness-qa", 0),
    ("authored", "QA may not write the run's state.yaml", "r-1-validator/state.yaml",
     "harness-qa", 2),
    ("authored", "QA may not write the lead's digest.md", "r-1-validator/digest.md",
     "harness-qa", 2),
    ("authored", "QA may not write a run log beside its receipt", "r-1-validator/qa/unit.log",
     "harness-qa", 2),
    ("authored", "QA may not write a sibling run's state.yaml", "r-0-eng/state.yaml",
     "harness-qa", 2),
    ("authored", "QA may not write a manifest outside qa/", "r-1-validator/manifest-unit.json",
     "harness-qa", 2),
    ("authored", "QA may not write a manifest nested below qa/",
     "r-1-validator/qa/extra/manifest-unit.json", "harness-qa", 2),
    ("authored", "an unrelated reader may not write QA's receipt",
     "r-1-validator/qa/manifest-unit.json", "harness-code-reviewer", 2),
    ("authored", "a dev may not write QA's receipt", "r-1-validator/qa/manifest-unit.json",
     "harness-backend-dev", 2),
    ("template", "QA writes its own receipt (template layout)",
     "r-1-validator/qa/manifest-unit.json", "harness-qa", 0),
    ("template", "QA may not write the run's state.yaml (template layout)",
     "r-1-validator/state.yaml", "harness-qa", 2),
    ("template", "QA may not write the lead's digest.md (template layout)",
     "r-1-validator/digest.md", "harness-qa", 2),
    ("template", "QA may not write a run log (template layout)", "r-1-validator/qa/unit.log",
     "harness-qa", 2),
    ("template", "an unrelated reader may not write QA's receipt (template layout)",
     "r-1-validator/qa/manifest-unit.json", "harness-code-reviewer", 2),
)

# (case, path under the authored runs/, whether `--resolve` names harness-qa)
FEAT2337_RESOLVE_ROWS = (
    ("the resolver routes a receipt to harness-qa", "r-1-validator/qa/manifest-unit.json", True),
    ("the resolver does not route run state to harness-qa", "r-1-validator/state.yaml", False),
    ("the resolver does not route a run log to harness-qa", "r-1-validator/qa/unit.log", False),
)


def _feat2337_root(convention):
    """A fixture root carrying a verbatim copy of the convention's real manifest."""
    source, runs = FEAT2337_CONVENTIONS[convention]
    with open(source, encoding="utf-8") as handle:
        return fixture(handle.read()), runs


def _feat2337_detail(result):
    return f"exit {result.returncode}: {(result.stdout + result.stderr).strip()[:200]}"


def _feat2337_grant_results(roots):
    results = []
    for convention, name, path, agent, want in FEAT2337_GRANT_ROWS:
        root, runs = roots[convention]
        result = fire(root, f"{runs}/{path}", content="{}", agent=agent)
        results.append((f"[{convention}] {name}", result.returncode == want,
                        _feat2337_detail(result)))
    return results


def _feat2337_resolve_results(roots):
    root, runs = roots["authored"]
    results = []
    for name, path, routed in FEAT2337_RESOLVE_ROWS:
        result = subprocess.run([HOOK, "--resolve", f"{runs}/{path}"], capture_output=True,
                                text=True, env=_env(root))
        names = result.stdout.split()
        results.append((f"[authored] {name}",
                        result.returncode == 0 and ("harness-qa" in names) == routed,
                        f"exit {result.returncode}: {names}"))
    return results


def _feat2337_claim_results(roots):
    """QA's live claim on one feature's worktree binds where its receipt may land. A refusal
    must name the claim or checkout rule, so a missing grant cannot pass these rows."""
    root, runs = roots["authored"]
    own = make_linked_worktree(root, os.path.join(root, ".claude", "worktrees", "FEAT-9"), "A")
    other = make_linked_worktree(root, os.path.join(root, ".claude", "worktrees", "FEAT-8"), "B")
    inflight_registry.claim(own, "harness-qa", "harness-validator-lead", own,
                            feature="FEAT-9-receipt")
    receipt = f"{runs}/r-1-validator/qa/manifest-unit.json"
    rows = (
        ("a claimed QA writes the receipt in its own feature worktree",
         os.path.join(own, receipt), 0, ""),
        ("a claimed QA may not write another feature's receipt in that feature's worktree",
         os.path.join(other, ".harness/harness/features/FEAT-8-other/runs/r-2-validator/qa/"
                      "manifest-unit.json"), 2, "holds worktree claim"),
        ("a claimed QA may not write its feature's receipt in the main checkout",
         os.path.join(root, receipt), 2, "belongs in worktree"),
    )
    results = []
    for name, destination, want, cause in rows:
        result = fire(root, destination, content="{}", agent="harness-qa")
        results.append((f"[authored] {name}",
                        result.returncode == want and cause in result.stderr,
                        _feat2337_detail(result)))
    return results


def run_feat2337_receipt_grant_cases():
    roots = {convention: _feat2337_root(convention) for convention in FEAT2337_CONVENTIONS}
    results = []
    for collect in (_feat2337_grant_results, _feat2337_resolve_results, _feat2337_claim_results):
        results += collect(roots)
    for root, _runs in roots.values():
        shutil.rmtree(root, ignore_errors=True)
    fails = 0
    for name, ok, detail in results:
        print(f"ok    {name}" if ok else f"FAIL  {name}\n      | {detail}")
        fails += 0 if ok else 1
    print(f"\n{len(results) - fails}/{len(results)} FEAT-2337 receipt-grant cases passed.")
    return fails


def main(argv=None):
    """Every case and block by default; `--only run_<block>` runs that one block (FEAT-2337)."""
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        return drive(globals(), CASES)
    block = globals().get(argv[-1]) if len(argv) == 2 and argv[0] == "--only" else None
    if not (callable(block) and argv[-1].startswith("run_")):
        print(f"usage: {os.path.basename(__file__)} [--only run_<block>]", file=sys.stderr)
        sys.exit(2)
    total, verdict = _run_block_captured(block, argv[-1])
    if verdict is not None:
        print(f"FAIL  aggregation safeguard: {verdict}")
    return total + (verdict is not None)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
