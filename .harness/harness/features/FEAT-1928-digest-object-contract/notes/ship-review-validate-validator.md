# FEAT-1928 — ship review after validate-validator (BLOCKED)

**Bottom line: candidate `828b3605` is not ship-ready.** The independent panel returned BLOCKED (qa could not pass its gate), with five high must-fix findings, three blocking questions for the operator, and — reported by the main session during the run, outside the panel — a plan/CI budget blocker on T-02 and a freshness refusal because `origin/main` advanced two commits past the pin. Every remediation is main-session-direct under DEC-174 except M5 (documentor). A fresh candidate, a new pin, and a fresh independent panel are required before any ship verdict.

No report round was spawned. This briefing is assembled from the digests on disk: `runs/validate-validator/digest.md` (this run), `runs/simplify-eng/digest.md`, `runs/plan-reconcile-T02b-product/digest.md`, `runs/plan-reconcile-T02-product/digest.md`, `runs/plan-reconcile-product/digest.md`, `runs/plan-c1-product/digest.md`, `runs/plan-product/digest.md`, plus the five reader notes named below and `notes/handoff-build.md`. Run dirs for `plan-product-c1`, `build-main-direct`, `build-docs-product-resume` are absent (noted by check-state); their verdicts are taken from `feature.json`.

## Definition of done, graded (validate goal-check, `notes/research-FEAT-1928-digest-object-contract-goalcheck-validate-c3.md`; lead reconciliation in the digest)

| Perspective (as signed) | pm grade | lead reconciliation after qa evidence | SCs | Evidence |
|---|---|---|---|---|
| **operator** — closed object contract on every dispatch incl. main-session; malformed text/null/dispatcher schema controls rejected; live host evidence of native retry before old repair removed | partial | partial | SC-01 met, SC-04 **not met**, SC-05 met | hook suite 105/0 + constructed base RED (qa note); current receipt + transcript, seven under-test hashes individually match the pin (digest table); no automated actual OMP YieldTool-path null/retry test (M4) |
| **orchestrator** — same typed VERDICT/DIGEST/artifact object from every persona | partial | pass (typed contract; not ship clearance) | SC-02 met | object-only validation, 8 agent + 3 skill example migrations, base 121 FAIL lines / 24 agent-skill failures reconstructed by qa |
| **code maintainer** — one canonical schema per persona consumed by injection and validation; ref-free bundles; parser/renderer/fallback/tables/templates gone | partial | pass for contract and retirement; **signed verify still failing (M3)** | SC-03 met, SC-08 met | schema tests + whitelist RED, provider suites 111/0 (source identity d0d1f810); independent retirement census; DEC-237 replaces four decisions, DEC-208 bytes equal |
| **reader** — human prose then validated YAML, append-only corrections, historical digests byte-unchanged | partial | **fail** | SC-06 partial, SC-07 **not met** | M1 unauthorized append destination; advisory F2 hidden append; 291-row parity retained with 14 planned deltas vs. literal SC-06 wording (Q1) |

## Consolidated actionable set (for the main session)

Fix order per the lead: M1 → M4/M2 → M3 → M5. Full paths, reproductions and acceptance are in the digest `must_fix` and the reader notes.

| ID | Sev | Kind | Raised by | Task / route | What | Acceptance |
|---|---|---|---|---|---|---|
| M1 | high | substance | security F-SEC-01, code F1 | T-02 main-session-direct | `.claude/skills/harness/bin/validate-digest.py:1827-1935` appends to any digest path a valid yield names (cross-domain confused deputy) and does not realpath-contain relative targets with an escaping parent symlink | refuse unauthorized destinations without altering bytes; authorized no-op/correction retained |
| M2 | high | substance | qa F1 | T-02 main-session-direct | `tests/manual/probe-inflight-claim-lifecycle.py` is in the diff → `inflight_claim_lifecycle_live` (status `locally_run`, harness.json) is required; no `notes/live-omp-probe.md` receipt at the pin | credentialled live run from the worktree with retained receipt; `--dry-run` is not a receipt |
| M3 | high | substance | qa F2 | T-01 + T-04 main-session-direct | signed verify clause `python3 tests/integration/test-check-plan-routes.py --canonical-reader-self-test` exits 1 at pin and at base (8 failures / 30 missing inventory rows in `tests/integration/canonical-reader-classification.json`) | clause exits 0 with complete classification; any clause change is an approved amendment, not a waiver |
| M4 | high | substance | goalcheck F-01 (qa F3 med, code Q2) | T-02 main-session-direct | no automated test exercising the actual OMP YieldTool path for null → retryable rejection → same-job completion with its pre-change failing evidence; current RED is hook-level only | actual-host automated coverage with discriminating RED; hook mocks and SC-05 inspection do not substitute |
| M5 | high | substance | ui F-UI-01 | T-03 team / harness-documentor | `.harness/harness/docs/org.html:273-291` new `.sub` instructions at 3.421:1 light / 4.179:1 dark | ≥ 4.5:1 both themes, content retained, no global restyle |
| P1 | blocker | plan/CI | main session (preflight, not panel) | T-02 record | `check-plan-routes.py` DEC-182: T-02 machine-field count 53 vs limit 50; counts parsed files/traces items, so YAML formatting cannot fix it; two obsolete file declarations (dispatch-guard.py, test-checker-structure-locks.py byte-identical to main) leave 51 | approved-scope task decomposition or file-list correction via plan-merge verbs; no scope or criteria change |
| P2 | blocker | freshness | main session (`/harness-ship` gate) | — | `origin/main` advanced past the pin: 0d21fd02 (BUG-2003, hook URI allowances) and 60d9a729 (FEAT-495 done metadata); 0d21fd02 touches `.omp/extensions/harness-hooks.ts` / `tests/unit/omp-hooks.test.ts`, which are in this feature's diff | reconcile, re-verify source-bound evidence and live proof where changed, re-pin, fresh independent panel |

