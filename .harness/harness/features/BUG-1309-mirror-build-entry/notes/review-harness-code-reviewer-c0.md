# Code review — BUG-1309-mirror-build-entry — cycle 0 — review_sha 6f64a21c

## BLUF

**FAIL.** Stage 1 (spec compliance) surfaces one HIGH-severity mismatch between SC-04/D-08/DEC-220
and `merge-gate.py`'s actual era-exempt bypass condition — the code denies a merge that three
independent authoritative sources (the BRIEF, the plan's own T-11 task note, and DECISIONS.md
DEC-220) say must be allowed, and `gh-sync.py` itself prints an operator-facing promise that the
gate then breaks. Stage 2 adds one MED code-quality finding: an unruled new grade-2 function the
mechanical grader flags that the dispatch's "already ruled" list omits. `code_grade: grade_2`
(four gated grade-2 records total, zero grade-1/production-grade-3 blockers).

**Path drift caught and corrected mid-review**: my first pass of `read`/`grep` on relative paths
silently resolved against the *main checkout*'s stale copy of this file tree, not the worktree —
exactly the trap the dispatch flagged. Re-ran every citation below against the absolute worktree
path; all file:line anchors in this note are verified against
`/Users/.../worktrees/harness/BUG-1309-mirror-build-entry/...` at `HEAD` (`7a5808d7`), which is
byte-identical to `6f64a21c` for every source file cited (`git diff 6f64a21c..HEAD` is empty for
each).

## Stage 1 — spec compliance: **FAIL**

Every REQ/D traced cleanly except one. `D-08`'s own text states the three refusals "each skip a
feature whose directory basename is in that set" (era membership alone), and `DEC-220`
(`.harness/harness/docs/DECISIONS.md:6988`) repeats it: "One frozen set... bounds INV-37 and
**both refusals** to the post-receipt era." `BRIEF.md` SC-04 states it as a hard requirement: "for
a feature that IS in that set the merge is ALLOWED at exit 0 with no permission decision emitted"
— unconditional on the era set, no value qualifier.

**The code implements a narrower rule.** `merge-gate.py:132`:
```
if feat in feature_schema.BUILD_ENTRY_ERA_EXEMPT and entry is None:
    return
```
The era bypass fires **only** when `build_entry` is absent. An era-exempt feature that carries
`build_entry == "recovery-required"` falls through to `entry in {"opened", "not-applicable",
"recovered-terminal"}` (false), then to `deny(...)` at the bottom of `main()` — **denied**, not
allowed, contradicting SC-04's plain unconditional reading.

**This is not a paper scenario.** `feature_schema.BUILD_ENTRY_ERA_EXEMPT`
(`feature_schema.py:226-303`) is a frozen snapshot of every feature directory that existed at
generation time — including `BUG-1309-mirror-build-entry` itself, and by construction every other
feature dispatched before this fix shipped whose own real, first-ever `gh-sync.py open` call has
not yet happened. Any such feature (era-exempt by directory-existence, but running Build entry for
real) that hits a transient `gh` failure on its first remote call records
`build_entry = "recovery-required"` (`gh-sync.py:166-186`, `skip()`'s recording logic does not
consult era membership at all). That feature is now era-exempt **and** `recovery-required`
simultaneously — exactly the combination `merge-gate.py` mishandles.

**`gh-sync.py` itself promises the opposite of what `merge-gate.py` does.**
`_build_entry_recovery_notice` (`gh-sync.py:1379-1386`), reached from `_build_entry_preflight` on
every `start-task` for such a feature, prints to the operator: *"Build proceeds. This feature
predates the build-entry receipt..., so its merge is not refused."* The plan's own T-11 task
intent (`plan.yaml:1796-1808`) states this explicitly for its test case BE-23: reverting the
`rstrip` fix at `gh-sync.py:1360` "routes an era member into `_build_entry_recovery_notice`'s
NON-era branch... whose line claims 'the MERGE is refused until gh-sync.py open records opened' -
**false for an era feature, whose merge SC-04 requires to be ALLOWED**." BE-23
(`tests/integration/test-check-state.py` — actually `test-gh-sync-build-entry.py`/unit per T-11)
only asserts the **printed stderr string**, never `merge-gate.py`'s actual permission decision for
this state. `tests/integration/test-merge-gate.py` has exactly one era-exempt case,
`"T-05 era-exempt absent build_entry allows"` (entry is `None`) — no case exists for era-exempt +
`recovery-required`. The gap between the promised message and the enforced behaviour is untested
in both directions and, on the code as written, real: an operator who trusts the printed notice
and proceeds to merge gets an unexpected deny.

