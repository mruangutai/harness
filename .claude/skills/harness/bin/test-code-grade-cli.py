#!/usr/bin/env python3
"""Subprocess contract tests for code-grade.py."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("code-grade.py")


def run(repo, *args, cwd=None):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], text=True,
                          capture_output=True, cwd=cwd or repo)


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
        "detect": ".claude/skills/harness/bin/test-*.py", "exclude": ".claude/worktrees/**",
        "status": "active"}}}))


def expect(actual, expected, label):
    if actual != expected:
        print(f"FAIL {label}: expected {expected!r}, got {actual!r}")
        return 1
    return 0


def test_paths(repo):
    write(repo, "src/risk.py", """def grade_two(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k

def grade_one(a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t,u):
    return a and b and c and d and e and f and g and h and i and j and k and l and m and n and o and p and q and r and s and t and u
""")
    write(repo, ".claude/skills/harness/bin/test-sample.py", """def test_grade_three(a,b,c,d,e,f,g,h,i):
    return a and b and c and d and e and f and g and h and i
""")
    result = run(repo, "src/risk.py", ".claude/skills/harness/bin/test-sample.py")
    failures = 0
    failures += expect(result.returncode, 1, "path bar exit")
    for field in ("PATH: src/risk.py", "LINE: 1", "QUALNAME: grade_two",
                  "CYCLOMATIC: 11", "COGNITIVE: 1 (Sonar-style approximation)", "ABC: 10.0",
                  "GRADE: 2", "DRIVER: cyclomatic", "BAR: 4", "RESULT: FAIL",
                  "SEVERITY: med", "REASON REQUIRED: grade_two", "SEVERITY: high",
                  "BAR: 3", "RESULT: PASS", "PASSING: 1"):
        failures += expect(field in result.stdout, True, f"text field {field}")
    data = run(repo, "--json", "src/risk.py", ".claude/skills/harness/bin/test-sample.py")
    failures += expect(data.returncode, 1, "json bar exit")
    report = json.loads(data.stdout)
    record = next(row for row in report["records"] if row["qualname"] == "grade_two")
    for key, value in {"path": "src/risk.py", "line": 1, "qualname": "grade_two",
                       "cyclomatic": 11, "cognitive": 1,
                       "cognitive_method": "Sonar-style approximation", "abc": 10.0, "grade": 2,
                       "driver": "cyclomatic", "bar": 4, "severity": "med"}.items():
        failures += expect(record[key], value, f"json {key}")
    clean = run(repo, ".claude/skills/harness/bin/test-sample.py")
    failures += expect(clean.returncode, 0, "test grade three passes")
    failures += expect("REASON REQUIRED" in clean.stdout, False, "reason omitted without grade two")
    return failures


def test_parse_and_usage(repo):
    write(repo, "src/bad.py", "def broken(:\n")
    result = run(repo, "src/bad.py")
    failures = expect(result.returncode, 3, "parse error exit")
    failures += expect("PARSE ERROR: src/bad.py" in result.stderr, True, "parse stderr")
    failures += expect("UNGRADED:\n  src/bad.py" in result.stdout, True, "ungraded report")
    failures += expect("PASSING: 0" in result.stdout, True, "ungraded excluded from passing")
    usage = run(repo, "--base", "HEAD")
    return failures + expect(usage.returncode, 2, "usage exit")


def test_diff_and_determinism(repo):
    write(repo, "src/diff.py", "def changed():\n    pass\n")
    write(repo, "src/deleted.py", "def deleted():\n    pass\n")
    write(repo, "src/rename\told.py", "def renamed():\n    pass\n")
    base = commit(repo, "base")
    write(repo, "src/diff.py", """def changed(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k
""")
    git(repo, "rm", "src/deleted.py")
    git(repo, "mv", "src/rename\told.py", "src/rename\nnew.py")
    write(repo, "src/rename\nnew.py", """def renamed(a,b,c,d,e,f,g,h,i,j,k):
    return a and b and c and d and e and f and g and h and i and j and k
""")
    head = commit(repo, "head")
    result = run(repo, "--base", base, "--head", head)
    failures = expect(result.returncode, 1, "diff bar exit")
    failures += expect("QUALNAME: changed" in result.stdout, True, "diff gated record")
    failures += expect("PATH: src/rename\nnew.py" in result.stdout, True, "renamed odd path")
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
    return failures


def main():
    with tempfile.TemporaryDirectory() as directory:
        repo = Path(directory) / "fixture"
        repo.mkdir()
        make_repo(repo)
        failures = test_paths(repo)
        failures += test_parse_and_usage(repo)
        failures += test_diff_and_determinism(repo)
    if not failures:
        print("PASS test-code-grade-cli")
    return failures


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
