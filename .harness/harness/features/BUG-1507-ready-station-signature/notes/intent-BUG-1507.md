# Stated intent — BUG-1507 (issue #1507)

The operator's stated intent for this flow is **GitHub issue #1507**, authored by @mruangutai on
2026-09-08 (`https://github.com/mruangutai/harness/issues/1507`). There was no grilling or wayfinding
session; the issue is the intake artifact and its "Definition of Done" is the acceptance sentence.
This note transcribes that intent and records what the orchestrator verified on disk before
planning, so the goal-check and the plan panel grade the plan against the operator's words rather
than against a paraphrase.

## The operator's Definition of Done, transcribed verbatim

- Once the operator signs a feature's plan, that feature's ticket visibly moves to the **Ready**
  column on the GitHub board — automatically, as part of running the normal signature step, with no
  extra manual command needed.
- A ticket sitting in **Ready** always means "plan is signed, build hasn't started yet" — nothing
  else can put a card there, and nothing puts a card there without a real signature.
- Once the orchestrator actually starts dispatching build work on a feature, that feature's own plan
  record advances to **Building** (not just its individual tasks) — so looking at the plan alone
  tells you it's being built, before build phase.
- We can grep `.harness/harness/features/*/plan.yaml` after this fix and see real features with
  `status: ready` and `status: building` recorded in their history — not just `plan`, `review`,
  `done`.
- No new station names, no schema changes, no changes to the frozen six-station list. This is fixing
  two dead wires, not building anything new.

## The operator's stated scope, transcribed

The issue's own scope line: *"documentation/instruction only — no station enum work, no schema
change, no new decision; this only restores what FEAT-41 already designed"*, enumerated as four
items — `harness-plan.md:24` `Ready`→`ready`; `github-mirror.md:94,96,55-56` lowercased; a
feature-level `building` write added to `SKILL.md`'s build phase plus the matching row in
`github-mirror.md`'s writer table; and `gh-sync.py`'s `cmd_status` docstring stating what
`status <dir> building` does, "a stated decision, not silent fallthrough".

## What the orchestrator verified on disk, worktree at 4b5dbb23

Every claim below was measured in
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1507-ready-station-signature`,
not inferred from the issue.

- `.claude/commands/harness-plan.md:24` reads `gh-sync.py status <feature-dir> Ready` — capital `R`.
  Confirmed present.
- `gh-sync.py` `cmd_status` refuses an unrecognised station before any write: `if station not in
  STATION_VALUES: refuse(...)`, and there is no case-folding on the path in. So the documented
  command refuses, always.
- `.claude/skills/harness/references/github-mirror.md:94` and `:96` carry the capitalized
  `gh-sync.py status <dir> Ready` and `status <dir> Review` spellings in the "who writes each
  station" table. The prose paragraph under that table also carries `gh-sync.py status
  <feature-dir> Review`. Confirmed present.
- The same file's "a phase transition happens" row (line ~55) ALREADY says lowercase and already
  names `plan-merge.py set-feature-station` — so the file contradicts itself between its rows. The
  issue's `:55-56` citation is that row's neighbourhood; the capitalized spellings that actually
  refuse are at `:94`/`:96` and in the post-table prose.
- `SKILL.md`'s build phase (lines 136-153, the four segments) names no feature-level `building`
  write. Its segment 4 already says `gh-sync.py status <feature-dir> review`, lowercase, with the
  FEAT-41 comment. Confirmed absent.
- `gh-sync.py` `cmd_status` docstring's "STATION WRITES" list enumerates Ready, Review, and
  "Plan, Done, Abandoned: no station write at all". **Building appears nowhere in it.**
- The actual current behaviour for `building`, read from the code: `_record_station(feat_dir,
  station)` runs (which shells out to `plan-merge.py set-feature-station`), then the early return
  guard `if board is None or station in ("plan", "done", TERMINAL_MARKER)` does NOT catch
  `building`, so control falls through to `rec = load_recorded(feat_dir)` — a receipts read — and
  then neither the `if station == "ready"` nor the `elif station == "review"` branch fires. Net:
  the plan station is recorded, the receipts file is read for nothing, and no card is written.
- `.agents/skills` is a **symlink to `../.claude/skills`** (verified: matching inodes on all three
  shared files, and `git ls-files` tracks only the `.claude/...` paths). All four surfaces therefore
  have exactly one canonical path, spelled `.claude/...`.

## Lane resolution, measured with check-domain.sh --resolve

- `.claude/commands/harness-plan.md` → **NOBODY**
- `.claude/skills/harness/references/github-mirror.md` → **NOBODY**
- `.claude/skills/harness/SKILL.md` → **NOBODY**
- `.claude/skills/harness/bin/gh-sync.py` → `harness-backend-dev`, `harness-dev-ops`

Three of the four surfaces are main-session-direct by lane; only `gh-sync.py` is team lane.

## The one ambiguity a reader must resolve, not paper over

The first Definition-of-Done bullet says the Ready move happens "as part of running the normal
signature step, with no extra manual command needed", while the issue's own scope item 1 asks only
for a capitalization fix to an instruction the operator runs *after* the signature. Two readings:
(a) the documented signature STEP includes the gh-sync call, so the operator does nothing beyond
following that step — the capitalization fix satisfies the bullet; or (b) `sign-approval` itself
must trigger the station write, which would be a code change to the signature path and contradicts
the issue's stated "documentation/instruction only" scope.

The planner must state which reading it took as a `decisions:` entry and why, rather than leaving it
implicit. The orchestrator did not resolve it and did not instruct a resolution.
