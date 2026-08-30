# Receipt — harness-backend-dev — SEC-01 wave 3 (branch corroboration)

## BLUF

The residual SEC-01 hole is closed for the concretely reachable path: `code_grade`'s
review-sha binding now ALSO requires the resolved feature's `feature.json` `branch`
to match the current checkout's `git rev-parse --abbrev-ref HEAD` — additively, so it
can only turn an accept into a reject. The cross-feature forgery described in the
dispatch (`artifact:` naming FEAT-06, `reviewed:` reusing FEAT-06's own honest
`review_sha` twice) is now rejected with a named, actionable message; the honest
FEAT-43 digest still accepts. Both proved live against the real
`.harness/harness/features/` tree, not only in the test fixtures. Test-first: the new
cross-feature case was proven RED against the unmodified (pre-branch-check) binding
before being turned GREEN. Mutation proof inverts the one comparison the fix adds and
kills exactly the two cases that depend on it. `test-validate-digest.py` is green
(115/115 named CLI+gate cases via aggregate; every SEC-01/SC-19/SC-20 case named
below still passes). `validate()` gained a parameter, not a branch (cyclomatic stays
102, unchanged from the wave-2 receipt).

**Residual, not closed** (Rule 15): a checkout whose branch legitimately maps to more
than one `feature.json` (this repo has several today — `feat/harness-native-foundation`
→ FEAT-02 and FEAT-03; `main` → FEAT-06, and likely other older/merged features) can
still have its digest name ANY of the features sharing that branch. Raised as an
`open_question` below, not buried.

## What changed

`.claude/skills/harness/bin/validate-digest.py`:
- New: `_resolve_feature_dir` (factored out of `resolve_review_sha`'s derivation so
  the SHA half and the new branch half resolve the SAME feature, never two
  independent guesses), `_BRANCH_UNSET` sentinel, `_read_feature_branch`,
  `_current_branch_or_none`, `_branch_corroboration_error`.
- `resolve_review_sha` now delegates derivation to `_resolve_feature_dir` —
  behaviourally unchanged (proven by every pre-existing white-box case against it
  still passing unmodified).
- `code_grade_bound_to_review` gained a `branch_override=_BRANCH_UNSET` parameter
  and, on the SHA binding holding, now returns
  `_branch_corroboration_error(feature_dir, _current_branch_or_none(branch_override))`
  instead of unconditional `None` — the one line the hardening adds.
- `validate()` gained a `branch_override=_BRANCH_UNSET` parameter (fixture-override
  seam, mirrors `feature_dir`/`config_path`) threaded verbatim into the
  `code_grade_bound_to_review` call. No new branch in `validate()` itself — confirmed
  by `code-grade.py`: cyclomatic 102, identical to the wave-2 receipt's measured value.

`.claude/skills/harness/bin/test-validate-digest.py`:
- `make_feature_dir()` gained an optional `branch=None` parameter — omitted by
  default (matches every existing fixture, which carries no `branch` key at all, so
  none of the 100+ pre-existing cases changed shape); a string writes the field,
  including the literal `"none"`.
- `reviewer_digest()` gained an optional `artifact="a.md"` parameter (default
  unchanged) so the new cases can point `artifact:` at a specific feature directory.
- New `check_branch_corroboration`, wired into `run_code_grade_cases()` after
  `check_resolve_review_sha_feature_json`. Four assertions, all in one function
  sharing the three-feature-fixture setup (`FEAT-UNDER-REVIEW`, `FEAT-OTHER-SHIPPED`,
  `FEAT-NO-BRANCH`) under one `_root_or_none` monkeypatch:
  1. cross-feature forgery rejects, naming both branches (the finding).
  2. the honest digest (artifact: names the feature actually under review) accepts.
  3. an undeterminable current branch (`branch_override=None`) must not introduce a
     new rejection.
  4. a feature.json with `branch: "none"` must not introduce a new rejection.

## Test-first (RED confirmed before implementing, and again independently after)

