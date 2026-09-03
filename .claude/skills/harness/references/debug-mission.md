# Mission debug — investigate first, then it becomes a plan (DEC-139)

Read this when your dispatch names mission **debug**. Missions map and deepen were retired with the
codebase map tier; debug is the only mission outside the plan-to-ship loop that survives.

For *symptom known, cause unknown*. When the cause is already known there is nothing to
investigate — that is a plan mission with a `BUG-NN` id (the FEAT-02 pattern).

1. **Investigation segment** — dispatch eng-lead: one specialist, chosen by `consult-when`, in
   debug mode (`harness-systematic-debugging` governs it — NOT preloaded since DEC-158: the
   dispatch prompt must tell the specialist to Read
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-systematic-debugging/SKILL.md` first): **reproduce → localize → root-cause,
   with evidence — no fix.** The deliverable is a root-cause report in the flow's `notes/`
   (repro steps, the failing case, the causal chain with `file:line` anchors, and the fix surface
   it implies). Three failed reproduction/hypothesis cycles → `BLOCKED` up, per the skill — an
   uninvestigatable bug is a decision for the user, not a budget sink.
2. **The report seeds the plan** — pm drafts the mini-BRIEF/PLAN from it (`## Problem` = the
   diagnosis; SC-01 is always "the repro fails pre-fix and passes post", verify: automated;
   tasks are `change_type: bugfix`). Same signature, same gates, same mirror (`bug` label derives).
3. **Ship as normal.** Nothing about being a bug relaxes a gate — a second, lighter lane is how
   approval bypasses grow.

Ids: **`BUG-NN-<kebab-slug>`**, independent sequence from FEAT, same folder root and machinery.
