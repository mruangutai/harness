# Briefing — BUG-20261006-fleet-planning-recovery — pending plan, simplify pass done, return refused

**Where it stands.** The five-task repair plan and BRIEF are complete and `pending`. The mandatory pre-signature four-angle `harness-simplify` pass ran as four separate read-only readers under `harness-eng-lead`; all four completed and their receipts are on disk (13 consolidated advisory findings, none a scope or design correction, none touching the settled set). The lead's valid structured return was then **refused by the host hook** ("authorization has no trusted hook-owned digest binding", #2110) on both the first and the resume dispatch; its run is closed on the ledger as `BLOCKED` via the governed `close-run --refused-return`, cycles 0. Nothing was applied to `plan.yaml`/`BRIEF.md`; no signature, GitHub/Kaya write, build, test, lint or formatter ran. Planning artifacts stay **uncommitted** because canonical check-state exits 1 on honest findings (below).

No report round was spawned. Assembled from: `runs/2026-10-06-1-plan-product/digest.md`, `runs/2026-10-06-2-simplify-eng/{digest.md,state.yaml}`, the four `notes/receipt-harness-*-2026-10-06-2-simplify-eng-*.md`, `notes/research-…-goalcheck-plan.md`, `notes/research-…-apply-plan.md`, `runs/2026-10-06-1-plan-product/panel-c1.md`.

## Done-when, graded (planning coverage only — no SC is delivered)

| Perspective | Plan goal-check | Discharged by | Evidence |
|---|---|---|---|
| operator | covered | SC-01, SC-02, SC-08 (T-01/T-02/T-03–T-05) | `notes/research-BUG-20261006-fleet-planning-recovery-goalcheck-plan.md` |
| orchestrator | covered | SC-03, SC-05 (T-01/T-02/T-04) | same |
| reader | covered | SC-04, SC-07 (T-01–T-04) | same |
| code maintainer | covered | SC-01, SC-06 (T-01/T-02) | same |

SC-01…SC-08 all `not_met` (implementation, pinned review and operator UAT are future work).

## Legitimate anchor / panel / goal-check evidence (unchanged by this run)

- `plan-merge.py check --file <plan.yaml> --root <worktree>`: `CHECK: 5 task(s), 42 anchor(s) resolved, 0 failure(s)` (T-01 33, T-02 6, T-03–T-05 1 each) — pm, `notes/research-…-apply-plan.md`; main session independently reproduced exit 0 (`notes/main-session-plan-review.md`).
- `record-panel --cycle 1` exit 0; `plan.yaml` `panel.readers`: scope (code-reviewer) ran · should-not-exist (fable-advisor) ran · design (ui-reviewer) ran, self-scoped out · goalcheck (pm) ran. Findings: PF-d051… high **resolved** (T-01/T-03/T-04 canonical target-local authorization note); PF-2157… med proportionality/task **open**; PF-aa1a… info **resolved/disclosed**; PF-0dbb… info endorsement.
- `propose-rework`: 2 rounds / 90 minutes for 5 tasks (main-session note).
- Task count: 5, all `execution_agent: main-session-direct` (DEC-174 / NOBODY routes). Run 1 verdict FAIL = preserved scope-reader roll-up with **zero send-backs**; `cycles_used` 0 throughout, genuine.

## Four-angle simplify pass — findings and dispositions (FLAG-ONLY; pm alone may apply)

Readers: reuse (backend-dev, 7), simplification (backend-dev, 5), efficiency (dev-ops, 2), altitude (dev-ops, 5); 19 raw → 13 mechanisms. Mission altitude and T-02..T-05 altitude: empty (a real result). T-01 size itself was weighed by both simplification and altitude and **left**: each mechanism closes a named SC on an existing seam; the shared evidence resolver would be the natural split seam only if S-3 is not taken.

