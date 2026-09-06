# Panel transcription c3 — FEAT-55 — what the operator now reads in `panel:`

## BLUF

`plan.yaml`'s top-level `panel:` now describes **cycle 3**: `last_run: 2026-09-04-18-validator`,
`cycle: 3`, `severity_max: high`, both readers `ran`, and **exactly twelve findings** — the six
carried unruled findings transcribed verbatim, plus the six new cycle-3 findings. Nothing was
repaired, adjudicated, resolved or dismissed here. `approval.status` is still `pending` and
`status:` is still `plan`. **One finding is gating and unruled: F1, `high`, `disposition:
awaiting_user`** — DEC-176 forbids a pre-signature fix dispatch and nobody in this batch may accept
its risk.

## New finding ids — name these to the operator

| digest tag | PF- id | severity as stored | disposition |
|---|---|---|---|
| **F1** | `PF-df3caaeb7d520653866034e477d3718b` | `high` (should-not-exist high, scope high) | **`awaiting_user`** |
| N5 | `PF-1280cd8fc7536c65bc22f076576c28fa` | `low` (should-not-exist) | `batched_to_signature_review` |
| N2 | `PF-62b2b8ae0acc3509b474b744469137dc` | `med` (scope `med`, should-not-exist `info`) | `batched_to_signature_review` |
| N3 | `PF-3626edafbb21d2afb151ff470a450714` | `low` (scope) | `batched_to_signature_review` |
| N4 | `PF-595ce69d5574361d12a048900fcf3e0f` | `low` (should-not-exist) | `batched_to_signature_review` |
| N6 | `PF-e74a2da89380cfa94f6b1693191d759d` | `med` (should-not-exist `info`, scope `med`) | `batched_to_signature_review` |

Every id was computed with `panel_findings.py id` from the exact `reader` and `summary` strings
stored in `panel:`; none was hand-written.

**Two-reader severities are preserved, never averaged.** N2 and N6 are one defect each with two
reporters at different values. Following the shape cycle 2 used for
`PF-8b5853220e5f2768339090bdbc44b1a5`, both readers' own values live in the `reader:` string
(`"scope (med) + should-not-exist (info) — … neither reader's value reassigned"`), and the scalar
`severity:` carries the higher stated value so the block never under-reports. No finding is
`unrated` — that would read as gating-equivalent to `high`.

**F1 keeps the thread it must not lose.** Its `summary` names
`PF-60f3544bd486fe9d3541a26658e5fa9f` explicitly: the operator ruled **fix** on that id, the fix
landed as text in cycle-5 edit 1, and F1 is that the added zero-`updateIssue` assertion is inert on
all three FAKE_TYPES=partial cases it was added to (T-03 case F, T-05 case G, T-07 case I — all
fresh fixtures), so that route is still untested. Both readers reached `high` independently.

## Carried findings — six, verbatim, all ids reproduce

Transcribed byte-for-byte from the cycle-2 block (`id`, `reader`, `severity`, `summary`, `why`,
`disposition: batched_to_signature_review`). Each id was re-derived with
`panel_findings.py id --reader '<stored reader>' --summary '<stored summary>'`:

| id | reproduction check |
|---|---|
| `PF-56a2ce7a053111a3aff62a4b97c5902e` | **REPRODUCES** |
| `PF-1286544c197d1b0eb4a9b0dc8e1234dc` | **REPRODUCES** |
| `PF-452948136bf467869d223e027191ae49` | **REPRODUCES** |
| `PF-e27f1c3018b6b8477547a1b028607f96` | **REPRODUCES** |
| `PF-0c12a033f69bb6bc60b8f96134f94fd0` | **REPRODUCES** |
| `PF-9a71cb9a0c590b06b890ff1517b80385` | **REPRODUCES** |

Zero mismatches, so nothing was rewritten and nothing re-hashed.

