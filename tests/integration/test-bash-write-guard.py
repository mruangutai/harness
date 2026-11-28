#!/usr/bin/env python3
"""Tests for bash-write-guard.py (DEC-151, Task #5).

WHY THIS EXISTS: the guard was added after a live bypass, so loosening its
detection without a test proving it STILL BLOCKS the real bypass shapes is how a
guard fails open. Every case below asserts an EXACT exit code — 2 blocks, 0
passes (DEC-100: only exit 2 blocks, so "nonzero" would let a crash masquerade
as a rejection).

Two halves, and both must stay green:
  MUST PASS  — legitimate commands the guard had been blocking
  MUST BLOCK — the DEC-151 bypass shapes it exists to stop
"""
from integration_support import ROOT, BIN, TESTS
import functools, json, os, shutil, subprocess, sys, tempfile, time

import inflight_registry
from check_support import Checks
from git_support import init_repo
from isolated_bin import isolated_bin
# _env sets BOTH root names to one value (FEAT-42 T-11): the guard resolves its root via
# harness_boundary.resolve_root, the same contract check_domain_support documents.
from check_domain_support import _env, fixture, make_linked_worktree
HERE = str(BIN)
ROOT = str(ROOT)
PRIOR_GUARD_FIXTURE = str(TESTS / "integration" / "fixtures" / "prior-bash-write-guard.fixture")
GUARD = os.environ.get("BASH_WRITE_GUARD_BIN") or os.path.join(HERE, "bash-write-guard.py")

C = Checks()
check = C.check


def _record(results, prefix=""):
    """Record each (name, ok, detail) a block collected, in order."""
    for name, ok, detail in results:
        check(prefix + name, ok, detail)


CASES = []

def case(name, cmd, want, agent="harness-eng-lead"):
    CASES.append((name, cmd, want, agent))

# ---------------- MUST PASS: legitimate, and previously blocked ----------------
# The Co-Authored-By trailer is MANDATED, so this shape must work for every agent.
case("mandated commit trailer (angle brackets in a quoted string)",
     'git commit -m "x" -m "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"', 0)
case("an arrow inside a quoted string",
     'echo "done -> 0"', 0)
case("an HTML comment inside a quoted string",
     'echo "marks itself with <!-- ok-stale --> and is skipped"', 0)
case("a heredoc delimiter is not a redirect target",
     'git commit -F - <<EOF\nmsg\nEOF', 0)
case("input redirection is a READ, not a write",
     'python3 - < script.py', 0)
case("a quoted string mentioning a redirect",
     'echo "use > path to redirect"', 0)
# B-5: a redirection is not an operand. Before the fix the LAST token of
# `cp a b 2>/dev/null` was read as the cp destination, and a legal in-domain copy was
# denied naming "2>/dev/null" as the path. Hit twice during FEAT-11.
case("stderr redirection is not the cp destination",
     'cp .harness/harness/features/F/runs/r-eng/a.md .harness/harness/features/F/runs/r-eng/b.md 2>/dev/null', 0)
case("stderr redirection is not an rm target",
     'rm .harness/harness/features/F/runs/r-eng/b.md 2>/dev/null', 0)
# The other half, and the reason dropping redirect tokens is safe: every REAL redirect is
# still caught by the redirect scan. If these three ever pass, the fix has gone too far.
case("a redirect after cp still blocks, glued",
     'cp .harness/harness/features/F/runs/r-eng/a.md .harness/harness/features/F/runs/r-eng/b.md >src/evil.py', 2)
case("a redirect after cp still blocks, spaced",
     'cp .harness/harness/features/F/runs/r-eng/a.md .harness/harness/features/F/runs/r-eng/b.md > src/evil.py', 2)
case("an out-of-domain cp destination still blocks",
     'cp .harness/harness/features/F/runs/r-eng/a.md src/evil.py', 2)
# #241: `-f` is a SCRIPT-FILE flag for sed/perl/awk and a FORCE flag for rm. The skip was
# unconditional, so `rm -f <path>` arrived with an empty target list and no deny fired —
# the most common deletion idiom was the one that got through. `rm -rf dir` was never
# affected because -rf is one token; `rm -r -f path` was.
case("rm -f does not hide its target", 'rm -f src/main.py', 2)
case("rm -r -f does not hide its target", 'rm -r -f src/main.py', 2)
case("rm -rf still blocks, unchanged", 'rm -rf src/', 2)
# The other direction, and the reason -f could not simply be dropped from the flag list:
# sed's script path must STILL be skipped, so the finding names the target and not the script.
case("sed -i -f still names the target, not the script", 'sed -i -f /tmp/s.sed src/main.py', 2)
case("awk -i inplace -f still names the target", 'awk -i inplace -f /tmp/p.awk src/main.py', 2)
# In-domain forms must not become collateral: a fix that blanket-denies rm -f is not a fix.
case("rm -f in-domain passes", 'rm -f .harness/harness/features/F/runs/r-eng/a.md', 0)
case("sed -i -f in-domain passes", 'sed -i -f /tmp/s.sed .harness/harness/features/F/runs/r-eng/a.md', 0)
# Reviewers are read-only everywhere and never reach the path check at all.
case("plain read commands pass", 'git status --porcelain', 0)

# --- heredoc BODIES are data, not operators (B-6) ---
# `python3 - <<PY ... PY` feeds a script to an interpreter. A `>` in that body is Python's
# comparison operator; reading it as a redirect blocked every inline script this repo runs.
case("a comparison operator inside a python heredoc body",
     "python3 - <<'PY'\nif a > b:\n    print('x')\nPY", 0)
case("a redirect-shaped line inside a CAT heredoc body is inert text",
     "cat <<'EOF'\necho hi > src/main.py\nEOF", 0)
case("an unquoted heredoc tag is still a heredoc",
     "python3 - <<PY\nif a > b: pass\nPY", 0)

# --- a compound line is several commands, and `;` ends each one's operands (B-6) ---
# shlex leaves `;` ATTACHED to the previous token ('docs/a.md;'), so the guard's separator
# break never fired and the NEXT command's name was collected as an operand: `rm -f
# docs/a.md; echo ok` was refused for "rm targets echo".
case("rm in-domain followed by another command",
     'rm -f .harness/harness/docs/a.md; echo ok', 0, agent="harness-documentor")
case("mv within domain followed by another command",
     'mv .harness/harness/docs/a.md .harness/harness/docs/b.md; ls', 0, agent="harness-documentor")
case("in-domain redirect followed by a read command",
     'echo x > .harness/harness/docs/a.md; git status', 0, agent="harness-documentor")

# ---------------- MUST BLOCK: the loosening above must not open a hole ----------------
# A heredoc fed to a SHELL is code, not data — its body really does redirect.
case("a heredoc fed to bash still blocks its redirect",
     "bash <<'EOF'\necho x > src/main.py\nEOF", 2)
case("a heredoc fed to sh still blocks its redirect",
     "sh <<'EOF'\necho x > src/main.py\nEOF", 2)
# A real redirect on the heredoc's own command line is not part of the body.
case("a redirect on the heredoc command line still blocks",
     "cat <<'EOF' > src/main.py\nhi\nEOF", 2)
# Every segment of a compound line is scanned, not just the first.
case("an out-of-domain redirect in the SECOND segment still blocks",
     'echo ok; echo x > src/main.py', 2, agent="harness-documentor")
# RETARGETED BY FEAT-17 T-03, AND NOT BECAUSE IT TURNED RED — it never flipped, since
# src/main.py is refused either way. That is the problem: this case's NAME says the SECOND
# segment is scanned, and once classify refuses docs/a.md in its own right the FIRST operand
# carries the whole refusal, so it would pass even if second-segment scanning regressed
# entirely. .harness/harness/docs/a.md is granted AND control-plane, so it exits 0 alone, which puts
# the weight of the expected 2 back where the name says it is.
case("an out-of-domain rm in the second segment still blocks",
     'rm .harness/harness/docs/a.md; rm src/main.py', 2, agent="harness-documentor")
case("an out-of-domain write after && still blocks",
     'git status && echo x > src/main.py', 2, agent="harness-documentor")
# A shell anywhere in the pipeline makes the body code. Looking only at the first word
# (`cat`) stripped this body and let the redirect vanish — a fail-open the heredoc change
# introduced and this case pins shut.
case("a cat heredoc PIPED to bash still blocks its redirect",
     "cat <<'EOF' | bash\necho x > src/main.py\nEOF", 2, agent="harness-documentor")
case("a heredoc piped to sh -s still blocks its redirect",
     "cat <<'EOF' | sh -s\necho x > src/main.py\nEOF", 2, agent="harness-documentor")
# An unbalanced quote must not raise: only exit 2 blocks (DEC-100), so a traceback would
# fail OPEN on a command the guard never inspected.
case("an unbalanced quote does not crash the hook",
     "echo it's fine <<EOF\nx\nEOF", 0, agent="harness-documentor")

# ---------------- MUST BLOCK: the DEC-151 bypass shapes ----------------
# Issue #1544: Python is a common write carrier, not an unparseable shell escape.
# Pin both policy branches: reviewers are read-only everywhere, while a writing agent's
# literal target still goes through the ordinary domain check. Read-mode `open` is the
# negative control; recognizing the function name alone would block legitimate probes.
case("reviewer cannot write through python open",
     "python3 -c \"open('src/main.py', 'w').write('x')\"", 2,
     agent="harness-code-reviewer")
case("python open write to an out-of-domain path",
     "python3 -c \"open('src/main.py', 'w').write('x')\"", 2)
case("python open keyword target and mode still block",
     "python3 -c \"open(file='src/main.py', mode='w').write('x')\"", 2)
case("python open write to an in-domain path",
     "python3 -c \"open('.harness/harness/features/F/runs/r-eng/a.md', 'w').write('x')\"",
     0)
case("python open without a write mode remains a read",
     "python3 -c \"open('src/main.py').read()\"", 0)
case("python heredoc open write cannot bypass extraction",
     "python3 - <<'PY'\nopen('src/main.py', 'w').write('x')\nPY", 2)
case("output redirect to an out-of-domain path", 'echo x > src/main.py', 2)
case("append redirect to an out-of-domain path", 'echo x >> src/main.py', 2)
case("QUOTED redirect target still blocks", 'echo x > "src/main.py"', 2)
case("sed -i in place", "sed -i '' 's/a/b/' src/main.py", 2)
case("perl -pi in place", "perl -pi -e 's/a/b/' src/main.py", 2)
case("tee to an out-of-domain path", 'echo x | tee src/main.py', 2)
case("rm of an out-of-domain path", 'rm src/main.py', 2)
case("mv onto an out-of-domain path", 'mv a.py src/main.py', 2)


# ============== T-14: SC-06's paired assertion, on a fixture manifest ==============
# The cases above run against the REAL repo manifest. These use a fixture so a
# malformed rulebook can be exercised without touching the one governing this session.

