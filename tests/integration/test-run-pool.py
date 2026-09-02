#!/usr/bin/env python3
"""Integration tests for run_pool.py."""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import os
import subprocess
import sys
import tempfile

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
BIN_DIR = os.path.join(ROOT, ".claude", "skills", "harness", "bin")
HERE = BIN_DIR
POOL = os.path.join(HERE, "run_pool.py")
FAILURES = []


def check(name, ok, detail=""):
    print(f"{'ok' if ok else 'FAIL'}    {name}")
    if not ok:
        FAILURES.append(name)
        if detail:
            print("      " + detail)


def run(paths, *options, env=None):
    return subprocess.run([sys.executable, POOL, *options, "--", *paths],
                          capture_output=True, text=True, env=env)


def script(root, name, body):
    path = os.path.join(root, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(body)
    return path


def base_scripts(root):
    return [script(root, f"t{i}.py",
                   f"import sys; print('OUT{i}'); print('ERR{i}', file=sys.stderr)\n")
            for i in range(3)]


def case_attribution(paths):
    result = run(paths, "--workers", "3")
    output = result.stdout
    attributed = all(output.index(f"----- t{i}.py") < output.index(f"OUT{i}")
                     < output.index(f"PASS t{i}.py")
                     and output.index(f"ERR{i}") < output.index(f"PASS t{i}.py")
                     for i in range(3))
    check("captured output stays inside its file block",
          result.returncode == 0 and attributed, output)


def case_failure(root, paths):
    bad = script(root, "bad.py", "import sys; print('BADTOKEN'); sys.exit(3)\n")
    result = run(paths + [bad], "--workers", "4")
    failures = [line for line in result.stdout.splitlines() if line.startswith("FAIL ")]
    all_passed = all(f"PASS t{i}.py" in result.stdout for i in range(3))
    check("one failure propagates after every file runs",
          result.returncode == 1 and failures == ["FAIL bad.py"]
          and "BADTOKEN" in result.stdout and all_passed, result.stdout)


def case_exactly_once(root):
    ledger = os.path.join(root, "ledger")
    paths = [script(root, f"once{i}.py", f"open({ledger!r}, 'a').write('once{i}\\n')\n")
             for i in range(8)]
    result = run(paths, "--workers", "4")
    with open(ledger, encoding="utf-8") as handle:
        entries = handle.read().splitlines()
    check("every file runs exactly once",
          result.returncode == 0 and len(entries) == 8 and len(set(entries)) == 8,
          repr(entries))


def case_worker_selection(paths):
    for value in ("1", "3"):
        result = run(paths, env=dict(os.environ, HARNESS_TEST_WORKERS=value))
        check(f"environment selects {value} workers",
              result.returncode == 0 and f"pool: {value} workers, 3 files" in result.stdout,
              result.stdout)
    for value in ("0", "many"):
        result = run(paths, env=dict(os.environ, HARNESS_TEST_WORKERS=value))
        check(f"invalid worker value {value} is loud",
              result.returncode == 2 and "HARNESS_TEST_WORKERS" in result.stderr,
              result.stderr)


def case_completion_order(root, paths):
    slow = script(root, "slow.py", "import time; time.sleep(.4)\n")
    parallel = run([slow, *paths], "--workers", "4")
    serial = run([slow, *paths], "--workers", "1")
    p_order = [line[5:] for line in parallel.stdout.splitlines() if line.startswith("PASS ")]
    s_order = [line[5:] for line in serial.stdout.splitlines() if line.startswith("PASS ")]
    check("completion order is not input order",
          p_order != s_order and set(p_order) == set(s_order), repr((p_order, s_order)))


def case_default_cap(paths):
    result = run(paths)
    pool_line = next(line for line in result.stdout.splitlines() if line.startswith("pool: "))
    workers = int(pool_line.split()[1])
    check("default worker count is capped", 2 <= workers <= 8, pool_line)


def watched_fixture(root):
    watched = os.path.join(root, "watched")
    os.mkdir(watched)
    keep = os.path.join(watched, "keep.txt")
    with open(keep, "w", encoding="utf-8") as handle:
        handle.write("x")
    return watched, keep


def case_file_mutations(root, paths, watched, keep):
    clean = run(paths, "--mutation-check", watched)
    edit = script(root, "edit.py", f"open({keep!r}, 'a').write('y')\n")
    changed = run(paths + [edit], "--mutation-check", watched)
    shell = script(root, "shell.py",
                   f"import subprocess; subprocess.run(['sh','-c','echo y >> {keep}'])\n")
    shelled = run(paths + [shell], "--mutation-check", watched)
    created_path = os.path.join(watched, ".mutant-x.sh")
    create = script(root, "create.py", f"open({created_path!r}, 'w').write('z')\n")
    created = run(paths + [create], "--mutation-check", watched)
    ok = (clean.returncode == 0 and "MUTATED " not in clean.stdout
          and changed.returncode == 1 and "MUTATED keep.txt" in changed.stdout
          and shelled.returncode == 1 and "MUTATED keep.txt" in shelled.stdout
          and created.returncode == 1 and "MUTATED .mutant-x.sh" in created.stdout)
    check("mutation check covers clean, direct, subprocess, and creation", ok)


def case_symlinks(root, paths, watched):
    dangling_path = os.path.join(watched, "dangling")
    dangling_script = script(root, "dangling.py",
                             f"import os; os.symlink('missing', {dangling_path!r})\n")
    dangling = run(paths + [dangling_script], "--mutation-check", watched)
    directory_path = os.path.join(watched, "linked-dir")
    directory_script = script(
        root, "linked_dir.py",
        f"import os; os.symlink({root!r}, {directory_path!r}, target_is_directory=True)\n")
    directory = run(paths + [directory_script], "--mutation-check", watched)
    ok = (dangling.returncode == 1 and "MUTATED dangling" in dangling.stdout
          and directory.returncode == 1 and "MUTATED linked-dir" in directory.stdout)
    check("mutation check catches dangling and directory symlinks", ok,
          dangling.stdout + directory.stdout)


def case_cache_exclusion(root, paths, watched):
    cache = os.path.join(watched, "__pycache__")
    loose = os.path.join(watched, "loose.pyc")
    cache_script = script(root, "cache.py",
                          f"import os; os.makedirs({cache!r}); open(os.path.join({cache!r},'x.pyc'),'w').write('x')\n")
    cache_result = run(paths + [cache_script], "--mutation-check", watched)
    loose_script = script(root, "loose.py",
                          f"open({loose!r}, 'w').write('x')\n")
    loose_result = run(paths + [loose_script], "--mutation-check", watched)
    ok = (cache_result.returncode == 0 and "MUTATED " not in cache_result.stdout
          and loose_result.returncode == 1 and "MUTATED loose.pyc" in loose_result.stdout)
    check("only __pycache__ bytecode is excluded", ok,
          cache_result.stdout + loose_result.stdout)


def case_invalid_watch(paths, root):
    empty = tempfile.mkdtemp(dir=root)
    missing = run(paths, "--mutation-check", empty + "-missing")
    empty_result = run(paths, "--mutation-check", empty)
    check("empty and missing watched directories refuse",
          empty_result.returncode == 2 and missing.returncode == 2)


def main():
    with tempfile.TemporaryDirectory() as root:
        paths = base_scripts(root)
        case_attribution(paths)
        case_failure(root, paths)
        case_exactly_once(root)
        case_worker_selection(paths)
        case_completion_order(root, paths)
        case_default_cap(paths)
        watched, keep = watched_fixture(root)
        case_file_mutations(root, paths, watched, keep)
        case_symlinks(root, paths, watched)
        case_cache_exclusion(root, paths, watched)
        case_invalid_watch(paths, root)
    print(f"\n{len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
