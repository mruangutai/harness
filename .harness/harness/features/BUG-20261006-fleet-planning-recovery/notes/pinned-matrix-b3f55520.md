# Passing full matrix — b3f55520

Review pin: `b3f5552088c271c2083025ea9e7ff815741c310f`.
Operator authority: `operator-omp-matrix-ruling-2026-10-19.md`, expressly authorizing both kinds once at this pin while preserving the two earlier failed receipts. No automatic retry, Kaya operation, installation, push or merge is authorized.

| Command | Result | Files | Pool wall | Command wall | Full session output |
|---|---|---:|---:|---:|---|
| `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` | exit 0, PASS | 55/55 | 29.44s | 29.59s | artifact 374 |
| `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` | exit 0, PASS | 83/83 | 101.00s | 101.14s | artifact 375 |

Both commands were launched once in parallel from this worktree and completed without source changes. All 282 tracked tooling/test/native-extension/config blobs checked against Git blob hashes match the pin exactly; the signed plan bytes also match the pinned plan. Post-pin files are feature-local operator rulings, receipts and checkpoint metadata, not changed test subjects. Unit output includes 137 passing OMP tests with zero failures. All 138 active unit/integration files passed.

Real runtime smoke separately loaded OMP's actual main-session bundle and both closed fully-required variants. Actual canonical CLI accepted omitted, zero and positive counts and rejected negative, boolean and fractional counts. No live installation or model call was used for that smoke.

Pinned code grading exited 0: raw grade_2, 66 passing, 35 named grade-2 reasons in `build-verification-2026-10-18.md`, zero high and zero ungraded. Four independent final quality-angle follow-ups returned no findings. These results are not whole-feature deployment/UAT certification: T-03 through T-05 remain unactivated and separately gated.

The e9ecbd4c and f9a13cac failed full-matrix receipts remain unchanged. Historical returns, verdicts, timestamps, counts and old remote objects remain unchanged.
