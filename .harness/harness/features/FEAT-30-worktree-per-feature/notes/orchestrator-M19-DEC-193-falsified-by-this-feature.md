# M-19. This feature FALSIFIES DEC-193's stated worktree location, and no task in the plan fixes it

Not a delivery defect. A **record-integrity** consequence that no gate in this repository can detect,
which is exactly why it is written down rather than left as a carried open question (it was Q13,
"DEC-193's and DEC-95's stale spelling of the worktree location" — now measured).

## The contradiction, both sides quoted

**DEC-193 says one segment.** `DECISIONS.md:5877`:

> **There are exactly two places code is written under harness's authority:**
> `.claude/worktrees/<id>/`, …

restated at `:5983`, and carried in the index row at `DECISIONS-INDEX.md:211`:

> Exactly two locations hold code under harness authority — `.claude/worktrees/<id>/` and
> `workspace_root/<repo>`, that segment renamed from `<product>` by am.2; any other checkout is refused.

**FEAT-30 ships two segments.** `feature-worktree.py:56-59`, delivered:

    return os.path.join(owner_root, hb.WORKTREES_SEGMENT, segment, id)

where `segment` is the repository path segment (for `mruangutai/harness`, `harness`). So a harness
worktree becomes `.claude/worktrees/harness/FEAT-NN/`, not `.claude/worktrees/FEAT-NN/`. T-04's whole
purpose is to make the guards depth-agnostic precisely because the depth changed.

**After this feature lands, DEC-193's sentence is false as written.**

## Why nothing will catch it

`CLAUDE.md` is explicit: a decision the tree flatly contradicts is **STRUCK, never marked** (DEC-188)
— and *"there is no propagation checker — nothing detects a falsified statement left standing, so the
striking has to actually happen."* No test asserts DECISIONS.md against the tree. `check-state.sh`
does not read it. So this survives indefinitely unless someone acts.

It also has reach: **D-02 and D-03 of this very plan cite DEC-193**, and DEC-189 references it. A
future reader resolving "where may code live" lands on the one-segment spelling and is misled by an
entry this feature invalidated.

## Why it is NOT a fix cycle, and not mine to add

- **No requirement covers it.** REQ-01 through REQ-08 say nothing about the decision record, and no
  task's `files:` includes any path under `.harness/harness/docs/` — I checked all ten.
- So adding it is a **plan-level change**, which is pm's under the operator's approval, never an
  execution-time adjustment I may make. Editing an approved plan to insert a task is exactly the
  authority boundary I do not cross.

## The routing answer, since it is not obvious

`check-domain.sh --resolve` puts all three docs on **`harness-documentor`** — a granted agent. So
this is a **team-lane** surface reachable through `harness-product-lead`, **not** a
`main-session-direct` task and **not** something the operator must type by hand. That matters: the
cheapest correct disposal is one documentor spawn, not an operator segment.

Precedent exists for the shape: **DEC-193 am.2 already renamed a segment** (`<product>` → `<repo>`).
An am.3 recording the `<repo>/<id>` depth is the same, well-trodden move.

## Recommendation

Surface it to the operator as a **named pre-ship step or an explicit backlog row**, their choice —
not as a silent omission. My recommendation: an **am.3 on DEC-193** recording the two-segment layout,
dispatched to `harness-documentor` through product-lead **after** the operator's T-04 lands, so the
amendment describes a tree that actually exists rather than one that is half-built.

Doing it before T-04 would document a layout the guards do not yet honour, which is the same
falsification pointing the other way.

DEC-95 (`@1229`, "one feature per worktree … `.harness/` as per-worktree state") is **not** falsified
— it makes no claim about path depth. Q13 was half right, and this note supersedes it.
