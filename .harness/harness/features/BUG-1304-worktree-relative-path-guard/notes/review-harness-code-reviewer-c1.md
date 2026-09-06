# Code Review — BUG-1304 worktree-relative-path-guard — panel-c1 — pinned `af5ddd7a`

## Headline

Stage 1 (spec compliance) PASSES: all 12 files trace to REQ/D, no scope creep, no omission, all
SC-01..SC-12 and REQ-01..REQ-07 are met by the diff. Stage 2 (code quality) FAILS on the mechanical
grader: one new production function and three new test functions ship at a grade the review
protocol defines as build-blocking. `code_grade: fail`. Everything else — both-route equivalence,
fail-open reachability, read-only/exception-safety of the new enumerator — checks out clean on
direct trace, not inference.

## Stage 1 — spec compliance

### Per-ID table

| id | verdict | evidence |
|---|---|---|
| REQ-01 | met | `claim_checkout_guard` returns immediately when `not agent or not agent.startswith("harness-")` (check-domain.sh:772-773, bash-write-guard.sh:730-731); `claim_worktrees` returns `[]` when no live claim resolves to a worktree |
| REQ-02 | met | both guards resolve `destination = harness_boundary.real(destination)` before any comparison; SC-03 asserts relative/absolute parity in both test suites |
| REQ-03 | met | SC-04 cases pass on both routes; regression floor (T-05 case 14: digest.md/state.yaml/missing-manifest/`/tmp` unchanged) present in `test-bash-write-guard.py:1178-1188` |
| REQ-04 | met | `claim_checkout_guard` is byte-identical in shape between the two files (diffs only in message prefix and `sys.exit(2)` vs `deny()`, both of which exit 2) — see "Both-route equivalence" below |
| REQ-05 | met | `harness_boundary.claim_worktrees` implements D-10's exact 3-step ordering (harness_boundary.py:262-284); unit cases 6/7/8 and integration cases at SC-05/SC-10/SC-12 exercise all three branches |
| REQ-06 | met | `claim_set_refusal` (harness_boundary.py:280-303) names every claim-set member and the destination's home, never says "remove the worktree", and redirects `.harness/expertise/` destinations to the merge CLI — unit-tested directly (test-harness-boundary.py:447-459) and via the Bash-route positive/negative pair (test-bash-write-guard.py:1147-1160) |
| REQ-07 | met | plan.yaml D-01..D-11; DECISIONS.md `## DEC-218` (6844) + DECISIONS-INDEX.md row, verified present at pinned sha |
| SC-01 | met | `test-check-domain.py:4471` "relative main-checkout write is refused" |
| SC-02 | met | `test-bash-write-guard.py:1043,1046` redirect + in-place `sed` cases |
| SC-03 | met | absolute-path cases on both routes, same exit 2 |
| SC-04 | met | 5 sub-cases present on both routes, including the discriminating owner-root-registry pair (T-01 case 2 cross-reference honored) |
| SC-05 | met | malformed `.git` pointer + ambiguous-worktree cases, both routes, `"FEAT, FEAT-X"` asserted in stderr |
| SC-06 | met | `bug1304_assert_pre_change_allows` fires every refusal case at a byte-verified frozen pre-change fixture (identical to `c369fb1f`, confirmed by direct diff), asserts absence of the three fail-open markers AND a positive control still refused — 10 call sites (check-domain) / 12 (bash-write-guard), matching each task's exact floor |
| SC-07 | met, with one deviation noted (see below) | all five boundary questions present in the one DEC-218 entry; D-03's "verbatim" instruction not honored literally (LOW finding) |
| SC-08 | met | short-form worktree case on both routes |
| SC-09 | met | aged-claim (backdated past `CLAIM_TTL_SECONDS`, under `OMP_UNVERIFIED_TTL_SECONDS`) case on both routes with pre-change proof |
| SC-10 | met | unreadable-registry refusal + paired well-formed control, both routes, file path named in stderr |
| SC-11 | met | `case_bug1304_retention` / `case_bug1304_retention_admission` verify file-content retention separately from the 1200s dispatch answer; `claim_with_receipt` admission traced to source (uses `live`, never `retained`) |
| SC-12 | met | disjoint "mixed" fixture on both routes: allow-half (own worktree) and refusal-half (main checkout, unreadable elsewhere) both asserted |

