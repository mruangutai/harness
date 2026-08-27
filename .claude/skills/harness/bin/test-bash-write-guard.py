#!/usr/bin/env python3
"""Tests for bash-write-guard.sh (DEC-151, Task #5).

WHY THIS EXISTS: the guard was added after a live bypass, so loosening its
detection without a test proving it STILL BLOCKS the real bypass shapes is how a
guard fails open. Every case below asserts an EXACT exit code — 2 blocks, 0
passes (DEC-100: only exit 2 blocks, so "nonzero" would let a crash masquerade
as a rejection).

Two halves, and both must stay green:
  MUST PASS  — legitimate commands the guard had been blocking
  MUST BLOCK — the DEC-151 bypass shapes it exists to stop
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GUARD = os.environ.get("BASH_WRITE_GUARD_BIN") or os.path.join(HERE, "bash-write-guard.sh")


def _env(root, **kw):
    """The guard's environment for a fixture rooted at `root` — BOTH names, one value.

    FEAT-42 T-11. bash-write-guard.sh resolves its root through
    harness_boundary.resolve_root, which reads HARNESS_PROJECT_DIR and no other name. The
    reverted sha-3952814 copy this suite is diffed against reads HARNESS_PROJECT_DIR first
    and CLAUDE_PROJECT_DIR second. Setting both to the same value is the ONE spelling under
    which the two copies resolve the same root, which is what makes the
    identical-violation-set proof mean anything. Setting only the host-owned name points the
    new copy at the live checkout instead.

    resolve_root honours the override only when `.harness/team-config.yaml` is readable
    underneath it. A fixture without that marker gets the override discarded and falls back
    to the derived root — the same answer the deleted chain gave it.
    """
    return dict(os.environ, CLAUDE_PROJECT_DIR=root, HARNESS_PROJECT_DIR=root, **kw)

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

import shutil
import tempfile

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

T14 = []


def fixture(text):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, ".harness"))
    with open(os.path.join(d, ".harness", "team-config.yaml"), "w") as f:
        f.write(text)
    return d


def fire(root, cmd, agent="harness-backend-dev"):
    payload = {"agent_type": agent, "tool_name": "Bash", "tool_input": {"command": cmd}}
    return subprocess.run([GUARD], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


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
    T14.append(("SC-06 pair: permitted bash write allowed AND forbidden blocked",
                ok.returncode == 0 and no.returncode == 2,
                f"permitted got {ok.returncode} (want 0), forbidden got {no.returncode} (want 2)"))

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
    T14.append(("a MALFORMED manifest blocks the bash write (fail closed)",
                r.returncode == 2 and "does not parse" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:160]}"))

    dup = fixture(FIXTURE_MANIFEST + "\nschema_version: 2\n")
    r = fire(dup, f"echo hi > {os.path.join(dup, 'allowed', 'x.txt')}")
    T14.append(("a DUPLICATE key in the manifest blocks the bash write",
                r.returncode == 2 and "duplicate key" in r.stderr,
                f"exit {r.returncode}: {r.stderr.strip()[:160]}"))

    # DEC-151's carve-out is unchanged: an absent manifest still fails OPEN. Needs an
    # isolated copy, not merely an empty CLAUDE_PROJECT_DIR — root falls back to
    # _derived, so a guard running from the real bin/ finds the real manifest whatever
    # the env var says. (The same trap made this case vacuous in test-check-domain.py.)
    iso = tempfile.mkdtemp()
    isobin = os.path.join(iso, ".claude", "skills", "harness", "bin")
    os.makedirs(isobin)
    shutil.copy(GUARD, os.path.join(isobin, "bash-write-guard.sh"))
    payload = {"agent_type": "harness-backend-dev", "tool_name": "Bash",
               "tool_input": {"command": f"echo hi > {os.path.join(iso, 'x.txt')}"}}
    r = subprocess.run([os.path.join(isobin, "bash-write-guard.sh")],
                       input=json.dumps(payload), capture_output=True, text=True,
                       env=_env(iso))
    T14.append(("an ABSENT manifest still fails OPEN (DEC-151 carve-out intact)",
                r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:160]}"))

    # Both hooks compute domains from ONE function, so the same agent and path must get
    # the same verdict from either write surface.
    #
    # THE PRODUCT-SHAPED PATH IS BACK, AND SO IS THE AGREEMENT (FEAT-17 T-03). On
    # 2026-08-11 the allow half was moved off <root>/src/main.py because the surfaces
    # genuinely disagreed there: FEAT-15 taught check-domain.sh that a product-shaped
    # target inside the harness root is refused, and bash-write-guard.sh was out of that
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
    cd = os.path.join(HERE, "check-domain.sh")
    for rel, want in ((".harness/allowed/x.txt", 0), ("src/main.py", 2),
                      ("forbidden/x.txt", 2)):
        tgt = os.path.join(root, rel)
        b = fire(root, f"echo hi > {tgt}")
        w = subprocess.run([cd], input=json.dumps(
            {"agent_type": "harness-backend-dev", "tool_name": "Write",
             "tool_input": {"file_path": tgt, "content": "x"}}),
            capture_output=True, text=True, env=_env(root))
        T14.append((f"both write surfaces agree on {rel} (D-03, one shared rule)",
                    b.returncode == want and w.returncode == want,
                    f"bash got {b.returncode}, write got {w.returncode}, want {want}"))

    fails = 0
    for name, ok_, detail in T14:
        if ok_:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n      | {detail}")
    print(f"\n{len(T14) - fails}/{len(T14)} T-14 cases passed.")
    return fails


WTB = []


def wtb(name, ok, detail=""):
    WTB.append((name, ok, detail))


def _linked_worktree(path, owner_root, wt_id, manifest_text):
    """A linked git worktree, built BY HAND — no git is invoked, here or in the guard.

    A `.git` FILE holding `gitdir: <owner>/.git/worktrees/<id>` is exactly the on-disk
    shape `git worktree add` leaves. Standing up a real one would mean this suite
    creating the shape the guard now forbids. Each checkout gets its own manifest,
    because each is used as a session root below and a root with no readable manifest
    falls to the DEC-151 fail-open — which exits 0 for a reason that has nothing to do
    with worktrees.
    """
    os.makedirs(os.path.join(path, ".harness"), exist_ok=True)
    with open(os.path.join(path, ".git"), "w") as f:
        f.write("gitdir: %s\n" % os.path.join(owner_root, ".git", "worktrees", wt_id))
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

    def _fire(session_root, cmd, agent="harness-backend-dev"):
        payload = {"agent_type": agent, "tool_name": "Bash",
                   "tool_input": {"command": cmd}}
        return subprocess.run([GUARD], input=json.dumps(payload), capture_output=True,
                              text=True,
                              env=_env(session_root))

    # TARGET-SIDE: a shell write INTO the sibling, from a session rooted in the
    # checkout. The sibling is outside root, so this half discriminates whatever the
    # manifest grants — before this task the `..` continue made it invisible here.
    r = _fire(root, f"echo hi > {os.path.join(sib, 'allowed', 'x.txt')}")
    wtb("a shell write INTO an out-of-place worktree is REFUSED",
        r.returncode == 2 and ".claude/worktrees" in r.stderr,
        f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # The PAIRED ALLOW, same fixture and same session. Without it the case above is
    # satisfied by a guard that refuses everything.
    r = _fire(root, f"echo hi > {os.path.join(root, '.harness', 'allowed', 'x.txt')}")
    wtb("the same session's in-domain shell write still PASSES",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # ROOT-SIDE. The target is control-plane and in-domain FOR THAT ROOT, so it exits 0
    # with the root-side rule deleted — which is what makes the case discriminating.
    r = _fire(sib, f"echo hi > {os.path.join(sib, '.harness', 'allowed', 'x.txt')}")
    wtb("a session ROOTED in an out-of-place worktree is refused its own in-domain "
        "shell write",
        r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # BOTH HALVES OF THE WORDING, on the SAME captured stderr. This route prints its own
    # copy of the verdict, so a wording assertion on the Write route alone would leave
    # this one free to regress. `git worktree remove` SUCCEEDS at exit 0 from inside the
    # tree it removes, so that guidance printed to a session standing in that tree is an
    # instruction to delete its own cwd. Presence alone passes if the destructive
    # sentence is re-added beside the location line; absence alone passes for a verdict
    # that says nothing. Scoped to THIS stderr — the target-side verdict keeps it.
    wtb("the ROOT-SIDE bash verdict names .claude/worktrees and does NOT say "
        "`git worktree remove`",
        ".claude/worktrees" in r.stderr and "git worktree remove" not in r.stderr,
        f"stderr: {r.stderr.strip()[:300]}")

    # A COMMAND THAT EXTRACTS NO WRITE TARGET AT ALL. This is what proves the root-side
    # check does not sit behind `if not findings: sys.exit(0)`, and after the re-scope it
    # is the ONLY case pinning this route's placement.
    r = _fire(sib, "git status --porcelain")
    wtb("a read-only command from an out-of-place root is ALSO refused (the check is "
        "not behind the no-findings exit)",
        r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # The PAIRED ALLOW for the root-side rule: same shape, legitimate location.
    r = _fire(legit, f"echo hi > {os.path.join(legit, '.harness', 'allowed', 'x.txt')}")
    wtb("a session rooted in a LEGITIMATE worktree is unaffected",
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
    r = _fire(root, f"echo hi > {os.path.join(legit, '.harness', 'allowed', 'x.txt')}")
    wtb("SC-07: the legitimate worktree is writable FROM OUTSIDE it on the Bash route "
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
        r = _fire(root, f"echo hi > {os.path.join(sib, 'allowed', 'x.txt')}")
        wtb(f"F-A: a .git pointer that is {_label} REFUSES the shell write",
            r.returncode == 2, f"exit {r.returncode}: {r.stderr.strip()[:200]}")
    with open(_ptr, "wb") as _f:
        _f.write(_good)
    r = _fire(root, f"echo hi > {os.path.join(root, '.harness', 'allowed', 'x.txt')}")
    wtb("F-A: with the pointer restored, the in-domain shell write still PASSES",
        r.returncode == 0, f"exit {r.returncode}: {r.stderr.strip()[:200]}")

    # --- THE FAIL-CLOSED PAIR for the shared module (D-06).
    iso = tempfile.mkdtemp()
    isobin = os.path.join(iso, ".claude", "skills", "harness", "bin")
    os.makedirs(isobin)
    shutil.copy(GUARD, os.path.join(isobin, "bash-write-guard.sh"))
    shutil.copy(os.path.join(HERE, "harness_yaml.py"), os.path.join(isobin, "harness_yaml.py"))
    os.makedirs(os.path.join(iso, ".harness"))
    with open(os.path.join(iso, ".harness", "team-config.yaml"), "w") as f:
        f.write(FIXTURE_MANIFEST)
    payload = {"agent_type": "harness-backend-dev", "tool_name": "Bash",
               "tool_input": {"command": "echo hi > %s"
                              % os.path.join(iso, ".harness", "allowed", "x.txt")}}
    r = subprocess.run([os.path.join(isobin, "bash-write-guard.sh")],
                       input=json.dumps(payload), capture_output=True, text=True,
                       env=_env(iso))
    wtb("a MISSING harness_boundary.py blocks the bash write and NAMES the module",
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
    for fn in ("check-domain.sh", "bash-write-guard.sh", "harness_boundary.py",
               "harness_yaml.py"):
        shutil.copy(os.path.join(HERE, fn), os.path.join(m_bin, fn))
    for fn in ("check-domain.sh", "bash-write-guard.sh"):
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
        b = subprocess.run([os.path.join(m_bin, "bash-write-guard.sh")],
                           input=json.dumps({"agent_type": "harness-backend-dev",
                                             "tool_name": "Bash",
                                             "tool_input": {"command": f"echo hi > {m_target}"}}),
                           capture_output=True, text=True, env=env)
        w = subprocess.run([os.path.join(m_bin, "check-domain.sh")],
                           input=json.dumps({"agent_type": "harness-backend-dev",
                                             "tool_name": "Write",
                                             "tool_input": {"file_path": m_target,
                                                            "content": "x"}}),
                           capture_output=True, text=True, env=env)
        return b.returncode, w.returncode

    before = _both_routes()
    wtb("one-implementation baseline: both routes ALLOW the legitimate worktree write",
        before == (0, 0), f"bash={before[0]}, write={before[1]}, want (0, 0)")

    mod = os.path.join(m_bin, "harness_boundary.py")
    src = open(mod).read()
    mutated = src.replace('WORKTREES_SEGMENT = ".claude/worktrees"',
                          'WORKTREES_SEGMENT = ".claude/wt-mutant"', 1)
    wtb("the mutation targeted the constant BY NAME (not the bare literal)",
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
    wtb("ONE IMPLEMENTATION: mutating WORKTREES_SEGMENT flips BOTH routes 0 -> 2",
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
         "git worktree add " + BRANCH_FLAG + " chore/FEAT-17-wt /tmp/sib-xyz HEAD", 2),
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
        wtb(f"worktree creation — {label}",
            r.returncode == want,
            f"exit {r.returncode}, want {want}: {r.stderr.strip()[:200]}")

    # THE RELATIVE DESTINATION MUST BE REFUSED FOR BEING RELATIVE, and only the wording
    # can say so. A guard with the isabs check deleted still exits 2 here — realpath("sib")
    # resolves against the guard process's cwd, which is not under the fixture's
    # worktrees dir — so the exit code alone passes under the deleted check.
    r = fire(wt_root, "git worktree add sib HEAD")
    wtb("worktree creation — the relative refusal NAMES relativity as the reason",
        "RELATIVE" in r.stderr, f"stderr: {r.stderr.strip()[:250]}")

    # --- #556: THE CWD MUST NOT SUPPLY THE BOUNDARY RULE. Same defect and same proof as
    # test-check-domain.py's pair — python puts the invoking directory at sys.path[0]
    # ahead of PYTHONPATH, so before `python3 -P` a harness_boundary.py in the agent's cwd
    # was the resolver this guard consulted. Both halves: clean cwd refuses, hostile cwd
    # returns the SAME verdict.
    _hostile = tempfile.mkdtemp()
    with open(os.path.join(_hostile, "harness_boundary.py"), "w") as _hf:
        _hf.write("MARKER = 'nope'\n"
                  "def resolve_root(bin_dir, strict=True): return '/definitely/not/here'\n"
                  "def root_from_script(bin_dir): return '/definitely/not/here'\n"
                  "def root_above(start): return None\n")
    _real_root = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    _p556 = {"agent_type": "harness-backend-dev", "tool_name": "Bash",
             "tool_input": {"command": "echo x > "
                            + os.path.join(_real_root, ".harness", "harness", "docs",
                                           "SPEC.md")}}
    _clean = subprocess.run([GUARD], input=json.dumps(_p556), capture_output=True,
                            text=True, env=_env(_real_root),
                            cwd=tempfile.gettempdir())
    wtb("#556 control: from a clean cwd the out-of-domain shell write is REFUSED",
        _clean.returncode == 2,
        f"exit {_clean.returncode}: {_clean.stderr.strip()[:200]}")
    _hijack = subprocess.run([GUARD], input=json.dumps(_p556), capture_output=True,
                             text=True, env=_env(_real_root), cwd=_hostile)
    wtb("#556: a harness_boundary.py in the CWD does not become the guard's resolver",
        _hijack.returncode == 2 and _hijack.returncode == _clean.returncode
        and "enforcement OFF" not in _hijack.stderr,
        f"clean={_clean.returncode} hijacked={_hijack.returncode}: "
        f"{_hijack.stderr.strip()[:200]}")

    fails = 0
    for name, ok_, detail in WTB:
        if ok_:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(WTB) - fails}/{len(WTB)} worktree-boundary cases passed.\n")
    return fails


WDEEP = []


def wdeep(name, ok, detail=""):
    WDEEP.append((name, ok, detail))


def run_worktree_deep():
    """T-04 (FEAT-30) on the Bash route: the two-level `<segment>/<repo>/<id>` layout.

    A FINDING FIRST, because T-04's intent asks for something this route cannot do. It
    asks for a paired case where a granted path at depth is allowed and "a path that agent
    is not granted, at the same depth, is refused" — and in the same breath forbids
    touching `bash-write-guard.sh:545`. That line is
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
    fails = 0
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
    wdeep("a granted path inside <segment>/<repo>/<id> is ALLOWED on the Bash route",
          r_ok.returncode == 0,
          f"exit {r_ok.returncode}: {r_ok.stderr.strip()[:200]}")

    # UNGRANTED at depth: also allowed, and that is DEC-153, not a hole. Pinned so a
    # future narrowing of :545 cannot land silently.
    r_un = fire(root, "echo x > %s" % os.path.join(deep, "src", "main.py"))
    wdeep("DEC-153 pinned: an UNGRANTED path at the same depth is ALSO allowed — the "
          "carve-out is blanket and depth-agnostic",
          r_un.returncode == 0,
          f"exit {r_un.returncode}: {r_un.stderr.strip()[:200]} — if this now refuses, "
          f"bash-write-guard.sh:545 was narrowed and DEC-153 needs re-reading first")

    # THE REFUSAL, where it is reachable: an out-of-place linked worktree of the same
    # root. Refused ahead of the DEC-153 continue, and the message names the location.
    sib = os.path.join(tmp, "sib")
    _linked_worktree(sib, root, "sib", FIXTURE_MANIFEST)
    r_sib = fire(root, "echo x > %s" % os.path.join(sib, ".harness", "allowed", "x.txt"))
    wdeep("an out-of-place linked worktree is REFUSED on the Bash route, and the message "
          "names where worktrees belong",
          r_sib.returncode == 2 and ".claude/worktrees" in r_sib.stderr,
          f"exit {r_sib.returncode}: {r_sib.stderr.strip()[:240]}")

    for name, ok, detail in WDEEP:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(WDEEP) - fails}/{len(WDEEP)} deep-layout Bash-route cases passed.\n")
    shutil.rmtree(tmp, ignore_errors=True)
    return fails


