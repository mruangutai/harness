# BRIEF — FEAT-2225 Member Expertise writes

## Problem

FEAT-2206's security reviewer accepted an Expertise replacement but could not execute the prescribed merge route. Its shell-less lead staged the op, requested main-session execution, and returned BLOCKED even though the member's judgment was complete. All 16 personas already retain Write and grants to their own Expertise; contradictory application instructions turn a successful distillation into an execution handoff. Separate feature worktrees also need reconciliation before their Expertise changes reach main.

## Done when — by perspective

**operator** — I can finish distillation without acting as another persona's scribe or accepting a false execution-only BLOCKED. Concurrent distills preserve accepted learning or return a real conflict to its author rather than silently losing it.

**orchestrator** — I can rely on each member having applied the ops it reports and its lead having checked the result. I confirm completion without acquiring another persona's pen.

**code maintainer** — I can change one existing merge mechanism and understand one current application contract, including who writes, where changes land, and how concurrent changes reconcile. Existing capability limits and grants remain intact.

## Success criteria

- SC-01 (operator): Every one of the 16 configured personas can use the caller-bound host tool under a distill dispatch to create its own feature-worktree Expertise and apply add, replace and drop with a receipt, for craft and repository destinations, without a shell, scribe, IRC execution request or execution-only BLOCKED. Tests independently assert each persona's tool availability, retained Write and own-file grants; capability-class behavioral representatives cover a shell-less lead, READ-ONLY reviewer, dev-ops, orchestrator and leaf developer. QA demonstrates the missing capability fails first.
  verify: automated evidence: integration
- SC-02 (orchestrator): Mixed-persona expertise_update items require persona and forbid state; a member may report only its own applied ops, a lead's consolidated list matches its members' verified receipts, and live-yield plus durable close-run validation refuse fabricated, missing or file-inconsistent receipts. Rejected candidates remain valid with an empty list. The lead reads the receipt and resulting file; the orchestrator confirms and never applies another persona's ops. QA demonstrates the new refusals fail first.
  verify: automated evidence: integration
- SC-03 (code maintainer): Caller identity, feature and runtime lineage cannot be supplied or overridden by tool arguments; a held, unidentified or non-distill caller cannot apply. Cross-persona, control-plane, global-tier, undeclared-repository and symlink-escape tool destinations refuse without writing. Direct shell expertise-merge mutation is blocked for governed callers, including dev-ops, without removing their existing Write ability or own-file grants. Unreceipted or file-inconsistent changes cannot pass close-run or replay/merge integrity checks. QA demonstrates these boundary cases fail first.
  verify: automated evidence: integration
- SC-04 (operator): Two independent worktrees adding the same section/id preserve both entries when recorded ops are replayed onto current main; colliding adds receive deterministic fresh ids. An entry changed on main makes a same-entry replace/drop refuse, and cap overflow refuses rather than truncates; the lead returns the exact conflict to the original member for re-judgment/curation. That member can authorize a replacement batch that supersedes its refused batch for active replay while retaining historical receipts in the current PR; another persona cannot retire it. Repeated replay does not duplicate entries, and a refused file remains unchanged. QA demonstrates each new replay behavior, including refusal → original-member re-judgment → successful replay, fails first.
  verify: automated evidence: integration
- SC-05 (orchestrator): Both git-merge and gh-pr-merge routes, including the OMP main session, identify a distill PR by its changed Expertise paths and require recorded ops, replay/check-expertise success and an up-to-date main-base receipt. Distill merges serialize against current main and retain DEC-220's existing owner/binding/mirror-receipt predicate before the synchronous internal gh merge: replay-valid candidates with missing, wrong-repository or recovery-required build-entry evidence refuse without merging. A second stale candidate, missing receipt, changed head/base, unresolved replay or unidentifiable changed-path set is refused. Ordinary non-distill merge behavior remains unchanged. QA demonstrates each added refusal fails first.
  verify: automated evidence: integration
- SC-06 (code maintainer): At git show <review_sha>:<path>, the changed SPEC Expertise passages, distillation procedure, distill/expertise/curate skills and persona guidance consistently name member application, feature-tree destinations, lead verification, orchestrator confirmation, replay and refusal routing. DEC-86 is struck under DEC-188 with the new decision as successor; DEC-125/69/87/106/151 are corrected in place, DEC-18/145/199/219 remain unchanged, and the new decision cites every strike/correction. The decision index is regenerated and incoming live DEC-86 references in the owned decision file are repointed. Inspection cites the pinned files and sections, not working-tree content.
  verify: inspection

## Verification gaps

- typecheck has cmd: null and status: unresolved; the TypeScript host-tool change in SC-01/03/05 is not proven by a configured static typecheck. Bun-backed unit tests and integration boundary tests carry executable evidence instead; no typecheck success is claimed. This standing runner gap is recorded for dev-ops at signature, not silently skipped.
- component and ui have unresolved null runners but this feature has no browser/UI surface; no SC rests on them. functional and eval are excluded by DEC-187 and carry no SC here. Unit and integration are active, runnable directory-selected kinds; cross_module uses their configured floor. No operator UAT criterion is needed.
- T-03's MANUAL prerequisite affects SC-01/02/03/04/05/06: guidance and tool grants cannot be exercised until T-04 builds the host-tool/contract assertions. T-04 is the terminal automated behavior gate; SC-06 additionally requires pinned-content inspection. This is a task-ordering gap, not a claim that the integration kind lacks a runner.
- The configured locally_run handoff_comprehension probe requires OMP and live model credentials. Before ship, run tests/manual/probe-handoff-comprehension.py on a credentialled host and record its result in this feature's notes; it is not part of this planning run or claimed as executed.

## Constraints

- Binding intake: .harness/notes/grilling-member-expertise-writes-2026-11-21.md, Settled; it governs over issue #2225's proposed pending/state/scribe design. Source issues: [2225]. Mission: plan, operator-confirmed.
- SUPPLIES: DEC-199's harness_merge lock/atomic-update core and DEC-219's section/id ops and base-snapshot semantics; reuse them rather than introduce a second merge implementation. Keep these decisions unchanged.
- BLOCKS: DEC-18 keeps leads without Bash/Edit; DEC-151 keeps reviewers without shell writes. All 16 retain Write and their existing own-Expertise domain grants; adding a narrow caller-bound tool is not granting broader shell access.
- BLOCKS: DEC-145 keeps member judgment, distillation-only Expertise writes and ordinary-run empty expertise_update. Keep its entry unchanged; the new successor decision states the new application mechanism explicitly.
- BLOCKS: DEC-174 requires host hooks, dispatch/digest/write/merge enforcement, schemas and their tests to execute main-session-direct. Resolve every owned path through check-domain; an ungranted skill or persona path is also a declared main-session step, never an assumed squad grant.
- SUPPLIES: DEC-188 and DEC-205 govern the DEC-86 strike and present-tense corrections; DEC-202 makes .claude/skills the authored tree, with .agents/skills only a discovery symlink. No approval is authored or signed by this run.
- SUPPLIES: DEC-220's shared owner/binding/mirror-receipt predicate remains mandatory for merge-distill, including recovery-required refusal; the internal gh subprocess is not a second host-tool enforcement event.

## Out of scope

- A full Expertise queue or background reconciler with an ops ledger independent of PRs: replay before merge covers the need at its smallest size.
- The plan-template decisions_affected block and goal-check grading of dispositions: separate issue #2229.
- A reciprocal-link checker for decisions: deferred in #2229; it would reintroduce automated detection removed by DEC-188.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-21