### D-07's two same-edit rewrites — verified landed

- DEC-153 (DECISIONS.md:3446-3448): "bash-write-guard permits a governed agent's writes under the
  assigned worktree" — confirmed narrowed from the prior "any disposable checkout" wording.
- DEC-193 first surviving-divergence bullet (DECISIONS.md:~5334): now reads "Both routes bind a
  governed write to the writer's claim set. The Bash route's remaining DEC-153 carve-out permits
  only writes inside the assigned worktree." — confirmed the old "Bash route keeps DEC-153's
  blanket allow" sentence is gone (grepped, zero hits).

### D-03's "verbatim" residues — LOW finding

D-03's own text: *"Both residues must appear verbatim in the DECISIONS.md entry T-07 lands."*
The delivered DEC-218 entry (DECISIONS.md ~6864-6868) states the FALSE-ALLOW/FALSE-REFUSE
residues in **paraphrase**, not the plan's literal wording (different sentence structure, dropped
the "exact match would refuse it" / "REQ-01 calls that session unbound" clauses). Substance is
preserved; the explicit "verbatim" instruction is not honored literally. Low severity — no
functional or doctrine-fidelity risk, but it is a stated, unambiguous requirement that the record
does not meet on its own terms.

## Both-route equivalence — REQ-04, D-08 (probe 1)

**The call-site sets differ by design (D-08); the guard body does not.**

Write/Edit route (`check-domain.sh`) reaches `claim_checkout_guard` at exactly two call sites,
both inside `domain_check()`: `outcome == "allow"` (:967) and `outcome == "shared"` (:973).
`out_of_place_worktree` and `wrong_checkout` always `sys.exit(2)` before either call point (:922-949);
`not_a_domain_question` returns before rel is even computed (:953); `deny` (fallthrough) exits 2.
So every write that would otherwise land is examined exactly once.

Bash route (`bash-write-guard.sh`) reaches `claim_checkout_guard` at **three** call sites: the
pre-classify worktree-shortcut (`rel` matches `^\.claude/worktrees/`, :830, this is the DEC-153
narrowing) plus the post-classify `allow` (:876) and `shared` (:882) branches. This third site has
no Write-route counterpart because the Write route never had DEC-153's blanket worktree allow to
narrow (grepped: no `\.claude/worktrees/` shortcut exists in check-domain.sh) — this asymmetry is
the intended D-08 shape, not a gap. Both `out_of_place_worktree`/`wrong_checkout` (:834-847) and
`deny` (fallthrough, :898) exit before either call point.

**Why "allow"/"shared" is the single point of divergence risk, verified not inferred:** a worktree
under `.claude/worktrees/<repo>/<name>/` is physically *inside* `root` (confirmed: this session's own
worktree lives at `<main-checkout>/.claude/worktrees/harness/BUG-1304.../`), so
`select_base` (harness_boundary.py:509-512) resolves `base = root` for both a main-checkout path and
a worktree path — `inside(abs_target, abs_root)` is true either way. The DEC-143 `checkout_relative`
second `rel_candidate` (harness_boundary.py:641-648) is what makes the SAME checkout-agnostic glob
(e.g. `.claude/skills/harness/bin/**`) match both locations under the identical `allow` outcome.
That is exactly why `claim_checkout_guard` had to be inserted there and nowhere else on either route.

