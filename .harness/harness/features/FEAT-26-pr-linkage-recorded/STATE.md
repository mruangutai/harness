# STATE

## Current

- feature: FEAT-26-pr-linkage-recorded
- squad: product
- status: in-flight
- phase: plan — **the #673 accepted-cost entry has LANDED and the BRIEF is signable and UNSIGNED.**
  `BRIEF.md` is 166 lines; the diff against HEAD is **15 insertions and 0 DELETIONS**, and an
  insertion-only diff structurally cannot have altered SC-01..SC-11, `## Requirements`,
  `## Constraints`, `## Verification gaps` or `## Approval`. Both guarded md5s confirm it
  independently (`## Requirements`..`## Verification gaps` = `4a76e0b616b0ed0f3a69cec66c1fa789`,
  `## Approval`..EOF = `c380e46b2c62bd5dede69a2c96810c44`). `## Approval` reads `status: pending`.
  Only the main session signs.
- It took THREE product runs, and the reason is worth recording: **issue #673 — handed to me as
  carrying "the full measurement" — contains four falsified claims, and I relayed all four into my
  dispatches before measuring any of them.** Every number in the landed entry is now one I took
  myself in this worktree.
  - **31 -> 32 `ProjectV2` mutations.** #673's prose says 31 while its own code block lists 32. I
    diffed my introspected set against that block: the sets are IDENTICAL, so the list is right and
    the prose miscounts. Robust under two independent denominators — by mutation name, and by
    mutations whose input type mentions `ProjectV2`, both 32.
  - **"509 items, 222 of 222" -> the invariant, dated.** I measured 510, then 512 items within one
    session, with 226 of 226 closed issues at `Done` both times. A pinned total is false within
    hours; the entry now states "no closed item sits off `Done`, 226 of 226 on 2026-08-22".
  - **"the three workflows on this repository's board" -> the board carries EIGHT.** Seven enabled
    (`Auto-add sub-issues to project`, `Auto-add to project`, `Auto-archive items`,
    `Auto-close issue`, `Item added to project`, `Item closed`, `Pull request merged`) and one OFF
    (`Pull request linked to issue`, workflow 11). The three #673 names are the ones bearing on
    closing behaviour — a different claim from the board carrying three.
  - **"#673 is a sub-issue of #492" -> its parent is #675** ("The board's whole lifecycle,
    native-first"). #492 has ZERO sub-issues. I removed the false clause from the entry.
- Also measured, and it strengthens the entry rather than undercutting it: **the board holds 512
  items and NOT ONE is a pull request**, so `Pull request merged` cannot be a producer of the
  closed-at-`Done` figure at all; only `Item closed` and `Auto-close issue` can. pm independently
  reached the weaker, correct claim before I got there. And of four merged PRs sampled, only #491
  carried a closing keyword — #452, #451 and #415 all return an empty `closingIssuesReferences`,
  which is precisely the forgetting REQ-03 exists to end.
- What I verified and found SOUND, unchanged: the only workflow mutation is
  `deleteProjectV2Workflow` and nothing creates, enables or updates one; `CopyProjectV2Input` has no
  workflow argument; `ProjectV2Workflow` exposes 8 fields, neither trigger nor action;
  `grep -rn 'projectV2Workflow'` across `bin/` returns 0; `harness-init/SKILL.md` step 1 is headed
  "Install the eight prerequisites — HARD GATE" with no board workflow among them; and PR #491
  merged at `2026-08-18T12:54:54Z` with `closingIssuesReferences` returning exactly `[417, 430, 453]`,
  closed at `:55Z`, `:55Z`, `:56Z`.
- **Two edits in that entry are MINE, not pm's, and are disclosed rather than absorbed:** I added the
  PR #491 measurement, which my own re-dispatch commissioned but the run's rubric (AC-9..AC-15) did
  not require, so pm dropped it to fit a line ceiling; and I removed the false #492 parentage clause,
  which that same rubric positively REQUIRED. Both are measurements I took, in a file that resolves
  to `harness-orchestrator` as well as `harness-pm`. Neither touches a requirement, an SC, a decision
  or scope.
