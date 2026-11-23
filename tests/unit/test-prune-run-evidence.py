#!/usr/bin/env python3
"""prune-run-evidence.py — at ship, a feature keeps the UI evidence that still means something
(every PASS validator validate/fix run and every run bound to the shipped pin) and drops only
the other runs' `runs/<id>/ui/` (#1997). Every run directory, digest.md, state.yaml,
.run-identity.json and other non-UI file survives byte-for-byte (#2294): #2177 pins each recorded
run's digest as check-state cycle evidence. Every surviving non-UI file of each feature.json
recorded run is force-staged into the git index (`runs/**` is ignored), and a missing
cycle_evidence path refuses with exit 2 before anything changes (#2399). Fixtures are real git
repositories with the run directories ignored, so the index assertions exercise `git add -f`.

PRUNE_RUN_EVIDENCE_BIN overrides the subject so the regressions can be proven RED against a
reverted copy of the pruner."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
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


def tool(root, *args):
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root), *args], capture_output=True, text=True)


def git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-C", str(root), *args],
                          capture_output=True, env=env, check=True).stdout


def checkout(root):
    """A real git repository that ignores run directories the way .gitignore:11 does."""
    (root / ".harness").mkdir(parents=True, exist_ok=True)
    (root / ".harness" / "team-config.yaml").write_text("agents: {}\n")
    (root / ".gitignore").write_text(".harness/*/features/*/runs/**\n")
    git(root, "init", "-q")
    git(root, "add", ".gitignore", ".harness/team-config.yaml")
    git(root, "commit", "-q", "-m", "init")


def staged_runs(root, feat):
    """{path relative to runs/: index blob bytes} of every indexed file under the feature's runs/."""
    prefix = str((feat / "runs").relative_to(root)) + "/"
    paths = [p for p in git(root, "ls-files", "-z").decode().split("\0") if p.startswith(prefix)]
    return {p[len(prefix):]: git(root, "cat-file", "blob", f":{p}") for p in paths}


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
    records, ui = files_bytes(feat, ui=False), files_bytes(feat, ui=True)
    dry = tool(root, "--feature", "FEAT-9-thing", "--dry-run")
    would = [line for line in dry.stdout.splitlines() if line.startswith("would remove")]
    expected = [f"would remove runs/{r}/ui" for r in ALL_RUNS if r not in EXPECTED_KEPT and r != "plan-c0-product"]
    check("dry-run names exactly the ui/ lanes it would drop — no kept run, no run without ui/",
          dry.returncode == 0 and would == expected, dry.stdout + dry.stderr)
    check("dry-run changes no bytes", files_bytes(feat, ui=True) == ui and ui_runs(feat) == sorted(r for r, _v, s in RUNS if s))
    records_intact("dry-run leaves every run record byte-identical", feat, records)


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


def staging_feature(root):
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


def expected_staged(feat):
    return {k: v for k, v in files_bytes(feat, ui=False).items() if not k.startswith("stray-run/")}


def staging_dry_run(root, feat, expected):
    files, index = tree_bytes(feat), index_bytes(root)
    dry = tool(root, "--feature", "FEAT-9-thing", "--dry-run")
    would = sorted(line for line in dry.stdout.splitlines() if line.startswith("would stage"))
    check("dry-run names every non-UI file of every recorded run it would stage, and nothing else",
          dry.returncode == 0 and would == sorted(f"would stage runs/{k}" for k in expected), dry.stdout + dry.stderr)
    check("dry-run leaves every file and the git index byte-identical",
          tree_bytes(feat) == files and index_bytes(root) == index and not staged_runs(root, feat))


def staging_prune(root, feat, expected):
    pruned = tool(root, "--feature", "FEAT-9-thing")
    staged = staged_runs(root, feat)
    check("prune force-stages every surviving non-UI file of every recorded run, kept or pruned, nested qa/ included, byte-identical",
          pruned.returncode == 0 and staged == expected,
          f"rc={pruned.returncode} missing={sorted(set(expected) - set(staged))} extra={sorted(set(staged) - set(expected))}")
    check("prune stages no ui/ file and nothing of an unrecorded run",
          not [k for k in staged if k.split("/")[1] == "ui" or k.startswith("stray-run/")], str(sorted(staged)))


def staging_cases():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat = staging_feature(root)
        expected = expected_staged(feat)
        staging_dry_run(root, feat, expected)
        staging_prune(root, feat, expected)
        again = tool(root, "--feature", "FEAT-9-thing")
        check("a repeated prune exits 0 and leaves the same staged records",
              again.returncode == 0 and staged_runs(root, feat) == expected, again.stdout + again.stderr)


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
    complete = tool(root, "--feature", "FEAT-9-thing")
    staged = staged_runs(root, feat)
    digests = [f"validate-c{n}-validator/digest.md" for n in (1, 2, 3)]
    check("complete cycle evidence permits the prune and stages every digest",
          complete.returncode == 0 and all(d in staged for d in digests), complete.stdout + complete.stderr)


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


def symlink_staging(root, feat):
    staged = sorted(staged_runs(root, feat))
    through = [k for k in staged if k.split("/")[0] in ("build-alias", "evil-alias") or "/notes-link/" in f"/{k}"]
    check("staging never follows a linked run or linked subdirectory and stages no external content",
          not through and "ui-link-run/digest.md" in staged and "validate-c2-validator/digest.md" in staged, str(staged))


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
        symlink_prune(root, feat, destinations, before)
        symlink_staging(root, feat)


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
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR")}
    env.update(CLAUDE_PROJECT_DIR=str(root), HARNESS_PROJECT_DIR=str(root))
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
    staging_cases()
    missing_evidence_cases()
    print(f"{len(FAILURES)} failure(s)" if FAILURES else "all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
