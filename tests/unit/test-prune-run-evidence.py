#!/usr/bin/env python3
"""prune-run-evidence.py — at ship, a feature keeps the UI evidence that still means something
(every PASS validator validate/fix run and every run bound to the shipped pin) and drops only
the other runs' `runs/<id>/ui/` (#1997). Every run directory, digest.md, state.yaml,
.run-identity.json and other non-UI file survives byte-for-byte (#2294): #2177 pins each recorded
run's digest as check-state cycle evidence. Run records are tracked like any artifact (DEC-257),
so the pruner runs no git command and leaves the index byte-identical (#2451). Before any
mutation, dry-run included, a missing recorded cycle_evidence path refuses with exit 2 and an
unreadable directory under a recorded run, its ui/ included, fails with exit 1, each naming every
offender (#2399). Fixtures are real git repositories ignoring only `runs/*/ui/**`, as DEC-257's
.gitignore does.

PRUNE_RUN_EVIDENCE_BIN overrides the subject so the regressions can be proven RED against a
reverted copy of the pruner."""
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude" / "skills" / "harness" / "bin"
sys.path.insert(0, str(ROOT / "tests"))
from harness_config_support import write_config  # noqa: E402
TOOL = Path(os.environ.get("PRUNE_RUN_EVIDENCE_BIN") or BIN / "prune-run-evidence.py")
CHECK_STATE = BIN / "check-state.py"
FAILURES = []
PIN = "f" * 40
RUNS = [
    ("build-c0-eng", "PASS", "a" * 40),
    ("validate-c1-validator", "FAIL", "b" * 40),
    ("validate-c2-validator", "PASS", "c" * 40),
    ("fix-c3-eng", "PASS", "d" * 40),
    ("validate-c4-validator", "FAIL", "e" * 40),
    ("validate-ship-validator", "FAIL", "9" * 40),
    ("fix-c5-validator", "pass", "6" * 40),          # the readers' PASS after a failed validate lives here; verdict case varies
    ("fix-c5-eng", "PASS", "5" * 40),                # the fix team's engineer run is not evidence
    ("briefing-reconciliation-validator", "PASS", "8" * 40),
    ("distill-validator", "PASS", "7" * 40),
    ("simplify-eng", "PASS", PIN),                   # bound to the pin by its bundle
    ("plan-c0-product", "PASS", None),               # no UI lane: nothing to prune, and its record stays
]
EXPECTED_KEPT = ["fix-c5-validator", "simplify-eng", "validate-c2-validator"]
ALL_RUNS = sorted(r for r, _v, _s in RUNS)

def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL") + " - " + name)
    if not condition:
        FAILURES.append(name)
        print("       " + detail[:500])


def scrubbed_env():
    return {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR")}


def tool(root, *args):
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root), *args],
                          capture_output=True, text=True, env=scrubbed_env())


# Runs the subject under an audit hook: any subprocess or exec it starts — a read-only
# `git status` included — is logged and raised inside the subject, so it cannot succeed.
NO_SUBPROCESS = textwrap.dedent("""
    import os, runpy, sys
    def hook(event, args):
        if event in ("subprocess.Popen", "os.posix_spawn", "os.exec", "os.spawn", "os.system", "os.fork"):
            with open(os.environ["PRUNE_SUBPROCESS_LOG"], "a", encoding="utf-8") as log:
                log.write(f"{event} {args!r}\\n")
            raise RuntimeError(f"prune-run-evidence started a subprocess: {event}")
    sys.addaudithook(hook)
    sys.argv = sys.argv[1:]
    runpy.run_path(sys.argv[0], run_name="__main__")
""")


def hooked_tool(root, log, *args):
    env = scrubbed_env()
    env["PRUNE_SUBPROCESS_LOG"] = str(log)
    return subprocess.run([sys.executable, "-c", NO_SUBPROCESS, str(TOOL), "--root", str(root), *args],
                          capture_output=True, text=True, env=env)


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(root), *args],
                          capture_output=True, env=env, check=True).stdout


def checkout(root):
    """A real git repository that ignores only run UI lanes, as DEC-257's .gitignore does."""
    (root / ".harness").mkdir(parents=True, exist_ok=True)
    (root / ".harness" / "team-config.yaml").write_text("agents: {}\n")
    (root / ".gitignore").write_text(".harness/*/features/*/runs/*/ui/**\n")
    git(root, "init", "-q")
    git(root, "add", ".gitignore", ".harness/team-config.yaml")
    git(root, "commit", "-q", "-m", "init")


def index_bytes(root):
    return (root / ".git" / "index").read_bytes()


