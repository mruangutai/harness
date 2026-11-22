# BUG-2253 security c6 — PASS

No new exploitable refusal bypass or privilege change. Two nonblocking advisories remain; no must-fix.

Reviewed immutable base `3dd8bb677bb2936361e3952030fc24f15bf9afc6` through pin `3aa17de30917ca7eee9d5edb6ebc944e6dc45236`, excluding later record-only `d21cf97f`. Run: `2026-11-22-05-validate-validator`. Read BRIEF, plan, prior validation digest, round-3 ruling and simplify record. Product spec/decisions/architecture are absent as explicitly recorded; no substitute requirements assumed.

## Measured scope and boundaries

- **IN:** `.claude/skills/harness/bin/validate-digest.py` — captured runner output enters human diagnostics (SC-01). `_is_failed_file_line` only adds names; captured same-name PASS cannot erase the enclosing header's name. `_run_pool_mutated_indexes` retains mutation-note adjacency. `_print_independent_run` changes diagnostics only; `check_qa_matrix_claim` still returns 2 for nonzero completed runs (`:2480–2550`). Forged summary text never supplies acceptance authority. Tail remains `lines[-20:]`.
- **IN:** `tests/integration/test-validate-digest.py` — local executable fixtures, six timeout sites and process termination (SC-02). Shared 30s constant is test-only. Fixture source is repository-authored, emitted values use repr, and executables live under a private temporary directory. Watchdog selects only this test process's direct children, excludes its own ps child, and stops/joins in finally; probes run sequentially (`_bug2253_children`, `_bug2253_watchdog`, `_bug2253_block_probe`). This is containment of authored direct-child fixtures, not a promise to sandbox arbitrary descendant trees.
- **OUT of executable-security review:** all 71 remaining paths in the measured 73-path diff: feature specifications, metadata, approvals, historical assessments, run records and receipts. No executable policy or new dependency there. Full-diff credential-pattern sweep found only null token counters and explanatory prose, not an introduced credential. No new network, auth, cross-user data or dependency surface.

## Findings retained, not blockers

1. **Low / substance / accepted diagnostic attribution ambiguity:** a test author can echo a header for `victim.py` then `FAIL victim.py`, or echo FAIL after a real header of that name, and get a spurious filename listed on a rejected run. The author already executes test code; gain is misleading operator attribution, not acceptance or additional privilege. Round 3 explicitly accepts this over-listing. Boundary runner text → human diagnosis remains spoofable (STRIDE T/R).
2. **Info / substance / unchanged, outside patch:** `_reverify_suite` returns None for missing runner, spawn error or timeout, and `check_qa_matrix_claim` accepts with a warning (`:2431–2480`). If the runner cannot launch, an unconditional QA PASS is not independently verified. Base and pin have identical policy; BRIEF excludes changing it. Boundary runner availability → QA acceptance remains unmitigated (STRIDE T). No scope expansion requested.

## Evidence and limits

Inspection only: no tests, probes, grader, builds, lint or formatter executed. Supplied `green-c4.txt/stdout` reports 17 selected cases pass (10.82s), including same-name PASS and delayed/never-ready children, plus full-file exit 0 (23.17s), on fix `3c6fb908`; code equivalence to pin is supplied, not independently executed here. `red-c4.txt` records reconstructed exact-base subjects; `discriminate-c4` isolates the prior gate's echo failure. Main supplies grading exit 0 / PASSING 29 / no FAIL. These are not this reviewer's execution receipts. Unit-kind absence (#2281) stays outside patch; neither selected nor full-file evidence establishes whole integration-kind coverage.

Open questions: none. Required literal verification remains QA-owned: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases`.
