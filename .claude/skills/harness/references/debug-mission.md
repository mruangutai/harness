# Mission debug — investigate first, then it becomes a mission judgement (DEC-139)

Read this when your dispatch names mission **debug**. Missions map and deepen were retired with the
codebase map tier; debug is the only mission outside the plan-to-ship loop that survives.

For *symptom known, cause unknown*. When the cause is already known there is nothing to
investigate — the change goes through the grilling's mission judgement like any other, and a known
cause with a bounded diff and no new surface is the `patch` case (`/harness-patch`, SC-01/SC-02);
a wider fix is `plan`. Neither is debug.

1. **Investigation segment** — dispatch eng-lead: one specialist, chosen by `consult-when`, in
   debug mode (`harness-systematic-debugging` governs it — NOT preloaded since DEC-158: the
   dispatch prompt must tell the specialist to Read
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-systematic-debugging/SKILL.md` first): **reproduce → localize → root-cause,
   with evidence — no fix.** The deliverable is a root-cause report in the flow's `notes/`
   (repro steps, the failing case, the causal chain with `file:line` anchors, and the fix surface
   it implies). Three failed reproduction/hypothesis cycles → `BLOCKED` up, per the skill — an
   uninvestigatable bug is a decision for the user, not a budget sink.
2. **The report seeds the grilling, and the grilling judges the mission** — the root-cause report
   is what makes the cause known, so the harness can now say `patch` or `plan` with a reason in the
   artifact's `## Mission` block; the operator confirms or overrides in the same dialog. pm then
   drafts from it (`## Problem` = the diagnosis; SC-01 is always "the repro fails pre-fix and
   passes post", verify: automated; tasks are `change_type: bugfix`) — under `patch`, one product
   run, one task, no panel; under `plan`, the one `plan` run. Same signature with its rework
   ruling, same mirror (`bug` label derives).
3. **Ship as normal.** Being a bug relaxes no gate on the diff: qa with fail-first evidence and
   review over one pinned `review_sha` are where a patch is gated (DEC-139 as amended by FEAT-59)
   — what it skips is the panel over a document, never the readers over code.

Ids: **`BUG-NN-<kebab-slug>`**, independent sequence from FEAT, same folder root and machinery.
