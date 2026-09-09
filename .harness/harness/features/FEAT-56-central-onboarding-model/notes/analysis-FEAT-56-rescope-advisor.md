# Digest — rescope-advisor-validator — FEAT-56 re-scope ruling

**TRANSCRIBED BY harness-orchestrator, not written by its author.** `harness-validator-lead` ran this
segment and returned a complete four-part ruling, but `check-domain.sh` refused every write by that
persona — this run dir AND its own granted `.harness/notes/analysis-*.md` — citing a stale claim on
`.claude/worktrees/harness/BUG-1309-mirror-build-entry`. It holds no shell and could not clear it.
The content below is its return verbatim in substance; the transcription is mine, and the two
defects that made it necessary are recorded at the foot of this file.

`fable-advisor` **RAN**: it resolved on this host, was not skipped, triggered no `on_fail`, and
returned a well-formed four-entry ruling. The lead dismissed none of its findings, revised none of
its severities, and invented no `PF-` id.

## VERDICT: ESCALATE — severity_max high, must_fix []

Four rulings; two of the questions are the operator's alone and no squad may take them.

## A1 — continue or succeed: (b) SUCCEED, conditional on the operator

Ship the delivered central model as FEAT-56; open a successor for provider neutrality plus the
command split. Reason: the work is pinned green at `review_sha` 9b72dd4b and the operator confirmed
its GOAL, so revising in place re-reviews accepted work with no new information; `feature.json` is
11/11 at a cap already raised once, so in-place forces a second raise; and SC-09 is a UAT read of the
very blob the re-scope orders split, so it cannot be met in its current form and must not be silently
dropped — record it `superseded by operator re-scope` and re-own it as a fresh `uat` criterion over
both successor artifacts. The advisor's own caveat is load-bearing: "do not ship" attached to the OLD
scope, so (b) is a PROPOSAL needing the operator's signature, never a licence to ship around a
binding FAIL. `scope_impact: smaller`, `severity: high`.

## A2 — provider-neutral: (b) RE-HOME the command surface. A LIVE DEFECT, not a doc gap

`.omp/config.yml` disables the `claude` DISCOVERY provider and `check-omp-port.py:61-62` asserts it;
the only discovery root reading `.claude/commands/**` is that provider, and neither `.omp/commands/`
nor `.agents/commands/` exists; an unmatched `/…` returns the original text and proceeds as prompt
content — fail-open, no error, no symptom. Everything else in neutrality landed with #589, and skills
are already neutral through the `.agents/skills` symlink, so **`harness-init` itself is already
provider-neutral**. Residual: re-home 4-5 command files to a canonical neutral root with generated
adapters on the `sync-agent-adapters.py` pattern plus a `check-omp-port.py` assertion, and scrub
Claude-only prose from Track A (`SKILL.md:33-34`, `:38`, `:44-45`). `scope_impact: larger`,
`severity: high` — bigger than the operator appears to expect, but bounded engineering on landed
prior art, not a second #206.

**The measurement is the orchestrator's, not the reader's** (the advisor holds no shell and said so):
`.omp/config.yml` carries `disabledProviders: [claude]`; `.omp/commands/` does not exist;
`.omp/extensions/harness-hooks.ts` registers NO slash command — every `command` occurrence in it is
the Bash-tool payload; `.omp/providers/` holds `anthropic.yml` and `openai.yml`. Agent and model
neutrality are delivered; the four `/harness*` doors are not.

## A3 — the name: `harness-add-repo` stands, and the artifact is a SKILL, not a command

All 23 skill directories are `harness-*`, `check-instruction-paths.py:29` hard-requires the prefix,
nothing collides. There is no `harness-init` command anywhere — only prose refs at `harness.md:12`,
`harness-plan.md:18`, `harness-grilling.md:7,12`. `BUILD.md:377-380` states init is a flat skill "not
a command, because commands do not distribute (DEC-06)". Files that must change: a new
`.claude/skills/harness-add-repo/SKILL.md`; `harness-init/SKILL.md` cut to Track A plus `--upgrade`;
`MAIN_SESSION_ONLY` at `check-instruction-paths.py:12-16` gains the name; three prose cross-refs; the
SC-04 doc set (`SPEC.md:441-447`, `BUILD.md:377-397`/`:784`, `org.html:286`, `README.md:192`,
`.harness/README.md`, `templates/README.md`); a new DECISIONS entry plus index regeneration; and every
verify block anchored on Track B line content re-anchored. `scope_impact: as_expected`,
`severity: med`.

