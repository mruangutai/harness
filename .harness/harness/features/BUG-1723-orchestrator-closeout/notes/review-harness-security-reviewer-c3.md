# Security review — BUG-1723-orchestrator-closeout — c3

**PASS.** I audited the complete feature range `1a1c1925171803db8ac7f7464560a3767fa902a8..6999227750f68b3ec9c8f77a3ae4f281310742a9` from pinned Git objects (the live worktree was later than the review SHA). The feature is security-relevant: `close-run` consumes repository-controlled paths and ledger values, starts local authority subprocesses, mutates durable records, and forwards diagnostics; INV-43 interprets handoff/run/judgement chronology as a tampering and repudiation gate. No exploitable security defect remains.

## Scope census and boundaries

The range changes 39 paths. The two runtime files are in scope: `.claude/skills/harness/bin/feature-record.py` is the path/input, subprocess, durable-write, and diagnostic boundary; `.claude/skills/harness/bin/check-state.py` is the chronology/tampering boundary. The three changed tests were reviewed as security evidence, not production surfaces. The three playbook/reference files and two decision files were checked for unsafe commands and false safety claims. The other 29 paths are BRIEF/state/plan/feature, handoff, receipt, and review records; they were checked for secrets, PII, dangerous/interpreted paths, record-tampering guidance, and export injection. No changed auth route, dependency, network request, redirect, SQL/NoSQL/template construction, archive/export, spreadsheet formula sink, credential, or cross-tenant response exists.

- **Input/path/subprocess construction:** `close-run` validates argument pairing, judgement shape, `n_a` code grade, run existence, recorded agent, and digest before mutation. Each stage uses list-form argv, `sys.executable`, and fixed local authority-script paths; there is no shell interpolation. `--file` and `--digest` are operator-local paths. A caller able to choose another feature ledger or alter the recorded agent already has equivalent local read/write and direct-authority capability, so this composition grants no privilege delta.
- **Durable tampering/repudiation:** earlier completed writes intentionally survive a later refusal and the failing stage is named. INV-43 parses aware ISO-8601 instants, reports malformed/missing relevant chronology as `CANNOT VERIFY`, and gates retrospective succession at every station, including `done`. The final DEC-159 clause now matches the executable and ledger, removing c2's contradictory terminal-note guidance rather than weakening enforcement.
- **Information disclosure/secrets:** child refusal output and INV-43 diagnostics expose only local feature metadata and authority diagnostics already available to the invoking operator. The full patch credential sweep found only prose/schema uses of words such as token, secret, and authorization; no credential-shaped value was introduced.
- **Injection/export:** no shell, query, template, URL, archive, CSV, or spreadsheet interpreter is introduced. Judgement text remains a list-form argv value and is written through the existing schema-validating atomic authority.
- **DEC-159/T-03 c3 delta:** from c2 pin `972d5c054e6a1dbab811f957ff5d5186a7445f63` to the review pin, production Python is unchanged. The decision/index and approved T-03 scope now state the same all-stations INV-43 contract as `check-state.py` and `ledger.md`; the remaining delta is durable feature/review bookkeeping and adds no new trust boundary.

## Threat model

A repository-local actor can supply CLI paths/values and edit feature records, but already possesses the direct capabilities composed by `close-run`; fixed list-form subprocesses and existing validators prevent added injection/elevation. A maintainer or orchestrator can accidentally or deliberately postdate/garble succession chronology; INV-43 makes both retrospective and unverifiable records gating violations, including after terminal transition. Diagnostics cross only to the invoking local operator and contain no newly reachable secret or other-user data. There is no remote actor, authentication boundary, multi-tenant data boundary, or unbounded request surface in this range.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Exact-pin audit passes: close-run and INV-43 add measured local trust boundaries without an exploitable security defect"
  in_scope: true
  scope_reason: "The 39-path range consumes repository-controlled paths and ledger data, starts authority subprocesses, mutates durable records, and interprets chronology; both runtime files and every non-runtime path were censused."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "digest path and recorded agent to persona digest validator", stride: "T/E", mitigated: true }
    - { boundary: "CLI and ledger values to composed authority argv", stride: "T/E", mitigated: true }
    - { boundary: "ordered authority results to feature and plan durable records", stride: "T/R", mitigated: true }
    - { boundary: "handoff, succession, and run timestamps to INV-43", stride: "T/R", mitigated: true }
    - { boundary: "child refusal and chronology diagnostics to local operator terminal", stride: "I", mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-security-reviewer-c3.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-security-reviewer-c3.md
```
