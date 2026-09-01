# Distillation receipt — harness-data-engineer — FEAT-45-adversarial-plan-panel

## Material read
- `notes/receipt-harness-data-engineer-simplify-efficiency.md` (my EFFICIENCY angle)
- `notes/receipt-harness-data-engineer-simplify-simplification.md` (my SIMPLIFICATION angle)
- Skimmed cross-cutting: `notes/handoff-build.md`, `notes/handoff-validate.md`,
  `notes/ship-review-2026-08-31.md`, reviewer findings `review-harness-code-reviewer-c0..c4.md`,
  `review-harness-qa-c0..c4.md` — none contained a data-engineer-attributable durable lesson beyond
  what my own two receipts already carried; no additional self-derived candidate found there.
- I wrote no observation log this feature (confirmed absent), so my two receipts are my sole
  primary material, as the dispatch states.

## Candidate rulings

**C1 — ACCEPTED as craft Pattern P-12.** The single-question test ("does the dependent's own
intent/verify read a file the predecessor wrote") is generalizable to any task-DAG planning tool,
not specific to this repo's `plan.yaml` shape. True and useful in a repository never seen.

**C2 — ACCEPTED, split across tiers.** The general lesson — a failed content-read test does not
license dropping an edge without also checking for a shared-file write conflict — is craft
(P-13): true of any DAG regardless of what the "no mutates_repo primitive" mechanism happens to be
in this repo. The repo-specific mechanism itself (plan-level tasks in `plan.yaml` have no
`mutates_repo` field, only team-step YAML does) is repository-tier (G-02 in the repo file): it
turns on an invariant of THIS repo's plan schema and would be false or meaningless elsewhere.
Not stale at HEAD d7f31bb — confirmed by my own receipt's citation of "T-02's own intent, line
~282" at review time; the schema split (plan-level vs. team-step) is a structural property of the
harness plan format, not this feature's content, so it persists past merge.

**C3 — ACCEPTED as craft Pattern P-14.** The distinction (same reader seeing a restatement twice
vs. two independently-dispatched subagents each needing their own copy) is a general review
principle about what counts as duplication, not specific to this repo's team-YAML format.

**Self-derived, from the efficiency receipt's "Repeated work" section — ACCEPTED as craft
Gotcha G-07.** Two tasks running the identical full-suite command in their verify blocks is not
automatically redundant work: each run is that task's own proof its own registration didn't
regress a drift invariant (the KIND-DRIFT boundary DEC-174 exists for). This generalizes beyond
this repo's specific `run-unit-tests.sh` to any CI/verify setup where two independent changes each
re-run a shared full check as their own drift-proof.

**No other self-derived candidates.** Re-scanned the simplification receipt's three doc-duplication
findings and the "explicitly not flagged" INV-32-conjunct reasoning — all already covered by
existing entries (P-09/P-11 for backlog-routing of out-of-scope findings; the INV-32 reasoning is a
one-off instance of applying an existing precedent-check, not a new rule). Not added, to avoid
padding a section that already covers the ground.

## Ops applied (verbatim)

Craft — `.harness/expertise/harness-data-engineer.md`:
```
- P-12: WHEN judging a depends_on edge in a task DAG DO check whether the dependent's own intent or verify block reads a file the predecessor wrote. An edge with no such read is narrative-only; dropping narrative-only edges collapses over-serialized waves into parallel ones.
- P-13: WHEN a depends_on edge fails that content-read test DO still check whether both tasks write the same file or data structure before dropping it — a write-conflict-only edge is genuinely load-bearing even though it looks like a false content dependency.
- P-14: WHEN two independently-dispatched subagents each restate the same instruction DO NOT flag it as duplication — separate dispatches share no context, so each needs its own copy or the rule silently stops applying to one of them. Duplication only applies within one reader's context.
- G-07: WHEN two tasks' verify blocks both run the same full-suite command DO check whether each run proves a different task's own registration didn't break a drift invariant before flagging it as duplicate work — a repeated command can be two independent proofs, not one redundant one.
```
Applied via `expertise-merge.py apply` — output: `ADDED P-12`, `ADDED P-13`, `ADDED P-14`,
`ADDED G-07`, plus `PRESERVED` for all 17 pre-existing entries. Exit 0.

Repository — `.harness/harness/expertise/harness-data-engineer.md`:
```
- G-02: WHEN a plan.yaml depends_on edge fails the content-read test DO check for a shared-file write between the two tasks before dropping it — plan-level tasks have no mutates_repo primitive, so depends_on is the only serialization mechanism for such writes; keep the edge, correct its stated reason.
```
Applied via `expertise-merge.py apply` — output: `ADDED G-02`, `PRESERVED G-01`. Exit 0.

## Section counts

Craft (`.harness/expertise/harness-data-engineer.md`, 150-line budget, 26 lines after):
| Section | Before | After |
|---|---|---|
| Patterns | 11 | 14 |
| Gotchas | 6 | 7 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

Repository (`.harness/harness/expertise/harness-data-engineer.md`, 40-line budget, 7 lines after):
| Section | Before | After |
|---|---|---|
| Patterns | 0 | 0 |
| Gotchas | 1 | 2 |
| Outcomes | 0 | 0 |
| Open | 0 | 0 |

No displacement needed; both files well under budget after these adds.

## Note on merge-tool usage

First `apply` attempt on both files used a YAML `expertise_update:` op-list as `--entries` (matching
the DIGEST schema shown in `harness-distill`) and silently produced zero `ADDED`/only
`PRESERVED` lines with `APPLIED` and exit 0 — the tool parses `--entries` as an Expertise-format
markdown fragment (`## Section` + `- ID: text` lines), not as the ops YAML. Re-ran with the entries
rewritten as markdown fragments under the correct `## Patterns (max 15)` / `## Gotchas (max 15)`
headers; second attempt produced the expected `ADDED` lines. No file was corrupted by the first
attempt — it was a no-op union with the base, not a partial write.
