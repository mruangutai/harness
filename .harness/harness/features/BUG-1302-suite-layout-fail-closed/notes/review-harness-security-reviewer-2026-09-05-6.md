# Security review — BUG-1302 @ ac8dd671

**Verdict: PASS, severity_max=info.** In scope (test files touch git fixtures, subprocess, and a
new exception-guarded file read of tracked repo content); examined; no exploitable finding.

## Surfaces examined

1. **`_violations_callers` (tests/unit/test-suite-layout.py:160-190)** — the diff's only new
   read-of-arbitrary-tracked-bytes surface (B-14). Wraps the pre-existing unconditional
   `(root/rel).read_text()` in `try/except (OSError, UnicodeDecodeError)`; on failure appends
   `f"unreadable tracked source {rel}: {type(error).__name__}"`. Confirmed:
   - **No content leak.** Only the tracked *path* and the exception *class name* ever reach output
     — never file bytes, decoded or raw. Ruled out log/output injection via file content.
   - **The symlink-following read is pre-existing, not introduced.** `git diff 54f01854..ac8dd671`
     shows the unconditional `.read_text()` call already existed before this diff (confirmed via
     side-by-side hunk); B-14 only adds exception handling around it. A tracked symlink pointing
     outside the repo was already followed pre-fix — this diff doesn't create that surface, it
     makes failure on it fail-closed instead of crashing the suite (a fix, not a regression).
   - **No unbounded-read exploit path**: `git ls-files -s` in this worktree shows exactly one
     tracked symlink (`.agents/skills`, mode 120000), which has no extension and is filtered out
     by `os.path.splitext(rel)[1] not in source_extensions` before any read is attempted — not
     reachable today.
   - **Threat model**: triggering this at all (planting a tracked symlink or oversized/binary file
     under a `SOURCE_EXTENSIONS` path outside `tests/`) requires commit access to the repo. Per
     P-02, an actor who can already commit tracked source already has stronger avenues (arbitrary
     code executed directly by CI) — no privilege escalation here.
   - **Read size is unbounded** (`.read_text()`, no cap) — noted as an info-level hardening item,
     not blocking, since it requires the same pre-existing commit-access precondition as above.
   - Confirmed live: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-suite-layout.py` — `PASS
     violations() has exactly one non-test caller repository-wide` and `PASS b14: unreadable
     tracked sources are reported, not raised`, exit 0. The real ROOT today has zero unreadable
     tracked sources (the exact-equality check against `{"run-unit-tests.sh"}` passed), so no live
     exploit exists.

2. **Subprocess invocations, both files** — `git ls-files`, `git init -b main -q`, `git add -A`,
   `git commit -q -c user.email=... -c user.name=...`, and the runner invocation in
   `tests/integration/test-run-unit-tests-layout.py:run()` — all list-form argv, no `shell=True`
   anywhere in either file (`grep shell=` empty), no string-built shell commands, no argv element
   built from a filesystem-derived (non-fixture-literal) name. `git commit` pins `-c
   user.email`/`-c user.name` so it does not read the developer's global git identity. `run()`'s
   `env=dict(os.environ, HARNESS_PROJECT_DIR=...)` inherits the caller's full environment
   (including whatever `HARNESS_AGENT_TYPE` is set to) — **but this function is unchanged by the
   diff** (only one line changed in this file: the B-8 string-match widening at line ~93); out of
   scope per the dispatch's non-goal on untouched production/fixture code.

3. **Temp-directory handling** — every fixture (`legal_tree`, `base_git_fixture`,
   `Path(tempfile.mkdtemp())` call sites) uses `tempfile.mkdtemp()` (mode 0700, non-predictable
   name) and every write target is a fixture-literal relative path under the returned root — none
   of the corpus tuples (`B5_CORPUS`, `B4_CORPUS`, e.g. `"../x/*.py"`, `"tests/../evil/*.py"`,
   `"/abs/tests/*.py"`) ever reach a filesystem call; they are pure string arguments to
   `_is_inside_tests()`, which does `posixpath.normpath`/`splitext` only, no I/O. No path
   traversal. Cleanup is `try/finally: shutil.rmtree(...)` around every fixture, including the new
   B-14 block, so a failed `check()` (which never raises) or a raised subprocess exception both
   still clean up.

4. **Secrets/credentials** — `grep -niE "token|secret|password|api[_-]?key|credential"` over both
   files and the feature's red-demonstrations note: zero matches. None expected, none found.

5. **B-6 and B-8 changes** — B-6 converts a fail-open `print("INAPPLICABLE"...)` into a hard
   `check(..., False, ...)`; B-8 widens a substring assertion. Both tighten test-suite fail-closed
   posture (the feature's own intent); neither loosens a validation invariant or touches
   production code, so P-03 (scope-in on loosened guards) does not fire here — this is the
   opposite direction.

## Findings

None. `must_fix: []`.

## Scope note

Diff touches only the two named test files (confirmed via `git diff --stat 54f01854..ac8dd671`,
8 paths total, six of which are feature-lifecycle artifacts with no code content). No production
code path (`suite_layout.py`, `run-unit-tests.sh`, `code_grade.py`) is touched by this diff —
read-only per the dispatch's carve-out list, and `git diff --stat` confirms none of them appear.
