Removed 23 key(s) from FEAT-04-decisions-index's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `shipped`
- old phase: `ship`
- new status: `Done`  (rule)

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
baseline:
  amendment_headings: 9
  check_docs_after_goal_check: exit 0, 45 patterns across 105 files
  check_docs_at_plan_exit: exit 0, 45 patterns across 95 files
  check_docs_at_validate_open: exit 0, 45 patterns across 101 files
  cost_total_at_run15: 6735.1706
  decisions_md: 171 raw / 170 live DEC headings at 363b539, one fenced at :1583
  index_at_363b539: 170 rows, 190 lines, 0 RULING PENDING, 0 rows over the 30-word
    cap
  sc_count: 12
  stale_marker_lines: 48
cost_usd: 324
max_cost_usd: 120
pending:
- '`test-gen-decisions-index.py:115,:120` FREEZE the authority''s DEC counts at raw
  171 / distinct 170. Both pass at 363b539, all six cases `ok`. Brittleness, not a
  defect: the next feature to append a decision reddens the unit gate until the constants
  are bumped — backlog, eng'
- '`ROW_RE` in the generator and test 5''s row regex at `test-gen-decisions-index.py:373`
  are TWO grammars for one row format. A `^- DEC-` line failing ROW_RE is treated
  as "no prior row" rather than a hard error, unlike the orphan case. Silent in the
  generator, loud at the gate — backlog, eng'
- DEC-102's index row states its superseded conclusion with NO `— SUPERSEDED BY` clause.
  The clause is harvested from the superseding decision's TITLE and DEC-120 declares
  it in body prose instead. GENERATOR gap — backlog, eng, not a FEAT-04 fix
- Post-ship standing obligation — a feature appending a decision must regenerate the
  index AND write the row's ruling in the same commit, or the unit gate fails. DEC-170
  was its first exercise
- COST is 2.7x the budget and the figure is a FLOOR — advisor spend appears in no
  cost-report.py row, which is the very gap DEC-170 leaves open. Never a gate (DEC-134),
  but the user should see it
- 'HARNESS DEFECT — the orchestrator playbook mandates appending cost-report output
  to the run state file while harness-team has the lead pre-write `cost: pending_orchestrator`;
  the duplicate top-level key trips INV-16. Suppressed by dispatch on runs 13-15;
  unfixed at source'
- HARNESS DEFECT — every per-feature `.harness/**/*.md` artifact is a check-docs.sh
  scan target, documented nowhere an agent writing one would see it. check-docs.sh
  prints the pattern on TWO physical lines (:143 and :144), so escaping one occurrence
  is not enough
- HARNESS DEFECT — bash-write-guard.sh reads `>` and `<` inside an unquoted heredoc
  body, and operands across a compound `;` line, as shell redirects. The 3a989a0 fix
  does not cover these
- HARNESS DEFECT — a member whose deliverable is a verification receipt has no writable
  per-feature artifact path but its observations log, overloading DEC-145's never-injected
  hot layer
- CALIBRATION — 3/3 panel members re-derived the tier-level gate results the dispatch
  told them to audit rather than reproduce. Receipts came out independent, but the
  instruction did not hold
- qa's note at notes/qa-matrix-c1.md:106 invents `audit-only` as SC-08's verify method
  where BRIEF.md:103 says `inspection`. pm's split of seven/five is the authority
pre_ship_steps:
- 'T-09 — DONE at 363b539 by main-session. SC-09 re-verified by me: presence 2, absence-1
  0, absence-2 0'
- 'T-10 — DONE at 363b539 by main-session. SC-10 re-verified by me: trigger markers
  4, ''floor'' 1'
resolved:
- 'APPROVAL GATE PASSED — BRIEF.md and PLAN.md both `status: approved`, Mike Ruangutai,
  2026-08-02, RE-SIGNED after the mid-build cap amendment. Verified by me at 363b539'
