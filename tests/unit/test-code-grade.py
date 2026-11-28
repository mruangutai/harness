#!/usr/bin/env python3
"""Hand-derived contract tests for code_grade.py."""
from unit_support import ROOT, BIN
import ast
import importlib.util
import itertools
import json
import operator
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from check_support import Checks
from git_support import checked_git, init_repo
C = Checks()
GRADER = ("grader@example.test", "Code Grader")
spec = importlib.util.spec_from_file_location("code_grade", BIN / "code_grade.py")
code_grade = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = code_grade
spec.loader.exec_module(code_grade)
CLI_SPEC = importlib.util.spec_from_file_location("code_grade_cli", BIN / "code-grade.py")
code_grade_cli = importlib.util.module_from_spec(CLI_SPEC)
CLI_SPEC.loader.exec_module(code_grade_cli)



# Each source is adjacent to an independent hand derivation.  A/B/C are the
# ABC components; cyc/cog are cyclomatic and Sonar-style cognitive counts.
FIXTURES = [
    # A=0 B=0 C=0; cyc=1 (base); cog=0; abc=sqrt(0)=0.0.
    ("grade5-empty", '''def empty():\n    pass\n''', ("empty", 1, 1, 0, 0, 0, 0, 0.0, 5, "cyclomatic+cognitive+abc")),
    # A=2 (x, y assignments) B=2 (one, two calls) C=0; cyc=1 (base); cog=0; abc=sqrt(8)=2.8.
    ("bindings-and-calls", '''def bindings():\n    x = one()\n    y = two()\n''', ("bindings", 1, 1, 0, 2, 2, 0, 2.8, 5, "cyclomatic+cognitive+abc")),
    # A=3 (for x, with y, except err) B=0 C=3 (for, except, assert); cyc=4; cog=2 (for, except); abc=sqrt(18)=4.2.
    ("control-basics", '''def controls(xs, cm):\n    for x in xs:\n        pass\n    with cm as y:\n        pass\n    try:\n        pass\n    except ValueError as err:\n        assert err\n''', ("controls", 1, 4, 2, 3, 0, 3, 4.2, 5, "cyclomatic+cognitive+abc")),
    # A=0 B=0 C=4 (four BoolOp operands beyond first); cyc=5; cog=1 (one BoolOp node); abc=4.0.
    ("grade4-cyclomatic", '''def four_conditions(a, b, c, d, e):\n    return a and b and c and d and e\n''', ("four_conditions", 1, 5, 1, 0, 0, 4, 4.0, 4, "cyclomatic")),
    # A=0 B=0 C=8 (eight BoolOp operands beyond first); cyc=9; cog=1; abc=8.0.
    ("grade3-cyclomatic", '''def eight_conditions(a,b,c,d,e,f,g,h,i):\n    return a and b and c and d and e and f and g and h and i\n''', ("eight_conditions", 1, 9, 1, 0, 0, 8, 8.0, 3, "cyclomatic")),
    # A=0 B=0 C=10 (ten BoolOp operands beyond first); cyc=11; cog=1; abc=10.0.
    ("grade2-cyclomatic", '''def ten_conditions(a,b,c,d,e,f,g,h,i,j,k):\n    return a and b and c and d and e and f and g and h and i and j and k\n''', ("ten_conditions", 1, 11, 1, 0, 0, 10, 10.0, 2, "cyclomatic")),
    # A=0 B=0 C=20 (twenty BoolOp operands beyond first); cyc=21; cog=1; abc=20.0.
    ("grade1-cyclomatic", '''def twenty_conditions(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u):\n    return a and b and c and d and e and f and g and h and i and j and k and l and m and n and o and p and q and r and s and t and u\n''', ("twenty_conditions", 1, 21, 1, 0, 0, 20, 20.0, 1, "cyclomatic")),
    # A=0 B=0 C=4 (if, Compare's two operators, unary Not); cyc=2; cog=1; abc=4.0.
    ("compare-and-not", '''def comparison(a, b, c):\n    if not a < b < c:\n        return 1\n''', ("comparison", 1, 2, 1, 0, 0, 4, 4.0, 5, "cyclomatic+cognitive+abc")),
    # A=3 (tuple targets a,b and comprehension target x) B=0 C=1 (comprehension if); cyc=3 (base, for, if); cog=0; abc=sqrt(10)=3.2.
    ("unpacking-comprehension", '''def unpack(xs):
    a, b = 1, 2
    return [x for x in xs if x]
''', ("unpack", 1, 3, 0, 3, 0, 1, 3.2, 5, "cyclomatic+cognitive+abc")),
    # A=0 B=1 (helper call) C=0; cyc=1; cog=0; abc=1.0.
    ("bare-call", '''def called():\n    helper()\n''', ("called", 1, 1, 0, 0, 1, 0, 1.0, 5, "cyclomatic+cognitive+abc")),
    # A=0 B=0 C=2 (both match cases); cyc=2 (non-wildcard case); cog=0; abc=2.0.
    ("match-case", '''def matched(x):\n    match x:\n        case 1:\n            return 1\n        case _:\n            return 0\n''', ("matched", 1, 2, 0, 0, 0, 2, 2.0, 5, "cyclomatic+cognitive+abc")),
    # A=1 (comprehension target) B=1 (bool call) C=11 (eight if clauses and three comparisons); cyc=10; cog=0; abc=sqrt(123)=11.1.
    ("comprehension-filters", '''def filtered(xs):
    return [x for x in xs if x if x > 1 if x < 9 if x != 4 if x % 2 if x + 1 if x - 1 if bool(x)]
''', ("filtered", 1, 10, 0, 1, 1, 11, 11.1, 3, "cyclomatic")),
]



