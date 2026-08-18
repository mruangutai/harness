# Segment 02 — the T-02 cutover cannot be crossed as planned. Your ruling, then two hand edits.

## Outcome

If we proceed as the approved plan orders it, the first agent to land T-02's `factory_config.py`
edit locks every `harness-*` agent out of every write in the repository — whatever the target path —
until a human edits `.harness/factory/fleet.yaml`. The build would stop with a half-finished T-02 in
an uncommitted tree. Nothing has been damaged: the eng lead measured the trap and refused to enter
it rather than discovering it halfway through.

**T-01 and T-08 are done, verified and committed.** T-09 is still open — kaya's `master` still
carries all four pre-FEAT-18 pinned ids, so its pull request has not merged.

## Why — the chain, each link read at `ada8e99`

1. `check-domain.sh:485` calls `harness_boundary.classify()` for every governed write.
2. `harness_boundary.py:263` — `resolve_fleet(...)` is the **first statement** of `classify()`,
   ahead of anything that asks where the target lives. Its own comment says so: *"Resolution runs
   for EVERY governed write, whatever the target looks like."*
3. `harness_boundary.py:157-169` — it calls `factory_config.load_fleet()` on the live `fleet.yaml`
   and `sys.exit(2)` on any exception.
4. `factory_config.py:151-156` — the **current** loader *requires* `board` in every repos entry.
   T-02 item 3 makes the **new** loader *reject* that same key. `fleet.yaml:26` carries one.

**No state of `fleet.yaml` satisfies both loaders.** Remove the board before T-02 and the old loader
raises; leave it and the new one raises. Either way the hook exits 2 and no governed agent can write
— including the agent that would fix it.

The plan's premise was `plan.yaml:667`, that the guard "reads `name` and `workspace_root` only".
That is true of the keys the guard **consumes** and false of what `load_fleet` **validates** on the
way to handing them back. T-07's own intent states the consequence but scopes it to writes *outside*
the harness root; `harness_boundary.py:263` contradicts that scoping.

Confirmed separately: the main session is **not** governed — `check-domain.sh:271`,
`_governed = bool(agent) and agent.startswith("harness-")`, and the whole domain phase is gated on
it. Your hands still work while every agent's are tied. That is what makes every option possible.

**And I am inside the blast radius too.** `harness-orchestrator` is a governed agent, so during the
window I cannot write `STATE.md`, `feature.json` or a handoff note either. I measured what survives:
`bash-write-guard.sh:375` records that `git` produces no write findings, and `classify` is only
reached per finding (`:551`, after `if not findings: sys.exit(0)` at `:475`) — so **`git add` and
`git commit` still work while `Write` and `Edit` do not.** That is what makes option A survivable
rather than a trap for me as well, and it is why A's procedure below front-loads my state writes.

## Your options

**A — agent lands the code, you delete seven lines. My recommendation.**
Merge T-09 first. Then, in order:
1. I write `STATE.md`, `feature.json` and the handoff **ahead of the dispatch**, describing the
   post-T-02 state and naming your `fleet.yaml` edit as the next action — because I cannot write
   them once the window opens.
2. I dispatch T-02 with a hard constraint: the member writes its tests and its receipt *first*, its
   **final** write is `factory_config.py`, then it runs the verify (read-only, still permitted) and
   returns.
3. On its return I commit (commits survive) and return to you immediately, recording nothing else.
4. You delete the `board:` block from `fleet.yaml`'s kaya entry — **T-07 Part A item 1 only**, the
   seven lines from `board:` to the last station. Items 4 and 5 of Part A rewrite the header
   paragraph and add a pointer line; they are not needed to unblock the loader and stay with T-07
   proper. Keep `name` and `default_branch`.
5. Writes reopen. A continuation run finishes T-02's post-migration mutation proofs and carries on
   into T-03, T-06, T-04.

*Costs:* a window in which no agent — me included — can Write, lasting from the T-02 member's final
write to your deletion. One extra run for T-02's mutation proofs, which cannot happen before that
deletion. T-07's Part A item 1 is pulled forward, splitting the task.
*One inference, flagged:* that the write landing the new loader is itself permitted, because
PreToolUse runs before the write and therefore imports the pre-edit module. I did not measure it —
probing it would have locked me out mid-session. If it is wrong, the write is refused and nothing is
half-done, so the downside is bounded.

**B — re-lane T-02 as a second carve-out.** You hand-write the `factory_config.py` migration and the
`fleet.yaml` deletion back to back. No window at all, no split run.
*Cost:* you hand-write this feature's largest change — nine specified items plus twenty-six named
test cases — and the feature's core code leaves the lane that tests it.

**C — make the transition crossable instead of atomic.** T-02 lands with `load_fleet` **ignoring** a
board key in a repos entry rather than rejecting it; you then remove the board from `fleet.yaml`
normally; a later task in this same feature adds the rejection. `fleet.yaml` loads at every instant,
so no window ever exists and nothing has to be hand-edited inside one.
*Cost, stated accurately:* it changes T-02 item 3, so it is a plan amendment and needs pm. What it
does **not** cost is D-01's silent-failure concern: the failure mode D-01 targets is `load_board`
returning `None`, which T-04 still removes, and after T-02 nothing reads `repos[].board` at all — so
a temporarily tolerated key is inert rather than silently wrong, and the rejection lands before this
feature ships.

## The window D-10 describes, and how to make it zero

Once `fleet.yaml` loses the board and the new loader is live, `board_for(kaya)` reads kaya's own
config from `master`. Today that config has no board, so it would raise until T-09 merges — the
window D-10 accepts. **Merge T-09 before the cutover and that window is zero.** T-09 is already out
to you as segment 01 and depends on nothing; it is now on the critical path for a second reason.

## What I need back

1. Your ruling: A, B or C.
2. T-09 executed and merged (segment 01, `notes/segment-01-main-session.md` — unchanged and still
   accurate).
3. Under A: your `fleet.yaml` deletion the moment I tell you the T-02 run has returned.

## State right now

- Committed on `feat/FEAT-24-config-responsibility-split`: `000934b` `[harness:t-01]`,
  `22814c7` `[harness:t-08]`, plus the state commits. Full unit suite green, zero FAIL lines.
- `plan.yaml`: T-01 and T-08 `done`; T-02, T-03, T-04, T-06 put **back to `pending`** — they were
  marked `building` at dispatch and never ran, and a status the receipts do not support is a lie to
  my successor. Their board cards were returned to `Backlog` with `board-station.py` — INV-26 caught
  the drift as four real violations before I did, which is the check earning its place.
- `check-state.sh`: FEAT-24 is back to its one expected violation, the unpinned `review_sha`.
- Cycles: **1 of 10, unchanged.** The lead reported zero send-backs; a blocked-before-dispatch task
  is not rework.
- Runs: 7 of 20.
