#!/usr/bin/env python3
"""FEAT-2081 SC-01: run-unit-tests.py --shard i/n and --manifest PATH.

Every shard fixture runs in a private copied git repository with its own versioned weight
document; the checkout is never executed against. Witnesses: deterministic completeness,
weighted (not round-robin) partition, equal-weight tie breaking, unknown-file inclusion, empty
shards, malformed arguments, and completed-versus-selected manifest records.
"""
from integration_support import ROOT, BIN

from concurrent.futures import ThreadPoolExecutor
import contextlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import statistics
import subprocess
import tempfile
import sys

from check_support import Checks
from git_support import MAINTENANCE_OFF, checked_git, commit_all, git_out, init_repo

BIN_REL = ".claude/skills/harness/bin"
DURATIONS = "tests/integration/integration-durations.json"
BIN_FILES = ("run-unit-tests.py", "harness_boundary.py", "run_identity.py",
             "artifact_accessors.py", "suite_layout.py", "run_pool.py")
C = Checks()
check = C.check


@contextlib.contextmanager
def fixture(integration, weights, unit=("test-u1.py",), default=1.0, failing=()):
    """Private git repo: copied runner, named test files, isolated weight document.

    The repo is <tmp>/repo, so a case's manifest goes in <tmp> (outside the repo and its bin
    tree) and is removed with the rest of the directory."""
    with tempfile.TemporaryDirectory() as outer:
        root = Path(outer) / "repo"
        build_repo(root, integration, weights, unit, default, failing)
        yield root


def build_repo(root, integration, weights, unit, default, failing):
    (root / ".harness").mkdir(parents=True)
    (root / ".harness/team-config.yaml").write_text("teams: []\n")
    (root / BIN_REL).mkdir(parents=True)
    for name in BIN_FILES:
        shutil.copy2(BIN / name, root / BIN_REL / name)
    for kind, names in (("unit", unit), ("integration", integration)):
        (root / "tests" / kind).mkdir(parents=True)
        for name in names:
            code = "raise SystemExit(1)" if name in failing else "pass"
            (root / "tests" / kind / name).write_text(f'print("RAN {name}")\n{code}\n')
    doc = {"schema": 1, "source_run_url": "https://example.invalid/run/1",
           "source_commit": "0" * 40, "default_seconds": default,
           "weights": {f"tests/integration/{k}": v for k, v in weights.items()}}
    (root / DURATIONS).write_text(json.dumps(doc))
    init_repo(root, "main", config=MAINTENANCE_OFF, git=checked_git)
    commit_all(root, "f", git=checked_git)


def run(root, *args):
    env = dict(os.environ, HARNESS_PROJECT_DIR=str(root))
    return subprocess.run([str(root / BIN_REL / "run-unit-tests.py"), *args], cwd=root, env=env,
                          text=True, capture_output=True, timeout=60)


def selected(proc):
    return [line[len("selected "):] for line in proc.stdout.splitlines()
            if line.startswith("selected ")]


def shard_sets(root, kind, count):
    return [selected(run(root, "--kind", kind, "--shard", f"{i}/{count}"))
            for i in range(1, count + 1)]


