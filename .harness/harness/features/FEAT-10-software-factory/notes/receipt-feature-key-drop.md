Removed 19 key(s) from FEAT-10-software-factory's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `complete`
- old phase: `ship`
- new status: `Done`  (rule)

**check-plan-routes.py's verdict on this feature CHANGES.** Its finished-feature skip reads `status`; at `Done` this feature LEAVES the checked set. Named here so a later reader does not read it as a silent regression. The skip is repointed at `Done` by T-11.

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
a1:
  defect: 'Step 7 persisted the item id BEFORE project_field_set with no station receipt,
    so a raise left an issue+item the dispositions graded full/edges_unwritten, step
    7 skipped forever, and factory_claim.py:237''s `status:"Ready" is:open` poll could
    never see it. Deterministic on a fleet/board mismatch: preflight() runs `gh auth
    status` and nothing else, so one typo orphans every task and publish still exits
    0 with a clean payload. Operator REPRODUCED IT LIVE.'
  ownership_ruling: 'READING (a): THE CODE MISMATCHED THE SIGNED PLAN. plan.yaml:610-611
    resumes a partial task by adding the item and setting its station THEN recording
    the id — after BOTH calls — and the `partial` disposition already models the state
    a failed station-set leaves. Reading (b), that step 8''s three receipt triggers
    omit station-set, was REJECTED: acting on it needs a new ledger key, a new disposition
    and sort_dispositions edits. T-04 unchanged; pm has nothing to re-plan.'
  red_verified_by_me: 'NOT taken from the lead''s capture. The predecessor ran the
    segment''s FINAL test file against the PRE-FIX factory_decompose.py from 28302a6,
    injected in-memory via `git show`, writing nothing: 17 of 172 checks FAIL, including
    the three that reproduce the operator''s live defect. GREEN re-measured at the
    settled tree by this segment before committing.'
  second_order_risk: 'CAUGHT AND CLOSED, NOT ASSUMED. The fix promotes a rare crash
    window to the ordinary recovery path, so step 7 re-calls project_item_add on an
    issue already on the board; idempotence there is UNVERIFIED and the stub cannot
    settle it. Closed by REMOVING the dependency: _find_existing_item_id reads the
    board first, on the `partial` path only. The lead rejected its member''s first
    lookup, which compared content.repository bare while factory_claim.py:69-84 documents
    that field can be ABSENT and carries a URL fallback. Fixed as _item_repo.'
  status: FIXED — runs/a1fix-eng/digest.md, committed b86565b
  verified_against: THE STUB ONLY. No live re-run of the operator's typo journey,
    which is the only thing that ever reproduced A1 outside a test. That re-run is
    the operator's open Q5.
briefing: .harness/features/FEAT-10-software-factory/notes/ship-review-ship-2026-08-09.md
counts:
  decisions: 15
  reqs: 8
  sc_automated: 18
  sc_inspection: 2
  sc_uat: 0
  scs: 20
  tasks: 12
counts_note: 'D-01..D-15 in plan.yaml. DEC-186/187 are PROJECT decisions, uncounted.
  tasks_main_session_direct: 2 (T-01, T-08).'
cycles_raise: 'RAISED 10 -> 12 BY THE OPERATOR, 2026-08-09, recorded here as DEC-157
  requires. The decision is notes/answers-a1fix-eng.md Q1; the operator accepted the
  count as honest, including the a1fix-eng lead''s second send-back NOT being charged.
  ZERO HEADROOM REMAINS: any rework ordered from here exhausts the budget and the
  next orchestrator returns BLOCKED.'
declared_widening:
  status: RESOLVED 2026-08-09 by the operator (answers-a1fix-eng.md Q2). The behaviour
    SHIPS and runs/a1fix-eng/digest.md stands as the record. NO D-NN amendment; plan.yaml
    is not amended. It was declared rather than slipped in, and that is what the ruling
    credits.
  what: _validate_stations, called at step 3b — after preflight(), before the step-4
    ledger load, so ahead of ensure_labels, THE POINT OF NO RETURN at plan.yaml:818-830.
    Validates EVERY fleet station against the board's real options; exit 2, zero mutating
    calls, naming key, value and real options. Reuses factory_gh.project_field_options,
    which already existed at 28302a6.
