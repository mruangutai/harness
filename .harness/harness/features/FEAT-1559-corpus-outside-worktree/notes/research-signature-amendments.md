# Signature amendments — FEAT-1559

All nine requested items are applied. BRIEF and plan remain pending and unsigned; final plan check exits 0. No production tests were run. All plan writes used amend or set-panel; no approval block was touched and no APPROVAL-RESET receipt was emitted.

## Fields changed, by requested item

1. Content classes A/B/C: BRIEF SC-07, SC-08, SC-10 and Constraints; D-12.choice; T-01.intent, T-04.intent, T-05.intent and T-06.intent. Tests explicitly discriminate merge repro A, byte-identical B, real edit C, staged deletion C, and mixed A/B/C refusing without filesystem/index/config mutation. Hidden-feature unstaged deletion is deliberately A, not a provenance inference.
2. Recordless checkout identity: BRIEF SC-01, SC-07, SC-08 and Constraints; D-08.choice; T-01.intent, T-04.intent and T-05.intent. First-creation coverage explicitly requires feature-worktree.py create AND bare git worktree add before any record exists, all-segment id includes and later record creation. Ambiguity/underivable identity refusal remains; creator algorithms remain unchanged.
3. FEAT-57 prerequisite: BRIEF Constraints; D-07.choice/because; T-01.intent. Ruling 3 cites #1655 closed abandoned. Research draft summary, D-07 handling and former Q-01 section are superseded too. No replay receipt or T-19 serialization remains a BRIEF/plan prerequisite.
4. Skipped class-C recovery: T-05.intent operator guidance, T-06.intent migration record and BRIEF Constraints. Old layout remains; merging/rebasing post-1559 main can produce structural verify 3/4/7 and audit/gate refusal. Preserve work by commit/stash including untracked files, repair, verify, rerun refused gate/audit, and recheck after restoring work; never force/prune/erase changes.
5. Receipt endpoints: BRIEF SC-11 (and SC-06 clarification); T-01.intent, T-05.intent and T-06.intent. Resolve merge-base(review_sha, main) at receipt execution and record immutable pre_change_sha and main endpoint. 652e70d4 remains planning baseline only; carried D-13 is unchanged.
6. Live disposable pin: BRIEF SC-12 and T-05.intent use current owner HEAD resolved at collected-test execution and record owner/probe HEAD. Frozen review subjects remain one-time receipts, not collected probes. Carried D-16 is unchanged.
7. Mapping: research-FEAT-1559-corpus-outside-worktree-draft.md now explicitly maps N-01/03/06/07/08/09/10/11/12/13 to current task obligations, covering every N-NN in D-13/D-14/D-15 including references through historical receipt filenames. Historical wording is provenance, not a stale dispatch.
8. panel.findings[*].disposition via set-panel: PF-5e51b4e6 resolved by ruling 1; PF-9bbc626c addressed (full clone); PF-8040e714 applied (receipt demotion); PF-f28aa400 and PF-7621c35d closed, no change. IDs, summaries and severities were preserved.
9. Final check below: exit 0. Six tasks, sixteen decisions, fourteen SCs remain; execution routes, anchors and trace lists unchanged.

## Final check output — verbatim

```
OK T-01 7 anchor(s) resolved
OK T-02 8 anchor(s) resolved
OK T-03 14 anchor(s) resolved
OK T-04 5 anchor(s) resolved
OK T-05 9 anchor(s) resolved
OK T-06 2 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree/.harness/harness/features/FEAT-1559-corpus-outside-worktree/plan.yaml against /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1559-corpus-outside-worktree: 6 task(s), 45 anchor(s) resolved, 0 failure(s)
```

## Open questions and limitations

No ruling could not be propagated. The writer's automatic check-state diagnostics still report pending BRIEF, stale STATE.md T-19 and absent feature.json github.build_entry. STATE.md/feature.json were intentionally unchanged: this assignment targets BRIEF/plan, not runtime metadata. These diagnostics are not the final plan check and are not represented as product test evidence. All product SC outcomes remain unexecuted/not_met; this PASS is for plan amendment only. The parent owns any signature-tier reader pass and operator signature.
