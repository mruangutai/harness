# Review — harness-code-reviewer — FEAT-50-run-artifact-integrity (pinned)

Reviewed: `9f2a0702bda6de929d42506f5aced2496669a2dc..dca2d3dabc5c1a3c3d7dab19f6d674b5d94ede78`

## Changed files (37; `git diff --stat`)

Code/behaviour (12): `.claude/skills/harness-team/SKILL.md`,
`.claude/skills/harness/bin/{bash-write-guard.sh,check-domain.sh,harness_boundary.py,
inflight_registry.py,test-bash-write-guard.py,test-check-domain.py,test-harness-boundary.py,
test-validate-digest.py,validate-digest.py}`,
`.harness/harness/docs/{DECISIONS.md,DECISIONS-INDEX.md}`.

Process/feature artifacts (25, expected — not code): BRIEF.md, STATE.md, feature.json,
plan.yaml, and notes/{answers,handoff,receipt×6,research×4,review×3,observations×3}.

## Stage 1 — spec compliance

All REQ-01..09 MET. All SC-01..21 MET or correctly NOT REACHABLE/inspection per BRIEF's own
disclosure (SC-11 external blocker, SC-08/09/10 unchanged-suite claims). Verified each by
reading the cited code at the review SHA and by running the targeted single-file tests named
in each criterion's own `command:` (never the full suites).

