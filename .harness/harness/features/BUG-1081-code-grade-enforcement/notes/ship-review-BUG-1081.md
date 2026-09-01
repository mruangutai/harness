# Ship review — BUG-1081, code-grade enforcement

**Recommendation: ship, after one rebase.** Every success criterion is met, the only blocking
gate passes, and the review panel's one critical finding was fixed and confirmed closed by the
reviewer who raised it. One thing stands between this branch and a merge, and it has nothing to
do with the change: `main` moved while we built, and this branch is now behind it on the harness
contract itself. That is item **P-1** below and it needs your decision.

**How this briefing was assembled.** No report round was spawned — the run digests were read
from disk. They are `runs/2026-09-01-01-eng/digest.md`, `runs/2026-09-01-1-product/digest.md`,
`runs/2026-09-01-01-validator/digest.md`, `runs/2026-09-01-c2-validator/digest.md`,
`runs/2026-09-01-2-product/digest.md`, all under
`.harness/harness/features/BUG-1081-code-grade-enforcement/`, together with the reviewer and
receipt notes cited by name throughout.

---

## What was broken, and what now holds

A code reviewer reported `code_grade` as `pass`, `fail`, `grade_2` or `n_a`. The digest validator
confirmed the report *ended* at the feature's `review_sha` — and then, for `pass`, `fail` and
`grade_2`, never ran the grader at all. A review therefore passed when `code-grade.py` was
skipped, when it crashed, or when a blocking result was simply reported as a clean one.

That is not a hypothetical. Measured against the unmodified validator before any code was
written, with the process cwd inside the fixture repository so the reproduction matched how the
hook actually ran in production:

| Case | Digest claimed | `validate()` | `--hook` exit |
|---|---|---|---|
| a new grade-1 production function | `code_grade: pass` | `errors=[]` | **0** |
| a committed Python file that does not parse | `code_grade: pass` | `errors=[]` | **0** |

Both accepted, grader never invoked. That block is committed verbatim in the test file's own
header, so the evidence ships with the fix rather than living in a receipt nobody re-reads.

Now the validator **computes** the result over a range the repository derives —
`merge-base(<default branch>, review_sha)..review_sha` — and refuses any digest that disagrees,
naming the value it expected. The reviewer keeps every part of the job that is judgment:
findings, `must_fix`, severity, grade-2 reasons and the review policy. A mechanically clean
grade still cannot rescue a review whose judgment failed.

**The feature grades itself.** At the pinned commit the canonical range contains 44 gated
functions with no blocking and no grade-2 record, so an honest `code_grade: pass` from the panel's
own code reviewer was accepted by the very enforcement it was reviewing.

---

## The one thing that needs your decision

**P-1 — this branch is behind `main` on the harness contract, and a rebase is yours, not mine.**

While this feature was being built, `main` landed FEAT-41 T-07 (`98b10135`), which **deletes
`status` from `feature.json`** and moves the feature's station into `plan.yaml` so one file
records it; and BUG-1080 (`a2fb6c0b`), which adds `runs[].code_grade`. Because hooks resolve
through the project root, the schema now judging every write to this branch's `feature.json`
comes from the `main` checkout — and it refuses the `status` key that this branch's own schema
still *requires*. `gh-sync.py status` on `main` writes `plan.yaml`; on this branch it writes
`feature.json`.

Nothing here is caused by this change, and the branch is internally consistent — its suites run
against its own copies and are green. But merged as-is it would land a `feature.json` carrying a
key `main`'s schema rejects. **The remedy is a rebase onto `main`, which moves HEAD and is
refused to every governed agent, correctly.** I did not attempt it.

A related, smaller instance of the same drift I *did* resolve, and am declaring because it is an
undeclared-file edit: this branch's `.harness/team-config.yaml` had fallen two comment blocks
behind `main`, and `test-check-plan-routes.py` compares it against the owner checkout's copy — so
the blocking integration gate was red for reasons wholly unrelated to the diff (7 failures). I
confirmed the **parsed YAML of the two copies is identical**, so the resync changes no grant,
route or domain, then took `main`'s copy. Both kinds went green immediately after. If you would
rather that arrive via the rebase than in this diff, strike it and I will revert it.

---

## Gates

