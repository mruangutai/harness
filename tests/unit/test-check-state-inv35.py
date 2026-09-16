#!/usr/bin/env python3
"""Focused behavioral coverage for check-state.py INV-35.

Written against check-state.sh; #1674 converted the checker to Python while this branch was
open, and a test aimed at a file that no longer exists passes its two "is silent" checks
vacuously. So the checker's absence is a failure here, never an empty output."""

import os
from pathlib import Path
import subprocess
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[2]
CHECKER_RELATIVE = Path(".claude/skills/harness/bin/check-state.py")
FAILURES = []


def materialize_checker(directory):
    revision = os.environ.get("CHECK_STATE_REV")
    if not revision:
        return ROOT / CHECKER_RELATIVE

    archive = Path(directory) / "checker.tar"
    subprocess.run(
        ["git", "archive", "--format=tar", f"--output={archive}", revision,
         str(CHECKER_RELATIVE.parent)],
        cwd=ROOT,
        check=True,
    )
    extracted = Path(directory) / "revision"
    extracted.mkdir()
    with tarfile.open(archive) as bundle:
        bundle.extractall(extracted, filter="data")
    return extracted / CHECKER_RELATIVE


def run_checker(checker, notes):
    if not checker.is_file():
        raise SystemExit(f"FAIL - checker missing at {checker}; nothing was tested")
    with tempfile.TemporaryDirectory() as fixture_dir:
        root = Path(fixture_dir)
        feature = root / ".harness/harness/features/FEAT-TEST"
        feature.mkdir(parents=True)
        (root / ".harness/team-config.yaml").write_text("agents: {}\n")
        (root / ".harness/harness.json").write_text(
            '{"github": {"sync": false, "repo": null}}\n'
        )
        (feature / "plan.yaml").write_text(
            "schema: plan/1\nfeature: FEAT-TEST\nstatus: done\n"
            "station_only: true\ntasks: []\n" + notes
        )
        environment = dict(os.environ)
        environment["CLAUDE_PROJECT_DIR"] = str(root)
        environment["HARNESS_PROJECT_DIR"] = str(root)
        result = subprocess.run(
            ["python3", str(checker)], cwd=root, text=True, env=environment,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        return [line for line in result.stdout.splitlines() if "INV-35" in line]


def check(name, condition, detail):
    print(("PASS" if condition else "FAIL") + " - " + name)
    if not condition:
        FAILURES.append(name)
        print("       " + detail[:500])


def main():
    with tempfile.TemporaryDirectory() as checker_dir:
        checker = materialize_checker(checker_dir)

        double_lines = run_checker(
            checker, 'notes: "close out the fix\n  tracked by #217"\n'
        )
        check(
            "multiline double-quoted #217 is silent",
            not double_lines,
            "\n".join(double_lines),
        )

        single_lines = run_checker(
            checker, "notes: 'close out the fix\n  tracked by #217'\n"
        )
        check(
            "multiline single-quoted #217 is silent",
            not single_lines,
            "\n".join(single_lines),
        )

        unquoted_lines = run_checker(checker, "notes: close out #217\n")
        check(
            "unquoted notes value reports INV-35 naming #217",
            bool(unquoted_lines) and any("#217" in line for line in unquoted_lines),
            "\n".join(unquoted_lines),
        )

    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
