# Documentor receipt — BUG-1699-lifecycle-cards T-05

T-05 passes: lifecycle decision authority and its generated index now match the executable T-01 through T-04 behavior.

## Authority refreshed

- `.harness/harness/docs/DECISIONS.md` now states the complete-card active projection and its explicit best-effort phase callers in DEC-138.
- DEC-203 now carries every recorded source, parent, and non-abandoned task card through Plan, Ready, Building, Review, and ship-owned Done, and records complete-card reconciliation against one bounded snapshot. Its exact six-station vocabulary, no-alias rule, bounded readbacks, workflow-owned closure, open-child ship guard, and abandonment behavior remain in force.
- DEC-220 now places idempotent mirror opening and the existing `github.build_entry` receipt immediately after signature; ordinary Build requires the receipt and sends Building, while recovery remains explicit and idempotent.
- DEC-224 now assigns Building before a must-fix run and Review at the next validation boundary after return to the orchestrator without changing the fix-team DAG or parallel reader wave.
- DEC-229 now records the atomic Plan reset, transient resume metadata, and the signature's `RESUME:` receipt while retaining `sign-approval` as the only approval writer.
- DEC-146's uncapped issue-to-`projectItems` lookup and best-effort station-write contract are substantively unchanged.
- `.harness/harness/docs/DECISIONS-INDEX.md` was regenerated with updated anchors, reference graphs, tags, and current ruling summaries.

## Verification

Ran the signed command unchanged from the worktree root:

```text
python3 .claude/skills/harness/bin/check-decision-anchors.py && python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md
```

Result: exit 0. Anchor checker reported `examined 40 anchor(s), 0 failed`; the generator diff emitted zero bytes, which is the pass condition.
