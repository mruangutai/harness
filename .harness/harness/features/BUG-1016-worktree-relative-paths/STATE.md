# STATE

## Current

- feature: BUG-1016-worktree-relative-paths
- run: validate-c2-validator (closed FAIL, 1 cycle; must_fix R2 med substance)
- squad: validator
- status: awaiting_user
- mission: plan
- station: building (board reset from review for the R2 fix)
- verdict: FAIL
- approval: BRIEF approved, plan.yaml approved (2026-10-04, molchairuangutai; rework 2 rounds / 90 min); BRIEF Constraints predicate amended b011c90f per R1 ruling (a), notes/brief-amendment-2026-10-04.md
- T-01: done (main-session-direct, 10f38a42; verify re-run by qa c2 at 55c99a85: 123/0)
- T-02: done (run t02-docs-product PASS, 0 cycles, commit 89b7d960; DEC-251 @ DECISIONS.md:8012)
- simplify: run build-simplify-eng — 8/8 angles PASS, nothing applied; F1 fixture-reuse → backlog (operator ruling)
- validate c1: run validate-validator over 8211687f — FAIL on R1; closed by BRIEF amendment b011c90f
- validate c2: run validate-c2-validator over 55c99a85 — qa/security/ui/goalcheck PASS, code FAIL on R2 (rootTarget `raw.indexOf(target)` places the root before the opening quote when the unquoted target is itself all quotes, e.g. raw `"""` → `<root>/"""`); orchestrator probe reproduces R2 ONLY for all-quote inputs of 3+ chars; every other quote-leading target (`""foo"`, `""x""`, `" foo"`) roots inside the quotes — runs/validate-c2-validator/digest.md, notes/review-harness-code-reviewer-c2.md
- handoff: notes/handoff-build.md seq-6 (build→validate); regate recorded on validate-c2-validator run-start
- github: station building on #1016 #1570 #2016 #2017 #2018
- cycles_used: 3/10; rework_minutes 25/90, rounds 0/2
- review_sha: 55c99a85 (stale once the R2 fix lands; re-pin to the fix seam commit)
- next: main session decides R2 — fix rootTarget main-session-direct (DEC-174): anchor the insertion at the quote boundary (leading whitespace + one `"` when the trimmed raw is quoted) instead of `raw.indexOf(target)`, add literal regressions for `"""` and `""""`, run tests/unit/test-omp-hooks.py (recommended; ~2 lines + 1 test) OR pm records the all-quote filename as out of scope under approval; then re-pin, status review, one validate run over the new sha

## Open Questions

- Q1 (harness defect, non-blocking): governed `write agent://<peer>` and `write xd://report_issue` were refused by check-domain as filesystem paths in product, eng and validator squads this feature (again in validate c2) — BUG-2003's scheme pass-through is not reaching the live hook's domain gate. Harness owner to triage.
- Q2 (blocking, main session): validate c2 must_fix R2 — `rootTarget` (.omp/extensions/harness-hooks.ts:354-361) computes the insertion point with `raw.indexOf(target)`; when the unquoted target consists only of `"` characters the earliest match is the opening wrapper, so raw `"""` (a quoted filename that is one literal `"`) becomes `<root>/"""` instead of `"<root>/""`. Orchestrator probe: repro set is exactly the all-quote inputs; `""foo"`, `""x""`, `"""foo"""`, `" foo"` all root inside the quotes. DEC-174 file: fix main-session-direct with a literal regression, or pm waives the all-quote filename under approval. Recommendation: fix — the insertion offset is derivable from the trim/unquote step itself (leading-whitespace length + 1 when quoted), two lines plus one test, no DEC-251 change needed.
- Q3 (harness defect, non-blocking): a feature.json post-write check in this worktree emitted "OVER BUDGET (already written)" handoff-shape complaints about notes under a different worktree (FEAT-1928-digest-object-contract); the sweep crosses worktree boundaries.
- Q4 (backlog, non-blocking): simplify F1 — rootedHooks fixture duplicates governedUriHooks (tests/unit/omp-hooks.test.ts:1291); operator ruled backlog. qa c2 G1 (no dedicated regression rows for quoted `~`/scheme path-field exclusions) is advisory, same lane.
