# Goal-check — BUG-1724-run-end-tokens — validate c1

Pinned review SHA: `3eb4c27525a17640c4b60a9b735d02eb911dc074`

Task binding: `T-01`, which traces `SC-01` through `SC-04`. The code-review range is `1a1c1925..3eb4c27525a17640c4b60a9b735d02eb911dc074`. This grade considers only the approved six-file surface; five files change in that scoped diff and `tests/unit/test-omp-hooks.py` remains the runner for the Bun suite. The prior `_quoted_scalar_closed` high finding is absent: neither that symbol nor `check-state.py` is changed in the clean task range.

## Overall grade

**PASS.** All three declared perspectives and all four signed success criteria pass. `needs_approval: false`.

## Perspective grades

| Perspective | Grade | Criteria | Evidence |
|---|---|---|---|
| operator | **pass** | SC-01, SC-02 | The pinned hook sums qualifying result tokens and stamps once before spend (`.omp/extensions/harness-hooks.ts:372,1022-1030`); bare `run-end` preserves an existing figure (`.claude/skills/harness/bin/feature-record.py:143`), while no qualifying figure leaves the run unmeasured. QA recorded the exact bounded T-01 command green at the pin (`notes/review-harness-qa-c1.md:9-15,35-36`). |
| orchestrator | **pass** | SC-03 | The pinned playbook removes normal `--tokens` transcription and retains the no-host-figure override (`.claude/skills/harness/SKILL.md:79-85`). Focused tests prove two result counts are summed into one stamp, bare close preserves the sum, and `run-end --tokens N` remains (`tests/unit/omp-hooks.test.ts:1237`; `tests/unit/test-feature-record.py:148,185`). |
| code maintainer | **pass** | SC-04 | The pinned CLI defines open as `started_at` present and `ended_at` absent, writes only with exactly one open run, and refuses zero or multiple open runs before mutation (`.claude/skills/harness/bin/feature-record.py:156-184`). Focused tests cover the successful write, exit-2 refusals, byte preservation, and both ambiguous run ids (`tests/unit/test-feature-record.py:148,161,168`). |

## Success-criterion grades

### SC-01 — pass

The pinned diff implements integer filtering and summation in `taskResultTokens`, invokes `stamp-tokens` before `spend`, and preserves the stamped value through a bare close (`.omp/extensions/harness-hooks.ts:372-386,1022-1033`; `.claude/skills/harness/bin/feature-record.py:143,163-184`). The focused hook test asserts `135888 + 68447 = 204335`, exactly one stamp, and stamp-before-spend; the CLI test asserts bare-close preservation (`tests/unit/omp-hooks.test.ts:1237`; `tests/unit/test-feature-record.py:148`). Existing focused reader assertions prove spend sums recorded tokens and the advisory names `spend.tokens` (`tests/unit/test-feature-record.py:381`; `tests/unit/omp-hooks.test.ts:983`). QA ran the literal T-01 command at the pin with 45 Python tests and 74 Bun tests passing (`notes/review-harness-qa-c1.md:9-15`). The named fail-first receipt records both positive regressions red on parent `1a1c1925` because `stamp-tokens` and host stamping were absent (`notes/receipt-main-session-T-01-fail-first.md:3-19,21`).

### SC-02 — pass

When no result carries a non-negative integer, `taskResultTokens` returns `undefined`, so the hook skips stamping; bare close then writes `null` (`.omp/extensions/harness-hooks.ts:372-386,1022-1029`). The focused tests assert no stamp for an absent host value, `null` after bare close, and rejection of string, negative, and fractional values (`tests/unit/omp-hooks.test.ts:1251,1264`). QA's exact bounded command recorded those cases green at the pin (`notes/review-harness-qa-c1.md:9-15,36`). The fail-first receipt honestly identifies this as a construction-negative companion that passed before the fix: it discriminates an implementation that invents a number, while SC-01's positive branch supplies the captured red (`notes/receipt-main-session-T-01-fail-first.md:21`; `notes/review-harness-qa-c1.md:36,40`).

### SC-03 — pass

