# QA — test-matrix gate — BUG-1290 B-27 fix cycle, panel/qa at `review_sha` 72a97b99 (HEAD)

## BLUF

**PASS.** `matrix_ok: true`. Both named suites print their exact expected final lines at exit 0.
I independently reproduced all five orchestrator controls plus both extra probes with my own
perturbations (not read from the prior note) — every one lands exactly as claimed. The one commit
between the prior qa pin (`fb9a4ac4`) and this one touches only notes/receipts (`git show --stat
72a97b99`); production stays byte-identical to `c488218e` (re-measured: `git diff --stat c488218e
72a97b99 -- .agents/ .claude/skills/ bin/` empty). Working tree is clean apart from my own note (and
sibling panel notes already present); no scratch worktree created; every perturbation restored and
confirmed via `git status --porcelain`.

## Phase 1 (no source access, from BRIEF/plan/operator answer alone)

This directed B-27 cycle needed exactly two things to exist: (1) `5g`'s assertion tightened to the
mutation's *specific* observable rather than a bare negation a merely-raising mutant could also
satisfy, and (2) an independent path where the real suite literally *prints* `FAIL BUG-1290 5b`
under the issue-map key-collapse, not merely an in-process capture. Both exist
(`test-factory-claim.py:1319-1352`, `test-factory-claim-mutation.py:150-201`). `coverage_gaps: []`.

## Matrix resolution (change_type: bugfix for all five tasks T-01..T-05; graded over the FEATURE
diff `main..HEAD`, consistent with the prior cycle's standing instruction — this cycle's own diff is
notes-only and carries no code to grade)

- **unit** — required (`touches_runtime_code` fires: the feature diff touches
  `factory_claim.py`/`factory_config.py`/`feature-worktree.py`/`layout_migration.py` in earlier
  tasks T-03/T-04). **satisfied** — `run-unit-tests.sh --kind unit` exit 0, 29/29 script rows
  `PASS`, 0 `FAIL test-*` rows, including `test-factory-claim.py` and
  `test-factory-claim-mutation.py`.
- **integration** — the `bugfix` `when` predicate `fix_confined_to_tests_and_contract_docs` does
  NOT fire for the feature as a whole (production changed in T-03/T-04), but SC-07/SC-09 name
  `tests/integration/test-factory-integration.py` and `test-layout-migration.py` as their own
  verification surface, so I add it per floor-not-ceiling. **satisfied** — `run-unit-tests.sh
  --kind integration` exit 0, 46 files, all `PASS` (confirmed via two separate runs; `grep -n
  "factory-integration"` shows `test-factory-integration.py (exit 0, 50.49s)` ... `PASS
  test-factory-integration.py`).
- **`__bug_class__` / `match_bug_class`** — **n/a**, per repository Expertise G-08: this predicate
  is a currently-unresolvable placeholder (no bug-class taxonomy entry fires for any diff yet), so
  no kind is obligated by it.
- **ai_behavior / config / frontend / feature / api / cross_module / logic** — **n/a**; this task
  set is exclusively `bugfix`-typed.
- All other named `test_kinds` — **n/a**, not implicated by this diff's touched-file globs.

`matrix_ok: true`.

## Suites run (verbatim final lines, my own execution at this pin)

- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim.py` → `125/125 checks passed.`,
  exit 0.
- `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-factory-claim-mutation.py` → `BASELINE 3/3 ok`
  … `MUTATION PROOF: 3/3 cases reddened` … `KEY-COLLAPSE PROOF: FAIL BUG-1290 5b printed`, exit 0.
- `run-unit-tests.sh --kind unit` → exit 0, 29 script rows all `PASS`.
- `run-unit-tests.sh --kind integration` → exit 0, 46 files, all `PASS` (two independent runs; the
  second was truncated by my own 180s tool timeout partway through a re-verification pass, but the
  first run completed cleanly to its pool summary and both are consistent for every line captured).
- Production identity: `git diff --stat c488218e 72a97b99 -- .agents/ .claude/skills/ bin/` →
  empty, re-measured myself.

## Standing question — can each gate report RED, and for the RIGHT reason? Five controls,
reproduced or challenged, plus two extra probes — each is MY OWN fresh perturbation, in this
worktree, restored and `git status --porcelain`-confirmed clean immediately after

1. **Merely-raising mutant reddens `5g`.** REPRODUCED. Replaced `_FeatureOnlyIssueMapCache
   .issue_number` (`test-factory-claim.py:1326-1328`) with a bare `raise RuntimeError(...)`. Result:
   `5g` reddened — `1 of 125 FAILING`, detail `(False, 2, '', 'factory: claim: unexpected failure:
   RuntimeError: merely-raising mutant probe ...')` — code 2 and the exception text, neither
   matching the required `(1, "", .../"952"/"unresolvable blocker")` shape, so the tightened
   assertion (not a bare negation) is what catches it. Restored; suite back to 125/125.
2. **Deleting the harness fixture's `depends_on=["T-99"]` reddens the suite.** REPRODUCED. Changed
   `test-factory-claim.py:382` to `task_dict("T-77")` (no dependency). Result: `1 of 125 FAILING` —
   `5g` reddened specifically (the now dependency-free task resolves "clear" even under the
   collapsed cache, so the mutation stops producing its expected observable — the fixture's
   dependency is load-bearing for the mutation proof's discriminating power, not incidental).
   Restored; suite back to 125/125.
3. **Emptying the harness segment's issue map reddens `5b`.** REPRODUCED. Changed
   `test-factory-claim.py:383` to `{"factory": {"issues": {}}}`. Result: `1 of 125 FAILING` — `5b`
   reddened directly (not via `5g`), since `T-99` is now unresolvable in harness's own map too, so
   952 is refused instead of claimed. Restored; suite back to 125/125.
4. **Neutering the key-collapse arm leaves the mutant REACHED yet `5b` NOT red.** REPRODUCED
   myself, the load-bearing one. Changed `test-factory-claim-mutation.py:175` from
   `super().issue_number(canonical, feature, task_id)` to
   `super().issue_number(repo, feature, task_id)` — kept the `_reached`/print side effect intact.
   Result: `MUTANT KEY-COLLAPSE ACTIVE` printed (REACHED = True) yet `KEY-COLLAPSE MISSING: 5b`,
   `KEY-COLLAPSE PROOF: INCOMPLETE`, exit 1. This proves the arm's redness depends on the collapse
   itself, not merely on the mutant class's installation. Restored; verified clean; re-ran to
   confirm exit 0 / both marker lines again.
5. **Captured verdict keyed by `name_5b`, is False, and the real cache is restored.** CHALLENGED —
   verified externally without touching any file: imported `factory_claim`, recorded
   `id(claim._BlockerCache)` before running the suite in-process via `runpy`, ran it, and confirmed
   `before is after` → `True` (the `try/finally` at `test-factory-claim.py:1335-1340` restores the
   real class regardless of path taken) and that `5g` itself reported `ok` — which is only possible
   if the captured `captured[name_5b]` tuple 5g reads was correctly `False` under the mutant (5g's
   own assertion, unperturbed, requires exactly that).

### Two extra probes, not on the controls list

- **4a. Does `test-factory-claim-mutation.py` exit non-zero when `_key_collapse_proof` fails?**
  OBSERVED, not read: under perturbation #4 above (key-collapse neutered), `python3
  tests/unit/test-factory-claim-mutation.py` exited **1** (captured directly, not inferred from
  `main()`'s source).
- **4b. Does the unit RUNNER surface that failure?** OBSERVED: re-applied the same neutering edit,
  ran `run-unit-tests.sh --kind unit` — it printed `----- test-factory-claim-mutation.py (exit 1,
  0.28s) -----` and `FAIL test-factory-claim-mutation.py`, and the runner's own exit code went to
  **1**. The new arm is NOT invisible to CI. Restored; verified clean; re-ran to confirm the file
  and the runner are both green again.

## Probe 5 — the prior note's `^FAIL ` attribution, re-measured at this pin

Prior note (`fb9a4ac4`) claimed: "the 4 [`^FAIL `] in unit are `test-factory-claim-mutation.py`'s
own internal PROOF markers inside an exit-0 pass, not script failures." CONFIRMED at this pin:
`grep -c '^FAIL ' <unit output>` = **4**, all four lines fall between
`test-factory-claim-mutation.py`'s own `----- ... -----` header and its `PASS
test-factory-claim-mutation.py` row (three from the baseline features-root mutation arm: `5a`/`5b`/
`5c`, one from the key-collapse arm's own `5b` diagnostic print). `grep -nE '^FAIL test-'` over the
same output returns **zero** matches — no script-level failure exists. The attribution holds. I flag
the underlying observation as a residual finding below (`enhancement`) — a diagnostic print line
that is textually indistinguishable from a real failure line is a real hazard for any future reader
who greps the log without knowing this file's convention, even though it does not gate anything
here.

## Test-first audit

No production code in this cycle's diff (`git show --stat 72a97b99` touches only notes/receipts).
"Test written before the code" doesn't apply; this cycle is qa-note/receipt bookkeeping for a
directed test-only fix that already landed at `fb9a4ac4`. No violation to report.

## sc_evidence (this cycle's scope, unchanged from the prior cycle since no test code moved)

- Operator directive item 1 (`5g` tightened) → `tests/unit/test-factory-claim.py:1319-1352`.
- Operator directive item 2 (literal `5b` failure, no mutant leak) →
  `tests/unit/test-factory-claim-mutation.py:150-201`.

## Residual findings (non-gating)

- **enhancement** — `test-factory-claim-mutation.py`'s diagnostic `FAIL  BUG-1290 5x: ...` print
  lines (emitted deliberately, inside its own exit-0 `PASS`-scored row) are byte-identical in shape
  to a real script-level failure line. Anyone auditing `run-unit-tests.sh --kind unit` output with a
  bare `grep '^FAIL '` — rather than the file/row-scoped grep this gate used — will over-count
  failures. Confirmed the current state produces exactly 4 such lines at this pin; not gating
  (the runner's own PASS/FAIL-per-script accounting is what governs exit code, and that is correct
  and green), but worth a distinguishing prefix (e.g. `PROOF-FAIL`) if this file is touched again.
- Already-ruled items (T-01's `verify:` exiting 1, REQ-05 wording, the inert `match_bug_class` leg,
  the null-yield reviewer pattern) are NOT re-raised here per the standing instruction; I did not
  observe a fresh recurrence of the null-yield pattern in my own gate-only scope.

## Working tree

Clean apart from this note and sibling panel notes already present (`review-harness-security-
reviewer-b27-c4.md`, `review-harness-ui-reviewer-b27-c4.md`) and the orchestrator's own in-flight
`feature.json` bookkeeping (`review_sha` pin bump + run-log entries — pre-existing, not mine). Every
perturbation I made was restored in-place and confirmed via `git -C <worktree> status --porcelain
<path>` immediately after; no scratch worktree created anywhere.
