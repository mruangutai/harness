# REUSE angle — FEAT-58-corpus-outside-worktree plan review

Six findings. All flag-only (plan surface); routed to harness-pm.

## F1 — T-03 verify omits check-state.sh's own existing regression suite
- Anchor: plan.yaml T-03 `verify:` (line 196-197): `python3 tests/integration/test-check-state-corpus.py`
- The tree already carries six test files exercising check-state.sh through the shared
  `tests/integration/check_state_support.py` driver (SCRIPT env override, `make_fixture`, `run`):
  `test-check-state-entry.py:1-2`, `test-check-state-handoff.py`, `test-check-state-inv26.py`,
  `test-check-state-plans.py`, `test-check-state-records.py`, `test-check-state-worktrees.py`.
  None is named in T-03's verify command.
- Cost: T-03 rewrites check-state.sh's corpus-enumeration internals (21 glob sites per its own
  intent). The task's own gate proves only the one new behaviour; a regression in any of the six
  pre-existing invariant families (INV-9/21/24/28/30 etc.) is invisible to this task's verify and
  ships until whatever later step happens to run the full suite.
- Alternative: append the six existing files to T-03's verify line, the same way T-01 already
  chains `test-corpus-boundary.py && test-harness-boundary.py`.
- Severity: med

## F2 — T-04 verify omits each validator's own existing test
- Anchor: plan.yaml T-04 `verify:` (line 249-250)
- `board_lifecycle.py` already has `tests/integration/test-board-lifecycle.py:1-13` (targets it by
  name); `check-plan-routes.py` already has `tests/integration/test-check-plan-routes.py:1-5`;
  `validate-feature-json.py` already has `tests/integration/test-validate-feature-json.py:1-6`;
  `layout_migration.py` already has `tests/integration/test-layout-migration.py:1-5`. None of the
  four is in T-04's verify, which runs only the two new corpus-sweep-validators files.
