# Layer-0 segments — FEAT-30, the five tasks no agent may execute

**BLUF.** Five of this plan's ten tasks are `main-session-direct` and they form **ONE segment, not
two** — because the team lane has **zero** dependencies on the layer-0 lane, so the entire eng
segment lands before the DAG ever reaches T-03. That is the one structurally lucky thing about this
feature: you get a single, uninterrupted, dependency-ordered batch, and none of your five tasks is
waiting on a squad run.

Do not hand any of these to an agent. `check-plan-routes.py` prints `DEVIATION` for T-03, T-04 and
T-05 — that is **correct output for a correct plan**: `--resolve` answers who may WRITE a path, while
the DEC-174 execution carve-out is a separate axis that is mechanized nowhere. It prints `OK` for
T-07 and T-09 because those paths resolve to `NOBODY`, which I re-verified in this tree rather than
trusting the plan's `eeabc59` snapshot.

## Precondition — start from MY commit, not from `49c528a`

All five of your tasks assume the team lane is already in your tree, and two of them fail outright
without it:

- **T-07's `verify:`** runs `python3 .claude/skills/harness/bin/test-expertise-merge.py` — that file
  is T-06's, from my lane. On a tree at `49c528a` it does not exist and T-07 cannot pass.
- **T-04's** new cases exercise the two-segment layout that T-01's CLI produces.

Also: run every `verify:` **from the repository root**. They use repo-root-relative paths
(`.claude/skills/harness/bin/…`), and the two guard suites additionally resolve their
worktree-boundary fixtures against the current directory — see the false-red section below.

## Run them in this order

| # | Task | Issue | Surface | Why layer 0 | Blocked until |
|---|---|---|---|---|---|
| 1 | **T-03** | #618 | `bin/test-check-domain.py` | DEC-174 am.4 — test file of a gate script | nothing |
| 2 | **T-04** | #619 | `bin/harness_boundary.py`, `bin/check-domain.sh`, `bin/test-check-domain.py`, `bin/test-bash-write-guard.py` | DEC-174 am.4 — the enforcement layer, and the cutover making a gate use the new mechanism is yours | T-03 |
| 3 | **T-05** | #620 | `bin/bash-write-guard.sh`, `bin/test-bash-write-guard.py` | DEC-174 am.4 — registered PreToolUse gate script + its test file | T-04 |
| 4 | **T-07** | #622 | `.claude/skills/harness-distill/SKILL.md` | `--resolve` prints `NOBODY` | T-06 (team lane) |
| 5 | **T-09** | #624 | `.claude/agents/harness-orchestrator.md`, `.claude/commands/harness.md`, `.claude/skills/harness/SKILL.md` | `--resolve` prints `NOBODY` | T-04, T-05, T-07, T-08 |

**T-03 → T-04 → T-05 is a hard chain** and it is the plan's own dependency order. T-07 is independent
of all three and may be done at any point after this note; doing it first is fine and costs nothing.
T-09 must be last — it depends on four tasks, three of them yours.

## Read this before T-04 — a fail-open window I measured, not inferred

`harness_boundary.py:37` defines `WORKTREE_REL_RE` as `^\.claude/worktrees/[^/]+/(.+)$` and
`check-domain.sh:644` repeats the same shape as its own inline literal. **Both hard-code exactly ONE
path segment below `.claude/worktrees`.** T-01's **delivered** `dest_for` — read from the artifact,
not from the plan's intent — is `feature-worktree.py:56-59`:

    return os.path.join(owner_root, hb.WORKTREES_SEGMENT, segment, id)

That is **two** components below the segment, `<segment>/<id>`.

So in the window between T-01 landing (already in the tree) and T-04 landing:

- a **real** worktree created by the new CLI is not reached by the `check-domain.sh` sweep globs
  (`:602`), and its paths do not match the boundary strip;
- `check-domain.sh` therefore returns **without enforcing** on those paths. That is a **silent
  fail-open, not a block** — nothing prints, nothing exits non-zero, and the write is simply
  ungoverned.

**Consequence for you: do not create a real feature worktree with `feature-worktree.py` until T-04
has landed.** T-01's and T-10's own cases are unaffected — they build worktrees inside temp fixtures
with an anti-escape guard, and they never touch `.claude/worktrees/` in this checkout.

This is also the reason T-04 must not be split per file: `WORKTREE_REL_RE` has consumers in two
files, so a partial cutover leaves `harness_boundary.py` without the attribute while
`check-domain.sh` still reaches for it — and that direction fails **open** too. Atomicity is the
safety property here, not tidiness (D-02, DEC-193).

## A LIVE one-segment worktree exists — use it as T-04's real regression target

`git worktree list --porcelain` in this checkout reports two trees: the main checkout on
`feat/FEAT-30-worktree-per-feature`, and **`.claude/worktrees/FEAT-31` on
`feat/FEAT-31-orchestrator-context-watch`** — yours, and not to be touched.

What matters for T-04: FEAT-31 sits **one** segment below `.claude/worktrees`, the OLD layout. So it
currently DOES match `WORKTREE_REL_RE` and it IS governed today. Two consequences:

