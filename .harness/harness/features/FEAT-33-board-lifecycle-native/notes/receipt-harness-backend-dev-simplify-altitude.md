# ALTITUDE pass — FEAT-33 plan surface — harness-backend-dev

BLUF: one fold-in finding (the declared-vs-board-options diff is authored twice across T-04 and
T-05 with no named shared authority). Two candidates considered and rejected, with reasons. The
invited cross-repo-sequence soundness check passes.

## Finding 1 — the byte-for-byte declared/board diff has two independent authors, not one

- **File/lines**: `plan.yaml:282-286` (T-04, provision step 4) and `plan.yaml:328-330` (T-05, audit
  finding class DECLARATION).
- **Summary**: Both tasks independently specify the same computation — "declared station values
  not present among the board Status field's option names, compared byte for byte and case
  sensitively" — as prose in two separate task intents, in the same target file
  (`board_lifecycle.py`), with no shared function named to carry it once.
- **Concrete cost**: D-05 makes case-sensitive, exact comparison a deliberately load-bearing
  property ("exactness is what makes a drifted declaration loud"). With two independent
  implementations of that comparison in one module, a later edit that loosens or fixes the
  comparison (trimming whitespace, a normalization step, an off-by-one in set semantics) has two
  places to find and update, and nothing in the plan states they must stay identical — the
  precise failure mode D-05 was written to prevent, reintroduced one level down inside the file
  DEC-05 governs. T-05 depends on T-04 (`plan.yaml:315`), so the diff already exists in the tree
  by the time T-05 is written — the ordering makes reuse free, not merely desirable.
- **Alternative**: name one private helper in `board_lifecycle.py` (e.g. a function that takes the
  declared key→value map and the board's existing option names and returns the missing values, in
  declared order) and have both provision step 4 and audit's DECLARATION class call it. State this
  once in T-04's intent as "expose it for T-05 to reuse" and reference it from T-05's intent rather
  than re-deriving the same comparison in prose.
- **Recommendation**: `fold-in` — cheap, reversible, no new API surface, and T-04/T-05 are both
  still `pending` on the same file.

## Considered and rejected

- **T-07's closed/done-station guard living in gh-sync.py's `cmd_start_task` rather than in
  `gh_board.py`** (`plan.yaml:436-443`). This looked like a candidate for "a check living inside
  one call site where a shared home already exists," since `gh_board.set_station` is also called
  by T-06's reconcile. Rejected: reconcile's STATION-finding fix *moves closed cards to the done
  station* by design — the same guard applied there would block the exact fix reconcile exists to
  perform. The two call sites have opposite station-write semantics on closed issues, so there is
  no single shared invariant to hoist, and the existing codebase pattern already keeps this class
  of caller-specific policy in gh-sync.py's `cmd_*` functions (e.g. `cmd_ship`'s origin-gated
  close). Leaving it in `cmd_start_task` matches that precedent rather than fighting it.
- **Cross-repo sequence soundness (D-06, T-01 before T-02)** — explicitly invited by the dispatch.
  Assessed and it is sound: `validate_board` is exact-set-equality in both directions
  (`factory_config.py:134` per the research note), so no ordering is atomic and every ordering
  leaves a window. The chosen order (kaya-ai's six-key declaration merges first) means the *only*
  live failure mode in the window is `factory_config.board_for('mruangutai/kaya-ai')` raising
  `FleetError` naming `github.board.stations` if a factory command runs against kaya-ai before
  T-02 — a loud, named, latent-not-live failure, not a silent one. T-01's intent states this
  exactly and instructs "do not run a factory command against kaya-ai between this task and T-02"
  (`plan.yaml:119-123`). The reverse order would have produced the identical class of failure in
  the opposite direction with no better outcome, so the choice does not trade a real safety
  margin for a cosmetic one. No finding.
- **The workflow-detection limitation (D-09) restated in T-03, T-05 and T-10's intents** — each
  restates "ProjectV2Workflow exposes neither trigger nor action, only a click enables one."
  Rejected as a duplication concern: the three restatements target three different audiences that
  each need the fact in their own artifact (a code docstring, an audit report line, onboarding
  prose for a human operator), all citing the same D-09 authority rather than asserting it
  independently. This is propagation of one fact to its necessary surfaces, not drift risk.

## Not flagged — explicitly settled, not re-litigated

`plan` derivation, `Abandoned` as a column, workflow-enable-by-API, workflow detection's home at
`/harness-init`, FEAT-26 scope, `mruangutai/harness` absence from `fleet.yaml`, and the three
`ensure_labels` implementations staying three (D-04) — all confirmed present and correctly
reasoned in `plan.yaml`/`BRIEF.md`, none touched by this finding.
