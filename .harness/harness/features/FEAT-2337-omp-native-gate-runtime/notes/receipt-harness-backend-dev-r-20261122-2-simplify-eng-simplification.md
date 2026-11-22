# Simplification receipt — FEAT-2337 plan surface (flag-only)

BLUF: 3 low findings, all plan-surface restatement drift. No dead references (all `files:` anchors resolve in the worktree: drive, check_self_grading, run_bug919_qa_matrix_cases, discover_expected, FileLines, manifest, repository). Settled set untouched.

Scope: plan.yaml + BRIEF.md (pending). Angle: angle-simplification.md. No execution.

## S-1 (low) — benchmark acceptance spec stated in three places
- plan.yaml T-01 intent (~l.295-310): 3 warmups, 15 alternating pairs, 0.75, idle host, evidence fields; T-03 intent (~l.537-541): re-states "idle host, no concurrent suites, exit 0, ratio <= 0.75, retain samples/medians/identities"; BRIEF SC-04 states it a third time.
- Cost: thresholds/protocol can drift on a later edit (e.g. 0.75 or pair count changed in one place).
- Alternative: T-03 keeps only "QA runs `--benchmark` at review_sha per SC-04/T-01 and persists stdout under its run"; protocol lives in SC-04 (+ T-01 build detail).

## S-2 (low) — "source SHA vs installed pre-existing hook; focused modes never replace full suites; 55s/60s" repeated in T-01, T-02, T-03 (and BRIEF Verification gaps)
- plan.yaml T-01 ~l.312-316, T-02 ~l.416-420, T-03 ~l.527-534; BRIEF "Verification gaps" l.52.
- Cost: four copies of one rule, each slightly different wording ("Label candidate source SHA separately" / "Source execution ... is not evidence" / "Record invocation-time launcher path/version/hash"); an edit to one leaves the others contradicting.
- Alternative: keep the identity-labelling rule once (BRIEF gap + T-03 docs statement, where the guidance is landed); T-01/T-02 keep only their per-task verify budget line.

## S-3 (low) — "new/changed Python test functions grade >= 3, no new exemptions" in T-01, T-02, T-03 and SC-08
- plan.yaml T-01 ~l.292, T-02 ~l.413-414, T-03 ~l.481-486; BRIEF SC-08.
- Cost: T-03's cumulative `--feat2337` check is the enforcement; per-task restatements add no gate and can drift from it (e.g. different bar wording).
- Alternative: T-01/T-02 say only "tests graded by T-03 --feat2337 (SC-08)".

Not flagged (checked): D-01/D-02 vs decisions_affected rows (consistent; DEC-255 new, not in affected by design); 30 s vs 30000 ms (same fact, consistent); SC-10 deletion list matches T-02 deletion list; lane rows vs task execution_mode (required literal resolution, DEC-179).
