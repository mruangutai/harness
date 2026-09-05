# Receipt — harness-backend-dev — T-03 (tree-audit census subcommand)

## What changed

`tests/manual/suite-census.py` only:
- inserted `ROOT/.claude/skills/harness/bin` at the front of `sys.path` and imported
  `RESTRICTED_NAME_PATTERNS`, `AGNOSTIC_NAME_PATTERNS`, `SOURCE_EXTENSIONS`, `DOCUMENTED_EXCEPTIONS`
  from `suite_layout` (never re-declared)
- added `_vocabulary_paths`, `_disposition`, `_measure`, `_read_note_rows`, `_print_measurement`,
  `_print_diff`, `tree_audit` and `add_tree_audit_parser`, and registered the subcommand in `main()`
  the same way the existing four are registered
- did NOT call `baseline()`; did NOT touch `suite_layout.py` (a sibling concurrently modified it —
  observed, not mine, see below)

Selection is basename-vs-either-tuple with no extension filter. Dispositions: `in-tests-tree` (path
starts `tests/`), `documented-exception` (exact `DOCUMENTED_EXCEPTIONS` match), `out-of-vocabulary`
(restricted-only match AND extension not in `SOURCE_EXTENSIONS`), else `violation`. Row block + TOTAL
line print unconditionally, before any `--against` comparison, per spec.

## Verify (verbatim command, cross-checked against `plan.yaml` T-03 `verify:` at line 904 — identical)

Command:
```
out=$(python3 tests/manual/suite-census.py tree-audit --ref HEAD) && printf '%s\n' "$out" | grep -q 'probe-session-accessors\.ts.*documented-exception'
```

Result: `VERIFY_EXIT=0` (pass).

## Full measurement (plain invocation, `--ref HEAD` at `5eebad66`)

```
.harness/harness/features/FEAT-10-software-factory/notes/probe-board-limits.md	out-of-vocabulary
.harness/harness/features/FEAT-10-software-factory/notes/probe-edge-idempotence.md	out-of-vocabulary
.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-delivery-channel.md	out-of-vocabulary
.harness/harness/features/FEAT-31-orchestrator-context-watch/notes/probe-hook-payload-identity.md	out-of-vocabulary
.harness/harness/features/FEAT-40-harness-writes-done/notes/probe-done-closes.md	out-of-vocabulary
.harness/harness/features/FEAT-40-harness-writes-done/notes/probe-sweep-fires.md	out-of-vocabulary
.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors-out.jsonl	out-of-vocabulary
.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts	documented-exception
.harness/notes/probe-746-foreground-dispatch-2026-08-26.md	out-of-vocabulary
tests/integration/test-*.py (49 files)	in-tests-tree
tests/manual/probe-handoff-comprehension.py	in-tests-tree
tests/manual/probe-omp-session-accessor.py	in-tests-tree
tests/unit/omp-hooks.test.ts	in-tests-tree
tests/unit/test-*.py (28 files)	in-tests-tree
TOTAL 85 OUTSIDE 9 VIOLATIONS 0
```
(Full row-by-row output observed directly in this run; the `tests/` rows collapsed above only for
receipt brevity — the actual command prints every one of the 85 rows in full, unabridged.)

**Matches the plan's expected measurement exactly**: `TOTAL 85 OUTSIDE 9 VIOLATIONS 0`, 1 documented
exception (`.ts`), 8 out-of-vocabulary Markdown/JSONL probe records all matching `probe-*` only. No
delta to report.

## Branch exercise (throwaway notes under `/tmp`, all removed after)

1. **Zero-fence refusal** — note `no fences here at all\n`:
   `exit=2`, stderr exactly `note carries no fenced block: /tmp/note-zero-fence.md`. Row block + TOTAL
   line still printed to stdout before the refusal (confirmed via `tail`).
2. **Two-fence refusal** — note with two ` ```text ` blocks:
   `exit=2`, stderr exactly `note carries 2 fenced blocks, expected exactly 1: /tmp/note-two-fence.md`.
3. **Matching `--against`** — note built from the measured rows verbatim, one fence:
   `exit=0`, empty stderr, no MISSING/EXTRA lines, block + TOTAL printed as normal.
4. **Differing `--against`** — note with one row dropped (`probe-board-limits.md`) and one bogus row
   added (`some/bogus/path.md`):
   `exit=1`, stdout tail:
   ```
   TOTAL 85 OUTSIDE 9 VIOLATIONS 0
   MISSING .harness/harness/features/FEAT-10-software-factory/notes/probe-board-limits.md	out-of-vocabulary
   EXTRA some/bogus/path.md	violation
   ```
   MISSING/EXTRA print AFTER the block and TOTAL line, additive as specified.
5. **`--ref` other than HEAD** — `--ref $(git rev-parse HEAD~1)` (`5bf1e120`):
   `exit=0`, same `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` (no vocabulary-relevant tracked-file change between
   the two commits).

## Scope / repo state

`git -C <worktree> status --porcelain`:
```
 M .claude/skills/harness/bin/suite_layout.py
 M .harness/harness/features/BUG-1286-test-tree-enforcement/STATE.md
 M .harness/harness/features/BUG-1286-test-tree-enforcement/feature.json
 M .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
 M tests/integration/test-run-unit-tests-layout.py
 M tests/manual/suite-census.py
 M tests/unit/test-suite-layout.py
?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-T-01-c1.md
?? .harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-backend-dev-T-02-c1.md
```
Only `tests/manual/suite-census.py` is this task's change. All other entries are concurrent sibling
work (T-01/T-02 landed as unstaged working-tree changes, plus feature-tracking files and their own
receipts) — observed, not touched, not reverted. `HEAD` still `5eebad66`; nothing staged, nothing
committed.

## Note on process

An initial edit attempt used a bare relative path (`tests/manual/suite-census.py`) and landed against
the MAIN checkout instead of the worktree. Caught immediately via `git status --porcelain` in the main
checkout, reverted with `git checkout -- tests/manual/suite-census.py` there (confirmed clean
afterward), and redone correctly against the absolute worktree path. Main checkout is clean; only the
worktree carries this change.
