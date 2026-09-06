# UI review — BUG-1290 B-16 fix cycle (pin `c488218e`)

**Verdict: PASS (scoped out, earned decline). No UI surface in this diff.**

## 1. DESIGN.md
Absent, measured directly: `git cat-file -e c488218e:.harness/harness/features/BUG-1290-factory-claim-repo-root/DESIGN.md`
exits 128 (`does not exist in c488218e...`). Confirmed a second way — a glob for `*DESIGN*`
under the feature dir returns no matches. No Mode A contract exists for this feature; nothing to
audit there.

## 2. Census of the changed file
`git diff 7104aa43 c488218e -- tests/unit/test-factory-claim.py` is the full diff (+57/-8, the
only changed path in the review_sha diff-stat against the byte-identical production pin). New
code, all inside `tests/unit/test-factory-claim.py` ~L1181-1323:

- `_run_5b_scenario()` — extracts fleet/board/issue-data setup into a helper, returns
  `(code, out, err)`. Plain Python, no I/O beyond the existing harness fixture calls.
- `_5b_property_holds(code, out, err)` — a pure predicate over the tuple, `json.loads` plus
  substring checks.
- case `5g` — a mutant `_BlockerCache` subclass and one `check()` call reusing both.

Enumerated every changed line (57 added, 8 removed) against: rendered surface — 0; component — 0;
stylesheet — 0; template — 0; terminal-output formatting — 0 (the `print(...)`/`check()`
formatting is untouched — see below); accessibility affordance — 0. **Census result: zero.** This
is a pure Python test-refactor-plus-new-case; no line in the diff emits, styles, or lays out
anything.

## 3. The one judgement worth the spawn — developer-facing legibility of a failing `5g`

Confirmed by diff inspection that `check()` (L41-47) and the final summary line
(`print(f"\n{RAN - FAILS}/{RAN} checks passed."...)`, EOF) are **byte-unchanged** by this commit —
pre-existing, not new UI-adjacent surface introduced by B-16. What IS new is that `check()`'s
existing failure rendering now receives 5g's `(code, out, err)` triple, and 5g's assertion is
`not _5b_property_holds(...)` — a negation, unlike every other `check()` call in the file.

Traced what a reader actually sees on a 5g FAIL: `check()` prints
`FAIL  <name_5g>\n        <detail>` where `name_5g` = *"collapsing the issue-map cache key to
feature-only breaks 5b's property"* and `detail` = the raw `(code, out, err)` tuple. Concretely,
if 5g fails it is because the mutant did NOT corrupt 5b's scenario, so `detail` will look exactly
like 5b's own healthy-passing tuple: `code == 0`, a JSON payload with `issue: 952`, and the usual
diagnostic strings in `err`. **This is the legibility gap**: every other `check()` in the suite
prints a name stating the wanted-good behavior, and a FAIL's detail visibly shows the broken
values — the reader's eye is trained to read "does this detail look wrong?". For 5g that training
misfires: the detail that signals FAILURE is indistinguishable in shape from the detail that
signals PASS on every neighboring case, and the only cue that inverts the reading is parsing
`name_5g`'s sentence as an assertion ("breaks the property") and negating it — one extra logical
step the other ~10 cases in this file don't require. A reader skimming a red CI line without
re-deriving the sentence's polarity could misjudge a 5g FAIL as a benign/healthy-looking payload
and under-react.

This is real but does not rise to a shipped defect — it costs a moment of re-reading, not a wrong
verdict (the FAIL line itself, and `sys.exit(1)`, are unambiguous; only the *reason* requires
parsing the sentence). Per dispatch: legibility opinions do not gate.

**Backlog candidate (non-gating), nature `enhancement`**: consider printing an explicit inverted
cue in 5g's `check()` name or detail (e.g. prefixing `detail` with a literal marker like
`"mutant NOT caught:"` before the tuple) so a 5g FAIL reads as wrong without requiring the reader
to negate the sentence first. Not filed as `must_fix` — it is a readability nicety on a
test-only, developer-facing print path with zero user-facing exposure, and the feature is at its
last rework cycle.

## Findings
- `must_fix`: none.
- `should_fix` (backlog): the 5g legibility gap above, nature `enhancement`, non-blocking.

Nothing modified. No production, test, or plan file edited by this review.
