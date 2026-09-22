# FEAT-1821 T-03 security fix review c1

**BLUF:** PASS. The seven-file T-03 delta is security-relevant because it recursively deletes/copies fixture paths, traverses source, executes Python/Git, serves a copied project, and writes browser evidence/results. At `a71ea2a9c294aa1326f101493a2a5b6709a25334`, none gives an untrusted actor a new capability. The four original findings remain partly open as browser-product or verification-lane completeness issues, but none is a security must-fix.

## Original findings, security disposition

1. **Objective predicates — resolved from the security lens; product failure remains.** The predicates now execute against the served browser surface. The reported missing production `<header>` is an objective FEAT-53/browser-product failure, not injection, authorization, exposure, or fail-open behavior in T-03 (`feat-53.e2e.spec.ts:135-229`; send-back receipt finding 1).
2. **C3 keyboard — resolved from the security lens; product/fixture failure remains.** The test drives real focus and activation transitions. Zero KPI links aborts the predicate and the run fails rather than accepting incomplete work (`feat-53.e2e.spec.ts:81-165`; send-back receipt finding 2). No privilege boundary depends on these focus transitions.
3. **Copied fixture/interactions — resolved for path safety; verification omission remains.** `rmSync` targets the module-derived constant `client/test-results/fixture-project-a`; copy sources and destinations are module-derived constants, and state IDs are a closed literal table (`fixture.ts:5-27`). No environment, manifest, page, or fixture content controls the deletion/copy destination. The sidecar/runtime-consumption concern in the send-back receipt is a T-03 verification implementation omission, not traversal or unsafe deletion.
4. **Source/reporter/parser — resolved from the security lens; negative-proof omission remains.** Source traversal begins at constant `client/src`; directory entries are joined beneath that tree and no user path enters it (`feat-53.e2e.spec.ts:7,41-64`). `execFileSync` uses fixed executables and list-form argv for both Python and Git (`ui-manifest.ts:11-13`, `ui-reporter.ts:42`), so manifest content cannot become shell syntax. Unknown tests, duplicate records, missing records, title mismatch, absent evidence, parser exceptions, and failed Playwright status do not produce a passing summary (`ui-reporter.ts:18-43`). The absent negative mutation evidence is a verification-lane proof omission, not an exploitable fail-open path established by this diff.

## New security observation

- **Low, substance, T-03:** `HARNESS_UI_FEATURE` and `HARNESS_UI_RUN_ID` are interpolated into repository-relative evidence/result paths without segment validation (`feat-53.e2e.spec.ts:9-20`; `ui-reporter.ts:8-11`). A focused path-semantics probe showed `feature=../../outside, run=../../target` resolves to `/repo/.harness/target/ui/results.json`. The actor must already control the test process environment and therefore already has same-user filesystem/command capability; no privilege delta or cross-user exploit is demonstrated. T-01/QA is also contractually responsible for binding these values. This is low-severity defense-in-depth and does not gate T-03.

## Threat model and per-file census

- **Filesystem boundary (T/I): mitigated.** Fixture deletion/copy roots are code-derived constants; evidence has validated RIFF/WEBP bytes before write. Environment-derived report paths are not contained, but the only demonstrated actor is the invoking operator with equivalent filesystem capability.
- **Process boundary (T/E): mitigated.** Python and Git use list-form argv with fixed executable/arguments. Playwright's shell-form web-server command interpolates only the code-derived fixture path; a checkout-path metacharacter requires control over the invocation location, which already supplies command execution.
- **Browser/server boundary (S/I): mitigated.** `reuseExistingServer: false` prevents accepting a pre-existing process on port 8972; base URL is loopback and `serve.py` receives the deterministic copied root (`playwright.config.ts:7-25`).
- `package.json`, `package-lock.json`: exact-version Playwright/Axe development dependencies; no credentials or lifecycle script introduced.
- `playwright.config.ts`: fixed loopback server and fixed projects; no externally supplied URL.
- `fixture.ts`: constant-root recursive deletion/copy; no attacker-controlled path segment.
- `ui-manifest.ts`: fixed parser/design paths and non-shell argv; JSON parse fails closed.
- `ui-reporter.ts`: environment-derived artifact path noted above; accounting failures make summary failed.
- `feat-53.e2e.spec.ts`: constant source root, fixed routes, validated WebP output; browser/product failures abort downstream checks rather than pass.

No secrets, credential-shaped additions, SSRF-capable URL, authorization surface, cross-user data response, or new high/critical dependency signal was found in the signed seven-file diff.
