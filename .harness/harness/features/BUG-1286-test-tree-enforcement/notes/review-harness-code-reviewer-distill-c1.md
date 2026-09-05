# Distillation — harness-code-reviewer — BUG-1286-test-tree-enforcement

**Not a code review.** No diff was read, no severity assigned, no code graded — this is the one
feature-close Expertise write for this persona. `code_grade: n_a` because no `review_sha` applies
to a distillation dispatch.

## What changed

- **Repository tier** (`.harness/harness/expertise/harness-code-reviewer.md`): Gotchas 7→8. Added
  G-08, self-derived from my own `notes/review-harness-code-reviewer-c1.md` Finding A —
  `_registry_findings` in `suite_layout.py` runs unconditionally on any successful git enumeration,
  independent of the self-ownership test, misfiring on a checkout that doesn't itself ship
  `suite_layout.py` (open backlog, unresolved as of the merged build). Durable, one-repo fact —
  fails the "true in a repo never seen" test, so repository tier, not craft.
- **Craft tier** (`.harness/expertise/harness-code-reviewer.md`): unchanged. Patterns 15/15,
  Gotchas 15/15, Outcomes 10/10 — all three used sections at exact cap both before and after.

## Two displacements I judged worth making, both blocked by a confirmed tool limitation

`expertise-merge.py apply` is pure additive union-merge: it never removes a base entry. Verified
live, twice:
- Reusing `P-04`'s id with different text → `CONFLICT section=Patterns id=P-04` (exit 7), file
  untouched.
- Adding a new id (`P-16`-equivalent) to a section already at cap → `CAP EXCEEDED section=Patterns
  cap=15 union_size=16` (exit 8), file untouched.

Both refusals are pre-write (atomic `locked_update`) — no partial or corrupted state. Gotchas is
symmetrically full and would refuse the same way; I did not re-run the identical probe against it.

Candidates I would have applied here, recorded for a future `harness-curate` pass:

1. **Displace `P-04`** (narrow: PLAN duplication-risk sibling-absence-check tell) **with**: "WHEN an
   ordering/precondition guarantee (X before Y) is confirmed only by reading the code DO construct
   a genuine adversarial fixture and drive it live — a correct structural argument can still leave
   the empirical case unbuilt, and repeated inspection-only checks by peers do not substitute for
   one real run." Source: my own c2/c3 cycle — D-03's ordering constraint had been verified "by
   inspection" by me at c1, by QA, and by a prior cycle, until c2, when I built a two-repo fixture
   (editing `.git/config` to add `core.worktree`) and drove the actual toplevel-mismatch case live.
2. **Displace `G-12`** (narrow: severity-weighting for findings about carriers injected into every
   spawn of a persona) **with**: "WHEN a spec or guard classifies a path/string as safe via literal
   prefix or substring comparison DO test it against a `..`-segment or symlink-based mutant before
   trusting the classification — an unnormalized string check can rate a directory-escaping path
   safe while the underlying vocabulary check never sees it." Source: `notes/review-harness-code-
   reviewer-planpanel-c6.md` Finding F1 (HIGH) — a plan's literal-prefix excusal rule stayed GREEN
   under a `tests/../evil/**`-style mutant, reproducing the exact defect class the feature exists
   to close.

## Candidates rejected, with reason

- **C1** (the mechanical grader nobody had run before c1) — already protocol-mandated every
  review, not a discretionary judgment; residual lesson ("don't trust upstream silence as evidence
  of clean") already covered by existing craft P-03.
- **C2** (general form of "reading absence" from a diff-based report) — already present at both
  layers: craft `G-11` states the generic rule, repository `G-06` states the code-grade.py-specific
  instance. One new grounding instance is not enough to add a third restatement.
- **C3-ii** (the git `core.worktree` nested-checkout construction technique, standalone) — real and
  reusable, but ranked below the F1 path-traversal candidate for the one Gotchas slot I could argue
  for; moot regardless given the tool's no-removal behavior.
- **Cross-member confirmation** (peer's note mis-described a list comprehension's loop order) —
  fully covered by existing craft `P-01` (verify a label/comment's coverage claim against the
  actual invocation).
- **C8(a)/C10(b)** (plan-panel: an overbroad impossibility claim; a rule that rejects its own
  safest witness case) — both real, well-verified, both resolved benign (no operational defect),
  both specific instances of the "test absolute claims against a constructed counterexample" ethos
  already covered by `P-08`/`P-09`/`P-14`.

## Verification run

- `expertise-merge.py apply` on the repository file: `ADDED G-08`, 7×`PRESERVED`, exit 0.
- `expertise-merge.py apply` on the craft file, `P-04` reuse: `CONFLICT`, exit 7 (live probe).
- `expertise-merge.py apply` on the craft file, new id at cap: `CAP EXCEEDED`, exit 8 (live probe).
- `check-expertise.sh` on the repository file: exit 0 (OK), post-change.
- `check-expertise.sh` on the craft file: exit 0 (OK), unchanged pre- and post- (both write
  attempts refused before commit).

Nothing committed, nothing staged, no worktree removed, no project-wide suite run.
