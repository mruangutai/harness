# Orchestrator measurements — FEAT-30 plan phase, all at eeabc59

Probes I ran myself because a tier without Bash cannot close these. **M-2 CARRIED A WRONG
CONCLUSION and is corrected below — read M-2c before acting on M-2.** Method is given for each so
every line is re-runnable.

## The one that changes a test's design

**M-1. The refusal REQ-08 removes exists only when the SESSION ROOT is OUTSIDE the worktree.**
Write route, `agent_type: harness-pm`, target
`<tree>/.harness/harness/features/FEAT-30-worktree-per-feature/plan.yaml`, against a REAL detached
worktree at `.claude/worktrees/harness/PROBE-eeabc59`:

    CLAUDE_PROJECT_DIR = the worktree      -> exit 0
    CLAUDE_PROJECT_DIR = the main checkout -> exit 2

So an SC-02c test MUST fix `CLAUDE_PROJECT_DIR` at the outer checkout. Root it in the worktree and
the assertion is green today and incapable of going red — SC-02c's own stated trap, one level deeper
than the brief states it. This is also why REQ-08 is load-bearing rather than cosmetic: a subagent
inherits the session's project dir, so an orchestrator working in a worktree while the session is
rooted in the main checkout IS the failing shape, and it is the shape this feature must support.

## The one I got wrong, and the correction

**M-2. A DIRECT `git worktree add` into a served repository's own checkout is refused.**
On stdin to `bash-write-guard.sh`:

    git worktree add <workspace_root>/kaya-ai/.claude/worktrees/kaya-ai/FEAT-30 <branch>
      harness-backend-dev   exit 2
      harness-orchestrator  exit 2
    git worktree add <harness_root>/.claude/worktrees/harness/FEAT-30 <branch>
      both                  exit 0

The legal home is `realpath(CLAUDE_PROJECT_DIR)/.claude/worktrees` with no fleet awareness, so the
door only ever permits worktrees of the repository the session is rooted in.

**M-2b.** The same served-repo command exits **0** for `agent_type: harness-dev-ops`, which DEC-151
exempts from this guard entirely. So a plan that routes creation to dev-ops passes the door by
exemption rather than by being legal, and proves nothing about any other persona.

**M-2c. CORRECTION — I concluded "REQ-01's served-repo half is BLOCKED and needs a guard task".
That is false for the plan as drafted.** Measured after reading T-01's intent:

    python3 .claude/skills/harness/bin/feature-worktree.py create --repo org/repoB --id FEAT-30
      harness-backend-dev   exit 0
      harness-orchestrator  exit 0

The door's parser looks for a `git` token in the Bash payload. A CLI that forks git internally
presents none, so the door never fires and creation for a served repository succeeds. **Nothing is
blocked and no task is required to unblock it.**

What survives is not a blocker but an architecture question: after this feature the SANCTIONED way to
create a worktree is invisible to the door that exists to refuse bad worktrees, while a hand-typed
`git worktree add` for the same legal destination is refused. Two options, and the choice is
`harness-eng-lead`'s in the architecture review, not mine:

- **Accept it.** Record that door 1 governs ad-hoc git only and the CLI is the sanctioned path. Costs
  nothing now; leaves the guard's rule and the sanctioned mechanism disagreeing.
- **Widen door 1 to be owner-aware** — legal home computed per owning checkout rather than per
  session root. Enforcement layer, `main-session-direct`, and it makes the door true for both routes.

I am recording the error rather than quietly deleting it: it was passed to `harness-product-lead` as
S-2 of a staged send-back and could have bought an unnecessary enforcement-layer task.

## The one that shrinks a task

**M-3. Refuse-on-dirty is already git's behaviour; the gap is the force flag.**
`git worktree remove` on a tree holding one untracked file: exit **128**, message
`contains modified or untracked files, use --force to delete it`. The same removal with `--force`
passes `bash-write-guard.sh` at exit **0** — its git parser handles `worktree add|move` only. SC-07 is
therefore a small addition to that parser plus a rule, not a dirty-tree detector.

## Corroborations

**M-4.** `WORKTREE_REL_RE` on `.claude/worktrees/harness/FEAT-30/.harness/x.md` returns
`FEAT-30/.harness/x.md`; the one-level form returns `.harness/x.md`. REQ-08's premise holds.

**M-5.** `git worktree add --detach <harness_root>/.claude/worktrees/harness/<id>` succeeds and
`git worktree list` shows both trees. Git has no opinion about depth, and `.gitignore:21` already
ignores `.claude/worktrees/`, so a worktree never pollutes the outer status.

**M-6.** `git -C <two-level worktree> diff --name-only HEAD~1..HEAD` prints
`.harness/harness/features/FEAT-30-worktree-per-feature/BRIEF.md` — WORKTREE-relative, no
`.claude/worktrees/` prefix. This closes by measurement the residue `f4-downgrade.md` left as
inference: the `.claude/worktrees/**` matrix exclude cannot blind a worktree-hosted run.

**M-7.** `git switch <existing branch>` exits 0 for every governed `agent_type` probed, on both
hooks. REQ-04 is new surface.

**M-8.** The creation door parses the LITERAL Bash string: a destination carried in a shell variable
is refused as "a RELATIVE destination" although it resolves to a legal absolute path. Measured on one
of my own commands. This is the same mechanism M-2c rests on.

**M-9. Baseline for SC-09**, both suites at eeabc59: `--kind unit` and `--kind integration` each pass
with zero FAIL or ERROR lines. `check-state.sh` reports exactly two VIOLATIONs, both unapproved
BRIEFs in the paused FEAT-26 and FEAT-28 flows, neither belonging to this feature. State the sha AND
the condition when citing this: two violations later is not FEAT-30 regressing, and zero later is not
an improvement — it means those flows moved.

## Lane facts I resolved (`check-domain.sh --resolve`, this checkout)

    .claude/skills/harness/bin/**            -> harness-backend-dev harness-dev-ops
    .harness/harness.json                    -> harness-dev-ops
    .harness/harness/docs/DECISIONS.md       -> harness-documentor
    .harness/harness/docs/DECISIONS-INDEX.md -> harness-documentor
    .claude/agents/*.md                      -> NOBODY
    .claude/commands/harness.md              -> NOBODY
    .claude/skills/harness/SKILL.md          -> NOBODY
    CLAUDE.md                                -> NOBODY
    .harness/team-config.yaml                -> NOBODY
    .harness/factory/fleet.yaml              -> NOBODY
    tests/integration/**                     -> NOBODY

`check-plan-routes.py` refuses the NOBODY rows if they are team-laned, and does NOT notice a
team-laned enforcement-layer file, because `bin/**` is granted. The carve-out is a hand check.

**A pointer I gave and had not read:** my dispatch suggested `layout_fixtures.py` as the fixture
route. It is 75 lines of layout-detector stub DATA with one function and no mention of worktrees, so
it cannot build a repository. `fixture-route.md` corrected it and I have since verified the
correction. Recommending a tool I had not opened is how a wrong pointer travels three tiers down.
