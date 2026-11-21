# BLOCKED — judgments complete; one accepted merge needs main-session execution

All four members returned PASS on distillation. **Accepted 2, rejected 11; QA's replacement applied, security's replacement staged verbatim but NOT applied.** This lead has no shell/execution tool. Main was asked to execute the merge and final check; the runtime reports Main cannot answer before this blocking child returns. No diff reviewed or product suite run. No review or shipping decision reopened.

## Member decisions and section counts

Counts are **Patterns / Gotchas / Outcomes / Open**. Before → current after; security's proposed replacement also preserves these counts.

| Member | Accepted / rejected | Craft before → after | Repository before → after |
|---|---|---|---|
| QA | 1 / 4 (3 relay + 2 independent judgments) | 15/15/10/1 → 15/15/10/1 | 0/11/0/0 → 0/11/0/0 |
| Code reviewer | 0 / 5 (2 relay + 3 independent) | 15/15/10/0 → 15/15/10/0 | 3/11/0/0 → 3/11/0/0 |
| Security reviewer | 1 / 1 (2 relay) | 15/15/10/0 → 15/15/10/0 | 8/9/1/0 → 8/9/1/0 |
| UI reviewer | 0 / 1 (1 relay) | 15/15/10/0 → 15/15/10/0 | 4/0/0/0 → 4/0/0/0 |
| Lead | 0 accepted; retained rules cover candidates | 15/15/10/0 → 15/15/10/0 | 2/4/0/0 → 2/4/0/0 |

Member reasoning lives in feature `notes/qa-distill-validator.md` and `notes/review-harness-{code-reviewer,security-reviewer,ui-reviewer}-distill.md`. The sourced relay is `candidates.md`; no observation logs existed. PM was not re-dispatched.

## Lead assessment

QA's P-03 replacement earns displacement: neighbouring baseline/pin probes on every caller path catch new regressions that the repaired reproducer cannot. Security's P-11 replacement earns displacement independently: local record refusal may erase another enforcement consumer's usable identity or ownership evidence. These are different actions, not duplicate entries. QA applied its exact op through expertise-merge (`REPLACED P-03`, exit 0); security's exact returned op is preserved in `security-ops.json` for host application. No code/UI ops were proposed.

Code and UI's rejection decisions identify retained rules rather than merely declining work. Lead candidates are covered by craft G-03/G-06/G-10, P-09/P-12 and repository G-03; no displacement is justified. QA/code repeat the already-filed omitted-audit concern (#2223/B-7); deduplicated as an existing owner-routed backlog, not a new open question or Expertise entry. Product's previous 0 accepted/3 rejected judgments remain separate.

## Check evidence and exact remaining prerequisite

QA ran `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/expertise/`: **exit 0; 16 OK files; zero violations; one unchanged advisory** (security G-01 names DEC-100). This validates the current tree after QA's change, NOT the unapplied security proposal. Counts were measured by members; QA independently measured both lead tiers.

A shell-capable main session must execute these two commands; neither was executed by this lead:

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/expertise-merge.py ops --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/expertise/harness-security-reviewer.md --ops /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/runs/distill-validator/security-ops.json
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/expertise/
```

**Open question EXEC-01 (blocking):** can the main session supply the missing merge/check execution receipt? No judgment or operator approval is needed. All children are terminal; checkpoint status is blocked solely on execution capability.

```yaml
VERDICT: BLOCKED
DIGEST:
  headline: 'Distillation judgments complete: 2 accepted, 11 rejected; QA replacement
    applied, security replacement awaits shell-capable main-session execution.'
  team: distill
  steps_run: 4
  cycles_used: 0
  members:
  - step: qa
    persona: harness-qa
    verdict: PASS
    headline: Accepted 1, rejected 4; P-03 replacement applied.
    files_touched:
    - .harness/expertise/harness-qa.md
  - step: code
    persona: harness-code-reviewer
    verdict: PASS
    headline: Accepted 0, rejected 5; retained rules already cover candidates.
    files_touched: []
  - step: security
    persona: harness-security-reviewer
    verdict: PASS
    headline: Accepted 1, rejected 1; verbatim P-11 replacement staged, not applied.
    files_touched: []
  - step: ui
    persona: harness-ui-reviewer
    verdict: PASS
    headline: Accepted 0, rejected 1; measured-scope lessons already covered.
    files_touched: []
  must_fix: []
  files_touched:
  - .harness/expertise/harness-qa.md
  - .harness/harness/features/FEAT-2206-skip-shipped-features/runs/distill-validator/candidates.md
  - .harness/harness/features/FEAT-2206-skip-shipped-features/runs/distill-validator/security-ops.json
  - .harness/harness/features/FEAT-2206-skip-shipped-features/runs/distill-validator/state.yaml
  branch: chore/distill-FEAT-2206-skip-shipped-features
  open_questions:
  - id: EXEC-01
    question: Main must apply security-ops.json through expertise-merge.py and run
      the final directory-wide check. This lead has no execution tool; Main cannot
      answer while its blocking child runs. Exact commands are in the digest artifact.
    blocking: true
  escalations: []
  expertise_update:
  - op: replace
    target: P-03
    section: Patterns
    entry: "WHEN a repair closes a crash reproducer DO diff baseline against the repaired\
      \ tree over neighboring inputs on every caller path, preserved ones included\
      \ \u2014 a repair can regress a sibling path or turn a crash into silent loss\
      \ of usable data, neither visible to the original reproducer."
    why: relay 1 plus independent c3/c4 probes; displaces weaker fixture-comment rule
  - op: replace
    target: P-11
    section: Patterns
    entry: WHEN validation rejects or projects a record DO trace every downstream
      enforcement consumer before calling the result fail-closed; verify omitted fields
      or records cannot erase usable identity or ownership evidence, or make absence
      mean permission.
    why: 'Proposed target: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/expertise/harness-security-reviewer.md.
      Security candidate 2 strengthens the sparse-object rule with whole-record refusal
      coverage. Candidate 1 rejected as redundant with P-02/P-12/P-05/O-05. Exact
      ops and before/projected-after counts are in the artifact.'
  adequacy_notes:
  - Counts ordered Patterns/Gotchas/Outcomes/Open; before equals current after for
    every layer.
  - 'QA craft: 15/15/10/1; repository: 0/11/0/0.'
  - 'Code craft: 15/15/10/0; repository: 3/11/0/0.'
  - 'Security craft: 15/15/10/0; repository: 8/9/1/0. Accepted replacement remains
    unapplied; projected counts are unchanged.'
  - 'UI craft: 15/15/10/0; repository: 4/0/0/0.'
  - 'Lead craft: 15/15/10/0; repository: 2/4/0/0; unchanged.'
  - Only the first expertise_update op is applied. The second is preserved verbatim
    in security-ops.json.
  - 'QA directory check exited 0: 16 OK files, zero violations, one unchanged advisory
    concerning security G-01''s DEC-100 reference. Final post-security-merge check
    remains outstanding.'
  - Repair-boundary probing and downstream refusal tracing are distinct durable lessons;
    both replacements earn displacement.
  - 'Existing omitted-CI-audit concern remains routed through backlog #2223/B-7; no
    duplicate decision request.'
  - PM was not re-dispatched. All four children are terminal. No diff reviewed or
    product suite run.
  sc_status: []
  needs_approval: false
  severity_max: none
  matrix_ok: none
  coverage_gaps: []
  findings: []
  readers: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2206-skip-shipped-features/.harness/harness/features/FEAT-2206-skip-shipped-features/runs/distill-validator/digest.md
```
