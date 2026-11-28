#!/usr/bin/env python3
"""DEC-262: a feature's notes/, runs/, observations/ and scratch/, and .harness/notes/, are local
working files. None is tracked, the repository .gitignore ignores each class, and the
committed record (plan.yaml, feature.json, BRIEF.md, STATE.md) stays un-ignored."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FEATURE_JSON = re.compile(r"^\.harness/[^/]+/features/[^/]+/feature\.json$")
WORKING = re.compile(r"^\.harness/[^/]+/features/[^/]+/(notes|runs|observations|scratch)/"
                     r"|^\.harness/notes/")
PATHSPECS = (
    "':(glob).harness/*/features/*/notes/**'",
    "':(glob).harness/*/features/*/runs/**'",
    "':(glob).harness/*/features/*/observations/**'",
    "':(glob).harness/*/features/*/scratch/**'",
    "':(glob).harness/notes/**'",
)
SCRATCH_PROBE = ".harness/harness/features/FEAT-0-probe/scratch/pytest.log"
IGNORED = (
    ".harness/kaya/features/FEAT-0-probe/notes/prototypes/FEAT-0-probe/shot.png",
    ".harness/harness/features/FEAT-0-probe/notes/mockups/shot.png",
    ".harness/harness/features/FEAT-0-probe/runs/r/digest.md",
    ".harness/harness/features/FEAT-0-probe/observations/a.md",
    ".harness/notes/probe.md",
    SCRATCH_PROBE,
)
RECORD = tuple(".harness/harness/features/FEAT-0-probe/" + name
               for name in ("plan.yaml", "feature.json", "BRIEF.md", "STATE.md"))

failures = 0


def check(name, ok, detail=""):
    global failures
    if ok:
        print("ok %s" % name)
    else:
        failures += 1
        print("FAIL %s: %s" % (name, detail))


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, check=False)


listing = git("ls-files", "-z")
check("ls_files_exits_0", listing.returncode == 0, listing.stderr.decode(errors="replace"))
paths = [p for p in listing.stdout.decode("utf-8", errors="replace").split("\0") if p]
check("feature_json_tracked", any(FEATURE_JSON.match(p) for p in paths),
      "no tracked .harness/<repo>/features/<id>/feature.json; the scan is vacuous")
tracked = [p for p in paths if WORKING.match(p)]
check("no_working_files_tracked", not tracked,
      "%d tracked working files, first ten: %s; repair: git rm -r --cached --sparse "
      "--ignore-unmatch -- %s" % (len(tracked), tracked[:10], " ".join(PATHSPECS)))
check("a tracked scratch/ probe is refused", bool(WORKING.match(SCRATCH_PROBE)),
      "WORKING does not match %s" % SCRATCH_PROBE)
for path in IGNORED:
    code = git("check-ignore", "-q", "--no-index", path).returncode
    check("ignored %s" % path, code == 0, "git check-ignore exited %d, want 0" % code)
for path in RECORD:
    code = git("check-ignore", "-q", "--no-index", path).returncode
    check("not_ignored %s" % path, code == 1, "git check-ignore exited %d, want 1" % code)

sys.exit(1 if failures else 0)
