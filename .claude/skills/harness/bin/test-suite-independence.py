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
    return sorted(set(findings))


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


def _fixture_findings(root, name, source):
    path = os.path.join(root, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(source)
    return scan_file(path)


def _resolved_root_or_exit(start):
    root = resolve_scan_root(start)
    if root is None:
        print(f"ERROR could not resolve scan root above {start}", file=sys.stderr)
        raise SystemExit(2)
    return root


def run_self_tests():
    failures = []
    with tempfile.TemporaryDirectory() as root:
        cases = [
            ("injection idiom",
             "import os\nfs=os.path.join(os.path.dirname(os.path.realpath(__file__)),'x')\nopen(fs,'w').write('x')\n",
             {3}),
            ("mutant beside original",
             "import os,shutil\nSCRIPT=os.path.join(os.path.dirname(__file__),'s')\nmpath=os.path.join(os.path.dirname(os.path.realpath(SCRIPT)),'.m')\nopen(mpath,'w').write('x')\nshutil.copymode(SCRIPT,mpath)\n",
             {4, 5}),
            ("pid named mutant",
             "import os\nHERE=os.path.dirname(__file__)\npath=os.path.join(HERE,f'.mutant-{os.getpid()}.sh')\nopen(path,'w').write('x')\n",
             {4}),
        ]
        for index, (name, source, expected) in enumerate(cases):
            got = {line for _path, line, _sink in
                   _fixture_findings(root, f"test-red-{index}.py", source)}
            ok = got == expected
            print(f"{'ok' if ok else 'FAIL'} self-test {name}")
            if not ok:
                failures.append(f"{name}: expected {sorted(expected)}, got {sorted(got)}")

        clean = """import os, pathlib, shutil, tempfile
BIN_DIR=os.path.dirname(os.path.realpath(__file__))
text=open(os.path.join(BIN_DIR,'source')).read()
root=tempfile.mkdtemp()
dest=os.path.join(root,'bin')
shutil.copytree(BIN_DIR,dest)
open(os.path.join(root,text),'w').write('x')
pathlib.Path(root,'x').write_text('x')
"""
        clean_findings = _fixture_findings(root, "test-clean.py", clean)
        ok = not clean_findings
        print(f"{'ok' if ok else 'FAIL'} self-test clean controls")
        if not ok:
            failures.append(f"clean controls: {clean_findings!r}")

    expected = None
    current = os.path.dirname(os.path.realpath(__file__))
    while True:
        if os.path.isfile(os.path.join(current, ".harness", "team-config.yaml")):
            expected = current
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    live_root = resolve_scan_root(HERE)
    files, live_findings = scan_directory(live_root) if live_root else ([], [])
    ok = live_root == expected and len(files) >= 50 and not live_findings
    print(f"{'ok' if ok else 'FAIL'} self-test live tree, independent root and discovered floor")
    if not ok:
        failures.append(
            f"live tree: root={live_root!r} expected={expected!r} "
            f"discovered={len(files)} findings={len(live_findings)}")

    with tempfile.TemporaryDirectory() as rootless:
        none = resolve_scan_root(rootless)
        try:
            _resolved_root_or_exit(rootless)
        except SystemExit as exc:
            refused = exc.code == 2
        else:
            refused = False
        ok = none is None and refused
        print(f"{'ok' if ok else 'FAIL'} self-test unresolved root refuses")
        if not ok:
            failures.append(f"root refusal: resolved={none!r} refused={refused}")
    return failures


def main(argv=None, start=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-dir")
    args = parser.parse_args(argv)
    if args.scan_dir:
        root = os.path.abspath(args.scan_dir)
    else:
        origin = start or HERE
        root = _resolved_root_or_exit(origin)
    self_failures = run_self_tests()
    files, findings = scan_directory(root)
    print(f"root {root}")
    print(f"discovered {len(files)}")
    for path, line, sink in findings:
        print(f"VIOLATION {path}:{line} {sink} mutates a path derived from the live checkout")
    if findings or self_failures:
        for failure in self_failures:
            print(f"FAIL self-test detail: {failure}")
        print(f"FAIL {len(findings)} live-tree mutation site(s), "
              f"{len(self_failures)} self-test failure(s)")
        return 1
    print("ok no test mutates a path derived from the live checkout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