## A4 — the seam: line 239 is the right A/B cut, but Track B must itself be re-cut

DEC-220 (`DECISIONS.md:6985-6989`) defines onboarding as exactly three things — config landed on the
default branch, fleet entry, central per-segment tree. Steps 2 (`:245`), 3 (`:284`), 4 (`:292`) plus
the GitHub-mirror (`:350`) and project-board (`:364`) sections discharge those and belong to
`add-repo`. Steps 6 (`:324`), 7 (`:335`), 8 (`:408`) write `BRIEF.md`, take its approval and run a
design pass — planning territory; keeping them inside `add-repo` reproduces the exact conflation the
operator rejected. Duplicated or orphaned: preamble `:8-19` goes to add-repo while `:22-29` must be
DUPLICATED into both; Preflight `:30-46` splits and add-repo needs a NEW preflight that does not
exist; `--upgrade`'s "through step 2" (`:211-212`) dangles; the Red flags table (`:419-434`) splits
row by row; and the interleaved numbering (A: 1, 5, 9 — B: 2, 3, 4, 6, 7, 8, no 5) forces both to
renumber. `scope_impact: larger`, `severity: med`.

## What the lead added beyond the reader

1. Ranked by IRREVERSIBILITY before severity. Terminus first — decided wrong it discards a green pin.
   Artifact kind second — it reverses a signed decision. Defect scope third. The seam last: authoring
   cost, fully reversible.
2. **A4 closes onto a route that does not exist.** The advisor said first-BRIEF "belongs to" the
   router at `harness.md:12`. That line routes `BRIEF.md missing` TO `/harness-init` — the artifact
   the split strips of steps 6-8. Cutting them from both files orphans first-BRIEF unless that router
   is repointed. Nobody had listed that task.
3. **A2's defect is not FEAT-56's.** It predates this feature and belongs to the #589 port; folding it
   in makes the successor look like the operator's request when half of it is unrelated debt.

## Adequacy notes

- ONE reader, no cross-check. A single advisor's ruling is an opinion with citations, not a panel;
  nothing attempted to falsify it.
- The port-commit hash is DISPUTED and unverified by the lead: the advisor reported `d35aa81a`, the
  orchestrator's `git log` on `feat/589-omp-provider-neutral` gives `184960d1` and finds no
  `d35aa81a`. **Cite issue #589** — a hash on an unmerged branch is not stable.
- A4's cost claim ("the bulk of the successor's authoring work") is unpriced judgement; no task
  breakdown exists, and that is pm's.

## Two harness defects this run exposed, both orchestrator-measured

1. **The guard and the registry read different stores.** `inflight_registry.py list` from the main
   checkout reports NO CLAIMS while `check-domain.sh` refuses on a stale claim. The claim record
   lives in the OTHER worktree's own registry — `REGISTRY_REL = .harness/.inflight-claims.json`
   resolved against that root — so a `list` run from the main checkout cannot see it and reports
   clear. `list --root <that worktree>` shows five live claims for BUG-1309: validator-lead,
   code-reviewer, qa, security-reviewer, ui-reviewer.
2. **`reconcile` cannot clear them.** `reconcile --root <that worktree>` returns `RECONCILED 0`
   because every claim carries `agent_id=None, job_id=None`, so there is no runtime identity to test
   for liveness. The sanctioned automatic route therefore cannot clear an identity-less stale claim,
   and the only remaining route is a blind `release` — which the orchestrator declined, because those
   claims belong to ANOTHER feature's flow and releasing them is not this feature's act.

The recovery that did work: the orchestrator holds the feature-directory grant, so it transcribed
this file itself. A validator artifact is recoverable by the tier above; the block is on the persona,
not on the path.
