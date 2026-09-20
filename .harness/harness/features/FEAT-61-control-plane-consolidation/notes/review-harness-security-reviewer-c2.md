# Security review — FEAT-61 control-plane consolidation — c2

**PASS.** The immutable range `066638e8acf68b47e74637006a01c8823cff939c..f3825ca1dcb1d5bb6ff6e62b876988ebd46ebb08` is security-scoped **in** because it changes untrusted JSON parsing, authorization-adjacent checkout binding, dynamic repo-local module execution, lifecycle validation, and gate configuration. OWASP injection, auth, secrets, exposure, validation, dependency, SSRF/redirect and STRIDE were assessed. No exploitable security regression was found; `severity_max: none` records no finding on an assessed security surface, not a scoped-out review.

## Measured threat review

- **Tampering / elevation — checkout binding, mitigated.** Feature-artifact paths remain slash-bounded and anchored; the shared predicate resolves the expected linked worktree and rejects a target outside it (`.claude/skills/harness/bin/harness_boundary.py:247-280`). Containment and worktree legitimacy use resolved paths plus `commonpath`, not string prefixes (`harness_boundary.py:325-330`, `harness_boundary.py:795-869`). Extraction makes the Write/Edit and Bash routes share the same decision without expanding any grant.
- **Tampering / injection — strict JSON, mitigated.** The canonical decoder rejects duplicate keys at every nesting depth and rejects `NaN`/`Infinity` (`.claude/skills/harness/bin/artifact_accessors.py:21-48`); feature and harness readers retain mapping-shape validation (`artifact_accessors.py:67-81`, `artifact_accessors.py:109-130`). Hook and GitHub payloads now cross the same decoder (`artifact_accessors.py:431-449`). This tightens rather than weakens the input boundary.
- **Elevation / code execution — dynamic loading, no capability delta.** `load_repo_module` executes only caller-supplied fixed repo-local paths, checks the spec/loader, restores prior registration on failure, and re-raises the original exception (`.claude/skills/harness/bin/harness_boundary.py:283-322`). All migrated callers previously executed those same repository files; an actor able to alter them already controls the gate code.
- **Tampering / availability — lifecycle values, mitigated.** The single table partitions every station, and unknown/non-string values raise rather than fall through (`.claude/skills/harness/bin/factory_config.py:43-95`). The post-c1 change derives approval resume states from `ACTIVE_STATIONS` minus `plan`; it neither accepts a value outside the signed vocabulary nor creates a new trust boundary (`.claude/skills/harness/bin/plan-merge.py:2025-2031`). The accompanying route lock is static repository validation, not an attacker-facing interpreter.
- **Elevation / repudiation — policy keys, no disabled control.** Only the consumed `review` policy remains; removed `qa_gate`, `uat`, and `merge` keys had no readers. Missing or invalid `review` remains rejected by `gate_policy.py`; no authorization moved client-side.
- **Secrets / disclosure / exports / requests, clean.** The full changed-path census and added lines contain no credential, private key, auth header, token-bearing URL, PII log, export/spreadsheet sink, dependency addition, user-controlled URL request, or redirect. Secret-shaped values are detector controls/comments, not credentials. Existing `gh` subprocess/request sites receive list-form argv and were not newly introduced by this range.

## Per-file census

- **Runtime/security-relevant (20), inspected:** `.claude/skills/harness/bin/{artifact_accessors.py,bash-write-guard.py,board_lifecycle.py,branch-create-gate.py,check-domain.py,check-plan-routes.py,check-state.py,factory_config.py,feature_json_write.py,gate_policy.py,gh-close-gate.py,gh-sync.py,gh_board.py,handoff_done_when.py,harness_boundary.py,merge-gate.py,plan-merge.py,plan-sign-gate.py,run-unit-tests.py,worktree_terminal.py}`.
- **Configuration/templates (3), inspected for policy and secrets:** `.harness/harness.json`, `.claude/skills/harness/templates/{harness.json,examples/harness.kaya-ai.json}`.
- **Doctrine/feature records (28), non-executable; inspected for trust claims and exposure:** `.harness/glossary.md`, `.harness/harness/docs/{DECISIONS.md,DECISIONS-INDEX.md}`, and all 25 changed files under `.harness/harness/features/FEAT-61-control-plane-consolidation/` (BRIEF, STATE, feature JSON, plan, and notes). No secret or executable boundary was added there.
- **Verification-only (18), inspected for sensitive fixtures and claimed boundary cases:** `tests/integration/canonical-reader-classification.json`, `tests/integration/fixtures/feat61-check-plan-routes-lifecycle.receipt.json`, the 10 changed `tests/integration/test-*.py` files, and the 6 changed `tests/unit/test-*.py` files in the pinned census. No production authority or committed secret was introduced.

No findings. `must_fix: []`. Per dispatch, no tests, formatters, linters, or unrelated probes were run. The trusted VAL-03 operator ruling was not reopened.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned OWASP/STRIDE review found no exploitable security regression across the 69-path consolidation diff."
  in_scope: true
  scope_reason: "The diff changes untrusted JSON readers, checkout/write authorization boundaries, repo-local dynamic loading, strict lifecycle validation, and gate policy; all 69 changed paths were censused and the post-c1 delta was re-measured at f3825ca1dcb1d5bb6ff6e62b876988ebd46ebb08."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "untrusted artifact and hook JSON -> strict parser", stride: T, mitigated: true }
    - { boundary: "agent-selected feature artifact path -> authorized linked checkout", stride: E, mitigated: true }
    - { boundary: "repository-controlled fixed path -> Python module execution", stride: E, mitigated: true }
    - { boundary: "plan/task station value -> lifecycle and approval decisions", stride: T, mitigated: true }
    - { boundary: "configuration policy -> review gate decision", stride: R, mitigated: true }
    - { boundary: "changed files/logs/fixtures -> operators and external systems", stride: I, mitigated: true }
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-61-control-plane-consolidation/notes/review-harness-security-reviewer-c2.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-61-control-plane-consolidation/.harness/harness/features/FEAT-61-control-plane-consolidation/notes/review-harness-security-reviewer-c2.md
```