def feature(root, runs, review_sha=PIN):
    """Every run carries its durable record (digest.md, state.yaml, .run-identity.json and a
    non-UI sentinel); a run with a served commit also carries a UI lane under ui/."""
    feat = root / ".harness" / "harness" / "features" / "FEAT-9-thing"
    for run_id, _verdict, sha in runs:
        run_dir = feat / "runs" / run_id
        run_dir.mkdir(parents=True)
        (run_dir / "digest.md").write_text(f"digest {run_id}\n")
        (run_dir / "state.yaml").write_text(f"run: {run_id}\n")
        (run_dir / ".run-identity.json").write_text(json.dumps({"run_id": run_id}))
        (run_dir / "notes").mkdir()
        (run_dir / "notes" / "sentinel.txt").write_bytes(f"sentinel {run_id}\n".encode())
        if sha is not None:
            (run_dir / "ui" / "evidence").mkdir(parents=True)
            (run_dir / "ui" / "evidence" / "shot.webp").write_bytes(b"RIFF")
            (run_dir / "ui" / "results.json").write_text(json.dumps({"served_bundle_commit": sha}))
    record = {"review_sha": review_sha, "runs": [
        {"id": r, "squad": "validator" if r.endswith("-validator") else "eng", "verdict": v} for r, v, _ in runs]}
    (feat / "feature.json").write_text(json.dumps(record))
    return feat


def run_dirs(feat):
    return sorted(p.name for p in (feat / "runs").iterdir())


def ui_runs(feat):
    return sorted(p.name for p in (feat / "runs").iterdir() if (p / "ui").is_dir())


def files_bytes(feat, ui):
    """{relative path: bytes} of every run file inside (ui=True) or outside (ui=False) a ui/ lane."""
    runs = feat / "runs"
    return {str(p.relative_to(runs)): p.read_bytes() for p in sorted(runs.rglob("*"))
            if p.is_file() and (p.relative_to(runs).parts[1] == "ui") == ui}


def records_intact(name, feat, before):
    after = files_bytes(feat, ui=False)
    check(name, run_dirs(feat) == ALL_RUNS and after == before,
          f"dirs={run_dirs(feat)} changed={sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))}")


def dry_run_cases(root, feat):
    records, ui, files = files_bytes(feat, ui=False), files_bytes(feat, ui=True), tree_bytes(feat)
    dry = tool(root, "--feature", "FEAT-9-thing", "--dry-run")
    would = [line for line in dry.stdout.splitlines() if line.startswith("would remove")]
    expected = [f"would remove runs/{r}/ui" for r in ALL_RUNS if r not in EXPECTED_KEPT and r != "plan-c0-product"]
    check("dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/",
          dry.returncode == 0 and would == expected, dry.stdout + dry.stderr)
    check("dry-run changes no bytes", files_bytes(feat, ui=True) == ui and ui_runs(feat) == sorted(r for r, _v, s in RUNS if s))
    records_intact("dry-run leaves every run record byte-identical", feat, records)
    check("dry-run leaves every file in the feature byte-identical, feature.json included", tree_bytes(feat) == files)


def retention_cases(root, feat):
    records = files_bytes(feat, ui=False)
    kept_ui = {k: v for k, v in files_bytes(feat, ui=True).items() if k.split("/")[0] in EXPECTED_KEPT}
    pruned = tool(root, "--feature", "FEAT-9-thing")
    check("keeps the ui/ of every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill ui/",
          ui_runs(feat) == EXPECTED_KEPT, str(ui_runs(feat)))
    check("kept runs' UI evidence is byte-identical", files_bytes(feat, ui=True) == kept_ui)
    check("exit 0 and names the ui/ it removed", pruned.returncode == 0 and "runs/fix-c3-eng/ui" in pruned.stdout, pruned.stdout + pruned.stderr)
    records_intact("every run directory, digest.md, state.yaml, .run-identity.json and non-UI sentinel survives prune", feat, records)
    again = tool(root, "--feature", "FEAT-9-thing")
    check("a second prune succeeds and removes nothing more", again.returncode == 0 and ui_runs(feat) == EXPECTED_KEPT
          and "removed" not in again.stdout, again.stdout + again.stderr)
    records_intact("a repeated prune still leaves every run record byte-identical", feat, records)


def explicit_keep_cases():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat = feature(root, RUNS)
        records = files_bytes(feat, ui=False)
        kept = tool(root, "--feature", "FEAT-9-thing", "--keep", "build-c0-eng")
        check("an explicit --keep of an otherwise pruned run keeps its ui/",
              kept.returncode == 0 and ui_runs(feat) == sorted(EXPECTED_KEPT + ["build-c0-eng"]), kept.stdout + kept.stderr)
        records_intact("an explicit --keep prune leaves every run record byte-identical", feat, records)


def recorded(feat, extra):
    """Record extra run ids in feature.json next to the ones already there."""
    record = json.loads((feat / "feature.json").read_text())
    record["runs"] += [{"id": r, "squad": "eng", "verdict": "PASS"} for r in extra]
    (feat / "feature.json").write_text(json.dumps(record))


