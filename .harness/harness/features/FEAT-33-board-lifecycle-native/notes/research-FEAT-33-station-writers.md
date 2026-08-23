# Research — FEAT-33 station writers and ticket titles — 2026-08-22

BLUF, and the headline is a blocker: **the operator's ruling that `Ready` means "the plan is
signed" everywhere collides with live code, not with documentation.** `factory_claim.py:302` polls
`Status:"Ready" is:open` as the factory's **claim queue**, and `factory_decompose.py:399,411` is what
puts every served-repo TASK card there. Repurposing `Ready` makes a signed-plan PARENT card a claim
candidate on board 2. The brief's current text (`BRIEF.md:171`) says board 2's `Ready` meaning is
documented in kaya-ai's `harness.json`; that is true and incomplete. **This needs the operator.**

## Measured, all at worktree HEAD `f5f5185`, board 3, 539 items

| Station | Items | Writer in the tree today |
|---|---|---|
| `Backlog` | 304 | `gh-sync.py open` create, plus GitHub's `Item added to project` |
| `Plan` | 2 | `board-station.py <n> Plan`, told to the session in prose at `commands/harness-plan.md:11` |
| `Ready` | **0** | **nothing on the harness lane.** On the factory lane: `factory_decompose.py:411` |
| `Building` | 5 | `gh-sync.py start-task`, told to the orchestrator in prose at `skills/harness/SKILL.md:191` |
| `Review` | **0** | `gh_board.derive_station` all-tasks-done, written only by `close-task` |
| `Done` | 228 | GitHub natively, from `Closes #N` at merge |

`Review` is reachable in principle — `close-task` on the FINAL task derives it — but has never
fired in 539 items, because the last `close-task` runs while later tasks are still `pending` and
nothing calls `gh-sync` again until ship. `Ready` has no harness-lane writer at all.

**Live drift right now, not historical:** FEAT-32's `feature.json` `status` reads `Review` while its
parent `#700` card reads `Building`; `T-13` and `T-17` are `pending` with cards at `Backlog`. The
per-task drift the operator measured has since repaired itself — all 15 `done` tasks now read `Done`,
because the merge's `Closes #N` closed the issues and GitHub's `Item closed` workflow moved them.
That is the point: **the only station that self-heals is the one GitHub writes.**

## The mechanism finding — `feature.json.status` already IS the station map

`check-state.sh:494` declares `STATUS_ORDER = ["Backlog","Plan","Ready","Building","Review","Done",
"Abandoned"]`, schema-required with a closed value set, and `gh-sync.py`'s `_record_status` already
writes it at ship (`Done`) and abandon (`Abandoned`). Those are DEC-192's six column names plus the
one with no column. So the event-driven map needs **no new vocabulary**: the station a parent card
should read is `feature.json.status` resolved through the board's declared `stations` map, and the
station writer is whatever records the status.

That makes the absence-catcher **free and offline** — comparing `feature.json.status` to a card
station needs the board read the audit already performs, and needs no new derivation.

## Why "caused, not remembered" has a hard ceiling here

Only two things in this system cause a write without an agent choosing to: **GitHub's own
workflows**, and **a Claude Code hook**. Hooks are the enforcement layer, which DEC-174 forbids this
feature from executing, and a board read inside `PostToolUse Write|Edit` would fire on every edit in
every session — measured cost of one board read on board 3 is **490–506 GraphQL points**
(`notes/grilling-graphql-cost-2026-08-10.md`, struck-and-restated entry). That is the waste the
operator already refused for `check-state.sh`, an order of magnitude worse.

So the achievable design, stated as a ceiling rather than sold as a solution: **fold each station
write into a command that is already mandatory at that moment**, so forgetting the station requires
forgetting the whole act, and make the residue detectable offline. `open` is mandatory after
signature (INV-26's mirror-never-ran clause makes its absence a red gate). Recording
`feature.json.status` is mandatory at every phase transition (`SKILL.md:343`). Those two are the
hooks that already exist without being hooks.

## The station-writer hole, re-derived

`skills/harness/SKILL.md:191` addresses `start-task` to the **orchestrator** only. DEC-174 forbids
the orchestrator `main-session-direct` tasks, and the only mention of `main-session-direct` in that
file is `:131`, about run counting. So a main-session-direct task has no instructed card-mover.
FEAT-32 has **9 of 17** tasks main-session-direct.

## Ticket titles — measured, and the cost warning does not apply

- **188** issues match `^T-\d+ ` on `mruangutai/harness` (640 issues, `--state all`). **All 188 carry
  a milestone naming their feature**, so the backfill needs no recovery and no guessing — the feature
  id is read off the milestone. **0** are already prefixed.
- 21 distinct milestones. Worst case combined length `FEAT-24-config-responsibility-split — T-NN — …`
  is **226** characters (`#654`). GitHub's title cap is commonly 256; I did **not** verify the cap.
- **Cost, measured by differencing `gh api rate_limit --jq .resources.graphql.used` at `f5f5185`:**
  `gh issue edit --title` = **2 points**. `gh issue list --state all --limit 1000 --json` over 640
  issues = **7 points**. Whole backfill = 7 + 188x2 = **383 points**, 7.7% of the 5000/hour budget.
  The ~102-point warning is about `gh project field-list`; **titles live on the issue, not the card,
  so no `gh project` call is needed at all.**
- Interruption: the rename is idempotent and self-resuming with no state file, because the title
  itself records whether it was done. One pass.
- Separator: `gh-sync.py:574` builds the parent as `f"{feat} — {phrase}"` with an em dash. `:592`
  uses the same em dash. So the prefix reuses it; nothing is invented.

## Open question for the operator

**Q1 (blocking): `Ready` is the factory's claim queue in code.** `factory_claim.py:302` searches
`Status:"Ready" is:open`; `factory_decompose.py:411` puts every served-repo task card there. Making
`Ready` mean "plan signed" either (a) feeds signed-plan parent issues into the claim queue, (b)
keeps a per-repo meaning, which is the thing the ruling exists to forbid, or (c) moves the claim
queue to a different station, which is new scope. The plan holds all three side by side and applies
none, mirroring how the DEC-186 question is held in `BRIEF.md`'s `## Constraints` blockquote.

**Note on a shifted anchor:** the DEC-186 blockquote was cited as `BRIEF.md:228-238` in the plan
digest, `STATE.md:23` and `notes/handoff-plan.md:7`. Adding this round's sections moved it to
`BRIEF.md:337-353`, content unchanged. Those three anchors are now stale and are not mine to edit —
the block is best cited by its heading, not by line.
