# Handoff — build seam

Build complete and committed, pinned at `83282dea`. Every `feature.json` writer
is on the locked core, and the OMP edit route that had zero test coverage now
has six cases plus S2's notice.

## next

Run the `review` team against `83282dea` (base `6d6d1cea`). Then decide the two
approval-gated items: the DEC-199 amendment ("exactly four consumers" is now
false — there are six) and whether S3 ships.

## trust

- Full suite at the pin: exit 0, 1038 PASS files, 0 FAIL. `check-omp-port` ok,
  `check-kinds` agrees, `bun test omp-hooks.test.ts` 48 pass.
- The edit-route gap is demonstrated, not argued: with the `postDomain` edit
  route neutered, the pre-existing suite stayed completely green.
- S2 is mutation-proven — replacing its condition with `false` reddens exactly
  one test.

## dead ends

- **`_dabsentT02` does not bind `gh-sync`'s never-create rule.** Killing both
  refusal sites leaves the suite at FAIL 0; `require_destination` refuses as a
  third layer. The guarantee holds, but not for the stated reason. Do not cite
  that test as the witness.
- **Q1 is undecidable from a static tree** — whether the gate fired on the
  original incident and went unread, or never ran. Do not assert either.
- **S3 has not shipped.** The guidance remedy is outstanding, not done.
- The producing squad returned one false PASS (19 integration failures) and one
  overstated evidence claim. Verify its reports rather than accepting them.

## working set

- `.omp/extensions/harness-hooks.ts` — S2, enforcement layer, DEC-174
- `.claude/skills/harness/bin/omp-hooks.test.ts` — the six edit-route cases
- `.claude/skills/harness/bin/feature_json_write.py` — the locked writer
- `.claude/skills/harness/bin/gh-sync.py`, `factory_decompose.py` — rewired
