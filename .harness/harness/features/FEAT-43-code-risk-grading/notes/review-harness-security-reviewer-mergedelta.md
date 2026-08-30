# FEAT-43 merge-delta security review — SEC-01 re-discrimination + stale-ref ruling

Merge commit reviewed: `1d292c2b2e22486fd7ad47fa9021ddec880dabcb` (parents `cbdadef` feature,
`6d6d1ce` origin/main). Prior pin: `baa96b7ee1cfbc7fcbea8873692cc91751a0c171` (still
`feature.json`'s `review_sha` at time of this run). HEAD not moved; worktree left byte-identical
except this artifact (verified `git status --porcelain` before/after).

## BLUF

SEC-01 still discriminates correctly at the merged head, exactly as before the merge — the
automatic merge into `validate-digest.py` (+34/−8) never touched the SEC-01 machinery; it is
byte-identical to `baa96b7e` there. The stale/missing-`origin/HEAD` hazard is real but its
measured direction is **safe**: it only ever widens the reviewed range or refuses outright, never
narrows it. **No must_fix. PASS.**

**Send-back addendum (below): the one state I had not measured — `origin/HEAD`'s target
CONTAINING `review_sha` (the ordinary shape of the repo the moment this feature merges into
main) — is measured now, end-to-end. It is fail-closed, by an explicit, already-tested guard.
The hypothesized vacuous `n_a` grant does not occur. Ruling and severity unchanged: no
must_fix, PASS.**

## Item 2 — SEC-01 discrimination, re-run at the merged head

All four commands run as `python3 .claude/skills/harness/bin/validate-digest.py harness-code-reviewer <file>`
from the worktree, `PIN=baa96b7ee1cfbc7fcbea8873692cc91751a0c171`, `artifact:` pointed at this
review's own path so `_feature_dir_from_artifact` binds to FEAT-43's real `feature.json`.

| Case | `reviewed:` named | code_grade | Exit | Output |
|---|---|---|---|---|
| (i) forged, `pin..pin` | `PIN..PIN` | `n_a` | **1** | `VERDICT: BLOCKED (contract violation)` / `code_grade='n_a' is only valid when the reviewed diff has no Python file.` |
| (ii) forged, `pin~1..pin` | `PIN~1..PIN` | `n_a` | **1** | same message, verbatim |
| (iii) honest | `HEAD..PIN` | `fail` | **0** | `digest ok` |
| (iv) forged, wide arbitrary base | `7ebfc9e..PIN` (19 commits further back than (i)/(ii)) | `n_a` | **1** | same message, verbatim |

(i) and (ii) are both refused, exit 1, identical message — the forged no-op and its `~1` ancestor
variant are both inside the class SEC-01 wave 4 closes. (iii) proves the control is not a blanket
refusal: an honest `fail` claim is accepted, exit 0. (iv) is the discriminator for the load-bearing
property: **the range the digest NAMES does not change the answer.** Case (iv) names a
completely different, much wider base (`7ebfc9e`, an ancestor 19 commits before the base used in
(i)/(ii)) and still gets the *exact same* rejection, for the *exact same* reason — because the
`n_a` decision is never computed over the digest's stated range at all. It is computed over
`merge-base(origin/HEAD's target, review_sha)..review_sha`, a range the repository derives
independently (confirmed by reading `_derived_reviewed_python_change`,
`validate-digest.py:637-684`, unchanged by the merge — see Item 3(c)). Varying the digest's claim
three different ways (i, ii, iv) and getting one invariant verdict is the proof, not an inference
from reading the source.

## Item 3 — the stale/missing-`origin/HEAD` hazard

**(a) What the shipped code resolves, and its behaviour under each ref state — measured, not
argued.** `_default_branch_or_none()` (`validate-digest.py:597-619`) runs bare
`git symbolic-ref -q refs/remotes/origin/HEAD` (no `-C`) and returns the symref target or `None`.
This is the **only** ref FEAT-43's `n_a` derivation ever reads — it never touches local `main` at
all, so the orchestrator's own TRAP scenario (a shell gate literally computing
`merge-base(main, HEAD)` against the *stale local branch*) is a defect in some *other* script, not
in `validate-digest.py`. That distinction is confirmed by inspection; what needed an experiment is
what happens to *this* mechanism when the ref it *does* read is itself stale or absent, which the
orchestrator's brief also asked for. I built an isolated fixture — `git clone --mirror` of the
repo's common `.git` into a throwaway `/tmp` dir, `GIT_DIR`-pointed, refs mutated only inside that
copy, nothing in the worktree or the shared common `.git` touched — and imported the real,
unmodified `validate-digest.py` via `importlib` to call `_default_branch_or_none()` and
`_derived_reviewed_python_change("1d292c2...")` (the merge commit) directly, three ref states:

