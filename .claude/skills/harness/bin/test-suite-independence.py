#!/usr/bin/env python3
"""Fail when a Python test mutates a path derived from its live checkout."""

import argparse
import ast
import fnmatch
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
import harness_boundary

CONTENT_READS = {"read", "readline", "readlines", "read_text", "read_bytes", "load", "safe_load"}
OS_ONE = {"remove", "unlink", "rmdir", "truncate", "utime", "chmod", "makedirs", "mkdir"}
OS_TWO = {"rename", "replace"}
OS_DEST = {"symlink", "link"}
SHUTIL_DEST = {"copy", "copy2", "copyfile", "copytree", "move", "copymode", "copystat"}
PATH_METHODS = {"write_text", "write_bytes", "touch", "unlink", "rename", "replace", "mkdir", "rmdir", "chmod", "symlink_to", "hardlink_to"}


def resolve_scan_root(start):
    return harness_boundary.root_above(start)


def _names(node):
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _content_read(node):
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in CONTENT_READS


def _tainted(node, taint):
    return "__file__" in _names(node) or bool(_names(node) & taint)


def _targets(node):
    if isinstance(node, (ast.Tuple, ast.List)):
        for elt in node.elts:
            yield from _targets(elt)
    elif isinstance(node, ast.Name):
        yield node.id


def _call_name(call):
    if isinstance(call.func, ast.Attribute):
        owner = call.func.value
        if isinstance(owner, ast.Name):
            return owner.id, call.func.attr
        return None, call.func.attr
    if isinstance(call.func, ast.Name):
        return None, call.func.id
    return None, None


def _path_receiver(node, taint):
    if not _tainted(node, taint):
        return False
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        return _path_receiver(node.left, taint) or _path_receiver(node.right, taint)
    return (isinstance(node, ast.Call)
            and ((isinstance(node.func, ast.Name) and node.func.id == "Path")
                 or (isinstance(node.func, ast.Attribute)
                     and isinstance(node.func.value, ast.Name)
                     and node.func.value.id == "pathlib" and node.func.attr == "Path")))


def _sink(call, taint):
    owner, name = _call_name(call)
    args = call.args
    if owner is None and name == "open" and args:
        mode = "r"
        if len(args) > 1 and isinstance(args[1], ast.Constant) and isinstance(args[1].value, str):
            mode = args[1].value
        for kw in call.keywords:
            if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                mode = kw.value.value
        if any(c in mode for c in "wax+") and _tainted(args[0], taint):
            return "open"
    if owner == "os" and name in OS_ONE and args and _tainted(args[0], taint):
        return f"os.{name}"
    if owner == "os" and name in OS_TWO and any(_tainted(x, taint) for x in args[:2]):
        return f"os.{name}"
    if owner == "os" and name in OS_DEST and len(args) > 1 and _tainted(args[1], taint):
        return f"os.{name}"
    if owner == "shutil" and name in SHUTIL_DEST and len(args) > 1 and _tainted(args[1], taint):
        return f"shutil.{name}"
    if owner == "shutil" and name == "rmtree" and args and _tainted(args[0], taint):
        return "shutil.rmtree"
    if isinstance(call.func, ast.Attribute) and name in PATH_METHODS:
        if _path_receiver(call.func.value, taint):
            return name
    return None


def _scan_statements(statements, inherited, path, findings):
    taint = set(inherited)
    for stmt in statements:
        for call in (n for n in ast.walk(stmt) if isinstance(n, ast.Call)):
            sink = _sink(call, taint)
            if sink:
                findings.append((path, call.lineno, sink))
        if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
            value = stmt.value
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            if value is not None and _tainted(value, taint) and not _content_read(value):
                for target in targets:
                    taint.update(_targets(target))
        elif isinstance(stmt, ast.With):
            for item in stmt.items:
                if item.optional_vars and _tainted(item.context_expr, taint) and not _content_read(item.context_expr):
                    taint.update(_targets(item.optional_vars))
            _scan_statements(stmt.body, taint, path, findings)
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _scan_statements(stmt.body, taint, path, findings)
        elif isinstance(stmt, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try)):
            for field in ("body", "orelse", "finalbody"):
                _scan_statements(getattr(stmt, field, []), taint, path, findings)
            for handler in getattr(stmt, "handlers", []):
                _scan_statements(handler.body, taint, path, findings)


def scan_file(path):
    try:
        tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    except (OSError, SyntaxError, UnicodeError) as exc:
        return [(path, getattr(exc, "lineno", 1) or 1, "parse-error")]
    findings = []
    _scan_statements(tree.body, {"__file__"}, path, findings)
    return findings


def discover(root):
    found = []
    worktrees = os.path.join(root, ".claude", "worktrees")
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs
                   if d not in {".git", "node_modules", ".venv"}
                   and os.path.realpath(os.path.join(current, d)) != os.path.realpath(worktrees)]
        found.extend(os.path.join(current, name) for name in files
                     if fnmatch.fnmatch(name, "test-*.py") or fnmatch.fnmatch(name, "test_*.py"))
    return sorted(found)


def scan_directory(root):
    files = discover(root)
    findings = []
    for path in files:
        findings.extend(scan_file(path))
    return files, findings


def main(argv=None, start=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-dir")
    args = parser.parse_args(argv)
    if args.scan_dir:
        root = os.path.abspath(args.scan_dir)
    else:
        origin = start or HERE
        root = resolve_scan_root(origin)
        if root is None:
            print(f"ERROR could not resolve scan root above {origin}", file=sys.stderr)
            raise SystemExit(2)
    files, findings = scan_directory(root)
    print(f"root {root}")
    print(f"discovered {len(files)}")
    for path, line, sink in findings:
        print(f"VIOLATION {path}:{line} {sink} mutates a path derived from the live checkout")
    if findings:
        print(f"FAIL {len(findings)} live-tree mutation site(s)")
        return 1
    print("ok no test mutates a path derived from the live checkout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
