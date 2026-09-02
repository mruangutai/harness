#!/usr/bin/env python3
"""Subprocess contract tests for code-grade.py."""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import os
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / ".claude/skills/harness/bin/code-grade.py"
MODULE_SPEC = importlib.util.spec_from_file_location("code_grade_cli", SCRIPT)
code_grade_cli = importlib.util.module_from_spec(MODULE_SPEC)
MODULE_SPEC.loader.exec_module(code_grade_cli)



def run(repo, *args, cwd=None, env=None):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], text=True,
                          capture_output=True, cwd=cwd or repo, env=env)


def write(repo, path, text):
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True,
                          capture_output=True)


def commit(repo, message):
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD").stdout.strip()


def make_repo(root):
    git(root, "init")
    git(root, "config", "user.email", "grader@example.test")
    git(root, "config", "user.name", "Code Grader")
    write(root, ".harness/harness.json", json.dumps({"test_kinds": {"unit": {
        "detect": "tests/unit/**", "exclude": ".claude/worktrees/**",
        "status": "active"}}}))


def expect(actual, expected, label):
    if actual != expected:
        print(f"FAIL {label}: expected {expected!r}, got {actual!r}")
        return 1
    return 0


def decode_path(value):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return "<not JSON path>"


def test_paths(repo):
    write(repo, "src/risk.py", """def grade_two(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k

def grade_one(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u):
    return a and b and c and d and e and f and g and h and i and j and k and l and m and n and o and p and q and r and s and t and u
""")
    write(repo, "tests/unit/test-sample.py", """def test_grade_three(a,b,c,d,e,f,g,h,i):
    return a and b and c and d and e and f and g and h and i
""")
    result = run(repo, "src/risk.py", "tests/unit/test-sample.py")
    failures = 0
    failures += expect(result.returncode, 1, "path bar exit")
    for field in ('PATH: "src/risk.py"', "LINE: 1", "QUALNAME: grade_two",
                  "CYCLOMATIC: 11", "COGNITIVE: 1 (Sonar-style approximation)", "ABC: 10.0",
                  "GRADE: 2", "DRIVER: cyclomatic", "BAR: 4", "RESULT: FAIL",
                  "SEVERITY: med", "REASON REQUIRED: grade_two", "SEVERITY: high",
                  "BAR: 3", "RESULT: PASS", "PASSING: 1"):
        failures += expect(field in result.stdout, True, f"text field {field}")
    data = run(repo, "--json", "src/risk.py", "tests/unit/test-sample.py")
    failures += expect(data.returncode, 1, "json bar exit")
    report = json.loads(data.stdout)
    record = next(row for row in report["records"] if row["qualname"] == "grade_two")
    for key, value in {"path": "src/risk.py", "line": 1, "qualname": "grade_two",
                       "cyclomatic": 11, "cognitive": 1,
                       "cognitive_method": "Sonar-style approximation", "abc": 10.0, "grade": 2,
                       "driver": "cyclomatic", "bar": 4, "severity": "med",
                       "result": "FAIL"}.items():
        failures += expect(record[key], value, f"json {key}")
    clean = run(repo, "tests/unit/test-sample.py")
    failures += expect(clean.returncode, 0, "test grade three passes")
    failures += expect("REASON REQUIRED" in clean.stdout, False, "reason omitted without grade two")
    authorized = run(repo, "src/risk.py")
    failures += expect(authorized.returncode, 1, "grade one still blocks")
    write(repo, "src/grade-two.py", """def grade_two(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k
""")
    authorized = run(repo, "src/grade-two.py")
    failures += expect(authorized.returncode, 0, "grade two authorization is nonblocking")
    failures += expect("RESULT: FAIL" in authorized.stdout, True,
                       "grade two surface result remains fail")
    return failures


def test_parse_and_usage(repo):
    write(repo, "src/bad.py", "def broken(:\n")
    result = run(repo, "src/bad.py")
    failures = expect(result.returncode, 3, "parse error exit")
    failures += expect('PARSE ERROR: "src/bad.py"' in result.stderr, True, "parse stderr")
    failures += expect('UNGRADED:\n  "src/bad.py"' in result.stdout, True, "ungraded report")
    failures += expect("PASSING: 0" in result.stdout, True, "ungraded excluded from passing")
    usage = run(repo, "--base", "HEAD")
    return failures + expect(usage.returncode, 2, "usage exit")

