---
name: harness-curate
description: Out-of-band Expertise distillation — audit every .harness/expertise/ and .harness/*/expertise/ file against the format contract and distill violators into rule-form entries. Use when expertise files have bloated, when check-expertise.py fails, or for a one-time retrofit of files written under the old mid-run rules.
---

# harness-curate — distill Expertise out-of-band

The feature-close distillation step (the orchestrator playbook, DEC-145) is the normal path.
This skill is the manual escape hatch: run it from the main session when files have bloated
between features, after upgrading a project from the old mid-run-write rules, or when the user
asks for a cleanup.

## Procedure

1. **Audit:** one call names both tiers; the checker applies each tier's own line budget by path,
   and an empty tier directory adds nothing.

   ```
   <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/check-expertise.py <HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/ <HARNESS_CONTROL_PLANE_ROOT>/.harness/*/expertise/
   ```

   Files reported `OK` are done — do not touch them.
2. **Distill each failing file — by its own persona, never inline.** Create a feature worktree
   and dispatch each failing file's original persona with `HARNESS-MISSION: distill`; it reads
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-distill/SKILL.md` (NOT preloaded, DEC-158)
   and applies its own ops with `expertise_apply`. You recommend; you never rewrite another
   persona's judgment. Landing follows the same receipt check, replay and `merge-distill` gate
   as feature-close distillation (`harness/references/distillation.md` step 3). Two rules are
   curation's own, passed to each persona as recommendations:
   - Entries under invented section names are still real lessons — reclassify into the four
     canonical sections, don't discard. When a section overflows, keep the entries that pass
     the six-spawns test hardest: rules that fire on every dispatch beat rules for rare shapes.
   - Preserve entry IDs where the entry survives recognizably; renumber only on merge.
3. **Move, don't destroy:** anything distilled away that is still feature-specific context worth
   keeping goes to `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/observations/<agent>.md` if the feature dir exists;
   otherwise it is dropped — it already failed the durability test.
4. **Verify:** re-run the step-1 audit (a read) until every file passes, and check each persona's
   receipt against its resulting file. Report per-file entry and word counts before and after —
   counted, not estimated.

## What this skill never does

- Invent lessons not present in the source file.
- Touch the plan's decisions — `plan.yaml`'s `decisions:` list, or `PLAN.md ## Decisions` for a
  feature still on the pre-DEC-182 format. Decisions are approval-gated and are not Expertise.
- Edit rule skills or agent files — curation is data maintenance, not constitution changes.
