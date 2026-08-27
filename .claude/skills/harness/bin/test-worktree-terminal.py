#!/usr/bin/env python3
"""test-worktree-terminal.py — unit coverage for worktree_terminal.py's classify() and
classify_all() (FEAT-34 T-02).

TDD PROVENANCE NOTE (Iron Law): T-01 shipped a minimal RED/GREEN baseline at this exact path
(cases (a),(b),(d),(e),(f),(h)/dirty, plus a real-implementation-only version of (c)) because the
Iron Law required a failing test before its implementation, and the plan splits impl (T-01) and
tests (T-02) in the opposite order. T-02 c1 extended that baseline into the FULL classify() case
list from the plan: explicit red-proof demonstrations for (c) and (e)/(f) against deliberately
wrong stub implementations, and case (g), the real second-repository fixture. c1's receipt closed
believing REQ-04's cross-repository enumeration would be proven by a caller iterating repos; D-10
overturned that (`plan.yaml` D-10) and gave `classify_all(root)` its own entry point in
worktree_terminal.py. T-02 c2 (this revision) adds the CLASSIFY_ALL cases (i)-(l) that grade D-10's
three-way failure posture and corrects this docstring, which is the only change c2 makes to
anything already here — c1's cases (a)-(h) and their red proofs are unmodified.

Directory trees are not enough — every classification depends on reading a LANDED blob, so every
case below builds a REAL git repository with real commits and a real `git worktree add`, the way
test-check-state.py's case_u already does for INV-25.
"""
import json
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.abspath(__file__)
BIN_DIR = os.path.dirname(SCRIPT)
sys.path.insert(0, BIN_DIR)


def _repo(path, branch="main"):
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


def _commit_feature(repo, feature_id, status_or_raw, repo_segment="harness"):
    """Commit `.harness/<repo_segment>/features/<feature_id>/feature.json` on the CURRENT
    branch of `repo` (main, for every case here) — classify() reads
    `.harness/<repo_segment>/features`, never a hard-coded `.harness/harness/features`, so a
    fixture for a non-"harness" repo_segment must land its feature.json under that same
    segment or `git ls-tree` legitimately finds nothing there. `status_or_raw` is a dict
    written as JSON, or a raw string to write verbatim (for the unparseable case)."""
    rel = os.path.join(".harness", repo_segment, "features", feature_id, "feature.json")
    abs_path = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w") as f:
        if isinstance(status_or_raw, str):
            f.write(status_or_raw)
        else:
            json.dump(status_or_raw, f)
    subprocess.run(["git", "add", rel], cwd=repo, capture_output=True)
    subprocess.run(["git", "commit", "-qm", f"add {feature_id}"], cwd=repo, capture_output=True)


def _add_wt(repo, worktree_id, repo_segment="harness"):
    dest = os.path.join(repo, ".claude", "worktrees", repo_segment, worktree_id)
    subprocess.run(["git", "worktree", "add", "-q", "-b", f"wt-{worktree_id}-{repo_segment}",
                    dest, "HEAD"], cwd=repo, capture_output=True)
    return dest