- Q0 ACCEPTED — T-09 and T-10 were main-session pre-ship steps; both landed at 363b539
- Q4 ACCEPTED — the unit gate is deliberately RED between T-03 and T-07, by design
- NO LOWER BOUND on ruling length — user decision, in both `## Approval` notes
- '`.harness/notes/pending-dec-advisor-disclosure.md` DELETED by the main session;
  verified absent'
- SC-08 LIVE RECEIPT — run 13. Bare plant at docs/harness/SPEC.md:2162 drove check-docs.sh
  0 -> 1 -> 0, exactly one hit attributed to DEC-120, tree byte-clean after revert,
  --audit exit 0
- 'REVIEWER PANEL PASS — run 14 at 363b539. must_fix [], severity_max med, `review:
  advisory_unless_high` so not blocking. ui step SKIPPED, qa step ADDED to cover the
  blocking gate'
- GOAL-CHECK PASS — run 15, 12/12
- Q3, MF-1..MF-6, the check-docs regression, D-01's pricing, A-1/A-2/A-4 — closed
  in the plan phase
runs[0].cost_usd: 18
runs[10].cost_usd: 5.7
runs[11].cost_usd: 20
runs[12].cost_usd: 10
runs[13].cost_usd: 20
runs[14].cost_usd: 19.3
runs[1].cost_usd: 9
runs[2].cost_usd: 18
runs[3].cost_usd: 13
runs[4].cost_usd: 10
runs[5].cost_usd: 12
runs[6].cost_usd: 17
runs[7].cost_usd: 4.5
runs[8].cost_usd: 45.5
runs[9].cost_usd: 16
sc_status:
- all 12 of 12 met at 363b539, pm goal-check run 15. Seven `automated`, five `inspection`,
  each against BRIEF's own declared `verify:` field. Evidence in notes/research-goal-check-c1.md
- 'SC-01''s PROSE pins 169 rows at f723194; the committed index carries 170 because
  DEC-170 landed mid-build. SC-01''s operative clause is "counted at run time rather
  than against a frozen number", so 170 is CORRECT and no BRIEF amendment is warranted.
  Verified by me: 170 index rows, 171 raw authority headings, one fenced at DECISIONS.md:1583,
  so 170 live'
- SC-11's PROSE cites "82 of 169 over the cap, max 165" — the pre-remediation ce2cd17
  figure. At 363b539 it is 0 of 170 over, max 30
skipped_segments:
- reason: no end-user visual surface, no DESIGN.md
  segment: 1b-visual-designer-design-pass
- reason: no DESIGN.md contract exists to review (Expertise O-01)
  segment: 3-ui-reviewer-contract-check
- reason: markdown-and-python diff, no user-facing surface, no DESIGN.md — the same
    rationale as segment 3 retires the post-build audit (Expertise O-01)
  segment: review-team-step-ui
- reason: no `.harness/codebase/` on disk, so no map to intersect (verified by me
    at 363b539)
  segment: ship-refresh
- reason: DEFERRED to feature close post-acceptance, not skipped. The ship gate is
    still ahead, and the four validate-phase members (validator-lead, code-reviewer,
    security-reviewer, qa) hold NO observations log yet, so distilling now would distill
    the build phase twice and validate zero
  segment: feature-close-distillation
- reason: SKIPPED and disclosed in the briefing itself. The round exists so the briefing
    is not the orchestrator narrating work it did not see; I hosted all three validate
    runs and cite every digest by path. eng-lead had zero activity this phase. Three
    lead spawns at ~20 USD each to re-narrate digests I hold is spend with nothing
    to surface it
  segment: briefing-three-lead-report-round
```

## value normalization added during execution — a gap in T-04's instruction

- `github.milestone`: `'none'` (string) -> `null`
- `github.parent`: `'none'` (string) -> `null`

T-04's intent names only `pr` for the string-`none` normalization, and explicitly leaves
`branch` and `review_sha` alone because INV-6 reads them as placeholders. It says nothing about
`github.milestone` and `github.parent`, which the schema types as `integer|null`. Left as written,
T-04's own verify clause could not reach exit 0. Normalized on the same reasoning as `pr` — the
string `none` is a placeholder for absent — and recorded here rather than applied silently.
