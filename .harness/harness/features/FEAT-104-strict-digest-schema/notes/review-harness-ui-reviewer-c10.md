# UI Review (Mode B) — FEAT-104-strict-digest-schema — panel c10, pin `790023f0`

## Scope — measured, not predicted

`git diff --name-only origin/main..790023f0` → **75 files** (census, `cat -n`). Extension sweep for
rendered-UI kinds (`html|css|scss|tsx|jsx|vue|svelte|less`) hits only
`notes/ship-review-plan-signature-c{1,2,3,4}.html` — confirmed generated (`grep -i 'do not edit'` →
hit) and **unchanged between 168f875f and 790023f0** (`git diff --stat` on `*.html` for that range
is empty). Same c7/c9-confirmed generated ship-review artifacts, not authored product UI.

**No `DESIGN.md` for this feature** — direct `find . -iname DESIGN.md` lists only
FEAT-19/FEAT-40/FEAT-11/FEAT-10 and the template; FEAT-104 has none.

**No rendered UI surface changed in this diff.** By the letter of Mode B's remit this scopes OUT.
Per the dispatch's explicit override, I scope **IN** on the adjacent non-rendered surface it names:
the denial/rejection text emitted by `check-domain.sh`, `check-state.sh`, `validate-digest.py` —
judged as an interface (what was refused / why / where the fix route is).

**Bookkeeping-commit claim, verified**: `git diff --stat 790023f0..3321bcdd` touches only 8 files,
all under `.harness/harness/features/FEAT-104-strict-digest-schema/` — claim holds.

**c9→c10 delta claim, verified then corrected**: `git diff --stat 168f875f..790023f0` touches 19
files. All but **two** are under the feature directory. The dispatch named one
(`tests/integration/test-check-domain.py`, confirmed exactly `+4/-2`, diff read verbatim) but missed
a second: `.harness/notes/analysis-feat104-run07-review-sha-recordfix.md` (+81/-0, new file). That
second file is a repo-level analysis note, not code, not a DESIGN doc, not a rendered surface — no
UI-review consequence, but the dispatch's "ONLY" claim was not quite accurate and I record that
rather than silently drop it.

## Verified test-check-domain.py delta (the reason this panel exists)

Read the diff directly: `_undeclared_cases()`'s version-2 case gained
`"run-state-schema.json" in strict.stderr` and `` "`evidence`" in strict.stderr ``, and its label
gained "and gives its route". Ran the suite live (`env -u HARNESS_AGENT_TYPE python3
tests/integration/test-check-domain.py`): **12/12 T-06 cases pass**, including this one. Read the
actual denial text the case is pinning (`check-domain.sh:1653-1659`):

> `check-domain: <VERB> — <path>: undeclared step key or evidence shape.`
> `  offending key(s): 'rogue_step_key'. A recovery field is declared in`
> `  .claude/skills/harness/bin/run-state-schema.json; a per-dispatch fact goes under`
> `` `  `evidence` with a lowercase identifier key and a scalar or scalar-array value.` ``

Reader test: **what** — names the key(s) (aggregated, comma-joined, not one-at-a-time — confirmed
against the 3-rogue-key case in `test-validate-digest.py:_t04_three_key_failures` too, same
one-message convention). **Why** — "undeclared step key or evidence shape". **Route** — the schema
file path, spelled out. All three present; the new assertions are not decorative, they pin real
text. Backtick-wrapping `` `evidence` `` in stderr renders as literal backtick characters in a
terminal (this file has no markdown renderer downstream) — but it is an **established convention in
this codebase**, not a one-off: the same file already backtick-quotes a literal token in the
schema_version-floor message (`` `write the literal `none`` ``, line ~1401 equivalent in
validate-digest.py) and dozens of comments follow the same style. Not a defect; noted as confirmed-
consistent, non-gating.

## New finding (mine) — HIGH, must_fix: empty/misleading text on the missing-required-field path

**Concrete failure scenario, reproduced directly** (own throwaway script against
`check_domain_support.fire`, no tracked file touched): a `schema_version: 2` run checkpoint with a
step missing `status` (or `id`, or both) — a plausible hand-edit or partial-template mistake, the
same class of slip CF-4 already covers for `schema_version` itself — is correctly refused (exit 2)
but the stderr reads:

```
check-domain: BLOCKED — <path>: undeclared step key or evidence shape.
  offending key(s): . A recovery field is declared in .claude/skills/harness/bin/run-state-schema.json; ...
```

`offending key(s): .` — **empty**. Worse: the header text is **wrong** for this case — nothing is
undeclared; a *required* key (`id`/`status`) is *absent*. Root cause, read directly in
`check-domain.sh:1645-1659`: the code only harvests `_offending` from a schema error's `_path[0]`,
but a jsonschema `required` violation reports its error at the *container's own* path (`[]`), so
`if _path:` never fires for it and nothing is added. Verified precisely with the schema loaded
standalone: `jsonschema.Draft202012Validator(step_schema).iter_errors({'status': 'pending'})` yields
`path: [] message: "'id' is a required property"` — **the informative text already exists inside
jsonschema's own error object** (`e.message`) and is discarded; only `e.path` is consulted.

