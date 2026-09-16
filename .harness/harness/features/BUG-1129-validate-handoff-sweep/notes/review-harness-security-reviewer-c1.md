# Security review — BUG-1129 validate handoff sweep — c1

## Conclusion

PASS at immutable review SHA `499eaf0b9c1eb04e0f51dcfec47fab9ea50abd54` over `142026456c64c80c3dd3aa776636dadbc0e21881..499eaf0b9c1eb04e0f51dcfec47fab9ea50abd54`. T-01 remains security-relevant because repository-controlled plan/handoff evidence authorizes irreversible GitHub and lifecycle writes. The c0 security conclusion is explicitly **carried and confirmed**: c0 had no security finding to remediate, and c1's test/evidence strengthening does not alter the production threat boundary. No substantive auth, secrets, validation, injection, path-handling, parser fail-open, or data-exposure defect remains.

## Scope evidence and c0 disposition

- Production: `.claude/skills/harness/bin/gh-sync.py`, `handoff_policy.py`, and `check-state.py` are in scope. The fixed child path `notes/handoff-validate.md` is checked before comment posting, board edits, issue/milestone writes, or station recording. `handoff_policy.exempt_reason` grants exemption only for a parsed mapping with a non-empty task list whose every mapping has exact `execution_mode: main-session-direct`; missing, unreadable, malformed, non-mapping, empty, malformed-task, missing-mode, team, and mixed plans deny exemption. YAML values are not interpolated into shell, SQL, URLs, templates, exports, or output paths. The local refusal exposes only the feature path and bounded parser detail to the invoking operator; it reads or emits no credential or cross-user data.
- Tests/fixtures: `tests/integration/gh_sync_support.py`, `test-gh-sync-abandon.py`, `test-gh-sync-ship.py`, `test-hooks-install.py`, `test-post-merge-sweep.py`, and `tests/unit/test-handoff-policy.py` contain synthetic local evidence only. The c1 delta closes prior non-security review gaps by asserting the complete GitHub-write boundary, exact plan preservation, required diagnostic, fail-closed malformed-plan behavior, and fixture contract. It adds no runtime authority or untrusted sink.
- Records/evidence: `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`, `answers-2026-09-16-sign.md`, `handoff-build.md`, `handoff-plan.md`, both Main receipts, the c0 goal-check, and all four c0 review notes are repository metadata only. They contain no credential-shaped value, executable interpolation, dependency, or new data sink.
- The c0 security review returned PASS with no findings. Its three boundaries remain mitigated at c1. The c0 code/QA/goal-check findings Q1/Q2/Q3 were coverage/evidence defects, not exploitable security defects; the c1 changes strengthen proof without broadening reachability.

A committer who can create the handoff note or alter the signed plan already controls the repository evidence this local lifecycle command consumes. T-01 gives no lower-trust actor a new capability. Authentication of commits and domain-write enforcement remain upstream controls rather than a boundary weakened by this diff.

## Threat-boundary conclusion

- **Tampering / elevation:** selectively shaped or malformed `plan.yaml` cannot obtain an exemption; parsing and shape failures deny it.
- **Tampering / repudiation:** absent validation evidence produces exit 1 before irreversible writes and does not emit the sweep's permissive `SKIP` signal.
- **Injection / unsafe path:** no attacker-controlled plan value reaches a command/query/template/path sink; the handoff suffix is fixed.
- **Information disclosure / secrets:** no secret handling was added; diagnostics remain local and limited to the path/parser failure needed for recovery.
- **Denial of service:** malformed/unreadable evidence refuses shipping, the intended fail-closed result, without destroying the recovery worktree.

No formatter, linter, build, or project-wide test was run, as required for this security review; the pinned diff and supplied c1/fail-first receipts are the evidence assessed.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The c0 security PASS remains valid at the c1 pin; strengthened evidence adds no new threat surface and the write authorization boundary remains fail-closed."
  in_scope: true
  scope_reason: "T-01 consumes repository-controlled plan and handoff evidence to authorize irreversible GitHub and lifecycle writes; all 23 changed paths were censused and the production boundary was audited at the exact pin."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "repository-controlled plan.yaml -> all-direct exemption", stride: T, mitigated: true }
    - { boundary: "handoff evidence -> irreversible GitHub and lifecycle writes", stride: E, mitigated: true }
    - { boundary: "local parser/path diagnostic -> invoking operator stderr", stride: I, mitigated: true }
    - { boundary: "malformed or unreadable repository evidence -> ship availability", stride: D, mitigated: true }
  open_questions: []
  files_touched: [".harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-security-reviewer-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1129-validate-handoff-sweep/.harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-security-reviewer-c1.md
```