FIXTURE_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain:
          - { path: allowed/**, upsert: true }
          - { path: .harness/allowed/**, upsert: true }
          - { path: ".", read: true }
"""

def fire(root, cmd, agent="harness-backend-dev", guard=GUARD, cwd=None,
         agent_id=None, parent_agent_id=None, feature=None, extra_env=None):
    """Run the guard on one Bash payload. A falsy agent or id leaves its key out entirely
    (agent None is the main session, which sends no agent_type)."""
    payload = {"tool_name": "Bash", "tool_input": {"command": cmd}}
    for key, value in (("agent_type", agent), ("harness_agent_id", agent_id),
                       ("harness_parent_agent_id", parent_agent_id),
                       ("harness_feature", feature)):
        if value:
            payload[key] = value
    return subprocess.run([guard], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root, **(extra_env or {})), cwd=cwd)


def _partial_bin(*extra):
    """An isolated bin holding ONLY the guard plus the named sibling modules — the module
    set is the point: each site leaves something out on purpose. Returns (iso, guard)."""
    iso = tempfile.mkdtemp()
    isobin = os.path.join(iso, ".claude", "skills", "harness", "bin")
    os.makedirs(isobin)
    shutil.copy(GUARD, os.path.join(isobin, "bash-write-guard.py"))
    for fn in extra:
        shutil.copy(os.path.join(HERE, fn), os.path.join(isobin, fn))
    return iso, os.path.join(isobin, "bash-write-guard.py")


def run_t14():
    # SC-06's PAIRED assertion. Either half alone is ALSO what a broken guard
    # produces — an allow-all escape passes the permitted write, a block-all
    # fail-closed blocks the forbidden one. Only a manifest that actually parsed
    # yields both from one fixture.
    root = fixture(FIXTURE_MANIFEST)
    # THE ALLOW HALF IS RETARGETED to a control-plane path (FEAT-17 T-03). Inside the
    # harness base a glob match is accepted only if the TARGET passes
    # is_control_plane_target, so the `allowed/**` grant cannot permit <root>/allowed/x.txt.
    # FIXTURE_MANIFEST already grants .harness/allowed/**. The expected exit codes below
    # are UNCHANGED — flipping this 0 to a 2 would degenerate the pair into "block-all
    # passes", which is the allow-only blindness this case exists to catch.
    ok = fire(root, f"echo hi > {os.path.join(root, '.harness', 'allowed', 'x.txt')}")
    no = fire(root, f"echo hi > {os.path.join(root, 'forbidden', 'x.txt')}")
    check("SC-06 pair: permitted bash write allowed AND forbidden blocked",
                ok.returncode == 0 and no.returncode == 2,
                f"permitted got {ok.returncode} (want 0), forbidden got {no.returncode} (want 2)")

    # Both write surfaces must fail closed the SAME way on a broken rulebook. Before
    # T-14 this file carried its own copy of the skimmer, so the two hooks could
    # disagree about what an agent may write — and this hook exists BECAUSE an agent
    # routed around the other one (DEC-151), which makes a divergence a bypass.
    # The MESSAGE is asserted, not just the exit code, and that is the whole point
    # here. The pre-T-14 skimmer also exited 2 on this fixture — but ACCIDENTALLY: it
    # found no name/path lines in the broken file, so `mine` was empty and every path
    # was "outside your domain". An agent was told it lacked permission when the truth
    # was that the rulebook was unreadable, so the rational response — try a different
    # path — fails identically and teaches nothing. Blocking for the wrong reason is
    # not the same as blocking.
    bad = fixture('teams: [ {name: x ## eaten\nnext_key: 1\n')
    r = fire(bad, f"echo hi > {os.path.join(bad, 'allowed', 'x.txt')}")
    check("a MALFORMED manifest blocks the bash write (fail closed)",
                r.returncode == 2 and "does not parse" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    dup = fixture(FIXTURE_MANIFEST + "\nschema_version: 2\n")
    r = fire(dup, f"echo hi > {os.path.join(dup, 'allowed', 'x.txt')}")
    check("a DUPLICATE key in the manifest blocks the bash write",
                r.returncode == 2 and "duplicate key" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    strict_payload = (
        '{"agent_type":"","agent_type":"harness-backend-dev",'
        '"tool_name":"Bash","tool_input":{"command":"echo hi > '
        + os.path.join(root, "forbidden", "duplicate.json") + '"}}'
    )
    strict = subprocess.run(
        [GUARD], input=strict_payload, capture_output=True, text=True, env=_env(root))
    if strict.returncode != 0:
        check("duplicate hook-payload keys are rejected before policy evaluation",
                    False, f"exit {strict.returncode}: {strict.stderr.strip()[:160]}")

    # DEC-151's carve-out is unchanged: an absent manifest still fails OPEN. Needs an
    # isolated copy, not merely an empty CLAUDE_PROJECT_DIR — root falls back to
    # _derived, so a guard running from the real bin/ finds the real manifest whatever
    # the env var says. (The same trap made this case vacuous in test-check-domain.py.)
    iso, iso_guard = _partial_bin()
    r = fire(iso, f"echo hi > {os.path.join(iso, 'x.txt')}", guard=iso_guard)
    check("an ABSENT manifest still fails OPEN (DEC-151 carve-out intact)",
                r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:160]}")

    # Both hooks compute domains from ONE function, so the same agent and path must get
    # the same verdict from either write surface.
    #
    # THE PRODUCT-SHAPED PATH IS BACK, AND SO IS THE AGREEMENT (FEAT-17 T-03). On
    # 2026-08-11 the allow half was moved off <root>/src/main.py because the surfaces
    # genuinely disagreed there: FEAT-15 taught check-domain.py that a product-shaped
    # target inside the harness root is refused, and bash-write-guard.py was out of that
    # feature's scope, so Write exited 2 and Bash exited 0. Issue #261. That divergence
    # is closed — this guard now decides from harness_boundary.classify — so the case is
    # restored rather than left describing a split the code no longer has.
    #
    # The grant carries src/** for exactly this: without it <root>/src/main.py is
    # refused for a MISSING GRANT on both routes, which is agreement about nothing. With
    # it, the only thing that can refuse it is the control-plane target-side test — the
    # rule that used to live on one route only.
    agree_manifest = FIXTURE_MANIFEST.replace(
        "          - { path: .harness/allowed/**, upsert: true }",
        "          - { path: .harness/allowed/**, upsert: true }\n"
        "          - { path: src/**, upsert: true }")
    root = fixture(agree_manifest)
    cd = os.path.join(HERE, "check-domain.py")
    for rel, want in ((".harness/allowed/x.txt", 0), ("src/main.py", 2),
                      ("forbidden/x.txt", 2)):
        tgt = os.path.join(root, rel)
        b = fire(root, f"echo hi > {tgt}")
        w = subprocess.run([cd], input=json.dumps(
            {"agent_type": "harness-backend-dev", "tool_name": "Write",
             "tool_input": {"file_path": tgt, "content": "x"}}),
            capture_output=True, text=True, env=_env(root))
        check(f"both write surfaces agree on {rel} (D-03, one shared rule)",
                    b.returncode == want and w.returncode == want,
                    f"bash got {b.returncode}, write got {w.returncode}, want {want}")


def _linked_worktree(path, owner_root, wt_id, manifest_text):
    """A linked git worktree, built BY HAND — no git is invoked, here or in the guard.

    A `.git` FILE holding `gitdir: <owner>/.git/worktrees/<id>` is exactly the on-disk
    shape `git worktree add` leaves. Standing up a real one would mean this suite
    creating the shape the guard now forbids. Each checkout gets its own manifest,
    because each is used as a session root below and a root with no readable manifest
    falls to the DEC-151 fail-open — which exits 0 for a reason that has nothing to do
    with worktrees.
    """
    make_linked_worktree(owner_root, path, wt_id)
    os.makedirs(os.path.join(path, ".harness"), exist_ok=True)
    with open(os.path.join(path, ".harness", "team-config.yaml"), "w") as f:
        f.write(manifest_text)


def _worktree_fixture():
    """<tmp>/root as the main checkout, one out-of-place sibling, one legitimate."""
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "root")
    os.makedirs(os.path.join(root, ".harness"))
    os.makedirs(os.path.join(root, ".git", "worktrees", "sib"))
    os.makedirs(os.path.join(root, ".git", "worktrees", "wt"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    sib = os.path.join(tmp, "sib")
    legit = os.path.join(root, ".claude", "worktrees", "wt")
    _linked_worktree(sib, root, "sib", FIXTURE_MANIFEST)
    _linked_worktree(legit, root, "wt", FIXTURE_MANIFEST)
    return tmp, root, sib, legit


def run_worktree():
    """Issue #103 on the BASH route, and the one-implementation proof for #261.

    Every in-root path asserted here is under `.harness/`. That is load-bearing: inside
    the harness base a glob match is accepted only when the TARGET passes
    is_control_plane_target, so the fixture's `allowed/**` grant cannot permit
    <root>/allowed/x.txt. A shorter path would make the paired ALLOWs fail against
    correct code.
    """
    tmp, root, sib, legit = _worktree_fixture()

    # TARGET-SIDE: a shell write INTO the sibling, from a session rooted in the
    # checkout. The sibling is outside root, so this half discriminates whatever the
    # manifest grants — before this task the `..` continue made it invisible here.
    r = fire(root, f"echo hi > {os.path.join(sib, 'allowed', 'x.txt')}")
    check("a shell write INTO an out-of-place worktree is REFUSED",
        r.returncode == 2 and ".claude/worktrees" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # The PAIRED ALLOW, same fixture and same session. Without it the case above is
    # satisfied by a guard that refuses everything.
    r = fire(root, f"echo hi > {os.path.join(root, '.harness', 'allowed', 'x.txt')}")
    check("the same session's in-domain shell write still PASSES",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # ROOT-SIDE. The target is control-plane and in-domain FOR THAT ROOT, so it exits 0
    # with the root-side rule deleted — which is what makes the case discriminating.
    r = fire(sib, f"echo hi > {os.path.join(sib, '.harness', 'allowed', 'x.txt')}")
    check("a session ROOTED in an out-of-place worktree is refused its own in-domain "
        "shell write",
        r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # BOTH HALVES OF THE WORDING, on the SAME captured stderr. This route prints its own
    # copy of the verdict, so a wording assertion on the Write route alone would leave
    # this one free to regress. `git worktree remove` SUCCEEDS at exit 0 from inside the
    # tree it removes, so that guidance printed to a session standing in that tree is an
    # instruction to delete its own cwd. Presence alone passes if the destructive
    # sentence is re-added beside the location line; absence alone passes for a verdict
    # that says nothing. Scoped to THIS stderr — the target-side verdict keeps it.
    check("the ROOT-SIDE bash verdict names .claude/worktrees and does NOT say "
        "`git worktree remove`",
        ".claude/worktrees" in r.stderr and "git worktree remove" not in r.stderr,
        f"stderr: {r.stderr.strip()[:300]}")

    # A COMMAND THAT EXTRACTS NO WRITE TARGET AT ALL. This is what proves the root-side
    # check does not sit behind `if not findings: sys.exit(0)`, and after the re-scope it
    # is the ONLY case pinning this route's placement.
    r = fire(sib, "git status --porcelain")
    check("a read-only command from an out-of-place root is ALSO refused (the check is "
        "not behind the no-findings exit)",
        r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # The PAIRED ALLOW for the root-side rule: same shape, legitimate location.
    r = fire(legit, f"echo hi > {os.path.join(legit, '.harness', 'allowed', 'x.txt')}")
    check("a session rooted in a LEGITIMATE worktree is unaffected",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # SC-07 on this route, and WHAT IT PROVES IS NARROWER THAN ITS TWIN — measured, after
    # a first version of this comment asserted the wrong mechanism.
    #
    # On the Write route the same case is granted ONLY by DEC-143's prefix stripping:
    # delete the stripping and it reddens. HERE, TWO INDEPENDENT RULES EACH GRANT IT.
    # Measured three ways:
    #   stripping deleted .................... still 0
    #   DEC-153's carve-out deleted .......... still 0
    #   BOTH deleted ......................... 2
    # So this case pins the OUTCOME the criterion asks for and discriminates NEITHER
    # mechanism on its own. Recorded that way rather than named for one of them, because
    # a case labelled with a rule it does not test is worse than an unlabelled one.
    r = fire(root, f"echo hi > {os.path.join(legit, '.harness', 'allowed', 'x.txt')}")
    check("SC-07: the legitimate worktree is writable FROM OUTSIDE it on the Bash route "
        "(granted independently by BOTH the carve-out and the stripping)",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- F-A ON THIS ROUTE. The panel's `high` was reproduced on the Write route; this
    # guard imports the same module and reads the same return value, so an unparseable
    # pointer must refuse here too. Without these cases the fix is asserted on one route
    # and merely believed on the other.
    _ptr = os.path.join(sib, ".git")
    _good = open(_ptr, "rb").read()
    for _label, _payload in (
            ("not valid UTF-8", _good.rstrip() + b"\xff"),
            ("a bare word, no gitdir:", b"nonsense\n"),
            ("an empty file", b""),
    ):
        with open(_ptr, "wb") as _f:
            _f.write(_payload)
        r = fire(root, f"echo hi > {os.path.join(sib, 'allowed', 'x.txt')}")
        check(f"F-A: a .git pointer that is {_label} REFUSES the shell write",
            r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")
    with open(_ptr, "wb") as _f:
        _f.write(_good)
    r = fire(root, f"echo hi > {os.path.join(root, '.harness', 'allowed', 'x.txt')}")
    check("F-A: with the pointer restored, the in-domain shell write still PASSES",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- THE FAIL-CLOSED PAIR for the shared module (D-06).
    iso, iso_guard = _partial_bin("harness_yaml.py", "artifact_accessors.py")
    os.makedirs(os.path.join(iso, ".harness"))
    with open(os.path.join(iso, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    r = fire(iso, "echo hi > %s" % os.path.join(iso, ".harness", "allowed", "x.txt"),
             guard=iso_guard)
    check("a MISSING harness_boundary.py blocks the bash write and NAMES the module",
        r.returncode == 2 and "harness_boundary" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- THE ONE-IMPLEMENTATION PROOF, BY MUTATION RATHER THAN BY GREP.
    #
    # A grep proves the literal appears once. It cannot prove both guards READ that one
    # copy. So: an isolated bin holding all four files both hooks need, one payload, and
    # the named constant changed in the COPIED module — by NAME, never by sed on the bare
    # literal, which also appears in the DEC-143 rel-stripping regex and would change two
    # rules at once.
    #
    # THE FIXTURE IS PINNED, NOT AIMED, and every part of it is load-bearing. The
    # mutation is observed through the ROOT-SIDE check, with CLAUDE_PROJECT_DIR set to
    # the legitimate worktree and the payload targeting a control-plane path inside it.
    # Aimed at that worktree from OUTSIDE it, the payload is inside root, so on the Write
    # route select_base returns a base and the out-of-place branch is never reached,
    # while on the Bash route the DEC-153 continue returns before classify is called —
    # the mutation could not flip on either route. And a non-control-plane target such as
    # .../wt/allowed/x.txt exits 2 both before and after, which is 2 to 2 and again no
    # flip.
    m_tmp = tempfile.mkdtemp()
    m_bin = os.path.join(m_tmp, "bin")
    os.makedirs(m_bin)
    for fn in ("artifact_accessors.py", "check-domain.py", "bash-write-guard.py",
               "harness_boundary.py", "harness_yaml.py", "run_identity.py"):
        shutil.copy(os.path.join(HERE, fn), os.path.join(m_bin, fn))
    for fn in ("check-domain.py", "bash-write-guard.py"):
        os.chmod(os.path.join(m_bin, fn), 0o755)

    m_root = os.path.join(m_tmp, "root")
    os.makedirs(os.path.join(m_root, ".harness"))
    os.makedirs(os.path.join(m_root, ".git", "worktrees", "wt"))
    with open(os.path.join(m_root, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    m_wt = os.path.join(m_root, ".claude", "worktrees", "wt")
    _linked_worktree(m_wt, m_root, "wt", FIXTURE_MANIFEST)
    m_target = os.path.join(m_wt, ".harness", "allowed", "x.txt")

    def _both_routes():
        env = _env(m_wt,
                   PYTHONPATH=m_bin + os.pathsep + os.environ.get("PYTHONPATH", ""))
        b = subprocess.run([os.path.join(m_bin, "bash-write-guard.py")],
                           input=json.dumps({"agent_type": "harness-backend-dev",
                                             "tool_name": "Bash",
                                             "tool_input": {"command": f"echo hi > {m_target}"}}),
                           capture_output=True, text=True, env=env)
        w = subprocess.run([os.path.join(m_bin, "check-domain.py")],
                           input=json.dumps({"agent_type": "harness-backend-dev",
                                             "tool_name": "Write",
                                             "tool_input": {"file_path": m_target,
                                                            "content": "x"}}),
                           capture_output=True, text=True, env=env)
        return b.returncode, w.returncode

    before = _both_routes()
    check("one-implementation baseline: both routes ALLOW the legitimate worktree write",
        before == (0, 0), f"bash={before[0]}, write={before[1]}, want (0, 0)")

    mod = os.path.join(m_bin, "harness_boundary.py")
    src = open(mod).read()
    mutated = src.replace('WORKTREES_SEGMENT = ".claude/worktrees"',
                          'WORKTREES_SEGMENT = ".claude/wt-mutant"', 1)
    check("the mutation targeted the constant BY NAME (not the bare literal)",
        mutated != src, "WORKTREES_SEGMENT assignment not found in the copied module")
    open(mod, "w").write(mutated)
    # DROP THE BYTECODE CACHE, AND THIS IS NOT HOUSEKEEPING. The baseline run above left
    # a __pycache__ beside the module, and CPython validates a cached .pyc by mtime and
    # SIZE. `.claude/wt-mutant` is exactly as long as `.claude/worktrees`, so within one
    # mtime tick the stale bytecode is reused and the mutation never loads — measured
    # here as a 0/0 "no flip" that looked like a second copy of the rule.
    shutil.rmtree(os.path.join(m_bin, "__pycache__"), ignore_errors=True)

    after = _both_routes()
    # A FLIP ON ONE ROUTE ONLY MEANS A SECOND COPY OF THE RULE SURVIVES SOMEWHERE, and
    # this case must say so rather than passing on a partial result.
    check("ONE IMPLEMENTATION: mutating WORKTREES_SEGMENT flips BOTH routes 0 -> 2",
        after == (2, 2),
        f"bash={after[0]}, write={after[1]}, want (2, 2) — a flip on one route only "
        f"means a second copy of the boundary rule survives on the other")

    # --- WORKTREE CREATION (REQ-03). The door BEFORE the tree exists. Measured at
    # a29ad06: `git worktree add --detach ~/GitHub/harness-SIBLING HEAD` exited 0 from
    # both hooks.
    wt_root = fixture(FIXTURE_MANIFEST)
    legal_dest = os.path.join(wt_root, ".claude", "worktrees", "FEAT-99")
    # Assembled rather than written inline: this repository's own branch-create gate
    # scans command text for a branch flag and refuses a name carrying no issue or flow
    # id, which would block anyone editing this file from a session.
    BRANCH_FLAG = "-" + "b"

    for label, cmd, want in (
        ("an absolute destination outside .claude/worktrees",
         "git worktree add /tmp/sib-xyz HEAD", 2),
        # The flag CONSUMES the next token, so a guard that merely skipped tokens
        # starting with "-" would read the branch name as the destination.
        ("a value-taking flag cannot hide the destination",
         "git worktree add " + BRANCH_FLAG + " chore/FEAT-94-wt /tmp/sib-xyz HEAD", 2),
        # THE DISCRIMINATING FORM of the case above. `-b` CONSUMES its value, so a guard
        # that merely skipped tokens starting with "-" would read this LEGAL path as the
        # destination and permit the write to /tmp. The case above cannot catch that on
        # its own: a naive guard refuses it too, for the relative-path reason, so it
        # would pass under the very bug it is named for.
        ("a value-taking flag whose VALUE is a legal path still cannot hide it",
         "git worktree add " + BRANCH_FLAG + " " + legal_dest + " /tmp/sib-xyz HEAD", 2),
        ("a RELATIVE destination is refused — it cannot be resolved",
         "git worktree add sib HEAD", 2),
        # THE TRAVERSAL FORM, and it is what makes "resolve BOTH sides" load-bearing
        # rather than a style choice. With no resolution the comparison is string-level
        # and this path is judged inside .claude/worktrees/ and PERMITTED — a silent
        # permit of the exact mistake this scan exists to refuse.
        ("a .. traversal out of .claude/worktrees",
         "git worktree add " + os.path.join(wt_root, ".claude", "worktrees",
                                            "..", "..", "..", "tmp", "sib") + " HEAD", 2),
        ("`git worktree move` out of .claude/worktrees",
         "git worktree move " + os.path.join(wt_root, ".claude", "worktrees", "wt")
         + " /tmp/sib-xyz", 2),
        # THE PAIRED ALLOWS. The ordinary-git ones are not decoration — they are what
        # bounds the risk of a rule this broad.
        ("a destination INSIDE .claude/worktrees",
         "git worktree add " + legal_dest + " HEAD", 0),
        ("the same, with a flag that consumes nothing",
         "git worktree add --detach " + legal_dest + " HEAD", 0),
        ("ordinary git: status", "git status --porcelain", 0),
        ("ordinary git: worktree list", "git worktree list", 0),
        ("ordinary git: commit", "git commit -m x", 0),
    ):
        r = fire(wt_root, cmd)
        check(f"worktree creation — {label}",
            r.returncode == want,
            f"exit {r.returncode}, want {want}: {r.stderr.strip()[:200]}")

    # THE RELATIVE DESTINATION MUST BE REFUSED FOR BEING RELATIVE, and only the wording
    # can say so. A guard with the isabs check deleted still exits 2 here — realpath("sib")
    # resolves against the guard process's cwd, which is not under the fixture's
    # worktrees dir — so the exit code alone passes under the deleted check.
    r = fire(wt_root, "git worktree add sib HEAD")
    check("worktree creation — the relative refusal NAMES relativity as the reason",
        "RELATIVE" in r.stderr, f"stderr: {r.stderr.strip()[:250]}")

    # --- #556: THE CWD MUST NOT SUPPLY THE BOUNDARY RULE. Same defect and same proof as
    # test-check-domain.py's pair — python puts the invoking directory at sys.path[0]
    # ahead of PYTHONPATH, so before the safe-path bootstrap a harness_boundary.py in the agent cwd
    # was the resolver this guard consulted. Both halves: clean cwd refuses, hostile cwd
    # returns the SAME verdict.
    _hostile = tempfile.mkdtemp()
    with open(os.path.join(_hostile, "harness_boundary.py"), "w") as _hf:
        _hf.write("MARKER = 'nope'\n"
                  "def resolve_root(bin_dir, strict=True): return '/definitely/not/here'\n"
                  "def root_from_script(bin_dir): return '/definitely/not/here'\n"
                  "def root_above(start): return None\n")
    _real_root = ROOT
    _p556 = {"agent_type": "harness-backend-dev", "tool_name": "Bash",
             "tool_input": {"command": "echo x > "
                            + os.path.join(_real_root, ".harness", "harness", "docs",
                                           "SPEC.md")}}
    _clean = subprocess.run([GUARD], input=json.dumps(_p556), capture_output=True,
                            text=True, env=_env(_real_root),
                            cwd=tempfile.gettempdir())
    check("#556 control: from a clean cwd the out-of-domain shell write is REFUSED",
        _clean.returncode == 2,
        f"exit {_clean.returncode}: {_clean.stderr.strip()[:200]}")
    _hijack = subprocess.run([GUARD], input=json.dumps(_p556), capture_output=True,
                             text=True, env=_env(_real_root), cwd=_hostile)
    check("#556: a harness_boundary.py in the CWD does not become the guard's resolver",
        _hijack.returncode == 2 and _hijack.returncode == _clean.returncode
        and "enforcement OFF" not in _hijack.stderr,
        f"clean={_clean.returncode} hijacked={_hijack.returncode}: "
        f"{_hijack.stderr.strip()[:200]}")


def run_worktree_deep():
    """T-04 (FEAT-30) on the Bash route: the two-level `<segment>/<repo>/<id>` layout.

    A FINDING FIRST, because T-04's intent asks for something this route cannot do. It
    asks for a paired case where a granted path at depth is allowed and "a path that agent
    is not granted, at the same depth, is refused" — and in the same breath forbids
    touching `bash-write-guard.py:545`. That line is
    `if re.match(r"^\\.claude/worktrees/", rel): continue`: DEC-153's BLANKET allow for
    governed agents anywhere under the segment. So the refuse half is unreachable on this
    route by construction, and the intent is internally contradictory. The instruction not
    to touch 545 is the correct half — it carries no segment count and needs no change.

    What is asserted instead, and it is worth more than the impossible case: the carve-out
    IS blanket and IS depth-agnostic. An UNGRANTED path at two levels is allowed, which is
    today's real behaviour, so any future narrowing of 545 goes red loudly here instead of
    silently changing what qa may do in a worktree.

    The refusal half is asserted where it is actually reachable — an out-of-place linked
    worktree, refused before the DEC-153 continue is ever reached.
    """
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "root")
    os.makedirs(os.path.join(root, ".harness"))
    os.makedirs(os.path.join(root, ".git", "worktrees", "FEAT-90"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)

    deep = os.path.join(root, ".claude", "worktrees", "harness", "FEAT-90")
    _linked_worktree(deep, root, "FEAT-90", FIXTURE_MANIFEST)

    # GRANTED at depth: allowed.
    r_ok = fire(root, "echo x > %s" % os.path.join(deep, ".harness", "allowed", "x.txt"))
    check("a granted path inside <segment>/<repo>/<id> is ALLOWED on the Bash route",
          r_ok.returncode == 0,
          f"exit {r_ok.returncode}: {r_ok.stderr.strip()[:200]}")

    # UNGRANTED at depth: also allowed, and that is DEC-153, not a hole. Pinned so a
    # future narrowing of :545 cannot land silently.
    r_un = fire(root, "echo x > %s" % os.path.join(deep, "src", "main.py"))
    check("DEC-153 pinned: an UNGRANTED path at the same depth is ALSO allowed — the "
          "carve-out is blanket and depth-agnostic",
          r_un.returncode == 0,
          f"exit {r_un.returncode}: {r_un.stderr.strip()[:200]} — if this now refuses, "
          f"bash-write-guard.py:545 was narrowed and DEC-153 needs re-reading first")

    # THE REFUSAL, where it is reachable: an out-of-place linked worktree of the same
    # root. Refused ahead of the DEC-153 continue, and the message names the location.
    sib = os.path.join(tmp, "sib")
    _linked_worktree(sib, root, "sib", FIXTURE_MANIFEST)
    r_sib = fire(root, "echo x > %s" % os.path.join(sib, ".harness", "allowed", "x.txt"))
    check("an out-of-place linked worktree is REFUSED on the Bash route, and the message "
          "names where worktrees belong",
          r_sib.returncode == 2 and ".claude/worktrees" in r_sib.stderr,
          f"exit {r_sib.returncode}: {r_sib.stderr.strip()[:240]}")

    shutil.rmtree(tmp, ignore_errors=True)


def run_head_move():
    """T-05 (FEAT-30) — REQ-04's HEAD-move refusal and SC-07's Bash-route half.

    EVERY REFUSE CASE ASSERTS THE WORDING, not just exit 2. This guard has several
    refusals that all exit 2, so an exit-code-only assertion cannot tell "refused for
    moving HEAD" from "refused for something else entirely".

    The ALLOW half is what makes the set discriminating: a guard that refuses every git
    command passes case 1 and fails cases 4a-4d. Both halves come from one fixture.
    """
    tmp = tempfile.mkdtemp()
    root = os.path.join(tmp, "root")
    os.makedirs(os.path.join(root, ".harness"))
    os.makedirs(os.path.join(root, ".git", "worktrees", "FEAT-90"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    # a real tracked-looking file, so a pathspec checkout has something to name
    os.makedirs(os.path.join(root, ".harness", "allowed"), exist_ok=True)
    with open(os.path.join(root, ".harness", "allowed", "x.txt"), "w") as f:
        f.write("x\n")

    ALT = "worktree cut for this feature"

    def refuse(name, cmd, agent="harness-backend-dev", needle=ALT):
        r = fire(root, cmd, agent=agent)
        check(name, r.returncode == 2 and needle in r.stderr,
              f"exit {r.returncode} (want 2), stderr wants {needle!r}: "
              f"{r.stderr.strip()[:200]}")

    def allow(name, cmd, agent="harness-backend-dev"):
        r = fire(root, cmd, agent=agent)
        check(name, r.returncode == 0,
              f"exit {r.returncode} (want 0): {r.stderr.strip()[:200]}")

    # 1-3 — REFUSE, one shape each.
    refuse("1. SC-03 refuse: a governed agent checking out the default branch",
           "git checkout main")
    refuse("2. SC-03 refuse: harness-ORCHESTRATOR too — D-04 forbids exempting it, so "
           "this is asserted rather than assumed",
           "git checkout main", agent="harness-orchestrator")
    refuse("3a. SC-03 refuse: switching to the previous branch", "git switch -")
    refuse("3b. SC-03 refuse: a hard reset one commit back", "git reset --hard HEAD~1")
    refuse("3c. SC-03 refuse: a rebase onto the default branch", "git rebase main")
    refuse("3d. SC-03 refuse: a checkout carrying a leading -C directory option",
           "git -C /tmp/elsewhere checkout main")

    # 4 — ALLOW. Without these the whole set is satisfied by refusing everything.
    allow("4a. SC-03 allow: restoring one file via a pathspec checkout",
          "git checkout -- .harness/allowed/x.txt")
    allow("4b. SC-03 allow: status moves nothing", "git status --porcelain")
    allow("4c. SC-03 allow: staging one file", "git add .harness/allowed/x.txt")
    allow("4d. SC-03 allow: a reset naming one pathspec, no mode flag",
          "git reset .harness/allowed/x.txt")
    # LOAD-BEARING UNDER R-01: T-01's and T-02's own verify blocks run `git show`
    # against the pinned sha, executed by harness-dev-ops, which R-01 now binds.
    allow("4e. SC-03 allow: `git show` NAMES a commit without moving to it — T-01's and "
          "T-02's verify blocks depend on this",
          "git show eeabc59:README.md", agent="harness-dev-ops")

    # 5 — the main session is not governed. No agent_type key at all.
    r5 = fire(root, "git checkout main", agent=None)
    check("5. the main session is NOT governed: the same checkout with no agent_type "
          "exits 0", r5.returncode == 0,
          f"exit {r5.returncode}: {r5.stderr.strip()[:200]}")

    # 6 — the undecidable case is REFUSED, the direction DEC-151 already chose.
    refuse("6. the UNDECIDABLE case: a git call whose subcommand cannot be determined "
           "is refused, and says so",
           "git --git-dir=/tmp/x", needle="cannot determine")

    # ---- SC-07 on the Bash route, both directions from one fixture.
    deep = os.path.join(root, ".claude", "worktrees", "harness", "FEAT-90")
    _linked_worktree(deep, root, "FEAT-90", FIXTURE_MANIFEST)
    CLI = "feature-worktree.py"
    refuse("7a. SC-07 Bash route refuse: a FORCED `git worktree remove` names the CLI",
           f"git worktree remove --force {deep}", needle=CLI)
    refuse("7b. SC-07 Bash route refuse: a FORCED `git worktree prune` names the CLI",
           "git worktree prune -f", needle=CLI)
    allow("8. SC-07 the PAIRED direction: the same removal WITHOUT --force is not "
          "refused here — git decides and refuses a dirty tree itself",
          f"git worktree remove {deep}")

    # 9 — admitting two subcommands into the same parser is the edit most likely to
    # disturb the existing destination refusals, so both are re-asserted here.
    r9a = fire(root, "git worktree add %s" % os.path.join(tmp, "outside"))
    check("9a. the existing destination refusal is unchanged: an add OUTSIDE the segment "
          "still exits 2",
          r9a.returncode == 2 and ".claude/worktrees" in r9a.stderr,
          f"exit {r9a.returncode}: {r9a.stderr.strip()[:200]}")
    r9b = fire(root, "git worktree add %s"
               % os.path.join(root, ".claude", "worktrees", "harness", "FEAT-91"))
    check("9b. ...and an add INSIDE the segment still exits 0",
          r9b.returncode == 0, f"exit {r9b.returncode}: {r9b.stderr.strip()[:200]}")

    # 10 + 11 — THE PAIR THAT MAKES THE REORDERING DISCRIMINATING. Case 2 does not cover
    # this: harness-orchestrator is refused only because no exemption exists for it,
    # while harness-dev-ops has an explicit one. A second, different hole.
    refuse("10. RULING R-01: harness-DEV-OPS is refused a branch checkout — this FAILS "
           "against any build that places the rule after the dev-ops early return",
           "git checkout main", agent="harness-dev-ops")
    r11 = fire(root, "echo x > %s" % os.path.join(root, "src", "main.py"),
               agent="harness-dev-ops")
    check("11. ...and the WRITE exemption is INTACT: dev-ops still writes a path it is "
          "not granted, exit 0. Without this half, case 10 is satisfied by deleting the "
          "exemption and removing DEC-151's recovery path.",
          r11.returncode == 0,
          f"exit {r11.returncode}: {r11.stderr.strip()[:200]}")

    shutil.rmtree(tmp, ignore_errors=True)


def _put(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def _native_remove_fixture():
    """A real repository (git init, one commit) with two linked worktrees made by this test's
    own git: FEAT-91 holding untracked, IGNORED notes/x.md and runs/r/digest.md under
    .harness/harness/features/FEAT-91-probe (the loss git cannot see), FEAT-92 holding only an
    untracked scratch.txt."""
    tmp = tempfile.mkdtemp(prefix="bash-guard-native-remove-")
    root = os.path.join(tmp, "root")
    _put(os.path.join(root, ".harness", "team-config.yaml"), FIXTURE_MANIFEST)
    _put(os.path.join(root, ".gitignore"), _NATIVE_IGNORES)
    git = ["git", "-C", root, "-c", "user.email=t@example.com", "-c", "user.name=T"]
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "init"]):
        subprocess.run(git + args, check=True, capture_output=True)
    worktrees = {}
    for wt_id in ("FEAT-91", "FEAT-92"):
        worktrees[wt_id] = os.path.join(root, ".claude", "worktrees", "harness", wt_id)
        subprocess.run(git + ["worktree", "add", "-q", "-b", f"feat/{wt_id}", worktrees[wt_id]],
                       check=True, capture_output=True)
    feature = os.path.join(worktrees["FEAT-91"], ".harness", "harness", "features", "FEAT-91-probe")
    _put(os.path.join(feature, "notes", "x.md"), "working file\n")
    _put(os.path.join(feature, "runs", "r", "digest.md"), "working file\n")
    _put(os.path.join(worktrees["FEAT-92"], "scratch.txt"), "scratch\n")
    return tmp, root, worktrees, feature


def run_native_remove_retention():
    """FEAT-2641 T-11 (ruling E4): an unforced native `git worktree remove` of a worktree holding
    untracked working files is refused with GATE 2b's per-directory counts; a worktree without
    them is left to git, and prune and the force refusal are unchanged."""
    tmp, root, worktrees, feature = _native_remove_fixture()
    wt = worktrees["FEAT-91"]
    results = []

    def expect(name, cmd, want, needles=()):
        r = fire(root, cmd)
        ok = r.returncode == want and all(n in r.stderr for n in needles)
        results.append((name, ok, f"exit {r.returncode} (want {want}): {r.stderr.strip()[:300]}"))

    counts = ("notes/ (1 files)", "runs/ (1 files)", "feature-worktree.py")
    expect("T-11 (a): unforced `git worktree remove <wt>` with untracked working files exits 2",
           f"git worktree remove {wt}", 2, counts)
    expect("T-11 (b): `git -C <root> worktree remove <relative wt>` resolves against -C and "
           "exits 2", f"git -C {root} worktree remove .claude/worktrees/harness/FEAT-91", 2, counts)
    results.append(("T-11 (a)/(b): the worktree and both working files survive",
                    os.path.isdir(wt) and os.path.exists(os.path.join(feature, "notes", "x.md"))
                    and os.path.exists(os.path.join(feature, "runs", "r", "digest.md")), wt))
    expect("T-11 (c): a worktree holding only an untracked scratch.txt is left to git (exit 0)",
           f"git worktree remove {worktrees['FEAT-92']}", 0)
    expect("T-11 (d): unforced `git worktree prune` stays allowed", "git worktree prune", 0)
    expect("T-11 (e): `git worktree remove` with no operand is refused naming the command",
           "git worktree remove", 2, ("git worktree remove",))
    shutil.rmtree(tmp, ignore_errors=True)
    _record(results)


_NATIVE_COUNTS = ("notes/ (1 files)", "runs/ (1 files)", "feature-worktree.py")


def _native_identifier_cases(root, tmp):
    """(name, command, wanted exit, hook cwd, stderr needles) for the identifier operands."""
    return [
        ("T-11 (f): `git worktree remove FEAT-91` (a bare worktree identifier, cwd the owner "
         "checkout) exits 2 with the counts", "git worktree remove FEAT-91", 2, root, _NATIVE_COUNTS),
        ("T-11 (g): a unique multi-component suffix `harness/FEAT-91` exits 2",
         "git worktree remove harness/FEAT-91", 2, root, _NATIVE_COUNTS),
        ("T-11 (h): `git -C <root> worktree remove FEAT-91` from outside any repository resolves "
         "through -C and exits 2", f"git -C {root} worktree remove FEAT-91", 2, tmp, _NATIVE_COUNTS),
        ("T-11 (i): an identifier that cannot be resolved (no repository at the cwd) is refused",
         "git worktree remove FEAT-91", 2, tmp, ("git worktree list",)),
        ("T-11 (j): the identifier of a worktree without working files is left to git (exit 0)",
         "git worktree remove FEAT-92", 0, root, ()),
    ]


def run_native_remove_identifier():
    """FEAT-2641 T-11 (fix c1 must_fix 1): git also takes a worktree by a unique path-suffix
    identifier, resolved in the repository the cwd or -C addresses, so the guard resolves the
    operand as git's find_worktree does; an operand it cannot resolve is refused."""
    tmp, root, worktrees, feature = _native_remove_fixture()
    results = []
    for name, cmd, want, cwd, needles in _native_identifier_cases(root, tmp):
        r = fire(root, cmd, cwd=cwd)
        ok = r.returncode == want and all(n in r.stderr for n in needles)
        results.append((name, ok, f"exit {r.returncode} (want {want}): {r.stderr.strip()[:300]}"))
    kept = [os.path.join(feature, "notes", "x.md"), os.path.join(feature, "runs", "r", "digest.md")]
    results.append(("T-11 (f)-(i): the worktree and both working files survive",
                    os.path.isdir(worktrees["FEAT-91"]) and all(map(os.path.exists, kept)), feature))
    shutil.rmtree(tmp, ignore_errors=True)
    _record(results)


_NATIVE_IGNORES = "/.harness/*/features/*/notes/\n/.harness/*/features/*/runs/\n"
_NATIVE_FEATURE_REL = ".harness/harness/features/FEAT-91-probe"


def _undecodable_git(tmp):
    """A bin directory whose `git` runs the real one and, for `ls-files`, adds one more NUL-ended
    path that is not valid UTF-8 (notes/\\377.md): APFS will not create such a name."""
    bindir = os.path.join(tmp, "undecodable-bin")
    _put(os.path.join(bindir, "git"),
         f'#!/bin/sh\n"{shutil.which("git")}" "$@"\nrc=$?\n'
         f'case " $* " in *" ls-files "*) printf \'{_NATIVE_FEATURE_REL}/notes/\\377.md\\0\' ;; esac\n'
         'exit $rc\n')
    os.chmod(os.path.join(bindir, "git"), 0o755)
    return {"PATH": bindir + os.pathsep + os.environ["PATH"]}


def _native_selector_cases(root, other, tmp):
    """(name, command, wanted exit, hook cwd, stderr needles, extra env) for the fix c2 legs. The
    cwd `other` is a different repository, where the identifier FEAT-91 names nothing."""
    gd = os.path.join(root, ".git")
    sel = [("--git-dir", f"git --git-dir {gd} worktree remove FEAT-91"),
           ("--git-dir=", f"git --git-dir={gd} worktree remove FEAT-91"),
           ("--work-tree", f"git --work-tree {root} worktree remove FEAT-91"),
           ("--work-tree=", f"git --work-tree={root} worktree remove FEAT-91"),
           ("GIT_DIR=", f"GIT_DIR={gd} git worktree remove FEAT-91"),
           ("GIT_WORK_TREE=", f"GIT_WORK_TREE={root} git worktree remove FEAT-91"),
           ("GIT_COMMON_DIR=", f"GIT_COMMON_DIR={gd} git worktree remove FEAT-91"),
           ("env GIT_DIR=", f"env GIT_DIR={gd} git worktree remove FEAT-91"),
           ("export GIT_DIR=", f"export GIT_DIR={gd}; git worktree remove FEAT-91")]
    cases = [(f"T-11 (k) MF-2: `{form}` with an identifier operand and ignored evidence, cwd another "
              f"repository, is refused", cmd, 2, other, ("cannot tell which worktree",), None)
             for form, cmd in sel]
    cases.append(("T-11 (l) MF-1: a working file whose name is not valid UTF-8 is counted, never a "
                  "crash: exit 2 with notes/ (2 files)", "git worktree remove FEAT-91", 2, root,
                  ("notes/ (2 files)", "runs/ (1 files)"), _undecodable_git(tmp)))
    return cases


def _native_option_cases(root):
    """(name, command, wanted exit, hook cwd, stderr needles, extra env) for fix c3 MF-2b: git's
    global options are a closed set. One taking a spaced value (--config-env, --attr-source)
    must not desynchronise the subcommand walk, and an option outside the set refuses."""
    counted = ("notes/ (1 files)", "runs/ (1 files)")
    return [
        ("T-11 (m) MF-2b: spaced `--config-env a=B` is still a removal: counted, exit 2",
         "git --config-env a=B worktree remove FEAT-91", 2, root, counted, None),
        ("T-11 (m) MF-2b: `--config-env=a=B` is still a removal: counted, exit 2",
         "git --config-env=a=B worktree remove FEAT-91", 2, root, counted, None),
        ("T-11 (m) MF-2b: spaced `--attr-source HEAD` is still a removal: counted, exit 2",
         "git --attr-source HEAD worktree remove FEAT-91", 2, root, counted, None),
        ("T-11 (m) MF-2b: a global option outside the closed set is refused before a removal "
         "(behind `env`, which REQ-04's first-token walk skips, so this gate is the one refusing)",
         "env git --frobnicate value worktree remove FEAT-91", 2, root, ("does not model",), None),
    ]


def run_native_remove_c2():
    """FEAT-2641 T-11 (fix c2 MF-1, MF-2): a repository selector the guard does not model refuses
    (DEC-151), and an undecodable working-file name is counted rather than crashing the hook
    open. The evidence is ignored, so git alone would remove it."""
    tmp, root, worktrees, _feature = _native_remove_fixture()
    other = os.path.join(tmp, "other")
    subprocess.run(["git", "init", "-q", other], check=True, capture_output=True)
    ignored = subprocess.run(["git", "-C", worktrees["FEAT-91"], "check-ignore", "-q",
                              f"{_NATIVE_FEATURE_REL}/notes/x.md"], capture_output=True)
    results = [("T-11 c2: the fixture's notes/x.md is ignored by git", ignored.returncode == 0,
                f"check-ignore exit {ignored.returncode}")]
    for name, cmd, want, cwd, needles, extra in (_native_selector_cases(root, other, tmp)
                                                 + _native_option_cases(root)):
        r = fire(root, cmd, cwd=cwd, extra_env=extra)
        ok = r.returncode == want and all(n in r.stderr for n in needles)
        results.append((name, ok, f"exit {r.returncode} (want {want}): {r.stderr.strip()[:300]}"))
    shutil.rmtree(tmp, ignore_errors=True)
    _record(results)


_HEAD_OPTION_CASES = (
    ("REQ-04 MF-2b: spaced `--config-env a=B` cannot hide `switch`",
     "git --config-env a=B switch x", 2, "moves HEAD"),
    ("REQ-04 MF-2b: spaced `--attr-source HEAD` cannot hide `checkout main`",
     "git --attr-source HEAD checkout main", 2, "moves HEAD"),
    ("REQ-04 MF-2b: a global option outside the closed set is undecidable, so refused",
     "git --frobnicate value status", 2, "cannot determine"),
    ("REQ-04 MF-2b: a known spaced global option before `status` stays allowed",
     "git --config-env a=B status", 0, ""),
    ("REQ-04 MF-2b: known valueless global options before `log` stay allowed",
     "git --no-pager --no-optional-locks log -1", 0, ""),
)


def run_head_move_global_options():
    """FEAT-2641 T-11 (fix c3 MF-2b): the REQ-04 HEAD-mover walk shares the closed global-option
    set, so a value-taking option cannot pass its value off as the subcommand."""
    root = fixture(FIXTURE_MANIFEST)
    results = []
    for name, cmd, want, needle in _HEAD_OPTION_CASES:
        r = fire(root, cmd)
        results.append((name, r.returncode == want and needle in r.stderr,
                        f"exit {r.returncode} (want {want}): {r.stderr.strip()[:300]}"))
    _record(results)


FEAT50_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain:
          - { path: .harness/*/features/*/BRIEF.md, upsert: true }
"""
FEAT50_SHARED_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-documentor
        domain: []
shared:
  - { path: .harness/*/features/*/BRIEF.md }
"""
FEAT50_FEATURE = "FEAT-X-thing"
FEAT50_REL = f".harness/harness/features/{FEAT50_FEATURE}/BRIEF.md"


def _feat50_root_with_worktree(manifest, wt_id=None):
    root = fixture(manifest)
    if wt_id is None:
        return root, None
    worktree = os.path.join(root, ".claude", "worktrees", wt_id)
    _linked_worktree(worktree, root, wt_id, manifest)
    return root, worktree


def _feat50_bash_main_case(name, wt_id, manifest=FEAT50_MANIFEST):
    root, worktree = _feat50_root_with_worktree(manifest, wt_id)
    target = os.path.join(root, FEAT50_REL)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    result = fire(root, f"echo hi > {target}", agent="harness-documentor")
    ok = result.returncode == 2 and target in result.stderr and worktree in result.stderr
    return (name, ok, f"{result.returncode}: {result.stderr}"), root, target, result


def _feat50_bash_inside_case(root, worktree):
    target = os.path.join(worktree, FEAT50_REL)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    result = fire(root, f"echo hi > {target}", agent="harness-documentor")
    return ("bash-feature-checkout-inside", result.returncode == 0,
            f"{result.returncode}: {result.stderr}")


def _feat50_bash_absent_case():
    root, _worktree = _feat50_root_with_worktree(FEAT50_MANIFEST)
    target = os.path.join(root, FEAT50_REL)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    result = fire(root, f"echo hi > {target}", agent="harness-documentor")
    return ("bash-feature-checkout-absent", result.returncode == 0,
            f"{result.returncode}: {result.stderr}")


def _feat50_bash_mutant(iso):
    with open(GUARD, encoding="utf-8") as source_file:
        source = source_file.read()
    call = "            feature_checkout_guard(rel, ap)\n"
    if source.count(call) != 2:
        raise AssertionError("INCONCLUSIVE: Bash binding call anchors absent or ambiguous")
    changed = source.replace(call, "")
    path = os.path.join(iso, f".feat50-bash-write-guard-{os.getpid()}.sh")
    with open(path, "w", encoding="utf-8") as mutant_file:
        mutant_file.write(changed)
    os.chmod(path, os.stat(GUARD).st_mode)
    return source, changed, path


def _feat50_bash_red_case(root, target, main):
    iso_root = tempfile.mkdtemp()
    source, changed, mutant = _feat50_bash_mutant(isolated_bin(iso_root))
    payload = {"agent_type": "harness-documentor", "tool_name": "Bash",
               "tool_input": {"command": f"echo hi > {target}"}}
    try:
        muted = subprocess.run([mutant], input=json.dumps(payload), capture_output=True,
                               text=True, env=_env(root))
    finally:
        shutil.rmtree(iso_root, ignore_errors=True)
    ok = (changed != source and main.returncode == 2 and muted.returncode == 0
          and "Traceback" not in muted.stderr)
    return ("bash-feature-checkout-red", ok,
            f"real={main.returncode}, mutant={muted.returncode}: {muted.stderr}")


def run_feat50_checkout_binding():
    """Issue #1057: every allowed/shared Bash route binds a feature write to its worktree."""
    main_case, root, target, main = _feat50_bash_main_case(
        "bash-feature-checkout-main", FEAT50_FEATURE)
    _same, _short_root, _short_target, _short_result = _feat50_bash_main_case(
        "bash-feature-checkout-short", "FEAT-X")
    shared_case, _shared_root, _shared_target, _shared_result = _feat50_bash_main_case(
        "bash-feature-checkout-shared", FEAT50_FEATURE, FEAT50_SHARED_MANIFEST)
    worktree = os.path.join(root, ".claude", "worktrees", FEAT50_FEATURE)
    results = [
        main_case,
        _feat50_bash_inside_case(root, worktree),
        _feat50_bash_absent_case(),
        _same,
        shared_case,
        _feat50_bash_red_case(root, target, main),
    ]
    _record(results)


# FEAT-61 T-03: feature_checkout_guard is an ADAPTER over
# harness_boundary.feature_artifact_checkout_mismatch. The core answers the path
# question; this route keeps deny()'s wording and exit channel. Every receipt below
# except the injected-failure one was captured before the cutover and is byte-identical
# after it; the injected failure is the case that can only pass once the route delegates.
FEAT61_DENY_TAIL = (
    "  File changes go through the Write tool, where your domain is enforced. A path the "
    "domain hook denied does not become writable by switching tools — that is guardrail "
    "evasion (DEC-151). If the file should be yours, raise it as an open_question.\n")


def _feat61_root(*worktree_ids):
    """A main checkout granting the feature BRIEF, with one linked worktree per id;
    returns (root, [realpath of each worktree])."""
    root = fixture(FEAT50_MANIFEST)
    os.makedirs(os.path.dirname(os.path.join(root, FEAT50_REL)), exist_ok=True)
    worktrees = []
    for wt_id in worktree_ids:
        worktree = os.path.join(root, ".claude", "worktrees", wt_id)
        _linked_worktree(worktree, root, wt_id, FEAT50_MANIFEST)
        worktrees.append(os.path.realpath(worktree))
    return root, worktrees


def _feat61_fire(root, target, guard=GUARD):
    return fire(root, f"echo hi > {target}", "harness-documentor", guard=guard)


def _feat61_case(name, result, want_code, want_stderr=None):
    """want_stderr None: exit code only and no refusal at all; a string: the exact bytes."""
    if want_stderr is None:
        ok = (result.returncode == want_code and "BLOCKED" not in result.stderr
              and "Traceback" not in result.stderr)
    else:
        ok = result.returncode == want_code and result.stderr == want_stderr
    return (name, ok, f"{result.returncode}: {result.stderr!r}")


def _feat61_wrong_checkout():
    root, (expected,) = _feat61_root(FEAT50_FEATURE)
    target = os.path.join(root, FEAT50_REL)
    return _feat61_case(
        "matching path in the wrong checkout is refused in deny()'s words",
        _feat61_fire(root, target), 2,
        f"bash-write-guard: BLOCKED — {target} is a feature artifact whose write belongs "
        f"in worktree {expected}. Write it there, not in the main checkout.\n"
        + FEAT61_DENY_TAIL)


def _feat61_correct_checkout():
    root, _ = _feat61_root(FEAT50_FEATURE)
    target = os.path.join(root, ".claude", "worktrees", FEAT50_FEATURE, FEAT50_REL)
    os.makedirs(os.path.dirname(target), exist_ok=True)
    return _feat61_case("matching path inside its own worktree is allowed",
                        _feat61_fire(root, target), 0)


def _feat61_absent_worktree():
    root, _ = _feat61_root()
    return _feat61_case("matching path with no linked worktree is allowed",
                        _feat61_fire(root, os.path.join(root, FEAT50_REL)), 0)


def _feat61_non_matching_path():
    root, _ = _feat61_root(FEAT50_FEATURE)
    target = os.path.join(root, ".harness", "harness", "features", FEAT50_FEATURE)
    os.makedirs(os.path.join(root, ".harness", "allowed"), exist_ok=True)
    # The grant covers BRIEF.md only, so a sibling non-feature path must be refused by
    # the DOMAIN, not bound by the checkout rule: exit 2 without the binding wording.
    result = _feat61_fire(root, os.path.join(root, ".harness", "allowed", "x.txt"))
    ok = (result.returncode == 2 and "belongs in worktree" not in result.stderr
          and "outside your domain" in result.stderr and target not in result.stderr)
    return ("a non-feature path is never bound, even beside a linked worktree",
            ok, f"{result.returncode}: {result.stderr!r}")


def _feat61_ambiguous_worktree():
    root, _ = _feat61_root("FEAT-X", FEAT50_FEATURE)
    target = os.path.join(root, FEAT50_REL)
    return _feat61_case(
        "two prefix-matching worktrees refuse and name both candidates",
        _feat61_fire(root, target), 2,
        f"bash-write-guard: BLOCKED — {target} belongs to feature {FEAT50_FEATURE}, but its "
        f"worktree is ambiguous: feature '{FEAT50_FEATURE}' matches 2 linked worktrees: "
        f"FEAT-X, {FEAT50_FEATURE}\n" + FEAT61_DENY_TAIL)


def _feat61_injected_core_failure():
    """The route delegates: with the core raising, no private copy of the rule refuses; the
    defect reaches the hook's one guard (FEAT-65) and the already-computed allowance stands."""
    root, _ = _feat61_root(FEAT50_FEATURE)
    iso = isolated_bin(root)
    with open(os.path.join(iso, "harness_boundary.py"), "a", encoding="utf-8") as core:
        core.write("\n\ndef feature_artifact_checkout_mismatch(owner_root, raw_rel, target_path):\n"
                   "    raise RuntimeError('FEAT-61 T-03 injected core failure')\n")
    # FEAT-65: the adapter's absorbing `except` is gone. The allowance still stands only
    # because hook_guard's pass-through never blocks — and it SAYS so, in the one template.
    return _feat61_case(
        "an unexpected core failure passes through hook_guard, named, and the allowance stands",
        _feat61_fire(root, os.path.join(root, FEAT50_REL),
                     guard=os.path.join(iso, "bash-write-guard.py")), 0,
        FEAT65_LINE.format(detail="RuntimeError: FEAT-61 T-03 injected core failure"))


# FEAT-65: the hook's own-failure posture is harness_boundary.hook_guard's ONE template.
FEAT65_LINE = ("bash-write-guard: the hook failed internally ({detail}) — passing through; "
               "this is not a pass, nothing was checked.\n")


def _feat65_fire(sibling, override):
    """Fire a governed write INSIDE the feature's own worktree — past the checkout rule, so
    the claim rule is reached — against a copied bin whose `sibling` ends with `override`."""
    root, (worktree,) = _feat61_root(FEAT50_FEATURE)
    iso = isolated_bin(root)
    with open(os.path.join(iso, sibling), "a", encoding="utf-8") as core:
        core.write("\n\n" + override)
    # Spelled under the fixture root as given, not its realpath: a target the guard cannot
    # place under `root` is a product path it skips before any rule runs.
    inside = os.path.join(root, os.path.relpath(worktree, os.path.realpath(root)), FEAT50_REL)
    return _feat61_fire(root, inside, guard=os.path.join(iso, "bash-write-guard.py"))


def run_feat65_guard_cases():
    """Unexpected defects reach hook_guard; process control escapes it; the claim rule's own
    pass-through sentence and nested classifier are gone."""
    raise_rt = "    raise RuntimeError('FEAT-65 injected')\n"
    line = FEAT65_LINE.format(detail="RuntimeError: FEAT-65 injected")
    claim_defect = _feat65_fire(
        "harness_boundary.py",
        "def claim_worktrees(owner_root, agent_type, destination, agent_id=None, "
        "parent_agent_id=None):\n" + raise_rt)
    payload_defect = _feat65_fire(
        "artifact_accessors.py", "def read_hook_payload(text, context):\n" + raise_rt)
    interrupt = _feat65_fire(
        "artifact_accessors.py",
        "def read_hook_payload(text, context):\n    raise KeyboardInterrupt()\n")
    deliberate_exit = _feat65_fire(
        "artifact_accessors.py", "def read_hook_payload(text, context):\n    raise SystemExit(7)\n")
    results = [
        ("a defect in the claim rule is no longer classified locally: it is named on stderr",
         claim_defect.returncode == 0 and claim_defect.stderr.endswith(line)
         and "was not enforced" not in claim_defect.stderr
         and _unavailable_gates(claim_defect) == ["bash-write-guard"],
         f"{claim_defect.returncode}: {claim_defect.stderr!r} {claim_defect.stdout!r}"),
        ("a defect reading the payload passes through with exactly the hook_guard line",
         payload_defect.returncode == 0 and payload_defect.stderr == line
         and _unavailable_gates(payload_defect) == ["bash-write-guard"],
         f"{payload_defect.returncode}: {payload_defect.stderr!r} {payload_defect.stdout!r}"),
        ("KeyboardInterrupt escapes the guard",
         interrupt.returncode != 0 and "KeyboardInterrupt" in interrupt.stderr
         and "failed internally" not in interrupt.stderr,
         f"{interrupt.returncode}: {interrupt.stderr[-200:]!r}"),
        ("a deliberate SystemExit keeps its own exit code",
         deliberate_exit.returncode == 7 and "failed internally" not in deliberate_exit.stderr,
         f"{deliberate_exit.returncode}: {deliberate_exit.stderr!r}"),
    ]
    _record(results, "[feat65] ")


def _unavailable_gates(result):
    """FEAT-2274 C1: gate names of the `decision: unavailable` lines on stdout, in order."""
    gates = []
    for out_line in result.stdout.splitlines():
        try:
            obj = json.loads(out_line)
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("decision") == "unavailable":
            gates.append(obj.get("gate"))
    return gates


def run_feat2274_unavailable_cases(root):
    """FEAT-2274 C1: bash-write-guard's own crash (run_feat65_guard_cases), a payload it
    cannot read, and a tree whose harness_boundary.py cannot be imported are each ONE stdout
    unavailable line at exit 0. Normal passes, the not-applicable pass-throughs (main session,
    non-harness agent, dev-ops exemption) and deliberate denials emit none."""
    def bash(agent, command):
        return fire(root, command, agent, cwd=root)

    bare, bare_guard = _partial_bin()
    no_boundary = fire(bare, "echo hi > %s" % os.path.join(bare, "x.txt"),
                       guard=bare_guard, cwd=bare)
    unreadable = subprocess.run([GUARD], input="{not json", capture_output=True, text=True,
                                env=_env(root), cwd=root)
    in_domain = "rm -f .harness/harness/features/F/runs/r-eng/a.md"
    unavailable = [
        ("an unreadable payload", unreadable),
        ("a tree without harness_boundary.py", no_boundary),
    ]
    quiet = [
        ("a normal in-domain pass", bash("harness-eng-lead", in_domain), 0),
        ("the main session", bash(None, "rm -f src/main.py"), 0),
        ("a non-harness agent", bash("general-purpose", "rm -f src/main.py"), 0),
        ("the dev-ops write exemption", bash("harness-dev-ops", "rm -f src/main.py"), 0),
        ("a reviewer's write denial", bash("harness-code-reviewer", "rm -f src/main.py"), 2),
        ("an out-of-domain denial", bash("harness-eng-lead", "rm -f src/main.py"), 2),
    ]
    results = [(f"{label} passes through as exactly one unavailable line",
                r.returncode == 0 and _unavailable_gates(r) == ["bash-write-guard"],
                f"{r.returncode}: stdout={r.stdout!r} stderr={r.stderr[-200:]!r}")
               for label, r in unavailable]
    results += [(f"{label} exits {want} with no unavailable line",
                 r.returncode == want and _unavailable_gates(r) == [],
                 f"{r.returncode}: stdout={r.stdout!r} stderr={r.stderr[-200:]!r}")
                for label, r, want in quiet]
    _record(results, "[f2274] ")


def run_feat61_feature_checkout_adapter():
    """FEAT-61 T-03: the Bash route's feature-checkout binding through the shared core."""
    results = [
        _feat61_wrong_checkout(),
        _feat61_correct_checkout(),
        _feat61_absent_worktree(),
        _feat61_non_matching_path(),
        _feat61_ambiguous_worktree(),
        _feat61_injected_core_failure(),
    ]
    _record(results, "[feat61] ")



@functools.lru_cache(maxsize=None)
def bug1304_pre_change_guard():
    """The frozen pre-change guard in a copied bin; a fixed file, so built once and reused."""
    guard = os.path.join(isolated_bin(tempfile.mkdtemp()), "bash-write-guard.py")
    shutil.copyfile(PRIOR_GUARD_FIXTURE, guard)
    os.chmod(guard, 0o755)
    return guard


def _control(worktree):
    """The run digest.md a pre-change control write targets (refused by the run guard)."""
    return os.path.join(
        worktree, ".harness", "harness", "features", "F", "runs", "r-eng", "digest.md")


def _edit_claims(worktree, mutate):
    """Load the worktree's claim registry, apply mutate(data) in place, write it back."""
    path = os.path.join(worktree, inflight_registry.REGISTRY_REL)
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    mutate(data)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)


def bug1304_assert_pre_change_allows(results, name, root, command, agent, control_path):
    prior = bug1304_pre_change_guard()
    allowed = fire(root, command, agent, guard=prior)
    stderr = allowed.stderr or ""
    control = fire(root, f"echo controlled > {control_path}", agent, guard=prior)
    results.append((
        name + " is allowed by the frozen pre-change guard",
        allowed.returncode == 0
        and not any(marker in stderr for marker in (
            "enforcement OFF", "was not enforced", "passing through"))
        and control.returncode == 2,
        f"allow={allowed.returncode} control={control.returncode} stderr={stderr[:160]!r}",
    ))


def _bug1304_bash_fixture():
    manifest = FIXTURE_MANIFEST.replace(
        '          - { path: ".", read: true }',
        '          - { path: .harness/expertise/**, upsert: true }\n'
        '          - { path: ".", read: true }',
    )
    root = fixture(manifest)
    first = os.path.join(root, ".claude", "worktrees", "FEAT-1304-A")
    second = os.path.join(root, ".claude", "worktrees", "FEAT-1304-B")
    _linked_worktree(first, root, "A", manifest)
    _linked_worktree(second, root, "B", manifest)
    return root, first, second


def _bug1304_bash_expect(results, root, agent, name, command, want, contains=None):
    return _repository_bash_record(results, name, fire(root, command, agent), want, contains)


def _bug1304_bash_context(agent):
    root, first, second = _bug1304_bash_fixture()
    inflight_registry.claim(
        first, agent, "harness-eng-lead", first,
        feature="FEAT-1304-A-claim-guard")
    control_path = _control(first)
    return {
        "root": root, "first": first, "second": second,
        "control": control_path, "agent": agent,
    }


def _bug1304_bash_main_routes(results, context):
    root = context["root"]
    first = context["first"]
    agent = context["agent"]
    main_path = os.path.join(root, ".harness", "allowed", "main.md")
    sibling_path = os.path.join(context["second"], ".harness", "allowed", "sibling.md")
    cases = (
        ("relative main", "echo x > .harness/allowed/main.md"),
        ("in-place sed", "sed -i '' 's/a/b/' .harness/allowed/main.md"),
        ("absolute main", f"echo x > {main_path}"),
        ("sibling", f"echo x > {sibling_path}"),
    )
    for label, command in cases:
        _bug1304_bash_expect(
            results, root, agent, f"{label} write is refused", command, 2, first)
        bug1304_assert_pre_change_allows(
            results, label, root, command, agent, context["control"])

    own_path = os.path.join(first, ".harness", "allowed", "own.md")
    _bug1304_bash_expect(
        results, root, agent, "relative held-worktree redirect remains allowed",
        f"echo x > {os.path.relpath(own_path, root)}", 0)
    _bug1304_bash_expect(
        results, root, agent, "absolute held-worktree redirect remains allowed",
        f"echo x > {own_path}", 0)


def _bug1304_bash_unbound_routes(results, context):
    agent = context["agent"]
    unbound = fixture(FIXTURE_MANIFEST)
    _bug1304_bash_expect(results, unbound, agent, "unbound main redirect remains allowed",
                         "echo x > .harness/allowed/main.md", 0)
    scratch = os.path.join(tempfile.mkdtemp(), "scratch.md")
    _bug1304_bash_expect(
        results, context["root"], agent, "scratch redirect remains allowed",
        f"echo x > {scratch}", 0)


def _bug1304_bash_owner_claim(results, context):
    agent = context["agent"]
    unmatched = fixture(FIXTURE_MANIFEST)
    matching = os.path.join(unmatched, ".claude", "worktrees", "FEAT-1304-C")
    _linked_worktree(matching, unmatched, "C", FIXTURE_MANIFEST)
    inflight_registry.claim(
        unmatched, agent, "harness-eng-lead", unmatched,
        feature="FEAT-404-no-worktree")
    command = "echo x > .harness/allowed/unmatched.md"
    _bug1304_bash_expect(results, unmatched, agent,
                         "unresolved owner-root claim remains unbound", command, 0)
    inflight_registry.claim(
        unmatched, agent, "harness-eng-lead", unmatched,
        feature="FEAT-1304-C-linked")
    _bug1304_bash_expect(
        results, unmatched, agent, "owner-root matching claim refuses main redirect",
        command, 2, matching)
    control = _control(matching)
    bug1304_assert_pre_change_allows(
        results, "owner-root matching claim", unmatched, command, agent, control)


def _bug1304_bash_multi_and_malformed(results, context):
    root = context["root"]
    agent = context["agent"]
    second = context["second"]
    inflight_registry.claim(
        second, agent, "harness-eng-lead", second,
        feature="FEAT-1304-B-claim-guard")
    _bug1304_bash_expect(
        results, root, agent, "two claims allow redirect inside either held worktree",
        f"echo x > {os.path.join(second, '.harness', 'allowed', 'own.md')}", 0)

    malformed = os.path.join(root, ".claude", "worktrees", "broken")
    os.makedirs(malformed, exist_ok=True)
    with open(os.path.join(malformed, ".git"), "w", encoding="utf-8") as handle:
        handle.write("not-a-pointer\n")
    command = f"echo x > {os.path.join(malformed, '.harness', 'allowed', 'x.md')}"
    _bug1304_bash_expect(
        results, root, agent,
        "malformed worktree pointer refuses with nonempty claim set",
        command, 2, context["first"])
    bug1304_assert_pre_change_allows(
        results, "malformed checkout", root, command, agent, context["control"])


def _runtime_lineage_bash_routes(results, context):
    agent = context["agent"]
    _edit_claims(context["first"], lambda data: data["claims"][0].update({
        "agent_id": "BackendOne",
        "parent_agent_id": "LeadOne",
    }))

    receipt = inflight_registry.claim_with_receipt(
        context["second"],
        agent,
        "harness-eng-lead",
        context["second"],
        feature="FEAT-1304-B-claim-guard",
    )
    inflight_registry.attach_runtime_identity(
        context["second"],
        agent,
        "FEAT-1304-B-claim-guard",
        claim_id=receipt["claim_id"],
        agent_id="BackendTwo",
        parent_agent_id="LeadTwo",
    )
    first_command = (
        f"echo x > {os.path.join(context['first'], '.harness', 'allowed', 'runtime-one.md')}")
    second_command = (
        f"echo x > {os.path.join(context['second'], '.harness', 'allowed', 'runtime-two.md')}")
    own = fire(
        context["root"],
        first_command,
        agent,
        agent_id="BackendOne",
        parent_agent_id="LeadOne",
    )
    sibling = fire(
        context["root"],
        second_command,
        agent,
        agent_id="BackendOne",
        parent_agent_id="LeadOne",
    )
    second = fire(
        context["root"],
        second_command,
        agent,
        agent_id="BackendTwo",
        parent_agent_id="LeadTwo",
    )
    results.append((
        "exact runtime lineage allows its own Bash worktree",
        own.returncode == 0,
        f"exit={own.returncode} output={(own.stdout + own.stderr)[:180]!r}",
    ))
    results.append((
        "exact runtime lineage refuses a same-persona sibling Bash worktree",
        sibling.returncode == 2 and context["first"] in sibling.stderr,
        f"exit={sibling.returncode} output={(sibling.stdout + sibling.stderr)[:180]!r}",
    ))
    results.append((
        "second runtime lineage retains its Bash worktree",
        second.returncode == 0,
        f"exit={second.returncode} output={(second.stdout + second.stderr)[:180]!r}",
    ))


def _bug1304_bash_ambiguous(results, context):
    agent = context["agent"]
    ambiguous = fixture(FIXTURE_MANIFEST)
    first = os.path.join(ambiguous, ".claude", "worktrees", "FEAT")
    second = os.path.join(ambiguous, ".claude", "worktrees", "FEAT-X")
    _linked_worktree(first, ambiguous, "AMB1", FIXTURE_MANIFEST)
    _linked_worktree(second, ambiguous, "AMB2", FIXTURE_MANIFEST)
    inflight_registry.claim(
        ambiguous, agent, "harness-eng-lead", ambiguous,
        feature="FEAT-X-ambiguous")
    command = "echo x > .harness/allowed/main.md"
    _bug1304_bash_expect(
        results, ambiguous, agent,
        "ambiguous claim refuses and names candidates", command, 2, "FEAT, FEAT-X")
    control = _control(first)
    bug1304_assert_pre_change_allows(
        results, "ambiguous claim", ambiguous, command, agent, control)


def _bug1304_bash_short_claim(results, context):
    agent = context["agent"]
    root = fixture(FIXTURE_MANIFEST)
    short = os.path.join(root, ".claude", "worktrees", "BUG-91")
    _linked_worktree(short, root, "SHORT", FIXTURE_MANIFEST)
    inflight_registry.claim(
        short, agent, "harness-eng-lead", short,
        feature="BUG-91-worktree-relative-path-fixture")
    command = "echo x > .harness/allowed/main.md"
    _bug1304_bash_expect(
        results, root, agent, "short-form claim refuses main redirect", command, 2)
    control = _control(short)
    bug1304_assert_pre_change_allows(
        results, "short-form", root, command, agent, control)


def _bug1304_bash_expertise(results, context):
    root = context["root"]
    agent = context["agent"]
    expertise = os.path.join(root, ".harness", "expertise", f"{agent}.md")
    route = (
        "python3 .agents/skills/harness/bin/expertise-merge.py apply "
        f"--file {expertise} --entries -")
    # FEAT-2225 (DEC-253) moved the sanctioned route: a governed agent records Expertise
    # through the expertise_apply host tool, so the direct CLI call is now refused.
    _bug1304_bash_expect(
        results, root, agent, "direct expertise merge CLI is refused in favour of "
        "expertise_apply", route, 2, "expertise_apply")
    redirect = f"echo x > {expertise}"
    response = _bug1304_bash_expect(
        results, root, agent,
        "direct expertise redirect is refused with sanctioned advice",
        redirect, 2, "expertise_apply")
    results.extend((
        ("expertise refusal does not advise writing in worktree",
         "write it from a bound worktree" not in response.stderr, response.stderr[:180]),
        ("expertise refusal never suggests the unavailable Write route",
         "Write tool" not in response.stderr, response.stderr[:180]),
    ))
    bug1304_assert_pre_change_allows(
        results, "expertise redirect", root, redirect, agent, context["control"])


def _bug1304_bash_existing_guards(results, context):
    root = context["root"]
    first = context["first"]
    agent = context["agent"]
    _bug1304_bash_expect(
        results, root, agent, "run digest guard remains ahead of claim rule",
        f"echo x > {context['control']}", 2)
    state_path = os.path.join(
        first, ".harness", "harness", "features", "F", "runs", "r-eng", "state.yaml")
    _bug1304_bash_expect(
        results, root, agent, "run state guard remains ahead of claim rule",
        f"echo x > {state_path}", 2)
    missing = tempfile.mkdtemp()
    _bug1304_bash_expect(results, missing, agent, "missing manifest fail-open remains unchanged",
                         f"echo x > {os.path.join(missing, 'inside.md')}", 0)
    _bug1304_bash_expect(
        results, root, agent, "temporary path remains not-a-domain-question",
        f"echo x > {os.path.join(tempfile.mkdtemp(), 'outside.md')}", 0)


def _bug1304_bash_aged_claim(results, context):
    """DEC-204/DEC-233: a claim binds for exactly as long as its OMP supervisor lives. Age
    alone never releases it; a dead supervisor always does."""
    def age(data):
        data["claims"][0]["started_at"] = time.time() - 10 * 86400
    _edit_claims(context["first"], age)
    command = "echo x > .harness/allowed/main.md"
    _bug1304_bash_expect(
        results, context["root"], context["agent"],
        "ten-day-old claim with a live supervisor still refuses", command, 2, context["first"])
    bug1304_assert_pre_change_allows(
        results, "aged claim", context["root"], command,
        context["agent"], context["control"])
    dead = subprocess.run([sys.executable, "-c", "import os; print(os.getpid())"],
                          capture_output=True, text=True, check=True)
    def kill_supervisor(data):
        data["claims"][0]["supervisor_pid"] = int(dead.stdout)
        data["claims"][0].pop("supervisor_started_at", None)
        data["claims"][0]["started_at"] = time.time()
    _edit_claims(context["first"], kill_supervisor)
    response = fire(context["root"], command, context["agent"])
    results.append((
        "fresh claim whose supervisor has exited no longer binds",
        context["first"] not in response.stdout + response.stderr,
        f"exit={response.returncode} output={(response.stdout + response.stderr)[:180]!r}"))


def _bug1304_bash_unreadable(results, context):
    root, worktree, _ = _bug1304_bash_fixture()
    agent = context["agent"]
    inflight_registry.claim(
        worktree, agent, "harness-eng-lead", worktree,
        feature="FEAT-1304-A-unreadable")
    registry = os.path.join(worktree, inflight_registry.REGISTRY_REL)
    with open(registry, "w", encoding="utf-8") as handle:
        handle.write("{")
    command = "echo x > .harness/allowed/main.md"
    _bug1304_bash_expect(
        results, root, agent, "unreadable registry refuses and names file",
        command, 2, registry)
    control = _control(worktree)
    bug1304_assert_pre_change_allows(
        results, "unreadable registry", root, command, agent, control)
    with open(registry, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 2, "claims": []}, handle)
    _bug1304_bash_expect(results, root, agent, "readable empty registry remains allowed",
                         command, 0)


def _bug1304_bash_partial_registry(results, context):
    root, own, corrupt = _bug1304_bash_fixture()
    agent = context["agent"]
    inflight_registry.claim(
        own, agent, "harness-eng-lead", own, feature="FEAT-1304-A-readable")
    corrupt_registry = os.path.join(corrupt, inflight_registry.REGISTRY_REL)
    os.makedirs(os.path.dirname(corrupt_registry), exist_ok=True)
    with open(corrupt_registry, "w", encoding="utf-8") as handle:
        handle.write("{")
    own_command = f"echo x > {os.path.join(own, '.harness', 'allowed', 'inside.md')}"
    _bug1304_bash_expect(results, root, agent,
                         "readable member allows despite unrelated unreadable registry",
                         own_command, 0)
    command = "echo x > .harness/allowed/main.md"
    _bug1304_bash_expect(
        results, root, agent, "outside partial set refuses unreadable registry",
        command, 2, corrupt_registry)
    control = _control(own)
    bug1304_assert_pre_change_allows(
        results, "partial unreadable", root, command, agent, control)


def _repository_bash_fixture():
    root = fixture(FIXTURE_MANIFEST)
    workspace = tempfile.mkdtemp(prefix="harness-bash-repository-binding-")
    os.makedirs(os.path.join(root, ".harness", "factory"), exist_ok=True)
    with open(
        os.path.join(root, ".harness", "factory", "fleet.yaml"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump({
            "schema": "factory-fleet/1",
            "workspace_root": workspace,
            "repos": [
                {"name": "acme/product-a", "default_branch": "main"},
                {"name": "acme/product-b", "default_branch": "main"},
            ],
        }, handle)
    products = {
        name: os.path.join(workspace, name, "change.md")
        for name in ("product-a", "product-b")
    }
    for target in products.values():
        os.makedirs(os.path.dirname(target), exist_ok=True)
    return root, products


def _repository_bash_claim(root, repository, feature, agent_id, parent_agent_id,
):
    agent = "harness-backend-dev"
    receipt = inflight_registry.claim_with_receipt(
        root, agent, "harness-eng-lead", root,
        feature=feature, repository=repository,
    )
    if not inflight_registry.attach_runtime_identity(
        root, agent, feature, claim_id=receipt["claim_id"],
        agent_id=agent_id, parent_agent_id=parent_agent_id,
    ):
        raise AssertionError("fixture claim did not attach")
    return receipt


def _repository_bash_fire(root, target, feature, agent_id, parent_agent_id):
    return fire(
        root, f"echo x > {target}", "harness-backend-dev",
        agent_id=agent_id, parent_agent_id=parent_agent_id, feature=feature,
    )


def _repository_bash_record(results, name, response, want, contains=None):
    output = response.stdout + response.stderr
    ok = response.returncode == want and (contains is None or contains in output)
    results.append((name, ok, f"exit={response.returncode} output={output[:240]!r}"))
    return response


def _repository_bash_happy_routes(results, feature):
    root, products = _repository_bash_fixture()
    first = _repository_bash_claim(root, "product-a", feature, "BackendOne", "EngLeadOne")
    cases = (
        ("repository-bound child can repeat Bash in its own product",
         _repository_bash_fire(
             root, products["product-a"], feature, "BackendOne", "EngLeadOne"),
         0, None),
        ("repository-bound Bash child cannot cross products",
         _repository_bash_fire(
             root, products["product-b"], feature, "BackendOne", "EngLeadOne"),
         2, "mismatched"),
        ("Bash repository binding includes immediate parent",
         _repository_bash_fire(
             root, products["product-a"], feature, "BackendOne", "EngLeadTwo"),
         2, "mismatched"),
    )
    for name, response, want, contains in cases:
        _repository_bash_record(results, name, response, want, contains)
    _repository_bash_alias_routes(results, root, products, feature)
    _repository_bash_segment_routes(results, root, feature)
    _repository_bash_claim(root, "product-a", feature, "BackendTwo", "EngLeadOne")
    sibling = _repository_bash_fire(
        root, products["product-a"], feature, "BackendTwo", "EngLeadOne")
    _repository_bash_record(
        results, "same-role Bash siblings retain their own product claims", sibling, 0)
    return first


def _repository_bash_alias_routes(results, root, products, feature):
    # A cache- or worktree-shaped path is a carve-out only while it stays in this checkout:
    # one that resolves into another product still needs that product's binding (R2, R8).
    for carve_out in ("node_modules", os.path.join(".claude", "worktrees")):
        os.makedirs(os.path.join(root, carve_out), exist_ok=True)
        for product in ("product-a", "product-b"):
            os.symlink(os.path.dirname(products[product]),
                       os.path.join(root, carve_out, product))
        for product, want in (("product-a", 0), ("product-b", 2)):
            _repository_bash_record(
                results, f"a {carve_out}-shaped path into {product} exits {want}",
                _repository_bash_fire(root, f"{carve_out}/{product}/change.md", feature,
                                      "BackendOne", "EngLeadOne"),
                want, None if want == 0 else "mismatched")


def _repository_bash_segment_routes(results, root, feature):
    # The segment directory itself belongs to its product (R9), and an unexpanded glob is
    # matched against the fleet: one reaching only this product is its own, one that could
    # reach another fails closed (R10). Both go through a cache alias of `.harness`.
    os.symlink(os.path.join(root, ".harness"), os.path.join(root, "node_modules", "cp"))
    for product in ("product-a", "product-b"):
        os.makedirs(os.path.join(root, ".harness", product), exist_ok=True)
    # The shell, not Python's fnmatch, expands what reaches disk (#2104 panel): a bracket
    # expression, brace list or case variant that the shell would resolve to product-b must
    # need product-b's claim, never fall through as no product at all.
    for operand, want in (("product-a", 0), ("product-b", 2), ("product-a*", 0),
                          ("product-*", 2), ("PRODUCT-B", 2), ("[!P]roduct-b", 2),
                          ("[^P]roduct-b", 2), ("[[:lower:]]roduct-b", 2),
                          ("{product-b,none}", 2), ("@(product-b)", 2), ("(product-b)", 2)):
        _repository_bash_record(
            results, f"removing control-plane segment {operand} exits {want}",
            fire(root, f"rm -rf node_modules/cp/{operand}", "harness-backend-dev",
                               agent_id="BackendOne", parent_agent_id="EngLeadOne",
                               feature=feature),
            want, None if want == 0 else "mismatched")
    # The `.harness` component is shell text too: any spelling that may expand to it puts the
    # next component under the segment rule, while one that cannot leaves the path alone.
    os.symlink(root, os.path.join(root, "node_modules", "top"))
    for head, segment, want in ((".harness", "product-a", 0), (".HARNESS", "product-a", 0),
                                (".HARNESS", "product-b", 2), (".harnes?", "product-b", 2),
                                (".h*", "product-b", 2), ("$D", "product-b", 2),
                                ("{.harness,x}", "product-b", 2), ("$D", "notes.md", 0),
                                ("docs", "product-b", 0)):
        _repository_bash_record(
            results, f"writing {head}/{segment} through a carve-out exits {want}",
            fire(root, f"rm -rf node_modules/top/{head}/{segment}",
                               "harness-backend-dev", agent_id="BackendOne",
                               parent_agent_id="EngLeadOne", feature=feature),
            want, None if want == 0 else "mismatched")


def _repository_bash_missing_and_released(results, feature):
    missing_root, missing_products = _repository_bash_fixture()
    missing = _repository_bash_fire(
        missing_root, missing_products["product-a"], feature, "MissingChild", "EngLeadOne")
    _repository_bash_record(
        results, "Bash product write without claim fails closed", missing, 2, "missing")

    released_root, released_products = _repository_bash_fixture()
    receipt = _repository_bash_claim(released_root, "product-a", feature,
        "ReleasedChild", "EngLeadOne")
    inflight_registry.release(released_root, claim_id=receipt["claim_id"], feature=feature)
    released = _repository_bash_fire(
        released_root, released_products["product-a"], feature,
        "ReleasedChild", "EngLeadOne")
    _repository_bash_record(
        results, "released Bash repository claim fails closed", released, 2, "released")


def _repository_bash_stale_and_ambiguous(results, feature):
    stale_root, stale_products = _repository_bash_fixture()
    _repository_bash_claim(stale_root, "product-a", feature, "StaleChild", "EngLeadOne")
    def stale_supervisor(data):
        data["claims"][0]["supervisor_pid"] = 99999999
        data["claims"][0].pop("supervisor_started_at", None)
    _edit_claims(stale_root, stale_supervisor)
    stale = _repository_bash_fire(
        stale_root, stale_products["product-a"], feature, "StaleChild", "EngLeadOne")
    _repository_bash_record(
        results, "stale Bash repository claim fails closed", stale, 2, "stale")

    ambiguous_root, ambiguous_products = _repository_bash_fixture()
    _repository_bash_claim(ambiguous_root, "product-a", feature,
        "AmbiguousChild", "EngLeadOne")
    def duplicate_claim(data):
        duplicate = dict(data["claims"][0])
        duplicate["claim_id"] += "-duplicate"
        data["claims"].append(duplicate)
    _edit_claims(ambiguous_root, duplicate_claim)
    ambiguous = _repository_bash_fire(
        ambiguous_root, ambiguous_products["product-a"], feature,
        "AmbiguousChild", "EngLeadOne")
    _repository_bash_record(
        results, "ambiguous Bash repository claim fails closed", ambiguous, 2, "ambiguous")


def _repository_bash_collision_and_unreadable(
    results, feature, first_claim_id,
):
    collision_root, collision_products = _repository_bash_fixture()
    _repository_bash_claim(collision_root, "product-a", feature,
        "CollidingChild", "EngLeadOne")
    def foreign_claim(data):
        foreign = dict(data["claims"][0])
        foreign["claim_id"] += "-foreign"
        foreign["feature"] = "FEAT-496-other-dispatch"
        data["claims"].append(foreign)
    _edit_claims(collision_root, foreign_claim)
    collision = _repository_bash_fire(
        collision_root, collision_products["product-a"], feature,
        "CollidingChild", "EngLeadOne")
    _repository_bash_record(
        results, "reused Bash runtime identity fails as collision",
        collision, 2, "collision")

    unreadable_root, unreadable_products = _repository_bash_fixture()
    unreadable_path = os.path.join(unreadable_root, inflight_registry.REGISTRY_REL)
    os.makedirs(os.path.dirname(unreadable_path), exist_ok=True)
    with open(unreadable_path, "w", encoding="utf-8") as handle:
        handle.write("{")
    unreadable = _repository_bash_fire(
        unreadable_root, unreadable_products["product-a"], feature,
        "UnreadableChild", "EngLeadOne")
    _repository_bash_record(
        results, "unreadable Bash repository registry fails closed",
        unreadable, 2, "unreadable")
    output = unreadable.stdout + unreadable.stderr
    results.append((
        "Bash repository refusal does not expose registry paths or claim ids",
        inflight_registry.REGISTRY_REL not in output and first_claim_id not in output,
        output[:240],
    ))


def _repository_binding_bash_routes(results):
    """FEAT-495: product Bash writes require exact runtime repository lineage."""
    feature = "FEAT-93-product-bash"
    first = _repository_bash_happy_routes(results, feature)
    _repository_bash_missing_and_released(results, feature)
    _repository_bash_stale_and_ambiguous(results, feature)
    _repository_bash_collision_and_unreadable(
        results, feature, first["claim_id"])


def run_bug1304_claim_set():
    """Issue #1304 claim-set cases; frozen guard provenance: a4e8ecf7."""
    results = []
    context = _bug1304_bash_context("harness-backend-dev")
    _bug1304_bash_main_routes(results, context)
    _bug1304_bash_unbound_routes(results, context)
    _bug1304_bash_owner_claim(results, context)
    _bug1304_bash_multi_and_malformed(results, context)
    _runtime_lineage_bash_routes(results, context)
    _bug1304_bash_ambiguous(results, context)
    _bug1304_bash_short_claim(results, context)
    _bug1304_bash_expertise(results, context)
    _bug1304_bash_existing_guards(results, context)
    _bug1304_bash_aged_claim(results, context)
    _bug1304_bash_unreadable(results, context)
    _bug1304_bash_partial_registry(results, context)

    _repository_binding_bash_routes(results)
    _record(results, "[bug1304] ")


def _cases_root():
    """A throwaway checkout for the CASES table (#1962): the live manifest, nothing else.

    Run against the live checkout, the in-domain cases read its in-flight claim registry, so
    any running feature turned five expected passes into claim-worktree refusals and a real
    guard regression became indistinguishable from "a feature is running". This root carries
    the real team-config.yaml (the domain rules under test) and no claim registry.
    """
    root = tempfile.mkdtemp(prefix="bash-guard-cases-")
    os.makedirs(os.path.join(root, ".harness"))
    shutil.copy(os.path.join(ROOT, ".harness", "team-config.yaml"),
                os.path.join(root, ".harness", "team-config.yaml"))
    return init_repo(root, None)


def main():
    cases_root = _cases_root()
    for name, cmd, want, agent in CASES:
        r = fire(cases_root, cmd, agent, cwd=cases_root)
        verb = "should have BLOCKED (2)" if want == 2 else "should have PASSED (0)"
        head = (r.stdout + r.stderr).strip().splitlines()[:2]
        check(name, r.returncode == want,
              "\n".join([f"{verb}, got {r.returncode}"] + [f"| {l}" for l in head]))
    run_t14()
    run_worktree()
    run_worktree_deep()
    run_head_move()
    run_native_remove_retention()
    run_native_remove_identifier()
    run_native_remove_c2()
    run_head_move_global_options()
    run_feat50_checkout_binding()
    run_feat61_feature_checkout_adapter()
    run_feat65_guard_cases()
    run_feat2274_unavailable_cases(cases_root)
    run_bug895_wrong_checkout()
    run_bug1106_bash_route()
    run_bug1304_claim_set()
    run_feat2225_expertise_cli()
    return C.report()


def run_bug895_wrong_checkout():
    """Issue #895 code review (PR #1188): the Bash route must refuse the SAME
    wrong-checkout write check-domain.py (Write/Edit route) already refuses — two
    surfaces disagreeing is a bypass by construction (DEC-151)."""
    root = os.path.join(tempfile.mkdtemp(), "root")
    os.makedirs(os.path.join(root, ".harness"))
    os.makedirs(os.path.join(root, ".git", "worktrees", "OTHER"))
    os.makedirs(os.path.join(root, ".harness", "allowed"))
    with open(os.path.join(root, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    wt = os.path.join(root, ".claude", "worktrees", "OTHER")
    _linked_worktree(wt, root, "OTHER", FIXTURE_MANIFEST)

    target_in_main = os.path.join(root, ".harness", "allowed", "x.txt")
    r = fire(wt, "echo x > %s" % target_in_main)
    ok = (r.returncode == 2 and "BLOCKED" in r.stderr and "is in" in r.stderr
          and "this session is rooted in" in r.stderr)

    # NEGATIVE CONTROL: the same session writing its OWN checkout's copy still works.
    target_own = os.path.join(wt, ".harness", "allowed", "y.txt")
    r_own = fire(wt, "echo x > %s" % target_own)
    ok_own = r_own.returncode == 0

    results = [
        ("bug895 Bash route: worktree session writing into main is refused", ok,
         f"{r.returncode}: {r.stderr}"),
        ("bug895 Bash route NEGATIVE CONTROL: same session, own checkout, still allowed",
         ok_own, f"{r_own.returncode}: {r_own.stderr}"),
    ]
    _record(results)



RUN_ARTIFACT_MANIFEST = """schema_version: 1
teams:
  - name: build
    members:
      - name: harness-backend-dev
        domain:
          - { path: .harness/harness/features/**, upsert: true }
"""


def _run_artifact_fixture():
    root = fixture(RUN_ARTIFACT_MANIFEST)
    digest_rel = ".harness/harness/features/FEAT-99-fixture/runs/r1/digest.md"
    state_rel = ".harness/harness/features/FEAT-99-fixture/runs/r1/state.yaml"
    identity_rel = ".harness/harness/features/FEAT-99-fixture/runs/r1/.run-identity.json"
    other_rel = ".harness/harness/features/FEAT-99-fixture/runs/r1/notes.txt"
    os.makedirs(os.path.dirname(os.path.join(root, digest_rel)), exist_ok=True)
    with open(os.path.join(root, identity_rel), "w") as marker:
        marker.write("{}\n")
    return root, digest_rel, state_rel, identity_rel, other_rel


def run_bug1106_bash_route():
    """Issue #1106, gap (a) on the Bash route. Bash carries no complete incoming payload
    to compare against prior content, so content-based protection (issue #1058's digest
    guard, issues #1124/#1106's state.yaml identity guard, both in check-domain.py) is
    structurally impossible here — a route-only refusal is the weakest sufficient rule."""
    results = []
    root, digest_rel, state_rel, identity_rel, other_rel = _run_artifact_fixture()

    r = fire(root, f"echo hi > {os.path.join(root, digest_rel)}")
    results.append(("bug1106 Bash route: a write to a run's digest.md is REFUSED",
                    r.returncode == 2 and "digest.md or state.yaml" in r.stderr,
                    f"exit {r.returncode}: {r.stderr.strip()[:200]}"))

    r = fire(root, f"echo hi > {os.path.join(root, state_rel)}")
    results.append(("bug1106 Bash route: a write to a run's state.yaml is REFUSED",
                    r.returncode == 2 and "digest.md or state.yaml" in r.stderr,
                    f"exit {r.returncode}: {r.stderr.strip()[:200]}"))

    r = fire(root, f"echo hi > {os.path.join(root, other_rel)}")
    results.append((
        "bug1106 Bash route NEGATIVE CONTROL: an unrelated file in the same run "
        "directory is still ALLOWED — this is not a blanket run-dir Bash ban",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}"))

    r = fire(root, f"echo hi > {os.path.join(root, identity_rel)}")
    results.append((
        "bug1305 Bash route: overwriting the write-once identity witness is refused",
        r.returncode == 2 and "identity witness" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:250]}"))

    r = fire(root, f"rm {os.path.join(root, identity_rel)}")
    results.append((
        "bug1305 Bash route: removing the write-once identity witness is refused",
        r.returncode == 2 and "identity witness" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:250]}"))

    r = fire(root, f"echo hi | tee {os.path.join(root, digest_rel)}")
    results.append((
        "bug1106 Bash route: `tee` onto a run's digest.md is ALSO refused (a path "
        "rule, not a redirect-only one)",
        r.returncode == 2 and "digest.md or state.yaml" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:200]}"))

    # --- CODE REVIEW FINDING (PR #1249): run artifacts normally live inside a
    # feature's own WORKTREE (DEC-95), not the main checkout. The guard must fire there
    # too — it must not be inert behind the DEC-153 carve-out that exists for a
    # different (domain-identity) question. A session rooted at the MAIN checkout,
    # writing into a linked worktree's own run directory, must still be refused.
    wt_tmp = tempfile.mkdtemp()
    wt_root = os.path.join(wt_tmp, "root")
    os.makedirs(os.path.join(wt_root, ".harness"))
    with open(os.path.join(wt_root, ".harness", "team-config.yaml"), "w") as f:
        f.write(RUN_ARTIFACT_MANIFEST)
    wt = os.path.join(wt_root, ".claude", "worktrees", "FEAT-W")
    _linked_worktree(wt, wt_root, "FEAT-W", RUN_ARTIFACT_MANIFEST)
    wt_digest = os.path.join(
        wt, ".harness", "harness", "features", "FEAT-W-thing", "runs", "r1", "digest.md")
    os.makedirs(os.path.dirname(wt_digest), exist_ok=True)
    wt_other = os.path.join(
        wt, ".harness", "harness", "features", "FEAT-W-thing", "runs", "r1", "notes.txt")

    r = fire(wt_root, f"echo hi > {wt_digest}")
    results.append((
        "bug1106 Bash route: a write to digest.md INSIDE A LINKED WORKTREE is ALSO "
        "refused — the guard is checkout-agnostic, not inert behind DEC-153",
        r.returncode == 2 and "digest.md or state.yaml" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:250]}"))

    r = fire(wt_root, f"echo hi > {wt_other}")
    results.append((
        "bug1106 Bash route NEGATIVE CONTROL: an unrelated file inside the same "
        "worktree run directory is still ALLOWED",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}"))
    _record(results)


# ======== FEAT-2225 T-04: governed Bash may not run the Expertise mutators ========
# Every governed persona records Expertise through the `expertise_apply` host tool; the
# CLI's mutating subcommands and the distill merge are the main session's. Refused ahead
# of the reviewer and dev-ops branches, so the four personas below span every branch.
F2225_CLI = ".claude/skills/harness/bin/expertise-merge.py"
F2225_LINK = ".agents/skills/harness/bin/expertise-merge.py"
F2225_GATE = ".agents/skills/harness/bin/merge-gate.py"
F2225_MEMBER = ("member-ops --root /r --feature FEAT-1 --persona harness-qa --runtime-id A "
                "--parent-id B --tier craft --ops -")
F2225_PERSONAS = ("harness-eng-lead", "harness-code-reviewer", "harness-dev-ops",
                  "harness-backend-dev")
F2225_MUTATORS = (
    ("direct executable: member-ops", f"{F2225_CLI} {F2225_MEMBER}"),
    (".agents symlink spelling: apply", f"{F2225_LINK} apply --file x.md --entries - < e.md"),
    ("python3 prefix: ops", f"python3 {F2225_LINK} ops --file x.md --ops ops.json"),
    ("python3 flags, absolute path: replay",
     f"python3 -u /abs/harness/{F2225_CLI} replay --root /r --feature F --base abc"),
    ("env python3 prefix: member-ops", f"env python3 {F2225_LINK} {F2225_MEMBER}"),
    ("/usr/bin/env with an assignment: apply",
     f"/usr/bin/env PYTHONPATH=x python3 {F2225_CLI} apply --file x.md --entries -"),
    ("bash -c nested: apply", f"bash -c 'python3 {F2225_LINK} apply --file x.md --entries -'"),
    ("sh -c nested: replay", f'sh -c "{F2225_CLI} replay --root /r --feature F --base abc"'),
    ("compound after cd: member-ops", f"cd /tmp && python3 {F2225_LINK} {F2225_MEMBER}"),
    ("stdin heredoc: member-ops", f"python3 {F2225_LINK} {F2225_MEMBER} <<'EOF'\n[]\nEOF"),
    ("merge-gate merge-distill", f"python3 {F2225_GATE} merge-distill --root /r --feature F --pr 7"),
    ("bash -c nested merge-distill", f"bash -c '{F2225_GATE} merge-distill --root /r --feature F --pr 7'"),
)
F2225_READS = (
    ("replay --check", f"python3 {F2225_LINK} replay --root /r --feature F --base abc --check"),
    ("verify-receipt", f"python3 {F2225_LINK} verify-receipt --root /r --feature F --claimed -"),
    ("subcommand --help", f"python3 {F2225_LINK} apply --help"),
    ("top-level --help", f"{F2225_CLI} --help"),
    ("nested replay --check", f"bash -c 'python3 {F2225_LINK} replay --root /r --feature F --base a --check'"),
    ("reading the CLI source", f"grep -n member-ops {F2225_LINK}"),
    ("the command quoted as text", f"echo 'python3 {F2225_LINK} apply'"),
)


def _f2225_expect(results, root, agent, name, cmd, want):
    r = fire(root, cmd, agent)
    advised = want == 0 or "expertise_apply" in r.stderr
    results.append((f"feat2225 {agent or 'main session'}: {name}",
                    r.returncode == want and advised,
                    f"exit {r.returncode} (want {want}): {r.stderr.strip()[:240]}"))


def _f2225_cli_matrix(results, root):
    for agent in F2225_PERSONAS:
        for name, cmd in F2225_MUTATORS:
            _f2225_expect(results, root, agent, f"refused {name}", cmd, 2)
        for name, cmd in F2225_READS:
            _f2225_expect(results, root, agent, f"read allowed: {name}", cmd, 0)
    for name, cmd in F2225_MUTATORS:
        _f2225_expect(results, root, None, f"allowed {name}", cmd, 0)


def _f2225_repository_tier(results):
    """A claimed agent's repository-tier Expertise write gets the expertise_apply advice."""
    manifest = FIXTURE_MANIFEST.replace(
        '          - { path: ".", read: true }',
        '          - { path: .harness/expertise/**, upsert: true }\n'
        '          - { path: .harness/*/expertise/**, upsert: true }\n'
        '          - { path: ".", read: true }')
    root = fixture(manifest)
    first = os.path.join(root, ".claude", "worktrees", "FEAT-2225-A")
    _linked_worktree(first, root, "A", manifest)
    agent = "harness-backend-dev"
    inflight_registry.claim(first, agent, "harness-eng-lead", first, feature="FEAT-2225-A-x")
    target = os.path.join(root, ".harness", "harness", "expertise", f"{agent}.md")
    r = fire(root, f"echo x > {target}", agent)
    advice = ("expertise_apply", "tier: repository", "repository: harness")
    results.append(("feat2225 repository-tier Expertise redirect names expertise_apply "
                    "with the repository tier",
                    r.returncode == 2 and all(a in r.stderr for a in advice)
                    and "expertise-merge.py" not in r.stderr,
                    f"exit {r.returncode}: {r.stderr.strip()[:300]}"))


def run_feat2225_expertise_cli():
    """FEAT-2225 T-04: the Bash route refuses governed Expertise mutation."""
    results = []
    _f2225_cli_matrix(results, fixture(FIXTURE_MANIFEST))
    _f2225_repository_tier(results)
    _record(results)


if __name__ == "__main__":
    sys.exit(main())
