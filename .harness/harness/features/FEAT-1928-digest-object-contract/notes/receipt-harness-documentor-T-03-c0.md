# FEAT-1928 T-03 documentor receipt

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: "DEC-236 is already allocated on a fetched ref, so the signed T-03 plan must be amended before documentation work can start."
  commit_sha: none
  head_observed: dbeb43c1517b4d9095b3c11efec96eae86d5dbf6
  verify_result: "PASS — `python3 tests/integration/test-gen-decisions-index.py && python3 .agents/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md` exited 0; all 12 named generator tests printed `ok`; the generated-index diff emitted zero bytes. This was the required pre-edit baseline; no owned docs were edited."
  docs_updated: []
  gaps:
    - "T-03 is unimplemented pending a signed plan amendment: .harness/harness/docs/DECISIONS.md, .harness/harness/docs/DECISIONS-INDEX.md, .harness/harness/docs/SPEC.md, .harness/harness/docs/BUILD.md, .harness/harness/docs/org.html, and .harness/README.md remain untouched."
    - "No T-03 commit exists because the task explicitly requires stopping rather than silently renumbering an allocated decision."
  stale_found:
    - ".harness/harness/features/FEAT-1928-digest-object-contract/plan.yaml — T-03 reserves DEC-236, but fetched branch feat/FEAT-1896-dashboard-from-prototype already allocated DEC-236."
  open_questions:
    - { id: Q1, question: "Which newly approved decision number should replace DEC-236 throughout T-03?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/notes/receipt-harness-documentor-T-03-c0.md
```

## Allocation evidence

- `git log --all --oneline -G'DEC-236' -- .harness/harness/docs/DECISIONS.md .harness/harness/docs/DECISIONS-INDEX.md` found commit `4b6ed10918349c9a1cee3ba7941c92087bf33441` (`DEC-236: grilling lifecycle front-matter is a registered decision; INV-50 cites it`).
- `git branch -a --contains 4b6ed109` identified fetched local branch `feat/FEAT-1896-dashboard-from-prototype`.
- That commit adds the live heading `DEC-236 — Every grilling note carries lifecycle front-matter, and INV-50 enforces it` and its generated index row.
- T-03 says: if DEC-236 is allocated, stop for a plan amendment rather than silently renumbering. No owned documentation or enforcement-layer file was changed.
