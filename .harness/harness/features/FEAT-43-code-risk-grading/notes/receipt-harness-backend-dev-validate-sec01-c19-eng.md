# Receipt — SEC-01 wave 4 closure (validate-sec01-c19)

**BLUF:** SEC-01 is closed as a CLASS, per Q8's binding ruling. `code_grade: n_a`'s
decision no longer reads the digest's own `reviewed:` field at all — it comes from
`merge-base(<default branch>, review_sha)..review_sha`, a range the repository
derives with no digest input and no new `feature.json` field. The literal QA-note
forged digest (`review_sha..review_sha`) and its `~1` variant both now reject at
exit 1; `pass`/`fail`/`grade_2` stay ungated on base derivation, proven with a real
checkout that genuinely cannot resolve a default branch. `code_grade_bound_to_review`
(the head↔review_sha binding) is untouched. HEAD is still `34a49c4b78c74…`, tree
uncommitted, no scratch files in the repo.

## What changed

- `validate-digest.py`: added `_default_branch_or_none`, `_merge_base_or_none`,
  `_derived_reviewed_python_change` (~line 597-682), and rewired the
  `code_grade == "n_a"` branch inside `validate()` (~line 1137-1154) to decide from
  the derived range via `resolve_review_sha` + `_derived_reviewed_python_change`,
  discarding — not deciding on — `reviewed_python_change(seen.get("reviewed"))`'s
  boolean (kept only for its shape/injection-safety check, unchanged wording).
  `code_grade_bound_to_review` and `reviewed_python_change` are byte-identical to
  HEAD — confirmed by re-running the mutation/restore diff below.
- `test-validate-digest.py`: `REVIEW_SHA` now points at this feature's own real
  `review_sha` (`94383e67…`) instead of aliasing `PRE_FEATURE_REVISION`, because the
  new tests need a pin whose TRUE derived range genuinely changes Python. Inverted
  `check_reviewed_range`'s `honest_no_op` case (now `_assert_n_a_rejects`) to expect
  REJECT, added the `~1` variant, added `check_derived_base_range` (real, purpose-built
  `/tmp` git repo — accept/reject/degenerate) and `check_unresolvable_default_branch`
  (real checkout with no `origin/HEAD`, proving pass/fail/grade_2 stay ungated).
  Decoupled `check_branch_corroboration`'s `forged`/`no_branch` fixtures from
  `code_grade: n_a` (switched to `pass`) since their `review_sha="HEAD"` now
  genuinely has Python changes under wave 4 and isn't what branch-corroboration
  is testing.

## Design decision: cwd (`.`) basis, not `_root_or_none()`

All new git plumbing (`_default_branch_or_none`, `_merge_base_or_none`, and the
final `reviewed_python_change(f"{base_oid}..{review_oid}")` delegate) is bare `git`
with no `-C`, deliberately matching `resolve_reviewed_commit`'s existing
`commit_oid(".", revision)` cwd basis — not `_root_or_none()`. Reason: the head/pin
commits `code_grade_bound_to_review` already binds are resolved against cwd; the
derived base must agree with those SAME commits in the SAME repository, or the
comparison is meaningless. `_root_or_none()` stays reserved for the
directory-shaped feature.json/artifact-path lookups it already served
(`_resolve_feature_dir`, branch corroboration) — a different concern (which
`.harness/…/FEAT/` a review belongs to), never git commit resolution.

## Q8 fidelity

- Rejected the ranked minimal remedy (`base == head`) per Q8 — not implemented.
- The digest's `reviewed:` field never decides `n_a`; its only remaining role is a
  shape/injection-safety check (unchanged), discarding the boolean.
- `pass`/`fail`/`grade_2` never call the new derivation — verified live by
  `check_unresolvable_default_branch`, not asserted.
- Degenerate range (review_sha already an ancestor of default branch) REFUSES with
  its own, distinctly-worded error ("already an ancestor of the default branch"),
  never accepts.

