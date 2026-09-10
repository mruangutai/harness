# Receipt — harness-dev-ops — ALTITUDE angle + test-delta grade — FEAT-104 cycle 10

## BLUF

The fix is correct and safe to ship as-is: it removes the specific PF-C10-01 false head for
`required` violations. But it fixes an **instance**, not the **class** — it special-cases the
`required` validator by name rather than the structural property that actually caused the bug
(an empty `error.path` on an object-level violation). Today's schema only uses `required` and
`additionalProperties`/`propertyNames`, so the residual gap is currently unreachable; it becomes
live the day someone adds `minProperties`, `maxProperties`, or `dependentRequired` to
`run-state-schema.json`, at which point that violation would produce **no denial line at all**
(silently swallowed, not even under the old false head). Test delta: the new assertions
genuinely witness the fix — verified empirically against the exact pre-fix message text, not
executed. `"status"` is a loose but non-incidental substring here; recommend tightening to
`"'status'"` as a backlog note, not blocking.

**VERDICT: PASS.**

## Altitude — four questions

**Q1. Right layer for the distinction?**
Yes, `required` vs. "undeclared/shape" genuinely differ to the human reading the denial —
"supply this" vs. "remove/reshape that" are different remediation actions, not an artifact of
jsonschema's naming. Detecting the difference via `_error.validator == "required"` is also the
correct *mechanism* (there is no other way to learn an error came from the `required` keyword).
But the branch condition is checking the *keyword name*, not the *structural cause* of the bug —
which was really "this error's `.path` is empty, so `_path[0]` can't identify an offending key."
`minProperties`, `maxProperties`, and `dependentRequired` errors also report against the object
with an empty `.path` (dependentRequired in Draft 2020-12 keys off the *dependency's* property
which is present on the instance, and the failing dependent property is not surfaced via `.path`
either). Under the current code, any of those three would land in neither `_missing_required` nor
`_offending` — `_schema_errors` is truthy, the whole `if _schema_errors:` block runs, but *neither*
inner `if` fires, so **no line is appended for that violation at all**: not even the old false
head, just silence, while other, unrelated `_offending`/`_missing_required` content (if any) from
the same write would still print. `patternProperties` is fine — jsonschema reports a real
`.path` for it. Answer: **this removed one instance of the bug class, not the class itself.**
→ `briefing-row`

**Q2. One authoritative statement, or several that can drift?**
The delta's *new* message text is well-behaved: `"Required step fields are declared in
run-state-schema.json; supply each required field."` names the file and stops — it does not
restate the schema's `required` list or field semantics, so it cannot drift from the schema.
The pre-existing `_offending` message (unchanged by this delta, just re-indented under a new
`if`) is the one with a duplication risk: it restates the evidence-key convention in prose
(`"a per-dispatch fact goes under \`evidence\` with a lowercase identifier key and a scalar or
scalar-array value"`) that paraphrases `run-state-schema.json`'s own `evidence.description`
(`"matchable, per-dispatch facts that do not belong in the closed step vocabulary"`) and its
`propertyNames.pattern` (`^[a-z][a-z0-9_]*$`) — two independently-maintained English descriptions
of the same regex. That duplication predates this delta and this delta made no line of it worse
(only moved it inside `if _offending:`), so it is not a defect *of this delta*. → `leave` (for
this delta; the pre-existing duplication is a legitimate backlog item, not gating here per
DEC-174's scope boundary — it is outside the two-file diff's actual changes).

**Q3. Special case bolted on, or correct home?**
Bolted on, and Q1 is why: the `continue` arm reads "if this specific known-bad validator name,
do X" rather than restructuring the loop around the real invariant ("an error with no path needs
a different bucket than a vocabulary error"). The loop was uniform before (`path -> offending`)
and is now a two-tier dispatch keyed on keyword identity, with a silent third case (empty path,
not `required`) nobody wrote. It is the right *file* and right *function* — shape_problems is
exactly where JSON-Schema errors get turned into remediation prose — but the right *shape* for the
branch is "does this error have a path" first, "is it `required`" second (for message wording
only), not "is it `required`" as the sole gate. → `briefing-row`

**Q4. Verdict on the class-vs-instance question, explicitly:** the fix removed the one shipped
case of the bug (missing-required steps), and left a same-shaped gap for any future
non-`required`, empty-path schema keyword. Not gating today (no such keyword exists in the
schema yet); worth a line in the next simplify/eng briefing.

## Recommended fix (one, prose diff, NOT applied)

In `check-domain.sh` `shape_problems`, ~1648-1659, replace the validator-name dispatch with a
path-first dispatch so a *future* empty-path keyword degrades to a generic message instead of
silence:

```
for _error in _schema_errors:
    _path = list(_error.path)
    if _path:
        _offending.add(str(_path[0]))
        continue
    if _error.validator == "required" and isinstance(_error.instance, dict):
        _missing_required.update(
            str(_key) for _key in _error.validator_value
            if _key not in _error.instance
        )
        continue
    _object_level.append(_error.message)
```
with `_object_level = []` initialized alongside `_missing_required`, and a third `if
_object_level:` block after the existing two, appending a head such as `"step does not conform to
schema."` plus `"; ".join(_object_level)`. This makes the *class* — not just the `required`
instance — safe, at the cost of a slightly less specific message for whatever keyword lands in
that new bucket (acceptable: it still names the failure instead of staying silent).

