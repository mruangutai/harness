# FEAT-43 code-risk grading — ship review (cycle 28, final)

**Supersedes `ship-review-c27.md`.** That briefing withdrew the ship recommendation over a crash in
the feature's own engine. **The crash class is closed, and I am reinstating the recommendation.**

**Recommendation: SHIP.** 20 of 20 criteria met, zero `not_met`, zero open, `must_fix` empty across
every review. Push PR #978 and let CI confirm what the depth-1 clone already showed.

## The crash class is closed — structurally, not patched three times

Three `None` guards, matching the pattern `visit_Assert` already used in the same class:

```
visit_AnnAssign  node.value            →  x: int
visit_With       item.optional_vars    →  with lock:
visit_Try        handler.type          →  except:
```

**The measurement, run by me and reproduced independently:** over the harness's own `bin/*.py` the
sweep goes from **83 graded / 16 crash** to **99 graded / 0 crash**. `harness_merge.py` and
`harness_boundary.py` — production files that aborted the tool — now grade.

**The part that matters more than the count.** I asked the review to prove the *class* was closed
rather than three instances of it, and it did, structurally rather than by enumeration:
`ast.NodeVisitor.generic_visit` skips `None` behind an `isinstance(value, AST)` check, so **only a
custom `visit_*` override calling `self.visit()` directly can crash**. The reviewer enumerated all 18
optional fields `_Counter` can reach and executed 30 construct probes: 30/30 clean at this pin, and
the same three raise at the prior pin — so the fix is demonstrably what changed the outcome.
`Return.value`, `Raise.exc`/`cause`, `Yield.value`, `Starred`, slice bounds, comprehension `ifs`,
argument defaults, `alias.asname`, `keyword.arg`, `Global`/`Nonlocal` and `FunctionDef.returns` are
all safe because `_Counter` never overrides them.

Each guard binds: three isolated mutations, three *named* test failures, sha256-verified byte-identical
restores — and the mutations were run inside a disposable clone, so the worktree file was never opened
for write. The tests assert **literal metric values**, re-derived term by term by QA, not merely the
absence of an exception. They correctly do **not** claim bare `with` and `with … as …` are
metric-identical; `abc_a` differs by 1.

## Cycle 27, for completeness

The PR #978 CI failure is closed. `check_prior_validator` ran `git show df63193:<file>`, absent in a
shallow checkout. Your patch deleted the check; **I refused** — it is the sole implementation of
SC-20's fourth clause (`BRIEF.md:210-218`, verbatim). The files are now byte-identical `.fixture` data
under a non-`.py` suffix, proven hermetic in a real `git clone --depth 1`. Two further history
dependencies in the same file were fixed with it; the scope call was reported and you ratified it.

## Evidence at the ship pin `baa96b7e`

| Gate | Result |
|---|---|
| Goal-check | **20 of 20 met, 0 `not_met`, 0 open** |
| Engine crash sweep | **99 graded, 0 crash** (was 83/16) |
| The feature's own grading gate | **exit 0** — 201 graded, zero blocking, 12 grade-2 |
| The engine against its own bar | 53 functions, zero below grade 4 |
| Delta review (this cycle) | **PASS**, `must_fix: []`, `severity_max: low` |
| Delta review (cycle 27) | **PASS** — hermeticity, discrimination and fixture inertness each proven |
| Full independent panel (`17106762`) | **PASS**, `must_fix: []` |
| Focused suites | five, all exit 0 |
| `check-state.sh` | **exit 0** |
| SC-11 UAT | **passed**, and see below |

**The nicest result in this cycle answers a question I expected to have to argue.** Your SC-11 UAT
ran at pin `cd8dae47`, and two source changes have landed since — including a production change to
the grading engine. Does a UAT executed at an earlier pin still evidence the criterion here? pm did
not argue it: it **re-graded the four surviving arm outputs at this pin and reproduced 6, 5, 16, 14
exactly**. The measurement is stable across the change, so the pass carries.

## What is still true and uncovered

- **The class-closure probe was throwaway.** The 30-construct enumeration that proves the class is
  closed no longer exists; the committed suite defends the three fixed constructs, not the class. The
  reviewer ranks this the highest-value of the three new rows, and I agree — B30.
- `visit_Try` now grades **exactly 4 with zero headroom**. One added branch drops the crash class's
  own repair site below the production bar. B28.
- **The generic containment fix is deeper but not strictly better**, and I am recording the refined
  judgement rather than my first one. A one-line `_Counter.visit()` override that no-ops on `None`
  would close the class permanently at one site. But it converts a *diagnosed, bounded* null into
  *unbounded* null tolerance across every present and future override — including required fields that
  are `None` because of a genuine bug, which it would then silently swallow. B29, with the trade-off
  recorded rather than a recommendation to just do it.
- The last three reviews were **two-member delta reviews**, not full panels. The c21 panel's security
  and UI verdicts stand and were not refreshed; no delta added an input, auth, secret, serialization
  or rendered surface.
- No coverage instrumentation exists in this repository.

## Backlog

B1–B20 and B22–B24 carry forward from `ship-review-final.md`; B25 is **closed** by this cycle. B26 and
B27 remain untouched, as you instructed — they were not bundled merely for sharing a file. Four rows
are new, with the evidence you asked for.

| ID | Nature | What |
|---|---|---|
| **B28** | chore | `visit_Try` grades exactly 4 (cyc 4 / cog 4 / abc 8.7, driver `cognitive+abc`) — zero headroom at the crash class's own repair site |
| **B29** | enhancement | the generic `_Counter.visit()` `None`-no-op override. Deeper — one site instead of three, and permanent for future overrides. **Not strictly better:** it trades a diagnosed bounded null for unbounded null tolerance and would silently swallow a required field that is `None` because of a real bug. Needs a decision, not a tidy-up |
| **B30** | bug | the 30-construct class-closure probe that proved the class closed was **throwaway and no longer exists**. The committed suite defends three constructs; nothing defends the class against a future `visit_*` override that dereferences a new optional field. Highest-value of these four |
| **B31** | bug | **harness, second occurrence with evidence.** A specialist ran `git checkout -- code_grade.py` mid-run this cycle against an explicit written prohibition, self-reported it, and hand-reapplied its work; I verified the diff vs the prior pin was exactly the three guards, so nothing was lost. The first occurrence was in cycle 14 (`git checkout -- code-grade.py`, reverting a completed refactor). **The rule is two-for-two on being ignored by different agents in different cycles**, which is evidence it needs a mechanical guard rather than stronger prose. B17 is the rule; this is the recurrence and the case for the mechanism |

## Budget

`cycles_used` is **28 of 28** — exhausted. `runs` is **45** against an informational 20-run budget
(INV-22). **B20 recurred again**: three run `state.yaml` files arrived carrying non-checkpoint keys.
Ten repairs by hand across this feature. It remains the harness's most reliable defect.

## What is left for you

**1. Ship.** Push PR #978 and await CI — the depth-1 clone is a local proxy for it, and it is green.
**2. Strike any backlog rows you do not want.** Unstruck rows become issues on acceptance; anything
struck dies silently. B25 is closed and removed.

Merge, `gh-sync.py ship`, backlog creation, feature-close distillation and worktree removal are all
yours or the main session's. None has been done.

## State of the branch

Nothing shipped. No PR merged, no deploy, no issue closed; the worktree stands. `review_sha` is
`baa96b7ee1cfbc7fcbea8873692cc91751a0c171`, `check-state.sh` exits 0, the working tree is clean, and
no source has moved past the pin.
