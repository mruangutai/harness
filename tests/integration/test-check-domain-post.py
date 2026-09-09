#!/usr/bin/env python3
"""check-domain.sh: the SHAPE gate on the routes PreToolUse cannot reach.

Slice of the former test-check-domain.py (issue #1527) — the --post sweep across all
four write routes, the runs/<id>/state.yaml write path, and the handoff `Done when`
validator. Shared fixtures and the block driver live in check_domain_support.py.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import errno, json, os, shutil, subprocess, sys, tempfile, time
from isolated_bin import isolated_bin
from check_domain_support import (FIXTURE_MANIFEST, HOOK, _env, _handoff_done_when_fixture,
    _handoff_text, _legal_feature_json, drive, fire, fire_post, fixture,
    make_linked_worktree)


# ============ #132: the shape gate on the routes PreToolUse cannot reach ============
# Measured before the fix, ONE 400-line feature.yaml against a 200-line budget:
#   Write/harness-orchestrator exit 2 · Edit exit 0 · Bash exit 0 · Write/MAIN exit 0.
# One route of four. Each case below is one of those routes, run against a REAL file in a
# fixture repo, because the whole point of the post mode is that it reads the disk rather
# than a payload it could have been handed.

POST = []


def post(name, ok, detail=""):
    POST.append((name, ok, detail))


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


def _record_handoff_result(results, name, result, want, needles=None):
    needles = () if needles is None else (
        needles if isinstance(needles, tuple) else (needles,))
    stderr = result.stderr.lower()
    ok = result.returncode == want and all(needle.lower() in stderr for needle in needles)
    results.append((name, ok, f"exit {result.returncode}: {result.stderr.strip()[:180]}"))


def _invoke_handoff(root, target, content):
    payload = {"tool_name": "Write",
               "tool_input": {"file_path": target, "content": content}}
    return subprocess.run([HOOK], input=json.dumps(payload), capture_output=True,
                          text=True, env=_env(root))


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


def main():
    return drive(globals())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
