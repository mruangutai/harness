# T-04 receipt — record the `ops` operation in SPEC §5.3 and as DEC-219

**PASS. The written contract now matches the committed tool.** Three doc files changed, all pure
additions (75 insertions, 0 deletions). The task's `verify:` block exits 0. No commit, HEAD unmoved
at `f7d221fa`.

## What was written

- **`.harness/harness/docs/SPEC.md` §5.3**, inserted after the existing union-merge refusal table
  (search: `**Replace and drop are a second subcommand`). Documents the `ops` invocation; that a
  target is keyed on section plus entry id with both required; that a replace rewrites in place so a
  replace-only proposal leaves section size and ordinals unchanged; that every op resolves against
  one base snapshot and each affected section is rebuilt in base order, making the result
  order-independent; that caps are checked once on the final state (pointed at `CAPS`/§5.2, numbers
  not restated); and the three new refusals `10 MISSING TARGET`, `11 AMBIGUOUS TARGET`,
  `12 MALFORMED OPS` beside `apply`'s 6, 7, 8 and 9. Nothing else in SPEC.md touched.
- **`.harness/harness/docs/DECISIONS.md`**, DEC-219 appended at EOF in the file's shape (`Chose:`,
  `Over:`, `Because:`, `Tradeoff accepted:`, `Record:`), refs DEC-66, DEC-95, DEC-145.
- **`.harness/harness/docs/DECISIONS-INDEX.md`**, regenerated with
  `python3 .claude/skills/harness/bin/gen-decisions-index.py` (which emitted `⚠ RULING PENDING`),
  then that half hand-written. Ruling carries the graded substring `replace and drop through the ops
  subcommand` contiguous and unmarked-up. Every other row byte-identical.

## Claims verified against the code, not the plan

Every SPEC claim was checked by **running** the committed
`.claude/skills/harness/bin/expertise-merge.py ops`, not only by reading it (scratch file under
`/tmp`, never a real Expertise file):

- `drop P-01` + `replace P-03` → `DROPPED P-01`, `REPLACED P-03`, exit 0; P-03 stayed in position
  after P-02 — replace does not move the entry.
- The same two ops in **reversed** order produced a byte-identical file — order-independence observed,
  not inferred.
- A replace-only proposal left section size and all three ordinals unchanged.
- `P-99` → `MISSING TARGET section=Patterns id=P-99`, **exit 10**.
- Two ops naming `P-01` → `AMBIGUOUS TARGET … reason=two ops in one proposal name this target`,
  **exit 11**.
- An op omitting `section` → `MALFORMED OPS op index=0: missing required key section`, **exit 12**;
  `op: merge` → **exit 12** with the replace-plus-drop instruction.

Exit **9** (destination refusal) is shared with `apply` via `require_expertise_destination`
(`expertise-merge.py:360-399`) and is now stated in SPEC, where it previously appeared nowhere.

## Baseline and gate

Ran the verify block **before** editing: all four SPEC tokens and the DEC-219 entry were absent, so
the gate was red and the work was not already landed. After the edits it exits 0, including
`tests/integration/test-gen-decisions-index.py` (14 tests, all `ok`). No other suite, linter or
formatter was run.

## Notes for the orchestrator

- Stage by exact pathspec: `.harness/harness/docs/SPEC.md`, `.harness/harness/docs/DECISIONS.md`,
  `.harness/harness/docs/DECISIONS-INDEX.md`, and this receipt. `BRIEF.md`, `plan.yaml`,
  `observations/harness-pm.md` and `notes/research-dec219-renumber.md` were already dirty at spawn
  and are **not mine**.
- Correction to the dispatch's stated rationale, recorded rather than silently absorbed: appending
  DEC-219 at EOF shifted **no** earlier row's `@line` anchor — the index diff is a single added line.
  Regeneration was still required, because the generator is what emits the new row at all.
- DEC-219 was free: DECISIONS.md ended at DEC-218 before this edit. DEC-216/217/218 untouched.
- No `verify:` clause tests the *substance* of the SPEC prose or of DEC-219 — the clauses check four
  literals in SPEC, four labels and three refs inside DEC-219, and one substring on the index row.
  The prose's truth rests on the tool runs recorded above and on a human reading the diff.
