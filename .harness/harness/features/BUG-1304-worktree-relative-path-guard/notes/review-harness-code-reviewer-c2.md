# Code Review — BUG-1304 worktree-relative-path-guard — panel-c2 (re-grade) — pinned `c5869301`

## Headline

Both cycle-1 gating findings are CLOSED, verified at source against `c5869301`, not from the fix
report. F-01 (REQ-06/D-08 vocabulary mismatch, found by ui-reviewer) is closed: `deny_bare()` now
carries all three claim refusals on the Bash route and the two routes' operator text matches
byte-for-byte modulo the route-name prefix. F-02 (four HIGH code-grade records, found by
code-reviewer at cycle 1) is closed: re-run at the pin, zero HIGH, exit 0. The four splits that
produced this (JOB 2) were audited pairwise against `af5ddd7a` and preserve every prior assertion
verbatim — two of them are strictly TIGHTENED (a `contains` argument added), one gains a new
assertion, none is weakened or dropped. `code_grade: grade_2` — five grade-2 records remain (none
were among the four cycle-1 HIGH records; per `harness-code-risk-grading`, grade-2 never blocks the
build, but its presence means the correct enum value is `grade_2`, not `pass`).

## JOB 1 — F-01 and F-02, verified at source

### F-01 (REQ-06/D-08 spec violation) — CLOSED

Diffed `af5ddd7a..c5869301` for `bash-write-guard.sh` directly (`git show <sha>:<path>`, not
working tree).

- **(a) `deny_bare()` exists, no Write-tool advice.** `bash-write-guard.sh:655-659` (at c5869301):
  ```
  def deny_bare(reason):
      print(f"bash-write-guard: BLOCKED — {reason}", file=sys.stderr)
      sys.exit(2)
  ```
  One line, no second `print`. Confirmed by reading the full file body at the pin, not the diff
  alone.
- **(b) all three claim-refusal sites route through it**, enumerated by line at c5869301:
  1. `:744` — `except harness_boundary.AmbiguousWorktree as exc: deny_bare(f"{agent} has an
     ambiguous worktree claim: {exc}")`
  2. `:750` — `except ... UnreadableRegistry: deny_bare(harness_boundary.claim_set_refusal(agent,
     [], destination, unreadable_paths=exc.paths))`
  3. `:764` — normal mismatch: `deny_bare(harness_boundary.claim_set_refusal(agent, claim_set,
     destination))`
- **(c) no other refusal path reaches a claim refusal through `deny()`.** Grepped every `deny(`
  call site in the file at c5869301 (9 total): the READ-ONLY-reviewer check (`:662`),
  `feature_checkout_guard`'s two sites (`:723`, `:726` — a pre-existing, different check: main-
  checkout feature-artifact misplacement, not this feature's claim-set rule), the run
  digest/state.yaml guard (`:804`), the two out-of-place/wrong-checkout worktree-pointer denials
  (`:843`, `:850`, `:864` — pre-existing D-03 logic), and the final domain deny (`:902`). None of
  these is one of the three claim-refusal sites; all three claim sites use `deny_bare`.
