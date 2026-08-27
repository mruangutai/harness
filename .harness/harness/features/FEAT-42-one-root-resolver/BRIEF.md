# BRIEF — FEAT-42 One root resolver

source_issues: [742, 866]

## Problem

Nine different places in the harness each answer "which checkout am I looking at?" their own way, and
they disagree. Measured on 2026-08-26: today's `gh-cost-2026-08-26.jsonl` exists in the FEAT-41
worktree (1,213 lines) and the FEAT-37 worktree (36 lines) and **not at all** in the main checkout,
because `gh_cost_log.py:111` derives the root from its own file's location and a worktree runs its own
copy. The same mechanism split the single-flight claim registry: six `harness-pm` collisions passed a
gate that was watching a different registry, because `dispatch-guard.sh:83` resolves from the
DISPATCHING agent's working directory and an agent's process cwd does not follow its assignment. A
subagent told to work in `FEAT-42`'s worktree stands in the main checkout until it happens to run `cd`.
So a guard can be green and wrong at the same time, and the operator finds out when two agents overwrite
each other's `plan.yaml`.

Two sites already solved this privately and shared nothing — `check-domain.sh:885-890` built its own
worktree enumeration, `dispatch-guard.sh:75` its own upward walk. That copy/paste is the defect.

The override makes one wrong answer spread. `HARNESS_PROJECT_DIR`, once set by a parent, is inherited
by every child process it spawns and by their children in turn, so a root chosen in one place is
silently in force everywhere below it. That inheritance is not hypothetical as a mechanism: during
FEAT-40 it misled an orchestrator far enough that it nearly filed a wrong finding, attributing a
failing test to a scratch clone's sweep having inherited the variable
(`.harness/harness/features/FEAT-40-harness-writes-done/observations/harness-orchestrator.md:58`).
**Stated at its evidenced strength and no further:** that author records the reasoning and then
rejects it verbatim — "That reasoning was plausible and WRONG — the main-clone run fails too" — so
what is on the record is the mechanism and its power to mislead, NOT a confirmed wrong-root failure.
`.omp/extensions/harness-hooks.ts:144` is where that inheritance chain starts today: the host adapter
injects the variable into every policy script it spawns.

## Goal

One function answers where the harness is, every mechanism calls it, and nothing infers a root from
where a process happens to be standing. A dispatch declares which feature it belongs to, so the answer
comes from the assignment rather than from an accident of inheritance. The claim registry that guards
parallel work becomes trustworthy: one registry, claims that expire inside the cycle they guard, and a
printed remedy that does not destroy another feature's work.

## Requirements

- REQ-01: One resolver answers "where is this harness rooted" for every harness mechanism, and no
  executable site **anywhere in the repository** outside that resolver's own module carries the
  environment fallback chain, sets its variable, or does its own directory arithmetic. This is every
  occurrence, not a chosen subset: measured at sha 3952814 over tracked non-test source files, the
  chain occurs **21 times across 17 files**. One of them (`inject-expertise.sh:31`) is a
  `SubagentStart` hook falling back to `$(pwd)`; one of them (`.omp/extensions/harness-hooks.ts:144`)
  is the host adapter INJECTING the variable into every policy script it spawns, and it is the only
  occurrence outside `.claude/skills/harness/bin/`.
- REQ-02: A site that cannot establish a root refuses, rather than proceeding against a guessed one.
- REQ-03: The former resolver names no longer exist. Every former caller reaches the shared resolver
  directly, with no forwarder left behind.
- REQ-04: A harness install is recognised by one marker, spelled the same way in every project, so a
  directory that merely happens to be named `.harness` is never mistaken for one.
- REQ-05: Every governed dispatch declares the feature it belongs to, and a dispatch that does not is
  refused rather than recorded against a guessed root.