def records_feature(root):
    """RUNS plus panel, acceptance and nested qa manifests in a kept and a pruned recorded run,
    and an unrecorded run holding both a record and a UI lane."""
    feat = feature(root, RUNS)
    kept, pruned = feat / "runs" / "validate-c2-validator", feat / "runs" / "build-c0-eng"
    (kept / "qa").mkdir()
    (kept / "qa" / "manifest-unit.json").write_bytes(b'{"kind": "unit"}')
    (kept / "panel-c2.md").write_bytes(b"panel c2\n")
    (kept / "acceptance.md").write_bytes(b"acceptance\n")
    (pruned / "qa" / "deep").mkdir(parents=True)
    (pruned / "qa" / "deep" / "manifest-integration.json").write_bytes(b'{"kind": "integration"}')
    stray = feat / "runs" / "stray-run"
    (stray / "ui").mkdir(parents=True)
    (stray / "digest.md").write_bytes(b"unrecorded\n")
    (stray / "ui" / "results.json").write_text(json.dumps({"served_bundle_commit": PIN}))
    return feat


def tracked_repo(root):
    """records_feature committed as DEC-257 tracks it, then a modified tracked record, an
    untracked record in a recorded run and an unrelated change already staged."""
    checkout(root)
    feat = records_feature(root)
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "records")
    with open(feat / "runs" / "validate-c2-validator" / "digest.md", "a", encoding="utf-8") as handle:
        handle.write("edited after commit\n")
    (feat / "runs" / "build-c0-eng" / "late.md").write_bytes(b"late record\n")
    (root / "unrelated.txt").write_bytes(b"pre-staged\n")
    git(root, "add", "unrelated.txt")
    return feat


MODES = (("dry-run", ("--dry-run",)), ("prune", ()))


def unchanged_as_mode(feat, args, before):
    """Dry-run changes no feature byte; a prune keeps every run record and drops fix-c3-eng's ui/."""
    files, records = before
    if args:
        return tree_bytes(feat) == files
    return files_bytes(feat, ui=False) == records and not (feat / "runs" / "fix-c3-eng" / "ui").exists()


def no_git_hooked(label, args):
    """One mode under the audit hook in a fresh tracked repository: (no subprocess, every leg passed)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        feat = tracked_repo(root)
        log = Path(tmp) / "subprocess.log"
        index, before = index_bytes(root), (tree_bytes(feat), files_bytes(feat, ui=False))
        ran = hooked_tool(root, log, "--feature", "FEAT-9-thing", *args)
        started = log.read_text(encoding="utf-8") if log.exists() else ""
        quiet = ran.returncode == 0 and not started
        check(f"{label} starts no subprocess and exits 0", quiet, f"rc={ran.returncode} log={started} {ran.stderr}")
        no_stage = "stage" not in ran.stdout + ran.stderr
        check(f"{label} prints no staging output", no_stage, ran.stdout)
        verb = "would remove" if args else "removed"
        behaves = (f"{verb} runs/fix-c3-eng/ui" in ran.stdout and unchanged_as_mode(feat, args, before)
                   and index_bytes(root) == index)
        check(f"{label} prunes as before and leaves every run record and the index byte-identical", behaves,
              ran.stdout + ran.stderr)
        return quiet, quiet and no_stage and behaves


def no_git_index(label, args):
    """The same mode with no hook in a fresh tracked repository, so a git call that would write the
    index runs and the raw index bytes catch it."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        feat = tracked_repo(root)
        index, before = index_bytes(root), (tree_bytes(feat), files_bytes(feat, ui=False))
        ran = tool(root, "--feature", "FEAT-9-thing", *args)
        same = ran.returncode == 0 and index_bytes(root) == index and unchanged_as_mode(feat, args, before)
        check(f"{label} leaves the real git index byte-identical", same,
              f"rc={ran.returncode} index {len(index)} -> {len(index_bytes(root))} bytes {ran.stderr}")
        return same


def no_git_cases():
    hooked = [no_git_hooked(label, args) for label, args in MODES]
    unhooked = [no_git_index(label, args) for label, args in MODES]
    check("pruner invokes no git subprocess", all(quiet for quiet, _ in hooked))
    check("real temporary git repository index is byte-identical", all(ok for _, ok in hooked) and all(unhooked))


def evidence_feature(root):
    feat = feature(root, [("validate-c1-validator", "FAIL", "a" * 40), ("validate-c2-validator", "FAIL", "b" * 40),
                          ("validate-c3-validator", "PASS", "c" * 40)])
    record = json.loads((feat / "feature.json").read_text())
    for run in record["runs"]:
        raw = (feat / "runs" / run["id"] / "digest.md").read_bytes()
        run["cycle_evidence"] = {"source": "lead-digest", "path": f"runs/{run['id']}/digest.md",
                                 "sha256": hashlib.sha256(raw).hexdigest()}
    (feat / "feature.json").write_text(json.dumps(record))
    return feat


def evidence_refused(root, feat, missing):
    files, index = tree_bytes(feat), index_bytes(root)
    for label, args in (("prune", ()), ("dry-run", ("--dry-run",))):
        refused = tool(root, "--feature", "FEAT-9-thing", *args)
        check(f"{label} refuses with exit 2 naming every missing cycle_evidence path",
              refused.returncode == 2 and all(p in refused.stderr for p in missing), f"rc={refused.returncode} {refused.stderr}")
        check(f"a refused {label} changes no file and no index byte", tree_bytes(feat) == files and index_bytes(root) == index)