def case_classify():
    """Every classification branch classify() is required to reach, on one shared fixture
    repository so the records can be cross-checked against each other by path. Covers (a),
    (b), (d), (e), (f) and (h)/dirty."""
    import worktree_terminal as w

    results = []

    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))

        # (a) landed Done, exact-named worktree -> terminal.
        _commit_feature(repo, "FEAT-01-done-thing", {"status": "Done"})
        done_dest = _add_wt(repo, "FEAT-01-done-thing")

        # (b) landed Review, exact-named worktree -> omitted from the returned list entirely.
        _commit_feature(repo, "FEAT-02-review-thing", {"status": "Review"})
        review_dest = _add_wt(repo, "FEAT-02-review-thing")

        # (d) never landed at all -> exempt_absent.
        absent_dest = _add_wt(repo, "FEAT-03-never-landed")

        # (e) short-named worktree whose id is a prefix of exactly one landed Done directory
        # -> terminal, not exempt_absent.
        _commit_feature(repo, "FEAT-04-short-name-target", {"status": "Done"})
        short_dest = _add_wt(repo, "FEAT-04")

        # (f) feature.json present on the default branch but unparseable -> unresolved.
        _commit_feature(repo, "FEAT-05-bad-json", "{not json")
        bad_json_dest = _add_wt(repo, "FEAT-05-bad-json")

        # ambiguous prefix: two landed directories share the same short prefix -> unresolved.
        _commit_feature(repo, "FEAT-06-amb-one", {"status": "Done"})
        _commit_feature(repo, "FEAT-06-amb-two", {"status": "Done"})
        amb_dest = _add_wt(repo, "FEAT-06")

        recs = w.classify(repo)
        by_path = {r["path"]: r for r in recs}

        def get(dest):
            return by_path.get(os.path.realpath(dest)) or by_path.get(dest)

        r = get(done_dest)
        results.append(("(a) landed Done, exact name -> terminal",
                         bool(r) and r["klass"] == "terminal" and r["feature_id"] ==
                         "FEAT-01-done-thing",
                         f"record: {r}"))

        r = get(review_dest)
        results.append(("(b) landed Review -> omitted from the returned list",
                         r is None, f"record: {r}"))

        r = get(absent_dest)
        results.append(("(d) never landed -> exempt_absent",
                         bool(r) and r["klass"] == "exempt_absent",
                         f"record: {r}"))

        r = get(short_dest)
        results.append(("(e) short-named prefix of one landed Done dir -> terminal, "
                         "NOT exempt_absent",
                         bool(r) and r["klass"] == "terminal"
                         and r["feature_id"] == "FEAT-04-short-name-target",
                         f"record: {r}"))

        r = get(bad_json_dest)
        results.append(("(f) landed feature.json unparseable -> unresolved",
                         bool(r) and r["klass"] == "unresolved",
                         f"record: {r}"))

        r = get(amb_dest)
        results.append(("ambiguous prefix (matches 2 landed dirs) -> unresolved, "
                         "never exempt_absent",
                         bool(r) and r["klass"] == "unresolved",
                         f"record: {r}"))

        # (h) dirty: make the Done worktree dirty and reclassify.
        with open(os.path.join(done_dest, "scratch.txt"), "w") as f:
            f.write("dirty\n")
        recs2 = w.classify(repo)
        r2 = {rec["path"]: rec for rec in recs2}.get(os.path.realpath(done_dest)) \
            or {rec["path"]: rec for rec in recs2}.get(done_dest)
        results.append(("(h) uncommitted change in a Done worktree -> terminal with dirty True",
                         bool(r2) and r2["dirty"] is True and r2["klass"] == "terminal",
                         f"record: {r2}"))

        # every callable klass is one of CLASSES; every record carries all six keys.
        keys_ok = all(
            set(rec.keys()) == {"path", "feature_id", "klass", "dirty", "reason", "repo"}
            and rec["klass"] in w.CLASSES
            for rec in recs
        )
        results.append(("every returned record carries exactly the six documented keys, "
                         "klass is always one of CLASSES", keys_ok, f"records: {recs}"))

        # sorted by path.
        results.append(("records are sorted by path",
                         [rec["path"] for rec in recs] == sorted(rec["path"] for rec in recs),
                         f"paths: {[rec['path'] for rec in recs]}"))

        # the main checkout itself (root) is never in the returned list.
        results.append(("root itself is never a returned record",
                         os.path.realpath(repo) not in by_path,
                         f"paths: {list(by_path.keys())}"))

    return results


def case_deadlock():
    """(c) DEADLOCK, against the REAL implementation: the working tree's own copy of
    feature.json must never be consulted. A worktree whose OWN working copy says Done but
    whose LANDED copy says Review must not classify terminal; the inverse (landed Done,
    working copy Review) must classify terminal."""
    import worktree_terminal as w

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))

        _commit_feature(repo, "FEAT-07-deadlock-a", {"status": "Review"})
        dest_a = _add_wt(repo, "FEAT-07-deadlock-a")
        # overwrite the WORKING TREE copy to say Done, without committing.
        wt_feature = os.path.join(dest_a, ".harness", "harness", "features",
                                   "FEAT-07-deadlock-a", "feature.json")
        with open(wt_feature, "w") as f:
            json.dump({"status": "Done"}, f)

        _commit_feature(repo, "FEAT-08-deadlock-b", {"status": "Done"})
        dest_b = _add_wt(repo, "FEAT-08-deadlock-b")
        wt_feature_b = os.path.join(dest_b, ".harness", "harness", "features",
                                     "FEAT-08-deadlock-b", "feature.json")
        with open(wt_feature_b, "w") as f:
            json.dump({"status": "Review"}, f)

        recs = w.classify(repo)
        by_path = {r["path"]: r for r in recs}

        r_a = by_path.get(os.path.realpath(dest_a)) or by_path.get(dest_a)
        results.append(("(c) landed Review, working copy Done -> NOT terminal (omitted)",
                         r_a is None, f"record: {r_a}"))

        r_b = by_path.get(os.path.realpath(dest_b)) or by_path.get(dest_b)
        results.append(("(c) inverse: landed Done, working copy Review -> terminal regardless",
                         bool(r_b) and r_b["klass"] == "terminal", f"record: {r_b}"))

    return results


