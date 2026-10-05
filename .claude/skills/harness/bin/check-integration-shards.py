#!/usr/bin/env python3
"""Aggregate sharded integration evidence into the single required `integration` verdict.

FEAT-2081 T-02 (SC-02/SC-03). The workflow's aggregation job passes the GitHub `needs`
results of the checks job and the shard matrix, the tested commit, and a directory holding
the downloaded shard manifests written by `run-unit-tests.py --shard i/n --manifest PATH`.
Expected coverage is discovered independently from the tested commit's git tree
(`git ls-tree -r --name-only SHA`), never from the duration table, the manifests'
selections, the working tree, or the partition function. A completed record is the only
coverage evidence.

Exit 0 only on exact success; 1 when valid evidence shows an incomplete or failed
execution; 2 for an unusable invocation or malformed evidence.
"""
import contextlib as _bootstrap_contextlib
import io as _bootstrap_io
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys

_bootstrap_bin = _bootstrap_os.path.dirname(
    _bootstrap_os.path.abspath(__file__))
_bootstrap_original_path = list(_bootstrap_sys.path)
_bootstrap_pythonpath = {
    _bootstrap_os.path.realpath(entry)
    for entry in (_bootstrap_os.environ.get("PYTHONPATH") or "").split(
        _bootstrap_os.pathsep)
    if entry
}
_bootstrap_user_sites = _bootstrap_site.getusersitepackages()
if isinstance(_bootstrap_user_sites, str):
    _bootstrap_user_sites = [_bootstrap_user_sites]
_bootstrap_unsafe = _bootstrap_pythonpath | {
    _bootstrap_os.path.realpath(_bootstrap_bin),
    _bootstrap_os.path.realpath(_bootstrap_os.getcwd()),
    *(_bootstrap_os.path.realpath(entry) for entry in _bootstrap_user_sites),
}
_bootstrap_sys.path[:] = [
    entry for entry in _bootstrap_sys.path
    if entry and _bootstrap_os.path.realpath(entry) not in _bootstrap_unsafe
]


# ACCEPTED DUPLICATION (FEAT-61 D-09, DEC-234). This prologue is copied, not shared, in
# branch-create-gate.py, gh-close-gate.py, merge-gate.py, plan-sign-gate.py: it runs BEFORE the
# trusted bin path is on sys.path, so no helper can be imported to hold it — the code below IS
# what creates the import seam. Change all five together; never replace one with an import.
def _resolve_root():
    """Resolve through the trusted sibling with isolated import semantics."""
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        with _bootstrap_contextlib.redirect_stderr(_bootstrap_io.StringIO()):
            import harness_boundary
            return harness_boundary.resolve_root(_bootstrap_bin)
    except (ModuleNotFoundError, ValueError):
        # FEAT-64: the module did not import (a missing first-party sibling), or resolve_root
        # refused (strict: no MARKER anywhere) -- the two shapes "no root" takes, matching
        # check-state.py's copy. The four gate copies narrow the same way in FEAT-65.
        return ""


ROOT = _resolve_root()
if not ROOT or not _bootstrap_os.path.isdir(ROOT):
    print(
        f"check-integration-shards.py: no harness root could be resolved from "
        f"{_bootstrap_bin} — refusing to run",
        file=_bootstrap_sys.stderr,
    )
    raise SystemExit(2)

import argparse
from collections import Counter
import json
import os
import posixpath
import re
import subprocess
import sys

RESULTS = ("success", "failure", "skipped", "cancelled", "missing")
KIND = "integration"
EXPECTED_PATH = re.compile(r"tests/integration/test-[^/]*\.py")
OBJECT_ID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
INCOMPLETE, MALFORMED = 1, 2


class Malformed:
    """A manifest file whose bytes could not be decoded as JSON."""

    def __init__(self, error):
        self.error = error


def exit_status(defects):
    return max((status for status, _message in defects), default=0)


def _conclusion_defect(field, value):
    if value is None:
        return [(MALFORMED, f"{field}-result was not supplied")]
    if value not in RESULTS:
        return [(MALFORMED, f"{field}-result {value!r} is not one of {', '.join(RESULTS)}")]
    if value != "success":
        return [(INCOMPLETE, f"{field}-result is {value}, not success")]
    return []


