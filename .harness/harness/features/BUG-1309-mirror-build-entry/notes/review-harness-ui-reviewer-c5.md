# UI review — cycle 5 — BUG-1309-mirror-build-entry @ 473d82cb

## BLUF

**FAIL.** Not on copy wording — on what the wording is attached to. The new unusable-target
deny is emitted by a global, branch-independent sentinel: `feature_for` sets `unusable = True`
on *any* non-dict `feature.json` it encounters anywhere in the glob, with no relationship check
to the branch being merged. When no feature.json matches the branch under merge and an
*unrelated* feature's record elsewhere is malformed, this pin denies the unrelated merge —
reproduced by direct execution. This is the exact cycle-3 "any malformed record anywhere denies
every merge" bystander-lockout pattern, closed at `af132780` (cycle 4, confirmed fixed by
security review's S3/S4) and **reintroduced** by this pin's fix for the opposite bug (silent
allow on a self-corrupted record). It is the "SET BUT STALE" interaction the dispatch asked me
to re-derive, not a restatement of the settled bystander-lockout item — that item was settled
*at the previous pin*; this pin undoes it.

## Scope-out — visual/accessibility/dark-light dimension

Census, measured: `git diff --name-only 473d82cb~1 473d82cb` → 2 files
(`.claude/skills/harness/bin/merge-gate.py`, `tests/integration/test-merge-gate.py`), both
`.py`. Zero hits for html/css/scss/tsx/jsx/vue/svelte/less. `git diff --stat 473d82cb HEAD` → 1
file (`feature.json`, a checkpoint/state bump, not code) — confirms the constraint that the
code diff between the pin and branch tip is empty. No `DESIGN.md` in this diff. There is no
rendered surface, no theme, no colour, no focus/keyboard path anywhere in this change —
scoping that dimension out is a measured absence, not an inferred one.

The one operator-facing surface this diff *does* touch is CLI text: the `deny()` JSON
`permissionDecisionReason` and the two `stderr` allow lines in `merge-gate.py`. That is audited
below per the dispatch's explicit instruction to treat it as in-remit.

## The deny copy, on the three questions asked

Literal string, confirmed two ways — read at `merge-gate.py:139`, and reproduced verbatim by
executing `merge-gate.sh` against a fixture (`t-selfbad`-equivalent: one feature.json = `[]`,
branch under merge matches nothing):

> `merge-gate: could not evaluate a feature's Build-entry receipt, so this merge is denied. Repair the malformed feature record and re-run the merge.`

1. **WHAT / WHICH / WHAT-next.** WHAT is generic ("could not evaluate... Build-entry receipt" /
   "malformed feature record") — it never says *how* the record is malformed (not an object).
   WHICH is absent by construction: `feature_for` (`merge-gate.py:98-110`) discards the path of
   the offending file the moment it sets `unusable = True` (`merge-gate.py:106-107`), so `main()`
   structurally cannot name it even if it wanted to. WHAT-next ("repair... and re-run the merge")
   gives no path, no command — contrast the sibling D-09 deny (`merge-gate.py:154`, names the
   exact file and the exact `gh repo view` command) and the missing-build-entry deny
   (`merge-gate.py:158`, builds `command_line` naming the exact `gh-sync.py` invocation). This one
   sibling gives no equivalent remedy command. An operator hitting this message has no way to
   locate the broken file without grepping `.harness/*/features/*/feature.json` by hand.