Wrote `check_branch_corroboration` and its four assertions before touching
`code_grade_bound_to_review`'s return value; ran the suite against the
unmodified-for-this-wave source and watched case 1 fail:
`cross-feature forgery (artifact: names a different feature and reuses ITS OWN
honest review_sha) must reject, naming both branches (the SEC-01 residual hole)` —
under the SHA-only binding this shape validates cleanly (head resolves to
`FEAT-OTHER-SHIPPED`'s own `review_sha`), exactly the residual hole the dispatch
names. Only then did I add `_branch_corroboration_error` and wire it in, turning the
suite green.

Confirmed independently a second time after the full implementation (mechanical race
with a sibling forced a re-sequenced edit — see Design decisions): snapshotted the
fixed file, reverted `code_grade_bound_to_review`'s last line to bare `return None`
(the exact pre-hardening behaviour), reran, and observed the SAME single named
failure — nothing else broke or flipped. Restored the snapshot byte-identically
(`cp`, not `git checkout`) and reran green. `md5sum` before/after the revert-and-restore
cycle: `26ae05f5ec7834810352e105e8f8de5b` both times.

## Verification run and reported

**1. `python3 .claude/skills/harness/bin/test-validate-digest.py`**

Exit status **0**. Final line `ALL PASSED.` Named cases, new and preserved:

- `check_branch_corroboration` (new, 4 assertions in one function, all passing):
  cross-feature forgery rejects naming both branches; the honest digest (artifact:
  names the feature actually under review) accepts; undeterminable current branch
  introduces no new rejection; `branch: "none"` introduces no new rejection.
- `check_review_sha_binding` (preserved): honest range accepts; forged no-op range
  rejects naming `review_sha`.
- `check_review_sha_binding_unconditional` (preserved): forged range rejects for
  `code_grade` in `{pass, fail, grade_2}`, not only `n_a`.
- `check_review_sha_binding` unresolvable-feature branch (preserved): a missing
  `feature.json` directory fails closed.
- `check_review_sha_binding_other_personas` (preserved): `harness-ui-reviewer` /
  `harness-security-reviewer` unaffected — SEC-01 binds `harness-code-reviewer` only.
- `check_resolve_review_sha_artifact_path` (preserved, white-box, unmodified
  behaviour through the new `_resolve_feature_dir` indirection): no `artifact:`
  line, non-feature `artifact:` path, no checkout root each fail closed; the
  happy path still derives `FEAT-PROD`'s `review_sha` correctly.
- `check_resolve_review_sha_feature_json` (preserved): unpinned and absent
  `feature.json` each fail closed.
- CLI case `code_grade's missing-field hint names the four legal values` (preserved).
- SC-19 `code reviewer omission of code_grade is rejected` (preserved).
- SC-19/SC-20 `check_code_grade_state`'s `fail-plus-PASS must reject` / `grade_2
  with a written reason must permit PASS` / `without reasons must reject`
  (preserved, unchanged).

**2. Live CLI cross-feature reproduction** (temp files outside the repo, deleted
after), against the REAL `.harness/harness/features/` tree, run from this worktree
(current branch `feat/FEAT-43-code-risk-grading`; `.harness/harness/features/FEAT-06-team-layer-inv6/feature.json`
carries `review_sha: "9f87c48"`, `branch: "main"` — both read live, not fixtured):

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/.../forged-digest.txt
VERDICT: BLOCKED (contract violation)
  - code_grade cannot be bound to review_sha: this feature's recorded branch ('main') does not match the current checkout's branch ('feat/FEAT-43-code-risk-grading') — the digest's artifact: line must name the feature actually under review in this checkout, not another shipped feature's notes/ path.
$ echo $?
1
```

Forged digest: `code_grade: n_a`, `reviewed: "9f87c48..9f87c48"` (FEAT-06's own,
perfectly honest, resolvable `review_sha`, named twice — a self-consistent range
that binds cleanly to FEAT-06 under the SHA check alone), `artifact:` pointed at
`.harness/harness/features/FEAT-06-team-layer-inv6/notes/review-whatever.md` — the
exact shape from the dispatch. Before this wave this validated (`digest ok`, exit 0,
per the wave-2 receipt's own repro of the SHA-only binding on this same shape).

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/.../honest-digest.txt
digest ok
$ echo $?
0
```

Honest digest: same shape, `reviewed:` and `artifact:` both naming FEAT-43 (this
feature's own, real, pinned `review_sha`, `94383e67...`) — accepted, confirming the
hardening does not reject a reviewer legitimately reporting on this checkout's own
feature.

**3. `python3 .claude/skills/harness/bin/code-grade.py .claude/skills/harness/bin/validate-digest.py`**
(paths mode)

Every function added or modified this wave grades 4 or better:

| qualname | grade |
|---|---|
| `_resolve_feature_dir` | 5 |
| `_read_review_sha` | 4 (unmodified body; unchanged from wave 2) |
| `_read_feature_branch` | 4 |
| `_current_branch_or_none` | 4 |
| `_branch_corroboration_error` | 5 |
| `resolve_review_sha` | 5 |
| `code_grade_bound_to_review` | 4 |

`validate()` measured `CYCLOMATIC: 102`, `GRADE: 1`, `RESULT: FAIL`, `SEVERITY: high`
— identical to the wave-2 receipt's own measurement (`101 -> 102`, all from wave 2's
own unavoidable `if`). This wave adds a parameter and a call-site argument to
`validate()`, neither a branch; the cyclomatic count is unchanged, confirming
`validate()` did not gain a branch. Pre-existing, out of scope, unchanged by this fix
(same ruling as the wave-2 receipt: a full decomposition of a 100+ branch dispatcher
is a separate, much larger effort than this hardening).

Not used as an acceptance gate: overall paths-mode exit status is 1 (multiple
pre-existing failing functions in this file — `strip_comment`, `split_items`,
`top_level_colon`, `bracket_depth`, `parse_digest`, `reviewed_python_change`,
`check_artifact_file`, `hook_mode`, `validate` — none touched by this wave).

**4. Mutation proof**

Mutated `_branch_corroboration_error`'s `if feature_branch == current_branch:` to
`if feature_branch != current_branch:` (inverted the one comparison the hardening
adds). Reran `test-validate-digest.py`: exactly the two dependent named cases failed,
nothing else:

- `cross-feature forgery (artifact: names a different feature and reuses ITS OWN
  honest review_sha) must reject, naming both branches (the SEC-01 residual hole)`
  (now wrongly ACCEPTED — the inverted mutation flips the reject to an accept)
- `the honest digest (artifact: names the feature actually under review) must
  accept` (now wrongly REJECTED, with the mutated message naming
  `'feat/checkout-under-test'` on both sides of the mismatch — the inverted mutation
  flips the accept to a reject)

Restored `if feature_branch == current_branch:` byte-identically via `cp` from a
pre-mutation snapshot (never `git checkout`). `md5sum` matched before mutation and
after restore (`26ae05f5ec7834810352e105e8f8de5b`). Reran suite: exit 0, `ALL
PASSED.` `git -C <worktree> status --porcelain` on both touched files shows only the
intended (non-mutation) diff remains — confirmed after every snapshot/restore cycle
in this run, including the separate RED-reproduction cycle in "Test-first" above.

## Design decisions

- **What corroborates**: `git rev-parse --abbrev-ref HEAD` (via the checkout root
  from `_root_or_none`, the existing FEAT-42 seam) against the resolved feature's
  OWN `feature.json` `branch` field — never a digest-supplied field. This is
  additive corroboration, not a second independent binding: it can only downgrade an
  accept to a reject.
- **Additive-only, proven three ways, not asserted**: (1) current branch
  undeterminable (`branch_override=None`) → no new rejection, (2) feature branch is
  the literal `none` → no new rejection, (3) every one of the ~115 pre-existing cases
  — none of which write a `branch` key in their `feature.json` fixtures at all — pass
  unchanged, because `_read_feature_branch` returns `None` for an absent key exactly
  as it does for the literal `"none"`, short-circuiting `_branch_corroboration_error`
  before any comparison runs.
- **Where the branch value comes from is NOT a digest field**: `branch_override`
  exists ONLY as a fixture-override seam (mirrors `feature_dir`/`config_path`); in
  production it is always `_BRANCH_UNSET`, meaning `_current_branch_or_none` always
  runs the real `git rev-parse --abbrev-ref HEAD`. A digest cannot spoof its own
  claimed branch through this mechanism the way it could through `artifact:` for
  SEC-01 wave 2 — there is no `branch:` digest field this reads.
- **`_resolve_feature_dir` factored out, not duplicated**: both the SHA half
  (`resolve_review_sha`) and the branch half (`code_grade_bound_to_review`) resolve
  the feature directory through the SAME function, so they can never derive two
  different features for the same digest — a duplicated derivation would have been a
  second seam to keep in sync and a second place for exactly this class of bug to
  reappear.
- **Mechanical note on this run's sequencing**: a transient hash-mismatch loop hit
  the edit tool when addressed by a relative path (it appears to have resolved
  against a different checkout than the absolute worktree path `read`/`bash` were
  using); switching to the absolute worktree path resolved it immediately, with no
  concurrent-editor involvement (confirmed with the sibling `ReviewShaBinding`, which
  had already yielded and was not writing). This delayed — but did not skip — the
  RED-before-GREEN sequence; both a fresh RED proof and the required mutation proof
  are included above.

## Open questions

- Same-branch, multiple-features residual: a digest validated on a checkout whose
  branch legitimately maps to MORE than one `feature.json` can still name any of
  those features' `artifact:` paths and pass this corroboration. Measured from this
  repo's own data: `feat/harness-native-foundation` is the recorded `branch` for both
  FEAT-02 and FEAT-03; `main` is the recorded `branch` for FEAT-06 (and plausibly
  other long-merged features sharing that trunk state). This is not closed by wave
  3 — it narrows the forgeable set from "any of 42 features" to "any feature sharing
  this checkout's branch," which for most feature branches is exactly one, but is not
  a universal guarantee. Flagged for the validator panel rather than closed here,
  per Rule 15.

## Verdict

```yaml
VERDICT: PASS
DIGEST:
  headline: SEC-01's residual cross-feature hole is closed for the concretely reachable path — code_grade's binding now additionally corroborates the resolved feature's recorded branch against the current checkout's actual git branch, rejecting a digest whose artifact: line names a different shipped feature while leaving every undeterminable-branch and branch-less-feature case, and every pre-existing SEC-01/SC-19/SC-20 case, accepted exactly as before
  tests_added: 4
  suite: pass
  task: T-08
  task_verify: pass
  blocked_on: none
  open_questions:
    - { id: Q1, question: "Same-branch multi-feature residual (feat/harness-native-foundation -> FEAT-02 and FEAT-03; main -> FEAT-06 and possibly others): should the validator panel accept this narrowed-but-not-closed guarantee, or is a stronger per-feature anchor (e.g. a feature-scoped worktree/branch-naming convention, or a digest-independent run-id binding) required?", blocking: false }
  files_touched:
    - .claude/skills/harness/bin/validate-digest.py
    - .claude/skills/harness/bin/test-validate-digest.py
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-remediate-c14-eng-s3b.md
```