def _classify_stub_reads_working_tree(worktree_path, feature_id):
    """DELIBERATELY WRONG stub, independent of worktree_terminal: classifies by reading the
    WORKTREE'S OWN on-disk feature.json instead of the landed blob on the default branch. Its
    only purpose is to demonstrate the RED state (c) guards against — 'an implementation
    reading the working tree fails both halves' (T-02's intent)."""
    fj = os.path.join(worktree_path, ".harness", "harness", "features", feature_id,
                       "feature.json")
    try:
        with open(fj) as f:
            data = json.load(f)
    except Exception:
        return "omitted"
    return "terminal" if data.get("status") == "Done" else "omitted"


def case_deadlock_red_proof():
    """(c) RED PROOF: run the same deadlock pair against a stub that reads the working tree.
    It must get BOTH halves wrong — that failing state is what the real classify() is built
    to avoid, and the intent requires demonstrating it explicitly."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))

        _commit_feature(repo, "FEAT-07-deadlock-a", {"status": "Review"})
        dest_a = _add_wt(repo, "FEAT-07-deadlock-a")
        wt_feature = os.path.join(dest_a, ".harness", "harness", "features",
                                   "FEAT-07-deadlock-a", "feature.json")
        with open(wt_feature, "w") as f:
            json.dump({"status": "Done"}, f)

        _commit_feature(repo, "FEAT-08-deadlock-b", {"status": "Done"})
        dest_b = _add_wt(repo, "FEAT-08-deadlock-b")
        wt_feature_b = os.path.join(dest_b, ".harness", "harness", "features",
                                     "FEAT-08-deadlock-b", "feature.json")
        with open(wt_feature_b, "w") as f:
            json.dump({"status": "Review"}, f)

        stub_a = _classify_stub_reads_working_tree(dest_a, "FEAT-07-deadlock-a")
        stub_b = _classify_stub_reads_working_tree(dest_b, "FEAT-08-deadlock-b")

        # correct (real-implementation) answers, per case_deadlock above: dest_a -> omitted
        # (landed Review), dest_b -> terminal (landed Done).
        results.append(("(c) red proof, forward: working-tree-reading stub wrongly says "
                         "terminal for a landed-Review worktree",
                         stub_a == "terminal", f"stub_a: {stub_a} (correct: omitted)"))
        results.append(("(c) red proof, inverse: working-tree-reading stub wrongly says "
                         "omitted for a landed-Done worktree",
                         stub_b == "omitted", f"stub_b: {stub_b} (correct: terminal)"))

    return results


def _stub_landed_names(repo, default_branch="main"):
    r = subprocess.run(
        ["git", "ls-tree", "--name-only", f"{default_branch}:.harness/harness/features"],
        cwd=repo, capture_output=True, text=True)
    if r.returncode != 0:
        return []
    return [line for line in r.stdout.splitlines() if line]


def _stub_landed_feature_json(repo, feature_id, default_branch="main"):
    rel = os.path.join(".harness", "harness", "features", feature_id, "feature.json")
    r = subprocess.run(["git", "show", f"{default_branch}:{rel}"], cwd=repo,
                        capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except Exception:
        return None


def _classify_stub_absent_on_any_miss(repo, wt_id):
    """DELIBERATELY WRONG stub, independent of worktree_terminal: keys the exempt_absent
    exemption on 'the landed lookup returned nothing', conflating true absence (no matching
    directory at all) with any other read/parse failure (unparseable JSON, or a short name
    that only matches by prefix rather than exactly). Only for the red-proof demonstration
    T-02's intent requires for (e) and (f); never called from worktree_terminal itself."""
    names = _stub_landed_names(repo)
    if wt_id not in names:
        return "exempt_absent"
    data = _stub_landed_feature_json(repo, wt_id)
    if data is None:
        return "exempt_absent"  # BUG: unparseable/unreadable folded into "absent"
    if data.get("status") == "Done":
        return "terminal"
    return "omitted"