| State | `_default_branch_or_none()` | Derived range | python_changed | Result |
|---|---|---|---|---|
| FRESH (`origin/main`=`6d6d1ce`, true tip) | `refs/remotes/origin/main` | `6d6d1ce..1d292c2`, **40 commits** | `True` | decision made |
| STALE (`origin/main` forced back to ancestor `7ebfc9e`) | `refs/remotes/origin/main` | `7ebfc9e..1d292c2`, **59 commits** | `True` | decision made, over a **wider** range |
| MISSING (`origin/HEAD` symref deleted) | `None` | — | `None` | **refused**: `"code_grade='n_a' cannot be confirmed: this checkout's default branch (origin/HEAD) could not be resolved, ... this refuses the claim, it does not grant it."` |

`7ebfc9e` is confirmed (`git merge-base --is-ancestor 7ebfc9e 6d6d1ce` → true) to be a genuine
ancestor of the true tip, i.e. exactly the "haven't fetched recently" shape of staleness, not a
diverged/force-pushed ref. Under that shape the derived range only ever **grows** — 40 → 59
commits, +19, all main's own history between the stale point and the true tip — never shrinks.

**(b) Ruling (superseded — see the send-back addendum below for the complete, five-state
ruling).**

**(c) Did main's automatic +34/−8 merge change this?** No. `git diff baa96b7e HEAD --
.claude/skills/harness/bin/validate-digest.py` shows exactly three hunks, all inside `hook_mode()`
at lines 1392/1428/1450 — the `#551` claim-release plumbing (`_reg.live_children(..., feature=...)`,
`_reg.release_cmd(..., feature=...)`). Zero lines changed in `_default_branch_or_none`,
`_merge_base_or_none`, `_derived_reviewed_python_change`, or `code_grade_bound_to_review`
(lines 541–905) — that region is byte-identical to `baa96b7e`. `test-validate-digest.py`'s +3/−1
is likewise confined to `run_t09()`'s claim-shape read, not the SEC-01 test suite
(`check_reviewed_range`, `check_derived_base_range`, `check_review_sha_binding`, etc.). Ran
`python3 .claude/skills/harness/bin/test-validate-digest.py` at the merge head: **ALL PASSED, exit
0** (24/24 T-09 cases, 2/2 template cases, 18/18 reviewer severity_max checks, plus the SEC-01
suites folded into the same run) — no regression from the merge in either the SEC-01 code or its
coverage. This byte-identity is exactly what makes the send-back's untested state safe to settle
without re-running the full suite again: the guard that closes it (`base_oid == review_oid`,
`validate-digest.py:700-704`) sits inside this same untouched region.

**Severity (original, Item 3 only — see addendum for the final combined figure).**
The stale-ref widening is a real, reproducible nuisance (spurious findings attributed to
`origin/main`'s own unrelated files) but its direction is the safe one per the brief's own rule.

## Explicitly not covered

- Main's own content (the `#551` claim-release plumbing in `hook_mode()`, or main's other 24
  commits) was **not reviewed on its merits** — main merged on its own review; only whether the
  merge preserved FEAT-43's guarantees was in scope here.
- The eight previously-closed defects were not re-opened or re-reviewed.
- No canonical/project-wide suite was run — only `test-validate-digest.py` (targeted, directly
  relevant to this domain) and the ad hoc SEC-01 fixtures built for this review.
- No file in the worktree or the shared common `.git` was mutated; all ref manipulation happened in
  a throwaway `git clone --mirror` under `/tmp`, deleted after use.

---

## Send-back addendum — the narrowing state: `origin/HEAD`'s target CONTAINS `review_sha`

**Why this state matters and was missing.** My original Item 3 fixture tested FRESH, STALE
(ancestor of the tip — widens), and MISSING (explicit refusal). It never tested the fourth,
dangerous shape: `origin/HEAD`'s target has **advanced past** `review_sha` — the ordinary state of
this very repo the moment FEAT-43 merges into main and anyone fetches. In that shape
`merge-base(default, review_sha)` collapses to `review_sha` itself, so if nothing catches it, the
derived range is empty and `n_a` would be granted on a range that reviewed nothing. My own BLUF
sentence — "no code path anywhere returns a false nothing-changed from an unresolved default
branch" — was true and answered a different question (the *unresolved* branch case) than the one
the brief asked (a *resolved* branch that has moved past the pin). This addendum measures that
state directly, plus the diverged/force-push shape, using the same `/tmp` `git clone --mirror`
technique, extended.

**Fixture.** Rebuilt the mirror clone of the shared `.git` into a fresh `/tmp` dir,
`GIT_DIR`-pointed, `refs/remotes/origin/HEAD` re-pointed at `refs/remotes/origin/main` (the mirror
clone does not preserve the symref shape itself — confirmed and corrected before use). All
mutation confined to that mirror; nothing in the worktree or the shared `.git` touched (verified
`git status --porcelain` unchanged, `HEAD` unmoved at `1d292c2`, before and after).

