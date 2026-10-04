# Receipt — reuse angle, BUG-1016 plan DRAFT

**Angle result: 3 findings (all advisory, plan-surface, no settled item reopened).** Read-only; no edits.

Finding shape: file · line · summary · cost · alternative · kind.

## R1 — T-01 restates the edit header/MV grammar instead of naming `extractEditPaths`
- file: plan.yaml · T-01 `intent`, paragraph beginning "For edit, rewrite the input string's valid hashline section paths and MV destinations…" (also BRIEF SC-02)
- kind: substance
- Existing: `.omp/extensions/harness-hooks.ts:74-88` `extractEditPaths` already owns the grammar (`^\[path#HHHH\]$` headers, `^MV (.+)$`, trim, `"…"` unquote). `fileDomain` (:300-301) consumes it for pre and post, and the S2 zero-path advisory (:1342) depends on it.
- Cost: the plan lets the implementer spell a second header/MV regex for rewriting. When one drifts (quote handling, CRLF, hash width), the rewriter and the pre/post gate disagree on which paths exist — exactly the SC-02 "same effective destinations" failure, and the stale spelling is the one nobody greps for. The plan's "never rewrite body rows that merely resemble a header or MV" is a property of that single grammar, not a new one.
- Alternative: in T-01 intent, require the edit rewrite to share the header/MV match definition with `extractEditPaths` (extract one pattern/iterator, used by both; or rewrite via the same matches), and state that the existing extraction tests remain the grammar's oracle. Add one assertion: the paths `extractEditPaths` returns for the revised input equal the rewritten effective targets.

## R2 — T-01 re-specifies the scheme test already held as `URI_SCHEME`
- file: plan.yaml · T-01 `intent` relative-predicate paragraph (and BRIEF Constraints "Relative filesystem predicate")
- kind: form
- Existing: `harness-hooks.ts:269` `const URI_SCHEME = /^([A-Za-z][A-Za-z0-9+.-]*):\/\//;` used by `domainTarget` (:273-285). The plan's `[A-Za-z][A-Za-z0-9+.-]*://` is character-for-character the same pattern.
- Cost: two copies of the scheme grammar; if BUG-2003 policy later widens/narrows what is a URI, the rewriter may prefix a string the domain gate considers a URI (or vice versa), turning a refused URI into a "file" and reaching check-domain.py — a fail-open shape.
- Alternative: T-01 should say "scheme test is the existing `URI_SCHEME`" and keep the predicate prose as the contract it must satisfy; the explicit regex in the BRIEF is fine as the observable spec, but the task must forbid a new constant.

## R3 — feature-root answer parsing: a second ad hoc parser beside the one at ~:1298
- file: plan.yaml · T-01 `intent` ("prints one absolute root… empty output, multiple output roots or nonabsolute output, refuse")
- kind: proportionality (scope: task)
- Existing: `harness-hooks.ts:1298-1301` already invokes `inflight_registry.py feature-root --feature --root ctx.cwd` through `policyRunner` and parses `stdout.trim().split("\n").pop()` — a tolerant, last-line parse with no validation.
- Cost: the draft adds a strict validator (one line, absolute) beside the lax one. Two parsers of one CLI contract disagree on multi-line output (new refuses, old takes the last line); the older caller then stays the lax one and silently diverges. The plan says "do not enumerate worktrees in TypeScript" but not "share the invocation".
- Alternative: have T-01 say the new strict resolver helper is the single TypeScript wrapper for `feature-root`, and migrate the ~:1298 call to it (or explicitly record the one-line reason that call is left lax), rather than adding a sibling invocation. If the spend path must keep its non-refusing behavior, require the shared helper to return a result the caller interprets, not two argv spellings.

## Checked, no finding
- T-01 verify (`python3 tests/unit/test-omp-hooks.py`) is the existing runner (tests/unit/test-omp-hooks.py exists); no hand-rolled check.
- T-02 verify uses the existing `gen-decisions-index.py --stdout | diff`; intent says regenerate with the existing generator, no restated procedure.
- Revised-input channel (`revisedInput`, :1065/1221) and `runtimeLineage`/`basePayload` reuse are already named in the plan.
- T-02 intent restates T-01's behavior list by design (it documents it); this is the DEC content, not a procedure another task owns.

```yaml
VERDICT: PASS
DIGEST:
  headline: Reuse review of BUG-1016 draft - 3 advisory findings (edit-grammar and URI_SCHEME restated, feature-root parser duplicated), no settled item reopened
  tests_added: 0
  suite: n/a
  task: none
  blocked_on: none
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/receipt-harness-backend-dev-plan-simplify-eng-reuse.md
```
