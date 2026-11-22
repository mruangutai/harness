# Goal-check c2 — BUG-2294

Implementation and DEC-238 disposition pass inspection at 88bf039f6ff31edbb1d5a4b2f6620762e3cc095a; operator automated assurance remains partial until QA's scheduled final gate. This is an evidence gap, not a new product finding. No tests were run by PM.

## Perspectives

- **operator — partial** (SC-01, SC-03): pinned prune-run-evidence.py:120–146 targets only real ui/ under real run entries and skips run/UI symlinks before rmtree. Existing keep/refusal/CLI code is unchanged in the base-to-pin diff; harness-ship.md:38–54 retains placement and both invocations. tests/unit/test-prune-run-evidence.py:100–135 covers byte preservation, kept UI, dry-run, absent UI, repeat and explicit keep; :150–194 adds all three SEC-01 shapes with positive real-run deletion and destination-byte assertions. c1 QA verified ordinary retention, but did not execute these new assertions.
- **code maintainer — pass** (SC-02, SC-03): pinned test-prune-run-evidence.py:197–253 constructs ten hash-bound digests, final BLOCKED, no UI and empty keep; invokes real feature-scoped INV-7 before/after and checks every hash. c1 validator digest's QA assessment records independent genuine base failure and passing fixture. That accepted scope is unchanged. Pinned production change still never deletes absent UI. Matching docstring, ship instructions and decision text describe UI-only deletion and protected records.

## SC outcomes and evidence provenance

- **SC-01 partial, automated:** c1 QA evidence is runs/2026-11-22-02-validate-validator/digest.md and notes/review-harness-qa-c1.md. SEC-01 is repaired by direct pinned inspection at prune-run-evidence.py:129–146; new symlink_dry_run / symlink_prune regressions are present at test lines 168–184. notes/red-first-T-01.md, c1 fix, claims four genuine assertion failures at 70981edd and 25 green checks after repair. Pin SHA-256 values exactly match that receipt's subjects (pruner 3ce3bb40d97f8cb7c3274826f6cc4f3db653f38eadca8de76a0411a5aef02af9; test 7f4274f8e272d112c29405dc4690fce6498bc99d8a6550ecdc8f85f1522cdd23). Identity binding authenticates the claimed subjects, not execution: independent c2 QA verification is not yet available. T-01 owns remediation if its final gate fails; no additional implementation change requested.
- **SC-02 met, automated:** c1 QA specifically independently reproduced lost ten digests and failed post-prune INV-7 on c1724230, with clean-before/empty-keep preconditions passing, then verified fixed behavior. Fixture/assertions remain present unchanged; c2 modification only excludes symlink deletion paths. This is carried c1 verification plus inspected change, not a claim of c2 re-execution.
- **SC-03 met, inspection:** direct git show at the pin and diff from c1724230 confirm unchanged _passing_validate_runs, pin selection, --keep, refusals, CLI, and ship commands/placement. UI-only prose and protected files appear at pruner:12–17 and ship:47–54.

## Decision dispositions

**DEC-238 amend — met, inspection.** Plan row identity: DEC-238 / amend / clause “it deletes engineering, product, reconciliation and distill run directories” / successor D-01. At 88bf039f6ff31edbb1d5a4b2f6620762e3cc095a:.harness/harness/docs/DECISIONS.md:7990–7998, replacement current text explicitly deletes only runs/<id>/ui/, protects run directory/digest.md/state.yaml/.run-identity.json, states #2177 digest-pinning rationale, and retains selectors/refusals. Base-to-pin diff changes only this ship clause; Abandon/INV-51 at :7986–7989 and later pin/prototype clauses are unchanged. Pinned DECISIONS-INDEX.md:232 still resolves DEC-238 @7978 with updated tags; subsequent anchors shift by the two added source lines. Owner: T-01. No partial or unmet disposition. All other decisions_affected rows are keep and are intentionally not graded.

## Scope and open questions

Both perspectives trace through T-01 to all three SCs. Pin contains remediation commit e51277a4ce11c91f2252026ae4dd6e0fbf12a503 (ancestry exit 0). Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent at the pin; no substitute guidance used. No scope change or severity re-grading. Open questions: none. Final QA should supply independent current-pin automated evidence, particularly the five symlink assertions, before SC-01/operator can be promoted to met/pass.