# Direction pairs change exactly one named metric in the stated direction.
DIRECTION_PAIRS = [
    ("nested-early-return", '''def f(a, b, c, d, e):
    if a and b and c:
        return 1
    return 0
''', '''def f(a, b, c, d, e):
    if a and b and c:
        if e:
            return 1
    return 0
''', "cognitive", "worse"),
    ("nested-loops", '''def f(a, b, c, d, e, xs):
    for x in xs:
        if a and b and c:
            pass
    for y in xs:
        if d and e:
            pass
''', '''def f(a, b, c, d, e, xs):
    for x in xs:
        for y in xs:
            if a and b and c:
                pass
            if d and e:
                pass
''', "cognitive", "worse"),
    ("third-condition", '''def f(a, b, c):
    if a and b:
        pass
    assert a
''', '''def f(a, b, c):
    if a and b and c:
        pass
    assert a
''', "cyclomatic", "worse"),
    ("inline-helper", '''def f(a, b, c, d, e):
    return helper(a, b, c, d, e)
''', '''def f(a, b, c, d, e):
    return a and b and c and d and e
''', "abc", "worse"),
    ("early-return-better", '''def f(a, b, c, d, e):
    if a and b and c:
        if e:
            return 1
    return 0
''', '''def f(a, b, c, d, e):
    if a and b and c:
        return 1
    return 0
''', "cognitive", "better"),
    ("condition-better", '''def f(a, b, c):
    if a and b and c:
        pass
    assert a
''', '''def f(a, b, c):
    if a and b:
        pass
    assert a
''', "cyclomatic", "better"),
]


def check_commit_resolution():
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
        _write(repo_root, "sample.py", "def sample():\n    pass\n")
        head_ref = _commit(repo_root, "base")
        blob = subprocess.run(["git", "-C", str(repo_root), "hash-object", "-w", "--stdin"],
                              input="not a commit", text=True, capture_output=True,
                              check=True).stdout.strip()
        failures = 0
        for position in ("base", "head"):
            for existing in (True, False):
                selected = repo_root / f"selected-output-{position}-{existing}"
                if existing:
                    selected.write_text("unchanged")
                option = f"--output={selected}"
                base, head = (option, head_ref) if position == "base" else (head_ref, option)
                failures += _check_rejected_revision(repo_root, base, head, option, position,
                                                     f"option-like {position}")
                failures += check(selected.read_text() if existing else selected.exists(),
                                  "unchanged" if existing else False,
                                  f"library leaves option-selected {position} output untouched")
            base, head = (blob, head_ref) if position == "base" else (head_ref, blob)
            failures += _check_rejected_revision(repo_root, base, head, blob, position,
                                                 f"blob {position}")
        return failures


def _check_rejected_revision(repo_root, base, head, revision, position, label):
    original_run = code_grade.subprocess.run
    calls = []

    def traced_run(args, *args_tail, **kwargs):
        calls.append(args)
        return original_run(args, *args_tail, **kwargs)

    code_grade.subprocess.run = traced_run
    try:
        try:
            code_grade.gated_set(repo_root, base, head)
        except ValueError as error:
            failures = check(str(error), f"invalid Git commit revision: {revision}",
                             f"library names invalid {label} revision")
        else:
            failures = check("accepted", "rejected", f"library rejects {label} revision")
    finally:
        code_grade.subprocess.run = original_run
    arguments = [argument for call in calls for argument in call]
    if label.startswith("option-like"):
        failures += check(any(argument.startswith(revision) for argument in arguments), False,
                          f"library never sends option-like {position} revision to Git")
    else:
        failures += check(f"{revision}^{{commit}}" in arguments, True,
                          f"library resolves blob {position} as commit only")
        failures += check("--end-of-options" in arguments, True,
                          f"library resolves blob {position} after end-of-options")
    failures += check(any(argument in {"diff", "show"} for argument in arguments), False,
                      f"library never diffs or shows after invalid {label} revision")
    return failures


# CR-01: the full set of .py files this feature changed under bin/ (production and test alike —
# `git diff --name-only <base>..<head> -- '*.py'` restricted to this directory), so a below-bar
# function in a test file cannot hide the way test-code-grade.py:main itself once did. Every
# changed file must appear here or be excluded in a one-line comment beside it; none are excluded.
SELF_GRADED_FILES = (
    "check-plan-routes.py",
    "code-grade.py",
    "code_grade.py",
    "gate_policy.py",
    "test-check-plan-routes.py",
    "test-code-grade-cli.py",
    "test-code-grade.py",
    "test-gate-policy.py",
    "test-validate-digest.py",
    "validate-digest.py",
)