| ID | Angle | Sev | plan.yaml | Finding → alternative | Disposition |
|---|---|---|---|---|---|
| S-1 | reuse+altitude (R-01/A5) | med | :134-135, :140 | gh-sync, INV-37, board_lifecycle, merge-gate each re-derive "factory.repo → declared → product_config/board_for, no fallback"; issue-type overrides come from owner cfg (`load_config`:309) — same leak class. One `resolve_binding(feature_doc, root) → (repo, board, issue_types)` named in intent, called by all. | **fold-in** (one sentence naming the home) |
| S-2 | reuse (R-02) | med | :148 | Fake-gh trap: `product_config` reads via `FACTORY_GH`, gh-sync via `GH_SYNC_GH`; `gh_sync_support.run` sets only the latter, so fleet-case tests hit real `gh` or SC-01's "no Harness mutation" log is vacuous. Set both in `run`, add one shared contents handler. | **fold-in** (T-01 tests paragraph) |
| S-3 | reuse+simplification+altitude (R-03/F1/F5/A3) | med-low | :136, :141, :143, :145 | Confined feature-local path + sha256 reference is specified three times (cycle_evidence, refusal, history/recovery) with three authorization shapes; `_require_decision_file` (feature-record.py:383) is the existing, looser precedent. One `evidence_ref` `$def` + one resolver/verifier in `feature_schema`, used by writers, readers, recover-mirror; T-03/T-04 point to it. Do **not** migrate `set-rework`/`raise-cycles` (scope). | **fold-in** |
| S-4 | reuse (R-04) | low-med | :138, :140 | Recovery mode and gate command text should derive from existing `recovery_command_for` (feature_schema.py:330-345); today the text is hard-coded at gh-sync:1366-1399, merge-gate:254, post-merge-sweep:260. Extend that one function; route all three. | **fold-in** |
| S-5 | reuse (R-05) | low | :140 | "Reuse pure provenance/receipt predicates in feature_schema" names predicates that don't exist; allowed-receipt set is literal in merge-gate:247, post-merge-sweep:256, board.py:308. Say: create one `receipt_allows_merge(doc, bound_repo)` and delete the three literals. | **fold-in** (wording) |
| S-6 | reuse (R-06) | low | :136, :141, :143 | ISO-8601/sha256 regexes inline in feature-schema.json (×5) will be pasted ~12 more times; `$defs.timestamp`/`$defs.sha256` for new fields. [INFERENCE] error-text shape under `$ref` unconfirmed. | **briefing-row** B-1 |
| S-7 | reuse (R-07) | low | :167-168 | T-02 verify omits the existing index-drift check for its own deliverable: append `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md` (expect empty). | **fold-in** (verify) |
| S-8 | simplification+altitude (F2/A1) | proportionality/task, med-low | :141 | `cycle_evidence.reported_cycles` is a third copy of one integer (`runs[].cycles_used`, digest `cycles_used`); store `{source,path,sha256}` and check `run.cycles_used == digest.cycles_used` via `digest_record`. Explicit count only for operator-history. | **fold-in** |
| S-9 | simplification+altitude (F3/A2) | proportionality/task, low | :143 | `return_status: refused` (single-valued) duplicates presence of `refusal`; `validation_exit=1` is constant for source=close-run. Keep the typed `refusal` object alone (BLOCKED-only). D-04's "typed refused-return provenance" is preserved. | **fold-in** |
| S-10 | simplification+altitude (F4/A4) | proportionality/task, low | :136 | `github.history[]` hand-lists the github field set a second time; `previous` should validate against the same github sub-schema (`$ref`, minus history/recovery), copied verbatim so absence-vs-value is preserved. | **fold-in** |
| S-11 | efficiency (E-1) | low | :149, :187, :220 | "Full matrix once after all tasks land" is ambiguous against operator-gated T-03..T-05; state: once at the pinned review_sha after T-02, before T-03 activation; T-03..T-05 add no code. | **fold-in** (wording) |
| S-12 | efficiency (E-2) | low | :132, :149 | 60 s focused ceiling is unmeasured; record measured wall time at first green, move the slowest case to the full matrix rather than raise the claim. | **leave** (note at build) |
| S-13 | simplification (F2 tail) | low | :141 | Optionally derive `close-run`'s count from the validated digest and drop `--cycles-used` — a CLI change, not implicit. | **briefing-row** B-2 |