## RED, before the fix (verbatim)

Ran the new/changed test cases against `HEAD`'s committed `validate-digest.py`
(copied to a scratch dir alongside its unmodified sibling modules, `VALIDATE_DIGEST_BIN`
override — the file's own convention):

```
FAIL  code-grade and review-policy gates
        a forged no-op AT review_sha itself must reject — the n_a decision must never read the digest's own reviewed:
        a forged no-op AT review_sha whose TRUE derived range changed Python must still reject: []
        a review_sha already merged into the default branch must refuse with its own named error: []
        n_a with an unresolvable default branch must refuse: []
```
(The `~1` unit-test variant didn't independently fail pre-fix — that specific
single real commit happens to touch `.py` on its own, so the OLD digest-named diff
caught it by coincidence; the mutation proof below closes that gap definitively.)

## GREEN, after the fix

`python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL PASSED`, exit 0.

## The exact QA-note forged digest, live, before/after (verbatim commands + exit)

Reconstructed `reviewed: "94383e67…94383e67"`, `code_grade: n_a`, artifact pointing
at this feature's own notes — the literal security-reviewer panel shape.

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe/forged_pin_pin.txt
```
- **BEFORE** (HEAD's committed file, swapped in-place via `cp`, restored after):
  `digest ok` — **EXIT=0**
- **AFTER** (current fix): `VERDICT: BLOCKED (contract violation) - code_grade='n_a'
  is only valid when the reviewed diff has no Python file.` — **EXIT=1**

Also reproduced the `~1` variant (`94383e67~1..94383e67`) live: **EXIT=1**, same
message.

## Mutation proof (binds — performed twice, same result)

- md5 of `validate-digest.py` before: `42297a46503d1331c020b0e75b3385c9`.
- Mutation: `return reviewed_python_change(f"{base_oid}..{review_oid}")` →
  `return False, None` (unconditionally claims "no Python changed", disabling the
  whole derived-range decision).
- `python3 .claude/skills/harness/bin/test-validate-digest.py` against the mutant:
  exit 1, exact failing lines:
  ```
  FAIL  code-grade and review-policy gates
          n_a with a reviewed Python diff must reject
          a forged no-op AT review_sha itself must reject — the n_a decision must never read the digest's own reviewed:
          <review_sha>~1..<review_sha> is inside the class Q8 closes and must also reject
          a forged no-op AT review_sha whose TRUE derived range changed Python must still reject: []
          <review_sha>~1..<review_sha> against a real repo must also reject: []
  ```
- Restored via `cp` from a pre-mutation backup (never `git checkout`/`git restore`).
  md5 after restore: `42297a46503d1331c020b0e75b3385c9` — matches. `git status
  --porcelain -- .../validate-digest.py` after restore shows only my own
  in-progress diff against HEAD (` M`), not the mutation. Re-ran green: `ALL
  PASSED`, exit 0.

## Suites (each run independently, exit status reported)

| suite | exit |
|---|---|
| `test-validate-digest.py` | 0 (`ALL PASSED`) |
| `test-code-grade.py` | 0 (`PASS test-code-grade`) |
| `test-code-grade-cli.py` | 0 (`PASS test-code-grade-cli`) |
| `test-gate-policy.py` | 0 |
| `test-check-plan-routes.py` | 0 (`ALL PASS`) |

CR-01/CR-02/UI-01 undisturbed: no file outside `validate-digest.py` /
`test-validate-digest.py` touched; `test-code-grade.py`'s self-grading (CR-01's
own guard) passes unchanged — I did not touch its `SELF_GRADING_ALLOWLIST`, and
didn't need to (see grading below).

## Per-qualname grades (every function I added or changed)

`validate-digest.py` (production, bar 4), via `code-grade.py`:

| qualname | grade | note |
|---|---|---|
| `_default_branch_or_none` | 5 | new |
| `_merge_base_or_none` | 5 | new |
| `_derived_reviewed_python_change` | 4 | new, clears bar exactly |
| `resolve_reviewed_commit` | 5 | **unchanged**, byte-identical to HEAD |
| `reviewed_python_change` | 2 (allowlisted) | **unchanged**, byte-identical to HEAD — no staleness introduced in `test-code-grade.py`'s allowlist since its body never moved |
| `validate` | 1 (allowlisted) | pre-existing grade-1 floor; adding straight-line calls inside the `n_a` branch cannot push it lower than 1, confirmed by measurement |

`test-validate-digest.py` (test file, bar 3), via `code-grade.py`:

| qualname | grade |
|---|---|
| `_assert_n_a_rejects` | 5 |
| `_check_option_like_revisions` | 4 |
| `check_reviewed_range` | 5 |
| `_assert_derived_accepts` | 5 |
| `_assert_derived_rejects` | 5 |
| `check_derived_base_range` | 4 |
| `_assert_ungated_grade` | 5 |
| `_assert_fail_ungated` | 5 |
| `check_unresolvable_default_branch` | 3 (clears bar exactly) |

`test-code-grade.py` (CR-01's own self-grading guard) exits 0 confirming no
allowlist staleness anywhere in either touched file.

## Tree state

```
$ git -C <worktree> rev-parse HEAD
34a49c4b78c74cac6676ec91d7cb7f262abf19e7
```
Working tree uncommitted; only `validate-digest.py` and `test-validate-digest.py`
carry my edits (plus pre-existing, not-mine modifications to `STATE.md`/
`feature.json` and untracked prior receipts/answers). No scratch files left in the
repo — all probes/backups under `/tmp`.

## Open questions

None. Q8's ruling was unambiguous once measured; no design choice here needed
operator input.

## Send-back 1 — ambient-repo assertion durability

**BLUF:** the lead's assessment was correct and reproducible — confirmed live, not
argued. `check_reviewed_range`'s three `n_a` cases, run against this repo's real
ambient state, pinned the single substring `"only valid"`; that reason is a
function of `merge-base(origin/HEAD, REVIEW_SHA)`, and the moment FEAT-43 lands
on `main` (REVIEW_SHA becomes an ancestor of `origin/main`) the SAME correct fix
refuses with a different, equally valid reason ("already an ancestor of the
default branch"), failing all three assertions on a tree where SEC-01 works
perfectly. Fixed by asserting the CONTRACT (an `n_a` refusal, for one of wave-4's
own named reasons) instead of one specific reason. `validate-digest.py` untouched
— confirmed by md5, matches predecessor's own recorded hash.

### Proving the time bomb before defusing it

Constructed the exact post-merge condition without moving HEAD or merging
anything: `git clone --shared` of the worktree into `/tmp/sec01_timebomb_clone`
(independent refs, shared objects — REVIEW_SHA is a real commit already in this
repo's object store), then forced `refs/remotes/origin/main` directly to
REVIEW_SHA and `refs/remotes/origin/HEAD` to point at it — the degenerate range
FEAT-43's own eventual non-squash merge produces (review_sha trivially an
ancestor of itself). A standalone repro script
(`/tmp/sec01_timebomb_repro.py`, deleted after use, never inside the repo)
imported the actual `test-validate-digest.py` and `validate-digest.py` from the
worktree, chdir'd into the clone, and called `check_reviewed_range` directly
against the real validator.

**BEFORE (pre-fix `test-validate-digest.py`, worktree's committed edits at the
time of the send-back), verbatim:**
```
FAIL check_reviewed_range under simulated post-merge state:
        n_a with a reviewed Python diff must reject
        a forged no-op AT review_sha itself must reject — the n_a decision must never read the digest's own reviewed:
        <review_sha>~1..<review_sha> is inside the class Q8 closes and must also reject
EXIT=1
```
All three assertions failed, live, on a tree where the fix is correct — exactly
the phantom failure the lead named, reproduced before any edit.

**AFTER (this fix), same repro, same clone, same script:**
```
ok    check_reviewed_range under simulated post-merge state
EXIT=0
```

### The fix

`test-validate-digest.py`:
- Added a module-level constant `N_A_REFUSAL_SUBSTRINGS` (line 1870, just above
  `_assert_n_a_rejects`) — the union of wave-4's own named `n_a` refusal
  reasons (`"only valid"`, `"already an ancestor of the default"`,
  `"default branch"`, `"no merge base"`), each traced to its exact producing
  string in `validate-digest.py` (lines 661, 672-673, 678-679, 1154). Expressed
  ONCE, with a comment explaining why the reason is environment-dependent here
  and hermetic elsewhere — not scattered as an `or` chain across the three call
  sites in `check_reviewed_range`, which are unchanged.
- Rewrote `_assert_n_a_rejects` to assert `any(substring in error for error in
  errors for substring in N_A_REFUSAL_SUBSTRINGS)` instead of the bare
  `"only valid"` substring — never a bare `if errors:` (would pass vacuously on
  an unrelated schema rejection, the exact failure mode the substring match
  exists to prevent). Failure messages now also print the actual `errors` list,
  since "which n_a reason fired" is no longer implied by the assertion itself.
- Updated the `REVIEW_SHA` constant's comment (~line 1727) to state plainly that
  `check_reviewed_range`'s ambient cases no longer depend on REVIEW_SHA's
  derived range "genuinely changing Python" as a property their assertions
  need — that dependency is what made them fragile — and points at
  `N_A_REFUSAL_SUBSTRINGS` and the two hermetic tests for where the exact-reason
  discrimination now lives.

### Exact-reason discrimination not lost — confirmed hermetic, not just claimed

Read `check_derived_base_range` (lines 1987-2037) and
`check_unresolvable_default_branch` (lines 2055-2088) directly, both unchanged
by this send-back:
- `check_derived_base_range`, against a purpose-built `/tmp` repo with a real
  `origin/HEAD`: pins `"only valid"` exactly (line 2020) for the forged no-op
  whose true range changed Python, and pins `"already an ancestor of the
  default branch"` exactly (line 2031) for the degenerate case.
- `check_unresolvable_default_branch`, against a real checkout with no
  `origin/HEAD` at all: pins `"default branch"` exactly (line 2083).

`"no merge base"` (validate-digest.py:672-673, an unresolvable merge base with
a resolvable default branch — distinct from no `origin/HEAD` at all) is NOT
currently pinned hermetically anywhere in the suite; it was not pinned before
this send-back either (the old ambient assertions matched it only by accident,
via the "only valid" substring never appearing and the case being untested).
Adding a hermetic repro for it (a real repo with `origin/HEAD` resolvable but
`review_sha` sharing no history at all with the default branch — an orphan
branch) is real, addable work but is out of the change this send-back
specifies: the task names three call sites and a comment, not a new hermetic
case. Flagged as `Q1` below rather than silently added or silently dropped.

### Suites and probes (each run independently, exit status reported)

| check | command | exit |
|---|---|---|
| full suite | `python3 .claude/skills/harness/bin/test-validate-digest.py` | 0 (`ALL PASSED`) |
| `test-code-grade.py` | same | 0 (`PASS test-code-grade`) |
| `test-code-grade-cli.py` | same | 0 (`PASS test-code-grade-cli`) |
| `test-gate-policy.py` | same | 0 |
| `test-check-plan-routes.py` | same | 0 (`ALL PASS`) |

Live forged-digest probe, re-run verbatim against this fix:
```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe/forged_pin_pin.txt
VERDICT: BLOCKED (contract violation)
  - code_grade='n_a' is only valid when the reviewed diff has no Python file.
EXIT=1
```
Still non-zero — the closure is not loosened.

### Per-qualname grades (via `code-grade.py`, test-file bar 3)

| qualname | grade | note |
|---|---|---|
| `_assert_n_a_rejects` | 5 | changed body; unchanged from predecessor's own grade (5) |
| `check_reviewed_range` | 5 | call sites untouched; unchanged from predecessor's own grade (5) |

`code-grade.py` on the whole file reports pre-existing FAILs (`run_cli_cases`,
`run_t09`, `run_hook_cases`) — none touched by this send-back, all present
before this send-back and outside its scope. No allowlist entry needed or
added.

### Tree state

`git status --porcelain -- .../validate-digest.py` → ` M`, md5
`42297a46503d1331c020b0e75b3385c9` before and after this send-back — matches
the predecessor's own recorded hash exactly; I did not touch it.
`git status --porcelain -- .../test-validate-digest.py` → ` M` (my edits only).
`git rev-parse HEAD` → `34a49c4b78c74cac6676ec91d7cb7f262abf19e7`, unchanged.
No scratch files added to the repo — the `/tmp` clone and repro script were
both deleted after use.

### Open questions

- `{ id: Q1, question: "check_derived_base_range/check_unresolvable_default_branch
  pin three of wave-4's four n_a refusal reasons hermetically; \"no merge base\"
  (an unresolvable merge base with a RESOLVABLE default branch — e.g. an orphan
  review_sha branch) is pinned nowhere, ambiently or hermetically, before or
  after this send-back. Worth a fourth hermetic case (real /tmp repo, orphan
  branch, no shared history with origin/main)?", blocking: false }

## Send-back 2 — the fourth refusal branch (member Q1, ruled)

**BLUF:** all four of `_derived_reviewed_python_change`'s fail-closed `n_a`
refusal reasons are now pinned hermetically — the fourth ("no merge base
between the default branch and review_sha could be computed",
`validate-digest.py:672-673`) had no test of its own before this send-back;
it does now. `validate-digest.py` untouched — confirmed by md5 both before
and after, matches every prior recorded hash exactly.

### The fix

`test-validate-digest.py`:
- Added `make_orphan_review_repo(td)` (a real, purpose-built `/tmp` repo:
  `main`/`origin/main`/`origin/HEAD` resolve fine, and `review_sha` sits on
  a genuine `git checkout --orphan` branch sharing no commit history with
  `main` at all — `git merge-base` itself returns nothing, against real
  plumbing, never a stub).
- Added `check_no_merge_base(td, failures)`, wired into
  `run_code_grade_cases()` immediately after `check_unresolvable_default_branch`.
  It reuses `_assert_derived_rejects` (unchanged) to pin `code_grade: n_a`
  REFUSED with `"no merge base"` for the orphan pin, and additionally
  asserts the discrimination Q1 named: `code_grade: pass` for the SAME
  orphan pin in the SAME repo is still ACCEPTED — proving the refusal is
  narrow to `n_a`'s own derivation, the same ungated property
  `check_unresolvable_default_branch` already proves for the sibling
  ("no `origin/HEAD` at all") branch. No new assertion helper was needed for
  the `pass` half; it is four lines of direct `validator.validate(...)` +
  `if errors:` inline in the check function, since the only existing
  candidate (`_assert_ungated_grade`) hardcodes an "unresolvable default
  branch" wording that is factually wrong here (the default branch resolves
  fine; only the merge base doesn't), and reusing it would have pinned a
  misleading failure message.

### RED, before the fix (mutation, not absence — the behaviour already
### existed; only its test didn't)

md5 of `validate-digest.py` before: `42297a46503d1331c020b0e75b3385c9`.
Mutation: the `no merge base` refusal (`if base_oid is None: return None,
(...)`) → `if base_oid is None: return False, None` (unconditionally claims
"no Python changed" instead of refusing). Ran the new test against the
mutant:

```
$ python3 .claude/skills/harness/bin/test-validate-digest.py
FAIL  code-grade and review-policy gates
        n_a on an orphan review_sha with no merge base to the default branch must refuse: []
1 FAILING.
EXIT=1
```

Exactly the new case, failing by name, message quoted verbatim (`errors`
came back `[]` — the mutant silently accepted). Restored via `cp` from a
`/tmp` backup taken before the mutation (never `git checkout`/`git
restore`). md5 after restore: `42297a46503d1331c020b0e75b3385c9` — matches.
`git status --porcelain -- .../validate-digest.py` after restore shows only
the pre-existing ` M` against HEAD from wave 4's own committed fix, not the
mutation.

### GREEN, after restore

`python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL
PASSED`, **EXIT=0**.

### Live forged-digest probe, re-run

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer /tmp/sec01probe/forged_pin_pin.txt
VERDICT: BLOCKED (contract violation)
  - code_grade='n_a' is only valid when the reviewed diff has no Python file.
EXIT=1
```
Still non-zero.

### Suites (each run independently, exit status reported)

| suite | exit |
|---|---|
| `test-validate-digest.py` | 0 (`ALL PASSED`) |
| `test-code-grade.py` | 0 (`PASS test-code-grade`) |
| `test-code-grade-cli.py` | 0 (`PASS test-code-grade-cli`) |
| `test-gate-policy.py` | 0 |
| `test-check-plan-routes.py` | 0 (`ALL PASS`) |

`test-code-grade.py`'s self-grading guard (CR-01's own check) exits 0 —
confirms no allowlist staleness was introduced.

