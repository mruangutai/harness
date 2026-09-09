```yaml
VERDICT: ESCALATE
DIGEST:
  headline: "fable-advisor RAN and ruled all four: succeed rather than revise in place, re-home the command surface, keep harness-add-repo but as a SKILL, cut at line 239 then re-cut Track B — and Q2 is now a MEASURED live defect, the four .claude/commands/*.md are undiscoverable under OMP so /harness* silently falls through as prompt text today"
  team: rescope-advisor
  steps_run: 1
  cycles_used: 0
  members:
    - { step: rescope-ruling, persona: fable-advisor, verdict: PASS, headline: "Four rulings in the required shape, each anchored to a path or line it opened; disputed one fact the batch context supplied", files_touched: [] }
  must_fix: []
  severity_max: high
  files_touched:
    - .harness/harness/features/FEAT-56-central-onboarding-model/notes/analysis-FEAT-56-rescope-advisor.md
  branch: feat/FEAT-56-central-onboarding-model
  open_questions:
    - { id: Q1, question: "TERMINUS — operator only. Advisor rules (b): ship the delivered central model AS FEAT-56, open a successor for the command split. But the operator's ruling said do not ship and invalidate the current UAT/ship readiness, so (b) is a narrowed brief needing their signature, never a licence to ship around a binding FAIL. Accept a narrowed FEAT-56 shipping nine SCs with SC-09 recorded superseded by operator re-scope, or revise in place — which needs a THIRD cycle-cap raise on 11/11?", blocking: true }
    - { id: Q2, question: "ARTIFACT KIND — operator only, and the premise has EXPIRED, which changes what is being asked. The operator said adding a repository becomes a separate command. Source says onboarding is deliberately NOT one: BUILD.md:377-380, not a command, because commands do not distribute (DEC-06). But that reason is dead — deploy.sh was deleted under DEC-113 and nothing distributes anything now, a fact this very feature depends on. So this is not defying a signed decision to satisfy a word; it is re-taking one whose stated premise is gone. Skill harness-add-repo (conforms; advisor endorses; orchestrator recommends), or a real command file, which is a fresh decision replacing DEC-06 rather than a task.", blocking: true }
    - { id: Q3, question: "DEFECT SCOPE. The undiscoverable command surface predates FEAT-56 — it is a #589 port gap — and it makes /harness, /harness-plan and /harness-ship inert under OMP. Fix inside the re-scope successor, or as its own ticket ahead of it?", blocking: true }
    - { id: Q4, question: "ORPHAN nobody had listed. Cutting init steps 6-8 out of harness-add-repo (DEC-220 supports it) leaves first-BRIEF owned by nobody: .claude/commands/harness.md:12 routes BRIEF.md missing to /harness-init, which the split strips of those steps. Repoint that router to /harness-plan, or keep 6-8 in add-repo?", blocking: false }
    - { id: Q5, question: "HARNESS DEFECT, artifact-destroying, root cause now measured by the orchestrator. check-domain refused EVERY write by harness-validator-lead — the named run dir AND its own granted .harness/notes/analysis-*.md — citing a stale claim on .claude/worktrees/harness/BUG-1309-mirror-build-entry, while inflight_registry.py list from the main checkout reported NO CLAIMS. Cause: REGISTRY_REL is .harness/.inflight-claims.json resolved against a ROOT, so the claim lives in that worktree's own registry and a list run elsewhere cannot see it; list --root against it shows five claims (validator-lead, code-reviewer, qa, security-reviewer, ui-reviewer). Worse, reconcile --root returns RECONCILED 0 on them because every claim carries agent_id=None and job_id=None, leaving no runtime identity to grade liveness against — so the sanctioned automatic route cannot clear an identity-less stale claim and only a blind release remains, which the orchestrator declined because those claims belong to another feature's flow. The next validator dispatch loses its artifact the same way.", blocking: true }
  escalations:
    - { id: E1, raised_by: harness-validator-lead, question: "Q1 and Q2 are operator decisions: the panel cannot choose the terminus against a binding FAIL, nor re-take DEC-06 to satisfy the word command", domain: product, routed_to: main-session, resolution: pending, decided_by: operator, recorded_as: open_questions }
    - { id: E2, raised_by: harness-validator-lead, question: "Stale worktree claim blocks all writes by this persona; the guard and the registry read different stores and reconcile cannot clear identity-less claims", domain: eng, routed_to: orchestrator, resolution: "resolved by escalation, not by clearance — harness-orchestrator transcribed the ruling under its own feature-directory grant; the block is on the persona, not the path", decided_by: harness-orchestrator, recorded_as: open_questions }
  expertise_update: []
  sc_status: []
  adequacy_notes:
    - "ONE reader, no cross-check — a single advisor's ruling is an opinion with citations, not a panel; nothing attempted to falsify it."
    - "Q2's door defect is MEASURED, not doc-only, and the measurement is harness-orchestrator's, not the reader's: .omp/config.yml carries disabledProviders [claude]; .omp/commands/ does not exist; .omp/extensions/harness-hooks.ts registers NO slash command (every command occurrence is the Bash-tool payload); .omp/providers/ holds anthropic.yml and openai.yml. Agent and model neutrality are delivered; the four /harness* doors are not."
    - "The port-commit hash is DISPUTED and unverified by the lead: the advisor reported d35aa81a, the orchestrator's git log on feat/589-omp-provider-neutral gives 184960d1 and finds no d35aa81a. Cite issue #589 — a hash on an unmerged branch is not stable."
    - "A4's cost claim, the bulk of the successor's authoring work, is unpriced judgement; no task breakdown exists, and that is pm's."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-56-central-onboarding-model/.harness/harness/features/FEAT-56-central-onboarding-model/notes/analysis-FEAT-56-rescope-advisor.md
```