| # | Verdict | Evidence |
|---|---|---|
| REQ-01/REQ-02, SC-01 | MET | `validate-digest.py:1593-1614`: `_ABSENT` sentinel discriminates absent/null (exit 0, "NOT VALIDATED" on stderr) from present-empty (exit 2, names persona). `test-validate-digest.py` hook_cases "empty-string", "absent-key", "null-passthrough" — ran green. |
| SC-02 | MET | `run_empty_red_case` (`test-validate-digest.py:2957`) reverts exactly the presence branch to the old `or ""` truthiness join; real=2, mutant=0. Ran green. |
| REQ-03, SC-03 | MET | `check-domain.sh:715-746` `feature_checkout_guard` + `harness_boundary.worktree_for_feature` (prefix match). `test-check-domain.py::run_feat50_artifact_integrity` cases feature-checkout-main / -short-prefix / -inside / -absent — ran green, all 4 clauses incl. the short-flow-id one an equality match would fail. |
| SC-04 | MET | feature-checkout-red mutant deletes the one `feature_checkout_guard` call on the `allow` branch; real=2, mutant=0. Ran green. |
| REQ-04, SC-05 | MET | `check-domain.sh:1139-1151` `RE_RUN_DIGEST` guard, fixture places digest.md inside a registered worktree (not fixture root). digest-clobber (2), digest-append/whitespace/new (0), post-route (0, PRE-only by construction — verified: POST reads `content` and `prior` from the *same* on-disk file, so they are trivially equal and the guard can never fire on that route). Ran green. |
| SC-06 | MET | digest-clobber-red deletes the whole `# Issue #1058…` block; real=2, mutant=0. Ran green. |
| SC-07 | MET | `check-domain.sh --resolve check-domain.sh` → `harness-backend-dev` present; pre-existing worktree-strip cases untouched by diff. |
| REQ-05, SC-08/SC-09 | MET | `check-state.sh` and `run-unit-tests.sh` absent from the diff (untouched). `def case_inv32` present; `test-run-unit-tests-kinds.py` ran green (23/23). |
| REQ-06 | MET | All 5 red cases (empty-red, feature-checkout-red, digest-clobber-red, bash-feature-checkout-red, dec156-worktree-red) construct their mutant by deleting exactly the discrimination under test (verified each diff region), not an unrelated edit. |
| REQ-07, SC-14 | MET | `gen-decisions-index.py --stdout` diffed byte-identical against `DECISIONS-INDEX.md`; `grep -c` on the DEC-208 heading returns exactly 1. All 5 anchors DEC-208 cites (`validate-digest.py:1602-1614`, `check-domain.sh:1139-1151`, `bash-write-guard.sh:711-722`, `check-domain.sh:727-741`, `validate-digest.py:1413-1424`) spot-checked and match verbatim. |
| REQ-08, SC-18 | MET | `bash-write-guard.sh:699-726` reuses the same `harness_boundary.worktree_for_feature`/`checkout_relative`/`AmbiguousWorktree` primitives check-domain.sh uses (see Stage-2 note on the wrapper duplication). DEC-153 `.claude/worktrees/` continue and the `..` product-workspace continue are unmoved by the diff. bash-feature-checkout-{main,inside,absent,short,red} all ran green. |
| SC-19 | MET | bash-feature-checkout-red deletes the one-line `feature_checkout_guard(rel, ap)` call; real=2, mutant=0. Ran green. |
| REQ-09, SC-20 | MET | `validate-digest.py:1413-1424` resolves via `inflight_registry.feature_root(owner_root, harness_feature)` when the key is present, else falls back to `owner_root` unchanged. dec156-worktree-{narrative,valid,nofeature} fixtures place root and checkout in *different* directories (unlike `_dec156_case`) and ran green. |
| SC-21 | MET | dec156-worktree-red reverts to the bare `_root_or_none()` join; real=2, mutant=0. Ran green. |
| SC-10 | Not independently re-run (full-suite; per assignment, treated as reported ground truth) | — |
| SC-11 | NOT REACHABLE, as BRIEF states (external INV-32 blocker) | — |
| SC-12 | MET (inspection) | `notes/answers-2026-08-31-plan.md:134-152` — `## Operator ruling — INV-32`, `choice: d`, `who: operator`, `date: 2026-08-31`, not restated as a/b/c. |
| SC-13 | MET | `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exactly 9 DEVIATION lines (T-01,02,03,04,05,09,10,11,12), no VIOLATION. |
| SC-15 | MET | `test-harness-boundary.py` (`case_worktree_for_feature`) — exact/short-prefix/no-match/hyphen-boundary/ambiguous/no-worktrees-dir all covered, ran green. |
| SC-16 | MET | `inflight_registry.py:260-266` cutover to `worktree_for_feature`; inline `os.path.basename(worktree)` loop confirmed gone (`grep -cF` = 0); pre-existing `test-inflight-registry.py` (111/111) ran unchanged and green. `except Exception: return owner_root` catches `AmbiguousWorktree` too, so nothing escapes `feature_root` (SC-16's explicit requirement). |
| SC-17 | MET | obsolete "pass-through: empty last_assistant_message…" hook_case is gone; the two DEC-122 pass-throughs (non-harness agent_type, stop_hook_active) remain. |

`plan.yaml` spot-checked: `approval.rulings` absent (confirmed no `rulings:` key); the `panel:`
block present is this feature's *own* cycle-1 panel transcription (not a 32-plan backfill —
different mechanism, matches D-09/D-08 framing). No violation of the already-ruled items found.

## Scope leakage

None. Every code file in the diff traces to a REQ (T-01..T-12 all map 1:1); the harness-team
SKILL.md edit is T-06's compensating-control playbook note, explicitly required by REQ-04's
disclosed Write-only residual. No unrelated documentation or enforcement change found.

## Stage 2 — code quality

**Ranked findings:**

1. **[HIGH] code_grade: fail — `run_feat50_checkout_binding`** (`test-bash-write-guard.py:835`).
   Grade 1 (bar 3 for test code): cyclomatic 11, cognitive 9, ABC 59.6, driver=abc. The function
   packs 4 independent fixture scenarios (main-checkout deny, inside-worktree allow, no-worktree
   allow, short-flow-id deny) plus a hand-rolled mutant harness into one body with heavy reuse of
   mutable locals across scenarios (`root`, `worktree`, `target` get reassigned per scenario),
   making it hard to isolate which scenario broke on a red run or to safely extend one scenario
   without touching the others' state.
2. **[HIGH] code_grade: fail — `run_feat50_artifact_integrity`** (`test-check-domain.py:2694`).
   Grade 1: cyclomatic 17, cognitive 14, ABC 85.8, driver=abc — worse than finding 1, same shape:
   7 scenarios (checkout binding ×4 + digest-clobber ×4 + 2 mutant harnesses) in one function.
3. **[MED] code_grade: grade_2 — `case_worktree_for_feature`** (`test-harness-boundary.py:252`).
   Cyclomatic 5, cognitive 7, ABC 29.8. Reason for accepting grade 2 as-is: the function's six
   assertions are all boundary conditions of the *same* one-line contract
   (`worktree_for_feature`'s prefix-match rule), and splitting them into separate `case_` functions
   would only fragment one coherent equivalence-class table across several `tempfile.mkdtemp()`
   fixtures for no readability gain.
4. **[MED] Untested `AmbiguousWorktree` branch sits beside a blanket fail-open absorber.**
   `check-domain.sh:733-736` / `bash-write-guard.sh:713-716` both catch
   `harness_boundary.AmbiguousWorktree` and deny (verified live: a hand-built two-worktree
   ambiguous fixture against `check-domain.sh` today correctly exits 2). But neither
   `test-check-domain.py` nor `test-bash-write-guard.py` constructs that fixture — only
   `test-harness-boundary.py` exercises `AmbiguousWorktree` at the bare-primitive level, never
   through the guard's own `except`/`deny` wiring. Both guard functions immediately follow that
   `except AmbiguousWorktree` with a bare `except Exception: return` (fail-open, "absorbing by
   design"). Concrete scenario: a future refactor that merges or reorders those two `except`
   clauses (e.g. collapses them into one `except Exception` before the `AmbiguousWorktree` check,
   or a linter "simplification" pass) would silently turn an ambiguous-feature write from a denial
   into a silent allow into the main checkout — exactly issue #1057's failure shape — and nothing
   in the shipped suite would go red.
5. **[MED] `feature_checkout_guard` is duplicated near-verbatim across two files instead of using
   the shared-verdict pattern `harness_boundary.classify` already established.**
   `check-domain.sh:715-742` and `bash-write-guard.sh:699-726` re-implement the same
   worktree/ambiguity/checkout-comparison decision independently rather than exposing it from
   `harness_boundary.py` as a returned verdict (the way `classify()` does, with each hook only
   supplying its own wording) — the exact drift risk `harness_boundary.py`'s own module docstring
   names as the reason it exists ("a heredoc cannot be imported… written twice it would drift",
   citing issue #261). Only the print/deny wording differs between the two copies today; a future
   change to the matching logic (e.g. a new fallback rule) has to be applied twice to stay
   consistent, with no test asserting the two stay in sync.

No fail-open/silent-failure defect found in the shipped, reachable behaviour beyond finding 4 (a
coverage gap on a currently-correct path, not a live bug).

## Verdict rationale

`must_fix` carries the two grade-1 functions because the grading tool's own `RESULT: FAIL` is
gating per the reviewed protocol, independent of my own view that both are reachable, correct,
and well-commented tests. `severity_max: high` follows from that gate alone; findings 3-5 are
`should_fix` notes, not blockers.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Spec compliance is clean across all REQ/SC, but two new test functions are grade-1 (code_grade gate) and one gating fail-open path is untested — must_fix is code-grade only.
  severity_max: high
  findings: 5
  must_fix:
    - "code_grade: fail — run_feat50_checkout_binding (test-bash-write-guard.py:835), grade 1 (cyclomatic 11, cognitive 9, ABC 59.6, driver=abc, bar=3)"
    - "code_grade: fail — run_feat50_artifact_integrity (test-check-domain.py:2694), grade 1 (cyclomatic 17, cognitive 14, ABC 85.8, driver=abc, bar=3)"
  spec_violations: []
  reviewed: "9f2a0702bda6de929d42506f5aced2496669a2dc..dca2d3dabc5c1a3c3d7dab19f6d674b5d94ede78"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-50-run-artifact-integrity/notes/review-harness-code-reviewer-feat50-pinned.md
```
