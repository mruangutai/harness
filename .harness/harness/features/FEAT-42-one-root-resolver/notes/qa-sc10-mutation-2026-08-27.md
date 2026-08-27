# SC-10 vacuity probe by mutation — 2026-08-27

**Verdict: the assertions in `test-harness-boundary.py` are NOT vacuous.** All 6 mutants died,
including the 3 whose recorded red was `AttributeError` (name-absence only). The suite's live
assertions compare actual computed values (paths, stderr text, exception messages), and those
assertions — not the name-presence the receipt captured — are what kill every mutant below.

## Method

Mirror built via `shutil.copytree`-equivalent (`cp -R`) of the whole `bin/` directory (not a
single file — a lone-file copy has no sibling modules to import, the exact mistake
`notes/verify-technique-2026-08-27.md` records as having already voided one proof on this
feature) into scratchpad, at `f42-mirror-bin`. Mutated `harness_boundary.py` inside the mirror
only, ran the mirror's own `test-harness-boundary.py` (11 verdict lines baseline, all PASS,
`ALL PASS` / exit 0), reverted each mutant before the next. Confirmed live tree untouched:
`git status --porcelain .claude/skills/harness/bin/` → empty, both before and after. Confirmed
mirror fully restored: `diff` against `git show HEAD:.../harness_boundary.py` → byte-identical
after the final revert.

## Mutants

1. **`MARKER`** → `.harness/nonexistent-marker-xyz.yaml`. Applied line read back:
   `41:MARKER = os.path.join(".harness", "nonexistent-marker-xyz.yaml")`. Suite ran (8 verdict
   lines). **5 named FAILs**: `marker_constant_exact_value`,
   `case_resolve_root_strict_did_not_crash`,
   `case_resolve_root_override_normalises_relative_did_not_crash`,
   `root_above_finds_marker_walking_up`, `root_above_bare_dot_harness_does_not_satisfy`.

2a. **`root_from_script`, one level deeper** (5×`..`). Applied line:
   `50:    return os.path.abspath(os.path.join(bin_dir, "..", "..", "..", "..", ".."))`.
   Suite ran (9 lines). **3 named FAILs**: `root_from_script_four_levels_up_no_marker`,
   `root_from_script_unchanged_when_marker_exists`, `case_resolve_root_strict_did_not_crash`.

2b. **`root_from_script`, one level shallower** (3×`..`). Applied line:
   `50:    return os.path.abspath(os.path.join(bin_dir, "..", "..", ".."))`. Suite ran
   (9 lines). Same **3 named FAILs** as 2a.

3a. **`resolve_root`, precedence inverted** — override branch now tests the *derived* root's
   marker instead of the override's own. Applied lines confirmed by reading the mutated block
   back (`if os.path.isfile(os.path.join(derived, MARKER)): return os.path.abspath(override)`).
   Suite ran (8 lines). **2 named FAILs**: `case_resolve_root_strict_did_not_crash`,
   `case_resolve_root_override_normalises_relative_did_not_crash`.

3b. **`resolve_root`, marker guard dropped** — `if os.path.isfile(os.path.join(override,
   MARKER))` replaced with `if True`, trusting any override unconditionally. Applied line
   confirmed (`if True: / return os.path.abspath(override)`). Suite ran (11 lines).
   **3 named FAILs**: `resolve_root_strict_bad_override_falls_through_to_derived`,
   `resolve_root_strict_bad_override_reported_on_stderr`,
   `resolve_root_strict_neither_carries_marker_raises`.

4. **`root_above` control** — marker check widened to accept a bare `.harness` *directory*
   (`os.path.isdir(os.path.join(cur, ".harness"))`), reinstating the fail-open T-02 exists to
   close. Applied line confirmed. Suite ran (11 lines). **1 named FAIL**:
   `root_above_bare_dot_harness_does_not_satisfy`. Control behaved as required — it died, so the
   harness is trustworthy rather than broken.

Every mutant produced a nonzero verdict-line count and a **named** FAIL, never a bare exit code
or a silently-filtered empty set — the failure mode the dispatch specifically warned against did
not occur here.

## Second question — cwd-parity, standalone runs at 9d12e3a

Ran both files directly (no `--kind all`, no fixture setup) from this worktree's root:

- `python3 .claude/skills/harness/bin/test-bash-write-guard.py` → exit 0, `20/20 HEAD-move and
  forced-removal cases passed.`, 101 `ok` lines, **0 failures**.
- `python3 .claude/skills/harness/bin/test-check-domain.py` → exit 0, `28/28 T-14 cases
  passed.`, 203 `ok` lines, **0 failures**.

**This contradicts the eng digest's Q6 claim** (`runs/2026-08-26-7-eng/digest.md`) of 2 and 7
standalone failures at the same SHA. Either the claim was measured from a different cwd/env than
this worktree's root, or it was itself wrong, or something changed between that run and now. As
measured here, both suites are green standalone — so the #556 cwd-parity byte-identical proof is
**not** satisfied by a uniformly-red suite in this configuration; the specific concern Q6 raised
does not reproduce. Recommend a fresh, cwd-explicit re-run of Q6's own repro steps rather than
trusting either number un-remeasured.

## Findings for the backlog

- **bug (unconfirmed / needs repro)**: Q6's claimed standalone failure counts (2, 7) for
  `test-bash-write-guard.py` / `test-check-domain.py` did not reproduce here (0, 0) at the same
  SHA. Someone should re-run Q6's exact original invocation (cwd, env) to determine whether the
  original claim was an environment artifact or has since been fixed/masked.
- No new SC-10 defect: the mutation proof shows the existing assertions are live and
  discriminating despite the misleading `AttributeError`-shaped receipts.

## Files touched

None in the worktree. All mutation and revert activity happened inside the scratchpad mirror at
`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/e69cbdc1-8355-4358-b5f2-d7604a1a913b/scratchpad/f42-mirror-bin`,
which is disposable scratch, not a tracked path.
