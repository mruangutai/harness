#!/usr/bin/env python3
"""FEAT-2489 T-02: one-time matched-tree CLI-equivalence checker for the plan-routes split.

Run from the checkout root. It reads committed content only and writes nothing outside its
own temporary directory. OLD is the base commit; NEW is the base commit with only the head's
.claude/skills/harness/bin and tests overlaid. Both entries run over nine checks; the only
rewrite any comparison applies is the relocation map, derived from the move (never from the
inventory) and applied only to the path span of the locator field of formats R1 to R6. Line
numbers and traceback frames are not modelled: an R7 locator in the three split files FAILs,
and every unrecognised line is compared exactly (plan conditions C1 and C2).

This is feature-notes evidence, never a permanent test (grilling Q3).
"""

import argparse
import ast
import concurrent.futures
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

CHECKOUT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
BIN = ".claude/skills/harness/bin"
ENTRY = BIN + "/check-plan-routes.py"
MODULES = (BIN + "/canonical_reader_audit.py", BIN + "/structure_audit.py")
SPLIT_FILES = ("check-plan-routes.py", "canonical_reader_audit.py", "structure_audit.py")
FEATURE_DIR = ".harness/harness/features/FEAT-2489-plan-routes-split/"
OVERLAID = (BIN + "/", "tests/")
CLASSIFICATION = "tests/integration/canonical-reader-classification.json"
RELOCATED_ROW = "::_classification_document::json_file#1"
RELOCATED_FINDING = "::_classification_document json_file remedy=none: exemption requires a reason"
SCRUBBED_ENV = ("CLAUDE_PROJECT_DIR", "HARNESS_PROJECT_DIR", "HARNESS_AGENT_TYPE")

LOC = r"(?P<path>[^\s:]+\.py)::(?P<symbol>[^\s:]+)"
RECOGNIZED = tuple(re.compile(pattern) for pattern in (
    r"^CLASSIFICATION " + LOC + r" \S+ remedy=.*$",                                    # R1
    r"^CLASSIFICATION " + LOC + r" \S+: artifact row absent from AST\. PLAN AMENDMENT REQUIRED$",  # R2
    r"^CLASSIFICATION " + LOC + r"::[^\s:]+#\d+: observed state=.*$",                  # R3
    r"^CLASSIFICATION duplicate classification row " + LOC
    + r"::[^\s:]+#\d+\. PLAN AMENDMENT REQUIRED$",                                       # R4
    r"^VIOLATION " + LOC + r" \S+ artifact=.*$",                                        # R5
    r"^CONSOLIDATION " + LOC + r" source_parse: .*$",                                   # R6
    r"^CONSOLIDATION " + LOC + r" authority audit CANNOT RUN: .*$",                     # R6
))
R7 = re.compile(r"^CONSOLIDATION " + LOC + r":(?P<line>\d+) .*$")
SUMMARY = re.compile(r"^(\d+) unresolved reader site\(s\) across (\d+) Python file\(s\)$")

CLEAN = (
    ("route", []),
    ("canonical", ["--canonical-reader-audit"]),
    ("consolidation", ["--consolidation-audit"]),
    ("help", ["--help"]),
    ("both_flags", ["--canonical-reader-audit", "--consolidation-audit"]),
    ("missing_plan", ["does-not-exist/plan.yaml"]),
)
PERTURBED = (
    ("canonical", ["--canonical-reader-audit"]),
    ("consolidation", ["--consolidation-audit"]),
)

PROBE_A = """import json


def probe_file(path):
    try:
        with open(path) as handle:
            return json.load(handle)
    except Exception:
        return None


def probe_text(text):
    try:
        return json.loads(text)
    except:
        return None
"""
PROBE_B = """def probe_unparseable(:
    pass
"""


class GitError(Exception):
    pass


