#!/usr/bin/env python3
"""Census of feature-directory enumerations under bin/ (FEAT-1559 SC-04, FEAT-58 D-15).

A DETECTED SITE is a call to glob.glob / glob.iglob — through any import alias — whose pattern,
resolved statically, enumerates feature directories: a `features` path component with a
wildcard in the segment before it or in the feature component after it. The resolver follows
string constants, os.path.join, f-strings, `+` concatenation, and names bound once to such an
expression (module constants and single-assignment locals).

Both assertions quantify over DETECTED sites only, never over marked ones:

  1. every detected site carries exactly one marker from the closed vocabulary, written as a
     `# corpus-scope: <value>` comment on the call's statement or in the comment lines directly
     above it;
  2. every detected `owner-root` site sits in a file that names feature_corpus.

THE BLIND CLASS, stated so nobody mistakes this for a guarantee: a pattern assembled at run
time — a loop variable, an argument, a value read from data — is not statically resolvable and is
not detected. check-domain.py's post-write sweep is one (its patterns reach glob through a list
built from SWEEP_GLOBS). pathlib's Path.glob, os.listdir and os.scandir are not detected either:
the census exists to catch an unresolved glob of the corpus, not to audit every directory read.
"""
import ast
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
VOCABULARY = ("owner-root", "active-feature", "checkout-local", "not-a-corpus-read")
MARKER = re.compile(r"#\s*corpus-scope:\s*(\S+)")
DYN = "<dyn>"


def _is_join(func):
    return (isinstance(func, ast.Attribute) and func.attr == "join"
            and isinstance(func.value, ast.Attribute) and func.value.attr == "path")


class Resolver:
    """Resolve an expression to path components, or [DYN] where it cannot."""

    def __init__(self, tree):
        self.bindings = {}
        counts = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                name = node.targets[0].id
                counts[name] = counts.get(name, 0) + 1
                self.bindings[name] = node.value
        for name, count in counts.items():
            if count > 1:
                del self.bindings[name]          # rebound: not a constant

    def components(self, node, depth=0):
        if depth > 8:
            return [DYN]
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return [p for p in node.value.split("/") if p] or [""]
        if isinstance(node, ast.Call) and _is_join(node.func):
            out = []
            for arg in node.args:
                out.extend(self.components(arg, depth + 1))
            return out
        if isinstance(node, ast.JoinedStr):
            text = "".join(v.value if isinstance(v, ast.Constant) else DYN for v in node.values)
            return [p for p in text.split("/") if p]
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left, right = self.components(node.left, depth + 1), self.components(node.right, depth + 1)
            return left[:-1] + [left[-1] + right[0]] + right[1:] if left and right else left + right
        if isinstance(node, ast.Name) and node.id in self.bindings:
            return self.components(self.bindings[node.id], depth + 1)
        return [DYN]


def enumerates_features(parts):
    for i, part in enumerate(parts):
        if part != "features":
            continue
        before = parts[i - 1] if i > 0 else ""
        after = parts[i + 1] if i + 1 < len(parts) else ""
        if "*" in before or "*" in after:
            return True
    return False


def glob_names(tree):
    """`(module aliases, function aliases)` that reach glob.glob / glob.iglob."""
    modules, functions = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "glob":
                    modules.add(alias.asname or "glob")
        elif isinstance(node, ast.ImportFrom) and node.module == "glob":
            for alias in node.names:
                if alias.name in ("glob", "iglob"):
                    functions.add(alias.asname or alias.name)
    return modules, functions


def statement_lines(tree):
    """`{line: first line of the innermost statement containing it}`."""
    first = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt) and hasattr(node, "end_lineno"):
            for line in range(node.lineno, node.end_lineno + 1):
                if line not in first or node.lineno > first[line]:
                    first[line] = node.lineno
    return first


def markers_for(lines, start, end):
    """Markers on lines start..end and in the comment block directly above `start`."""
    found = []
    for line in range(start, end + 1):
        found += MARKER.findall(lines[line - 1])
    above = start - 1
    while above >= 1 and lines[above - 1].strip().startswith("#"):
        found += MARKER.findall(lines[above - 1])
        above -= 1
    return found


