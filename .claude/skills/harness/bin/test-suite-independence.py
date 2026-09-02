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
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def _content_read(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in CONTENT_READS)


def _tainted(node, taint):
    names = _names(node)
    return "__file__" in names or bool(names & taint)


def _targets(node):
    if isinstance(node, (ast.Tuple, ast.List)):
        for item in node.elts:
            yield from _targets(item)
    elif isinstance(node, ast.Name):
        yield node.id


def _call_name(call):
    if not isinstance(call.func, ast.Attribute):
        return (None, call.func.id) if isinstance(call.func, ast.Name) else (None, None)
    owner = call.func.value
    return (owner.id if isinstance(owner, ast.Name) else None, call.func.attr)


def _is_path_constructor(node):
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Name):
        return node.func.id == "Path"
    return (isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "pathlib" and node.func.attr == "Path")


def _path_receiver(node, taint):
    if not _tainted(node, taint):
        return False
    current = node
    while isinstance(current, ast.BinOp) and isinstance(current.op, ast.Div):
        if _is_path_constructor(current.right):
            return True
        current = current.left
    return _is_path_constructor(current)


def _open_mode(call):
    positional = call.args[1].value if (
        len(call.args) > 1 and isinstance(call.args[1], ast.Constant)
        and isinstance(call.args[1].value, str)) else None
    keyword = next((item.value.value for item in call.keywords
                    if item.arg == "mode" and isinstance(item.value, ast.Constant)
                    and isinstance(item.value.value, str)), None)
    return keyword or positional or "r"


def _open_sink(call, owner, name, taint):
    if owner is not None or name != "open" or not call.args:
        return None
    writes = any(char in _open_mode(call) for char in "wax+")
    return "open" if writes and _tainted(call.args[0], taint) else None

def _os_sink(call, owner, name, taint):
    if owner != "os":
        return None
    indexes = ([0] if name in OS_ONE else [0, 1] if name in OS_TWO
               else [1] if name in OS_DEST else [])
    return f"os.{name}" if any(i < len(call.args) and _tainted(call.args[i], taint)
                               for i in indexes) else None


def _shutil_sink(call, owner, name, taint):
    if owner != "shutil":
        return None
    index = 1 if name in SHUTIL_DEST else 0 if name == "rmtree" else None
    return (f"shutil.{name}" if index is not None and index < len(call.args)
            and _tainted(call.args[index], taint) else None)


def _method_sink(call, _owner, name, taint):
    if not isinstance(call.func, ast.Attribute) or name not in PATH_METHODS:
        return None
    return name if _path_receiver(call.func.value, taint) else None


def _sink(call, taint):
    owner, name = _call_name(call)
    for detector in (_open_sink, _os_sink, _shutil_sink, _method_sink):
        result = detector(call, owner, name, taint)
        if result:
            return result
    return None


def _record_sinks(stmt, taint, path, findings):
    for call in (item for item in ast.walk(stmt) if isinstance(item, ast.Call)):
        sink = _sink(call, taint)
        if sink:
            findings.append((path, call.lineno, sink))


def _update_assignment(stmt, taint):
    if not isinstance(stmt, (ast.Assign, ast.AnnAssign)):
        return
    value = stmt.value
    targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
    if value is not None and _tainted(value, taint) and not _content_read(value):
        for target in targets:
            taint.update(_targets(target))


def _update_with(stmt, taint):
    if not isinstance(stmt, ast.With):
        return
    for item in stmt.items:
        if (item.optional_vars and _tainted(item.context_expr, taint)
                and not _content_read(item.context_expr)):
            taint.update(_targets(item.optional_vars))


def _nested_blocks(stmt):
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.With)):
        return [stmt.body]
    if isinstance(stmt, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try)):
        blocks = [getattr(stmt, field, []) for field in ("body", "orelse", "finalbody")]
        return blocks + [handler.body for handler in getattr(stmt, "handlers", [])]
    return []


def _scan_statements(statements, inherited, path, findings):
    taint = set(inherited)
    for stmt in statements:
        _record_sinks(stmt, taint, path, findings)
        _update_assignment(stmt, taint)
        _update_with(stmt, taint)
        for block in _nested_blocks(stmt):
            _scan_statements(block, taint, path, findings)


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
    worktrees = os.path.realpath(os.path.join(root, ".claude", "worktrees"))
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in {".git", "node_modules", ".venv"}
                   and os.path.realpath(os.path.join(current, name)) != worktrees]
        found.extend(os.path.join(current, name) for name in files
                     if fnmatch.fnmatch(name, "test-*.py") or fnmatch.fnmatch(name, "test_*.py"))
    return sorted(found)


