# Receipt — harness-backend-dev — simplify c10 — SIMPLIFICATION angle

## BLUF
The required/error split at `check-domain.sh:1645-1683` is close to the right shape and I am
**not** recommending any structural change to the two-set/two-message design. One real, cheap
finding: the comment at line 1646-1647 describes only half of what the loop now does and should
be rewritten (concrete replacement given below). The `isinstance(_error.instance, dict)` guard at
line 1651 is empirically dead code given the current schema, but I am **not** recommending its
removal — it is load-bearing defensive clarity, not complexity added by this diff, and removing it
trades a one-line safety net for zero measurable simplification. No gating defect.

## 1. Is the `isinstance(_error.instance, dict)` guard load-bearing?

**Probe** (throwaway `python3 -c` via heredoc in a `tempfile.mkdtemp()` dir, cleaned up with
`shutil.rmtree` from inside the same Python process — no bash `rm` used, per DEC-174/write-guard):
schema `{"required": ["id","status"], "properties": {...}}`, `jsonschema` 4.26.0,
`Draft202012Validator.iter_errors`:

```
--- instance: list [] ---
count: 0
--- instance: string 'x' ---
count: 0
--- instance: dict missing both id and status ---
validator= required  validator_value= ['id', 'status']  path= []  message= 'id' is a required property
validator= required  validator_value= ['id', 'status']  path= []  message= 'status' is a required property
count: 2
```

Confirmed: jsonschema's own `required` validator emits **zero** errors when the instance is not a
mapping — it returns early internally, exactly as the dispatch predicted. I also checked
`run-state-schema.json`'s step schema (`.claude/skills/harness/bin/run-state-schema.json`,
`properties.steps.items`): the only `"required"` keyword anywhere in the step schema is the
top-level one (`["id", "status"]`); there is no nested object with its own `required` reachable
under a non-dict sub-instance. So `_error.instance` for a `validator == "required"` error is always
exactly the top-level `_step` object being validated at `check-domain.sh:1633`
(`_validator.iter_errors(_step)`), and that call always receives `_step` untouched by the
`isinstance(_step, dict)` branch at line 1634 (which only affects `_offending`, `continue`s past
the `_declared`/`evidence` checks, but does **not** skip the `iter_errors` call already made on
line 1633 for that same `_step`).

**Conclusion: the guard can never be `False` when `_error.validator == "required"`.** It is dead
weight by the strict "can this branch execute" test. I am not recommending removing it: the
line costs one `isinstance` call per required-error (bounded by step count, trivial), it makes the
`.update(...)` below manifestly safe against a `TypeError: argument of type 'NoneType' is not
iterable`-class failure if the schema ever grows a nested `required` under a differently-typed
subschema, and a future schema edit reintroducing that possibility would silently re-arm it. This
is the "cheap defensive clarity a reader benefits from" case the dispatch names, not complexity the
delta introduced — I am not flagging it as a finding.

## 2. Is `validator_value` minus present keys the right recovery, or does jsonschema expose it more directly?

**Same probe, instance `{}`**: jsonschema emits **one `required` error per missing key** (2 errors
for 2 missing keys, `count: 2` above), each carrying the **full** `validator_value` (`['id',
'status']`) and `path: []` (empty — the required error is anchored at the *object*, not at the
missing field). The only place the single missing key is expressed per-error is inside
`_error.message` (`"'id' is a required property"`, `"'status' is a required property"`) — free text
that is fragile to parse and versioned by jsonschema's message strings, not its data model.

Given that, `set(_error.validator_value) - set(_error.instance)` (`check-domain.sh:1652-1655`) is
the **right** choice: it reads the missing-key set off structured data (`validator_value`, a plain
list; `instance`, the dict itself) with no string parsing, and it is naturally idempotent — every
`required` error on the same instance recomputes the identical full missing-set, so re-running it
once per error (there are exactly as many `required` errors as missing keys) just re-derives the
same `frozenset`-equivalent result into a `set.update`, which is a no-op after the first. That
redundant-but-idempotent recomputation is real (backlog note below) but not a correctness problem
and not worth restructuring for.

