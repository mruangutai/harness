#!/usr/bin/env python3
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = Path(__file__).resolve().parent
ROOT = TESTS_DIR.parents[1]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import suite_layout

# Exactly four implementation sites are expected on purpose.
SOLE_IMPLEMENTATION_EXEMPTIONS = [
    ".claude/skills/harness/bin/suite_layout.py",
    "tests/unit/test-suite-layout.py",
    "tests/integration/test-run-unit-tests-layout.py",
    "tests/manual/suite-census.py",
]
KIND_PATTERNS = (
    re.compile(r"""tests['"]?\s*[,/]\s*['"]?\s*unit"""),
    re.compile(r"""tests['"]?\s*[,/]\s*['"]?\s*integration"""),
)
DISCOVERY_FRAGMENTS = (
    "os.listdir", "os.scandir", "os.walk", "glob.glob",
    "iterdir", "rglob", ".glob(",
)

failures = []
def check(name, condition, detail=""):
    print(("PASS" if condition else "FAIL"), name, detail if not condition else "")
    if not condition:
        failures.append(name)

def sole_implementations(root, relative_paths):
    matches = []
    for relative in relative_paths:
        path = root / relative
        if not path.is_file():
            continue
        source = path.read_text(errors="replace")
        if all(pattern.search(source) for pattern in KIND_PATTERNS) and any(
                fragment in source for fragment in DISCOVERY_FRAGMENTS):
            matches.append(relative)
    return matches

check("real layout is valid", suite_layout.violations(ROOT) == [],
      repr(suite_layout.violations(ROOT)))

def legal_tree():
    td = Path(tempfile.mkdtemp())
    (td / "tests/unit").mkdir(parents=True)
    (td / "tests/integration").mkdir(parents=True)
    (td / ".claude/skills/harness/bin").mkdir(parents=True)
    (td / "tests/unit/test-unit.py").write_text("pass\n")
    (td / "tests/integration/test-integration.py").write_text("pass\n")
    return td

def add_nested_test(root):
    path = root / "tests/integration/api/test-nested.py"
    path.parent.mkdir()
    path.write_text("pass\n")


def add_undiscoverable_test(root):
    (root / "tests/unit/test_hidden.py").write_text("pass\n")


for name, mutate, needle in [
    ("empty unit", lambda r: (r/"tests/unit/test-unit.py").unlink(), "tests/unit"),
    ("empty integration", lambda r: (r/"tests/integration/test-integration.py").unlink(), "tests/integration"),
    ("duplicate", lambda r: (r/"tests/integration/test-unit.py").write_text("pass\n"), "test-unit.py"),
    ("planted bin test", lambda r: (r/".claude/skills/harness/bin/test-planted.py").write_text("pass\n"), "test-planted.py"),
    ("nested test", add_nested_test, "test-nested.py"),
    ("undiscoverable test name", add_undiscoverable_test, "test_hidden.py")]:
    r = legal_tree()
    try:
        mutate(r)
        got = suite_layout.violations(r)
        check(name, len(got) == 1 and needle in got[0], repr(got))
    finally:
        shutil.rmtree(r)

r = legal_tree()
try:
    (r/"tests/unit/test-unit.py").unlink()
    (r/"tests/integration/test-integration.py").unlink()
    (r/".claude/skills/harness/bin/test-planted.py").write_text("pass\n")
    (r/".claude/skills/harness/bin/probe-planted.py").write_text("pass\n")
    got = suite_layout.violations(r)
    check("all layout violations reported", len(got) == 4, repr(got))
finally:
    shutil.rmtree(r)

repo_cfg = json.loads((ROOT/".harness/harness.json").read_text())
tpl_cfg = json.loads((ROOT/".claude/skills/harness/templates/harness.json").read_text())
for kind in ("unit", "integration"):
    got = repo_cfg["test_kinds"][kind]["detect"]
    check(f"{kind} detect matches template", got == tpl_cfg["test_kinds"][kind]["detect"])
    check(f"{kind} detect excludes .claude", ".claude/" not in got)
active = [v["detect"] for v in repo_cfg["test_kinds"].values() if v.get("status") == "active"]
check("manual tests are not actively detected", all("tests/manual" not in d for d in active))

tracked = subprocess.run(
    ["git", "ls-files", "--", "*.py"], cwd=ROOT, check=True,
    text=True, capture_output=True).stdout.splitlines()
check("sole implementation discovery floor", len(tracked) >= 90, str(len(tracked)))
implementations = sole_implementations(ROOT, tracked)
unexpected = sorted(set(implementations) - set(SOLE_IMPLEMENTATION_EXEMPTIONS))
check("sole implementation sweep", unexpected == [], repr(unexpected))
for expected in (".claude/skills/harness/bin/suite_layout.py",
                 "tests/manual/suite-census.py"):
    check(f"sole implementation positive control {expected}",
          expected in implementations, repr(implementations))

shapes = (
    'os.listdir("tests/unit"); os.listdir("tests/integration")\n',
    'os.listdir(os.path.join(r, "tests", "unit")); os.listdir(os.path.join(r, "tests", "integration"))\n',
    'Path(r, "tests", "unit").glob("*"); Path(r, "tests", "integration").glob("*")\n',
)
for number, source in enumerate(shapes, 1):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        relative = "tests/unit/kindcheck_helper.py"
        (root / relative).parent.mkdir(parents=True)
        (root / relative).write_text(source)
        found = sole_implementations(root, [relative])
        check(f"sole implementation red proof shape {number}",
              relative in found
              and bool(set(found) - set(SOLE_IMPLEMENTATION_EXEMPTIONS)),
              repr(found))

runner = (BIN/"run-unit-tests.sh").read_text().splitlines()
check("runner delegates layout once",
      sum("suite_layout" in line and not line.strip().startswith("#")
          for line in runner) == 1)
raise SystemExit(1 if failures else 0)
