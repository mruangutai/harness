# Review — harness-code-reviewer — FEAT-50-run-artifact-integrity (recheck)

Reviewed delta: `dca2d3dabc5c1a3c3d7dab19f6d674b5d94ede78..7505b8739fd19a68601a27898d880fc719962712`
(HEAD). Note: the dispatch's full 40-char pinned sha (`7505b87681c8d8007a2677381313581f61faf1b0`)
does not exist in this repo — `git rev-parse HEAD` resolves to `7505b8739fd19a68601a27898d880fc719962712`,
whose short form `7505b87` matches the dispatch and whose subject is "fix: close FEAT-50 review
findings" — the expected fix commit. Treated as the intended pin; a typo in the dispatch, not a
tree mismatch.

`git diff --stat dca2d3d..HEAD`: 5 files — `bash-write-guard.sh` (+1), `check-domain.sh` (+9/-2),
`test-bash-write-guard.py` (156 changed lines, refactor), `test-check-domain.py` (279 changed
lines, refactor), `feature.json` (review_sha repin only). No other file in the reviewed set
(`harness_boundary.py`, `inflight_registry.py`, `validate-digest.py`,
`test-harness-boundary.py`, `test-validate-digest.py`, `harness-team/SKILL.md`,
`DECISIONS.md`, `DECISIONS-INDEX.md`) changed in the delta — confirmed via
`git diff --stat` returning empty for each.

## Verdict per prior finding

**Finding 1 [HIGH, security] — CLOSED.**
`bash-write-guard.sh:785` now calls `feature_checkout_guard(rel, ap)` on the `"shared"` outcome
branch (it already ran on `"allow"/"not_a_domain_question"` at line 781, pre-existing since
dca2d3d — confirmed via `git show dca2d3d:bash-write-guard.sh:770-795`). Direct evidence, not
inference: `test-bash-write-guard.py`'s `run_feat50_checkout_binding` gained a new
`bash-feature-checkout-shared` case (absent at dca2d3d — confirmed via
`git show dca2d3d:test-bash-write-guard.py | grep FEAT50_SHARED_MANIFEST` returning nothing)
that fires `echo hi > <main-checkout feature path>` under a manifest where the target classifies
`"shared"` (`FEAT50_SHARED_MANIFEST`, empty domain + `shared:` list) and asserts exit 2 with the
worktree named in stderr. Ran: `python3 .claude/skills/harness/bin/test-bash-write-guard.py` →
`ok bash-feature-checkout-shared`, `6/6 FEAT-50 Bash binding cases passed`, 0 `^FAIL` lines
across the whole suite. The mutant harness (`_feat50_bash_mutant`) was also tightened in lockstep:
it now requires `source.count(call) != 2` (was `!= 1` at dca2d3d, matching the pre-fix single call
site) — a future revert of either call site trips `INCONCLUSIVE`, not a silent pass.

**Finding 2 [HIGH, code quality] — CLOSED, verified by direct re-grade, not the CLI's default
report.**
`code-grade.py`'s diff report only prints functions whose grade is unchanged-or-worse (its
`gated_set` drops "informational" records — grade held or improved against a name-matched
pre-image). Both flagged functions match by name and improved, so they never appear in
`code-grade.py --base dca2d3d --head HEAD`'s output; I graded them directly via
`code_grade.grade_source` against `git show HEAD:<path>`:

| Function | Before (dca2d3d) | After (HEAD) |
|---|---|---|
| `run_feat50_checkout_binding` (`test-bash-write-guard.py:932`) | cyc 11 / cog 9 / ABC 59.6 / **grade 1** | cyc 1 / cog 0 / ABC 16.1 / **grade 4** |
| `run_feat50_artifact_integrity` (`test-check-domain.py:2857`) | cyc 17 / cog 14 / ABC 85.8 / **grade 1** | cyc 1 / cog 0 / ABC 20.0 / **grade 4** |

Before-numbers reproduced exactly against the prior review note's citation, confirming the same
source. Every extracted helper the refactor introduced was graded by the standard CLI run
(`code-grade.py --base dca2d3d --head HEAD`, exit 0): 21 new functions across the two test files,
**all grade 4 or 5**, none grade ≤3 or grade 2 (full per-function cyc/cog/ABC numbers in the raw
tool output — none below the test-code bar of 3, no complexity was quietly parked in one new
grade-1 helper).

*Coverage superset, not just grade:* enumerated case names before/after both driver functions.
- `run_feat50_checkout_binding`: before = {main, inside, absent, short, red} (5). after = same 5
  **plus** `bash-feature-checkout-shared` (6). Superset.
- `run_feat50_artifact_integrity`: before = {feature-checkout-main, -short-prefix, -inside,
  -absent, -red, digest-clobber, digest-append, digest-PRE-only, digest-clobber-red} (9). after =
  same 9 **plus** `digest-unreadable` (10). Superset.
No case name present at dca2d3d is missing at HEAD in either function.

