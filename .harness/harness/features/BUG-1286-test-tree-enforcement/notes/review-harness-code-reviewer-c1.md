# Code review — BUG-1286-test-tree-enforcement — review_sha 9adbce6b (c1)

**BLUF: FAIL.** The mechanical code-risk grader — which nothing in this feature's build, QA or
simplify history appears to have run against this diff — reports two production functions in
`suite_layout.py` below their grade-4 bar and not grade-2: `violations` (grade 1) and
`_registry_findings` (grade 3). Per `harness-code-risk-grading`/`harness-code-review`, that is
`SEVERITY: high` on both and `RESULT: FAIL`, independent of everything else in this review.
Everything else I hunted (the fail-open/registry-scoping questions the dispatch weighted highest,
sole-implementation drift, a prior QA disposition I re-verified and found wrong) stays at MED or
is a corroboration of an already-accepted, already-documented residual — none of that gates on its
own, but the grader result does.

`git diff 1977ebd6..9adbce6b` is what I reviewed. Working-tree `suite_layout.py` is byte-identical
to the pinned blob (`diff` empty) so line citations below are safe against either revision.

## Code grade (run first per protocol; drives the digest field)

```
python3 .claude/skills/harness/bin/code-grade.py \
  --base "$(git merge-base origin/main 9adbce6b690cd4b319c3758ab2a16505dd15900e)" \
  --head 9adbce6b690cd4b319c3758ab2a16505dd15900e
```

Blocking (not grade-2, below bar — **must_fix, high**):

- **`violations`** — `.claude/skills/harness/bin/suite_layout.py:101`. cyclomatic 23, cognitive 35,
  ABC 45.7. GRADE 1, bar 4 (production). Driver: cyclomatic+cognitive+abc — all three metrics are
  above even the grade-2 ceiling (cyclomatic<=20, cognitive<=30, ABC<=45). This is the "one reason
  to change per function" violation by the book: it does five orthogonal things in one body — (1)
  unit/integration existence + duplicate-name check, (2) runner-selection shape check over
  `tests/**`, (3) bin-planted-file glob check, (4) the new git-tracked-outside-tests scan
  (existence, enumeration, self-ownership, per-path loop with four `continue`s), (5) delegating to
  `_registry_findings`. Before this feature the file was 34 lines total
  (`receipt-harness-data-engineer-simplify-efficiency-build-c1.md`); this feature's own T-01 task
  is what pushed this function past its bar by adding (4) and (5) inline rather than as named
  helpers — squarely in scope for this review.
- **`_registry_findings`** — `.claude/skills/harness/bin/suite_layout.py:79`. cyclomatic 9,
  cognitive 15, ABC 16.4. GRADE 3, bar 4 (production). Driver: cyclomatic+cognitive. A grade-3
  production function below the grade-4 bar blocks identically to grade 1, per the skill. Four
  self-policing rules (glob-character, duplicate, unnecessary, no-longer-tracked), each its own
  `continue`, one compound boolean (`not is_test_shaped(rel) or rel.startswith("tests/")`) — this
  is new code, added whole by T-01 for D-02's registry.

Grade-2, reasoned (not blocking, **med**, reason required and supplied below):

- **`tracked_paths`** — `.claude/skills/harness/bin/suite_layout.py:44`. cyclomatic 10, cognitive 7,
  ABC 26.6. GRADE 2, bar 4. Driver: abc. **Reason:** the ABC score is inflated by two near-identical
  try/except pairs (`FileNotFoundError`/`TimeoutExpired` around `git ls-files` and again around
  `git rev-parse --show-toplevel`), each raising a distinct, command-specific `LookupError` message.
  Collapsing the two subprocess calls into one shared try/except helper would lower ABC but costs
  the specific "which git command failed" detail in the raised message that `tracked_paths`'s own
  docstring promises ("a one-line reason") and that case 4/case-4-integration's assertions key off
  (`cannot enumerate tracked files under {root}: {error}` — the `{error}` half is what a shared
  helper would have to reconstruct). A plausible trade-off, not obviously wrong, but the grade-2
  result should have been reasoned and recorded before this build closed, not left silent.
- **`_literal_key_present`** — `tests/unit/test-suite-layout.py:405`. cyclomatic 12, cognitive 13,
  ABC 18.4. GRADE 2, bar 3 (test code). Driver: cyclomatic. **Reason:** this is the same function
  already carrying the pre-dispositioned F-1 (tautological conjunct, backlogged in
  `notes/receipt-harness-dev-ops-simplify-simplification-build-c1.md`) — the complexity and the
  tautology share a root cause, the per-prefix wildcard-position scan or-ed with the `_test.`/
  `.test.` infix shortcut. I did not re-litigate F-1's disposition (already accepted as backlog);
  recording here only because grade-2 independently requires its own named reason, which the
  existing F-1 disposition does not supply in code-grade's vocabulary.

