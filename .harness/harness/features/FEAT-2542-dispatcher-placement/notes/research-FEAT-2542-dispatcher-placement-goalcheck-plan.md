# Goal-check (plan exit) — FEAT-2542 against the operator's grilling

**BLUF. FAIL, narrowly.** The plan delivers the operator's stated intent in all four
perspectives and in eight of the nine grilling checks below. One check is partial. The grilling
says to "extend case-33's matrix with product→code-reviewer rows". The plan puts those rows in a
new `case_38` instead, and that case carries only four of case 33's five bound-child shapes. **Case 33's
"a foreign feature-tree root" shape has no row for the product-lead → code-reviewer pair.** The
fix is one row, added by an amend to T-01's intent. Nothing else needs to change.

- Source of intent: `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-dispatch-guard-bundle-a-2026-11-26.md`
  (Q1–Q5 and the full ruling).
- Graded: `BRIEF.md`, `plan.yaml` and `notes/research-FEAT-2542-dispatcher-placement-characterization.md`.
  All three are untracked in the worktree at base `2e7a2c77` (approval pending), so I read the
  working tree; nothing is committed to pin yet.
- `plan-merge.py check` (control-plane copy, run read-only): 2 tasks, 5 anchors resolved,
  0 failures.

## Perspectives (one line each)

