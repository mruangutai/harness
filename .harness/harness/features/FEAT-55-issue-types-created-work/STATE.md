# STATE

## Current

- feature: FEAT-55-issue-types-created-work
- run: .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-05-28-validator/state.yaml
- squad: validator
- status: awaiting_user
- station: plan (plan.yaml `status: plan`, `approval.status: pending`, BRIEF `## Approval` pending)
- mission: plan — the operator's THIRD batched ruling pass is discharged. All five rulings of
  `notes/answers-plan-panel-20260904-c3.md` landed in ONE consolidated revision (c6), and the
  cycle-4 panel re-verified every one HOLDING at source: R1 the three partial-Type cases pre-seeded
  with a declared-type `created` remnant plus a remnant-unchanged assertion (the fix that was inert
  twice is now genuinely reddenable); R2 the backlog receipt on the locked atomic writer; R3 the
  override surface narrowed to four canonical keys, sweep complete, D-12's false "EXISTING key"
  claim corrected; R4 T-10 §1's configured-repo gate exempted for the explicit opt-in; R5 REQ-10 on
  T-07 and T-08 traces. Detail: `notes/research-FEAT-55-planrepair-c6.md`.
- fix cycle: goal-check c5 answered NO on exactly one criterion — R3's own narrowing left BRIEF
  SC-06's chore leg with no integration fixture. Routed as a fix cycle, not a plan amendment, since
  the criterion was met-able as written: c7 widened T-03 case E to
  `{"Bug": "Defect", "Task": "Maintenance", "parent": "Epic"}`, asserting three distinct declared
  type ids per issue. Goal-check c6 then answered the verbatim question YES, unhedged, 0 route
  violations (`notes/research-FEAT-55-goalcheck-plan-c6.md`).
- panel: cycle 4 PASS, `severity_max: med`, `must_fix: []` — NOTHING GATES. Both readers RAN,
  neither skipped. plan.yaml `panel:` records ELEVEN findings: seven carried with every id
  re-derived and reproducing, one re-scoped (`PF-d8a7b516b793e1227b17d61c754240c7` supersedes
  `PF-1280cd8fc7536c65bc22f076576c28fa` — residue (b) ruled and fixed, residue (a) survives), three
  new. The five discharged ids are dropped. Nothing above `med` remains, so INV-32 needs no operator
  risk acceptance. Detail: `notes/research-FEAT-55-panel-transcription-c4.md`.
- readers block CORRECTED: the cycle-3 record keyed entries `step:` and carried two. INV-32
  (`bin/check-state.sh:533-546`) builds its map from `reader:` and requires three —
  `should-not-exist`, `scope`, `goalcheck` — so the old shape would have raised three hard BADs the
  moment the plan was signed. It now matches the SIGNED FEAT-52 precedent
  (`FEAT-52-factory-control-plane/plan.yaml:1235-1244`); `goalcheck: ran` is truthful, the product
  segment ran twice (c5 NO, c6 YES). This CLOSES the old Q10: a FEAT-55 transcription defect, not
  the harness defect it was recorded as.
- next: the main session takes a FOURTH batched signature pass (DEC-176). Nothing gates it — the
  package is signature-ready as it stands, and `sign-approval` may run with the eleven findings
  accepted via `--overrule PF-ID:<reason>`, or a fourth ruling batch may be ordered first.
- advisor: by operator instruction every unresolved item went to `fable-advisor` before escalating.
  It RAN, was not skipped, no substitute answered:
  `.harness/notes/analysis-fable-advisor-consult-FEAT-55-c4.md`.
