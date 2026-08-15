---
name: harness-curate
description: Out-of-band Expertise distillation — audit every .harness/expertise/ file against the format contract and distill violators into rule-form entries. Use when expertise files have bloated, when check-expertise.sh fails, or for a one-time retrofit of files written under the old mid-run rules.
---

# /harness-curate — distill Expertise out-of-band

The feature-close distillation step (the orchestrator playbook, DEC-145) is the normal path.
This skill is the manual escape hatch: run it from the main session when files have bloated
between features, after upgrading a project from the old mid-run-write rules, or when the user
asks for a cleanup.

## Procedure

1. **Audit:** run `.claude/skills/harness/bin/check-expertise.sh .harness/expertise/`. Files
   reported `OK` are done — do not touch them.
2. **Distill each failing file.** The contract lives in `.claude/skills/harness-distill/SKILL.md`
   — **read it first; it is NOT preloaded** (DEC-158). The summary below is a checklist, not the
   contract, and the ops schema and read-modify-write rule are only in that file. For each:
   - Every entry becomes **WHEN <situation> DO <action>**, ≤50 words, or a durable repo fact.
   - Strip feature/task/issue IDs (`FEAT-NN`, `T-NN`, `#NN`) and per-incident case histories —
     an entry citing multiple incidents keeps the rule and drops the cases.
   - Re-home entries into the four canonical sections (Patterns/Gotchas/Outcomes/Open); entries
     under invented section names are still real lessons — reclassify, don't discard.
   - Respect caps (15/15/10/5, 150 lines). When a section overflows, keep the entries that pass
     the six-spawns test hardest: rules that fire on every dispatch beat rules for rare shapes.
   - Preserve entry IDs where the entry survives recognizably; renumber only on merge.
3. **Move, don't destroy:** anything distilled away that is still feature-specific context worth
   keeping goes to `.harness/harness/features/<FEAT>/observations/<agent>.md` if the feature dir exists;
   otherwise it is dropped — it already failed the durability test.
4. **Verify:** re-run `check-expertise.sh` until every file passes. Report per-file entry and
   word counts before and after — counted, not estimated.
5. Distillation may be delegated (one agent per file) or done inline for small sets; the checker
   is the gate either way.

## What this skill never does

- Invent lessons not present in the source file.
- Touch the plan's decisions — `plan.yaml`'s `decisions:` list, or `PLAN.md ## Decisions` for a
  feature still on the pre-DEC-182 format. Decisions are approval-gated and are not Expertise.
- Edit rule skills or agent files — curation is data maintenance, not constitution changes.
