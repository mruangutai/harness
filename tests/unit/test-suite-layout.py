#!/usr/bin/env python3
import fnmatch
import json
import os
from pathlib import Path
import posixpath
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
import code_grade

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

def _is_violations_invocation(line):
    """True when line invokes suite_layout.violations(...) with an argument --
    excludes the zero-arg `suite_layout.violations()` mention that appears in
    layout_fixtures.py's own docstring, which is prose, not a call."""
    return re.search(r"suite_layout\.violations\(\s*[^)\s]", line) is not None


def _violations_callers(root, source_extensions):
    """Non-test, git-tracked, source-extension files that invoke
    suite_layout.violations(...). Comment lines never count as callers."""
    tracked = subprocess.run(
        ["git", "ls-files"], cwd=root, check=True,
        text=True, capture_output=True).stdout.splitlines()
    callers = []
    for rel in tracked:
        if rel.startswith("tests/"):
            continue
        if os.path.splitext(rel)[1] not in source_extensions:
            continue
        for line in (root / rel).read_text().splitlines():
            if line.strip().startswith("#"):
                continue
            if _is_violations_invocation(line):
                callers.append(rel)
                break
    return sorted(set(callers))


check("violations() has exactly one non-test caller repository-wide",
      set(_violations_callers(ROOT, suite_layout.SOURCE_EXTENSIONS))
      == {".claude/skills/harness/bin/run-unit-tests.sh"},
      repr(_violations_callers(ROOT, suite_layout.SOURCE_EXTENSIONS)))

def base_git_fixture(include_self=True):
    td = Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-b", "main", "-q"], cwd=td, check=True)
    (td / ".harness").mkdir(parents=True)
    (td / ".harness/team-config.yaml").write_text("teams: {}\n")
    (td / "tests/unit").mkdir(parents=True)
    (td / "tests/integration").mkdir(parents=True)
    (td / "tests/manual").mkdir(parents=True)
    (td / "tests/unit/test-unit.py").write_text("pass\n")
    (td / "tests/integration/test-integration.py").write_text("pass\n")
    (td / "tests/manual/probe-fixture.py").write_text("pass\n")
    if include_self:
        (td / ".claude/skills/harness/bin").mkdir(parents=True)
        shutil.copy(BIN / "suite_layout.py", td / ".claude/skills/harness/bin/suite_layout.py")
    return td


def git_commit(td, message="fixture"):
    subprocess.run(["git", "add", "-A"], cwd=td, check=True)
    subprocess.run(
        ["git", "-c", "user.email=t@example.com", "-c", "user.name=t",
         "commit", "-q", "-m", message],
        cwd=td, check=True)


# Case 1: rogue tracked file outside tests/ is refused, and the exact-equality
# assertion that grades SC-06's first clause once DOCUMENTED_EXCEPTIONS is cleared.
td = base_git_fixture()
try:
    (td / ".harness/tools").mkdir(parents=True)
    (td / ".harness/tools/test_rogue.py").write_text("pass\n")
    git_commit(td)
    got = suite_layout.violations(td)
    matches = [g for g in got if "test_rogue.py" in g]
    check("case 1: rogue tracked file reported exactly once as the outside-tests finding",
          matches == ["tracked test-shaped file outside tests/: .harness/tools/test_rogue.py"],
          repr(got))
    check("case 1: legal manual probe file is not named by any finding",
          not any("probe-fixture.py" in g for g in got), repr(got))

    saved_exceptions = suite_layout.DOCUMENTED_EXCEPTIONS
    suite_layout.DOCUMENTED_EXCEPTIONS = ()
    try:
        got_cleared = suite_layout.violations(td)
    finally:
        suite_layout.DOCUMENTED_EXCEPTIONS = saved_exceptions
    check("case 1: exact one-element violation list with exceptions cleared",
          got_cleared == ["tracked test-shaped file outside tests/: .harness/tools/test_rogue.py"],
          repr(got_cleared))
finally:
    shutil.rmtree(td)

# Case 2: the same shape, untracked, is invisible — tracked-versus-untracked.
td = base_git_fixture()
try:
    git_commit(td)
    (td / ".harness/tools").mkdir(parents=True)
    (td / ".harness/tools/test_rogue.py").write_text("pass\n")
    got = suite_layout.violations(td)
    check("case 2: untracked rogue file is not reported",
          not any("test_rogue.py" in g for g in got), repr(got))
finally:
    shutil.rmtree(td)