**Cycle 3 re-corroborated all six and refuted none.** Both readers independently re-derived them
against the post-c5 text; no cycle-5 edit collided with text any of them cites. That corroboration
is recorded **here only** — no stored finding's severity, summary, `why` or disposition was altered
to reflect it, and their disposition remains the operator's alone.

## Discharged — three, dropped from `findings:`, ruled and applied

They left the block the way cycle 2's ruled findings left it: ruled by the operator and applied,
not evaporated. Ruling source: `notes/answers-plan-panel-20260904-c2.md`.

- `PF-60f3544bd486fe9d3541a26658e5fa9f` — ruled **fix** ("add the missing zero-`updateIssue`
  assertion to T-03's gh-sync-open partial-type refusal case"); applied as cycle-5 edit 1.
  **F1 re-opens the underlying risk this remedy was meant to close** — the ruling is discharged,
  the defect is not.
- `PF-08da208931348b8cb200b34e8e7a1d31` — ruled **allow** (T-10 live-probe destination:
  `--create-in` may name an explicitly supplied Issue-Type-enabled repository rather than being
  restricted to configured `github.repo`, retaining the probe's opt-in guard); applied as cycle-5
  edit 3. N5 records two residues of that change; it does not re-open the ruling.
- `PF-8b5853220e5f2768339090bdbc44b1a5` — folded into the same edit as the fix ruling (cycle-5
  edit 2, T-03's required-string loop at `:470`); applied. N6 records that edit 2 bought parity and
  not coverage, which that finding's own disposition already disclosed.

## `last_run` versus the digest directory — why they differ

`panel.last_run` is **`2026-09-04-18-validator`**: that is the run of record and its `state.yaml`
is the checkpoint. But the block transcribed here comes from
**`runs/2026-09-04-19-validator/digest.md`**. The `-18` digest carried a schema violation
(`status: ran` on member entries, where the schema reserves `status:` for the literal `skipped`),
and `check-domain` refuses any replacement of a written run digest — so a second run directory
exists **solely to carry the corrected block**. The `-18` digest is not deleted and its findings are
identical in substance.

## `must_fix` and `fix_order`

`must_fix` carries the digest's single F1 entry verbatim, with both reader severities and the note
that `gates.review` in `harness.json` is `advisory_unless_high`, which `severity_max: high` clears —
so this FAIL blocks rather than advises.

`fix_order` is `[F1, N5, N2, N3, N4]`. The reason travels with it in a sibling
`fix_order_reason:` key, because it is **deliberate and not severity order**: F1 leads because its
remedy adds cases to the same `verify` loops edit 2 just changed; N5 and N2 are adjacent edits to
one region of T-10 §6; N5 outranks N2 despite a lower stated severity because it is a fresh
consequence of the ruling the operator just made. **N6 is recorded and not ranked** — it is the
accepted scope of a ruled remedy, not a new defect.

## Open questions for the operator (raised, not decided here)

- **Q1 (blocking)** — F1's remedy is a NEW case pairing a pre-recorded `typed="created"` remnant
  with `FAKE_TYPES=partial` in one run, on all three routes; adding cases changes T-03/T-05/T-07's
  CASE-marker and required-string loops. Does the operator want that, or does
  `PF-60f3544bd486fe9d3541a26658e5fa9f` get re-ruled as accepted-untested?
- **Q2** — N2's two SKIP wordings: pin a discriminating rule, or delete the third bullet?
- **Q3/Q4 (harness defects, not plan defects)** — the digest validator appears to require a
  `review_sha` whenever `code_grade` is present, which a plan-phase panel never has; and member
  entries may carry `status:` only with the literal `skipped`, so a lead cannot state that a member
  RAN in that field. Both are carried up as harness defects, not worked around in the plan.

## What was not touched

No task, no decision, no `approval:`, no `status:`, no BRIEF edit, no `review_sha`, no GitHub
mirroring. The only `plan.yaml` write went through
`plan-merge.py set-panel --value-file /tmp/feat55-panel-c3.yaml` (a `/tmp` input, not a repo
artifact).