def evidence_complete(root, feat):
    index = index_bytes(root)
    complete = tool(root, "--feature", "FEAT-9-thing")
    digests = [feat / "runs" / f"validate-c{n}-validator" / "digest.md" for n in (1, 2, 3)]
    check("complete cycle evidence permits the prune, keeps every digest and leaves the index alone",
          complete.returncode == 0 and all(d.is_file() for d in digests) and index_bytes(root) == index,
          complete.stdout + complete.stderr)


def missing_evidence_cases():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat = evidence_feature(root)
        missing = ["runs/validate-c1-validator/digest.md", "runs/validate-c3-validator/digest.md"]
        saved = {path: (feat / path).read_bytes() for path in missing}
        for path in missing:
            (feat / path).unlink()
        evidence_refused(root, feat, missing)
        for path, raw in saved.items():
            (feat / path).write_bytes(raw)
        evidence_complete(root, feat)


UNREADABLE = ["runs/build-c0-eng/qa", "runs/validate-c2-validator/qa"]


def unreadable_checks(root, feat):
    files, index = tree_bytes(feat / "runs" / "fix-c3-eng" / "ui"), index_bytes(root)
    for label, args in (("dry-run", ("--dry-run",)), ("prune", ())):
        failed = tool(root, "--feature", "FEAT-9-thing", *args)
        check(f"{label} fails with exit 1 naming every unreadable directory under a recorded run",
              failed.returncode == 1 and all(p in failed.stderr for p in UNREADABLE), f"rc={failed.returncode} {failed.stderr}")
        check(f"a {label} over unreadable directories changes no index byte and removes no ui/",
              index_bytes(root) == index and tree_bytes(feat / "runs" / "fix-c3-eng" / "ui") == files)


def unreadable_cases():
    """Unreadable qa/ directories inside recorded runs refuse the prune before anything changes (c1 MF-1)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat = records_feature(root)
        dirs = [feat / p for p in UNREADABLE]
        for qa in dirs:
            qa.chmod(0)
        try:
            if os.access(dirs[0], os.R_OK):
                print("SKIP - unreadable subtree: chmod 000 has no effect for this user (root?)")
                return
            unreadable_checks(root, feat)
        finally:
            for qa in dirs:
                qa.chmod(0o755)


UNREADABLE_UI = ["runs/fix-c3-eng/ui/evidence", "runs/fix-c5-eng/ui", "runs/validate-c2-validator/ui/evidence"]


def readable_bytes(path):
    """{relative path: bytes} of every file os.walk can reach; an unreadable directory is passed over."""
    found = {}
    for current, _dirs, files in os.walk(path):
        for name in files:
            found[os.path.relpath(os.path.join(current, name), path)] = Path(current, name).read_bytes()
    return found


def named_unreadable(stderr):
    _head, sep, tail = stderr.strip().partition("cannot read recorded run content: ")
    return set(tail.split(", ")) if sep else set()


def unreadable_ui_checks(root, feat):
    files, index = readable_bytes(feat), index_bytes(root)
    for label, args in MODES:
        failed = tool(root, "--feature", "FEAT-9-thing", *args)
        check(f"{label} fails with exit 1 naming every unreadable directory under a recorded run's ui/",
              failed.returncode == 1 and set(UNREADABLE_UI) <= named_unreadable(failed.stderr),
              f"rc={failed.returncode} {failed.stderr}")
        check(f"a {label} over unreadable ui/ directories removes no readable lane and changes no index byte",
              readable_bytes(feat) == files and index_bytes(root) == index)


def unreadable_ui_cases():
    """Unreadable directories inside recorded runs' ui/ lanes — a kept lane, a pruned lane's subtree
    and a pruned ui/ itself — beside readable prunable lanes refuse before anything changes (c1 MF-1)."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "repo"
        root.mkdir()
        feat = tracked_repo(root)
        before = tree_bytes(feat)
        dirs = [feat / p for p in UNREADABLE_UI]
        for directory in dirs:
            directory.chmod(0)
        try:
            if os.access(dirs[0], os.R_OK):
                print("SKIP - unreadable ui/: chmod 000 has no effect for this user (root?)")
                return
            unreadable_ui_checks(root, feat)
        finally:
            for directory in dirs:
                directory.chmod(0o755)
        check("refused prunes over unreadable ui/ directories leave every feature file byte-identical",
              tree_bytes(feat) == before)


def outside_ui(base, sha):
    """A directory outside the feature holding a real ui/ lane."""
    (base / "ui" / "evidence").mkdir(parents=True)
    (base / "ui" / "evidence" / "shot.webp").write_bytes(b"RIFF outside")
    (base / "ui" / "results.json").write_text(json.dumps({"served_bundle_commit": sha}))
    return base


