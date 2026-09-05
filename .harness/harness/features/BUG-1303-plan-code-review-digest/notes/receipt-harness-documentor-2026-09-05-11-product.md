# Receipt — harness-documentor — BUG-1303 T-04

**BLUF.** The contract-divergence rule is recorded as **DEC-216**, appended at the end of
`.harness/harness/docs/DECISIONS.md` and indexed with a hand-written ruling. T-04's `verify:`,
run verbatim from the worktree root, exited **0**.

## Number derivation

Re-derived at edit time, not taken from the dispatch's hint. `grep -n "^## DEC-" .harness/harness/docs/DECISIONS.md`
in this worktree topped out at `DEC-215`; `git show <ref>:.harness/harness/docs/DECISIONS.md` across
every local and remote ref also topped out at 215 on `origin/main` and every sibling feature branch.
(`refs/heads/feat/FEAT-46-decision-standard` reaches 548 under a different, unmerged numbering scheme —
`git merge-base --is-ancestor` reports it not an ancestor of `origin/main`, so it does not bound the
sequence.) Allocated **max+1 = DEC-216**.

## Anchors

- Entry: `.harness/harness/docs/DECISIONS.md:6792` — `## DEC-216 — A persona's documented output block
  is an enforced half of the digest contract`. Body runs to `:6815`; **24 lines**, under the
  twenty-five-line ceiling. Three bold Chose-and-why runs, matching the file's existing voice.
- Index row: `.harness/harness/docs/DECISIONS-INDEX.md:216`. Everything left of ` :: ` is the
  generator's own (`[digest,plan,tests] refs: DEC-174 DEC-207 DEC-209 @6792`); the ruling right of
  the separator is hand-written and carries the exact phrase `documented output block`.

## Intent coverage — every enumerated bullet

Origin BUG-1303 measured at `c369fb1f` (reviewer persona + `.omp` twin documented no `code_grade`,
plan-phase reviewer settled as failed) · why doctrine alone was refused (silent on both sides, the
pointer just dies) · direction of the check (required-by-schema must be documented; extra documented
fields stay legal, because `SCHEMAS` holds only enum-and-typed required fields while `headline`,
`files_touched`, `open_questions` are required elsewhere in `validate()`) · block-not-whole-file scope
(seven of sixteen personas share two files) · what it does not change (DEC-207 unamended, SEC-01
`review_sha` binding, DEC-209 recomputation, INV-6, `validate-digest.py` unedited) · refs DEC-207,
DEC-209, DEC-174. The entry **names** `required_by_persona` in `run_documented_contract_cases`
(`tests/integration/test-validate-digest.py`) as the hand-written mirror of `validate()`'s inline
per-persona extension (`code_grade`, `reviewed`); that site is live at
`tests/integration/test-validate-digest.py:383-387`, so the entry's "checked mechanically" claim is
true as written (T-01 has landed).

## Verification

- T-04 `verify:` verbatim — `grep -qF "documented output block" … && gen-decisions-index.py --stdout | diff -q - …`
  → **exit 0**. The index is byte-identical to a fresh regeneration.
- `gen-decisions-index.py` (file write) → exit 0; zero `RULING PENDING` rows.
- `python3 tests/integration/test-gen-decisions-index.py` → **exit 0**, all cases `ok` (this is the only
  place the index's ruling length budget is asserted; the verify clause does not cover it).

## Tree state — no commit made

`git status --porcelain` shows eight modified files. **Mine, and only these two:**
`.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/DECISIONS-INDEX.md` (plus this receipt,
untracked-in-listing under the feature dir). The other six —
`.claude/agents/harness-code-reviewer.md`, `.omp/agents/harness-code-reviewer.md`,
`.claude/skills/harness-code-review/SKILL.md`, `tests/integration/test-validate-digest.py`,
and the feature's `plan.yaml` / `feature.json` — belong to concurrent lanes T-01..T-03 and were
neither read-modified nor re-anchored by this run. HEAD was not moved; nothing was staged or committed.

## Open

- None blocking. Advisory: the entry appends at end-of-file, so no `@line` anchor above it moved and no
  other document needed re-anchoring.
