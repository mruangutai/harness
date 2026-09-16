# Security review — BUG-1723-orchestrator-closeout — c2

**PASS.** The complete pinned range `1a1c1925171803db8ac7f7464560a3767fa902a8..972d5c054e6a1dbab811f957ff5d5186a7445f63` is security-relevant because `close-run` accepts repository-controlled paths and ledger values, launches local authorities, mutates durable records, and forwards diagnostics. No exploitable security defect was found.

## Boundaries and result

- `.claude/skills/harness/bin/feature-record.py` is the input/subprocess boundary. Digest validation precedes mutation; malformed pairing, judgement shape, code grade, unknown run, and recorded-agent errors refuse before later stages. Every child uses list-form argv with `sys.executable` and fixed local authority scripts; no shell, query, template, URL, redirect, or export interpreter is introduced. A caller choosing `--file` or modifying its ledger already has equivalent local record-write authority, so no privilege delta is created.
- `.claude/skills/harness/bin/check-state.py` is the chronology/tampering boundary. Aware ISO instants are compared; malformed, missing, or unrelatable chronology becomes a gating diagnostic rather than a silent pass. Diagnostics contain local feature metadata already readable by the invoking operator, not credentials or cross-user data.
- The c2 delta changes runtime-neutral ledger wording and a unit test. The public `close-run` refusal test mocks list-form `subprocess.run` only in-process and uses fixed fixture data; it adds no production construction or trust boundary. The ledger now accurately describes fail-closed INV-43 behavior at every station and explicitly preserves unverifiable chronology, improving tampering/repudiation guidance.
- C1-V01 is closed for security: removing the terminal-state exception eliminates misleading fail-open guidance. C1-V02 is historical evidence only and adds no security surface. C1-V03 is closed without weakening subprocess construction: the test now reaches the public composition and discriminates the real `spend` stage.
- The known INV-43 census for BUG-1723-orchestrator-closeout and BUG-285-canonical-reader is expected evidence of the tightened chronology invariant, not a new security regression.
- Per-file census: all 33 paths were covered. In scope were the two runtime Python files and their three tests. The three playbook/reference files and two decision files were checked for unsafe commands and false safety claims. The remaining 23 BRIEF/state/plan/feature/receipt/review/handoff records were checked for secrets, PII, dangerous paths, and interpreted export content. No auth route, dependency, network request, SQL/NoSQL/template construction, credential, archive/export, spreadsheet formula sink, or cross-tenant path was added. The credential-shaped diff sweep produced only prose containing words such as “authorization” and “secret”; no credential value was present.

## Threat model

- **Tampering / elevation:** CLI and ledger values cross into composed authorities; fixed argv, fixed authority paths, validation, and ordered refusal mitigate the boundary.
- **Tampering / repudiation:** handoff and ledger timestamps cross into INV-43; invalid chronology is fail-closed and the c2 wording matches executable behavior.
- **Information disclosure:** child diagnostics cross to the operator terminal; content remains local feature metadata and child refusal text, with no newly exposed secret or other-user data.
- **Denial of service:** inputs are local repository records under an actor already able to alter or invoke the same authorities; no remote or unbounded amplification surface is introduced.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Pinned c2 security audit found no exploitable defect; the delta tightens tampering and repudiation guidance"
  in_scope: true
  scope_reason: "The full pin consumes repository-controlled digest/ledger input, invokes subprocess authorities, mutates durable records, and emits diagnostics; all 33 paths and the c2 delta were censused."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "digest and recorded agent to persona validator", stride: "T/E", mitigated: true }
    - { boundary: "CLI and ledger values to composed list-form subprocess argv", stride: "T/E", mitigated: true }
    - { boundary: "ordered authorities to feature and plan records", stride: "T/R", mitigated: true }
    - { boundary: "handoff and ledger chronology to INV-43 diagnostics", stride: "T/R", mitigated: true }
    - { boundary: "child refusal diagnostics to the invoking operator", stride: "I", mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-security-reviewer-c2.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1723-orchestrator-closeout/.harness/harness/features/BUG-1723-orchestrator-closeout/notes/review-harness-security-reviewer-c2.md
```