**Descendant/contains state.** Synthesized one honest commit on top of the merge with
`git commit-tree <1d292c2's tree> -p 1d292c2` (same tree, new commit — a minimal, honest
descendant), then `git update-ref refs/remotes/origin/main <synthetic>`. Confirmed
`git merge-base --is-ancestor 1d292c2 <synthetic>` → true: `origin/main`'s new target is a real
descendant of the merge commit.

Direct helper calls (`_default_branch_or_none()`, `_derived_reviewed_python_change('1d292c2...')`)
against that fixture:

```
default_ref: refs/remotes/origin/main
derived result: (None, "code_grade='n_a' cannot be confirmed: review_sha (1d292c2b2e22486fd7ad47fa9021ddec880dabcb) is
already an ancestor of the default branch, so the derived review range is empty BY CONSTRUCTION —
that is zero evidence nothing changed, not proof that it didn't.")
```

The derived range is **empty by construction** (`base_oid == review_oid`), `python_changed` is
never computed (short-circuited to `None`) — but the function does **not** treat that as "nothing
changed" and grant `n_a`. It returns the named refusal above. This is not incidental: it is a
distinct, explicitly-coded branch at `validate-digest.py:700-704`, and it is the exact same branch
already covered by the pre-existing hermetic regression test `check_derived_base_range`'s
`FEAT-DERIVED-DEGENERATE` case (`test-validate-digest.py:2196-2201`, asserting the substring
"already an ancestor of the default branch") — which construction hits the identical
`base_oid == review_oid` condition via `review_sha == origin/main`'s tip exactly, rather than one
commit further ahead. My fixture is the strictly-more-general form the send-back asked for
(default branch strictly *past* the pin, not merely equal to it) and it hits the same code path
with the same result.

**End-to-end.** Called `validate("harness-code-reviewer", digest, config, feature_dir)` — the
exact function the CLI's `__main__` invokes — with a fixture `feature_dir` (`/tmp`, the
codebase's own documented "fixture-override seam for tests", the same seam
`test-validate-digest.py` uses throughout) carrying `review_sha = 1d292c2b2e22486fd7ad47fa9021ddec880dabcb`,
and a digest claiming:

```yaml
code_grade: n_a
reviewed: "1d292c2~1..1d292c2"   # head resolves to review_sha, satisfies SEC-01 binding
```

under the descendant `GIT_DIR` fixture above. Result, quoted verbatim:

```
errs: ["code_grade='n_a' cannot be confirmed: review_sha (1d292c2b2e22486fd7ad47fa9021ddec880dabcb) is already an
ancestor of the default branch, so the derived review range is empty BY CONSTRUCTION — that is zero evidence
nothing changed, not proof that it didn't."]
=== END-TO-END RESULT: REFUSED (exit 1 equivalent) ===
VERDICT: BLOCKED (contract violation)
  - code_grade='n_a' cannot be confirmed: review_sha (1d292c2b2e22486fd7ad47fa9021ddec880dabcb) is already an
    ancestor of the default branch, so the derived review range is empty BY CONSTRUCTION — that is zero evidence
    nothing changed, not proof that it didn't.
```