def test_rejected_revisions(repo):
    wrapper = repo / "git-wrapper"
    wrapper.mkdir()
    git_wrapper = wrapper / "git"
    log = repo / "git-arguments"
    git_wrapper.write_text("#!/bin/sh\nprintf '%s\\n' \"$@\" >> \"$GIT_LOG\"\nexec /usr/bin/git \"$@\"\n")
    git_wrapper.chmod(0o755)
    env = {**os.environ, "PATH": f"{wrapper}:{os.environ['PATH']}", "GIT_LOG": str(log)}
    blob = subprocess.run(["git", "-C", str(repo), "hash-object", "-w", "--stdin"],
                          input="not a commit", text=True, capture_output=True, check=True).stdout.strip()
    failures = 0
    for position in ("base", "head"):
        for existing in (True, False):
            selected = repo / f"selected-output-{position}-{existing}"
            if existing:
                selected.write_text("unchanged")
            option = f"--output={selected}"
            log.unlink(missing_ok=True)
            revisions = {"base": "HEAD", "head": "HEAD"}
            revisions[position] = option
            result = run(repo, f"--base={revisions['base']}", f"--head={revisions['head']}", env=env)
            failures += expect(result.returncode, 2, f"CLI rejects option-like {position} revision")
            failures += expect(f"invalid Git commit revision: {option}" in result.stderr, True,
                               f"CLI names invalid option-like {position} revision")
            failures += expect(selected.read_text() if existing else selected.exists(),
                               "unchanged" if existing else False,
                               f"CLI leaves option-selected {position} output untouched")
            arguments = log.read_text().splitlines() if log.exists() else []
            failures += expect(any(argument.startswith(option) for argument in arguments), False,
                               f"CLI never sends option-like {position} revision to Git")
            failures += expect(any(argument in {"diff", "show"} for argument in arguments), False,
                               f"CLI never diffs or shows after option-like {position} revision")
        log.unlink(missing_ok=True)
        revisions = {"base": "HEAD", "head": "HEAD"}
        revisions[position] = blob
        result = run(repo, f"--base={revisions['base']}", f"--head={revisions['head']}", env=env)
        arguments = log.read_text().splitlines()
        failures += expect(result.returncode, 2, f"CLI rejects blob {position} revision")
        failures += expect(f"invalid Git commit revision: {blob}" in result.stderr, True,
                           f"CLI names invalid blob {position} revision")
        failures += expect("--end-of-options" in arguments, True,
                           f"CLI resolves blob {position} after end-of-options")
        failures += expect(any(argument in {"diff", "show"} for argument in arguments), False,
                           f"CLI never diffs or shows after blob {position} revision")
    return failures


def test_control_paths(repo):
    odd_path = "src/odd\n\r\t\x1b.py"
    write(repo, odd_path, "def safe():\n    pass\n")
    result = run(repo, odd_path)
    rendered = next(line.removeprefix("PATH: ") for line in result.stdout.splitlines()
                    if line.startswith("PATH: "))
    failures = expect(decode_path(rendered), odd_path, "normal text path round trips")
    failures += expect(any(byte in rendered for byte in "\n\r\t\x1b"), False,
                       "normal path text is single line")
    write(repo, odd_path, "def broken(:\n")
    result = run(repo, odd_path)
    parse_path = result.stderr.split("PARSE ERROR: ", 1)[1].split(": ", 1)[0]
    failures += expect(decode_path(parse_path), odd_path, "parse error path round trips")
    failures += expect(any(byte in parse_path for byte in "\n\r\t\x1b"), False,
                       "parse error path text is single line")
    ungraded = result.stdout.split("UNGRADED:\n  ", 1)[1].splitlines()[0]
    failures += expect(decode_path(ungraded), odd_path, "ungraded path round trips")
    failures += expect(any(byte in ungraded for byte in "\n\r\t\x1b"), False,
                       "ungraded path text is single line")
    return failures


