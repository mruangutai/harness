# Code review c2 — BUG-2294

PASS — T-01 closes SEC-01 for the reported run/UI symlink shapes; SC-01–03 comply, with no code-quality findings.

Reviewed `c1724230c4d931ad46d433c8ba93df8cf312f898..88bf039f6ff31edbb1d5a4b2f6620762e3cc095a`, emphasizing `70981edd6f9f110965a0148b4490ed2673d262dc..e51277a4ce11c91f2252026ae4dd6e0fbf12a503`. Feature record agrees with the review pin. Commit history includes the fix, and fix-to-pin source/test diff is empty. Human commit in scope: `128a7158 [harness:human] BUG-2294-prune-keeps-run-digests: operator signature (rework 1 round / 45 min, main-session-direct T-01)`. Working changes are feature records only; implementation reads used pinned `git show`, not HEAD.

## Stage 1 — compliance

- SC-01: `.claude/skills/harness/bin/prune-run-evidence.py:120-146` excludes kept runs, skips run and UI symlinks with named output, and passes only selected UI paths to `rmtree`; absent UI and repeated pruning are no-ops. Run records/non-UI siblings are not deletion targets.
- SC-02: `tests/unit/test-prune-run-evidence.py:197-253` executes the real pruner and accepted feature-scoped INV-7 check-state around ten hash-bound digests, final BLOCKED, no UI or passing validator run. No reopening of settled verification scope.
- SC-03 inspection: pinned pruner `:49-117,151-162` and baseline diff establish unchanged PASS selection, pin selection, CLI, `--keep` validation and refusals. `.omp/commands/harness-ship.md:38-54` preserves step placement and both invocations at `:43-44`; only retention prose changes. `.harness/harness/docs/DECISIONS.md:7986-7998` preserves Abandon/INV-51 and keep/refusal policy while narrowing ship removal and naming the three protected files/#2177. `DECISIONS-INDEX.md:232-237` retains ruling semantics, updates generated tags and subsequent line offsets.
- All product changes serve SC-01–03/D-01; feature records document the task. Requested product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` remain absent; no substitute guidance used. Main-session-direct handoff has no build-lead amendments list.

## Stage 2 — quality and evidence

- `_ui_targets` owns selection and named skips; `_prune` consumes its relative paths consistently. Reported aliases to kept/external runs cannot enter deletion targets, and UI symlinks are excluded before directory selection. Exceptions from deletion are not swallowed. No speculative seam or compatibility layer added.
- `tests/unit/test-prune-run-evidence.py:150-194` binds actual subprocess behavior: dry-run requires a real target alongside absence of linked targets; prune requires real UI removal, all named skips, and nonempty byte-identical destination trees. Reverting link guards would violate those assertions.
- `notes/red-first-T-01.md` c1 fix records four assertion failures against 70981edd and 25 passing checks after remediation, with sibling-import setup and subject hashes. This is inspected evidence, not a rerun by this reviewer.
- Executed only mandated pinned Python risk grading: 20 reported functions PASS; `_ui_targets` cyclomatic 6, cognitive 6, ABC 11.5, grade 4/bar 4. Test functions meet bar 3; no high or grade-2 records.

## Principles applied

- Delete First: accepted the local selection/removal replacement without a new abstraction stack or changes to keep-policy callers.

Open questions: none. Must-fix: none. QA owns final `python3 tests/unit/test-prune-run-evidence.py`; no tests, builds, lint or formatters run here.
