# Distillation — harness-pm — BUG-1286

**Two entries applied, both repository-tier. Three craft entries were accepted on merit and then
DIED at the tool boundary: every craft section is at cap, and `expertise-merge.py apply` — the only
sanctioned write route — cannot express a displacement.** Measured, not argued: a proposal
re-stating an existing id with new text exits **7 CONFLICT** (nothing applied); a proposal adding a
new id to a full section exits **8 CAP EXCEEDED** (nothing applied). Condensing, the exit-8 remedy,
is itself a replace, so it exits 7. The craft file is therefore frozen (`git diff` empty, md5
`58ece55f…`). That is Q1, and it is a harness defect, not a shortage of candidates:
`check-expertise.sh:20` names displacement as the intended operation.

## Applied — repository tier (`.harness/harness/expertise/harness-pm.md`, 26 → 28 lines of 40)

| id | one-question: true in a repo I have never seen? | why |
|---|---|---|
| **P-07** (add) | **No** — turns on `plan-merge.py`'s own bootstrap branch | `apply` with an absent base DOES bootstrap (`plan-merge.py:602-630`): it refuses only a proposal that itself carries an `approval` mapping, then splices `status: pending` after `feature:`. Verified at source. |
| **O-01** (add) | **No** — turns on `HARNESS_AGENT_TYPE` and this repo's plan-merge refusal | A pm-typed shell makes `tests/integration/test-plan-merge.py` return 10 FAILs; unset, the suite is 291/291 exit 0. Filed under **Outcomes** because Gotchas is at cap and unexpressible; Outcomes here already holds evidence-production rules. |

**Live `G-07` in that file is now FALSE** ("write a new plan.yaml directly … apply refuses with
exit 8"). The correct rule went in as P-07 beside it because a replace exits 7. A curation pass
should drop G-07; it is injected at every spawn until then. Part of Q1.

## Candidates — every one judged

| # | source | verdict |
|---|---|---|
| 1 | relayed — `behaviour wrong` vs `unproven only` | **ACCEPTED, craft, blocked.** P-06 today is two-way (code vs sentence); the run needed three — SC-12's property was FALSE (a note's SHA not an ancestor of `review_sha`), SC-16's was TRUE but unasserted. The two route different one-line remedies and only the third escalates. Proposed as a same-length sharpening of P-06; **displaces nothing**, so its death is purely mechanical. |
| 2a | relayed — stale BRIEF line pins | **ACCEPTED, craft, blocked.** New G-11: re-resolve a cited construct by search at every new pin; a moved anchor is a documentation defect that changes no verdict, an absent construct is a real miss. Displacement target named: **G-11 (wall-time headroom)** — an environment-tuning heuristic whose failure is loud and self-diagnosing, over a rule that decides verdicts on any criterion carrying a line anchor. |
| 2b | relayed — re-derive rather than carry forward | **REJECTED.** Covered: G-07 (evidence produced before the graded commit must be re-run at it) plus G-09 (a remedy commit falsifies met verdicts). Nothing here is sharper. |
| 3 | relayed — contradicting the orchestrator's `check-state.sh` exit status | **REJECTED.** G-06 already prescribes exactly what I did — reproduce the recorded invocation before calling it drift. I reproduced twice, ~75s each, and the single VIOLATION was a gitignored run artifact. My contradiction was an instance of the live rule, not evidence for a new one. |
| 4 | self-derived — SC-16 clause 2 | **ACCEPTED, craft, blocked.** Read the asserting test's SEARCH SCOPE, not only its assertion: the nearest test counted `suite_layout` lines inside one file and was blind to a second caller anywhere else. Distinct from P-04 (which is about enumerating items, not about the scope a search covers). Displacement target named: **P-15 (generated-artifact derived-vs-copied fields)**, the narrowest live Pattern — it needs a generated artifact AND a copied field AND a hand-edit ban to fire. |
| 5 | self-derived | applied as repo **P-07** above. |
| 6 | self-derived | applied as repo **O-01** above. |

Rejected without a row, for the record: the panel/`set-panel` mechanics, the `amend --show` sha
chaining and the wrap-corruption repairs recur across the log but are recipes against one tool's
current surface — pointers, not rules, and they rot with the CLI.

## Open questions

- **Q1 — `expertise-merge.py apply` cannot displace.** Union-only by construction
  (`expertise-merge.py:130-138`). At cap, a distiller has no legal write. Either the tool needs a
  replace/drop verb keyed to an existing id, or the distillation contract must stop instructing
  displacement. Three accepted craft rules are stranded in this note today; repo G-07 stays false.
- **Q2 — the unit/integration suite is not hermetic against the caller's agent identity** (carried
  from the c2 goal-check). `HARNESS_AGENT_TYPE=harness-pm` turns a green run into 10 FAILs that read
  as a regression.

Verification: `check-expertise.sh` exit **0** on both files (craft carries its pre-existing P-01
advisory, unchanged by me). Nothing committed, nothing staged, no worktree touched.
