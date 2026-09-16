# Security review — FEAT-1714-reject-verb — cycle 1

## BLUF

PASS. Reviewed immutable SHA `8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`; c1 range `82bdef1a6f7cd89005f661a06296725f5b1ad9b1..8090ce0b0fd8eb9d12c63df83ef9cb45a7b38125`. SEC-1714-01 / VAL-02 is closed. Required reject mutations now stop at the first failed write, return nonzero, report landed and not-run work, and withhold the station. No security finding survives.

## Scope and pinned evidence

The delta is security-relevant because it consumes plan/operator input, publishes GitHub comments, performs irreversible GitHub mutations, and writes terminal state. All nine changed paths were inspected. `gh-sync.py` and `SKILL.md` define the trust/authority boundary; the four changed tests/support files supply executable evidence; the validator/worktree refactors add no security boundary; the fix receipt is provenance only. A full pinned-diff credential scan found no added secret, token, password, authorization header, API key, or private key.

At the pin, `.claude/skills/harness/bin/gh-sync.py:1810-1928` routes required remote writes through `_RejectWrites` and `_must`. `_run_reject_steps` catches `_RejectHalt`, identifies the failed step, reports already-landed and not-run steps, and exits 1 before station recording. `cmd_reject` records `rejected` only after all numeric-successor steps complete and converts station-write failure to exit 1.

Pinned regression evidence at `tests/integration/test-gh-sync-abandon.py:692-775` proves the irreversible partial-progress case: after close and comment land, label failure returns 1, identifies partial progress, runs neither backlog nor milestone, and leaves the station unwritten. The same runner and raising write methods govern both parent and first-sync shapes.

Targeted verification: `python3 tests/integration/test-gh-sync-abandon.py` exited 0 with `ALL PASSED`, including numeric failure and first-sync lifecycle cases.

## OWASP / STRIDE disposition

- **Recorded parent (T/R/I):** close `not_planned`, comment, optional label, backlog after close, optional milestone, then numeric station. No task/sub-issue traversal. Failures halt nonzero before later work/station.
- **No parent / unowned source ticket (T/E):** `_source_reject_steps` reads non-boolean integer `plan.yaml.source_issues`, comments and reseats each card only. It has no close or label action, so the harness never closes or labels a source ticket it did not create.
- **Injection/input validation (T):** successor is positive digits or `none`; reason is one non-empty line; GitHub uses list argv and `--body-file`. Neither value becomes shell syntax.
- **Auth/data exposure (E/I):** writes use the invoking operator's configured `gh` authority and require `--yes`; dry-run is non-mutating. The reason/successor is the intended operator-confirmed disclosure. No new cross-repository selector, credential handling, secret-bearing error, or over-broad response exists.
- **Availability (D):** execution is a bounded ordered list over validated recorded issues and halts rather than amplifying writes after failure.

```yaml
VERDICT: PASS
DIGEST:
  headline: "SEC-1714-01 / VAL-02 is closed; reject fails closed with auditable partial progress, and parent/no-parent lifecycles preserve authority boundaries."
  in_scope: true
  scope_reason: "The pinned delta validates plan/operator input, publishes human-interpreted GitHub comments, performs irreversible GitHub writes, and records terminal state."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "plan and CLI input to reject lifecycle", stride: T, mitigated: true }
    - { boundary: "local feature record to GitHub lifecycle", stride: R, mitigated: true }
    - { boundary: "recorded parent mutation authority", stride: I, mitigated: true }
    - { boundary: "unowned source ticket mutation authority", stride: E, mitigated: true }
    - { boundary: "ordered external writes", stride: D, mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-security-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-security-reviewer-c1.md
```
