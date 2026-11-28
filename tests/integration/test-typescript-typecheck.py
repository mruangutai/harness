#!/usr/bin/env python3
"""FEAT-2257 — the pinned TypeScript typecheck against the REAL compiler.

Covers what a green `bun run typecheck` alone cannot show:
  1. coverage: every git-tracked .ts file is in the compiler's own file list, so a tsconfig that
     silently drops a source (a dot-directory, a new test) fails here;
  2. no suppression: no tracked source silences the checker with @ts-nocheck / @ts-ignore /
     @ts-expect-error;
  3. discrimination: a copy of the checked tree with one deliberate type error fails the same
     command, naming the poisoned file, so the gate cannot pass vacuously;
  4. activation: `test_kinds.typecheck` is active with exactly the command run here.

Every failure exits nonzero; a missing toolchain or a timeout fails, never skips. The real
checkout is never modified: the poison goes into a temporary copy outside it.
"""
from integration_support import ROOT as _ROOT
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

from check_support import Checks  # noqa: E402

ROOT = str(_ROOT)
COMMAND = ["bun", "run", "typecheck"]
SETTLED = (".omp/extensions/harness-hooks.ts",
           "tests/unit/omp-hooks.test.ts", "tests/manual/probe-session-accessors.ts")
POISONED = ".omp/extensions/harness-hooks.ts"
SUPPRESSIONS = ("@ts-nocheck", "@ts-ignore", "@ts-expect-error")
DEADLINE = time.monotonic() + 40
C = Checks()
check = C.check


def run(argv, cwd):
    """Run with the shared deadline; a timeout is a failure (TimeoutExpired propagates)."""
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                          timeout=max(0.1, DEADLINE - time.monotonic()))


def tracked_sources():
    listed = run(["git", "ls-files", "-z", "--", "*.ts"], ROOT)
    if listed.returncode != 0:
        raise SystemExit(f"FAIL git ls-files: {listed.stderr}")
    return sorted(p for p in listed.stdout.split("\0") if p)


def compiler_files(cwd):
    tsc = os.path.join(cwd, "node_modules", ".bin", "tsc")
    if not os.path.exists(tsc):
        raise SystemExit(f"FAIL no installed compiler at {tsc}: run bun install --frozen-lockfile")
    listed = run([tsc, "--noEmit", "-p", "tsconfig.json", "--listFilesOnly"], cwd)
    if listed.returncode != 0:
        raise SystemExit(f"FAIL tsc --listFilesOnly rc={listed.returncode}: {listed.stdout}{listed.stderr}")
    return {os.path.realpath(line.strip()) for line in listed.stdout.splitlines() if line.strip()}


def check_coverage(sources):
    check("tracked .ts discovery is non-empty", bool(sources), repr(sources))
    missing = [p for p in SETTLED if p not in sources]
    check("the settled sources are tracked", not missing, repr(missing))
    listed = compiler_files(ROOT)
    uncovered = [p for p in sources if os.path.realpath(os.path.join(ROOT, p)) not in listed]
    check("every tracked .ts is in the compiler's file list", not uncovered, repr(uncovered))


def check_no_suppression(sources):
    found = []
    for rel in sources:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as handle:
            for number, line in enumerate(handle, 1):
                found += [f"{rel}:{number}: {word}" for word in SUPPRESSIONS if word in line]
    check("no tracked source suppresses the compiler", not found, repr(found))


def check_real_tree_passes():
    result = run(COMMAND, ROOT)
    check("bun run typecheck passes on the real tree", result.returncode == 0,
          f"rc={result.returncode} {result.stdout}{result.stderr}")


def check_poison_fails(sources):
    with tempfile.TemporaryDirectory(prefix="feat2257-typecheck-") as scratch:
        for rel in ("tsconfig.json", "package.json", *sources):
            os.makedirs(os.path.dirname(os.path.join(scratch, rel)), exist_ok=True)
            shutil.copy2(os.path.join(ROOT, rel), os.path.join(scratch, rel))
        os.symlink(os.path.join(ROOT, "node_modules"), os.path.join(scratch, "node_modules"))
        clean = run(COMMAND, scratch)
        check("the clean copy passes the same command", clean.returncode == 0,
              f"rc={clean.returncode} {clean.stdout}{clean.stderr}")
        with open(os.path.join(scratch, POISONED), "a", encoding="utf-8") as handle:
            handle.write('\nexport const feat2257TypecheckPoison: never = "not never";\n')
        poisoned = run(COMMAND, scratch)
        output = poisoned.stdout + poisoned.stderr
        check("one deliberate type error fails the same command, naming the poisoned file",
              poisoned.returncode != 0 and "error TS" in output and POISONED in output,
              f"rc={poisoned.returncode} {output}")


def check_activation():
    with open(os.path.join(ROOT, ".harness", "harness.json"), encoding="utf-8") as handle:
        kind = json.load(handle).get("test_kinds", {}).get("typecheck")
    check("test_kinds.typecheck is active with exactly this command and no _reason",
          isinstance(kind, dict) and kind.get("status") == "active"
          and kind.get("cmd") == " ".join(COMMAND) and "_reason" not in kind, repr(kind))


def main():
    if shutil.which("bun") is None:
        print("FAIL bun is not on PATH")
        return 1
    sources = tracked_sources()
    check_coverage(sources)
    check_no_suppression(sources)
    check_real_tree_passes()
    check_poison_fails(sources)
    check_activation()
    return C.report()


if __name__ == "__main__":
    sys.exit(main())
