# QA c5 — FEAT-2229 at c163d5ea0fb17da27b3455559f317d67852981c7 (run r-20261122-validate-c5-validator)

**BLUF: PASS for the authorized scope.** M6 (both directions), M8 and the SEC-C4-01 spoof are each red by live mutation of the pinned code and green at the pin. The T-01 verify, the unit runner and the integration runner exit 0. Four *additional* tilde-leg mutants survive (advisory, T-01/SC-02; outside the operator's M6/M8 authorization, never must_fix here).

## Phase 1 (from BRIEF/plan/ruling only)
Expected: actual-CLI cases for (a) a ``` run never closing ~~~ and vice versa, (b) ~~~ opener with a backtick in info still opening, (c) `## DEC-10x` / `_a` / `-1` / `.5` never matching DEC-10 with real heading shapes still matching. Each needs a spoof-fails + genuine-passes pair. All three exist (`tests/integration/test-plan-decision-dispositions.py` `case_closer_must_match_opener_character`, `case_tilde_info_string_may_hold_backticks`, `case_heading_names_the_full_identifier`; registered in `main`). No Phase 1 gap on the authorized three.

## Matrix (T-01 change_type cross_module -> unit + integration always)
- unit: satisfied. `tests/unit/test-decision-disposition-schema.py` 40/40; runner `run-unit-tests.py --kind unit` exit 0, 62 files.
- integration: satisfied. `tests/integration/test-plan-decision-dispositions.py` 130/130; runner `--kind integration` exit 0, 89 files (this script 47.5s under 8-worker load; 21.5s standalone).
- T-01 verify verbatim (`set -eu` + both scripts) exit 0. Env: HARNESS_AGENT_TYPE unset for runners; HARNESS_* stripped in subprocess probes. Pin tree clean (`git status --porcelain` empty) before and after every mutation; pin removed on return.
- Delta c163d5ea is check.py +8/-2 and +32 test lines: only those subjects re-measured; c4 evidence for other SCs retained by pointer to `notes/review-harness-qa-c4.md`.

## Mutation proofs (mutant applied to the pinned check.py inside my own pin; each run = 130 cases)
Red is semantic: every red is "spoof clause fails the DEC-10 row" with output `OK T-01 1 anchor(s) resolved` (check wrongly passed); setup is sound because the paired genuine-clause control stays green in the same case.
|mutant|result|
|---|---|
|M6-both (closer ignores fence character)|exit 1, 128/130; red: `rule 4 ~~~ in ```` and `rule 4 ``` in ~~~`|
|M6 backtick run closes tilde only|exit 1, 129/130; red: `rule 4 ``` in ~~~`|
|M6 tilde run closes backtick only|exit 1, 129/130; red: `rule 4 ~~~ in ```` |
|M8 (no-backtick-in-info applied to tilde openers)|exit 1, 129/130; red: `rule 3 tilde`|
|SEC pre-fix matcher `(?!\d)` transplanted for `DEC_ID_END`|exit 1, 122/130 (12 FAIL: spoof passes for `DEC-10x`, `_a`, `-1`, `.5`; and genuine DEC-10 clause fails since the spoof heading shadows it)|
Green: pin unmutated 130/130, exit 0 (before and after). Fail-first for SC-02 tilde/identifier legs = these mutation reds (tier: mutation, not natural pre-fix RED; `notes/red-first-T-01.md` not relied on). No natural pre-fix SHA run was taken: base for the delta is c163d5ea~1, which I did not check out (instructed no prior pins).

## Extra tilde-leg mutants — SURVIVORS (two unique gaps; both kind: substance, severity: low, scope: task, owner T-01, SC-02; backlog, not must_fix)
Gap A = X2/X5/X6 (tilde closer length rule); Gap B = X3 (tilde closer-with-info-string rule). Each is a missing assertion on live behavior (substance); low because the backtick-leg versions are covered and the authorized M6/M8 are killed.
All four stay 130/130 exit 0, and each is proven live (a `_real_headings` probe differs from the pin):
- X2 tilde closer of any length closes (probe `~~~~ / ~~~ / ## DEC-10 / ~~~~`: pin `[]`, mutant `[(2,2)]`).
- X3 tilde closer carrying an info string closes (probe `~~~ / ~~~ x / ## DEC-10`: pin `[]`, mutant `[(2,2)]`; first attempt hit a stale .pyc — same-size rewrite in the same second — re-run with `-B` showed the divergence).
- X5 tilde closer must equal opener length (probe `~~~ / ~~~~`: pin closes, mutant doesn't).
- X6 tilde closer only length 3 (same probe family).
Same class as expertise P-06 (each leg needs its own case): the length rule and closer-info rule are pinned only on the backtick leg. Backtick-leg versions are covered; the tilde legs are not. Not in the operator's authorized M6/M8 set; retained as backlog advisory, no tests authored.
Killed extras: X1 tilde never opens (5 red), X4 tilde min length 4 (5 red), X7 4-space indent for tilde (2 red), X8 tilde opener info needs leading space (2 red).

## Digest-contract note
The qa schema has no findings field: survivors are recorded in `coverage_gaps` only; a green suite with advisory-only gaps takes PASS.

## Principles applied
none read this run.
