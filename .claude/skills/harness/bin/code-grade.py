#!/usr/bin/env python3
"""Report code-risk grades through the importable ``code_grade`` seam."""
from __future__ import annotations

import argparse
import ast
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


def _load_test_kinds(root):
    with (root / ".harness" / "harness.json").open(encoding="utf-8") as stream:
        return json.load(stream)["test_kinds"]


def _paths_report(root, paths, test_kinds):
    grades, ungraded = [], []
    for raw_path in paths:
        path = _relative(root, raw_path)
        try:
            grades.extend(code_grade.grade_source((root / path).read_text(), path))
        except (OSError, SyntaxError) as error:
            print(f"PARSE ERROR: {_display_path(path)}: {error}", file=sys.stderr)
            ungraded.append(path)
    records, _ = code_grade.classify(grades, test_kinds)
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


def _diff_report(root, base, head, test_kinds):
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
    records, _ = code_grade.classify(gated, test_kinds)
    return records, []


def _text(records, ungraded):
    lines = []
    for record in records:
        lines.extend(("FUNCTION", f"PATH: {_display_path(record['path'])}", f"LINE: {record['line']}",
                      f"QUALNAME: {record['qualname']}", f"CYCLOMATIC: {record['cyclomatic']}",
                      f"COGNITIVE: {record['cognitive']} ({record['cognitive_method']})",
                      f"ABC: {record['abc']:.1f}", f"GRADE: {record['grade']}",
                      f"DRIVER: {record['driver']}", f"BAR: {record['bar']}",
                      f"RESULT: {record['result']}"))
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
    return 1 if any(record["severity"] == "high" for record in records) else 0


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
        test_kinds = _load_test_kinds(root)
        base = code_grade.commit_oid(root, args.base) if args.base else None
        head = code_grade.commit_oid(root, args.head) if args.head else None
        records, ungraded = (_diff_report(root, base, head, test_kinds) if base else
                             _paths_report(root, args.paths, test_kinds))
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
