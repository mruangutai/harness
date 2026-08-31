# Receipt — harness-documentor — FEAT-45 T-01 fix (renumber)

**The two entries this feature added are now DEC-206 and DEC-207.** Prose untouched; only the two
`## DEC-NNN` heading numbers and their two index rows changed. **No body self-reference to `DEC-205`
or `DEC-206` existed — none found**, so no in-body renumbering was needed (`grep -n 'DEC-20[5-7]'`
over DECISIONS.md matched the two heading lines only, before the edit). The gap at 205 is
intentional: `main` (ba338d8) holds a different DEC-205 that this branch cannot see, and
`gen-decisions-index.py` sorts by number without asserting contiguity.

- `## DEC-206 — A harness lead may wrap a non-harness panel reader…` @ DECISIONS.md:7416
- `## DEC-207 — A gate may grade a specification before any code exists…` @ DECISIONS.md:7445

Renumbered high-number-first (206→207, then 205→206) so the two edits could not alias.

## Cross-check of T-01 `verify`

Read from `plan.yaml:309-316`: byte-for-byte the block quoted in the dispatch. Clause 2
(`git diff --quiet`) is unsatisfiable on an uncommitted tree by construction; replaced with the
fixed-point checksum below. **Nothing was committed.**

## Acceptance evidence

1. Heading counts — `grep -c '^## DEC-205' → 0`, `'^## DEC-206' → 1`, `'^## DEC-207' → 1`.
   `grep -n 'DEC-205'` across both docs emits **zero bytes**; that emptiness is the pass condition.
2. Literal phrases, all four green (`grep -c`):
   - `wrapped non-harness reader` — DECISIONS.md:1, DECISIONS-INDEX.md:1
   - `plan-phase gate` — DECISIONS.md:1, DECISIONS-INDEX.md:1
3. `python3 .claude/skills/harness/bin/test-gen-decisions-index.py` → 10 `ok -` lines, exit 0
   (includes `test_committed_index_matches_a_fresh_regeneration` and the length-budget test).
4. Regeneration is a fixed point — both generator runs exited 0, and:
   - after run 1: `7c5397549341c7a7e82b66522d97f507ed1cce263e72977fab8fa6542612c058`
   - after run 2: `7c5397549341c7a7e82b66522d97f507ed1cce263e72977fab8fa6542612c058`
5. Index rows and ruling text:
   - `- DEC-206 @7416 [digest,dispatch,plan,skills] refs:  :: …`
   - `- DEC-207 @7445 [plan,approval,digest,dispatch] refs: DEC-176 :: …`
   Anchors match the two heading line numbers above. Ruling text after ` :: ` **byte-identical** to
   pre-edit (`diff` of the stripped rows, before vs after, reported no difference). No
   `RULING PENDING` sentinel in the output; no orphan row survived the rename.

## Scope proof

Heading list and index diffed against `HEAD`: the only differences are the two added entries/rows
(`202a203,204` and `222a223,224`). No other DEC entry, no other index row, no other file touched.
Main's DEC-205 was **not** imported. Tree left uncommitted.
