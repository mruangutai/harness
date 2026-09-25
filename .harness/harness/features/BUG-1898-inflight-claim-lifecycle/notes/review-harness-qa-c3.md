# QA gate — BUG-1898 c3

**BLUF: PASS.** At immutable pin `6bfc21e3ccdf78eb86cdd0eb250067348d887096`, the repaired suite-preservation oracle passes only for the complete two-label BUG-1898 mutant signature; both required matrix gates pass, F-01/F-02 remain closed, and SC-07 remains an unrun operator gate.

## Scope and matrix

- Canonical range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..6bfc21e3ccdf78eb86cdd0eb250067348d887096` (47 paths); focused c3 range: `4942950a83c1895d85922f7cd9e9cfd41e28daf8..6bfc21e3ccdf78eb86cdd0eb250067348d887096` (nine feature-record/note paths plus `tests/integration/test-suite-claim-preservation.py`).
- Phase 1 expectation from BRIEF/plan: unit coverage for SC-02/SC-04; integration coverage for SC-01/SC-03/SC-05/SC-06 and T-04's config-shape change; exact mutant identity/count proof for SC-01. The `bugfix` runtime predicate and config-shape predicate together require unit + integration. No configured typecheck runner applies; UI/component do not match this lifecycle change.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` — exit 0; 42/42 named files PASS.
- `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` — exit 0; 70/70 named files PASS, including `test-validate-digest.py` and `test-suite-claim-preservation.py`.
- `python3 tests/integration/test-suite-claim-preservation.py` — exit 0; pinned suite, byte-identical governed-persona sentinels, and real persona-release mutation all PASS (0 wrapper failures).

## Exact oracle and negative controls

The real mutation path in `tests/integration/test-suite-claim-preservation.py:107-121` copied the pinned validator bin, installed the persona-wide release mutant, ran the real `test-validate-digest.py`, and passed its equality assertion at lines 115-119. Its extracted complete `FAIL  [bug1898]` set is exactly:

1. `after the child settles the identical yield passes`
2. `and releases only the parent`

The child accounting remains 79/81 BUG-1898 exact-release checks passed, with nonzero child exit. The four other child failures are relocated-copy/schema controls — `drifted key spelling is caught`, `enum near-miss is caught, not normalized`, `code reviewer omission of code_grade is rejected`, and `code_grade's missing-field hint names the four legal values, not the list wording` — and each is `FAIL  ` without the `[bug1898]` prefix. They therefore neither enter nor spoil the equality set.

I independently invoked the pinned `mutant_run` predicate with a one-required-label control and with `unrelated lifecycle regression` as its only BUG-1898 label. Both printed `FAIL a persona-wide release reddens exactly the parent-settlement checks` and exited 0 only because the harness asserted that rejection; neither subset nor replacement passed the oracle. This binds the checker to exact identity rather than nonempty redness.

## SC status and fail-first

| SC | status | current evidence | fail-first source |
|---|---|---|---|
| SC-01 | met | preservation oracle; exact real mutant and both negative controls | `notes/review-harness-qa-c0.md:23` |
| SC-02 | met | unit gate; `tests/unit/omp-hooks.test.ts` | `notes/review-harness-qa-c0.md:24` |
| SC-03 | met | integration gate; `tests/integration/test-inflight-registry.py` | `notes/review-harness-qa-c0.md:25` |
| SC-04 | met | unit gate; `tests/unit/omp-hooks.test.ts` | `notes/review-harness-qa-c0.md:26` |
| SC-05 | met | integration gate; `tests/integration/test-check-omp-port.py` | `notes/review-harness-qa-c0.md:27` |
| SC-06 | met | integration gate; `tests/integration/test-validate-digest.py:5815-5844` | `notes/review-harness-qa-c0.md:28` |
| SC-07 | pending_operator_gate | intentionally not run; no live receipt claimed | n/a (UAT) |
| SC-08 | met | unchanged inspection evidence in `notes/review-harness-qa-c0.md:32-36` | inspection |

F-01 and F-02 remain closed: the passing integration gate retains unreadable-registry no-write/blocked-only and exact held-child/parent-only settlement cases; c3 changes only the oracle test. No findings; coverage gaps are limited to the BRIEF-recorded non-gating typecheck runner and pending SC-07 operator receipt.

## Cleanup

A `git archive` at the pin ran the focused oracle successfully but cannot satisfy configured runners that require `.git`; its archive-only unit failure was correctly classified as environment misconfiguration, not a pin regression. I then used a detached exact-pin worktree for the configured gates, confirmed their success, removed it cleanly, and removed both temporary archive directories. No formatter, linter, live OMP, or unrelated suite ran.

## Principles applied

- **Build the Lever** — the retained deterministic preservation wrapper was rerun, including its real copied-bin mutation, instead of hand-evaluating output labels.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned c3 exact oracle accepts only the two required BUG-1898 parent-settlement reds; unit/integration gates pass and no regression remains."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 42 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 70 }
  coverage_gaps:
    - "Configured typecheck has no executable runner for .omp/extensions/harness-hooks.ts; BRIEF.md records it as non-gating."
    - "SC-07 remains the required pending_operator_gate live OMP receipt."
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-suite-claim-preservation.py:107-121" }
    - { id: SC-02, test: "tests/unit/omp-hooks.test.ts:1875-2001" }
    - { id: SC-03, test: "tests/integration/test-inflight-registry.py:1238-1410" }
    - { id: SC-04, test: "tests/unit/omp-hooks.test.ts:2003-2113" }
    - { id: SC-05, test: "tests/integration/test-check-omp-port.py:194-214" }
    - { id: SC-06, test: "tests/integration/test-validate-digest.py:5815-5844" }
    - { id: SC-08, test: "notes/review-harness-qa-c0.md:32-36" }
  fail_first:
    - { sc: SC-01, evidence: "notes/review-harness-qa-c0.md:23" }
    - { sc: SC-02, evidence: "notes/review-harness-qa-c0.md:24" }
    - { sc: SC-03, evidence: "notes/review-harness-qa-c0.md:25" }
    - { sc: SC-04, evidence: "notes/review-harness-qa-c0.md:26" }
    - { sc: SC-05, evidence: "notes/review-harness-qa-c0.md:27" }
    - { sc: SC-06, evidence: "notes/review-harness-qa-c0.md:28" }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-qa-c3.md
```