def tree_bytes(path):
    return {str(p.relative_to(path)): p.read_bytes() for p in sorted(path.rglob("*")) if p.is_file()}


def linked_feature(root):
    """A kept run, a prunable run, and three link shapes: a run symlink to the kept run, a run
    symlink to an outside directory holding ui/, and a real run whose ui/ links outside."""
    feat = feature(root, [("validate-c2-validator", "PASS", "c" * 40), ("build-c0-eng", "PASS", "a" * 40)])
    runs = feat / "runs"
    (runs / "build-alias").symlink_to("validate-c2-validator", target_is_directory=True)
    (runs / "evil-alias").symlink_to(outside_ui(root / "outside-run", "b" * 40), target_is_directory=True)
    (runs / "ui-link-run").mkdir()
    (runs / "ui-link-run" / "digest.md").write_text("digest ui-link-run\n")
    (runs / "ui-link-run" / "ui").symlink_to(outside_ui(root / "outside-ui", "d" * 40) / "ui", target_is_directory=True)
    return feat, [runs / "validate-c2-validator" / "ui", root / "outside-run" / "ui", root / "outside-ui" / "ui"]


def through_link(stdout, verb):
    return [line for line in stdout.splitlines() if line.startswith(verb)
            and any(f"runs/{name}" in line for name in ("build-alias", "evil-alias", "ui-link-run"))]


def symlink_dry_run(root, destinations, before):
    dry = tool(root, "--feature", "FEAT-9-thing", "--dry-run")
    check("dry-run names no deletion target through a symlink", dry.returncode == 0 and not through_link(dry.stdout, "would remove")
          and "would remove runs/build-c0-eng/ui" in dry.stdout, dry.stdout + dry.stderr)
    check("dry-run leaves every link destination's ui/ byte-identical", [tree_bytes(d) for d in destinations] == before)


def symlink_prune(root, feat, destinations, before):
    pruned = tool(root, "--feature", "FEAT-9-thing")
    check("prune removes no ui/ through a symlink and still prunes the real run",
          pruned.returncode == 0 and not through_link(pruned.stdout, "removed")
          and not (feat / "runs" / "build-c0-eng" / "ui").exists(), pruned.stdout + pruned.stderr)
    skips = [f"skipped runs/{name} (symlink)" for name in ("build-alias", "evil-alias", "ui-link-run/ui")]
    check("prune names each symlink it skipped", all(line in pruned.stdout for line in skips), pruned.stdout)
    after = [tree_bytes(d) for d in destinations]
    check("a kept run, an outside run and an outside ui/ reached through links keep their ui/ bytes",
          after == before and all(after), str([sorted(a) for a in after]))


def symlink_cases():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat, destinations = linked_feature(root)
        recorded(feat, ["build-alias", "evil-alias", "ui-link-run"])
        (root / "outside-notes").mkdir()
        (root / "outside-notes" / "secret.txt").write_bytes(b"external\n")
        (feat / "runs" / "validate-c2-validator" / "notes-link").symlink_to(root / "outside-notes", target_is_directory=True)
        before = [tree_bytes(d) for d in destinations]
        symlink_dry_run(root, destinations, before)
        notes = tree_bytes(root / "outside-notes")
        symlink_prune(root, feat, destinations, before)
        check("a linked subdirectory's external content is left byte-identical", tree_bytes(root / "outside-notes") == notes)


def blocked_feature(root):
    """FEAT-2229's shape: ten recorded validator runs, each digest hash-bound as cycle_evidence,
    the last BLOCKED, no PASS validate/fix run, no UI lane anywhere — an empty keep set under a
    valid review_sha."""
    (root / ".harness" / "factory").mkdir(parents=True)
    (root / ".harness" / "factory" / "fleet.yaml").write_text(
        "schema: factory-fleet/1\nrepos:\n  - name: org/x\n    default_branch: main\nworkspace_root: /nonexistent\n")
    write_config(root / ".harness" / "harness.json")
    feat = root / ".harness" / "harness" / "features" / "FEAT-9-thing"
    (feat / "runs").mkdir(parents=True)
    (feat / "plan.yaml").write_text("schema: plan/1\nfeature: FEAT-9-thing\nstatus: review\nstation_only: true\ntasks: []\n")
    runs = []
    for cycle in range(10):
        run_id, verdict = f"validate-c{cycle}-validator", "BLOCKED" if cycle == 9 else "FAIL"
        raw = f"```yaml\nVERDICT: {verdict}\nDIGEST: {{cycles_used: 1}}\n```\n".encode()
        (feat / "runs" / run_id).mkdir()
        (feat / "runs" / run_id / "digest.md").write_bytes(raw)
        runs.append({"id": run_id, "squad": "validator", "verdict": verdict, "cycles_used": 1,
                     "cycle_evidence": {"source": "lead-digest", "path": f"runs/{run_id}/digest.md",
                                        "sha256": hashlib.sha256(raw).hexdigest()}})
    (feat / "feature.json").write_text(json.dumps(
        {"feature_id": "FEAT-9-thing", "branch": "none", "pr": None, "review_sha": PIN,
         "cycles_used": 10, "max_total_cycles": 10, "runs": runs}))
    return feat, runs