### Per-qualname grades (via `code-grade.py`, test-file bar 3)

| qualname | cyclomatic | ABC | grade | note |
|---|---|---|---|---|
| `make_orphan_review_repo` | 1 | 8.5 | 4 | new, clears bar |
| `check_no_merge_base` | 2 | 16.7 | 4 | new, clears bar |

No allowlist entry added or needed.

### All four `n_a` refusal reasons, now pinned hermetically

For the record: every one of `_derived_reviewed_python_change`'s four
fail-closed refusal reasons now has its own real, purpose-built `/tmp`-repo
test, never a stub of the function under test:

| refusal reason | producing lines | hermetic test |
|---|---|---|
| default branch unresolvable (no `origin/HEAD`) | 658-663 | `check_unresolvable_default_branch` |
| `review_sha` does not resolve to a commit | 664-668 | not independently hermetic (shape-checked earlier by `reviewed_python_change`'s own resolvability check; the merge-base path is unreachable without a resolvable `review_oid`) — unchanged by this send-back, out of Q1's scope |
| no merge base between default branch and `review_sha` | 670-675 | `check_no_merge_base` (this send-back) |
| degenerate range (`review_sha` already an ancestor of the default branch) | 676-681 | `check_derived_base_range` |

Q1 named the third row specifically; it is closed. The second row's
resolvability check is a distinct, narrower condition (a malformed/unknown
`review_sha` string) already covered by existing shape/resolvability tests
elsewhere in this file and was not raised by Q1 or the dispatch — flagged
here for completeness, not treated as in scope.

### Tree state

```
$ git -C <worktree> rev-parse HEAD
34a49c4b78c74cac6676ec91d7cb7f262abf19e7
```
`validate-digest.py`: md5 `42297a46503d1331c020b0e75b3385c9` before this
send-back and after — byte-identical, confirmed both ways, matches every
prior receipt's recorded hash. Working tree uncommitted; only
`test-validate-digest.py` carries my edits in this send-back (plus the
predecessor's own pre-existing, unchanged `validate-digest.py` diff against
HEAD). No scratch files left in the repo — the `/tmp` md5 backup and mutant
run artifacts were deleted after use.

### Open questions

None. Q1 is answered by construction — a fourth hermetic case, following
the exact shape of its three siblings.
