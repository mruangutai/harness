# Security review — FEAT-104-strict-digest-schema — panel c11 @ 984bd26b

**VERDICT: PASS.** No new must-fix. The central question this panel exists to grade — whether the
new `_missing_required`/`_offending` split can fail OPEN (accept a write the old code refused) — is
**REFUTED for the schema as it stands today**, by independent code trace, not by adopting the
dispatcher's claim.

## Census (MEASURED)

`git diff --stat origin/main..984bd26b`: 18 files, +3203/-19. Security surface, checked
`790023f0..984bd26b` per file:
- **`check-domain.sh`** — MOVED, `+26/-8` (MEASURED `git diff --stat`). The only code file that
  changed. Audited in full below.
- **`check-state.sh`** — byte-identical (`git diff --stat 790023f0..984bd26b -- check-state.sh`
  returns nothing). CF-1's site is unchanged.
- **`validate-digest.py`**, **`run-state-schema.json`** — byte-identical, same measurement. The c10
  finding that these two are unmoved is CONFIRMED still true at this pin, re-measured, not carried
  forward blind.
- **`tests/integration/test-check-domain.py`** (+6 lines) — test-only, exercises the new message
  text, no trust-boundary change.
- Out of scope, no surface: 6 agent `.md` files + 2 `SKILL.md` (dispatcher prose), the inert
  `pre-t04-validate-digest.py.fixture` (loaded as text, run as a subprocess target — reconfirmed via
  grep, not imported), and the 8 `.harness/harness/features/…` bookkeeping files (STATE.md,
  feature.json, notes, observations — prose, not consumed by any gate). `tests/unit/` — 0 files
  touched (measured, empty diff).

## The fail-open question — REFUTED, by trace + schema census (MEASURED)

Traced `shape_problems` (`check-domain.sh` ~1618–1685) against `run-state-schema.json`'s step
subschema (`git show 984bd26b:...run-state-schema.json`, parsed): step level declares exactly
`type: object`, `required: [id, status]`, `additionalProperties: false`, `properties: {...}` — no
other keyword. Every one of the 21 step properties is a scalar/array leaf; **none** is `type:
object` with its own `required`; the one nested object, `evidence`, uses `propertyNames`/`oneOf`
under `additionalProperties`, never `required`. Given that:
- a whole-step `type` violation (step not a dict) is caught by `_offending.add("<step>")`, reached
  **before** the `if _schema_errors:` block runs, regardless of what `_schema_errors` contains;
- an `additionalProperties` violation is caught by `_offending.update(set(_step) - _declared)`, also
  before that block;
- a `required` violation is now caught by the new `_missing_required` branch;
- every other possible error (any property-level `type`/pattern mismatch) carries that property as
  `error.path[0]`, so `_path` is non-empty and lands in `_offending` via the walk.

No schema error in this document can reach the loop with an empty `error.path` AND a validator other
than `required`/`additionalProperties`/`type` — because the schema declares no other keyword capable
of firing at the step's own level. **Both messages cannot go simultaneously empty for any input this
schema can currently reject.** Confirmed, not adopted.

**Sharper than the batch framing (worth carrying forward):** the `_missing_required` branch keys on
`_error.validator == "required"` with no path check — it would also swallow a **nested** `required`
violation (e.g. under a future `evidence` sub-object) into the wrong bucket, since nothing gates on
`error.path == []`. No such nested `required` exists today (evidence has none), so this is unreachable,
same as Q15 — but it's a second, narrower fragility inside the branch the panel is asking about, not
just "a future sibling keyword." Recorded as info; not a present finding.

## Data exposure in the two new/changed stderr paths — no finding

- `missing key(s): …` — keys come from `_error.validator_value`, i.e. the schema file's own
  `required` array (`id`, `status` — static, developer-authored), never the user document, and are
  still passed through `repr()`. No attacker-influenced or secret-bearing content reaches this line.
- `offending key(s): …` (pre-existing, unchanged by this diff) — genuinely user-document-derived,
  and correctly `repr()`'d; unchanged posture from c9/c10.