# CR-01 exemptions: records in SELF_GRADED_FILES that legitimately sit below their derived bar
# (3 for test files, 4 for production — see check_self_grading). Keyed by (filename, qualname);
# value is the grade the record must still carry. An entry whose qualname no longer exists, or
# whose grade has moved, is itself a failure below (`self-grading allowlist has no stale entries`)
# — an exemption must not outlive the record it excused.
SELF_GRADING_ALLOWLIST = {
    # Grade 2, REASON REQUIRED and recorded at review time (commit 94383e6, before cycle-14
    # renumbered these files) — cite the notes file:
    # notes/review-harness-code-reviewer-validate-final-panel.md, "SC-15" section, items 1-12,14,15.
    # Item 13 (test-code-grade.py:main) is deliberately NOT re-cited here: it was grade 2 at review
    # time and has since regressed to grade 1 (ABC 45.7) — the exact silent regression CR-01 named.
    # It is fixed in code, not exempted.
    ("check-plan-routes.py", "main"): 2,                              # SC-15 item 1
    ("code-grade.py", "main"): 2,                                     # SC-15 item 2
    ("test-check-plan-routes.py", "_case_27_owner_manifest"): 2,      # SC-15 item 5
    ("test-code-grade-cli.py", "test_paths"): 2,                      # SC-15 item 6
    ("test-code-grade-cli.py", "test_rejected_revisions"): 2,         # SC-15 item 7
    ("test-code-grade-cli.py", "test_control_paths"): 2,              # SC-15 item 8
    ("test-code-grade-cli.py", "test_bars_follow_test_kinds"): 2,     # SC-15 item 9
    ("test-code-grade-cli.py", "test_diff_and_determinism"): 2,       # SC-15 item 10
    ("test-code-grade.py", "check_commit_resolution"): 2,             # SC-15 item 11
    ("test-code-grade.py", "check_changed_function_resolution"): 2,   # SC-15 item 12
    ("validate-digest.py", "reviewed_python_change"): 2,              # SC-15 item 15
    # Pre-existing legacy debt, never gated by the FEAT-43 diff (7ccfae8..a643e44): confirmed by
    # running `code-grade.py --base 7ccfae8..a643e44` and checking each qualname is absent from
    # the gated (diff) output below — the function's body is unchanged from before the feature, so
    # the grade could not have moved and no REASON REQUIRED line was ever demanded for it.
    ("check-plan-routes.py", "parse_files"): 2,
    ("check-plan-routes.py", "process_task"): 2,
    ("check-plan-routes.py", "discover_plans"): 1,
    ("test-check-plan-routes.py", "case_18"): 2,
    ("test-check-plan-routes.py", "case_19"): 1,
    ("test-check-plan-routes.py", "case_22"): 2,
    ("test-check-plan-routes.py", "case_23"): 1,
    ("test-check-plan-routes.py", "case_24"): 1,
    ("test-validate-digest.py", "run_cli_cases"): 1,
    ("test-validate-digest.py", "run_hook_cases"): 2,
}


def _check_self_graded_file(filename, repo_root, test_kinds):
    failures = 0
    candidates = [BIN / filename,
                  repo_root / "tests/unit" / filename,
                  repo_root / "tests/integration" / filename]
    path = next((candidate for candidate in candidates if candidate.is_file()), candidates[0])
    failures += check(path.is_file(), True, f"{filename} exists")
    try:
        records = code_grade.grade_source(path.read_text(), filename)
    except SyntaxError:
        records = None
    failures += check(records is not None, True, f"{filename} parses")
    relative = str(path.resolve().relative_to(repo_root))
    bar = 3 if code_grade._is_test_path(relative, test_kinds) else 4
    matched = set()
    for record in records or ():
        key = (filename, record.qualname)
        if key in SELF_GRADING_ALLOWLIST:
            matched.add(key)
            failures += check(record.grade, SELF_GRADING_ALLOWLIST[key],
                              f"{filename}:{record.qualname} allowlisted grade is stale")
            continue
        failures += check(record.grade >= bar, True,
                          f"{filename}:{record.qualname} grade >= {bar}")
    return failures, matched


def _load_test_kinds(repo_root):
    """The configured test_kinds policy every self-grading check classifies against."""
    with (Path(repo_root) / ".harness" / "harness.json").open(encoding="utf-8") as stream:
        return json.load(stream)["test_kinds"]


def check_self_grading():
    """CR-01: every function `code_grade.grade_source` reports across SELF_GRADED_FILES — the full
    set of .py files this feature changed under bin/, production and test alike — must grade at or
    above its derived bar (3 for test files per `code_grade._is_test_path`, 4 for production),
    except the qualnames named in SELF_GRADING_ALLOWLIST — each justified there — and each
    allowlist entry must still match a real below-bar record at the recorded grade, so a fix or a
    rename cannot let an exemption silently outlive it. Each named file is also asserted to exist
    and parse, so a rename or removal fails loudly instead of silently shrinking coverage.
    """
    repo_root = ROOT
    test_kinds = _load_test_kinds(repo_root)
    failures = 0
    matched_allowlist = set()
    for filename in SELF_GRADED_FILES:
        file_failures, matched = _check_self_graded_file(filename, repo_root, test_kinds)
        failures += file_failures
        matched_allowlist |= matched
    failures += check(matched_allowlist, set(SELF_GRADING_ALLOWLIST),
                      "self-grading allowlist has no stale (renamed/removed) entries")
    return failures


# FEAT-2337 SC-08: every new or changed Python test function in the feature grades >= 3, graded
# from git between a FIXED feature base and the COMMITTED tip, with no allowlist at all. It runs
# only under `--feat2337` (and at the review pin): a fixed base in the default suite would grade
# a diff that grows with every later commit. The base is d04c765a, the recorded build-entry
# baseline (plan base dd04e52a plus one upstream merge, BUG-2328/#2338, whose only Python test
# change is another feature's) — the 2026-11-22 grading-base ruling in the feature's notes.
FEAT2337_BASE = "d04c765aba6ba5044492a622625894085b99a2bc"

