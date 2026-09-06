# FEAT-55 — cycle-4 panel transcription into `plan.yaml: panel:`

## BLUF

`plan.yaml`'s top-level `panel:` now records the cycle-4 panel: `last_run:
2026-09-05-27-validator`, `cycle: 4`, `severity_max: med`, `must_fix: []`, **eleven findings**,
**three `reader:`-keyed reader entries**, nothing gating. Written with one
`plan-merge.py set-panel` call (exit 0, `PANEL cycle 4` / `APPLIED`); no other write to the file.
Every PF id was computed with `panel_findings.py id`; all seven carried ids reproduced from their
stored reader+summary strings. The plan is transcription-complete for operator signature — the
eleven findings are unruled operator decisions, not a fix queue.

## The eleven findings

| # | id | status | reader | sev |
|---|---|---|---|---|
| 1 | `PF-56a2ce7a053111a3aff62a4b97c5902e` | carried, id reproduced | should-not-exist | low |
| 2 | `PF-452948136bf467869d223e027191ae49` | carried, id reproduced | scope | med |
| 3 | `PF-e27f1c3018b6b8477547a1b028607f96` | carried, id reproduced | should-not-exist | low |
| 4 | `PF-0c12a033f69bb6bc60b8f96134f94fd0` | carried, id reproduced | should-not-exist | low |
| 5 | `PF-9a71cb9a0c590b06b890ff1517b80385` | carried, id reproduced | should-not-exist | info |
| 6 | `PF-62b2b8ae0acc3509b474b744469137dc` | carried, id reproduced | scope+s-n-e | med |
| 7 | `PF-e74a2da89380cfa94f6b1693191d759d` | carried, id reproduced | s-n-e+scope | med |
| 8 | `PF-d8a7b516b793e1227b17d61c754240c7` | **re-scoped**, supersedes `PF-1280cd8fc7536c65bc22f076576c28fa` | should-not-exist | low |
| 9 | `PF-1f968f2cd73a799708e4be589d48e61b` | **new c4** | scope | med |
| 10 | `PF-383a1a92195cf2cdfba9828bda854195` | **new c4** | should-not-exist | low |
| 11 | `PF-e02dcbdf60fdf5eede40feb6066e8a08` | **new c4** | should-not-exist | info |

Carried findings 1–7 were transcribed byte-identically (reader, severity, summary, why,
`disposition: batched_to_signature_review`) and each id recomputed from the stored strings and
confirmed equal — a carried id that failed to reproduce would have been a transcription error, and
none did. The three new findings' `reader`/`severity`/`summary`/`why` were loaded programmatically
from the digest's own `panel_findings` YAML block rather than retyped, so their text is provably the
readers' own (an em-dash-for-hyphen substitution in my first hand-typed draft of finding 9's `why`
is what made that non-negotiable). Finding 10's `why` is complete: the digest line is 895 chars and
carries the full sentence through "…the row should not be that large)." — only the reading tool
truncated it, nothing was invented.

**The re-scope (#8).** `PF-1280cd8fc7536c65bc22f076576c28fa` described two residues of the removed
equality design. Residue (b) — section 1's configured-repo availability gate fronting the explicit
opt-in — was discharged by operator ruling R4 and re-verified HOLDING this cycle. Residue (a) still
reproduces: T-10 §6 resolves the live-pass type from the LOCAL `harness.json` via
`gh_issue_types.type_for_parent(overrides)` and applies it against the foreign TARGET. The narrowed
summary necessarily hashes to a new id (`panel_findings.py id` is a content hash), so the entry
carries `supersedes: PF-1280cd8fc7536c65bc22f076576c28fa` and says so in its summary and why: it is
the surviving half of a finding the operator already read, not a twelfth item.

- old id: `PF-1280cd8fc7536c65bc22f076576c28fa`
- new id: `PF-d8a7b516b793e1227b17d61c754240c7`

**Dropped — the five discharged this cycle** (all re-verified HOLDING at source by the `scope`
reader, per the digest's `discharged_rollcall`): `PF-df3caaeb7d520653866034e477d3718b` (R1, was the
only `high` and the only `awaiting_user`), `PF-1286544c197d1b0eb4a9b0dc8e1234dc` (R2),
`PF-595ce69d5574361d12a048900fcf3e0f` (R3), the old `PF-1280cd8fc7536c65bc22f076576c28fa` entry
(R4 discharged its residue (b); residue (a) survives as #8), `PF-3626edafbb21d2afb151ff470a450714`
(R5). With `PF-df3caaeb…` gone, no severity above `med` remains anywhere in the record, so INV-32
has no hard BAD to raise and no operator risk acceptance is needed.

## The readers block — a malformed record corrected

The cycle-3 record keyed its entries `step:` and carried only two of them.
`check-state.sh` INV-32 (`bin/check-state.sh:533-546`) builds `by_reader` from the **`reader:`**
key and requires all three of `should-not-exist`, `scope`, `goalcheck` with `status` in
`{ran, skipped}` — so the old shape would have emitted three BAD entries ("never ran or was not
recorded") the moment the plan was signed. The block now matches the signed FEAT-52 precedent
(`.harness/harness/features/FEAT-52-factory-control-plane/plan.yaml:1235-1244`): `reader`,
`persona`, `status`, no `reason` because nothing was skipped.

`goalcheck: ran` is truthful, not a shape-filler: the plan-phase product segment ran twice this
cycle — `notes/research-FEAT-55-goalcheck-plan-c5.md` (NO on SC-06) and
`notes/research-FEAT-55-goalcheck-plan-c6.md` (YES). Both files exist in this tree.

## fix_order

`fix_order` ranks **only** the three new findings, in the lead's order: `PF-1f968f2c…` (med) first —
its remedy adds one case to the same T-03/T-05/T-07 verify loops the c7 edits touched, and it is the
one implementation shape every currently-planned case passes — then `PF-383a1a92…` (low), then
`PF-e02dcbdf…` (info, a one-sentence edit to D-14's `because`). `fix_order_reason` states plainly
that the other eight are unranked unruled operator decisions, and `must_fix: []` because the panel
returned PASS.

## Verification

- `set-panel` exit 0; the verb splices only the top-level `panel:` range and refuses unless the
  spliced file reloads equal to the supplied value (`plan-merge.py:1050-1066`).
- Post-write reload: `approval: {status: pending}`, `status: plan`, 12 tasks, 20 decisions — all
  untouched.
- `git -C <worktree> diff --stat`: `BRIEF.md | 8 +-`, `observations/harness-pm.md | 9 +`,
  `plan.yaml | 489 +++---`. **BRIEF.md was not touched by me** — I issued no write to it; its mtime
  is 06:00:48, ~50 minutes before this plan.yaml write at 06:50:14, so its 8 changed lines are
  pre-existing uncommitted c6/c7 work. Likewise the non-`panel:` plan.yaml hunks in that stat
  (decisions and tasks) predate this run.

## Open

- Q1/Q4 in the validator digest are harness defects (validate-digest's `code_grade`/`review_sha`
  binding rejecting `n_a` on a plan review; check-domain refusing an in-place run-digest
  correction, which is why this one panel occupies two run dirs). Recorded here so they reach the
  harness owner; nothing in this transcription works around them.
- Q2 (the med, `PF-1f968f2c…`) is the operator's call at signature: add the all-recorded-rerun case
  before signing, or accept.
