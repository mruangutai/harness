# Operator answers — FEAT-45 plan questions — 2026-08-30

Written by the main session. ONE consolidated revision covers everything below. The plan is NOT
signed; both approval fragments stay `pending` until this revision lands.

## Q1 — model independence: THE PREMISE WAS WRONG, RESTORE THE STRONGER CLAIM

REQ-02 and REQ-05 were weakened to promise an independent **CONTEXT** on the finding that no
`harness-` lead may select a model for what it spawns. That finding is correct but it does not
support the conclusion.

**Measured by the main session:**

- `dispatch-guard.sh:41-51` blocks a lead from **passing** `model:` in a dispatch. Its own comment
  states the rule it is enforcing: *"A member runs on the model pinned in its agent frontmatter —
  that pin is org design."* The guard does not strip an agent's own pin.
- `~/.omp/agent/agents/fable-advisor.md` frontmatter carries `model: anthropic/claude-fable-5`.

So a lead that spawns the advisor **without** passing `model:` gets Fable 5. Model independence
survives lead dispatch. **Restore REQ-02 and REQ-05 to the independent-MODEL claim.**

**But the real constraint, which nobody named, must be handled:** that definition lives at
`~/.omp/agent/agents/`, in the USER'S HOME, not in this repository. Under Q3 the team file ships as
doctrine to every project the factory is pointed at, where the persona may simply not exist.

**Required:** define the absent-persona behaviour explicitly. A panel whose advisor persona cannot be
resolved must **skip that reader and record the skip durably** — never a silent pass, and never a
panel that reports clean because a reader never ran. The existing SC-07 shape (a missing panel result
is machine-detectable) is the right instrument; extend it, or add a criterion, as pm judges. Do NOT
bring the advisor's definition into the repository — that is agent distribution and it is new scope.

## Q2 — re-plan scope: RATIFIED

pm's ruling stands and is now the operator's: a task-set change resets approval, so the plan is
presented again and therefore READ again, scoped to the not-done tasks. This was left in the
grilling's `## Not yet specified` and is hereby settled.

Evidence it matters, from this same day: FEAT-38's panel revision was exactly a resume-phase re-plan,
and the panel found a **high-severity defect in it** — T-24's verify could not pass at its own
completion. Under a first-signature-only rule that defect would have reached the build.

## Q3 — team file: SHIPPED DOCTRINE

`.claude/skills/harness/teams/plan-panel.yaml`, not the `.harness/teams/` project-override lane.
Confirmed as standing doctrine for every project the factory is pointed at. This is what makes Q1's
absent-persona handling mandatory rather than optional.

## Q4 — DEC-174 carve-out reading: CONFIRMED

T-07 and T-08 stay `main-session-direct` on paths resolving to `harness-backend-dev` /
`harness-dev-ops`. That is a deliberate carve-out deviation, not a route violation, and it is
correctly recorded as such.

## Q5..Q8 — backlog rows: DECLINED, ALL FOUR

The operator was offered these as backlog issues and struck every one. Recorded so the decision is
visible rather than lost:

- **Q5 — DEC-170 cites `advisorModel` at a settings line where it does not exist.** Not filed.
- **Q6 — the plan door's feature enumeration reads the main checkout** and is blind to any feature
  living only on its branch. Not filed. NOTE FOR THE RECORD: this defect caused a real id collision
  today — FEAT-44 was coined twice and a worktree, branch and orchestrator run had to be destroyed
  and recut as FEAT-45. It is not hypothetical. The operator declined it anyway; it stays out of
  FEAT-45's scope and off the backlog.
- **Q7 — `plan-merge.py` can neither create a plan (exit 8 on an `approval:` key) nor express a fix
  cycle (exit 7 on a changed task).** Not filed. Both cycles in this feature used direct writes.
- **Q8 — a reference set giving panel QUALITY evidence** beyond one operator eyeball. Not filed.
  The BRIEF continues to record openly that finding quality is ungraded.

## Not changing

- The 16-agent roster does not grow. SC-06's census stands.
- `review_sha` stays at `1d3e5db` and is NOT re-pointed forward: that is genuinely the sha the
  simplify and ui readers reviewed, and the fix cycle landed after. Pinning forward would claim a
  review that never happened.
- The plan-door id-scan defect stays OUT of FEAT-45. It fires at feature creation, before a brief or
  plan exists, so no panel reader could ever reach it.