**Finding 3 [MED, security] — CLOSED.**
`check-domain.sh:1143-1156`: `prior = None` before the read; `FileNotFoundError` sets
`prior = ""` only when `os.path.lexists(absolute_path)` is also false (genuine absence — a
dangling-symlink `FileNotFoundError` leaves `prior` at `None`); the generic `except OSError: pass`
(permission errors, `IsADirectoryError`, etc.) also leaves `prior` at `None`; `if prior is None:`
denies with "cannot be read safely" before the clobber-prefix check ever runs. This is exactly
"OSError → `prior = None` → deny" from the finding. New test `_feat50_digest_unreadable_case`
(`test-check-domain.py:2817`, absent at dca2d3d) makes the digest path a directory
(`os.makedirs(path)`), which raises `IsADirectoryError` (a non-`FileNotFoundError` `OSError`) on
`open()`, and asserts exit 2 with `"cannot be read safely"` in stderr. Ran:
`python3 .claude/skills/harness/bin/test-check-domain.py` → `ok digest-unreadable`,
`10/10 FEAT-50 artifact-integrity cases passed`, 0 `^FAIL` lines across the whole suite (69 `ok`
lines total).

## Delta-scoped spec table

| Hunk | Answers | Breaks a prior MET item? | Scope leakage? |
|---|---|---|---|
| `bash-write-guard.sh:785` (+1 line) | Finding 1 / REQ-08 (route-complete checkout binding across both write surfaces — the `"shared"` branch was the uncompleted route) | No — re-ran SC-18/19 commands (below), still green | No |
| `check-domain.sh:1143-1156` (+9/-2) | Finding 3 / REQ-04 (digest-clobber guard's "preserve recorded content" guarantee, now closed against unreadable-not-absent) | No — re-ran SC-05/06 (via SC-03..06 command), still green | No |
| `test-bash-write-guard.py` (refactor, 156 lines) | Finding 2 (code_grade) + adds direct coverage for Finding 1 (`bash-feature-checkout-shared`) | No — full suite green, case superset confirmed | No |
| `test-check-domain.py` (refactor, 279 lines) | Finding 2 (code_grade) + adds direct coverage for Finding 3 (`digest-unreadable`) | No — full suite green, case superset confirmed | No |
| `feature.json` (review_sha repin, 1 line) | Process bookkeeping (repin to dca2d3d ahead of this fix commit, per the standard repin→fix cycle; commit `b3895ff "chore: repin FEAT-50 review source"`) | N/A | No — not a REQ/SC-scoped change, expected repin artifact |

No hunk in the delta traces to nothing (no scope creep); no hunk touches a REQ/SC surface without
also re-passing that surface's own verify command.

## Re-run success-criteria commands (evidence, this pin)

All commands below substitute `HEAD` for `<review_sha>`.

- SC-03/04/05/06: `python3 .claude/skills/harness/bin/test-check-domain.py` → 0 `^FAIL` lines.
- SC-04: `git show HEAD:.../test-check-domain.py | grep -q 'feature-checkout-red'` → found.
- SC-06: `git show HEAD:.../test-check-domain.py | grep -q 'digest-clobber-red'` → found.
- SC-17: all three clauses of the compound command → all satisfied (obsolete pass-through case
  absent; `stop_hook_active` and `empty-string` cases present). File untouched by delta as
  expected (`git diff --stat` empty for `test-validate-digest.py`).
- SC-18: `python3 .claude/skills/harness/bin/test-bash-write-guard.py` → 0 `^FAIL` lines.
  `git show HEAD:.../test-bash-write-guard.py | grep -q 'bash-feature-checkout-short'` → found.
- SC-19: `git show HEAD:.../test-bash-write-guard.py | grep -q 'bash-feature-checkout-red'` → found.
- SC-20: `python3 .claude/skills/harness/bin/test-validate-digest.py` → 0 `^FAIL` lines.
  `git show HEAD:.../test-validate-digest.py | grep -q 'dec156-worktree-nofeature'` → found.
- SC-21: `git show HEAD:.../test-validate-digest.py | grep -q 'dec156-worktree-red'` → found.

All eight re-run. All pass at HEAD. Nothing previously MET went red.

## Non-gating findings 4 and 5 — unchanged by this delta

Confirmed via `git diff dca2d3d..HEAD -- bash-write-guard.sh check-domain.sh | grep 'def feature_checkout_guard'`
returning no hits — neither `feature_checkout_guard` function body (the `AmbiguousWorktree`/
blanket-`except Exception` absorber pair, finding 4) nor its duplication across the two files
(finding 5) was touched. Finding 1's fix added a *second call site* to the existing function in
`bash-write-guard.sh`; it did not add a second implementation, and does not aggravate or resolve
either note. Both remain open exactly as previously recorded, `should_fix`, non-gating.

## Verdict rationale

All three prior findings are CLOSED with direct evidence (a real subprocess run through the
production hook for 1 and 3, a direct re-grade for 2 bypassing the CLI's improved-function
omission). No REQ or SC that was MET before the delta broke. No scope leakage. No new finding
in the delta itself: the refactor's extracted helpers all clear the test-code bar with margin,
and the only behavioural change (`feature_checkout_guard` on the shared branch,
`prior = None` on OSError) is exactly what each finding called for, backed by an executed
mutant/negative case, not just a read.

```yaml
VERDICT: PASS
DIGEST:
  headline: All three prior findings (bash-write-guard shared-branch gap, two grade-1 test functions, digest OSError fail-open) are CLOSED with re-run evidence; no regression, no new finding, no scope leakage in the delta.
  severity_max: none
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: "dca2d3dabc5c1a3c3d7dab19f6d674b5d94ede78..7505b8739fd19a68601a27898d880fc719962712"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-50-run-artifact-integrity/notes/review-harness-code-reviewer-feat50-recheck.md
```
