# STATE

## Current

- feature: FEAT-55-issue-types-created-work
- run: .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-05-02-validator/state.yaml
- squad: validator
- status: awaiting_user
- station: plan (plan.yaml `status: plan`, `approval.status: pending`, BRIEF `## Approval` pending)
- mission: plan — the operator's FOURTH batched ruling pass is discharged. All five FIX rulings of
  `notes/answers-plan-panel-20260905-c4.md` landed in ONE consolidated revision (c8), the four
  ACCEPT rulings were honoured by changing nothing but their disposition strings, and the cycle-5
  panel re-verified every FIX HOLDING at source. Detail: `notes/research-FEAT-55-planrepair-c8.md`.
- the five fixes, each verified at source by content string (b0aa961a):
  1. `PF-1f968f2c…` — a backfill-only refusal case on ALL THREE creation routes: T-03 `CASE K`
     (FAKE_TYPES=nobug), T-05 `CASE H`, T-07 `CASE J`, each with its letter in its own verify loop
     and each fixture built from that ROUTE's own recorded shape. Non-inert by construction: every
     issue the run would create has a DECLARED type, so refusal cannot fire from the creation side
     and the only undeclared type is the one the recorded `created` remnant needs. Each asserts
     non-zero exit, the refusal naming the type and `github.issue_types`, zero create argv, zero
     updateIssue argv, and the remnant unchanged.
  2. `PF-e02dcbdf…` — D-14's `because` now says a GraphQL `createIssue` with `issueTypeId` IS
     possible and is DELIBERATELY UNUSED. One send-back was needed: the same overclaim survived in
     T-02's builder-facing intent after D-14 was fixed. The string is now absent plan-wide.
  3. `PF-45294813…` — `python3 tests/integration/test-gh-issue-types.py || exit 1` is in T-06's
     `verify:`, and its intent no longer asks the builder to run it by hand.
  4. `PF-62b2b8ae…` — T-10 §6 carries ONE `query_failed` SKIP wording covering authorisation,
     NOT_FOUND and unreachable-host; §7's four verdict tokens unchanged, no fifth token.
  5. `PF-383a1a92…` + `PF-9a71cb9a…` (one coupled edit) — SPLIT, not merely shrunk: the pinned
     duplicated row went 511 → 394 chars and now covers only the reads THIS feature introduces; the
     pre-existing `gh_issues.internal_id_args` enumeration survives as ONE unpinned prose sentence
     in DECISIONS.md alone. The drift guard is durable: T-01 gains `tests/unit/test-issue-types-pin.py`,
     which `run-unit-tests.sh` globs into the STANDING suite forever, asserting presence in each file
     and identity between them as separate failures.
- accepted and untouched, confirmed by the panel: the `adopted` provenance marker
  (`PF-56a2ce7a…`, `PF-0c12a033…`), T-05 case F's compatibility-mode duplicate-creation tripwire
  (`PF-e27f1c30…`), T-10 §6's local-override / foreign-TARGET residue (`PF-d8a7b516…`). All four now
  read `disposition: operator_accepted`, citing the answers file.
- panel: cycle 5 PASS, `severity_max: med`, `must_fix: []` — NOTHING GATES. Both readers RAN,
  neither skipped; `goalcheck: ran` is truthful (c7 answered the verbatim question YES, unhedged, 0
  route violations — `notes/research-FEAT-55-goalcheck-plan-c7.md`). plan.yaml `panel:` records NINE
  findings — four NEW `low`, one carried `med`, four `operator_accepted` `low` — with every id
  computed by `panel_findings.py id` and all five carried ids reproducing. The six discharged ids
  live in `discharged_at_cycle_5:` with the content string that proved each HOLDING. Detail:
  `notes/research-FEAT-55-panel-transcription-c5.md`.
- build-phase sequencing constraint, RECORDED NOT PLANNED (`panel.sequencing_note`): the new pin
  guard is deliberately RED from T-01 until T-11 and T-12 land, it sits in `tests/unit/`, which
  `run-unit-tests.sh` globs, and `gates.qa_gate` is blocking. No plan gate or task verify between
  T-01 and T-12 invokes the suite, but nothing PLAN-ENCODES that order and T-12 is
  main-session-direct. The build orchestrator MUST land T-11 then T-12 before the qa segment; a qa
  run before T-12 reddens the only blocking gate and its `loop_back` has no legal owner, since
  DEC-174 bars every squad from T-12's file. Segment ordering is execution-time authority, so this
  is a handoff constraint, not a new task or dependency.
- backlog candidate (one, per instruction): B-1 (chore) — the other SEVEN read-back rows are
  duplicated across DECISIONS.md and github-mirror.md with no drift protection at all; only the
  eighth is guarded. Recorded in `notes/research-FEAT-55-planrepair-c8.md`; no task, no decision.