# Case 3: three rogue tracked files in different directories, stable sorted order.
td = base_git_fixture()
try:
    (td / ".harness/tools").mkdir(parents=True)
    (td / ".harness/tools/test_rogue.py").write_text("pass\n")
    (td / ".harness/notes").mkdir(parents=True)
    (td / ".harness/notes/test_second.py").write_text("pass\n")
    (td / ".harness/evidence").mkdir(parents=True)
    (td / ".harness/evidence/test_third.py").write_text("pass\n")
    git_commit(td)
    got1 = suite_layout.violations(td)
    rogue_findings = [g for g in got1 if g.startswith("tracked test-shaped file outside tests/:")]
    expected = [
        f"tracked test-shaped file outside tests/: {p}"
        for p in sorted([
            ".harness/evidence/test_third.py",
            ".harness/notes/test_second.py",
            ".harness/tools/test_rogue.py",
        ])
    ]
    check("case 3: all three rogue files reported in sorted path order",
          rogue_findings == expected, repr(got1))
    got2 = suite_layout.violations(td)
    check("case 3: repeat call returns an identical list", got2 == got1, repr((got1, got2)))
finally:
    shutil.rmtree(td)

# Case 4: a broken .git (empty directory) fails closed with exactly one finding.
td = base_git_fixture()
try:
    shutil.rmtree(td / ".git")
    (td / ".git").mkdir()
    got = suite_layout.violations(td)
    enumerate_findings = [g for g in got if g.startswith("cannot enumerate tracked files under")]
    check("case 4: exactly one enumeration-failure finding", len(enumerate_findings) == 1, repr(got))
    check("case 4: no tracked-dependent finding is present",
          not any(g.startswith("tracked test-shaped file outside tests/:") for g in got)
          and not any("no longer tracked" in g for g in got),
          repr(got))
finally:
    shutil.rmtree(td)

# Case 5: a non-git tree is unaffected by the tracked-outside-tests clause, which
# never fires without a .git index.
r = legal_tree()
try:
    (r/"tests/unit/test-unit.py").unlink()
    (r/"tests/integration/test-integration.py").unlink()
    (r/".claude/skills/harness/bin/test-planted.py").write_text("pass\n")
    (r/".claude/skills/harness/bin/probe-planted.py").write_text("pass\n")
    got = suite_layout.violations(r)
    check("case 5: non-git tree still returns exactly its four findings", len(got) == 4, repr(got))
finally:
    shutil.rmtree(r)

# Case 6: registry self-policing, each rebound temporarily in a try/finally.
td = base_git_fixture()
try:
    (td / ".harness/tools").mkdir(parents=True)
    (td / ".harness/tools/test_rogue.py").write_text("pass\n")
    git_commit(td)
    rogue_rel = ".harness/tools/test_rogue.py"
    saved_exceptions = suite_layout.DOCUMENTED_EXCEPTIONS

    suite_layout.DOCUMENTED_EXCEPTIONS = ((rogue_rel, "accepted for case 6"),)
    try:
        got = suite_layout.violations(td)
    finally:
        suite_layout.DOCUMENTED_EXCEPTIONS = saved_exceptions
    check("case 6: listed tracked rogue path is accepted",
          not any(g.startswith("tracked test-shaped file outside tests/:") and rogue_rel in g
                  for g in got),
          repr(got))

    suite_layout.DOCUMENTED_EXCEPTIONS = (("foo/test-*.py", "glob reason"),)
    try:
        got = suite_layout.violations(td)
    finally:
        suite_layout.DOCUMENTED_EXCEPTIONS = saved_exceptions
    check("case 6: glob entry refused as not an exact path",
          "documented exception is not an exact path: foo/test-*.py" in got, repr(got))

    suite_layout.DOCUMENTED_EXCEPTIONS = ((rogue_rel, "one"), (rogue_rel, "two"))
    try:
        got = suite_layout.violations(td)
    finally:
        suite_layout.DOCUMENTED_EXCEPTIONS = saved_exceptions
    check("case 6: duplicate entry refused as listed twice",
          f"documented exception is listed twice: {rogue_rel}" in got, repr(got))

    suite_layout.DOCUMENTED_EXCEPTIONS = ((".harness/team-config.yaml", "not test-shaped"),)
    try:
        got = suite_layout.violations(td)
    finally:
        suite_layout.DOCUMENTED_EXCEPTIONS = saved_exceptions
    check("case 6: non-test-shaped entry refused as unnecessary",
          "documented exception is unnecessary: .harness/team-config.yaml" in got, repr(got))

    suite_layout.DOCUMENTED_EXCEPTIONS = (("does/not/exist/test_x.py", "not tracked"),)
    try:
        got = suite_layout.violations(td)
    finally:
        suite_layout.DOCUMENTED_EXCEPTIONS = saved_exceptions
    check("case 6: untracked entry refused as no longer tracked",
          "documented exception is no longer tracked: does/not/exist/test_x.py" in got, repr(got))
