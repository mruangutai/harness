# Security review — FEAT-1821-ui-verification-lane — c0

Pinned review: `23097d785fc6614686b3c38590df7934ed2e25d3..711ba16227eda39ddb397ed574e4ca199fbc5984` (review SHA `711ba16227eda39ddb397ed574e4ca199fbc5984`).

## BLUF

PASS. The diff is security-scoped because it centralizes browser screenshot capture and writes interpreted evidence to repository paths, but it preserves the prior write destination and makes malformed/duplicate capture fail closed. No exploitable capability delta, credential exposure, command injection, browser/server exposure, artifact traversal available to a lower-trust actor, or silent-success path was found. The 22 expected FEAT-53 predicate failures are product RED and are not security findings.

## Surface census

- `.claude/skills/harness/bin/dashboard/client/ui-evidence.ts:6-27` — **in scope**: shared browser-to-filesystem evidence boundary. `HARNESS_UI_FEATURE`, `HARNESS_UI_RUN_ID`, project/check/label values compose a path; screenshot bytes are written and attached. The helper rejects empty/non-RIFF/non-WEBP output and existing destinations before write (`:14-26`), so malformed capture and duplicates fail closed. Feature/run environment values are operator-controlled; they are not a new lower-trust boundary introduced by this extraction, and the same interpolation existed in each replaced helper.
- `.claude/skills/harness/bin/dashboard/client/feat-53.e2e.spec.ts:1-4,82-103,127` — **in scope**: adopts the identical shared capture path for inspection/execution evidence; caught test failures are rethrown after capture, so capture cannot convert a failed predicate into success.
- `.claude/skills/harness/bin/dashboard/client/e2e/colour-placement.e2e.spec.ts:1-3,55-60` — **in scope**: helper substitution only; capture remains in `afterEach` and is hard-failing.
- `.claude/skills/harness/bin/dashboard/client/e2e/contrast-hatch.e2e.spec.ts:1-3,34-39` — **in scope**: same disposition.
- `.claude/skills/harness/bin/dashboard/client/e2e/geometry.e2e.spec.ts:1-3,21-26` — **in scope**: same disposition.
- `.claude/skills/harness/bin/dashboard/client/e2e/tables-a11y.e2e.spec.ts:2-4,22-27` — **in scope**: same disposition.
- `.harness/harness/features/FEAT-1821-ui-verification-lane/STATE.md:1-8` — scoped out: workflow state only; no secret or untrusted payload.
- `.harness/harness/features/FEAT-1821-ui-verification-lane/feature.json:150-160` — scoped out: run ledger metadata only; no credential-shaped additions.
- `.harness/harness/features/FEAT-1821-ui-verification-lane/runs/simplify-eng/.run-identity.json:1` — scoped out: local run identity metadata; no secret.
- `.harness/harness/features/FEAT-1821-ui-verification-lane/runs/simplify-eng/digest.md:1-37` — scoped out: review record/pointers only; no secret or executable content.
- `.harness/harness/features/FEAT-1821-ui-verification-lane/runs/simplify-eng/state.yaml:1-133` — scoped out: orchestration state only; no credential-shaped content.

## OWASP / STRIDE disposition

- Injection/path traversal: no shell call or dependency/install change in the diff. Path components can be influenced only through operator environment or repository-authored manifest/project data—actors already able to write in the checkout—and preserve the pre-diff destination semantics; no privilege delta.
- Authentication/authorization/SSRF: no route, auth, redirect, outbound request, or server-binding change.
- Secrets/data exposure: screenshots are deliberate UI evidence. The exercised dashboard is bound to `127.0.0.1` and fixture-backed (`playwright.config.ts:12,23-26`); this diff neither broadens content nor changes evidence publication. No credentials were added to source or run records.
- Input validation/fail-open: empty or malformed screenshot bytes and duplicate labels throw before attachment/write completion (`ui-evidence.ts:14-26`); original test failures are rethrown after evidence capture (`feat-53.e2e.spec.ts:82-104`).
- Dependencies: none added or changed.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned diff centralizes screenshot evidence without adding an exploitable trust-boundary or fail-open path."
  in_scope: true
  scope_reason: "The diff writes browser-rendered evidence to repository paths and therefore crosses browser/filesystem and interpreted-artifact boundaries; all 11 changed paths were censused, and the security-relevant six preserve prior path semantics while hard-failing malformed or duplicate evidence."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "browser CDP screenshot -> repository WebP evidence (ui-evidence.ts:10-27)", stride: "T|I", mitigated: true }
    - { boundary: "operator environment/manifest identifiers -> evidence path (ui-evidence.ts:7-16)", stride: "T|E", mitigated: true }
    - { boundary: "test failure/capture failure -> reporter result (feat-53.e2e.spec.ts:82-104,127-129)", stride: "R|T", mitigated: true }
    - { boundary: "fixture-backed localhost dashboard -> committed visual artifact (playwright.config.ts:12,23-26)", stride: "I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-security-reviewer-c0.md
```
