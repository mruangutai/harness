#!/usr/bin/env python3
"""prune-run-evidence.py — at ship, a feature keeps the evidence that still means something
(the shipped pin's validate run and the last PASS validate before it) and drops the rest (#1997)."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / ".claude" / "skills" / "harness" / "bin" / "prune-run-evidence.py"
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
]
EXPECTED_KEPT = ["fix-c5-validator", "simplify-eng", "validate-c2-validator"]


def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL") + " - " + name)
    if not condition:
        FAILURES.append(name)
        print("       " + detail[:500])


def tool(root, *args):
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root), *args], capture_output=True, text=True)


def checkout(root):
    (root / ".harness").mkdir(parents=True, exist_ok=True)
    (root / ".harness" / "team-config.yaml").write_text("agents: {}\n")


def feature(root, runs, review_sha=PIN):
    feat = root / ".harness" / "harness" / "features" / "FEAT-9-thing"
    for run_id, _verdict, sha in runs:
        (feat / "runs" / run_id / "ui" / "evidence").mkdir(parents=True)
        (feat / "runs" / run_id / "ui" / "evidence" / "shot.webp").write_bytes(b"RIFF")
        (feat / "runs" / run_id / "ui" / "results.json").write_text(json.dumps({"served_bundle_commit": sha}))
        (feat / "runs" / run_id / "digest.md").write_text("digest\n")
    record = {"review_sha": review_sha, "runs": [
        {"id": r, "squad": "validator" if r.endswith("-validator") else "eng", "verdict": v} for r, v, _ in runs]}
    (feat / "feature.json").write_text(json.dumps(record))
    return feat


def remaining(feat):
    return sorted(p.name for p in (feat / "runs").iterdir())


def dry_run_cases(root, feat):
    dry = tool(root, "--feature", "FEAT-9-thing", "--dry-run")
    would = [line for line in dry.stdout.splitlines() if line.startswith("would remove")]
    names_failed = any("validate-c1-validator" in line for line in would)
    names_pin = any(("simplify-eng" in line or "fix-c5-validator" in line) for line in would)
    check("dry-run lists the runs it would drop", dry.returncode == 0 and names_failed and not names_pin, dry.stdout + dry.stderr)
    check("dry-run removes nothing", len(remaining(feat)) == len(RUNS))


def retention_cases(root, feat):
    pruned = tool(root, "--feature", "FEAT-9-thing")
    kept = remaining(feat)
    check("keeps every PASS validator validate/fix run and any run bound to the pin; drops eng, failed, reconciliation, distill", kept == EXPECTED_KEPT, str(kept))
    check("exit 0 and names what it removed", pruned.returncode == 0 and "fix-c3-eng" in pruned.stdout, pruned.stdout + pruned.stderr)
    extra = tool(root, "--feature", "FEAT-9-thing", "--keep", "validate-c2-validator")
    check("an explicit --keep is honoured and a second run is a no-op", extra.returncode == 0 and remaining(feat) == EXPECTED_KEPT, extra.stdout)


def refusal_cases(root):
    other = root / "other"
    checkout(other)
    nopin = feature(other, [("validate-c1-validator", "PASS", "a" * 40), ("build-eng", "PASS", "b" * 40)], review_sha="none")
    refused = tool(other, "--feature", "FEAT-9-thing")
    untouched = (nopin / "runs" / "build-eng").exists()
    check("refuses the placeholder review_sha 'none' — nothing shipped, nothing pruned", refused.returncode == 2 and untouched, refused.stderr)
    empty = feature(Path(tempfile.mkdtemp()), [("build-eng", "PASS", "b" * 40)], review_sha="")
    refused_empty = tool(empty.parents[3], "--feature", "FEAT-9-thing")
    check("refuses an empty review_sha", refused_empty.returncode == 2 and (empty / "runs" / "build-eng").exists(), refused_empty.stderr)
    typo = tool(root, "--feature", "FEAT-9-thing", "--keep", "validate-c2-validatr")
    check("refuses a --keep that names no run directory", typo.returncode == 2 and "validate-c2-validatr" in typo.stderr, typo.stderr)
    absent = tool(root, "--feature", "FEAT-404")
    check("refuses an unknown feature", absent.returncode == 2, absent.stderr)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        checkout(root)
        feat = feature(root, RUNS)
        dry_run_cases(root, feat)
        retention_cases(root, feat)
        refusal_cases(root)
    print(f"{len(FAILURES)} failure(s)" if FAILURES else "all checks passed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
