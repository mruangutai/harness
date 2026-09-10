# Record fix — run-07 checkpoint `review_sha` corrected — FEAT-104-strict-digest-schema

**BLUF. The correction LANDED. `check-domain.sh` did not refuse it.**
`.harness/harness/features/FEAT-104-strict-digest-schema/runs/2026-09-09-07-qa-gate-validator/state.yaml`
now reads `review_sha: 168f875f`, the commit the run actually graded, replacing the stale
dispatch-time pin `6126ac07`. Nothing else about the run changed: `schema_version` stays `2`,
`run_uid` is preserved verbatim, the single `qa-gate` step is still `complete` with `verdict: PASS`,
and `verdict`/`status`/`severity_max`/`cycles_used` are untouched.

**`tip_sha` was already correct** (`168f875f`) and needed no edit — the checkpoint was internally
inconsistent, pinning a review at one commit while recording the tip it actually measured at another.
That inconsistency is now resolved; the file no longer contradicts its own digest
(`runs/2026-09-09-07-qa-gate-validator/digest.md`) or its member note
(`notes/qa-feat104-tip-168f875f.md`), both of which say `168f875f` throughout, and it now agrees with
`feature.json`'s re-pinned `review_sha: 168f875f`.

## The measurement the dispatch asked for — closed-run artifacts have TWO correction regimes, not one

The eng-side refusal at `check-domain.sh:1327` is **not** a general "closed run artifacts cannot be
corrected" rule. It is specific to `digest.md`, and the guard's routes behave oppositely:

| Route | Matcher | Regime | Field correction possible? |
|---|---|---|---|
| run digest | `RE_RUN_DIGEST` (`check-domain.sh:1315-1332`) | **prefix-append only** — `not content.startswith(prior)` denies; message says "the missing line must be appended at the end" | **No.** `validate-digest.py`'s parser stops at the indent-0 `artifact:` line, so appended text is never parsed |
| run checkpoint | state-file shape / DEC-150 + `run-state-schema.json` | **schema validation only** — closed allowlist checked; no prior-content prefix relation required | **Yes.** Verified by this write landing |
| run identity witness | `RE_RUN_IDENTITY` (`check-domain.sh:1334-1342`) | **write-once, refuses always** | No, by design |

The third witness the dispatch anticipated did not materialise, and the negative result is the more
useful one: **the missing correction channel is a `digest.md` defect, not a closed-run-artifact
defect.** `state.yaml` — the file a successor actually reads for control flow — is correctable in
place. Generalising the eng-side refusal to all run artifacts would have been wrong.

## What was added, and why it is not a schema widening

Two keys inside the `qa-gate` step's existing `evidence:` map:

- `review_sha_corrected_from: 6126ac07`
- `review_sha_corrected_reason: dispatch_pin_stale_run_graded_tip_168f875f`

`evidence` is a **declared** step property whose `propertyNames` pattern (`^[a-z][a-z0-9_]*$`) and
scalar-or-scalar-array value constraint both admit these (`run-state-schema.json`, step `evidence`
block). No key outside the closed vocabulary was invented and no top-level key was added — the
top-level allowlist declares no `note`, so the rationale lives here and the matchable markers live in
`evidence` (DEC-154). The record is honest about having been amended rather than silently rewritten
(PRINCIPLES rule 15).

## Artifact path — the dispatch's path was denied, correctly

The dispatch named
`.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-validator-lead-recordfix.md`.
`check-domain.sh` refused it verbatim:

```
check-domain: BLOCKED — harness-validator-lead may not write .claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-validator-lead-recordfix.md
  Permitted for you: .harness/*/features/*/runs/*-validator/**, .harness/expertise/harness-validator-lead.md, .harness/*/expertise/harness-validator-lead.md, .harness/*/features/*/observations/harness-validator-lead.md, .harness/notes/analysis-*.md
```

That `notes/review-<self>-*.md` pattern belongs to the four **reviewer** personas, not to the lead.
Per `harness-handoff` (#216), a dispatch naming a path for me does not override the guard, so this
artifact went to a path I do own. **This denial is about MY artifact only — the checkpoint correction
itself was never refused.**

## What this does NOT do

- **Nothing was re-graded.** No suite ran, no member spawned, no run directory created, nothing
  committed. Run-07's PASS stands on its original evidence, which was always measured at `168f875f`.
- **`digest.md` was not touched** and needs none: it already names `168f875f` correctly.
- **`STATE.md` was not inspected** — outside the one-file target. See Q1.

## Open questions

- **Q1 (non-blocking, orchestrator):** `feature.json` carries `review_sha: 168f875f`. Was `STATE.md`'s
  human-facing pointer re-pinned in the same operation? Repository Expertise G-01: a re-pin applied to
  one and not the other sends the next run at a stale SHA. Not verified here.
- **Q2 (non-blocking, harness owner):** the `digest.md` correction channel is representable but not
  readable — `check-domain.sh:1327` mandates a strict prefix-append while `validate-digest.py` stops
  parsing at the indent-0 `artifact:` line, so an appended correction can never be parsed. The
  contrast with `state.yaml` is now measured. A harness defect report, not a workaround to memorise.
- **Q3 (non-blocking, harness owner):** dispatches keep routing lead artifacts to
  `features/*/notes/review-harness-validator-lead-*.md`, which no lead may write. Either the lead's
  grant in `.harness/team-config.yaml` should include it, or dispatch templates should stop naming it.
