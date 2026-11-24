# Goal-check (plan) — FEAT-2489-plan-routes-split vs the operator's stated intent

**Verdict: yes — the applied plan (cycle 1) delivers the intent in the grilling ruling
(`.harness/notes/grilling-plan-routes-split-e2-2026-11-24.md`).** All three perspectives pass, and so does
every item the ruling mandates. Five places where the wording departs from the ruling are listed below
so the operator can see them at signature. None reverses a ruling. Read-only grading: BRIEF.md and
plan.yaml were read in the worktree, unchanged. Control plane at 261fdf72.

## Perspectives (BRIEF `## Done when — by perspective`)

| Perspective | Grade | Carried by |
|---|---|---|
| operator | pass | SC-02 (with SC-01 and SC-05 as structural proof). T-02 builds the matched-tree checker. T-03 shows it red on the stale inventory. T-04 records `notes/equivalence-final.txt` ALL PASS. `projection_confined` turns red if `tests.yml` changes. |
| code maintainer | pass | SC-01, SC-04, SC-05. T-03 does the move, the import shape, the test re-point and the provenance check. T-04 applies the inventory delta and runs the copied-bin smoke. The payoff is real: team-config grants `.claude/skills/harness/bin/**` to squads (`.harness/team-config.yaml`, the bin upsert rows), so after the cutover the two modules are squad-writable without any config change. |
| reader (qa / reviewer) | pass | SC-03 (automated, integration) and the SC-02 receipt. T-01 records the red receipt, the fix, default registration and the green receipt bound to its HEAD and BLOB. T-03 records the real red on the moved tree. T-04 brings it back to green. |

## Ruling items beyond the perspectives

| Item | Grade | Evidence |
|---|---|---|
| Q3 class-shaped contract | pass | SC-02 states one invariant for every audited tree state and argv, then a closed four-item delta that matches Q3 items 1–4. Q3 item 5 (broad-catch ceilings) is implied by SC-01: every moved line is byte-identical except one T07 key. Item 6 (instrumentation) is covered by SC-04 and T-03 item 9. Item 7 (grading) is covered by Constraints DEC-209. |
| Q4 task 1 first, no audit production code | pass | T-02 has `depends_on: [T-01]` and T-03 has `depends_on: [T-01, T-02]`. T-01's `files:` lists only the test file and two notes receipts. T-01 is red first, fixes both FAILs to the true contract, corrects the FEAT-71 docstrings and registers the canonical tuple by default (items 1–6). The runtime confirmation the ruling asked of pm is in D-03 (about 6 s). |
| Q6 SC seeds SC-01..SC-05 | pass | All five are present, each tagged with a DEC-231 standard perspective name. The engineering and qa seed tags were mapped to code maintainer and reader. The info finding's extra SC-06 and SC-07 were folded back in. |
| Named non-goals | pass | BRIEF `## Out of scope` lists every non-goal from Q6 and the Destination (audit and route logic, tests.yml, argparse/--help, test-file split, SELF_GRADED_FILES, scan/census consolidation, shipped or archived plan rows, package/__init__, DECISIONS.md renumbering), plus the Q5 citations. |
| Honest LOC framing, no line-count SC | pass | BRIEF Constraints, "Honest size". The seed's "~980 lines" was moved out of SC-01 into Constraints, so no SC counts lines. |
| Q1 all main-session-direct, none to harness-eng-lead | pass | T-01..T-04 are all `execution_mode: main-session-direct` with an `execution_reason`. No task names harness-eng-lead. |
| Q2 target shape | pass | D-01 and T-03 items 1–3: two flat modules with no sys.path edits. `_reader_source_paths` lives in canonical_reader_audit, and structure_audit imports it. The entry imports exactly the token and the two runners. main and the dispatch are statement-unchanged, with only a comment added. There are no re-exports. Tests use ordinary imports (T-03 items 5–9). The `plan_merge/check.py` comment is re-pointed (T-03 item 4). |

## Departures from the ruling's wording (for the operator at signature)

1. **SC-02 covers only a complete install, and an incomplete one now fails at import.** Q3 says the
   invariant holds "for every tree state and every argv". SC-02 holds it only with both modules
   beside the entry. A bin missing either module now dies at import (traceback, exit 1) where the base
   entry ran. This is a consequence of Q2's module-scope import, disclosed in BRIEF `## Verification
   gaps`. Only case 19b's copy list covers it.
2. **The SC-02 evidence uses matched archive trees and samples, not one tree.** Q3 asked for "all three
   CLI modes … before and after on the same tree". The plan instead compares the base commit with the
   base commit plus the pinned bin and tests overlaid (fixing finding PF-0e91). It samples six argv
   shapes and one perturbed state, and compares stderr too. Coverage of "any tree, any argv" beyond
   those samples rests on inspection (SC-01), not on a measurement.
3. **The named-plan check reads "this checkout" as the audit's corpus resolution.** Q4 says plans resolve
   "in this checkout". T-01 resolves them through `feature_corpus.corpus_path`, which in a sparse
   worktree reads the owner root (`feature_corpus.corpus_path` docstring). This matches the audit
   (`_task_files`), so the check cannot disagree with the gate. T-01 also adds a check that was not
   ruled: `canonical_reader_live_inventory_has_no_document_plan`.
4. **SC-04 is graded by inspection, not by automated tests.** The seed implied the satellites going
   green. The BRIEF grades by reading the code plus the `green-t04-suites.txt` receipt, and adds a
   `CHECK_PLAN_ROUTES_BIN` provenance check. The three integration files are not run against a copied
   bin (disclosed).
5. **The rework budget is not recorded.** Q6's "2 rounds / 90 minutes at signature" appears in neither
   BRIEF, plan nor feature.json. It is the main session's to record at signature.

## Record state the lead should see

`panel.findings` still shows PF-b25f (high), PF-0e91 (high), PF-5dbe (med), PF-293c (med) and PF-2f03
(low) as `disposition: open`. The applied text appears to address each one:
- SC-02 now has a normative invariant with samples (PF-b25f).
- The trees are matched and the receipts record runs whole (PF-0e91).
- T-01's verify is stage-aware, with its green bound to the HEAD and BLOB (PF-5dbe).
- T-02 no longer runs any AST checks (PF-293c).
- No pre-move red receipt is recorded (PF-2f03).

No cycle-2 reading has recorded these as resolved. Until one does, or rulings are signed, the open high
findings stand against signature. That is panel bookkeeping, not a goal defect.

## Principles applied

None cited. This was grading only, and no craft leaf was read this run.