**The guard body itself, compared side by side (extracted and diffed programmatically):** identical
branch order, identical exception handling, identical message construction on both files. The only
differences are: (a) stderr prefix ("check-domain:" vs "bash-write-guard:"), (b) `sys.exit(2)`
directly vs. `deny(...)` — confirmed `deny()` (bash-write-guard.sh:647-653) itself calls
`print(...); sys.exit(2)`, so the two are behaviourally identical, (c) unused return values
(`return []` / `return claim_set` on the Bash side vs. bare `return` on the Write side — dead, since
no caller on either route captures the return; INFO, not a finding).

**Refusal-condition SET, enumerated on each route (for the lead to check against, not take on trust):**

- Write/Edit: `{AmbiguousWorktree while building S} ∪ {UnreadableRegistry, readable roots cannot
  place destination} ∪ {S non-empty AND destination outside every member of S}` — exactly at outcome
  ∈ {allow, shared}, agent is `harness-*`, destination resolves inside `root`.
- Bash: **identical set**, at outcome ∈ {allow, shared} OR `rel` matches `^\.claude/worktrees/`, same
  agent/destination gating.
- The two sets are equal wherever both routes are reachable (`allow`/`shared`); the Bash route adds
  reachability for worktree-shaped destinations that never had an equivalent Write-route blanket
  allow to narrow — this is the D-08 asymmetry, not a divergence in what gets refused once reached.

No condition is reachable on one route and not examined identically on the other, wherever both
routes see the write at all.

## Fail-open hunt (probe 2)

**(a) Can the new code be reached only after a branch that already fail-opened?** Yes, in exactly two
PRE-EXISTING, SYMMETRIC conditions, neither introduced nor worsened by this diff:
- Missing `team-config.yaml` manifest: `domain_check()` (and thus `claim_checkout_guard`) is called
  only under `if _run_domain and not _no_parser:` (check-domain.sh:1002-1003); `_run_domain` is set
  False at the "enforcement OFF" print (check-domain.sh:384-386). On Bash, the same manifest check
  (`bash-write-guard.sh:268-269`) exits 0 before any of this code is even imported. REQ-03 explicitly
  accepts this as unchanged, pre-existing behaviour, and T-05 case 14/"missing manifest fail-open
  remains unchanged" tests it directly.
- PyYAML unavailable (`_no_parser`): both files gate the domain walk behind `_no_parser`
  (check-domain.sh:1002, bash-write-guard.sh:664-665) — confirmed symmetric: bash-write-guard.sh's
  own comment at :322-325 documents this is the SAME reachability tier on both routes for this
  reason (the file's *root-side* worktree check is placed deliberately ABOVE this gate for a
  DIFFERENT, pre-existing rule; `claim_checkout_guard`'s three call sites all sit below it on both
  files). Neither route enforces the new rule in this state — symmetric, not a bypass.

Both are inherited reachability tiers matching `feature_checkout_guard`'s own placement, not new
holes this diff opens.

**(b) Any input that silently skips the rule while a governed write proceeds?** None found beyond
(a). Every other exception path — `AmbiguousWorktree`, `UnreadableRegistry`, or any other
`Exception` — is caught and either exits 2 or explicitly PRINTS "boundary was not enforced; passing
through because the guard failed internally" before allowing (check-domain.sh:801-805,
bash-write-guard.sh:754-758) — loud, not silent, matching the existing quarantine-branch convention
this file already uses elsewhere.

## New enumerator: reachability, mutation-safety, read-only (probe 3)

- **Every exception is caught on both routes.** `except AmbiguousWorktree` first, `except Exception`
  catches everything else (`UnreadableRegistry` included), so nothing "raises past" either guard —
  confirmed by exception hierarchy (`AmbiguousWorktree(Exception)`, harness_boundary.py:197) and by
  direct trace of both `claim_checkout_guard` bodies.