**Backlog note (not a finding, not gating):** the loop recomputes the full missing-key diff once
per missing-required-error rather than once per instance. At current step counts (dozens, not
thousands) this is unmeasurable; a lead could special-case "first required error per instance" to
save the redundant recompute, but doing so adds a dict keyed by `id(_error.instance)` or similar —
more code to save work that is already O(missing-keys) and already idempotent. Not recommended.

## 3. Does the two-set, two-conditional-message structure read as the simplest correct shape?

**Yes — recommend keeping it as-is.** The two facts are independently true and can co-occur on the
*same* step (e.g. a step missing `status` while also carrying an undeclared `notes` key): the
`_missing_required` and `_offending` sets are populated by genuinely disjoint code paths (the
`continue` at line 1656 is exactly what keeps a `required` error from *also* falling into
`_offending` via `_path[0]`, since `path` is `[]` for a required error and would previously have
silently produced `_offending.add("")`  → the empty-list PF-C10-01 bug). Collapsing to "a single
set of `(reason, key)` pairs grouped at print time" would still need two grouped output blocks to
answer "which keys, and why" distinctly for the reader, so it buys nothing over two named sets — it
only defers the branching from build-time to print-time. Collapsing to "one message whose label
switches" is worse: it cannot represent the both-missing-and-undeclared case without picking one
label and hiding the other category's keys, which is precisely the class of bug this diff exists to
fix (a message reporting the wrong reason, or none). The existing file already uses sequential
independent `_head()`/`out.append()` blocks for multiple simultaneously-true denial reasons
elsewhere (e.g. `schema_version` block at 1608-1614 is one of several sequential checks appended to
`out`), so two conditional messages here matches established file idiom, not a stylistic
inconsistency the change introduced.

## 4. Comment accuracy at ~1646-1647

`check-domain.sh:1646-1647`:
> `# Type/value failures on declared fields may not be captured by the vocabulary comparisons
> above; name their nearest field.`

This is **still true but now incomplete**. It describes only the `_offending`/`_path[0]` branch
(lines 1657-1659); it says nothing about the new `_missing_required` diversion (lines 1650-1656),
which is the majority of what changed in this delta and the actual fix for PF-C10-01. A reader
hitting this comment first, before line 1650's `if`, would not learn that required-property errors
are handled separately at all.

**Recommended fix (rank 1 of 1 — the only fix I'm recommending from this angle), described as a
prose diff, NEVER applied (DEC-174):**

At `check-domain.sh:1646-1647`, replace the two-line comment

```
                    # Type/value failures on declared fields may not be captured by
                    # the vocabulary comparisons above; name their nearest field.
```

with:

```
                    # A required-property error is anchored at the object itself (empty
                    # path), so its missing field names are recovered from validator_value
                    # instead, below. Every other type/value failure on a declared field may
                    # not be captured by the vocabulary comparisons above; name its nearest
                    # field via the error path.
```

This is a comment-only rewrite (no behavior change), states what both branches of the now-two-way
split actually do, and explains *why* the required case needs the `validator_value` recovery
(the empty `path`) rather than just asserting it. Cost of not fixing: low (a maintainer reading only
the comment under-estimates what the loop does, until they read the `if` on the next line), so this
is worth a one-line diff but not gating.

## Verdict rationale
No correctness defect within the SIMPLIFICATION angle's scope. The delta does not add unnecessary
complexity: the guard is cheap and defensible, the set-diff recovery is the right call against the
empirical jsonschema behavior, and the two-message structure is required by the two independently-
true facts it reports, not accidental duplication.

## git status --porcelain (observed at end of run)
```
?? .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-backend-dev-2026-09-10-16-simplify-eng-reuse.md
```
Only an untracked sibling reader's receipt (reuse angle, concurrent run) is present. No file under
the tracked delta (`check-domain.sh`, `run-state-schema.json`, `test-check-domain.py`) shows any
change; my own probes ran entirely inside `tempfile.mkdtemp()` and were cleaned up with
`shutil.rmtree` from inside the same Python process before this receipt was written.
