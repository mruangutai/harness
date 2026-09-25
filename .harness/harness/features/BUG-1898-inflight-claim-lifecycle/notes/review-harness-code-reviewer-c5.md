# Code review — BUG-1898 c5

**PASS.** Two-stage review of canonical range `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..7893fe7a23e493dcd1554e439f28e3c9832b4de4`, focused on `f73c999482fd931021a3eb50d30aa8ab2a885283..7893fe7a23e493dcd1554e439f28e3c9832b4de4`, finds no spec violation or code-quality defect. The c4 nested-lead oracle finding is closed.

## Stage 1 — spec compliance

The only executable c5 delta is T-04's probe oracle. It directly closes F-SEC-C4-01 and serves SC-04/SC-07: `nested_ids` recognizes only lineage under an observed governed orchestrator by requiring the `governed_id + "."` prefix, so dotless `Plain` cannot qualify (`tests/manual/probe-inflight-claim-lifecycle.py:433-437`). `check_batch_ids` requires exactly one nested id (`:452-460`). `crossed_rows` requires that nested row to have persona `harness-eng-lead` and `parent_agent_id` equal to the lineage prefix, while retaining the top-level `harness-orchestrator` check (`:439-450`). Final no-row settlement includes both top-level and nested ids (`:461-466`). Thus the c4 concrete mutant—`Nest.Probe` bound to `harness-qa`—now reddens; wrong parent also reddens; a real `Nest.Probe` lead row under parent `Nest` remains green; and direct `Plain`/`Nest` orchestrators remain green.

The retained operator receipt distinguishes the immediately prior **FAIL 28/29** at `notes/live-omp-probe.md:717-909` (dotless `Plain` was incorrectly treated as nested) from the final **PASS 29/29** at `:911-1103`. The final receipt records `Plain` and `Nest` as top-level orchestrators, `Nest.Probe` as the nested `harness-eng-lead`, all S3 assertions green, suite preservation green, and an empty final registry. **SC-07 is stated from that retained receipt only; no live probe was rerun.** Earlier c4 product evidence for SC-01–SC-06 and SC-08 remains settled because the focused executable delta changes only the manual probe oracle and signals no regression.

The historical/cycle artifacts added in the focused range record validation history and the operator receipt; they do not alter shipped behavior or escape an SC/D. INV-43 late succession for `handoff-validate.md` seq-3 and the operator-owned dirty overlay remain instructed residuals, not findings.

## Stage 2 — code quality

Stage 1 passed, so quality review proceeded. The new oracle is fail-closed for the relevant defect class: no nested match or two nested matches fails the exact-one assertion; wrong nested persona or parent populates `stray`; and a nested row left after settlement is caught by the expanded no-row query. Prefix matching includes the dot delimiter and therefore does not silently classify dotless ids or sibling prefixes as descendants. The top-level behavior remains independent of nested classification.

Inspection of the final real rows confirms the accepting path is not vacuous: `Nest.Probe` is recorded as started/completed `harness-eng-lead` beneath `Nest`, while `Plain` and `Nest` remain top-level `harness-orchestrator` rows. Python risk grading over the canonical range reports `PASSING: 129`, including `nested_ids` grade 4 and all changed probe functions at or above the test-code bar; no failure or reason-required record.

## Commands and evidence

- `git status --porcelain`; `git merge-base origin/main 7893fe7a...`; human-commit grep — base `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`, no `[harness:human]` commits; dirt only in Harness feature metadata.
- `git log --oneline a4d72e7f...7893fe7a...` — full commit range walked; focused c5 executable change is the probe oracle.
- `git diff --unified=80 f73c9994...7893fe7a -- tests/manual/probe-inflight-claim-lifecycle.py` and pinned `git show` inspection — lineage-only selection, singleton requirement, nested persona/parent binding, and nested no-row settlement verified.
- `python3 .../code-grade.py --base a4d72e7f... --head 7893fe7a...` — `PASSING: 129`; no failures or grade-2 reasons.
- `python3 tests/manual/probe-inflight-claim-lifecycle.py --dry-run` — correctly refused with `prerequisites: NOT READY` because validation claims are active; it started no OMP process and ran no scenario. This is prerequisite behavior, not SC-07 evidence.
- No archive scratch or temporary directory was created; scratch cleanup: nothing remains. The operator-owned overlay was untouched.

## Principles applied

None.

```yaml
VERDICT: PASS
DIGEST:
  headline: The c5 lineage oracle closes the nested-lead gap without a fail-open path, and the retained final receipt is PASS 29/29.
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: pass
  reviewed: "a4d72e7fc91d0cf7a568d9e2a5225465a422170e..7893fe7a23e493dcd1554e439f28e3c9832b4de4"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1898-inflight-claim-lifecycle/.harness/harness/features/BUG-1898-inflight-claim-lifecycle/notes/review-harness-code-reviewer-c5.md
```