def check_state(root):
    """The real check-state.py, scoped to the fixture feature's cycle-evidence row, rooted at
    the fixture only (inherited roots cleared first)."""
    env = scrubbed_env()
    env.update(HARNESS_PROJECT_DIR=str(root))
    return subprocess.run([sys.executable, str(CHECK_STATE), "--feature", "FEAT-9-thing", "--only", "INV-7"],
                          cwd=root, env=env, capture_output=True, text=True)


def digests_match(feat, runs):
    return [r["id"] for r in runs if not (feat / r["cycle_evidence"]["path"]).is_file()
            or hashlib.sha256((feat / r["cycle_evidence"]["path"]).read_bytes()).hexdigest() != r["cycle_evidence"]["sha256"]]


def blocked_no_ui_cases():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat, runs = blocked_feature(root)
        before = check_state(root)
        check("FEAT-2229 shape: check-state is clean before prune",
              before.returncode == 0 and "VIOLATION" not in before.stdout + before.stderr, before.stdout + before.stderr)
        pruned = tool(root, "--feature", "FEAT-9-thing")
        check("FEAT-2229 shape: an empty keep set still exits 0", pruned.returncode == 0, pruned.stdout + pruned.stderr)
        lost = digests_match(feat, runs)
        check("FEAT-2229 shape: every cycle_evidence digest survives prune at its recorded hash", not lost, f"lost or changed: {lost}")
        after = check_state(root)
        check("FEAT-2229 shape: check-state is still clean after prune",
              after.returncode == 0 and "VIOLATION" not in after.stdout + after.stderr, (after.stdout + after.stderr)[:500])


def refusal_cases(root):
    other = root / "other"
    checkout(other)
    nopin = feature(other, [("validate-c1-validator", "PASS", "a" * 40), ("build-eng", "PASS", "b" * 40)], review_sha="none")
    refused = tool(other, "--feature", "FEAT-9-thing")
    untouched = (nopin / "runs" / "build-eng" / "ui").exists()
    check("refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned", refused.returncode == 2 and untouched, refused.stderr)
    empty = feature(Path(tempfile.mkdtemp()), [("build-eng", "PASS", "b" * 40)], review_sha="")
    refused_empty = tool(empty.parents[3], "--feature", "FEAT-9-thing")
    check("refuses an empty review_sha", refused_empty.returncode == 2 and (empty / "runs" / "build-eng" / "ui").exists(), refused_empty.stderr)
    lookup_refusal_cases(root)
    duplicate_key_case(root)


def lookup_refusal_cases(root):
    typo = tool(root, "--feature", "FEAT-9-thing", "--keep", "validate-c2-validatr")
    check("refuses a --keep that names no run directory", typo.returncode == 2 and "validate-c2-validatr" in typo.stderr, typo.stderr)
    absent = tool(root, "--feature", "FEAT-404")
    check("refuses an unknown feature", absent.returncode == 2, absent.stderr)


def duplicate_key_case(root):
    dup_root = root / "duplicate"
    checkout(dup_root)
    dup = feature(dup_root, [("validate-c1-validator", "PASS", "a" * 40), ("build-eng", "PASS", "b" * 40)])
    (dup / "feature.json").write_text('{"review_sha": "none", "review_sha": "%s", "runs": []}' % PIN)
    refused_dup = tool(dup_root, "--feature", "FEAT-9-thing")
    check("refuses a feature.json with a duplicate key through the canonical reader, pruning nothing (#1993)",
          refused_dup.returncode == 2 and "feature.json" in refused_dup.stderr and (dup / "runs" / "build-eng" / "ui").exists(),
          f"rc={refused_dup.returncode} stderr={refused_dup.stderr}")


REFUSALS = ("Before any mutation, including dry-run, it refuses with exit 2 naming every recorded cycle_evidence "
            "path missing from disk and with exit 1 naming every unreadable directory under a recorded run.")
# DEC-238's ship bullet and the /harness-ship prune paragraph exactly as they stood at 5e51124e,
# each with the anchor the one refusal sentence follows and that sentence exactly as wrapped (#2451).
# Current text must equal the historical text with the insertion, character for character.
SHIP_BULLET = ("""- **Ship keeps the record and drops the rest.** `prune-run-evidence.py` keeps every validator-squad
  validate or fix run (`validate-…`, `fix-cN-…`) recorded PASS — the validator-lead hosts the fix
  team too, so after a failed validate a reader's last PASS lives in a fix run — and every run
  whose `results.json` names the shipped `review_sha`. For every other run (engineering, product,
  reconciliation, distill) it deletes only `runs/<id>/ui/`, never the run directory, `digest.md`,
  `state.yaml` or `.run-identity.json`, because #2177 pins each recorded run's digest as
  check-state cycle evidence. It refuses a feature whose `review_sha` is unset,
  empty or a `PLACEHOLDER_UNSET` value. `/harness-ship` runs it before the ship PR. Trace ZIPs are never
  committed at all (`runs/*/ui/traces/` is ignored); the gate reads them from disk.""",
               "`PLACEHOLDER_UNSET` value.",
               """ Before any mutation, including dry-run, it refuses with
  exit 2 naming every recorded cycle_evidence path missing from disk and with exit 1 naming every
  unreadable directory under a recorded run.""")