# The self-grading additions must themselves be in the graded set: their absence means the tip
# does not yet contain the tests being graded, which is not a pass.
FEAT2337_SELF_GRADERS = (
    ("tests/unit/test-code-grade.py", "check_feat2337_self_grading"),
    ("tests/unit/test-code-grade.py", "check_feat2337_grade_two_mutant"),
    ("tests/integration/test-check-domain-grant.py", "run_feat2337_receipt_grant_cases"),
)


def _base_bodies(repo_root, base, tip):
    """{path: {(qualname, body hash)}} at `base` for every Python file changed up to `tip`,
    renames followed, so a record is unchanged only when its name AND body both pre-exist."""
    base_oid = code_grade.commit_oid(repo_root, base)
    tip_oid = code_grade.commit_oid(repo_root, tip)
    bodies = {}
    for path, old_path in code_grade._changed_python_files(repo_root, base_oid, tip_oid):
        source = code_grade._resolve_base_source(repo_root, base_oid, path, old_path)
        bodies[path] = set(code_grade._body_hashes(source).items()) if source else set()
    return bodies


def _is_changed(repo_root, tip, record, before, after):
    if record.path not in after:
        after[record.path] = code_grade._body_hashes(
            code_grade._git_show(repo_root, tip, record.path))
    return (record.qualname, after[record.path][record.qualname]) not in before[record.path]


def _changed_test_records(repo_root, base, tip, test_kinds):
    """code_grade.classify() records of every new or changed function on a test path between
    `base` and `tip`: gated_set's gated records plus its informational records whose body or
    name changed. Untouched legacy functions in a changed file are not this check's subject."""
    gated, informational = code_grade.gated_set(repo_root, base, tip)
    before, after = _base_bodies(repo_root, base, tip), {}
    changed = [record for record in gated + informational
               if _is_changed(repo_root, tip, record, before, after)]
    records, _result = code_grade.classify(changed, test_kinds)
    return [record for record in records if record["bar"] == 3]


def _print_graded(records, label):
    for record in records:
        verdict = "ok   " if record["result"] == "PASS" else "FAIL "
        print(f"{verdict} {label}: {record['path']}:{record['qualname']} grade "
              f"{record['grade']} (bar 3)")
    return sum(record["result"] != "PASS" for record in records)


def check_feat2337_self_grading():
    """SC-08 at the committed tip: every changed test function grades >= 3, the self-grading
    additions included. TypeScript tests are not Python-graded; Bun runs them."""
    repo_root = ROOT
    records = _changed_test_records(repo_root, FEAT2337_BASE, "HEAD",
                                    _load_test_kinds(repo_root))
    failures = _print_graded(records, "feat2337")
    graded = {(record["path"], record["qualname"]) for record in records}
    for key in FEAT2337_SELF_GRADERS:
        failures += check(key in graded, True, f"the committed tip grades {key[0]}:{key[1]}")
    print(f"feat2337: {len(records)} changed Python test functions graded from "
          f"{FEAT2337_BASE[:8]} to HEAD; tests/unit/omp-hooks.test.ts is TypeScript, covered "
          f"by Bun through tests/unit/test-omp-hooks.py, never by this grader")
    return failures


def _grade_two_source(name):
    """A function with twelve branches: cyclomatic 13, which is grade 2 and nothing lower."""
    body = "".join(f"    if value == {n}:\n        return {n}\n" for n in range(12))
    return f"def {name}(value):\n{body}    return -1\n"


_LEGACY_TEST = _grade_two_source("check_legacy") + "\n\ndef check_kept():\n    return 1\n"

# (path, source at base or None, source at tip): the mutant is a NEW grade-2 test function;
# an unchanged grade-2 legacy function and a new grade-2 production function sit beside it.
FEAT2337_MUTANT_FILES = (
    ("tests/unit/test-sample.py",
     _LEGACY_TEST + "\n\ndef check_edited():\n    return 1\n",
     _LEGACY_TEST + "\n\ndef check_edited():\n    return 2\n\n\n"
     + _grade_two_source("check_mutant")),
    ("bin/prod.py", None, _grade_two_source("prod_mutant")),
)

# Exactly these test functions are graded, with these results.
FEAT2337_MUTANT_EXPECTED = {"check_mutant": "FAIL", "check_edited": "PASS"}


def _mutant_repository(directory):
    repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
    for path, before, _after in FEAT2337_MUTANT_FILES:
        if before is not None:
            _write(repo_root, path, before)
    base_ref = _commit(repo_root, "base")
    for path, _before, after in FEAT2337_MUTANT_FILES:
        _write(repo_root, path, after)
    return repo_root, base_ref, _commit(repo_root, "tip")


def check_feat2337_grade_two_mutant():
    """The control: the same cumulative grader rejects a new grade-2 test function, and only it."""
    failures = check(code_grade.grade_source(_grade_two_source("m"), "m.py")[0].grade, 2,
                     "the mutant fixture grades exactly 2")
    with tempfile.TemporaryDirectory() as directory:
        repo_root, base_ref, tip_ref = _mutant_repository(directory)
        records = _changed_test_records(repo_root, base_ref, tip_ref, _load_test_kinds(ROOT))
    outcome = {record["qualname"]: record["result"] for record in records}
    failures += check(outcome, FEAT2337_MUTANT_EXPECTED,
                      "the cumulative grader rejects the grade-2 mutant and grades nothing else")
    if outcome.get("check_mutant") == "FAIL":
        print("ok    feat2337 control: the new grade-2 test function check_mutant is rejected")
    return failures


