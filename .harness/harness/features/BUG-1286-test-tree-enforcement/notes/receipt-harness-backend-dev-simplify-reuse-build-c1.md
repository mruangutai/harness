# SIMPLIFY / REUSE — BUG-1286-test-tree-enforcement (build, c1)

## BLUF

One real finding: `git_commit()` is defined twice, nearly identically, across
`tests/unit/test-suite-layout.py` and `tests/integration/test-run-unit-tests-layout.py` — both
additions of this feature's own commits, with no importable shared test-fixture module in the tree
for either to reuse. Everything else I looked at that resembles duplication is either explicitly
settled (D-01/D-04, the four-site sole-implementation exemption) or a pre-existing, repo-wide test
idiom that predates this feature and is out of scope.

## Findings

### F1 — `git_commit()` duplicated verbatim (minus one flag) across two test files

- **File/line**: `tests/unit/test-suite-layout.py:162-167` and
  `tests/integration/test-run-unit-tests-layout.py:38-43`.
- **Summary**: both files define their own `git_commit(root, message="fixture")` helper —
  `git add -A` followed by a `git -c user.email=... -c user.name=... commit -q -m <message>` — with
  no shared import between them. The only difference is `capture_output=True` on the integration
  version's `subprocess.run` calls.
- **Concrete cost**: this feature introduced both copies in its own two commits (`66b068a4` added
  the unit-test copy, `bd4973d3` added the integration copy) — confirmed by `git show <sha> --
  <path> | grep git_commit`, so this is fresh duplication, not inherited history. Any future change
  to the fixture identity (committer name/email, `-q` verbosity, adding `--no-verify` once a hook
  exists) must be applied in both places by hand; the two are already one flag apart
  (`capture_output`), which is exactly the kind of silent drift the dispatch's cost model names —
  the second site is the one nobody remembers to touch.
- **Alternative**: factor `git_commit` (and, if the lead wants to go further, `base_git_fixture`'s
  git-init preamble) into one small importable helper — e.g. a `tests/support/` module, or simply
  have one file import the function from the other via `sys.path` the same way both already import
  `suite_layout` from `bin/`. Either keeps one spelling instead of two.
- Note: I deliberately did **not** extend this finding to the larger fixture builders
  (`base_git_fixture()` in test-suite-layout.py vs. `tree()`/`git_tree()` in
  test-run-unit-tests-layout.py) — those build genuinely different trees (one drives
  `suite_layout.violations()` directly and needs a copy of `suite_layout.py` itself plus a
  `tests/manual` probe fixture; the other drives the real `run-unit-tests.sh` end-to-end and needs
  copies of `run-unit-tests.sh`, `harness_boundary.py`, `run_pool.py`). Collapsing those would cost
  more clarity than it recovers, so I scoped the finding to the one exactly-duplicated primitive.

## Considered and dropped

- **Unifying `RESTRICTED_NAME_PATTERNS`, `AGNOSTIC_NAME_PATTERNS`, `SOURCE_EXTENSIONS` across the
  three clauses / files** — REFUSED by D-01/D-04 (settled item 1/3). The tuples are deliberately
  importable at module level precisely so `tests/manual/suite-census.py` can import them directly
  without going through `is_test_shaped`. Not raised as a finding.
- **`tests/manual/suite-census.py`'s `_vocabulary_paths`/`_disposition` re-deriving the same
  agnostic/restricted/extension boolean logic that `is_test_shaped()` already encodes, instead of
  calling `is_test_shaped()` directly** — looks at first glance like exactly the re-spelling settled
  item 4 forbids. But `tests/unit/test-suite-layout.py:21-26` names
  `.claude/skills/harness/bin/suite_layout.py`, `tests/unit/test-suite-layout.py`,
  `tests/integration/test-run-unit-tests-layout.py` and `tests/manual/suite-census.py` as **exactly
  four expected implementation sites** in `SOLE_IMPLEMENTATION_EXEMPTIONS`, self-policed by a sweep
  (`sole_implementations`/`sole_implementation sweep`, lines 42-52 and 114-117) that fails if a
  *fifth* site appears. `suite-census.py` also needs a three-way disposition
  (`in-tests-tree`/`documented-exception`/`out-of-vocabulary`/`violation`) that plain
  `is_test_shaped()` cannot produce alone — it needs the `agnostic`/`restricted` booleans
  separately. This is a certified, load-bearing second site, not an oversight. Dropped under
  settled-citation (item 4) plus the design's own self-policing test.
- **`check(name, condition, detail="")` defined separately in every test file in scope
  (`test-suite-layout.py:37-40`, `test-run-unit-tests-layout.py:11-13`)** — confirmed by a
  repo-wide grep that this exact helper is independently redefined in at least four *other*
  pre-existing test files outside this feature's scope (`test-run-unit-tests-kinds.py`,
  `test-handoff-done-when.py`, `test-instruction-workflow-gate.py`, plus a near-variant in
  `test-instruction-workflow-gate.py`). It is a repo-wide, self-contained-script convention that
  predates BUG-1286 by at least one prior feature; this feature did not introduce it and fixing it
  would reach far outside the reviewed scope. Dropped as out-of-scope, not a false positive.
- **`suite_layout.py`'s `tracked_paths()` duplicating a check some other `bin/` module already
  performs** — searched `.claude/skills/harness/bin/` for another Git `ls-files`/toplevel-guard
  helper; found none. `run-unit-tests.sh` and `harness_boundary.py` do not implement an equivalent
  tracked-file enumeration. No finding.
- **`suite-census.py`'s `_measure`/`_vocabulary_paths` duplicating `suite_layout.violations()`
  itself** — they overlap in vocabulary (both look at tracked test-shaped files outside `tests/`)
  but serve different purposes (`violations()` is a fail-fast gate; `_measure`/`tree-audit` is a
  full census with per-path disposition for human review) and already share their vocabulary via
  the settled tuple imports (item 3). No further reuse available without collapsing the
  gate/census distinction, which is out of scope for this pass.

## Angle conclusion

REUSE surfaces exactly one concrete finding (F1). No other candidate survives — most of what looks
like duplication here is either a certified, self-policed exception (the four sole-implementation
sites) or a pre-existing repo convention this feature did not introduce.