- **It bounds the fail-open above.** The window I described affects only NEW two-segment trees from
  the CLI. FEAT-31 is not silently ungoverned right now.
- **It is a free, real regression target.** T-04's replacement must be depth-agnostic, so after the
  cutover a path inside `.claude/worktrees/FEAT-31/` must still resolve to the same grant it does
  now. That is checkable against a real linked worktree rather than only a fixture — and T-04's own
  intent already commits to keeping the one-segment case working (`wt1 is still exactly one segment
  deep`). **I already captured it for you**, at `49c528a`, pre-T-04 — these are
  `check-domain.sh --resolve` answers for paths INSIDE `.claude/worktrees/FEAT-31/`:

      .claude/skills/harness/bin/feature-worktree.py   harness-backend-dev, harness-dev-ops
      .claude/skills/harness/bin/check-domain.sh       harness-backend-dev, harness-dev-ops
      .harness/harness.json                            harness-dev-ops

  Each is **identical** to the same path resolved outside the worktree, which is SC-05's property
  holding today at one segment. Re-run those three after T-04 and they must be unchanged. If any of
  them turns into `NOBODY`, the depth-agnostic resolution regressed and the guard is failing open —
  that is the single cheapest post-T-04 check available, and it uses a real linked worktree rather
  than a fixture.

Do not create, move or remove that worktree to test anything.

## T-04's line anchors are still valid — I checked, because they were taken at `eeabc59`

`check-domain.sh` and `harness_boundary.py` are **byte-identical** between `eeabc59` and my HEAD
(`git diff --stat eeabc59 HEAD` empty for both), and each anchor lands on the content T-04 claims:

- `harness_boundary.py:37` → the `WORKTREE_REL_RE` assignment
- `check-domain.sh:602` → `SWEEP_GLOBS = tuple(...)`
- `check-domain.sh:644` → `wt = re.match(r"^\.claude/worktrees/[^/]+/(.+)$", rel)`
- `test-bash-write-guard.py:491-506` → the `WORKTREES_SEGMENT` mutation case T-04 says to leave in place

Line anchors normally rot inside one feature's lifetime; these did not. **They will rot the moment
you start editing, so work top-down within each file** — or anchor on the content strings above
rather than the numbers.

## The two suites you will re-run most give a FALSE RED from the wrong directory

T-03, T-04 and T-05 all modify `test-check-domain.py` and/or `test-bash-write-guard.py`, so you will
run them by hand many times. **They are cwd-sensitive.** Measured both ways at `49c528a`:

    cwd = .claude/skills/harness/bin   ->  exit 1,  13/14 and 25/27   <- FALSE RED
    cwd = repository root              ->  exit 0,  14/14 and 27/27   <- true state

Their worktree-boundary cases resolve paths against the current directory. **Always run them from
the repository root.** I nearly reported a red suite off the first reading; the cwd was the whole
difference. Their true pre-state, before you touch anything, is fully green.

Related, and it will bite you if you run a suite mid-sequence: **`run-unit-tests.sh` exits 2 for
every kind while an unregistered `test-*.py` sits in `bin/`** — a deliberate drift detector at
`run-unit-tests.sh:41-56`. That window is entirely inside my lane (T-01 opens it, T-08 closes it) and
I will not hand you a tree with it open. If you ever see `MISCONFIGURED: … is not in
run-unit-tests.sh's explicit script list`, it is a registration gap, not a test failure.

## Two operator rulings bind these tasks. Do not re-derive them.

**R-01 governs T-05.** REQ-04's `HEAD` refusal binds **all sixteen** governed agents, `harness-dev-ops`
included. The HEAD-move matcher is evaluated **before** `bash-write-guard.sh`'s `harness-dev-ops`
early return at `:56-57`, and that early return **survives unchanged for every WRITE**. The authority
is `DECISIONS.md:3650` — not the `DECISIONS-INDEX.md:170` summary row, which is what three tiers
argued from before anyone opened the entry. Accepted cost, recorded: when HEAD is wrong and the guard
is working, `harness-dev-ops` cannot fix it either; the repair is yours from the main session, which
carries no `agent_type` and which this guard does not bind.

I verified both R-01 anchors live in this tree, because a wrong anchor wastes your hands:
`bash-write-guard.sh:56-57` is exactly `if agent == "harness-dev-ops": sys.exit(0)`, the early
return — so **T-05's HEAD matcher must be inserted ABOVE line 56**, and everything at or below it is
the WRITE path that survives unchanged. `DECISIONS.md:3650-3652` reads "Every other harness agent
except dev-ops (exempt per DEC-85 - owns builds) gets extractable **target paths** checked against
its team-config domain", which is exactly why moving HEAD falls outside the exemption. The ruling and
its citation both hold.

**R-02 governs the budget, not these tasks directly**, but its third clause matters to you: **no fix
cycle for SC-01b lands in the enforcement layer**, so an SC-01b failure costs my cycles and never
your hands. T-05's refusal is a PreToolUse Bash hook, so it sees an agent's Bash tool calls and not a
git fork from inside a python test — and T-10's four writers are forks.