# Digest — rescope-advisor-validator — FEAT-56 re-scope ruling

**TRANSCRIBED BY harness-orchestrator, not written by its author.** `harness-validator-lead` ran this
segment and returned a complete four-part ruling, but `check-domain.sh` refused every write by that
persona — this path AND its own granted `.harness/notes/analysis-*.md` — citing a stale claim on
`.claude/worktrees/harness/BUG-1309-mirror-build-entry`. It holds no shell and could not clear it. It
returned `artifact: none` and declined to claim a write the guard refused three times, which is
correct. The content below is its return verbatim in substance; the transcription and the contract
block above are the orchestrator's, and the two defects that made them necessary are recorded at the
foot of this file.

`fable-advisor` **RAN**: it resolved on this host, was not skipped, triggered no `on_fail`, and
returned a well-formed four-entry ruling. The lead dismissed none of its findings, revised none of
its severities, and invented no `PF-` id.

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

## A3 — the name: `harness-add-repo` stands, and the artifact is a SKILL, not a command

All 23 skill directories are `harness-*`, `check-instruction-paths.py:29` hard-requires the prefix,
nothing collides. There is no `harness-init` command anywhere — only prose refs at `harness.md:12`,
`harness-plan.md:18`, `harness-grilling.md:7,12`. `BUILD.md:377-380` states init is a flat skill "not
a command, because commands do not distribute (DEC-06)" — and see Q2: that premise expired with
`deploy.sh`. Files that must change: a new `.claude/skills/harness-add-repo/SKILL.md`;
`harness-init/SKILL.md` cut to Track A plus `--upgrade`; `MAIN_SESSION_ONLY` at
`check-instruction-paths.py:12-16` gains the name; three prose cross-refs; the SC-04 doc set
(`SPEC.md:441-447`, `BUILD.md:377-397`/`:784`, `org.html:286`, `README.md:192`, `.harness/README.md`,
`templates/README.md`); a new DECISIONS entry plus index regeneration; and every verify block anchored
on Track B line content re-anchored. `scope_impact: as_expected`, `severity: med`.

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
   Artifact kind second — it re-takes a signed decision. Defect scope third. The seam last: authoring
   cost, fully reversible.
2. **A4 closes onto a route that does not exist.** The advisor said first-BRIEF "belongs to" the
   router at `harness.md:12`. That line routes `BRIEF.md missing` TO `/harness-init` — the artifact
   the split strips of steps 6-8. Cutting them from both files orphans first-BRIEF unless that router
   is repointed. Nobody had listed that task.
3. **A2's defect is not FEAT-56's.** It predates this feature and belongs to the #589 port; folding it
   in makes the successor look like the operator's request when half of it is unrelated debt.

## Two harness defects this run exposed, both orchestrator-measured

1. **The guard and the registry read different stores.** `inflight_registry.py list` from the main
   checkout reports NO CLAIMS while `check-domain.sh` refuses on a stale claim. `REGISTRY_REL` is
   `.harness/.inflight-claims.json` resolved against a ROOT, so the record lives in the OTHER
   worktree's own registry and a `list` run from the main checkout cannot see it — it reports clear,
   which reads exactly like a cleared claim. `list --root <that worktree>` shows five live claims for
   BUG-1309: validator-lead, code-reviewer, qa, security-reviewer, ui-reviewer.
2. **`reconcile` cannot clear them.** `reconcile --root <that worktree>` returns `RECONCILED 0`
   because every claim carries `agent_id=None, job_id=None`, so there is no runtime identity to test
   for liveness. The sanctioned automatic route therefore cannot clear an identity-less stale claim,
   and the only remaining route is a blind `release` — which the orchestrator declined, because those
   claims belong to ANOTHER feature's flow and clearing another flow's state to unblock this one is
   not this feature's act.

The recovery that did work: the orchestrator holds the feature-directory grant, so it transcribed
this file itself. A validator artifact is recoverable by the tier above; the block is on the persona,
not on the path. And the first landing site was wrong — `runs/**` is gitignored at `.gitignore:7`, so
the transcription would have died with the worktree at merge; this tracked `notes/` path is where it
survives.
