Security re-grade — BUG-1304, panel-c2, pinned `c5869301` (delta since c1's `af5ddd7a`: `e9dbc91d`
plan-docs-only, `c5869301` code+tests). PASS. Cycle 1's HIGH must_fix (Finding 1, registry
release/release-all over Bash) is ruled NON-GATING by the orchestrator (settled, not re-argued
here). Cycle 1's MED advisory (Finding 2, malformed-claim-entry fail-open) is re-derived below and
confirmed unchanged, still non-gating.

## What I measured

**1. `deny_bare()` changes the MESSAGE only, never the decision.** Read the full diff
(`bash-write-guard.sh:655-659` new function; three call sites at the ambiguous-claim, unreadable-
registry, and claim-set-refusal branches of `claim_checkout_guard`, previously `deny(...)`, now
`deny_bare(...)`). Both functions print to stderr and `sys.exit(2)`; `deny_bare` only omits the
"File changes go through the Write tool" tail. Cross-read `check-domain.sh:claim_checkout_guard`
(`:769-816`, untouched by this diff) — it never had that tail for claim refusals in the first
place, so this change actually REMOVES a route-local asymmetry (bash-write-guard.sh's old advice to
"switch to the Write tool" was misleading for a claim refusal, since check-domain.sh's identical
predicate would refuse there too). Ran both integration suites live against the pinned code
(`python3 tests/integration/test-bash-write-guard.py`, `test-check-domain.py`) — 100% PASS, every
one of the 9 refusal-exit-2 assertions per route still fires at exit 2 including all three
`deny_bare` sites, and the new `"Write tool" not in stderr` case (`test-bash-write-guard.py`,
expertise-redirect case) passes. No route now falls through to allow.

**2. `claim_worktrees` split introduces no new fail-open.** `_registry_claim_worktrees` (new,
`harness_boundary.py:252-262`) is a verbatim factoring of the original per-registry-root inner loop:
the `worktree_for_feature` call (and its possible `AmbiguousWorktree` raise) sits inside the new
helper, which is itself invoked *inside* the caller's `try` — but that `try` only catches
`inflight_registry.UnreadableRegistry`, so `AmbiguousWorktree` still propagates unchanged, exactly
as it did pre-split when the claim-processing loop sat outside the try. Traced the accumulation
semantics (per-root `unreadable` set, `if any(inside(...)) return result` before raising) line by
line against the pre-split version — identical order of operations, identical short-circuit on the
first `AmbiguousWorktree`. Ran `tests/unit/test-harness-boundary.py` live — all `bug1304:` cases
pass, including `ambiguous feature worktrees propagate`, `unreadable linked registry refuses`,
`unreadable owner registry also refuses`, `proven destination is allowed with unrelated unreadable
registry`. No new branch returns empty/partial where it previously raised.

**Re-derived, not new: cycle-1 Finding 2 (MED, advisory) is unchanged by this diff.**
`_registry_claim_worktrees` still calls `worktree_for_feature(owner_root, claim.get("feature"))`
with no default; a v2-schema claim entry missing `"feature"` still raises uncaught `AttributeError`
inside `worktree_for_feature`'s `feature_id.startswith(...)`, still uncaught by the narrow
`except inflight_registry.UnreadableRegistry`, still caught only by the callers' generic
`except Exception` → "passing through... failed internally" → **allowed unenforced**. The split
moved this code but did not touch its exception surface. Reachability is unchanged from c1 (requires
a hand-written malformed registry entry bypassing the sanctioned CLI, which always sets `feature`).
Still non-gating under `gates.review: advisory_unless_high`; recorded here so panel c3 (if any) does
not need to re-derive it a third time. This is the one (MED) finding this note reports.

**3. Refusal-string data exposure: no new fields, net reduction.** `claim_set_refusal` (the
function that actually builds the printed text) is byte-unchanged in this diff — cycle 1's Probe 3
assessment (same-persona sibling worktree visibility, advisory-only, pre-accepted DEC-218 residue)
stands untouched. `deny_bare` prints strictly less text than `deny` did (drops the Write-tool advice
paragraph), so this diff's own net effect on stderr content is a reduction, not an addition. No
absolute path, registry content, or cross-feature claim beyond what c1 already assessed is newly
echoed.

