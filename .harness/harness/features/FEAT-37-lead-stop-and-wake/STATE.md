# STATE

## Current

- feature: FEAT-37-lead-stop-and-wake
- run: eng segment complete for every task the squad can reach; blocked on the operator
- squad: none — awaiting the main-session-direct task
- status: Building — cycles 1/10, runs 10/20, HEAD e73d545

**BOTH ARTIFACTS APPROVED 2026-08-27. FIVE tasks: T-01, T-02, T-04, T-05, T-06.** One task was
struck at signature with REQ-08 and SC-09; its id is not cited here because a live STATE.md may not
name a task its plan no longer holds. **plan.yaml D-12 is the strike record**, the regression is
issue #903, and any proposal to restore it is refused on that citation. Numbering is NOT compacted.

**DONE: T-01 (`79c2a46`) and T-04 (`e73d545`).** A third commit, `0c46bfb`, carries an
orchestrator-directed detector widening — split out because it touches a file outside T-04's
`files:` list. Every verify block was re-run by the orchestrator rather than taken on report:
`T01_PASS` and `T04_PASS`, and `test-validate-digest.py` exits 0 both before and after T-04's edit.

**BLOCKED ON THE OPERATOR — THIS IS THE WHOLE REASON THE RUN STOPPED.** Dependencies are
`T-01 -> {T-02, T-04}` and `T-02 -> T-05 -> T-06`. T-01 and T-04 are done, so **T-02 is the only
runnable task and it is main-session-direct** (`check-domain.sh --resolve` returns NOBODY on
`.claude/skills/harness-team/SKILL.md`; issue #906). T-05 and T-06 sit behind it. After the strike,
T-02 is the ONLY main-session-direct task, though the `lanes:` block still lists two NOBODY surfaces.

**THE EXPECTED-FAIL SET. Anything outside it is NEW and gates.** `run-unit-tests.sh --kind unit`
exits 1 by design until T-02, T-05 and T-06 land. The red is exactly `test-lead-stop-and-wake.py`:
  - `--group playbook` exits 1 — closes at **T-02**
  - `--group coverage` exits 1 — closes at **T-05**
  - `--group bound` exits 1 with THREE failures, all DECISIONS.md: `_6869_1`, `_6870_2`, `_6872_3`
    — all close at **T-06**. The two former `inflight_registry.py_339` failures are CLOSED by T-04;
    if either returns it is a regression, not expected red.
`--self-check` and `--check-kinds` exit 0 today and must never go red. The qa segment therefore runs
AFTER the last task, not before — its matrix cannot be green until T-06 lands.

**THE DETECTOR WIDENING, DISCLOSED FOR OVERRULE.** DECISIONS.md:6872 reads "a second identical
return ships"; the alternation spelled only the "will ship" variant at `inflight_registry.py:339`.
D-11 and T-06 both mandate correcting 6872, but T-06's verify would have exited 0 whether or not it
was touched. Widening it took DECISIONS.md from two occurrence failures to three — predicted, then
confirmed. It changes no requirement; if the operator reads it as a spec change it backs out to pm.

**SC-08 IS NOT GRADABLE FROM THIS BUILD AND MUST NOT BE SCORED FROM IT** (D-13, BRIEF.md). A spawned
agent loads skills from the MAIN CHECKOUT while the rewritten playbook sits in this worktree.
CORROBORATED THIS RUN: the eng lead reported the refusal that fired on it mid-run still printed the
OLD sentence, because the `SubagentStop` hook resolves `inflight_registry.py` from the main checkout.
Read nothing post-merge into this run's evidence. SC-08 stays `not_met` at ship.

**EVERY LINE ANCHOR IN plan.yaml IS ORIENTATION ONLY** — measured at 8fc87f8 before `origin/main`
(FEAT-42) merged. Four were found stale so far: `UNIT_SCRIPTS` is line 30 not 17, and the registry
site is 339 not 274. Re-derive by TEXT, never by number.

**CHECK-STATE HAS TWO OPEN INV-26 VIOLATIONS THAT I CANNOT CLEAR** — T-01 and T-04 cards read
Building while the plan says done. INV-26 accepts a non-Done card only when feature.json status is
`Review`; `gh-sync.py` exposes no subcommand that moves a single task card to Done; and the mirror
reference says to record `done` in plan.yaml and "run nothing else". Structural, not a missed step.
`check-state.sh` is enforcement-layer, so under DEC-174 the fix is the operator's, not the squad's.

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
