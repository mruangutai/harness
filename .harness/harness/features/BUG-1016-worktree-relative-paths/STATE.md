# STATE

## Current

- feature: BUG-1016-worktree-relative-paths
- run: validate-validator (closed FAIL, 1 cycle; must_fix R1 med substance)
- squad: validator
- status: awaiting_user
- mission: plan
- station: building (board reset from review for the R1 fix)
- verdict: FAIL
- approval: BRIEF approved, plan.yaml approved (2026-10-04, molchairuangutai; rework 2 rounds / 90 min)
- T-01: done (main-session-direct, 10f38a42; verify re-run by orchestrator at c2d4d7b6: 123/0)
- T-02: done (run t02-docs-product PASS, 0 cycles, commit 89b7d960; DEC-251 @ DECISIONS.md:8012)
- simplify: run build-simplify-eng — 8/8 angles PASS, nothing applied; lead FAIL on false premise (own run-start in feature.json), 1 cycle charged; F1 fixture-reuse flag-only
- validate: run validate-validator over 8211687f — qa/code/security/ui/goalcheck all PASS individually; lead FAIL on R1 (rootTarget trims/unquotes before classification vs BRIEF Constraints exact raw predicate; SC-01/SC-07) — notes/review-harness-code-reviewer-c1.md, runs/validate-validator/digest.md
- handoff: notes/handoff-build.md seq-6 (build→validate); succession continue + regate recorded on validate-validator run-start
- github: station building on #1016 #1570 #2016 #2017 #2018
- cycles_used: 2/10; rework_minutes 13/90, rounds 0/2
- review_sha: 8211687f (stale once the R1 fix lands; re-pin to the fix seam commit)
- next: main session decides R1 — amend BRIEF Constraints predicate to classify after trim + one surrounding quote pair (recommended; DEC-251 and tests already describe that behaviour) OR fix rootTarget main-session-direct (DEC-174) + test + DEC-251 edit; then re-pin, status review, one validate run over the new sha

## Open Questions

- Q1 (harness defect, non-blocking): governed `write agent://<peer>` and `write xd://report_issue` were refused by check-domain as filesystem paths in product, eng and validator squads this feature — BUG-2003's scheme pass-through is not reaching the live hook's domain gate. Harness owner to triage.
- Q2 (blocking, main session): validate must_fix R1 — code and DEC-251 classify a target after trimming whitespace and stripping one surrounding `"` pair; BRIEF Constraints "Relative filesystem predicate" classifies the raw entry. Counterexample: read path `"~/notes.md"` (literal quotes) is relative under the BRIEF (first char is `"`) but the adapter leaves it unrooted. Either amend the approved predicate (pm, under approval) or change `rootTarget` (.omp/extensions/harness-hooks.ts:354) main-session-direct with a discriminating test and a DEC-251 edit. Recommendation: amend — rooting a quoted `~`/absolute path yields `<root>/"~/notes.md"`, which is worse, and SC-02 already requires unquoting MV destinations.
- Q3 (harness defect, non-blocking): a feature.json post-write check in this worktree emitted "OVER BUDGET (already written)" handoff-shape complaints about notes under a different worktree (FEAT-1928-digest-object-contract); the sweep crosses worktree boundaries.
