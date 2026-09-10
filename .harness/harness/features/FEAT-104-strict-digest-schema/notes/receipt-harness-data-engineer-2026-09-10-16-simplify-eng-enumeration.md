# Receipt — harness-data-engineer — accept-shape enumeration — FEAT-104 c10

## BLUF

No accept-shape hole. Every JSON Schema keyword reachable under `properties.steps.items`
produces an error that either (a) routes through `_missing_required` (the `required` arm), or
(b) has a non-empty `error.path` and lands in `_offending` via `_path[0]`, or (c) has an empty
path but is independently caught by one of the three manual checks that run outside the
`_schema_errors` loop (`not isinstance(_step, dict)`, `set(_step) - _declared`, or the evidence
manual checks). **13 rows enumerated, 0 fall through to accept.** The fix is correct: the
conditional split does not open an accept path.

Two real but non-gating findings surfaced along the way: the `isinstance(_error.instance, dict)`
guard on the `required` arm is dead weight (simplification, not correctness), and the two output
messages CAN both name the same key across a multi-step document (a UX/wording confusion, not a
denial-bypass — the write is still denied either way).

## Enumeration table (empirical `error.path` from Draft202012Validator, script below)

| # | Keyword / location | validator | empirical `path` | empty+non-required fallback catcher | verdict |
|---|---|---|---|---|---|
| 1 | step itself: `type: object` (non-dict step, e.g. list/string) | `type` | `[]` | `not isinstance(_step, dict): _offending.add("<step>")` (line 1634-1636, runs unconditionally per step, independent of `_schema_errors`) | CAUGHT |
| 2 | step itself: `additionalProperties: false` (extra top-level key) | `additionalProperties` | `[]` | `_offending.update(set(_step) - _declared)` (line 1637, runs unconditionally per dict step) | CAUGHT |
| 3 | step itself: `required: ["id","status"]` (either/both missing) | `required` | `[]` | routed to `_missing_required` arm directly (not "fallback" — this is the primary path for this keyword) | CAUGHT |
| 4 | `properties.id.type` wrong (e.g. `id: 1`) | `type` | `['id']` | n/a — path non-empty, `_offending.add('id')` fires directly | CAUGHT |
| 5 | `properties.seq.type` union `["integer","string"]` wrong (e.g. `seq: null`) | `type` | `['seq']` | n/a — path non-empty | CAUGHT |
| 6 | `properties.depends_on.items.type` wrong (e.g. `[1,2]`) | `type` | `['depends_on', 0]` (and `[..., 1]` per bad item) | n/a — `path[0] == 'depends_on'` | CAUGHT |
| 7 | `properties.outputs.items.type` wrong | `type` | `['outputs', 0]` | n/a — path non-empty | CAUGHT |
| 8 | `properties.mutates_repo.type` wrong (e.g. `"yes"`) | `type` | `['mutates_repo']` | n/a — path non-empty | CAUGHT |
| 9 | `properties.cycles.minimum: 0` violated (e.g. `-1`) | `minimum` | `['cycles']` | n/a — path non-empty | CAUGHT |
| 10 | `properties.max_cycles.minimum: 0` violated | `minimum` | `['max_cycles']` | n/a — path non-empty | CAUGHT |
| 11 | `properties.redispatches.minimum: 0` violated | `minimum` | `['redispatches']` | n/a — path non-empty | CAUGHT |
| 12 | `properties.evidence.type: object` wrong (e.g. `evidence: "nope"`) | `type` | `['evidence']` | n/a — path non-empty | CAUGHT |
| 13 | `evidence.propertyNames.pattern` violated (bad key, e.g. `"BadKey"`) | `pattern` | `['evidence']` **(empirically non-empty — jsonschema attributes propertyNames errors to the containing object's path, not `[]`)** | n/a — path non-empty; also independently caught by the manual `_name_pattern.fullmatch` check (adds the literal bad key string) | CAUGHT (doubly) |
| 14 | `evidence.additionalProperties.oneOf` violated — dict value | `oneOf` | `['evidence', '<key>']` | n/a — `path[0] == 'evidence'`; also independently caught by the manual `isinstance(_value, dict)` check (adds the literal key) | CAUGHT (doubly) |
| 15 | `evidence.additionalProperties.oneOf` violated — array-of-dict value (`{"k": [{"x":1}]}`, NOT caught by the manual dict-value check since the value itself is a list, not a dict) | `oneOf` | `['evidence', '<key>']` | n/a — `path[0] == 'evidence'` fires via the schema-error route alone; this is the one row where the manual evidence checks do NOT independently catch it, but the schema-error path route does | CAUGHT (schema-error route only) |

Every non-`required` step-object-level error (`type`, `additionalProperties`) that legitimately
reports an empty path is independently caught by a manual check that runs *unconditionally*, in
the same per-step iteration, before/alongside `_schema_errors` accumulation — so the conditional
split in the `if _schema_errors:` block cannot suppress them.

Row 15 is the closest thing to a "gap" in redundancy — it is the one keyword instance where the
schema-error route is the ONLY catcher (the manual evidence checks miss it) — but the schema-error
route still fires correctly (non-empty path, `_offending.add('evidence')`), so it is CAUGHT, not a
fall-through. Confirms the schema-error path route is load-bearing, not merely decorative.

## isinstance guard — dead weight, empirically confirmed

Fed `V.iter_errors([1,2,3])` and `V.iter_errors("abc")` (both fail the top-level `type: object`
check first): only a `type`-validator error is produced; jsonschema's `required` validator never
even runs against a non-dict instance (it is only meaningful for objects and is a no-op / not
invoked by the validator machinery for non-object instances under Draft202012). So
`_error.validator == "required"` implies `isinstance(_error.instance, dict)` is already true —
the `isinstance` check can never evaluate false when the `validator == "required"` branch is
taken. **Dead weight — a simplification finding, not a correctness finding.** One-line
consequence: the `and isinstance(_error.instance, dict)` clause on line 1651 could be dropped
without changing behavior.

## Collision — id/status CAN appear in both messages, empirically confirmed

`required` only names `id` and `status`, both of which are declared properties, so a key can
never enter `_offending` via `set(_step) - _declared` (undeclared-key route) while also being
"missing" — those routes are mutually exclusive **per key, per step**. But `_missing_required`
and `_offending` accumulate across ALL steps in one document (both sets are built outside the
per-step loop). Ran the two-step case: step A `{"status": "pending"}` (missing `id`), step B
`{"id": 123, "status": "pending"}` (`id` present but wrong type) → result:
`missing_required = {'id'}`, `offending = {'id'}`. Both output messages fire and both list `id`.
This is confusing wording (a reader sees `id` flagged as both "missing" and "offending" in one
denial), **not a correctness bug** — the write is still denied either way, so it does not gate
this delta. Flagging as a backlog note for whoever owns message wording, not a finding against
this fix.

## Empty `_missing_required` after a `required` error — unreachable

By construction of jsonschema's `required` validator: it emits an error object specifically when
it finds a property in `validator_value` absent from the instance — that is the trigger condition
for the error to exist at all. So whenever `_error.validator == "required"`, at least one key in
`_error.validator_value` is guaranteed absent from `_error.instance`, meaning
`{k for k in validator_value if k not in instance}` is guaranteed non-empty for that error.
**Unreachable** — this holds for any schema, not just this one; the `continue` can never swallow
a required error into a silent no-op given jsonschema's own error-generation semantics.

## Probe method

Throwaway `python3 -c`-equivalent heredoc script run under `env -u HARNESS_AGENT_TYPE`, working
in-process against the worktree's `run-state-schema.json` (read-only), no files written. Second
run replicated the actual `check-domain.sh` accumulation algorithm (two-step list, same variable
names) to observe the cross-step collision directly. No temp directory was needed since the
probes only read the schema and built strings/instances in memory — nothing was written to disk
under a temp root, so there was nothing to delete.

## Tree state

`git -C <worktree> status --porcelain` at the end of this run:

```
?? .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-backend-dev-2026-09-10-16-simplify-eng-reuse.md
?? .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-dev-ops-2026-09-10-16-simplify-eng-efficiency.md
```

Both entries are sibling agents' own receipts (concurrent runs), not mine. The three DEC-174
read-only files (`check-domain.sh`, `run-state-schema.json`, `test-check-domain.py`) are absent
from this output — untouched, byte-identical.