def test_bars_follow_test_kinds(repo):
    write(repo, ".harness/harness.json", json.dumps({"test_kinds": {"configured": {
        "detect": "checks/**", "exclude": "", "status": "active"}}}))
    sources = {
        "src/grade-four.py": """def boundary(a,b,c,d,e):
    return a and b and c and d and e
""",
        "src/grade-three.py": """def boundary(a,b,c,d,e,f,g,h,i):
    return a and b and c and d and e and f and g and h and i
""",
        "checks/grade-three.py": """def boundary(a,b,c,d,e,f,g,h,i):
    return a and b and c and d and e and f and g and h and i
""",
        "checks/grade-two.py": """def boundary(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k
""",
    }
    for path, source in sources.items():
        write(repo, path, source)
    failures = 0
    for path, exit_code, result, grade, bar, below_bar, severity in (
        ("src/grade-four.py", 0, "PASS", 4, 4, False, None),
        ("src/grade-three.py", 1, "FAIL", 3, 4, True, "high"),
        ("checks/grade-three.py", 0, "PASS", 3, 3, False, None),
        ("checks/grade-two.py", 0, "FAIL", 2, 3, True, "med"),
    ):
        outcome = run(repo, path)
        failures += expect(outcome.returncode, exit_code, f"{path} boundary exit")
        failures += expect(f"RESULT: {result}" in outcome.stdout, True, f"{path} boundary result")
        failures += expect((f"GRADE: {grade}" in outcome.stdout and f"BAR: {bar}" in outcome.stdout),
                           True, f"{path} exact grade and configured bar")
        failures += expect(grade < bar, below_bar, f"{path} surface-bar boundary")
        if severity is None:
            failures += expect("SEVERITY:" in outcome.stdout, False,
                               f"{path} bar-relative severity omitted")
        else:
            failures += expect(f"SEVERITY: {severity}" in outcome.stdout, True,
                               f"{path} bar-relative severity present")
        if grade == 2:
            failures += expect("REASON REQUIRED: boundary" in outcome.stdout, True,
                               f"{path} grade two reason requirement")
        data = run(repo, "--json", path)
        report = json.loads(data.stdout)
        record = report["records"][0]
        failures += expect(data.returncode, exit_code, f"{path} JSON boundary exit")
        failures += expect((record["grade"], record["bar"], record["result"]),
                           (grade, bar, result), f"{path} JSON grade-bar-result")
        failures += expect(record["severity"], severity, f"{path} JSON bar-relative severity")
    return failures


def test_diff_and_determinism(repo):
    write(repo, "src/diff.py", "def changed():\n    pass\n")
    write(repo, "src/deleted.py", "def deleted():\n    pass\n")
    write(repo, "src/rename\told.py", "def renamed():\n    pass\n")
    base = commit(repo, "base")
    write(repo, "src/diff.py", """def changed(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k
""")
    git(repo, "mv", "src/rename\told.py", "src/rename\nnew.py")
    write(repo, "src/rename\nnew.py", """def renamed(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k
""")
    head = commit(repo, "head")
    result = run(repo, "--base", base, "--head", head)
    failures = expect(result.returncode, 0, "diff grade two authorization exit")
    failures += expect("QUALNAME: changed" in result.stdout, True, "diff gated record")
    failures += expect('PATH: "src/rename\\nnew.py"' in result.stdout, True, "renamed odd path")
    failures += expect("deleted.py" in result.stdout, False, "deleted file omitted")
    failures += expect("UNGRADED:" in result.stdout, False, "deleted file never ungraded")
    left = repo.parent / "left-copy"
    right = repo.parent / "right-copy"
    shutil.copytree(repo, left)
    shutil.copytree(repo, right)
    for copy, order in ((left, ("zeta.py", "alpha.py")), (right, ("alpha.py", "zeta.py"))):
        for path in order:
            write(copy, f"src/{path}", """def unordered(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k
""")
        commit(copy, "vary enumeration order")
    one = run(left, "--base", head, "--head", "HEAD")
    two = run(right, "--base", head, "--head", "HEAD")
    failures += expect(one.stdout, two.stdout, "enumeration independent stdout")
    failures += expect(one.returncode, two.returncode, "enumeration independent exit")
    absolute = run(left, "--base", head, "--head", "HEAD", cwd=left / "src")
    failures += expect(absolute.stdout, one.stdout, "absolute script and distinct cwd stdout")
    supplied_orders = []
    original_paths = code_grade_cli._diff_paths
    try:
        for order in (["src/zeta.py", "src/alpha.py"], ["src/alpha.py", "src/zeta.py"]):
            code_grade_cli._diff_paths = lambda root, base, head, order=order: supplied_orders.append(
                tuple(order)) or order
            records, ungraded = code_grade_cli._diff_report(
                left, head, "HEAD", code_grade_cli._load_test_kinds(left))
            failures += expect(code_grade_cli._text(records, ungraded), one.stdout,
                               f"supplied changed-path order {order!r}")
    finally:
        code_grade_cli._diff_paths = original_paths
    failures += expect(supplied_orders, [("src/zeta.py", "src/alpha.py"),
                                         ("src/alpha.py", "src/zeta.py")],
                       "different changed-path orders supplied")
    return failures


