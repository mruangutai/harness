# UI Review (Mode B) — FEAT-104-strict-digest-schema — panel c11, pin `984bd26b`

## BLUF

**PF-C10-01 is genuinely CLOSED** — MEASURED live: a step missing `status` now renders a truthful
head, a non-empty correctly-named key list, and an actionable remedy. **The fail-open shape the
batch context flagged is CONFIRMED closed** at this pin, by direct code tracing, not adopted from
the dispatch. **Q14 is real and reproduces today** — a declared-key type error (`cycles:
not-an-int`) still prints under "undeclared step key" with remedy advice ("move it under
`evidence`") that is actively wrong for a key that is already declared; rated **med**, not high,
because the key is still named correctly and the cited schema file remains a correct escape hatch
for a diligent reader. Mixed violations compose cleanly (two ordered, non-contradictory messages).
Stale comment at `check-domain.sh:1646-1647` confirmed still stale, now describing only one of two
branches — low, non-gating. No `severity_max >= high`, `must_fix: []` → **PASS**.

## Scope — measured, not predicted

`git diff --stat origin/main..984bd26b -- . ':!.harness'` → **18 files, +3203/-19**, matching the
dispatch exactly. No rendered-UI extension (`html|css|scss|tsx|jsx|vue|svelte|less`) appears outside
`.harness/` notes (excluded, and c10 already confirmed those are generated ship-review artifacts).
No `DESIGN.md` for this feature (unchanged from c10). The only user-facing surface in this diff is
the CLI stderr text emitted by `check-domain.sh`'s step-schema denial — the dispatch's named
diagnostic-surface remit, and the exact surface `790023f0..984bd26b`'s two-file delta
(`check-domain.sh` +26/-8, `test-check-domain.py` +6/-0) touches.

## PF-C10-01 closure — MEASURED

Live repro under a disposable `mktemp -d` fixture root (no tracked file touched), reusing
`tests/integration/check_domain_support.fire`/`fixture` read-only, a `schema_version: 2` step with
`status` deleted:

```
check-domain: BLOCKED — …/state.yaml: missing required step key.
  missing key(s): 'status'. Required step fields are declared in .claude/skills/harness/bin/
  run-state-schema.json; supply each required field.
```

Against the three things I graded `high` at c10: **head is truthful** (no longer "undeclared step
key" for an absent field), **key list is non-empty and correct** (`'status'`, not `.`), **remedy is
actionable** (names the schema file and states the concrete fix — supply the field). This is a full
closure of the exact shape I rated, not a partial fix. Root cause read in
`git show 984bd26b:.claude/skills/harness/bin/check-domain.sh:1648-1668`: a new `_missing_required`
set, populated only from `_error.validator == "required"` errors against `_error.validator_value`,
gets its own head/remedy pair ahead of the pre-existing `_offending` branch.

`tests/integration/test-check-domain.py`'s new case (`_undeclared_cases()`, "schema_version 2 names
a missing required step key") pins the same shape I reproduced independently — confirms my repro is
not an artifact of my own fixture construction.

## Fail-open re-derivation — CONFIRMED, by my own trace (not adopted)

Before `984bd26b`, an unconditional append made a non-empty `_schema_errors` always emit some
denial line. After it, both branches are conditional (`if _missing_required:` / `if _offending:`),
so the risk is a schema error populating neither bucket, silently accepting a write the old code
refused. I traced every step-level keyword the schema actually declares
(`git show 984bd26b:.claude/skills/harness/bin/run-state-schema.json`'s
`properties.steps.items` has exactly `type`, `required`, `additionalProperties` at its own level —
confirmed by direct read, matching the dispatcher's measurement) against the three places that can
populate the buckets:

- **`type`** (step not an object) — caught *before* the schema-errors loop even runs, by
  `if not isinstance(_step, dict): _offending.add("<step>"); continue` (line ~1633). Non-empty
  regardless of how the loop later routes the matching `iter_errors` entry.
- **`additionalProperties`** (rogue step key) — caught independently by
  `_offending.update(set(_step) - _declared)` (line ~1636), a straight set difference that runs
  whether or not the corresponding schema-errors entry (path `[]`, validator
  `"additionalProperties"`) gets routed anywhere by the loop.
- **`required`** (missing key) — the only keyword with *no* independent pre-existing catcher; this
  is exactly the gap `_missing_required` was added to close, and Case 1 above shows it firing.

So for the three keywords this schema actually declares, every one has a guaranteed non-empty
source independent of the new conditional gating. **CONFIRMED closed at this pin** — not because no
gap could exist in principle (Q15, below), but because none of the three currently-reachable
schema-error shapes can fall through both `if`s empty-handed. Method: source trace plus the three
live reproductions in this note (Cases 1–3) as confirming evidence, not the sole basis.

## Q14 — MEASURED reproduction, rated `med`

Same disposable fixture, `schema_version: 2` step with `cycles: not-an-int` (a **declared** field,
not required, wrong type):

```
check-domain: BLOCKED — …/state.yaml: undeclared step key or evidence shape.
  offending key(s): 'cycles'. A recovery field is declared in .claude/skills/harness/bin/
  run-state-schema.json; a per-dispatch fact goes under `evidence` with a lowercase identifier key
  and a scalar or scalar-array value.
```

Concrete failure scenario: an author who trusts the remedy sentence literally would move `cycles`
under `evidence:` — evidence keys need only an identifier-pattern name and a scalar/scalar-array
value, so `evidence: {cycles: "3"}` would pass the schema cleanly (**exit 0**) while the step-level
`cycles` field the harness's retry-accounting logic actually reads stays silently absent. The
denial itself is safe (exit 2, correct key named) and `cycles` is not in `required: ['id',
'status']` (confirmed by reading the schema directly) so this is not PF-C10-01's total-information-
loss shape — a reader who instead opens the linked `run-state-schema.json` (the message's own
cited route) can see `cycles`'s declared type and self-correct without acting on the wrong
sentence. That tempering is why I rate this **med**, not high: the key is truthfully named and a
correct authoritative pointer is present, but the prose actively recommends the wrong fix for a
key that is not undeclared at all. **Would move to high** if either (a) the remedy sentence were
the *only* signal offered (it currently sits alongside a correct file pointer), or (b) a plausible
follow-on write of the misdirected fix could itself pass validation *and* violate `required` — it
doesn't here because `cycles` isn't required, so the failure is silent field loss, not a second
denial. Both qa and eng scoped this the same way last cycle without gating it; I reach the same
`med`-not-high call independently, on the surface I own (message truth/remedy correctness), not by
adopting their number.

Root cause, read directly: the loop's fallback branch (`_path = list(_error.path); if _path:
_offending.add(str(_path[0]))`) treats *any* non-`required` schema error as an "offending key,"
regardless of whether that key is declared — a type/range error on a declared field and a genuinely
undeclared key both land in the same bucket with the same header and the same evidence-relocation
remedy.

## Q15 — latent, present-tense unreachable (not rated as a current defect)

The branch keys on the validator's *name* (`"required"`) rather than the structural cause (an
empty `error.path`). A future `minProperties`/`dependentRequired` addition at step level would
report at an empty path with a validator name the branch doesn't special-case, reopening the
fail-open shape for that new keyword. Confirmed no such keyword exists at this pin (schema census
above). This is a latent design-coupling risk worth naming, not a present defect — I make no
present-tense rating and propose no hardening against keywords the schema does not declare, per the
dispatch's explicit boundary.

## Mixed violations — comprehensible, ordered, non-contradictory (MEASURED)

Same fixture, a step missing `status` *and* carrying `rogue_step_key`:

```
check-domain: BLOCKED — …/state.yaml: missing required step key.
  missing key(s): 'status'. Required step fields are declared in …
check-domain: BLOCKED — …/state.yaml: undeclared step key or evidence shape.
  offending key(s): 'rogue_step_key'. A recovery field is declared in …
```

Order is deterministic by code structure (`if _missing_required:` always precedes `if _offending:`,
two independent conditionals — not an artifact of jsonschema's error-iteration order). Reading it
as a reader would: "what's missing" then "what's extra," each naming a distinct, correctly-owned
key, remedies pointing at non-overlapping fixes. No contradiction between the two sentences. Not a
finding.

## Disposal of c10 items in this lens

- **PF-C10-01** — **CLOSED**, per the MEASURED repro above. Not carried.
- **Backticked `` `evidence` `` in stderr** — unchanged at `check-domain.sh:1675` (still present
  verbatim in the offending-key remedy sentence). c10 already confirmed this is a codebase-wide
  convention (matching quote style elsewhere in the same file and in `validate-digest.py`); I did
  not re-derive that grep this cycle since the text itself is byte-identical to what c10 examined.
  Not gating; not re-raised.
- **Stale comment, `check-domain.sh:1646-1647`** — confirmed still present verbatim: "Type/value
  failures on declared fields may not be captured by the vocabulary comparisons above; name their
  nearest field." That describes only the second (`_offending`, `_path[0]`) branch. The first
  branch the comment now sits above (`_missing_required`, lines 1648–1659) does something the
  comment doesn't mention at all — it intercepts `required` errors *before* they'd ever reach the
  "name their nearest field" behavior the comment describes. Rated **low** — comments don't affect
  runtime behavior, but a reader debugging this block would be misled about what the first half of
  the loop is for. Non-gating; likely co-owned with `harness-code-reviewer`'s lens, flagged there
  too.

## Accessibility / theme parity

Not applicable — batch/CLI stderr only, no colour-only state encoding, no light/dark variant to
compare (repo Expertise G-02). Confirmed not-applicable, not an omission.

```yaml
VERDICT: PASS
DIGEST:
  headline: PF-C10-01 closed (measured) — head truthful, key list non-empty and correct, remedy actionable; fail-open shape re-derived and confirmed closed for the schema's three declared step-level keywords; Q14 reproduces today (declared-field type error mislabeled "undeclared," remedy tells reader to relocate a key that is already correctly placed) rated med, not high, because the key is still named truthfully and a correct route is still cited.
  mode: B
  in_scope: true
  severity_max: med
  findings: 2
  must_fix: []
  contract_violations:
    - { path: ".claude/skills/harness/bin/check-domain.sh:1657-1659,1669-1677", actual: "a declared step key with a type/range violation (e.g. `cycles: not-an-int`) prints under 'undeclared step key or evidence shape.' with a remedy telling the author to move the key under `evidence`", specified: "the key IS declared (present in run-state-schema.json's step properties); the correct remedy is to fix the value's type, not relocate the key" }
    - { path: ".claude/skills/harness/bin/check-domain.sh:1646-1647", actual: "comment 'Type/value failures on declared fields may not be captured by the vocabulary comparisons above; name their nearest field.' sits above a loop with two branches", specified: "comment describes only the second (_offending) branch; the first (_missing_required) branch added in 984bd26b does something the comment doesn't mention" }
  a11y: ["not applicable — batch/CLI stderr text only, no colour-only encoding, no rendered surface (repo Expertise G-02)"]
  open_questions:
    - { id: Q1, question: "Q14: should the offending-key branch check `key in DECLARED` and route declared-but-wrong-type keys to a third, distinct head/remedy pair ('declared step key has the wrong shape' + 'fix its value, see run-state-schema.json for the expected type') instead of the undeclared-key remedy? DEC-174 means I cannot apply this myself.", blocking: false }
    - { id: Q2, question: "Stale comment at check-domain.sh:1646-1647 — should it be split or reworded to describe both branches now that 984bd26b added the _missing_required branch above it?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-ui-reviewer-c11.md
```
