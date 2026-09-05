# Cycle-4 panel amendment — both operator-selected findings closed by contract

**Both findings are closed by a contract in the plan and by a criterion that can fail.** PF-8de8…
(med) is answered by a new T-01 unit case whose globs are read from `harness.json` at test time and
judged by an imported predicate, graded by new **SC-19** under new **REQ-09**. PF-8da8… (low) is
answered by a one-fence note contract stated identically in T-03, T-04 and SC-12. The `panel:` block
is byte-unchanged (6061 bytes, verified against `HEAD:plan.yaml`); both approvals stay `pending`.

## Fix 1 — the guard-covers-detect invariant now has a mutant that reddens it

- **T-01 names the predicate.** `suite_layout.py` exposes `is_test_shaped(path)` as one module-level
  function; the repository-wide clause and the registry self-policing clause both call it, and
  `tests/unit/test-suite-layout.py` **imports** it. The two pattern tuples and `SOURCE_EXTENSIONS`
  stay module-level and exported, because T-03's census selects without the extension filter.
- **T-01 case 11** (new, additive, plants no file): read `test_kinds.unit.detect` from
  `.harness/harness.json` via the `repo_cfg` dict the file already loads, split on `|`.
- **Partition rule.** Final `/`-separated segment; in scope iff it contains `*` or `?` **and**
  `segment.strip("*?")` is non-empty. Today: `tests/unit/**` → `**` → strips to `""` → **out**;
  `*.test.*`, `*_test.*`, `test_*.py` → **in**. Three in, one out, and the count is asserted.
- **Synthesis rule.** Leading `**/` → fixed prefix `.harness/tools/` (outside `tests/`); every `*`
  and `?` in the final segment → the literal token `x`. Worked: `**/*.test.*` →
  `.harness/tools/x.test.x`; `**/*_test.*` → `.harness/tools/x_test.x`; `**/test_*.py` →
  `.harness/tools/test_x.py`.
- **Mutant.** Adding `**/*.spec.*` to `unit.detect` in `.harness/harness.json` **and** the template
  synthesises `.harness/tools/x.spec.x`, which matches no group of the vocabulary → case 11 RED,
  while the pre-existing template-equality assertion (`tests/unit/test-suite-layout.py:100-103`)
  stays GREEN because both files moved together. Remedy when it fires: widen the vocabulary, or
  record in DEC-213 why the new kind is out of scope — never delete the assertion.
- **Proved buildable before signature.** A faithful prototype of case 11 against the real
  `harness.json` prints GREEN today (3 in scope, 1 out, all three accepted) and RED under the mutant.

## Fix 2 — one fenced block, three sites, same words

`suite-census.py:24`'s `re.findall` collects **every** fence, so a second row-shaped block silently
merges into the note's row set and a correct measurement reports spurious MISSING/EXTRA.

- **T-03**: exactly one fenced block required; **zero** → `note carries no fenced block: {path}`,
  **two or more** → `note carries {n} fenced blocks, expected exactly 1: {path}`; both **exit 2**,
  reserved so it is distinguishable from the exit 1 of a row difference or a violation row. Refusing
  is the contract, explicitly *not* first-block-only. The unconditional row block and `TOTAL` line
  still print first.
- **T-04**: the pasted instrument block is the **only** fence in the note; everything else is prose
  with no fence, including quoted commands. Names the failure prevented.
- **SC-12**: the one-fence property is part of the observable — a second fence fails the criterion,
  not merely a command.
- **`verify:` blocks unchanged, deliberately.** T-03's verify runs without `--against`, so the note
  contract cannot reach it. T-04's verify runs with `--against` and already requires exit 0, which
  the new rule only narrows; a correct one-fence note still exits 0 and still emits the
  `probe-session-accessors.ts…documented-exception` non-vacuity anchor.

## Carry-through, item by item

| Checked | Result |
|---|---|
| D-01 `because` | amended: the at-least-as-wide claim now cites case 11's runtime-derived assertion and SC-19 instead of resting on a snapshot. Vocabulary itself unchanged |
| BRIEF "Verification gaps", `unit.detect` residual bullet | amended: closure is asserted, not assumed; points at SC-19 |
| T-05 DEC-213 bullets | amended: the agnostic bullet now instructs the documentor to state that the property is *enforced* by the unit assertion, citing it and not re-listing globs |
| SC-06 / T-01 case 1 fixture | **unchanged and safe** — case 11 builds no fixture and plants no file, so the one-element exact-equality list still holds |
| AC traceability table | SC-19 → REQ-09 → AC-01 added; all 19 SCs present, all eleven ACs (AC-01…AC-11) still covered |
| D-05 FEAT-44 exception, D-01 two-group vocabulary | untouched, as instructed |
| SC renumbering | none — SC-19 appended, so every existing reference (SC-06, SC-12, SC-18) stays valid |

## The five mechanical checks

1. `plan.yaml` loads; `status: plan`; `approval: {status: pending}` with no `rulings`; `panel:` block
   byte-identical to `HEAD` (6061 bytes).
2. `check-plan-routes.py` → `0 violation(s) across 1 plan(s)`, exit 0; all five tasks carry 11 keys.
3. `check-state.sh` → for this feature only `VIOLATION … BRIEF.md is NOT approved` plus the pending
   approval note; **no INV-35 line**.
4. 9 REQs, all traced; 19 SCs, each with exactly one `verify:` and every `automated` one naming a
   `test_kinds` kind (`unit`/`integration`); table rows match the SC set exactly; ACs 01–11 covered.
5. Greps: every fence mention in T-03/T-04/SC-12 now says exactly one, and the only plural-fence
   text left in either artifact is inside the frozen `panel:` block (the finding summary and the
   cross-reference note), which must stay verbatim. No site states the guard-covers-detect invariant
   as argued-only.

## Open

- The fresh panel still has to be transcribed after this amendment; this run deliberately left
  `panel:` untouched, so it currently records a cycle-4 record whose two open findings are now
  addressed in the plan text it grades.

## Follow-up correction — case 11's worked example for `**/test_*.py` (2026-09-04)

The amendment above shipped one wrong intermediate value. Case 11 states the partition rule as
`segment.strip("*?")` non-empty, but worked `**/test_*.py` as stripping to `"test_.py"` — that is
what `replace("*","").replace("?","")` yields. `str.strip(chars)` removes leading and trailing
characters only, and the segment starts with `t` and ends with `y`, so it is returned unchanged:
`"test_*.py".strip("*?") == "test_*.py"` (measured). The rule, the IN verdict and the other three
worked results were all correct; only the fourth intermediate was wrong, and as written the one
sentence described two different operations to the builder.

Amended via `plan-merge.py amend --key tasks --id T-01 --field intent --expect-sha256`, twice: the
correction, then a rewrap of the sentence that followed it on the same line. T-01's `intent:` now
reads:

> `**/test_*.py -> "test_*.py" -> strips to "test_*.py", unchanged, because str.strip removes only
> leading and trailing characters and this segment starts with "t" and ends with "y" -> IN. Three in
> scope, one out.`

Nothing else in the field moved — not the rule, the synthesis rule, the mutant paragraph, the
one-out count assertion, or the additive paragraph — and no other task, decision, `panel:`,
`approval:` or BRIEF text was touched. Re-checked: file loads, `status: plan`,
`approval: {status: pending}` with no `rulings`, `panel:` still byte-identical to HEAD at 6061
bytes; `check-plan-routes.py` → `0 violation(s) across 1 plan(s)`, exit 0, all five tasks at 11
keys; `check-state.sh` → no `INV-35` line anywhere and this feature's only VIOLATION is the
expected unsigned BRIEF.