- **(d) both routes' vocabulary now MATCHES.** Read `check-domain.sh`'s three call sites at
  c5869301 (`:761-816`, unchanged since af5ddd7a — not in this diff's file list): each prints
  `"check-domain: BLOCKED — " + harness_boundary.claim_set_refusal(...)` (or the ambiguous/
  unreadable variants) then `sys.exit(2)`, no second line. `bash-write-guard.sh`'s three sites now
  print `f"bash-write-guard: BLOCKED — {reason}"` where `reason` is the identical
  `claim_set_refusal()` text, then exit 2, no second line. The only difference remaining is the
  route-name prefix (`check-domain:` vs `bash-write-guard:`), which is pre-existing and expected.
  This is exactly the property D-08's amended clause pins ("the same exit 2 and the same
  claim_set_refusal text, with no route-local additions") — read at `plan.yaml:490`.
- The new Bash test at `test-bash-write-guard.py:_bug1304_bash_expertise` directly pins this:
  `("expertise refusal never suggests the unavailable Write route", "Write tool" not in
  response.stderr, ...)`.

**F-01 CLOSED.**

### F-02 (code-grade) — CLOSED

Ran the grader myself against the range the repository derives, not `HEAD`:

```
git merge-base origin/main c5869301   ->  6e95435a585f85136ed17fd6835369e30b784583
python3 .claude/skills/harness/bin/code-grade.py \
  --base 6e95435a585f85136ed17fd6835369e30b784583 --head c5869301
```
Exit code: **0**. Zero `RESULT: FAIL` at `SEVERITY: high` (i.e. zero grade-1-anywhere or
grade-3-in-production records). The four cycle-1 blocking records are gone: `claim_worktrees`
split into `_registry_claim_worktrees` (grade 5) + `claim_worktrees` (grade 4, bar 4); both
`run_bug1304_claim_set` mega-functions now grade 4 (bar 3); `case_bug1304_claim_set` (unit) now
grade 5 (bar 3, its body is now nine one-line delegating calls).

Five MED (grade-2, non-blocking, `REASON REQUIRED` but does not fail the build) records remain,
listed by name only, per `gates.review: advisory_unless_high` — backlog, not mine to gate on:
`inflight_registry.py:290 live_claims`, `inflight_registry.py:592 reconcile.mutator`,
`test-bash-write-guard.py:1301 main`, `test-inflight-registry.py:1091
case_36_live_claims_read_only_and_binding_horizon`, `test-inflight-registry.py:1176
case_bug1304_retention`. Per `harness-code-risk-grading`, their presence means the mechanical
`code_grade` value for this range is `grade_2`, not `pass` — none of them is a build-blocking
record and none was among the four cycle-1 HIGH findings.

**F-02 CLOSED** (all four HIGH records are gone). **`code_grade: grade_2`** (mechanical result,
independently re-derivable; not itself the review verdict per `harness-code-review` — grade-2
never blocks the build).

## JOB 2 — the four splits, audited for weakened or dropped assertions

Diffed each split's file `af5ddd7a..c5869301` directly and read both sides in full (not sampled).

### `claim_worktrees` (harness_boundary.py) — behavior-preserving, confirmed by direct comparison

Old body: one `for registry_root in roots` loop with `try: claims = inflight_registry.live_claims(...)
except UnreadableRegistry: unreadable.update(...); continue` then an inner `for claim in claims:
worktree = worktree_for_feature(...); if worktree is not None: claim_set.add(worktree)`.

New body: the inner loop is hoisted into `_registry_claim_worktrees(owner_root, registry_root,
agent_type)`, called as `claim_set.update(_registry_claim_worktrees(...))` inside the SAME
try/except UnreadableRegistry at the call site. Exception semantics are identical: `UnreadableRegistry`
raised from `live_claims` (now inside the helper) is still caught only at the `claim_worktrees` call
site, and `AmbiguousWorktree` raised from `worktree_for_feature` (also inside the helper, uncaught
there) still propagates all the way out of `claim_worktrees` uncaught, exactly as before — neither
version's try/except catches it. Per-registry continuation on `UnreadableRegistry` is unaffected
(implicit loop continuation either way). The three properties JOB 2 asks me to pin, each unaffected
by this split because none of the touched code is on their path:
1. **Raises `UnreadableRegistry` naming the file** — `if unreadable: raise
   inflight_registry.UnreadableRegistry(unreadable)` at the tail of `claim_worktrees` is untouched,
   byte-identical at both shas.
2. **Refuses ambiguous resolution rather than guessing** — raised inside `worktree_for_feature`,
   a function this diff does not touch at all (confirmed: no diff hunk touches it).
3. **Contributes nothing to S for a feature with no linked worktree** — `if worktree is not None:
   result.add(worktree)` inside the new helper is the same guard, same placement, as the old
   `if worktree is not None: claim_set.add(worktree)`.

### The three test mega-functions — every prior assertion present, none weakened

Read `bug1304_assert_pre_change_allows` in full at c5869301 in both integration files. Both still
assert all three SC-06 predicates in one boolean expression:
`allowed.returncode == 0 and quiet and control.returncode == 2` (check-domain.py:4457, `quiet =
not any(marker in stderr for marker in ("enforcement OFF", "was not enforced", "passing
through"))`), and `allowed.returncode == 0 and not any(marker in stderr for marker in (same three))
and control.returncode == 2` (bash-write-guard.py:1004-1010) — same three literals, same three-way
AND, in both files, unchanged from af5ddd7a (I diffed this specific function; it has zero net
change in either file — only call sites around it moved).

**Textual-vs-runtime split, verified by direct read, not by the grep the task warns against:**
- `test-check-domain.py`: `_bug1304_domain_main_routes` now loops `for label, destination in
  cases:` over 3 tuples (relative/absolute/sibling), each iteration calling
  `bug1304_assert_pre_change_allows` once — 3 runtime calls from 1 textual call site. The other 7
  cases (owner-claim, multi-and-malformed, ambiguous, short-claim, aged-claim, unreadable,
  partial-registry) are still one call site each. Total: 8 textual, 10 runtime. Matches the shared
  context exactly.
- `test-bash-write-guard.py`: `_bug1304_bash_main_routes` loops over 4 tuples (relative/in-place
  sed/absolute/sibling), 4 runtime calls from 1 textual site; the other 8 cases (owner-claim,
  multi-and-malformed, ambiguous, short-claim, expertise, aged-claim, unreadable,
  partial-registry) are one call site each. Total: 9 textual, 12 runtime. Matches.
- All 10 and all 12 original cases are traceable one-to-one into the split (I matched every case
  name string — e.g. `"relative main"`, `"sibling"`, `"owner-root matching claim"`,
  `"ambiguous claim"`, `"short-form"`, `"aged claim"`, `"unreadable registry"`, `"partial
  unreadable"`, `"expertise redirect"` (bash only) — none renamed, none dropped, none merged with
  another).
- `test-harness-boundary.py`'s `case_bug1304_claim_set` (unit) is now a 7-line dispatcher calling
  `case_bug1304_short_claim`, `_owner_claim`, `_unresolved_and_empty_claims`, `_multiple_claims`,
  `_ambiguous_claim`, `_unreadable_claims`, `_refusal_text` in the SAME order as the original
  monolith's `check(...)` calls appeared; every `check(...)` call and its condition is byte-
  identical, just re-indented into its own function. `main()` calls `run_case(case_bug1304_claim_set)`
  explicitly (not reflection over `case_*` names), so the sub-functions are not independently
  discovered and run only once, via the dispatcher — no double-execution risk.

### The two malformed-pointer cases — TIGHTENED, not replaced

`test-check-domain.py`: at af5ddd7a, `expect("malformed checkout pointer refuses with a nonempty
claim set", os.path.join(malformed, ...), 2)` — no third positional (`contains=None`). At c5869301,
`_bug1304_domain_expect(..., destination, 2, context["first"])` — `contains=context["first"]` is
ADDED. Confirmed by direct diff hunk: the old line has 3 positional args (name, dest, want); the new
call has 4 (…, want, contains). Same for `test-bash-write-guard.py`'s
`_bug1304_bash_multi_and_malformed`: af5ddd7a's `expect(..., malformed_cmd, 2)` (no contains) vs
c5869301's `_bug1304_bash_expect(..., command, 2, context["first"])`. Both are a strict superset of
the prior assertion (exit==2 still required; presence of the held worktree name in output is a
new, additional requirement) — a TIGHTENING, confirmed.

**JOB 2: no dropped or weakened assertion found in any of the four splits. All four confirmed
behavior- and assertion-preserving by direct byte-level comparison, not by trusting the green
suite.**

## Not re-litigated (per dispatch)

Both-route refusal-condition-set equivalence, `live_claims` read-only, no new reachable fail-open —
cycle 1's conclusions on these stand, unaffected by this diff (the touched lines do not sit on any
of those paths). The ui-reviewer's separate cycle-1 HIGH finding (ambiguous-claim branch never
prints `destination`) is OUT OF SCOPE for this dispatch (my two jobs are F-01/F-02 only); noted for
the record rather than silently passed over: D-02's new clause (`plan.yaml:459-462`, landed
`e9dbc91d`) states the ambiguous-claim refusal need only name "the candidate worktrees the resolver
declined to choose between," not the destination — narrower than REQ-06's general "names ... the
destination" language — and the shipped code (`check-domain.sh:775-779`,
`bash-write-guard.sh:744`) matches that narrower, Advisor-ratified clause exactly. Whether that
plan amendment fully discharges the ui-reviewer's finding is that reviewer's own call to make in
their own cycle-2 pass, not mine.

## Advisory (non-blocking)

- The five MED code-grade records (listed above) carry no written `REASON REQUIRED` justification
  in source as `harness-code-risk-grading` asks for a passing grade-2. Non-blocking under this
  project's `advisory_unless_high` policy; filing as advisory only.

```yaml
VERDICT: PASS
DIGEST:
  headline: Both cycle-1 gating findings (F-01 REQ-06/D-08 vocabulary mismatch, F-02 four HIGH code-grade records) verified CLOSED at source against c5869301; the four splits that closed F-02 preserve every prior assertion, with two genuine tightenings and one new assertion, none weakened.
  severity_max: none
  findings: 1
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: "af5ddd7a..c5869301"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should the five MED-severity code-grade records (live_claims, reconcile.mutator, test-bash-write-guard.py main, case_36_live_claims_read_only_and_binding_horizon, case_bug1304_retention) get a written REASON REQUIRED justification in source, or a filed backlog issue, before this ships? Non-blocking under gates.review: advisory_unless_high.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1304-worktree-relative-path-guard/.harness/harness/features/BUG-1304-worktree-relative-path-guard/notes/review-harness-code-reviewer-c2.md
```
