# Ship review — FEAT-56, the central onboarding model, revised (issue #206)

**Recommendation: ship, once you have run the UAT.** Eleven of sixteen criteria are met at
`review_sha` `8ff5197f`. One is red by your own signed acceptance and expires at merge. Three are
your hand-tests and are the only thing outstanding. This is the second attempt at this feature: you
rejected the first at the UAT gate and re-scoped it, and what follows is the result.

**No report round was spawned.** Assembled by reading the run digests off disk, per DEC-69. Built
from, all under `.harness/harness/features/FEAT-56-central-onboarding-model/`:
`notes/answers-rescope-2026-09-08.md`, `notes/research-FEAT-56-goalcheck-ship-c2.md`,
`notes/uat-FEAT-56-c2.md`, `notes/qa-FEAT-56-c2.md`, the `notes/review-harness-*-c2.md` set,
`notes/analysis-FEAT-56-rescope-advisor.md`, `notes/research-FEAT-56-init-audit.md`, and the task
run digests under `runs/`. Note that many `runs/` digests could not be written at all — see the
harness defects below — so several segments are recorded by their inline returns and by the commit
messages instead.

## What you asked for, and what you got

You rejected the first attempt because it was Claude-Code-only and because it combined two jobs in
one command. Your four rulings, and their outcomes:

1. **Revise in place.** Done — no successor feature. The advisor recommended splitting; you
   overruled it and the record says so.
2. **A provider-neutral `harness-add-repo` skill.** It exists: 185 lines, three steps, its own
   preflight, and no CLI-only gate.
3. **The OMP command-door port in this same feature.** Done, and this is the substantive fix. The
   four `/harness*` doors were invisible under OMP — `.omp/config.yml` disables the claude discovery
   provider, `.omp/commands/` did not exist, and an unmatched `/…` falls through silently as prompt
   text. `.omp/commands/` is now canonical, `.claude/commands/` is generated, and two gates redden
   if that regresses.
4. **First BRIEF, approval and design out of onboarding.** Done; they route to `/harness-plan`.

You also ruled the CLI 2.1.217 floor removed entirely rather than made conditional, and the dead
`cli_min_version` key struck from all five config sites. Both done, DEC-83 amended to keep its
behavioural record.

## What the gates caught that nobody would have caught by reading

- **The split orphaned an instruction and misplaced it at the same time — twice.** The
  control-plane instantiation sentence, the only one in the tree, was both deleted from
  `harness-init` and dragged into `harness-add-repo`, where it would have told an operator to write
  a file into a product repo. The plan-phase goal-check caught the first; the cycle-1 panel caught a
  second of the same class. Both were plan defects, fixed before any code was written.
- **Two canonical doors delegated back into the generated ones.** `.omp/commands/harness-plan.md`
  and `harness-ship.md` opened by telling the reader to open `.claude/commands/harness.md` — the
  source depending on its own output, which is the exact dependency this feature exists to end.
  Neither gate could see it: one compares bytes, the other checks existence. A human reviewer found
  it.
- **A gate that could not fail.** `--check` built its expected door set from what was on disk, so
  deleting a door and its adapter together produced zero drift and exit 0.
- **A banner naming a path that does not exist.** An operator following it would have run nothing.
- **A test whose assertion could never redden.** The ordering predicate SC-01 rests on had no
  fixture, because the comparison blob had no file to order.

## What this feature still cannot prove

**No runner grades an instruction being FOLLOWED.** Both skills are prose executed by you and by a
model. The suite proves ordered markers, the command strings a test reads, and that the gates stay
green. Whether either procedure actually works rests on your UAT. Three rounds of UAT have already
failed — on ambiguous wording, then on misleading structure, then on wrong scope — so this is not a
formality, and the new script is written to expose a wrong shape rather than a wrong word.

**Nothing observes a live provider resolving a door.** SC-15 is your session; no gate can see a
wrong canonical root, which fails exactly as silently as the bug being fixed.

**One red test, by your own decision.** `test-check-plan-routes.py` fails six cases because this
branch's `.harness/team-config.yaml` differs from the main checkout's after the key removal. You
accepted it as D-14; it expires at merge. I verified the failure set is exactly those six, one file,
one cause, no seventh.

## Budget

Twenty rework cycles of twenty-two, and forty-eight runs against an informational twenty. Both are
high and both earned it: this feature was planned twice, panelled three times and UAT-failed three
times, and every one of those rounds found something. The cycle count is two from the bound, so a
UAT failure leaves room for exactly one fix.

## Proposed backlog

Unstruck rows become issues on acceptance. **Anything not listed dies silently.**

