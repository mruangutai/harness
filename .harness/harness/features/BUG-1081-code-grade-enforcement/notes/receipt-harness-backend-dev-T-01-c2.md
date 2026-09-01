# Receipt — harness-backend-dev — T-01 cycle 2

Narrow repair only. Does not overwrite the c1 receipt (`receipt-harness-backend-dev-T-01-c1.md`),
which records why this cycle was spent.

## Pre-repair diff (ground truth for the task)

`git -C <worktree> diff -- .claude/skills/harness/bin/code-grade.py` before any cycle-2 edit
contained the MOVE plus three unauthorized regions (R1, R2, R3):

```diff
diff --git a/.claude/skills/harness/bin/code-grade.py b/.claude/skills/harness/bin/code-grade.py
index 569e19a..c70b90e 100755
--- a/.claude/skills/harness/bin/code-grade.py
+++ b/.claude/skills/harness/bin/code-grade.py
@@ -4,7 +4,6 @@ from __future__ import annotations
 
 import argparse
 import ast
-import fnmatch
 import json
 import subprocess
 import sys
@@ -29,82 +28,51 @@ def _display_path(path):
 def _git_text(root, *args):
     result = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True)
     if result.returncode:
-        raise ValueError(result.stderr.strip())
+        raise ValueError(result.stderr.strip() or f"git {' '.join(args)} failed")
     return result.stdout
 
 
 def _relative(root, path):
     try:
-        return Path(path).resolve().relative_to(root).as_posix()
+        return str((root / path).resolve().relative_to(root))
     except ValueError as error:
         raise ValueError(f"path outside repository: {path}") from error
 
 
-def _patterns(value):
-    return [part.strip() for part in value.split("|") if part.strip()]
-
-
-def _is_test(root, relative):
+def _load_test_kinds(root):
     with (root / ".harness" / "harness.json").open(encoding="utf-8") as stream:
-        kinds = json.load(stream)["test_kinds"]
-    return any(any(fnmatch.fnmatch(relative, pattern) for pattern in _patterns(kind["detect"])) and
-               not any(fnmatch.fnmatch(relative, pattern) for pattern in _patterns(kind.get("exclude", "")))
-               for kind in kinds.values() if kind.get("status") == "active")
-
-
-def _blocks(grade, bar):
-    return grade < bar and grade != 2
-
-
-def _severity(grade, bar):
-    if _blocks(grade, bar):
-        return "high"
-    return "med" if grade == 2 else None
-
+        return json.load(stream)["test_kinds"]
 
-def _record(grade, root):
-    bar = 3 if _is_test(root, grade.path) else 4
-    severity = _severity(grade.grade, bar)
-    record = {"path": grade.path, "line": grade.lineno, "qualname": grade.qualname,
-              "cyclomatic": grade.cyclomatic, "cognitive": grade.cognitive,
-              "cognitive_method": "Sonar-style approximation", "abc": grade.abc,
-              "grade": grade.grade, "driver": grade.driver, "bar": bar, "severity": severity}
-    record["result"] = _result(record)
-    return record
 
-
-def _paths_report(root, paths):
-    records, ungraded = [], []
+def _paths_report(root, paths, test_kinds):
+    grades, ungraded = [], []
     for raw_path in paths:
         path = _relative(root, raw_path)
         try:
-            grades = code_grade.grade_source((root / path).read_text(), path)
+            grades.extend(code_grade.grade_source((root / path).read_text(), path))
         except (OSError, SyntaxError) as error:
             print(f"PARSE ERROR: {_display_path(path)}: {error}", file=sys.stderr)
             ungraded.append(path)
-            continue
-        records.extend(_record(grade, root) for grade in grades)
+    records, _ = code_grade.classify(grades, test_kinds)
     return records, ungraded
 
 
 def _run_name_status_diff(root, base, head):
     result = subprocess.run(
-        ["git", "-C", str(root), "diff", "--find-renames", "--name-status", "-z", base, head],
-        capture_output=True,
+        ["git", "-C", str(root), "diff", "--name-status", "-z", "--find-renames", base, head],
+        text=False, capture_output=True,
     )
     if result.returncode:
-        raise ValueError(result.stderr.decode(errors="replace").strip())
+        raise ValueError(result.stderr.decode(errors="surrogateescape").strip() or "git diff failed")
     return result.stdout
 
 
 def _name_status_entries(raw):
     fields = iter(raw.split(b"\0"))
-    for raw_status in fields:
-        if not raw_status:
+    for status in fields:
+        if not status:
             continue
-        status = raw_status.decode()
-        if status.startswith(("R", "C")):
-            next(fields)
+        status = status.decode()
         yield status, next(fields).decode(errors="surrogateescape")
 
 
@@ -118,7 +86,7 @@ def _diff_paths(root, base, head):
     return sorted(path for status, path in entries if _is_changed_python(status, path))
 
 
-def _diff_report(root, base, head):
+def _diff_report(root, base, head, test_kinds):
     paths = _diff_paths(root, base, head)
     ungraded = []
     for path in paths:
@@ -130,13 +98,8 @@ def _diff_report(root, base, head):
     if ungraded:
         return [], ungraded
     gated, _ = code_grade.gated_set(root, base, head)
-    return [_record(grade, root) for grade in gated], []
-
-
-
-
-def _result(record):
-    return "PASS" if record["grade"] >= record["bar"] else "FAIL"
+    records, _ = code_grade.classify(gated, test_kinds)
+    return records, []
 
 
 def _text(records, ungraded):
@@ -147,7 +110,7 @@ def _text(records, ungraded):
                       f"COGNITIVE: {record['cognitive']} ({record['cognitive_method']})",
                       f"ABC: {record['abc']:.1f}", f"GRADE: {record['grade']}",
                       f"DRIVER: {record['driver']}", f"BAR: {record['bar']}",
-                      f"RESULT: {_result(record)}"))
+                      f"RESULT: {record['result']}"))
         if record["severity"]:
             lines.append(f"SEVERITY: {record['severity']}")
         if record["grade"] == 2:
@@ -163,7 +126,7 @@ def _text(records, ungraded):
 def _status(records, ungraded):
     if ungraded:
         return 3
-    return 1 if any(_blocks(record["grade"], record["bar"]) for record in records) else 0
+    return 1 if any(record["severity"] == "high" for record in records) else 0
 
 
 def main(argv=None):
@@ -177,10 +140,11 @@ def main(argv=None):
         parser.error("provide PATH... or both --base REF and --head REF")
     try:
         root = _git_root(Path.cwd())
+        test_kinds = _load_test_kinds(root)
         base = code_grade.commit_oid(root, args.base) if args.base else None
         head = code_grade.commit_oid(root, args.head) if args.head else None
-        records, ungraded = (_diff_report(root, base, head) if base else
-                             _paths_report(root, args.paths))
+        records, ungraded = (_diff_report(root, base, head, test_kinds) if base else
+                             _paths_report(root, args.paths, test_kinds))
     except ValueError as error:
         parser.error(str(error))
     records.sort(key=lambda record: (record["path"], record["line"]))
```

