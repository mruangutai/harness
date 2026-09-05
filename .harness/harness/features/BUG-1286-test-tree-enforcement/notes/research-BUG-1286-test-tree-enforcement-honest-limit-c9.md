# BUG-1286 — closing the two non-gating honest-limit gaps (cycle 9, plan phase)

**BLUF. Both gaps are closed. GAP-2's conjunct is STRUCK and the strike is MEASURED SAFE — all four
required red cases still fail, today's 7 running-kind patterns still certify, and the four
previously over-refused shapes now certify. GAP-1's overstated sentence now agrees with D-01 at all
three sites. Nothing else moved: `panel:` byte-identical, `approval.status: pending` with no
`rulings`, `status: plan`, T-01 the only task changed, no REQ/SC added, removed or renumbered.**

Amended: `plan.yaml` (T-01 `intent` only, via `plan-merge.py amend --field intent
--expect-sha256 f6f3e4b3…`) and `BRIEF.md` (`## Verification gaps`, one bullet's one sentence).

## GAP-2 — the strike, and why the record now supports what it says

Condition (d) CORPUS ORACLE lost its first conjunct. The surviving half is unchanged in force:
every corpus basename `core` matches must be judged test-shaped by the IMPORTED `is_test_shaped`
under `.harness/tools/`; it is still the vocabulary check; it must never be re-spelled. The oracle
is now **vacuously satisfied** when no corpus basename matches, and the intent says so, with the
removal reason in the same place: the conjunct caught nothing (c) did not, and it reported
`**/test-*.sh`, `**/probe-*.ts`, `**/test_*.js`, `**/test_*.mjs` as UNCERTIFIED because the corpus
samples restricted shapes at only 3 of the 7 `SOURCE_EXTENSIONS` (`plan.yaml:443`).

Two dependent statements were corrected in the same pass:

- The "(c) and (d) are independent and both are load-bearing" sentence is gone. It was doubly
  unsupported: nothing exhibited (d) catching what (c) misses, and its cited witness
  `**/test_*.[ps]y` is *not* corpus-unmatched — `fnmatch('test_x.py', 'test_*.[ps]y')` is True, so
  the oracle does see it and passes it. The replacement states only what the surviving (d) buys.
- The remedy bullet "extend the fixed CORPUS with a basename of the new shape…" is deleted; it
  existed only to service the struck conjunct. The corpus's ADD-NEVER-REMOVE rule stays where the
  corpus is specified.

Red case (iv)'s mechanism text was checked and left unchanged: `**/test_*.p?` still fails (d)
independently — corpus matches `['test_x.py', 'test_x.pw']`, and `test_x.pw` is not accepted.

## GAP-1 — three sites, one formulation

`plan.yaml` D-01 (`:103-106`) was already accurate and was not touched. The two overstated sites
now carry the same claim: (a) refuses a wildcard in any **non-final** segment, closing only the
non-final-segment form of the directory-component axis, while the directory-component residual
stays with the behavioural half. Each site's self-correction four lines later is now consistent
rather than contradictory.

## Measurement — throwaway prototype of the amended rule against the real `.harness/harness.json`

Same prototype approach as the c9 goal-check; deleted after the run.

- **7 running-kind detect patterns, all CERTIFIED, case PASSES**: `tests/unit/**`,
  `tests/integration/**`, `tests/manual/probe-omp-session-accessor.py`,
  `tests/manual/probe-handoff-comprehension.py` (inside-tests); `**/*.test.*`, `**/*_test.*`,
  `**/test_*.py` (guard-covered).
- **All four required red cases still FAIL**: `tests/../evil/**` and `**/test_*/**` on (a);
  `**/*.spec.*` and `**/test_*.p?` on (c). Checked independently, (d) also fails the latter two.
- **The four over-refused shapes now CERTIFY**: `**/test-*.sh`, `**/probe-*.ts`, `**/test_*.js`,
  `**/test_*.mjs` — each `UNCERTIFIED (no corpus basename matches)` before, `guard-covered` after.

## Mechanical re-verification

| check | result |
|---|---|
| `plan.yaml` loads; `status: plan`; `approval.status: pending`, `rulings` absent | PASS |
| `panel:` and `decisions:` identical to pre-edit; T-01 the only task changed; T-01's ten non-`intent` fields identical | PASS |
| `check-plan-routes.py` | `0 violation(s) across 1 plan(s)`; all five tasks OK; 11 keys on every task |
| `check-state.sh` | no `INV-35`; the only VIOLATION for this feature is the expected unsigned BRIEF |
| 11 AC rows, 9 REQ, 19 SC unchanged; `SC-19 \| REQ-09` intact (`BRIEF.md:255`) | PASS |

## Open

- The four cycle-8 `panel:` findings still read `disposition: open`. Deliberately untouched — the
  next panel transcription owns them (goal-check gap 3).
