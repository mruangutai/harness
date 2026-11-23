# Sign-off by delegated authority — BUG-2420 — 2026-11-22

## Delegation

On 2026-11-22 the operator, Mike Ruangutai, gave this instruction for Feature C (FEAT-2397):
**"start feature C. same rules, defer to fable-advisor."** This patch exists because
`fable-advisor` ruled (`AdvisorC3Stations`, option B) that FEAT-2397's task-station deadlock is fixed
as a separate patch shipped to main first. Its questions and approvals therefore go to
`fable-advisor` under the same delegation.

## Presented

Presented to `fable-advisor` (`AdvisorC4PatchSignoff`) at plan HEAD `f5d6d7d2`:
- BRIEF.md (SC-01..03) and plan.yaml, both pending.
- Plan: one main-session-direct T-01 with an explicit `status: ready`.
- Proposed rework: 1 round / 45 min (patch mission).

## Ruling (fable-advisor, on the operator's behalf)

1. **Approve, with two conditions to land before signature.** All five AdvisorC3Stations
   constraints are honoured.
   - The plan inserts at the field indent and rewrites an existing status unchanged.
   - A missing task gets its own refusal, distinguishable from a missing status line.
   - `apply` does not seed status.
   - Tests: a 3-row unit table, one integration case on the drafting path, and a byte-identical
     approval assertion that also requires the insertion to succeed.
   - It does not duplicate BUG-2349's tests, and its scope is `stations.py` plus its tests.
2. **Condition 1.** Remove the false claim that the product docs are absent. Point the BRIEF and
   T-01 intent at `.harness/harness/docs/SPEC.md` and `DECISIONS.md`.
3. **Condition 2.** Drop the inert `export CLAUDE_PROJECT_DIR` from T-01's verify, and the intent
   clause crediting it. Keep `cd` and both unsets.
4. **Rework: 1 round / 45 minutes.**

Both conditions landed at `294faa6f` (amendment run `2026-11-22-02-patch-product`). Main verified
them: the plan has no `CLAUDE_PROJECT_DIR`, and both files point at the real SPEC/DECISIONS paths.

Signed by the main session as `Mike Ruangutai (delegated to fable-advisor)`.
