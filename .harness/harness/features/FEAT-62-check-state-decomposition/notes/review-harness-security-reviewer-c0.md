# Security review — FEAT-62 — cycle 0

BLUF: PASS. The pinned diff is security-relevant because T-01 consumes Git-controlled path bytes and T-03 derives an executable checkout then forwards checker output, but the reviewed paths add no exploitable capability, trust-boundary bypass, secret exposure, or authorization change.

## Scope and evidence

Reviewed exactly `16ee44f0..1380727cc6a866627595a267b9b681fc3f7026bc` (15 paths; 4,892 insertions, 1,986 deletions).

- `.claude/skills/harness/bin/check-state.py` (T-01): `git status --porcelain=v1 -z --untracked-files=all` uses list-form argv; `_dirty_records` consumes NUL records and both rename names; `_dirty_paths` normalizes from Git top-level and drops paths outside the selected root. Selector values are exact registry/feature identifiers, not shell, path, query, or template interpolation. Existing Git/GitHub subprocesses remain list-form; no credential-bearing output was added.
- `.claude/skills/harness/bin/harness_boundary.py`, `plan-merge.py`, `feature_json_write.py` (T-03): writers pass destinations already canonicalized with `realpath(abspath(...))` by `harness_merge.require_destination`; `changed_state_root` accepts only canonical feature `plan.yaml`/`feature.json` shapes. The subprocess is fixed argv `[sys.executable, checker, "--changed"]`, `shell=False` by default, runs in the derived checkout, drops `HARNESS_PROJECT_DIR`, and has a recursion marker and timeout. A repository author who can replace that checkout's checker already has code-execution capability in that checkout, so this adds no privilege escalation. Forwarding is confined to checker stdout/stderr after the durable write; it does not print environment values, file contents, credentials, or newly fetched export data.
- `.claude/skills/harness/bin/check-plan-routes.py` (T-02): AST/static consolidation audits inspect repository source and command shapes; they neither execute parsed input nor add an auth, network, shell, or write boundary.
- `.harness/README.md`, `BRIEF.md`, `STATE.md`, `plan.yaml`, `notes/build-divergences.md`: documentation/state records only; added lines contain no credential-shaped values. The two parked divergence-ledger anomalies are operator record matters, not security findings.
- `tests/integration/test-check-plan-routes.py`, `test-check-state-table.py`, `test-feature-json-merge.py`, `test-plan-merge.py`, and `tests/unit/test-harness-boundary.py`: fixtures/tests only. They cover exact selector rejection, rename/untracked mapping, canonical target-root derivation, fixed child argv/cwd/environment, recursion suppression, and forwarding of both child streams; no production trust boundary is introduced by these paths.

OWASP census: no route/auth/session change; no SQL/template/shell interpolation; canonicalized destination paths prevent traversal into another file class; no secrets or dependency changes; no user-controlled URL/redirect; no export/spreadsheet surface; advisory output adds no new sensitive fields. STRIDE census found no capability delta for spoofing/elevation, no durable mutation beyond the already-authorized canonical write, no repudiation-sensitive audit claim, no new disclosure, and only bounded advisory child execution (120-second timeout). Failure to spawn remains fail-open only for explicitly non-authoritative edit-loop feedback; full hooks/workflows/pre-commit remain authoritative.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned diff has real path/subprocess/output surfaces, but introduces no exploitable security regression."
  in_scope: true
  scope_reason: "T-01 parses untrusted Git path records and T-03 derives a checkout, executes its checker, and forwards advisory output; all 15 changed paths were censused and the concrete boundaries were audited."
  severity_max: info
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "Git index/worktree path bytes -> --changed invariant selection", stride: T, mitigated: true }
    - { boundary: "canonical writer destination -> derived checkout/checker executable", stride: "T|E", mitigated: true }
    - { boundary: "checker child stdout/stderr -> operator stderr", stride: I, mitigated: true }
    - { boundary: "Git/GitHub reads -> invariant diagnostics", stride: "S|T|I", mitigated: true }
    - { boundary: "advisory child runtime -> writer availability", stride: D, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-62-check-state-decomposition/.harness/harness/features/FEAT-62-check-state-decomposition/notes/review-harness-security-reviewer-c0.md
```
