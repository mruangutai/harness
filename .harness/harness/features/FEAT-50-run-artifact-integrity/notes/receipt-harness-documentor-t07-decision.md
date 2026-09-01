# Receipt — harness-documentor — FEAT-50 T-07

**DEC-208 is the number, and the heading names all five rulings, not three.** One entry appended to
`.harness/harness/docs/DECISIONS.md` (69 lines, heading included), one row written in
`.harness/harness/docs/DECISIONS-INDEX.md`. T-07's verify block prints `OK DEC-208`.

## The number

208. Resolved at execution time against the file, not from the plan. Ceiling checked in every place a
concurrent documentor could have consumed it: this worktree, the main checkout's working tree, `main`,
every local and remote branch, and all nine sibling worktrees' working copies. Highest live heading was
`DEC-207` everywhere; nothing else had claimed 208.

## The heading deviates from T-07's prescribed text, deliberately

T-07 prescribes a heading naming three surfaces; open finding `PF-cec83ae44219d710691dfae021622ce1`
records that as a defect — the Bash-route ruling and the lead-digest-location ruling would be
unsearchable in the index. The dispatch's acceptance criterion requires all five named. Shipped
heading keeps T-07's graded prefix verbatim (`A run's own record is enforced, not expected:`) and
extends the clause list, so both this task's verify and SC-14 still match by heading text. The finding
is thereby cleared for `T-07` and `DEC-208`; `SC-14` and `D-08` still read "three rules" in
`BRIEF.md`/`plan.yaml`, which are not mine to edit.

## Every claim in the entry was measured against the code, not transcribed

| Ruling | Anchor cited | What was read |
|---|---|---|
| 1 presence | `validate-digest.py:1602-1614` | `_ABSENT` sentinel; absent/null → stderr + `return 0`, blank string → `return 2` |
| 2 checkout binding | `feature-worktree.py:236-248` | the FEAT-32 short-form/long-form measurement and the refuse-on-two-candidates comment |
| 3 digest preservation | `check-domain.sh:1139-1151` | `prior.strip() and not content.startswith(prior)`, guard commented Write/PRE-only |
| 4 route completeness | `bash-write-guard.sh:711-722`, `check-domain.sh:727-741` | both call `harness_boundary.worktree_for_feature` and both catch `AmbiguousWorktree` |
| 5 digest location | `validate-digest.py:1413-1424` | `base = inflight_registry.feature_root(owner_root, feature)`, falling back to `_root_or_none()` |

All eleven cited decisions (`DEC-95 122 127 143 151 154 156 174 180 191 193`) resolve to exactly one
live heading each.

## Verification, task-local only

- T-07's verify block: `OK DEC-208`. It **discriminates** — before the edit the heading grep returned
  nothing, so this clause was red on the baseline tree and is green now.
- `check-decision-anchors.py`: `examined 27 anchor(s), 0 failed`. All six new anchors confirmed
  extracted and individually clean; the same checker returns `line past end of file` for a
  deliberately bogus line on one of them, so the pass is not vacuous.
- `test-gen-decisions-index.py`: 11/11 ok, which is where the index's 260-line budget, the 30-word
  ruling cap and the `RULING PENDING` sentinel are actually asserted. Row is 29 words; index is 208
  lines.
- Diff is exactly two hunks: `DECISIONS-INDEX.md @@ -207,0 +208 @@` and
  `DECISIONS.md @@ -6361,0 +6362,70 @@`. Nothing before the new entry moved, so every existing
  `@line` anchor in the index is unchanged.

No formatter, linter or project-wide suite was run.

## Open

- The entry is 69 lines against T-07's "roughly 45 to 65". Five rulings each carrying a rejected
  alternative, a measurement and an honest scope clause do not compress further without dropping one
  of the three, and the scope clauses are the part a later reader most needs.
- Nothing in T-07's verify tests the entry's substance — it checks a heading prefix, a uniqueness
  count, a byte-for-byte index regeneration and that the ruling starts with a letter. A green run here
  is compatible with prose saying the opposite of the five rulings. Only my own reading covers that.
