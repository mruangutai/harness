# Receipt — FEAT-1559 T-03 (2026-10-05)

Executed directly in the main session under DEC-174.

## What changed

- **`feature_corpus.py`**, the seam every reader now goes through:
  - **`population(root)`**: the landed records at the owner root, with this checkout's own
    directories in place of their landed copies. In a main checkout it first confirms every
    tracked feature directory is present. Outside git it is whatever is on disk.
  - **`corpus_roots(root)`**: `[root]`, or `[root, owner]` from a linked worktree, built from
    `.git` pointer files with no subprocess.
  - **`corpus_path(root, rel)`**: a path inside a feature directory this checkout does not
    hold is read at the owner root. Anything else stays local, absent or not, so a file missing
    from this checkout's own feature is never answered from a stale landed copy.
  - **`verify_layout` / `verify_report_findings` / `layout_refusal`**: the `--verify` report
    parser moved here from `check_state/corpus.py`, so the gates and the checker share one.
  - **`owner_root`'s refusal** now reads "owner manifest is not readable: …", the same wording
    `check-plan-routes.py` already used for that condition.
- **`harness_boundary.linked_worktrees`**: a caller inside a linked worktree normalises to its
  owner, so the peer list is the same from the owner and from any worktree. No subprocess.
- **`check-domain.py`**: the post-write sweep skips the caller's own checkout after
  normalisation. The hardlink scan is marked `checkout-local` and otherwise unchanged (D-14).
- **`merge-gate.py` `feature_for`** and **`branch-create-gate.py`'s flow check** read
  `population()` after `layout_refusal()`. A broken layout or an unreadable corpus denies through
  the existing `permissionDecision` payload. `branch-create-gate.py` now allows a flow landed at
  the owner and absent locally.
- **Repo-wide discovery** reads the landed corpus from a sparse worktree:
  - `board_lifecycle._feature_dirs` uses `population()`; a corpus failure is a STATUS finding.
  - `check-plan-routes.discover_plans` walks `corpus_roots()`, keyed on `<segment>/<name>`.
    `_task_files` reads a classification row's plan through `corpus_path()`.
  - `validate-feature-json.discover_paths` uses `population()`; a corpus failure exits 3.
- **Two more readers of other features' files**, found when the suite ran in this sparse
  worktree:
  - `check-decision-anchors.check_anchor` counts lines through `corpus_path()`. An unreachable
    corpus exits 2.
  - `check-skill-refs._resolves` resolves through `corpus_path()`; an unreachable corpus is a
    "cannot be checked" finding. This is INV-48's checker, and it resolves the INV-48 conflict
    recorded in STATE.md: the `harness-simplify` citation of a FEAT-23 note keeps its
    `<HARNESS_FEATURE_TREE_ROOT>` anchor and resolves in the main corpus. No re-anchoring, and
    no `check-instruction-paths.py` change.
- **Census markers**: `digest_destination.py`, `layout_migration.py` (both sites) and
  `check-domain.py`'s hardlink scan are `checkout-local`. `check-plan-routes.py`'s walk is
  `owner-root`, in a file that names `feature_corpus`.

## Deviations from the plan text, with reasons

All of the following were recorded through `plan-merge.py amend` on T-03 `files`.

- **The seam and T-02's parser.** `corpus_path`, `corpus_roots` and the shared report parser
  went into T-01's `feature_corpus.py`, and the parser left T-02's `check_state/corpus.py`
  (its rules test followed). One parser, not two.
- **Five suite files and two readers outside the plan.** Once this worktree went sparse, the
  following failed because they read another feature's file from the checkout:
  - unit: `test-factory-cli.py`, `test-check-skill-refs.py`, `test-feature-json-budget.py`,
    `test-plan-depends-on.py`;
  - integration: `test-check-decision-anchors.py`, through `check-decision-anchors.py`;
  - `check-skill-refs.py` (above).

  Each now reads through the seam. SC-06 only promised green suites in a plain clone, but
  every Harness developer runs the suites in a worktree, so these were regressions this
  feature caused. The census could not catch them: it covers glob enumerations under `bin/`,
  not named single-file reads or tests.
- **`test-check-plan-routes.py`** copies `feature_corpus.py` beside its lone script copy, as it
  already does for the script's other direct dependencies.
- **`f58_sparse_fixture.py`** no longer ships a `fleet.yaml`. A fixture with a fleet declaration
  is a factory, and both write guards then demand a valid one, which blocked every write before
  the corpus question was reached. `.harness/factory/README.md` keeps the subtree tracked.
- **`tests/unit/test-feature-corpus.py` renamed** to `test-feature-corpus-discovery.py` through
  a T-01 amendment. It clashed with this task's integration file (`run-unit-tests.py` refuses the
  same basename in both kinds).
- **`layout_fixtures.py` and `dispatch-guard.py`** stay in `files` but needed no edit:
  - `layout_fixtures.py`'s glob text lives inside string literals;
  - `dispatch-guard.py` has no statically resolvable feature enumeration;
  - the census confirms neither is a detected site.

## Red before implementation

The eleven production files T-03 touched were stashed (`git stash push`), then the three plan
verify files ran against the pre-change code:

- **`tests/unit/test-feature-corpus-gates.py`**: exit 1. Five errors (`population` and
  `layout_refusal` absent), plus the `linked_worktrees` parity failure (a worktree caller listed
  nothing).
- **`tests/integration/test-feature-corpus.py`**: exit 1, 11 of 18 failing:
  - **corpus reads**: missing owner root, missing landed path, in-progress sibling (3 errors);
  - **merge-gate**: duplicate claim between two other landed features, missing landed
    directory, broken layout;
  - **branch-create-gate**: landed-flow allow, broken layout;
  - **discovery**: validate-feature-json scan count and refusal, check-plan-routes count.

  The cross-checkout byte reads, the unknown-flow deny and both write-guard routes passed
  pre-change. They are controls: those reads and refusals do not depend on T-03's code.
  Separately, the absence half of SC-02 was observed failing on unconverted checkouts: in a
  fresh worktree, a fleet planning worktree and a pin, the other feature was materialised
  locally (all three `True`).
- **`tests/integration/test-feature-corpus-census.py`**: exit 1. Four unmarked detected sites:
  `check-domain.py:2480`, `digest_destination.py:27`, `layout_migration.py:190`, `:191`.

## Green

| Command | Exit | Cases |
|---|---|---|
| `python3 tests/unit/test-feature-corpus-gates.py` | 0 | 11 |
| `python3 tests/integration/test-feature-corpus.py` | 0 | 18 (~10 s) |
| `python3 tests/integration/test-feature-corpus-census.py` | 0 | 7 |
| `python3 tests/integration/test-check-plan-routes.py` | 0 | — |
| `python3 tests/integration/test-check-decision-anchors.py` | 0 | — |
| `python3 tests/unit/test-check-skill-refs.py` | 0 | 10 |
| `python3 .claude/skills/harness/bin/check-skill-refs.py` (this sparse worktree) | 0 | 73 files |
| `python3 .claude/skills/harness/bin/check-plan-routes.py --canonical-reader-audit` | 0 | 0 unresolved, 99 files |

Canonical-reader classification:

- two rows followed their sites (`feature_corpus.py::_entry`, `feature_corpus.py::verify_layout`);
- merge-gate's `feature_for` `json_file` row was removed, because its read now goes through
  `population()`;
- `scanned_files` was regenerated from the live tree.
