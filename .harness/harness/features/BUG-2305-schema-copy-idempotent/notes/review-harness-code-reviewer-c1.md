# T-01 code review — c1

PASS — no substantive or form findings at `7f9cc9d86a72346f250d0e2d6f7afb942473fe8b..297913318472d066ecb9d5eb3f83ee2ca82c3ad7`. Inspection only; QA owns the final unit gate.

## Stage 1 — spec compliance: PASS
- BRIEF SC-01..04 and plan D-01 read before the diff; no build amendments declared. Four product files implement the agreed change; other range entries are feature intake/signature/build records. Human commit in scope: `be7347f2d491` (operator signature).
- SC-01: `.omp/extensions/harness-hooks.ts:379-427` accepts only a Harness target's own structurally equal strict pair and re-injects the canonical bundle. `tests/unit/omp-hooks.test.ts:1743-1764` independently asserts flat/item acceptance, cloned/reordered keys and canonical identity for all sixteen authoritative personas.
- SC-02: hook `:393-409` retains field/location refusals; tests `:1789-1859` cover changed/wrong-persona bundles, non-strict values, incomplete pairs, non-Harness controls, batch-top-level controls, later invalid items and unknown bundles. Hook `:1474-1491` completes refusal/loading before dispatch guards and claims.
- SC-03: removed note constant, emission and obsolete references verified by pinned search of both owned files. Positive injection assertions accompany note-absence assertions (`tests/unit/omp-hooks.test.ts:1687-1723,1767-1786`); unrelated expertise context remains at hook `:1326-1332`. Existing loading refusal test remains at test `:1877-1895`. Red-first receipt records five assertion failures then green, not import failures; these are builder-reported results, not independently executed here.
- SC-04 inspection: pinned `.harness/harness/docs/DECISIONS.md:7917-7928` narrowly amends schema delivery; all other decision bytes are unchanged in the diff. `.harness/harness/docs/DECISIONS-INDEX.md:231-237` preserves DEC-237's row and shifts downstream anchors by the amendment's five added lines; regeneration receipt is in `notes/red-first-T-01.md`.

## Stage 2 — code quality: PASS
- `isDeepStrictEqual` avoids serialization/order dependence. Expected bundle failures return false, producing explicit refusal; unexpected exceptions propagate rather than accepting. Canonical cached/frozen loading remains the single authority; no new persistence or compatibility path.
- Accepted batch items only skip their own refusal collection, never terminate the scan. All bundles load before claims. Regression assertions execute registered hooks, bind concrete returned inputs/refusal locations, and would reject undefined-return or unconditional-accept implementations.
- No changed Python; digest validator reports mechanical code grade `n_a` for this range. No tests, builds, lint, formatters or mutants run, as assigned. Review used pinned `git show`/diff/search, not ambient source bytes; only dirty tracked file was feature metadata carrying the matching review pin.

## Dismissed / settled
Typecheck runner gap #2257 is approved/disclosed; batch-top-level and non-Harness controls intentionally remain refused; OMP persistence remains out of scope. No new findings or scope-change recommendation. No open questions.

## Principles applied
- Type System Discipline: inspected untyped control narrowing at the dispatch seam and reuse of authoritative projected schemas rather than parallel schema types.
- Migrate Callers, Then Delete Legacy APIs: verified removal of the workaround constant, emission, tracking flag and obsolete test expectations together, without removing unrelated context.

## Receipt correction
Initial digest submission was refused for mechanical-grade and human-commit representation mismatches. Corrected to the validator-reported `n_a` and twelve-character commit ID; substantive review unchanged.
