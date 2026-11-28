#!/usr/bin/env python3
"""FEAT-2081 SC-06: each structure audit traverses every parsed AST exactly once.

Instruments `ast.parse` and `ast.iter_child_nodes` (the primitive `ast.walk` drives) and runs
the audits through both existing entry paths over an isolated copy of the checked-out tree:
the in-process public calls test-checker-structure-locks.py makes (`consolidation_findings`,
`feat62_findings`, `broad_catch_findings`), and the `--consolidation-audit` CLI. Per
invocation, every node of every parsed physical or embedded AST must be visited exactly once,
no node outside those trees may be visited, and no source may be parsed twice -- check-state.py
and its check_state/ package sit in the reader census AND the checker-structure surface AND
the broad-catch census, so they are where a repeated parse would show. CHECK_PLAN_ROUTES_BIN
points the test at another checker file and the audit modules beside it.
"""
from integration_support import ROOT, BIN
import ast
import collections
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile

from check_support import Checks

REPO_ROOT, BIN_DIR = str(ROOT), str(BIN)
BIN_REL = os.path.relpath(BIN_DIR, REPO_ROOT)
SCRIPT = os.environ.get("CHECK_PLAN_ROUTES_BIN") or os.path.join(BIN_DIR, "check-plan-routes.py")
# The audit modules UNDER TEST sit beside SCRIPT, so a mutant bin named through the override
# is what gets imported.
AUDIT_DIR = os.path.dirname(os.path.abspath(SCRIPT))
sys.path.insert(0, AUDIT_DIR)
import structure_audit  # noqa: E402
_TREE_FILES = (os.path.join(".harness", "harness", "docs", "DECISIONS-INDEX.md"),)
_TREE_DIRS = (os.path.join(".github", "workflows"), os.path.join(".claude", "skills", "harness", "hooks"))
_MARKER = os.path.join(".harness", "team-config.yaml")
# An embedded program (the `python3 -c` shape the broad-catch census parses) so the embedded
# AST is always among the counted trees; its narrow catch keeps the fixture tree clean.
_EMBEDDED_PROGRAM = "try:\n    import json\nexcept ValueError:\n    json = None\n"
_EMBEDDED_FIXTURE = (f'"""Fixture for test-structure-audit-single-pass.py."""\n'
                     f'PROGRAM = {_EMBEDDED_PROGRAM!r}\nAGAIN = {_EMBEDDED_PROGRAM!r}\n')
_OVERLAP = (os.path.join(BIN_REL, "check-state.py"), os.path.join(BIN_REL, "check_state", "table.py"))

C = Checks()
check = C.check


class Traversal:
    """Every tree `ast.parse` returns and every node `ast.iter_child_nodes` is asked about."""

    def __init__(self):
        self.trees, self.parses, self.visits, self.held = [], collections.Counter(), collections.Counter(), {}
        self._parse, self._children = ast.parse, ast.iter_child_nodes

    def parse(self, source, filename="<unknown>", *args, **kwargs):
        tree = self._parse(source, filename, *args, **kwargs)
        self.trees.append(tree)
        self.parses[(filename, source)] += 1
        return tree

    def children(self, node):
        self.visits[id(node)] += 1
        self.held[id(node)] = node        # keep it alive so its id is never reused
        return self._children(node)

    def __enter__(self):
        ast.parse, ast.iter_child_nodes = self.parse, self.children
        return self

    def __exit__(self, *exc):
        ast.parse, ast.iter_child_nodes = self._parse, self._children

    def _tree_nodes(self, tree):
        todo, nodes = [tree], []
        while todo:
            node = todo.pop()
            nodes.append(node)
            todo.extend(self._children(node))
        return nodes

    def summary(self):
        """Counts and the defects: nodes not visited exactly once, foreign visits, re-parses.
        CPython shares one `Load()`/`Store()` context object across a tree, so a node's expected
        visits are its number of occurrences in the parsed trees, not one per object."""
        expected = collections.Counter(id(node) for tree in self.trees for node in self._tree_nodes(tree))
        return {
            "trees": len(self.trees), "nodes": sum(expected.values()), "visits": sum(self.visits.values()),
            "not_once": sum(1 for key, n in expected.items() if self.visits[key] != n),
            "foreign": len(set(self.visits) - set(expected)),
            "reparsed": sorted(f for (f, _s), n in self.parses.items() if n > 1),
            "files": sorted({f for f, _s in self.parses}),
            "embedded": sum(n for (_f, s), n in self.parses.items() if s == _EMBEDDED_PROGRAM),
        }


