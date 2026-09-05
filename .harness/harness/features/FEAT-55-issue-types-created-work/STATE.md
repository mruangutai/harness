# STATE

## Current

- feature: FEAT-55-issue-types-created-work
- run: .harness/harness/features/FEAT-55-issue-types-created-work/runs/2026-09-04-22-validator/state.yaml
- squad: validator
- status: awaiting_user
- station: plan (plan.yaml `status: plan`, `approval.status: pending`, BRIEF `## Approval` pending)
- mission: plan — the operator's SECOND batched ruling pass is discharged. Both rulings of
  `notes/answers-plan-panel-20260904-c2.md` are applied in ONE consolidated revision (c5): T-03
  case F gains the zero-`updateIssue` assertion; T-03's `verify` string loop gains `partial` and
  `github.issue_types` (the folded low finding, disclosed not silent); T-10 §6 unbinds `--create-in`
  from configured `github.repo` in favour of an explicitly supplied TARGET with the opt-in retained
  as the whole safety mechanism, and BRIEF SC-10 is reworded to match. Goal-check c4 answers YES
  with the eleven baseline findings still closed and 0 route violations. The adversarial panel
  re-ran at cycle 3 — both readers RAN, none skipped — and returned FAIL, `severity_max: high`.
  plan.yaml `panel:` now records TWELVE findings: cycle 3's six new plus cycle 2's six unruled ones
  carried verbatim, every carried id re-derived and reproducing; the three discharged ids dropped.
- next: the main session takes a THIRD batched signature pass (DEC-176). ONE high finding gates it —
  `PF-df3caaeb7d520653866034e477d3718b` (F1), which proves the operator's own ruled c5 fix INERT.
  Neither pm nor the orchestrator may accept its risk: it needs a directed remedy or
  `sign-approval --overrule PF-df3caaeb7d520653866034e477d3718b:<reason>`.
- advisor: by operator instruction, every unresolved item was put to `fable-advisor` before
  escalating. It resolved on both consults and was never skipped. Recommendations, none of them
  dispositions: `.harness/notes/analysis-fable-advisor-consult-FEAT-55-c3.md` (F1, N2, N5, the six
  carried ids, the two harness defects) and `.harness/notes/analysis-fable-advisor-consult-FEAT-55-c3-tail.md`
  (N3, N4, N6, plus the cross-cutting ruling-order question).