| Perspective | Grade | Carried by |
|---|---|---|
| operator | **pass** | SC-02 and SC-05 (T-01 case 39, case 40, case 41 and the case 38 failure rows; `source_issues: [2542, 2532]`, re-checked by T-02 verify) |
| orchestrator | **pass** | SC-01 (T-01 case 38: `c38/distill/distill` proceeds; `c38/distill/plan` and `distill-pending/plan` refuse, so relabeling fails in both directions; the plan and norun rows keep their base outcomes) |
| reader | **pass** | SC-03 (research note Appendix A; T-01 Step 2 predicted_red/observed_red inventory plus the Pin run; T-02's terminal `tested_sha` equality) |
| code maintainer | **pass** | SC-04 (T-02 DEC-258 with Chose/Over/Because/Tradeoff/Record, lineage to DEC-100/174/204/214/218/228/250/253 with none amended, and an index row with a hand-written ruling) |

## Grilling checks

| # | Grilling item | Grade | Evidence |
|---|---|---|---|
| 1 | #2532 discriminator inside `_mission_scope`, keyed on trusted placement, no preflight reorder | met | T-01 Step 3(iv): `plan_route = … and _placed_distill_feature() is None`. Placement goes claim → `find_run_claim` persona-matched → `_distill_run_feature` → `registered_destination` → `DISTILL_RUN_RE` (base `dispatch-guard.py#_distill_run_feature`, `#_registered_run_id`). Step 3(iii) adds `_dispatcher_placement()` ahead of the preflights but keeps `_start_preflight` before `_distill_preflight` (the base module sequence). D-02 rejects the declared-mission, run-id/phase and panel discriminators. |
| 2 | #2542: five states each an exit-2 lineage denial with cause and remedy; `emit_unavailable` rejected; Main/non-lead unchanged; claim-step pass-through unchanged | met | Step 3(i)–(ii) gives the cause tokens and per-cause remedies plus `find-run`. Each lineage row asserts `exit`, `claim`, `cause`, `remedy` and `unavailable` (empty), plus `bytes` for the unreadable states. Case 41 runs the controls in unreadable-owner and escaped-oserror. That proof is sound: at base `find_run_claim` is called only in `_dispatcher_feature`, which the task deletes, so a control reaching it would now exit 2. Step 3 leaves the terminal claim `try/except` with its `emit_unavailable` unchanged, and the existing f2274 case (`_f2274_unavailable_fires`, "the registry's own claim-step failure") stays in the suite. |
| 3 | New DEC; no DEC-100/DEC-253 amendment | met | T-02 appends DEC-258. `decisions_affected` lists every DEC as `keep`, DEC-100 and DEC-253 included. Step 0 stops on a renumber. DEC-258 is free today in the worktree, at `origin/main` (2e7a2c77) and in the control plane (`grep -c '^## DEC-258 '` gives 0, 0, 0). |
| 4 | SCs by class with LEAVE lists | met | SC-01 is route class × mission and SC-02 is placement class. Each has a LEAVE list, and both require fail-first at base. |
| 5 | SC-characterization discharged before signature by the measured note, then repeated base-vs-pin at build | met | The research note covers 98 measured rows at `2e7a2c77`, with a branch witness and a filecmp check of the instrumented copy. T-01 Step 2 records the base run and Step 4 the pin run, and T-02 checks `tested_sha` equality at the end. Advisory: `c38/distill/foreign-feature` and `c38/distill/no-tree-root` have no measured row in Appendix A. They are first measured at build, through predicted_red = observed_red. |
| 6 | Non-goals verbatim | met | BRIEF `## Out of scope` matches all five grilling non-goals and their reasons. The plan never touches the hook, validate-digest or `expertise_apply`, and T-01 verify keeps `inflight_registry.py` byte-identical. |
| 7 | Test matrix | **partial** | Met: placement-state cases (39); exemption-does-not-fire-on-failed-placement (case 40); cases 32–37 stay green (Step 2 requires cases 1–37 to pass, verify runs the whole suite); `sc02_scope_reader` and `sc02_plan_status_refusals` stay unmodified (verify checks that `test-lead-start-return.py` is byte-identical). **Gap:** case 33 tests five shapes for each pair (base `test-dispatch-guard.py#case_33_every_child_of_a_bound_distill_run_carries_the_mission`): no mission, conflicting (validate), no tree root, foreign feature-tree root, and mission+tree. Case 38 covers four of them for product-lead → code-reviewer (`missing`, `other`, `no-tree-root`, `distill`). It has no foreign-tree-root row. That check is `_require_feature_tree_root` in shared code, which is inferred coverage, not executed coverage. The T-01 `files:` anchor `#case_33_…` also names a function the intent never edits. |
| 8 | Every task main-session-direct | met | T-01 and T-02 are both `execution_mode: main-session-direct` with DEC-174 reasons, and all four `lanes:` rows are main-session-direct. |
| 9 | Rework 2 rounds / 90 min, proposal only | met | BRIEF `## Constraints`: "proposed for the signer, not approved". plan.yaml claims no budget, and the template has no such field. |

## Remediation (owner: pm, by `plan-merge.py amend` on T-01)

Either:

- add the row `c38/distill/foreign-tree-root` to case 38: distill placement, mission `distill`,
  child declares X with `HARNESS-FEATURE-TREE-ROOT` pointing at a foreign root; outcome exit 2,
  claim, cause `declared feature-tree root`; or
- add `("harness-product-lead", "harness-code-reviewer")` to case 33's pair tuple. This also makes
  the `#case_33` anchor true.

Either way, add its base prediction to the Step 2 inventory. [INFERENCE: base refuses it at the
plan-route mission rule, so I expect only `cause` to be red; build-time observed_red settles it.]

## Advisory, not grading

- PF-0017 (low, open) covers the id-less-lead rows in case 41. These rows are consistent with the
  grilling, whose contract scopes to "a dispatcher in `LEADS` carrying `harness_agent_id`". The
  signer's OQ-1 ruling governs them.
- Case 38 rotates missions across failure states, and case 40 puts only not-found and
  persona-mismatch on a plan-run (the base-exit-0 product class). Case 39 covers the base-exit-0
  class in all eight states through the eng-lead pair. This is accepted proportionality
  (PF-658a), not a gap.

## Expertise applied

- O-14: the foreign-tree-root check is inferred through a shared helper, not executed for the
  product pair.
- P-04: I asserted each case-33 shape separately, not as a count of "rows added".
