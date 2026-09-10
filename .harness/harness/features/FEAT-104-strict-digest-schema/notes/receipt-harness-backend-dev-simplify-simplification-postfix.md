BLUF: the fix delta (6126ac07→99035a9c) adds two SIMPLIFICATION-angle issues — a
ternary-plus-guard in `check-domain.sh` that restates a predicate already written twice in the
same file, and a comment in `validate-digest.py` that narrates the change instead of stating the
current rule; the test refactors in both files are genuine reductions, not relocations, and one
prior-pass residual (S2) already covers the cross-file duplication so I do not re-derive it.

## Findings

### F-S1 — `check-domain.sh:1760-1770` (hardlinked `.agents/skills/harness/bin/check-domain.sh`, same inode)
The new `_prior_is_strict`/`_version_decreased` pair restates a predicate this file already
computes twice: `_valid_version` at `:1594-1597` is `isinstance(v, int) and not isinstance(v, bool)
and v >= 2` — exactly `_prior_is_strict`'s shape, just for `_version` instead of `_prior_version`
— and the bad-type disjunction `not isinstance(_version, int) or isinstance(_version, bool)` at
`:1767-1768` is byte-for-byte the same test already written at `:1601`. The wrapping
`(X) if _prior_is_strict else False` is also strictly equivalent to `_prior_is_strict and (X)` —
Python's `and` short-circuits identically, so the ternary buys nothing.
**Cost:** the "what counts as a strict schema_version" rule is now spelled three times in one
~180-line span (`:1594-1597`, `:1601`, `:1761-1770`). A future change to the floor (e.g. raising it
to 3, or accepting a float) that updates two of the three sites and misses the third reopens
exactly the downgrade hole this commit closes, silently.
**Alternative (concrete):**
```python
def _is_strict_version(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 2

def _is_bad_version_type(v):
    return not isinstance(v, int) or isinstance(v, bool)
```
then `_valid_version = _is_strict_version(_version)`, the `:1601` `elif` becomes
`elif _is_bad_version_type(_version):`, and the new block becomes:
```python
_prior_is_strict = _is_strict_version(_prior_version)
_version_decreased = _prior_is_strict and (
    _is_bad_version_type(_version) or _version < _prior_version
)
```
**Anchor preserved, not trimmed:** the disjunct order inside `_version_decreased` — bad-type check
before `_version < _prior_version` — is load-bearing short-circuit, not incidental: if `_version`
is a string, `_version < _prior_version` raises `TypeError`, and only the `or`'s left-to-right
short-circuit stops it from ever being evaluated. My alternative keeps that order; do not reorder
it looking for further "simplification."
**Preserves every exercised case** (`tests/integration/test-check-domain.py:_floor_update_cases`,
99035a9c): `legacy` (prior schema_version 1 → `_is_strict_version` False → `_version_decreased`
False, matches "allows an existing version-1 update"); `downgrade` (prior 2, new 1 → strict True,
new is a valid non-bool int so the type disjunct is False, `1 < 2` True → `_version_decreased`
True, matches "refuses a version-2 checkpoint downgrade").

### F-S2 — `validate-digest.py:1404-1406`
The reworded comment reads "Generic `lead` **remains** an explicit compatibility persona for
callers that truly cannot recover the producing raw persona or contract era." — this narrates
continuity through the fix rather than stating today's rule, and it drops the one concrete anchor
the pre-fix comment carried (naming `check-state.sh` as the actual caller).
**Cost:** "remains" has no antecedent for a reader six months out with no memory of this commit,
and without the caller name the comment can no longer be checked against the real invariant F2
just introduced in `check-state.sh:1590-1596` (99035a9c) — `"lead"` is now provably used *only* for
the `schema_version 1` legacy branch, `_host` is used for `>= 2`. The comment states a looser,
unfalsifiable "callers that truly cannot recover" instead of that exact, checkable rule.
**Alternative (concrete):**
```python
# Generic `lead` is the compatibility persona used only for legacy
# (schema_version 1) run-state digests, whose producing raw persona
# cannot be recovered. Current returns and persisted run states
# (schema_version >= 2) carry harness-*-lead and are closed.
```
This states the present, version-gated fact directly instead of describing what changed. (The
adjacent message-text edit at `:1416` adding "Declare the field in
.claude/skills/harness/bin/validate-digest.py:" is the required F3 fix itself — SC-08's by-file
requirement — and is not flagged; it is a correct addition, not narration.)

## Test refactors — reduced, not relocated
- `test-check-state.py`: splitting the former inline `run_t07_cases()` (append-per-line) into
  `_step_cases()` / `_digest_cases()` / `_report()` is a genuine reduction — each function now has
  one concern, `_report()` is reused across both case lists instead of a duplicated print loop, and
  `_run_state`'s new optional `digest=` param is additive. No finding.
- `test-check-domain.py`: `_floor_update_case()` → `_floor_update_cases()` is a minimal rename plus
  one added case (`downgrade`), using `.extend` in place of `.append`. No finding.
- Per dispatch: I did not touch, weaken, or propose deleting any assertion in either file.

## Unchanged from the prior pass
No prior SIMPLIFICATION receipt exists for this feature (this is the first run of this angle), so
there is nothing of my own to reaffirm. A sibling in this same postfix run
(`receipt-harness-ai-dev-simplify-altitude-postfix.md`) already covers the cross-file duplication
of the same "strict version" idiom between `check-domain.sh` and `check-state.sh` under accepted
residual **S2** ("its fold-in already covers the newly-repeated type-check idiom too") — I do not
re-derive that cross-file angle here; F-S1 above is a narrower, same-file finding (three
restatements inside `check-domain.sh` alone) that S2's fold-in note does not itself spell out. A
bounded keyword scan of the broader pre-fix diff (`78e34f06`→`6126ac07`, the same four bin files)
turned up no further narrating-comment or redundant-conjunct instances beyond what S1/S2/S4 already
name in the prior receipts.

## Out-of-band
None. No correctness observations beyond the panel's own findings.

```yaml
VERDICT: PASS
DIGEST:
  headline: two SIMPLIFICATION findings in the fix delta (a same-file triple-restated version predicate in check-domain.sh, a narrating comment in validate-digest.py); both test refactors are genuine reductions; flag-only per DEC-174 NOBODY carve-out
  tests_added: 0
  suite: pass
  task: none
  blocked_on: none
  open_questions: []
  files_touched: ["/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-backend-dev-simplify-simplification-postfix.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/receipt-harness-backend-dev-simplify-simplification-postfix.md
```
