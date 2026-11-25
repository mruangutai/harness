# FEAT-2537 distill — orchestrator (run distill-orchestrator) — PASS

**BLUF:** The orchestrator log's 4 bullets are judged. 2 were applied (1 craft replace, 1 repository add) and 2 were rejected as already held. No cap is exceeded. This run reviewed no diff, ran no suite and committed nothing; cycles used: 0.

## Judgement per bullet (`observations/harness-orchestrator.md`)

| # | Bullet | Outcome | Reason |
|---|---|---|---|
| 1 | Enumerate a deletion's contract by input shape, not the ticket's named instance | **Rejected, already held** | Craft P-04 (state the class by its invariant, with an exhaustive census) and P-06 (probe the input space) cover it. Patterns is full and the bullet is an application of P-04, not a sharper rule. |
| 2 | A single granted fix round must hit the ruling's literal wording | **Applied**: craft Gotchas G-06 replaced | New rule; craft G-16 checks a ruling's terminal condition, not the letter of the fix. It displaces G-06 (exclude the feature record from a clean-tree acceptance), which I judged weakest: it turns on one repository's record file and its failure is cheap and self-diagnosing. |
| 3 | Run state writers alone (`run-start` raced a commit) | **Rejected, already held** | Craft G-17 states exactly this. A slip in following a rule is not a new rule. |
| 4 | Commit the observations log before the PR merges | **Applied**: repository `harness` Gotchas G-17 added | Repo-specific: `post-merge-sweep.py` ships the feature and then removes its worktree (`_ship_allows_removal`, then `_remove_worktree`). Gotchas had a free slot. |

## Receipts

- Craft batch `3fa3da86…`: `REPLACED G-06`. Counts P15→15 G15→15 O10→10 Open4→4.
- Repository batch `7639f3f2…`: `ADDED G-17`. Counts P13→13 G14→15 O3→3 Open1→1.
- Receipt for both: `notes/expertise-receipt-4ec14a62b36e21f50917992c6895756502c8e590ddb1a9c6e1876eea976f6a6b.json`.

## Notes

- The repository tier's Gotchas section is now full (15/15); the next repository gotcha must displace one.
- The product and validator squads' files were not touched.
- Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2537 is shipped and its orchestrator distill is applied: one craft gotcha replaced (brief a single granted fix round to the ruling''s letter), one repository gotcha added (commit the observations log before merge), two bullets rejected as already held.'
  feature: FEAT-2537-registry-record-cleanup
  status: shipped
  runs:
  - id: distill-orchestrator
    squad: orchestrator
    verdict: PASS
  cycles_used: 0
  briefing: none
  judgement: none
  open_questions: []
  files_touched:
  - .harness/expertise/harness-orchestrator.md
  - .harness/harness/expertise/harness-orchestrator.md
  - .harness/harness/features/FEAT-2537-registry-record-cleanup/notes/expertise-receipt-4ec14a62b36e21f50917992c6895756502c8e590ddb1a9c6e1876eea976f6a6b.json
  expertise_update:
  - persona: harness-orchestrator
    op: replace
    target: G-06
    section: Gotchas
    entry: WHEN a ruling grants exactly one fix round DO quote its operative wording verbatim in the fix dispatch as the acceptance, and brief the letter rather than the intent — an intent-met fix that misses the letter fails re-validation, and the round it then needs was never granted.
    why: 'One granted round was spent on a fix that met the ruling''s intent but not its literal wording (a text-mode read where it said raw bytes), forcing a completion round and a full extra validate dispatch. Displaces G-06, the weakest Gotcha: it turns on one repository''s record file and its failure is cheap and self-diagnosing.'
  - persona: harness-orchestrator
    op: add
    target: G-17
    section: Gotchas
    entry: WHEN a feature's pull request is about to merge DO append and commit your observations log first — the post-merge sweep ships the feature and then removes its worktree, so a log left uncommitted there never reaches the merged branch and can vanish before distillation reads it.
    why: Repository tier. The orchestrator log was still uncommitted at merge and survived only because the sweep removes a worktree after the ship record lands. Turns on this repository's post-merge-sweep.py (ship, then feature-worktree remove); Gotchas had a free slot.
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2537-registry-record-cleanup/.harness/harness/features/FEAT-2537-registry-record-cleanup/runs/distill-orchestrator/digest.md
```
