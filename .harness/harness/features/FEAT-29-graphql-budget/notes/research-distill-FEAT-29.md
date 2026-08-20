# Distillation — harness-pm — FEAT-29-graphql-budget

**Two of three relayed candidates accepted, both as displacements into full sections; one rejected
because a preloaded rule skill already carries it verbatim in intent.** No repository-tier entry
earned a slot — none of the three turns on a path, file or invariant of this checkout. Gate exit 0.

No observations log exists for this feature, so the raw material was my own artifacts:
`notes/research-goalcheck-FEAT-29.md`, `notes/research-plan-product.md`,
`notes/research-plan-product-c1.md` and the two run digests.

## Candidate 1 — a cost figure recorded without its conditions: REJECTED

The observation is real and well evidenced (`notes/research-plan-product.md:114-127`: a 31-point
figure with no board, no item count, no sha; an out-of-scope exclusion built on it; the correction
records 490-506 with board 3, 473 items, commit `6bbd706`). It is rejected because it is **already a
rule I carry at every spawn**: `harness-spec-driven` states "A recorded baseline carries the sha it
was observed at, and the condition ... A bare number is unfalsifiable and therefore unverifiable."
My own research note names the failure as "the B-12 failure exactly" — i.e. the rule fired
correctly as written, and the defect was in an old record, not in my ruleset. Gotchas is full, so
accepting it would have to kill a rule that nothing else carries in order to restate one that is
already injected. G-06 and G-07 are adjacent but were not the deciding reason; the preloaded rule
was. Not re-litigated.

## Candidate 2 — a verify that reads the working tree: ACCEPTED, displacing G-15

Evidence: `notes/research-goalcheck-FEAT-29.md` SC-09 — `git show 4f2e5d0:CLAUDE.md` carries no such
rule; the deliverable lived only in the operator's uncommitted working tree, and the task's
`verify:` passed because it read the tree rather than the tree under review. That gate would pass
for any task whose deliverable was never committed, and I author those gates.

Displaced G-15 (untracked capture artifacts leave no commit evidence). Same subject — working tree
versus the commit — and the new entry is strictly wider: it fires on every verify I author over a
file the task produces, not only on measurement captures, and its remedy (read the ref) also
detects the missing-capture case G-15 named. Same length, sharper trigger.

## Candidate 3 — a criterion quantifying wider than its task's file list: ACCEPTED, displacing P-11

Evidence: SC-08's absence clause spanned every surviving document; the task traced to it named only
the grilling note, and a shipped brief elsewhere survived carrying the forbidden claim
(`notes/research-goalcheck-FEAT-29.md`, SC-08 section). The criterion failed at goal-check for a
**planning** reason — no execution retry could have satisfied it.

Distinct from P-03 (grading set derived from the artifact under grading) and P-04 (per-item
assertions when grading N items): both are grading-time rules, this one is a plan-time scope
agreement between a criterion and the tasks tracing to it.

Displaced P-11 ("declared evidence names a suite holding no case, yet the state measures as
delivered → grade met, route coverage debt"). P-11 was the weakest entry in the section on three
counts: it fires rarely, it yields a judgement rather than an action, and it points the same
direction as softening a `not_met` — which my role rule explicitly forbids. The replacement fires on
every plan carrying a quantified criterion and is checkable before dispatch.

## Counts and gate

| File | Section | Before | After |
|---|---|---|---|
| `.harness/expertise/harness-pm.md` | Patterns | 15 | 15 |
| | Gotchas | 15 | 15 |
| | Outcomes | 9 | 9 |
| | Open | 0 | 0 |
| `.harness/harness/expertise/harness-pm.md` | all | 0/3/0/0 | unchanged, not written |

`check-expertise.sh .harness/expertise/` → **exit 0**, every file OK, no re-run needed. The one
advisory on my file (`P-01 names '.harness/'`) is pre-existing and unchanged by me; the path there
is an exemplar pointer, which the layer rule keeps in craft.

## Open questions

- **Q1 (non-blocking).** Nothing at plan time compares a criterion's quantified scope against the
  union of `files:` across the tasks tracing to it. `check-plan-routes.py` checks routing and field
  size, not scope agreement, so the new P-11 is a rule with no gate behind it — the same shape the
  criterion-versus-task gap took here. Worth a dev-ops task; not a defect in this feature.
