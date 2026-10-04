# BUG-1016 security review — c2

PASS: no introduced exploitable security defect found; the amended predicate agrees with the unchanged adapter.

**Pin/range:** `55c99a856321ef9d059b144b6ee2ac2bf1f75096`, canonical `main...55c99a856321ef9d059b144b6ee2ac2bf1f75096` (merge-base to pin). Pinned show/diff inspected; HEAD not moved. Comparing c1 pin `8211687f` to c2 produces an empty diff for adapter, tests and both decision files. The pinned feature.json retains c1's historical review_sha; this review grades the explicit c2 dispatch pin, not that old record.

## Measured scope and conclusions

Full pinned census: **39 files, +1812/-20**. Seven are security-relevant implementation/evidence/authority: T-01 adapter and tests; T-02 DECISIONS.md/index; BRIEF.md, plan.yaml and amendment note. The other 32 comprise STATE/feature.json, handoffs, receipt/research/review/rework notes, observations and grilling: reviewed as records, not new executable authorization, request, dependency or export surfaces. Credential-shaped sweep of the complete diff found token-count metadata/prose, not credentials. No new dependency or network surface. This boundary also received c1 security inspection; c2 scope was remeasured rather than inherited.

- **Claim/resolver authority (T-01):** `harness-hooks.ts:975-1013,1139-1186` uses currentFeature plus ctx.cwd through the fixed PolicyRunner; gate binaries derive from module location (`:20-39,210-243`). Ready claim and existing write/edit/Bash authorization precede rooting. Dispatch checkout prose, tool input and environment overrides do not supply the rewritten root. Existing CLI `_feature_root_command` delegates to `worktree_for_feature`, refuses ambiguity rather than using the fallback helper, and returns checkout on no match (`inflight_registry.py:1004-1016`; `harness_boundary.py:243-277`). Adapter rejects refusal reasons even when blocked:false, thrown errors and empty/multiple/nonabsolute answers; failures are uncached.
- **Cache isolation (T-01):** closure-local success cache is keyed by runtime id/feature/cwd, bound to its fixed runner, cleared at run start/end (`:981-1002,1031,1486`). Cache hits do not skip readiness or mutation authorization. Tests assert sibling/new-run separation, retry after refusal, no-match preservation and held-run refusal (`omp-hooks.test.ts:1432-1503`).
- **Effective destinations/URI (T-01):** preDomain receives effectiveInput and the host receives that same revisedInput; post reroots original or revised input idempotently (`:1174-1186,1451-1460`). Shared EDIT_TARGET drives extraction and rewrite. Unchanged fileDomain checks every write/edit destination, including ordinary siblings beside allowed URIs; only agent:// and exactly xd://report_issue are URI exceptions (`:276-345`). Literal target and refusal assertions bind both callbacks (`tests:1505-1549`).
- **R1 resolved by amendment, not code:** pinned approved BRIEF Constraints and amendment note explicitly classify after trim and removal of one double-quote pair, preserving original whitespace/quotes on rooting. `rootTarget:353-362` and DEC-251 (`DECISIONS.md:8029-8039`, index `:237`) agree. The former counterexample `"~/notes.md"` is now expressly excluded, so R1 is not reopened.

**Limits:** lexical rooting is not a sandbox; traversal/symlink restrictions and absolute relocation are explicitly out of scope. ast_edit's mutation-set omission and malformed-edit advisory behavior predate this change. Settled SC-06/receipt-shape advisories and fixture reuse do not become security findings. No concrete introduced attacker capability delta identified.

**Evidence:** inspection only; no suites, builds, lint, formatting or runtime probes executed here. Prior `notes/t01-receipts-main-session.md` reports 123/0 adapter tests, seven killed mutations and real-resolver smoke; prior `runs/validate-validator/digest.md` reports QA's 123/0 adapter and 44-file unit gate. These are reused prior execution receipts, not c2 execution claims. QA owns final prescribed verification. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: Amended lexical rooting preserves resolver authority and pre/post write-policy boundaries.
  in_scope: true
  scope_reason: "39-file pinned census includes governed destination rewriting, claim/resolver/cache authority and URI policy; remaining record-only paths add no executable security surface."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "T-01 governed input/assignment to resolver-selected checkout", stride: "S,T", mitigated: true }
    - { boundary: "T-01 effective write/edit targets to pre/post domain and mixed-URI policy", stride: "T,E", mitigated: true }
    - { boundary: "T-01 cached root across governed runs and siblings", stride: "T,I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-security-reviewer-c2.md
```
