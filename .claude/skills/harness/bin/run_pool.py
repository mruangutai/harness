#!/usr/bin/env python3
"""Run Python test files concurrently with attributed output."""

import argparse
import concurrent.futures
import os
import subprocess
import sys
import time


def worker_count(explicit):
    if explicit is not None:
        if explicit <= 0:
            raise ValueError("--workers must be a positive integer")
        return explicit
    raw = os.environ.get("HARNESS_TEST_WORKERS")
    if raw is not None:
        try:
            value = int(raw)
        except ValueError:
            raise ValueError("HARNESS_TEST_WORKERS must be a positive integer") from None
        if value <= 0:
            raise ValueError("HARNESS_TEST_WORKERS must be a positive integer")
        return value
    return min(8, max(2, os.cpu_count() or 2))


def _record(state, root, path):
    try:
        entry = os.lstat(path)
    except OSError:
        return
    state[os.path.relpath(path, root)] = (entry.st_mode, entry.st_size, entry.st_mtime_ns)


def _snapshot_directory(state, root, current, dirs, files):
    descend = []
    for name in dirs:
        if name == "__pycache__":
            continue
        path = os.path.join(current, name)
        if os.path.islink(path):
            _record(state, root, path)
        else:
            descend.append(name)
    dirs[:] = descend
    for name in files:
        _record(state, root, os.path.join(current, name))


def snapshot(root):
    state = {}
    for current, dirs, files in os.walk(root):
        _snapshot_directory(state, root, current, dirs, files)
    return state


def run_one(path):
    started = time.monotonic()
    proc = subprocess.run([sys.executable, path], stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    return path, proc.returncode, proc.stdout, time.monotonic() - started


def _parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int)
    parser.add_argument("--mutation-check")
    parser.add_argument("scripts", nargs="+")
    args = parser.parse_args(argv)
    if args.scripts and args.scripts[0] == "--":
        args.scripts = args.scripts[1:]
    if not args.scripts:
        parser.error("at least one test path is required")
    return args


def _resolve_workers(explicit):
    try:
        return worker_count(explicit)
    except ValueError as exc:
        print(f"run_pool.py: ERROR: {exc}", file=sys.stderr)
        return None


def _mutation_baseline(value):
    if not value:
        return None, None, None
    root = os.path.abspath(value)
    if not os.path.isdir(root):
        return root, None, f"mutation-check directory is missing: {root}"
    before = snapshot(root)
    if not before:
        return root, None, f"mutation-check measured no files under {root}"
    return root, before, None


def _emit_result(result):
    path, rc, output, seconds = result
    name = os.path.basename(path)
    print(f"----- {name} (exit {rc}, {seconds:.2f}s) -----")
    if output:
        print(output, end="" if output.endswith("\n") else "\n")
    print(f"{'PASS' if rc == 0 else 'FAIL'} {name}")


def _run_scripts(scripts, workers):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_one, path) for path in scripts]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            _emit_result(result)
    return results


def _mutation_changes(root, before):
    if before is None:
        return []
    after = snapshot(root)
    mutated = sorted(name for name in before.keys() | after.keys()
                     if before.get(name) != after.get(name))
    for name in mutated:
        print(f"MUTATED {name}")
    if mutated:
        print("A file under the watched directory changed while the suite ran; this violates REQ-01. A concurrent hand edit or agent edit is indistinguishable.")
    return mutated


def _print_summary(results, workers, wall):
    print(f"pool: {workers} workers, {len(results)} files, {wall:.2f}s wall")
    slowest = sorted(results, key=lambda item: item[3], reverse=True)[:3]
    print("slowest: " + ", ".join(
        f"{os.path.basename(path)} {seconds:.2f}s" for path, _rc, _out, seconds in slowest))


def main(argv=None):
    args = _parse_args(argv)
    workers = _resolve_workers(args.workers)
    if workers is None:
        return 2
    root, before, error = _mutation_baseline(args.mutation_check)
    if error:
        print(f"run_pool.py: ERROR: {error}", file=sys.stderr)
        return 2
    started = time.monotonic()
    results = _run_scripts(args.scripts, workers)
    mutated = _mutation_changes(root, before)
    _print_summary(results, workers, time.monotonic() - started)
    failed = mutated or any(rc != 0 for _path, rc, _out, _seconds in results)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