2. **Consistency.** It is near-duplicate of the pre-existing exception-handler fallback at
   `merge-gate.py:160` ("could not evaluate {feat}'s Build-entry receipt, so this merge is
   denied. Repair the feature record and re-run the merge.") — same shape, differing only in
   "a feature's"/"malformed feature record" vs `{feat}`'s/"the feature record". Two structurally
   different failure modes (a specific malformed-record detection during scan vs. any uncaught
   exception in `main`) now read as the same boilerplate, where every other deny in this file
   (D-09, missing-entry, era-exempt allow, DEC-138 allow) is individually worded with a concrete
   remedy. This message is the outlier in the file's own convention.
3. **Interpolation.** Does not interpolate at all — no `{feat}`, no path, no branch. It uses the
   indefinite "a feature's", not even the fallback's "this feature" pattern. That sidesteps
   misattributing a *name* (arguably better than a wrong name) but at the cost of offering zero
   orientation — and per the finding below, the message frequently fires for a merge that has no
   relationship whatsoever to the malformed record, so even "this feature" would have been wrong.

None of this is severity-gating **on its own** — it is a real actionability gap (`med`), matching
G-13 (an operator-facing withhold naming only the fact, not a concrete remedy).

## Finding — SET-BUT-STALE sentinel denies an unrelated merge (high, must_fix)

`feature_for` (`merge-gate.py:98-110`):
```
unusable = False
for path in glob.glob(...):
    ...
    if not isinstance(document, dict):
        unusable = True
        continue
    if document.get("branch") == branch:
        return os.path.dirname(path), document, False
return None, None, unusable
```
`unusable` is set by *any* non-dict `feature.json` the scan visits, independent of whether that
record has any relationship to `branch`. It is read back only in the fallthrough
(`return None, None, unusable`) — i.e. exactly when no record for *this* branch was found. A
healthy match for a *different* branch never clears it.

**Reproduced by execution** (script run against the pinned `merge-gate.sh`, in-worktree,
throwaway, not committed): fixture with `FEAT-9001-fixture-non-era` (branch `feature/test`,
healthy) plus an unrelated `FEAT-9999-unrelated/feature.json` = `[]`. Ran
`git merge feature/nonexistent-branch` (matches no feature.json at all):
```
returncode: 0
decision: deny
reason: "merge-gate: could not evaluate a feature's Build-entry receipt, so this merge is denied. Repair the malformed feature record and re-run the merge."
```
A merge for a branch that owes no receipt, and has no relationship to the broken record, is
denied — with a message that cannot name the record and cannot tell the operator their own
branch isn't the one at fault.

This is not a restatement of the settled "bystander lockout" item: that item was **closed at
`af132780`** (cycle 4, `review-harness-security-reviewer-c4.md` §"Direction 2", S3/S4, confirmed
by execution) precisely by making `feature_for` `continue` silently past non-dict records with no
state retained. This pin (`473d82cb`) reintroduces state (`unusable`) to fix the opposite,
also-real bug (self-corruption silent-allow) — but that state is global to the scan, not scoped
to the branch, so it resurrects cycle 3's exact failure mode for the "branch matches nothing"
path. It is the SET-BUT-STALE interaction the dispatch asked me to re-derive rather than assume
closed.

**Coverage gap, measured**: the 19-case suite has `T-05 unrelated non-object feature record does
not block healthy merge` (unrelated malformed + a *matching* healthy record — passes, unaffected
by this bug since the match short-circuits) and `T-05 branch matching no feature allows` (no
malformed record present at all). No case combines "no match for this branch" with "an unrelated
malformed record exists" — exactly the gap that let this regression ship.

`must_fix`: `feature_for` must scope "unusable" to records that are actually candidates for
`branch` (or `main` must not deny on a global `unusable` when `branch` matched nothing at all).
This is a control-flow fix, not a copy fix — flagging for the code/security reviewer lens to own
the remedy; I raise it here because it is the mechanism that fires the copy I was asked to audit,
and it is reachable by the same "ordinary write access, no privilege escalation" threat model
cycle 4's security review already established for `feature.json`.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Unusable-target deny copy is a med actionability gap on its own, but the sentinel that triggers it is global-not-branch-scoped and denies unrelated merges — a reintroduction of the cycle-3/af132780 bystander-lockout bug, reproduced by execution"
  mode: B
  in_scope: true
  severity_max: high
  findings: 2
  must_fix:
    - "merge-gate.py:98-110 feature_for: `unusable` is set by any non-dict feature.json anywhere in the glob, not scoped to `branch`; when no record matches `branch` at all, an unrelated feature's malformed record denies this merge with an unattributable message. Reproduced by execution (fixture: healthy FEAT-9001 + unrelated FEAT-9999=[]  merging feature/nonexistent-branch -> rc=0, deny, generic reason). Regresses the bystander-lockout fix closed at af132780 (cycle 4)."
  states_unspecified: []
  contract_violations:
    - { path: "merge-gate.py:139", actual: "merge-gate: could not evaluate a feature's Build-entry receipt, so this merge is denied. Repair the malformed feature record and re-run the merge.", specified: "operator-actionable deny naming WHAT/WHICH/next-step, per dispatch; message names none of WHICH (no path/feature id — feature_for discards the offending path at merge-gate.py:106-107) and gives no remedy command, unlike sibling denies at merge-gate.py:154 and :158" }
  a11y: ["n/a — CLI stdout/stderr text only, no colour-only state encoding, no rendered surface in this diff"]
  open_questions:
    - { id: Q1, question: "Should feature_for track (path, unusable) per branch-candidate instead of a single scan-wide boolean, so `unusable` only fires when the malformed record is actually a candidate match for the branch under merge? This is the concrete shape of the must_fix and needs the code/security reviewer or backend-dev to own the remedy design.", blocking: true }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-ui-reviewer-c5.md
```
