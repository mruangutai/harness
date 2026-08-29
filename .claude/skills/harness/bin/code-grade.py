#!/usr/bin/env python3
"""Report code-risk grades through the importable ``code_grade`` seam."""
from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

import code_grade


def _git_root(directory):
    result = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                            text=True, capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or "not inside a git repository")
    return Path(result.stdout.strip()).resolve()



def _display_path(path):
    return json.dumps(path, ensure_ascii=True)


def _git_text(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.strip())
    return result.stdout


def _relative(root, path):
    try:
        return Path(path).resolve().relative_to(root).as_posix()
    except ValueError as error:
        raise ValueError(f"path outside repository: {path}") from error


def _patterns(value):
    return [part.strip() for part in value.split("|") if part.strip()]


def _is_test(root, relative):
    with (root / ".harness" / "harness.json").open(encoding="utf-8") as stream:
        kinds = json.load(stream)["test_kinds"]
    return any(any(fnmatch.fnmatch(relative, pattern) for pattern in _patterns(kind["detect"])) and
               not any(fnmatch.fnmatch(relative, pattern) for pattern in _patterns(kind.get("exclude", "")))
               for kind in kinds.values() if kind.get("status") == "active")


def _blocks(grade, bar):
    return grade < bar and grade != 2


def _severity(grade, bar):
    if _blocks(grade, bar):
        return "high"
    return "med" if grade == 2 else None


def _record(grade, root):
    bar = 3 if _is_test(root, grade.path) else 4
    severity = _severity(grade.grade, bar)
    record = {"path": grade.path, "line": grade.lineno, "qualname": grade.qualname,
              "cyclomatic": grade.cyclomatic, "cognitive": grade.cognitive,
              "cognitive_method": "Sonar-style approximation", "abc": grade.abc,
              "grade": grade.grade, "driver": grade.driver, "bar": bar, "severity": severity}
    record["result"] = _result(record)
    return record


def _paths_report(root, paths):
    records, ungraded = [], []
    for raw_path in paths:
        path = _relative(root, raw_path)
        try:
            grades = code_grade.grade_source((root / path).read_text(), path)
        except (OSError, SyntaxError) as error:
            print(f"PARSE ERROR: {_display_path(path)}: {error}", file=sys.stderr)
            ungraded.append(path)
            continue
        records.extend(_record(grade, root) for grade in grades)
    return records, ungraded


def _run_name_status_diff(root, base, head):
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--find-renames", "--name-status", "-z", base, head],
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def _name_status_entries(raw):
    fields = iter(raw.split(b"\0"))
    for raw_status in fields:
        if not raw_status:
            continue
        status = raw_status.decode()
        if status.startswith(("R", "C")):
            next(fields)
        yield status, next(fields).decode(errors="surrogateescape")


def _is_changed_python(status, path):
    return not status.startswith("D") and path.endswith(".py")


def _diff_paths(root, base, head):
    raw = _run_name_status_diff(root, base, head)
    entries = _name_status_entries(raw)
    return sorted(path for status, path in entries if _is_changed_python(status, path))


def _diff_report(root, base, head):
    paths = _diff_paths(root, base, head)
    ungraded = []
    for path in paths:
        try:
            ast.parse(_git_text(root, "show", f"{head}:{path}"))
        except (SyntaxError, ValueError) as error:
            print(f"PARSE ERROR: {_display_path(path)}: {error}", file=sys.stderr)
            ungraded.append(path)
    if ungraded:
        return [], ungraded
    gated, _ = code_grade.gated_set(root, base, head)
    return [_record(grade, root) for grade in gated], []




def _result(record):
    return "PASS" if record["grade"] >= record["bar"] else "FAIL"


def _text(records, ungraded):
    lines = []
    for record in records:
        lines.extend(("FUNCTION", f"PATH: {_display_path(record['path'])}", f"LINE: {record['line']}",
                      f"QUALNAME: {record['qualname']}", f"CYCLOMATIC: {record['cyclomatic']}",
                      f"COGNITIVE: {record['cognitive']} ({record['cognitive_method']})",
                      f"ABC: {record['abc']:.1f}", f"GRADE: {record['grade']}",
                      f"DRIVER: {record['driver']}", f"BAR: {record['bar']}",
                      f"RESULT: {_result(record)}"))
        if record["severity"]:
            lines.append(f"SEVERITY: {record['severity']}")
        if record["grade"] == 2:
            lines.append(f"REASON REQUIRED: {record['qualname']}")
        lines.append("")
    lines.append(f"PASSING: {sum(record['grade'] >= record['bar'] for record in records)}")
    if ungraded:
        lines.append("UNGRADED:")
        lines.extend(f"  {_display_path(path)}" for path in ungraded)
    return "\n".join(lines) + "\n"


def _status(records, ungraded):
    if ungraded:
        return 3
    return 1 if any(_blocks(record["grade"], record["bar"]) for record in records) else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report code-risk grades")
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("paths", nargs="*")
    args = parser.parse_args(argv)
    if bool(args.base) != bool(args.head) or (args.base and args.paths) or not (args.base or args.paths):
        parser.error("provide PATH... or both --base REF and --head REF")
    try:
        root = _git_root(Path.cwd())
        base = code_grade.commit_oid(root, args.base) if args.base else None
        head = code_grade.commit_oid(root, args.head) if args.head else None
        records, ungraded = (_diff_report(root, base, head) if base else
                             _paths_report(root, args.paths))
    except ValueError as error:
        parser.error(str(error))
    records.sort(key=lambda record: (record["path"], record["line"]))
    if args.json:
        print(json.dumps({"records": records, "passing": sum(
            record["grade"] >= record["bar"] for record in records), "ungraded": sorted(ungraded)},
                         sort_keys=True))
    else:
        print(_text(records, sorted(ungraded)), end="")
    return _status(records, ungraded)


if __name__ == "__main__":
    sys.exit(main())
