# Security review — FEAT-36 — c2

**PASS.** The pinned range is security-scoped in because it adds a real subprocess test, an environment-selected executable seam, temporary filesystem writes, path/cwd separation, and captured human-readable diagnostics. No high-severity or must-fix security regression exists. The `f494553` SC-05 amendment strengthens caller/project isolation without adding unsafe behavior.

## Pin and authority

- Base: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`
- Review SHA: `f494553`
- Exact reviewed range: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..f494553`
- Continuity comparison: `df23bdaa7113700977ec43e617e293c854c0854e..f494553`
- Authority: approved `BRIEF.md` REQ-01–REQ-05 and SC-01–SC-06; approved `plan.yaml` D-01, D-02, and T-01; prior `review-harness-security-reviewer-c1.md`; `runs/review-c1-validator/digest.md`.
- Pin discipline: every diff command named the immutable base and review SHA. `git diff --exit-code f494553 -- .agents/skills/harness/bin/test-merge-gitignore.py` returned no hunk before the focused execution, proving the exercised working-tree test matched the review pin.

## Measured path census and c2 delta

The exact base-to-review name-status census contains 59 paths.

- **Executable/configuration, scoped in:** `.agents/skills/harness/bin/test-merge-gitignore.py` (subprocess, environment, paths, temporary files, diagnostics); `.agents/skills/harness/bin/test-bash-write-guard.py` (isolated child environment and mutation fixture); `.agents/skills/harness/bin/run-unit-tests.sh` (fixed test registration); `.harness/harness.json` (fixed integration detector literal).
- **Control records, scoped in for integrity/disclosure:** `BRIEF.md`, `STATE.md`, `feature.json`, and `plan.yaml` under the FEAT-36 feature directory. They contain repository-authored requirements/state, not a new executable or lower-trust input channel.
- **Evidence-only, disclosure/provenance sweep:** every remaining changed path is under the same feature's `notes/` or `runs/`: the 29 named notes from `check-state-build-boundary.md` through `review-harness-ui-reviewer-c1.md`, and both `digest.md` and `state.yaml` for each of `goal-check-fix-eng`, `goal-check-fix-qa-validator`, `goal-check-product`, `plan-product`, `plan-simplify-eng`, `qa-validator`, `review-c1-validator`, `review-fix-eng`, `review-validator`, `simplify-eng`, and `t01-eng`. These 51 paths are non-executable feature evidence. A full exact-range credential-pattern sweep found no private key, bearer authorization, API key, password, secret, or token-shaped value.

Against `df23bdaa`, the only executable/configuration change is `.agents/skills/harness/bin/test-merge-gitignore.py`: the explicit-root case now creates `unrelated-caller/.gitignore`, snapshots its bytes, and replaces an absence-only postcondition with byte equality (`test-merge-gitignore.py:117-126`). The other c2-delta paths are feature state and review evidence, with no command, dependency, auth, or network behavior.

## OWASP/STRIDE assessment

- **Subprocess and environment — Tampering/Elevation:** `subprocess.run` receives list-form argv and does not invoke a shell (`test-merge-gitignore.py:18-23`), so project paths and `--check` cannot become shell syntax. `MERGE_GITIGNORE_BIN` is resolved before invocation. An actor able to set this test-process environment already has authority to select or execute test code; the seam grants no additional privilege and is explicitly approved for controlled mutants by plan T-01.
- **Filesystem, paths, symlinks — Tampering/Information disclosure/DoS:** every project and caller root is authored beneath `TemporaryDirectory`; the SC-05 project and caller are distinct sibling directories, the explicit project root is absolute, and both `.gitignore` objects are regular test-authored files. No fixture uses an attacker-controlled path or symlink, follows a project-provided symlink, deletes data, extracts an archive, or writes a persistent user project. Inputs and outputs are small and bounded. Cleanup remains confined to the temporary root.
- **Caller/project separation — Tampering/Repudiation:** before the subprocess, the requested project target is absent while the caller target contains fixed bytes. Afterward, exit 0 plus existence of `project/.gitignore` proves the requested target changed, while byte equality proves the pre-existing caller target did not. This is materially stronger and non-vacuous compared with merely proving an initially absent caller file stayed absent. It introduces no unsafe behavior: the only new write is fixed fixture data inside the temporary caller directory.
- **Diagnostics — Injection/Information disclosure:** stdout/stderr are captured, not evaluated. Normal output contains fixed case names, canonical ignore rules, and randomized temporary paths; the new assertion message does not print caller file contents. There is no template, CSV/spreadsheet, HTML, SQL, shell, or log-command interpretation surface.
- **Auth, SSRF, secrets, dependencies:** no authentication/authorization decision, user-controlled URL, redirect, network request, credential, dependency, lockfile, or cross-user response changes.

## Continuity and findings

- **F-01 / prior MF-01 remains closed.** The pinned range retains `PYTHONDONTWRITEBYTECODE=1` for both isolated mutation children and changes no production hook. The SC-05 amendment is independent of that mechanism.
- **F-02 remains a non-security `med` advisory, not `must_fix`.** Substring membership can accept a fabricated longer diagnostic such as `.claude/worktrees/NOT-THE-RULE`, but there is no lower-trust actor who gains privilege, data, execution, or a filesystem write from that assertion. An actor controlling `MERGE_GITIGNORE_BIN` already controls the executable run by the test. The weakness can mask a future diagnostic correctness regression; it does not bypass a security decision. Exact emitted-bullet-set comparison remains advisable in later approved work.
- **Pre-existing non-findings:** `git diff --exit-code 0fa8f336e55dc57bca09a9f7df0524a35195ee7e..f494553 -- .agents/skills/harness/bin/merge-gitignore.sh` returned no hunk. Its project-target symlink behavior and final unquoted `$missing` diagnostic expansion therefore remain unchanged and are not newly reachable through the regular-file, captured-output fixtures. They are assessed and dismissed from this feature review, not claimed safe in general.
- **Registration reconciliation:** the actual pinned registry is 23 unit plus 23 integration scripts, 46 total. The c1 digest's 24-integration/47-total sentence was inherited evidence and is incorrect; `qa-T-01-c1.md` records the corrected 23 + 23 execution. This count correction has no security impact.

## Focused verification

`python3 .agents/skills/harness/bin/test-merge-gitignore.py` exited 0 at the pin-matching working tree: all seven named cases passed, including `explicit_project_root_ignores_caller_cwd`; output ended `7 passed; 0 failed`. No formatter, linter, build, unrelated suite, or project-wide test was run.

## Disposition

- In scope: **yes**.
- New security findings: **0**.
- Severity maximum: **info** (scoped in and assessed; `n/a` would be incorrect).
- Must fix: `[]`.
- Open questions: `[]`.
