# Distill — FEAT-2452 — product squad — distill-product

**PASS.** harness-pm applied 7 ops in 2 `expertise_apply` batches: 6 craft and 1 harness-repository. Every section count is unchanged because each add at a full section displaced a named survivor. Both lead-relayed candidates landed: LC-1 became craft P-18 and LC-2 became craft G-21. The lead applied no ops of its own; none passed the six-spawns test. No git writes, no suite, no diff reviewed.

## Counts (before → after)
| file | Patterns | Gotchas | Outcomes | Open |
|---|---|---|---|---|
| pm craft `.harness/expertise/harness-pm.md` | 15 → 15 | 15 → 15 | 10 → 10 | 0 → 0 |
| pm repo `.harness/harness/expertise/harness-pm.md` | 13 → 13 | 15 → 15 | 1 → 1 | 0 → 0 |
| product-lead craft (no ops) | 15 → 15 | 15 → 15 | 8 → 8 | 0 → 0 |
| product-lead repo (no ops) | 3 → 3 | 0 → 0 | 0 → 0 | 0 → 0 |

## pm ops (verified against the receipt and the resulting files)
- Craft: replace P-16 (it now also covers each kept decision's whole entry), drop P-15 and add P-18 (LC-1), drop G-04 and add G-21 (LC-2), replace O-13 (adds the earlier-failure-point red).
- Repository: replace G-03 (amend does not enforce the 50-line cap; derive file lists from plan.yaml).
- Batches `13417dc3…` and `066c4811…`. Receipt: `notes/expertise-receipt-fd6ae0e7….json`, which has 6 and 1 ops. Grep of the files confirms P-15 and G-04 are gone from craft and P-16, P-18, G-21 and O-13 carry the reported text. Note: `notes/research-FEAT-2452-gh-one-transport-distill.md`.

## Lead assessment
- All six send-back criteria are met (`sendback-criteria.md`, written before dispatch). There was no send-back.
- Candidate sourcing (P-04): both LCs were already in pm's own material. LC-1 matched pm's observation 9 and the c3 goalcheck note. LC-2 matched `notes/research-…-goalcheck-plan.md:99`. I flagged this in the dispatch, so their acceptance measures pm's own lessons more than my relay.
- Reservation, not a send-back (O-03): pm displaced craft G-04 (a runner ignoring a production-only flag). The product lead carries the same lesson as its own craft G-01. pm's call stands.
- Lead's own lessons: none applied. Every candidate from this run (receipt path outside the member's grant, cap-status relay, checking a member's artifacts before relaying) is already covered by my P-10, O-06 and P-04.

```yaml
VERDICT: PASS
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/distill-product/digest.md
DIGEST:
  headline: 'harness-pm applied 7 ops: 6 craft and 1 harness-repo. Both relayed candidates
    landed: per-field payload enumeration as craft P-18 and the durable writer-stdout
    receipt as craft G-21. Every section count is unchanged because each add displaced
    an entry at cap. The lead applied no ops of its own.'
  open_questions: []
  files_touched:
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/expertise/harness-pm.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/notes/research-FEAT-2452-gh-one-transport-distill.md
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/notes/expertise-receipt-fd6ae0e7a80f05243080602934c00a1d5fc25004ac71207359c0a37e44f69c62.json
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/distill-product/state.yaml
  - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/runs/distill-product/sendback-criteria.md
  expertise_update:
  - persona: harness-pm
    op: replace
    target: P-16
    section: Patterns
    entry: 'WHEN a plan deletes or changes behaviour, or every criterion passes, DO
      grade the affirmative present-tense claims in signed prose against measured
      behaviour: the plan''s text and each kept decision''s whole entry, not only
      its policy clause. No criterion quantifies over them, so an overclaim survives
      panels and goal-checks.'
    why: 'Sharpens P-16 to plan time: a ''no decision amendments'' scope collided
      with a kept decision whose present-tense implementation sentence the planned
      deletion falsified; same rule, wider reach, same length.'
  - persona: harness-pm
    op: drop
    target: P-15
    section: Patterns
    why: 'Displaced: byte-for-byte preservation criteria are rare and narrow; the
      external-payload field enumeration rule cost three validate rounds and an operator
      escalation this feature.'
  - persona: harness-pm
    op: add
    target: P-18
    section: Patterns
    entry: WHEN a criterion declares what counts as valid or absent in an external
      payload DO enumerate every field the decision reads, plus the identity binding
      of related objects, in the criterion and again as per-field graded evidence;
      container-shape cases alone let each later round surface one more unvalidated
      field.
    why: Three validate rounds each found the next unvalidated field of one payload
      class; the last fell outside the signed criterion with rework budget spent.
      Goal-check evidence citing only container cases graded met wrongly.
  - persona: harness-pm
    op: drop
    target: G-04
    section: Gotchas
    why: 'Displaced: a runner swallowing a production-only flag is a narrow tooling
      trap; losing a writer receipt forced an operator ruling on the record itself.'
  - persona: harness-pm
    op: add
    target: G-21
    section: Gotchas
    entry: 'WHEN a writer''s stdout is the evidence of what it did DO capture it whole
      into a durable path inside your write grant as it runs: a temp file vanishes
      and printed prefixes truncate, and re-running a writer to recover it records
      a different run.'
    why: Apply step redirected writer stdout to a temp file and printed 300-char prefixes;
      the temp dir vanished, leaving only a truncated receipt the operator had to
      rule on.
  - persona: harness-pm
    op: replace
    target: O-13
    section: Outcomes
    entry: 'WHEN proving a verify is red on the unbuilt tree DO read where the red
      arises, not the status: a missing argument exits 2, a diff over a self-edited
      file is red while uncommitted, and an earlier failure point reddens before the
      one the task names. Each mimics discrimination.'
    why: A fail-first gap was closed by a red from a pre-loop failure rather than
      the per-item failure the signed task named; generalizes O-13's mimic list at
      equal length.
  - persona: harness-pm
    op: replace
    target: G-03
    section: Gotchas
    entry: 'WHEN sizing or amending a task DO count its machine-field lines against
      the 50-line per-task cap first: amend accepts an over-cap task and only plan-merge
      check or check-plan-routes.py fails it, and intent is not counted, so derive
      a long file list inside verify from plan.yaml rather than inlining it.'
    why: An amend adding files and verify lines tipped a task to 53 lines, caught
      only at check; a literal file list in a verify heredoc blew the cap. Sharpens
      G-03 with the amend blind spot and the remedy.
  team: distill (product)
  steps_run: 1
  cycles_used: 0
  members:
  - step: distill-pm
    persona: harness-pm
    verdict: PASS
    headline: Applied 7 ops in 2 batches (craft 6, repo 1). LC-1 became P-18 and LC-2
      became G-21. All sections remain at their pre-run counts. No diff reviewed,
      no suite run, no git writes.
    files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/expertise/harness-pm.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/expertise/harness-pm.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/notes/research-FEAT-2452-gh-one-transport-distill.md
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2452-gh-one-transport/.harness/harness/features/FEAT-2452-gh-one-transport/notes/expertise-receipt-fd6ae0e7a80f05243080602934c00a1d5fc25004ac71207359c0a37e44f69c62.json
  must_fix: []
  branch: none
  escalations: []
  adequacy_notes:
  - "Counts before \u2192 after. pm craft: P 15\u219215, G 15\u219215, O 10\u2192\
    10, Open 0\u21920. pm harness-repo: P 13\u219213, G 15\u219215, O 1\u21921, Open\
    \ 0\u21920. product-lead craft: P 15\u219215, G 15\u219215, O 8\u21928, Open 0\u2192\
    0 (no ops). product-lead harness-repo: P 3\u21923, G 0\u21920, O 0\u21920, Open\
    \ 0\u21920 (no ops)."
  - Verified against the receipt (batch 13417dc3 with 6 ops and batch 066c4811 with
    1 op) and by grepping the resulting files. P-15 and G-04 are gone from craft.
    P-16, P-18, G-21 and O-13 in craft, and G-03 in repo, carry the applied text.
  - 'Relayed 2 candidates, not 3. Both were already in pm''s own material: LC-1 in
    observation 9 and the c3 goalcheck note, LC-2 in notes/research-...-goalcheck-plan.md:99.
    I flagged this in the dispatch, so their acceptance measures pm''s lessons more
    than the relay.'
  - 'Reservation, no send-back: pm dropped craft G-04, the runner that ignores a production-only
    flag. The same lesson survives in product-lead craft G-01. The call is the member''s.'
  - The lead applied no ops of its own. This run's candidates (a receipt path outside
    the member's grant, relaying cap status, checking the member's own artifacts first)
    are already covered by product-lead P-10, O-06 and P-04.
  - 'Distill mission: no diff reviewed, no suite run, no git writes. All six send-back
    criteria in runs/distill-product/sendback-criteria.md are met.'
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: n/a
  coverage_gaps: []
  findings: []
  readers: []
```
