# STATE

## Current

- feature: FEAT-18-board-truth
- run: .harness/features/FEAT-18-board-truth/runs/qa-validator/state.yaml
- squad: validator
- status: review

**All six tasks are done and the build phase is closed.** T-01/T-05 `1fd6f9a`, T-02 `4755b6e`,
T-03 `7102d45`, T-04 `bb5863b`, T-06 `6d2d61b`, with two operator re-signatures in between —
`3862a64` (T-05's `files:` list) and `5c835c7` (D-02's two false clauses). **`review_sha` is pinned
at `6d2d61b`**, which contains all six tasks, and `notes/handoff-build.md` was written at the seam
rather than reconstructed later. Gates at the pin, re-run by me: unit 0, integration 0,
`check-plan-routes.py` 0 violations, `check-state.sh` 0. **Two rework cycles of ten; five runs of
twenty.**

**In flight: the validate segment**, sequenced by me as qa → review panel → pm goal-check, returned
together. qa runs first and alone because qa *writes* tests — a panel running concurrently would be
reviewing a tree moving underneath its pin, which is the INV-6 failure.

**Live board 3 agrees with the plan, and no criterion asked it to.** `BRIEF.md`
`## Verification gaps` records that nothing in this feature observes GitHub — every automated
criterion runs against a fake `gh` because `functional` has `cmd: null` (DEC-187). The run produced
live evidence anyway: INV-26 against the real board with **zero findings**, six cards `Done`, parent
#326 derived `Review` and reading `Review`. **The `Review` derivation executed for the first time**
when T-06 went `done` — computed, never typed. This does not convert an inspection criterion into an
automated one and must not be counted as if it did; it also must not be ignored.

**Do not let a reviewer "fix" the `SKILL.md` divergence.** T-06's signed `intent:` step 2 still
listed "no board configured" among the whole-invocation skips — the exact falsehood D-02's amendment
corrected. `SKILL.md` was written against the amended D-02. The divergence is the amendment working.

## Open Questions

- None open. Q1 and Q3 were answered at signature (`BRIEF.md` `## Approval`); Q2 was overtaken by the
  2026-08-13 revision; Q4 was settled by operator re-signature at `3862a64`; Q6 by operator
  amendment at `5c835c7`. None of the five is to be reopened.
- Standing constraint on this segment: **a `not_met` criterion is reported, never fixed and never
  re-scoped.** Amending `BRIEF.md` stops the run and goes to the operator. SC-08 is **struck** —
  nine live criteria, not ten — and is never counted `not_met`.
