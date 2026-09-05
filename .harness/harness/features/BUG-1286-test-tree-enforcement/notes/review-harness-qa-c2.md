# QA test-matrix gate — cycle 2, re-pinned `bb3a31ed`

BLUF: **matrix_ok: true.** Every orchestrator-reported number reproduced exactly. `unit` and
`integration` (the floor for `cross_module`, T-01's `change_type`) both satisfied. B-3's new
assertion has real, narrow discriminating power — verified live, not accepted on the eng squad's
say-so. One genuine coverage gap found and it is real: no test catches a reordering between the
two *categories* of finding (tracked-scan vs registry), only within-category order. Not gating —
B-1 is measured behaviour-preserving on every path a test does exercise — but it is the same class
of blind spot that hid the cycle-1 finding, so it is reported plainly rather than folded into "PASS
means nothing to see here."

## Change-type / matrix floor
`plan.yaml` T-01 (the only task touching `suite_layout.py`): `change_type: cross_module`. Matrix
(`harness.json:173-178`) → `always: [unit, integration]`. No `config`-shape trigger (no task sets
`touches_config_shape`). Floor is unit+integration; both required and both run.

## Literal re-measurement (worktree `BUG-1286-test-tree-enforcement`, HEAD `be46f5d4`, diff vs
`bb3a31ed` outside `.harness/harness/features/` is empty — confirmed)

| Orchestrator claim | My measurement | Match |
|---|---|---|
| unit exit 0, 342 PASS / 0 FAIL, 27 files | exit 0, **342 PASS / 0 FAIL**, 27 script-level PASS lines | ✅ exact |
| `test-suite-layout.py` alone: 47 checks, exit 0 | ran standalone: **47 `PASS` lines, exit 0** | ✅ exact |
| integration exit 0, 14 PASS / 0 FAIL | full `--kind integration`: exit 0, 46 files, **1240 `PASS`/1787 `ok` lines, 0 FAIL** (whole-bucket total, not what "14" describes); `tests/integration/test-run-unit-tests-layout.py` alone (the file this diff actually touches): **exit 0, 14 `PASS`, 0 FAIL** — orchestrator's "14" is this file's count, not the bucket's. Both true; worth the correction so a later reader doesn't take "14" as the whole integration suite. | ✅ (scoped correctly) |
| `--check-layout` exit 0 | exit 0 | ✅ |
| tree-audit TOTAL 85 OUTSIDE 9 VIOLATIONS 0 | read `notes/qa-tree-audit.md` BLUF verbatim: TOTAL 85, OUTSIDE 9, VIOLATIONS 0 at `4b343d80` — did not re-run tree-audit myself (author-nothing dispatch, note is the pinned record); consistent with a clean `--check-layout` | ✅ (accepted on record, corroborated by check-layout) |
| `check-state.sh` exit 0, no note for this feature | exit 0; scanned full output — every emitted `note` line names a *different* feature (FEAT-29, BUG-1128, FEAT-15, FEAT-20, FEAT-02, FEAT-05, FEAT-43, INV-28/BUG-1081); none names BUG-1286 | ✅ |

## Which of the 12 new helpers a test can actually redden
All 12 (`_unit_integration_findings`, `_runner_selection_findings`, `_bin_planted(_findings)`,
`_tracked_scan`, `_tracked_outside_tests_findings`, `_duplicate_or_malformed`,
`_unnecessary_or_stale`, `_entry_finding`, `_registry_findings`, `_is_untracked_exclusion`) are
called **only** through the public `violations()` entry point — none is named directly in the test
file (`grep` count 0 each). That is correct test hygiene (black-box over the seam that matters), and
every one of the 12 is reached by a case that could go red: cases 1/3/8/10 redden
`_tracked_outside_tests_findings`/`_is_untracked_exclusion`; case 6 reddens all four registry rules
(`_duplicate_or_malformed`, `_unnecessary_or_stale` via `_entry_finding`/`_registry_findings`); case
4 reddens `_tracked_scan`'s ls-files-failure branch; "duplicate"/"empty unit"/"empty integration"
redden `_unit_integration_findings`; "nested test"/"undiscoverable test name" redden
`_runner_selection_findings`; "planted bin test" reddens `_bin_planted`/`_bin_planted_findings`.
None is "only reached incidentally."

