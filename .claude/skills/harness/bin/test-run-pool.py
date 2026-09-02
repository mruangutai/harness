#!/usr/bin/env python3
"""Integration tests for run_pool.py."""

import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.realpath(__file__))
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


def main():
    with tempfile.TemporaryDirectory() as root:
        paths = [script(root, f"t{i}.py", f"import sys; print('OUT{i}'); print('ERR{i}', file=sys.stderr)\n") for i in range(3)]
        result = run(paths, "--workers", "3")
        lines = result.stdout
        attributed = all(lines.index(f"----- t{i}.py") < lines.index(f"OUT{i}") < lines.index(f"PASS t{i}.py") and lines.index(f"ERR{i}") < lines.index(f"PASS t{i}.py") for i in range(3))
        check("captured output stays inside its file block", result.returncode == 0 and attributed, lines)

        bad = script(root, "bad.py", "import sys; print('BADTOKEN'); sys.exit(3)\n")
        result = run(paths + [bad], "--workers", "4")
        failures = [line for line in result.stdout.splitlines() if line.startswith("FAIL ")]
        check("one failure propagates after every file runs", result.returncode == 1 and failures == ["FAIL bad.py"] and "BADTOKEN" in result.stdout and all(f"PASS t{i}.py" in result.stdout for i in range(3)), result.stdout)

        ledger = os.path.join(root, "ledger")
        once = [script(root, f"once{i}.py", f"open({ledger!r}, 'a').write('once{i}\\n')\n") for i in range(8)]
        result = run(once, "--workers", "4")
        entries = open(ledger).read().splitlines()
        check("every file runs exactly once", result.returncode == 0 and len(entries) == 8 and len(set(entries)) == 8, repr(entries))

        for value in ("1", "3"):
            env = dict(os.environ, HARNESS_TEST_WORKERS=value)
            result = run(paths, env=env)
            check(f"environment selects {value} workers", result.returncode == 0 and f"pool: {value} workers, 3 files" in result.stdout, result.stdout)
        for value in ("0", "many"):
            result = run(paths, env=dict(os.environ, HARNESS_TEST_WORKERS=value))
            check(f"invalid worker value {value} is loud", result.returncode == 2 and "HARNESS_TEST_WORKERS" in result.stderr, result.stderr)

        slow = script(root, "slow.py", "import time; time.sleep(.4)\n")
        parallel = run([slow, *paths], "--workers", "4")
        serial = run([slow, *paths], "--workers", "1")
        p_order = [line[5:] for line in parallel.stdout.splitlines() if line.startswith("PASS ")]
        s_order = [line[5:] for line in serial.stdout.splitlines() if line.startswith("PASS ")]
        check("completion order is not input order", p_order != s_order and set(p_order) == set(s_order), repr((p_order, s_order)))

        result = run(paths)
        pool_line = next(line for line in result.stdout.splitlines() if line.startswith("pool: "))
        workers = int(pool_line.split()[1])
        check("default worker count is capped", 2 <= workers <= 8, pool_line)

        watched = os.path.join(root, "watched")
        os.mkdir(watched)
        keep = os.path.join(watched, "keep.txt")
        open(keep, "w").write("x")
        clean = run(paths, "--mutation-check", watched)
        edit = script(root, "edit.py", f"open({keep!r}, 'a').write('y')\n")
        changed = run(paths + [edit], "--mutation-check", watched)
        shell = script(root, "shell.py", f"import subprocess; subprocess.run(['sh','-c','echo y >> {keep}'])\n")
        shelled = run(paths + [shell], "--mutation-check", watched)
        new_path = os.path.join(watched, ".mutant-x.sh")
        create = script(root, "create.py", f"open({new_path!r}, 'w').write('z')\n")
        created = run(paths + [create], "--mutation-check", watched)
        check("mutation check covers clean, direct, subprocess, and creation", clean.returncode == 0 and "MUTATED " not in clean.stdout and changed.returncode == 1 and "MUTATED keep.txt" in changed.stdout and shelled.returncode == 1 and "MUTATED keep.txt" in shelled.stdout and created.returncode == 1 and "MUTATED .mutant-x.sh" in created.stdout)
        empty = tempfile.mkdtemp()
        missing = run(paths, "--mutation-check", empty + "-missing")
        empty_result = run(paths, "--mutation-check", empty)
        check("empty and missing watched directories refuse", empty_result.returncode == 2 and missing.returncode == 2)
    print(f"\n{len(FAILURES)} failed")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    raise SystemExit(main())