- **No legitimate-write failure mode found.** Concurrent writer: `harness_merge.locked_update`
  (harness_merge.py:107-135) writes via tempfile + `os.replace`, so a concurrent reader never sees a
  torn file — `live_claims` needs no lock and none is taken. Missing directory / stale worktree
  pointer: `FileNotFoundError` is caught explicitly and returns `[]` (inflight_registry.py:296-297),
  not routed through `UnreadableRegistry`. Symlinked root: `real()`/`inside()` use
  `os.path.commonpath`, already guarded against `ValueError` (harness_boundary.py:245-248).
  Permission-denied registry FILE *is* routed to `UnreadableRegistry` (broad `except OSError`,
  inflight_registry.py:301) — this is a deliberate, documented widening beyond the BRIEF's literal
  JSON/schema enumeration: DECISIONS.md's DEC-218 entry says outright *"The listed JSON failures are
  illustrative, not exhaustive: OSError and undecodable input are also unreadable"* — so this is
  reviewed-and-intentional, not an unreviewed edge case.
- **Genuinely read-only, unlike `live_claim`.** `live_claims` opens the registry with mode `"r"` only
  and never calls `_update_registry`/`locked_update` (inflight_registry.py:290-323); the file's own
  test (`case36: live_claims is byte-for-byte read only`) asserts before/after byte equality, and I
  traced the call graph to confirm no write path is reachable from it.

## Code quality (Stage 2) — code-grade.py result: **FAIL**

Ran `code-grade.py --base $(git merge-base origin/main af5ddd7a) --head af5ddd7a`. Four records are
gated and below their bar; per `harness-code-risk-grading`, a grade-1-anywhere or grade-3-in-production
record is a **HIGH**, build-blocking finding regardless of whether the mechanical test matrix is
green:

| severity | file:line | qualname | cyclomatic | cognitive | ABC | grade | bar |
|---|---|---|---:|---:|---:|---:|---:|
| **high** | `.claude/skills/harness/bin/harness_boundary.py:252` | `claim_worktrees` | 8 | 10 | 20.3 | 3 | 4 (production) |
| **high** | `tests/unit/test-harness-boundary.py:345` | `case_bug1304_claim_set` | 11 | 15 | 89.2 | 1 | 3 (test) |
| **high** | `tests/integration/test-bash-write-guard.py:1018` | `run_bug1304_claim_set` | 6 | 8 | 140.0 | 1 | 3 (test) |
| **high** | `tests/integration/test-check-domain.py:4446` | `run_bug1304_claim_set` | 6 | 8 | 119.6 | 1 | 3 (test) |

All four are driven by ABC (assignments/branches/conditions), not cyclomatic complexity: each is a
single function carrying dozens of sequential fixture builds and inline assertions rather than being
decomposed into the file's own established one-case-per-function convention
(`case_NN_something()` elsewhere in these same files). `claim_worktrees` mixes the S/U-collection
loop with the D-10 three-step ordering decision in one function — a natural, low-risk split point
(collect-S-and-U vs. decide-and-raise) that would likely clear grade 4 on its own.

Grade-2 records present (reasoned, non-blocking per the skill, but no such reason is written in
source for any of them — flagged as should_fix):
`inflight_registry.py:290 live_claims` (17/24/40.5, bar 4), `inflight_registry.py:592
reconcile.mutator` (7/17/14.5, bar 4, worsened by the new `_binding_retained` branch),
`tests/integration/test-inflight-registry.py:1091 case_36_live_claims_read_only_and_binding_horizon`
(5/1/42.6, bar 3), `tests/integration/test-inflight-registry.py:1176 case_bug1304_retention`
(1/0/30.1, bar 3), `tests/integration/test-bash-write-guard.py:1240 main` (4/10/26.2, bar 3, worsened).

`code_grade: fail` — this is an independent, mechanical check `validate-digest.py` re-derives over
`merge-base(origin/main, af5ddd7a)..af5ddd7a`; I am reporting what the tool reports, not asserting
a value.

