#!/usr/bin/env python3
"""validate-digest.py's #919 refusal report (#2253, #2281).

A red independent re-run is pooled by run_pool.py, which prints files in completion order
and echoes each file's captured output verbatim. The refusal must name every failing and
mutated file before the 20-line tail, so the parsers decide which lines are run_pool's own.
"""
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / ".claude/skills/harness/bin"
sys.path.insert(0, str(BIN))
import harness_boundary  # noqa: E402

vd = harness_boundary.load_repo_module("validate_digest_run_pool_lines", str(BIN / "validate-digest.py"))

NOTE = ("A file under the watched directory changed while the suite ran; this violates REQ-01. "
        "A concurrent hand edit or agent edit is indistinguishable.")


def block(name, rc, *body):
    return [f"----- {name} (exit {rc}, 0.10s) -----", *body, f"{'PASS' if rc == 0 else 'FAIL'} {name}"]


class FileLines(unittest.TestCase):
    def test_failing_files_listed_in_order_with_duplicates_passing_files_not(self):
        lines = block("a.py", 1) + block("b.py", 0) + block("c.py", 2) + block("a.py", 1)
        self.assertEqual(vd._run_pool_file_lines(lines), ["FAIL a.py", "FAIL c.py", "FAIL a.py"])

    def test_names_with_spaces_are_listed(self):
        lines = block("my test.py", 1) + ["MUTATED notes/my file.md", NOTE]
        self.assertEqual(vd._run_pool_file_lines(lines), ["FAIL my test.py", "MUTATED notes/my file.md"])

    def test_echoed_case_lines_inside_a_block_are_not_files(self):
        lines = block("a.py", 1, "FAIL  [x] some case: detail", "FAIL unknown case label",
                      "MUTATED echoed.txt", "FAILED-NOT-A-FILE-LINE")
        self.assertEqual(vd._run_pool_file_lines(lines), ["FAIL a.py"])

    def test_no_echo_hides_a_genuine_failure(self):
        lines = (block("outer.py", 1, "----- fixture.py (exit 1, 0.01s) -----", "PASS outer.py")
                 + block("ok.py", 0, "----- echoed.py (exit 0, 0.00s) -----")
                 + block("later.py", 1, "PASS later.py"))
        self.assertEqual(vd._run_pool_file_lines(lines), ["FAIL outer.py", "FAIL later.py"])

    def test_only_mutated_lines_directly_above_run_pools_note_count(self):
        lines = (["MUTATED stray-before.txt"] + block("a.py", 0, "MUTATED in-block.txt")
                 + ["MUTATED x.txt", "MUTATED y z.txt", NOTE, "MUTATED after-note.txt"])
        self.assertEqual(vd._run_pool_file_lines(lines), ["MUTATED x.txt", "MUTATED y z.txt"])


class Report(unittest.TestCase):
    def report(self, output):
        err = StringIO()
        with redirect_stderr(err):
            vd._print_independent_run(output)
        return err.getvalue()

    def test_buried_files_are_named_before_the_unchanged_tail(self):
        passing = [line for i in range(12) for line in block(f"p{i}.py", 0)]
        out = self.report("\n".join(block("slow fail.py", 1) + passing) + "\n")
        self.assertEqual(out.splitlines()[:3],
                         ["Failing or mutated files:", "  FAIL slow fail.py", "Tail of the independent run:"])
        self.assertEqual(out.splitlines()[3:], [f"  {line}" for line in passing[-20:]])

    def test_a_run_with_no_file_line_keeps_the_tail_alone(self):
        out = self.report("Traceback: runner crashed\n")
        self.assertEqual(out.splitlines(), ["Tail of the independent run:", "  Traceback: runner crashed"])


if __name__ == "__main__":
    unittest.main()
