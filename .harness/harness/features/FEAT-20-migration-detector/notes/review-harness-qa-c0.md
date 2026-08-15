# Gate-only matrix re-run — FEAT-20-migration-detector — pinned SHA `ea476fd`

**PASS.** Both required kinds ran green, independently, at `ea476fd`, in an isolated worktree.
Author-nothing dispatch: no tests, fixtures or source touched.

## Matrix — denominator (P-04)

`test_matrix` binds 2 of the 4 tasks:
- T-01 (`layout_migration.py`, `test-layout-migration.py`, `run-unit-tests.sh`) — `change_type: logic` → **unit** required.
- T-02 (`check-state.sh`, `test-check-state.py`) — `change_type: cross_module` → **unit + integration** required.
- T-03 (`.github/workflows/tests.yml`) — `change_type: config` → matrix requires `[]`. `verify: inspection` only.
- T-04 (`docs/harness/DECISIONS.md`, `DECISIONS-INDEX.md`) — `change_type: docs` → matrix requires `[]`. `verify: inspection` only.

T-03 and T-04's own `verify:` commands were run and passed (both greps/diffs `ok`), but this is
**inspected, not mutation-proven** (O-03) — the matrix itself asserts nothing about config/docs.

## Kinds

- **unit** — `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`, run in-place at `ea476fd`
  in worktree `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-feat20-gate`. Exit 0.
  `PASS test-layout-migration.py`, 27 named `ok` assertions, cases 1–18 (18 required by plan, plus
  cases 17–18 added: a non-enum surface row is a loud error, and `scan()`/`exit_code()` contract).
  All 18 T-01 cases present and asserting content (exit code + named surface/reader/tag), not exit
  code alone. State: **satisfied**.
- **integration** — `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`, same
  worktree. Exit 0. `PASS test-check-state.py`, 84 named `ok` assertions in its block, including
  the five INV-27 cases the plan specifies: (x.1) mixed → INV-27 names reader+tag+remedy,
  (x.2) unjudgeable → CANNOT VERIFY, (x.3) applicable clean → no INV-27 line, (x.4) no marker → no
  INV-27 line, (x.5) unimportable module → CANNOT RUN, exit 1. State: **satisfied**.

Both test files (`test-layout-migration.py`, `test-check-state.py`) are themselves in the diff
(P-05) — presence is not borrowed from a pre-existing test.

## SHELL NOTE — substitution made

The plan's own `verify:` blocks pipe to `u=$(mktemp)`, which this environment's write-guard blocks
(redirect-to-shell-variable). I ran the same commands directly (no redirect) and read the captured
stdout/stderr in place of `cat "$u"`, checking for the same literal markers the plan's `grep -q`
lines check (`^PASS test-layout-migration\.py$`, `^PASS test-check-state\.py$`) and reading exit
codes directly rather than via `$ru`/`$ri`. Semantically identical to the plan's clause; only the
capture mechanism differs.

## 11cb644..ea476fd delta

`git diff --name-only 11cb644..ea476fd` touches only `.harness/features/FEAT-20-migration-detector/{STATE.md,feature.json,notes/handoff-build.md,notes/qa-c0.md}` — feature-state and receipt files. **Zero of the eight source files named in this dispatch changed.** The source tree the prior qa segment ran the matrix on at `11cb644` is byte-identical to `ea476fd`. My run at `ea476fd` is not a relay of that result — it re-executed both kinds independently — but the underlying code under test did not move between the two SHAs.

## SC evidence

| SC | Test | Anchor |
|---|---|---|
| SC-01 | case 1 | `test-layout-migration.py:161-174` |
| SC-02 | case 2 | `test-layout-migration.py:176-181` |
| SC-03 | case 3 | `test-layout-migration.py:183-191` |
| SC-04 | case 4 | `test-layout-migration.py:193-198` |
| SC-05 | case 6 | `test-layout-migration.py:217-222` |
| SC-06 | cases 7, 8 | `test-layout-migration.py:224-236` |
| SC-07 | case 9 | `test-layout-migration.py:238-244` |
| SC-08 | (x.1)-(x.3) | `test-check-state.py:1649-1683` |
| SC-09 | T-03 verify (CI config, inspection) | `.github/workflows/tests.yml` — Layout gate step, ran verify script directly, `ok T-03 verify` |
| SC-10 | inspection — `git diff --name-only 88b1182..ea476fd` scope | 8 source files + expected feature/plan/notes artifacts, nothing else |
| SC-11 | grep `TemporaryDirectory` | `test-layout-migration.py` (20 occurrences), `test-check-state.py` (48 occurrences) |
| SC-12 | cases 14, 15 + (x.4) | `test-layout-migration.py:276-299`, `test-check-state.py:1685-1692` |
| SC-13 | case 16 | `test-layout-migration.py:300-`(check block) |
| SC-14 | cases 5a, 5b | `test-layout-migration.py:200-215` |
| SC-15 | (x.1) | `test-check-state.py:1649-1663` |

## Non-finding

The `check-domain.sh --post` OVER BUDGET noise emitted when the worktree was created (about
`FEAT-02` and `FEAT-05-pyyaml-file-parsers` `STATE.md` shape) is pre-existing at `ea476fd`, unrelated
to this diff and not a finding of this gate — omitted from `coverage_gaps`/`open_questions`.

## Coverage gaps

None found against Phase 1 expectations (derived from BRIEF SC-01..SC-15 and plan.yaml task
`change_type`s before code was read): every SC above has a named, content-asserting test. Cases 1
and 15 not asserting doc-root count non-zero was already ruled redundant at source (V-1, info) —
not reopened.

Worktree `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/qa-feat20-gate` created for this
audit, verified `git status --porcelain` clean, and removed via `git worktree remove` before this
note was written.