SHIP_PARAGRAPH = ("""It keeps every validator-squad validate or fix run recorded PASS (a reader's judgement lives in
  that run's directory, so that is the last PASS of every reader) and every run whose
  `results.json` names the shipped `review_sha`; for every other run (eng, product,
  reconciliation, distill) it deletes only `runs/<id>/ui/`, and refuses a feature whose
  `review_sha` is unset, empty or a placeholder. Every run directory, `digest.md`, `state.yaml`
  and `.run-identity.json` survives — check-state pins each recorded run's digest as cycle
  evidence (#2177). Commit the removal as `[harness:human] <flow-id>: prune run evidence at
  ship`.""",
                  "empty or a placeholder.",
                  """ Before any mutation, including dry-run, it
  refuses with exit 2 naming every recorded cycle_evidence path missing from disk and with exit 1
  naming every unreadable directory under a recorded run.""")
FORBIDDEN = ("force-stag", "force stag", "git add", "`runs/**` is ignored", "runs/** is ignored", "would stage", "staged runs/")
# DEC-257 exactly as it stands: its history quotes two FORBIDDEN phrases in order to reject them, so
# it is exempt from the scan only while it equals this byte for byte; any change to it is scanned.
DEC_257 = """## DEC-257 — Retained run evidence is tracked like any artifact; only run UI is ephemeral

**Chose:** every file a run writes under `.harness/*/features/*/runs/<id>/` is ordinary tracked
material, except `runs/<id>/ui/` (screenshots and traces, which the gate reads from disk). That
covers `digest.md`, `state.yaml`, `.run-identity.json`, acceptance notes, panel files, rulings and
QA receipts. The orchestrator's normal feature-directory commit carries them, with no `git add -f`.
The repository `.gitignore` and the fleet `templates/gitignore.snippet` both ship the one narrow
rule `.harness/*/features/*/runs/*/ui/**`, with no negations, and keep `.harness/**/*.lock`.
`merge-gitignore.py` replaces the two broad rules Harness once shipped (`.harness/features/*/runs/**`
and `.harness/*/features/*/runs/**`) and their false rationale, and `--check` reports them. An
existing checkout narrows through the operator checklist in `references/checkout-upgrade.md`: review
the evidence the old rule hid, stage it by explicit path, and commit it separately before teams
resume.

**Over:** keeping the broad ignore and force-staging the records at some seam, which leaves git
tracking files its own rules ignore, so a re-clone, `git rm -r --cached` or a clean silently
diverges from the record; and letting INV-7 tolerate an absent digest in CI, which deletes the
evidence #2177 pinned.

**Because:** DEC-238 already keeps these records at ship, and INV-7 and INV-36 read them as cycle
evidence. An ignore rule that called them "ephemeral scratch" contradicted both. Nothing in the
flow committed them, so every feature PR went red at the repository-state gate in CI until someone
force-added them by hand (#2399). The rule's deadlock rationale was false too: the dirty-tree halt
(SPEC §8.6) whitelists `.harness/**`.

**Tradeoff accepted:** two gates now see uncommitted run records, by design and with their
semantics unchanged. `merge-gate.py merge-distill` refuses uncommitted `.harness` changes, so a
distill run's own records are committed and pushed before it runs. `feature-worktree.py remove`
refuses an aborted run's untracked records (GATE 2, exit 4) instead of discarding them with the
tree. Retention is unchanged: DEC-238 still decides what ship keeps and what abandon prunes.

**Record:** BUG-2399 (#2399); D-01 signed by fable-advisor under the operator's delegation on
2026-11-22. Cites DEC-238, which it does not amend. Refs: DEC-112, DEC-174.
"""
DOCS = ROOT / ".harness" / "harness" / "docs"
SHIP = ROOT / ".omp" / "commands" / "harness-ship.md"


def claims(text):
    """Forbidden phrases in `text`, in any letter case, matched across line wraps."""
    joined = " ".join(text.split())
    return [phrase for phrase in FORBIDDEN if re.search(re.escape(phrase), joined, re.IGNORECASE)]


def restored(surface):
    """The 5e51124e text with the one refusal sentence inserted after its anchor, exactly."""
    historical, anchor, insertion = surface
    if historical.count(anchor) != 1 or insertion.replace("\n  ", " ") != f" {REFUSALS}":
        return None
    return historical.replace(anchor, anchor + insertion)