## Read this before T-09 — a POSITIONAL assertion you can break without deleting anything

T-09 edits `.claude/skills/harness/SKILL.md`. A **unit** test asserts on that file:
`test-team-catalog.py` check (8) requires `test_matrix` to appear at least once AND `qa`,
`validator` and `loop_back` to all appear **within 8 CONSECUTIVE lines**.

I measured the current state: **only 5 windows in the whole 388-line file satisfy it, all clustered
at lines 50-54**, with `validator` at line 54, `harness-qa` at 55 and `loop_back` at 57. The span
you must not disturb is roughly **lines 50-61**.

**So inserting your worktree paragraph in the wrong place reds the unit suite while deleting
nothing.** The assertion is positional, not textual — pushing `loop_back` more than 8 lines away
from `validator` fails it, and the failure message talks about the qa gate, which will not look like
it has anything to do with the worktree text you just added.

Insert outside lines 50-61 and this cannot fire. **The good news: T-09's own `verify:` catches it
anyway** — it runs `run-unit-tests.sh` with no `--kind`, which defaults to `all`, and greps for
`^FAIL `. So the plan already protects you here; this note only tells you what the failure MEANS if
you see it, so you do not go hunting in the wrong file.

## The "sixteen" in T-03 and R-01 is correct — I counted it

T-03 pins in-worktree grant behaviour "for all sixteen agents" and R-01 binds "all sixteen governed
agents". Verified against `.harness/team-config.yaml`: **exactly 16** distinct `harness-*` agents —
ai-dev, backend-dev, code-reviewer, data-engineer, dev-ops, documentor, eng-lead, frontend-dev,
orchestrator, pm, product-lead, qa, security-reviewer, ui-reviewer, validator-lead, visual-designer.

`main-session` is **not** among them, which is correct and load-bearing: D-04 scopes the HEAD refusal
to governed agents and answers the main-session case by isolation instead, and the main session
carries no `agent_type` so this guard cannot bind it.

A criterion quantifying over 16 items is satisfied by 15 conforming ones, so **enumerate the roster
in T-03's fixture rather than grepping file-globally** — a whole-file grep passes on 15 and cannot
see the 16th.

## Where the instructions are — read them from the plan, not from here

Each task's `intent:` is the executable specification and each `verify:` is its gate. **They are
deliberately not copied into this note.** T-04's intent alone is ~15,500 characters with byte-exact
strings, embedded heredocs and explicit do-not-do rules in it, and a second copy can drift from the
signed artifact. Read them from
`.harness/harness/features/FEAT-30-worktree-per-feature/plan.yaml`, by task id.

One trap, and it IS measured — a predecessor recorded it first-hand in
`observations/harness-orchestrator.md`: an append was denied because an angle-bracket placeholder in
prose read as an input redirect, and the denial named a target appearing nowhere in the intent. Their
conclusion: documentation about git or shell cannot reliably be written through the Bash route; use
the Write tool. I confirmed the masking half at `bash-write-guard.sh:155-167`, which documents this
exact behaviour and states it fails safe. So: **the Bash write
guard parses heredoc content as shell and masks quoted spans wholesale** (the masking half I did
confirm, at `bash-write-guard.sh:155-167`, which documents exactly this and says it fails safe), so a `verify:` containing a heredoc or a quoted redirect
target may be refused. That is the guard reading the content, not a defect in the verify — re-express
the invocation as a script file. Do not weaken a `verify:` to get past it.

## What I have NOT done, and why

- **No review panel.** T-04 and T-05 are the highest-risk surfaces in this feature and they are
  yours; a panel on a team-only diff reviews half the feature, and its verdict would die the moment
  your tasks move the tip. The panel, the goal-check and the docs segment all belong to the phase
  after this one.
- **No PR, no merge.** Out of scope by instruction.
- **A false FAIL is waiting for T-04 at the qa gate, and it is not a defect in your work.** T-04 is
  `cross_module`, so `test_matrix` requires `integration`, and the gate confirms coverage via
  `test_kinds.integration.detect` globs (`harness-qa-gate/SKILL.md:57`, with `:74` making "nothing
  found" a FAIL). T-04's test files — `test-check-domain.py`, `test-bash-write-guard.py` — are NOT in
  that detect list, though both genuinely run under `--kind integration`
  (`run-unit-tests.sh:18`). So a gate reading the glob literally reports "integration missing" on a
  correctly-tested task. Full analysis and the exact wording to hand the grader are in
  `notes/orchestrator-M17-build-baseline-exact.md`. Pass it on when you re-delegate, or it costs a
  cycle to discover and another to argue away.
- **No `phase:` key in `feature.json`.** The playbook says to write one; `check-domain.sh --post`
  denies it as an undeclared key against the execution-state schema. Phase is in `STATE.md` instead.
  That contradiction is a harness defect and it is not mine to fix inside this feature.
