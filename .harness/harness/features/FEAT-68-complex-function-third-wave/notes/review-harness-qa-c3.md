# FEAT-68 QA c3 gate

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The required matrix and all three T-01 assertions pass at b6b8c28d, but direct VF-04-C2 execution leaves the durable receipt non-reproducible and its D-02..D-05 provenance false."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 41 }
    - { kind: integration, state: satisfied, cmd: "python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 70 }
  coverage_gaps:
    - "SC-04: no durable, rerunnable reproduction remains after direct execution; the regenerated receipt omits its Reproduction section and its actual D-02..D-05 bytes disagree with the ledger."
    - "SC-05 final actual validate-output Markdown/no-HTML-sibling observation remains deliberately unavailable until a clean panel; this panel is not clean."
  sc_evidence:
    - { id: SC-01, test: "T-01 inline grade assertion; notes/clean-pin-byte-receipts.md:124-139" }
    - { id: SC-02, test: "direct feat68-cleanpin.py run: 53/57 normalized-identical; notes/clean-pin-byte-receipts.md:11-78" }
    - { id: SC-05, test: "T-01 HTML-removal and prohibited-reference inline assertions" }
  fail_first:
    - { sc: SC-01, evidence: "notes/red-first-receipts.md:19-31 (baseline exit 1; exactly five grade-1 targets)" }
    - { sc: SC-02, evidence: "BRIEF.md:18-21 and notes/red-first-receipts.md:42-45 (operator-approved baseline-versus-pin comparison equivalent)" }
    - { sc: SC-05, evidence: "notes/red-first-receipts.md:33-40 (baseline renderer/reference and 102-HTML presence)" }
  must_fix:
    - id: VF-04-C3
      kind: form
      severity: med
      task_binding: T-01
      owner: main-session-direct
      new_class: false
      scope_change: false
      scenario: "The receipt says its exact commands run from /Users/molchairuangutai/GitHub/harness, but there .harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts/feat68-cleanpin.py is absent and the recorded step-3 command exits 2 before opening the baseline JSON or existing detached checkouts."
      remedy: "Make the declared root and script home agree, then rerun the preserved command without overwriting required reproduction/provenance evidence."
    - id: VF-05-C3
      kind: form
      severity: med
      task_binding: T-01
      owner: main-session-direct
      new_class: true
      scope_change: false
      scenario: "At the feature worktree root, direct step 3 exits 0 and reports 53/57, but feat68-cleanpin.py:42-76 overwrites clean-pin-byte-receipts.md without its Reproduction section and uses a second suite run for raw differences (lines 56-62). The regenerated D-02/D-03/D-04/D-05 bytes (receipt:84-85,100-101,106-107,120-121) differ from ledger D-02..D-05 (build-divergences.md:25-45), so the ledger cannot derive from the table hashes produced by the first run (cleanpin.py:24-31)."
      remedy: "Produce one durable, rerunnable receipt that retains the exact invocation and binds each retained raw difference and ledger byte to the same per-suite execution whose hashes/table it reports."
  findings:
    - { id: VF-04-C3, kind: form, severity: med, task_binding: T-01, owner: main-session-direct, new_class: false, scope_change: false }
    - { id: VF-05-C3, kind: form, severity: med, task_binding: T-01, owner: main-session-direct, new_class: true, scope_change: false }
  vf_04_c2_closed: false
  sc_05_final_observation_permitted: false
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-qa-c3.md
```