# Security review — FEAT-64 c1

**PASS.** Immutable range `a4a3d7f8e9b91181fb6cc3ae058df8e02275d983..50dd75c4b97a51f6a3fe7ffb5f27d3c5e2889a31` is security-scoped **in**: it changes untrusted YAML/JSON/config and GitHub-response handling, subprocess boundaries, repository paths, exception rendering, and fail-open behavior. Inspection found no exploitable regression.

## Canonical changed set

QA supplied this ordered 59-path identity; the pinned diff inspected here used exactly this set:

```text
.claude/skills/harness/bin/board-station.py
.claude/skills/harness/bin/check-omp-port.py
.claude/skills/harness/bin/check-plan-routes.py
.claude/skills/harness/bin/check-skill-weight.py
.claude/skills/harness/bin/factory_decompose.py
.claude/skills/harness/bin/factory_gh.py
.claude/skills/harness/bin/feature_schema.py
.claude/skills/harness/bin/gh-sync.py
.claude/skills/harness/bin/gh_cost_log.py
.claude/skills/harness/bin/handoff_done_when.py
.claude/skills/harness/bin/handoff_policy.py
.claude/skills/harness/bin/harness_boundary.py
.claude/skills/harness/bin/harness_yaml.py
.claude/skills/harness/bin/post-merge-sweep.py
.claude/skills/harness/bin/run-unit-tests.py
.claude/skills/harness/bin/run_identity.py
.claude/skills/harness/bin/upgrade-config.py
.claude/skills/harness/bin/worktree_terminal.py
.harness/harness/features/FEAT-64-broad-exception-libs-tools/BRIEF.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/STATE.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/feature.json
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/build-divergences.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/byte-evidence.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/handoff-plan.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/red-first-receipts.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-plan.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools-goalcheck-validate-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-broad-exception-libs-tools.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-c0-resolution.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/research-FEAT-64-gc-64-02-evidence-kinds.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-code-reviewer-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-code-reviewer-plan-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-qa-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-security-reviewer-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-ui-reviewer-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-ui-reviewer-plan-c0.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/plan.yaml
.harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/validate-validator/digest.md
.harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/validate-validator/state.yaml
tests/integration/test-board-lifecycle.py
tests/integration/test-board-station.py
tests/integration/test-check-omp-port.py
tests/integration/test-check-plan-routes.py
tests/integration/test-check-skill-weight.py
tests/integration/test-factory-decompose.py
tests/integration/test-gh-sync-ship.py
tests/integration/test-harness-yaml.py
tests/integration/test-post-merge-sweep.py
tests/integration/test-run-unit-tests-layout.py
tests/integration/test-upgrade-config.py
tests/integration/test-worktree-terminal.py
tests/unit/test-broad-catch-census.py
tests/unit/test-factory-gh.py
tests/unit/test-feature-schema-build-entry.py
tests/unit/test-gh-cost-log.py
tests/unit/test-handoff-done-when.py
tests/unit/test-handoff-policy.py
tests/unit/test-harness-boundary.py
tests/unit/test-run-identity.py
```

## Measured self-scope and threat audit

- **Injection / subprocess:** `factory_gh._launch_gh` and `post-merge-sweep` retain list-form argv, closed stdin, and no shell. No SQL/template/export/formula sink, redirect, or user-controlled network destination was added. GraphQL option names continue through `json.dumps`; the diff does not weaken that escaping.
- **Inputs / paths / fail posture:** narrowed catches around manifests, fleet, plans, feature JSON, frontmatter, and YAML retain their typed read/parse/shape outcomes. `handoff_done_when._read_target` containment and size checks are unchanged. Plan memos are cleared at public entry and keyed by resolved path. No auth or authorization decision changed.
- **Secrets / disclosure:** credential-pattern sweep over the full pinned diff found no added bearer token, authorization header, API key, client secret, password assignment, private key, or credential-bearing fixture. Malformed GitHub success bodies become `GhError` without rendering the body; captured streams remain debugger attributes as before. The new launch-failure diagnostic can expose only the local operator-selected `FACTORY_GH` path and OS error to that operator.
- **Fail-open / availability:** narrowing makes unrelated programming defects escape instead of becoming success or silence. Expected OSError/parser/subprocess classes remain caught at their owning seams. `_as_repo_module_failure` preserves the prior conversion and chains the cause. `hook_guard` is the only new broad fail-open renderer, but the pinned census and tests establish zero callers, so it has no actor or capability delta in this review; FEAT-65 must reassess when wiring it.
- **Dependencies / SSRF / auth / tenancy:** no dependency declaration, redirect, request URL, session, credential, tenant selector, or response-field expansion changed.

## c0 remedy closure independently checked

- **CR-64-01 / GC-64-03:** `git diff --exit-code` proves `.claude/skills/harness/bin/board_lifecycle.py` byte-identical between baseline and pin. Open defect `#1897` exists and describes the one-argument `GhError`/`TypeError`. Ledger B2 records the measured baseline stderr versus the pinned propagated `TypeError`; the reverted out-of-scope repair is absent.
- **GC-64-01:** `byte-evidence.md` gives per-suite raw and normalized stdout/stderr digests and verbatim zero-context differing lines. `build-divergences.md` §A accounts for exactly eight removed lines (one retitle, six count/progress lines, one corpus count), with replacements and rulings; all other differences are additions or normalized tempfile paths.
- **GC-64-02:** pinned BRIEF separates shared-library SC-03/unit from tool SC-07/integration and route SC-06/integration from handoff SC-08/unit. Pinned plan traces SC-07 from T-02/T-03 and SC-08 from T-01/T-03; approval is revoked-and-re-signed `2026-09-23` in both plan and BRIEF.
- All six required shared artifacts were inspected independently: `runs/validate-validator/digest.md`, `runs/build-main-direct/digest.md`, `notes/red-first-receipts.md`, `notes/byte-evidence.md`, `notes/build-divergences.md`, and `notes/research-FEAT-64-gc-64-02-evidence-kinds.md`.

## Findings and dismissals

Findings: none.

- **Dismissed — future hook bypass/data disclosure:** `hook_guard(fail="open")` prints exception text and returns 0. It has zero callers at this pin, so no user can reach it and no enforcement or information-disclosure capability changes. Re-audit at FEAT-65 wiring.
- **Dismissed — propagated `board_lifecycle` TypeError:** narrowing `_ship_audit` exposes pre-existing defect #1897 instead of swallowing it. The actor already needs operator control of malformed board configuration, gains no privilege or foreign data, and the behavior is the signed fail-loud objective; the underlying repair is correctly outside this feature.
- **Dismissed — `FACTORY_GH` executable selection:** the environment already selected the executable before this diff. List argv prevents shell injection; an actor able to set the harness process environment already has equivalent code-execution capability. The delta only types launch `OSError`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The 59-path pinned diff narrows parser, subprocess, path, and error boundaries without an exploitable security regression; all c0 remedies are independently closed."
  in_scope: true
  scope_reason: "The diff processes untrusted config/YAML/JSON and GitHub responses, subprocess argv/status/streams, repository paths, and exception diagnostics, so injection, disclosure, validation, and fail-open review applies."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "config/manifest/YAML/JSON into validators", stride: "T|D|E", mitigated: true }
    - { boundary: "operator environment/argv and GitHub responses into subprocess/parser", stride: "T|I|D", mitigated: true }
    - { boundary: "repository-module failures into gate diagnostics", stride: "I|D|E", mitigated: true }
    - { boundary: "future hook exception into stderr and verdict (precondition absent: zero callers at pin)", stride: "I|E", mitigated: false }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-security-reviewer-c1.md
```
