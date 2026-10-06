# Receipt — FEAT-1559 T-02 (2026-10-04)

Executed directly in the main session under DEC-174.

## What changed

- **`check_state/corpus.py` (new)**:
  - **`preflight()`** runs before `Ctx` is built.
    - In a record-bearing linked worktree it calls `worktree-state.py --verify --json`, never
      `--repair`, and reads every finding in the report.
    - Cone (3), skip-bits (4) and materialisation (7) refuse. Dirty (8) is a note.
    - An unusable or unknown report refuses.
    - It settles the subject: the active feature by default; an explicit `--feature` must name a
      local directory.
    - It compares expected and reached feature-directory names (record-less directories
      included). A missing name refuses with "N of M"; an unexpected-only name is a note.
  - **`inv_52`**: branch claims across landed records, from the main corpus, on demand.
- **`check_state/ctx.py`**:
  - The BRIEF, PLAN, plan.yaml, STATE.md and abandoned loads read only the selected feature
    directories.
  - The enumeration carries `# corpus-scope: checkout-local`.
  - `Ctx(scoped, owner)` and `population()` were added. Unscoped runs keep their old semantics.
    Scoped runs see every landed record, with the active record in place of its landed copy.
- **`check_state/board.py`**: INV-24's factory-claim population reads `ctx.population()`. An
  unreadable main corpus is reported (CANNOT VERIFY), never treated as empty.
- **`check_state/runner.py`**: the preflight runs before `Ctx`; refusals print and exit 1;
  `--list` is unchanged.
- **`check_state/table.py`**: INV-52 is registered in a new `branch-claims` group (repo scope;
  reads `feature.json` and `git:ls-tree`; authority DEC-95).
- **`check-plan-routes.py`**: the `ROW_FAMILIES` map gained `"corpus": ("INV-52",)`. The
  structure lock requires every row to name its family.
- **`feature_corpus.tracked_dirs`**: an unborn HEAD (no commit yet) tracks nothing, so the
  result is empty rather than an error. A fixture with `git init` and no commit is the case that
  showed it.
- **Canonical-reader classification**: one exempt `json_string` row for `corpus._verify`, and
  the scanned-file manifest regenerated from the live tree.

## Deviations from the plan text, with reasons

- **INV-29 is unchanged.** `worktree_terminal` already resolves landed terminal state from the
  owner's default branch through git objects (`ls-tree` / `cat-file`), whatever the caller's
  layout. Routing it through the owner-file view would replace a fixed-commit read with a
  mutable working-tree read and gain nothing.
- **INV-26 is unchanged.** It already compares per feature over `ctx.features`, which is the
  selected subject. Narrowing in a sparse worktree is the same narrowing `--feature` already
  applies. INV-24's factory-claim collision is the repo-wide record predicate that a one-feature
  population would silently shrink, so that is the one routed through the owner view.
- **Unit test renamed** to `tests/unit/test-check-state-corpus-rules.py`, because
  `run-unit-tests.py` refuses a basename present in both kinds. The change was recorded through
  `plan-merge.py amend` on T-02 `files` and `verify`.
- **Fixture fleet file** gained `schema: factory-fleet/1`, so the fixture's checker output
  carries no unrelated fleet-schema findings.

## Red before implementation

T-02's production edits were stashed and `corpus.py` moved aside, then both test files ran:

- `tests/unit/test-check-state-corpus(-rules).py`: exit 1,
  `ImportError: cannot import name 'corpus'`.
- `tests/integration/test-check-state-corpus.py`: exit 1, 11 of 13 failing. The failing cases:
  - open confinement;
  - missing record-less directory;
  - missing selected feature;
  - structural break;
  - untracked extra directory;
  - unusable report;
  - dirty-only;
  - dirty plus structural;
  - `--list`;
  - duplicate branch between two other landed features;
  - full/sparse agreement.

  The two cases that passed pre-change are positive controls: a plain clone keeps the full
  audit, and a converged worktree holds only its own directory.

## Green

| Command | Exit | Cases |
|---|---|---|
| `python3 tests/unit/test-check-state-corpus-rules.py` | 0 | 13 |
| `python3 tests/integration/test-check-state-corpus.py` | 0 | 13 (~8 s) |

On the main checkout, the new checker reports the same 23 violations as `main`'s checker, line
for line. It adds one non-gating note, for the untracked `kaya/FEAT-01-kaya-platform`
directory. INV-52 is clean over the 116 landed records; the FEAT-02 / FEAT-03-subissue-mirror
pair is exempt.
