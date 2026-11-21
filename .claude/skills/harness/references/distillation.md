# Feature-close distillation — runs at MERGE, not at close-out (DEC-145)

Read this only when your dispatch names mission **distill**. You do not reach it on your own: it
runs once the feature's pull request has MERGED, triggered by the main session in the same act as
`gh-sync.py ship`. Before the merge nothing is settled enough to distill, and a feature that never
merges should teach the org nothing.

Mid-run, nobody writes Expertise; `expertise_update: []` is the normal DIGEST. This is the
feature-close write seam; `harness-curate` also authorizes out-of-band distillation (DEC-145).

1. **Dispatch each lead that ran the feature, once, in the feature worktree:** "distill — **read
   `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-distill/SKILL.md` first and tell each
   member to read it too**, read your members' logs under `<FEAT>/observations/`, skim the run
   digests for lessons nobody logged, have each member distill what passes the six-spawns test
   into its own Expertise file under `<HARNESS_FEATURE_TREE_ROOT>` with `expertise_apply`,
   report per-section counts before and after." **The read is mandatory:** the skill carries
   the ops format and refusal meanings; the tool's `check-expertise` catches format violations.
   **Put `HARNESS-MISSION: distill` on its own line in every distill dispatch — yours to the
   lead, and the lead's to each member.** The host forwards it to the digest validator (the
   road `HARNESS-REVIEW-PIN` takes, #1677), which then pins the readers' gate fields to their
   did-nothing spelling — qa `suite: n/a` / `matrix_ok: n/a`, code-reviewer `code_grade: n_a` /
   `reviewed: none` — instead of demanding a suite nobody ran or a diff nobody reviewed
   (#1855). Without the line, qa's honest return is refused and the code-reviewer cannot bind.
   **Register each lead's run as `distill-<squad>`** (`feature-record.py run-start --id
   distill-validator`, `distill-product`, `distill-eng`): that id is how the digest validator and
   the dispatch guard know the run is a distill, so applied ops on any other run id are refused.
   **Every distill dispatch, lead and member alike, also carries `HARNESS-FEATURE-TREE-ROOT`**
   naming the feature worktree; a child of a distill run without it is refused before it starts.
   **Product and validator go one after the other, never together** (#2033): both put a
   `harness-pm` to work (product's pm, validator's `goalcheck`), and `harness-pm` is single-flight
   per feature, so the second spawn is refused and its lead returns BLOCKED. Dispatch the eng
   lead alongside either one; dispatch the second of product and validator once the first has
   returned.
2. **The skim is recall, not judgment** (DEC-145). The lead relays **at most 3 candidates per
   member** as sourced observations ("your t04 digest noted X"), never pre-written entries, and
   flags stale ones. **The member is the sole judge** — it accepts, or **rejects with a reason** in
   its digest; rejection is first-class and never re-litigated. A full section takes a candidate
   only by **displacing** a weaker entry; nothing weaker → it dies, which is healthy, not
   `expertise_full`.
3. **Who applies the ops: each member applies its own, through `expertise_apply`** — reviewers
   included; the host binds persona and destination, so nobody applies another's judgment.
   Members return the applied ops (each with `persona`, no `state`) plus the tool's receipt.
   **The lead reads each member's receipt and the actual resulting file**, applies its own
   lessons the same way, consolidates the active ops exactly as applied, and returns PASS when
   no real refusal remains. **You confirm and never apply** a member's or lead's ops; your own
   log you distill into your own file the same way. A refusal (same-entry conflict, cap)
   returns through the lead to the **original member**, who re-judges and re-applies with
   `supersedes`; an empty withdrawal is that member's judgment, never the lead's or yours.
   **Before merge, in the still-live worktree:** fetch and rebase onto current `main`; run
   `expertise-merge.py replay --root <wt> --feature <id> --base <main sha>`; run
   `check-expertise`; commit and push the reconstructed files with the original applied
   receipts and any authorized replacement receipts. Then Main runs
   `merge-gate.py merge-distill --root <wt> --feature <id> --pr <n>`, which re-checks replay
   under the owner lock and merges; it never re-judges or applies a lesson. If the rebase stops
   on Expertise conflicts, keep the receipts, rebuild only the conflicted Expertise files from
   current main by replay, stage and continue — **never** take ours/theirs. Ordinary
   non-Expertise conflicts stay the operator's.
4. **Observation logs stay under the feature dir** — archived, never injected. Each digest counts
   accepted entries by source; a skim count stuck at ~0 across features gets the skim cut.