## The three reverts applied

**R1 — `_name_status_entries`**: restored the `raw_status` variable name and the
`if status.startswith(("R", "C")): next(fields)` skip that consumes a rename/copy's OLD
path field before yielding the status/NEW-path pair. Without it, `git diff --name-status -z
--find-renames` emits `R100\0old\0new\0` and the generator desynchronises, yielding
`("R100", old_path)` and then misreading the new-path bytes as the next status.

**R2 — `_relative`**: restored `return Path(path).resolve().relative_to(root).as_posix()`
verbatim, dropping the `(root / path).resolve()` resolution-base change. The base resolves a
relative CLI argument against the process cwd, matching how a human invokes `code-grade.py
some/file.py` from inside a subdirectory.

**R3 — `_git_text` and `_run_name_status_diff`**: restored both to base content —
`raise ValueError(result.stderr.strip())` (no `or f"git ... failed"` fallback);
`git diff --find-renames --name-status -z <base> <head>` argument order; no `text=False`;
stderr decode `errors="replace")` (not `surrogateescape`); no `or "git diff failed"` fallback.

## Final diff — hunk by hunk, all MOVE

`git -C <worktree> diff -- .claude/skills/harness/bin/code-grade.py` after the reverts:

```diff
diff --git a/.claude/skills/harness/bin/code-grade.py b/.claude/skills/harness/bin/code-grade.py
index 569e19a..0b06910 100755
--- a/.claude/skills/harness/bin/code-grade.py
+++ b/.claude/skills/harness/bin/code-grade.py
@@ -4,7 +4,6 @@ from __future__ import annotations
 
 import argparse
 import ast
-import fnmatch
 import json
 import subprocess
 import sys
@@ -40,50 +39,21 @@ def _relative(root, path):
         raise ValueError(f"path outside repository: {path}") from error
 
 
-def _patterns(value):
-    return [part.strip() for part in value.split("|") if part.strip()]
-
-
-def _is_test(root, relative):
+def _load_test_kinds(root):
     with (root / ".harness" / "harness.json").open(encoding="utf-8") as stream:
-        kinds = json.load(stream)["test_kinds"]
-    return any(any(fnmatch.fnmatch(relative, pattern) for pattern in _patterns(kind["detect"])) and
-               not any(fnmatch.fnmatch(relative, pattern) for pattern in _patterns(kind.get("exclude", "")))
-               for kind in kinds.values() if kind.get("status") == "active")
-
-
-def _blocks(grade, bar):
-    return grade < bar and grade != 2
-
-
-def _severity(grade, bar):
-    if _blocks(grade, bar):
-        return "high"
-    return "med" if grade == 2 else None
-
+        return json.load(stream)["test_kinds"]
 
-def _record(grade, root):
-    bar = 3 if _is_test(root, grade.path) else 4
-    severity = _severity(grade.grade, bar)
-    record = {"path": grade.path, "line": grade.lineno, "qualname": grade.qualname,
-              "cyclomatic": grade.cyclomatic, "cognitive": grade.cognitive,
-              "cognitive_method": "Sonar-style approximation", "abc": grade.abc,
-              "grade": grade.grade, "driver": grade.driver, "bar": bar, "severity": severity}
-    record["result"] = _result(record)
-    return record
 
-
-def _paths_report(root, paths):
-    records, ungraded = [], []
+def _paths_report(root, paths, test_kinds):
+    grades, ungraded = [], []
     for raw_path in paths:
         path = _relative(root, raw_path)
         try:
-            grades = code_grade.grade_source((root / path).read_text(), path)
+            grades.extend(code_grade.grade_source((root / path).read_text(), path))
         except (OSError, SyntaxError) as error:
             print(f"PARSE ERROR: {_display_path(path)}: {error}", file=sys.stderr)
             ungraded.append(path)
-            continue
-        records.extend(_record(grade, root) for grade in grades)
+    records, _ = code_grade.classify(grades, test_kinds)
     return records, ungraded
 
 
@@ -118,7 +88,7 @@ def _diff_paths(root, base, head):
     return sorted(path for status, path in entries if _is_changed_python(status, path))
 
 
-def _diff_report(root, base, head):
+def _diff_report(root, base, head, test_kinds):
     paths = _diff_paths(root, base, head)
     ungraded = []
     for path in paths:
@@ -130,13 +100,8 @@ def _diff_report(root, base, head):
     if ungraded:
         return [], ungraded
     gated, _ = code_grade.gated_set(root, base, head)
-    return [_record(grade, root) for grade in gated], []
-
-
-
-
-def _result(record):
-    return "PASS" if record["grade"] >= record["bar"] else "FAIL"
+    records, _ = code_grade.classify(gated, test_kinds)
+    return records, []
 
 
 def _text(records, ungraded):
@@ -147,7 +112,7 @@ def _text(records, ungraded):
                       f"COGNITIVE: {record['cognitive']} ({record['cognitive_method']})",
                       f"ABC: {record['abc']:.1f}", f"GRADE: {record['grade']}",
                       f"DRIVER: {record['driver']}", f"BAR: {record['bar']}",
-                      f"RESULT: {_result(record)}"))
+                      f"RESULT: {record['result']}"))
         if record["severity"]:
             lines.append(f"SEVERITY: {record['severity']}")
         if record["grade"] == 2:
@@ -163,7 +128,7 @@ def _text(records, ungraded):
 def _status(records, ungraded):
     if ungraded:
         return 3
-    return 1 if any(_blocks(record["grade"], record["bar"]) for record in records) else 0
+    return 1 if any(record["severity"] == "high" for record in records) else 0
 
 
 def main(argv=None):
@@ -177,10 +142,11 @@ def main(argv=None):
         parser.error("provide PATH... or both --base REF and --head REF")
     try:
         root = _git_root(Path.cwd())
+        test_kinds = _load_test_kinds(root)
         base = code_grade.commit_oid(root, args.base) if args.base else None
         head = code_grade.commit_oid(root, args.head) if args.head else None
-        records, ungraded = (_diff_report(root, base, head) if base else
-                             _paths_report(root, args.paths))
+        records, ungraded = (_diff_report(root, base, head, test_kinds) if base else
+                             _paths_report(root, args.paths, test_kinds))
     except ValueError as error:
         parser.error(str(error))
     records.sort(key=lambda record: (record["path"], record["line"]))
```

