# BUG-1016 security review — c1

PASS: no introduced exploitable security defect found in rooted destination authority or downstream write policy.

Pin: `8211687fd442258a4ae1a50d8e5375228a51b540`; base: `af2a958ab06c0d6fc026b363b59fc3147e3982f1` (`merge-base(main,pin)`). Pinned `git show`/diff inspected, not HEAD; `8211687f..fe8c50ea` changes only feature.json.

## Scope and evidence

- **T-01, in scope:** `.omp/extensions/harness-hooks.ts:975-1013,1139-1186,1451-1460` consumes governed tool input and selects executed/policy destinations. Held-run readiness and per-mutation authorization precede rewriting; preDomain receives effectiveInput; tool execution receives the same revisedInput; postDomain reroots original inputs idempotently. Resolver argv uses currentFeature and ctx.cwd, never checkout prose/tool input. Errors, refusal reasons, ambiguity and non-single/nonabsolute output refuse; failures are not cached. The cache is closure-local to a fixed PolicyRunner, keyed by runtime id/feature/cwd and cleared at run start/end (`:1031,1486`).
- **T-01, evidence-bearing:** `tests/unit/omp-hooks.test.ts:1279-1551` asserts literal revised destinations, resolver argv/refusal and retry, sibling/run isolation, held-run refusal, rooted forbidden-target refusal pre/post, and allowed-URI/refused-URI/file siblings including MV. Existing `fileDomain` URI classification remains downstream, with every extracted target checked (`harness-hooks.ts:276-345`). Shared EDIT_TARGET extraction/rewrite preserves the previous section/MV recognition and gate ordering (`:76-89,374-379`).
- **T-02, in scope as authority documentation:** SC-07 inspection at pin: `.harness/harness/docs/DECISIONS.md:8013-8089` and `DECISIONS-INDEX.md:237` record seven tools, actual ast_edit paths-array interface, lexical predicate, claim/resolver/cache authority, pre/execution/post agreement, URI restrictions, and host exclusions; production and inspected tests agree on these security boundaries.
- **Remaining changed-file census:** BRIEF/plan define authority; feature.json/STATE, grilling, handoff-plan, observations and all receipt/research/review/rework notes are records, not executable policy, dependency, network or credential changes. Full 32-file pinned diff was swept for credential-shaped material: matches were spend/token-count metadata, not secrets. No new dependency or network request surface.

## Preserved dismissals and limits

Traversal, symlink containment and explicit absolute-path relocation are deliberately not introduced by approved BRIEF/DEC-251; this is lexical checkout selection, not a new sandbox. Existing malformed-edit advisory behavior is retained. ast_edit's omission from mutation authorization/domain gates predates this diff and is explicitly excluded; no new enforcement exemption was added. Fixture reuse F1 is not a security finding. Resolver/cache failures cannot substitute an inferred fallback; cache success is not a substitute for per-call mutation authorization.

Evidence is inspection-only: no tests, builds, linters, formatters or adversarial runtime probes executed by this reader. T-01 receipt's prior execution/mutation/smoke claims were read, not independently reproduced; QA owns final execution. PASS is limited to introduced security defects in the pinned change, not certification of all existing host controls. Findings: none. Open questions: none.

```yaml
VERDICT: PASS
DIGEST:
  headline: Pinned lexical rooting preserves claim authority, resolver refusal and write-policy boundaries.
  in_scope: true
  scope_reason: Governed tool input crosses checkout-selection and pre/post authorization boundaries; documentation and tests describe those controls.
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "T-01 governed assignment/tool input to resolver-selected root", stride: "S,T", mitigated: true }
    - { boundary: "T-01 revised write/edit destinations to pre/post domain policy, including mixed URI targets", stride: "T,E", mitigated: true }
    - { boundary: "T-01 cached root across governed runs and siblings", stride: "T,I", mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/review-harness-security-reviewer-c1.md
```
