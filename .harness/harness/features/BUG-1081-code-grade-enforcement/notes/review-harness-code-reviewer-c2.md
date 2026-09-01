# Review — harness-code-reviewer — BUG-1081-code-grade-enforcement — cycle 2

**VERDICT: PASS.** The two-file delta (`validate-digest.py`, `test-validate-digest.py`,
`827219b5..2562e45a`) closes c1's critical must_fix cleanly, stays inside its DEC-174 lane, and
introduces no fail-open. One `should_fix` (med): the new containment check's actual-refusal
branch is provably never exercised by the committed suite. One `low`/info: one of the four
"hostile" fixtures doesn't exercise the new function at all — still correctly refused, by a
different, pre-existing check. Neither gates. `must_fix: []`.

## What was re-graded vs. what carries forward

Re-graded, at this pin, from measurement — not narrated: DEC-174 lane/attribution for the two
changed files; the mechanical grader over the full range through `2562e45a`; the new
`_contained_feature_dir` function and its one caller, both checks, line-by-line; the
`_hook_feature_dir` → `feature_dir=None` → `_resolve_feature_dir` fallback interaction the delta
creates; the new test fixtures' actual code paths (traced, not read as prose); c1's Q1 status.

Carries forward from `review-harness-code-reviewer-c1.md` UNCHANGED, because the delta does not
touch the code or artifacts those findings depend on: every REQ-01..REQ-06 and SC-01..SC-12
verdict; the six Stage-2 adversarial reads (`_repo_root_for_feature`'s four `..` hops — now
additionally protected by containment, not superseded; `err` accumulation ordering;
`_load_test_kinds`' exhaustive malformed-shape refusal; `_is_plan_review`'s uniqueness;
the pre-existing `resolve_reviewed_commit` `OSError` gap, confirmed still byte-identical to
before, not widened here); no scope creep in T-01/T-03/T-04's files (untouched by this delta).

## 1. Lane and attribution

`2562e45a` touches exactly `validate-digest.py` and `test-validate-digest.py` — nothing else —
matching T-02's declared `files:` list in `plan.yaml` exactly (`git diff --stat 827219b5..2562e45a`
confirms two files, no others). `STATE.md` records `T-02 (main-session-direct, DEC-174)`. The
commit is authored directly by the human (Mike Ruangutai), tagged `[harness:BUG-1081]` — not a
`[harness:t-XX]` team-task tag — consistent with every other DEC-174-carve-out commit in this
range (`17e94e56` likewise) and distinct from the one `[harness:human]`-tagged commit
(`965c0e35`, plan-authoring only, out of range here). No team receipt exists for these two files
(confirmed absent in `notes/`), matching the carve-out: this file class is never certified by the
gates it changes. No scope creep: the diff is exactly `_contained_feature_dir` plus its wiring
plus tests — nothing beyond containment.

## 2. Self-grading — measured, not narrated

```
$ BASE=$(git merge-base origin/main 2562e45a)   # 9f2a0702bda6de929d42506f5aced2496669a2dc
$ python3 .claude/skills/harness/bin/code-grade.py --base "$BASE" --head 2562e45a
... 44 FUNCTION records ...
PASSING: 44
$ echo $?
0
```
Independently counted from the same output: `SEVERITY:` lines = 0, `GRADE: 2` records = 0. 44 =
c1's 41 + 3 new records (one production, two test), matching the delta exactly. The three new
records:

| function | file | grade | bar | driver | result |
|---|---|---|---|---|---|
| `_contained_feature_dir` | validate-digest.py:793 | 4 | 4 | cyclomatic+cognitive+abc | PASS |
| `_assert_honest_artifact_resolves` | test-validate-digest.py | 4 | 3 | cognitive+abc | PASS |
| `check_artifact_path_traversal` | test-validate-digest.py | 4 | 3 | cyclomatic+cognitive+abc | PASS |

**At the edge:** `_contained_feature_dir` grades exactly 4 against a bar of 4 — the tightest
margin in the whole range, though still a clean `RESULT: PASS`, no `SEVERITY:` line. Not a
finding; noting it because the dispatch asked which function sits at the edge.

## 3. The `_hook_feature_dir` error-swallow interaction — traced, not assumed

`_hook_feature_dir` (validate-digest.py:1471, **unchanged by this diff**) already collapses every
failure reason into `None`: `return None if error else feature_dir`. That pattern is
pre-existing. The delta adds exactly one *new* reason `_feature_dir_from_artifact` can produce an
error — the containment refusal — joining the pre-existing set (no artifact line, regex
mismatch, or the outer `except Exception`).

