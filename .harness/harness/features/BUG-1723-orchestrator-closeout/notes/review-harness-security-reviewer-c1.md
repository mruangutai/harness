# Security review — BUG-1723-orchestrator-closeout — c1

**PASS.** Audited pinned range `1a1c1925171803db8ac7f7464560a3767fa902a8..c700a71e5f513a483f33e495cd3aa559cdd2ee78` and c1 delta `e23646776b1cf1d1833ca0b7cab5da12272eba7b..c700a71e5f513a483f33e495cd3aa559cdd2ee78`. The review remains in scope because `close-run` consumes digest and ledger-controlled values, launches subprocess authorities, mutates records, and forwards child diagnostics. No exploitable security defect was found.

## Audit result

- `.claude/skills/harness/bin/feature-record.py:285-405` remains the material input/subprocess boundary. Child processes use list-form argv, fixed local authority scripts, and `sys.executable`, never a shell. Digest validation precedes mutation; paired task/station, judgement shape, known run, and recorded agent are refused before later stages. Values such as task, station, verdict, digest path, and judgement fields remain arguments rather than executable text. A caller able to choose `--file` or alter its ledger already holds equivalent local record-write authority, so this adds no privilege escalation.
- `.claude/skills/harness/bin/check-state.py:2857-3064` reads repository records and handoff notes and emits them only as terminal diagnostics. ISO parsing refuses malformed or timezone-naive values. The c1 change removes a terminal-state downgrade and routes all in-era INV-43 hits to the existing `bad` list; it tightens a Tampering/Repudiation control and adds no interpreter, query, network, credential, or subprocess boundary. The named BUG-1723 and BUG-285 INV-43 violations are the expected evidence of this fail-closed change, not regressions.
- The c1 tests add refusal coverage and update expected enforcement/document binding; they introduce no runtime surface. The c1 playbook wording records an existing field and introduces no unsafe command construction.
- Per-file census: the full pin changes 27 paths — two runtime Python files (in scope above), three playbook/reference files, two decision files, three tests, and seventeen feature records/notes. The c1 delta changes five paths: one runtime checker, one playbook, and three tests. The non-runtime files contain no new auth route, dependency, network request, export/spreadsheet output, SQL/template construction, secret-bearing fixture, or credential-shaped value. A full patch credential sweep returned no matches.

## OWASP / STRIDE disposition

- Injection and subprocess execution: mitigated by list-form argv and fixed authority paths; no shell, SQL, template, spreadsheet, or URL sink exists.
- Authentication/authorization and elevation: no route, identity provider, permission check, or cross-tenant data path changes.
- Input validation/tampering: malformed CLI and chronology inputs refuse or become gating findings rather than silently passing.
- Secrets/information disclosure: no credential material was introduced; diagnostics expose only local feature metadata already readable by the invoking operator.
- Denial of service: inputs are local bounded feature records under repository-writer control; c1 intentionally makes known historical INV-43 records gating and does not create an attacker-controlled amplification path.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned c1 security audit found no exploitable defect; c1 tightens INV-43 fail-closed enforcement"
  in_scope: true
  scope_reason: "The pin consumes digest/ledger input, invokes subprocess authorities, mutates records, and emits diagnostics; all 27 pinned paths and all five c1 paths were censused, including a credential-shaped patch sweep."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "digest and recorded agent to persona validator", stride: "T/E", mitigated: true }
    - { boundary: "CLI and ledger values to composed subprocess argv", stride: "T/E", mitigated: true }
    - { boundary: "ordered authorities to feature and plan records", stride: "T/R", mitigated: true }
    - { boundary: "handoff and ledger chronology to gating diagnostics", stride: "T/R/I", mitigated: true }
    - { boundary: "child diagnostics to operator terminal", stride: "I", mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-security-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-security-reviewer-c1.md
```
