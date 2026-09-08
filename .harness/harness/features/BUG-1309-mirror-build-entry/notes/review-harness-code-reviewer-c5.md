# Code review — BUG-1309-mirror-build-entry — cycle 5 (tri-state pin)

reviewed: `6ad7233f..473d82cb8442ac4ec5ca84566f5635f046ab723f` (merge-base(origin/main, review_sha)..review_sha)
Diff of the pinned commit itself (`473d82cb^..473d82cb`): `.claude/skills/harness/bin/merge-gate.py` (+8/-4), `tests/integration/test-merge-gate.py` (+6).

## BLUF

Stage 1 PASS, Stage 2 **FAIL**. One `must_fix`, high: the new `unusable` sentinel in
`feature_for` is scanned across the **entire** `.harness/*/features/*/feature.json` glob, not
scoped to the branch under evaluation, so it denies merges for branches that own **no** feature
record at all whenever some unrelated feature's record is malformed. Demonstrated by execution
(pre/post pin divergence below): this is a real regression this exact commit introduces, distinct
from the settled/closed cross-feature DoS (that one denied every branch via an uncaught exception
and was closed at `af132780`; this one is narrower — only unmatched branches — and is new at
`473d82cb`). Everything else checked out clean: all four required states hold together in one
fixture, the sentinel never goes stale on a same-branch healthy/unusable pair regardless of glob
order, `feature_for` has no other caller, no sibling gate shares this code, the new deny path is
unreachable without at least one malformed record, and `test-merge-gate.py` (19/19) plus code-grade
(clean apart from four pre-reasoned grade-2 functions) are both green.

## 1. Four states, one fixture (`/tmp` fixture, `merge-gate.sh` end to end)

All four held **simultaneously** in one temp root (features `FEAT-A-healthy`,
`FEAT-B-unrelated-malformed`, `FEAT-C-owing`, `FEAT-E-owes-nothing`, then `FEAT-D-selfbad` added
after and (a)/(b)/(d) re-run unchanged — no pairwise conflict):

- (a) healthy match + unrelated malformed record, `git merge feature/healthy` → `rc=0, decision=None, stdout='', stderr=''` — silent ALLOW.
- (b) matched feature, own plan.yaml 0 bytes, `git merge feature/owing` → `rc=0, decision=deny, reason="merge-gate: could not evaluate FEAT-C-owing's Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge."`
- (c) branch whose only candidate record is unusable, `git merge <branch>` → `rc=0, decision=deny, reason="merge-gate: could not evaluate a feature's Build-entry receipt, so this merge is denied. Repair the malformed feature record and re-run the merge."`
- (d) `gh pr merge 99` with `GH_BIN=/nonexistent/gh`, local-branch fallback owes nothing → `rc=0, decision=None, stderr="merge-gate: could not verify this merge - the head branch could not be resolved through gh ([Errno 2] No such file or directory: '/nonexistent/gh') and the local branch feature/test owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).\n"`

All four hold at once; no conflict found.

## 2. Sentinel question — executed evidence

**(i) Stale sentinel governing a wrong decision — YES, confirmed by execution.** `unusable` is a
single flag accumulated over the *whole* glob scan (`merge-gate.py:99-111`), not per-branch. A
healthy match always overrides it (`:110` returns the literal `False`, not the accumulated flag),
so the *matched-branch* case never goes stale. But an **unmatched** branch inherits whatever
`unusable` was left by scanning records that have nothing to do with it — see the regression below.

**(ii) First-match ordering deciding between healthy and unusable for the SAME branch — NO,
confirmed by execution.** Two records for one branch (`feature/dup-target`), one healthy
(`build_entry: opened`) one malformed (`[]`), directory names forced to bracket both glob orders
(`AAA-healthy`/`ZZZ-malformed` and `ZZZ-healthy`/`AAA-malformed`), 6 trials each: ALLOW,
deterministically, in all 12 runs, both orders. `feature_for`'s hardcoded `False` on match
(`:110`) makes ordering irrelevant for the same-branch case — this part of the design is sound.

## 3. must_fix — `merge-gate.py:98-111`, `:136-141`, severity **high**

**Scenario.** Repo has feature `FEAT-A` (healthy, matched to some other branch) and feature `FEAT-B`
whose `feature.json` happens to be a malformed non-object (`[]`) — unrelated to either branch.
Someone merges `totally/unrelated/orphan-branch`, a branch that owns **no** harness feature at
all (a docs fix, a dependency bump, any non-tracked branch). Execution:

