#!/usr/bin/env python3
"""check-domain.sh: which CHECKOUT and which CWD a verdict is bound to.

Slice of the former test-check-domain.py (issue #1527) — the worktree boundary, the
deep-layout shape cases, the clean-tracked sweep, BUG-895's wrong-checkout refusals
and B-2's cwd independence. The grant-parity block is a file of its own
(test-check-domain-worktree-parity.py) because it alone is a ~6s serial run.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json, os, shutil, subprocess, sys, tempfile, time
from check_domain_support import (FIXTURE_MANIFEST, HERE, HOOK, ROOT, _env,
    _legal_feature_json, drive, fire_post, fixture, make_linked_worktree)


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


def main():
    return drive(globals())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