- intake: .harness/notes/grilling-issue-types-2026-09-04.md (source ticket #1289)
- handoff: .harness/harness/features/FEAT-55-issue-types-created-work/notes/handoff-plan.md
- cycles: 6 of 10 used. Runs: 21 of 20 — OVER the informational budget (INV-22). No run in this
  session was wasted: two produced the revision and its goal check, two the panel and its
  transcription, two the advisor consults the operator asked for, and one
  (`2026-09-04-19-validator`) exists solely because `check-domain.sh` refuses to replace a written
  run digest. The count is high because the plan is being signed by rulings rather than in one act.
- record note: `2026-09-04-19-validator` is not a run. It is the corrected digest of
  `2026-09-04-18-validator`, whose `state.yaml` is the checkpoint of record; it is absent from
  `feature.json` `runs:` deliberately.
- anchor drift: transcribing the cycle-3 panel inserted ~77 lines at plan.yaml`:159`, so every line
  anchor stored INSIDE `panel:` findings pointing past `:159` is stale by exactly +77. The advisor
  tail note carries the re-measured table. Read anchors from that table, not from the finding text.

## Open Questions

- Q1 (BLOCKING, operator): `PF-df3caaeb7d520653866034e477d3718b` (F1, high, `awaiting_user`) — the
  c5 zero-`updateIssue` assertion cannot fail. T-03 case F, T-05 case G and T-07 case I are the
  plan's only `FAKE_TYPES=partial` cases and all three specify a FRESH fixture, so the backfill set
  built from already-recorded `created` keys is EMPTY and a backfill-before-refusal-check
  implementation passes identically to a correct one. Premise verified at source twice
  (advisor + validator lead). Three dispositions: (a) the advisor's cheap remedy — re-specify the
  three existing cases' fixtures from fresh to pre-seeded with one declared-type remnant plus a
  remnant-unchanged assertion, zero CASE-marker and zero string-loop edits; (b) the panel's remedy —
  a new case per route plus six loop edits; (c) accepted-untested, which the advisor judges
  defensible and advises against. Advisor recommends (a). If (c) is chosen, plan.yaml `:539`
  ("this case is what fails when it does") is untrue as written and the ruling should name it.
- Q2 (operator): `PF-62b2b8ae0acc3509b474b744469137dc` (N2, scope `med` / should-not-exist `info`) —
  T-10 §6's two SKIP wordings map to one `query_failed` state with no discriminating rule. Advisor
  recommends DELETING the third bullet and folding it into the second: T-01 assertion 7 already
  binds NOT_FOUND to `query_failed`, so it is a contradiction, not an ambiguity.
- Q3 (operator): `PF-1280cd8fc7536c65bc22f076576c28fa` (N5, low) — two residues of the removed
  equality design in T-10 §6. Advisor: (a) local overrides applied to a foreign TARGET is benign,
  fails safe, accept; (b) §1's configured-repo gate still fronting the opt-in is a genuine partial
  residue of the coupling the `allow` ruling paid to remove — accept for this signature, and fold a
  one-line exemption in if any edit batch is ordered anyway.
- Q4 (operator): `PF-595ce69d5574361d12a048900fcf3e0f` (N4, low) — D-12's sixteen-key override
  surface exceeds REQ-03's four roles, and a partial key set silently splits one role across two
  native types with no refusal. Advisor recommends FIX NOW and kept its own `low`: the remedy
  SHRINKS the spec, `github.issue_types` does not yet exist in `.harness/harness.json` so there is
  no installed base until ship, and narrowing it later is a breaking config migration. The remedy
  edits decisions D-12 and D-02, so it is approval-gated and the operator's alone.
- Q5 (operator): `PF-3626edafbb21d2afb151ff470a450714` (N3, low) — T-07 and T-08 omit `REQ-10` from
  `traces:` though both implement its guarantee and T-07 case F names it in prose. No gate ever goes
  red on this, but `gh-sync.py:359-367` publishes `traces` verbatim into GitHub issue bodies.
  Advisor: fix if any edit batch is ordered, otherwise accept.
- Q6 (operator, read-only): `PF-e74a2da89380cfa94f6b1693191d759d` (N6, should-not-exist `info` /
  scope `med`) — the c5 string-loop edit buys gate parity, not coverage; the loop is a whole-file
  `grep -qF`. Advisor: nothing to rule, but READ it immediately before ruling Q1, because it is the
  proof that marker and string-loop edits do not bind behaviour.
- Q7 (operator): the six carried, unruled findings, all re-corroborated at cycle 3 and none refuted.
  Advisor recommendations: `PF-1286544c197d1b0eb4a9b0dc8e1234dc` fix now (highest
  consequence-per-cost — a truncated receipt re-creates every backlog issue);
  `PF-0c12a033f69bb6bc60b8f96134f94fd0` accept, the advisor WITHDRAWS its own finding;
  `PF-56a2ce7a053111a3aff62a4b97c5902e` rule jointly with it or risk an inconsistent pair;
  `PF-452948136bf467869d223e027191ae49` fix only if an edit batch is ordered;
  `PF-e27f1c3018b6b8477547a1b028607f96` accept, the tripwire is worth keeping;
  `PF-9a71cb9a0c590b06b890ff1517b80385` defer to backlog, also self-withdrawn.
- Q8 (operator, ordering): the advisor found ZERO conflicting remedies across the twelve. Two
  groups must be ruled together — `PF-56a2ce7a` with `PF-0c12a033`, and N4 before or with F1's edit
  batch since both reopen the same case text — and the batch-contingent items
  (`PF-452948`, N5(b), N3) only make sense once it is known whether a batch exists at all.
- Q9 (plan accuracy, no ruling needed): D-12 (`:92`) calls `github.issue_types` an EXISTING key.
  Lead-verified: `.harness/harness.json` has a `github` block at `:357` and no `issue_types` key,
  and D-16 keeps it out of the shipped template. Inaccurate as written however Q4 is ruled.
- Q10 (harness defect, not FEAT-55): `panel.readers[]` is written with a `step:` key while
  `check-state.sh` INV-32 keys those entries by `reader:` (`:534-546`), and its `expected_readers`
  set includes a `goalcheck` reader no panel writes. INV-32 fails closed the moment a plan carrying
  a panel is signed. Unchanged from the previous pass; still verified at HEAD by direct read.
- Q11 (harness defect, not FEAT-55): the digest validator appears to require a `review_sha` whenever
  `code_grade` is present, though a plan-phase panel carries `code_grade: n_a` and no `review_sha`
  by design (DEC-207/BUG-1080). It failed the cycle-3 scope reader's return and exited its job 1;
  the same shape exited the advisor tail run 1 after its work had completed and landed.
- Q12 (harness defect, not FEAT-55): a member entry accepts `status:` only with the literal
  `skipped`, so a lead cannot state that a member RAN in that field — the plan-panel roll-call the
  team file requires had to go into `adequacy_notes`. And `check-domain.sh` refuses replacing a
  written run digest, so a contract violation in a just-written `digest.md` cannot be corrected in
  place; run dir `2026-09-04-19-validator` exists only to carry the corrected block.
- Q13 (harness defect, not FEAT-55): `harness-spec-driven` names `apply`, `set-task-station`,
  `set-feature-station` and `sign-approval` as the plan-writing verbs, but `apply` is add-only
  (CONFLICT exit 7) and cannot revise an existing task or decision. The verb that can is `amend`
  (BUG-1128), which every revision cycle after the first needs; the skill's verb list omits it.
