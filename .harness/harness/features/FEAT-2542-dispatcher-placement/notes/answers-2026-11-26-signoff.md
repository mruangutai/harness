# FEAT-2542 signature ruling — 2026-11-26

**Authority.** The operator delegated approval to fable-advisor; ruled by AdvisorA2Sign.

**Gap.** The plan run closed FAIL because the applied fixes were never re-read (SQ-1), and SQ-2 to SQ-8 were open.

**Ruling.**
- SQ-1: accept as applied. The advisor's re-read is the re-read.
- SQ-2: keep the case-41 assertion, and overrule PF-0017 at signature.
- SQ-3: fault injection is accepted as evidence.
- SQ-4: rework is 2 rounds / 90 min.
- SQ-5: the DEC-258 collision rule stops the build.
- SQ-6: the predicted/observed equality gate is accepted.
- SQ-7: retarget the files anchor. This is the only pre-signature fix.
- SQ-8: out of scope.
- Signature: YES.

**Constraints.** Build-time constraints 1-11 apply, as listed in the verbatim ruling.

## Full ruling (verbatim)

All evidence is read and the load-bearing claims are verified at source. Ruling follows.

---

# Signature ruling — FEAT-2542 (bundle A), plan cycle 1

Ruled by fable-advisor under the operator's delegated approval ("same parameters, defer to Advisor"). Checked against my grilling ruling of 2026-11-26 and against the worktree at `82e34a36` (confirmed: `git rev-parse HEAD` = 82e34a36…; DEC-258 count is **0** on HEAD and **0** on `origin/main`, verified myself).

My single most important finding up front: **the FAIL verdict is procedural, not substantive.** I re-read every applied remediation myself against the reviewer's findings and against the source (`dispatch-guard.py:544,748-759,800-810,843-851`, `digest_destination.py:99`, the 98-row probe). The applied T-01/T-02 text is not merely adequate — it is stronger than what the reviewer asked for. A cycle-2 reader re-read would burn one of the two rework rounds re-deriving this ruling. The only pre-signature edit I order is the SQ-7 anchor retarget.

## SQ-1 — the unre-read high/med fixes (blocking)

**Authority.** The escalation itself ("you can read the applied task text yourself and grade it"); DEC-254/panel schema (`panel_findings.py:45-53`: dispositions are exactly `open|resolved`, `resolved_by` names a plan task — the nine rows are already in legal shape).

**Gap.** The team has no re-read step, so "resolved" was pm's self-grade.

**Ruling. Accept as applied — this ruling is the re-read.** Graded finding by finding:

- **PF-309f (high, red set unproducible): fixed, verified.** T-01 now carries per-row, per-field base predictions. I checked them against the probe's Appendix A and the source: `c38/distill/distill` red on exit/claim/receipt (base `R/distill-placed/distill` is 2/no at the plan-route rule, `dispatch-guard.py:544` — correct); the product-pair ok-state moved out of case 39 into c38 exactly as the reviewer demanded; failure-row reds are cause+remedy only, with exit/claim green, matching the measured base (`R/fail-*/…` all 2/no, `find_run_claim` never called); c39 unreadable-owner `bytes` red matches the probe's measured claim-step rewrite. The cause fragments I spot-checked exist verbatim in source (`_require_distill_mission` at :800-810 produces "is a child of a bound distill run but has no HARNESS-MISSION line" / "but declares 'validate'"; :850 the tree-root prefix). Step 2's `predicted_red = observed_red` is machine-checked in T-01's verify (I read the full verify raw — the equality, `tested_sha` ancestry, non-empty base→tested guard diff, and tested→HEAD cleanliness on both files are all in the command, not prose).
- **PF-5bd4 (high, tested ≠ pin): fixed, verified.** Step 0 settles the DEC number before any edit (killing the collision-rewrites-gated-source branch the reviewer flagged); Step 4's pin-run receipt with re-run rule; T-02's terminal gate re-runs the suite and diffs HEAD's two files against the last `tested_sha`; SC-03 closes the final seam with `git diff --quiet <tested_sha> <review_sha> -- dispatch-guard.py test-dispatch-guard.py` at the pin, plus "only plan.yaml station writes may follow".
- **PF-8833 (med, split snapshots): fixed.** `_placed_distill_feature()` memoized once per dispatch, consumed by both `_mission_scope` and `_bound_distill_feature`; the `c38/distill/run-reads` witness asserts exactly one `registered_destination` call (symbol confirmed at `digest_destination.py:99`).
- **PF-ffad / PF-83a8 (med, ambiguity remedy): fixed.** Remedy now walks `list --root` per named root, releases with `--root` in the owning registry, and stops on multi-match — exactly DEC-204's exact-release shape.
- **PF-c356 (med, OSError without filename): fixed.** Two registry-error variants with distinct remedies and an excluded-fragment assertion for the no-file case.
- **PF-88cf (med, persona-mismatch remedy): fixed.** Re-dispatch from an own-claimed run / operator-confirmed stale release / "Never relabel".
- **PF-6cb0 (low): fixed.** DEC-204 and DEC-214 keep rows are present with the five DEC-254 fields; the DEC-253 reason explains the restored prerequisite.