def case_absent_red_proof():
    """(e)/(f) RED PROOF: the stub above must PASS (a) and (d) — where exact-match lookup and
    true absence line up with the correct answer — and FAIL (e) and (f), where the correct
    answer depends on prefix resolution or on distinguishing 'unparseable' from 'absent'."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))

        # (a) exact match, Done -> correct answer terminal.
        _commit_feature(repo, "FEAT-01-done-thing", {"status": "Done"})
        # (d) never landed -> correct answer exempt_absent.
        # (e) short name, prefix of a landed Done dir -> correct answer terminal.
        _commit_feature(repo, "FEAT-04-short-name-target", {"status": "Done"})
        # (f) landed but unparseable -> correct answer unresolved.
        _commit_feature(repo, "FEAT-05-bad-json", "{not json")

        stub_a = _classify_stub_absent_on_any_miss(repo, "FEAT-01-done-thing")
        stub_d = _classify_stub_absent_on_any_miss(repo, "FEAT-03-never-landed")
        stub_e = _classify_stub_absent_on_any_miss(repo, "FEAT-04")
        stub_f = _classify_stub_absent_on_any_miss(repo, "FEAT-05-bad-json")

        results.append(("(a) red-proof stub PASSES: exact-match Done -> terminal",
                         stub_a == "terminal", f"stub_a: {stub_a}"))
        results.append(("(d) red-proof stub PASSES: truly absent -> exempt_absent",
                         stub_d == "exempt_absent", f"stub_d: {stub_d}"))
        results.append(("(e) red-proof stub FAILS: short-named prefix wrongly folded into "
                         "exempt_absent instead of terminal",
                         stub_e != "terminal", f"stub_e: {stub_e} (correct: terminal)"))
        results.append(("(f) red-proof stub FAILS: unparseable landed JSON wrongly folded "
                         "into exempt_absent instead of unresolved",
                         stub_f != "unresolved", f"stub_f: {stub_f} (correct: unresolved)"))

    return results


def case_second_repo():
    """(g) SECOND REPOSITORY: a real second git repo, fleet-resolved (never the hard-coded
    "harness" literal), with its own default branch, its own Done feature landed on it and a
    real `git worktree add`. classify() is called directly on that repository's own root — the
    same call shape post-merge-sweep.sh's contract (T-03) makes per repository — and must
    classify that worktree terminal.

    Fleet resolution requires factory_config.FLEET_PATH, computed at IMPORT time from
    HARNESS_PROJECT_DIR, so this case runs in a FRESH SUBPROCESS rather than reusing the
    already-imported worktree_terminal/factory_config from this process."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        # The harness_boundary.resolve_root() MARKER: HARNESS_PROJECT_DIR is honored only
        # when .harness/team-config.yaml underneath it is readable.
        probe_root = os.path.join(tmp, "probe")
        os.makedirs(os.path.join(probe_root, ".harness", "harness", "docs"), exist_ok=True)
        with open(os.path.join(probe_root, ".harness", "harness", "docs", "SPEC.md"), "w") as f:
            f.write("probe\n")
        with open(os.path.join(probe_root, ".harness", "team-config.yaml"), "w") as f:
            f.write("teams: []\n")

        workspace_root = os.path.join(tmp, "workspace")
        os.makedirs(workspace_root, exist_ok=True)

        fleet_dir = os.path.join(probe_root, ".harness", "factory")
        os.makedirs(fleet_dir, exist_ok=True)
        with open(os.path.join(fleet_dir, "fleet.yaml"), "w") as f:
            f.write(
                "schema: factory-fleet/1\n"
                f"workspace_root: {workspace_root}\n"
                "repos:\n"
                "  - name: acme/second-repo\n"
                "    default_branch: main\n"
            )

        # workspace_path(fleet, "acme/second-repo") == workspace_root/second-repo — the real
        # second repository must actually live there for resolve_repo's fleet branch to line
        # its owner_root up with where classify() is told to look.
        repo2 = _repo(os.path.join(workspace_root, "second-repo"), branch="main")
        _commit_feature(repo2, "FEAT-09-second-repo-done", {"status": "Done"},
                         repo_segment="second-repo")
        dest2 = _add_wt(repo2, "FEAT-09-second-repo-done", repo_segment="second-repo")

        script = (
            "import json, sys\n"
            f"sys.path.insert(0, {BIN_DIR!r})\n"
            "import worktree_terminal as w\n"
            f"recs = w.classify({repo2!r})\n"
            "print(json.dumps(recs))\n"
        )
        env = dict(os.environ)
        env["HARNESS_PROJECT_DIR"] = probe_root
        proc = subprocess.run([sys.executable, "-c", script], cwd=repo2,
                               capture_output=True, text=True, env=env, timeout=30)

        detail = f"rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}"
        ok = False
        record = None
        if proc.returncode == 0:
            try:
                recs = json.loads(proc.stdout)
                by_path = {r["path"]: r for r in recs}
                record = by_path.get(os.path.realpath(dest2)) or by_path.get(dest2)
                ok = (bool(record) and record["klass"] == "terminal"
                      and record["feature_id"] == "FEAT-09-second-repo-done"
                      and record["repo"] == "second-repo")
            except Exception as exc:
                detail += f" json-error={exc!r}"
                ok = False

        results.append(("(g) real second git repo, fleet-resolved default branch, real "
                         "worktree add, landed Done -> terminal",
                         ok, detail + f" record={record}"))

    return results