effort: https://github.com/mruangutai/harness/issues/181
gate_status:
  brief_approval: PASS — Mike Ruangutai, 2026-08-09
  build: PASS — 12 of 12 DONE (10 by team, T-01 and T-08 main-session-direct)
  commit_pen: 'EXERCISED. b86565b [harness:t-04] carries the A1 fix, its tests and
    the five notes, staged by explicit pathspec. .harness/logs/2026-08-09.md was left
    DIRTY on purpose — its added lines are the main session''s own record and carry
    claims I cannot verify. NOT pushed, NO PR: both are the operator''s call and main
    is 10 commits ahead of origin/main.'
  distillation: DELIBERATELY NOT RUN, and the operator may overrule. DEC-145 puts
    feature-close distillation after ship, and this feature is returning FOR the ship
    decision with Q5 still open. Distilling a run the operator may reopen produces
    Expertise written hot, which is the failure DEC-145 names.
  docs: 'PASS — check-docs.sh run BY ME pre-commit, AFTER every write: exit 0, 62
    patterns across 317 files, no stale statements'
  github_mirror: 'gh-sync.py open DELIBERATELY NOT RUN — operator RULED: wait for
    the factory to own it (notes/answers-github-mirror.md)'
  goal_check: 'PASS — 20/0/0 at runs/goalcheck2-product/digest.md; not re-run after
    the A1 fix. ONE GRADE IS CONDITIONAL AND THE BRIEFING SAYS SO: SC-05 was recorded
    met on the rider that it flips to not_met if factory_land.py:77 is judged a defect.
    panel1 declined to — F1, med, must_fix empty. Blast radius is exactly one criterion:
    SC-10/11/14 each carry a recorded unaffected-by reason and SC-19 is driven elsewhere
    (runs/goalcheck-product/digest.md).'
  handoffs: 'CLOSED, AND IT WAS A REAL GAP. Advancing `phase:` to `ship` made INV-17
    fire two VIOLATIONs: the build and validate seams were both crossed with no handoff
    note, so each successor lost its predecessor''s working memory and ran the disk-only
    path DEC-159 supports. Written now as notes/handoff-build.md and notes/handoff-validate.md,
    each labelled RECONSTRUCTED AT FEATURE CLOSE in its own first line so the loss
    is preserved rather than papered over, each within the 60-line shape cap. The
    gate went from exit 1 to exit 0 on that write.'
  plan_approval: PASS — Mike Ruangutai, 2026-08-09
  qa_gate: 'PASS. RE-MEASURED BY ME at the settled tree immediately before the commit:
    run-unit-tests.sh exit 0, 22 test files PASS, 0 FAIL. The 22 is FILE-level; a
    bare `grep -c "^PASS"` returns 85 by counting sub-case lines. CAVEATS: green is
    FILE-level not mutation-bound, and `functional` is EXCLUDED BY SIGNED DECISION
    (DEC-187), not satisfied.'
  review_panel: PASS. panel2's single must_fix (A1, high) is CLOSED, so with gates.review
    advisory_unless_high nothing here gates. Eleven advisory findings survive, NONE
    dispatched; two dismissed with reasons. NO RE-REVIEW of the fix was run — the
    operator ruled re-pin and re-run nothing (Q4).
  sc_traces: PASS — 20 of 20 traced, no REQ uncovered
  security_review: PASS at panel2, low. The low (INV-24 builds its repo allow-list
    from a raw YAML read, so a null repo passes both checks) IS FIXED by bf8f191 —
    verified by me in that commit's own diff, whose comment cites "panel2 C1" and
    adds an isinstance guard plus a factory.repo type check.
  ship_refresh: SKIPPED, MEASURED NOT ASSUMED. No codebase map exists — `find . -name
    INDEX.md` returns nothing and .harness/map/ is absent — so the union of files_touched
    intersects no map domain. Zero dispatches. It runs when a map first exists.
  state: 'PASS — check-state.sh run BY ME pre-commit, AFTER every write: exit 0, ZERO
    violations. The four carried VIOLATIONs (FEAT-04 x2, FEAT-07 x2, the DEC-156 lead-digest
    defect) are GONE, cleared by bf8f191. Only notes remain, including this feature''s
    expected INV-22.'
  uat: 'NO SCRIPTED UAT — sc_uat is 0 because the operator DELETED SC-07 under #194''s
    one-in-flight cap. Largely closed by MEASUREMENT: his first live journey ran green
    end to end after the project-id fix, his second REPRODUCED A1. The A1 fix is verified
    against the STUB ONLY.'
  ui_contract_postbuild: PASS at panel2, low — factory_workspace prints a good diagnostic
    then calls its own documented failure 'unexpected'