| ID | Nature | What |
|---|---|---|
| C-1 | bug | Single-flight is enforced by agent TYPE across every linked worktree, so any concurrent feature holding `harness-pm`, `harness-product-lead` or `harness-validator-lead` refuses this feature's squad writes mid-run. Hit seven times here and independently by another flow. Structural, not stale-claim debris. |
| C-2 | bug | The claim registry resolves per-root, so `inflight_registry.py list` from the main checkout reports NO CLAIMS while the guard refuses on a claim in another worktree's registry. It reads exactly like a cleared claim. |
| C-3 | bug | A claim is retained while its `supervisor_pid` lives, and that PID is a long-lived supervisor, not the run. A leaked claim can never expire inside that supervisor's lifetime, and `reconcile` correctly returns `RECONCILED 0`. |
| C-4 | bug | `validate-digest.py` has no spelling for "gate failed, acceptance signed". A qa persona reporting `suite: fail` can never return PASS, so an operator-signed acceptance like D-14 is unrepresentable end to end and forces an escalation. |
| C-5 | bug | Subagent returns intermittently arrive as `failed (exit 1)` with "called yield with null data" while a well-formed digest is present. Hit at least eight times; routing on exit status alone would have re-spent each spawn. |
| C-6 | bug | The `read` tool served STALE cached content under an unchanged snapshot tag — 370 lines for a 279-line file — caught only by the edit tool's hash rejection. A silent stale read is how a correct agent writes a wrong edit. |
| C-7 | bug | `xd://report_issue` refused a write when qa tried to file C-6. |
| C-8 | enhancement | `check-plan-routes.py` counts any owner-manifest deviation as a violation, so ANY feature editing `.harness/team-config.yaml` reddens it from every worktree of its branch until merge. Comment-only differences are already tolerated; a key removal is not. |
| C-9 | enhancement | The code-risk grader scores the diff, so a pre-existing grade-1 function is invisible to it. `test-check-omp-port.py:main()` was already grade 1 before this feature and no panel saw it. |
| C-10 | chore | `check-omp-port.py:169`'s hardcoded four-door tuple is now the SOLE independent pin on the door count — measured, not predicted. A routine DRY refactor pointing it at `REQUIRED_DOORS` would retire the last guard with nothing reddening. |
| C-11 | chore | `commands/harness-plan.md:19` says "per the Gate check in step 0" — a self-reference; the real gate is in `commands/harness.md`. |
| C-12 | chore | `BUILD.md:527`'s "Requires CLI ≥ 2.1.217" is a dated verification record that can read as a pin instruction out of context. Assessed and deliberately left twice. |
| C-13 | chore | Roughly twenty `/harness-init` slash-command spellings remain across the corpus, referring to a skill that is not a command. Declared a non-goal here. |
| C-14 | chore | `feat/FEAT-46-decision-standard` carries an unmerged DECISIONS.md renumbered to DEC-548 including its own DEC-221. Ours is correct against the integration branch; merging FEAT-46 faces a wholesale renumbering. |
| C-15 | chore | Nothing schedules the post-merge re-run of `check-plan-routes.py` that D-14's expiry implies. |
| C-16 | enhancement | A plan-phase review has no diff to pin, so a reviewer is forced to bind `reviewed:` to a `base..review_sha` range that does not describe what it read. |
| C-17 | bug | Inverting an authoring direction mid-flight is unguarded. `sync-command-adapters.py --check` reports that an adapter DRIFTED from its canonical file but never which side is stale, so any merge that auto-merges a generated `.claude/commands/*.md` carries another feature's fix into the generated side, and `--apply` then silently reverts it from stale canon. This nearly happened at merge `bb39d5c4`: main's `e5223f10` lowercase station fix — which IS BUG-1507 — landed in the adapter while our canonical copy still carried the capitalised forms. Only the gate's staleness report stopped the revert, and it could not say which side was right. |
| C-18 | bug | `check-state.sh` INV-37's remedy text names `gh-sync.py recover-terminal --yes` for a case it does not fit. That subcommand is main-session-only on the operator's explicit approval and is scoped to an already-merged feature that never opened its mirror. For a feature whose mirror IS open and which has not merged, the correct writer of the `github.build_entry` receipt is `gh-sync.py open`, which is the orchestrator's own and is re-run safe. The printed remedy sends a reader to the wrong command at the wrong tier. |
| C-19 | enhancement | A decision citation's SUBJECT is unverifiable by any gate this repository has. Occurrence counts, index regeneration diffs, uniqueness checks and `check-decision-anchors.py` all verify that a cited id EXISTS; none verifies that it names the RIGHT entry. Four instances of that class passed every one of those gates in a single integration — two in docs and test citations, and two latent in `plan.yaml`'s own `decisions:` trace (D-01 and D-08) which predated the merge and were merely preserved by the renumber. The concrete remedy, proposed by pm: a subject-match check comparing a plan decision's `choice` against the header of the entry its `dec:` field names. This is the row I would promote above the rest. |