def conclusion_defects(checks, matrix):
    """Both upstream needs results must be exactly success; nothing defaults to success."""
    return _conclusion_defect("checks", checks) + _conclusion_defect("matrix", matrix)


def integration_paths(names):
    return sorted(name for name in names if EXPECTED_PATH.fullmatch(name))


def _is_normalized(path):
    return (isinstance(path, str) and path != "" and not path.startswith("/")
            and "\\" not in path and posixpath.normpath(path) == path
            and ".." not in path.split("/"))


def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _completed_shape(name, records):
    if not isinstance(records, list):
        return [f"{name}: completed_files must be a list"]
    problems = []
    for record in records:
        if not isinstance(record, dict):
            problems.append(f"{name}: completed record {record!r} must be an object")
            continue
        if not _is_normalized(record.get("path")):
            problems.append(f"{name}: completed path {record.get('path')!r} is "
                            "not a normalized repository-relative path")
        if not _is_int(record.get("returncode")):
            problems.append(f"{name}: completed {record.get('path')!r} returncode must be an integer")
    return problems


def _selected_shape(name, selected):
    if not isinstance(selected, list):
        return [f"{name}: selected_files must be a list"]
    return [f"{name}: selected path {path!r} is not a normalized repository-relative path"
            for path in selected if not _is_normalized(path)]


def _identity_shape(name, doc):
    problems = []
    if doc.get("schema") != 1:
        problems.append(f"{name}: schema must be 1, got {doc.get('schema')!r}")
    for field in ("shard_index", "shard_count", "runner_exit"):
        if not _is_int(doc.get(field)):
            problems.append(f"{name}: {field} must be an integer, got {doc.get(field)!r}")
    for field in ("tested_commit", "kind"):
        if not isinstance(doc.get(field), str):
            problems.append(f"{name}: {field} must be a string, got {doc.get(field)!r}")
    return problems


def _shape_defects(name, doc):
    if isinstance(doc, Malformed):
        return [f"{name}: malformed JSON: {doc.error}"]
    if not isinstance(doc, dict):
        return [f"{name}: manifest must be a JSON object"]
    return (_identity_shape(name, doc) + _selected_shape(name, doc.get("selected_files"))
            + _completed_shape(name, doc.get("completed_files")))


def _identity_defects(name, doc, tested_commit, shards):
    problems = []
    if doc["tested_commit"] != tested_commit:
        problems.append(f"{name}: tested_commit {doc['tested_commit']} is not the supplied {tested_commit}")
    if doc["kind"] != KIND:
        problems.append(f"{name}: kind {doc['kind']!r} is not {KIND}")
    if doc["shard_count"] != shards:
        problems.append(f"{name}: shard_count {doc['shard_count']} is not {shards}")
    if not 1 <= doc["shard_index"] <= shards:
        problems.append(f"{name}: shard_index {doc['shard_index']} outside 1..{shards} (extra manifest)")
    return problems


def _shard_set_defects(manifests, shards):
    counts = Counter(doc["shard_index"] for _name, doc in manifests)
    problems = [f"no manifest for shard {index}" for index in range(1, shards + 1)
                if counts[index] == 0]
    problems += [f"shard {index} has {count} manifests"
                 for index, count in sorted(counts.items()) if count > 1]
    return problems


def _record_defects(name, doc):
    index = doc["shard_index"]
    selected = Counter(doc["selected_files"])
    completed = Counter(record["path"] for record in doc["completed_files"])
    problems = [] if doc["runner_exit"] == 0 else [f"{name}: runner_exit {doc['runner_exit']}"]
    problems += [f"{name}: {record['path']} returned {record['returncode']}"
                 for record in doc["completed_files"] if record["returncode"] != 0]
    problems += [f"{name}: {path} duplicated within shard {index}"
                 for path, count in sorted((selected | completed).items()) if count > 1]
    problems += [f"{name}: {path} selected but has no completed record"
                 for path in sorted(selected - completed)]
    problems += [f"{name}: {path} completed but not selected"
                 for path in sorted(completed - selected)]
    return problems


