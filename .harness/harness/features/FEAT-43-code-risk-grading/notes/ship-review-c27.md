# FEAT-43 code-risk grading — ship review (cycle 27)

**Supersedes `ship-review-final.md`.** That briefing recommended shipping. **I am withdrawing that
recommendation**, and the reason is not the CI blocker you sent me to fix — that is fixed and proven.
It is what fixing it uncovered.

**Recommendation: authorize one more narrow cycle, then ship.**

## The CI blocker is closed, and your patch was revised rather than applied

CI run `33294260861` failed because `check_prior_validator` ran `git show df63193:<file>` and that
object does not exist in GitHub's shallow checkout. Your suggested patch deleted the check.

**I refused the deletion.** `check_prior_validator` is the only implementation of SC-20's fourth
clause, which `BRIEF.md:210-218` states verbatim: *"The previous revision of the validator is run
against the first return and shown to accept it, so the assertion is proven able to fail."*
`check_review_policy` proves the rejection *happens*; the prior-revision run proves it is *new*, which
is what stops a hardcoded always-reject from passing as enforcement. Deleting a test named in a signed
criterion to turn CI green is the failure mode this whole feature exists to prevent.

Instead the two files are committed as byte-identical `.fixture` data — a non-`.py` suffix, so they
stay out of the graded set and cannot drag a pre-feature file's old grades into this feature's own
gate. **Proven, not asserted:** the suite exits 0 inside a real `git clone --depth 1` where
`git cat-file -e df63193…` fails. I ran that myself; so did QA. The delta review corrupted the
fixture and confirmed the named failure still fires, so the control still discriminates.

The shallow clone also exposed two further history dependencies in the same file, reddening the same
CI run. The engineering lead fixed all three and **reported the scope call rather than hiding it**;
the delta review ratified it, and so do I — same file, same red run, no production or workflow change.

## What that work uncovered — and why I am withdrawing the ship recommendation

**FEAT-43's own engine crashes on ordinary Python.**

`code_grade._Counter` visits three ASDL-optional AST fields without a `None` guard —
`visit_With`/`optional_vars`, `visit_Try`/`handler.type`, `visit_AnnAssign`/`node.value`. So:

```
with lock:          →  AttributeError: 'NoneType' object has no attribute '_fields'
except:             →  same
x: int              →  same
```

I reproduced all three. `visit_Assert` in the same class guards `node.msg is not None` correctly, so
the pattern was present and omitted three times.

**Scale, measured twice independently:** of the harness's own 99 `bin/*.py` files, **83 grade and 16
crash** — all sixteen from bare `with` alone — including production `harness_merge.py` and
`harness_boundary.py`. It is reachable through the shipped CLI, demonstrated rather than argued.

**Provenance:** introduced by commit `1ac1bd0`, **this feature's first commit**, the 367-line addition
of `code_grade.py`. I checked. So accepting it is not shipping around inherited debt; it is shipping a
feature that introduced a crash into its own product.

Two things that bound how bad it is, and I want them stated as plainly as the defect: it is **always a
loud raise, never a silent mis-grade** — the gate aborts rather than reporting a wrong answer — and it
has **zero intersection with this feature's own 200-record gated set**, which is exactly why 27 cycles
of green gates never touched it.

**The validator lead's finding on that last point is the most important sentence written in this
feature, and it is not about this bug:**

> The feature's verification apparatus was **structurally incapable** of finding this defect. The
> self-grading gate reports `code_grade.py` clean because grading measures complexity, not
> correctness, and the engine's own source happens to contain no bare `with`; and the gated set has
> zero overlap with the crash list.

That is the **third** time in this feature a green suite concealed a missing control — B21 was the
first, the severity-enum drift the second. Each was found by a *different* kind of scrutiny than the
one before, and none by the gates.

## Evidence at pin `4adb2219`

| Gate | Result |
|---|---|
| Delta review of the CI fix | **PASS** — hermeticity, control discrimination and fixture inertness each proven by the reviewers' own runs |
| SC-20 | **met** — all four clauses live at this pin, clause 4 verified as a genuine prior-revision subprocess |
| The feature's own grading gate | **exit 0** — 200 graded, zero blocking, 12 grade-2, no `.fixture` in the gated set |
| The engine against its own bar | 53 functions, zero below grade 4 |
| Focused suites | five, all exit 0; `test-validate-digest.py` also exit 0 in a depth-1 clone |
| `check-state.sh` | **exit 0** |
| Goal-check | **20 of 20** stands; SC-20 re-verified at this pin, the rest carried forward — the only source change is one test file and its suites are green |
| SC-11 UAT | passed, operator-executed, unchanged |

All five of my measurements were independently reproduced by the delta review and none contradicted.

## The decision

**Authorize cycle 28.** Three one-line `None` guards plus six literal-value assertions, already
specified to one-pass precision by QA, bundling naturally with a med fail-open and a low containment
item because they touch the same two files.

**One caution the review earned the hard way:** a send-back discovered that `with lock:` and
`with lock as _discard:` are **not** metric-identical — `abc_a` differs by 1 — so a cycle 28 executing
the earlier draft spec verbatim would have written a failing test and burned its single pass. Use
QA's corrected spec in `notes/qa-delta-c27.md`.

**The alternative is to ship with it recorded as a backlog row.** I do not recommend it. The gate is
the product; a Python risk-grading tool that aborts on `with lock:` fails on one file in six of the
repository it ships into, and it would undercut the claim your SC-11 test just measured. The cost of
fixing it is three lines and one cycle. The cost of shipping it is that the first person to run the
gate over a diff touching `harness_merge.py` gets a traceback instead of a grade.

If you disagree and want to ship now, the row is written and I will hand it over — but the
recommendation on the record is fix.

## Backlog

B1–B20 and B22–B24 carry forward from `ship-review-final.md` unchanged. Three rows are new, all from
this cycle, and **all three are proposed for cycle 28 rather than the backlog** if you authorize it:

| ID | Nature | What |
|---|---|---|
| **B25** | **bug** | `code_grade._Counter` crashes on three unguarded ASDL-optional visits — bare `with`, bare `except:`, bare annotation. 16 of 99 `bin/*.py`, CLI-reachable, introduced by this feature's first commit. **High** |
| **B26** | **bug** | a med fail-open advisory the code reviewer raised in the same two files |
| **B27** | **chore** | a low containment item in the same two files |

## Budget

`cycles_used` is **27 of 27**. Cycle 28 requires your authorization; I will not take it otherwise.
`runs` is **42** against an informational 20-run budget (INV-22).

**B20 recurred again this cycle** — both lead digests arrived not meeting the digest contract, one
with no contract block at all. That is seven I have repaired by hand across this feature. It is the
single most reliable defect the harness has.

## State of the branch

Nothing shipped. No PR merged, no deploy, no issue closed; the worktree stands. PR #978's lifecycle
is yours. `review_sha` is `4adb2219954aa132b1e8450cdd9e571dbedba309`, `check-state.sh` exits 0, the
working tree is clean, and no source has moved past the pin.