| Gate | Result |
|---|---|
| **qa_gate** (blocking — the project's only one) | **PASS.** unit exit 0 / 0 `FAIL`; integration exit 0 / 0 `FAIL`. Re-run by me at the final pin, not taken from a digest |
| **review** (`advisory_unless_high`) | **PASS at cycle 2.** Cycle 1 returned FAIL/critical; that finding is closed |
| **goal-check** | **12 of 12 criteria MET** (11 at the goal-check, SC-11 closed afterwards) |
| **uat** | Not applicable — no user-facing surface; the BRIEF declares no `verify: uat` criterion |

**Cycles used: 2 of 10.** One for a send-back inside T-01, one for the panel's critical.

---

## The critical finding, and why it mattered

`harness-security-reviewer` found that `FEATURE_DIR_IN_ARTIFACT_RE`'s `[^/\s]+` segments match
`..`, and `_repo_root_for_feature` took four `..` off the result with no containment check. I
verified the premise myself before spending a cycle on it — a finding resting on a false premise
buys a fix cycle for nothing — and it held: an artifact line of
`.harness/../features/../notes/fake.md` resolved the repository root to
`/Users/molchairuangutai/GitHub/harness`, a **different git work tree sharing this one's object
store**. Both the `review_sha` read and every grading `git -C` call would have run against a tree
the digest itself chose, which defeats REQ-02 from the inside — the feature's own central
property, undone by its own new code.

Fixed at `2562e45a`: `_contained_feature_dir` refuses any `.`, `..` or empty segment *and*
requires the resolved path to be a strict descendant of the root. The security reviewer
re-derived the evidence itself and returned **CLOSED** after nine defeat attempts — encodings,
unicode variants, trailing dots, symlinked components, root-equality, absolute paths, Windows
separators, and the `feature_dir=` override seam. All held.
(`notes/review-harness-security-reviewer-c2.md`.)

---

## A theme worth your attention: gates that cannot report red

This feature makes a gate grade itself, and three separate times a branch was **green because
nothing could make it red**, not because it was correct:

1. A mutation turning the grader's catch-all exception into an acceptance reddened **nothing** —
   the branch was unreachable from the suite. Closed by `check_malformed_test_kinds`.
2. The panel's `sys.settrace` showed the new containment check's realpath branch **never
   executed**; deleting it left everything green. Closed by `check_symlinked_feature_component`,
   including a sibling-prefix case for the `+ os.sep` boundary that a first fixture still missed.
3. The goal-check found SC-11's degenerate-range refusal fixtured only against an `n_a` claim
   when the criterion binds it to `pass`/`fail`/`grade_2` too. Closed at `acda74d1`.

Each was found by a *different* reader, and none was visible to the others. Nine mutations were
run in total, each against a staged copy with a control run, because staging alone produces
failures that would otherwise be credited to the mutation. `validate-digest.py`'s checksum was
verified identical before and after every one.
(`notes/receipt-harness-orchestrator-reachability.md`, `notes/receipt-harness-orchestrator-T-02.md`.)

---

## Proposed backlog

Unstruck rows become issues on ship acceptance. **Anything not listed here dies silently.**

| ID | Nature | What |
|---|---|---|
| B-1 | chore | `_load_test_kinds`-equivalent config read is spelled twice (`code-grade.py`, `validate-digest.py`), one raising and one fail-closed. Unifying changes CLI behaviour that T-01's tests pin |
| B-2 | chore | 6 redundant `git rev-parse --verify` per code-review digest, measured at ~59 ms of 467 ms. Overlaps B-3's mechanism; take both or neither |
| B-3 | chore | `notes/receipt-harness-backend-dev-simplify-simplification.md` Finding 1 overstates the duplication at `validate-digest.py:776`. Left uncorrected, a future simplify pass could delete a load-bearing injection check for the wrong reason |
| B-4 | chore | Six refusal conditions enumerated in prose in three places (SKILL.md, the validator, DEC-209). The altitude reader's own recommendation was `leave` |
| B-5 | bug | The validation squad cannot produce its own mutation evidence: `bash-write-guard` denies it the scratch copy and no disposable worktree is provisioned. Today that work falls to whoever holds Bash at the orchestrator tier |
| B-6 | bug | `bash-write-guard` behaved inconsistently across panel cycles — it permitted a `/tmp` copy that the previous cycle recorded as blocked — silently changing what the squad can measure run to run |
| B-7 | bug | A relative-path section edit issued while cwd is the main checkout lands in the **main** checkout silently. Caught and reverted during T-04; a wrong-tree guard is warranted |
| B-8 | bug | `observations-merge.py` raises `FileNotFoundError` on its `.lock` path when the feature's `observations/` directory does not yet exist, instead of creating it |
| B-9 | bug | A lead's run-dir write silently overwrote another run's `state.yaml`: the guard fires only on `digest.md` while `state.yaml` carries `upsert: true`, and the stale run id was reused because `runs/**` returned nothing under glob |
| B-10 | chore | T-01's RED evidence is receipt-narrated; qa reproduced it in panel cycle 2 but not in cycle 1. T-02's is committed in the test file, which is the pattern worth standardising |

---

## What is deliberately traded

`n_a`-only availability is gone. Previously `pass`, `fail` and `grade_2` were exempt from range
derivation so an unresolvable default branch could not block reviewer validation generally. **That
exemption was the bypass** — a checkout that cannot derive the repository-owned range cannot prove
any mechanical result, and falling back to the digest's base would restore digest-chosen grading.
Every derivation or grading failure now refuses and names its repair: unresolvable `origin/HEAD`,
unresolvable `review_sha`, no merge base, a degenerate range, a missing or malformed `test_kinds`
policy, and committed Python that does not parse. Recorded as DEC-209.

The practical cost: a checkout with a broken `origin/HEAD` can no longer land a code review until
it is repaired. Reviews already require `origin/main` for the reviewer's own command, so this
asks for nothing a review did not already need.

---

## State

- Branch `feat/BUG-1081-code-grade-enforcement`, 12 commits on `965c0e35`.
- `review_sha` pinned at `acda74d1527edbea279c914d685baec7eaf9d3cb`.
- Parent issue #1098, sub-issues #1099–#1102, milestone #36, all at **Review**. Source issue
  #1081 is linked and reaches `Done` only when the merge lands, exactly as the BRIEF specifies.
- The worktree still stands and is mine to work in, not to remove.

**The decision I need: ship (with the rebase in P-1), or strike rows first.**
