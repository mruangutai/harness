# Security review — FEAT-36 — c3

**PASS.** The pinned change is security-scoped in because it adds an environment-selectable real subprocess test that writes temporary filesystem targets and captures diagnostics. At `be27d99454352e581fdf7cbace20fb52d0f45133`, it introduces no exploitable security defect, high-severity issue, or must-fix item.

## Pin, scope, and file census

Reviewed the immutable range `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..be27d99454352e581fdf7cbace20fb52d0f45133` against approved REQ-01–REQ-05, SC-01–SC-06, plan task T-01, and the operator ruling. The substantive union has no working-tree delta from the pin; the only tracked feature-tree delta from the pin is a one-line `feature.json` trace/status edit, which was excluded from the committed review surface.

- `.agents/skills/harness/bin/test-merge-gitignore.py` — **in scope:** new subprocess, inherited environment, explicit path/cwd handling, temporary files, and captured output.
- `.agents/skills/harness/bin/run-unit-tests.sh` — **in scope:** the new test becomes runner-reachable and inherits the runner environment; the only pinned change is its fixed-name integration registration.
- `.harness/harness.json` — **in scope:** the exact test path is added to integration detection; no command, secret, privilege, or externally supplied value is added.
- `.agents/skills/harness/bin/merge-gitignore.sh` — **in scope, unchanged:** exact-range `git diff --exit-code` was clean. Its filesystem and diagnostic behavior was assessed because the new test executes it, but the fixtures add no new production reachability.
- `notes/operator-ruling-rendered-review-scope.md` — **assessed, no security surface:** repository-authored scope evidence only; no executable content or sensitive value. The ruled-out renderer contrast issue is neither security-relevant nor an FEAT-36 gate.

A credential-pattern sweep over the full pinned range found only the word “token” in prior review prose; inspection found no credential, private key, bearer value, password, API key, or secret fixture.

## OWASP / STRIDE threat analysis

- **Subprocess and shell injection (Tampering/Elevation):** `subprocess.run` receives list-form argv and leaves `shell=False` (`test-merge-gitignore.py:18-23`). Project paths and `--check` therefore cannot be reinterpreted as shell syntax. `MERGE_GITIGNORE_BIN` selects argv element zero after path resolution; metacharacters remain filename characters rather than commands.
- **Environment override trust (Tampering/Elevation):** an actor able to set `MERGE_GITIGNORE_BIN` can choose the tested executable, but this is the operator/CI-authored mutant seam explicitly required by T-01. That actor already controls what executable the test runs and gains no privilege transition. Reopen this conclusion if lower-trust pull-request or user data is ever mapped into that environment variable.
- **Project roots and temporary filesystem (Tampering/Information disclosure/DoS):** every exercised project/caller path and file is test-authored beneath `TemporaryDirectory`; argv values are quoted by list construction, the project root is absolute in the cwd-isolation case, and caller/project targets are distinct regular files. No archive extraction, attacker-controlled symlink, persistent project, unbounded input, or cross-user data is introduced.
- **Diagnostics and logs (Information disclosure/Repudiation):** stdout/stderr are captured as data, never evaluated. Failure output can contain fixed case names, canonical ignore rules, and randomized temporary paths; assertions do not print fixture contents or environment values. A selected executable could print arbitrary data, but the actor selecting it already controls executable code in the same test process trust domain.
- **Registry and runner reachability (Tampering/DoS):** both registrations are fixed repository literals. The existing drift/kind cross-check compares the runner list to `harness.json`; this change adds no runtime interpolation or authorization decision.
- **Auth, SSRF, dependencies, and cross-user exposure:** no route, identity, authorization, URL, redirect, network request, dependency, lockfile, credential, or multi-tenant response changes.

## Findings and advisory disposition

- Scope verdict: **in scope; PASS**.
- Findings: **0**; concrete finding scenarios: **none applicable**.
- Severity maximum: **info**.
- Ranked must-fix: `[]`.
- Advisory: the environment-override closure depends on operator/CI provenance; reopen if lower-trust data can set `MERGE_GITIGNORE_BIN`.
- Assessed-and-dismissed pre-existing behavior: the unchanged shell utility will follow a project-provided `.gitignore` symlink and its final unquoted `$missing` status expansion can expose caller-cwd filenames or distort output. Neither mechanism is introduced or widened here: all new fixtures create controlled regular files, capture output, and run without a privilege boundary. They are not FEAT-36 findings and do not gate this exact diff.
- Focused proof: `python3 .agents/skills/harness/bin/test-merge-gitignore.py` exited 0 with all seven named cases passing (`7 passed; 0 failed`). No formatter, linter, build, unrelated test, or full suite was run.
- Files touched: [`.harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-security-reviewer-c3.md`].
- Open questions: `[]`.
