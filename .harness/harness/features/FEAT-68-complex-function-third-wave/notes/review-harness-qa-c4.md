# FEAT-68 QA c4 gate

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The cross_module matrix and signed checks pass, and c3's one-execution reproduction reruns cleanly, but SC-02's ledger does not retain exact old/new bytes for D-02–D-04."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 41 }
    - { kind: integration, state: satisfied, cmd: "python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 70 }
  coverage_gaps:
    - "SC-02: D-02–D-04 ledger entries replace portions of the required exact old/new raw bytes with literal ellipses."
  sc_evidence:
    - { id: SC-01, test: "T-01 inline grade assertion; notes/clean-pin-byte-receipts.generated.md:124-139" }
    - { id: SC-02, test: "isolated preserved feat68-baseline.py + feat68-cleanpin.py reproduction; artifact://4582" }
    - { id: SC-05, test: "T-01 HTML-removal and prohibited-reference inline assertions" }
  fail_first:
    - { sc: SC-01, evidence: "notes/red-first-receipts.md:19-31; detached-baseline assertion exit 1, exactly five grade-1 targets" }
    - { sc: SC-02, evidence: "BRIEF.md:18-21 and notes/red-first-receipts.md:42-45; approved baseline-versus-pin comparison equivalent" }
    - { sc: SC-05, evidence: "notes/red-first-receipts.md:33-40; baseline renderer/reference and 102 HTML derivatives present" }
  findings:
    - id: QA-C4-01
      kind: form
      severity: med
      owner: T-01
      affected_sc: [SC-02, SC-04]
      scenario: "An auditor comparing a divergence cannot recover the actual baseline or pin stream for D-02, D-03, or D-04 from build-divergences.md because the entries contain literal ellipses; a changed byte outside the displayed fragment could be omitted while the ledger still appears complete."
      evidence: "BRIEF.md:18-21; notes/build-divergences.md:25-41; notes/clean-pin-byte-receipts.generated.md:82-85,104-107,118-121"
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-qa-c4.md
```

## Evidence

- T-01 is `cross_module`; its required `unit` and `integration` kinds passed at review SHA `9d495ccdf9f8216a54a06356fe8c14227f190938`. Discovery is non-vacuous: 41 unit files and 70 integration files; integration reported `0 failure(s)`.
- The remaining signed grade, 102-HTML-removal, and prohibited-reference assertions exited 0.
- In an isolated detached review worktree, the preserved baseline and clean-pin commands completed: all 57 suite exits were 0, 53/57 normalized-identical, pin grade exit 0, and baseline grade exit 1 naming exactly the five grade-1 targets (`artifact://4582`). The regenerated receipt differs from the committed generated receipt only in its timestamp and the known D-02–D-05 nondeterministic streams/hashes (`artifact://4591`).
- `feat68-cleanpin.py:25-33,59-67` invokes each suite once; that call's `outputs[s]` supplies both raw-difference lines and the table hashes. The committed generated receipt's full D-02–D-05 raw lines agree with the corresponding new values in the ledger, but the ledger itself truncates D-02–D-04 and therefore fails the signed exact-byte requirement.
- No `ship-review-validate-validator*` file exists yet, so the eventual c4 markdown-only ship briefing remains possible; no `.html` sibling currently blocks it.

## Principles applied

- Build the Lever: reran the preserved receipt scripts in an isolated pinned worktree rather than relying on inherited claims.