None is a required scope/design correction; none contradicts the confirmed intake; none re-litigates PF-2157/PF-aa1a. S-1/S-2/S-3 are the ones worth a pm fold-in before signature because they bear on SC-01's proof and SC-04's "same hash-bound reference" clause; the rest are text tightening the executor can also carry as build notes.

## Open, approval-visible tradeoffs (neither is operator-approved yet)

1. **Recovery-marker read-back** (PF-2157…, med, `scope: task`, open) — retained by pm in T-01/T-02 (D-02); fable-advisor's alternative is refuse-and-operator-adopt. Simplify readers found no new cost beyond the panel's; marker scan would be new code (no issue-by-milestone reader exists) and the milestone 422 title lookup is not a template for it. Operator keeps or overrules at signature.
2. **Fleet-wide forward evidence duty** — `run-end --digest` required for every new/changed per-run attribution (SC-03, PF-aa1a… info, disclosed in BRIEF Constraints). Operator approves consciously at signature.

## The refused-return blocker (reported, not repaired)

- Run `2026-10-06-2-simplify-eng`: `state.yaml` verdict PASS, 4/4 steps complete; `digest.md` prose only, no fenced record; `validate-digest.py harness-eng-lead <digest.md>` → `BLOCKED (contract violation)` (no record to read). Lead's yield on both dispatches: object valid per schema, persistence refused by `check-digest` for missing trusted hook-owned digest binding; claim released. Ledger: `BLOCKED`, `cycles_used 0`, `code_grade n_a`, regate judgement recorded at run-start (reason: prior FAIL is a preserved roll-up, not a fix round).
- This is a second live instance of the class this feature repairs (D-04 / SC-04 / SC-05: execution completion ≠ accepted return; today's record cannot carry refusal provenance). The hook is out of scope for a planning-only authorization (#2110) and was not patched.
- Consequence: any further governed lead dispatch in this worktree (e.g. a pm fold-in run) would likely be refused the same way, so no product-lead apply run was dispatched.

## Validation observations (exact)

`check-state.py --feature BUG-20261006-fleet-planning-recovery` from the worktree copy, exit 1:
- VIOLATION INV-1: BRIEF.md not approved (expected: pending plan).
- VIOLATION INV-7: `cycles_used=0` but 1 FAIL run recorded (the honest zero-send-back roll-up; the FAIL-floor is the defect under repair).
- VIOLATION DEC-156: `runs/2026-10-06-2-simplify-eng/digest.md` has no fenced record (the refused return above).
- VIOLATION INV-37: no `github.build_entry`; remedy named is `gh-sync.py open`, which this feature suspends.
- notes: plan approval pending; feature directory untracked by HEAD (not gating).
No commit was made; none is required to deliver the pending plan, and no check bypass is requested.

## Spend

2 runs; wall clock 47 min; tokens 194,836; `rework_minutes 0`, `rework_rounds 0`; `cycles_used 0/10`; judgements 2 (mission plan; regate). `max_total_runs` not approached. Amendments: none — overrule rate 0/0.

## Proposed backlog (all residual; strike by ID)

| ID | Nature | Row |
|---|---|---|
| B-1 | chore | feature-schema.json: `$defs.timestamp`/`$defs.sha256` for new fields (S-6) |
| B-2 | enhancement | `feature-record.py close-run`: derive the cycle count from the validated digest and drop `--cycles-used` (S-13) |
| B-3 | bug | Hook `check-digest` refuses a valid lead return for missing trusted digest binding (#2110); planning-only authorization did not cover it |

## What the operator decides next

- Whether pm folds S-1..S-5, S-7..S-11 into the pending draft before signature (one product run, once the return hook accepts returns) or accepts them as build-time notes and signs the current text.
- PF-2157 keep/overrule; conscious acceptance of the fleet-wide evidence duty.
- Signature (`sign-approval --rework rounds=2,minutes=90` proposed), recovery authorization and implementation remain future user actions.
