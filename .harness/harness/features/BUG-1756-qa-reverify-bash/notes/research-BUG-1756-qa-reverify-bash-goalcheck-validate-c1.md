# Goal-check — BUG-1756-qa-reverify-bash — validate c1

## BLUF

**PASS** at immutable review SHA `c1f9601fe87660b732aac0bf5e5f72dd17fac0d7`. Both disclosed perspectives pass, SC-01 through SC-04 are met, and c0 Q1/Q2/Q3 are closed. The main-session fix receipt was treated as a claim: its assertions were checked against the pinned diff and independently corroborated by the pinned QA run. This goal-check ran no tests. In particular, it did not execute T-01's exact verify command, `python3 tests/integration/test-validate-digest.py`.

## Perspective grades

- **operator — pass.** SC-01, SC-02, and SC-03 are met: the pinned validator selects the claim's kinds, invokes the Python runner once per named kind or once bare, accepts green reruns, and refuses the first completed red rerun with its real output tail; `review-harness-qa-c1.md:13-16,22-24,32` records the pinned green matrix and successful repaired-hook exercise.
- **code maintainer — pass.** SC-04 is met: the pinned Python stub distinguishes the old bash launch, and separate missing-runner, completed-nonzero, real `OSError`, and `TimeoutExpired` cases preserve fail-open and disagreement behavior; `tests/integration/test-validate-digest.py#_bug1756_in_process_reverify`, `#_bug1756_spawn_error_case`, and `#_bug1756_timeout_case` reach the seam missed in c0, while `review-harness-qa-c1.md:25` records their passing and discriminatory evidence.

No signed perspective is undisclosed or omitted: `BRIEF.md:7-12` declares exactly operator and code maintainer, and both are graded above.

## Success-criterion status

- **SC-01 — met (automated).** At the pin, `validate-digest.py#_claimed_kinds` preserves and deduplicates named kinds and `#_reverify_suite` invokes `[sys.executable, run_bin, "--kind", kind]`; `tests/integration/test-validate-digest.py:2282-2288` asserts exit 0 and the exact unit/integration argv. QA records the pinned integration kind green (`review-harness-qa-c1.md:13-16,22`). Fail-first receipt arm 2 records this exact case red at pre-fix `24e766bb`, exit 2 with `argv=[]` (`receipt-main-session-T-01-fail-first.md:19-20`).
- **SC-02 — met (automated).** `validate-digest.py#_reverify_suite` returns on the first non-zero result and `#check_qa_matrix_claim` reports its real tail and returns 2; `tests/integration/test-validate-digest.py:2291-2306` asserts only unit ran, `UNIT_TAIL_LINE` was relayed, integration output was absent, and exit was 2. QA records the covering integration run green (`review-harness-qa-c1.md:23`). Receipt arm 2 records the exact pre-fix case red with exit 2 and `argv=[]` (`receipt-main-session-T-01-fail-first.md:21-22`).
- **SC-03 — met (automated).** `validate-digest.py#_reverify_suite` maps no claimed kinds to one bare invocation; `tests/integration/test-validate-digest.py:2309-2315` asserts one empty argv record and acceptance. QA records the pinned case green (`review-harness-qa-c1.md:24`). Receipt arm 2 records the exact pre-fix case red with exit 2 and `argv=[]` (`receipt-main-session-T-01-fail-first.md:17-18`).
- **SC-04 — met (automated).** The Python stub makes the bash defect observable; receipt arm 1 records the green Python runner refused by the pre-fix bash launch (`receipt-main-session-T-01-fail-first.md:3-5`). The pinned suite separately covers missing runner, completed non-zero, actual spawn `OSError`, and timeout; the latter two patch the loaded validator's `subprocess.run` and require exit 0 plus `could not independently re-run` (`tests/integration/test-validate-digest.py:2193-2207,2318-2370`). Receipt arm 3 shows both cases redden when `except Exception: return None` is mutated to `raise` (`receipt-main-session-T-01-fail-first.md:31-33`), and QA records all 10/10 bug919 cases green (`review-harness-qa-c1.md:14,25`).

## c0 question closure

- **Q1 — closed.** The pinned c1 diff replaces the directory precondition fixture with `_bug1756_in_process_reverify`, which intercepts the loaded validator's real `subprocess.run` lookup and raises `OSError(8)` or `TimeoutExpired`. Receipt arm 3 proves both arms fail under the exception-propagation mutant; QA confirms both pass at the pin (`review-harness-qa-c1.md:25,29`).
- **Q2 — closed.** Receipt arm 2 runs the final test file against pre-fix validator `24e766bb` and records SC-01, SC-02, and SC-03 each failing with exit 2 and `argv=[]`. The pinned test diff contains the same exact assertions QA executed green (`review-harness-qa-c1.md:22-24,30`).
- **Q3 — closed.** The reviewed range is based on `origin/main` merge-base `8ef4731e816f08dbc562206134c100b0c034a812`, excludes the operator's unrelated local commits, and does not modify `tests/unit/omp-hooks.test.ts`. QA's authorized pinned unit run executed 40 files, including that bun test, with `74 pass, 0 fail, 155 expectations` (`review-harness-qa-c1.md:13,31`). The repaired hook then reran both named kinds and accepted the unconditional QA PASS (`:32`).

## Trace, findings, and must-fix

`plan.yaml#T-01` traces all four SCs. The signed brief defines no REQ identifiers, so there is no separate REQ-coverage ledger.

```yaml
findings: []
must_fix: []
```

Every non-empty finding would require `kind`, `severity`, `task`, and a concrete failure scenario; none is supported by the pinned outcome evidence. Open questions are empty.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both signed perspectives pass; SC-01 through SC-04 are met and c0 Q1/Q2/Q3 are closed at review_sha c1f9601fe87660b732aac0bf5e5f72dd17fac0d7."
  feasibility: clear
  surface: M
  flags: [bugfix, gate, subprocess]
  recommend: proceed
  tasks: 1
  decisions: 0
  needs_approval: false
  risk: low
  sc_status:
    - { id: SC-01, verdict: met, method: automated, evidence: "review-harness-qa-c1.md:14,22; receipt-main-session-T-01-fail-first.md:19-20" }
    - { id: SC-02, verdict: met, method: automated, evidence: "review-harness-qa-c1.md:14,23; receipt-main-session-T-01-fail-first.md:21-22" }
    - { id: SC-03, verdict: met, method: automated, evidence: "review-harness-qa-c1.md:14,24; receipt-main-session-T-01-fail-first.md:17-18" }
    - { id: SC-04, verdict: met, method: automated, evidence: "review-harness-qa-c1.md:14,25; receipt-main-session-T-01-fail-first.md:3-5,31-33" }
  open_questions: []
  files_touched: [/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1756-qa-reverify-bash/.harness/harness/features/BUG-1756-qa-reverify-bash/notes/research-BUG-1756-qa-reverify-bash-goalcheck-validate-c1.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1756-qa-reverify-bash/.harness/harness/features/BUG-1756-qa-reverify-bash/notes/research-BUG-1756-qa-reverify-bash-goalcheck-validate-c1.md
```
