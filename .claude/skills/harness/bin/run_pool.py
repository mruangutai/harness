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


def snapshot(root):
    state = {}
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in files:
            if name.endswith(".pyc"):
                continue
            path = os.path.join(current, name)
            try:
                stat = os.stat(path)
            except OSError:
                continue
            state[os.path.relpath(path, root)] = (stat.st_size, stat.st_mtime_ns)
    return state


def run_one(path):
    started = time.monotonic()
    proc = subprocess.run([sys.executable, path], stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, text=True)
    return path, proc.returncode, proc.stdout, time.monotonic() - started


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int)
    parser.add_argument("--mutation-check")
    parser.add_argument("scripts", nargs="+")
    args = parser.parse_args(argv)
    if args.scripts and args.scripts[0] == "--":
        args.scripts = args.scripts[1:]
    if not args.scripts:
        parser.error("at least one test path is required")
    try:
        workers = worker_count(args.workers)
    except ValueError as exc:
        print(f"run_pool.py: ERROR: {exc}", file=sys.stderr)
        return 2
    before = None
    if args.mutation_check:
        root = os.path.abspath(args.mutation_check)
        if not os.path.isdir(root):
            print(f"run_pool.py: ERROR: mutation-check directory is missing: {root}", file=sys.stderr)
            return 2
        before = snapshot(root)
        if not before:
            print(f"run_pool.py: ERROR: mutation-check measured no files under {root}", file=sys.stderr)
            return 2
    started = time.monotonic()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(run_one, path) for path in args.scripts]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            path, rc, output, seconds = result
            name = os.path.basename(path)
            print(f"----- {name} (exit {rc}, {seconds:.2f}s) -----")
            if output:
                print(output, end="" if output.endswith("\n") else "\n")
            print(f"{'PASS' if rc == 0 else 'FAIL'} {name}")
    mutated = []
    if before is not None:
        after = snapshot(root)
        mutated = sorted(name for name in before.keys() | after.keys()
                         if before.get(name) != after.get(name))
        for name in mutated:
            print(f"MUTATED {name}")
        if mutated:
            print("A file under the watched directory changed while the suite ran; this violates REQ-01. A concurrent hand edit or agent edit is indistinguishable.")
    wall = time.monotonic() - started
    print(f"pool: {workers} workers, {len(results)} files, {wall:.2f}s wall")
    slowest = sorted(results, key=lambda item: item[3], reverse=True)[:3]
    print("slowest: " + ", ".join(f"{os.path.basename(p)} {s:.2f}s" for p, _r, _o, s in slowest))
    return 1 if mutated or any(rc != 0 for _p, rc, _o, _s in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
