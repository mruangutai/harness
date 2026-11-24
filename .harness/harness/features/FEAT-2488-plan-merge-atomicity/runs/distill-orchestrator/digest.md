# FEAT-2488 — distill-orchestrator — 4 craft ops applied, 4 candidates rejected

Feature-close distillation of harness-orchestrator's own lessons (DEC-145). No members dispatched, no diff reviewed, no suite run. One `expertise_apply` batch on the craft tier; the repository tier is untouched.

**Batch** `0ae8d5b54ab49344c600bf6da888cb0a87c7c3f7f77dd57519f78d32c972747c` — receipt `../../notes/expertise-receipt-1f0698aa8c22dec95dfa26d5f597fd62d7a22a971c81c9262b1a18c666814c31.json`; destination `.harness/expertise/harness-orchestrator.md`.

## Counts (from the tool's result)

| Tier | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15 | 15 |
| craft | Gotchas | 15 | 15 |
| craft | Outcomes | 10 | 10 |
| craft | Open | 3 | 3 |

Repository tier: no ops applied, so no tool count; the file injected at spawn shows Patterns 13, Gotchas 15, Outcomes 3, Open 1.

## Accepted

- **replace P-04 (Patterns)** — fix briefs state the class contract (invariant plus full state matrix) and a LEAVE list, never the instances reviewers measured. Source: observation 1 and the ship ruling's orchestrator row. A sharpening of the existing rule-over-site-survey entry, not a new row.
- **replace P-17 (Patterns)** — the pre-PR CI-parity run covers each CI interpreter version and diffs the environment against CI's; scrubbing alone leaves variables the interpreter reads. Source: observation 3 and the CI-fixture ruling's adjacent note.
- **add G-16 (Gotchas)** — before dispatching a final rework round, check its terminal condition defines each class by contract, rules non-member findings, and prescribes descope only where it remedies. Source: observation 2 and fable-advisor's P1. Accepted into my file because I carry the condition into the fix and validate dispatches and route the final return; the check costs one question and its absence cost an escalation.
- **drop G-08 (Gotchas)** — displaced to make room for G-16. The repository-tier G-08 carries the same guard workaround, and the guard belongs to one repository.

## Rejected

- **fable-advisor P2 (adjacency sweep one boundary beyond the contract)** — the sweep is done by the builder and the verifying readers, not by me; the validator distill run records it applied in those personas' files (`../distill-validator/state.yaml`). My share is the class-contract brief, which the P-04 replace already carries. A second row would merge a doer's rule into a dispatcher's file.
- **Ship ruling: reader highs by name with the lead's reconciliation alongside** — confirms practice the repository-tier P-04 already holds (read the per-reviewer severity split); no behaviour changes. The reconciliation itself is the validator lead's. The ruling's "G-06" names no entry of mine with that meaning.
- **Observation 4 (bare `env A=1; cmd` runs nothing)** — general shell knowledge, not a lesson about how I orchestrate; every section is full and nothing held is weaker. The masking half (a failure hidden behind filtered output) is covered by the repository-tier P-01.
- **Plan-run digest (scope loop spent with repairs unread; mechanism over-specified)** — the lesson belongs to pm and the product lead; my part, reading every panel disposition before returning a pending plan, is the repository-tier P-13.

## Open

None.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2488 is shipped and its orchestrator distill is applied: two craft patterns sharpened, one final-round gotcha added by displacing a duplicated one, four candidates rejected with reasons.'
  feature: FEAT-2488-plan-merge-atomicity
  status: shipped
  runs:
  - id: distill-orchestrator
    squad: orchestrator
    verdict: PASS
  cycles_used: 0
  briefing: none
  judgement: none
  open_questions: []
  files_touched:
  - .harness/expertise/harness-orchestrator.md
  - .harness/harness/features/FEAT-2488-plan-merge-atomicity/notes/expertise-receipt-1f0698aa8c22dec95dfa26d5f597fd62d7a22a971c81c9262b1a18c666814c31.json
  expertise_update:
  - persona: harness-orchestrator
    op: replace
    target: P-04
    section: Patterns
    entry: WHEN dispatching a fix DO brief the class contract — the invariant and its full state matrix — plus an explicit LEAVE list, never the instances reviewers measured. An instance brief closes one member per round; the LEAVE list stops a member re-judging what is already settled.
    why: Four rework rounds each closed only the measured instance; the cascade ended when the brief stated each class's contract and state matrix.
  - persona: harness-orchestrator
    op: replace
    target: P-17
    section: Patterns
    entry: WHEN validation has passed and a pull request is next DO run every CI step in a fresh clone on each CI interpreter version, diffing the environment against CI's — the validate matrix is not the CI step list, and scrubbing leaves variables the interpreter itself reads.
    why: 'A scrubbed parity run still missed a CI failure: the host set colour variables one interpreter version consults, and only one version was run.'
  - persona: harness-orchestrator
    op: drop
    target: G-08
    section: Gotchas
    why: 'Displaced by G-16: the repository-tier G-08 carries the same guard workaround, so the craft copy was the weakest Gotcha.'
  - persona: harness-orchestrator
    op: add
    target: G-16
    section: Gotchas
    entry: WHEN a ruling grants a final rework round DO check before dispatching that its terminal condition defines each class by contract, rules where findings outside those classes go, and prescribes descope only where descope remedies the class — a silent condition turns every non-member finding into another escalation.
    why: A final round's condition was silent on non-member findings, so two mediums forced a further escalation and the prescribed descope remedied neither.
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2488-plan-merge-atomicity/.harness/harness/features/FEAT-2488-plan-merge-atomicity/runs/distill-orchestrator/digest.md
```
