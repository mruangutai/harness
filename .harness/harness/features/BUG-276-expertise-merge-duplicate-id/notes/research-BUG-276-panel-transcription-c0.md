# Panel transcription — BUG-276 — cycle 0

**The cycle-0 panel is on the record in `plan.yaml`: `panel:` at top level (a sibling of `approval:`),
both readers at `status: ran`, all three findings at their reader's own severity, plus D-09 and the
T-02 citation correction. Approval is still `pending`; `status:` is still `plan`. Nothing else was
touched, and no reader's severity was reassigned.**

## The three finding ids — exactly what was hashed

Each id is `panel_findings.py id --reader <reader> --summary <stored summary>` over the summary
string as stored, unaltered. Re-derived from the WRITTEN file after the write: all three match.

| id | reader | severity | disposition |
|---|---|---|---|
| `PF-8eac8a4b4f41d3ea8f759cdec6e73186` | `should-not-exist` | med | open |
| `PF-d6fb0ad9a0491cc93c7ac648cd092e8c` | `should-not-exist` | low | open |
| `PF-9f0a5387a328f3997e3d0b55b95e076d` | `scope` | low | resolved, `resolved_by: T-02` |

The hashed summaries are the `summary:` values in `plan.yaml panel.findings` — read them there
rather than from any paraphrase, since any reword mints a different id and would silently strand a
later `approval.rulings` overrule (`sign-approval` refuses an absent id).

## Dispositions, and the one rejection

- **`PF-8eac…` (med, open)** — the apply refusal table in `harness-distill/SKILL.md` gains no row
  for exit 11. Not fixed here. Settled *as a stated exclusion* by **D-09**, and left to the operator
  at signature. The finding stays `open`; it is the operator's to accept, not pm's to close.
- **`PF-d6fb…` (low, open)** — **REJECTED, and the rejection is on the record, not the finding.**
  `case27b` is kept. `u23b` hands `compute_union` an in-memory dict and never touches
  `parse_expertise`, so `case27b` is the only planned probe driving two byte-identical entry *lines*
  through file → `parse_expertise` → `compute_union`. The two are equivalent only because
  `parse_expertise` appends every `ENTRY_RE` match with no dedup (`expertise-merge.py:84-86`); a
  future identical-line collapse at parse would restore a silent exit 0 with `case27b` the only case
  that reddens. The remedy would also edit **SC-02**, an approval-gated BRIEF criterion. The
  advisor's own `low` is carried unchanged — the reason lives in the finding's `note:`.
- **`PF-9f0a…` (low, resolved by T-02)** — the citation drift; corrected below.

## D-09 — the exclusion, priced

D-09 records that the exit-11 row is **not** added; the **cost** (a distilling agent meeting exit 11
consults the table it routes on and finds no row, while the only other mention of 11 in that file is
the *ops* code list at ~135-141 — a different context that invites the wrong response); the
**reason** (`check-domain.sh --resolve` returns **NOBODY** for that path, and `check-plan-routes.py`
treats a NOBODY path under team execution as a violation, so the remedy would have to be an
`execution_mode: main-session-direct` task — a widening of a deliberately narrow bug fix); and that
the **operator settles it at signature**. It cites `PF-8eac…` so ruling and finding stay linked.

If the operator says "add it", the plan needs exactly **one** new main-session-direct task plus
**one** amendment to D-09. Neither is pre-written.

## T-02 intent — the citation, and how identity was proved

Route: `amend --show` → `--expect-sha256 d395c20c…1dc1` + `--value-file`. The replacement was built
by string-replacing exactly one substring in what `--show` returned, so nothing else *could* change:

```
-case_atomic_failure does at lines 597-606. Add no imports.
+case_atomic_failure, which begins at line 583, does at its two sha256 calls at lines 589
+and 601. Add no imports.
```

Post-write `--show` output compares **equal byte-for-byte** to the intended replacement (single
unified diff, empty). Independently asserted present and unchanged afterwards: the three check names
`case27a: duplicate ids exit 11`, `case27b: identical duplicate ids exit 11`,
`case27c: absent destination exits 11`; the three sub-case heads (a)/(b)/(c); and the SC-04 reuse
clause naming `case_add_only_compatibility` at line 614. `597-606` no longer occurs in the field.

`check-plan-routes.py` on this plan: 0 violations, exit 0.

## Open — for the lead, not for me

- **The plan goal-check has no run directory.** `runs/` holds only `2026-09-07-01-product`
  (plan-draft + cycle 2 + skipped prototype-gate), `2026-09-07-02-product` (plan-fix-c0),
  `2026-09-07-03-validator` (this panel), `2026-09-07-04-product` (this transcription). The
  goal-check's artifact is `notes/research-BUG-276-goalcheck-plan-c0.md` (its F-01 is cited by
  D-07); no `runs/*/state.yaml` carries a goalcheck step. So INV-32's three-reader expectation has
  no `goalcheck` run to point at — hence no `goalcheck` reader entry in `panel.readers`, which this
  dispatch also forbade.
- **Q1/Q2 from the validator digest remain the operator's**, unchanged: take the exit-11 row or keep
  D-09's exclusion, and accept or reject the `case27b` trim (rejection recorded, reversible by the
  operator).
