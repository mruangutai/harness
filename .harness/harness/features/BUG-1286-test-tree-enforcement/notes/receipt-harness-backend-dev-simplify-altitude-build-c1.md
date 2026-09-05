# SIMPLIFY — ALTITUDE angle — BUG-1286-test-tree-enforcement (build-c1, read-only)

## BLUF

One real altitude finding: `tests/manual/suite-census.py`'s `_disposition` re-derives
`is_test_shaped`'s extension conjunct inline instead of calling the imported predicate, which
contradicts `is_test_shaped`'s own docstring claim of sole-implementation and creates a second
spelling that can drift silently. Recommendation: **fold-in**. Everything else examined sits at
its right home; two likely candidates are settled dead ends, cited below rather than re-argued.

## Finding

**F-1 — `tests/manual/suite-census.py:80-93`** (`_vocabulary_paths` lines 80-84,
`_disposition` lines 92-93)

- **Summary:** `_disposition` re-derives `is_test_shaped`'s exact extension-gate conjunct
  (`restricted and not agnostic and os.path.splitext(path)[1] not in SOURCE_EXTENSIONS`) inline,
  instead of importing `is_test_shaped` from `suite_layout` and branching on its boolean.
  `suite_layout.py:29-34`'s own docstring states: "The sole implementation of the vocabulary:
  the repository-wide clause and the registry self-policing clause in `violations()` both call
  this, and nothing else spells the expression inline" — `_disposition` is a third call site that
  does spell it inline, so the module's own claim about itself is currently false against the
  live tree.
- **Concrete cost:** if `is_test_shaped`'s extension-check logic ever changes (a new source
  extension added, the AND restructured, an extra guard added), `_disposition`'s copy must be
  updated in lockstep or the census's `out-of-vocabulary`/`violation` split silently diverges
  from what the live enforcement guard (`suite_layout.violations()`, called on every
  `run-unit-tests.sh` invocation) actually decides — and nothing catches the drift: the unit
  suite's `sole_implementations()` sweep (`tests/unit/test-suite-layout.py:42-52`) only greps for
  discovery-mechanism fragments (`os.listdir`, `.glob(`, etc.), not for a re-spelled boolean
  conjunct, so this particular duplication is outside what that sweep can ever flag.
- **Alternative:** add `is_test_shaped` to the existing `from suite_layout import (...)` block
  (`tests/manual/suite-census.py:15-20`) and compute `shaped = is_test_shaped(path)` once inside
  `_vocabulary_paths`, then have `_disposition` branch on `restricted and not agnostic and not
  shaped` — same disposition text, same rows, one fewer independent spelling of the extension
  rule. `_vocabulary_paths` already computes `agnostic`/`restricted` itself for other purposes
  (selecting which paths even reach `_disposition`), so only the extension-check conjunct itself
  moves, not the whole function.
- **Recommendation: fold-in.**

## Considered and dropped (dead ends per dispatch)

- **`is_test_shaped` sole-implementation / no `tracked_paths_fn` seam** — the two most likely
  altitude findings on this surface, both already refused: no injectable `tracked_paths_fn` seam
  (`notes/review-harness-eng-lead-plan-c0.md`), and `is_test_shaped` keeps its sole-implementation
  property rather than being duplicated or narrowed (dispatch hard boundary, item 4). F-1 does not
  reopen either of these — it closes a gap in the *second* one that the plan's own text had not yet
  noticed, it does not argue against the property.
- **Unifying the bin clause / under-`tests/` clause / repository-wide clause vocabularies** — three
  deliberately different vocabularies (D-01, D-04 in `plan.yaml`); folding them together is
  REFUSED by decision, not an open question. Not raised as a finding.
- **Whether the repository-wide clause belongs in a caller (the runner or the census script)
  rather than in `suite_layout.py`** — checked directly: `run-unit-tests.sh` is asserted by
  `tests/unit/test-suite-layout.py:140-143` ("runner delegates layout once") to call into
  `suite_layout` exactly once and non-comment, so the runner does not reimplement any part of the
  clause. `tests/manual/suite-census.py`'s `tree-audit` command is a separate one-shot audit tool
  operating over a different Git ref (`--ref`, defaulting to `HEAD`, versus the live-worktree
  enforcement path `violations()` runs), by design (plan.yaml D-01 area, and the commit message
  for T-03: "imports the vocabulary tuples from suite_layout rather than re-declaring them") — the
  audit/enforcement split itself is the right altitude, one live gate and one investigative tool
  reading the same vocabulary; only the extension-conjunct re-derivation inside that tool (F-1) is
  wrong.
- **`tests/unit/test-suite-layout.py` case 11's independent oracle (`_certify_pattern`,
  `_is_inside_tests`, `_literal_key_present`, `ADVERSARIAL_CORPUS`, `_corpus_oracle`)** — this
  deliberately does NOT call into `suite_layout` or reuse its vocabulary; per the plan's own
  GOVERNING SEMANTICS text (`plan.yaml` D-01, lines ~50-111) this is a from-scratch, independently
  derived oracle so it can catch drift in the vocabulary it audits rather than mirror it. Correct
  altitude for a verification oracle, not a duplication of the vocabulary's authoritative statement
  — `offenders()` in the same file (line ~470) does call the real `suite_layout.is_test_shaped`
  for the actual pass/fail boolean, keeping the "which mechanism actually governs" question
  answered once.
- **`{entry[0] for entry in DOCUMENTED_EXCEPTIONS}` repeated as a one-line set comprehension** in
  `suite_layout.violations()`, `suite_layout._registry_findings` (implicitly via the `seen` set),
  `tests/unit/test-suite-layout.py`'s `offenders()`/`select_control_candidate()`, and
  `suite-census.py`'s `_measure()` — considered, dropped: it is a trivial tuple-unpack idiom with
  no branch/conjunct to drift, below the bar of a concrete cost worth an apply.

## Empty-return note

Not applicable — one finding above. No other altitude-shaped issue was found on the four scope
files; the depth of every other capability checked (self-ownership precondition placement in
`tracked_paths`, the bin-clause dedup against the repo-wide clause, the DOCUMENTED_EXCEPTIONS
registry's self-policing) sits in the module or function that already owns the rule it enforces.