def feat2337_main():
    return check_feat2337_grade_two_mutant() + check_feat2337_self_grading()


def _cli(argv):
    """Default: the standing suite. `--feat2337`: SC-08's feature-pinned grading only."""
    if argv == ["--feat2337"]:
        return feat2337_main()
    if argv:
        print("usage: test-code-grade.py [--feat2337]", file=sys.stderr)
        sys.exit(2)
    return main()


def check_case_27_grade():
    source = (ROOT / "tests/integration/test-check-plan-routes.py").read_text()
    node = next(item for item in ast.parse(source).body if isinstance(item, ast.FunctionDef)
                and item.name == "case_27")
    case_source = ast.get_source_segment(source, node)
    record = code_grade.grade_source(case_source, "test-check-plan-routes.py")[0]
    return check(record.grade >= 2, True, "case_27 is not grade one")


def _git(repo_root, *args):
    return checked_git(args, repo_root)


def _write(repo_root, name, source):
    path = repo_root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source)


def _commit(repo_root, message):
    _git(repo_root, "add", ".")
    _git(repo_root, "commit", "-m", message)
    return _git(repo_root, "rev-parse", "HEAD").stdout.strip()


def check_changed_function_resolution():
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
        _write(repo_root, "main.py", '''\
def worsened():
    pass

def improved(a, b, c, d, e):
    return a and b and c and d and e

def renamed():
    return 1

def reformatted():
    return 1

def signature_changed(value):
    return value

def already_bad(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u):
    return a and b and c and d and e and f and g and h and i and j and k and l and m and n and o and p and q and r and s and t and u
''')
        _write(repo_root, "moved.py", "def moved():\n    return 1\n")
        base_ref = _commit(repo_root, "base")
        _write(repo_root, "main.py", '''\
def worsened(a, b, c, d, e):
    return a and b and c and d and e

def improved():
    pass

def renamed_new():
    return 1

def reformatted():

    return 1

def signature_changed(value, optional=None):
    return value

def already_bad(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u):
    return a and b and c and d and e and f and g and h and i and j and k and l and m and n and o and p and q and r and s and t and u

def newly_added():
    return 2
''')
        _git(repo_root, "mv", "moved.py", "relocated.py")
        head_ref = _commit(repo_root, "changes")
        gated, informational = code_grade.gated_set(repo_root, base_ref, head_ref)
        gated_names = {record.qualname for record in gated}
        informational_names = {record.qualname for record in informational}
        failures = check(gated_names, {"newly_added", "worsened"}, "gated set")
        gated_paths = {record.path for record in gated}
        informational_paths = {record.path for record in informational}
        failures += check(gated_paths, {"main.py"}, "gated source paths")
        failures += check(informational_paths, {"main.py", "relocated.py"},
                          "informational source paths")
        failures += check("improved" in gated_names, False, "improved absent from gated")
        failures += check("renamed_new" in gated_names, False, "renamed absent from gated")
        failures += check("reformatted" in gated_names, False, "reformatted absent from gated")
        failures += check("signature_changed" in gated_names, False, "signature change absent from gated")
        failures += check("moved" in gated_names, False, "moved file absent from gated")
        failures += check("already_bad" in gated_names, False, "untouched grade one absent from gated")
        failures += check("already_bad" in informational_names, True, "untouched grade one informational")
        return failures


def _grade_stub(qualname, grade, path="main.py"):
    return code_grade.FunctionGrade(
        qualname=qualname, lineno=1, cyclomatic=1, cognitive=1,
        abc_a=0, abc_b=0, abc_c=0, abc=0.0, grade=grade, driver="cyclomatic",
        path=path,
    )


# CR-XX: direct bar and precedence assertions for the code_grade.classify() seam. These live
# here (unit) rather than only in test-code-grade-cli.py (integration) per SC-06 / PF-7ab845aa.
_CLASSIFY_TEST_KINDS = {"unit": {"detect": "test_*.py|tests/*.py", "exclude": "", "status": "active"}}


def check_classify_bars():
    records, result = code_grade.classify(
        [_grade_stub("prod_fn", 4, path="src/prod.py")], _CLASSIFY_TEST_KINDS)
    failures = check(records[0]["bar"], 4, "production path bars at 4")
    failures += check(result, "pass", "clean production record classifies pass")
    records, result = code_grade.classify(
        [_grade_stub("test_fn", 3, path="test_sample.py")], _CLASSIFY_TEST_KINDS)
    failures += check(records[0]["bar"], 3, "test path bars at 3")
    failures += check(result, "pass", "clean test record classifies pass")
    return failures