def coverage_defects(manifests, expected):
    """Every expected path completed exactly once across all shards; nothing else completed."""
    if not expected:
        return [f"tested commit has no tests/integration/test-*.py files to cover"]
    completed = Counter(record["path"] for _name, doc in manifests
                        for record in doc["completed_files"])
    problems = []
    for path in expected:
        if completed[path] == 0:
            problems.append(f"{path}: omitted (no completed record in any shard)")
        elif completed[path] > 1:
            problems.append(f"{path}: completed {completed[path]} times across shards")
    problems += [f"{path}: unexpected (not in the tested commit's integration suite)"
                 for path in sorted(set(completed) - set(expected))]
    return problems


def evidence_defects(docs, tested_commit, shards, expected):
    """Validate named manifest documents against the independently discovered expected list."""
    defects, manifests = [], []
    for name in sorted(docs):
        problems = _shape_defects(name, docs[name])
        defects += [(MALFORMED, problem) for problem in problems]
        if not problems:
            manifests.append((name, docs[name]))
    incomplete = _shard_set_defects(manifests, shards)
    for name, doc in manifests:
        incomplete += _identity_defects(name, doc, tested_commit, shards)
        incomplete += _record_defects(name, doc)
    incomplete += coverage_defects(manifests, expected)
    return defects + [(INCOMPLETE, problem) for problem in incomplete]


def discover_expected(root, tested_commit):
    """The tested commit's own top-level tests/integration/test-*.py files."""
    proc = subprocess.run(
        ["git", "-C", root, "ls-tree", "-r", "-z", "--full-tree", "--name-only", tested_commit],
        capture_output=True, text=True)
    if proc.returncode != 0:
        return None, (MALFORMED, f"cannot list tested commit {tested_commit}: "
                                 f"{proc.stderr.strip()}")
    return integration_paths(proc.stdout.split("\0")), None


def _read_manifest(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.loads(handle.read())
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return Malformed(str(error))


def load_manifest_dir(directory):
    """Every regular file under the directory is a manifest; none may be ignored."""
    if not os.path.isdir(directory):
        return {}, [(MALFORMED, f"--manifest-dir {directory} is not a directory")]
    docs = {}
    for current, dirs, files in os.walk(directory):
        dirs.sort()
        for filename in sorted(files):
            absolute = os.path.join(current, filename)
            docs[os.path.relpath(absolute, directory).replace(os.sep, "/")] = _read_manifest(absolute)
    return docs, []


def _parse(argv):
    parser = argparse.ArgumentParser(prog="check-integration-shards.py", add_help=False)
    for option in ("--commit", "--shards", "--checks-result", "--matrix-result", "--manifest-dir"):
        parser.add_argument(option)
    opts, unknown = parser.parse_known_args(argv)
    problems = [f"unrecognized argument {arg!r}" for arg in unknown]
    for option, value in (("--commit", opts.commit), ("--manifest-dir", opts.manifest_dir)):
        if value is None:
            problems.append(f"{option} was not supplied")
    if opts.commit is not None and not OBJECT_ID.fullmatch(opts.commit):
        problems.append(f"--commit must be a full hexadecimal object id, got {opts.commit!r}")
    if opts.shards is None or not re.fullmatch(r"[1-9][0-9]*", opts.shards):
        problems.append(f"--shards must be a positive integer, got {opts.shards!r}")
    return opts, [(MALFORMED, problem) for problem in problems]


def _validate(opts):
    defects = conclusion_defects(opts.checks_result, opts.matrix_result)
    expected, discovery = discover_expected(ROOT, opts.commit)
    if discovery:
        return defects + [discovery], None
    docs, load_defects = load_manifest_dir(opts.manifest_dir)
    defects += load_defects
    if not load_defects:
        defects += evidence_defects(docs, opts.commit, int(opts.shards), expected)
    return defects, expected


def _report(defects, expected, opts):
    for status, message in defects:
        print(f"{'MALFORMED' if status == MALFORMED else 'INCOMPLETE'}: {message}")
    status = exit_status(defects)
    if status == 0:
        print(f"PASS integration: {len(expected)} expected files completed exactly once "
              f"across {opts.shards} shards at {opts.commit}")
    else:
        print(f"FAIL integration: {len(defects)} defect(s), exit {status}")
    return status


def main(argv=None):
    opts, defects = _parse(sys.argv[1:] if argv is None else argv)
    expected = None
    if not defects:
        defects, expected = _validate(opts)
    else:
        defects = conclusion_defects(opts.checks_result, opts.matrix_result) + defects
    return _report(defects, expected, opts)


if __name__ == "__main__":
    sys.exit(main())
