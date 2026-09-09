#!/usr/bin/env python3
"""check-state.sh INV-25, INV-27, INV-29 and INV-31: the checkout itself.

Sliced out of tests/integration/test-check-state.py (issue #1527). Every fixture here is
a REAL git repository — an out-of-place worktree (INV-25), the layout-migration invariant
at the session-entry call site (INV-27), a worktree outliving its feature's terminal
status (INV-29) and this clone's merge hook (INV-31) all read git itself, so a hand-built
.git pointer would grade nothing.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import json
import os
import re
import subprocess
import sys
import shutil
import tempfile
from check_state_support import (HARNESS_JSON_SYNC_OFF, SCRIPT, make_fixture, run,
    _HOOKS_REL_T, _hb, _root_env)


def case_u():
    """INV-25 (issue #103): an out-of-place worktree red-gates session entry.

    Built with REAL git, deliberately. The test process is not the Bash tool route, so
    it may create the shapes T-04 now forbids there — and INV-25 reads
    `git worktree list --porcelain`, so a hand-built .git pointer would not appear in
    that output at all and the case would pass vacuously.

    EVERY DIRECTORY USED AS A RUN ROOT GETS make_fixture. check-state.sh exits 1 with
    "project not onboarded" before any invariant runs, so a bare worktree root would
    exit non-zero while printing no INV-25 line, and these assertions could never be
    satisfied by correct code.
    """
    results = []

    def _repo(path):
        os.makedirs(path, exist_ok=True)
        for cmd in (["git", "init", "-q"],
                    ["git", "config", "user.email", "t@example.com"],
                    ["git", "config", "user.name", "t"]):
            subprocess.run(cmd, cwd=path, capture_output=True)
        with open(os.path.join(path, "f.txt"), "w") as f:
            f.write("x\n")
        subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=path, capture_output=True)
        return path

    def _add_wt(repo, dest):
        subprocess.run(["git", "worktree", "add", "-q", dest, "HEAD"],
                       cwd=repo, capture_output=True)
        return dest

    def _inv25_lines(out):
        return [l for l in out.splitlines() if "INV-25" in l]

    with tempfile.TemporaryDirectory() as tmp:
        # --- repo A: the PAIRED ALLOW. One worktree, in the legitimate location.
        # Without this the case cannot tell a working invariant from one that flags
        # every worktree it sees.
        a = _repo(os.path.join(tmp, "A"))
        _add_wt(a, os.path.join(a, ".claude", "worktrees", "wt"))
        make_fixture(a, '{}', "  parent: 40")
        _code_a, out_a = run(a)
        ok = not _inv25_lines(out_a)
        results.append(("(u.1) a worktree UNDER .claude/worktrees/ is silent", ok,
                        "\n".join(_inv25_lines(out_a))))

        # --- repo B: FORBIDDEN. A sibling outside the checkout, and the session is NOT
        # standing in it — so branch 3, which keeps the removal guidance.
        b = _repo(os.path.join(tmp, "B"))
        sib = _add_wt(b, os.path.join(tmp, "B-sib"))
        make_fixture(b, '{}', "  parent: 40")
        code_b, out_b = run(b)
        b_lines = [l for l in _inv25_lines(out_b) if os.path.realpath(sib) in l or sib in l]
        # SEVERITY IS ASSERTED ON THE LINE'S OWN PREFIX, not on the run's exit code. The
        # fixture is red for other reasons already, so `code != 0` passes with INV-25
        # demoted to a note — measured. VIOLATION vs note is the only thing that
        # discriminates, and the write guards now REFUSE writes in such a tree, so a
        # note would be the same silence in a quieter font.
        results.append(("(u.2) a sibling worktree is a VIOLATION, not a note",
                        bool(b_lines) and all("VIOLATION" in l for l in b_lines),
                        f"exit {code_b}; INV-25 lines: {_inv25_lines(out_b)}"))

        # THE PAIRED POSITIVE FOR THE BRANCH. Without it, the negative asserted on repo C
        # below is satisfiable by stripping removal guidance from EVERY branch — the
        # opposite defect, and nothing else in this suite would catch it. This is what
        # proves the branch actually branches.
        results.append(("(u.3) the not-my-root branch DOES carry `git worktree remove`",
                        bool(b_lines) and any("git worktree remove" in l for l in b_lines),
                        f"lines: {b_lines}"))

        # --- repo C: FORBIDDEN, own-root branch, plus the base-discriminating allow.
        # Two worktrees from the same mechanism: one out of place, which is ALSO the
        # session root, and one legitimate under the MAIN checkout.
        c = _repo(os.path.join(tmp, "C"))
        own = _add_wt(c, os.path.join(tmp, "C-own"))
        legit = _add_wt(c, os.path.join(c, ".claude", "worktrees", "legit"))
        make_fixture(own, '{}', "  parent: 40")
        code_c, out_c = run(own)
        c_lines = _inv25_lines(out_c)
        own_lines = [l for l in c_lines if os.path.realpath(own) in l or own in l]
        results.append(("(u.4) a session ROOTED in an out-of-place worktree is a "
                        "VIOLATION too — severity does not branch",
                        bool(own_lines) and all("VIOLATION" in l for l in own_lines),
                        f"exit {code_c}; INV-25 lines: {c_lines}"))

        # THE BASE-DISCRIMINATING PAIRED ALLOW, scoped BY PATH and not by the run — repo
        # C legitimately prints one INV-25 line for its own root, so asserting the run
        # prints none would contradict u.4.
        #
        # This is the assertion that pins the comparison base to the MAIN CHECKOUT. With
        # the base taken from the session root, `legit` sits outside
        # <root>/.claude/worktrees/, is not the session root and is not prunable — so it
        # falls to branch 3 and is handed `git worktree remove` on a correct tree. Repo
        # A's allow cannot detect this: there the run root and the main checkout are the
        # same directory and both bases agree.
        legit_lines = [l for l in c_lines if os.path.realpath(legit) in l or legit in l]
        results.append(("(u.5) the LEGITIMATE worktree under the main checkout is silent "
                        "even from an out-of-place root",
                        not legit_lines, f"lines: {legit_lines}"))

        # THE WORDING, both halves, on THAT LINE ONLY. Asserting over the whole run would
        # redden correct code the moment any other flagged entry printed the string.
        # Presence alone passes if the removal sentence is re-added beside the location
        # line; absence alone passes for a line that says nothing useful.
        results.append(("(u.6) the own-root line names .claude/worktrees and does NOT say "
                        "`git worktree remove`",
                        bool(own_lines)
                        and all(".claude/worktrees" in l for l in own_lines)
                        and all("git worktree remove" not in l for l in own_lines),
                        f"lines: {own_lines}"))

    # --- F-B: THE FOURTH IMPORT ROUTE. The three in the two write guards fail closed;
    # this one absorbed the ImportError, skipped every INV-25 branch, printed
    # "all state invariants hold" and exited 0. Found by the review panel, with zero
    # coverage: u.1-u.6 all have the module, and SC-10's module-absent fixture is a
    # different file. An isolated copy is required — a check-state running from the real
    # bin/ finds the real module whatever the fixture looks like.
    with tempfile.TemporaryDirectory() as tmp2:
        isobin = os.path.join(tmp2, ".agents", "skills", "harness", "bin")
        os.makedirs(isobin)
        _bin = os.path.dirname(os.path.abspath(SCRIPT))
        for fn in ("check-state.sh", "harness_yaml.py"):
            shutil.copy(os.path.join(_bin, fn), os.path.join(isobin, fn))
        os.chmod(os.path.join(isobin, "check-state.sh"), 0o755)
        b = _repo(os.path.join(tmp2, "B"))
        _add_wt(b, os.path.join(tmp2, "B-sib"))
        make_fixture(b, '{}', "  parent: 40")
        env = _root_env(b)
        r = subprocess.run([os.path.join(isobin, "check-state.sh")], cwd=b,
                           capture_output=True, text=True, env=env)
        # THE VERDICT MOVED FROM A FINDING TO A REFUSAL, and it moved LOUDER (FEAT-42
        # T-12). check-state.sh now resolves its own root through harness_boundary, so a
        # tree where that module cannot be imported is one this script cannot even locate
        # — it exits 2 before any invariant runs, naming the module on stderr, instead of
        # exiting 1 with an INV-25 CANNOT RUN line. The property this case exists to hold
        # is unchanged and is still asserted in full: an unimportable harness_boundary is
        # NEVER silent and NEVER reports a clean tree.
        results.append(("(u.7) F-B: an unimportable harness_boundary.py is a REFUSAL that "
                        "names it, not a silent skip of INV-25",
                        r.returncode == 2
                        and "harness_boundary" in r.stderr
                        and "all state invariants hold" not in r.stdout,
                        f"exit {r.returncode}: out={r.stdout.strip()[:200]} "
                        f"err={r.stderr.strip()[:200]}"))

    all_ok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - case {name}")
        if not ok:
            all_ok = False
            print(f"        {str(detail).strip()[:300]}")
    return all_ok


def case_x():
    """INV-27 (FEAT-20 T-02): the layout invariant at the session-entry call site.

    Existing fixtures hold no coupled reader and no control-plane marker, so under
    D-04 they are NOT APPLICABLE and INV-27 appends nothing — which is exactly why
    every case above keeps passing. The applicable trees are built ONLY here, by
    writing the marker and reader stubs explicitly; the shared helper is untouched
    on purpose (a stub in it would put an INV-27 verdict inside every unrelated case).
    """
    results = []
    import layout_fixtures as lf
    import layout_migration as lm
    STUBS = {rel: forms["legacy"] for rel, forms in lf.STUB.items()}

    def build(tmp, marker=True, overrides=None, evidence=True):
        h = os.path.join(tmp, ".harness")
        os.makedirs(h, exist_ok=True)
        with open(os.path.join(h, "harness.json"), "w") as f:
            f.write(HARNESS_JSON_SYNC_OFF)
        with open(os.path.join(h, "team-config.yaml"), "w") as f:
            f.write(STUBS[".harness/team-config.yaml"])
        if evidence:
            # LEGACY on purpose: case_x's reader stubs are all legacy-form, so its
            # evidence must be legacy too — a legacy sandbox is a valid detector
            # input in every era, and segmenting only the evidence made x.3's
            # "clean" tree an undeclared-segment cannot-verify.
            fd = os.path.join(h, "features", "FEAT-Z")
            os.makedirs(fd, exist_ok=True)
            open(os.path.join(fd, "feature.json"), "w").write(
                json.dumps({"feature_id": "FEAT-Z", "branch": "b", "pr": None,
                            "status": "Done", "review_sha": "abc1234",
                            "cycles_used": 0, "max_total_cycles": 10, "runs": []}))
            dd = os.path.join(tmp, "docs", "harness")
            os.makedirs(dd, exist_ok=True)
            open(os.path.join(dd, "SPEC.md"), "w").write("# spec\n")
        if marker:
            mp = os.path.join(tmp, lm.MARKER)
            os.makedirs(os.path.dirname(mp), exist_ok=True)
            open(mp, "w").write(lf.FLEET_TEXT)
        overrides = overrides or {}
        for rel, text in STUBS.items():
            if rel == ".harness/team-config.yaml":
                continue
            p = os.path.join(tmp, *rel.split("/"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(overrides.get(rel, text))
        return tmp

    inv = lambda out: [l for l in out.splitlines() if "INV-27" in l]

    # x.1 a tree the detector REDDENS: legacy evidence, one reader migrated. Assert the
    # tag AND the remedy here, not only in the unit suite — this is the only automated
    # evidence the session-entry call site renders them at all.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp, overrides={
            ".agents/skills/harness/bin/gen-decisions-index.py":
                'HEADER = "the authority is .harness/repoA/docs/DECISIONS.md"\n'})
        code, out = run(tmp)
        ls = inv(out)
        ok = (code == 1 and ls
              and any("gen-decisions-index.py" in l and "[migrated]" in l
                      and "atomic commit" in l for l in ls))
        results.append(("(x.1) a mixed tree -> exit 1, INV-27 names the reader, its "
                        "form-set tag and the remedy", ok, "\n".join(ls) or out[-400:]))

    # x.2 a tree it CANNOT JUDGE: one reader carries neither form.
    with tempfile.TemporaryDirectory() as tmp:
        # THE BLANKED FILE MUST STILL BE A READER. factory_config.py stood here until
        # FEAT-42 T-04 deleted its root resolution wholesale and its row left
        # layout_migration.READER_TABLE with it, so blanking it stopped producing
        # [neither] and produced silence. harness_boundary.py is a docs-surface reader
        # that survives, and layout_fixtures asserts STUB and READER_TABLE agree, so a
        # future row deletion breaks this at import rather than here.
        build(tmp, overrides={
            ".agents/skills/harness/bin/harness_boundary.py": "nothing relevant\n"})
        code, out = run(tmp)
        ls = inv(out)
        ok = code == 1 and any("CANNOT VERIFY" in l and "[neither]" in l for l in ls)
        results.append(("(x.2) an unjudgeable tree -> exit 1, INV-27 CANNOT VERIFY",
                        ok, "\n".join(ls) or out[-400:]))

    # x.3 an APPLICABLE clean tree: marker present, every reader legacy, legacy
    # evidence on both surfaces. Assert the ABSENCE of INV-27 specifically, not merely
    # exit 0 — a case that passes because the invariant never ran must be
    # distinguishable from one that passes because it ran clean.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp)
        _code, out = run(tmp)
        ls = inv(out)
        results.append(("(x.3) an applicable clean tree -> NO INV-27 line",
                        not ls, "\n".join(ls)))

    # x.4 no marker: the product-repository and existing-fixture case, pinned
    # deliberately rather than left as an emergent property.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp, marker=False)
        _code, out = run(tmp)
        ls = inv(out)
        results.append(("(x.4) no control-plane marker -> NO INV-27 line",
                        not ls, "\n".join(ls)))

    # x.5 layout_migration unimportable -> the CANNOT RUN wording, exit 1. The script
    # prepends ITS OWN dir to PYTHONPATH, so a shadow dir cannot outrank the real
    # module. Faithful route: run a COPY of check-state.sh from a bin dir holding its
    # one hard import (harness_yaml) and NO layout_migration.py — the same failure an
    # operator gets when the module is deleted from the tree.
    with tempfile.TemporaryDirectory() as tmp:
        build(tmp)
        import shutil
        bindir = os.path.join(tmp, "binx")
        os.makedirs(bindir)
        shutil.copy(SCRIPT, os.path.join(bindir, "check-state.sh"))
        # EVERY MODULE EXCEPT layout_migration.py, STATED AS THAT RATHER THAN AS A LIST.
        #
        # This was an explicit list of the script's imports, and the list was the defect. It
        # named harness_yaml, then harness_boundary when FEAT-42 T-12 added it, and each time
        # the script gained an import this case went red for the WRONG module — the script
        # refusing on a missing dependency before any invariant ran, reported as "INV-27 did
        # not say CANNOT RUN". FEAT-41 T-07 hit it again with factory_config, whose own
        # transitive closure is seven modules (factory_cli, factory_gh, gh_cost_log,
        # gh_issues ...), none of which this case has anything to say about.
        #
        # The case's actual premise is "a bin directory complete but for layout_migration.py",
        # so that is what is built. Self-maintaining: a new import needs no edit here, and the
        # one absence under test cannot be diluted by an unrelated one.
        for _f in sorted(os.listdir(os.path.dirname(SCRIPT))):
            if not _f.endswith(".py") or _f == "layout_migration.py":
                continue
            shutil.copy(os.path.join(os.path.dirname(SCRIPT), _f),
                        os.path.join(bindir, _f))
        env = dict(os.environ)
        env = _root_env(tmp, env)
        r = subprocess.run([os.path.join(bindir, "check-state.sh")],
                           cwd=tmp, capture_output=True, text=True, env=env)
        ls = inv(r.stdout)
        ok = r.returncode == 1 and any("CANNOT RUN" in l for l in ls)
        results.append(("(x.5) unimportable layout_migration -> INV-27 CANNOT RUN, "
                        "exit 1", ok, "\n".join(ls) or r.stdout[-400:]))

    allok = True
    for name, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - {name}")
        if not ok and detail:
            print("      " + detail.replace("\n", "\n      "))
        allok = allok and ok
    return allok


# --- FEAT-34 T-07 — INV-29 -----------------------------------------------------------
#
# BUILT WITH REAL GIT, for case_u's stated reason and one more of its own. INV-29 reads
# `git worktree list --porcelain` through worktree_terminal, so a hand-built `.git` pointer
# never appears in that output and every assertion would pass vacuously. It ALSO reads the
# feature's status from the DEFAULT BRANCH via `git show`, so a fixture that only writes a
# file on disk grades nothing about REQ-05.

def _i29_repo(path, branch="main"):
    os.makedirs(path, exist_ok=True)
    for cmd in (["git", "init", "-q", "-b", branch],
                ["git", "config", "user.email", "t@example.com"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=path, capture_output=True)
    with open(os.path.join(path, "f.txt"), "w") as f:
        f.write("x\n")
    subprocess.run(["git", "add", "f.txt"], cwd=path, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=path, capture_output=True)
    return path


def _i29_land(repo, feature_id, status_or_raw, repo_segment="harness", plan_station=None):
    """Commit the feature's `feature.json` ON THE CURRENT BRANCH. `status_or_raw` is a dict
    written as JSON, or a raw string written verbatim for the unparseable case.

    `plan_station` commits a sibling plan.yaml carrying that station in the SAME commit
    (FEAT-41 T-07) — INV-29 reads the landed station from there now. A dict carrying a
    `status` key has it LIFTED into that plan rather than left in feature.json, so the
    existing call sites keep their shape."""
    if isinstance(status_or_raw, dict) and "status" in status_or_raw:
        status_or_raw = dict(status_or_raw)
        plan_station = str(status_or_raw.pop("status")).lower()
    rel = os.path.join(".harness", repo_segment, "features", feature_id, "feature.json")
    ab = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(ab), exist_ok=True)
    with open(ab, "w") as f:
        if isinstance(status_or_raw, str):
            f.write(status_or_raw)
        else:
            json.dump(status_or_raw, f)
    paths = [rel]
    if plan_station is not None:
        prel = os.path.join(".harness", repo_segment, "features", feature_id, "plan.yaml")
        with open(os.path.join(repo, prel), "w") as f:
            f.write(f"feature: {feature_id}\nstatus: {plan_station}\ntasks: []\n")
        paths.append(prel)
    subprocess.run(["git", "add"] + paths, cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "land " + feature_id], cwd=repo, capture_output=True)


def _i29_wt(repo, worktree_id, repo_segment="harness"):
    dest = os.path.join(repo, ".claude", "worktrees", repo_segment, worktree_id)
    subprocess.run(["git", "worktree", "add", "-q", "-b", "wt-" + worktree_id,
                    dest, "HEAD"], cwd=repo, capture_output=True)
    return dest


def _i29_lines(out):
    return [l for l in out.splitlines() if "INV-29" in l]


def _i29_for(out, path):
    real = os.path.realpath(path)
    return [l for l in _i29_lines(out) if path in l or real in l]


def case_inv29():
    """INV-29 (FEAT-34 T-07): a worktree must not survive its feature reaching a terminal
    state. Six lettered groups, each asserted separately.

    SEVERITY IS ASSERTED ON THE FINDING LINE'S OWN PREFIX, NEVER ON THE RUN'S EXIT CODE.
    `:1214-1218` above already records as a measurement that these fixtures are red for other
    reasons, so a comparison against a non-zero exit code passes whether or not the invariant
    fired. Every assertion below reads the INV-29 line itself.
    """
    results = []

    # ---- (a) the firing pair, and its PAIRED SILENCE ------------------------------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "A"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        lines = _i29_for(out, wt)
        ok = len(lines) == 1 and lines[0].strip().startswith("VIOLATION")
        results.append(("(a.1) default branch Done + standing worktree -> one INV-29 at "
                        "VIOLATION", ok, "\n".join(_i29_lines(out))))

    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "A2"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Review"})
        wt = _i29_wt(r, "FEAT-T29")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        # THE PAIRED SILENCE IS NOT DECORATION. Without it the group cannot tell a working
        # invariant from one that flags every worktree it sees.
        ok = not _i29_for(out, wt)
        results.append(("(a.2) the SAME fixture at Review -> no INV-29 line at all", ok,
                        "\n".join(_i29_lines(out))))

    # ---- (b) the message, graded as composed content, not as a substring ----------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "B"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        _i29_land(r, "FEAT-OTHER", {"feature_id": "FEAT-OTHER", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        other = _i29_wt(r, "FEAT-OTHER")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        mine = _i29_for(out, wt)
        line = mine[0] if mine else ""
        # THE THREE RED INPUTS THE CRITERION NAMES, each its own claim:
        #   1. a message naming the directory but carrying NO command;
        #   2. a bare removal command with no identity in it;
        #   3. a command carrying ANOTHER worktree's identity.
        names_dir = wt in line or os.path.realpath(wt) in line
        has_cmd = "feature-worktree.py remove" in line
        carries_own = "--id FEAT-T29" in line and "--repo harness" in line
        not_other = "FEAT-OTHER" not in line
        results.append(("(b.1) the line NAMES the worktree directory found", names_dir, line))
        results.append(("(b.2) the line CARRIES the removal command", has_cmd, line))
        results.append(("(b.3) the command carries THIS worktree's own repo and id",
                        carries_own, line))
        results.append(("(b.4) and NOT the sibling worktree's identity", not_other, line))
        # The sibling must get its OWN line — proving the composition is per record and not
        # one message reused.
        theirs = _i29_for(out, other)
        ok_sib = len(theirs) == 1 and "--id FEAT-OTHER" in theirs[0]
        results.append(("(b.5) the sibling worktree gets its own line with its own id",
                        ok_sib, "\n".join(theirs)))

    # ---- (c) SC-02, THE DEADLOCK: the default branch decides, never the working tree -----
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "C"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Review"})
        wt = _i29_wt(r, "FEAT-T29")
        # The WORKING TREE inside the worktree says Done; the default branch still says
        # Review. An implementation reading the working tree fires here and must not.
        wpath = os.path.join(wt, ".harness", "harness", "features", "FEAT-T29",
                             "feature.json")
        os.makedirs(os.path.dirname(wpath), exist_ok=True)
        with open(wpath, "w") as f:
            json.dump({"feature_id": "FEAT-T29", "status": "Done"}, f)
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        ok = not _i29_for(out, wt)
        results.append(("(c.1) working tree Done, default branch Review -> silent", ok,
                        "\n".join(_i29_lines(out))))

    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "C2"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        wpath = os.path.join(wt, ".harness", "harness", "features", "FEAT-T29",
                             "feature.json")
        with open(wpath, "w") as f:
            json.dump({"feature_id": "FEAT-T29", "status": "Review"}, f)
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        ok = len(_i29_for(out, wt)) == 1
        # BOTH HALVES ARE ASSERTED. A working-tree read fails c.1 by firing and fails c.2 by
        # staying silent, so the pair is what demonstrates the failing state, not either one.
        results.append(("(c.2) the INVERSE — default branch Done, working tree Review -> "
                        "one line", ok, "\n".join(_i29_lines(out))))

    # ---- (d) SC-03, the dirty clauses, graded ONE AT A TIME -----------------------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "D"))
        _i29_land(r, "FEAT-T29", {"feature_id": "FEAT-T29", "status": "Done"})
        wt = _i29_wt(r, "FEAT-T29")
        with open(os.path.join(wt, "f.txt"), "a") as f:
            f.write("dirty\n")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        mine = _i29_for(out, wt)
        line = mine[0] if mine else ""
        results.append(("(d.1) a dirty Done worktree still fires", bool(mine), line))
        results.append(("(d.2) the message says the tree is DIRTY", "dirty" in line.lower(),
                        line))
        # NOT ONE COMBINED SUBSTRING. The two claims are separate because a message could
        # carry either alone and a single match would not notice.
        results.append(("(d.3) and says remove will DECLINE until the changes are dealt with",
                        "DECLINE" in line, line))

    # ---- (e) SC-04, a SECOND repository, from ONE check-state.sh run --------------------
    #
    # THE FIXTURE IS FLEET-RESOLVED, per D-10, and is NOT a directory placed under the
    # harness checkout's own WORKTREES_SEGMENT — no such second repository can exist, because
    # feature-worktree.py's dest_for joins WORKTREES_SEGMENT only to a resolved owner_root.
    # RED PROOF: an INV-29 built on classify(root) rather than classify_all(root) satisfies
    # (a) through (d) and (f) and fails exactly this.
    with tempfile.TemporaryDirectory() as tmp:
        probe = _i29_repo(os.path.join(tmp, "P"))
        # THE MARKER IS LOAD-BEARING, not scaffolding. factory_config resolves FLEET_PATH
        # through harness_boundary.resolve_root, which honours the override only when that
        # directory holds a readable .harness/team-config.yaml — otherwise it falls back to
        # the SCRIPT's own location and FLEET_PATH resolves to the REAL harness fleet.
        # Without this file the case reads the live fleet.yaml, finds no declared checkout on
        # disk, and passes or fails for a reason that has nothing to do with the fixture.
        # A docs/SPEC.md probe stood here until FEAT-42 T-04 replaced the resolver.
        _mp = os.path.join(probe, _hb.MARKER)
        os.makedirs(os.path.dirname(_mp), exist_ok=True)
        with open(_mp, "w") as f:
            f.write("agents: {}\n")
        ws = os.path.join(tmp, "ws")
        os.makedirs(ws, exist_ok=True)
        second = _i29_repo(os.path.join(ws, "second"))
        _i29_land(second, "FEAT-T29B", {"feature_id": "FEAT-T29B", "status": "Done"},
                  repo_segment="second")
        wt2 = _i29_wt(second, "FEAT-T29B", repo_segment="second")
        fdir = os.path.join(probe, ".harness", "factory")
        os.makedirs(fdir, exist_ok=True)
        with open(os.path.join(fdir, "fleet.yaml"), "w") as f:
            f.write("schema: factory-fleet/1\n"
                    "repos:\n"
                    "  - name: t/second\n"
                    "    default_branch: main\n"
                    "workspace_root: %s\n" % ws)
        make_fixture(probe, '{}', "  parent: 40")
        _c, out = run(probe)
        lines = _i29_for(out, wt2)
        ok = len(lines) == 1 and lines[0].strip().startswith("VIOLATION")
        results.append(("(e) a Done feature's worktree in a SECOND fleet-declared repository "
                        "produces an INV-29 line from ONE run", ok,
                        "\n".join(_i29_lines(out))))

    # ---- (f) SC-05, ONE fixture, four worktrees, four separate assertions ---------------
    with tempfile.TemporaryDirectory() as tmp:
        r = _i29_repo(os.path.join(tmp, "F"))
        _i29_land(r, "FEAT-FULL", {"feature_id": "FEAT-FULL", "status": "Done"})
        _i29_land(r, "FEAT-SHORT-named-in-full",
                  {"feature_id": "FEAT-SHORT-named-in-full", "status": "Done"})
        _i29_land(r, "FEAT-BAD", "{not json at all")
        wt_absent = _i29_wt(r, "FEAT-GONE")          # no landed dir at all
        wt_full = _i29_wt(r, "FEAT-FULL")
        wt_short = _i29_wt(r, "FEAT-SHORT")          # landed dir is the FULL name
        wt_bad = _i29_wt(r, "FEAT-BAD")
        make_fixture(r, '{}', "  parent: 40")
        _c, out = run(r)
        results.append(("(f.1) genuinely absent from the default branch -> SILENT",
                        not _i29_for(out, wt_absent), "\n".join(_i29_lines(out))))
        results.append(("(f.2) a full-named Done sibling -> fires",
                        len(_i29_for(out, wt_full)) == 1, "\n".join(_i29_lines(out))))
        # f.3 AND f.4 ARE THE RED PROOF. An implementation keying the exemption on "the
        # lookup returned nothing" passes f.1 and f.2 and fails both of these — which is the
        # over-suppression that would make every refusal in REQ-01..REQ-05 silently stop.
        short_lines = _i29_for(out, wt_short)
        results.append(("(f.3) a SHORT-named worktree whose landed dir is full-named and "
                        "Done -> fires", len(short_lines) == 1,
                        "\n".join(_i29_lines(out))))
        # THE MESSAGE IS READ, NOT JUST COUNTED. Firing is not enough: the printed command has to
        # be RUNNABLE. `--id` must be the worktree DIRECTORY's own name, because that is what
        # `feature-worktree.py remove` matches; the record's feature_id is the LANDED directory,
        # which for a short-named worktree is a different string and yields
        # "not a linked worktree" for a directory plainly sitting in front of the reader.
        # (f.3) counted the line and never read it, which is exactly how that shipped.
        short_line = short_lines[0] if short_lines else ""
        results.append(("(f.4) the SHORT-named worktree's command carries its OWN directory name",
                        "--id FEAT-SHORT`" in short_line, short_line))
        results.append(("(f.5) and NOT the landed full name",
                        "--id FEAT-SHORT-named-in-full" not in short_line, short_line))
        # ---- SC-17 clause (c): THE PRINTED COMMAND IS EXECUTED, not merely read ----------
        #
        # (f.4) and (f.5) grade the command's TEXT. Text can be right and the command still fail,
        # which is the whole reason SC-17 exists: sixteen criteria graded INV-29 and none of them
        # ever ran what it printed. This clause runs it verbatim and asserts the worktree is gone.
        #
        # THE SAFETY ASSERTION IS NOT OPTIONAL. feature-worktree.py resolves owner_root
        # through harness_boundary.resolve_root, which honours the override only when that
        # directory holds a readable .harness/team-config.yaml. Without the marker it falls
        # back to the SCRIPT's own location — the REAL harness checkout — and this case
        # would run a DELETE against a live worktree. So the marker is written first and the
        # resolver is asked, in a separate process with this case's exact environment, where
        # it lands BEFORE anything is removed.
        _mp = os.path.join(r, _hb.MARKER)
        os.makedirs(os.path.dirname(_mp), exist_ok=True)
        with open(_mp, "w") as f:
            f.write("agents: {}\n")
        import shlex
        m = re.search(r"`python3 ([^`]+)`", short_line) if short_line else None
        ran_ok = False
        gone = False
        run_it = False
        inside = False
        detail = "no command found in the line"
        if m:
            argv = [sys.executable] + shlex.split(m.group(1))
            # THE SCRIPT PATH IS RESOLVED AGAINST THE REAL BIN DIR; EVERY OTHER ARGUMENT IS
            # VERBATIM. The printed command is repo-relative, and an operator runs it from their
            # own checkout where that path exists. A tmpdir fixture has no bin/ of its own, so
            # only argv[1] is rewritten to the real script — the `--repo` and `--id` values SC-17
            # actually grades are untouched, and the override below points the resolver at
            # the fixture. Copying the whole bin dir in would test the copy, not the message.
            argv[1] = os.path.join(os.path.dirname(SCRIPT), os.path.basename(argv[1]))
            env = dict(os.environ)
            env = _root_env(r, env)
            env["HARNESS_PROJECT_DIR"] = r
            # THE GUARD THAT ACTUALLY BITES. What stood here compared wt_short against r —
            # both built from r, so it was true whatever the resolver decided and protected
            # nothing. Ask the resolver instead, with this case's exact environment, and
            # REFUSE to run the delete unless it lands inside the fixture.
            _bin = _anchor_bin
            _where = subprocess.run(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary as h; "
                 "print(h.resolve_root(sys.argv[1]))", _bin],
                capture_output=True, text=True, env=env, cwd=r).stdout.strip()
            inside = bool(_where) and os.path.realpath(_where) == os.path.realpath(r)
            run_it = inside
            if not inside:
                detail = ("REFUSED to run the delete: the resolver landed on %r, not the "
                          "fixture %r" % (_where, r))
        if run_it:
            probe = subprocess.run(argv,
                                   capture_output=True, text=True, env=env, cwd=r)
            ran_ok = probe.returncode == 0
            gone = not os.path.exists(wt_short)
            detail = ("exit=%d resolved_root_is_fixture=%s stdout=%s stderr=%s"
                      % (probe.returncode, inside,
                         probe.stdout.strip()[-200:], probe.stderr.strip()[-200:]))
        # THE REWRITE ABOVE HAS A COST AND THIS CLOSES IT. Rewriting argv[1] means the run does
        # NOT prove the printed script path resolves in a real checkout — so that is asserted
        # separately, against the real root. The path is repo-relative and may reach the tree
        # through the .agents compatibility symlink; what matters is that it resolves at all.
        printed_rel = shlex.split(m.group(1))[0] if m else ""
        real_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(SCRIPT)))))
        results.append(("(f.9) SC-17(c): the printed script path resolves in a real checkout",
                        bool(printed_rel) and os.path.exists(
                            os.path.join(real_root, printed_rel)),
                        "printed=%r real_root=%r" % (printed_rel, real_root)))
        results.append(("(f.7) SC-17(c): the printed command RUNS and exits 0", ran_ok, detail))
        results.append(("(f.8) SC-17(c): and that worktree is GONE afterwards", gone, detail))

        results.append(("(f.6) a landed feature.json that is present but UNPARSEABLE -> "
                        "fires", len(_i29_for(out, wt_bad)) == 1,
                        "\n".join(_i29_lines(out))))

    ok_all = True
    for label, ok, detail in results:
        print(f"{'ok' if ok else 'FAIL'} - INV-29 {label}")
        if not ok and detail:
            print("      saw: " + detail.replace("\n", "\n      "))
        ok_all = ok_all and ok
    return ok_all


# ---------------------------------------------------------------------------------------------
# INV-31 (FEAT-40 T-08): this clone's merge hook is not installed.
#
# EVERY FIXTURE IS A REAL GIT REPOSITORY, because the invariant reads `git config --get
# core.hooksPath` in the checkout it is invoked in. A plain temp directory would answer "unset"
# for the wrong reason and the silent case could never be built at all.
# ---------------------------------------------------------------------------------------------

def _inv31_fixture(tmp, hooks_path=None, post_merge="executable"):
    """A git repo carrying a minimal .harness, with core.hooksPath and the hook file under the
    caller's control.

    `hooks_path` None leaves the config unset. `post_merge` is "executable", "plain" (present
    but mode 0644) or "absent"."""
    subprocess.run(["git", "init", "-q"], cwd=tmp, capture_output=True)
    h = os.path.join(tmp, ".harness")
    os.makedirs(os.path.join(h, "harness", "features"), exist_ok=True)
    with open(os.path.join(h, "harness.json"), "w") as f:
        f.write('{"github": {"sync": false}}\n')
    hooks_dir = os.path.join(tmp, _HOOKS_REL_T)
    os.makedirs(hooks_dir, exist_ok=True)
    if post_merge != "absent":
        pm = os.path.join(hooks_dir, "post-merge")
        with open(pm, "w") as f:
            f.write("#!/usr/bin/env bash\nexit 0\n")
        os.chmod(pm, 0o755 if post_merge == "executable" else 0o644)
    if hooks_path is not None:
        subprocess.run(["git", "config", "core.hooksPath", hooks_path],
                       cwd=tmp, capture_output=True)
    return h


def _inv31_lines(out):
    return [l for l in out.splitlines() if "INV-31" in l]


def case_inv31_unset():
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=None)
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and "unset" in lines[0]
              and _HOOKS_REL_T in lines[0]
              and "git config core.hooksPath" in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 fires at VIOLATION when core.hooksPath is "
              f"unset, saying so and carrying the fix command"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_wrong_value():
    """THE VALUE FOUND IS REPORTED. An operator who cannot see what it currently reads has to
    go and run the command themselves before they can act on the line."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=".git/hooks")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and ".git/hooks" in lines[0]
              and "no harness hook runs" in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 fires when core.hooksPath names another "
              f"directory, quoting the value found"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_absolute_same_dir_passes():
    """AN ABSOLUTE VALUE NAMING THE SAME DIRECTORY IS FINE. The comparison resolves both sides
    to real paths on purpose; a string comparison would call a working clone broken."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=os.path.join(tmp, _HOOKS_REL_T))
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = not lines
        print(f"{'ok' if ok else 'FAIL'} - INV-31 is silent when an ABSOLUTE core.hooksPath "
              f"names the same directory"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_post_merge_absent():
    """A SECOND FINDING WITH A DIFFERENT SUBJECT. The first is a misconfigured clone; this is a
    damaged checkout. Different fixes, so they must never collapse into one message."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=_HOOKS_REL_T, post_merge="absent")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and "post-merge is missing" in lines[0]
              and "restore it" in lines[0]
              and "core.hooksPath" not in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 reports a MISSING post-merge as its own "
              f"finding, with its own fix, never as a tail on the config one"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_post_merge_not_executable():
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=_HOOKS_REL_T, post_merge="plain")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = (len(lines) == 1
              and lines[0].strip().startswith("VIOLATION")
              and "not executable" in lines[0]
              and "644" in lines[0]
              and "chmod +x" in lines[0])
        print(f"{'ok' if ok else 'FAIL'} - INV-31 reports a NON-EXECUTABLE post-merge, naming "
              f"the mode it found and the fix"
              + ("" if ok else f"\n      {lines}"))
        return ok


def case_inv31_silent_when_installed():
    """THE DISCRIMINATING CASE. An invariant that fires on everything is not a check."""
    with tempfile.TemporaryDirectory() as tmp:
        _inv31_fixture(tmp, hooks_path=_HOOKS_REL_T, post_merge="executable")
        _code, out = run(tmp)
        lines = _inv31_lines(out)
        ok = not lines
        print(f"{'ok' if ok else 'FAIL'} - INV-31 is SILENT when the hook is installed and "
              f"executable"
              + ("" if ok else f"\n      {lines}"))
        return ok


def main():
    results = []
    results.append(case_u())
    results.append(case_x())
    results.append(case_inv29())
    results.append(case_inv31_unset())
    results.append(case_inv31_wrong_value())
    results.append(case_inv31_absolute_same_dir_passes())
    results.append(case_inv31_post_merge_absent())
    results.append(case_inv31_post_merge_not_executable())
    results.append(case_inv31_silent_when_installed())
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