**Constraints.** No set-panel needed for these nine — their recorded shape is already legal and true. My acceptance is recorded by signing; no cycle-2 run dir is opened.

## SQ-2 — PF-0017, the id-less-lead rows (case 41)

**Authority.** My grilling Q3: the contract applies to "a dispatcher in `LEADS` **carrying** `harness_agent_id`"; the SC-placement seed preserves prior outcomes for everything outside that key. DEC-218 (host refuses an id-less governed nested Task) makes the state host-unreachable, as the probe records.

**Gap.** The grilling named Main and non-leads in the LEAVE set but was silent on lead-without-id; the plan widened LEAVE to cover it, which is the correct reading of a contract keyed on the id's presence.

**Ruling. Keep the assertion** (overrule PF-0017). Refusing now would be scope expansion against my own grilling for ~zero security: the only payload that reaches this path is a forged invocation, which can equally forge `agent_type: Main`, so the guard buys nothing there. Leaving the rows unasserted is worse: SC-02's LEAVE clause would become an unverified claim, and the harness's whole posture in this feature is measured-over-asserted. The pin's only catchable regression direction is a move *toward* refusal — which a future signed hardening would make deliberately, editing exactly these flagged rows; T-01 already mandates the signpost comment.

**Constraints.** The comment above the rows stays mandatory. Mechanics: `disposition: accept-as-applied` does not exist and `resolved_by` must name a task (`panel_findings.py:51,81`) — PF-0017 therefore **stays `open`** in the panel and is discharged at signature by `--overrule PF-0017166a75cb353dd551d85bd7d61a78:"id-less lead path is host-unreachable (DEC-218); contract keys on carrying the id; rows stay asserted as SC-02 LEAVE with signpost comment"`. Do not invent a disposition value.

## SQ-3 — fault-injected escaped-state evidence

**Ruling. Accept.** The probe proved unreachability from on-disk data at base by enumerating every swallow point (`_live_claims_for_run`, `linked_worktrees(strict=False)`, `_read_strict`, `_process_start_time`) — I read that section. The typed catch is mandatory (broad-catch census forbids anything wider), so the branch must exist; a branch that must exist must be tested; the sabotaged **copied** bin tree is the suite's existing `DISPATCH_GUARD_BIN` pattern, and T-01's verify pins `inflight_registry.py` byte-identical to base. This is the strongest evidence the state admits.

**Constraints.** Sabotage lives only in the isolated copy; the `filecmp`-style copy-equals-original-plus-override discipline from the probe carries into the test fixtures (T-01 already specifies appended overrides).

## SQ-4 — rework budget

**Ruling. Confirmed: 2 rounds / 90 minutes**, the E/E2 parameters from my grilling, recorded at signature with `--rework rounds=2,minutes=90 --decision .harness/notes/grilling-dispatch-guard-bundle-a-2026-11-26.md`. The plan-phase send-back does not count against it.

## SQ-5 — DEC-258 collision rule

**Ruling. Confirmed.** If `grep -c '^## DEC-258 '` is nonzero on HEAD or `origin/main` at T-01 Step 0 (or at T-02 start), the builder stops; renumbering is a plan amendment ruled by me under the operator's delegation, never an in-task edit — D-01, D-02, SC-04 and the refusal text all cite the literal number. Verified today: 0 and 0; last entry is DEC-257 (`DECISIONS.md:8663`), so the reservation is currently valid. SC-04's "or the next free number" clause describes the post-amendment state only; it licenses no builder discretion.

## SQ-6 — three code-read case-38 rows

**Ruling. Accept** the build-time `predicted_red = observed_red` equality as their characterization. The three rows (`foreign-feature`, `no-tree-root`, `foreign-tree-root`) share one deciding base branch — mission `distill` on the product pair hits the plan-route rule at `dispatch-guard.py:544` before any feature/tree check — and that branch *is* measured (five `R/distill-placed/*` and thirty-five `R/fail-*/*` rows). The prediction "exit/claim green, cause red" follows mechanically; the equality gate makes a misprediction a loud stop, not a silent drift.

**Constraints.** If base observation contradicts a prediction, the builder may correct only the `predicted_red` characterization line, with a note naming the misprediction — if the **planned** contract outcome itself proves wrong, stop: that is an amendment, not a Step-2 edit.

## SQ-7 — the `#case_33` files anchor