def scan_directory(root):
    files = discover(root)
    findings = [finding for path in files for finding in scan_file(path)]
    return files, findings


def _fixture_findings(root, name, source):
    path = os.path.join(root, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(source)
    return scan_file(path)


def _check_fixture(root, name, source, expected):
    got = {line for _path, line, _sink in _fixture_findings(root, name, source)}
    ok = got == expected
    print(f"{'ok' if ok else 'FAIL'} self-test {name}")
    return None if ok else f"{name}: expected {sorted(expected)}, got {sorted(got)}"


def _red_fixture_failures(root):
    cases = [
        ("injection idiom", "import os\nfs=os.path.join(os.path.dirname(os.path.realpath(__file__)),'x')\nopen(fs,'w').write('x')\n", {3}),
        ("mutant beside original", "import os,shutil\nSCRIPT=os.path.join(os.path.dirname(__file__),'s')\nmpath=os.path.join(os.path.dirname(os.path.realpath(SCRIPT)),'.m')\nopen(mpath,'w').write('x')\nshutil.copymode(SCRIPT,mpath)\n", {4, 5}),
        ("pid named mutant", "import os\nHERE=os.path.dirname(__file__)\npath=os.path.join(HERE,f'.mutant-{os.getpid()}.sh')\nopen(path,'w').write('x')\n", {4}),
    ]
    return [failure for index, (name, source, expected) in enumerate(cases)
            if (failure := _check_fixture(root, f"{index}-{name}", source, expected))]


def _clean_fixture_failure(root):
    source = """import os, pathlib, shutil, tempfile
BIN_DIR=os.path.dirname(os.path.realpath(__file__))
text=open(os.path.join(BIN_DIR,'source')).read()
changed=text.replace('a','b')
root=tempfile.mkdtemp()
dest=os.path.join(root,'bin')
shutil.copytree(BIN_DIR,dest)
open(os.path.join(root,changed),'w').write('x')
pathlib.Path(root,'x').write_text('x')
"""
    findings = _fixture_findings(root, "clean controls", source)
    print(f"{'ok' if not findings else 'FAIL'} self-test clean controls")
    return None if not findings else f"clean controls: {findings!r}"


def _independent_expected_root():
    current = HERE
    while True:
        if os.path.isfile(os.path.join(current, harness_boundary.MARKER)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def _live_fixture_failure():
    root = resolve_scan_root(HERE)
    files, findings = scan_directory(root) if root else ([], [])
    ok = root == _independent_expected_root() and len(files) >= 50 and not findings
    print(f"{'ok' if ok else 'FAIL'} self-test live tree, independent root and discovered floor")
    return None if ok else f"live tree: root={root!r} discovered={len(files)} findings={len(findings)}"


def _resolved_root_or_exit(start):
    root = resolve_scan_root(start)
    if root is None:
        print(f"ERROR could not resolve scan root above {start}", file=sys.stderr)
        raise SystemExit(2)
    return root


def _root_refusal_failure():
    with tempfile.TemporaryDirectory() as rootless:
        try:
            _resolved_root_or_exit(rootless)
        except SystemExit as exc:
            refused = exc.code == 2
        else:
            refused = False
        ok = resolve_scan_root(rootless) is None and refused
    print(f"{'ok' if ok else 'FAIL'} self-test unresolved root refuses")
    return None if ok else "unresolved root did not refuse at exit 2"


def run_self_tests():
    with tempfile.TemporaryDirectory() as root:
        failures = _red_fixture_failures(root)
        clean = _clean_fixture_failure(root)
    return failures + [failure for failure in (clean, _live_fixture_failure(), _root_refusal_failure())
                       if failure]


def main(argv=None, start=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--scan-dir")
    args = parser.parse_args(argv)
    root = os.path.abspath(args.scan_dir) if args.scan_dir else _resolved_root_or_exit(start or HERE)
    self_failures = run_self_tests()
    files, findings = scan_directory(root)
    print(f"root {root}")
    print(f"discovered {len(files)}")
    for path, line, sink in findings:
        print(f"VIOLATION {path}:{line} {sink} mutates a path derived from the live checkout")
    for failure in self_failures:
        print(f"FAIL self-test detail: {failure}")
    if findings or self_failures:
        print(f"FAIL {len(findings)} live-tree mutation site(s), {len(self_failures)} self-test failure(s)")
        return 1
    print("ok no test mutates a path derived from the live checkout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
