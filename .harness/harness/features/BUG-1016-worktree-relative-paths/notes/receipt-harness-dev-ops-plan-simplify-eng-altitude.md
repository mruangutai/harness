# Receipt — BUG-1016 plan simplify, altitude angle (harness-dev-ops)

**Altitude result: 3 findings (all low-medium, all plan-surface, none blocks signature). Placement is right: the capability belongs in the existing OMP adapter, resolver reuse is correct, no second resolver. The issues are rule duplication and one unnamed residual.**

Read-only; nothing applied. Settled items (grilling Settled/Out of scope, D-01, DEC-174/250, BUG-2003 policy, three resolved panel findings including the permitted cache) not reopened.

## F-1 — edit-path grammar has two authorities (kind: substance)
- File/line: plan.yaml T-01 intent, paragraph "For edit, rewrite the input string's valid hashline section paths and MV destinations…"
- Summary: T-01 specifies a new rewrite of hashline headers and MV destinations but never says it shares the existing grammar in `extractEditPaths` (`.omp/extensions/harness-hooks.ts:74-88`; header regex line 85, MV regex line 86), which pre/post `fileDomain` (line 301) and the zero-path S2 check (line 1342) already use.
- Cost: a second hand-written header/MV parser can disagree with the one the domain gate judges (quoted MV destinations with spaces, CRLF, header-lookalike body rows). The gate would then judge a different path set than the one the host executes, which is the exact SC-02 invariant, and the tests would only catch the shapes they list.
- Alternative: one sentence in T-01 intent: the rewriter reuses or extends the `extractEditPaths` match grammar (one parse, two consumers: extract and rewrite), so extraction of the revised input yields the effective destinations by construction.
- **fold-in**

## F-2 — the same rule set is restated in four places (kind: form)
- File/line: BRIEF.md Constraints (relative predicate, cache bullet) plus SC-01/03/05; plan.yaml T-01 intent (predicate, blank, default-path, cache paragraphs); T-02 intent (re-enumerates predicate, blank/default semantics, cache isolation, resolver authority).
- Summary: BRIEF Constraints already carry one authoritative statement of the predicate, blank preservation and cache bounds. T-01 and T-02 each re-spell them in full.
- Cost: four copies can drift. T-02 is the likeliest: it is authored after T-01 lands and documents "the actual T-01 implementation", so a retuned T-01 predicate leaves T-02's text contradicting it, and the documentor has no tie-break.
- Alternative: T-02 intent says DEC-251 transcribes the BRIEF Constraints predicate/cache/blank rules as landed in T-01 (cite BRIEF constraint names and the T-01 receipt) instead of re-listing them; T-01 intent refers to the BRIEF predicate by name and keeps only test-shaping detail.
- **fold-in**

## F-3 — no-match = silent passthrough is an accepted residual without its compensating control (kind: substance)
- File/line: plan.yaml T-01 intent ("prints ctx.cwd when there is no worktree match. Treat a root equal to ctx.cwd as no rewrite"); BRIEF SC-04 ("No matching worktree leaves input unchanged").
- Summary: a governed run whose feature has no matching worktree (misassigned or removed worktree) proceeds in the parent checkout, which is the BUG-1016 symptom, with no signal. The plan accepts it but does not name what makes that acceptable (e.g. worktree-less features legitimately run in ctx.cwd; existing claim-readiness/lineage gates).
- Cost: a reviewer or the documentor cannot tell whether silent no-match is intended for worktree-less features or an unexamined hole; DEC-251 would record it without rationale. [INFERENCE] The CLI's in-band `ctx.cwd` answer cannot separate "no worktree by design" from "worktree missing".
- Alternative: add one line to BRIEF Constraints (and carry into T-02's DEC text) stating no-match is the expected shape for features without a worktree, that detection of a missing assigned worktree is out of scope and owned by the existing claim/readiness gates. No new behavior or refusal.
- **briefing-row**

## Left alone (checked, correct altitude)
- Adapter-only home, no TypeScript worktree enumeration; resolver reuse via `feature-root`.
- Lexical rewrite with no traversal policy: compensating control named ("Existing write guards still decide destination permission").
- Optional cache: settled; conditional test branches are acceptable.

```yaml
VERDICT: PASS
DIGEST:
  headline: Altitude placement correct; 3 advisory plan-surface findings (edit-grammar authority, restated rules, unnamed no-match residual)
  change_type: infra
  applied: []
  suite: n/a
  task: none
  test_kinds_written: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1016-worktree-relative-paths/.harness/harness/features/BUG-1016-worktree-relative-paths/notes/receipt-harness-dev-ops-plan-simplify-eng-altitude.md
```
