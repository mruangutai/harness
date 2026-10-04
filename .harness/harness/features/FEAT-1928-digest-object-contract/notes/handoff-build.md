# Handoff — FEAT-1928-digest-object-contract, build → validate — written at 14f04a75 (worktree HEAD; records uncommitted), seq-14

## Next

1. Main session: commit the reconciled source and signed records; rerun the complete Python pool and hook suite; land the actual bundled-runtime null-rejection → same-job retry → valid-completion proof at `notes/live-digest-object-probe-current.md` and its transcript. The historical receipt remains byte-unchanged. T-02 and T-04 are re-signed under `notes/approval-2026-10-04.md`; BRIEF is approved and all cards are Building.
2. Successor orchestrator, first act: `run-start … --succession continue` on the first validate run. Main has closed `simplify-eng` as BLOCKED with one cycle: the original assessment is retained; `return-object-canonical.json` explicitly records its offline re-expression, and the worktree validator rendered the fence without looking up or releasing a claim. This is not a fresh review or a PASS.
3. Pin `review_sha` to main's final candidate commit (ancestor-of-tip check, P-08), `gh-sync.py status <feature-dir> review`, then ONE `validate` dispatch to `harness-validator-lead` from the pre-cutover control plane over that sha; qa consumes main's proof outputs (suite run, live receipt) and runs its own tests only where needed; goalcheck SC-01..SC-08; clean panel → `notes/handoff-validate.md` and ship briefing. Do not merge, ship or remove the worktree.

## Trust

- T-02 retains four canonical provider suites, ten Harness suites and the fresh receipt verifier; the retired hardcoded checkout equality is removed. All 38 T-02 anchors resolve — plan-merge check, main session — VERIFIED
- T-02 intent and BRIEF SC-05 distinguish installed launcher identity from release-tag source metadata; T-04's two deleted-symbol anchors are re-resolved without reducing scope. All four tasks' 76 anchors resolve with zero failures; their classification-file overlap is intentional — plan-merge check, main session — VERIFIED
- SC-03 suite source identity now lives in `notes/validator-parity.md` (checkout path, observed SHA, commands, results), not a verify-time pin — notes/research-plan-reconcile-T02.md — UNVERIFIED
- Simplify: 10 advisory findings (F-01..F-10, none blocking, backlog-only where an assertion would be retired) and MC-1 (probe runtime-pin read at HEAD, main already removing) + MC-2 (FEAT-495 lineage-field refusal unreachable on the OMP path; briefing row for the DEC-250 owner) — runs/simplify-eng/digest.md — UNVERIFIED
- Main reports: full Python pool 118/120 PASS with the two doc/index failures fixed directly; hook suite 105/0, provider suites 111/0; probe provenance helper smoke PASS on installed 18.6.0 / source 89d26109 — parent IRC, not on disk — UNVERIFIED
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

## Done when

Scope: independent validation of the signed four-task plan over one pinned candidate sha, all SC-01..SC-08 graded
Authority: approval:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#Approval
Authority: plan-task:T-02.verify
Authority: brief-perspective:.harness/harness/features/FEAT-1928-digest-object-contract/BRIEF.md#operator