### Backlog notes (not the recommended fix, not blocking)
- Tighten the test's `"status" in missing.stderr` to `"'status'" in missing.stderr` to pin the
  `repr()`-quoted form the code actually emits, matching G-arguments elsewhere in this repo about
  precise substring assertions. See test-delta grade below for why it is not required.
- Q2's pre-existing evidence-convention prose duplication (schema `description`/`propertyNames`
  vs. check-domain.sh's remedy sentence) — real, but outside this delta's changed lines.

## Test-delta grade

`_undeclared_cases()`'s new `missing` case (`tests/integration/test-check-domain.py:82-95`):

- **Pins behaviour, not wording, on the substantive question.** `"missing required step key"` is
  the literal head text the new code emits and is the minimum string that discriminates the new
  head from the old one (`"undeclared step key or evidence shape."`) — not over-specified; a
  harmless rephrase of the *sentence* under that head would not need to change this literal since
  the assertion targets only the head, which is intentionally part of the observable contract
  (DEC-174 already settles that the *existence* of the distinct heads is not up for
  re-litigation).
- **`"status" in missing.stderr` is loose but not incidental here.** Read literally
  (`check-domain.sh:1660-1668`): the new message is `f"  missing key(s): {_missing_names}. ..."`
  where `_missing_names = ", ".join(repr(key) for key in sorted(_missing_required))`. For this
  fixture `_missing_required == {"status"}`, so `_missing_names == "'status'"` (single-quoted via
  `repr`) — the substring `status` is embedded in `'status'`, so the assertion passes, but it
  would pass identically if the code emitted `"'status_x'"` or any other string containing the six
  letters `s-t-a-t-u-s` in sequence. I traced every other place `"status"` could appear in this
  script's output for this exact fixture (grep across the whole file) and found none reachable
  from this code path: the top-level `status: running` line the fixture also carries is never
  validated by this jsonschema branch (only `steps[].items` is validated; top-level fields are a
  separate, unrelated `ALLOWED` set check at line ~1537 that this fixture does not trip), and the
  plan.yaml station-vocabulary code that also prints `"status"` (line ~1382-1394) only fires for
  `plan.yaml`, not `state.yaml`, so it cannot contribute stray `"status"` text to this stderr. So
  for *this* fixture the assertion is not incidental in practice, only in principle. Exact prose
  diff to tighten it: change `and "status" in missing.stderr` to
  `and "'status'" in missing.stderr` at test-check-domain.py:95.
- **Would this test pass against the reverted fix? No — traced from literal strings, not
  executed** (DEC-174: file is read-only; reasoning from `git show 790023f0:...check-domain.sh`
  lines 1630-1658, not invoked). Under the pre-fix code, the single unconditional block computes
  `_offending` from `_path = list(_error.path)`; for a `required` error `error.path` is empty
  (jsonschema reports `required` failures against the *containing* object, not a child key), so
  `if _path:` never fires and `_offending` stays empty (no other schema violation exists in this
  fixture — only `status` is missing, `additionalProperties`/`propertyNames` are untouched). The
  pre-fix message is therefore exactly `_head("undeclared step key or evidence shape.")` +
  `"  offending key(s): . A recovery field is declared in ..."` (empty `_names` join — this is
  literally the PF-C10-01 bug as described in the dispatch). Neither the literal substring
  `"missing required step key"` nor the literal substring `"status"` appears anywhere in that
  string. **Both assertions would be `False`, so `missing.returncode == 2 and False and False`
  evaluates `False`, and the case tuple's second element is `False` — the test harness's assertion
  on that tuple would fail, correctly reddening against the reverted code.** The test does witness
  the fix.

**Grade: PASS.** No gating defect in the test delta.

## Git status (observed, verbatim)

Ran `git -C <worktree> status --porcelain` at the end of this run:

```
?? .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-backend-dev-2026-09-10-16-simplify-eng-reuse.md
?? .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-backend-dev-2026-09-10-16-simplify-eng-simplification.md
?? .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-data-engineer-2026-09-10-16-simplify-eng-enumeration.md
?? .harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-dev-ops-2026-09-10-16-simplify-eng-efficiency.md
```

All four are untracked sibling receipts from concurrent parallel readers (this run's own prior
receipt and three siblings' outputs); none of them are the two protected delta files. The
tree is otherwise clean — no tracked file, and none of the three DEC-174 protected paths
(`check-domain.sh`, `run-state-schema.json`, `test-check-domain.py`), show any modification. I
wrote no probe files and created no `mktemp -d` scratch root — all reasoning above is static,
from the literal message-construction code and `git show`, per the dispatch's explicit
allowance to reason from literal strings instead of invoking the fixture.