- REQ-06: A stranded single-flight claim cannot lock a tier chain out of reporting. A claim lives no
  longer than the cycle it guards and a claim belonging to a dead or foreign session is treated as
  absent; the printed remedy names an absolute path, works from any working directory, and releases
  only the claim it names; a returning agent's release never removes another agent's still-live claim;
  and neither consumer of the registry — the dispatch guard and the digest validator's
  children-in-flight check — can compound one stranding into a chain of refusals. Measured 2026-08-26
  (`runs/2026-08-26-2-plan-product/digest.md` and this feature's `STATE.md`): ONE stranded claim
  refused pm's spawn at `dispatch-guard.sh`, then refused the lead's return at `validate-digest.py`,
  then refused the orchestrator's return the same way. Each stranding creates the next, and the record
  survived only because the stop hook fires once.
- REQ-07: Each issue citation in the claim registry's refusal text names the issue whose subject it
  actually describes.
- REQ-08: Every function of the shared resolver, and every site moved onto it, is covered by a test
  that can go red, and no coded allowlist exempts a site this feature has moved onto the resolver.
- REQ-09: Behaviour the existing gates already pin — governed writes, plan-route discovery, worktree
  ownership — is unchanged by the cutover.

## Success Criteria

- SC-01: A COUNT that must reach ZERO, over a set nobody enumerates. The scan root is **every tracked
  source file in the repository**, not one directory: `git ls-files`, keeping every file whose
  basename does not begin with `test-`, excluding `harness_boundary.py` (the resolver's own module,
  the one place the variable may be read), excluding `*.md` (prose — notes and observations discuss
  the variable by name and always will) and excluding the harness's own record tree —
  `.harness/harness/features/**`, `.harness/notes/**`, `.harness/logs/**` — on that identical
  rationale. **Operator ruling, 2026-08-27.** The `*.md` exclusion had the reasoning right and the
  file extension too narrow: this feature's own `plan.yaml` names the variable **49 times** and a
  ship-review page twice, because their job is describing its removal. Measured at sha 3952814,
  committing the feature directory would move the count from 21 lines across 17 files to **72 across
  19**, and those 51 can never be removed. The exclusion is scoped to the record tree alone, so
  `.harness/harness.json`, `.harness/team-config.yaml`, everything under `.claude/`, and
  `.omp/extensions/harness-hooks.ts` all stay in scope — the last being the site the widened scan
  root exists to reach. Over that set the number of lines matching
  `HARNESS_PROJECT_DIR` is 0. The criterion FAILS while ANY ONE survives; no file list appears in the
  assertion, so a site added later — **and a site outside `.claude/skills/harness/bin/`** — is caught
  too. **The two exclusions are stated here on purpose**: `test-*.py` files SET the variable, it is
  the test-injection seam (`test-gh-close-gate.py:41`), and it stays; `harness_boundary.py` is the
  resolver. Paired per DEC-169 with a presence assertion — `harness_boundary.MARKER` and
  `resolve_root` exist, and at least 16 files under `.claude/skills/harness/bin/` import
  `harness_boundary` — so the absence half cannot pass vacuously. Baseline: **21 occurrences across 17
  files**, observed at sha 3952814, BRIEF pending — the 20 across 16 under
  `.claude/skills/harness/bin/`, plus `.omp/extensions/harness-hooks.ts:144`, which the narrower scan
  root structurally could not see. The assertion must be shown red at that widened baseline before it
  passes.
  verify: automated      evidence: unit
- SC-02: `resolve_root` raises when neither the override nor the derived root carries
  `.harness/team-config.yaml`, and a case demonstrates the refusal failing before the strict behaviour
  exists.
  verify: automated      evidence: unit
- SC-03: The successor to `wayfind.root()` does not resolve a marker-less directory named `.harness` as
  a root. A case built with such a directory above the start point returns the real root, and the same
  case is shown red against the old directory probe. This is the `$HOME/.harness/` fail-open measured
  at `check-plan-routes.py:489-495`.
  verify: automated      evidence: unit
- SC-04: The seven removed resolver definitions — `factory_config.harness_root`, `wayfind.root`,
  `context-watch._repo_root_from_script`, `dispatch-guard._root_from`,
  `post-merge-sweep._resolve_repo_root`, and the two inline chains at `harness_yaml.py:449` and
  `check-state.sh:22` — appear nowhere in executable code under `.claude/skills/harness/bin/`.
  `worktree_owner` and `_resolve_main_checkout_root` still exist and answer their own questions.
  verify: automated      evidence: unit
- SC-05: A governed write still succeeds and a denied write still fails after the `factory_config`
  cutover: `check-domain.sh --resolve` over a fixed path list produces a byte-identical verdict set
  before and after, captured to two files and diffed.
  verify: automated      evidence: integration
- SC-06: A governed dispatch carrying no `HARNESS-FEATURE:` line is refused at exit 2, and one carrying
  it is admitted and records its claim under the declared feature's root.
  verify: automated      evidence: integration
- SC-07: A single-flight claim is treated as absent once the guarded cycle has passed AND when it
  carries a session other than the reader's; the printed remedy command is absolute, runs from any
  working directory, and leaves another agent's claims intact; and a release issued by a returning
  agent never removes a still-live claim belonging to a different agent of the same persona. Four
  cases, each shown red first: (a) a second agent's claim survives the remedy; (b) a claim stamped
  with a foreign session is not counted live; (c) with two live same-persona claims and no way to tell
  them apart, release removes NEITHER and says so on stderr — shown red against today's
  `min(started_at)` pop at `inflight_registry.py:224-232`, which removed the abandoned run's claim and
  stranded the returning lead's; (d) the digest validator's children-in-flight check does not refuse a
  return against a claim its own registry should already have reaped.
  verify: automated      evidence: integration
- SC-08: In `inflight_registry.py`, the sentence about a second writer overwriting the first's
  `plan.yaml` cites #628, and the sentence about a verdict on a member still running keeps #551. Each
  occurrence is decided individually, and the test that pins each string moves with it.
  verify: automated      evidence: integration
- SC-09: `check-plan-routes.py`'s "no cwd fallback" — the issue-#133 fix — still holds:
  `test-check-plan-routes.py` cases at `:324-330`, `:935` and `:983` pass unmodified.
  verify: automated      evidence: integration
- SC-10: Each of the four resolver functions has at least one test case demonstrated to fail before its
  implementation existed, with the red output recorded to a receipt under the feature's `notes/`. A
  surviving mutant is not accepted as evidence unless the receipt also shows the mutation applied.
  verify: inspection
- SC-11: A dispatch to an agent assigned to a feature's worktree records its claim in THAT worktree's
  registry, not in the registry of wherever the dispatcher happened to be standing. Driven against the
  real `dispatch-guard.sh` in a fixture tree, the file's existing idiom
  (`test-dispatch-guard.py:121-142`): payload `cwd` is the fixture MAIN checkout, `tool_input.prompt`
  declares `HARNESS-FEATURE:` for a feature whose fixture worktree exists, and the assertion is that
  the claim is written to the worktree's `.harness/.inflight-claims.json` while the main checkout's is
  untouched. Shown red first against `dispatch-guard.sh:83`, which resolves from payload `cwd`.
  verify: automated      evidence: integration

## Verification gaps

- `component`, `ui`, `eval` and `typecheck` carry `cmd: null` in `.harness/harness.json`. None of their
  `detect` globs match Python or shell under `.claude/skills/harness/bin/`, so no criterion here rests
  on a null kind. `functional` is excluded under DEC-187 for the same reason.
- **SC-11 was `verify: uat` and is not any more.** What a live operator dispatch adds over a fixture
  test is the payload SHAPE, and the shape is already measured on disk from real spawns —
  `FEAT-31-orchestrator-context-watch/notes/probe-hook-payload-identity.md` (the eleven keys) and
  `FEAT-32-concurrent-write-merge/notes/research-FEAT-32-hook-payloads.md` (a real governed dispatch,
  `agent_type=harness-orchestrator`, `cwd=` the FEAT-32 worktree). Everything after the payload is
  deterministic code this feature edits, so a fixture case settles it. **The residual, stated:** no
  test can prove a real dispatch prompt CONTAINS the `HARNESS-FEATURE:` line — that is agent conduct.
  SC-06 pins the machine half instead: a dispatch without the line is refused at exit 2, which is what
  makes the conduct unnecessary to trust.
- **CLOSED, not a gap.** An earlier draft of this brief carried
  `.omp/extensions/harness-hooks.ts:144` as out of SC-01's scope by construction and as an open
  question at signature. The operator ruled on 2026-08-26 to scope it in. SC-01's scan root is now
  repository-wide and reaches that line, and a task removes the injection. Neither half of the old
  carve-out survives: the site is in scope, and it is not an open question.

## Constraints

- **DEC-174 amendment 4 BLOCKS execution** on `check-domain.sh`, `bash-write-guard.sh`,
  `validate-digest.py`, `check-state.sh`, `check-plan-routes.py`, `dispatch-guard.sh` and the test file
  of each. Those are main-session-direct. Its library rule also governs here: a squad may write
  `harness_boundary.py`, and the cutover that makes a gate use it is main-session-direct, proven by an
  identical violation set before and after.
- **DEC-179 SUPPLIES** the routing check: `check-domain.sh --resolve` answers whether a squad may write
  a surface at all. It is blind to DEC-174's lane and is not used to set one.
- **DEC-182 SUPPLIES** the `plan.yaml` format and its merge tool.
- **DEC-202 SUPPLIES** the provider-neutral mirror. Measured at this worktree: `.agents/skills` is a
  symlink to `../.claude/skills`, so both spellings reach one file.
- **DEC-183 SUPPLIES** the required `integration` CI job that runs `check-plan-routes.py` over every
  live plan.
- **DEC-187 SUPPLIES** the exclusion of the `functional` test kind.
- `post-merge-sweep.sh` is not in DEC-174's enumeration and carries zero refusals, but it DELETES
  worktrees and a run lives in one. It is main-session-direct for that reason.
- **This must not be built while another feature's build is live.** Changing the dispatch gate hits
  every in-flight agent mid-run.
- `harness_boundary.py` imports only `os`, `re` and `sys`. It must stay that way: a `PreToolUse` hook
  runs before every Bash call and cannot afford `factory_config`'s eager network import.
- `worktree_owner()` does not change by one line. `post-merge-sweep._resolve_main_checkout_root()` asks
  git a different question and stays.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-08-27
sc-01-amended: SC-01's exclusions gained the harness's own record tree (.harness/harness/features/**,
.harness/notes/**, .harness/logs/**) on the operator's ruling of 2026-08-27, extending the existing
*.md prose rule to the .yaml and .html records that carry the same content. The same three paths
already sit in test-no-distribution.py:92 as EXCLUDED_PREFIXES under the comment "Historical records
that stay true as written".