Verified at my tier before routing: the three M2/M3/M5 files are in `git diff --name-only b8e9f9c8 828b3605`; the T-01 and T-04 `verify:` clauses literally contain `--canonical-reader-self-test` (plan.yaml:217, :333); harness.json declares `inflight_claim_lifecycle_live` detect on the probe path with `status: locally_run`. M1/M4 reproductions are static reasoning by the readers, not executed exploits (digest adequacy note).

## What is clean

- Fresh qa gate at the pin: unit 46 files exit 0, integration 74 files exit 0, hooks 105/0, four canonical OMP provider source suites 111/0 (suite-source identity d0d1f810, distinct from installed omp/18.6.0 launcher identity). `matrix_ok: false` only because the touched `locally_run` kind is unrun.
- SC-05 inspection: the current receipt names Harness SHA, installed OMP version/launcher/sha256, release-tag SHA labeled as metadata, provider+model, exact invocation, strict injection, explicit-null retryable rejection, same-job retry, valid completion, exit 0; pm individually matched all seven under-test SHA-256 hashes and the transcript hash to `git show 828b3605:<path>`. Pin → HEAD (`10a9594c`) differs only in STATE.md and feature.json.
- SC-08 inspection met independently by code and pm; DEC-237 replaces DEC-122/172/216/223; DEC-208 unchanged.
- Fail-first evidence reconstructed and substantiated for SC-01/02/03/06/07 (qa note table); insufficient for SC-04 (hook-only).
- Eight grade-2 complexity reasons in `notes/code-risk-current.md` assessed and accepted by the code reviewer (`_task_dispatch`, `_yields`, `derive`, `run_live`, `verify`, `main`, `check_refusal`, `_object_shape_violations`).

## Open questions for the operator (from the panel; blocking ones gate the next candidate)

- **Q1 (blocking)** SC-06 literally promises the same verdict for every baseline case; retained parity has 14 approved intentional deltas and zero unplanned. Recommendation: pm reconciles the SC-06 wording to "zero unplanned mismatches, planned deltas enumerated" under approval — a criterion that cannot be met as written is pm's, not a fix cycle.
- **Q2 (blocking)** M3 inherited failure: repair the inventory, or amend the T-01/T-04 verify clause under approval. Recommendation: repair (the clause is signed and the failure is reachable).
- **Q3 (blocking)** SC-04 stage: the measured refusal is hook-level before `YieldTool.execute`. Recommendation: deliver the actual-path automated test (M4) rather than narrowing SC-04.
- Q4 (non-blocking) FEAT-495 record updates inside the 403-path diff have no T-01..T-04 owner — classify as unrelated bookkeeping carried by reconciliation.
- Q5 (non-blocking) `handoff_comprehension` runner_note asks for a credentialled run before a handoff-contract change ships; detect surface untouched; advisory assurance gap.

## Lead summaries, by digest

- validate (`runs/validate-validator/digest.md`): BLOCKED, 0 cycles, five readers terminal, zero send-backs, `severity_max: high`, two advisory findings retained (code F2 med: unclosed prose fence can hide the appended mapping, `validate-digest.py:1911-1935`, `digest_record.py:34-66`; qa F4 low: parity record omits three `group_errors` groups).
- simplify-eng (`runs/simplify-eng/digest.md`): BLOCKED, 1 cycle; main applied F-01/F-04 and recorded dispositions in `notes/ship-review-simplify-eng.md`. Not a PASS and not re-run.
- plan runs (`runs/plan-*`): signed plan at approval 2026-10-04 after two reconciliations; plan-reconcile-T02/T02b FAIL awaited main's re-signature (recorded regates).

## Spend and ledger

`feature-record.py spend`: 15 runs, 463 wall-clock minutes, 1,152,676 tokens, rework 18 min / 0 rounds. Cycles 3/10 (unchanged this run). Judgements: 7 (mission, finding_kind, succession ×2, regate ×2, continue=stop). `len(runs)` 15 vs `max_total_runs` — informational; the validate run earned its place: it found five highs main's own verification did not.

## Amendments (DEC-229)

No `amendment` judgements in `feature.json`. overrule rate: 0/0

## Proposed backlog (residual, non-gating; strike by ID)

| ID | Nature | Finding |
|---|---|---|
| B-1 | bug | code F2 (med): unclosed prose fence in lead prose consumes the appended YAML block; reader sees absent/stale mapping. Consider at the same writer boundary as M1. |
| B-2 | chore | qa F4 (low): `notes/validator-parity.md` should disclose the NULLABLE/SCHEMAS/FileNotFoundError `group_errors` groups and bridged rows; historical source includes an uncommitted slice. |
| B-3 | chore | Q5: `handoff_comprehension` runner_note vs. untouched detect surface — decide whether a handoff-contract change should trigger it. |
| B-4 | chore | Q4: reconciliation carried FEAT-495 record updates into this feature's diff range with no owning task; document the carry rule. |

## UAT

BRIEF has no `verify: uat` criteria; none invented.