## Advisory (LOW, non-blocking)

- **Untested Edit route on the claim-set boundary.** T-03's own intent: "Cases... repeated on the
  Edit route where the file's existing Edit-route helper allows." `_bug1304_fire`/`expect` in
  test-check-domain.py support `tool="Edit"` (built for exactly this), but no case in
  `run_bug1304_claim_set()` ever passes it. Low risk: Edit and Write share the identical
  `domain_check()`/`claim_checkout_guard` call path (the resolved `target` comes from the same
  `file_path` field regardless of tool, and Edit-route behaviour for this file's other guards is
  already covered elsewhere in the same suite, e.g. `run_bug1106_edit_route_cases`), but the task's
  own stated coverage intent isn't fully honored.
- **Misleading provenance comment.** Both `run_bug1304_claim_set` docstrings say *"frozen guard
  provenance: a4e8ecf7"*. Commit `a4e8ecf7` ("retain claims through binding horizon", T-09) touches
  only `inflight_registry.py` and its test — it never touches `check-domain.sh` or
  `bash-write-guard.sh`. I independently verified the actual fixture bytes are correct (byte-diffed
  identical to `c369fb1f`, the plan's own pre-change baseline), so this is a wrong citation in a
  comment, not a functional defect — but a future reader following it to verify provenance will be
  confused.
- **Duplicated liveness predicate.** `_binding_retained` (inflight_registry.py:239-248) and
  `live_claims`'s own inline OMP/non-OMP branch (inflight_registry.py: within :290-323) implement the
  identical binding-liveness rule as two separately-maintained blocks. A future edit to one without
  the other would silently desync what "binding-live" means between the read (`live_claims`) and
  retention (`_expire_where`/`reconcile`) paths. Worth a shared helper, not blocking.

## Settled matters not re-litigated

`RuleBug1304UnreadableConflict` (unreadable-registry fail-closed ruling, FEAT-51 fixture narrowing,
quarantine-own-failures-stay-fail-open) and the plan's recorded dead ends (payload binding key,
registry-file-derived S, `_expire`/`CLAIM_TTL_SECONDS` filtering, `CHECK_DOMAIN_BIN` override) are
confirmed correctly NOT reopened anywhere in this diff.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Stage 1 spec compliance passes cleanly; Stage 2 fails on code-grade.py — one production and three test functions ship at a build-blocking grade (grade 3 in production, grade 1 in tests).
  severity_max: high
  findings: 8
  must_fix:
    - "harness_boundary.py:252 claim_worktrees — grade 3, bar 4 (production); cyclomatic 8, cognitive 10, ABC 20.3"
    - "tests/unit/test-harness-boundary.py:345 case_bug1304_claim_set — grade 1, bar 3 (test); cyclomatic 11, cognitive 15, ABC 89.2"
    - "tests/integration/test-bash-write-guard.py:1018 run_bug1304_claim_set — grade 1, bar 3 (test); cyclomatic 6, cognitive 8, ABC 140.0"
    - "tests/integration/test-check-domain.py:4446 run_bug1304_claim_set — grade 1, bar 3 (test); cyclomatic 6, cognitive 8, ABC 119.6"
  spec_violations:
    - { kind: mismatch, path: ".harness/harness/docs/DECISIONS.md", ref: D-03 }
  code_grade: fail
  reviewed: "af5ddd7a (base for grading: merge-base(origin/main, af5ddd7a) = 6e95435a585f85136ed17fd6835369e30b784583)"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Should the four blocking code-grade records (claim_worktrees + the three run_bug1304_claim_set/case_bug1304_claim_set mega-functions) be decomposed before ship, or is a written grade-2/3-acceptance reason preferred given the panel already closed the plan-level review at cycle 3?", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1304-worktree-relative-path-guard/.harness/harness/features/BUG-1304-worktree-relative-path-guard/notes/review-harness-code-reviewer-c1.md
```