def section(text, start, end):
    """text from `start` up to (not including) the first `end` after it; '' when absent."""
    begin = text.find(start)
    stop = text.find(end, begin + len(start)) if begin >= 0 else -1
    return text[begin:stop if stop >= 0 else len(text)] if begin >= 0 else ""


def imported_modules(module):
    names = set()
    for node in ast.walk(module):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names |= {alias.name for alias in node.names} | {getattr(node, "module", None)}
    return names


def pruner_claims(source):
    """The subject itself (TOOL, so PRUNE_RUN_EVIDENCE_BIN switches it): no process launch, no
    staging code, and a docstring stating both refusals."""
    module = ast.parse(source)
    docstring = ast.get_docstring(module) or ""
    bad = sorted(imported_modules(module) & {"subprocess", "pty", "multiprocessing"})
    bad += [call for call in ("os.system", "os.popen", "os.exec", "os.spawn", "_stage") if call in source]
    refusals = all(word in docstring for word in ("Exit 2", "Exit 1", "unreadable", "dry-run included"))
    return bad + ([] if refusals else ["docstring refusals"])


def test_text():
    """This file minus its FORBIDDEN and DEC_257 literals: the phrases it rejects and the pinned
    history it compares against, not claims of its own."""
    source = Path(__file__).read_text(encoding="utf-8")
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") in ("FORBIDDEN", "DEC_257") for t in node.targets):
            source = source.replace(ast.get_source_segment(source, node), "", 1)
    return source


def current_texts():
    """The pruner, this file and harness-ship.md whole; in the decision documents, the surfaces T-01
    owns (DEC-238 and its index row) plus DEC-257 and its row, DEC-257 exempt only while it is
    byte-identical to DEC_257. Other decisions are not T-01's text and are not scanned."""
    decisions = (DOCS / "DECISIONS.md").read_text(encoding="utf-8")
    index = (DOCS / "DECISIONS-INDEX.md").read_text(encoding="utf-8")
    dec_257 = section(decisions, "## DEC-257 ", "\n## DEC-")
    return {
        str(TOOL): TOOL.read_text(encoding="utf-8"),
        "tests/unit/test-prune-run-evidence.py": test_text(),
        "DECISIONS.md DEC-238": section(decisions, "## DEC-238 ", "\n## DEC-"),
        "DECISIONS.md DEC-257": "" if dec_257 == DEC_257 else dec_257,
        "DECISIONS-INDEX.md DEC-238 and DEC-257 rows": section(index, "\n- DEC-238 @", "\n") + section(index, "\n- DEC-257 @", "\n"),
        "harness-ship.md": SHIP.read_text(encoding="utf-8"),
    }


def restoration_errors():
    decisions = (DOCS / "DECISIONS.md").read_text(encoding="utf-8")
    bullet = section(decisions, "- **Ship keeps the record and drops the rest.**", "\n- **")
    bad = [] if bullet == restored(SHIP_BULLET) else ["DEC-238 ship bullet text"]
    generated = subprocess.run([sys.executable, str(BIN / "gen-decisions-index.py"), "--stdout"],
                               capture_output=True, text=True, cwd=ROOT, env=scrubbed_env())
    bad += [] if generated.stdout == (DOCS / "DECISIONS-INDEX.md").read_text(encoding="utf-8") else ["stale DECISIONS-INDEX.md"]
    text = SHIP.read_text(encoding="utf-8")
    paragraph = section(text + "\n", "It keeps every validator-squad validate or fix run", "\n\n")  # ends at a blank line or EOF
    bad += [] if paragraph == restored(SHIP_PARAGRAPH) else ["ship prune paragraph text"]
    order = [text.find(marker) for marker in (
        "- **Terminus:**", '- **On "ship", before the PR — prune run evidence (#1997).**',
        "python3 .claude/skills/harness/bin/prune-run-evidence.py --feature <flow-id> --dry-run\n",
        "python3 .claude/skills/harness/bin/prune-run-evidence.py --feature <flow-id>\n", paragraph)]
    bad += [] if -1 not in order and order == sorted(order) else ["ship step position or invocations"]
    return bad + ([] if "[harness:human] <flow-id>: prune run evidence at\n  ship`" in text else ["ship commit name"])


def five_file_cases():
    """No forbidden claim, in any case, in the five files' current text (current_texts), the restored
    surfaces equal their 5e51124e text plus the one refusal sentence exactly, and the subject launches nothing."""
    bad = [f"{name}: {phrase}" for name, text in current_texts().items() for phrase in claims(text)]
    bad += pruner_claims(TOOL.read_text(encoding="utf-8")) + restoration_errors()
    check("five-file current claims and historical restoration", not bad, str(bad))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat = feature(root, RUNS)
        dry_run_cases(root, feat)
        retention_cases(root, feat)
        refusal_cases(root)
    explicit_keep_cases()
    blocked_no_ui_cases()
    symlink_cases()
    no_git_cases()
    missing_evidence_cases()
    unreadable_cases()
    unreadable_ui_cases()
    five_file_cases()
    print(f"{len(FAILURES)} failure(s)" if FAILURES else "all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
