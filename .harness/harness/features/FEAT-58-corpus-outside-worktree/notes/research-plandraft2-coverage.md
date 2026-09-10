# Coverage — FEAT-58 plan draft, cycle 1 — pm

**The plan is complete: 19 tasks, 11 decisions, 22 of 22 SC and 10 of 10 REQ traced, DAG acyclic,
`check-plan-routes.py` exit 0 with 0 violations.** The two halted-plan survivors (`T-17`, `D-15`)
are deleted; the remaining set is exactly `D-01..D-11` and `T-01..T-16, T-18, T-20` (no `T-17`).
Two things need the operator at signature: **D-06's arm**, and its interaction with **SC-22**
(below). The stale `lanes:` block is unwritable through `plan-merge` and still describes the
halted plan — raised upward, not touched here.

## SC → task, all 22

| SC | Task | SC | Task |
|---|---|---|---|
| SC-01 | T-13 | SC-12 | T-11 |
| SC-02 | T-05 | SC-13 | T-19 |
| SC-03 | T-06 | SC-14 | T-01 |
| SC-04 | T-07 | SC-15 | T-03 |
| SC-05 | T-07 | SC-16 | T-04 |
| SC-06 | T-07 | SC-17 | T-03 |
| SC-07 | T-18 | SC-18 | T-14 |
| SC-08 | T-08 | SC-19 | T-13 |
| SC-09 | T-08 | SC-20 | T-15 |
| SC-10 | T-09 | SC-21 | T-16 |
| SC-11 | T-10 | SC-22 | T-20 |

## REQ → task, all 10

| REQ | Tasks |
|---|---|
| REQ-01 | T-02, T-03, T-05, T-06, T-13 |
| REQ-02 | T-02, T-03, T-07 |
| REQ-03 | T-02, T-08, T-18 |
| REQ-04 | T-09, T-10 |
| REQ-05 | T-01, T-19 |
| REQ-06 | T-03, T-04 |
| REQ-07 | T-12, T-13, T-14, T-15, T-16 |
| REQ-08 | T-07 |
| REQ-09 | T-11 |
| REQ-10 | T-20 |

Every task traces at least one REQ. No SC is uncovered; no placeholder task was written.

## The final task list

T-01 suite baseline · T-02 synthetic fixture · T-03 `worktree-state.py` (six exits, idempotence) ·
T-04 `--verify` never repairs · T-05 required-paths positive control · T-06 derivation not literal ·
T-07 gitignore + corpus read/refusal · T-08 audit refuses + peer-sweep root · T-09 `feature-index.py`
+ uniqueness rule · T-10 `merge-gate.py` deny/allow + index staleness · T-11 the D-06 real-data act ·
T-12 the three hook shims · T-13 creation, harness route and bare route · T-14 the merge regression ·
T-15 rebase / `post-rewrite` · T-16 shim integrity per shim · T-18 finding-set equivalence ·
T-19 non-worktree unchanged · T-20 nothing altered.

Decisions: `D-01`..`D-11`, unchanged from cycle 0.

**19 vs the halted plan's 16.** Not a bigger feature — a different one. The halted plan carried a
worktree-convergence task, a corpus API in `harness_boundary.py`, a fifteen-reader ledger and the
`linked_worktrees` denial-tier fix (`T-17`/`D-15`, REQ-12), none of which the re-authored BRIEF
carries. What replaced them is one task per criterion where the DoD demands separation: SC-07,
SC-18 and SC-16 each got their own task, as did SC-02, SC-03, SC-19, SC-20 and SC-21.

## Resolved here, previously open

- **Who applies the cone at creation (T-13 intent).** The `post-checkout` hook alone;
  `feature-worktree.py` is not modified and appears in no task's `files:`. `post-checkout` fires on
  `git worktree add` with cwd already inside the new tree (independently reproduced,
  `notes/receipt-harness-dev-ops-arch2-eng.md` §A), so the harness route and the bare route are one
  code path. An explicit `cmd_create` call would make the two routes differ in source and not in
  behaviour. Same ruling as D-10.
- **Where D-01's staleness test lives.** T-10, exactly as D-01's text names.

## Open — the operator's, not mine

1. **D-06 Arm A collides with SC-22.** Arm A edits
   `.harness/harness/features/FEAT-03-subissue-mirror/feature.json`, which SC-22's unqualified
   `git diff` reports as an altered foreign feature directory. Arm B writes only
   `.harness/harness/feature-branch-exemptions.json`, outside that tree, and leaves SC-22 clean.
   T-11 and T-20 both specify the Arm A path: one named, operator-approved pathspec exclusion,
   recorded with the signature date. Under Arm B nothing is excluded.
2. **SC-21 declares `evidence: unit`; its decisive clause cannot be a unit test.** The effect-absent
   half needs a real worktree, merge and rebase. T-16 ships both halves — `tests/unit/` for the
   static per-shim assertions, `tests/integration/test-hooks-install.py` for the effect-absent proof
   extending `:397-447`. The BRIEF's declared kind is raised rather than reinterpreted.
3. **The `lanes:` block is stale** — it still names the halted plan's surfaces and cites
   `abff2a84`. `plan-merge` has no verb that writes it. D-07 carries the live lane table.
