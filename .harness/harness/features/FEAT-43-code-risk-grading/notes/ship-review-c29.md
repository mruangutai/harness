# FEAT-43 code-risk grading — ship review (cycle 29, final)

**Supersedes `ship-review-c28.md`.** **Recommendation: SHIP.** Push PR #978; the gate the merge turned
red is green again, and the defect that turned it red is now repaired at all three of its callsites
rather than the one that happened to fail loudly.

## What cycle 29 actually found

You authorized one assertion. The scope you then widened, on a direct source read, is what makes this
cycle worth its budget — and finding it was yours, not mine. My dispatch's non-goals explicitly told
the specialist to leave the other assertions alone. That was my scoping error.

**Three callsites carried the same defect, `"1 file(s)" in stderr` — a substring test on a rendered
count.** The merge unioned two features' directories 40 → 41, so stderr renders `41 file(s)` and
`"1 file(s)" in "41 file(s)"` is `True`.

- The **negative** callsite tripped and turned `--kind unit` red. That is how the defect surfaced.
- The two **positive** callsites were **worse, and silent.** Each asserts the sweep reported exactly
  one file — that it scanned the temporary fixture, not the real repository root. Under a wrongly
  redirected sweep they pass **vacuously, in precisely the failure they exist to catch.** The review
  reproduced that against real sweep stderr, not a synthetic string.

A loud failure gets fixed. A silent pass is a test that has quietly stopped being a test, and two of
the three were in that state.

## What landed, and the one design point that matters

One shared word-boundary predicate, all three callsites routing through it, two synthetic controls —
and an **AST guard over the file's own source**.

That last piece is the whole value, and the reasoning is worth stating because it is easy to get
wrong: a control that exercises the *helper* stays green when a *callsite* regresses, because the
helper is still correct — it is simply no longer called. So for both positive callsites **the AST
guard is the only thing that catches a reversion.** I proved it before believing it: I mutated
positive callsite `:371` back to substring form and the named case
`no bare rendered-count substring compare outside reports_exactly_one_file` fired at exit 1. The
review then mutated all three, individually.

## Evidence at the ship pin `73c636dd`

| Gate | Result |
|---|---|
| `--kind unit` — the gate the merge turned red | **exit 0**, zero failures |
| Delta review | **PASS**, `must_fix: []`, `severity_max: med` |
| Range gate over the `origin/main`-derived base | **exit 0**, 206 gated, zero blocking |
| Engine against its own bar | 53 functions, zero below grade 4 |
| Five focused FEAT-43 suites | all exit 0 |
| `check-state.sh` | **exit 0**, zero violations |
| Goal-check | **20 of 20** — see the note below |

**A methodological correction the review made against me, and it is right.** My earlier
`check-state.sh` exit-0 reading was taken *before* the review's own run directory existed. A gate
reading taken before the run that perturbs it is not evidence about that run. The exit 0 above was
taken after, and it is the one that counts.

**The goal-check was not re-derived, deliberately.** The delta touches one main-owned test file that
carries no success criterion's evidence; every criterion's evidence lives in the FEAT-43 suites, and
those are green with the engine unchanged at 53/0. Recording 20 of 20 as carried forward rather than
spawning a run for a file no criterion cites.

## Two rulings the validator lead made, and the reasoning I endorse

Both were raised as improvements and both were **declined for this cycle** — on grounds worth more
than the improvements themselves.

- **`re.fullmatch` → `re.search` in the guard.** Measured strictly stronger at zero false-fire cost,
  verified twice including a full-suite run against a patched copy. Declined because applying it is a
  source change and there is **no cycle 30 in which to re-verify the changed artifact**. *A measured
  green artifact beats an unverified better one.* Backlog.
- **The AST walker sits at grade 3 against a bar of 3**, one edit from red, with no automated
  tracking — and it is now the last line of defense for a defect class that has cost this feature
  three cycles. Passing at its own bar violates no written rule and the function is demonstrably
  correct today. Backlog.

## What is still true and uncovered

- **The guard detects reversion to the exact prior syntactic shape only.** A callsite broken some
  other way — an unconditional `True`, a differently-wrong predicate — is caught by nothing. That is
  acceptable for a regression guard, but it is not callsite correctness, and it should not be read as
  such.
- **The defect class remains armed in `main`.** One mutation confirmed the live tree still renders a
  count ending in `1`. This panel verified the fix; it did not verify the absence of the class.
- No security or UI reviewer ran on this delta — a test-only change with no production code and no
  new input surface. The c21 panel's verdicts stand and were not refreshed.
- Main's own content was never re-reviewed on its merits at any point in the reconciliation.

## Backlog

Your disposition is recorded: **B28, B30, B31 kept; B29 struck.** B1–B24 kept, B21 and B25 closed and
removed. Five rows are new.

| ID | Nature | What |
|---|---|---|
| B32 | chore | `_rendered_count_substring_compares` uses `re.fullmatch`; `re.search` is measured strictly stronger at zero false-fire cost. Deliberately not applied with no cycle left to re-verify |
| B33 | chore | the AST walker sits at grade 3 against bar 3 with no automated tracking, and is the last line of defense for a class that cost three cycles. Consider adding the file to `SELF_GRADED_FILES` |
| B34 | bug | **against main's owner:** the same substring-on-a-count defect class is live in `main` independently of FEAT-43 — it fires whenever main's own feature count ends in `1`, and a mutation this cycle confirmed the count still does |
| B35 | chore | a stale local `main` ref widens the validator's derived range and produces spurious findings attributed to main's own files. Ruled fail-closed across all five ref states — it can widen, never narrow |
| B36 | bug | **harness:** no mechanism surfaces a duplicate dispatch. Main and I both widened cycle 29 into the same file, unaware of each other; two leads held identical scope and a collision was avoided only because one lead's pre-dispatch check happened to straddle a live edit. The durable finding is the absence of detection, not the attribution |

## Budget and one credit

`cycles_used` is **29 of 29**. `runs` is **49** against an informational 20-run budget.

**B20 finally did not recur.** The cycle-29 validator lead found its own `state.yaml` in violation of
DEC-154 and **repaired it itself** — the first lead in this feature to do so rather than leave it for
me. Ten previous digests I fixed by hand. Worth recording as evidence the contract can be met.

## What is left for you

**Ship.** Push PR #978 and await CI. Then strike any backlog rows you do not want; unstruck rows
become issues on acceptance.

## State of the branch

Nothing shipped. No PR merged, no deploy, no issue closed, nothing distilled; the worktree stands.
`review_sha` is `73c636dda65977faa9f9c171eedad35fed3213eb`, `check-state.sh` exits 0, the working
tree is clean, and no source has moved past the pin.