Normal OMP completion is documented as bare `run-end`, with `--tokens N` reserved for no host figure (`.claude/skills/harness/SKILL.md:79-85`). The hook sums all qualifying result counts for one task call and invokes `stamp-tokens` once (`.omp/extensions/harness-hooks.ts:372-386,1022-1029`). Tests cover multi-result summing/one stamp, bare-close preservation, and the explicit override (`tests/unit/omp-hooks.test.ts:1237`; `tests/unit/test-feature-record.py:148,185`). QA's exact bounded command recorded all three green at the pin (`notes/review-harness-qa-c1.md:9-15,37`). The fail-first receipt supplies captured red for the new positive stamping path and explicitly records that the retained override is a construction-negative companion rather than mislabeling it red (`notes/receipt-main-session-T-01-fail-first.md:7-21`).

### SC-04 — pass

`stamp-tokens` selects entries with `started_at` and without `ended_at`; zero open runs yields a state-specific refusal, multiple open runs yields a refusal naming every conflicting id, and mutation occurs only after exactly-one validation (`.claude/skills/harness/bin/feature-record.py:156-184`). The tests assert success, exit 2 for each refusal, no-open wording, both `r2` and `r3`, and byte-identical preservation (`tests/unit/test-feature-record.py:148,161,168`). QA's exact bounded command recorded the focused suite green at the pin (`notes/review-harness-qa-c1.md:9-15,38`), while the named receipt records all three new CLI cases red on the parent because the verb did not exist (`notes/receipt-main-session-T-01-fail-first.md:5-11,21`).

## Gaps and qualifications

- **Pre-merge live-host observation is unavailable, not failed.** Main's c1 receipt records that the running OMP process loads `.omp/extensions/harness-hooks.ts` from the process-root checkout, not this feature worktree, so the changed hook cannot be live-loaded before merge. The c0 run therefore still recorded `tokens: null` despite a task result reporting `106997` (`notes/receipt-main-session-fix-c1.md:5`). This does not negate the signed `verify: automated, evidence: unit` method: the pinned Bun regression drives the pinned hook and the real `feature-record.py` gate path, asserts the file on disk, and QA's exact gate is green. A post-merge dispatch under a reloaded host remains the first available live observation.
- The BRIEF's standing typecheck limitation remains: the changed TypeScript hook has no active typecheck runner (`BRIEF.md:26-28`). The Bun unit suite is green and supplies the signed automated evidence, but static type validity is not separately proven by a typecheck gate.
- The fail-first evidence is intentionally clause-accurate: SC-01 and SC-04 have captured red; SC-02's absent-value case and SC-03's retained override are construction-negative companions that were already valid on the parent and would fail only if the new implementation regressed them (`notes/review-harness-qa-c1.md:33-40`).
- QA's artifact also reports `BLOCKED` after invoking a separately configured matrix runner (`notes/review-harness-qa-c1.md:3-5,17-27`). That invocation is outside this regate's explicit constraint that QA's only executable gate is the literal T-01 verify command. The configured-runner problem is therefore not used to erase the observed focused-test results or to turn a met product criterion into a failure; the validator lead may handle the out-of-contract QA gate independently.

## Findings

`[]` — no perspective or success criterion is partial or failed, so there is no finding requiring kind, severity, T-01 binding, or a concrete failure scenario.

## Canonical handoff

```yaml
VERDICT: PASS
DIGEST:
  headline: "All three perspectives and SC-01 through SC-04 pass at pinned SHA 3eb4c275; post-merge live-host observation remains unavailable pre-merge but does not weaken the signed unit verdict."
  feasibility: clear
  surface: M
  flags: [bugfix, host-hook, pre-merge-live-observation-unavailable]
  recommend: proceed
  tasks: 1
  decisions: 0
  needs_approval: false
  risk: low
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:9-15,35; tests/unit/omp-hooks.test.ts:1237; tests/unit/test-feature-record.py:148,381; fail-first receipt:3-19" }
    - { id: SC-02, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:36,40; tests/unit/omp-hooks.test.ts:1251,1264" }
    - { id: SC-03, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:37,40; tests/unit/omp-hooks.test.ts:1237; tests/unit/test-feature-record.py:148,185" }
    - { id: SC-04, verdict: met, method: automated, evidence: "notes/review-harness-qa-c1.md:38; tests/unit/test-feature-record.py:148,161,168; fail-first receipt:5-11" }
  open_questions: []
  files_touched: [/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1724-run-end-tokens/.harness/harness/features/BUG-1724-run-end-tokens/notes/research-BUG-1724-run-end-tokens-goalcheck-validate-c1.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1724-run-end-tokens/.harness/harness/features/BUG-1724-run-end-tokens/notes/research-BUG-1724-run-end-tokens-goalcheck-validate-c1.md
```