By contrast, `post-merge-sweep.sh:223-231` and `check-state.sh:2002` (INV-37) both implement the
**unconditional** era-membership skip D-08/DEC-220 actually describe — the era check there does
not consult the recorded value at all — which is the strongest evidence this is `merge-gate.py`
deviating from its own decision record, not the decision record being stale.

`severity: high` — wrong behaviour in a realistic, soon-to-recur case (every era-exempt feature's
first real Build entry that hits a transient failure), corroborated by three independent
authoritative sources (BRIEF SC-04, plan.yaml T-11/BE-23, DECISIONS.md DEC-220) plus the tool's own
contradictory operator-facing message, with zero test coverage of the actual gate decision for this
combination. `kind: mismatch`, `ref: SC-04 / D-08 / DEC-220`.

No other REQ/D was found unimplemented, and no scope creep was found beyond `plan-merge.py`'s
`_replace_signature_fields` regex fix (`plan-merge.py:1120`, commit `ae4abf8c`) — traced to T-11's
BE-23/T-12 dependency chain (an operator hand-fix bundled with the `gh-sync.py:1360` `rstrip`,
both landing before the pin), not undeclared scope creep.

## Probe 1 — `skip()` vs `refuse()`: every call site, honest or not

`refuse()` (`gh-sync.py:205`, exit 2) and `die()` (`gh-sync.py:199`, exit 1) are always honest:
every call site is a genuine non-zero exit with a message naming the cause. No finding there.

`skip()` (`gh-sync.py:166`, exit 0) always was, and remains, "did nothing, environmental" by
design — that convention is not itself the defect this feature targets. What changed is that
`open`'s skip sites now leave a **durable receipt** distinguishing the flavors of "did nothing,
exit 0" from each other, so a caller reading only the exit code is no worse off than before, but a
caller reading the **receipt** (post-merge-sweep, check-state, merge-gate, the next `start-task`)
now can tell. Enumerated (worktree line numbers):

| site | armed for `open`? | build_entry recorded | honest? |
|---|---|---|---|
| `gh-sync.py:242` `gh()` generic failure | if cmd==open | default → `recovery-required` (no remote write yet) | yes |
| `:278` no harness.json | if cmd==open | default → `recovery-required` | yes (see caveat below) |
| `:282` harness.json unreadable | if cmd==open | default → `recovery-required` | yes |
| `:285` sync not enabled | if cmd==open | `"not-applicable"` (D-01) | yes |
| `:288` repo not pinned | if cmd==open | `_NO_RECORD` sentinel → stays **absent** (D-09) | yes |
| `:291` gh not on PATH | if cmd==open | default → `recovery-required` | yes |
| `:293` gh not authenticated | if cmd==open | default → `recovery-required` | yes |
| `:1099` milestone create+recovery both fail | if cmd==open, and only if no create yet succeeded | default → `recovery-required` | yes |
| `:1454` start-task "no recorded issue" | never (not `open`) | untouched | n/a — this skip predates and is orthogonal to Build-entry; `_build_entry_preflight` already ran and refused/allowed above it |
| `:1699` abandon "nothing to abandon" | never | untouched | n/a — abandon doesn't touch build_entry |
| `:2015` ship "no recorded milestone" | never (`_BUILD_ENTRY` only arms for `open`) | untouched — stays whatever it was | yes: ship's own skip is not where the receipt is written; the message now names `recover-terminal`, and the **actual** fix for the original bug (ship-skip-then-delete-worktree) lives in `post-merge-sweep.sh`'s retention check, verified by T-07/T-10 |
| `recover-terminal`'s internal `gh()` failure (funnels to `:242`) | never (`_BUILD_ENTRY` only arms for `open`) | untouched, stays absent if never recorded | yes, matches `cmd_recover_terminal`'s own docstring at `gh-sync.py:1298-1303` |

