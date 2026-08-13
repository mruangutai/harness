# FEAT-18 — operator answers, 2026-08-13 — ONE decision, and it strikes D-08 and SC-08

The plan is **not signed**, so this is a revision before approval, not an amendment to a signed
artifact. Everything below was measured today by the main session. **Do not re-derive it.**

## The decision

> **D-08 is STRUCK. SC-08 is STRUCK. `gh issue develop` is not used at all.**
>
> The build branch is created the ordinary way — `git checkout -b feat/FEAT-18-board-truth` — like
> every feature shipped so far. Nothing links the PR to the parent issue. No `Closes #N` string is
> composed either; that remains declined, and it remains unnecessary.

Operator's ruling, taken after the two failures below were measured.

## Why — two breaks, both measured today, not argued

### Break 1 — `gh issue develop` bypasses `branch-create-gate.sh` entirely

The gate extracts a branch name from **four patterns, all `git` subcommands**
(`branch-create-gate.sh:62-71`): `checkout -b`, `switch -c|--create`, `worktree add -b`, and
`git branch NAME`. Anything else falls to **`else exit 0`** at `:72`.

`gh issue develop` matches none of them, so the gate exits silently. The `git checkout <branch>` that
follows has no `-b`, so it matches none either. **The flow-id check DEC-144 exists to run never runs
on either command.** D-08 recorded this gap and chose to accept it; the ruling above closes it
instead, for free, by not creating the gap.

### Break 2 — a linked-branch PR closes the parent issue on merge, with no keyword

**Measured end to end on the disposable fixture `mruangutai/harness-factory-smoke-a1`:**

1. created issue **#7**
2. `gh issue develop 7 --name probe/auto-close` — confirmed via GraphQL `linkedBranches`
3. committed one file to that branch
4. opened PR **#8**, body stating in words that it contains **no closing keyword**
5. merged it

> **Result: issue #7 `CLOSED`, `stateReason=COMPLETED`.** The branch linkage closed it.

Board 3 has **`Auto-close issue` and `Item closed` ENABLED** (measured 2026-08-13 via the `projectV2`
`workflows` field; also enabled: `Auto-add sub-issues to project`, `Auto-add to project`,
`Auto-archive items`, `Item added to project`, `Pull request merged`. **DISABLED:** `Pull request
linked to issue` — and that one governs column moves on link, not closure on merge, so it does not
rescue anything).

So a merged PR closes the parent and lands its card in `Done`.

### Why that is severe rather than theoretical

**5 of 14 features shipped more than one PR titled with their FEAT id. FEAT-16 shipped three**
(#311, #312, and one more). Counted from `gh pr list --state merged` at 2026-08-13.

So the ordinary case is: the **first** PR merges, the parent closes and lands in `Done` **while tasks
are still running**, and the next `close-task`'s parent rule writes `Building` or `Review` back onto
a closed issue's card. INV-26 then reports the parent as drift for the rest of the build.

It also falsifies the terminal exemption's stated premise at `plan.yaml:114` — "the ship closes the
parent". Something else can close it first.

## The fact that makes the strike cheap rather than a sacrifice

**`gh-sync.py`'s `cmd_ship` ALREADY closes the parent** (`gh-sync.py:552-582`, when
`parent_origin == "created"`, per D-01/SC-04), **and already posts the ship review as a comment on
it**. The linkage was adopted to replace the `Closes #N` string — but that string's only *effect*,
closing the issue at the end, was already built and already shipping.

**So D-08 solved a solved problem, and broke two things doing it.**

## What pm must change

1. **Strike D-08.** Keep its entry with a strike record so citations still land (DEC-188 shape), and
   record that both breaks were measured, not predicted. Its `because:` text about
   `gh issue develop` being unable to link an existing branch stays true and stays recorded — it is
   simply no longer load-bearing.
2. **Strike SC-08** — it asserts this feature's build branch appears as a linked branch of its parent
   (`BRIEF.md:73`). That will now be false by design. **If SC-08 was the only criterion covering a
   real behaviour, say so rather than silently dropping the coverage.**
3. **D-03's "sole driver" claim now stands unqualified** and should say why: with no linkage, nothing
   but `gh-sync.py` and the ship's own close writes the parent card. Fold the workflow roster above
   into its `because:` so the next reader sees that GitHub's enabled workflows were checked rather
   than assumed.
4. **Keep the `Closes #N` fence.** `BRIEF.md:114` currently justifies it by "the native linked branch
   replaces it". That justification is gone; the fence is not. Restate it as the operator's standing
   preference, which is what it always was.
5. **Check whether any task's `intent:` assumed the linked branch** — T-06's playbook ordering is the
   likely place — and correct it to plain `git checkout -b`.

## Two things NOT decided here

- **Q1 remains open and is the operator's alone.** D-05 adds `github.board` keys against the
  grilling's settled "never add its four config keys". pm's source analysis was accepted as correct;
  what is left is what the operator meant by the fence, which no agent can recover. It rides with the
  signature. **Do not resolve it.**
- **Q2 was settled by the advisor, not the operator** — accept the recorded gap, D-08 stands. **That
  ruling is now moot: D-08 is struck, so the gap it recorded cannot occur.** Record it as
  overtaken by this revision rather than as a decision still in force.

## Scope fence — unchanged

Still out: product boards (#278), and composing `Closes #N` into a PR body. **Do not widen scope on
the strength of this revision.** Teaching `branch-create-gate.sh` to parse `gh` subcommands is now
unnecessary and must not be added.
