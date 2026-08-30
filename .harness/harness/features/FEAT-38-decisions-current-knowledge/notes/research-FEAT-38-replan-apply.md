# FEAT-38 replan-apply — the amendment after both FAIL squads

**All four MUST-FIX items are applied to `plan.yaml` and `BRIEF.md`; the amendment is ready for the
operator's one fresh signature.** Task count 29 → 28. **T-26 is retired; its number is not reused and
nothing references it.** `check-plan-routes.py` exits 0, 0 violations (the two `DEVIATION` lines are
T-22/T-23, pre-existing and declared in their `execution_reason`). Both approval fragments are
byte-untouched.

## What each MF became

- **MF-1 (removal order took the suite to exit 2).** T-24 and T-26 merged into one
  `harness-backend-dev` task — **T-24 survives**, doing the `INTEGRATION_SCRIPTS` removal and both
  `git rm`s in one step, `change_type: config → logic`, `traces: [REQ-10, SC-14]`,
  `depends_on: [T-19, T-27]`. `T-25.depends_on: [T-24]` unchanged (no-op, as pre-worked);
  `T-29.depends_on: [T-26] → [T-24]`. The dependency algebra as handed to me was correct and is
  applied unchanged. T-24's and T-25's intents now name the **MISCONFIGURED file-presence detector at
  `run-unit-tests.sh:60-74`** — re-anchored: the loop is `:61-74`, the block comment opens at `:60`,
  not `:65-79`. The KIND-DRIFT asymmetry argument survives, **derived once in T-24** with T-25
  pointing at it by id (F-2).
- **MF-2 (index row falsified).** T-28 gains intent item 5 — hand-rewrite DEC-205's ruling in
  `DECISIONS-INDEX.md` — a corrected `do not hand-edit` sentence scoping the prohibition to the
  generated left side of a row (contract at `gen-decisions-index.py:12-14`, `ruling = prose` from the
  existing rows at `:203-213`), an explicit edit ORDER (edits 1-4 → regenerate → edit 5 → diff again,
  so the diff proves the hand-written ruling is idempotent), and three new verify clauses: the
  DEC-205 row must exist, must match neither `claim` nor `two mechanical`, and must positively match
  `one mechanical check`. `traces: [REQ-05, REQ-10, SC-16]` (ALT-6).
- **MF-3 (T-29 unfinishable).** All five sub-fixes: Q2 rewritten as a **provenance** question
  covering "any input the script does not control — a file it opens, or stdin"; the path-argument
  exclusion carved down to paths **the script itself constructs**; the decisive case named
  (`.harness/harness.json`'s `test_kinds.<kind>.cmd`) with the note required to show it was caught
  (verify greps `test_kinds`); third verdict **`NO-EXECUTION`** in the rubric and in the verify
  alternation, with a strictness order; the row regex now requires a non-empty third column; the
  closing `## TEXT-DERIVED-ARGV` section is asserted to exist and to state a disposition.
- **MF-4 (T-19 had no positive control).** The `48bbe7e` control folded in, mirroring T-20/T-21, with
  a paragraph saying what it prevents.

## Proof, not reasoning

- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0. `yaml.safe_load` clean.
- **New positive clauses discriminate.** On the pre-change tree the three DEC-205 count sentences and
  the index ruling are all **RED** (exit 1 each) and the index staleness clause **fires**; on a
  corrected `/tmp` fixture carrying exactly the strings T-28's intent mandates, every T-28 clause is
  GREEN. T-29's row regex accepts a good row and a `NO-EXECUTION` row, rejects an empty rationale and
  an unknown verdict.
- **The cheap verify pair is real** (EFF-01/EFF-02): `--check-kinds` + `test-check-decision-anchors.py`
  measured 0.52 s here, both exit 0, against the 157.7 s `--kind integration` it replaces in T-19 and
  T-24. T-24's first clause is correctly red now (`claims still registered`).
- Approval: `plan.yaml:6-9` unchanged (no diff hunk below new line 68); `## Approval` in `BRIEF.md`
  now at `:376-380`, bytes unchanged — no `approval:`/`approved_by`/`approved-by`/`## Approval` line
  appears in `git diff -U0`. The only changed `status:` lines are task-level `status: pending`.

## BRIEF edits the operator meets

- **REQ-10 conditioned, deliberately, and the conditioning is written where REQ-10 lives.** Met by the
  class being swept and its members named with a recommendation — **not** by the text-derived set
  being empty. Remediating any site beyond `check-decision-claims.py` is explicitly OUT of scope and
  becomes a backlog row at ship. A non-empty result is a finding this feature delivers.
- **SC-16 widened** to all three counting sentences (the third, `the two that are in`, was only
  checked negatively — ui F2) **plus the `DECISIONS-INDEX.md` DEC-205 ruling**, and it now names
  deletion-instead-of-restatement as a caught failure.
- **SC-17 aligned** with the three-verdict rubric, the non-empty rationale, stdin, and the
  config-stored-command case — it still said "fixed-literal or text-derived" only.

## Open

Nothing blocking. The one judgement a later reader may want to revisit: T-24's blast-radius sweep is
still unscoped, so the code lane waits on the documentor lane (T-27) — recorded in both intents as
deliberate, with the alternative (scoping the sweep) and its cost stated.
