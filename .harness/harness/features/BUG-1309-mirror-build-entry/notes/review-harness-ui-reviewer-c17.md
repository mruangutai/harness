# UI Review (Mode B) — BUG-1309 c17 panel

**Scoped out — measured, not predicted.**

## What I read
The exact file set named in the dispatch contract: `.claude/skills/harness/bin/merge-gate.py` and
`tests/integration/test-merge-gate.py`, via `git diff e374c9a2..94b5e465 -- <those two paths>`
(+50/-26, matches contract). Also ran a full-commit-range `--stat` across all 19 changed files in
`e374c9a2..94b5e465` to confirm no other path in the range carries a UI surface.

## Census measured
- Extension census of the two in-scope files: both `.py`. Zero `html/css/scss/tsx/jsx/vue/svelte/less`
  hits in the diff.
- Full-range `--stat` (19 files): 17 are `.md`/`.json` under `.harness/harness/features/BUG-1309-mirror-build-entry/`
  (plan, BRIEF, STATE, notes, observations) — docs/plan artifacts explicitly ruled out of code-review
  scope by the dispatch contract, and not rendered UI surfaces either.
- `DESIGN.md` search: no file named `DESIGN.md` exists anywhere under the feature directory. No design
  contract exists for this feature at this pin.
- Single diff hunk in `merge-gate.py` spans the rewritten `git_merge`/`option_end`/`first_subcommand`/
  `merge_target` functions (source lines ~43–85 in the new file). Confirmed by reading the post-image
  file (`git show 94b5e465:.claude/skills/harness/bin/merge-gate.py`) that the operator-facing surface —
  `deny()` (line 144), the four `print(..., file=sys.stderr)` lines (170, 184) and the `deny(f"...")`
  calls (174, 188, 192, 194) carrying the "predates the build-entry receipt", "could not verify …
  mirror", and duplicate-attribution wording — sits entirely outside the diff's hunk range, and every
  one of those literal strings is byte-identical to the pre-image; the diff never touches them.

## Verdict
The dispatch's own framing narrows the only plausible user-facing surface in this diff to the
operator-facing message text merge-gate.py emits (deny reason / stderr lines), conditioned on this
diff having changed that text. It measurably did not: the diff is confined to internal parser
plumbing (option-class sets, a two-function tokenizer rewrite) and to adding four new test-case tuples
to `tests/integration/test-merge-gate.py`. Test case names (`"T-05 merge -F detached value denies"`
etc.) are developer-facing check-harness labels printed by the test runner's own `check()` function,
not operator-facing product copy the gate emits — outside this role's remit per the dispatch's own
scoping language.

No user-facing surface changed. Nothing to audit under Mode B for fidelity/states/interaction/
accessibility/theme-parity; those sections are not applicable (no rendered surface, no message-copy
change) rather than silently skipped.
