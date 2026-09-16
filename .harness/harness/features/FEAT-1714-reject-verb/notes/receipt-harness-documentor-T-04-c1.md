# Receipt — harness-documentor — T-04 c1

## Result

DEC-230 now records `reject` as the sixth exhaustive judgement kind and states the landed reject return, intake, lifecycle, operator-overrule, and INV-44 contracts. Its existing Over/Because/Tradeoff rationale remains intact. The generated index coordinates and tags were refreshed while the hand-written DEC-230 ruling suffix was preserved verbatim.

## Source evidence inspected

- `.harness/harness/features/FEAT-1714-reject-verb/BRIEF.md`: perspectives, SC-01 through SC-05, constraints, and out-of-scope boundary.
- `.harness/harness/features/FEAT-1714-reject-verb/plan.yaml`: D-01, D-02, T-04 intent, and the exact verify command.
- Landed commits `8a83624b`, `4656654a`, and `31743180`: reject digest/ledger contract, GitHub lifecycle, terminal vocabulary, and rejected-record invariant.
- `.claude/skills/harness/bin/feature-record.py`: final six-member `JUDGEMENT_KINDS`.
- `.claude/skills/harness/bin/validate-digest.py`: closed inline reject judgement, `status: rejected`, positive successor-or-`none`, one-line reason, and zero-cycle validation.
- `.claude/skills/harness/bin/check-state.py`: INV-44's six rejected-record dimensions.
- `.claude/skills/harness/bin/gh-sync.py`: report-and-confirm parent-only reject path, conditional `superseded` label/station write, backlog reseat, milestone close, and final numeric-path station write.
- `.claude/skills/harness/bin/factory_config.py`: `rejected` as a non-board terminal station.

## Files changed

- `.harness/harness/docs/DECISIONS.md` — amended DEC-230 only.
- `.harness/harness/docs/DECISIONS-INDEX.md` — regenerated generated fields; hand-written annotation suffix retained.
- `.harness/harness/features/FEAT-1714-reject-verb/notes/receipt-harness-documentor-T-04-c1.md` — this receipt.

The pre-existing working-tree modification to `.harness/harness/features/FEAT-1714-reject-verb/feature.json` was not touched.

## Generator and verification boundary

Ran `python3 .claude/skills/harness/bin/gen-decisions-index.py` from the assigned worktree; it exited 0 and emitted no output, as expected for the in-place write action. The regenerated DEC-230 row is `@7414` with `[plan,cost,orchestrator,brief]`; downstream DEC-231 and DEC-232 coordinates moved to `@7465` and `@7500`.

The T-04 verify command in the dispatch exactly matches `plan.yaml`:

```text
python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
```

Per dispatch, I did not run that mechanical gate; the orchestrator owns it. I also ran no formatter, linter, test, project-wide build, or project-wide suite.