def detected_sites(path):
    """`[(line, markers)]` for every detected site in the Python file `path`."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = text.splitlines()
    modules, functions = glob_names(tree)
    resolver = Resolver(tree)
    stmts = statement_lines(tree)
    sites = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        is_glob = ((isinstance(func, ast.Attribute) and func.attr in ("glob", "iglob")
                    and isinstance(func.value, ast.Name) and func.value.id in modules)
                   or (isinstance(func, ast.Name) and func.id in functions))
        if is_glob and enumerates_features(resolver.components(node.args[0])):
            start = stmts.get(node.lineno, node.lineno)
            sites.append((node.lineno, markers_for(lines, start, node.end_lineno)))
    return sorted(sites)


def census(bin_dir):
    """`{relative file: [(line, markers)]}` over every .py under `bin_dir`."""
    out = {}
    for path in sorted(Path(bin_dir).rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        sites = detected_sites(path)
        if sites:
            out[str(path.relative_to(bin_dir))] = sites
    return out


def findings(bin_dir):
    bad = []
    for rel, sites in census(bin_dir).items():
        names_seam = "feature_corpus" in Path(bin_dir, rel).read_text(encoding="utf-8")
        for line, markers in sites:
            if len(markers) != 1 or markers[0] not in VOCABULARY:
                bad.append(f"{rel}:{line} carries {markers or 'no marker'}; exactly one of "
                           f"{', '.join(VOCABULARY)} is required")
            elif markers[0] == "owner-root" and not names_seam:
                bad.append(f"{rel}:{line} is an owner-root site in a file that does not "
                           f"name feature_corpus")
    return bad


class LiveTree(unittest.TestCase):
    def test_every_detected_site_is_marked(self):
        self.assertEqual(findings(BIN), [])

    def test_the_census_is_not_vacuous(self):
        # A floor, not a figure: the scanner finding nothing would pass the assertion above.
        self.assertTrue(census(BIN), "the census detected no site at all")


class Discrimination(unittest.TestCase):
    def setUp(self):
        self.bin = Path(tempfile.mkdtemp(prefix="census-"))
        self.addCleanup(shutil.rmtree, self.bin, True)

    def scan(self, source):
        Path(self.bin, "probe.py").write_text(source)
        return findings(self.bin), census(self.bin)

    def test_an_injected_unmarked_site_fails(self):
        bad, _ = self.scan("import glob, os\n"
                           "x = glob.glob(os.path.join(r, '.harness', '*', 'features', '*'))\n")
        self.assertEqual(len(bad), 1)
        self.assertIn("probe.py:2 carries no marker", bad[0])

    def test_aliases_constants_and_locals_are_resolved(self):
        _, sites = self.scan(
            "import glob as _g\nfrom glob import iglob as walk\nimport os\n"
            "PAT = '.harness/*/features/*/feature.json'\n"
            "def f(r):\n"
            "    p = os.path.join(r, '.harness', 'features', '*')\n"
            "    _g.glob(PAT)\n    walk(p)\n    _g.glob(f'{r}/.harness/x/features/*')\n")
        self.assertEqual([line for line, _m in sites["probe.py"]], [7, 8, 9])

    def test_shapes_that_are_not_sites(self):
        _, sites = self.scan(
            "import glob, os, re\n"
            "# glob.glob('.harness/*/features/*')\n"
            "TEXT = 'plans = glob.glob(os.path.join(root, \".harness\", \"*\", \"features\", \"*\"))'\n"
            "RX = re.compile(r'^\\.harness/[^/]+/features/([^/]+)/')\n"
            "glob.glob(os.path.join(r, '.harness', 'harness', 'features', fid, 'BRIEF.md'))\n"
            "for p in pats:\n    glob.glob(p)\n")
        self.assertEqual(sites, {})

    def test_one_valid_marker_passes_and_two_fail(self):
        good, _ = self.scan("import glob\n# corpus-scope: checkout-local\n"
                            "glob.glob('.harness/*/features/*')\n")
        self.assertEqual(good, [])
        two, _ = self.scan("import glob\n# corpus-scope: checkout-local\n"
                           "glob.glob('.harness/*/features/*')  # corpus-scope: owner-root\n")
        self.assertEqual(len(two), 1)
        unknown, _ = self.scan("import glob\n# corpus-scope: everywhere\n"
                               "glob.glob('.harness/*/features/*')\n")
        self.assertEqual(len(unknown), 1)

    def test_an_owner_root_site_must_name_the_seam(self):
        bad, _ = self.scan("import glob\n# corpus-scope: owner-root\n"
                           "glob.glob('.harness/*/features/*')\n")
        self.assertIn("does not name feature_corpus", bad[0])
        ok, _ = self.scan("import glob, feature_corpus\n# corpus-scope: owner-root\n"
                          "glob.glob('.harness/*/features/*')\n")
        self.assertEqual(ok, [])


if __name__ == "__main__":
    unittest.main()
