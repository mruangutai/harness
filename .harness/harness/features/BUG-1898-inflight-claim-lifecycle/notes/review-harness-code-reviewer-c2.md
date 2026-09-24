# Code review — BUG-1898 — c2

**BLUF.** PASS. Spec compliance and code quality both pass at exact pin `4942950a83c1895d85922f7cd9e9cfd41e28daf8`. F-02 and F-QA-01 are closed, F-01 has not regressed, and SC-07 remains `pending_operator_gate` rather than a panel failure.

## Scope

- Canonical base measured with `git merge-base origin/main <pin>`: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`.
- Reviewed range: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..4942950a83c1895d85922f7cd9e9cfd41e28daf8`; focused c2 delta: `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e..4942950a83c1895d85922f7cd9e9cfd41e28daf8`.
- No `[harness:human]` commits are in scope. The only tracked dirt is Harness-owned `feature.json`; `notes/cancelled-c1/` was ignored. Pinned source is otherwise clean. No scratch worktree was created, so none required removal.
- Per dispatch, no tests, formatter, linter, or project-wide suite was run. Static evidence comprised pinned diffs and the canonical code-risk grader.

## Stage 1 — spec compliance: PASS

The c2 delta serves SC-01/T-03/T-04 and SC-03/SC-06/T-03 without scope creep or mismatch. `_registry_errand` now performs only exact identity and canonical-root resolution, `_settle_in` strict-reads own and child claims before the child refusal gate, and `_release_own` contains the single exact release (`validate-digest.py:2306-2351`). The hook still performs this errand before digest validation (`validate-digest.py:2395-2410`), preserving the required release/read ordering.

- **F-01 remains closed (owned task T-03).** Any strict own/child read error exits `_settle_in` through `_unreadable_registry` before `_release_own` is reachable; a dispatching non-BLOCKED return is refused and no registry write occurs (`validate-digest.py:2290-2340`). No fail-open or write-before-refusal regression was found.
- **F-QA-01 closes (owned tasks T-03/T-04).** The wrapper uses a PID-qualified feature and runtime identities, eliminating the prior fixed-PM collision (`test-suite-claim-preservation.py:29-73`). More importantly, its mutant run substitutes the validator binary through the suite's real `VALIDATE_DIGEST_BIN` seam, changes `inflight_registry.release` to ignore only `agent_id`, and accepts failure only when output contains a `FAIL  [bug1898]` exact-release assertion (`test-suite-claim-preservation.py:31-42,76-80,100-111`; `test-validate-digest.py:28,5880-5898`). A crash alone supplies neither that discriminator nor acceptance, so this is a genuine exact-release mutant rather than an exit-code-only test.
- DEC-204 remains current truth for exact run-start ownership, canonical feature-root release, `pi.events` settlement, and held-child refusal (`DECISIONS.md:6383-6435`). SC-07 remains `pending_operator_gate`; no live receipt was inferred or fabricated.

## Stage 2 — code quality: PASS

**F-02 closes (owned task T-03).** Canonical code-risk measurement over the focused c2 delta reports every changed production Python function at or above the production bar of 4:

| Function | Cyclomatic | Cognitive | ABC | Grade |
|---|---:|---:|---:|---:|
| `_registry_errand` | 4 | 4 | 10.7 | 4 |
| `_settle_in` | 4 | 3 | 6.6 | 5 |
| `_release_own` | 3 | 2 | 3.7 | 5 |

The canonical whole-range measurement reports 127 passing changed functions, no blocking or grade-2 record. The split makes strict reads and the child gate precede the sole release call structurally, without adding a compatibility release path. No fail-open branch, silent failure regression, dead legacy selector, or substantive quality finding remains.

## Principles applied

- **Model the Domain:** identity/root resolution, settlement reads/gate, and exact release are now separate lifecycle responsibilities.
- **Delete First:** the focused delta moves behavior rather than retaining a second release path; the canonical validator contains no persona-wide or bulk fallback.

```yaml
VERDICT: PASS
DIGEST:
  headline: "F-02 and F-QA-01 close at the exact c2 pin; F-01 remains closed, and SC-07 remains a pending operator gate."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "a4d72e7fc91d0cf7a568d9e2a5225465a422170e..4942950a83c1895d85922f7cd9e9cfd41e28daf8"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-code-reviewer-c2.md
```
