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
from integration_support import BIN  # noqa: E402 (first import: the path seam)

import ast
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

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


def _module_aliases(node):
    """Names an `import glob [as x]` binds to the glob module."""
    if not isinstance(node, ast.Import):
        return set()
    return {alias.asname or "glob" for alias in node.names if alias.name == "glob"}


def _function_aliases(node):
    """Names a `from glob import glob|iglob [as x]` binds to a glob function."""
    if not (isinstance(node, ast.ImportFrom) and node.module == "glob"):
        return set()
    return {alias.asname or alias.name for alias in node.names
            if alias.name in ("glob", "iglob")}


def glob_names(tree):
    """`(module aliases, function aliases)` that reach glob.glob / glob.iglob."""
    modules, functions = set(), set()
    for node in ast.walk(tree):
        modules |= _module_aliases(node)
        functions |= _function_aliases(node)
    return modules, functions


def statement_lines(tree):
    """`{line: first line of the innermost statement containing it}`."""
    first = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.stmt):
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


def _parse(text):
    """The module's AST, or None when it cannot hold a site: no glob import, or no parse."""
    if "glob" not in text:
        return None
    try:
        return ast.parse(text)
    except SyntaxError:
        return None


def detected_sites(path):
    """`[(line, markers)]` for every detected site in the Python file `path`."""
    text = Path(path).read_text(encoding="utf-8")
    tree = _parse(text)
    if tree is None:
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
            start = stmts[node.lineno]
            sites.append((node.lineno, markers_for(lines, start, node.end_lineno)))
    return sorted(sites)


def census(bin_dir):
    """`{relative file: [(line, markers)]}` over every .py under `bin_dir`."""
    out = {}
    for path in sorted(Path(bin_dir).rglob("*.py")):
        sites = detected_sites(path)
        if sites:
            out[str(path.relative_to(bin_dir))] = sites
    return out


def findings(bin_dir, sites_by_file):
    """Marker violations over `sites_by_file`, a census of `bin_dir`."""
    bad = []
    for rel, sites in sites_by_file.items():
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
    @classmethod
    def setUpClass(cls):
        cls.sites = census(BIN)                # the live tree is read-only: one scan serves both

    def test_every_detected_site_is_marked(self):
        self.assertEqual(findings(BIN, self.sites), [])

    def test_the_census_is_not_vacuous(self):
        # A floor, not a figure: the scanner finding nothing would pass the assertion above.
        self.assertTrue(self.sites, "the census detected no site at all")


class Discrimination(unittest.TestCase):
    def setUp(self):
        self.bin = Path(tempfile.mkdtemp(prefix="census-"))
        self.addCleanup(shutil.rmtree, self.bin, True)

    def probe(self, source):
        Path(self.bin, "probe.py").write_text(source)

    def bad(self, source):
        self.probe(source)
        return findings(self.bin, census(self.bin))

    def sites(self, source):
        self.probe(source)
        return census(self.bin)

    def test_an_injected_unmarked_site_fails(self):
        bad = self.bad("import glob, os\n"
                       "x = glob.glob(os.path.join(r, '.harness', '*', 'features', '*'))\n")
        self.assertEqual(len(bad), 1)
        self.assertIn("probe.py:2 carries no marker", bad[0])

    def test_aliases_constants_and_locals_are_resolved(self):
        sites = self.sites(
            "import glob as _g\nfrom glob import iglob as walk\nimport os\n"
            "PAT = '.harness/*/features/*/feature.json'\n"
            "def f(r):\n"
            "    p = os.path.join(r, '.harness', 'features', '*')\n"
            "    _g.glob(PAT)\n    walk(p)\n    _g.glob(f'{r}/.harness/x/features/*')\n")
        self.assertEqual([line for line, _m in sites["probe.py"]], [7, 8, 9])

    def test_shapes_that_are_not_sites(self):
        sites = self.sites(
            "import glob, os, re\n"
            "# glob.glob('.harness/*/features/*')\n"
            "TEXT = 'plans = glob.glob(os.path.join(root, \".harness\", \"*\", \"features\", \"*\"))'\n"
            "RX = re.compile(r'^\\.harness/[^/]+/features/([^/]+)/')\n"
            "glob.glob(os.path.join(r, '.harness', 'harness', 'features', fid, 'BRIEF.md'))\n"
            "for p in pats:\n    glob.glob(p)\n")
        self.assertEqual(sites, {})

    def test_one_valid_marker_passes_and_two_fail(self):
        cases = (("checkout-local", "", 0),
                 ("checkout-local", "  # corpus-scope: owner-root", 1),
                 ("everywhere", "", 1))
        for above, trailing, expected in cases:
            with self.subTest(above=above, trailing=trailing):
                bad = self.bad(f"import glob\n# corpus-scope: {above}\n"
                               f"glob.glob('.harness/*/features/*'){trailing}\n")
                self.assertEqual(len(bad), expected)

    def test_an_owner_root_site_must_name_the_seam(self):
        bad = self.bad("import glob\n# corpus-scope: owner-root\n"
                       "glob.glob('.harness/*/features/*')\n")
        self.assertIn("does not name feature_corpus", bad[0])
        ok = self.bad("import glob, feature_corpus\n# corpus-scope: owner-root\n"
                      "glob.glob('.harness/*/features/*')\n")
        self.assertEqual(ok, [])


if __name__ == "__main__":
    unittest.main()
