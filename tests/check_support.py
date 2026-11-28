"""check_support.py — the pass/fail harness for script-style tests (no unittest).

    from check_support import Checks

    C = Checks()
    check = C.check                       # check(name, cond, detail="") -> bool
    ...
    sys.exit(C.report())                  # keep this line explicit in every file

Checks.check(name, cond, detail="")
    Records one check and prints one line: `PASS <name>` or `FAIL <name>`. On failure a
    non-empty `detail` (any object; str() is taken) follows on the next lines, indented four
    spaces. Returns bool(cond), so a caller can guard follow-on checks.
Checks.report() -> int
    Prints a one-line summary and returns the exit code: 1 when any check failed, 1 when no
    check ran at all (a file whose cases never executed must not pass), otherwise 0.
Checks.ran / Checks.failed
    The count of checks run and the list of failed names, for a file that prints its own extra
    summary.

The runner reads only a child's exit code, so a file that drops `sys.exit(C.report())` passes
with FAIL lines printed. Nothing here registers an atexit hook to cover for that. A file whose
check() does more (clears a memo first, tags a case id, returns an int) keeps a short local
wrapper that calls C.check.
"""
import textwrap


class Checks:
    def __init__(self):
        self.ran = 0
        self.failed = []

    def check(self, name, cond, detail=""):
        ok = bool(cond)
        self.ran += 1
        print(f"{'PASS' if ok else 'FAIL'} {name}")
        if not ok:
            self.failed.append(name)
            if detail != "":
                print(textwrap.indent(str(detail), "    "))
        return ok

    def report(self):
        if self.ran == 0:
            print("\nFAIL no checks ran")
            return 1
        if self.failed:
            print(f"\nFAIL {len(self.failed)} of {self.ran} checks failed: "
                  + ", ".join(self.failed))
            return 1
        print(f"\n{self.ran}/{self.ran} checks passed.")
        return 0
