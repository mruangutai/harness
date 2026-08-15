# UI Reviewer — FEAT-12 end-copy-distribution — c0

**review_sha:** `d543809` (full: `d54380922964552dc4e0e026b3fd4419c12cbe3c`). All claims below established by
`git show d543809:<path>` / `git show <commit> -- <path>` / `git ls-tree -r --name-only d543809` — the
sha exists and was confirmed reachable before reading (`git cat-file -e d543809`).

**Scope.** No `DESIGN.md`, no rendered markup in this diff — Mode B against a design contract is `n/a`.
The dispatch names an adjacent surface this role does own: the terminal doors (`.claude/commands/harness*.md`)
and the strings two scripts print. Per P-06, that is in-remit, not a decline. `in_scope: true`.

## Q1 — door set after `harness-deploy.md`'s deletion

`git ls-tree -r --name-only d543809 -- .claude/commands/` shows six surviving doors: `harness-deepen`,
`harness-grilling`, `harness-map`, `harness-plan`, `harness-ship`, `harness`. `harness-deploy.md` is
gone (T-08's verify's own `-ge 6` floor is met).

Grepped each door's body for `deploy|distribut|registry|copy`. Only one hit, `harness.md:81`, and in
context ("which *copy* of a file executes … a resolution question") it is about filesystem/hook
resolution, unrelated to the deleted distribution mechanism. No surviving door promises, describes, or
routes the user to a distribution step.

**Orphan check:** read each door's opening lines (front matter + first paragraph). All six describe a
self-contained mission (`deepen`, `grilling`, `map`, `plan`, `ship`, the general `harness` door) with no
framing as a step before/after deploy. None is orphaned by the deletion.

**Q1 answer: no live door dead-ends the user, and none is orphaned.**

## Q2 — the two rewritten `upgrade-config.py` messages

Read at the sha (`upgrade-config.py:174-179` and `:251-259`); diffed against T-10's plan-specified wording
(`plan.yaml:605-613`) and the prior commit (`9e49ba7`).

**Message 1** (missing templates dir, `:176-178`):
> `upgrade-config: no templates at {tdir} — the templates ship inside this repository at
> .claude/skills/harness/bin/../templates, so a missing templates directory means the checkout is
> incomplete.`

- **Literal deviation from the signed plan, verified word-for-word.** `plan.yaml:608-610` specifies the
  replacement ending "...checkout is incomplete, **not that a distribution step was skipped**." The
  shipped string ends at "incomplete." — the trailing clause is absent. The prose the task's own intent
  promised is not what shipped; low severity (the surviving sentence isn't false), but a literal-text
  finding, not narrative-only (P-07).
- **No remedy.** The message diagnoses ("checkout is incomplete") but does not tell the user what to do
  about it — no "re-clone", no "run X", nothing. Its sibling at `:254-257` does: "The remedy is a
  complete checkout of this repository, not a distribution step; report it if that does not fix it." The
  asymmetry is real: one message names a fix and an escalation path, the other names neither. Nothing
  gates this — `test-upgrade-config.py:175-177`'s case 6 asserts only `"checkout is incomplete" in out`.
- **The location claim doesn't track what it just reported.** The message prints the actual missing path
  as `{tdir}`, then in the same sentence hardcodes a second, different-looking path,
  `.claude/skills/harness/bin/../templates`, as where "this repository" ships templates. `tdir` is
  computed from `args[0]` (the project root the script was invoked against) unless `--templates`
  overrides it — confirmed by reading `test-upgrade-config.py`'s own case 6, which calls the script with
  `--templates <dir>/_does_not_exist`. So `{tdir}` can legitimately be an arbitrary path with no relation
  to `.claude/skills/harness/bin/../templates`, and "this repository" has no fixed referent for a reader
  comparing the two path strings in the same sentence.

**Message 2** (unparsable shipped template, `:254-257`):
> `THE SHIPPED TEMPLATE at {t_yaml} does not parse — {e}` / `This is a harness bug, NOT your project...
> The remedy is a complete checkout of this repository, not a distribution step; report it if that does
> not fix it.`

Matches the plan's specified wording verbatim (`git grep` confirms "complete checkout of this repository"
appears exactly as planned). Actionable — names a remedy and an escalation path — and true given the
harness's own architecture claim (templates live in this repo, not distributed).

