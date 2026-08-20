# Layer-0 segments — FEAT-29, the five tasks no agent may execute

**BLUF.** Five of this plan's nine tasks are `main-session-direct` and they split into **two
batches, not one** — because **T-06 must land before T-01/T-02 do**, and T-01/T-02 are mine. That
ordering is the one thing in this feature that cannot be recovered if it goes wrong, so the build
has NOT been dispatched. Batch A is yours to run now; tell me when it is done and I will run the
eng segment, then hand you batch B.

Do not hand any of these to an agent. `check-plan-routes.py` prints `DEVIATION` for T-06, T-07 and
T-09 — that is correct output for a correct plan (`--resolve` answers who may WRITE; the DEC-174
execution carve-out is a separate axis and is mechanized nowhere).

## Why this is two batches and not one

`check-state.sh` INV-26 calls `_gb.board_stations`. **T-02 rewires `board_stations` onto the cheap
read.** So T-02 landing in the working tree — not the commit, the *tree*, since `check-state.sh`
imports `gh_board.py` from disk — is what makes the gate cheap. The moment it lands, the 490–507
red state SC-01 and SC-04 are graded against is gone.

I considered three ways to keep the build in one session and rejected all three:

- **Build in a worktree.** The feature dir is untracked on `main`, so a worktree from the branch
  point would carry no `plan.yaml`. Fixing that needs the branch committed first, which puts the
  two trees on one branch. Real complexity for a saving of one spawn.
- **Land T-01 and T-04 only** (neither touches the gate's cost path) and hold T-02/T-03. T-01 edits
  `factory_gh.py`, which `check-state.sh` imports; T-03 wires cost logging into `run_gh` and creates
  `.harness/logs/gh-cost-<date>.jsonl` during the baseline run. Both perturb the tree SC-04 compares.
  Splitting the eng squad into two runs to save nothing measurable is a bad trade.
- **Recover the baseline later from a git checkout.** Technically possible; it is not the same
  measurement, because the board is live and its card count is the cost driver. You ruled the order
  non-negotiable and I am not going to defeat it on a technicality.

## Batch A — run NOW, before I dispatch anything

| # | Task | Issue | Surface | Why layer 0 | GraphQL cost |
|---|---|---|---|---|---|
| 1 | **T-05** | #583 | `.harness/notes/grilling-graphql-cost-2026-08-10.md` | `--resolve` prints `NOBODY` | 0 |
| 2 | **T-06** | #584 | `notes/measurement-before.md` | DEC-174 — runs the gate whose output IS the evidence | **~507** |

**T-05 first, T-06 second.** T-05 costs nothing and touches a file no invariant reads, so doing it
before the baseline means the two measurements see a tree that differs only by the change under
test. Doing it after works too; doing it *between* T-06 and T-07 adds a difference for no reason.

## Batch B — after the eng segment returns, and I will hand it to you again

| # | Task | Issue | Surface | Unblocked by | GraphQL cost |
|---|---|---|---|---|---|
| 1 | **T-09** | #587 | `notes/measurement-board6.md` | T-01, T-02 | ~110 |
| 2 | **T-07** | #585 | `check-state.sh`, `notes/measurement-after.md` | T-01, T-02, T-06 | ~5 |
| 3 | **T-08** | #586 | `CLAUDE.md` | T-07 | 0 |

T-09 before T-07 puts the two independent-of-each-other measurements first; if T-07's cutover proof
fails, T-09's board-6 evidence for SC-03 is already banked.

## Where the instructions are — read them from the plan, not from here

Each task's `intent:` is the executable specification and each `verify:` is its gate. **They are
deliberately not copied into this note.** A second copy can drift from the signed artifact, and
these intents run to 40+ lines with byte-exact strings and embedded heredocs in them.

```
python3 - <<'PY'
import yaml
d = yaml.safe_load(open('.harness/harness/features/FEAT-29-graphql-budget/plan.yaml'))
for t in d['tasks']:
    if t['id'] in ('T-05', 'T-06'):          # batch B: ('T-09', 'T-07', 'T-08')
        print('='*70); print(t['id'], '-', t['title'])
        print('--- FILES ---');  print('\n'.join(t['files']))
        print('--- INTENT ---'); print(t['intent'])
        print('--- VERIFY ---'); print(t['verify'])
PY
```

Run each `verify:` exactly as written, from the repository root, after its task's edits. All five
exit non-zero on an incomplete job and print a per-item line naming what is missing.

## The board protocol for a layer-0 task — this is on you, and it is not optional

I am not in session while you run these, so the two `gh-sync` sync points for T-05..T-09 are yours.
**`plan.yaml` is written FIRST, then the subcommand** — the parent card's station is *derived* from
task statuses, so the plan must already carry the new value when the subcommand reads it. Record
`done` after `close-task` and the derivation reads the old value, the parent write is a no-op, and
the parent card sits in `Building` forever.

`TID` and the two states are the only things to change. I verified this substitution against this
plan for all five ids: each matches **exactly one** task and the result round-trips through
`yaml.safe_load`.

```
python3 - <<'PY'
import re, io, yaml
TID, FROM, TO = "T-06", "pending", "building"
p = ".harness/harness/features/FEAT-29-graphql-budget/plan.yaml"
s = io.open(p, encoding="utf-8").read()
s, n = re.subn(r"(- id: %s\b.*?\n    status: )%s" % (TID, FROM), r"\g<1>" + TO, s, flags=re.S)
assert n == 1, "expected 1 substitution, got %d" % n
yaml.safe_load(s)
io.open(p, "w", encoding="utf-8").write(s)
print(TID, FROM, "->", TO)
PY

python3 .claude/skills/harness/bin/gh-sync.py start-task .harness/harness/features/FEAT-29-graphql-budget T-06
# ...do the task...
# re-run the block above with FROM="building", TO="done", THEN:
python3 .claude/skills/harness/bin/gh-sync.py close-task .harness/harness/features/FEAT-29-graphql-budget T-06
```

Each pair costs about 4 GraphQL points, extrapolated from a measurement: `gh-sync.py open` cost
**40 points** for a milestone plus 9 issues plus 9 sub-issue attachments (before 3676, after 3716,
2026-08-19, board 3).

**One trap, and it lands on T-06 specifically.** INV-26 skips a feature entirely while every task
reads `pending` — `check-state.sh:1218-1221`, *"Nothing has started. No card can be wrong yet, so no
claim is right."* So if you mark T-06 `building` before running the gate, INV-26 starts comparing all
nine FEAT-29 cards against the plan for the first time, **inside the baseline**. Either way is
defensible; **just be consistent across T-06 and T-07**, because SC-04 compares those two violation
blocks line by line. My recommendation: mark `building` and run `start-task` **before** the gate, so
the baseline and the after-measurement are taken under the same INV-26 regime.

## What I verified, and what you must re-check

Verified by me on `feat/FEAT-29-graphql-budget` at `3920513` plus this feature's own artifact
commit — no file either measurement reads is touched by that commit:

- **Both approval gates pass.** `BRIEF.md ## Approval` reads `status: approved`, and `plan.yaml`'s
  `approval.status` is `approved`, both signed *operator (Mike Ruangutai), via main session*,
  2026-08-19. Q1 is recorded RULED at `BRIEF.md:141`, code-fix-only.
- **Lanes re-resolved at `3920513`, unchanged from your reading.** `gh_board.py`, `factory_gh.py`,
  `gh_cost_log.py`, `gh-sync.py` → `harness-backend-dev, harness-dev-ops`. `CLAUDE.md` → `NOBODY`.
  `.harness/notes/grilling-graphql-cost-2026-08-10.md` → `NOBODY`. `resolved_at` re-pinned `d457d08`
  → `3920513`.
- **`check-plan-routes.py`: `0 violation(s)`, exit 0**, with `DEVIATION` on T-06, T-07, T-09 exactly
  as you predicted, and `OK ... declared main-session-direct` on T-05 and T-08.
- **`feature.json` validates** against `.claude/skills/harness/bin/feature-schema.json`.
- **The mirror ran clean**: milestone #18, parent #571 skipped as already recorded (no orphan
  created), sub-issues #579–#587 for T-01–T-09, all attached to #571.

