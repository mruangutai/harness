# Plan-panel scope review — BUG-151 — cycle 0

**BLUF: no orphan requirements, no broken traceability, no `depends_on` defect, and every hazard
named in the dispatch checks out refuted against the actual source text and line numbers. No
must_fix. This plan is ready to sign on scope grounds.**

## Traceability — clean

- REQ-01..REQ-04 (BRIEF.md) each have >=1 task `traces:` reaching them: REQ-01/REQ-03 from both
  T-01 and T-02; REQ-02/REQ-04 from T-02 only (correctly — T-01's intent explicitly declines to
  touch the comment or the aggregation sites). No orphan REQ.
- Both tasks' `traces:` cite only REQ-01..REQ-04 and D-01/D-02, all of which exist. No dangling
  citation.
- SC-01..SC-05 each map to a task step: SC-01(a) T-01 STEP 2 (permanent selfcheck), SC-01(b) T-02
  step 8(b) (one-off receipt), SC-02 T-02 step 4 (discovery) + `verify: inspection`, SC-03 the
  sha256 protocol (T-01 step 0 / T-02 step 8a), SC-04 T-02 step 6 (safeguard trips suite exit),
  SC-05 T-02 step 3. No SC left unaddressed.
- `depends_on`: T-02 -> [T-01] is a valid (trivial, two-node) topological order; T-02 needs
  `_aggregation_verdict`/`_AggTee` which only exist after T-01.

## The three named hazards — checked against source, all refuted

**1. Does T-01's `verify:` conflict with T-02 deleting the line T-01 adds?** No. T-01's verify
(`plan.yaml` T-01 `verify:`) calls `m._aggregation_verdict` and `m.run_bug151_selfcheck_cases()`
directly via importlib — it never calls `main()` and never touches the `fails += ` list. It runs
once, immediately after T-01, before T-02 exists. There is nothing in the plan that re-runs T-01's
verify after T-02 lands. The two verify blocks operate on disjoint surfaces (direct function call
vs. subprocess run of the whole file) and never race.

**2. Does the safeguard's own `FAIL`-prefixed diagnostic get counted by itself or a later block?**
No, by construction of T-02 step 6's ordering. Read literally: step 5 evaluates
`_aggregation_verdict` per-block, INSIDE the per-block capture window; step 6 says "Accumulate...
After the loop, print each problem at column 0" — the diagnostic print happens strictly after
every block (including `run_bug151_selfcheck_cases` itself) has already been run and captured. No
block's `_AggTee` window is open when the problems list prints, so no verdict evaluation can ever
see its own or a sibling's diagnostic line. Confirmed against `main()`'s current structure at
`tests/integration/test-check-domain.py:5190-5231` — the aggregation is currently one flat
function body, consistent with "loop, then print" being a simple sequential rewrite.

**3. Could the synthetic fixture strings in T-01's selfcheck cases echo at column 0 and trip the
outer safeguard on a green suite?** Refuted on the text as specified, not merely asserted safe.
Cases (a)-(f) (T-01 STEP 2) pass literal fixture strings as function ARGUMENTS to
`_aggregation_verdict(label, captured_text, total)` — they are never `print()`ed to real stdout;
only the block's own "ok/FAIL [bug151-selfcheck] <name>" summary line prints, and that line's
column-0 prefix is always the literal `"ok    "` or `"FAIL  "` token, with `<name>` appended after
it — so even a case name containing the word "FAIL" cannot land at column 0. The plan additionally
carries an explicit CRITICAL warning against this exact failure mode. No gap found.

## Independent arithmetic check (not trusted from the plan text)

`grep -n '^def run_' tests/integration/test-check-domain.py` on the current worktree returns
exactly 24 names: 23 leaf blocks (`run_t12` ... `run_bug1305_identity_cases`) plus the composite
`run_bug1305_cases` at line 5182. The 20 `fails += run_x()` sites sit at 5211-5230, the composite
return term at 5231, and the false "asserted non-negative" comment at 5207-5210 — all match the
plan's cited line numbers exactly (file is at 6d969ed3, `lanes.resolved_at`). No `run_`-prefixed
module-level name exists outside these `def` statements (checked module imports at
`tests/integration/test-check-domain.py:1-27`; no aliasing). So: baseline 24 -> +1 after T-01 adds
`run_bug151_selfcheck_cases` -> 25 -> -1 after T-02 step 1 deletes the composite -> **24**, matching
T-02's `verify:` assertion `len(blocks)==24` exactly, and `len(blocks)==24` is an equality (not a
lower bound), so it also catches over-inclusion, not just under-inclusion.

## Not re-raised

F-1, F-2 (goal-check cycle 0) are applied per the planfix-c1 note and verified present in
`plan.yaml` (STEP 0 RECOVERY ROUTE text, D-02's DEPARTURE FROM THE ISSUE clause). F-3, F-4 are
already ruled/accepted by the operator's prior cycle; I found no new evidence against either.

## Findings

None. Three candidate hazards were checked concretely against the plan text and the source file
and each refuted with a specific citation (see above); recording them here per practice, not as
defects. Empty findings list is the honest result of this pass.

files_touched: none (read-only review)
