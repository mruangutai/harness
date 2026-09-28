# Security review — validate c1

```yaml
VERDICT: PASS
DIGEST:
  headline: "The complete 161-path scope remains fail-closed and introduces no exploitable security regression; one stale sentence in the repaired VF-01 receipt is a low-severity record-form contradiction."
  in_scope: true
  scope_reason: "The five production refactors process untrusted plan/YAML, filesystem paths, hook writes, and GitHub issue/project data across authorization and enforcement boundaries; renderer/history deletion changes human-interpreted output. This surface has prior security review, but c1 was remeasured independently at base e655f14a56a14bf1777cae55a19195c9af10505d..review 66b9c914 rather than inheriting c0. Census: 143 pinned changed paths (5 enforcement modules, 1 deleted renderer, 2 command/reference docs, 102 deleted historical HTML derivatives, 22 FEAT-68 record/evidence paths, and 11 test/classification paths) plus 18 unchanged amended T-01 owning-suite/support paths, yielding 161 unique paths."
  severity_max: low
  findings:
    - id: SEC-C1-01
      kind: form
      scope: task
      severity: low
      reader: security-reviewer
      readers: [harness-security-reviewer, harness-code-reviewer, harness-pm]
      summary: "clean-pin-byte-receipts.md retains a stale sentence saying mkdtemp paths and unittest time were normalized even though the corrected tables and exact diffs treat all four suites as non-identical."
      why: "An auditor validating VF-01 can read two mutually exclusive experiment descriptions in the same durable receipt: the opening comparison paragraph says the temp paths were 'normalised to <tmpdir>' and names the timing normalization, while the table marks those streams NO and the later section says checkout-root normalization only. This does not create a code exploit or conceal the preserved raw differences, which are printed and ledgered D-02..D-05, so it is record form at low severity rather than a security gate. T-01 owns the record; remedy: reword that opening paragraph to say those nondeterministic lines were retained and ledgered, without changing evidence. Artifact: .harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-security-reviewer-c1.md."
      task_binding: T-01
      owner: T-01
      remedy: "Correct only the stale opening comparison sentence so it agrees with the table, exact raw-byte differences, D-02..D-05, and A-1/A-2."
      artifact: ".harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-security-reviewer-c1.md"
  must_fix: []
  threat_model:
    - boundary: "Agent-supplied write target and manifest grants -> check-domain.py / harness_boundary.py authorization verdict"
      stride: E
      mitigated: true
      assessment: "The refactor preserves ordered out-of-place and wrong-checkout refusals, allow/shared guards, and deny; unknown outcomes now explicitly select _deny_verdict. No path becomes fail-open."
    - boundary: "Untrusted plan.yaml fields and file anchors -> route ownership diagnostics"
      stride: T
      mitigated: true
      assessment: "Status and budget validation remain before per-task routing; every ungranted literal still increments the violation count, and glob paths remain unresolved rather than interpreted as grants. Subprocess argv construction is unchanged and list-form."
    - boundary: "GitHub issue/project responses -> lifecycle audit findings"
      stride: T
      mitigated: true
      assessment: "Four read calls retain their order; issue, label, station, workflow, and status finding order and failure propagation remain unchanged. No auth, mutation, URL, shell, or credential handling is added."
    - boundary: "Fleet/repository layout and reader files -> migration verdict"
      stride: T
      mitigated: true
      assessment: "Unreadable, undeclared, neither, and no-evidence cases still resolve CANNOT_VERIFY before MIXED/CLEAN; the extracted helper cannot call next(iter(shapes)) until non-empty evidence is established."
    - boundary: "Briefing markdown -> browser-interpreted generated HTML"
      stride: I
      mitigated: true
      assessment: "The renderer, its invocation/reference surfaces, its test, and all 102 generated HTML derivatives are removed. The delta eliminates rather than adds an interpreted-output/XSS or formula-export surface."
    - boundary: "Build/validation evidence -> reviewer trust in immutable-pin equivalence"
      stride: R
      mitigated: false
      assessment: "VF-01's detached base/pin identities, 53/57 result, exact D-01..D-05 bytes, and A-1..A-3 rulings are present, but SEC-C1-01 leaves one stale contradictory normalization sentence. VF-02 is internally consistent: 9ab1813e is the pin and 0c15bad6 only the superseded D-13 candidate."
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-security-reviewer-c1.md
```

## Security disposition

OWASP review found no new injection, authentication, secret, SSRF/redirect, dependency, deserialization, or cross-user data-exposure mechanism. STRIDE review found no capability delta: the authorization-sensitive decompositions preserve deny/exit behavior, and the sole unknown-dispatch case is explicitly denied. No credential-shaped addition appears in the full pinned diff; absolute checkout and temporary paths in evidence disclose workstation layout but no credential and are already required experiment provenance.

VF-01 was independently traced through the clean-pin receipt, D-01..D-05, A-1/A-2, the fix digest, and the build digest's append-only correction. Its experiment data supports detached checkouts and checkout-root-only comparison, subject to SEC-C1-01's stale prose. VF-02 is clean across the red-first receipt, D-13, A-3, fix digest, amendments, and handoff references.

From the security lens, the preconditions for the orchestrator-owned SC-05 final markdown/no-HTML-sibling check are clean: no security must-fix remains, and pre-fan-in absence is sequencing rather than a defect. The orchestrator must still decide panel-wide readiness after the other readers fan in.
