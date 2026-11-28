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
   lead, and the lead's to each member.** Without it the digest validator refuses the readers'
   did-nothing returns (`harness-distill`, #1855).
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
   flags stale ones. **The member is the sole judge** (`harness-distill` step 2); its rejection is
   never re-litigated.
3. **Who applies the ops: each member applies its own, through `expertise_apply`** — reviewers
   included; the host binds persona and destination, so nobody applies another's judgment.
   Members return the applied ops (each with `persona`, no `state`) plus the tool's receipt.
   **The lead reads each member's receipt and the actual resulting file**, applies its own
   lessons the same way, consolidates the active ops exactly as applied, and returns PASS when
   no real refusal remains. **You confirm and never apply** a member's or lead's ops; your own
   log you distill into your own file the same way. A refusal returns through the lead to the
   **original member**, who re-judges and re-applies with `supersedes` (`harness-distill`), never
   to the lead or you.
   **Before merge, in the still-live worktree:** fetch and rebase onto current `main`; run
   `expertise-merge.py replay --root <wt> --feature <id> --base <main sha>`; run
   `check-expertise`; once every distill run is closed, commit and push the reconstructed
   Expertise files and `feature.json`, which carries the distill runs' committed ledger
   (`git add -A -- .harness` stages only those, because the working files are ignored). The
   original and replacement receipts, the distill runs' directories and the observation logs
   are local working files, never staged and never force-added (DEC-260). Only after that push
   does Main run `merge-gate.py merge-distill --root <wt> --feature <id> --pr <n>`: it replays
   the worktree's local receipts and refuses any uncommitted `.harness` change, `feature.json`
   included, so no merge call may precede the commit. It re-checks replay
   under the owner lock and merges; it never re-judges or applies a lesson. If the rebase stops
   on Expertise conflicts, keep the receipts, rebuild only the conflicted Expertise files from
   current main by replay, stage and continue — **never** take ours/theirs. Ordinary
   non-Expertise conflicts stay the operator's.
   When no member applied an op, so the branch changes no Expertise file, `merge-distill`
   refuses it as not a distill candidate: commit `feature.json`, merge that pull request through
   the ordinary route, then run `feature-worktree.py clean --repo <repo> --id <FEAT> --yes`,
   which accepts the landed `done` station.
   `feature-worktree.py remove` refuses while working files remain, which keeps the worktree
   alive for distill or for `gh-sync.py skip-distill` when the distill is declined.
4. **Observation logs are local working files** — read here and never injected; nothing archives
   them. Each digest counts
   accepted entries by source; a skim count stuck at ~0 across features gets the skim cut.
5. **After it merges,** `merge-gate.py merge-distill` deletes the feature's `notes/`, `runs/`,
   `observations/` and the project notes its `feature.json` `project_notes` lists, and prints
   them; exit 4 means merged but cleanup failed — run
   `feature-worktree.py clean --repo <repo> --id <FEAT> --yes`. Never delete them before the
   merge, because replay reads the receipts.
