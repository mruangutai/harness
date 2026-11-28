#!/usr/bin/env python3
"""Focused behavioral coverage for check-state.py INV-35.

Written against check-state.sh; #1674 converted the checker to Python while this branch was
open, and a test aimed at a file that no longer exists passes its two "is silent" checks
vacuously. So the checker's absence is a failure here, never an empty output."""

from unit_support import ROOT

import os
from pathlib import Path
import subprocess
import tarfile
import sys
import tempfile

from check_support import Checks
from harness_config_support import write_config

CHECKER_RELATIVE = Path(".claude/skills/harness/bin/check-state.py")
C = Checks()
check = C.check

# (name, notes, expect_report): expect_report asks for an INV-35 line naming #217; otherwise the
# checker must print no INV-35 line at all.
CASES = [
    ("multiline double-quoted #217 is silent",
     'notes: "close out the fix\n  tracked by #217"\n', False),
    ("multiline single-quoted #217 is silent",
     "notes: 'close out the fix\n  tracked by #217'\n", False),
    ("unquoted notes value reports INV-35 naming #217",
     "notes: close out #217\n", True),
]


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
    with tempfile.TemporaryDirectory() as fixture_dir:
        root = Path(fixture_dir)
        feature = root / ".harness/harness/features/FEAT-TEST"
        feature.mkdir(parents=True)
        (root / ".harness/team-config.yaml").write_text("agents: {}\n")
        write_config(root / ".harness/harness.json")
        (feature / "plan.yaml").write_text(
            "schema: plan/1\nfeature: FEAT-TEST\nstatus: review\n"
            "station_only: true\ntasks: []\n" + notes
        )
        result = subprocess.run(
            ["python3", str(checker)], cwd=root, text=True,
            env={**os.environ, "HARNESS_PROJECT_DIR": str(root)},
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        )
        return [line for line in result.stdout.splitlines() if "INV-35" in line]


def main():
    with tempfile.TemporaryDirectory() as checker_dir:
        checker = materialize_checker(checker_dir)
        if not checker.is_file():
            raise SystemExit(f"FAIL - checker missing at {checker}; nothing was tested")
        for name, notes, expect_report in CASES:
            lines = run_checker(checker, notes)
            if expect_report:
                passed = bool(lines) and any("#217" in line for line in lines)
            else:
                passed = not lines
            check(name, passed, "\n".join(lines))
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