Caveat on `:278`/`:282` (no/unreadable harness.json): these fire before the project is even
confirmed onboarded, at the *root*, not the feature dir. If `_BUILD_ENTRY["feat_dir"]`'s
`feature.json` happens to exist (an onboarded-later project pointed at a stale feature dir), this
records `recovery-required` for what is really a root-level misconfiguration rather than a
mirror-specific one. This is a low-severity edge case — D-04's literal rule ("stopped before any
remote-mutating call" → `recovery-required`) is satisfied, and Build is allowed to retry per REQ-06
either way — not raised as a separate finding.

**Nothing now exits 0 while claiming completion it did not do.** `cmd_open`'s only unconditional
success write, `record_build_entry(feat_dir, "opened")` (`gh-sync.py:1229`), is the true last
statement of the function — every branch above it either records a truthful non-`"opened"` outcome
or raises/exits before reaching it. `cmd_recover_terminal`'s success write
(`record_build_entry(feat_dir, "recovered-terminal")`, `:1315`) is the last statement of *its*
`--yes` path likewise. This is the structural argument the docstrings assert, and I re-derived it
from the control flow rather than accepting the docstrings' word — it holds.

## Probe 2 — `merge-gate.py`'s local-record-only refusal on a `gh` read failure

`merge-gate.py:97` `head_branch()` — when `gh_head()` fails (`gh pr view` can't resolve
`headRefName`), `merge-gate.py:99-100` falls back to `local_branch(cwd)` and carries the failure
message forward. Traced through `main()` (`:115-146`):

- if the LOCAL branch resolves to **no** feature (`feature_for` finds nothing): print the
  "could not verify... allowing it" line to stderr and `return` — **allow**, never deny on a read
  failure alone (`:124-127`).
- if the LOCAL branch resolves to a feature whose local record **owes no receipt**
  (`opened`/`not-applicable`/`recovered-terminal`): allow, printing the same stderr caveat when
  `failure` is set (`:135-138`) — a harmless redundant message on an already-correct allow, not a
  defect.
- if the LOCAL branch resolves to a feature whose local record **owes a receipt** (absent or
  `recovery-required`, not era-exempt): `deny(...)` fires regardless of `failure` (`:139-145`) — it
  denies **only** because the local record condemns it, never because the read failed, matching
  D-07/DEC-138 exactly. Confirmed by `test-merge-gate.py`'s `"T-05 gh outage with a feature owing a
  receipt denies"` case, which asserts `"could not verify" not in reason`.

This exactly matches D-07's stated posture and is well-tested (`test-merge-gate.py`: outage+no-match
allows, outage+owing-feature denies). No finding.

## Probe 3 — the era boundary, five readers of one set

Definition: `feature_schema.py:226` `BUILD_ENTRY_ERA_EXEMPT = {...}` (one literal set, 78 members,
frozen at commit `71d4ba1f`). I enumerated every external reader by grep, not by trusting SIMPLIFY's
count:

1. `check-state.sh:2002` — `if _feat37 in _fs37.BUILD_ENTRY_ERA_EXEMPT or ...: continue` (INV-37,
   T-06) — unconditional skip, matches D-08's literal text.
2. `gh-sync.py:1361` — `_build_entry_preflight`'s Build refusal (T-04).
3. `gh-sync.py:1380` — `_build_entry_recovery_notice`'s messaging branch (paired with #2).
4. `merge-gate.py:132` — the merge deny (T-05) — **the one that diverges; see Stage 1 above.**
5. `post-merge-sweep.sh:223` — retention (T-07), correctly keyed differently per D-08 (era gates
   only the *absent* case; `recovery-required` retains regardless of era, exactly per spec).

