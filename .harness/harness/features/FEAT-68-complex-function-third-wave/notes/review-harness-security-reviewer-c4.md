# FEAT-68 security review — validate c4

**PASS.** I inspected the complete immutable diff `e655f14a56a14bf1777cae55a19195c9af10505d..9d495ccdf9f8216a54a06356fe8c14227f190938`: **178 paths (62 added, 104 deleted, 12 modified)**, including exactly **102 deleted feature-note HTML files**. I also enumerated and inspected every required shared artifact: BRIEF, plan, feature.json, all ten named prior-run digests, the six named evidence/ruling notes, and all three source scripts under `notes/receipt-scripts/` (generated `__pycache__` entries were enumerated but are not source). The diff is security-scoped in because it changes authorization/path enforcement, processing of plan, board/API and filesystem input, subprocess-backed audit evidence, raw output/hashes, and browser-interpreted exports.

## OWASP and STRIDE assessment

- **Authorization, path normalization, fail-open (T/E):** `harness_boundary.py:842-1006` still resolves the real target, refuses out-of-place and wrong-checkout targets before the unrelated-path outcome, evaluates allow/shared before deny, and returns deny when no grant matches. `check-domain.py:855-1055` parses manifest domains fail-closed and maps every unknown classifier outcome to `_deny_verdict`; allow/shared alone run the existing checkout/claim/approval guards. No auth/session mechanism or privilege delta is introduced.
- **Untrusted input, tampering and DoS (T/R/D):** `check-plan-routes.py:379-523`, `board_lifecycle.py:795-926`, and `layout_migration.py:224-286` retain typed YAML loading, rule order, API argv construction, unreadable/no-evidence states, and finding order. Board values remain display/audit data and do not enter shell or authorization decisions. No newly unbounded parser, unsafe deserialization, SQL/NoSQL/template injection, SSRF, redirect, or dependency appears.
- **Command construction:** changed production code adds no subprocess sink. Receipt scripts use list-form argv with no shell (`feat68-baseline.py:6`; `feat68-cleanpin.py:14-17,26,41-42`). Operator-provided refs and `FEAT68_BASELINE_JSON` affect an operator-invoked evidence tool only; the actor already has local command/file authority, so there is no capability gain. Suite names come from the locally produced baseline JSON and are passed as one argv element, preventing shell injection.
- **Secrets and disclosure (I):** the full changed-source/evidence sweep found no credential, password, API key, private key, bearer token, or credential-bearing URL. Receipts contain local paths, SHAs, test diagnostics and timing. Raw suite output could only disclose what the trusted operator elects to commit; the reviewed committed output contains no secret or cross-user data.
- **Exports/interpreted output (T/I):** deletion of `render-brief.py`, its test/references, and all 102 HTML derivatives removes the browser-interpreted surface. No replacement HTML, CSV, spreadsheet, or formula-injection surface exists. The current tree has no production/test/command reference to `render-brief` or `md_to_html`, so a c4 Markdown-only ship briefing with no `.html` sibling remains possible.

## c3 remedy verification

1. `notes/receipt-scripts/feat68-cleanpin.py:25-33,59-63` has exactly one `subprocess.run([sys.executable, s], ...)` inside the per-suite loop. That call's `p.stdout`/`p.stderr` feed both the table hashes/comparison and `outputs[s]`; raw-difference generation reads only `outputs[s]`. Grade-lock subprocesses are separate and are not suite executions.
2. `notes/clean-pin-byte-receipts.md:17-31` states the feature-worktree root, sets `SCRIPTS=.harness/harness/features/FEAT-68-complex-function-third-wave/notes/receipt-scripts`, invokes the generator, and cites `clean-pin-byte-receipts.generated.md`. The committed generated receipt reports 53/57 and its D-02..D-05 bytes match `notes/build-divergences.md:25-46`. I executed the exact preserved step-3 command from the feature-worktree root: it exited 0, resolved the full baseline/pin SHAs, ran 57 suites once each, reported 53/57, produced pin-grade exit 0 and baseline-grade exit 1, and generated fresh nondeterministic temp/timing bytes as A-1 predicts. The generated evidence input was restored unchanged after this required reproduction.

No exploitable OWASP or STRIDE regression, security must-fix, or surviving prior security finding remains.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The complete 178-path diff is security-clean; authorization remains deny-default, interpreted HTML is removed, and both c3 receipt-provenance remedies are freshly verified."
  in_scope: true
  scope_reason: "The diff changes authorization/path enforcement, untrusted plan/API/filesystem handling, subprocess-backed receipt generation, raw output and hashes, and browser-interpreted exports; all 178 paths and every named shared artifact were censused before assessment."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - boundary: "Agent-supplied target paths and manifest grants -> classify/domain authorization"
      stride: "T|E"
      mitigated: true
    - boundary: "Plan, board/API, hook, and filesystem input -> routing/audit/migration verdicts"
      stride: "T|R|D"
      mitigated: true
    - boundary: "Operator argv/environment and suite output -> detached-checkout receipt and auditor decision"
      stride: "T|R|I|D"
      mitigated: true
    - boundary: "Markdown/HTML records -> human browser"
      stride: "T|I"
      mitigated: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-68-complex-function-third-wave/.harness/harness/features/FEAT-68-complex-function-third-wave/notes/review-harness-security-reviewer-c4.md
```