`code_grade: fail` — two blocking records exist (not grade-2), which the enum's own rule makes
authoritative regardless of the reasoned grade-2 pair.

## Stage 1 — spec compliance

Read BRIEF.md (325 lines) and plan.yaml D-01..D-06 (lines 33-174) in full.

- D-01 (sole implementation of the vocabulary): honored as amended. `tests/manual/suite-census.py`'s
  `_disposition` was found, by the team's own simplify-altitude pass
  (`notes/receipt-harness-backend-dev-simplify-altitude-build-c1.md`), to re-derive the extension
  conjunct inline, and was folded to call `is_test_shaped` directly
  (`notes/receipt-harness-backend-dev-simplify-apply-build-c1.md`) — verified present at pinned sha
  (`suite-census.py:91-93`). `_vocabulary_paths`'s own `AGNOSTIC_NAME_PATTERNS`/
  `RESTRICTED_NAME_PATTERNS` fnmatch selection (lines 72-85) was explicitly left as a *separate*,
  deliberate, documented residual ("`_vocabulary_paths` untouched — still selects on basename
  patterns with no extension filter, per T-03's intent") — I traced the concrete consequence one
  step further than the existing note does (a future third pattern-group added to
  `is_test_shaped` without a matching `_vocabulary_paths` update would make `tree-audit`'s row set
  under-count relative to what the guard actually refuses, so a future `qa-tree-audit` note's
  "no unexplained match" claim (SC-12) could be silently wrong) but this is a corroboration of an
  already-accepted trade-off, not a new finding — I do not judge the disposition wrong.
- D-02 (registry shape, self-policing): module-level `DOCUMENTED_EXCEPTIONS` tuple, no glob, single
  FEAT-44 entry — present exactly as decided (`suite_layout.py:18-25`). All four self-policing rules
  fire correctly (proved, see matrix below).
- D-03 (tracked = Git index; ordering; fail-closed on enumeration failure): **honored**. The
  toplevel-vs-root check lives *inside* `tracked_paths()` (`suite_layout.py:52-53`) and is evaluated
  before the function can return successfully, so `violations()`'s self-ownership test
  (`suite_layout.py:137`) can never see a tracked list from a toplevel mismatch — the ordering
  constraint is structurally enforced, not merely sequenced by convention. Verified live: this
  worktree's own `.git` is a file (`file .git` → `ASCII text`), `os.path.exists(root/".git")`
  correctly returns `True` for it, and `suite_layout.violations('.')` returns `[]` run from inside
  the worktree right now — route (a) is reachable and clean under a worktree, not silently inert.
- D-04 (no double-report bin vs. index clause): confirmed by reading — `planted_rel` is computed
  from the *same* `planted` set the bin clause already used, and the index-driven loop `continue`s
  on any `rel in planted_rel` before it can be reported twice (`suite_layout.py:134-141`).
- D-05 (FEAT-44 exception, exact path, unrelocated): confirmed — `suite_layout.py:19-21` and
  `tests/manual/probe-omp-session-accessor.py:54-55` cite the identical path.
- D-06 (DEC-213 amendment + index regen): confirmed. `DECISIONS.md:6696` carries an "Amended by
  BUG-1286..." paragraph in the house idiom (matches DEC-179/DEC-192/DEC-201's own amendment style —
  none of those literally say "superseded" either, so this is consistent, not a deviation).
  `gen-decisions-index.py --stdout | diff - DECISIONS-INDEX.md` → **byte-identical**. The DEC-213
  index row states the repository-wide invariant. SC-13 holds.
- SC-14 (`harness.json` unchanged): `git diff 1977ebd6..9adbce6b -- .harness/harness.json` → 0
  lines. Confirmed.
- SC-15 (mutation-snapshot scope unchanged): `run-unit-tests.sh` diff is empty; pinned blob line 47
  is still `run_pool.py --mutation-check "$BIN_DIR" -- ...`. Confirmed.

## Stage 2 — code quality / fail-open hunt

### Item 2 — `tracked_paths()`'s four LookupError routes