Contrast with a type error on a *present* declared field (`id: 5` instead of a string): that DOES
populate `_offending` (`'id'`) correctly, because a type error's path is non-empty. Only the
*required-field-absent* shape is empty. **Untested**: `grep -n "required" tests/integration/
test-check-domain.py` → no hits; no case constructs a step missing `id`/`status`.

This directly fails the review's own reader test for "readable when the offending value is empty" —
it is not merely unreadable, it actively misdirects a reader (agent or human) toward hunting for an
extra key that isn't there, on exactly the seam (STEP-KEY/SC-08) this cycle exists to harden. Rated
**high**, not low like CF-4, because CF-4's message still carries a correct, actionable remedy
sentence around the one bad token; this one's diagnostic clause is empty and its stated reason is
false.

DEC-174: no fix applied; reasoned from code plus a live, disposable repro — not a source edit.

## Carried items, confirmed unchanged

- **F1** (schema_version downgrade refusal) — still CLOSED. Code present (`check-domain.sh:1766-
  1779`), test still green (`"schema_version floor refuses a version-2 checkpoint downgrade"` in the
  12/12 run above).
- **F3** (undeclared-digest-key message names file+symbols, three-key aggregation) — still CLOSED.
  Read `validate-digest.py:1411-1423` verbatim: unchanged since c9, still one message, all keys,
  file, and the three symbol names (`PASSTHROUGH`/`DOCUMENTED_OPTIONAL`/`SCHEMAS`). Test
  `_t04_three_key_failures` still present and asserting the aggregation.
- **F2** (generic `lead` exemption in `check-state.sh:1590`, `validate("lead", ...)`) — topology
  confirmed unchanged (same call site, same line). Disposition **DECLINED stands** — not
  relitigated. Residual carried as **Q9/Q3, unchanged**.
- **CF-1** (INV-16 bare-string interpolation) — not this role's lens; carried, unchanged, not
  re-raised.
- **CF-3** (cross-feature root commit) — carried, unchanged, not re-raised.
- **CF-4** (raw Python `None` in the schema_version-downgrade omitted-on-update edge) — **still
  present, unchanged**. Reproduced directly at this pin: an existing v2 checkpoint updated with
  `schema_version` omitted entirely still renders `"the proposed write declares None."` at
  `check-domain.sh:1775` (`f"...declares {_version!r}."` with `_version = None`).
  `grep -n required tests/integration/test-check-domain.py` confirms T-06's downgrade case only
  covers declared `2→1`, no omitted-on-update case. **Carried, unchanged** — not re-raised as new.
- **Q7** (duplicate strict-version predicate spellings) — not independently re-derived this cycle;
  no new evidence either way, carried as-is.

## Accessibility / theme parity

Not applicable. No rendered surface in this diff; the only user-facing text is batch/CLI stderr,
which carries no colour-only state encoding and has no light/dark variant to compare (repo
Expertise G-02). This is a confirmed not-applicable, not a skipped section.

## Verdict rationale

One new, independently reproduced, concrete defect on the exact interface this cycle exists to
harden (empty + falsely-labelled denial text on a missing-required-field step) — rated high because
it leaves the reader with zero actionable information and an actively wrong stated reason, not
merely an unpolished one. All carried items re-verified at this pin rather than assumed: F1/F3 still
closed, F2's decline stands untouched, CF-4 still present and still low. The c9→c10 test delta the
panel exists to close (`run-state-schema.json` + backticked `` `evidence` ``) does close a real gap:
the message genuinely gives the route it now asserts having, for the case it actually covers.

```yaml
VERDICT: FAIL
DIGEST:
  headline: New HIGH finding — check-domain.sh's step-schema denial goes empty and mislabels itself ("undeclared step key") when the real cause is a missing required field (id/status), discarding jsonschema's own informative message; all c9 carried items (F1/F3 closed, F2 decline stands, CF-4 low unchanged) reverified directly at this pin.
  mode: B
  in_scope: true
  severity_max: high
  findings: 2
  must_fix: ["check-domain.sh's step-schema denial ('undeclared step key or evidence shape.') renders 'offending key(s): .' (empty) and states the wrong reason when a step is missing a required field (id/status) instead of carrying an undeclared one — jsonschema's own error already names the missing field ('id' is a required property) but only e.path (empty for `required` violations) is consulted, not e.message; reproduced directly, untested by T-06."]
  contract_violations:
    - { path: ".claude/skills/harness/bin/check-domain.sh:1645-1659", actual: "offending key(s): . [empty] with header 'undeclared step key or evidence shape.'", specified: "reader test in dispatch: a rejection must tell the reader what was refused, why, and where the route is — even when the offending value is empty" }
  a11y: ["not applicable — batch/CLI stderr text only, no colour-only encoding, no rendered surface (repo Expertise G-02)"]
  open_questions:
    - { id: Q1, question: "Should check-domain.sh's required-field branch fall back to jsonschema's e.message (or e.validator=='required' plus e.validator_value) when e.path is empty, so a missing id/status names itself the way a type error on a present field already does? DEC-174 means I cannot apply this myself.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-104-strict-digest-schema/.harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-ui-reviewer-c10.md
```
