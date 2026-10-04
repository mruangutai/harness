# Security review — FEAT-65 validate c1

```yaml
VERDICT: FAIL
DIGEST:
  headline: "CR-01 is securely closed, but QA-65-01 remains open for SC-01 because its byte receipt did not run the final-pin test files."
  in_scope: true
  scope_reason: "The baseline-to-7596434c diff changes exception boundaries in enforcement hooks consuming untrusted hook JSON/config and deciding fail-open or fail-closed outcomes. I inspected all 13 changed production Python files, the broad-catch census, embedded reader, retained receipts, credential-shaped strings, subprocess boundaries, and diagnostics. C0 dispositions: QA-65-01 PARTIAL — SC-02/03/04/05/09/10 close because red-first-receipts uses test files byte-identical from a17269db through 7596434c, with baseline red and pin green; SC-01 remains open because its recorded task-head test sets differ from 7596434c. CR-01 CLOSED — the reader catches only OSError/ValueError/AttributeError; probes observed expected recovery, github-shape traceback, and injected RuntimeError escaping rc=1; census measurement is baseline 5, pin 0. No interpolation, credential, or new diagnostic leak was found. Artifact write had no issue #1898 refusal."
  severity_max: high
  findings:
    - id: SEC-65-01
      reader: security-reviewer
      SC: SC-01
      file: ".harness/harness/features/FEAT-65-broad-exception-hooks/notes/byte-evidence-vs-baseline.md:3-6,49-52,75-78"
      kind: substance
      severity: high
      owned_plan_tasks: "T-01, T-02, T-03"
      summary: "QA-65-01 remains open for SC-01: retained baseline byte runs used earlier task-head tests, not tests committed at 7596434c."
      defect: "The receipt names dd1203a3/e10c56de/ec0996cb. Git comparison shows SC-01 owning tests changed afterward before 7596434c, including 84 changed lines in test-check-domain.py and test-check-domain-worktree.py. It therefore does not prove the final-pin assertions fail against baseline production and pass at the pin."
      failure_scenario: "A later assertion change can weaken coverage of a fail-open hook defect while the earlier receipt remains credited, allowing an enforcement bypass to ship without baseline discrimination."
      satisfies: "Run every SC-01 owning test exactly as committed at 7596434c against 4e8c73c0 production and 7596434c, retaining commands, exits, and normalized stdout/stderr differences."
  must_fix:
    - "SEC-65-01 / QA-65-01 (SC-01; T-01/T-02/T-03): regenerate SC-01 byte evidence with test files committed at 7596434c against baseline production and the pin."
  threat_model:
    - boundary: "Hook payload/config -> enforcement verdict"
      stride: "T|E"
      mitigated: false
      note: "Code narrowing improves fail-open visibility, but final-pin SC-01 fail-first provenance is not established."
    - boundary: "harness.json -> isolated _CONFIG_READER subprocess"
      stride: "T|D|E"
      mitigated: true
      note: "List argv avoids shell interpolation; expected boundary errors recover and unrelated RuntimeError stays loud."
    - boundary: "Exception diagnostic -> operator stderr"
      stride: "I|R"
      mitigated: true
      note: "Local class/message disclosure is designed; no credential, payload dump, or cross-user data was added."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/review-harness-security-reviewer-c1.md
```
