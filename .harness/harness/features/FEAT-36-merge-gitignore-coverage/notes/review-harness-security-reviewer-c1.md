# Security review — FEAT-36 — c1

**PASS.** The exact delta is in scope because it adds subprocess, filesystem, environment, configuration, and human/machine-interpreted record surfaces. No exploitable security regression is introduced. The corrected mutation fixture improves the reliability of a security-control proof without changing either production guard; the diagnostic substring weakness remains a non-security correctness advisory.

## Pin and authority

- Base: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`
- Review SHA: `df23bdaa7113700977ec43e617e293c854c0854e`
- Reviewed range: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..df23bdaa7113700977ec43e617e293c854c0854e`
- Pin verification: `git rev-parse df23bdaa7113700977ec43e617e293c854c0854e^{commit}` resolved exactly to the requested review SHA. Inspection began with worktree HEAD at `4ac60a2bab8c94b57388513af4ecb7dbc5d638ae`, not the review SHA; HEAD was not moved and nothing was graded against HEAD. All change evidence came from the explicit immutable range.
- Authority inspected: approved `BRIEF.md` REQ-01–REQ-05 / SC-01–SC-06; approved `plan.yaml` D-01, D-02 and T-01; c0 code, QA, and security reviews; the c0 validator digest; the engineering MF-01 receipt and fix digest.

## Threat-surface census

The pinned diff contains 43 paths.

### Executable and repository configuration — scoped in

- `.agents/skills/harness/bin/test-merge-gitignore.py` — new environment-selected executable, list-form subprocess argv, captured output, canonical repository input, and temporary-filesystem writes.
- `.agents/skills/harness/bin/test-bash-write-guard.py` — changed isolated child-process environment and copied/mutated temporary fixture; no production hook change.
- `.agents/skills/harness/bin/run-unit-tests.sh` — fixed test registration only; no new shell interpolation, input parsing, or privilege decision.
- `.harness/harness.json` — fixed integration-detection literal only; no command, credential, authorization, or network change.

### Feature control records — scoped in for configuration integrity and disclosure

- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/BRIEF.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/STATE.md`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/feature.json`
- `.harness/harness/features/FEAT-36-merge-gitignore-coverage/plan.yaml`

These are repository-authored requirements/state, not newly accepted lower-trust payloads. They introduce no secret, executable interpolation, auth grant, URL, dependency, or cross-tenant data. The reviewed commit's `feature.json` records the prior c0 pin `ce29a059e37af5133ae5b4f87df6f622ed966a92`; the c1 review did not trust that lagging in-commit record and instead resolved the externally supplied immutable SHA above. No review-scope confusion resulted.

### Evidence records — disclosure/provenance sweep only

- Notes: `check-state-build-boundary.md`, `github-sync-build.md`, `github-sync-validate.md`, `handoff-build.md`, `handoff-plan.md`, `qa-T-01.md`, `receipt-harness-dev-ops-T-01-c0.md`, `receipt-harness-dev-ops-plan-simplify-altitude.md`, `receipt-harness-dev-ops-plan-simplify-efficiency.md`, `receipt-harness-dev-ops-plan-simplify-reuse.md`, `receipt-harness-dev-ops-plan-simplify-simplification.md`, `receipt-harness-dev-ops-review-fix-eng.md`, `receipt-harness-dev-ops-simplify-altitude.md`, `receipt-harness-dev-ops-simplify-efficiency.md`, `receipt-harness-dev-ops-simplify-final-suites.md`, `receipt-harness-dev-ops-simplify-reuse.md`, `receipt-harness-dev-ops-simplify-simplification.md`, `review-harness-code-reviewer-c0.md`, `review-harness-qa-c0.md`, `review-harness-security-reviewer-c0.md`, and `review-harness-ui-reviewer-c0.md`, all under `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/`.
- Run records: `plan-product/{digest.md,state.yaml}`, `plan-simplify-eng/{digest.md,state.yaml}`, `qa-validator/{digest.md,state.yaml}`, `review-fix-eng/{digest.md,state.yaml}`, `review-validator/{digest.md,state.yaml}`, `simplify-eng/{digest.md,state.yaml}`, and `t01-eng/{digest.md,state.yaml}`, all under `.harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/`.

All 35 evidence paths are added review/history output rather than executable product logic. A full changed-path credential/local-path sweep found no secret-shaped value, token, private key, authorization header, or user-home path; the records contain feature evidence and public repository issue identifiers only. No CSV/spreadsheet export, template evaluation, or newly trusted artifact instruction path is introduced.