def _fixture_root(td):
    shutil.copytree(BIN_DIR, os.path.join(td, BIN_REL), ignore=shutil.ignore_patterns("__pycache__"))
    for rel in _TREE_FILES:
        os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
        shutil.copy(os.path.join(REPO_ROOT, rel), os.path.join(td, rel))
    os.makedirs(os.path.dirname(os.path.join(td, _MARKER)), exist_ok=True)
    open(os.path.join(td, _MARKER), "w", encoding="utf-8").close()
    for rel in _TREE_DIRS:
        shutil.copytree(os.path.join(REPO_ROOT, rel), os.path.join(td, rel))
    with open(os.path.join(td, BIN_REL, "_single_pass_fixture.py"), "w", encoding="utf-8") as stream:
        stream.write(_EMBEDDED_FIXTURE)


def _in_process(entry, root):
    with Traversal() as traversal:
        getattr(structure_audit, entry)(root)
    return traversal.summary()


def cli_child(script, root, out):
    """Child-process body: run the CLI under instrumentation, write the summary as JSON."""
    sys.argv = [script, "--consolidation-audit"]
    os.environ["HARNESS_PROJECT_DIR"] = root
    code = None
    with Traversal() as traversal:
        try:
            runpy.run_path(script, run_name="__main__")
        except SystemExit as stop:
            code = stop.code
    with open(out, "w", encoding="utf-8") as stream:
        json.dump(dict(traversal.summary(), exit=code), stream)


def _start_cli(root, out):
    """Start the CLI child; its JSON goes to `out`, outside the audited root, so it can run beside
    the in-process audits without adding a file to the tree they walk."""
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR")}
    return subprocess.Popen([sys.executable, os.path.abspath(__file__), "--cli-child", SCRIPT, root, out],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)


def _collect_cli(child, out):
    try:
        _stdout, stderr = child.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        child.kill()
        _stdout, stderr = child.communicate()
    if child.returncode != 0 or not os.path.isfile(out):
        return {"error": f"exit {child.returncode}: {stderr[-400:]}"}
    with open(out, encoding="utf-8") as stream:
        return json.load(stream)


def _check_once(label, summary):
    print(f"COUNTS {label} {json.dumps({k: v for k, v in summary.items() if k != 'files'}, sort_keys=True)}")
    if "error" in summary:
        check(f"{label}_ran", False, summary["error"])
        return
    check(f"{label}_every_node_visited_exactly_once", summary["not_once"] == 0 and summary["visits"] == summary["nodes"],
          f"{summary['not_once']} node(s) not visited once; {summary['visits']} visits over {summary['nodes']} nodes")
    check(f"{label}_visits_no_node_outside_a_parsed_tree", summary["foreign"] == 0, f"{summary['foreign']} foreign")
    check(f"{label}_parses_no_source_twice", summary["reparsed"] == [], ", ".join(summary["reparsed"]))
    check(f"{label}_parses_embedded_programs", summary["embedded"] >= 1, "no embedded program parsed")
    missing = [rel for rel in _OVERLAP if rel not in summary["files"]]
    check(f"{label}_parses_the_overlapping_checker_sources", missing == [], ", ".join(missing))


def main():
    check("audit_modules_load_from_the_bin_under_test",
          all(os.path.dirname(os.path.abspath(m.__file__)) == AUDIT_DIR
              for m in (structure_audit, sys.modules["canonical_reader_audit"])),
          f"{structure_audit.__file__}, {sys.modules['canonical_reader_audit'].__file__}")
    with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as scratch:
        _fixture_root(root)
        out = os.path.join(scratch, "single-pass-cli.json")
        child = _start_cli(root, out)
        for entry in ("consolidation_findings", "feat62_findings", "broad_catch_findings"):
            _check_once(f"in_process_{entry}", _in_process(entry, root))
        cli = _collect_cli(child, out)
        _check_once("cli_consolidation_audit", cli)
        check("cli_consolidation_audit_exit_is_a_verdict", cli.get("exit") in (0, 1), f"exit {cli.get('exit')!r}")
    sys.exit(C.report())


if __name__ == "__main__":
    if sys.argv[1:2] == ["--cli-child"]:
        cli_child(*sys.argv[2:5])
    else:
        main()
