#!/usr/bin/env python3
"""FEAT-2081 SC-01: run-unit-tests.py --shard i/n and --manifest PATH.

Every shard fixture runs in a private copied git repository with its own versioned weight
document; the checkout is never executed against. Witnesses: deterministic completeness,
weighted (not round-robin) partition, equal-weight tie breaking, unknown-file inclusion, empty
shards, malformed arguments, and completed-versus-selected manifest records.
"""
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BIN = ".claude/skills/harness/bin"
DURATIONS = "tests/integration/integration-durations.json"
BIN_FILES = ("run-unit-tests.py", "harness_boundary.py", "run_identity.py",
             "artifact_accessors.py", "suite_layout.py", "run_pool.py")
failures = []


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True,
                          text=True).stdout.strip()


def fixture(integration, weights, unit=("test-u1.py",), default=1.0, failing=()):
    """Private git repo: copied runner, named test files, isolated weight document."""
    root = Path(tempfile.mkdtemp())
    (root / ".harness").mkdir()
    (root / ".harness/team-config.yaml").write_text("teams: []\n")
    exc = root / ".harness/harness/features/FEAT-44-omp-context-advisory/evidence"
    exc.mkdir(parents=True)
    (exc / "probe-session-accessors.ts").write_text("// D-05 documented exception stand-in\n")
    (root / BIN).mkdir(parents=True)
    for name in BIN_FILES:
        shutil.copy2(ROOT / BIN / name, root / BIN / name)
    for kind, names in (("unit", unit), ("integration", integration)):
        (root / "tests" / kind).mkdir(parents=True)
        for name in names:
            code = "raise SystemExit(1)" if name in failing else "pass"
            (root / "tests" / kind / name).write_text(f'print("RAN {name}")\n{code}\n')
    doc = {"schema": 1, "source_run_url": "https://example.invalid/run/1",
           "source_commit": "0" * 40, "default_seconds": default,
           "weights": {f"tests/integration/{k}": v for k, v in weights.items()}}
    (root / DURATIONS).write_text(json.dumps(doc))
    git(root, "init", "-b", "main", "-q")
    git(root, "config", "--local", "maintenance.auto", "false")
    git(root, "config", "--local", "gc.auto", "0")
    git(root, "add", "-A")
    git(root, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-q", "-m", "f")
    return root


def run(root, *args):
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    return subprocess.run([str(root / BIN / "run-unit-tests.py"), *args], cwd=root, env=env,
                          text=True, capture_output=True, timeout=60)


def selected(proc):
    return [line[len("selected "):] for line in proc.stdout.splitlines()
            if line.startswith("selected ")]


def shard_sets(root, kind, count):
    return [selected(run(root, "--kind", kind, "--shard", f"{i}/{count}"))
            for i in range(1, count + 1)]


def with_fixture(build, body):
    root = build()
    try:
        body(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


INTEG = [f"test-i{n:02d}.py" for n in range(1, 8)]


def case_completeness(root):
    first = shard_sets(root, "integration", 3)
    second = shard_sets(root, "integration", 3)
    flat = [path for shard in first for path in shard]
    expected = sorted(f"tests/integration/{n}" for n in INTEG)
    check("every discovered integration file appears in exactly one shard",
          sorted(flat) == expected and len(flat) == len(set(flat)), repr(first))
    check("partition is deterministic across invocations", first == second,
          repr((first, second)))
    check("each shard prints its selection in lexical order",
          all(shard == sorted(shard) for shard in first), repr(first))
    units = shard_sets(root, "unit", 2)
    check("sharding applies to the selected unit suite too",
          sorted(p for s in units for p in s) == ["tests/unit/test-u1.py"], repr(units))


def case_weighted(root):
    sets = shard_sets(root, "integration", 2)
    heavy = [["tests/integration/test-a.py"],
             [f"tests/integration/test-{c}.py" for c in "bcdef"]]
    check("longest-processing-time weighting, not round-robin", sets == heavy, repr(sets))


def case_ties(root):
    sets = shard_sets(root, "integration", 2)
    expected = [["tests/integration/test-a.py", "tests/integration/test-c.py"],
                ["tests/integration/test-b.py", "tests/integration/test-d.py"]]
    check("equal weights break ties by path, then lowest shard", sets == expected, repr(sets))


def case_unknown(root):
    sets = shard_sets(root, "integration", 2)
    flat = [p for s in sets for p in s]
    check("unknown new file uses default_seconds and is included once",
          sets == [["tests/integration/test-new.py"], ["tests/integration/test-old.py"]],
          repr(sets))
    check("stale weight keys add no files",
          "tests/integration/test-gone.py" not in flat, repr(flat))


def case_empty(root):
    manifest = root.parent / f"{root.name}-empty.json"
    proc = run(root, "--kind", "integration", "--shard", "3/3", "--manifest", str(manifest))
    data = json.loads(manifest.read_text()) if manifest.is_file() else {}
    check("empty shard succeeds without invoking the pool",
          proc.returncode == 0 and "pool:" not in proc.stdout and selected(proc) == [],
          proc.stdout + proc.stderr)
    check("empty shard writes an empty completed-file manifest",
          data.get("selected_files") == [] and data.get("completed_files") == []
          and data.get("runner_exit") == 0 and data.get("shard_index") == 3, repr(data))
    manifest.unlink(missing_ok=True)


BAD_ARGS = [
    ("missing shard value", ["--shard"]),
    ("malformed fraction", ["--shard", "1-2"]),
    ("non-decimal", ["--shard", "a/2"]),
    ("signed value", ["--shard", "+1/2"]),
    ("zero index", ["--shard", "0/2"]),
    ("zero count", ["--shard", "1/0"]),
    ("negative", ["--shard", "-1/2"]),
    ("index above count", ["--shard", "3/2"]),
    ("repeated shard", ["--shard", "1/2", "--shard", "2/2"]),
    ("repeated manifest", ["--shard", "1/2", "--manifest", "a.json", "--manifest", "b.json"]),
    ("manifest without shard", ["--manifest", "a.json"]),
    ("missing manifest value", ["--shard", "1/2", "--manifest"]),
    ("check-layout with shard", ["--check-layout", "--shard", "1/2"]),
    ("check-layout with manifest", ["--check-layout", "--manifest", "a.json"]),
]


def case_bad_args(root):
    for label, args in BAD_ARGS:
        proc = run(root, *args)
        check(f"rejects {label} before tests run",
              proc.returncode == 2 and re.search(r"shard|manifest", proc.stderr)
              and "RAN " not in proc.stdout, proc.stdout + proc.stderr)
    inside = run(root, "--shard", "1/1", "--manifest", str(root / BIN / "m.json"))
    check("rejects a manifest inside the watched bin tree",
          inside.returncode == 2 and "manifest" in inside.stderr
          and not (root / BIN / "m.json").exists(), inside.stderr)
    either = run(root, "--shard", "1/1", "--kind", "unit")
    check("--kind accepted after --shard",
          either.returncode == 0 and selected(either) == ["tests/unit/test-u1.py"],
          either.stdout + either.stderr)


def case_manifest(root):
    manifest = root.parent / f"{root.name}-m.json"
    proc = run(root, "--kind", "integration", "--shard", "1/1", "--manifest", str(manifest))
    data = json.loads(manifest.read_text()) if manifest.is_file() else {}
    records = {r.get("path"): r.get("returncode") for r in data.get("completed_files", [])}
    expected = {"tests/integration/test-a.py": 0, "tests/integration/test-b.py": 1}
    check("failing shard exits nonzero", proc.returncode == 1, proc.stdout + proc.stderr)
    check("manifest records actual completed files and their return codes",
          records == expected and len(data.get("completed_files", [])) == 2, repr(data))
    check("manifest identity fields",
          data.get("schema") == 1 and data.get("kind") == "integration"
          and data.get("shard_index") == 1 and data.get("shard_count") == 1
          and data.get("tested_commit") == git(root, "rev-parse", "HEAD")
          and data.get("selected_files") == sorted(expected)
          and data.get("runner_exit") == 1, repr(data))
    manifest.unlink(missing_ok=True)


def case_checked_in_document():
    doc = json.loads((ROOT / DURATIONS).read_text())
    weights = doc.get("weights") if isinstance(doc, dict) else None
    numbers = list(weights.values()) if isinstance(weights, dict) else []

    def positive(value):
        return (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value > 0)

    check("checked-in duration document provenance",
          doc.get("schema") == 1 and doc.get("source_run_url")
          == "https://github.com/mruangutai/harness/actions/runs/37264903064"
          and doc.get("source_commit") == "b046bdfed9fa262a25f53a41d566db2b90cd140b",
          repr({k: v for k, v in doc.items() if k != "weights"}))
    check("checked-in weights are 73 positive finite integration records",
          len(numbers) == 73 and all(positive(v) for v in numbers)
          and all(re.fullmatch(r"tests/integration/test-[^/]+\.py", k) for k in weights))
    check("default_seconds is the median measured duration",
          positive(doc.get("default_seconds"))
          and doc.get("default_seconds") == statistics.median(numbers))


def main():
    with_fixture(lambda: fixture(INTEG, {n: float(i + 1) for i, n in enumerate(INTEG)}),
                 case_completeness)
    weighted = {"test-a.py": 10.0, "test-f.py": 6.0,
                **{f"test-{c}.py": 1.0 for c in "bcde"}}
    with_fixture(lambda: fixture(sorted(weighted), weighted), case_weighted)
    ties = {f"test-{c}.py": 2.0 for c in "abcd"}
    with_fixture(lambda: fixture(sorted(ties), ties), case_ties)
    with_fixture(lambda: fixture(["test-new.py", "test-old.py"],
                                 {"test-old.py": 3.0, "test-gone.py": 99.0}, default=5.0),
                 case_unknown)
    with_fixture(lambda: fixture(["test-a.py"], {"test-a.py": 1.0}), case_empty)
    with_fixture(lambda: fixture(["test-a.py"], {"test-a.py": 1.0}), case_bad_args)
    with_fixture(lambda: fixture(["test-a.py", "test-b.py"], {}, failing=("test-b.py",)),
                 case_manifest)
    case_checked_in_document()
    print(f"\n{len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
