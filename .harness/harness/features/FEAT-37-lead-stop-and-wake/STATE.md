# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: build complete; BLOCKED at the qa gate on a missing eval, awaiting the operator
- squad: validation (last), product and eng before it
- status: Building — cycles 1/10, runs 13/20, HEAD 5e09992

**ALL FIVE TASKS DONE AND COMMITTED: T-01 (`79c2a46`), T-02 (`8f784b5`, executed by the main
session), T-04 (`e73d545`), T-05 (`1449c66`), T-06 (`5e09992`).** The gap in the task numbering is
deliberate — one task was struck at signature with REQ-08 and SC-09, plan.yaml D-12 is the strike
record, the regression is issue #903, and any proposal to restore it is refused on that citation.
Numbering is NOT compacted, and the struck id is deliberately not written here: check-state.sh
raises a violation when a live STATE.md names a task its plan no longer holds, which this run
tripped once and corrected.

**THE FEATURE IS BLOCKED AT THE QA GATE AND ONLY THE OPERATOR CAN UNBLOCK IT.** `gates.qa_gate` is
blocking. T-02 is `change_type: ai_behavior`, and DEC-70 (@852) requires an `eval` for that type,
authored by `ai-dev`, run by qa, adequacy assessed by validator-lead. `harness.json`
`test_kinds.eval` is `cmd: null` / `status: unresolved`, and DEC-36 (@448) plus DEC-187 (@5861) say
a null cmd is BLOCKED — never a soft skip. **No eval exists to point a runner at**, because the
plan has no ai-dev task: T-02 went `main-session-direct` under DEC-179. Both remedies — ai-dev
authors an eval (a plan change, so pm, under the operator's approval) or the operator signs a
`status: excluded` exclusion for `test_kinds.eval` — edit files outside every FEAT-37 task's
declared set. I verified DEC-70's text at disk rather than taking the lead's word.

**THE APPROVED BRIEF CONTRADICTS TWO SIGNED DECISIONS ON THIS EXACT POINT.** `BRIEF.md:275-278`
says the eval requirement "resolves to a soft skip and proves nothing". DEC-36 and DEC-187 say it
blocks. The BRIEF is signed, but a signed BRIEF does not override a signed decision. This is
material to the operator's call and is disclosed in the briefing, not resolved by me.

**VALIDATOR-LEAD'S ADEQUACY RULING, WHICH IS ITS CALL BY NAME UNDER DEC-70 (@856):**
`test-lead-stop-and-wake.py --group playbook` is NOT an eval. DEC-70 (@864) defines eval evidence as
a threshold and a measured rate, not a boolean; the group is ten boolean text assertions over one
file. `BRIEF.md:266-267` concedes the same in the feature's own words: it does not prove any lead
OBEYS the sentence, and conduct is carried by SC-08 alone.

**GREEN AND GENUINELY GOOD:** `run-unit-tests.sh --kind unit` exits 0 (was red by design for the
whole build; T-06 closed the last group). `--kind integration` shows zero FAIL lines and ends
ALL PASSED, corroborating the lead's exit-0 / 69-of-69 report. All three
`test-lead-stop-and-wake.py` groups pass and `--self-check` exits 0. I re-ran every task's own
`verify:` block myself rather than taking any of it on report.

**SC-08 IS NOT GRADABLE FROM THIS BUILD AND MUST NOT BE SCORED FROM IT** (D-13, BRIEF.md). A spawned
agent loads skills from the MAIN checkout while the rewritten playbook sits in this worktree.
Corroborated four times now, most recently by this run's own `SubagentStop` refusals still printing
the OLD pre-T-04 sentence while `inflight_registry.py:339-340` in this worktree carries the
corrected one. SC-08 stays `not_met`; the goal-check must say so plainly rather than scoring it.

**SIX INV-26 VIOLATIONS, ALL THE SAME STRUCTURAL GAP, ALL THE OPERATOR'S UNDER DEC-174.** Every one
of T-01/#905, T-02/#906 (at Backlog), T-04/#907, T-05/#908, T-06/#909 and parent/#904 reads a
station below what the plan derives. `gh-sync.py` exposes no subcommand that moves a single task
card to Done — only `ship` writes that station — and INV-26 widens only at feature.json status
`Review`. Do not edit `check-state.sh` and do not move cards by hand.

**A RUN-DIR COLLISION DESTROYED T-05's DIGEST.** The product lead reused `run_id`
`2026-08-27-01-product` for both the T-05 and T-06 runs; the second overwrote the first's
`digest.md` and `state.yaml` in place. I moved T-06's artifacts to `runs/t06-product/` and wrote an
honest loss note at `runs/2026-08-27-01-product/digest.md`. T-05's digest is unrecoverable; its
surviving record is the member receipt, my re-run of its verify, and commit `1449c66`.

**NOT RUN, BECAUSE THE BLOCKING GATE STOPPED THE SEQUENCE:** simplify, the `review_sha` pin, the
review panel, the goal-check and the docs sweep. `review_sha` is still `none` and must NOT be pinned
until the gate resolves and simplify has run — an apply commit after the pin invalidates the panel.

**EVERY LINE ANCHOR IN plan.yaml IS ORIENTATION ONLY** — measured at 8fc87f8 before `origin/main`
(FEAT-42) merged. Re-derive by TEXT. **The bound detector's alternation was deliberately widened and
must not be narrowed** (reconciled at `c0262e6`).

**UNCOMMITTED ON PURPOSE:** `notes/answers-2026-08-27-01.md` is the main session's artifact.
`.harness/logs/2026-08-27.md` is held dirt.

## Open Questions

- Q1 (was: D-02 and D-11 spell the ruling AMEND) — RESOLVED at re-plan. Both now read "corrected IN
  PLACE". The only `AMEND` strings left in `plan.yaml` are T-05's and T-06's own DO NOT ADD AN
  AMENDMENT instructions.
- Q2 (was: DEC-199 amend or STRIKE) — RESOLVED. Corrected in place. D-11 and T-06 carry the reasoning.
- Q3 (was: the #811 split ruling) — RESOLVED by operator ruling of 2026-08-24. D-07 is the strike
  record. Issue #811 stays OPEN and returns to the backlog.
- Q4: `notes/root-cause-*.md` is in no member's domain, so debug reports fall back to receipt paths.
- Q5: engineer DIGESTs carry no `files_touched`, so a member that wrote a receipt reported no files;
  the lead reconstructs it by hand. Schema gap or intended?
- Q6 (the #866 deadlock) — HALF CLOSED BY FEAT-42, and the note that said otherwise is now corrected.
  The dispatch end is fixed: `release_cmd` prints an absolute single-agent command, so a refusal no
  longer tells an agent to wipe every feature's live claims. The RETURN end is what T-04 still
  corrects. This feature does not close #866 and never claimed to.
- Q7: single-flight is keyed per checkout, so several orchestrators' children can share one registry
  when they run from one cwd.