finally:
    shutil.rmtree(td)

# Case 7: the live registry is load-bearing over the real repository root.
live_exception_path = suite_layout.DOCUMENTED_EXCEPTIONS[0][0]
saved_exceptions = suite_layout.DOCUMENTED_EXCEPTIONS
suite_layout.DOCUMENTED_EXCEPTIONS = ()
try:
    got = suite_layout.violations(ROOT)
finally:
    suite_layout.DOCUMENTED_EXCEPTIONS = saved_exceptions
check("case 7: live registry entry is load-bearing when cleared",
      any(live_exception_path in g for g in got), repr(got))
check("case 7: real layout is clean with the registry restored",
      suite_layout.violations(ROOT) == [], repr(suite_layout.violations(ROOT)))

# Case 8: extension-restricted boundary — probe-shaped Markdown is legal, .py is not.
td = base_git_fixture()
try:
    (td / ".harness/notes").mkdir(parents=True)
    (td / ".harness/notes/probe-something.md").write_text("notes\n")
    (td / ".harness/notes/probe-something.py").write_text("pass\n")
    git_commit(td)
    got = suite_layout.violations(td)
    check("case 8: markdown probe record is not flagged",
          not any("probe-something.md" in g for g in got), repr(got))
    check("case 8: python probe file is flagged",
          "tracked test-shaped file outside tests/: .harness/notes/probe-something.py" in got,
          repr(got))
finally:
    shutil.rmtree(td)

# Case 9: self-ownership is load-bearing in the other direction — a repo not
# shipping suite_layout.py itself is untouched by the outside-tests clause.
td = Path(tempfile.mkdtemp())
try:
    subprocess.run(["git", "init", "-b", "main", "-q"], cwd=td, check=True)
    (td / "tests/unit").mkdir(parents=True)
    (td / "tests/integration").mkdir(parents=True)
    (td / "tests/unit/test-unit.py").write_text("pass\n")
    (td / "tests/integration/test-integration.py").write_text("pass\n")
    (td / ".harness/tools").mkdir(parents=True)
    (td / ".harness/tools/test_rogue.py").write_text("pass\n")
    git_commit(td)
    got = suite_layout.violations(td)
    check("case 9: repository not shipping suite_layout.py gets no outside-tests finding",
          not any(g.startswith("tracked test-shaped file outside tests/:") for g in got), repr(got))
finally:
    shutil.rmtree(td)

# Case 10: extension-agnostic mirror — *_test.* / *.test.* are refused at any extension.
td = base_git_fixture()
try:
    (td / ".harness/tools").mkdir(parents=True)
    (td / ".harness/tools/session_test.md").write_text("notes\n")
    (td / ".harness/evidence").mkdir(parents=True)
    (td / ".harness/evidence/run.test.jsonl").write_text("{}\n")
    git_commit(td)
    got = suite_layout.violations(td)
    check("case 10: session_test.md flagged with no extension restriction",
          "tracked test-shaped file outside tests/: .harness/tools/session_test.md" in got,
          repr(got))
    check("case 10: run.test.jsonl flagged with no extension restriction",
          "tracked test-shaped file outside tests/: .harness/evidence/run.test.jsonl" in got,
          repr(got))
finally:
    shutil.rmtree(td)


# Case 11: the guard covers actual discovery, derived at test time and never copied.
def _running_kinds(test_kinds_cfg):
    return {name: cfg for name, cfg in test_kinds_cfg.items()
            if cfg.get("status") in ("active", "locally_run")}


def _is_inside_tests(pattern):
    segments = pattern.split("/")
    if ".." in segments:
        return False
    prefix_segments = []
    for segment in segments:
        if any(ch in segment for ch in "*?["):
            break
        prefix_segments.append(segment)
    prefix = "/".join(prefix_segments)
    normalized = posixpath.normpath(prefix) if prefix else ""
    if not normalized or normalized in (".", "..") or posixpath.isabs(normalized):
        return False
    return normalized == "tests" or normalized.startswith("tests/")


def _literal_key_present(core):
    if "_test." in core or ".test." in core:
        return True
    for prefix in ("test-", "test_", "probe-"):
        if not core.startswith(prefix):
            continue
        wildcard_positions = [i for i, ch in enumerate(core) if ch in "*?["]
        last_wildcard = max(wildcard_positions) if wildcard_positions else -1
        trailing = core[last_wildcard + 1:]
        if (trailing.startswith(".")
                and not any(ch in trailing for ch in "*?[")
                and any(trailing.endswith(ext) for ext in suite_layout.SOURCE_EXTENSIONS)):
            return True
    return False


