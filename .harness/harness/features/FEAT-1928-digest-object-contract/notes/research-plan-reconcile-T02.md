# T-02 reconciliation — bundled runtime provenance

T-02 now separates bundled-runtime identity from canonical-suite source provenance without removing any behavioral gate. BRIEF is pending; plan approval remains approved and requires main-session revocation followed by user-authorized re-signing. The sole mandated plan check exited 1 on the two existing, out-of-scope T-04 anchors; T-02 resolved all 36 anchors.

## Scope and adequacy notes

- Only T-02 verify and its last intent paragraph changed in plan.yaml. The sole removed verify conjunct was the hardcoded source-checkout HEAD equality. All ten parallel Harness suites, the --verify-receipt call, and all four absolute bun test paths remain verbatim. T-01/T-03/T-04, tasks, decisions, routes, and file ownership were not amended.
- The earlier sentence naming OMP's “pinned canonical” suites is unchanged as requested. Its qualification is the last paragraph's requirement to record the actual canonical-suite checkout SHA at execution time, commands, and results in validator-parity.md, not enforce a historical SHA at verify time. This existing T-02-owned artifact is SC-03's source-identity evidence; it is not evidence identifying the live binary. SC-03 is unchanged, with all four OpenAI/Anthropic suites still mandatory.
- The actual removed equality SHA was d0d1f81054a82d0e76d3f0bce42d8a706fe8cb10. The conflicting handoff spelling d0d1f81054a82d0e76d3f0bce412a8d706fe8cb10 is not that SHA. notes/research-digest-object-contract.md:3,40 records the former as the historical suite baseline and reports all four suites passed together there. Neither is asserted to be the current source checkout HEAD; no checkout HEAD command ran here.
- Operator-supplied runtime facts: /Users/molchairuangutai/.bun/bin/omp is bundled OMP 18.6.0, without a runtime git checkout or npm gitHead. The operator's gh api repos/can1357/oh-my-pi/git/ref/tags/v18.6.0 resolved source SHA 89d2610993af69427574bde17791df63906ec4e5. This is release metadata provenance, not measured binary identity. The amended intent requires installed version, launcher path and invocation-time sha256, and this explicitly labeled release source SHA; checkout-runtime HEAD is applicable only if the invoked runtime actually runs from that checkout. No launcher hash or runtime behavior was measured by this PM run.
- SC-05 recommendation: stronger installed-package identity wording, applied under the explicit authorization. Keeping “OMP SHA” alone would invite conflating source metadata with bundled executable identity. The criterion retains pinned review_sha inspection, Harness SHA, provider/model, exact invocation, null rejection, retry, valid completion, exit status, and sanitized transcript hash. Verification gaps now disclose the need for a fresh credentialled bundled-runtime receipt. BRIEF Approval is pending with stale signer/date cleared.
- The historical live receipt remains untouched: notes/live-digest-object-probe.md:5-15 reports a 2026-09-30 run at OMP 4620bb8338e0ecace7ea237da9d5088d16068617. It is not a rerun against installed 18.6.0. Explicit null rejection, same-job retry continuity, conforming completion, and refusal of dry-run/synthetic evidence remain mandatory; these are not retired lineage probes. No live probe, receipt verifier, project suite, build, lint, or formatter was executed here. Source/test work remains main-session-direct under DEC-174.

## Actual amendment commands and receipts

Control-plane --help and amend --help were read; amend --show supplied the compare-and-swap hashes below. Temporary raw value files carried the replacement values and were removed after successful writes.

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --key tasks --id T-02 --field verify --expect-sha256 47fd408132a1dc28e71ea56adf723882fd5f0f3d3a84c87c763369379496c2fe --value-file /tmp/feat-1928-T02-verify.txt
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py amend --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --key tasks --id T-02 --field intent --expect-sha256 67666145147d66f1f83dccb04d07a4c5fa60f266613fd97e3475e48f5a1adbeb --value-file /tmp/feat-1928-T02-intent.txt
```

Both exited 0 and printed respectively AMENDED tasks:T-02.verify / AMENDED tasks:T-02.intent, followed by APPLIED and the absolute plan path. Neither emitted APPROVAL-RESET:, so no gh-sync status command was run. Each tool automatically emitted check-state --changed diagnostics, including INV-40: T-02's new intent/files/verify hash differed from the signed 1a292e26304a… with no ledgered T-02 amendment (intermediate 6130ef2a00b3…, final 3eee6784b022…). These are not clean validation receipts. Ancillary output named resolved INV-32 findings, absent referenced run directories, and pre-existing INV-23 STATE.md notes for other features; none was edited.

The control-plane plan_merge/amend.py::_amended_text explicitly preserves approval on existing-field amendments. After both writes plan.yaml approval still reads status approved, approved_by main-session, date 2026-09-29; BRIEF.md reads status pending with empty approved-by/date. The T-03 precedent is runs/plan-amend-T03-product/digest.md:37-43. PM neither revoked nor signed approval.

## Single mandated check

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract
```

Executed exactly once after amendments; exit 1, stdout:

```text
OK T-01 22 anchor(s) resolved
OK T-02 36 anchor(s) resolved
OK T-03 6 anchor(s) resolved
FAIL T-04 files: .claude/skills/harness/bin/plan_merge/panel.py#_digest_mapping: no definition or token '_digest_mapping' in .claude/skills/harness/bin/plan_merge/panel.py
FAIL T-04 files: .claude/skills/harness/bin/plan_merge/panel.py#_fenced_blocks: no definition or token '_fenced_blocks' in .claude/skills/harness/bin/plan_merge/panel.py
OVERLAP tests/integration/canonical-reader-classification.json: T-01, T-04
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract: 4 task(s), 74 anchor(s) resolved, 2 failure(s)
```

The two failures and overlap are existing non-target T-04/T-01 plan issues, not regressions attributed to T-02. Reported only; no repair or retry occurred.

## Main-session approval commands — not executed

Run revocation before considering the amended plan approved. Re-sign only after the operator approves the reconciled plan and strengthened BRIEF; this note does not grant approval. The exact CLI arguments were read from control-plane plan-merge.py::_register_sign_approval and VERBS. An attempted sign-approval --help was refused by the persona gate; no signing invocation or approval write occurred.

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py revoke-approval --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --by main-session --reason 'Reconcile T-02 bundled-runtime provenance and strengthened SC-05'
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py sign-approval --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml --by main-session --date 2026-10-03
```

## Open questions

1. Main session: revoke the preserved signature, obtain operator approval for plan and BRIEF, and re-sign through the exclusive approval route. Blocking approval, not the completed authorized edits.
2. Lead/main: disposition the pre-existing T-04 anchor failures and T-01/T-04 overlap separately; this assignment expressly forbids fixing them.
3. Main: gather the fresh bundled-runtime receipt after the concurrent DEC-174 probe changes; this PM run does not discharge SC-05 or re-test SC-03.
4. Harness owner: peer messaging through write agent://CorrespondingSalamander.PriorTuna was incorrectly routed to the filesystem domain guard as agent:/CorrespondingSalamander.PriorTuna; the required write xd://report_issue attempt was similarly refused as xd:/report_issue. No workaround was used.

## Principles applied

- Redesign From First Principles: runtime identity is described directly as the installed invocation's version/path/hash plus separately labeled release metadata, not a source-HEAD requirement with a bundled-runtime exception. Canonical-source evidence stays separate without weakening its behavioral suites.
