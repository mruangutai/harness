# Distillation — harness-pm — FEAT-12

**BLUF. Eight ops applied: three Pattern replacements (two displacements, one sharpening), one
Gotcha replacement, four Gotcha adds. Both sections now sit at 15/15. Six of the eight entries come
from my own observations log and notes; two come from the relayed candidates. Four candidates were
rejected — two relayed halves, two of my own — and seven items (four harness defects, three pending
operator rulings) were routed to `open_questions` instead of Expertise, one Q entry each — seven.
Each ruling travels separately because each needs a different operator decision.**
`check-expertise.sh` → `OK`, exit 0. File is 101 lines of the 150 budget.

## Counts

| Section | Before | After | Cap |
|---|---|---|---|
| Patterns | 15 | 15 | 15 |
| Gotchas | 11 | 15 | 15 |
| Outcomes | 0 | 0 | 10 |
| Open | 0 | 0 | 5 |

Patterns was at cap, so two entries entered only by displacing two I judged weaker. Nothing was
merged into a survivor.

## Accepted — from my own observations log and notes (6)

- **P-12 (displaced the shadowed-fixture rule)** — the widest downstream grep is the real survey;
  run it tree-wide at plan time and assign every hit to an owning task. Source: my cycle-1
  observation (a narrow-pathspec task passed green while the wide one failed at the plan's own
  gate) plus the cycle-2 tree-wide re-run that found two unsurveyed sites. This entry also absorbs
  the ordering half of goal-check defect 3 (`depends_on` omitting the task whose files the verify
  greps) in one clause.
- **P-10 (sharpened in place, no displacement)** — widened from "line numbers in an inspection
  criterion" to any location anchor, explicitly including an ordinal such as a test-case number.
  Source: goal-check defect 1, where a signed citation names a case number and the file was
  reordered. The entry is an authoring rule only; it does not encode how the mis-citation is
  disposed of.
- **G-07 (replaced)** — kept the operational half (`git grep` versus `grep -r` in the main tree),
  replaced the implied untrackedness with the measured fact: worktree files are tracked on their own
  branch, and the parent's ignore rules say nothing about the child's index. Source: my cycle-2
  measurement (three of six worktrees, 153 files, all tracked; the main tree's `.gitignore` ignores
  only the container). The unsharpened entry invited exactly the inference that falsified a signed
  BRIEF constraint.
- **G-12 (add)** — a plain YAML scalar carrying a space-then-hash truncates under `safe_load`.
  Durable repo fact plus the authoring action (folded or quoted, then reload and check the tail).
  The "no gate detects it" half was split off to `open_questions`, per the dispatch bound.
- **G-13 (add)** — narrowing a claim in one section requires sweeping the whole artifact in the same
  edit. Source: my own observation of shipping two contradictory statements into one document after
  narrowing a requirement but not the goal. **Deliberately scoped to an artifact you are revising,
  not a signed one** — G-11 governs signed artifacts and says report, do not edit. The two do not
  collide.
- **G-15 (add)** — a criterion graded against working-tree state needs both capture commands and
  their artifacts named in the task. Source: goal-check defect 5, where untracked files left no
  post-hoc evidence and the gap was invisible until goal-check.

## Accepted — from the three relayed observations (2)

- **P-15 (displaced the aggregate-budget rule)** — from relayed candidate 1. A task's `intent:`
  that directs the doer to write a factual claim must have that claim verified at source first. I
  authored the false "only reader" instruction; the member proved it false and refused. The entry
  stays on my authoring duty and does not assert anything about gates.
- **G-14 (add)** — from relayed candidate 2, authoring half only. The absence-by-count shape passes
  when the search itself errors. The entry names the two fixes (assert exit status, or pair with a
  positive control). The shipped-instances half is a harness defect and went to `open_questions`.

## Rejected — with reasons (4)

1. **Relayed candidate 3 — guard posture at the moment a repository becomes fleet-reachable.** Not
   rejected as a decision: "a task granting the factory reach must record guard posture as an
   explicit precondition" is a rule about what my plan records, and it is mine. Rejected on the
   **cap**: Patterns is full, both displacements went to entries that caused defects in signed
   artifacts, and no survivor is weaker than this candidate. It dies as a candidate; the exposure
   itself is in `open_questions` and flagged `security`.
2. **Relayed candidate 2's second half — the false `\b`-is-a-GNU-extension claim I overturned.**
   Rejected as a narrow single-platform tool fact. The generalisation ("verify a handed-down
   portability claim by running it") is not currently stated anywhere in my file, so this is not a
   redundancy rejection — it is that no surviving entry is weaker than either form.
3. **Goal-check defect 3 as a standalone entry** (`depends_on` omitting a task whose files the
   verify greps). Its ordering consequence is carried by the new P-12 clause; a separate entry would
   need a third displacement and no survivor is weaker.
4. **The SC-05 manifest finding as an entry.** The durable authoring rule it implies — name the
   capture command and artifact for working-tree-graded evidence — is G-15. Any entry stating what
   a manifest must contain, or how the shortfall is disposed of, would encode a ruling the operator
   has not made.

## Routed to open_questions, not Expertise

Four harness defects (absence-count shape shipped in four verify strings; no gate detects a
`safe_load`-truncated scalar; nothing gates prose truth; zero guard posture on a newly
fleet-reachable repository) and three pending operator rulings (SC-05 disposition, the case-number
citation, the one-argument `repo_entry` verify). None was written as an entry: a defect ages into a
stale workaround, and a ruling written into a memory log bypasses the signature.