**Refused. Exit-1-equivalent** (the CLI's `__main__` prints exactly this `VERDICT: BLOCKED
(contract violation)` line and each `err` for a non-empty `errs`, and `sys.exit(1)`). The `n_a`
gate is **not** fail-open in the descendant/contains state. The hypothesis in the send-back —
that this state grants `n_a` vacuously — does not hold; it was a reasonable and correctly-targeted
thing to ask for given what my BLUF sentence *didn't* say, but the measurement refutes it.

**Diverged/force-push state.** Built a genuine divergence: a second synthetic commit off the
*same* parent the merge commit itself descends from (`6d6d1ce`, confirmed via
`git log --pretty=%P -1 1d292c2` → parents `cbdadef 6d6d1ce`), and pointed `origin/main` at it.
Confirmed neither commit is an ancestor of the other
(`merge-base --is-ancestor` both directions → false) and
`git merge-base <diverged> 1d292c2` → `6d6d1ce` — a genuine, non-degenerate common ancestor.

Direct helper call: `default_ref` resolves; `_derived_reviewed_python_change` returns
`(True, None)` — decision made, over `6d6d1ce..1d292c2`, **40 commits** (rev-list count,
confirmed), identical to the FRESH baseline in the original Item 3 table. This is expected and
correct: divergence downstream of the true merge-base cannot move the merge-base itself, so the
derived range can never collapse or narrow from a force-push shape — it can only ever match the
honest range or (if the divergence point were further back in history) widen it, symmetric to the
STALE case already measured.

End-to-end, same digest/fixture shape as above, under the diverged `GIT_DIR`:

```
errs: ["code_grade='n_a' is only valid when the reviewed diff has no Python file."]
=== END-TO-END RESULT: REFUSED (exit 1 equivalent) ===
```

**Refused** — correctly: Python genuinely changed in the true `6d6d1ce..1d292c2` range, so an
`n_a` claim is rightly rejected. This is not a hazard; it is the control working as designed.

### Re-issued Item 3 ruling — all five states

| State | Derived range | python_changed | Verdict on an `n_a` claim | Classification |
|---|---|---|---|---|
| FRESH (`origin/main` = true tip `6d6d1ce`) | `6d6d1ce..1d292c2`, 40 commits | `True` | refused ("only valid...") | baseline — correct, accurate decision |
| STALE-ANCESTOR (`origin/main` behind, at a real ancestor `7ebfc9e`) | `7ebfc9e..1d292c2`, 59 commits | `True` | refused | **fail-closed in effect** — range only ever widens (40→59), never narrows |
| MISSING (`origin/HEAD` unresolvable) | — | `None` | refused, named error | **fail-closed by construction** — explicit refusal, no derivation attempted |
| CONTAINS/DESCENDANT (`origin/main` past the pin, review_sha an ancestor of it) | empty, degenerate (`base_oid == review_oid`) | never computed | refused, named error, **measured end-to-end** | **fail-closed by construction** — explicit `base_oid == review_oid` guard (`validate-digest.py:700-704`), pre-existing test coverage (`FEAT-DERIVED-DEGENERATE`) plus this addendum's strict-descendant variant |
| DIVERGED (force-push shape, real common ancestor, neither side descends from the other) | `6d6d1ce..1d292c2`, 40 commits (== FRESH) | `True` | refused | **fail-closed** — merge-base is unaffected by downstream divergence; range cannot narrow below the true history |

**Overall ruling for the `n_a` gate:** across all five measured ref states — fresh, an ancestor
staleness, an unresolvable ref, a descendant/contains staleness, and a diverged/force-pushed ref —
the `n_a` gate is **fail-closed**. It never grants `n_a` on a degenerate or empty derived range;
the `base_oid == review_oid` check is the specific guard that closes exactly the state this
send-back named, and it holds under direct-helper measurement, under the pre-existing hermetic
test, and under a fresh end-to-end `validate()` call built for this addendum.

**Is the descendant/contains state reachable in normal operation?** Yes — emphatically. It is not
an edge case: it is the literal state of `origin/main` the moment this very merge commit lands on
main and any checkout fetches (`origin/main` then equals `1d292c2` exactly, the boundary case of
the same guard; my fixture pushed one commit further to test the strictly-more-general shape).
That is exactly why it needed measuring rather than reasoning about, per the brief. It is measured
safe.

**Whose fix would this have been, had it failed?** FEAT-43's, without qualification — not
inherited. `_derived_reviewed_python_change` and its `base_oid == review_oid` degeneracy guard
are wave-4 code this feature wrote (the docstring at `validate-digest.py:637-660` names the
guard as one of three explicit fail-closed conditions "SEC-01 wave 4" adds), not a pre-existing
mechanism FEAT-43 merely called into. There is no older derivation this collapsed from. Moot here
only because the measurement shows the guard already holds — but ownership, if it hadn't, would
not have been in question.

**Severity.** Unchanged from the original Item 3 finding, now confirmed complete: the only real
hazard across all five states is the STALE-ANCESTOR/DIVERGED **widening** direction (spurious
findings attributed to `origin/main`'s own unrelated files) — safe per the brief's own rule ("a
stale remote-tracking ref that silently WIDENS the reviewed range is worth a backlog row"). The
narrowing direction the brief specifically flagged as a `must_fix` candidate does **not** occur —
measured, not argued, in both a hermetic unit call and a full end-to-end `validate()` invocation.
**Severity: `low`. Backlog row (the widening nuisance only), not `must_fix`.**

```yaml
VERDICT: PASS
DIGEST:
  headline: "SEC-01's n_a gate is fail-closed across all five measured origin/HEAD states — including the descendant/contains narrowing state the send-back named, confirmed end-to-end; only the widening backlog row stands"
  in_scope: true
  scope_reason: "validate-digest.py's SEC-01 control is a trust boundary on the review record itself, and its merge into that file was automatic (nobody resolved it by hand) — exactly the security-reviewer's remit"
  severity_max: low
  findings: 1
  must_fix: []
  threat_model:
    - { boundary: "review-record integrity (forged code_grade/reviewed range vs feature.json review_sha)", stride: T, mitigated: true }
    - { boundary: "default-branch ref resolution for the n_a derived range (origin/HEAD staleness, absence, descendant/contains narrowing shape, and divergence)", stride: T, mitigated: true }
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/review-harness-security-reviewer-mergedelta.md
```