# --- CLASSIFY_ALL fixture helpers, D-10. Cases (i)-(l) reuse case_second_repo's fixture shape
# (a probe root carrying .harness/factory/fleet.yaml, a workspace_root, and a real second git
# repository under workspace_root with a landed Done feature and a real `git worktree add`) —
# no second fixture shape is built.


def _build_probe_repo(tmp):
    """probe_root, made a REAL git repo (not just directories + SPEC.md) with its own standing
    worktree over a landed Done feature under repo_segment "harness". classify_all(root) calls
    classify(root) for the harness half, and asserting that half returned SOMETHING requires it
    to have a record — an empty-vs-empty comparison against a bare probe directory would pass
    vacuously and grade nothing (dispatch note 2)."""
    probe_root = os.path.join(tmp, "probe")
    repo = _repo(probe_root, branch="main")
    docs_dir = os.path.join(probe_root, ".harness", "harness", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, "SPEC.md"), "w") as f:
        f.write("probe\n")
    # harness_boundary.resolve_root's MARKER — see the module docstring at :351-352.
    with open(os.path.join(probe_root, ".harness", "team-config.yaml"), "w") as f:
        f.write("teams: []\n")
    subprocess.run(["git", "add", ".harness/harness/docs/SPEC.md", ".harness/team-config.yaml"],
                    cwd=probe_root, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "spec"], cwd=probe_root, capture_output=True)
    _commit_feature(repo, "FEAT-10-probe-done", {"status": "Done"}, repo_segment="harness")
    dest_probe = _add_wt(repo, "FEAT-10-probe-done", repo_segment="harness")
    return probe_root, dest_probe


def _build_second_repo(workspace_root):
    """The real second repository, exactly as case_second_repo (g) builds it — reused, not
    rebuilt as a second shape."""
    repo2 = _repo(os.path.join(workspace_root, "second-repo"), branch="main")
    _commit_feature(repo2, "FEAT-09-second-repo-done", {"status": "Done"},
                     repo_segment="second-repo")
    dest2 = _add_wt(repo2, "FEAT-09-second-repo-done", repo_segment="second-repo")
    return repo2, dest2


def _write_fleet(probe_root, workspace_root, repos_yaml):
    fleet_dir = os.path.join(probe_root, ".harness", "factory")
    os.makedirs(fleet_dir, exist_ok=True)
    fleet_path = os.path.join(fleet_dir, "fleet.yaml")
    with open(fleet_path, "w") as f:
        f.write(
            "schema: factory-fleet/1\n"
            f"workspace_root: {workspace_root}\n"
            "repos:\n" + repos_yaml
        )
    return fleet_path


def _run_classify_all_subprocess(probe_root, script):
    env = dict(os.environ)
    env["HARNESS_PROJECT_DIR"] = probe_root
    return subprocess.run([sys.executable, "-c", script], cwd=probe_root,
                           capture_output=True, text=True, env=env, timeout=30)


