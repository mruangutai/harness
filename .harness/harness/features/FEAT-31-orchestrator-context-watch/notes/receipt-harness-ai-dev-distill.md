# Distillation receipt — harness-ai-dev — FEAT-31

**BLUF: accepted both relayed candidates as new craft Patterns (P-04, P-05); own receipt's
findings (F1/F2 correctness, ALTITUDE angle) did not surface a new durable rule beyond what
Candidates A and B already generalise. No stale entry found; no drop/replace.**

## Own material (receipt-harness-ai-dev-simplify-altitude.md)

My prior artifact is the raw finding (F1 fold-in, F2 briefing-row) that Candidates A and B
generalise from the *lead's* disposition of it, not from my finding text directly. I judged the
finding-level content (the specific duplication, the specific docstring lie) too FEAT-local to
distill on its own — the durable rule only emerges once paired with how the apply decision went,
which is what the two relayed candidates supply. So: 0 entries accepted straight from my own
receipt as an independent source; both accepted entries are credited to the relayed candidates
below, though my receipt is the evidentiary basis both cite.

## Candidate A — accepted

Added `P-04` (Patterns): "WHEN flagging duplicated code for a fold-in DO check whether the copies
already diverge in observable behaviour — if they do, file it as a behaviour question naming which
copy is intended, never as a refactor recommendation." Passes the six-spawns test: any future
audit/simplify dispatch over duplicated logic benefits, regardless of repository — the rule turns
on nothing specific to `context-watch.py`.

## Candidate B — accepted

Added `P-05` (Patterns): "WHEN sizing a finding for triage DO state its blast radius and timing —
lines rewritten, whose code path, how late in the pipeline — that sizing is part of the finding,
not only the reviewer's call afterward." Same test passes: sizing discipline for any finding,
any repo.

## Stale-entry check

Re-read all 6 current entries (P-01..P-03, G-01..G-03) against this feature's evidence. None
falsified: P-03 (grep the plan's decisions log before auditing) is consistent with — not
contradicted by — this pass, since ALTITUDE's F1/F2 were fresh findings, not re-litigation of a
signed decision. G-01 (drift-detector probes) and G-02/G-03 are unrelated surfaces. No drop or
replace proposed.

## Section counts

`.harness/expertise/harness-ai-dev.md` (craft, 150-line budget):
- Patterns: 3 → 5
- Gotchas: 3 → 3 (unchanged)
- Outcomes: 0 → 0
- Open: 0 → 0

`.harness/harness/expertise/harness-ai-dev.md` (repository tier, 40-line budget): unchanged,
0 ops applied (no entry from this feature turned on a fact true of only this repo).

## Accepted-entry counts by source

- Own receipt (independent of relayed candidates): 0
- Relayed candidate A: 1 (P-04)
- Relayed candidate B: 1 (P-05)

## Rejections

None. Both relayed candidates accepted as-is (re-worded to the WHEN/DO/50-word entry format;
no feature or task IDs retained per the format rule).

## Worktree staleness guard

Diffed worktree `.harness/expertise/harness-ai-dev.md` and `.harness/harness/expertise/harness-ai-dev.md`
against the main checkout's copies before applying: both identical (`diff` exit 0 on both). No
staleness; safe to apply.

## check-expertise.sh result (verbatim, whole directory)

```
OK   .harness/expertise/harness-ai-dev.md
OK   .harness/expertise/harness-backend-dev.md
ADVISORY .harness/expertise/harness-backend-dev.md:78: G-08 names 'team-config' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-code-reviewer.md
OK   .harness/expertise/harness-data-engineer.md
OK   .harness/expertise/harness-dev-ops.md
ADVISORY .harness/expertise/harness-dev-ops.md:22: G-03 names '.claude/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-documentor.md
OK   .harness/expertise/harness-eng-lead.md
OK   .harness/expertise/harness-orchestrator.md
ADVISORY .harness/expertise/harness-orchestrator.md:85: G-11 names '.claude/' — repository-layer candidate; rule on it (issue 340)
ADVISORY .harness/expertise/harness-orchestrator.md:85: G-11 names 'check-domain.sh' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-pm.md
ADVISORY .harness/expertise/harness-pm.md:4: P-01 names '.harness/' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-product-lead.md
OK   .harness/expertise/harness-qa.md
OK   .harness/expertise/harness-security-reviewer.md
ADVISORY .harness/expertise/harness-security-reviewer.md:66: G-01 names 'DEC-100' — repository-layer candidate; rule on it (issue 340)
OK   .harness/expertise/harness-ui-reviewer.md
OK   .harness/expertise/harness-validator-lead.md
OK   .harness/expertise/harness-visual-designer.md
```

My file (`harness-ai-dev.md`) reports `OK`, no advisory. All ADVISORY lines belong to other
personas' files (`harness-backend-dev`, `harness-dev-ops`, `harness-orchestrator`, `harness-pm`,
`harness-security-reviewer`) — reported here, not fixed, per dispatch scope.
