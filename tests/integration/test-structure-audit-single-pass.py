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
points the test at another checker file.
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
import ast
import collections
import importlib.util
import json
import os
import runpy
import shutil
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_REL = os.path.join(".claude", "skills", "harness", "bin")
BIN_DIR = os.path.join(REPO_ROOT, BIN_REL)
SCRIPT = os.environ.get("CHECK_PLAN_ROUTES_BIN") or os.path.join(BIN_DIR, "check-plan-routes.py")
_TREE_FILES = (os.path.join(".harness", "harness", "docs", "DECISIONS-INDEX.md"),)
_TREE_DIRS = (os.path.join(".github", "workflows"), os.path.join(".claude", "skills", "harness", "hooks"))
_MARKER = os.path.join(".harness", "team-config.yaml")
# An embedded program (the `python3 -c` shape the broad-catch census parses) so the embedded
# AST is always among the counted trees; its narrow catch keeps the fixture tree clean.
_EMBEDDED_PROGRAM = "try:\n    import json\nexcept ValueError:\n    json = None\n"
_EMBEDDED_FIXTURE = (f'"""Fixture for test-structure-audit-single-pass.py."""\n'
                     f'PROGRAM = {_EMBEDDED_PROGRAM!r}\nAGAIN = {_EMBEDDED_PROGRAM!r}\n')
_OVERLAP = (os.path.join(BIN_REL, "check-state.py"), os.path.join(BIN_REL, "check_state", "table.py"))

failures = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name}{'' if cond else ' ' + detail}")
    if not cond:
        failures.append(name)


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
    for rel in _TREE_FILES + (_MARKER,):
        os.makedirs(os.path.dirname(os.path.join(td, rel)), exist_ok=True)
        if rel == _MARKER:
            open(os.path.join(td, rel), "w", encoding="utf-8").close()
        else:
            shutil.copy(os.path.join(REPO_ROOT, rel), os.path.join(td, rel))
    for rel in _TREE_DIRS:
        shutil.copytree(os.path.join(REPO_ROOT, rel), os.path.join(td, rel))
    with open(os.path.join(td, BIN_REL, "_single_pass_fixture.py"), "w", encoding="utf-8") as stream:
        stream.write(_EMBEDDED_FIXTURE)
    return td


def _checker():
    spec = importlib.util.spec_from_file_location("_cpr_single_pass", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _in_process(module, entry, root):
    with Traversal() as traversal:
        getattr(module, entry)(root)
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


def _via_cli(root):
    out = os.path.join(root, "single-pass-cli.json")
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR")}
    run = subprocess.run([sys.executable, os.path.abspath(__file__), "--cli-child", SCRIPT, root, out],
                         capture_output=True, text=True, timeout=60, env=env)
    if run.returncode != 0 or not os.path.isfile(out):
        return {"error": f"exit {run.returncode}: {run.stderr[-400:]}"}
    with open(out, encoding="utf-8") as stream:
        return json.load(stream)


def _check_once(label, summary, physical):
    print(f"COUNTS {label} {json.dumps({k: v for k, v in summary.items() if k != 'files'}, sort_keys=True)}")
    if "error" in summary:
        check(f"{label}_ran", False, summary["error"])
        return
    check(f"{label}_every_node_visited_exactly_once", summary["not_once"] == 0 and summary["visits"] == summary["nodes"],
          f"{summary['not_once']} node(s) not visited once; {summary['visits']} visits over {summary['nodes']} nodes")
    check(f"{label}_visits_no_node_outside_a_parsed_tree", summary["foreign"] == 0, f"{summary['foreign']} foreign")
    check(f"{label}_parses_no_source_twice", summary["reparsed"] == [], ", ".join(summary["reparsed"]))
    check(f"{label}_parses_embedded_programs", summary["embedded"] >= 1, "no embedded program parsed")
    missing = [rel for rel in physical if rel not in summary["files"]]
    check(f"{label}_parses_the_overlapping_checker_sources", missing == [], ", ".join(missing))


def main():
    module = _checker()
    with tempfile.TemporaryDirectory() as td:
        root = _fixture_root(td)
        for entry in ("consolidation_findings", "feat62_findings", "broad_catch_findings"):
            _check_once(f"in_process_{entry}", _in_process(module, entry, root), _OVERLAP)
        cli = _via_cli(root)
        _check_once("cli_consolidation_audit", cli, _OVERLAP)
        check("cli_consolidation_audit_exit_is_a_verdict", cli.get("exit") in (0, 1), f"exit {cli.get('exit')!r}")
    if failures:
        print(f"\n{len(failures)} FAILURE(S): {failures}")
        sys.exit(1)
    print("\nALL PASS")
    sys.exit(0)


if __name__ == "__main__":
    if sys.argv[1:2] == ["--cli-child"]:
        cli_child(*sys.argv[2:5])
    else:
        main()
