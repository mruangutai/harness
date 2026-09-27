# FEAT-68 — clean-checkout implementation-pin receipts

This file is the hand-written record; the measurements it cites are in the sibling
`clean-pin-byte-receipts.generated.md`, which is produced — and only produced — by the command in
`## Reproduction` below, and committed exactly as produced (fix c3, VF-05-C3). Both are written
after the implementation pin and are not inside it.

- implementation pin: `9ab1813e86067ca4a21a84f49364cf4f453055b4`
- baseline: `e655f14a56a14bf1777cae55a19195c9af10505d` (= origin/main at the signed plan)
- pin checkout: `.claude/worktrees/harness/feat68-cleanpin-9ab1813e` (detached; the script asserts `git status --porcelain` empty)
- baseline checkout: `.claude/worktrees/harness/feat68-base-e655f14a` (detached; the baseline json was captured there)
- normalisation: ONE, on both sides — each checkout's own absolute root → `<checkout>`. No other
  substitution; every remaining byte difference is a divergence, ledgered in
  `notes/build-divergences.md` D-01..D-05 with its exact old/new bytes taken from the generated file.

## Reproduction

The feature tree exists only in the feature worktree until merge, so every command runs from the
worktree root `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave`
(after merge, the same relative paths hold from the main checkout root). Scripts, preserved verbatim:
`SCRIPTS=.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts`.

1. `git -C /Users/molchairuangutai/GitHub/harness worktree add --detach .claude/worktrees/harness/feat68-base-e655f14a e655f14a56a14bf1777cae55a19195c9af10505d`
2. `python3 $SCRIPTS/feat68-baseline.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/feat68-base-e655f14a /tmp/feat68-baseline.json`
   — runs the 57 suites listed in the script's body inside the baseline checkout; writes exit,
   stdout, stderr and sha1 per suite (`$FEAT68_BASELINE_JSON` overrides the path step 3 reads).
3. `python3 $SCRIPTS/feat68-cleanpin.py 9ab1813e e655f14a`
   — creates (or reuses) the detached pin checkout, runs each of the 57 suites there ONCE, and from
   that single execution writes the table (exit, raw sha1 per stream, normalised-identical flag) and
   the raw-difference lines; runs `$SCRIPTS/feat68-grade-assert.py` (the T-01 verify assertion,
   loaded from the script's own directory) in the pin checkout (green) and the baseline checkout
   (red); writes `notes/clean-pin-byte-receipts.generated.md`.

Environment: macOS, CPython 3.14.5 (`/opt/homebrew`), git worktrees.

## Result (from the generated file)

53/57 identical under the one normalisation; exit status matches in 57/57; stdout matches in 56/57.
SC-01: the grade assertion exits 0 in the pin checkout and 1 in the baseline checkout, naming
exactly the five targets at grade 1.

## The four non-identical suites

53/57 identical under the one signed normalisation. The four that differ are five ledgered
lines, each with exact old/new bytes above and its ruling in `notes/build-divergences.md`:
D-01 `test-suite-independence.py` `discovered 112 → 111` (the deleted renderer test — the
deletion's consequence); D-02/D-03/D-04 one stderr line each in `test-harness-yaml.py`,
`test-harness-boundary.py`, `test-suite-independence.py` naming the case's fresh `mkdtemp()`
directory; D-05 `test-artifact-accessors.py`'s unittest wall-clock. Exit statuses match in all
57; stdout matches in 56.

## Test kinds at the pin (change_type cross_module: unit + integration both required)

Run in the feature worktree at `9ab1813e` via the configured runner
(`.agents/skills/harness/bin/run-unit-tests.py`): `--kind unit` exit 0 (41 files — one fewer
than the base, the deleted renderer test); `--kind integration` exit 0 (70 files, `0 failure(s)`).
The candidate `0c15bad6` before it failed the unit kind on `test-code-grade.py`'s stale
`process_plan_yaml: 1` exemption (D-13); `9ab1813e` removes it and is the pin.

## SC-05 at the pin

The verify block's html-absence and reference-grep assertions pass at the pin (part of the
T-01 verify run above); no `render-brief` / `md_to_html` reference remains outside notes,
logs, decision records and feature-history dirs.

## History of this receipt

- `ae0b41d7` (build): baseline captured in the feature worktree; two extra normalisations. Validate
  c0 VF-01 rejected both → detached baseline, root-only (`66b9c914`).
- `ab17ca17` (fix c1): reproduction section added; its "repository root" paths did not resolve and
  the script still read `/tmp` (c2 VF-04-C2) → fix c2 (`b6b8c28d`), which regenerated the file by
  the recorded command; c3 found the paths still stated from the wrong root and, more seriously,
  that the generator ran every suite twice, deriving hashes and raw bytes from different executions
  (VF-04-C3, VF-05-C3).
- This version (fix c3): generator executes once and writes a separate generated file; this record
  is hand-written and cites it; commands stated from the worktree root, where they were run.
