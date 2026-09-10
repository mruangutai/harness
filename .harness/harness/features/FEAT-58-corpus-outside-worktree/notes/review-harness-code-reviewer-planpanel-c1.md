# FEAT-58 — plan-panel scope read (reader: scope)

**BLUF: the plan's own bookkeeping holds up — traceability, acyclicity, and task/intent/file
alignment all check out by independent recount — but T-03 and T-04 leave a real gap that T-06 (the
structurally identical sibling case) does not: no test asserts the "resolve root and gate
completeness exactly ONCE per module" instruction is actually honoured when a module has multiple
enumeration call sites.**

## Traceability, dependency shape, file/intent alignment — all clean (independently recounted)

- Every `REQ-01..11` and `SC-01..14` in `BRIEF.md` is cited by at least one task's `traces:`; no
  task cites an id absent from `BRIEF.md`. Recounted by hand across all 16 tasks, not taken on the
  dispositions note's word.
- `depends_on` is acyclic with single root `T-01` (recomputed by inspection, not by re-running
  `check-plan-routes.py`, per instructions). No task depends on a task that transitively depends on
  it.
- Every task's `files:` list contains every production/test file its `intent:` requires *editing*;
  files it only *runs as regression* (e.g. T-03's `verify:` running six pre-existing
  `test-check-state-*.py` files it did not author) are correctly omitted from `files:`.
- Settings.json independently confirmed to register exactly nine hook-script basenames
  (`bash-write-guard.sh`, `branch-create-gate.sh`, `check-domain.sh` ×2 hook types,
  `dispatch-guard.sh`, `gh-close-gate.sh`, `inject-expertise.sh`, `merge-gate.sh`,
  `plan-sign-gate.sh`, `validate-digest.py`) — matches the plan's repeated "nine" claim.
  `merge-gate.sh` is confirmed a thin wrapper that `exec`s `merge-gate.py "$root"`, so T-05's target
  file (`merge-gate.py`) is correct, not a naming mismatch.
- Spot-checked `check-plan-routes.py` for the two sites T-04 names: confirmed two independent
  `glob.glob` call sites at `check-plan-routes.py:678` and `:835`, in different functions —T-04's
  premise about this file holds.
- Spot-checked `branch-create-gate.sh`'s root-resolution and flow-glob lines against T-16's premise:
  both sites exist substantially as described (line numbers drift by ~1, which the plan already
  tells the executor to re-derive rather than trust).

## Finding

- **reader: scope | id: (none — pm assigns) | severity: med | anchor: T-03 intent (21 sites), T-04
  intent (`check-plan-routes.py`, 2 sites) vs T-06 intent case (g) / plan.yaml `check-domain.sh`
  section**
  **Summary:** T-03 and T-04 both instruct "resolve `root` ONCE, gate `feats` ONCE" across a module
  that has *multiple* internal enumeration call sites (21 in `check-state.sh` per the arch-eng
  receipt's hand count; 2 in `check-plan-routes.py` at `:678` and `:835`), and REQ-05's "two frame
  lines per module, never one per site" language confirms the intent really is one shared
  computation. But neither T-03's nor T-04's `verify:`/test-case list contains anything like T-06's
  case (g) — *"ONE enumeration per invocation: with `corpus_features` instrumented, assert exactly
  one call per hook invocation on a payload that exercises both the hardlink check and the sweep."*
  T-06 is the only one of the three multi-site conversions that mechanically pins the "ONCE" clause;
  T-03 and T-04 rely on prose alone.
  **Concrete consequence:** an implementer who converts `check-plan-routes.py`'s `:678` and `:835`
  sites independently (each calling `corpus_root`/`corpus_features` on its own) — a natural reading
  of "TWO sites... Both" if the "resolved ONCE" clause is skimmed as boilerplate — passes every
  stated T-04 case: all of them assert exit status, `"N of M"`, corpus-root text and next-step
  content, none assert call count. The same risk applies to T-03's 21 sites, at larger multiple.
  The failure is silent (no test reddens) and has two real costs: (1) it doubles (T-04) to
  21-times-multiplies (T-03) the `git ls-tree` subprocess cost the relocation was justified by
  cutting in the first place (D-11's own rationale is exactly this class of per-site cost), and
  (2) it opens a narrow window where two enumeration calls in the same invocation could observe a
  mid-run corpus mutation differently, producing two different refusal verdicts inside what the
  design treats as a single atomic completeness gate.
  **Fix shape (not mine to specify further):** add a T-06-style "assert `corpus_features` called
  exactly once per invocation" case to T-03's and T-04's test files, or at minimum to T-04's (the
  case with an already-identified two-site file, `check-plan-routes.py`, making it the cheaper and
  more clearly warranted of the two).

## Explicitly not re-raised

Per dispatch: the refusal-predicate-in-every-converged-worktree defect (fixed at all three sites),
the ledger's 11→12→14→15 movement (deliberately OPEN), and the `main-session-direct` lane
assignment on enforcement-path tasks (correct and deliberate) are not re-flagged here.

## Not filed as findings (considered, rejected)

- T-07's discovery-subset (⊆) assertion is a soundness-only check that would pass vacuously over an
  empty discovery set — but by T-07's own `depends_on` (T-03, T-04, T-05, T-06, T-08, T-13, T-16),
  several real API callers exist in the tree by the time T-07 runs, so the set is not empty in
  practice, and the plan already discloses the completeness limit in its own text ("This is a
  SUBSET assertion — soundness, not completeness"). Not a new gap.
- The `origin/main`-literal brittleness in T-10's second verify command and the five `merge-base`
  sites is already surfaced in `notes/research-FEAT-58-planfix-dispositions.md`'s own "Open, for the
  operator" section — re-raising it here would be re-finding, not finding.
