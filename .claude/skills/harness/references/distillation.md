# Feature-close distillation — runs at MERGE, not at close-out (DEC-145)

Read this only when your dispatch names mission **distill**. You do not reach it on your own: it
runs once the feature's pull request has MERGED, triggered by the main session in the same act as
`gh-sync.py ship`. Before the merge nothing is settled enough to distill, and a feature that never
merges should teach the org nothing.

Mid-run, nobody writes Expertise; `expertise_update: []` is the normal DIGEST. This is the only
place project Expertise changes.

1. **Dispatch each lead that ran the feature, once:** "distill — **read
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-distill/SKILL.md` first and tell each
   member to read it too**, read your members' logs under `<FEAT>/observations/`, skim the run
   digests for lessons nobody logged, have each member distill what passes the six-spawns test
   into its Expertise file, run `bin/check-expertise.sh <HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/`,
   report per-section counts before and after." **The read is mandatory:** writing from new
   entries alone wipes every earlier one (DEC-125), and `check-expertise.sh` catches format
   violations but never a wipe.
2. **The skim is recall, not judgment** (DEC-145). The lead relays **at most 3 candidates per
   member** as sourced observations ("your t04 digest noted X"), never pre-written entries, and
   flags stale ones. **The member is the sole judge** — it accepts, or **rejects with a reason** in
   its digest; rejection is first-class and never re-litigated. A full section takes a candidate
   only by **displacing** a weaker entry; nothing weaker → it dies, which is healthy, not
   `expertise_full`.
3. **Who applies the ops:** members holding `Write` apply their own; write-less reviewers return
   theirs to the lead and **you** apply them verbatim. Leads' logs and your own are yours to
   distill the way DEC-69 curates — recommend, the lead returns condense ops, you apply.
4. **Observation logs stay under the feature dir** — archived, never injected. Each digest counts
   accepted entries by source; a skim count stuck at ~0 across features gets the skim cut.