- next: the main session's signature pass. Nothing gates it: `must_fix: []`, nothing above `med`, so
  INV-32 needs no operator risk acceptance. Sign with `plan-merge.py sign-approval`, accepting the
  five unruled findings via `--overrule PF-ID:<reason>` as it chooses.
- intake: .harness/notes/grilling-issue-types-2026-09-04.md (source ticket #1289)
- handoff: .harness/harness/features/FEAT-55-issue-types-created-work/notes/handoff-plan.md
- cycles: 9 of 10 — ONE REMAINS. This pass cost exactly one cycle (one pm send-back inside the c8
  product run); the panel and the transcription ran clean at zero. A sixth ruling batch is NOT
  affordable as a fix-and-re-panel loop. Runs: 30 of 20, over the informational budget (INV-22) and
  still earning their place — three this session: one revision-plus-goal-check, one panel, one
  transcription. The count is high for one reason unchanged from round three: the plan is being
  signed by rulings rather than in one act.
- record note: `2026-09-05-c5-validator` is NOT a run — it is the first, contract-invalid digest
  write of the SAME cycle-5 panel, unreplaceable in place because `check-domain.sh` refuses to
  overwrite a written digest; the canonical digest is `2026-09-05-02-validator/digest.md`. Absent
  from `feature.json` `runs:` deliberately, on the `2026-09-05-26-validator` precedent. The
  check-state `orphaned run dirs` note names these deliberate exclusions and is expected.
- anchor drift: the c8 revision rewrote D-08, D-14 and the T-01 / T-03 / T-05 / T-06 / T-07 / T-10 /
  T-11 / T-12 bodies, and the transcription rewrote `panel:` wholesale. The file is now 1665 lines
  and EVERY stored line anchor is stale by an unknown amount. Anchor on content strings only.

## Open Questions

The nine `panel:` findings are the operator's to rule or to accept at signature; four already read
`operator_accepted`. Nothing gates, and only `sign-approval --overrule PF-ID:<reason>` records
acceptance. Full text: plan.yaml `panel:`.

- Q1 (operator) `PF-bad4d5185e8a8cedba6acd7d5ed1bb79` (low, NEW, fix_order 1) — the pin extraction
  regex has no `re.DOTALL`, so the 394-char row must sit on ONE physical line, but no task tells
  T-11 that and DECISIONS.md's comparable entries wrap.
- Q2 (operator) `PF-17e86df90d8237d8fdf5eb5cb96a274a` (low, NEW, fix_order 2) — the capability query
  pins an unpaginated `issueTypes(first:10)` and T-01 assertion 8 bakes the literal in, while GitHub
  documents up to 25 organisation issue types: a type beyond node 10 is invisible and triggers
  REQ-07's refusal on all three routes.
- Q3 (operator) `PF-f8e806d111d71a0bb6c4298cd47963c9` (low, NEW, fix_order 3) — github-mirror.md's
  table caption still says "seven purposes" after T-12 adds the eighth row; no T-12 instruction or
  verify updates the count.
- Q4 (operator) `PF-bc6cbd0c92ecd36a44eee2da8762f05a` (low, NEW, fix_order 4) — T-01's pin-guard
  verify greps for the substring `DRIFTED`, so it cannot prove missing-pin and drifted-pin are two
  independently triggerable failures.
- Q5 (operator) `PF-e74a2da89380cfa94f6b1693191d759d` (med, carried, deliberately UNRANKED) — the
  three tasks' `grep -qF` verify loops are file-global gate parity, never coverage, and that stays
  true of the new K / H / J markers. Standing record, nothing to rule.
- Q6 (operator, standing) — BRIEF SC-10 grades `partial`: T-09/T-10 planned and reachable, unmet
  until the operator records a live verdict against an Issue-Type-enabled repository. No fix cycle
  can close it; the live probe run remains an implementation/UAT requirement by operator ruling.
- Q7 (harness defect) — `validate-digest.py` rejects `code_grade: n_a` on a PLAN review where no
  `review_sha` can exist (DEC-207 / BUG-1080). Cycle 5 hit the same class again: the scope reader's
  task ended host status `failed (exit 1)` while emitting a complete, well-formed digest block.
- Q8 (harness defect) — the run-digest contract is checked only AFTER the write while
  `check-domain.sh` refuses replacing a written digest, so a first digest can never be repaired in
  place. Both the cycle-4 and the cycle-5 panel therefore occupy two run dirs each.
- Q9 (harness defect) — `harness-spec-driven`'s plan-writing verb list omits `amend` (BUG-1128),
  which every revision cycle after the first needs; `apply` is add-only and exits 7.
- Q10 (harness defect) — `plan-merge.py amend --key` accepts only `tasks|decisions`, so a
  disposition-only edit inside `panel:` has no `amend` route and must go through the panel setter.
- Q11 (process defect, standing) — batch-contingent recommendation phrasing ("fix only if a batch is
  ordered") delegates its condition-check to nobody and is retired; cycle 5 used none.