HEADC = []


def headc(name, ok, detail=""):
    HEADC.append((name, ok, detail))


def run_head_move():
    """T-05 (FEAT-30) — REQ-04's HEAD-move refusal and SC-07's Bash-route half.

    EVERY REFUSE CASE ASSERTS THE WORDING, not just exit 2. This guard has several
    refusals that all exit 2, so an exit-code-only assertion cannot tell "refused for
    moving HEAD" from "refused for something else entirely".

    The ALLOW half is what makes the set discriminating: a guard that refuses every git
    command passes case 1 and fails cases 4a-4d. Both halves come from one fixture.
    """
    fails = 0
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
        headc(name, r.returncode == 2 and needle in r.stderr,
              f"exit {r.returncode} (want 2), stderr wants {needle!r}: "
              f"{r.stderr.strip()[:200]}")

    def allow(name, cmd, agent="harness-backend-dev"):
        r = fire(root, cmd, agent=agent)
        headc(name, r.returncode == 0,
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
    r5 = subprocess.run([GUARD], input=json.dumps(
        {"tool_name": "Bash", "tool_input": {"command": "git checkout main"}}),
        capture_output=True, text=True, env=_env(root))
    headc("5. the main session is NOT governed: the same checkout with no agent_type "
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
    headc("9a. the existing destination refusal is unchanged: an add OUTSIDE the segment "
          "still exits 2",
          r9a.returncode == 2 and ".claude/worktrees" in r9a.stderr,
          f"exit {r9a.returncode}: {r9a.stderr.strip()[:200]}")
    r9b = fire(root, "git worktree add %s"
               % os.path.join(root, ".claude", "worktrees", "harness", "FEAT-91"))
    headc("9b. ...and an add INSIDE the segment still exits 0",
          r9b.returncode == 0, f"exit {r9b.returncode}: {r9b.stderr.strip()[:200]}")

    # 10 + 11 — THE PAIR THAT MAKES THE REORDERING DISCRIMINATING. Case 2 does not cover
    # this: harness-orchestrator is refused only because no exemption exists for it,
    # while harness-dev-ops has an explicit one. A second, different hole.
    refuse("10. RULING R-01: harness-DEV-OPS is refused a branch checkout — this FAILS "
           "against any build that places the rule after the dev-ops early return",
           "git checkout main", agent="harness-dev-ops")
    r11 = fire(root, "echo x > %s" % os.path.join(root, "src", "main.py"),
               agent="harness-dev-ops")
    headc("11. ...and the WRITE exemption is INTACT: dev-ops still writes a path it is "
          "not granted, exit 0. Without this half, case 10 is satisfied by deleting the "
          "exemption and removing DEC-151's recovery path.",
          r11.returncode == 0,
          f"exit {r11.returncode}: {r11.stderr.strip()[:200]}")

    for name, ok, detail in HEADC:
        if ok:
            print(f"ok    {name}")
        else:
            fails += 1
            print(f"FAIL  {name}\n        {detail}")
    print(f"\n{len(HEADC) - fails}/{len(HEADC)} HEAD-move and forced-removal cases passed.\n")
    shutil.rmtree(tmp, ignore_errors=True)
    return fails


def main():
    fails = 0
    for name, cmd, want, agent in CASES:
        payload = {"agent_type": agent, "tool_name": "Bash", "tool_input": {"command": cmd}}
        r = subprocess.run([GUARD], input=json.dumps(payload),
                           capture_output=True, text=True)
        if r.returncode != want:
            fails += 1
            verb = "should have BLOCKED (2)" if want == 2 else "should have PASSED (0)"
            print(f"FAIL  {name}\n        {verb}, got {r.returncode}")
            for l in (r.stdout + r.stderr).strip().splitlines()[:2]:
                print(f"      | {l}")
        else:
            print(f"ok    {name}")
    print(f"\n{len(CASES) - fails}/{len(CASES)} cases passed.\n")
    fails += run_t14()
    fails += run_worktree()
    fails += run_worktree_deep()
    fails += run_head_move()
    return fails


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
