# STATE

## Current

- feature: FEAT-54-handoff-done-when
- run: .harness/harness/features/FEAT-54-handoff-done-when/runs/2026-09-02-c2d-product/state.yaml
- squad: none — plan revision complete, awaiting the operator's signature
- status: awaiting-user

Renamed from FEAT-52-handoff-done-when: the number 52 belongs to the live feature
FEAT-52-factory-control-plane. The main session renamed the branch and worktree; this run renamed
the feature directory, the four `research-FEAT-52-*` notes and every internal id, path and archived
reference. FEAT-52 now appears only in this paragraph and in the revision note's commentary about
the rename.

The plan carries the operator's three batched rulings: pointer TARGETS resolve at write time only
(D-10; the persisted INV-17 pass checks presence, shape and pointer grammar and never opens a
target), the locally-run comprehension probe is kept whole (D-04 and its tasks and criterion), and
the shared-module mutation experiment is struck — its task, its decision and its clause in SC-07 are
all gone. BRIEF.md (10 REQ, 15 SC) and plan.yaml (12 tasks, 9 decisions, station `plan`) were
goal-checked at c2 — 0 uncarried settled lines, 0 out-of-scope violations — and read again by the
adversarial panel at cycle 2, both readers running, `severity_max: med`, nothing high, critical or
unrated. Three record defects the c2 gates found are closed: D-01's contradiction of D-10, the two
ruled dispositions, and the missing `goalcheck` reader. Both approval blocks read pending; only the
main session signs. Cycles 8 of 10. Handoff: notes/handoff-plan.md.

## Open Questions

- Q1 (blocking signature, operator): four panel findings stay `disposition: open` with no ruling —
  PF-570b9c87 (the real-corpus scan baked into the permanent suite, low), PF-91832661 (the new
  `test_kinds` entry omits `exclude`, which all 8 existing kinds carry, low), PF-d0ea19ff (SC-14's
  forever-green cases make an out-of-scope exclusion permanent machinery, low), PF-bd92960a (the
  plan never states that pointer GRAMMAR is immutable, which is what makes grammar-only persisted
  checking safe, info). Rule them or sign over them; none gates by severity.
- Q2 (blocking signature, main session): the batched 2026-09-02 ruling is legible only as
  `panel.findings[].disposition`. `approval.rulings` is the main session's write alone (DEC-120) and
  is still unmade — a struck item and an item nobody planned read alike to the next reader.
- Q3 (non-blocking, operator): the persisted INV-17 pass keeps checking pointer GRAMMAR — the
  prefix is one of the four types — while never opening a target (D-10). Grammar cannot rot, so it
  is read as inside "presence and shape"; say so if the ruling meant syntax was excluded too.
- Q4 (non-blocking, harness owner): two product-lead contexts independently chose the run dir
  `runs/2026-09-02-c2-product/` and one overwrote the other's `state.yaml`; only the digest guard
  noticed. Nothing makes a run id unique per host.