def case_classify_all_two_repos():
    """(i) ONE CALL, TWO REPOSITORIES: classify_all(probe_root) returns both the harness half's
    own terminal record AND the second repository's terminal record. RED PROOF: classify(root)
    alone — the call case (g) already makes, on the second repository's own root — never reaches
    the second repository when called on probe_root; that is the exact gap D-10 exists to close
    and (g) cannot reach."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        probe_root, dest_probe = _build_probe_repo(tmp)
        workspace_root = os.path.join(tmp, "workspace")
        os.makedirs(workspace_root, exist_ok=True)
        repo2, dest2 = _build_second_repo(workspace_root)
        _write_fleet(probe_root, workspace_root,
                     "  - name: acme/second-repo\n    default_branch: main\n")

        script = (
            "import json, sys\n"
            f"sys.path.insert(0, {BIN_DIR!r})\n"
            "import worktree_terminal as w\n"
            f"recs_all = w.classify_all({probe_root!r})\n"
            f"recs_classify_only = w.classify({probe_root!r})\n"
            "print(json.dumps({'all': recs_all, 'classify_only': recs_classify_only}))\n"
        )
        proc = _run_classify_all_subprocess(probe_root, script)
        detail = f"rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}"

        ok_probe = ok_second = red_proof = False
        record_probe = record_second = None
        if proc.returncode == 0:
            try:
                data = json.loads(proc.stdout)
                by_path_all = {r["path"]: r for r in data["all"]}
                by_path_classify_only = {r["path"]: r for r in data["classify_only"]}

                record_probe = by_path_all.get(os.path.realpath(dest_probe)) \
                    or by_path_all.get(dest_probe)
                ok_probe = bool(record_probe) and record_probe["klass"] == "terminal"

                record_second = by_path_all.get(os.path.realpath(dest2)) \
                    or by_path_all.get(dest2)
                ok_second = (bool(record_second) and record_second["klass"] == "terminal"
                             and record_second["repo"] == "second-repo")

                second_via_classify_only = by_path_classify_only.get(os.path.realpath(dest2)) \
                    or by_path_classify_only.get(dest2)
                red_proof = second_via_classify_only is None
            except Exception as exc:
                detail += f" json-error={exc!r}"

        results.append(("(i) classify_all(probe_root) includes the harness half's own "
                         "terminal record",
                         ok_probe, detail + f" record_probe={record_probe}"))
        results.append(("(i) classify_all(probe_root) includes the second repository's "
                         "terminal record",
                         ok_second, detail + f" record_second={record_second}"))
        results.append(("(i) RED PROOF: classify(probe_root) alone (classify_all==classify) "
                         "never returns a record for the second repository's worktree",
                         red_proof, detail))

    return results


def _stub_skip_both(declared):
    """DELIBERATELY WRONG, independent of worktree_terminal: skips a declared repo whenever its
    directory does not enumerate cleanly, whether that is because the directory does not exist
    (correct to skip) or because it exists but is not a git repository (WRONG to skip — (k)
    requires one repository-level unresolved record there). `declared` is a list of
    (path, is_git_repo) pairs."""
    records = []
    for path, is_git_repo in declared:
        if not os.path.isdir(path):
            continue
        if not is_git_repo:
            continue  # BUG: folds present-but-unenumerable into the same silence as absent
        records.append(("terminal-ish", path))
    return records


def _stub_reports_both(declared):
    """DELIBERATELY WRONG, independent of worktree_terminal: emits an unresolved record for
    EVERY declared repo whose directory is missing OR unenumerable, conflating absence (must
    emit nothing, per D-10) with present-but-unenumerable (must emit exactly one record)."""
    records = []
    for path, is_git_repo in declared:
        if not os.path.isdir(path) or not is_git_repo:
            records.append(("unresolved", path))  # BUG: also fires for the merely-absent case
    return records


def case_classify_all_absent_vs_unenumerable():
    """(j) ABSENT CHECKOUT and (k) PRESENT BUT UNENUMERABLE, on one fleet.yaml declaring the
    real second repository plus these two. (j): no record for the never-created directory, no
    raise, the real second repository's record is unaffected. (k): exactly one repository-level
    record, klass "unresolved", path equal to the directory — asserted separately per the
    dispatch. Also demonstrates, against local stubs (never worktree_terminal itself), the two
    failing states that discriminate (j) from (k): skip-both passes (j) and fails (k); report-both
    passes (k) and fails (j)."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        probe_root, dest_probe = _build_probe_repo(tmp)
        workspace_root = os.path.join(tmp, "workspace")
        os.makedirs(workspace_root, exist_ok=True)
        repo2, dest2 = _build_second_repo(workspace_root)

        absent_dir = os.path.join(workspace_root, "absent-repo")  # never created

        unenum_dir = os.path.join(workspace_root, "unenum-repo")
        os.makedirs(unenum_dir, exist_ok=True)
        with open(os.path.join(unenum_dir, "not-a-repo.txt"), "w") as f:
            f.write("plain directory, not a git repository\n")

        _write_fleet(probe_root, workspace_root,
                     "  - name: acme/second-repo\n    default_branch: main\n"
                     "  - name: acme/absent-repo\n    default_branch: main\n"
                     "  - name: acme/unenum-repo\n    default_branch: main\n")

        script = (
            "import json, sys\n"
            f"sys.path.insert(0, {BIN_DIR!r})\n"
            "import worktree_terminal as w\n"
            f"recs = w.classify_all({probe_root!r})\n"
            "print(json.dumps(recs))\n"
        )
        proc = _run_classify_all_subprocess(probe_root, script)
        detail = f"rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}"

        ok_second = ok_absent = ok_unenum_klass = ok_unenum_path = False
        record_second = record_absent = record_unenum = None
        if proc.returncode == 0:
            try:
                recs = json.loads(proc.stdout)
                by_path = {r["path"]: r for r in recs}
                by_repo = {r.get("repo"): r for r in recs if r.get("repo")}

                record_second = by_path.get(os.path.realpath(dest2)) or by_path.get(dest2)
                ok_second = bool(record_second) and record_second["klass"] == "terminal"

                record_absent = by_path.get(absent_dir) \
                    or by_path.get(os.path.realpath(absent_dir))
                ok_absent = record_absent is None

                record_unenum = by_repo.get("unenum-repo")
                ok_unenum_klass = bool(record_unenum) and record_unenum["klass"] == "unresolved"
                ok_unenum_path = bool(record_unenum) and record_unenum["path"] == unenum_dir
            except Exception as exc:
                detail += f" json-error={exc!r}"

        results.append(("(j) real second repository's terminal record is unaffected by an "
                         "absent declared repo alongside it",
                         ok_second, detail + f" record_second={record_second}"))
        results.append(("(j) absent checkout: no record for the never-created directory, "
                         "and classify_all does not raise",
                         ok_absent, detail + f" record_absent={record_absent}"))
        results.append(("(k) present-but-unenumerable: exactly one repository-level record, "
                         "klass unresolved",
                         ok_unenum_klass, detail + f" record_unenum={record_unenum}"))
        results.append(("(k) present-but-unenumerable: record path equals the declared "
                         "directory",
                         ok_unenum_path, detail + f" record_unenum={record_unenum}"))

        declared = [(absent_dir, False), (unenum_dir, False)]
        skip_both = _stub_skip_both(declared)
        report_both = _stub_reports_both(declared)

        results.append(("(j)/(k) RED PROOF: a stub skipping every non-enumerable declared repo "
                         "passes (j) but fails (k) — emits no record at all for unenum-repo",
                         skip_both == [], f"skip_both: {skip_both}"))
        results.append(("(j)/(k) RED PROOF: a stub reporting every non-enumerable declared repo "
                         "passes (k) but fails (j) — wrongly emits a record for absent-repo too",
                         len(report_both) == 2, f"report_both: {report_both}"))

    return results