- Run history: `2026-08-22-2-product` recorded BLOCKED — its host's context closed before pm
  returned, and it reported zero bytes written. **That report was true when written and false
  twenty minutes later**: its pm's write landed after the host had died, carrying all four bad
  numbers. `2026-08-22-3-product` then REPLACED that entry rather than duplicating it, with the
  mutation count and board-count discipline corrected. One cycle spent on the re-dispatch.
- `SendMessage` is disabled in this session, so there was no way to retract a bad number mid-run.
  That is why all four reached a member's rubric instead of being stopped at source.
- **Q1 IS CLOSED and T-06 is unblocked.** The previous round's claim that
  `notes/answers-Q1-pr-attribution.md` was fabricated consent was FALSE. The operator was asked
  through the operator-facing question tool and chose "Confirm the mapping as pm proposed"; the
  SC-08 narrowing that round believed invented was genuinely offered and genuinely declined. The
  file is restored and `notes/q1-pr-attribution-evidence.md` is corrected in place. The provenance
  gap is filed as **#671**.
- Two dispatch hazards remain FALSE here, re-verified at `e56ee60`: `run-unit-tests.sh` has no
  `--check-kinds` mode, and `feature-schema.json` closes `runs[]` at exactly `id`/`squad`/`verdict`.
- run dirs under `runs/**` are gitignored (`.gitignore:7`) and never enter a commit.
- source ticket: #492.

## Open Questions

- Q13 (non-blocking, operator — NEW and it outlives this feature): **issue #673 still carries all
  four falsified claims** (31 mutations, 509 items / 222 of 222, "the three workflows on this
  board", and a #492 parentage its own graph contradicts). #673 is the ticket that will implement
  the detection work, so whoever picks it up inherits them. It needs correcting at source; nothing
  in this feature's scope does that.
- Q1 CLOSED. Genuine operator consent on the four PR numbers — FEAT-01 -> 4, FEAT-02 -> 4,
  FEAT-03-subissue-mirror -> 15, FEAT-04-decisions-index -> 15, attributed by PR title, not branch.
- Q2 (non-blocking, operator): should the harness open its own PRs? Contradicts DEC-153, so it is
  not the plan's to choose. The plan is correct under either answer.
- Q3 (non-blocking, operator) — **the render-only branch is now EVIDENCED, not merely chosen.** The
  question was whether `ship` should close the source issues directly instead of rendering `Closes`
  lines; D-04 takes render-only and crosses DEC-196. GitHub already performs the close correctly and
  unaided in about one second — #491's three issues closed within two seconds of merge from the
  keyword alone — so closing directly would replace a working platform mechanism with harness code
  that posts to GitHub, and the Goal's own sentence says nothing in this feature ever posts, edits or
  closes. The operator may still choose otherwise; what changed is that render-only is no longer a
  bare preference.
- Q4 (non-blocking, harness defect): FILED AS #670. Feature-id coinage collided twice and nothing
  detected it. The surviving pair is `FEAT-25-claim-feature-root` and
  `FEAT-27-expertise-repository-tier`.
- Q5 (non-blocking, correction): "check-state.sh carries 19 invariants" is FALSE — INV-1..INV-27 run,
  INV-20 is taken, INV-10 is retired. pm used INV-28 correctly. Sibling orchestrators may carry the
  same false premise.
- Q7 (non-blocking, operator): REQ-05 and SC-08 keep pre-amend counts ("eleven ... eleven",
  "twenty-three features this plan enumerates") while `## Problem` says twelve of twenty-seven.
  Left untouched deliberately — they describe the plan's enumerated scope, and the plan already
  carves out later features. Consequence before signing: after FEAT-26 ships, FEAT-24 still carries
  `pr: null` and the new invariant names it — REQ-04 working, not a defect — and each feature shipped
  between signature and delivery adds another.
- Q8 (non-blocking, operator): the DEC-153 constraint bullet carries its own provenance (naming the
  defunct `DECISIONS.md:3660-3662` anchor). It stops someone re-pinning a line range later, but a
  signed brief now carries a paragraph about a dead anchor. Keep, or trim to id-only.
- Q11 (non-blocking, operator): the first accepted-cost entry names that *edits* and *closes* are
  unasserted even for the renderer — wider than the fix commissioned in that round. Accept, or narrow.