- intake: .harness/notes/grilling-issue-types-2026-09-04.md (source ticket #1289)
- handoff: .harness/harness/features/FEAT-55-issue-types-created-work/notes/handoff-plan.md
- cycles: 8 of 10 — TWO REMAIN. One more ruling pass is affordable; two are not. Runs: 28 of 20,
  over the informational budget (INV-22) and climbing ~7 a pass. No run this session was wasted:
  two for the revision and its goal-check, one for the SC-06 fix cycle, one for its delta re-grade,
  one panel, one transcription, one advisor consult the operator asked for. The count is high for
  one reason — the plan is being signed by rulings rather than in one act, and each pass costs a
  full revise-check-panel-record loop.
- record note: `2026-09-05-26-validator` is NOT a run. It is the first, incomplete digest write of
  the SAME cycle-4 panel; `check-domain.sh` refuses replacing a written run digest, so the canonical
  digest is `2026-09-05-27-validator/digest.md`. Absent from `feature.json` `runs:` deliberately, on
  the `2026-09-04-19-validator` precedent.
- anchor drift: the cycle-4 transcription rewrote `panel:` wholesale, so every line anchor stored
  inside a finding is stale again by an unknown amount. Anchor on content strings. The one
  re-measured anchor of record: D-14's `because` is at plan.yaml`:101`.

## Open Questions

All eleven findings are `disposition: batched_to_signature_review`; none gates. Each carries a
`fable-advisor` recommendation, and a recommendation is NOT a disposition — only
`sign-approval --overrule PF-ID:<reason>` records acceptance. Full text: plan.yaml `panel:`.

- Q1 (operator) `PF-1f968f2cd73a799708e4be589d48e61b` (scope, med, NEW, rank 1) — no planned case
  makes the required set's BACKFILL contribution the SOLE source of a missing type. An
  implementation omitting backfill candidates from `missing_types`, while still ordering backfill
  after the refusal check, passes EVERY planned case, then on an all-recorded rerun computes an
  empty required set, never refuses, and raises an uncaught KeyError instead of REQ-07's actionable
  refusal. Advisor: FIX, one case per route. LEAD CORRECTION verified at source: the existing cases
  already assert a non-zero exit status and that stdout+stderr name both `Task` and
  `github.issue_types`, so copying that block suffices — cheaper than the advisor states, and its
  "inert alone" claim overstates.
- Q2 (operator) `PF-383a1a92195cf2cdfba9828bda854195` (low, NEW) — D-08's eighth read-back purpose
  exceeds REQ-09 and mandates permanent byte-identical 511-char duplication across two files.
  Advisor: this and carried `PF-9a71cb9a…` are TWO findings with ONE decision variable; rule as one
  backlog item, kept OUT of any signature-cycle edit batch.
- Q3 (operator) `PF-e02dcbdf60fdf5eede40feb6066e8a08` (info, NEW) — D-14's `because` is contradicted
  one task later by T-02's measured `issueTypeId` input field, so a builder or SC-04 reviewer may
  defect to createIssue-with-issueTypeId mid-build and unwind the receipt ordering every remnant
  case pins. Advisor: FIX unconditionally, one sentence at plan.yaml`:101`.
- Q4 (operator) `PF-452948136bf467869d223e027191ae49` (med, carried) — T-06's verify omits
  `tests/integration/test-gh-issue-types.py` though T-06's own intent says to run it. Its c3
  recommendation was "fix only if an edit batch is ordered"; TWO batches have since been ordered and
  executed and this is the ONLY batch-contingent item the operator did not rule, so the advisor now
  reads it as FIX.
- Q5 (operator) `PF-62b2b8ae0acc3509b474b744469137dc` (med, carried) — T-10 §6's two SKIP wordings
  map to one `query_failed` state with no discriminating rule. Advisor: already UNCONDITIONAL at c3
  — fold the third bullet into the second; T-01 assertion 7 makes it a contradiction, not an
  ambiguity.
- Q6 (operator) `PF-56a2ce7a053111a3aff62a4b97c5902e` (low, carried) — the inert `adopted` marker
  sits in approval-gated BRIEF SC-12 while Q7 rides unruled. Rule the pair together.
- Q7 (operator) `PF-0c12a033f69bb6bc60b8f96134f94fd0` (low, carried) — `adopted` is behaviourally
  inert. Advisor WITHDRAWS its own finding; c6/c7 STRENGTHEN that. Accept, keep the marker.
- Q8 (operator) `PF-e27f1c3018b6b8477547a1b028607f96` (low, carried) — T-05 case F enshrines
  compat-mode duplicate creation as green contract. Advisor: accept, STRENGTHENED; worth keeping.
- Q9 (operator) `PF-9a71cb9a0c590b06b890ff1517b80385` (info, carried) — the 511-char row's drift
  protection expires when this feature's gate passes. Advisor: defer to backlog, JOINTLY with Q2.
- Q10 (operator) `PF-e74a2da89380cfa94f6b1693191d759d` (med, carried) — T-03's verify loop is a
  whole-file `grep -qF`: gate parity, never coverage. Nothing to rule; c7 grew it by one literal.
  READ IT BEFORE RULING Q1 — it is the standing proof that file-global literals do not bind
  behaviour.
- Q11 (operator) `PF-d8a7b516b793e1227b17d61c754240c7` (low, RE-SCOPED) — residue (a) of
  `PF-1280cd8f…`: T-10 §6 resolves the live-pass type from LOCAL harness.json overrides but applies
  it against the foreign TARGET. Advisor: unchanged — benign, fails safe, accept.
- Q12 (operator, standing) — BRIEF SC-10 grades `partial`: T-09/T-10 planned and reachable under R4,
  unmet until the operator records a live verdict. No fix cycle can close it.
- Q13 (harness defect) — `validate-digest.py` rejects `code_grade: n_a` on a PLAN review where no
  `review_sha` can exist (DEC-207/BUG-1080). It rejected the cycle-4 scope reader four times and
  ended that process exit 1 mid-retry; findings were carried through by hand, nothing lost.
- Q14 (harness defect) — the run-digest contract is checked only AFTER the write while
  `check-domain.sh` refuses replacing a written digest, so a first digest can never be corrected in
  place. One panel therefore occupies two run dirs.
- Q15 (harness defect) — a pm process ended exit 1 with "yield called with null data" though its
  well-formed digest block was emitted and its writes landed. Same class as Q13.
- Q16 (harness defect) — `harness-spec-driven`'s plan-writing verb list omits `amend` (BUG-1128),
  which every revision cycle after the first needs; `apply` is add-only and exits 7.
- Q17 (process defect, named by the advisor ON ITSELF) — a conditional recommendation delegates its
  condition-check to nobody; "fix only if a batch is ordered" survived two ordered batches
  unevaluated (Q4). Batch-contingent phrasing is retired.