**Two paths are NOT reddened by anything, and I verified both live, not by inspection alone:**

1. **`tracked_paths()`'s toplevel-mismatch `LookupError`** (suite_layout.py:74, "`{root} is not the
   toplevel of its own Git index`") — `grep` across `tests/` for that message: zero matches. Case 4
   only exercises the *ls-files*-failure branch of the same `except LookupError` in `_tracked_scan`,
   never the toplevel branch. D-03's own text names this exact branch as "the one way this refactor
   could fail-open." I read the code directly (not the docstring's claim) and confirmed the
   structural ordering is correct: `tracked_paths()` raises before `_tracked_scan` ever reaches the
   self-ownership line (`suite_layout.py:192-200`), so today's code is right — but nothing in the
   suite would catch a future edit that broke it. **Finding, med, coverage gap** — reasoned from
   code reading (structurally correct today), not proven by a red mutation, because I hold no write
   grant outside `tests/**` and could not add the missing fixture myself (author-nothing dispatch
   either way).
2. **Cross-category finding order** (file findings before registry findings). I proved this one
   live: built a synthetic git fixture that trips both a tracked-outside-tests violation and a
   registry violation in one `violations()` call, confirmed today's order is file-then-registry, then
   monkeypatched a **swapped** `violations()` (registry-then-file, same helper calls) into
   `sys.modules['suite_layout']` and re-executed the real, unmodified `tests/unit/test-suite-layout.py`
   against it: **all 47 checks still printed PASS.** No existing assertion is sensitive to this
   ordering — cases 1/3/4/5/9 assert exact ordered lists but each only ever contains findings from
   one category at a time; case 6/7 are registry-only. This is exactly the narrowness class the
   dispatch called out: an assertion that only ever sees one category can't bind the seam between
   categories. **Finding, med, coverage gap** — mutation-proven, not reasoned.

## B-3's assertion — verified, not accepted on report
`check("violations() has exactly one non-test caller repository-wide", set(_violations_callers(...))
== {".claude/skills/harness/bin/run-unit-tests.sh"}, ...)` (`test-suite-layout.py:173-176`).

Read `_violations_callers`/`_is_violations_invocation` verbatim (`test-suite-layout.py:145-170`):
filters to `git ls-files`-tracked, non-`tests/`-prefixed, `SOURCE_EXTENSIONS`-only
(`.py .sh .ts .tsx .js .mjs .cjs` — **`.md` is not a source extension**), skips comment lines, and
requires the regex `suite_layout\.violations\(\s*[^)\s]` (an argument present, not a bare
zero-arg mention).

Ran the **real, unmodified** functions (loaded by `exec`-ing the actual test file source with `check`
stubbed, so no reimplementation risk) against:
- the live repo → returns exactly `['.claude/skills/harness/bin/run-unit-tests.sh']`, matching the
  assertion — today's PASS is real, not vacuous.
- a synthetic git-tracked repo with `caller.py` (`x = suite_layout.violations(".")`, a genuine
  argument-carrying call) and `prose.md` (text reading `"...called with an argument like
  violations(\"/x\")"`, deliberately shaped to look like a call) → returned `['caller.py']` only.

This proves both halves of the audit: **(a)** a genuine second call site anywhere in the tree is
detected — `set(...)` would then have two elements, which can never equal the pinned one-element
set, so the check reddens deterministically; **(b)** the `.md` prose case is invisible *because it
is not a source extension*, not because of some regex leniency — so the nine `notes/`/`BRIEF.md`
files mentioning `violations()` in text cannot spuriously redden this check, and prose can't spoof a
green either. Also directly checked the docstring-exclusion the comment claims:
`suite_layout.violations()` (zero-arg) → `False`; `x = suite_layout.violations(".")` → `True`;
`"""suite_layout.violations() mention"""` (arg-shaped but inside a triple-quoted string on one
line) → `False`. All match intent. **Verdict: real discriminating power, not vacuous, not
satisfiable/falsifiable by prose. Measured, not reasoned.**

## D-03 ordering (toplevel precondition before self-ownership)
Read `suite_layout.py:44-76` (`tracked_paths`) and `:184-200` (`_tracked_scan`) directly.
`tracked_paths()` raises `LookupError` on toplevel mismatch (line 74) *inside the same function*
that produces the tracked-file list; `_tracked_scan` calls it (line 195) and only reaches the
self-ownership line (198) if it returns without raising. Structurally, toplevel-before-self-ownership
holds exactly as D-03 requires. (Coverage gap on this exact branch reported above — structurally
correct, not test-proven.)

## Registry rules / LookupError routes / vocabularies
- All four registry self-policing rules (glob-shaped, duplicate, non-test-shaped, untracked) fire
  independently, confirmed live via case 6's five sub-checks, all PASS.
- Both `LookupError` routes in `_tracked_scan` (ls-files failure, toplevel mismatch) return a
  finding string, never an empty clean list — confirmed by reading the `except` clause; only the
  first route has a fixture (case 4).
- Three vocabularies (`RESTRICTED_NAME_PATTERNS`, `AGNOSTIC_NAME_PATTERNS`, `SOURCE_EXTENSIONS`) still
  meet only inside `is_test_shaped` (lines 29-41) — sole implementation, unchanged by the
  decomposition; case 11's "sole implementation" battery (all PASS) still pins this.

## Backlogged items — not re-raised
Per the shared context I did not re-litigate: the `_registry_findings` self-ownership-scoping med
note, `tracked_paths` grade-2 record, F-1, F-2, case-11 `INAPPLICABLE` branch, integration case 2's
single-sentinel clause, the three stale BRIEF line pins. `_vocabulary_paths` (raised in prior
cycle's simplify pass) lives in `tests/manual/suite-census.py`, not one of the 12 B-1 helpers — out
of this cycle's scope, already assessed-and-dismissed by the c1 code reviewer as a deliberate
residual; I did not re-open it.

## Cleanup / provenance of my own probes
Mutation and helper-driven probes ran in a disposable worktree
(`.claude/worktrees/qa-probe-bug1286`, checked out at `bb3a31ed`) plus a synthetic tempdir repo
(`/tmp/qa_probe_repo`, git-tracked, outside any Harness domain). Neither touched source in the
feature worktree. The disposable worktree was removed with `git worktree remove` (no `--force`) once
its own `git status --porcelain` showed clean. Final state of the feature worktree:
`git status --porcelain` shows only three untracked files belonging to sibling reviewers
(`review-harness-security-reviewer-c2.md`, `review-harness-ui-reviewer-c2.md`,
`observations/harness-ui-reviewer.md`) — none mine. `HEAD` unchanged at `be46f5d4d62b0e512d52880b716963c6f5d2c77a`.

## Verdict basis
Both coverage gaps are genuine and named with a concrete failure scenario each (a future PR that
either (a) reorders the toplevel-precondition-vs-self-ownership check inside `tracked_paths`/
`_tracked_scan`, or (b) reorders the two finding categories in `violations()`) would ship past this
suite silently. Neither is high — today's code is correct on both axes (one proven by direct
mutation, one by structural reading), and neither is required by this cycle's three authorised
remedies (B-1/B-2/B-3), which were behaviour-preservation and one additive assertion, not new
coverage. `gates.review` is `advisory_unless_high`; these are med, so they do not gate. Matrix floor
(unit+integration) fully satisfied with real, non-vacuous, non-incidental coverage.
