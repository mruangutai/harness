# Ship review — BUG-1286-test-tree-enforcement (final)

**Reviewed revision `bb3a31ed`. Branch `feat/BUG-1286-test-tree-enforcement`, not merged, worktree intact.**

## Ready to ship

Every gate is green and every criterion is met. Your cycle-11 authorisation closed all three
remedies, and the revalidation found nothing new that gates.

- **Reviewer panel: PASS**, `must_fix` empty, `severity_max: med`. All four lenses ran.
- **pm goal-check: 19 of 19 success criteria MET**, every one re-derived from scratch at the new
  pin rather than carried forward from the earlier pass.
- **`code-grade.py`: exit 0**, zero high-severity records.
- **qa `test_matrix` gate: PASS** — the project's only blocking gate.
- unit 342 PASS / 0 FAIL / 27 files; integration 14 / 0; `--check-layout` exit 0; tree-audit
  `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` and the note round-trips at exit 0; decision anchors 30 / 0;
  `check-state.sh` exit 0 with no violation and no note for this feature.

All of the above I ran myself at the pinned revision rather than accepting a report.

**The one decision left is yours: merge.** `gates.merge` is `user_gated`, and neither the merge nor
the worktree removal is mine.

## What your cycle bought

**B-1, the gating finding — closed.** `violations()` went from grade 1 to a fourteen-line
delegating function that no longer produces a grade record at all; `_registry_findings` went from
grade 3 to grade 5. Twelve named helpers were introduced and every one grades 4 or 5. The panel
verified the decomposition is byte- and order-identical in its output, and — the part that
mattered most — it drove **D-03's ordering constraint live against a real nested-checkout fixture
for the first time in this feature's history** and confirmed it fails *closed*. That was the one
way this refactor could have silently fail-opened, and it did not.

**B-2 — closed.** The audit note's SHA now reads `4b343d80`, its post-rebase ancestor twin, and
the recorded measurement was re-confirmed true at that commit rather than merely plausible.

**B-3 — closed.** `violations()`'s single-caller property now has a repository-wide assertion,
proven by live probe to redden on a second caller and to be immune to the nine files that mention
the function in prose.

## Two things you should see anyway

**The record is not perfectly clean, and I would rather say so.** `runs/2026-09-05-02-validator/
digest.md` fails the lead digest contract — it has no `artifact:` line. pm caught it and I
confirmed it directly. It is gitignored, absent from the reviewed tree, covered by no criterion,
and superseded by the `-03` record, so it gates nothing. But it is a false-looking entry in the
factory's own record and it is row B-11 below. pm also reported `check-state.sh` exiting 1 where I
measured 0, twice, before and after; I could not reproduce their exit 1 and I am reporting the
disagreement rather than resolving it in my own favour.

**A harness defect worth its own ticket, found by two independent readers.** The integration suite
is not hermetic against `HARNESS_AGENT_TYPE`. Any Harness subagent running it from its own shell
sees 15 FAIL lines on a suite a human sees green — reproduced unchanged at the merge-base, so it is
inherited, not caused here. It means agents have been grading a red suite as evidence. Row B-13.

## Budget

`cycles_used` finished at **11 of 11**, exactly the one cycle you authorised and no more. Three
squads ran eight further runs across the fix and revalidation, all first-pass, none reporting a
send-back. `runs` is 41 against an informational budget of 20; INV-22 notes it and never gates. My
read: 29 of the 41 predate this session, and of this session's twelve, none was wasted.

## How this briefing was assembled

**No report round was spawned.** I read the digests and notes from disk and from the returns I
received. First-hand: every `runs/2026-09-05-*/digest.md`, the four `notes/review-harness-*-c2.md`
panel notes plus `review-harness-qa-c2-integration.md`, `notes/research-BUG-1286-goalcheck-build-
c2.md`, `notes/receipt-harness-backend-dev-c11-fix.md`, `notes/qa-audit-sha-correction.md`, and the
cycle-1 equivalents. **The plan phase I did not run** and read through `notes/handoff-plan.md`,
`plan.yaml`'s `panel:` block and `STATE.md` rather than its 29 run digests — treat that account as
inherited.

## Proposed backlog

Nothing here gates. Anything not listed dies silently, so this is everything that survived
collation across both cycles. Strike rows by ID.

| ID | Nature | Item |
|---|---|---|
| B-4 | chore | Tautological conjunct in `_literal_key_present` (`tests/unit/test-suite-layout.py`) — can never be False. Also the remaining grade-2 med code-grade record. |
| B-5 | chore | Unreachable `".."` disjunct in `_is_inside_tests`. |
| B-6 | chore | Case 11's `INAPPLICABLE` branch — latent, non-gating; confirmed not currently taken. |
| B-7 | chore | Stale BRIEF line-number pins (SC-06, SC-07, SC-19 and others moved by the decomposition). BRIEF is approval-gated so nobody touched them. |
| B-8 | chore | Integration case 2 asserts one sentinel absent where case 4 asserts both. |
| B-9 | bug | `validate-digest.py` demands `code_grade` on a code-reviewer digest and rejects every value while `review_sha` is unpinned, so a plan-phase reader that did its job settles as `failed`. |
| B-10 | bug | Agents assigned to a worktree edited the **main checkout** via bare relative paths — twice, both caught and reverted, main checkout verified clean. A guard refusing relative paths under a worktree dispatch would close it. |
| B-11 | bug | `runs/2026-09-05-02-validator/digest.md` fails the lead digest contract (no `artifact:`). Gitignored and superseded, but a false-looking record. Two other runs had `state.yaml` clobbered by a later run and needed repair. |
| B-12 | enhancement | Define "exhausts" for `max_total_cycles` as reached-versus-crossed, and decide whether it deserves a mechanical check at all — today there is none. |
| B-13 | bug | `tests/integration/test-plan-merge.py` is not hermetic against `HARNESS_AGENT_TYPE`: 15 FAIL lines suite-wide under an agent's own env, green for a human. Inherited, reproduced at the merge-base. Remedy: strip it from the default env and opt back in per case. |
| B-14 | chore | `_violations_callers` `read_text()`s every tracked source file, so a tracked-but-deleted or non-UTF-8 source would raise rather than fail as an assertion. |
| B-15 | chore | The audit note's `--against` comparison binds the row block but not the BLUF's prose counts; consistent by inspection, nothing mechanical enforces it. |

## What I did not do

Not merged, not pushed, no PR opened. The worktree stands; its removal is not mine. No risk was
accepted, no scope changed, and no fix was dispatched beyond the three you authorised.
