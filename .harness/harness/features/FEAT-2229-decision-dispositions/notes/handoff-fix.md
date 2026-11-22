# Handoff — FEAT-2229-decision-dispositions, validate (FAIL) → fix (main-session-direct segment) — written at 5eb1302a, seq-6

## Next

The validate run `r-20261121-validate-validator` returned FAIL at pin 1ef1edbf with three `must_fix` findings, every one citing T-01 or T-02 (`execution_mode: main-session-direct`, DEC-174): no squad dev owns them, so the fix is one main-session segment inside the rework ruling (round 1 of 3, 12 of 90 minutes spent at close). Fix all three test-first on top of 5eb1302a, in one `[harness:fix-c1]` commit (or one per task); re-run both signed verifies verbatim plus the full unit and integration runners; then re-delegate the orchestrator, which re-closes the FAIL run with `run-end --cycles-used 1` (P-11), re-pins `review_sha`, runs `gh-sync.py status review` and dispatches the second validate over the new pin.

RULE for each fix: the pinned behaviour the reader named must become red under a new fixture, then green. LEAVE everything else: D-01/DEC-254 content, `_is_draft` reading `FINISHED_STATIONS`, pm Mode 2's `<repo-relative DECISIONS.md path>` placeholder, the `## The gate` placement, every simplify leave note (L-1..L-4) and briefing row (B-1, B-2), the `create: true` plan-check behaviour on landed plans.

1. **F1 — T-01 / SC-01 / high.** `.claude/skills/harness/bin/plan_merge/union.py` `_seed_new_plan` (pinned :324-346) returns creation bytes after `_parsed_proposal` (YAML + anchors, :392-400) without `harness_yaml.validate_plan_doc`; an otherwise valid new-plan proposal carrying `decisions_affected: [{dec: DEC-10}]` is written and reported APPLIED, and only the next load refuses it. Fix: validate the parsed proposal's disposition shape before the creation write (the existing `set-key` refusal path is the model), refuse with no file written. Fixture: a CLI `apply` against an absent base with that malformed row → nonzero exit, no plan file; a valid-row control still creates. Verified premise: `union.py` calls `validate_plan_doc` only via `_verify_schema_preserved` (:51,:78), which creation never reaches — read at 5eb1302a.
2. **F2 — T-01 / SC-02 / med.** `plan_merge/check.py` `_Authority.section` (pinned :299-305) locates the DEC heading over every physical line with no fence state, while `_section_end` (:277-285) tracks fences only from that start. A fenced example `## DEC-10` inside DEC-11's section (before the real `## DEC-10`) is taken as DEC-10's section, so a clause present only in DEC-11's example satisfies a DEC-10 row; the end scan may also mistake the example's closing fence for an opener. Fix: skip fenced lines when locating the heading, and track fences consistently (same `FENCE_RE`, :201) from the top of the file. Fixture: a DECISIONS.md with the fenced impersonating heading → `plan-merge.py check` fails the row naming the wrong-section clause; the real-section control passes.
3. **F-01 — T-02 / SC-07 / med.** `tests/integration/test-plan-team.py:481-483` asserts pm Mode 2's strike test only up to `a strike only when the strike record exists`; deleting the alternative at `.omp/agents/harness-pm.md:78-79` — `or the deletion is justified by its named successor with citations repointed (DEC-188, DEC-205)` — leaves every pattern matched. Fix: an owner-scoped assertion for that alternative and a mutation witness in `notes/red-first-T-02.md`'s style that reddens when it is deleted. Test-only change; the instruction text stays.

Verify verbatim after the fixes (T-01, T-02 signed `verify:`):

```
set -eu
python3 tests/unit/test-decision-disposition-schema.py
python3 tests/integration/test-plan-decision-dispositions.py
python3 tests/integration/test-plan-team.py
```

plus `python3 tests/integration/test-plan-merge.py`, `python3 tests/integration/test-checker-structure-locks.py`, and `code-grade.py --base dfa52536 --head HEAD`, all with `HARNESS_AGENT_TYPE` unset.

