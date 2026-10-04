# Receipt — harness-dev-ops distill — BUG-1016

BLUF: 2 craft entries added (Outcomes O-5, O-6); 1 candidate rejected. No diff reviewed, no suite run.

Sources: six simplify receipts in notes/ (self-derived).
File: /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-dev-ops.md (craft). Repository tier: no ops.
Counts before→after: Patterns 15→15, Gotchas 15→15, Outcomes 4→6, Open 0→0.

Ops (applied via expertise-merge.py ops, exit 0):
- add O-5 (Outcomes): paired pre/post hook cost bounds — post handler must state its own root source. Source: plan efficiency E-1.
- add O-6 (Outcomes): tables that look duplicate may answer different questions; merging can widen a gate. Source: build altitude candidate 1.

Rejected: tests-efficiency fresh-fixture note — one feature's fixture-specific fact, already covered in spirit by P-16/O-2.

Grants: harness-dev-ops holds upsert on .harness/expertise/harness-dev-ops.md and .harness/*/expertise/harness-dev-ops.md (team-config.yaml:229-230). harness-eng-lead holds upsert on .harness/expertise/harness-eng-lead.md (team-config.yaml:314); no eng-lead ops proposed here.

Final check: `python3 .agents/skills/harness/bin/check-expertise.py .harness/expertise/harness-dev-ops.md` → OK, exit 0.

```yaml
VERDICT: PASS
DIGEST:
  headline: Two craft Outcomes added, one candidate rejected; check-expertise OK
  change_type: config
  applied: [.harness/expertise/harness-dev-ops.md]
  suite: n/a
  task: none
  test_kinds_written: []
  open_questions: []
  files_touched: [.harness/expertise/harness-dev-ops.md]
  expertise_update: [add O-5 Outcomes, add O-6 Outcomes]
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/receipt-harness-dev-ops-distill-devops.md
```