def test_absent_new_path_grades_the_range(repo):
    """Grading a historical range whose new paths no longer exist in the working tree
    reports the range's findings instead of aborting on the first absent path."""
    write(repo, "src/absent_anchor.py", "def anchor():\n    return 0\n")
    base = commit(repo, "absent-case base")
    write(repo, "src/added_clean.py", "def added_clean():\n    return 1\n")
    write(repo, "src/added_risky.py", """def added_risky(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u):
    return a and b and c and d and e and f and g and h and i and j and k and l and m and n and o and p and q and r and s and t and u
""")
    head = commit(repo, "absent-case head")
    git(repo, "rm", "--quiet", "src/added_clean.py", "src/added_risky.py")
    commit(repo, "absent-case worktree moves past the graded range")
    result = run(repo, "--base", base, "--head", head)
    failures = expect("Traceback" in result.stderr, False,
                      "no crash when a path new in the range is absent from disk")
    failures += expect("QUALNAME: added_risky" in result.stdout, True,
                       "the masked finding is reported")
    failures += expect("RESULT: FAIL" in result.stdout, True, "the range reports its verdict")
    failures += expect(result.returncode, 1, "a blocking finding still blocks")
    return failures


def test_rename_diff_paths(repo):
    write(repo, "src/mover.py", "def mover():\n    pass\n")
    base = commit(repo, "rename base")
    git(repo, "mv", "src/mover.py", "src/moved.py")
    head = commit(repo, "rename head")
    raw_status = git(repo, "diff", "--name-status", "-z", "--find-renames", base, head).stdout
    failures = expect(raw_status.startswith("R"), True,
                      "git actually reports a rename status for the unchanged-content fixture")
    paths = code_grade_cli._diff_paths(repo, base, head)
    failures += expect(paths, ["src/moved.py"],
                       "_diff_paths keeps only the renamed head-side path, never the old one")
    return failures


def test_review_skill_states_severity_vocabulary():
    repo_root = Path(__file__).resolve().parents[2]
    skill_path = repo_root / ".claude/skills/harness-code-review/SKILL.md"
    text = skill_path.read_text()
    failures = expect("SEVERITY: high" in text, True,
                      "review skill names the tool's SEVERITY: high surface word")
    failures += expect("code_grade: fail" in text, True,
                       "review skill names code_grade: fail for a blocking record")
    failures += expect("not grade 2" in text, True,
                       "review skill states the high finding covers every blocking grade, "
                       "not only grade one")
    failures += expect("code_grade: grade_2" in text, True,
                       "review skill names code_grade: grade_2 for the grade-two record")
    return failures


def test_diff_paths_complexity():
    source = SCRIPT.read_text()
    records = {record.qualname: record.grade
              for record in code_grade_cli.code_grade.grade_source(source, "code-grade.py")}
    failures = 0
    for qualname in ("_diff_paths", "_run_name_status_diff", "_name_status_entries",
                     "_is_changed_python", "_status", "_load_test_kinds"):
        failures += expect(qualname in records, True, f"{qualname} present in code-grade.py")
        failures += expect(records.get(qualname, 0) >= 4, True, f"{qualname} grades 4 or better")
    for qualname in ("_record", "_severity", "_blocks", "_is_test", "_result", "_patterns"):
        failures += expect(qualname in records, False,
                           f"{qualname} moved out of code-grade.py, not duplicated")
    seam_source = (SCRIPT.parent / "code_grade.py").read_text()
    seam_records = {record.qualname: record.grade
                    for record in code_grade_cli.code_grade.grade_source(seam_source, "code_grade.py")}
    for qualname in ("classify", "_is_test_path", "_severity", "_blocks"):
        failures += expect(qualname in seam_records, True, f"{qualname} present in code_grade.py")
        failures += expect(seam_records.get(qualname, 0) >= 4, True, f"{qualname} grades 4 or better")
    return failures


def main():
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory) / "fixture"
        repo.mkdir()
        make_repo(repo)
        failures = test_paths(repo)
        failures += test_parse_and_usage(repo)
        failures += test_diff_and_determinism(repo)
        failures += test_rename_diff_paths(repo)
        failures += test_control_paths(repo)
        failures += test_rejected_revisions(repo)
        failures += test_bars_follow_test_kinds(repo)
        failures += test_absent_new_path_grades_the_range(repo)
    failures += test_review_skill_states_severity_vocabulary()
    failures += test_diff_paths_complexity()
    if not failures:
        print("PASS test-code-grade-cli")
    return failures


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