All four raise sites (`suite_layout.py:44-61`) feed the *same* `except LookupError` in
`violations()` (`suite_layout.py:130-131`), which appends `cannot enumerate tracked files under
{root}: {error}` — never a clean result. Verified:
- git missing (`FileNotFoundError`) — **proved by reading**: trivial, deterministic control flow.
- non-zero exit — **proved by the suite**: unit case 4 / integration case 4 (`.git` replaced by an
  empty dir, so `git ls-files`/`rev-parse` both fail non-zero) both PASS in the 341/0 run.
- timeout (`subprocess.TimeoutExpired`) — **proved by reading** only; no fixture in this diff
  actually forces a 20s hang, so this route is untested end-to-end. Low-value to add (would need a
  hung git process), noting as an evidence gap rather than a finding.
- toplevel mismatch — **proved by reading** (see D-03 above); no fixture directly exercises "root
  nested inside another checkout with a matching `.git`" (case 9 tests "no `.git` of its own", not
  "own `.git`, wrong toplevel"), but the code path is identical to the other three raise sites and
  unconditionally caught the same way.
- `git ls-files` exit 0 with empty stdout — **proved by probe**: this is *not* a LookupError route;
  `tracked_paths` returns `()`. Self-ownership then legitimately fails (empty tuple doesn't contain
  the guard's own path) so the main clause stays inert — correct, matches SC-16/17's design. But see
  Finding A: this same empty/non-matching tuple still reaches `_registry_findings` unconditionally.

### Item 3 — the four registry rules

All four **proved reachable and firing** by re-running the shipped `tests/unit/test-suite-layout.py`
case 6 (part of the 341/0 corroborated run): glob-character, duplicate, unnecessary (not test-shaped
or under `tests/`), and no-longer-tracked each independently fire on their own synthetic
`DOCUMENTED_EXCEPTIONS` override, none masking another given the `continue`-per-rule control flow.

### Finding A (MED, Stage 2 — registry hygiene not self-ownership-scoped)

`_registry_findings(tracked)` is called unconditionally at the end of `violations()`
(`suite_layout.py:149`) with whatever `tracked` holds — which is populated as soon as `.git` exists
and enumeration succeeds, **independent of whether self-ownership passed**. The team already knows
the mechanism (`notes/receipt-harness-backend-dev-T-02-c1.md:14-18` describes it explicitly, and
`test-run-unit-tests-layout.py`'s `git_tree()` fixture plants a stand-in exception file specifically
to route around it) but the same care was not extended to unit case 9, which constructs exactly the
"repo not shipping suite_layout.py" shape SC-16 is about.

Demonstrated directly (no code edit needed — this is the shipped, unmutated code) by replicating
case 9's exact fixture (own `.git`, `tests/unit/test-unit.py`, `tests/integration/test-integration.py`,
committed `.harness/tools/test_rogue.py`, **no** copy of `suite_layout.py`):
`suite_layout.violations(td)` returns `['documented exception is no longer tracked:
.harness/harness/features/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts']` — not
`[]`. Case 9's own assertion (`not any(g.startswith("tracked test-shaped file outside tests/:") for
g in got)`) only checks that one prefix, so it stays green while `violations()` is demonstrably not
a clean result for the exact fixture SC-16 constructs.

No production impact: `violations()` has exactly one real caller (`run-unit-tests.sh` on Harness's
own root, per D-03/SC-16, where self-ownership and the registry's tracked-check always agree).
Rated MED: real, demonstrated, contradicts the loose framing of SC-16's opening sentence ("reached
by neither control") even though SC-16's own more precise text (about "the clause") stays literally
true; the fix, if wanted, is trivial — move `out.extend(_registry_findings(tracked))` inside the
same self-ownership `if` that gates the main clause, or pass `None` when self-ownership fails.

### Item 4 — assertion vacuity hunt, including a correction to a prior QA disposition

**Correction — I judge one clause of `qa-matrix-gate-c2.md`'s disposition wrong.** That note
concludes integration case 3 (`tests/integration/test-run-unit-tests-layout.py:97-112`, the
sorted-order assertion) "carries zero information about the order the runner printed the lines in"
and claims a probe showed it staying green under a reversed line order. I re-ran this end to end
with a genuine production mutation (not a hand-edited variable): copied the real `suite_layout.py`
into a scratch git fixture, changed exactly one line, `for rel in sorted(tracked):` →
`for rel in sorted(tracked, reverse=True):`, committed three rogue files, and invoked the actual
`run-unit-tests.sh` subprocess. Result: `MISCONFIGURED:` lines print in reverse order (c, b, a), and
applying integration case 3's exact check expression against that real output gives
`ordered = ['.harness/c/...', '.harness/b/...', '.harness/a/...']`, `sorted(rogue_paths) =
['.harness/a/...', ...]`, **`ordered == sorted(rogue_paths)` is `False`** — the check reddens
exactly as intended. The note's own write-up ("`ordered` is built by iterating `rogue_paths` (the
outer loop...)") mis-describes the actual comprehension, `[rel for line in misconfigured for rel in
rogue_paths if rel in line]`, where `line` is the outer loop and `rel` the inner one — so
`ordered`'s element order tracks `misconfigured`'s (the runner's real print order), not
`rogue_paths`'s fixed sort. This is good news, not a new problem: SC-03's ordering guarantee is
protected at the integration layer as well as the unit layer; no finding follows from this, but a
downstream reader should not treat that note's case-3 conclusion as settled.

**T-01 case 11 / hygiene / INAPPLICABLE branch** (the three pre-dispositioned items): read all
three, agree with all three dispositions as given (F-1 tautological conjunct in
`_literal_key_present`, F-2 unreachable `".."` disjunct in `_is_inside_tests`, case 11's
`INAPPLICABLE` branch at line 526 being latent/advisory) — did not re-litigate. Confirmed via the
real run that at `review_sha` the positive control is **not** currently in its `INAPPLICABLE`
branch (`select_control_candidate` finds `.harness/tools/test_dir/gen.py` and the check runs and
passes), consistent with the prior disposition's framing of this as a forward-looking, non-gating
risk rather than a live gap.

## Verification corroborated

Ran `python3 tests/unit/test-suite-layout.py` directly at pinned-sha content: 28/28 checks PASS,
matches the orchestrator's 341/0/27 claim for this file's slice. Did not independently re-run the
full 27-file/341-check suite or the 14-check integration suite in full, but exercised the specific
integration scenarios discussed above via direct subprocess invocation of the real
`run-unit-tests.sh`, all consistent with the stated 14/0 result.

## Not spent

Did not re-derive SC-19's full behavioural/hygiene proof from scratch (it is extensively
self-documented in BRIEF/plan.yaml and independently corroborated by the passing suite); spent the
budget on the code-grade run (which nothing else in this feature's history appears to have executed
against this diff) and the fail-open/registry hunt the dispatch weighted highest.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Mechanical code-risk grader (not run anywhere earlier in this feature's history) reports two production functions in suite_layout.py below their grade-4 bar and not grade-2 — violations (grade 1, suite_layout.py:101) and _registry_findings (grade 3, suite_layout.py:79) — which is SEVERITY high and blocks by rule regardless of the rest of the review; everything else hunted (registry self-ownership scoping gap, a corrected QA disposition, a corroborated-and-accepted sole-implementation residual) stays MED or non-gating.
  severity_max: high
  findings: 4
  must_fix:
    - "violations (.claude/skills/harness/bin/suite_layout.py:101): cyclomatic 23, cognitive 35, ABC 45.7, GRADE 1, bar 4 (production), driver cyclomatic+cognitive+abc — decompose into named helpers, one per responsibility (unit/integration existence+duplicate check, runner-selection shape check, bin-planted check, git-tracked-outside-tests scan, registry delegation)."
    - "_registry_findings (.claude/skills/harness/bin/suite_layout.py:79): cyclomatic 9, cognitive 15, ABC 16.4, GRADE 3, bar 4 (production), driver cyclomatic+cognitive — below the grade-4 production bar, not grade-2, blocks identically to a grade-1 finding per the grading skill."
  spec_violations: []
  reviewed: "1977ebd68d34cc0308968b03ad2d24399c0b5335..9adbce6b690cd4b319c3758ab2a16505dd15900e"
  human_commits_in_scope: []
  code_grade: fail
  open_questions:
    - { id: Q1, question: "Should _registry_findings' tracked-comparison rule be gated by the same self-ownership condition as the main outside-tests clause (currently it runs on any git repo whose toplevel matches root)? No production impact today (single caller always self-owns), but it misfires on the exact synthetic-checkout shape SC-16/case-9 constructs.", blocking: false }
    - { id: Q2, question: "tracked_paths (grade 2, ABC driver, suite_layout.py:44) and _literal_key_present (grade 2, cyclomatic driver, test-suite-layout.py:405) are each grade-2 with a reason supplied in this note — does the operator accept those reasons, or want them folded too while the file is open for the must_fix decomposition?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/notes/review-harness-code-reviewer-c1.md
```
