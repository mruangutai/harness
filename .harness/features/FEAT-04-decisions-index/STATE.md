# STATE

## Current

- feature: FEAT-04-decisions-index
- phase: **build CLOSED** at `bdfa3ab`; `phase: validate` is the next owner's. Seam note
  `notes/handoff-build.md` (58 lines) — read it before acting, and re-check anything it does not
  mark verified.
- status: awaiting_user — one BLOCKING item, below.
- branch: `feat/decisions-index`. Six commits of this feature's work: `ff9d866` `25493ae` `ce2cd17`
  `bdfa3ab` plus the main session's two guard fixes interleaved.
- **The deliverable is complete and green.** `docs/harness/DECISIONS-INDEX.md`: 170 rows, 190 lines,
  0 `RULING PENDING`, 0 `ok-stale`, ruling words min 13 / median 24 / max 30. All measured by me.
- gates at `bdfa3ab`, all run by me rather than taken on report: `run-unit-tests.sh` exit 0 with no
  `MISCONFIGURED` and no `SKIP` line; `check-docs.sh` exit 0 at 45 patterns across 102 files;
  `check-state.sh` exit 0; regenerating over the committed index changes nothing.
- runs: 07 eng (T-01/T-02) → 08 eng (header fix + the first dry run against the real authority) →
  09 product (T-03..T-08, the 169-row backfill) → 10 product (**ESCALATE** — the spec amendment and
  DEC-170) → 11 eng (the cap as a test) → 12 product (84 rulings compressed, 0 truth exceptions).
- **BLOCKING: the user must re-sign.** `BRIEF.md` SC-11 and `PLAN.md` D-07 were amended mid-build to
  carry the 30-word ruling cap, and both `## Approval` blocks still hold the pre-amendment note.
  SC-11's amendment is a **reversal** — it previously recorded that the length-cap question was
  closed without a character-count rule. No validator panel should run against unsigned criteria.
- **Three pre-ship steps no agent can do**, all the main session's: T-09 (`CLAUDE.md`), T-10
  (`harness-handoff`), and deleting `.harness/notes/pending-dec-advisor-disclosure.md`, which is now
  a false second copy of DEC-170. `.harness/notes/**` is in no agent's write domain, mine included.
- budgets: cost **$275 against $120 — 2.3x, and a FLOOR**, since advisor spend appears in no
  `cost-report.py` row. The single largest line is run 09's $45.5, of which $27.2 is six documentor
  spawns each reading a ~1,100-line slice of the authority — the mandatory-reading floor this index
  exists to remove. Never a gate (DEC-134). `cycles_used` **6 of 10**.

## Open Questions

- **BLOCKING — re-sign the amended BRIEF SC-11 and PLAN D-07** (see above). Everything else waits.
- **Delete the staged note** — `.harness/notes/pending-dec-advisor-disclosure.md`. Main session only.
- **DEC-102's row can be acted on when it should not be.** It states its superseded conclusion with
  no `— SUPERSEDED BY` clause, because that clause is harvested from the superseding decision's
  TITLE and DEC-120 declares the supersession in body prose. Generator gap; eng's, not documentor's.
- **Confirm no lower bound on ruling length is wanted** — the observed minimum is 13 words.
- **Q1** (the main session's) — declare a stale marker for the whole-read wording T-09 removes? Only
  decidable when T-09 runs. Yes re-pins the emitted pattern count 45 to 46 and reverses D-08.
- **Q2, for the user at ship** — post-ship, any feature appending a decision must regenerate the
  index AND write that row's ruling in the same commit or the unit gate fails. DEC-170 was the first
  exercise of it and it worked.
- **Four harness defects for the harness owner**, all in `feature.yaml pending`: the cost-append
  versus `pending_orchestrator` contradiction (INV-16, hit on all ten runs); `.harness/**/*.md`
  being an undocumented scan target; `bash-write-guard.sh` misreading heredoc and compound-line
  operands as redirects (four occurrences this phase, every one a legitimate command); and a
  code-deliverable member having no artifact path but its observations log.