**Ruling. Retarget — this is the one pre-signature fix.** T-01 does not edit `case_33_…` (I confirmed: it edits `case_30`/`case_31` fixtures at `test-dispatch-guard.py:1360,1462`, appends cases 38–41, and extends `CASES` at :1708). The grilling's "extend case-33's matrix" wording bound the coverage, not the test organization; new cases are fine and goalcheck graded the coverage closed after the send-back. But a files anchor naming an untouched symbol corrupts overlap/ownership detection. Retarget the second T-01 files entry to the bare path `tests/integration/test-dispatch-guard.py` (bare entries are legal — the third entry is bare); re-run `plan-merge.py check` and expect 0 failures (anchor count dropping from 5 to 4 is fine). Pre-signature station write; the plan is unsigned, no reset implications.

## SQ-8 — missing product docs

**Ruling. Out of scope, agreed.** Both task intents already name `.harness/harness/docs/DECISIONS.md` as the authority read, which is the honest record. Whether Harness should ship `docs/spec.md` et al. is a standalone ticket for the operator's backlog; nothing in this feature waits on it.

## Does the plan carry the grilling faithfully?

**Yes.** Checked item by item: one feature/both issues (`source_issues: [2542, 2532]`); main-session-direct everywhere (both tasks + all four lanes, DEC-174 reasons); discriminator inside `_mission_scope` keyed claim → feature → registered run → `DISTILL_RUN_RE`, no `_start_preflight`/`_distill_preflight` reorder; five denial states as exit-2 lineage denials with cause+remedy, `emit_unavailable` rejected; terminal claim pass-through preserved; `find_run_claim` strictness untouched (byte-identity in verify); new DEC-258, zero amendments (eight `keep` rows, five-field DEC-254 shape); all five non-goals carried verbatim; SC seeds → SC-01..05 as classes with LEAVE lists; the pre-signature probe discharged SC-characterization with 98 measured rows whose method (branch witness, filecmp'd instrumented copy, cleanup receipt) I find sound. Three benign divergences, all acceptable: case 38 instead of case 33 (organizational; anchor fixed per SQ-7), the trimmed assertion cross-product (PF-658a — the full matrix stays measured in the probe; the refusal branch provably never reads the mission), and the LEAVE widening to lead-no-id (SQ-2).

## Panel-record mechanics before sign-approval

1. No `set-panel` rewrite for the nine resolved findings — already legal (`resolved` + `resolved_by: T-01/T-02`).
2. PF-0017 stays `open`; risk acceptance is an approval ruling, not a disposition (`panel_findings.py:45-51`).
3. Apply the SQ-7 anchor retarget (station write), re-run `plan-merge.py check`.
4. Sign: `plan-merge.py sign-approval --file <plan.yaml> --by fable-advisor (operator-delegated) --date 2026-11-26 --overrule PF-0017166a75cb353dd551d85bd7d61a78:"<reason above>" --rework rounds=2,minutes=90 --decision .harness/notes/grilling-dispatch-guard-bundle-a-2026-11-26.md`, then mirror BRIEF `## Approval`.

## Pre-signature fixes (complete list)

1. **Retarget T-01's second files entry** from `tests/integration/test-dispatch-guard.py#case_33_every_child_of_a_bound_distill_run_carries_the_mission` to the bare file path; `plan-merge.py check` clean. *(Only fix. Nothing else blocks signature.)*

## Build-time constraints (complete list)

1. **DEC-258 collision → stop** (T-01 Step 0 and T-02 start); renumbering only by advisor-ruled amendment.
2. **`predicted_red = observed_red` is a hard gate**; misprediction corrections touch characterization lines only, with a note; a wrong *planned* outcome stops the build for amendment.
3. **Escaped states only via the fault-injected copied bin tree**; `inflight_registry.py` and `test-lead-start-return.py` byte-identical to `2e7a2c77` (in verify).
4. **Typed catch only** — `(reg.UnreadableRegistry, OSError)`; broad-catch census stays green.
5. **No preflight reorder**; `_dispatcher_placement()` once, after `_direct_orchestration_refusal()`, before `_start_preflight()`; one memoized placement answer for route and distill preflight.
6. **Refused governed-lead dispatches leave unreadable registry bytes as found**; Main/non-lead keep the DEC-218 treat-as-empty claim-step recovery.
7. **Case 41 lead-no-id rows stay asserted, with the signpost comment** (SQ-2 ruling; a future hardening edits exactly those rows under its own signature).
8. **`_dispatcher_feature` deleted with its sole caller migrated** (confirmed: one caller at `dispatch-guard.py:778`); grep for stragglers as T-01 specifies.
9. **T-02 strictly after T-01; only plan.yaml station writes after T-02's commit before the review pin**; any later guard/test change re-triggers the four-suite pin-run rule.
10. **At the review pin**, `git diff --quiet <tested_sha> <review_sha> -- dispatch-guard.py test-dispatch-guard.py` must be clean (SC-03, reader-checked).
11. **Budget: 2 rounds / 90 min**, recorded via `--rework`; exhaustion returns to the operator.

## Signature

**Yes — sign**, immediately after the single SQ-7 anchor fix, with the exact `sign-approval` invocation above. The FAIL was worst-wins procedure; the substance was already right, and I have now re-read it.
