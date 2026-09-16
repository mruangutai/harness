# Security review — BUG-1129 validate handoff sweep — c0

## Conclusion

PASS. T-01 is security-relevant because it reads repository-controlled `plan.yaml` and a handoff-path existence signal before performing irreversible GitHub and lifecycle writes. At pinned review SHA `df871448f55bcb7cf5804e5ffc9cca187a364131`, the new boundary fails closed: missing, unreadable, malformed, non-mapping, empty-task, malformed-task, missing-mode, and mixed-mode plans do not grant the exemption; the refusal precedes body posting, card movement, milestone closure, and station recording. No exploitable auth, authorization, secret, injection, unsafe-path, or data-exposure defect was found.

## Reviewed surfaces

- `.claude/skills/harness/bin/gh-sync.py:2188-2231` — local feature-directory input crosses into GitHub and repository terminal writes. The guard uses a fixed `notes/handoff-validate.md` suffix, checks before the first write, and reports only the local path and bounded parser detail. No shell interpolation, URL construction, credential handling, export, or cross-user response was added.
- `.claude/skills/harness/bin/handoff_policy.py:1-68` — repository-controlled YAML crosses the exemption boundary through canonical `artifact_accessors.load_plan`; only a non-empty list of mappings whose explicit mode is exactly `main-session-direct` grants exemption. Exceptions deny exemption. No dynamic command, query, template, redirect, or output-file path is constructed from YAML values.
- `.claude/skills/harness/bin/check-state.py:1185-1230` — the pre-existing INV-17 consumer now calls the same predicate; the change does not broaden authorization or data access.
- Test/fixture surfaces (`tests/integration/gh_sync_support.py`, `test-gh-sync-abandon.py`, `test-gh-sync-ship.py`, `test-hooks-install.py`, `test-post-merge-sweep.py`) add local synthetic artifacts and assertions only; no production trust boundary.
- Feature records (`BRIEF.md`, `STATE.md`, `feature.json`, `notes/answers-2026-09-16-sign.md`, `notes/handoff-build.md`, `notes/handoff-plan.md`, `notes/receipt-main-session-T-01-fail-first.md`, `plan.yaml`) contain lifecycle metadata and evidence only. The pinned diff contains no credentials, tokens, PII, executable interpolation, export fields, or new dependency.

The existence check can be satisfied by a party able to write the feature's notes, and the all-direct exemption by a party able to alter the signed plan. Those actors already control the repository evidence on which this local lifecycle tool necessarily relies; T-01 grants no additional capability to a lower-privilege actor. Authenticity of repository commits and domain-write enforcement remain upstream controls, not new boundaries introduced here.

## Threat model

- Tampering / elevation: malformed or selectively shaped `plan.yaml` attempts to obtain an exemption — mitigated by strict canonical parsing, non-empty-list enforcement, mapping checks, and exact execution-mode equality.
- Tampering / repudiation: shipping before validation evidence exists — mitigated by refusal before irreversible writes and by a non-SKIP failure signal that preserves the recovery worktree.
- Information disclosure: local path or YAML parser detail in the refusal — mitigated for this local operator CLI; no secret material is read or emitted by the new path.
- Injection / unsafe path: attacker-controlled YAML values or feature path reaching shell, SQL, URL, template, export, or arbitrary output path — no such sink is introduced; the only joined child path is fixed.

```yaml
VERDICT: PASS
DIGEST:
  headline: "T-01 fails closed at the validation-evidence boundary before irreversible writes; no exploitable security defect found."
  in_scope: true
  scope_reason: "The diff consumes repository-controlled plan and handoff evidence to authorize terminal GitHub/repository writes; every introduced production boundary and every changed file was audited."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "repository-controlled plan.yaml -> all-direct exemption", stride: T, mitigated: true }
    - { boundary: "handoff evidence -> irreversible GitHub and lifecycle writes", stride: E, mitigated: true }
    - { boundary: "local parser/path diagnostic -> operator stderr", stride: I, mitigated: true }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-security-reviewer-c0.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1129-validate-handoff-sweep/.harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-security-reviewer-c0.md
```
