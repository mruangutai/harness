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

1. **Audit:** run both tiers — the repository tier carries its own 40-line budget and the checker
   applies it by path, so an audit that reads one tier reports clean over the other.

   ```
   <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/check-expertise.py <HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/
   for d in <HARNESS_CONTROL_PLANE_ROOT>/.harness/*/expertise/; do
     [ -d "$d" ] && <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/check-expertise.py "$d"
   done
   ```

   Files reported `OK` are done — do not touch them.
2. **Distill each failing file.** The contract lives in `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-distill/SKILL.md`
   — **read it first; it is NOT preloaded** (DEC-158). The entry shape, the sections, the caps, the
   ops schema and the read-modify-write rule are only in that file. Three rules are curation's own:
   - A file that is itself a SKILL.md, or a cut that would land in one, obeys the three-part
     rule for skill text (DEC-158, FEAT-60): *if a gate refuses on it, name the gate; if a
     decision holds it, point; if one seam needs it, reference it.* Never put the weight back.
   - Entries under invented section names are still real lessons — reclassify into the four
     canonical sections, don't discard. When a section overflows, keep the entries that pass
     the six-spawns test hardest: rules that fire on every dispatch beat rules for rare shapes.
   - Preserve entry IDs where the entry survives recognizably; renumber only on merge.
3. **Move, don't destroy:** anything distilled away that is still feature-specific context worth
   keeping goes to `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<FEAT>/observations/<agent>.md` if the feature dir exists;
   otherwise it is dropped — it already failed the durability test.
4. **Verify:** re-run the step-1 audit until every file passes. Report per-file entry and word
   counts before and after — counted, not estimated.
5. Distillation may be delegated (one agent per file) or done inline for small sets; the checker
   is the gate either way.

## What this skill never does

- Invent lessons not present in the source file.
- Touch the plan's decisions — `plan.yaml`'s `decisions:` list, or `PLAN.md ## Decisions` for a
  feature still on the pre-DEC-182 format. Decisions are approval-gated and are not Expertise.
- Edit rule skills or agent files — curation is data maintenance, not constitution changes.