ADVERSARIAL_CORPUS = (
    "gen.py", "foo.py", "notes.md", "README.md", "conftest.py", "helper.ts",
    "data.jsonl", "x.test.y", "x.test.py", "run.test.jsonl", "a_test.md",
    "x_test.py", "test_x.py", "test_x.md", "test-x.py", "probe-x.py",
    "probe-x.md", "x.spec.y", "x.spec.tsx", "x.e2e.spec.ts", "test_dir",
    "evil.py", "test_x.pw", "probe-x.pw", "test-x.pw", "a_test.pw", "x.test.pw",
)


def _corpus_oracle(core):
    for basename in ADVERSARIAL_CORPUS:
        if fnmatch.fnmatch(basename, core) and not suite_layout.is_test_shaped(
                ".harness/tools/" + basename):
            return False, basename
    return True, None


def _certify_pattern(pattern):
    if _is_inside_tests(pattern):
        return "inside-tests", None
    core = pattern[len("**/"):] if pattern.startswith("**/") else pattern
    if "/" in core:
        return None, "core contains a directory separator"
    if not any(ch in core for ch in "*?[") or core.strip("*?[") == "":
        return None, "core carries no wildcard-free literal text"
    if not _literal_key_present(core):
        return None, ("no fixed literal key (_test., .test., or a restricted prefix "
                       "plus a source extension)")
    oracle_ok, offending = _corpus_oracle(core)
    if not oracle_ok:
        return None, f"corpus basename {offending!r} matches but is_test_shaped rejects it"
    return "guard-covered", None


def hygiene_uncertified(test_kinds_cfg):
    uncertified = []
    for kind_name, kind_cfg in sorted(_running_kinds(test_kinds_cfg).items()):
        for pattern in code_grade._patterns(kind_cfg["detect"]):
            category, reason = _certify_pattern(pattern)
            if category is None:
                uncertified.append(f"{kind_name}: {pattern} ({reason})")
    return uncertified


def offenders(paths, test_kinds_cfg):
    exception_paths = {entry[0] for entry in suite_layout.DOCUMENTED_EXCEPTIONS}
    return sorted(
        p for p in paths
        if not p.startswith("tests/")
        and code_grade._is_test_path(p, test_kinds_cfg)
        and (not suite_layout.is_test_shaped(p) or p in exception_paths))


CANDIDATE_CORPUS = (
    ".harness/tools/test_dir/gen.py",
    ".harness/tools/a.test.d/gen.py",
    ".harness/tools/a_test.d/gen.py",
    ".harness/tools/spec_dir/gen.py",
    ".harness/tools/plaindir/gen.py",
)


def select_control_candidate(test_kinds_cfg):
    exception_paths = {entry[0] for entry in suite_layout.DOCUMENTED_EXCEPTIONS}
    for cand in CANDIDATE_CORPUS:
        if (not cand.startswith("tests/")
                and code_grade._is_test_path(cand, test_kinds_cfg)
                and not suite_layout.is_test_shaped(cand)
                and cand not in exception_paths):
            return cand
    return None


test_kinds_cfg = repo_cfg["test_kinds"]

synthetic_tracked = [
    "tests/unit/test-unit.py",
    "tests/integration/test-integration.py",
    "tests/manual/probe-fixture.py",
    ".harness/tools/test_rogue.py",
    ".harness/tools/session_test.md",
    ".harness/evidence/run.test.jsonl",
    ".harness/notes/probe-something.md",
    ".claude/skills/harness/bin/suite_layout.py",
    suite_layout.DOCUMENTED_EXCEPTIONS[0][0],
]
check("case 11 behavioural: synthetic tracked set has no offenders",
      offenders(synthetic_tracked, test_kinds_cfg) == [],
      repr(offenders(synthetic_tracked, test_kinds_cfg)))

try:
    real_tracked = list(suite_layout.tracked_paths(ROOT))
except LookupError as error:
    check("case 11 behavioural: real tracked set has no offenders", False, str(error))
else:
    check("case 11 behavioural: real tracked set has no offenders",
          offenders(real_tracked, test_kinds_cfg) == [],
          repr(offenders(real_tracked, test_kinds_cfg)))

control_candidate = select_control_candidate(test_kinds_cfg)
if control_candidate is not None:
    control_result = offenders(synthetic_tracked + [control_candidate], test_kinds_cfg)
    check("case 11 behavioural: positive control offender is detected",
          control_result == [control_candidate], repr(control_result))
else:
    print("INAPPLICABLE case 11 behavioural: positive control -- no candidate in the corpus "
          "is counted-but-unrefused under the live test_kinds config")

uncertified = hygiene_uncertified(test_kinds_cfg)
check("case 11 hygiene: every running-kind detect pattern is certified",
      uncertified == [], repr(uncertified))
raise SystemExit(1 if failures else 0)