- `except Exception` route (`type(_schema_exc).__name__: _schema_exc`, pre-existing) — traced every
  way it can fire: schema-file load/parse failure, static `re.compile` failure, `KeyError` on the
  static schema's own structure, or a `RecursionError`/`MemoryError` from a pathologically large/deep
  document (structural, not content-carrying). `jsonschema.iter_errors` never raises
  `ValidationError` into this block — it yields error objects. No user-document *content* flows into
  this message either.

## CF-1 — re-derived at 984bd26b: CARRIED UNCHANGED, med

`check-state.sh:1524-1526` still interpolates `sdoc.get('run_id', '<unknown>')` and `_step_id` as
bare strings (no `!r`) into the INV-16 audit line. File is byte-identical to `790023f0` (MEASURED,
empty diff) — same offset, same code. Threat unchanged: an actor using the DEC-85 Bash-write route to
place a `state.yaml` with `run_id`/step `id` carrying ANSI/terminal control bytes gets that string
echoed raw into the operator's terminal at the next `/harness` entry, letting the audit line spoof or
hide itself. Disposition: **carried, non-blocking** (already Q1 in STATE.md under DEC-174, one-line
`!r}` fix routed to the next main-session touch of this file) — not re-raised as new, not escalated.

## DEC-85 Bash-write bypass — standing, unchanged reachability

`bash-write-guard.sh` is not in this diff's 18-file set; the bypass is unaffected in either
direction. It remains CF-1's sole precondition and, separately, the reason the new write-time
`schema_version`/step-schema checks in `check-domain.sh` bind only `Write`/`Edit` — a Bash-authored
`state.yaml` still reaches disk unchecked at write time, caught only by `check-state.sh`'s at-rest
INV-16 sweep (same topology as c9/c10; not widened or narrowed by `984bd26b`).

## Q14 / Q15 — my lens

- **Q14** (declared-key type/range error routed to "undeclared step key" remedy text): outside this
  lens. It is a wrong-remedy usability defect — no attacker gains capability, no data crosses a
  boundary, the denial itself is still correct and fail-closed. Not rated for security.
- **Q15** (latent, validator-name-keyed branch vs. a future `minProperties`/`dependentRequired`):
  CONFIRMED present-tense **unreachable** — no such keyword exists anywhere in `run-state-schema.json`
  today (full step-schema keyword census above), and the schema is developer-authored, not
  user-reachable input. Rated `info` as a design-fragility note, not a live security defect. Do not
  gate on it.

## Threat model

| boundary | STRIDE | mitigated |
|---|---|---|
| schema-error → denial-message routing (`_missing_required`/`_offending` split) | Tampering (fail-open write) | true — refuted by trace + schema census, this pin |
| `missing key(s)` message vs. schema-file-only content | Information disclosure | true — no user-document path reaches it |
| `except Exception` diagnostic vs. document content | Information disclosure | true — no content-carrying exception path found |
| Bash-authored state.yaml vs. check-state.sh INV-16 report echo (CF-1) | Spoofing | false, gated behind the pre-existing DEC-85 precondition — unchanged |
| DEC-85 Bash-write bypass vs. new write-time step schema | Tampering | false, precondition-absent for the ordinary path; unchanged reachability |

```yaml
VERDICT: PASS
DIGEST:
  headline: "Fail-open split REFUTED for the live schema (traced+censused); CF-1 carried unchanged at med; no new exposure."
  in_scope: true
  scope_reason: "check-domain.sh moved (+26/-8) this cycle and is the write-time schema gate; re-measured, not assumed stale-safe."
  severity_max: med
  findings: 2
  must_fix: []
  threat_model:
    - { boundary: "schema-error routing fail-open split", stride: "T", mitigated: true }
    - { boundary: "missing-key message vs schema-only content", stride: "I", mitigated: true }
    - { boundary: "except-Exception diagnostic vs document content", stride: "I", mitigated: true }
    - { boundary: "CF-1: Bash-authored state.yaml vs INV-16 echo", stride: "S", mitigated: false }
    - { boundary: "DEC-85 bypass vs new write-time step schema", stride: "T", mitigated: false }
  open_questions:
    - { id: Q1, question: "CF-1 one-line !r} fix on check-state.sh:1525-1526 — route to next main-session touch (DEC-174 carve-out), non-blocking.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-security-reviewer-c11.md
```
