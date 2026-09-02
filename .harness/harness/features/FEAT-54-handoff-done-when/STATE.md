# STATE

## Current

- feature: FEAT-54-handoff-done-when
- run: .harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-c3b-product/state.yaml
- squad: none — cycle 3 complete, awaiting the operator's signature
- status: awaiting-user

The operator's batched signature review of 2026-09-02 returned four rulings, and all four are applied
and recorded. ACCEPTED PF-570b9c87: the concurrency-sensitive real-corpus mtime/byte no-mutation audit
left the permanent integration suite — T-06 case (g) is now a fixture-corpus case and SC-04 keeps its
real-corpus claim with recorded review-time verification, pinned to the reviewer's own note. ACCEPTED
PF-91832661: T-09's intent and verify specify `exclude: .claude/worktrees/**`, the value all 8
existing kinds declare. REJECTED PF-d0ea19ff: SC-14, T-03(h) and T-06(h) stand byte-unchanged, and
the accepted consequence — a future deliberate contract change must update that coverage — is in the
disposition. REJECTED PF-bd92960a with Q3 confirmed: the typed pointer grammar is a stable contract,
the persisted pass validates grammar only and never target existence, and grammar validation is part
of the persisted shape validation; recorded in D-10's `because`, with no mechanism added.

Goal-check c3 (`notes/research-FEAT-54-goalcheck-plan-c3.md`): the plan delivers the operator's stated
intent — 10/10 grilling settled lines carried, 0 out-of-scope re-admissions. Panel c3
(`runs/2026-09-02-c3-validator/digest.md`): both readers ran, `severity_max: med`, nothing high,
critical or unrated; its one `must_fix` was the stale panel record, closed by the c3b transcription.
`plan.yaml` `panel:` now reads cycle 3, three readers `ran`, nine findings, every one dispositioned.
12 tasks T-01..T-12, decisions D-01..D-08 + D-10, `status: plan`; `check-plan-routes.py` 0 violations.
Both approval blocks read `pending` — only the main session signs. Cycles 9 of 10, runs 16 of 20.
Signature inputs: `notes/signature-inputs-c3.md`. Handoff: `notes/handoff-plan.md`.

Cycle accounting, stated so it can be audited: the correction pass that applied the two accepted
rulings is charged as cycle 9. The panel's `must_fix` repair is NOT charged a second cycle — the
transcription of a panel result into `plan.yaml` `panel:` is a mandated step of every panel cycle,
which this orchestrator had already sequenced before the panel returned, so charging it would count
one piece of work twice. Both leads reported 0 send-backs inside their runs.

Renamed from FEAT-52-handoff-done-when: the number 52 belongs to the live feature
FEAT-52-factory-control-plane. FEAT-52 now appears only in this paragraph and in the revision note's
commentary about the rename.

## Open Questions

- Q1 (blocking signature, main session): `approval.rulings` has NO write route. `sign-approval` writes
  only `status`, `approved_by` and `date` (`plan-merge.py:1052-1055`); `amend` refuses the key; `apply`
  exits 8 on a differing approval mapping. INV-32 grades the key and `templates/plan.yaml:53-56`
  documents it, so an invariant and a template promise a key no verb can produce. The four rulings are
  recorded in `panel.findings[].disposition` and, for ruling 4, in D-10's `because`; the exact ruling
  inputs are laid out in `notes/signature-inputs-c3.md`. Sign over them, or fix the verb first.
- Q2 (non-blocking, harness owner): the plan-panel's non-harness reader returned a shape outside the
  team spec's single-key `findings` envelope for the second cycle running; the hosting lead judged it
  parseable and recorded the deviation rather than correcting it. Nothing but the lead validates that
  shape — `validate-digest.py` passes non-harness agent types through.
- Q3 (non-blocking, harness owner): two product-lead contexts independently chose the run dir
  `runs/2026-09-02-c2-product/` and one overwrote the other's `state.yaml`; only the digest guard
  noticed. Nothing makes a run id unique per host. Worked around this cycle by assigning explicit
  slugs (`c3-product`, `c3-validator`, `c3b-product`) in each dispatch.
- Q4 (non-blocking, harness owner): the scope reviewer's cycle-3 note opens with a stray literal
  `yield` token before its heading (`notes/review-harness-code-reviewer-planpanel-c3.md:1`) — a tool
  artifact written into a durable signed record. Cosmetic, non-gating.