## OWASP and STRIDE assessment

- **Environment / subprocess (Tampering, Elevation):** `MERGE_GITIGNORE_BIN` can select the test executable, but only the actor already controlling the test process environment can set it. That actor already controls test execution, so the seam grants no additional privilege. Invocation is list-form argv with `shell=False` behavior (`test-merge-gitignore.py:18-23`); project paths and `--check` are not shell-interpreted. The selected executable is resolved to a path before use.
- **Filesystem / input validation (Tampering, DoS):** all new merge cases author their roots and regular `.gitignore` files under `TemporaryDirectory`; the explicit-root case uses an absolute internally authored path and separately checks the caller directory (`test-merge-gitignore.py:32-123`). The canonical rules are bounded repository content, not user input. There is no deletion, archive extraction, deserialization, or persistent user-project write in the new code.
- **Mutation-fixture environment (Tampering, Repudiation):** the c1 change sets `PYTHONDONTWRITEBYTECODE=1` only for both subprocesses in `_both_routes` (`test-bash-write-guard.py:465-478`). The copied module and payload remain isolated in a temporary tree. This prevents a same-size/same-mtime stale `.pyc` from substituting baseline behavior for mutated source; it neither broadens a guard permission nor changes production hook dispatch.
- **Configuration (Tampering):** runner and detector additions are exact repository-authored literals. No user-controlled glob, command, package, permission, or auth policy was added. The two lists continue to be compared by the pre-existing kind cross-check.
- **Output / disclosure (Information Disclosure, Repudiation):** the new subprocess captures stdout/stderr and successful test output prints only fixed case names and counts. Failure messages can contain fixed canonical rules or randomized temporary paths, not project data or credentials. Human-interpreted Markdown/YAML/JSON records contain no formula-export surface or secret material.
- **Auth, SSRF, dependencies:** no authentication or authorization decision, network request, redirect, URL, dependency, lockfile, package, credential, or cross-user response changed.

## c0 dispositions

- **F-01 / MF-01 — closed, security disposition: not a vulnerability.** The mandatory matrix failure was a real reliability defect: equal-size source mutation inside one timestamp tick could reuse baseline timestamp-validated bytecode and yield `(0,0)`. That failure was fail-loud—the mutation assertion failed and blocked review—rather than a green bypass of a production security guard. The pinned correction forces source import in both isolated children, retains the required `(2,2)` assertion, and changes no production hook. Engineering owns the fix and its receipt records the exact required matrix passing; QA alone owns acceptance of that execution evidence. `must_fix` is cleared for security.
- **F-02 — retained advisory, dismissed from security findings.** `rule in result.stderr` can accept a fabricated longer diagnostic such as `.claude/worktrees/NOT-THE-RULE`. This is a genuine `med` test-resilience/correctness gap owned by Engineering/harness-dev-ops, but there is no describable lower-trust actor, privilege gain, data access, or injected output execution. It does not change `.gitignore`, the production utility, or a security decision. Exact bullet-set comparison remains an advisable future code-quality improvement, not a security ship gate.

## Assessed and dismissed / scoped out

- `merge-gitignore.sh` is byte-identical across the exact pins (`git diff --exit-code` produced no hunk). Its project-supplied `.gitignore` symlink behavior can redirect the fixed append into another user-writable file, and its final unquoted `$missing` report can glob-expand caller-CWD names. Those are pre-existing, unmitigated utility behaviors, not introduced or newly reachable in this delta; every new fixture uses a test-authored regular file and captured output. They are recorded here rather than misreported as FEAT-36 findings.
- The `MERGE_GITIGNORE_BIN` override is not an arbitrary-execution vulnerability: its only setter is already authoritative over the standalone test's environment, and the plan explicitly approves it for controlled mutants.
- Temporary path disclosure, resource exhaustion, SQL/NoSQL injection, path traversal from external input, template injection, spreadsheet formula injection, SSRF, open redirect, session/auth failures, PII leakage, vulnerable dependencies, and cross-tenant access were assessed and have no introduced mechanism in the pinned range.
- UI behavior and QA matrix execution are outside this security review. Per assignment, no tests, builds, linters, or formatters were run.

## Findings and disposition

New security findings: **none**. `severity_max: info` because the diff was scoped in and assessed. `must_fix: []`. `open_questions: []`.

Exact files touched by this reviewer: `.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-c1.md`.