def case_classify_all_fleet_unloadable():
    """(l) FLEET UNLOADABLE: overwrite the probe root's fleet.yaml with bytes load_fleet
    rejects. classify_all still returns the harness root's own records AND returns one
    repository-level unresolved record whose path is the fleet path — two assertions. RED PROOF:
    a second, independent producer — a local stub that attempts factory_config.load_fleet(),
    catches the failure, and returns only the harness half's classify(root) records — is run in
    the SAME subprocess against the SAME unloadable fleet.yaml. It never emits a fleet-path
    record; the real classify_all does. Loop-back cycle 1 (T-02): the prior form compared the
    real output's fleet-path record to itself with the record filtered out, which cannot fail
    (see the c2 receipt's loop-back-cycle-1 section)."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        probe_root, dest_probe = _build_probe_repo(tmp)

        fleet_dir = os.path.join(probe_root, ".harness", "factory")
        os.makedirs(fleet_dir, exist_ok=True)
        fleet_path = os.path.join(fleet_dir, "fleet.yaml")
        with open(fleet_path, "w") as f:
            f.write("key: [unclosed\n  - broken: yaml: syntax\n")  # load_fleet must reject this

        # Second producer, same subprocess, same fixture: a DELIBERATELY WRONG stub that
        # attempts factory_config.load_fleet(), catches the failure, and returns ONLY the
        # harness half's classify(root) records — no fleet-path record at all. Independent of
        # classify_all's own code path (it never calls classify_all), in the same spirit as
        # _stub_skip_both/_stub_reports_both above.
        script = (
            "import json, sys\n"
            f"sys.path.insert(0, {BIN_DIR!r})\n"
            "import worktree_terminal as w\n"
            "factory_config = w._import_factory_config()\n"
            f"real = w.classify_all({probe_root!r})\n"
            f"stub = list(w.classify({probe_root!r}))\n"
            "try:\n"
            "    factory_config.load_fleet()\n"
            "except Exception:\n"
            "    pass\n"  # swallowed: no fleet-path record appended, unlike classify_all
            "print(json.dumps({'real': real, 'stub': stub}))\n"
        )
        proc = _run_classify_all_subprocess(probe_root, script)
        detail = f"rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}"

        ok_fleet = ok_harness = red_proof = False
        record_fleet = record_probe = None
        recs = stub_recs = None
        if proc.returncode == 0:
            try:
                both = json.loads(proc.stdout)
                recs = both["real"]
                stub_recs = both["stub"]
                by_path = {r["path"]: r for r in recs}

                record_fleet = by_path.get(fleet_path)
                ok_fleet = bool(record_fleet) and record_fleet["klass"] == "unresolved"

                record_probe = by_path.get(os.path.realpath(dest_probe)) \
                    or by_path.get(dest_probe)
                ok_harness = bool(record_probe) and record_probe["klass"] == "terminal"
            except Exception as exc:
                detail += f" json-error={exc!r}"

        results.append(("(l) fleet.yaml unloadable: classify_all returns an unresolved record "
                         "whose path is the fleet path",
                         ok_fleet, detail + f" record_fleet={record_fleet}"))
        results.append(("(l) fleet.yaml unloadable: classify_all still returns the harness "
                         "root's own records",
                         ok_harness, detail + f" record_probe={record_probe}"))

        if recs is not None and stub_recs is not None:
            stub_has_fleet = any(r["path"] == fleet_path for r in stub_recs)
            real_has_fleet = any(r["path"] == fleet_path for r in recs)
            red_proof = (not stub_has_fleet) and real_has_fleet
        results.append(("(l) RED PROOF: a stub that swallows the fleet-load exception "
                         "(catches it, returns only the harness half's own records) never "
                         "emits a fleet-path record, while the real classify_all against the "
                         "SAME unloadable fleet.yaml does",
                         red_proof,
                         detail + f" stub_recs={stub_recs} real_recs={recs}"))

    return results


def case_classify_from_linked_worktree():
    """(m) LINKED WORKTREE AS ROOT — T-02 rework: every case above calls classify(repo_root)
    from the repository ROOT, where the main checkout happens to equal `root` and gets skipped
    by coincidence. The harness never runs that way: it always runs with `root` set to a LINKED
    worktree. Under the unfixed classify(), `os.path.realpath(path) == root_real` at
    worktree_terminal.py:196 only skips the main checkout when it equals `root` — when root IS a
    linked worktree, the main checkout survives the loop, fails _split_owner_segment_id (it is
    not under WORKTREES_SEGMENT), and gets appended as an `unresolved` record with
    feature_id=None. This is the exact hole the operator measured; no prior case can catch it
    because none call classify with a linked worktree as root."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))
        _commit_feature(repo, "FEAT-11-linked-root", {"status": "Done"})
        dest = _add_wt(repo, "FEAT-11-linked-root")

        import worktree_terminal as w
        recs = w.classify(dest)
        main_checkout_real = os.path.realpath(repo)
        offending = [r for r in recs if os.path.realpath(r["path"]) == main_checkout_real]

        results.append(("(m) classify(<linked worktree as root>) never returns a record for "
                         "the main checkout",
                         offending == [], f"records: {recs}"))

        # The settled consequence (lead-approved, not re-opened here): under the fix, root
        # itself — the linked worktree — is no longer skipped and becomes its own classified
        # record. Assert its presence as its own clause, never folded into a total count.
        by_path = {r["path"]: r for r in recs}
        own_record = by_path.get(os.path.realpath(dest)) or by_path.get(dest)
        results.append(("(m) the linked worktree passed as root IS itself classified (landed "
                         "Done -> terminal), not silently skipped",
                         bool(own_record) and own_record["klass"] == "terminal"
                         and own_record["feature_id"] == "FEAT-11-linked-root",
                         f"record: {own_record}"))

    return results


def case_classify_empty_repo_no_linked_worktrees():
    """(n) EMPTY REPOSITORY: a repository with no linked worktrees at all (only the main
    checkout, which git worktree list always reports) yields no records and classify() does not
    raise."""
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        repo = _repo(os.path.join(tmp, "R"))

        import worktree_terminal as w
        try:
            recs = w.classify(repo)
            err = None
        except Exception as exc:
            recs = None
            err = exc

        results.append(("(n) repository with no linked worktrees yields no records and does "
                         "not raise",
                         err is None and recs == [], f"recs={recs} err={err!r}"))

    return results


def main():
    results = (
        case_classify()
        + case_deadlock()
        + case_deadlock_red_proof()
        + case_absent_red_proof()
        + case_second_repo()
        + case_classify_all_two_repos()
        + case_classify_all_absent_vs_unenumerable()
        + case_classify_all_fleet_unloadable()
        + case_classify_from_linked_worktree()
        + case_classify_empty_repo_no_linked_worktrees()
    )
    all_ok = True
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"{status}: {name}" + ("" if ok else f"\n  {detail}"))
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