def check_classify_locally_run_bars_as_test():
    """Issue #1187: a `locally_run` kind (a probe script that cannot run in CI) must still
    bar its own path at 3, the test bar, not 4 — it is test code, not production code,
    just because CI cannot run it. And a kind that is genuinely neither active nor
    locally_run (e.g. unresolved) must NOT relax the bar."""
    locally_run_kinds = {
        "unit": {"detect": "test_*.py|tests/*.py", "exclude": "", "status": "active"},
        "probe": {"detect": "probe_*.py", "exclude": "", "status": "locally_run"},
        "component": {"detect": "spec_*.py", "exclude": "", "status": "unresolved"},
    }
    records, result = code_grade.classify(
        [_grade_stub("probe_fn", 3, path="probe_thing.py")], locally_run_kinds)
    failures = check(records[0]["bar"], 3, "a locally_run path bars at 3, the test bar")
    failures += check(result, "pass", "clean locally_run record classifies pass")

    records, result = code_grade.classify(
        [_grade_stub("spec_fn", 4, path="spec_thing.py")], locally_run_kinds)
    failures += check(records[0]["bar"], 4,
                       "an unresolved-status kind does NOT relax the bar to 3")
    return failures


def check_is_test_path_honors_classifies_tests():
    """FEAT-2257: a running kind may detect PRODUCTION source for a static check (typecheck
    over every .ts). `classifies_tests: false` keeps such a kind from marking its matches as
    test code; absent or true keeps today's classification, and exclude/status still apply."""
    def kinds(status="active", **flag):
        return {"static": {"detect": "**/*.ts", "exclude": "vendor/**", "status": status, **flag}}
    failures = check(code_grade._is_test_path(".omp/extensions/hooks.ts", kinds(classifies_tests=False)),
                     False, "an active kind flagged classifies_tests false classifies nothing as test")
    failures += check(code_grade._is_test_path(".omp/extensions/hooks.ts",
                                               kinds("locally_run", classifies_tests=False)),
                      False, "a locally_run kind flagged false classifies nothing as test")
    failures += check(code_grade._is_test_path(".omp/extensions/hooks.ts", kinds()),
                      True, "an absent flag keeps a matching running kind's test classification")
    failures += check(code_grade._is_test_path(".omp/extensions/hooks.ts", kinds(classifies_tests=True)),
                      True, "an explicit true keeps a matching running kind's test classification")
    failures += check(code_grade._is_test_path("vendor/lib.ts", kinds(classifies_tests=True)),
                      False, "exclude still removes a match from a classifying kind")
    failures += check(code_grade._is_test_path(".omp/extensions/hooks.ts", kinds("unresolved")),
                      False, "a non-running kind still classifies nothing")
    return failures


def check_classify_grade_two_is_reasoned():
    records, result = code_grade.classify(
        [_grade_stub("boundary", 2, path="src/prod.py")], _CLASSIFY_TEST_KINDS)
    failures = check(records[0]["severity"], "med", "grade two is reasoned, not blocking")
    failures += check(result, "grade_2", "grade two alone classifies grade_2, not fail")
    return failures


def check_classify_precedence():
    mixed = [_grade_stub("blocked", 1, path="src/prod.py"),
             _grade_stub("reasoned", 2, path="src/prod.py")]
    records, result = code_grade.classify(mixed, _CLASSIFY_TEST_KINDS)
    failures = check(result, "fail", "a blocking record beats a simultaneous grade-two record")
    records, result = code_grade.classify([], _CLASSIFY_TEST_KINDS)
    failures += check(result, "pass", "an empty record set classifies pass")
    return failures


def check_pre_image_resolution_priority():
    """Characterizes the priority _resolve_pre_image enforces: a qualname match wins
    over a body-hash match, a body-hash match wins when no name matches, and a missing
    pre-image resolves to None. Swapping the lookup order breaks one of these by name."""
    by_name_match = _grade_stub("foo", 5)
    by_hash_match = _grade_stub("foo", 1)
    head = _grade_stub("foo", 3)
    before_hashes = {"headhash": [by_hash_match]}
    head_hashes = {"foo": "headhash"}

    resolved = code_grade._resolve_pre_image(head, {"foo": by_name_match}, before_hashes, head_hashes)
    failures = check(resolved is by_name_match, True, "qualname match wins over hash match")

    resolved = code_grade._resolve_pre_image(head, {}, before_hashes, head_hashes)
    failures += check(resolved is by_hash_match, True, "hash match wins when name absent")

    resolved = code_grade._resolve_pre_image(head, {}, {}, head_hashes)
    failures += check(resolved, None, "missing pre-image resolves to None")
    return failures


def check_base_source_rename_fallback():
    """A rename-only file resolves its pre-image through old_path, and a file with no
    old_path never falls back to one."""
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
        _write(repo_root, "old.py", "def kept():\n    return 1\n")
        base_ref = _commit(repo_root, "base")
        _git(repo_root, "mv", "old.py", "new.py")
        _commit(repo_root, "rename")
        base_oid = code_grade.commit_oid(repo_root, base_ref)
        resolved = code_grade._resolve_base_source(repo_root, base_oid, "new.py", "old.py")
        failures = check(resolved, "def kept():\n    return 1\n",
                         "rename resolves pre-image via old_path")
        resolved = code_grade._resolve_base_source(repo_root, base_oid, "new.py", None)
        failures += check(resolved, None, "no old_path fallback without a rename")
        return failures


