# QA distill — BUG-1016

**BLUF: no Expertise change.** All three skim recalls and three self-derived candidates were rejected as already covered. Zero ops applied. Neither file was touched, so I did not run check-expertise.py.

## Grant
`check-domain.py --resolve /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md` returned `harness-qa` when run with HARNESS_AGENT_TYPE=harness-qa. Write grant confirmed; unused.

## Sources read
review-harness-qa-c1.md, c2.md, c3.md. No QA observations log exists.

## Rejected (six-spawns test)
| Candidate | Source | Reason |
|---|---|---|
| One MV test killed both classifier mutants; quoted tilde/scheme path-field exclusions unexercised | skim 1 (c2) | Restates P-06: each triggering leg needs its own test case. Nothing sharper to add. |
| Pinned 124/0 vs supplemental 44-file run at later HEAD | skim 2 (c3) | Covered by G-15: use a detached checkout at the exact review SHA, because later-HEAD state changes the evidence. Labelling a supplemental run is ordinary receipt hygiene. |
| Keep new tests, revert to old adapter, expect 123/1, then restore to 124/0 | skim 3 (c3) | Covered by O-03 (evidence tier) and the DEC-153 worktree protocol in verification-rules. The restore check is already in the skill. |
| SC whose named cases are pre-change-passing controls has no dedicated red-first | self (c1 F1) | Covered by O-03 and O-04. It is a feature-specific ruling, and c2 dismissed it. |
| Receipt shows red counts and names but not the command/exit line | self (c1 F2) | Covered by O-03, which requires a retained command and outcome. |
| Verify `git diff pin..HEAD` over tested paths is empty before treating a later HEAD as the pin | self (c1-c3) | Covered by G-15. |

## Counts
Per-section entry counts are unchanged because no ops were applied.
- Craft: Patterns 15, Gotchas 15, Outcomes 10, Open 1.
- Repository: Gotchas 11, other sections 0.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Distill: no new durable QA rule; all candidates already covered by P-06, G-15, O-03, O-04"
  suite: n/a
  failures: 0
  matrix_ok: n/a
  kinds: []
  coverage_gaps: []
  sc_evidence: []
  fail_first: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/qa-distill-validator.md
```