i202_note: 'i202-validator reviewed GitHub issue #202, not this feature. It lives
  here because #202 owns no feature dir and the panel needed one. Its FAIL stands
  as the lead recorded it; four of five findings were later ruled void or fixed, and
  its envelope — written after the fact by the main session, because the lead died
  on an API error before writing it — records each disposition against evidence.'
mission: ship
operator_answers: .harness/features/FEAT-10-software-factory/notes/answers-a1fix-eng.md
review_sha_base: f9488a2922d0a2fd69f383b3e098f4e24ba9eb49
review_sha_note: 'RE-PINNED to the A1 commit under the operator''s Q4 ruling; nothing
  re-run, on the strength of the independently re-proved red. BASE DELIBERATELY UNMOVED
  at f9488a2 so every panel2 citation keeps its range. Two commits in that range are
  not this feature''s build: c5597be (the wayfinding door, unrelated) and bf8f191
  (the operator''s check-state.sh hand-edit, which IS in scope — T-08 is a FEAT-10
  task). 8bbb246, the old pin, survives only on wip-omp-and-feat10-mixed; deleting
  that branch kills every panel2 line citation.'
runs_correction_note: panel-validator was recorded PASS and was WRONG (two of three
  members FAILed). Repaired to FAIL — roll-up field only; it gates nothing.
runs_note: '31 of 20, INFORMATIONAL, never a stop (INV-22, #79). A FLOOR — two main-session-direct
  tasks and the digest-repair segment are uncounted. Still earning their place: each
  of the last four runs found or closed a defect that would otherwise have shipped,
  A1 among them.'
sc_tally:
  met: 20
  not_met: 0
  note: 'ALL TWENTY MET on the strict clause-level bar the operator ruled. SETTLED
    at runs/goalcheck2-product/digest.md. NOT re-goal-checked after the A1 fix: it
    adds behaviour and removes none, and its 19 new checks are the evidence. Provenance
    of the 20: three measured at goalcheck2, sixteen carried from goalcheck-product,
    SC-06 from sc06-product.'
  partial: 0
  residuals_not_demoting: 'SC-18: a module-scope alias not naming "fleet" evades the
    source-text rule, and the scan covers factory_*.py rather than all of bin/. SC-19:
    the sibling assertion at test-factory-integration.py:691-692 is DEAD (the fixture
    pre-creates the dir at :676); the clause rests on :704-708, which does redden.'
shipped: 'SHIPPED BY THE OPERATOR, 2026-08-10, after the live end-to-end verification
  against the real GitHub API passed on both halves of A1. Evidence: notes/live-verification-a1-2026-08-10.md.
  Nothing pushed and no PR opened by this decision — both remain the operator''s call.'
tasks:
  T-01: DONE
  T-02: DONE
  T-03: DONE
  T-04: DONE
  T-05: DONE
  T-06: DONE
  T-07: DONE
  T-08: DONE
  T-09: DONE
  T-10: DONE
  T-11: DONE
  T-12: DONE
tasks_note: 'T-08 landed operator-direct under the DEC-174 carve-out; plan.yaml:1435
  still says `pending` and is stale, pm''s to correct. T-04 stays DONE: the A1 fix
  brings its code INTO conformance with the signed text rather than changing what
  T-04 asks for.'
```