def run_with_manifest(root, shard):
    """Run one integration shard with --manifest outside the repo; ({} when none was written)."""
    manifest = root.parent / "m.json"
    proc = run(root, "--kind", "integration", "--shard", shard, "--manifest", str(manifest))
    return proc, (json.loads(manifest.read_text()) if manifest.is_file() else {})


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
    proc, data = run_with_manifest(root, "3/3")
    check("empty shard succeeds without invoking the pool",
          proc.returncode == 0 and "pool:" not in proc.stdout and selected(proc) == [],
          proc.stdout + proc.stderr)
    check("empty shard writes an empty completed-file manifest",
          data.get("selected_files") == [] and data.get("completed_files") == []
          and data.get("runner_exit") == 0 and data.get("shard_index") == 3, repr(data))


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
    with ThreadPoolExecutor() as pool:
        procs = list(pool.map(lambda args: run(root, *args), [args for _, args in BAD_ARGS]))
    for (label, _), proc in zip(BAD_ARGS, procs):
        check(f"rejects {label} before tests run",
              proc.returncode == 2 and re.search(r"shard|manifest", proc.stderr)
              and "RAN " not in proc.stdout, proc.stdout + proc.stderr)
    inside = run(root, "--shard", "1/1", "--manifest", str(root / BIN_REL / "m.json"))
    check("rejects a manifest inside the watched bin tree",
          inside.returncode == 2 and "manifest" in inside.stderr
          and not (root / BIN_REL / "m.json").exists(), inside.stderr)
    either = run(root, "--shard", "1/1", "--kind", "unit")
    check("--kind accepted after --shard",
          either.returncode == 0 and selected(either) == ["tests/unit/test-u1.py"],
          either.stdout + either.stderr)


def case_manifest(root):
    proc, data = run_with_manifest(root, "1/1")
    records = {r.get("path"): r.get("returncode") for r in data.get("completed_files", [])}
    expected = {"tests/integration/test-a.py": 0, "tests/integration/test-b.py": 1}
    check("failing shard exits nonzero", proc.returncode == 1, proc.stdout + proc.stderr)
    check("manifest records actual completed files and their return codes",
          records == expected and len(data.get("completed_files", [])) == 2, repr(data))
    check("manifest identity fields",
          data.get("schema") == 1 and data.get("kind") == "integration"
          and data.get("shard_index") == 1 and data.get("shard_count") == 1
          and data.get("tested_commit") == git_out(root, "rev-parse", "HEAD")
          and data.get("selected_files") == sorted(expected)
          and data.get("runner_exit") == 1, repr(data))


def case_checked_in_document():
    doc = json.loads((ROOT / DURATIONS).read_text())
    weights = doc.get("weights")
    numbers = list(weights.values()) if isinstance(weights, dict) else []

    def positive(value):
        return (isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value > 0)

    # Provenance shape, not one pinned run: the document is re-measured when shards drift.
    check("checked-in duration document provenance",
          doc.get("schema") == 1
          and re.fullmatch(r"https://github\.com/mruangutai/harness/actions/runs/\d+",
                           str(doc.get("source_run_url")))
          and re.fullmatch(r"[0-9a-f]{40}", str(doc.get("source_commit"))),
          repr({k: v for k, v in doc.items() if k != "weights"}))
    check("checked-in weights are positive finite integration records",
          bool(numbers) and all(positive(v) for v in numbers)
          and all(re.fullmatch(r"tests/integration/test-[^/]+\.py", k) for k in weights))
    check("default_seconds is the median measured duration",
          positive(doc.get("default_seconds"))
          and doc.get("default_seconds") == statistics.median(numbers))


def main():
    with fixture(INTEG, {n: float(i + 1) for i, n in enumerate(INTEG)}) as root:
        case_completeness(root)
    weighted = {"test-a.py": 10.0, "test-f.py": 6.0,
                **{f"test-{c}.py": 1.0 for c in "bcde"}}
    with fixture(sorted(weighted), weighted) as root:
        case_weighted(root)
    ties = {f"test-{c}.py": 2.0 for c in "abcd"}
    with fixture(sorted(ties), ties) as root:
        case_ties(root)
    with fixture(["test-new.py", "test-old.py"],
                 {"test-old.py": 3.0, "test-gone.py": 99.0}, default=5.0) as root:
        case_unknown(root)
    # case_empty writes only outside the repo, and case_bad_args reads nothing it wrote.
    with fixture(["test-a.py"], {"test-a.py": 1.0}) as root:
        case_empty(root)
        case_bad_args(root)
    with fixture(["test-a.py", "test-b.py"], {}, failing=("test-b.py",)) as root:
        case_manifest(root)
    case_checked_in_document()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