When `_hook_feature_dir` returns `None`, `validate(..., feature_dir=None)` reaches
`_resolve_feature_dir(text, feature_dir=None)` (validate-digest.py:856-873), which — because an
explicit `None` and "not passed" are indistinguishable — takes the **default** branch: derive
`root = _root_or_none()` (this file's own installed-checkout root, i.e. `owner_root`, confirmed
by reading `_root_or_none`'s body) and re-run `_feature_dir_from_artifact(text, root)` against
**that** root instead of the registry-resolved `checkout_root`.

**Verdict: not a fail-open, for the threat model this fix closes — structurally, not by luck.**
`_contained_feature_dir`'s first check (`segment in (".", "..") or not segment`) operates on
`relative` alone, extracted from `text` by the same regex regardless of which root is passed.
For every hostile artifact line in `HOSTILE_ARTIFACT_PATHS` (all contain a literal `.`/`..`
segment), the refusal fires identically whether tested against `checkout_root` or the
fallback's `owner_root` — the fallback recomputes the *same* refusal, not a different accept.
Concretely: if `checkout_root` refuses `.harness/../features/../notes/fake.md`, so does
`owner_root`, because the check never looks at `root` at all until *after* it has already
refused. There is no crafted-text input that a registry-resolved worktree root refuses and an
ambient owner root accepts.

**The one input class where fallback root *does* matter is the second check** (realpath
containment against a symlinked path component) — see §4. That class requires a symlink already
planted inside the checkout's filesystem, not merely crafted digest text, so it sits outside the
threat model DEC-174/this delta addresses (an attacker who controls only review prose). Recorded
as a residual, not folded into this verdict.

## 4. Stage 2 on the delta

**`_contained_feature_dir`'s literal-join return is sound for all three named callers.**
`_repo_root_for_feature` (line 552) applies its own `os.path.realpath` to the four-`..` join, so
it resolves the true root regardless of whether `feature_dir` arrived as a literal join or a
realpath. `_read_review_sha` and `_branch_corroboration_error` (via `_read_feature_branch`) only
`open()` a file under `feature_dir` — POSIX `open()` follows symlinks transparently, so a literal
join and its realpath name the same file. The only caller sensitive to the string form is a test
(`_assert_honest_artifact_resolves`, exact-equality against `os.path.join(repo, ...)`), which is
exactly what the docstring's macOS `/private` rationale is protecting. No caller depends on
`_contained_feature_dir` returning a realpath; the literal-join choice is correct as stated.

**Error text is a named repair** in both branches ("contains a relative segment... write your
review under this feature's own .../notes/ directory"; "resolves outside this checkout... the
feature it names is not the one under review") — both name the concrete condition and the fix,
consistent with every other refusal in this file.

**Coverage gap, measured (should_fix, med).** I traced line execution across the *entire*
`test-validate-digest.py` suite (`sys.settrace`, filtered to `validate-digest.py`, full run,
`ALL PASSED`, exit 0): line 822 — the second check's actual refusal
(`"...resolves outside this checkout..."`) — **never executes**. None of the four
`HOSTILE_ARTIFACT_PATHS` reach it: entries 1-3 are all caught by the first (segment) check before
the second check's `if` is ever evaluated in a way that returns an error; entry 4 doesn't reach
`_contained_feature_dir` at all (see below). The honest-path case (`_assert_honest_artifact_resolves`)
exercises the second check's *true* (accept) branch only. The function's own docstring states
the second check exists specifically because "a symlinked `.harness` or `<repo>` component...the
token check cannot see" — an intentional, documented defense with zero test proving it actually
refuses anything. A future edit that silently weakened or deleted that check (e.g. dropping the
`+ os.sep`, a classic prefix-bypass) would leave the suite fully green. This is not exploitable
today through the threat model this fix addresses (crafted digest text never reaches this branch
in a way that matters, per §3) and the code itself is currently correct — so it is a test-
completeness gap, not a live vulnerability, hence `should_fix`/med rather than `must_fix`.
Recommend one fixture: a `root` containing a real symlinked path segment that a hostile-but-
dot-free `relative` escapes through, asserting the named "resolves outside this checkout" message.

**Low/info — one fixture doesn't test what its framing implies.** `HOSTILE_ARTIFACT_PATHS[3]`
(`.harness/../harness/features/FEAT-TRAVERSAL/notes/fake.md`) never reaches
`_contained_feature_dir`: `FEATURE_DIR_IN_ARTIFACT_RE` requires exactly one segment between
`.harness/` and `/features/`, and this path has two (`..`, `harness`) — confirmed by direct
regex test (`re.search` returns `None` for this string). It is refused instead by the
pre-existing "does not name a `.harness/<repo>/features/<FEAT>/` location" error in
`_feature_dir_from_artifact`, unrelated to this delta's fix. The test's actual assertion
(`feature_dir is not None or not error`) doesn't overclaim mechanism — it only asserts "refused",
which is true — so this is not a false pass, just a docstring/framing imprecision (the comment
"an `artifact:` line whose captured segments contain `.` or `..` must not be able to redirect the
repository root" reads as if all four exercise the new function; three of four do). Not blocking.

## 5. c1's Q1 — still outstanding, untouched by this delta

The discarded `reviewed_python_change(root, reviewed)` call c1 flagged sits at
`code_grade_enforcement_error` line 776, unchanged byte-for-byte by this diff (confirmed by
direct read: the function body above `_contained_feature_dir`'s insertion point is identical).
The simplify receipt this concerns is not touched by `827219b5..2562e45a` either. Q1 remains
exactly as filed at c1 — open, low, non-blocking.

```yaml
VERDICT: PASS
DIGEST:
  headline: Cycle-1 must_fix closed correctly and inside its DEC-174 lane; no fail-open in the hook fallback; one measured should_fix (untested symlink-defense branch), non-blocking
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "827219b5..2562e45a (delta); 9f2a0702..2562e45a (full range measured)"
  human_commits_in_scope: [2562e45a, 17e94e56]
  open_questions:
    - { id: Q1, question: "carried from c1, unchanged: receipt-harness-backend-dev-simplify-simplification.md's Finding 1 overstates code_grade_bound_to_review's duplication of the discarded reviewed_python_change call at validate-digest.py:776 — still not corrected, still not touched by this delta.", blocking: false }
    - { id: Q2, question: "_contained_feature_dir's second check (realpath containment against a symlinked path component) has zero test coverage across the full suite (measured via line trace, line 822 never executes) — the code is correct today but a future regression there would go undetected; recommend a symlink-based fixture before this file is next touched.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/BUG-1081-code-grade-enforcement/notes/review-harness-code-reviewer-c2.md
```
