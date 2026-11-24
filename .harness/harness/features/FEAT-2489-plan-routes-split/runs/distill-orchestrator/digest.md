# Distill (orchestrator) — FEAT-2489-plan-routes-split

**PASS. Five ops applied to the orchestrator's own Expertise in two batches: four craft, one repository. No member was dispatched, no suite was run and no diff was reviewed.** `cycles_used: 0`.

## Counts, from the tool results

| Tier | Patterns | Gotchas | Outcomes | Open | Batch |
|---|---|---|---|---|---|
| Craft, before → after | 15 → 15 | 15 → 15 | 10 → 10 | 3 → 4 | 14991d42… |
| Repository (harness), before → after | 13 → 13 | 15 → 15 | 3 → 3 | 1 → 1 | d03130ff… |

Receipt: `notes/expertise-receipt-ce5284bb3b67b22d7119b13af411993bed263e502e9909ec732526b7ae8f3457.json`.

## Applied

- **Craft P-04, replaced.** The class-contract rule now covers a contract forwarded for signature as well as a fix brief. It says to state the class by the invariant the work guarantees, with an exhaustive census as evidence, because a class built by enumerating measured mechanisms is still an instance list. Source: the first observation, plus the sign-off, validate-c0 and validate-c1 rulings.
- **Craft G-17, added; craft G-01 dropped to make room.** Run a command that writes state, a hash or a signature alone, after its inputs land. Source: the second observation (two occurrences). G-01 was the weakest Gotcha: repository G-03 carries the same grant check, and each persona now applies its own ops.
- **Craft OQ-05, added.** Whether an upstream merge after a validation PASS needs a re-pin and re-validation. Recorded as open, not as a rule: one delegated ruling answered it for this feature (`notes/answers-2026-11-24-merge-ship.md` Q1).
- **Repository P-13, replaced.** When pm applies remedies and leaves findings open, ask the signer to accept them as applied, never to overrule. Source: the sign-off ruling's lead disagreement with the orchestrator's framing.

## Rejected

- **Committing with a gating check-state row on screen** (third observation, inv32 ruling). One incident, bookkeeping cause. Both Gotchas sections are full and nothing there is weaker; repository P-10 and P-12 already carry the ordering discipline.
- **record-panel replacing `panel.readers` wholesale** (inv32, sign-off Q3). A harness defect, already on the backlog; never Expertise.
- **T-03 verify unsatisfiable by construction** (t03-verify). A drafting lesson for pm; the routing is already O-07.
- **The digest's remedy hint that would have widened a frozen checker** (validate-c0). P-06 covers checking a premise before pricing a fix.
- **Cycle naming drift, c0/c1 against c1/c2** (validate-c1, merge-ship). The rulings key on run id and pin; no rule follows.
- **P-17 and G-16.** No new evidence in this feature; left unchanged.

## Open questions

- OQ-1 (non-blocking, harness owner): no decision rules whether an upstream merge landing after a validate PASS needs a re-pin or re-validation. Craft P-02, read literally, forces the heavier route. The validator distill raised the same question.

```yaml
VERDICT: PASS
DIGEST:
  headline: 'FEAT-2489 is shipped and its orchestrator distill is applied: the class-contract pattern sharpened to cover contracts at signature, one state-writing-verb gotcha added by displacing a duplicated one, one open question added, one repository pattern sharpened, five candidates rejected with reasons.'
  feature: FEAT-2489-plan-routes-split
  status: shipped
  runs:
  - id: distill-orchestrator
    squad: orchestrator
    verdict: PASS
  cycles_used: 0
  briefing: none
  judgement: none
  open_questions:
  - id: OQ-1
    question: 'Harness owner: no decision rules whether an upstream merge landing after a validate PASS needs a re-pin or re-validation; this feature rested on a one-off delegated ruling (notes/answers-2026-11-24-merge-ship.md Q1). Should a decision record it?'
    blocking: false
  files_touched:
  - .harness/expertise/harness-orchestrator.md
  - .harness/harness/expertise/harness-orchestrator.md
  - .harness/harness/features/FEAT-2489-plan-routes-split/notes/expertise-receipt-ce5284bb3b67b22d7119b13af411993bed263e502e9909ec732526b7ae8f3457.json
  expertise_update:
  - persona: harness-orchestrator
    op: replace
    target: P-04
    section: Patterns
    entry: WHEN briefing a fix or forwarding a contract for signature DO state the class by the invariant the work guarantees, with a LEAVE list and an exhaustive census as evidence — a class built by enumerating measured mechanisms is still an instance list and closes one member per round.
    why: A behaviour contract for a verbatim move, worded as identical-except-a-closed-list, took three signer amendments and ended only when anchored on the move's own guarantee with a census as evidence.
  - persona: harness-orchestrator
    op: drop
    target: G-01
    section: Gotchas
    why: 'Displaced by G-17: the repository tier carries the same grant-check rule and each persona now applies its own ops, so the craft copy was the weakest Gotcha.'
  - persona: harness-orchestrator
    op: add
    target: G-17
    section: Gotchas
    entry: WHEN a command writes state, a hash or a signature from files on disk DO run it alone, after the edits and registrations it reads have landed — batched in parallel with its own input it can run first and record the stale input at exit 0.
    why: 'Twice in one feature: a signing verb batched with its input edit re-hashed a signed task, and a lead dispatch raced the run registration it needed.'
  - persona: harness-orchestrator
    op: add
    target: OQ-05
    section: Open
    entry: 'Whether an upstream merge landing after a validation PASS needs a re-pin and re-validation. One ruling kept the pin: the delta decomposed into already-validated upstream code plus a mechanically measured remainder, void on any further code commit. Nothing rules the case generally.'
    why: The re-pin rule presumes rework, not a post-PASS merge; one delegated ruling is a data point, not a rule.
  - persona: harness-orchestrator
    op: replace
    target: P-13
    section: Patterns
    entry: 'WHEN a plan run returns pending DO read every panel finding''s disposition before returning it for signature — pm can apply remedies and leave findings open. Ask the signer to accept them as applied, never to overrule: an overrule records the reviewer wrong about a defect the plan fixed.'
    why: 'Repository tier. The signer refused the framing that open findings with applied remedies needed an overrule; accept-as-applied keeps the ledger consistent.'
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2489-plan-routes-split/.harness/harness/features/FEAT-2489-plan-routes-split/runs/distill-orchestrator/digest.md
```
