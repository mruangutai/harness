# BUG-1016 c3 — security review

**PASS: no introduced exploitable security defect found. Assurance is inspection-only.** Reviewed canonical `af2a958ab06c0d6fc026b363b59fc3147e3982f1..ef9cbce243444628d4ca74931be94a576e493dd5`, with base independently obtained by `merge-base(main, pin)`; also inspected `55c99a856321ef9d059b144b6ee2ac2bf1f75096..pin`. No tests, builds, lint, formatters or runtime probes executed; QA owns measurements, including the reported old-adapter mutant result.

## Scope and evidence

- **Full census: 44 changed paths (+2077/-20).** T-01 adapter/tests are in scope for attacker-authored tool input, destination integrity and authorization. T-02 decisions/index and BRIEF/plan/amendment are in scope as destination-authority specifications. Remaining feature state, handoffs, receipts, research/review/rework notes, observations and grilling are records, not new executable gates, dependencies, network requests or exports. Complete-diff credential-pattern search found token-count metadata/prose, not credentials. No new secret logging, SQL/shell/template interpolation, spreadsheet export or SSRF surface identified.
- **T-01, SC-04 / DEC-250:** pinned `.omp/extensions/harness-hooks.ts:20-39,210-243,975-1017,1138-1189` keeps gate binaries module-derived, runtime child/parent claim readiness and mutation authorization ahead of rooting. Resolver argv contains the established feature identity and checkout root, not a dispatch-prose path, environment override or tool-authored destination. Existing `inflight_registry.py:1004-1016` delegates to `harness_boundary.worktree_for_feature:243-279`; ambiguity/nonzero reason, invocation errors and unusable stdout refuse. Successful cache is adapter-local, keyed by runtime id/feature/cwd and reset at run boundaries; it caches roots, not authorization verdicts.
- **T-01, SC-01/02/03/05:** pinned adapter `:76-89,352-405,1178-1189,1455-1462` shares edit recognition between extraction and rewriting, preserves excluded destinations/selectors/body rows, and sends revised inputs to execution and ordinary-file pre/post gates. BUG-2003 classification `:276-322` remains downstream: only `agent://` and exact `xd://report_issue` bypass file-domain checks; refused URI siblings cannot be exempted by an allowed URI. Ordinary rooted files retain existing domain/DEC-250 repository checks; lexical rooting is not a new traversal sandbox.
- **R2 fix, T-01:** `rootTarget:352-368` now inserts at leading-whitespace length plus the opening-wrapper width, not the first matching target substring. Inspection closes the three/four-quote wrapper-placement defect while retaining the operator-approved trim/remove-one-pair predicate. Pinned test additions at `tests/unit/omp-hooks.test.ts:1347-1363` assert literal outputs for both quote-only cases, spaced paths, padded quoting and explicit quoted exclusions. These assertions were inspected, not executed.
- **T-02, SC-07 inspection:** pinned `.harness/harness/docs/DECISIONS.md:8013-8089`, index `:237`, adapter and canonical test diff agree on seven tools, actual `ast_edit.paths`, resolver/cache authority, pre/execution/post destinations, URI policy and silent/main/Bash/Claude boundaries. SC-06 inspection finds no new successful-rewrite notification path.

## Limits and dispositions

The unchanged `ast_edit` mutation-set omission and malformed-edit advisory remain existing surfaces, not fixes promised here. Existing live-host URI normalization/refusal advisory Q1 is outside this pin, not attributed to this adapter. No new blocker or remediation recommendation. Runtime integration, red-first lineage and final gate results require QA evidence; no suite counts are adopted from orchestrator claims.

```yaml
VERDICT: PASS
DIGEST:
  headline: No introduced exploitable destination-authority defect; inspection-only assurance.
  in_scope: true
  scope_reason: Governed tool inputs are rewritten into filesystem destinations before execution and security gates; authority documentation and tests are also changed.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - boundary: Governed tool input to resolver-selected destination; fixed gate binary and feature identity, not caller path prose
      stride: S
      mitigated: true
    - boundary: Revised write/edit destinations to existing domain and exact runtime-lineage authorization checks
      stride: E
      mitigated: true
    - boundary: Mixed edit file and URI targets to BUG-2003 per-target classification before and after execution
      stride: T
      mitigated: true
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-security-reviewer-c3.md
```
