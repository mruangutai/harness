# receipt — harness-dev-ops — FEAT-104 simplify c10, EFFICIENCY angle

## Tree-clean witness (run last, reported first per instructions)

```
$ git -C .../FEAT-104-strict-digest-schema status --porcelain
(empty output — clean)
$ git -C .../FEAT-104-strict-digest-schema rev-parse HEAD
984bd26b4dc339ea984d2532221477d465a2b05c
```
Matches the expected HEAD `984bd26b`. No probe files were created; nothing to delete.

## BLUF

**No measurable cost.** The added work per `required` error is two dict-membership tests plus one
`set()` allocation and one `continue`; it is swamped by orders of magnitude by the schema file
open+`json.load`, the `jsonschema.Draft202012Validator` construction, and `re.compile` that already
ran on the same call path *before* this delta touched it. No fix recommended.

## The four answers

**1. Cost of the added work, in the right units.** `shape_problems` is hot by call frequency (every
governed write), not by per-call volume, so the right unit is added work per invocation, not
aggregate CPU. The delta adds: one `set()` literal (`_missing_required = set()`), one `continue`
statement, and — only when `_error.validator == "required"` and `_error.instance` is a dict — a
generator over `_error.validator_value` (`["id", "status"]`, 2 elements) doing `_key not in
_error.instance` (dict `in`, O(1) amortized) for each. This is CPython-native, no I/O, no regex, no
subprocess. It is not measurable against the call's existing cost: the same code path already opens
`run-state-schema.json`, `json.load`s it, builds a `Draft202012Validator`, and `re.compile`s the
evidence-key pattern — each of those is orders of magnitude more expensive (filesystem I/O and
schema-graph construction, millisecond-range) than a handful of dict lookups (nanosecond-to-low-
microsecond range). Do not flag the pre-existing jsonschema import/file I/O — it is the evidence the
gate exists, per the dispatch's own instruction, and it already dwarfs this delta's addition.

**2. Does the second pass over `validator_value` add anything measurable?** Bounded and no. jsonschema's
`required` validator emits at most one `ValidationError` per instance (per step) when any required
key is absent — so at most one `required` error per step, i.e. at most `len(doc["steps"])` such
errors per checkpoint. `validator_value` is fixed at 2 keys (`"id"`, `"status"`) by the schema. At a
realistic step count (a handful to a few dozen steps in one run checkpoint; even a pathological
checkpoint with 100 steps), the total added work is at most `steps_count * 2` dict-membership tests
— e.g. 200 `in` checks for 100 steps. That is a few dozen to a couple hundred nanosecond-scale
operations per write, not an actionable cost: a reader can conclude this bound never needs revisiting
unless checkpoints grow to thousands of steps, which the domain doesn't produce.

**3. Can the two sets collide within one step?** No, by construction, for the case the dispatch asks
about. `_offending` gains keys from `_step`'s undeclared attributes via `set(_step) - _declared`
(check-domain.sh:1637) — since `required = ["id", "status"]` and both are listed in
`_step_schema["properties"]` (so both are in `_declared`), neither key can survive the set
difference and land in `_offending` via that route, regardless of whether the step is missing them.
The `_path[0]` route into `_offending` (line 1659) fires only for **non-`required`** schema errors
(the `required`-validator errors are diverted at line 1650–1656 via `continue` before reaching that
line), so for a single step a key that is *missing* enters only `_missing_required`, and a key that
is *present-but-invalid* (wrong type, wrong enum, etc.) enters only `_offending` — mutually exclusive
per step, because a key cannot be simultaneously absent and present-with-a-type-error on the same
step instance. **Cross-step note, out of the efficiency angle but volunteered since the dispatch
posed the question broadly:** across *different* steps in the same checkpoint the two module-level
sets are shared accumulators, so it is possible for step A to be missing `"status"` (→
`_missing_required`) while step B independently has `"status"` present with a bad type (→
`_offending`) in the same write. Both messages would then name `"status"`. This is not a false
collision — each message is factually true of a different step — and it is not new to this delta:
the pre-existing `_offending` accumulator already lacked step attribution before this fix. Not
flagging as a defect; noting only because Q3 explicitly asked for the reasoning.

**4. Repeated I/O — pre-existing, BACKLOG NOTE only, not part of this delta.**
`run-state-schema.json` is opened and `json.load`ed inside `shape_problems` on every version-2
write (line 1621–1623), and `re.compile` runs on the evidence-key pattern every call (line
1628–1629). Neither line changed in this delta — they predate `790023f0`. Backlog idea: a
module-level `functools.lru_cache`-backed loader (or a plain module-level global populated on first
call) for the parsed schema and the compiled evidence-key regex would remove the per-call
file-open/JSON-parse/regex-compile cost, which is the actually-measurable cost on this hot path —
unlike the two dict lookups this delta adds. This is explicitly a backlog note, not a finding against
`790023f0..984bd26b`.

## Recommended fix

None. The measured/bounded cost is at the noise floor against the call's pre-existing I/O and
validator-construction cost; no diff is worth proposing for this delta.

## Backlog notes (not gating)

- Cache the parsed `run-state-schema.json` and the compiled evidence-key regex at module scope
  (`functools.lru_cache` or a lazily-populated global) instead of re-reading/re-compiling on every
  `shape_problems` call. Pre-existing, unrelated to `790023f0..984bd26b`.