Hunk-by-hunk classification, all authorized MOVE, nothing else:
1. `-import fnmatch` — unused import removal (fnmatch usage moved into `code_grade.py`).
2. `_patterns`/`_is_test`/`_blocks`/`_severity`/`_record` removed, `_load_test_kinds` added —
   the MOVE, replaced by `code_grade.classify(...)`.
3. `_paths_report(root, paths)` → `_paths_report(root, paths, test_kinds)` — `test_kinds`
   threading, grades accumulated then classified via `code_grade.classify(grades, test_kinds)`.
4. `_diff_report(root, base, head)` → `_diff_report(root, base, head, test_kinds)` — same
   threading; `_result`/`_record` calls replaced by `code_grade.classify(gated, test_kinds)`.
5. `_text`: `f"RESULT: {_result(record)}"` → `f"RESULT: {record['result']}"` — reads the
   classifier's own `result` field instead of recomputing it.
6. `_status`: `_blocks(record["grade"], record["bar"])` → `record["severity"] == "high"` —
   keys on the classifier's severity instead of recomputing `_blocks`.
7. `main`: `test_kinds = _load_test_kinds(root)` added, threaded into both report calls.

No R1/R2/R3 hunks remain. `_name_status_entries`, `_relative`, `_git_text`,
`_run_name_status_diff` do not appear in this diff at all — they are byte-identical to
branch-base (confirmed: they carry zero hunks above; verified directly against the base
content quoted in the task dispatch).

