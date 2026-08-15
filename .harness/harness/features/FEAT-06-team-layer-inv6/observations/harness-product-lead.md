# Observations — harness-product-lead — FEAT-06

- 2026-08-04 (amend2-product): an amendment note written in the house `previously read "<literal>"`
  form REINTRODUCES the very token the pass exists to delete. pm's first draft did this and pushed
  the `filter` residual in PLAN.md from 1 to 11, with `eng_squad_tasks` back to 3 — defeating the
  residual-count gate I had set as the acceptance check. pm rewrote the notes to name the key by
  role ("the task-selection key") instead of by literal. My dispatch had explicitly mandated the
  house style (mirroring PLAN.md:410-412, where the quoted literal `personas:` is NOT gated by a
  count check), so the instruction was mine and it was wrong. Lesson candidate: when a deletion is
  verified by a residual-count grep, the record-of-change must not quote the deleted string.

- 2026-08-04 (amend2-product): I verified the six PLAN sites' counts but initially accepted the
  load-bearing claim — "the signed `verify:` executes green" — on pm's reported exit code, checking
  its asserted keys against a key list supplied in my own dispatch rather than against
  `build.yaml`. That is transitive trust through two tiers on exactly the claim the run existed to
  fix. Opening the file directly (`build.yaml:33,38,42-89`) confirmed every clause and also
  confirmed nothing under `.claude/` was touched — which pm's `files_touched` had only asserted.
  One Read settled both.

- 2026-08-04 (amend2-product): my grep sweep was confined to the two files named in the dispatch
  (PLAN.md, BRIEF.md) plus `.claude/` as pre-verified by the host. `docs/harness/` — where
  DECISIONS.md records EMF-2's disposition — was unchecked until prompted. It came back clean
  (0 hits for `eng_squad_tasks|squad == eng|EMF-2`), but an unchecked surface and a clean one read
  identically in a digest unless the check is named. Now named in the digest table.

- 2026-08-04 (amend2-product): second occurrence of the harness defect amend-product filed as Q4 —
  pm returned `artifact:` pointing at PLAN.md, a file with no contract block, and the SubagentStop
  hook accepted it. Two occurrences turn that run's either/or ("either the hook does not validate
  member artifact paths, or it validated PLAN.md and passed it") into a confirmed finding. Raised
  as a non-blocking open_question, NOT recorded as Expertise — it is a bug report and would age
  into a stale workaround the moment the hook is fixed.

- 2026-08-04 (amend2-product): a requirement can ride inside a paragraph being deleted for an
  unrelated reason. T-04's `filter:` paragraph also carried the DEC-118 "a non-eng task is not
  dropped" clause; deleting the dead key wholesale would have taken it too. pm caught it and
  re-anchored it onto the `persona:` comment block.