**4. Textual-vs-runtime assertion count — confirmed by reading, not by trusting the grep.** Measured
directly: `bug1304_assert_pre_change_allows(` call sites (excluding the `def` line) go from 12→9 in
`test-bash-write-guard.py` and 10→8 in `test-check-domain.py` between `af5ddd7a` and `c5869301`
(`git show <rev>:<path> | grep -c` then subtract the def line). But `_bug1304_bash_main_routes` and
`_bug1304_domain_main_routes` each hoisted 4 (resp. 3) previously-separate call sites into one
`for label, command in cases: ...` loop body — read both loop bodies directly, confirmed each
iteration still calls the assertion once. Runtime call count is therefore unchanged: 8 single sites
+ 4 looped = 12 for bash-write-guard; 7 single sites + 3 looped = 10 for check-domain. This matches
the values T-03/T-05's `-ge 10`/`-ge 12` verify blocks were written against. **Advisory note, not a
finding:** if those verify blocks literally `grep -c` the call-site pattern rather than executing
the suite and counting PASS lines, they now read the reduced textual number (9, 8) against a
threshold tuned for the runtime number (12, 10) and could go red on a check that is not actually
broken — worth confirming T-03/T-05's literal grep target before relying on their gate output,
but the underlying test coverage (verified live above) is intact.

## Threat model

| boundary | stride | mitigated |
|---|---|---|
| bash-write-guard.sh claim refusal message content (deny → deny_bare) | I (n/a — message-only change) | true — same predicate, same exit 2, verified live |
| harness_boundary.claim_worktrees split (ABC refactor) | T (fail-open regression) | true — no new branch, verified live |
| malformed v2 claim entry missing `feature` → AttributeError → generic-except passthrough | T | false — pre-existing, unchanged by this diff, MED/advisory, non-gating (re-derived from c1) |
| refusal string content (claim_set_refusal) | I | true — byte-unchanged from c1's assessed baseline; deny_bare reduces exposure |
| inflight_registry release/release-all over Bash | T,E | n/a — orchestrator ruling: non-gating, not re-argued |

## Settled, not re-litigated

Ruling `RuleBug1304UnreadableConflict` (unreadable-registry-incl.-OSError fail-closed); D-02
ambiguous-claim clause and D-08 identical-refusal-semantics clause (both verified live above, both
routes converge on the same predicate); the Bash-reachable `inflight_registry
release`/`release-all` non-gating ruling; both-route refusal-condition equivalence and
`live_claims` read-only (c1).

```yaml
VERDICT: PASS
DIGEST:
  headline: deny_bare and the claim_worktrees split change message text and code shape only; every refusal decision (exit 2) is unchanged and verified live against both integration suites plus the unit suite - no new fail-open, no new data exposure
  in_scope: true
  scope_reason: "diff is the authorization boundary itself (bash-write-guard.sh, harness_boundary.py, plus their test suites); reviewed both changed source files fully, ran all three affected test files live at the pinned commit"
  severity_max: med
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "bash-write-guard.sh claim refusal message content (deny -> deny_bare)", stride: "I", mitigated: true }
    - { boundary: "harness_boundary.claim_worktrees split (ABC refactor)", stride: "T", mitigated: true }
    - { boundary: "malformed v2 claim entry missing feature -> AttributeError -> generic-except passthrough", stride: "T", mitigated: false }
    - { boundary: "refusal string content (claim_set_refusal)", stride: "I", mitigated: true }
    - { boundary: "inflight_registry release/release-all over Bash", stride: "T,E", mitigated: false }
  open_questions:
    - { id: Q1, question: "T-03/T-05's verify blocks are described as grepping bug1304_assert_pre_change_allows( call-site counts with -ge 10 / -ge 12 thresholds; the ABC split reduced the textual count to 9/8 while the runtime assertion count I measured is unchanged at 12/10 (confirmed by reading both loop bodies). Confirm whether those verify blocks execute the suite and count PASS lines (unaffected) or literally grep source text (would now read red on a non-regression) - this is a QA/verify-clause question, not a security gate.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1304-worktree-relative-path-guard/.harness/harness/features/BUG-1304-worktree-relative-path-guard/notes/review-harness-security-reviewer-c2.md
```