def check_base_source_absent_from_worktree():
    """A path new in the graded range resolves to None even when it is absent from the
    working tree; a path git would otherwise read as pathspec magic is still found, so
    dropping `--literal-pathspecs` cannot make a present path read as absent; and a
    genuine git failure still raises rather than reading as absence."""
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
        _write(repo_root, "old.py", "def kept():\n    return 1\n")
        base_ref = _commit(repo_root, "base")
        _write(repo_root, "added.py", "def added():\n    return 2\n")
        _commit(repo_root, "add a path absent from base")
        _git(repo_root, "rm", "--quiet", "added.py")
        _commit(repo_root, "worktree moves past the graded range")
        base_oid = code_grade.commit_oid(repo_root, base_ref)
        failures = check(code_grade._git_show(repo_root, base_oid, "added.py"), None,
                         "absent at ref and absent on disk resolves to None")
        failures += check(
            code_grade._resolve_base_source(repo_root, base_oid, "added.py", None), None,
            "base source of a path new in the range is None")
        _write(repo_root, ":colon.py", "def colon():\n    return 3\n")
        head_oid = code_grade.commit_oid(repo_root, _commit(repo_root, "pathspec-magic name"))
        failures += check(code_grade._tree_has_path(repo_root, head_oid, ":colon.py"), True,
                          "a present path git would read as pathspec magic is not absent")
        try:
            code_grade._git_show(repo_root, "not-a-real-ref", "old.py")
        except RuntimeError:
            raised = True
        else:
            raised = False
        failures += check(raised, True, "a genuine git failure still raises")
        return failures


def check_nul_safe_changed_files():
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
        old_path = "odd\told\nname.py"
        new_path = "odd\tnew\nname.py"
        _write(repo_root, old_path, "def retained():\n    return 1\n")
        base_ref = _commit(repo_root, "base")
        _git(repo_root, "mv", old_path, new_path)
        head_ref = _commit(repo_root, "rename")
        failures = check(
            code_grade._changed_python_files(repo_root, base_ref, head_ref),
            [(new_path, old_path)],
            "NUL-safe rename preserves tab and newline Python paths",
        )
        gated, informational = code_grade.gated_set(repo_root, base_ref, head_ref)
        failures += check(
            [(record.path, record.qualname) for record in gated + informational],
            [(new_path, "retained")],
            "NUL-safe rename reaches the grading record",
        )
        return failures


def check_docstring_only_rename_not_gated():
    """_strip_docstring must be reached for this fixture: the qualname lookup misses
    (the function is renamed), so resolution falls through to the body hash. A
    docstring-only edit under a rename must still resolve by body hash and land
    informational, never gated."""
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
        _write(repo_root, "main.py", '''\
def documented():
    """Original text."""
    return 1
''')
        base_ref = _commit(repo_root, "base")
        _write(repo_root, "main.py", '''\
def renamed():
    """Rewritten text."""
    return 1
''')
        head_ref = _commit(repo_root, "changes")
        gated, informational = code_grade.gated_set(repo_root, base_ref, head_ref)
        gated_names = {record.qualname for record in gated}
        informational_names = {record.qualname for record in informational}
        failures = check(gated_names, set(), "docstring-only rename gated set")
        failures += check(informational_names, {"renamed"},
                          "docstring-only rename informational set")
        return failures


def check_method_qualname_collision_pre_images():
    """_qualname must join the class prefix: without it, two same-named methods on
    different classes collide in the body-hash map and a same-named top-level
    function that only changed which name it holds must still resolve by hash."""
    def source(top_name):
        return f'''\
def {top_name}():
    return "top"

class Alpha:
    def run(self):
        return "alpha"

class Beta:
    def run(self):
        return "beta"
'''
    with tempfile.TemporaryDirectory() as directory:
        repo_root = Path(init_repo(directory, None, GRADER, git=checked_git))
        _write(repo_root, "main.py", source("run"))
        base_ref = _commit(repo_root, "base")
        _write(repo_root, "main.py", source("dispatch"))
        head_ref = _commit(repo_root, "changes")
        gated, informational = code_grade.gated_set(repo_root, base_ref, head_ref)
        gated_names = {record.qualname for record in gated}
        informational_names = {record.qualname for record in informational}
        failures = check(gated_names, set(), "qualname collision gated set")
        failures += check(informational_names, {"Alpha.run", "Beta.run", "dispatch"},
                          "qualname collision informational set")
        return failures


def check_worked_examples():
    skill_path = ROOT / ".claude/skills/harness/references/code-risk-examples.md"
    worked_examples = skill_path.read_text().split("## Worked examples\n", 1)[1]
    examples = re.findall(
        r"```python\n(.*?)```\nEXPECTED GRADE: ([1-5])",
        worked_examples,
        re.DOTALL,
    )
    failures = 0
    grades = set()
    for index, (source, expected_text) in enumerate(examples, start=1):
        expected_grade = int(expected_text)
        name = re.search(r"^def (\w+)", source, re.MULTILINE).group(1)
        actual = [record.grade for record in code_grade.grade_source(source, f"{name}.py")]
        failures += check(actual, [expected_grade], f"worked example {index}: {name}")
        grades.add(expected_grade)
    failures += check(len(examples) >= 5, True, "worked examples parsed")
    failures += check({5, 4, 3, 1}.issubset(grades), True, "worked example grades")
    return failures


