# Stated intent — BUG-276

Transcribed by harness-orchestrator from the dispatch that opened this flow. There was no
grilling or wayfinding session: the intake is GitHub issue #276 plus the operator's narrowing,
both reproduced verbatim below. This file is the intent of record for the plan panel.

## GitHub issue #276, verbatim

> A distillation merging Expertise by ID drops entries, and nothing detects it. FEAT-13's
> distillation merged Expertise entries by their P-NN/G-NN identifier. Identifiers are per-file
> sequences that every distillation reassigns, so an incoming entry whose number is already taken
> is displaced rather than added. Measured 2026-08-12: harness-backend-dev.md lost P-09,
> harness-pm.md lost P-06/P-10/G-06 (two false positives noted separately). There is no check that
> an Expertise file's entry count never decreases across a distillation, and no check that every
> incoming entry is present by CONTENT afterwards. The merge is ID-keyed, so a collision is
> indistinguishable from an update. What would close this: a check that a distillation cannot
> silently reduce what a file records -- entry count monotonic, and every input entry present by
> CONTENT in the output.

## The operator's narrowing, verbatim from the dispatch

The operator commissioned a read-only investigation at HEAD before this flow opened, and narrowed
the ticket on its result:

> compute_union should detect a duplicate id within the incoming proposal itself and refuse
> (matching the ops path's existing exit-11 CONFLICT convention) rather than silently keeping only
> the last-seen one.

Bounds the operator set explicitly:

- Issue #381 (cross-time id reuse, tombstones) was resolved separately via BUG-1308/DEC-219 and
  must NOT be re-litigated.
- The base-versus-proposal id collision is ALREADY fixed (exit 7 CONFLICT) and is not in scope.
- The scope is the WITHIN-ONE-PROPOSAL duplicate-id silent drop on the `apply --entries` path.
- "This is a bug flow (BUG-NN), not a full feature — keep BRIEF/plan proportionate to the fix's
  actual size."

## Two corrections the panel should know are already established

1. The issue and the narrowing both describe the surviving entry as the later one ("displaced",
   "keeping only the last-seen one"). Measured at 6d969ed3: it is FIRST-wins — the later entry
   never arrives. BRIEF and plan follow the measurement.
2. The issue's field evidence (harness-backend-dev.md P-09; harness-pm.md P-06/P-10/G-06, dated
   2026-08-12) predates `expertise-merge.py`, which was first added 2026-08-21 in 47a9935a. Those
   losses came from the whole-file-rewrite distillation this tool ended, so the planned guard would
   not have prevented them. The defect is independently measured at 6d969ed3.
