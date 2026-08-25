```yaml
VERDICT: PASS
DIGEST:
  headline: "B-1 closed: exact diagnostic bullet-set equality rejects the fabricated extra rule, while the unchanged production utility passes all seven targeted cases."
  team: engineering
  steps_run: 1
  cycles_used: 0
  members:
    - { step: B-1, persona: harness-dev-ops, verdict: PASS, headline: "Strengthened SC-02's assertion, proved a controlled extra diagnostic bullet red, and retained production byte identity through the real green run.", files_touched: [.agents/skills/harness/bin/test-merge-gitignore.py, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-fix-b1-eng.md] }
  test_contract: "The test extracts every stderr line beginning with the production bullet prefix, compares that emitted rule set exactly with set(RULES[1:]), and reports sorted missing and unexpected differences."
  red_command: "MERGE_GITIGNORE_BIN=/tmp/fix-b1-mutant/bin/merge-gitignore.sh python3 .agents/skills/harness/bin/test-merge-gitignore.py"
  red_result: "exit 1; 6 passed, 1 failed; the sole failure reported missing=[] and unexpected=['.claude/worktrees/NOT-THE-RULE']."
  green_command: "python3 .agents/skills/harness/bin/test-merge-gitignore.py"
  green_result: "exit 0; all seven named behavioral cases passed (7 passed, 0 failed)."
  broader_gate_disposition: "The all-kinds runner was intentionally not run under the operator's targeted-only constraint."
  production_script_sha256_before: 86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12
  production_script_sha256_after: 86cfff73c88a2baa1c74d2e516e3608e38954fef1c9e4ef344113b011e425c12
  production_script_disposition: "Byte-identical; read, executed, and hashed only. No production defect was proven."
  must_fix: []
  files_touched: [.agents/skills/harness/bin/test-merge-gitignore.py, .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-fix-b1-eng.md, .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-eng/state.yaml, .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-eng/digest.md]
  branch: FEAT-36-merge-gitignore-coverage
  open_questions: []
  escalations: []
  expertise_update: []
  sc_status:
    - { id: SC-02, verdict: PASS, method: "controlled-mutant red plus real-production targeted green", evidence: ".harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/receipt-harness-dev-ops-fix-b1-eng.md" }
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/runs/fix-b1-eng/digest.md
```

The receipt contains exact invocation output and the discarded non-discriminating fixture attempt. No runner, registry, plan, brief, or production-script change was authored in this run.
