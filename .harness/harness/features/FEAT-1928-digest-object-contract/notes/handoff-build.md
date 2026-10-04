# Handoff — FEAT-1928-digest-object-contract, build → validate — code verified at 4379809b; final review pin in feature.json, seq-14

## Next

1. Main completed direct source/record reconciliation and verification: all 120 Python files passed, hook suite 105/0, canonical provider suites 111/0, actual clean-tree OMP null-rejection → same-job retry → valid-completion proof 18/18, receipt verification 33/33. Read `notes/verification-current.md`, `notes/code-risk-current.md`, and the fresh receipt/transcript. Historical live evidence is unchanged. All four tasks are done and all six cards are Review; main records the final evidence-inclusive pin before dispatch.
2. Successor orchestrator, first act: `run-start … --succession continue` on the first validate run. Main has closed `simplify-eng` as BLOCKED with one cycle: the original assessment is retained; `return-object-canonical.json` explicitly records its offline re-expression, and the worktree validator rendered the fence without looking up or releasing a claim. This is not a fresh review or a PASS.
3. Read main's recorded `feature.json.review_sha`, then ONE `validate` dispatch to `harness-validator-lead` from the pre-cutover main control plane over that exact SHA. QA consumes actual proof outputs and independently assesses coverage/fail-first; goalcheck grades SC-01..SC-08. Bind the live receipt's seven under-test hashes to the final pin (evidence commits must not change source). Clean panel → `notes/handoff-validate.md` and ship briefing. Do not merge, ship, or remove the worktree: main owns those already-authorized acts.

## Trust

- T-02 retains four canonical provider suites, ten Harness suites and the fresh receipt verifier; the retired hardcoded checkout equality is removed. All 38 T-02 anchors resolve — plan-merge check, main session — VERIFIED
- T-02 intent and BRIEF SC-05 distinguish installed launcher identity from release-tag source metadata; T-04's two deleted-symbol anchors are re-resolved without reducing scope. All four tasks' 76 anchors resolve with zero failures; their classification-file overlap is intentional — plan-merge check, main session — VERIFIED
- SC-03 canonical provider-suite source identity, exact commands, and observed results are recorded in `notes/verification-current.md`; installed-runtime identity is separately recorded in the fresh receipt — main-session execution — VERIFIED
- Simplify's original BLOCKED assessment remains truthful; main applied F-01/F-04, resolved MC-1, preserved assertions, and recorded backlog-only dispositions for inherited/advisory findings. Final changed-function grading has no high findings and eight explicit grade-2 reasons — `notes/ship-review-simplify-eng.md`, `notes/code-risk-current.md` — VERIFIED
- Full Python pool 120/120 PASS; hook suite 105/0; provider suites 111/0; fresh live probe 18/18 and receipt verifier 33/33 at clean code candidate `4379809b` — `notes/verification-current.md`, `notes/live-digest-object-probe-current.md` — VERIFIED
- cycles_used 3 of 10 (plan-c1 1, plan-reconcile-T02b 1, simplify-eng 1); all 14 runs are closed — feature-record close-run, main session — VERIFIED

## Dead ends

- Do not reintroduce `.omp/runtime-pin.json` or a `rev-parse HEAD` equality test; #2000 retired the pin and the lineage probe — c070395c — VERIFIED
- Do not read T-04 `plan-merge check` anchor failures `_digest_mapping`/`_fenced_blocks` as defects: T-04's intent deletes both symbols — plan.yaml#T-04 — VERIFIED
- Do not hand-author the fenced YAML in any run digest — that is the live-fence SC-08 forbids; the validator renders it — BRIEF.md#SC-08 — VERIFIED
- Do not treat `cycles_used < FAIL runs` as acceptable: check-state refuses it; the regate run after a FAIL carries the cycle — feature.json — VERIFIED
- `write agent://Main` and `write xd://report_issue` are refused by check-domain for orchestrator, pm and eng lead alike — hook output — VERIFIED

## Working set

- .harness/harness/features/FEAT-1928-digest-object-contract/feature.json
- .harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml
- .harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md
- .harness/harness/features/FEAT-1928-digest-object-contract/runs/plan-reconcile-T02-product/digest.md
- .harness/harness/features/FEAT-1928-digest-object-contract/runs/plan-reconcile-T02b-product/digest.md
- .harness/harness/features/FEAT-1928-digest-object-contract/runs/simplify-eng/digest.md
- .harness/harness/features/FEAT-1928-digest-object-contract/runs/simplify-eng/return-object.json
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-plan-reconcile-T02.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/research-plan-reconcile-T02b.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/verification-current.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/code-risk-current.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/ship-review-simplify-eng.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.md
- .harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.transcript.jsonl

## Done when

Scope: independent validation of the signed four-task plan over one pinned candidate sha, all SC-01..SC-08 graded
Authority: approval:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#Approval
Authority: plan-task:T-02.verify
Authority: brief-perspective:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#operator