That is five sites reading the one set, as SIMPLIFY claimed — confirmed by direct enumeration, not
inherited. `feature_schema.py:326`'s own `recovery_command_for` reads the set a sixth time,
internally, but that is the definition module checking its own set, not a reader; it is additionally
covered by a live unit case (`test-feature-schema-build-entry.py:62-65`, `BE-02`) proving it is not
dead code even though every current caller pre-filters era membership before calling it. No site
re-derives era membership through a separately-maintained list — the one place the *use* of the set
diverges from the others is the value-qualifier bug in finding 1 above, not a duplicate definition.

## Absence handling across the five-state enum

Checked every direct reader of `github.build_entry` for a `.get()` default that could collapse
absence into a permissive value:

- `gh-sync.py:load_recorded` (`~626`) normalizes: anything outside the four legal strings — absence
  included — becomes `None`. No silent promotion.
- `merge-gate.py:131` reads the raw field (`entry = ...get("build_entry")`); absence is `None`,
  which is excluded from the pass-set (`opened`/`not-applicable`/`recovered-terminal`) and (era
  aside) reaches `deny`. Fail-closed on absence, not permissive.
- `post-merge-sweep.sh:222-228` reads raw; a `None` (and any other value outside the pass-set)
  falls to the `elif` and **retains** the worktree — fail-closed toward keeping evidence, not
  toward deleting it.
- `check-state.sh:2010` (`(_doc37.get("github") or {}).get("build_entry") is not None`) treats
  *only* a non-`None` value as "receipt present"; true absence is exactly the condition INV-37
  flags. No collapse.

No consumer defaults absence to a permissive state. This part of the directed audit is clean.

## Stage 2 — code quality

**Grader run** (`code-grade.py --base 6ad7233f... --head 6f64a21c...`, the actual merge-base range,
not `HEAD`): 54 changed functions, 50 pass, 4 gated at grade 2 (none grade 1, none production-code
grade 3 — nothing blocks the build). `code_grade: grade_2`.

Of the four: `merge-gate.py:main` (already reasoned, per dispatch), `test-check-state.py
case_t06_build_entry_invariant` and `test-post-merge-sweep.py case_t07_build_entry_receipt`
(both already reasoned, per dispatch) — **and one the dispatch's "already ruled" list omits**:

- `tests/integration/test-hooks-install.py:392` `_run_merge_and_check` — CYCLOMATIC 5, COGNITIVE 6,
  ABC 27.0, GRADE 2, BAR 3, driver ABC. This function was touched by the diff (new
  `build_entry="opened"` argument threaded through `_commit_feature`, plus a new
  `results.append(...)` assertion at `:424-428` confirming the sweep took the *normal* removal path
  rather than the build-entry retention branch) — the grader's own selection rule means its
  appearance here is a new-or-worsened record, not stale debt. It carries **no** written
  `REASON REQUIRED` answer anywhere in the plan, DECISIONS.md, or panel record I found.
  `severity: med`, per the review protocol's "grade 2 never blocks, but needs a reasoned answer."
  This is advisory, not a `must_fix` (grade 2 doesn't gate), but the operator's "already ruled" set
  handed to this panel is incomplete and should be corrected before the next cycle re-derives it.

No other Stage 2 findings beyond what SIMPLIFY already reported and the operator already accepted
(the `merge-gate.py` module-scope `jsonschema` import cost).

## Findings summary

| id | severity | file:line | kind |
|---|---|---|---|
| F1 | high | `merge-gate.py:132` | spec mismatch — SC-04/D-08/DEC-220 vs. era-exempt+`recovery-required` denial |
| F2 | med | `tests/integration/test-hooks-install.py:392` | unruled grade-2 function, no written reason on file |
| F3 | low | `gh-sync.py:278,282` | `skip()`'s root-level onboarding checks can record `recovery-required` for a feature dir under an unrelated/misconfigured root — informational, not a `must_fix` |

## Open questions

None blocking — F1 is answerable by the eng lead with a one-line fix to `merge-gate.py:132`
(`entry is None or entry == "recovery-required"`, or in whichever direction the operator confirms
SC-04's intent points), and F2 by recording a reason for `_run_merge_and_check` alongside the other
three.
