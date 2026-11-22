# QA gate — FEAT-2225 @ 7065b650ab3b94bae3175978bfd0cf0d62478c89 (cycle 5, confirmatory)

**BLUF: PASS.** Unit and integration are green at the pin, T-02's verify (verbatim) exits 0 with empty diff, and C4-F1 is RESOLVED. No tests or code authored.

## Delta (measured)
- `git diff --name-only a5d8687f 7065b650`: DECISIONS-INDEX.md plus feature bookkeeping (feature.json, c4 notes, receipt-harness-documentor-fix-c4.md). Outside `.harness/harness/features`, only DECISIONS-INDEX.md differs.
- `git diff --quiet 219690d0 7065b650 -- . ':!.harness'` exit 0: code is identical to c2 tip, so c4's carried grades hold (notes/review-harness-qa-c4.md).
- The feature worktree HEAD is bd62ee2f (a pin-bookkeeping commit on top). I ran at a disposable pin of exactly 7065b650 (HEAD confirmed), key `--r-c5--harness-qa`; removed on return.

## Executions (all `env -u HARNESS_AGENT_TYPE`; logs /tmp/qa5, volatile)
| kind | state | cmd | result |
|---|---|---|---|
| unit | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0, 61 files run, 1136 PASS lines, 41.5s |
| integration | satisfied | `.agents/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0, 88 files run, 2922 PASS lines, 138.4s (c4: 2921 PASS + 1 FAIL; the gen-decisions-index file is now green) |
| T-02 verify | pass | `python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout \| diff - .harness/harness/docs/DECISIONS-INDEX.md` | gen exit 0, diff exit 0, empty output |

The plan's T-02 verify (plan.yaml:182) matches the command above. Unit log shows `FAIL BUG-1290 5a/5b/5c` lines: these are the deliberate mutation-proof diagnostics of test-factory-claim-mutation.py (Expertise G-09), not failures. The runner exit 0 is the grade.
Matrix: harness.json present; T-01/T-04 are cross_module and require unit + integration; T-02/T-03 add none. `matrix_ok: true`. typecheck/component/ui not claimed (cmd null, BRIEF-recorded gap), unchanged from c4.

## C4-F1: RESOLVED
Red evidence: c4 QA note (T-02 verify exit 1 at 236c236; integration `test_committed_index_matches_a_fresh_regeneration` failed) and receipt-harness-documentor-fix-c4.md (before: verify exit 1, integration exit 1 with 11 cases passing; after: verify exit 0, integration exit 0, 12 cases). Fix 8257a2e0 changed only DEC-253's generated tags line. My own re-measurement at the pin: verify exit 0, integration kind exit 0. No regression: unit and all other integration files green. Not F2 reopened.

## fail_first (verify: automated SC-01..SC-05)
Unchanged from c4, same code (0-byte non-.harness diff): SC-01 notes/red-first-T-04-host.md, red-first-fix-c1-host.md; SC-02 red-first-T-04-digest.md, red-first-fix-c1-core/digest.md, red-first-fix-c2-digest.md; SC-03 red-first-T-04-host.md, red-first-T-04-guard.md, red-first-fix-c2-core.md; SC-04 receipt-harness-backend-dev-T-01-c1.md, red-first-fix-c2-core.md; SC-05 red-first-t04-merge-gate.md. Tier natural RED; durability gap carried (raw logs were /tmp, notes keep counts). Green at pin via the full unit and integration runs above.

## Advisory and open
- C4-W1 (low, form, live-yield wording): not retested; no code or SPEC delta since c4. Advisory only.
- N3/N4 stay advisory low as in c4. F2 boundary is operator-ruled (answers-2026-11-21-f2-ruling.md, #2251); nonblocking open question only: no test pins the three hand-measured local-ref cases.
- Only my own evidence has examined the 8257a2e0 fix; no independent reviewer saw it before this gate (O-07).
- No locally_run kind's detect surface is touched.

## Principles applied
Verification is the product (rule 7): graded by exit code and failure kind at the exact SHA. Never falsify the record (rule 15): the FAIL-token lines are labeled as mutation diagnostics, with the exit code as the grade.

## Addendum: gate-side independent run disagreed once
The validator's independent `run-unit-tests.py` run at the feature worktree exited 1: "4 FAILING", file test-validate-digest.py, 221.5s wall (a loaded host; my pin runs took 41s unit and 138s integration). I could not reproduce it. I ran test-validate-digest.py alone in the feature worktree (HEAD bd62ee2f): exit 0, ALL PASSED, including the member-expertise leaf/lead/supersession/authority/F2/committed-tamper groups. I also ran the full `run-unit-tests.py` (no --kind) there: exit 0, 149 files, 128s. Net: 3 green runs (pin unit, pin integration, worktree full) against 1 red under load; the 4 failing checks are not in my logs. Likely load- or timing-sensitive, which is [INFERENCE], not established. Reported as an open question; not graded away.