**Q2 answer:** message 2 is actionable and true. Message 1 is true but not actionable (diagnosis without
remedy) and its "this repository" clause names a path unrelated to the one it just reported as missing —
a genuine copy defect, not a token-sweep miss (SC-07's sweep only checks for the four retired tokens, not
for message quality). Neither is a `must_fix` — the harm is a missing next-step sentence, not a false or
broken instruction, and closing it would mean editing text the signed plan itself specified (partially).
Recommend as a follow-up: give message 1 the same "remedy + report" close message 2 already has.

## Q3 — onboarding narrative coherence

**`harness-init/SKILL.md:27` and `:222`** (the two spots the dispatch named, both previously conditioned
on `/harness-deploy`): read in isolation, both are complete, self-contained instructions. `:27` — "the
harness templates directory is not readable from here. Stop and say so; there is nothing to instantiate."
`:222` — "but only if agent definitions were installed or updated during this same session" — a session-
scoped conditional, not one that references a deleted command. No headerless section, no dangling
conditional at either site.

**Narrow reading passes; the reading the question actually asks does not.** Read `README.md` top to
bottom as a first-time reader: "Prerequisites" (still) lists GSD installed globally, and the
"Repository structure" block a few lines later still shows `.planning/harness.json` and
`.planning/config.json` as the project layout — before the reader ever reaches "Getting your repository
into the harness," the one true onboarding step FEAT-12 wrote. This repo's own `CLAUDE.md` states "There
is no GSD dependency: no `.planning/` root, no `agent_skills`" — so the frame the onboarding paragraph now
sits inside is false, even though the paragraph itself is accurate. **This predates FEAT-12** — blame
shows the GSD/`.planning/` framing traces to `c06cf5d` (original README, long before this feature) and
T-12 (`ff75afb`) rewrote only the distribution-specific passages inside it, which is exactly what its own
scope said it would do. Not a `must_fix` here; worth a separate issue for a full README pass, since the
onboarding step this feature wrote is currently unreachable-looking from a cold read.

**One more residual, low severity:** `harness-init/SKILL.md:229-230` — "The hooks written in step 1 *are*
live immediately — verified — and agents that deploy installed before this session started are spawnable
now" — "deploy" here is a bare noun, past tense, describing history (agents a prior deploy run installed).
It does not instruct anyone to run a deleted step, so it is not a REQ-07 breach. But T-13's `TOKEN_RE`
(`harness-deploy|deploy\.sh|harness-registry|registry\.json`) structurally cannot match a bare "deploy",
so this stale-mechanism word survives, unflagged, inside a file this feature otherwise edited for exactly
this reason (`:27`, `:222`).

**One naming note, not a finding:** `README.md` and `.harness/README.md` both route the reader to
`/harness-init` as if it were a slash command. `git ls-tree -r --name-only d543809` confirms no
`.claude/commands/harness-init.md` exists — it is a skill (`.claude/skills/harness-init/SKILL.md`), not a
command door. This convention predates FEAT-12 and is used the same way throughout the corpus; whether the
runtime resolves `/harness-init` by skill-description match is a resolution question this role cannot
settle from source.

## Accessibility / theme parity

Explicitly out of scope and stated rather than omitted, per dispatch instruction: there is no rendered
surface, no colour, no focus model, no contrast pair, and no dark/light theme anywhere in this diff. Both
dimensions do not apply here.

## Verdict reasoning

No `must_fix`. The message-1 wording delta and actionability gap, the pre-existing README/GSD framing
mismatch, and the residual bare "deploy" mention are all `med` or `low` — none is an accessibility failure
(the only automatic `high` under this role's gate) and none blocks. `severity_max: med`.