def git(*args):
    result = subprocess.run(["git", *args], cwd=CHECKOUT, capture_output=True, text=True)
    if result.returncode:
        raise GitError(f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout


# --- relocation map -------------------------------------------------------------------------

def _target_names(target):
    if isinstance(target, ast.Name):
        return [target.id]
    if isinstance(target, (ast.Tuple, ast.List)):
        return [name for element in target.elts for name in _target_names(element)]
    return []


def _statement_names(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [name for target in node.targets for name in _target_names(target)]
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        return [node.target.id]
    return []


def top_level_names(rev, path):
    """Names a committed source binds at module level; none when it fails to load or parse."""
    try:
        tree = ast.parse(git("show", f"{rev}:{path}"))
    except (GitError, SyntaxError, ValueError):
        return set()
    return {name for node in tree.body for name in _statement_names(node)}


def relocation_map(base, head):
    """ENTRY::NAME -> MODULE::NAME for each name the split moved, sorted by NAME."""
    gone = top_level_names(base, ENTRY) - top_level_names(head, ENTRY)
    moved = {module: top_level_names(head, module) & gone for module in MODULES}
    shared = moved[MODULES[0]] & moved[MODULES[1]]
    owner = {name: module for module, names in moved.items() for name in names - shared}
    return [(name, owner[name]) for name in sorted(owner)]


def apply_map(line, owners):
    """Rewrite only the locator path span of an R1-R6 line naming a moved ENTRY symbol."""
    for pattern in RECOGNIZED:
        match = pattern.match(line)
        if match is None:
            continue
        module = owners.get(match.group("symbol").split(".", 1)[0])
        if match.group("path") != ENTRY or module is None:
            return line
        return line[:match.start("path")] + module + line[match.end("path"):]
    return line


# --- matched trees and runs -----------------------------------------------------------------

def extract(rev, directory, *paths):
    archive = subprocess.Popen(["git", "archive", rev, *paths], cwd=CHECKOUT,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    untar = subprocess.run(["tar", "-x", "-C", directory], stdin=archive.stdout,
                           capture_output=True)
    archive.stdout.close()
    archive_err = archive.stderr.read().decode(errors="replace")
    archive.stderr.close()
    if archive.wait() or untar.returncode:
        raise RuntimeError(f"git archive {rev} | tar -x -C {directory}: "
                           f"{archive_err.strip()} {untar.stderr.decode(errors='replace').strip()}")


def count_py(root):
    total = 0
    for directory, subdirs, files in os.walk(os.path.join(root, BIN)):
        subdirs[:] = [d for d in subdirs if d != "__pycache__"]
        total += sum(1 for name in files if name.endswith(".py"))
    return total


def build_trees(tmp, base, head):
    old, new = os.path.join(tmp, "old"), os.path.join(tmp, "new")
    for root in (old, new):
        os.mkdir(root)
        extract(base, root)
    shutil.rmtree(os.path.join(new, BIN))
    shutil.rmtree(os.path.join(new, "tests"))
    extract(head, new, BIN, "tests")
    return old, new, count_py(new) - count_py(old)


def normalize(text, root):
    return text.replace(os.path.realpath(root), "<ROOT>").replace(root, "<ROOT>").splitlines()


def run_entry(root, argv):
    env = {k: v for k, v in os.environ.items() if k not in SCRUBBED_ENV}
    env.update(PYTHONDONTWRITEBYTECODE="1", HARNESS_PROJECT_DIR=root)
    result = subprocess.run([sys.executable, os.path.join(root, ENTRY), *argv], cwd=root,
                            env=env, capture_output=True, text=True, timeout=50)
    return result.returncode, normalize(result.stdout, root), normalize(result.stderr, root)


def run_pair(old, new, argv):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run_entry, root, argv) for root in (old, new)]
        return [future.result() for future in futures]


def perturb_side(root):
    """Write both probes and blank the relocated row's reason; an error string or None."""
    with open(os.path.join(root, BIN, "zz_split_probe_a.py"), "w") as handle:
        handle.write(PROBE_A)
    with open(os.path.join(root, BIN, "zz_split_probe_b.py"), "w") as handle:
        handle.write(PROBE_B)
    path = os.path.join(root, CLASSIFICATION)
    with open(path) as handle:
        document = json.load(handle)
    rows = [row for row in document["rows"] if str(row.get("id", "")).endswith(RELOCATED_ROW)]
    if len(rows) != 1:
        return f"{len(rows)} rows end with {RELOCATED_ROW}"
    rows[0]["reason"] = ""
    with open(path, "w") as handle:
        handle.write(json.dumps(document, indent=2) + "\n")
    return None


def perturb(trees):
    errors = []
    for side, root in (("old", trees[0]), ("new", trees[1])):
        try:
            error = perturb_side(root)
        except Exception as exc:  # each side's setup failure becomes both checks' FAIL
            error = f"{type(exc).__name__}: {exc}"
        if error:
            errors.append(f"{side} side: {error}")
    return "; ".join(errors) or None


# --- comparison -----------------------------------------------------------------------------

def unmodelled_locators(lines):
    return [line for line in lines
            if (m := R7.match(line)) and m.group("path").endswith(SPLIT_FILES)]


def summary_counts(old_last, new_last, delta):
    old_sum, new_sum = SUMMARY.match(old_last), SUMMARY.match(new_last)
    if not (old_sum and new_sum):
        return "last stdout line is not the canonical summary"
    files_added = int(new_sum.group(2)) - int(old_sum.group(2))
    if old_sum.group(1) != new_sum.group(1) or files_added != delta:
        return f"summary delta is not D={delta}"
    return None


def summary_mismatch(mapped_out, new_out, delta):
    if not (mapped_out and new_out):
        return "canonical stdout is empty"
    if mapped_out[:-1] != new_out[:-1]:
        return "stdout differs after mapping"
    return summary_counts(mapped_out[-1], new_out[-1], delta)


def stdout_mismatch(label, mapped_out, new_out, delta):
    if label.endswith(":canonical"):
        return summary_mismatch(mapped_out, new_out, delta)
    return None if mapped_out == new_out else "stdout differs after mapping"


def run_reasons(label, old_run, new_run):
    """Emptiness, probe, exit, stderr and unmodelled-locator reasons."""
    (old_exit, old_out, old_err), (new_exit, new_out, new_err) = old_run, new_run
    reasons = [f"unmodelled line-numbered locator: {line}"
               for line in unmodelled_locators(old_out + new_out)]
    if not (old_out or old_err):
        reasons.append("old run printed nothing")
    if label.startswith("perturbed:") and old_exit == 0:
        reasons.append("old perturbed run exited 0")
    if old_exit != new_exit:
        reasons.append(f"exit {old_exit} != {new_exit}")
    if old_err != new_err:
        reasons.append("stderr differs")
    return reasons


def sample_reasons(label, old_out, owners, mapped):
    """perturbed:canonical must sample the relocated-row finding and, under a map, rewrite it."""
    if label != "perturbed:canonical":
        return []
    reasons = []
    if not any(RELOCATED_FINDING in line for line in old_out):
        reasons.append("relocated-row finding not sampled")
    if owners and mapped < 1:
        reasons.append("map rewrote no line")
    return reasons


def compare(label, old_run, new_run, owners, delta):
    """Reasons the pair is not equivalent, and the mapped line count (stderr is never mapped)."""
    old_out, new_out = old_run[1], new_run[1]
    mapped_out = [apply_map(line, owners) for line in old_out]
    mapped = sum(a != b for a, b in zip(old_out, mapped_out))
    reasons = run_reasons(label, old_run, new_run) + sample_reasons(label, old_out, owners, mapped)
    reasons.append(stdout_mismatch(label, mapped_out, new_out, delta))
    return [reason for reason in reasons if reason], mapped


def print_block(title, lines):
    print(f"--- {title}")
    for line in lines:
        print(f"| {line}")


def cli_check(label, argv, trees, owners, delta):
    old_run, new_run = run_pair(trees[0], trees[1], argv)
    reasons, mapped = compare(label, old_run, new_run, owners, delta)
    print(f"CLI {label} argv={argv!r} old_exit={old_run[0]} new_exit={new_run[0]} mapped={mapped}")
    print_block("old stdout", old_run[1])
    print_block("old stderr", old_run[2])
    print_block("diff stdout", difflib.unified_diff(old_run[1], new_run[1], "old", "new", lineterm=""))
    print_block("diff stderr", difflib.unified_diff(old_run[2], new_run[2], "old", "new", lineterm=""))
    return "; ".join(reasons) or None


def projection_confined(changed):
    others = [path for path in changed
              if not path.startswith(OVERLAID + (FEATURE_DIR,))]
    return f"outside the projection: {', '.join(others)}" if others else None


# --- driver ---------------------------------------------------------------------------------

def run_check(name, check, failures):
    try:
        detail = check()
    except Exception as exc:  # a check's own exception is that check's FAIL, never a traceback
        detail = f"{type(exc).__name__}: {exc}"
    if detail:
        failures.append(name)
        print(f"FAIL {name} {detail}")
    else:
        print(f"PASS {name}")


def print_header(base, head, changed, entries):
    print(f"BASE {base}")
    print(f"HEAD {head}")
    for side, rev in (("base", base), ("head", head)):
        for path in (BIN, "tests"):
            print(f"TREE {side} {path} {git('rev-parse', f'{rev}:{path}').strip()}")
    for path in changed:
        print(f"PROJECTED {path} {'overlaid' if path.startswith(OVERLAID) else 'excluded'}")
    for name, module in entries:
        print(f"MAP {ENTRY}::{name} -> {module}::{name}")
    if not entries:
        print("MAP none")


def cli_checks(state, cases, setup, owners, failures):
    """Run one state's comparisons; setup() yields (trees, delta) or raises its error."""
    def check(label, argv):
        trees, delta = setup()
        return cli_check(f"{state}:{label}", argv, trees, owners, delta)

    for label, argv in cases:
        run_check(f"cli_equivalent[{state}:{label}]",
                  lambda: check(label, argv), failures)


class MatchedTrees:
    """OLD and NEW, built once and perturbed once; a setup error is raised into every comparison."""

    def __init__(self, tmp, base, head):
        self.tmp, self.base, self.head = tmp, base, head
        self.built = None
        self.perturb_error = None
        self.perturbed_done = False

    def clean(self):
        if self.built is None:
            try:
                self.built = build_trees(self.tmp, self.base, self.head)
            except Exception as exc:  # recorded once, raised into every comparison
                self.built = exc
        if isinstance(self.built, Exception):
            raise self.built
        old, new, delta = self.built
        return (old, new), delta

    def perturbed(self):
        pair, delta = self.clean()
        if not self.perturbed_done:
            self.perturb_error, self.perturbed_done = perturb(pair), True
        if self.perturb_error:
            raise RuntimeError(self.perturb_error)
        return pair, delta


def run_all(base, head, changed, owners, failures):
    run_check("projection_confined", lambda: projection_confined(changed), failures)
    with tempfile.TemporaryDirectory() as tmp:
        trees = MatchedTrees(tmp, base, head)
        cli_checks("clean", CLEAN, trees.clean, owners, failures)
        cli_checks("perturbed", PERTURBED, trees.perturbed, owners, failures)


def resolve(rev):
    return git("rev-parse", "--verify", "--end-of-options", f"{rev}^{{commit}}").strip()


def parse_revs(argv):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args(argv)
    base = resolve(args.base or git("merge-base", "HEAD", "main").strip())
    return base, resolve(args.head)


def execute(base, head):
    """Header and the nine checks; the names of the checks that failed."""
    failures = []
    try:
        changed = git("diff", "--name-only", base, head).splitlines()
        entries = relocation_map(base, head)
        print_header(base, head, changed, entries)
        run_all(base, head, changed, dict(entries), failures)
    except Exception as exc:  # past resolution the script exits only 0 or 1, never a traceback
        print(f"ERROR {type(exc).__name__}: {exc}")
        failures.append("setup")
    return failures


def main(argv):
    try:
        base, head = parse_revs(argv)
    except GitError as error:
        print(f"split-equivalence: {error}", file=sys.stderr)
        return 2
    failures = execute(base, head)
    if failures:
        print(f"{len(failures)} FAILURE(S): {', '.join(failures)}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