## Trust

- Pin `review_sha` = 1ef1edbf4cd13eed110e5a187fe45b2ce0438d43 (station commit; code-identical to seam 108662c4); HEAD 5eb1302a differs only in `feature.json` — `git -C <worktree> log --oneline -3` — verified-at 5eb1302a
- T-03 landed 6c4da464 (DEC-254 @ DECISIONS.md:8253, DEC-188 rewritten @ :5290; index regenerated; SPEC folded); literal verify rc 0; pm graded the DEC-188 amend row **met** at the pin — `runs/r-20261121-t03-product/digest.md`, `notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c1.md` §Decision-disposition outcome — verified-at 1ef1edbf
- SIMPLIFY `r-20261121-simplify-build-eng` PASS, empty apply; briefing rows B-1 (index grammar triplicated across check.py / check-plan-routes.py / gen-decisions-index.py), B-2 (SPEC/DECISIONS prose duplication); leaves L-1..L-4 — `runs/r-20261121-simplify-build-eng/digest.md` — verified-at 6c4da464
- Validate readers: qa PASS (matrix_ok true, fail_first for SC-01/02/03/07), security PASS, ui PASS (self-scoped census), code FAIL (F1, F2), pm goalcheck FAIL (SC-01/02/07 partial, SC-03..06 met, DEC-188 met) — `runs/r-20261121-validate-validator/digest.md`, `notes/review-harness-*-c1.md` — verified-at 1ef1edbf
- Five suites rc 0 and code-grade rc 0 (83 passing) measured by the orchestrator at 6c4da464 — verified-at 6c4da464
- Station: tasks T-01..T-03 `done` in plan.yaml; feature station `building` again (`gh-sync.py status building` at 5eb1302a wrote #2278/#2279/#2280 → building) — plan.yaml:7 — verified-at 5eb1302a
- Spend at close of validate: 6 runs, 64 min, 0 cycles, rework 12 min / 0 rounds; `max_total_cycles` 10 — feature.json `spend` output of close-run — verified-at 5eb1302a

## Dead ends

- No `fix` dispatch to harness-validator-lead for these findings: the owning tasks resolve to NOBODY (`check-domain.py --resolve` on union.py/check.py → harness-dev-ops is the simplify apply lane only; T-01's `files:` are main-session-direct by the signed plan) — plan.yaml T-01/T-02 `execution_reason` — verified-at dfa52536
- Do not re-run the validate panel over 1ef1edbf (SC-13); the next validate needs a new pin that contains the fixes — build-phase.md step 5 — source
- Do not renumber or touch DEC-254; it was unallocated on main at d6d426ad and is now T-03's — DECISIONS.md:8253 — verified-at 6c4da464
- `plan-merge.py check` on this plan reports T-01's `create: true` rows as existing files: pre-existing post-landing tool behaviour (also FEAT-2225), backlog candidate, not a finding — notes/receipt-main-session-T-01-T-02.md §Known — source

## Working set

- .harness/harness/features/FEAT-2229-decision-dispositions/runs/r-20261121-validate-validator/digest.md
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/review-harness-code-reviewer-c1.md (F1, F2)
- .harness/harness/features/FEAT-2229-decision-dispositions/notes/research-FEAT-2229-decision-dispositions-goalcheck-validate-c1.md (F-01)
- .harness/harness/features/FEAT-2229-decision-dispositions/plan.yaml (T-01:129-241, T-02:243-332)
- /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/references/build-phase.md (step 6)

## Done when

Scope: F1, F2, F-01 fixed test-first on top of 5eb1302a and committed, both signed verifies and the full runners green, orchestrator re-delegated for cycle attribution, re-pin, status review and the second validate
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#operator
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#reader
Authority: brief-perspective:.harness/harness/features/FEAT-2229-decision-dispositions/BRIEF.md#code maintainer
Authority: plan-task:T-01.verify
