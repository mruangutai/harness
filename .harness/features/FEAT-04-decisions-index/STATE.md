# STATE

## Current

- feature: FEAT-04-decisions-index
- phase: **validate — exit predicate MET.** Panel PASS with `must_fix` empty, and the goal-check
  returned **12 of 12 success criteria met** at `363b539`. Next and last step of this mission is the
  CEO briefing; the ship gate itself is the user's.
- status: in_progress. No blocking question outstanding — the three my predecessor raised are all
  discharged (BRIEF/PLAN re-signed at `feebf60`; the staged note deleted; T-09/T-10 landed at
  `363b539`). I re-ran every receipt rather than taking them on report.
- branch: `feat/decisions-index`. `review_sha` **re-pinned `bdfa3ab` → `363b539`**: the old pin held
  neither T-09's nor T-10's edit, so a panel on it would have reported SC-09 and SC-10 unmet by a
  stale pin rather than by fact.
- **The deliverable is complete and green.** `docs/harness/DECISIONS-INDEX.md`: 170 rows, 190 lines
  (cap 260), 0 `RULING PENDING`, 0 rows over the 30-word ruling cap. Measured by me at `363b539`.
- gates at `363b539`, all run by me: `check-docs.sh` exit 0 at 45 patterns; `run-unit-tests.sh` exit
  0 with `PASS test-gen-decisions-index.py` and no `MISCONFIGURED`; `check-state.sh` exit 0;
  `test-gen-decisions-index.py` direct, exit 0, all six cases `ok`.
- **SC-01's count moved and that is correct.** Its prose pins 169 rows at `f723194`; the operative
  clause is "counted at run time rather than against a frozen number", and `DEC-170` landed mid-build.
  170 index rows against 170 live authority headings (171 raw, one fenced at `DECISIONS.md:1583`).
  No BRIEF amendment: the criterion as written is met, and a third re-signature is not warranted.
- validate runs: **13 product** (SC-08's live receipt — bare plant at `docs/harness/SPEC.md:2162`
  drove `check-docs.sh` 0 → 1 → 0, exactly one hit attributed to `DEC-120`, tree byte-clean after
  revert) → **14 validator** (panel: code + security + qa in one turn; `ui` skipped, no design
  surface; `severity_max: med`, `review: advisory_unless_high` so not blocking) → **15 product**
  (pm's goal-check, 12/12).
- budgets: cost **$324 against $120 — 2.7x, and a FLOOR**, since advisor spend appears in no
  `cost-report.py` row. Validate phase itself cost ~$49 across three runs. Never a gate (DEC-134).
  `cycles_used` **6 of 10** — the validate phase added **zero**: every run passed first time.
- `ship-refresh` skipped: there is no `.harness/codebase/` on disk, so no map to intersect.

## Open Questions

- **Nothing blocking.** The feature is ready for the user's ship decision.
- **Cost is 2.7x the budget and the figure is a floor.** Advisor spend is metered nowhere, which is
  the same gap `DEC-170` leaves open. The user should see it; it never gated anything.
- **Backlog, engineering — three generator findings, none gating.** `DEC-102`'s row states its
  superseded conclusion with no `— SUPERSEDED BY` clause (the clause is harvested from the
  superseding decision's title and `DEC-120` declares it in body prose). `test-gen-decisions-index.py`
  freezes the authority's DEC counts at raw 171 / distinct 170 — both pass today, but the next
  feature to append a decision reddens the unit gate until they are bumped. And the generator's
  `ROW_RE` and test 5's row regex are two grammars for one row format, so a malformed row is silent
  in the generator and loud only at the gate.
- **A standing obligation on every future feature** — appending a decision means regenerating the
  index *and* writing that row's ruling in the same commit, or the unit gate fails. `DEC-170` was
  its first exercise and it worked.
- **Four harness defects for the harness owner**, unrelated to the deliverable: the cost-append
  versus `cost: pending_orchestrator` duplicate-key contradiction (INV-16 — suppressed by dispatch
  on runs 13-15, unfixed at source); `.harness/**/*.md` being an undocumented `check-docs.sh` scan
  target, with the pattern printed on two physical lines so escaping one is not enough;
  `bash-write-guard.sh` misreading heredoc bodies and compound-line operands as redirects; and a
  member whose deliverable is a verification receipt having no writable artifact path but its
  observations log.
- **Calibration, worth pricing rather than repeating** — 3 of 3 panel members re-derived the
  tier-level gate results they were told to audit rather than reproduce. The receipts came out
  independent, which is a real gain, but "audit, do not reproduce" did not hold as an instruction.
