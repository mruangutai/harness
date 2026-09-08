# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: c16 SC-11 routing — `runs/2026-09-08-1-product/` (pm via product lead, BRIEF + plan
  amendment, PASS). No validator run: the amendment is product/state only, and the remedy it grades
  is DEC-174 main-session-direct.
- squad: product (brief + plan only)
- station: **building** (`plan.yaml` `status:`), T-05 `building`. Unchanged by this run.
- budget: **`cycles_used` 15 of `max_total_cycles` 16 — NOT incremented this run.** No FAIL was
  routed back, no unmet SC was re-dispatched and the lead reported zero send-backs (DEC-157: cycles
  count rework, and an operator-ruled amendment is not rework). `len(runs)` 48 of `max_total_runs`
  20 — INFORMATIONAL (INV-22); the count is high because this feature has run 13 remediation and
  grading cycles, and the recent ones each resolved a named defect.
- `review_sha` still reads `e374c9a29e4321968e4c2a6bbae045da9203440c` and is **STALE**: `plan.yaml`
  and `BRIEF.md` have both changed since the pin. It must move to the tip carrying the parser fix
  before any validator run (INV-6, INV-33).
- Approvals — **BOTH are now stale and both are the main session's act**: `BRIEF.md ## Approval`
  reads approved 2026-09-08 over text amended after that signature (SC-11), and `plan.yaml`
  `approval:` reads approved 2026-09-08 over T-05 text and D-16..D-18 amended after it. No governed
  agent can repair either — `approval_guard` denies the BRIEF fragment, `sign-approval` is refused
  at the tool.

### Operator ruling R-6 — SC-11 is added

`notes/rulings-2026-09-08-c16-sc11.md` (orchestrator transcription of an inline main-session relay;
there is no answers file on disk for this round and that note is not that channel).

> Add SC-11: `git merge --abort/--continue/--quit` must remain allowed to recover from interrupted
> merges even when the current branch owes a receipt.

The SC-04 exclusion sentence and the disclosed-gap option were both DECLINED. Q1 of the previous
`## Open Questions` is closed by this ruling; what remains of it is the signature.

### What landed, verified on disk by the orchestrator

- `BRIEF.md` — **append-only, one hunk** (`@@ -160,0 +161,12 @@`, +12/-0). SC-11 carries the three
  commands, the owing condition (`github.build_entry` absent under enabled sync or
  `recovery-required`, not in `feature_schema.BUILD_ENTRY_ERA_EXEMPT`), the required outcome (exit 0,
  no permissionDecision object), the recovery rationale, the **three T-05 case names verbatim**
  (`grep -c` = 3) and the `e374c9a2` discrimination requirement.
  `verify: automated  evidence: integration`.
- `BRIEF.md ## Approval` — byte-identical, still `approved / Mike Ruangutai / 2026-09-08`.
  SC-01..SC-10, `## Requirements`, `## Constraints` and `## Verification gaps` unchanged.
- `plan.yaml` — **D-18** added through `plan-merge.py apply` (one hunk, `@@ -307,0 +308,22 @@`;
  ids now D-01..D-18): control operations graded by a new criterion, never by reopening SC-04;
  `dec: DEC-132`. `approval:` (lines 3-24) and `panel:` untouched.
- The evidence binding is real: all three case names are present in T-05's `verify:` list
  (`plan.yaml:1043`) and declared in its `intent` (`:1440-1443`).
- `feature.json` — run `2026-09-08-1-product` appended, `code_grade` key omitted (this run graded
  neither code nor a plan panel). No other key changed.

### Next, in order — unchanged by this ruling

`notes/direct-packet-2026-09-08-c16-parser.md` — main-session-direct, the whole of it: seven
discriminating cases red first → the `git_merge` edit → the suites, T-05's `verify:` and
`code-grade` → commit + `set-task-station T-05 done` + the two `gh-sync.py` mirror writes. Then back
to the orchestrator: re-pin `review_sha` → `gh-sync.py status <feature-dir> review` → qa
`test_matrix` → panel c17 over the delta → pm goal-check of SC-04 **and SC-11** → extend UAT Step 3b
→ operator SC-10 UAT → rewritten briefing → ship.

## Open Questions

- Q1 (blocking, operator — **two signatures, the whole remaining product act**) — `BRIEF.md`
  `## Approval` must be re-signed over SC-11 (main-session-owned fragment; every governed agent is
  denied), and `plan.yaml` `approval:` must be re-signed with
  `plan-merge.py sign-approval` over the T-05/D-16/D-17/D-18 amendments. Neither blocks the
  main-session-direct implementation; both gate the ship.
- Q2 (non-blocking, pm recommendation) — the code-grade bar stays OUT of the success criteria: a
  quality gate, gated by T-05's `verify` and recorded as D-17. Consequence: no goal-check reports
  the grade; only T-05's verify and the panel's code-grade reader do.
- Q3 (non-blocking, plan hygiene, pre-existing) — T-05's enumerated case-name contract lists 21
  names while `verify:` gates 26; the five D-13/D-14 names never reached the enumeration. Harmless
  today (those cases exist and pass), but the enumeration no longer is the contract it claims.
- Q4 (non-blocking, harness defect) — `harness-pm`'s terminal yield carried null data (job status
  `failed (exit 1)`) while a complete, well-formed VERDICT/DIGEST/artifact block was present and
  every claimed change verified on disk. Seen on two consecutive cycles; no re-spawn was spent.
- SC-10 UAT is still NOT requested and still blocks the ship; its Step 3b needs the three
  previously-allowed forms once they deny.
- The stale briefing at `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still
  await operator disposition; rewritten after the fix lands, before the ship decision.