```
pinned (473d82cb):  rc=0 decision=deny reason="merge-gate: could not evaluate a feature's
                     Build-entry receipt, so this merge is denied. Repair the malformed feature
                     record and re-run the merge." stderr=''
parent (473d82cb^ == af132780 content, same bytes): rc=0 decision=None reason='' stderr=''
```

Pre/post divergence on the **identical fixture** proves this is a regression introduced by
`473d82cb`, not a restatement of the settled cross-feature DoS closed at `af132780` (that one
routed a **raised exception** into `deny()` for literally every merge, on every branch, matched or
not; this one is narrower — the scan completes normally, a matched branch is always safe
(`:110`'s hardcoded `False`), but any **unmatched** branch is now denied). It also contradicts
D-07's own text (`plan.yaml`): the merge-gate "decides on the LOCAL feature.json receipt alone …
denies only if that resolves to a feature owing a receipt" — here the branch resolves to no
feature at all. The deny reason also names no file and no feature (`"a feature's Build-entry
receipt"` — contrast the matched-deny paths at `:143`/`:150` which interpolate `feat`), so an
operator merging unrelated work gets no lead on which of N feature directories to repair.
Fix direction: scope `unusable` to whether the branch's *candidate* record (a `feature.json` whose
directory would otherwise plausibly own the branch) was malformed, not any record scanned during
the walk — or track and report the offending path instead of a generic message.

## 4. Widened checks

- **Other callers of `feature_for`**: none. `grep -rn "feature_for("` finds only its
  definition and the one call site in `merge-gate.py:136`; no sibling script imports it.
- **Sibling PreToolUse gates**: `gh-close-gate.py` and `branch-create-gate.sh` do not scan
  `.harness/*/features/*/feature.json` at all (pattern-match on the command / directory-existence
  checks respectively) — the sentinel is local to `merge-gate.py`, not shared.
- **DENY-with-no-malformed-record reachable?** No — `unusable` starts `False` and is set only at
  `:107`, inside the `not isinstance(document, dict)` branch; with zero malformed records it stays
  `False` for the life of the call.
- **Era exemption + malformed own record** (info, not a finding worth blocking): an era-exempt
  feature (e.g. `BUG-1030-stale-anchor-write-hazard`) whose own `feature.json` is corrupted to a
  non-object is DENIED rather than era-exempted — confirmed by execution — because the era check
  at `:142` only runs once `document is not None`, and a malformed record never yields a
  `feat_dir`. D-08 only discusses an absent `build_entry` key, not a fully malformed document, so
  this isn't a textual contradiction, and denying on unreadable local state is arguably the safer
  default. Noting it for the record, not gating on it.

## 5. `test-merge-gate.py` at the pin, and case discrimination

19/19 pass (`ALL PASSED`). Of the two integration cases named in the dispatch's CONTRACT:
- `T-05 unusable target record fails closed` — **new in this commit** (`473d82cb` diff). Run
  against the immediate-parent byte content (`473d82cb^`): parent `decision=None`, pinned
  `decision=deny` — **discriminating**.
- `T-05 unrelated non-object feature record does not block healthy merge` — **not new in this
  commit**; it was added at `af132780` (one commit earlier) and is unchanged by `473d82cb`. Run
  against the parent: both allow — **not discriminating at this pin**, because it is a
  regression-guard for a fix that already landed one commit before. Not vacuous relative to its
  own introducing commit, just not this commit's own contribution.

## 6. Code grade

`code-grade.py --base $(git merge-base origin/main 473d82cb) --head 473d82cb`: 50 functions
graded, no ungated `RESULT: FAIL` (no grade below its bar). Four grade-2 functions gate
(`RESULT: FAIL SEVERITY: med`, non-blocking per policy) and all four carry an in-source
`GRADE-2 REASON` comment naming the function and the reason: `merge-gate.py:123 main` (orchestration
boundary — pre-existing, not worsened by this diff's +8/-4), `test-check-state.py:4621
case_t06_build_entry_invariant`, `test-hooks-install.py:392 _run_merge_and_check`,
`test-post-merge-sweep.py:885 case_t07_build_entry_receipt` — all three test functions are
table/fixture-driven end-to-end cases from earlier tasks in this feature, each with a written
splitting-would-hide-the-contract reason. `code_grade: grade_2` — no `fail`.

## Dismissed, not re-raised

The five settled items named in the dispatch (`gh_head` OSError fail-open, era bypass on absence,
fail-open on internal error, cross-feature-DoS bystander lockout, silent-allow-on-unusable-target)
were checked and confirmed to remain fixed/unchanged at this pin — not re-litigated here.