**Re-check before you start:**

1. **The budget, first thing.** `gh api rate_limit --jq .resources.graphql.used` read **3673** at
   09:59 local — **1,327 points left**, not the 2,900 you handed me. Something spent ~1,605 points
   between your reading (2068) and mine, with no call of mine in between. That is the same
   counter-drift the BRIEF records at ~300 points, four times as large. The window resets
   **10:45:06 local**. T-06 needs ~507; it fits, but a second gate run in this window does not.
   **If you can wait for the reset, wait** — T-06 is the one measurement in this feature that cannot
   be retaken.
2. **Nothing else in flight.** T-06's intent requires it and requires you to say in the file that you
   confirmed it. FEAT-26 and FEAT-28 are paused; confirm no other agent run is live.
3. **`CLAUDE.md` is dirty in your tree** and I have not touched it. It is not on this branch's
   artifact commit. T-08 is yours and the collision is yours.
4. **The two standing `check-state.sh` violations** are FEAT-26 and FEAT-28 unapproved BRIEFs. They
   must appear identically in `measurement-before.md` and `measurement-after.md`. If either flow's
   BRIEF gets approved between the two runs, that is a legitimate `EXPLAINED-DIFFERENCE` — record it,
   do not adjust the captured output.
5. **`gh-sync.py open` printed no board-station line.** I did not spend a board read to find out
   whether #579–#587 actually landed on board 3, because a board read is the expensive call this
   feature exists to kill. INV-26 cannot see it today (every task is `pending`, so the feature is
   skipped), but it will the moment a status moves. If the baseline shows FEAT-29 card violations,
   that is a real finding about `open`, not about your run.

## What I did NOT do

- **I did not run `check-state.sh`.** You ran it minutes ago on this same tree at `3920513` and
  reported it clean for FEAT-29 with two violations on other flows. Spending 507 of 1,327 remaining
  points to re-derive your reading would have left T-06 unaffordable in this window.
- **I did not run `gh project item-list` or any board read.** Same reason.
- **I did not touch `CLAUDE.md`, `check-state.sh`, or `.harness/notes/`.**
