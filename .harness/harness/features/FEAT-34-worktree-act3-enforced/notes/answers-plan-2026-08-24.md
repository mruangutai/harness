# Operator answers — FEAT-34 plan — 2026-08-24

One consolidated set (DEC-176). Nothing else is open.

## Q5 — THE HOOK IS NOT ENFORCEMENT LAYER. THE INVARIANT IS.

**Ruling: the `post-merge` hook is `team`. `check-state.sh`'s invariant and its test are
`main-session-direct`.**

**The reason is DEC-174's own stated test**, in the table at `DECISIONS.md:4709`: *"the artifact
under change is the artifact doing the checking."* A `post-merge` hook checks nothing. It fires
after the merge has already happened and performs two writes — record the terminal status, remove
the checkout. **It cannot refuse anything.**

That is the same functional test amendment 4 applied when it added `dispatch-guard.sh`
(`DECISIONS.md:4887`): it joined *"on the evidence that it refuses dispatches — it declined a
`harness-orchestrator` dispatch over a `model` parameter on 2026-08-21."* A sweep that ACTS fails
that test.

**DEC-196 amendment 4 does not govern this.** Read in context at `DECISIONS.md:6550`, its subject is
a **Claude Code `PostToolUse` `Write`/`Edit` hook** — one that would fire on every edit in every
session and gate writes, at 490-506 GraphQL points per fire. That is enforcement. A git `post-merge`
hook is a different mechanism and the sentence was not written about it.

**The cost, named rather than argued away:** the hook deletes directories, which is destructive. But
destructive is not CIRCULAR. A broken `post-merge` hook fails loudly at merge time; a broken gate
hides its own breakage, and only the second is what DEC-174 exists to prevent.

**No DEC-174 amendment is written by this feature.** The category decides, the hook falls outside it,
and nothing joins the enumeration. Record the ruling as a `D-NN` in `plan.yaml` with the two anchors
above, so the next hook does not re-litigate it.

## Q1 — TRACK THE HOOKS DIRECTORY, AND `harness-init` SETS THE PATH.

pm's measurement is confirmed by the main session at `9165162`:

```
$ git config --get core.hooksPath
/Users/molchairuangutai/GitHub/harness/.git/hooks
```

**An absolute path carrying a username.** So no tracked hook can run in any other clone today, and
`harness-init` has no step that sets it. That is worse than "unspecified" — it is actively wrong for
every clone but this one.

**The fix has two halves and REQ-09/SC-08 get tasks for both:**
1. A **tracked** hooks directory in the repository. Resolve its path with `check-domain.sh --resolve`
   at HEAD and lane it by the result — do not assume. pm measured `.githooks/`, `.claude/hooks/` and
   `.claude/skills/harness/hooks/` all resolving NOBODY, which means the choice is a design decision
   and its own `D-NN`, not a lookup.
2. **`harness-init` runs `git config core.hooksPath <tracked dir>`** as a per-clone prerequisite,
   alongside the eight it already installs. It must be idempotent and must state what it found if the
   value was already set to something else — silently overwriting an operator's own hooks path is not
   acceptable.

**This is scope beyond the signed brief**, so it rides on the SAME amendment as #806. One amendment,
both additions, one re-signature.

## Q3 — NOT A DEADLOCK. A BACKLOG ROW.

Your reproduction stands: `check-state.sh` VIOLATES on a missing `approval:` block and no agent may
write one. But `.claude/skills/harness/templates/plan.yaml:30-35` already ships that block at
`status: pending`, and FEAT-19's plan carries exactly it. **The create path is to instantiate from the
template**, which this file did not. A procedural miss with a clean route.

The main session writes the `pending` block now to clear the gate. **File the backlog row** so the
next plan does not repeat it — a plan authored from scratch rather than from the template will hit
this every time, and nothing points pm at the template.

## Q4 — ACCEPTED, and say so in the plan.

SC-04's second-repository fixture is a new fixture CLASS: the only existing multi-repo fixture is a
declarative `fleet.yaml` plus plain files, never a real second git repo. Build it, and record in
T-02's intent that it is the first of its kind so a later reader does not assume a precedent exists.

## What you got right without being asked

**You checked the lead's `must_fix` instead of spending a cycle on it, and it dissolved.** The
assertion the lead objected to appears in none of `plan.yaml`, `state.yaml`, or pm's observations.
That is the second time in two features a lead's finding was a misreading, and both times the
orchestrator caught it by reading the artifact rather than the report.

**You reverted your own edit when the gate disagreed with it.** Reconciling the orphaned
`brief-audit-validator` run produced two new violations because the run dir does not exist in THIS
worktree — the note came from a scan of the main checkout. Reverting was right, and saying so is
what makes the record usable.

## SC-05 OF FEAT-35 IS CLOSED BY THIS RUN

Your dispatch ran **958.7 seconds** — `2026-08-24T16:46:48Z` to `≈17:02:47Z` — under the MERGED
stop-and-wake playbook with **no dispatch override**, ending its turn, taking the expected
single-flight refusal once, and being woken by the completion notification.

**That is the exact measurement FEAT-35's SC-05 owed**, and it cost nothing extra. The main session
records SC-05 as met and retires the obligation.

## After this

pm writes the amendment covering #806 AND the `core.hooksPath` addition, and the tasks for Q5's lane
and Q1's two halves. Return `awaiting_user`. The main session re-signs BRIEF and signs `plan.yaml`,
then runs `gh-sync.py status <dir> Ready`.

---

## Q6 — settled by the main session, 2026-08-24. Sign D-08 as written.

**Ruling: D-08 needs no harness-only scoping and no second mechanism for fleet repos.**

The orchestrator raised Q6 because `harness-init/SKILL.md:7-8` says the harness is not copied into a
product repository, so `.claude/skills/harness/hooks/` might not exist in a served repo. The premise
of the sentence is real. The conclusion does not follow, and the evidence is in the file `harness-init`
merges into the product repo.

**Measured at `9165162`:**

1. `.claude/skills/harness/templates/settings.snippet.json` points **all seven** hook entries at
   `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/`. `harness-init/SKILL.md:42-43` merges that
   snippet into the target project.
2. So an onboarded product repo must already carry `.claude/skills/harness/bin/`, or all seven
   harness gates are dead there. That requirement predates this feature.
3. `hooks/` sits beside `bin/` in the same tree. **D-08 therefore adds no assumption that the harness
   does not already depend on everywhere.** Putting the directory at a repository-root `.githooks/`
   would create a second harness-owned location while the first one stays required — strictly worse.

**The unverified thing, stated rather than folded in.** No onboarded product repo exists to check.
`/Users/molchairuangutai/GitHub/harness-factories/kaya-ai/.claude/` holds `commands`, `hooks` and
`settings.json` and **no `skills/` directory at all**, and its `settings.json` carries no harness hook
entries. So neither D-08 nor the seven existing gates have ever run in a fleet repo. That gap is real
and it is not this feature's to close — it belongs to whatever onboards the first product repo.

**Per-repo isolation is confirmed, and it does not change the ruling.** `feature-worktree.py:20-23`
records that `WORKTREES_SEGMENT` is joined only to a resolved `owner_root`, so each served repo's
worktrees live under that repo. A merge in a fleet repo fires that repo's hooks and sweeps that repo's
worktrees — which is correct, and which needs the same tree the seven gates already need.