def check_delivery():
    tree = ".omp/agents"
    failures = 0
    for agent in ("harness-frontend-dev", "harness-backend-dev", "harness-ai-dev",
                  "harness-data-engineer", "harness-dev-ops"):
        frontmatter = re.match(r"---\n(.*?)\n---\n", (ROOT / tree / f"{agent}.md").read_text(),
                               re.DOTALL).group(1).splitlines()
        skills_start = next(index for index, line in enumerate(frontmatter)
                            if line in ("skills:", "autoloadSkills:"))
        skills = [line[2:] for line in itertools.takewhile(lambda line: line.startswith("- "),
                                                           frontmatter[skills_start + 1:])]
        failures += check("harness-code-risk-grading" in skills, True, f"delivery {tree}: {agent}")
    return failures


def check(actual, expected, label):
    """One labelled equality check recorded in C; returns 1 on failure so callers can sum."""
    return 0 if C.check(label, actual == expected, f"expected {expected!r}, got {actual!r}") else 1


def check_fixtures():
    failures = 0
    grades = set()
    for name, source, expected in FIXTURES:
        if name == "match-case" and sys.version_info < (3, 10):
            continue
        records = code_grade.grade_source(source, "fixture.py")
        actual = [(r.qualname, r.lineno, r.cyclomatic, r.cognitive, r.abc_a, r.abc_b, r.abc_c, r.abc, r.grade, r.driver) for r in records]
        failures += check(actual, [expected], name)
        grades.add(records[0].grade)
    failures += check(len(FIXTURES) >= 12, True, "minimum hand-derived fixtures")
    failures += check(grades, {1, 2, 3, 4, 5}, "fixture bands")
    return failures


def check_nested_qualnames():
    nested = code_grade.grade_source('''def outer():
    def helper():
        pass
    helper()
''', "fixture.py")
    return check([record.qualname for record in nested], ["outer", "outer.helper"],
                 "nested source order and qualname")


def check_direction_pairs():
    failures = 0
    for name, before, after, metric, direction in DIRECTION_PAIRS:
        before_record = code_grade.grade_source(before, "fixture.py")[0]
        after_record = code_grade.grade_source(after, "fixture.py")[0]
        before_value, after_value = getattr(before_record, metric), getattr(after_record, metric)
        moved_as_named = after_value < before_value if direction == "better" else after_value > before_value
        failures += check(moved_as_named, True, f"{name}: {metric} moves {direction}")
        before_grade, after_grade = before_record.grade, after_record.grade
        moved_grade = after_grade > before_grade if direction == "better" else after_grade < before_grade
        failures += check(moved_grade, True, f"{name}: grade moves {direction}")
    return failures


# The five raw metrics, as one tuple, of a FunctionGrade record.
_metrics = operator.attrgetter("cyclomatic", "cognitive", "abc_a", "abc_b", "abc_c")


def check_optional_field_guards():
    """C28: _Counter.visit_With/visit_Try/visit_AnnAssign each visit an ASDL-optional AST
    field (withitem.optional_vars, ExceptHandler.type, AnnAssign.value) without a None guard,
    raising AttributeError instead of grading. Asserts literal metrics, not just absence of a
    crash, and asserts the two genuine identities QA's corrected spec names — bare except: vs
    except Exception:, and bare `x: int` vs `x: int = None` — while explicitly NOT asserting
    bare `with lock:` identical to `with lock as x:` (abc_a differs by 1: the `as` target is a
    Store-context Name, which visit_Name counts and the bare form has none)."""
    failures = 0
    with_record = code_grade.grade_source("def f():\n    with lock:\n        pass\n", "fixture.py")[0]
    failures += check(_metrics(with_record), (1, 0, 0, 0, 0), "bare with: literal metrics")

    try_record = code_grade.grade_source(
        "def f():\n    try:\n        pass\n    except:\n        pass\n", "fixture.py")[0]
    try_exc_record = code_grade.grade_source(
        "def f():\n    try:\n        pass\n    except Exception:\n        pass\n", "fixture.py")[0]
    failures += check(_metrics(try_record), (2, 1, 0, 0, 1), "bare except: literal metrics")
    failures += check(_metrics(try_record), _metrics(try_exc_record),
                      "bare except: metric-identical to except Exception:")

    ann_record = code_grade.grade_source("def f():\n    x: int\n", "fixture.py")[0]
    ann_none_record = code_grade.grade_source("def f():\n    x: int = None\n", "fixture.py")[0]
    failures += check(_metrics(ann_record), (1, 0, 1, 0, 0), "bare annotation: literal metrics")
    failures += check(_metrics(ann_record), _metrics(ann_none_record),
                      "bare annotation: metric-identical to explicit = None")
    return failures


def main():
    checks = (
        check_fixtures,
        check_nested_qualnames,
        check_nul_safe_changed_files,
        check_docstring_only_rename_not_gated,
        check_method_qualname_collision_pre_images,
        check_direction_pairs,
        check_changed_function_resolution,
        check_pre_image_resolution_priority,
        check_base_source_rename_fallback,
        check_base_source_absent_from_worktree,
        check_commit_resolution,
        check_case_27_grade,
        check_worked_examples,
        check_delivery,
        check_self_grading,
        check_optional_field_guards,
        check_classify_bars,
        check_classify_locally_run_bars_as_test,
        check_is_test_path_honors_classifies_tests,
        check_classify_grade_two_is_reasoned,
        check_classify_precedence,
    )
    return sum(fn() for fn in checks)


if __name__ == "__main__":
    # _print_graded's per-record verdicts (--feat2337) count outside C, so both feed the exit.
    failures = _cli(sys.argv[1:])
    sys.exit(C.report() or (1 if failures else 0))