- Cost: T-04 touches four independent modules' glob sites in one task. Its verify can pass while
  any one of the four regresses its pre-existing, module-specific behaviour (e.g.
  validate-feature-json.py's schema checks), because that module's own suite never runs as part
  of this task's gate.
- Alternative: chain all four pre-existing files into T-04's verify alongside the two new ones.
- Severity: med

## F3 — T-06 verify omits check-domain.sh's existing suite, and doesn't name the shared driver
- Anchor: plan.yaml T-06 `verify:` (line 338-339); intent line 357-358 ("follow the conventions
  in tests/integration/test-check-domain-worktree.py")
- check-domain.sh already has seven sibling test files (`test-check-domain-approval.py`,
  `-artifact.py`, `-claims.py`, `-grant.py`, `-post.py`, `-worktree-parity.py`, `-worktree.py`),
  all built on the shared `tests/integration/check_domain_support.py:1-51` module, whose docstring
  (`check_domain_support.py:13-18`) states explicitly that this split exists so new additions
  reuse `drive()`/`_env()` rather than hand-roll a subprocess harness. T-06's intent names one
  sibling file for "conventions" but never names the shared module, and T-06's verify runs only
  the new file.
- Cost: the new `test-check-domain-corpus-hardlink.py` is the natural eighth member of this
  family; without naming `check_domain_support.py` the implementer re-derives `_env()`'s
  CLAUDE_PROJECT_DIR/HARNESS_PROJECT_DIR double-set (`check_domain_support.py:36-51`) and the
  `CHECK_DOMAIN_BIN` override convention by hand — a second spelling of both that can drift the
  next time the shared module changes, and the seven-file suite never gates this task's own edit.
- Alternative: name `check_domain_support.py`'s `drive()`/`_env()` explicitly in T-06's intent as
  the required import, and add the existing seven files (or at minimum
  `test-check-domain-worktree.py`) to T-06's verify chain.
- Severity: med

## F4 — T-08 verify omits feature-worktree.py's own existing test file
- Anchor: plan.yaml T-08 `verify:` (line 427-428)
- `tests/integration/test-feature-worktree.py:1-4` already tests feature-worktree.py's `create`,
  `list`, `path` and `remove` subcommands via subprocess CLI invocation — T-11 later adds cases to
  this same file, confirming it is live and load-bearing. T-08's verify runs only the two brand
  new files it creates.
- Cost: T-08 changes `cmd_create` (adds the two new steps). A regression to `create`'s existing
  contract (return codes, printed destination, `list`/`path` interplay) is not caught by T-08's
  own verify; it surfaces only if/when T-11's later task happens to run this file.
- Alternative: add `test-feature-worktree.py` to T-08's verify chain.
- Severity: med

## F5 — the required-path positive control is defined once (T-08) but only described, never named, for its second caller (T-09)
- Anchor: plan.yaml T-08 intent (line 449-459, `REQUIRED_WORKTREE_PATHS`); T-09 intent (line
  514-517, "the SAME required-path existence positive control T-08 defines")
- T-08 defines a concrete named set (`REQUIRED_WORKTREE_PATHS`) and a check inside
  `feature-worktree.py`. T-09's `migrate-worktree-corpus.py` is told only that step 4 runs "the
  SAME" control — no function name, no constant name, no instruction to import it. Contrast: the
  plan is explicit elsewhere that `migrate-worktree-corpus.py` imports
  `feature-worktree.sparse_include_list` (same step 4, same sentence) via the module's own name,
  and T-08's own test does the actual cross-module import work (`importlib`, because the module
  name carries a dash) — but that importability is only demonstrated for the test, never stated
  as the production contract for T-09.
- Cost: without a named symbol, the natural reading is that `migrate-worktree-corpus.py` restates
  the six-entry required-path list and its existence-check loop as its own literal, alongside the
  one in `feature-worktree.py`. A future required path (the plan itself notes `.agents` was once
  omitted from an enumerated list at D-03) then needs editing in two files, and the one nobody
  remembers goes stale silently — precisely the failure mode this skill's REUSE section names.
- Alternative: T-08 names `REQUIRED_WORKTREE_PATHS` and its check as a public, importable
  function (e.g. `verify_required_paths(root)`) in `feature-worktree.py`; T-09's intent is amended
  to say explicitly that `migrate-worktree-corpus.py` imports and calls that function via
  `importlib`, not a re-derived list.
- Severity: high — this is exactly the two-spellings-in-lockstep case the skill instructs readers
  to name concretely, and it sits on a positive control (the only thing that makes an empty/wrong
  cone loud per D-03); a silently-diverged second copy defeats that control's purpose for the
  migration path specifically.

## F6 — the `git show <sha>:<path>` RED-FIRST idiom recurs five times with no named authority for `<sha>`
- Anchor: plan.yaml lines 231 (T-03d), 282 (T-04), 319 (T-05a), 361 (T-06a), 643 (T-12a)
- Five occurrences, each independently instructing "run the pre-change script from
  `git show <sha>:<path>`" as a RED-FIRST fixture input. The plan names `resolved_at: abff2a84`
  for the *lanes* routing decision (line 9) and cites `abff2a84` twice more for line-number
  provenance (lines 205, 267) — never for what `<sha>` should resolve to in the five RED-FIRST
  sites. T-14's `git show <review_sha>:<path>` (line 720) is a different, already-authoritative
  concept (the pinned review sha) and is not confused with this.
- Cost: five separate implementers (T-03, T-04, T-05, T-06, T-12 — several main-session-direct,
  several team-dispatched) independently choose what commit-ish `<sha>` means. A plausible split
  is "the commit immediately before my own task's edit" vs. "the feature branch's merge-base with
  main" (the latter already the convention this repo uses elsewhere, e.g.
  `code-grade.py --base "$(git merge-base origin/main HEAD)"` per harness-code-risk-grading). If
  two tasks resolve it differently, one task's "pinned reproduction of the failing state" (T-03,
  T-05, T-06 all say the RED assertion must stay in the file permanently) can end up pinned
  against a `<sha>` that includes another one of this same plan's earlier tasks' fixes, silently
  changing what the kept assertion actually proves.
- Alternative: name the resolution once — e.g. a plan-level note or D-11 stating `<sha>` is the
  merge-base of the feature branch with the default branch at task-execution time (mirroring the
  `git merge-base origin/main HEAD` convention already used for `code-grade.py`) — and have all
  five task intents reference that one authority instead of restating "the pre-change copy" five
  times with no named commit-ish.
- Severity: med

## Not flagged
- T-01, T-02, T-05, T-11, T-12 (test-dispatch-guard.py already existing and extended, not
  duplicated), T-13, T-14, T-15's own verify chains: either already chain the pre-existing test
  they extend, or edit new files with no pre-existing analog. Not REUSE findings.
- tests.yml's repository-state gate (lines 292-312) and T-08's instruction to mirror it
  (deriving the positive control from `git ls-files`, not from the checker) is correct reuse of
  an existing pattern, not a finding.