## New rename-discriminating assertion — RED/GREEN proof

Added `test_rename_diff_paths(repo)` to `test-code-grade-cli.py` (wired into `main()`):
builds a genuine `git mv` with UNCHANGED file content (`src/mover.py` → `src/moved.py`),
confirms `git diff --name-status -z --find-renames` actually emits a status starting `"R"`,
then asserts `code_grade_cli._diff_paths(repo, base, head) == ["src/moved.py"]`.

**RED** (R/C skip deleted from `_name_status_entries`, file hash before mutation
`f28ba0b0b9fcf1cfcbd8b693eaae8c34`, confirmed identical after restore):

```
FAIL _diff_paths keeps only the renamed head-side path, never the old one: expected ['src/moved.py'], got ['src/mover.py']
```

This is exactly the desynchronization the dispatch predicted — the OLD path (`src/mover.py`)
survives instead of the NEW one. The existing `test_diff_and_determinism` rename fixture
cannot see this because it rewrites file content at the same time as the `git mv`
(similarity drops below the rename threshold, so git reports delete+add, never `R`) —
confirmed by design here: this new fixture keeps content byte-identical specifically to force
`R`.

**GREEN** (skip restored, hash back to `f28ba0b0b9fcf1cfcbd8b693eaae8c34`):
`PASS test-code-grade-cli` (all cases green), `EXIT=0`.

## `_name_status_entries` complexity check

With the `R`/`C` branch restored, `code_grade.grade_source` on the current file reports
`_name_status_entries` at grade 4 (cyclomatic 4, cognitive 5, ABC 8.6) — meets
`test_diff_paths_complexity`'s `>= 4` requirement with the branch present. No trade-off was
needed; nothing was dropped to satisfy the gate.

## Suite results

**Unit** (`.agents/skills/harness/bin/run-unit-tests.sh --kind unit`): exit status `0`.
`grep -c '^FAIL '` over full captured output: `0`. `test-code-grade.py` ran and reported
`PASS test-code-grade` / `PASS test-code-grade.py`.

**Integration** (`.agents/skills/harness/bin/run-unit-tests.sh --kind integration`): exit
status `0`. `grep -c '^FAIL '` over full captured output: `0`. `test-code-grade-cli.py` ran
and reported `PASS test-code-grade-cli` / `PASS test-code-grade-cli.py` (script tail:
`ALL PASSED` … `PASS test-check-decision-anchors.py` as final entries in the log).

## `git status --porcelain` (worktree)

```
 M .claude/skills/harness/bin/code-grade.py
 M .claude/skills/harness/bin/code_grade.py
 M .claude/skills/harness/bin/test-code-grade-cli.py
 M .claude/skills/harness/bin/test-code-grade.py
 M .harness/harness/features/BUG-1081-code-grade-enforcement/feature.json
 M .harness/harness/features/BUG-1081-code-grade-enforcement/plan.yaml
?? .harness/harness/features/BUG-1081-code-grade-enforcement/STATE.md
?? .harness/harness/features/BUG-1081-code-grade-enforcement/notes/receipt-harness-backend-dev-T-01-c1.md
```

`code_grade.py` and `test-code-grade.py` show as modified from cycle 1's accepted seam work
(the MOVE landing `classify`/`TestKindsError`/`_is_test_path`/`_blocks`/`_severity`/
`_classify_record`) — untouched by this cycle. `feature.json`, `plan.yaml`, and `STATE.md`
are the orchestrator's concurrently-modified files, also untouched by this cycle. Nothing
was committed.

## Seam contract (unchanged, for T-02)

- `code_grade.classify(grades, test_kinds) -> (records, result)` — signature and return
  shape unchanged from cycle 1.
- `code_grade.TestKindsError(ValueError)` — unchanged.
- `_is_test_path`, `_blocks`, `_severity`, `_classify_record` in `code_grade.py` — unchanged,
  not touched this cycle.
