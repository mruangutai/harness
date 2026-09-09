# Code review — c18 — test-only SC-04 evidence diff at `9fe5cf31`

**BLUF: PASS.** All three gaps genuinely gain automated coverage; two (A, B) bind their SC-04 clause
robustly. Gap C binds 3 of its 4 noise arms robustly (crash-propagation) but its 4th arm (unreadable/
`OSError`) is bound only conditionally on the runtime not being root — a real but narrow, non-gating
verification weakness. No must_fix. `severity_max: low`.

## Census (self-verified, not taken on trust)

`git -C <worktree> diff --stat 9fe5cf31^..9fe5cf31` → `tests/integration/test-merge-gate.py | 38
+++++++++++++++++++++++++++++++++++- 1 file changed, 37 insertions(+), 1 deletion(-)`. Matches the
dispatch exactly. Full diff read (`git diff 9fe5cf31^..9fe5cf31 --`): one line renamed/strengthened
(:67-68, Gap A), two new blocks added (:164-174 Gap B, :183-206 Gap C). No other file touched. No
production source in this cycle, confirmed. `git status --porcelain` at end of my run: two lines,
`M feature.json` and `?? notes/review-harness-ui-reviewer-c18.md` — **neither authored by me**; I made
zero writes to the worktree (verified: every bash call I ran was `git diff/status/rev-parse`, `grep`,
`whoami`/`id`, and one direct `python3 tests/integration/test-merge-gate.py` invocation, which only
touches system `/tmp` via `tempfile.mkdtemp()`, never the worktree). One attempted `cp`/redirect for a
dynamic-mutation harness was correctly blocked by `bash-write-guard` before any write occurred — see
Methodology below.

Live run of the suite as committed: **34/34 `ok`, exit 0, `ALL PASSED`** (confirms baseline green,
matches the panel's claim).

## Methodology note — dynamic mutation not executable under this role

The dispatch's PRED-1..PRED-5 ask for measured mutant reddening on a **copy** under a temp root.
`harness-code-reviewer` is read-only Bash (git diff only) and Write-restricted to two paths (my own
report, my Expertise) — confirmed live: a `cp` to `mktemp -d` was blocked by `bash-write-guard`
("harness-code-reviewer is READ-ONLY... switching tools is guardrail evasion, DEC-151"). I did not
route around this. Every PRED verdict below is **static code-path tracing against the actual pinned
`merge-gate.py`** (read in full at `9fe5cf31`), not executed mutation. `C18Evidence` (harness-qa,
Bash-write-capable) is the peer positioned to execute the dynamic form; my verdicts are offered as an
independent, code-grounded cross-check, and I flag anywhere the two methods could disagree.

## Gap A — `test-merge-gate.py:67-68`

Clause carried: SC-04(a), "single-owner deny reason names the feature **and** the re-run command."
Assertion: `d == "deny" and "FEAT-9001-fixture-non-era" in reason and "gh-sync.py open" in reason`.

**Genuine, not incidental.** The fixture (`fixture()`, default args) creates exactly one feature
record, `entry=None`, `repo` pinned. Traced the only reachable path: `owners` has length 1 → skips
ambiguity (`:172`) and era-exempt (`:179`, id not in `BUILD_ENTRY_ERA_EXEMPT`) → `entry` not in the
allow set (`:182`) → `repo_pinned` true, skips the config deny (`:187`) → lands on the single-owner
receipt deny (`:190-192`), which is the **only** deny path in `main()` that interpolates both `feat`
and `command_line` into one string. No other deny path in this file's fixture shape could
coincidentally satisfy both substrings. PRED-4 (verify: substring match survives the rename):
confirmed independently — `check()` prints `f"{'ok   ' if condition else 'FAIL '} {name}"`, i.e.
`"ok    " + name`; `plan.yaml:1066`'s `grep -qF "ok    $n"` with the OLD literal `"T-05 non-era absent
build_entry denies"` is a strict prefix of the new printed line, so the grep still matches. (Matches
`review-harness-ui-reviewer-c18.md:67-71` — independently re-derived, not copied.)

**Gap A: YES, genuinely carried.**

## Gap B — `test-merge-gate.py:164-174`

Clause carried: SC-04(g), "ambiguity deny reached even when a claimant IS era-exempt — ambiguity is
decided before the era gate." Assertion: `d == "deny" and "FEAT-9001-fixture-non-era" in reason and
era_id in reason and "gh-sync.py" not in reason`, second claimant `BUG-1030-stale-anchor-write-hazard`
— confirmed present in `feature_schema.BUILD_ENTRY_ERA_EXEMPT` (`feature_schema.py:227`).

**Binds ordering, not just "a deny happened."** Read `main()` top to bottom (`:167-181`): the
`len(owners) > 1` check (`:172`) runs unconditionally, before `owners[0]` is ever touched, so era
status of *either* claimant cannot suppress it in the shipped code. Statically traced two plausible
"era decided first" mutant shapes against this fixture and both redden the case, regardless of
`glob.glob`'s (unspecified) iteration order:
- *any-owner-era-exempt-allows-first*: `owners` contains the era-exempt id → mutant returns ALLOW →
  `d is None`, failing `d == "deny"`.
- *hoist the era check above the length check, keyed on `owners[0]`*: if `owners[0]` resolves to the
  era-exempt record, same ALLOW failure as above; if `owners[0]` resolves to `FEAT-9001`, the era
  check is skipped and the mutant falls through to treat it as the sole owner, reaching the
  single-owner receipt deny (`:190-192`) — which threads a `gh-sync.py ...` command line into
  `reason`, and the case's own `"gh-sync.py" not in reason` clause rejects that. Both branches of this
  mutant redden the case on *either* glob order, exactly as PRED-3 claims.

The assertion is not satisfiable by a gate that decided era first under either mutant shape I could
construct that plausibly implements "era first." **Gap B: YES, genuinely carried, and it binds
ordering specifically, not merely presence of a deny.**

## Gap C — `test-merge-gate.py:183-206`

Clause carried: SC-04(h), "one owner plus any amount of noise ... changes NO verdict," across all four
enumerated noise kinds (unreadable, malformed, non-object, different-branch). Assertion: `r.returncode
== 0 and d is None` against `fixture(entry="opened")` plus the four noise records.

**3 of 4 arms robustly bound, via crash-propagation, not "quietly ignored."** Traced `feature_for`
(`merge-gate.py:132-142`): its `try` covers only `open`+`json.load`; the `isinstance(document, dict)`
test and the `document.get("branch") == branch` comparison are **outside** that `try`, at the same
level as the `try/except` itself, so any exception either arm currently guards propagates unchecked
out of `feature_for` into `main()`'s outer `except Exception: deny(...)` (`:193-194`) — flipping `d`
from `None` to `"deny"`. Traced each removal:
- drop `JSONDecodeError` from the caught tuple → `FEAT-9003-malformed`'s literal `"{"` raises inside
  the `try` → propagates → deny. **Catches.**
- drop the `isinstance(document, dict)` guard → `FEAT-9004-non-object`'s `[]` has no `.get` →
  `AttributeError` → propagates → deny. **Catches.**
- drop the `== branch` comparison (treat any dict with a `branch` key as a match) →
  `FEAT-9005-different-branch` becomes a second owner → `len(owners) > 1` → deny. **Catches.**

All three genuinely bind their clause: the assertion is NOT incidentally satisfied for these three,
because removing any one of their guards produces an observable, uncaught state change the assertion
detects. This confirms PRED-1 for those three arms.

**The 4th arm (`OSError`/unreadable) is bound only conditionally, confirming PRED-2.** The fixture
writes `json.dump({})` then `os.chmod(noise_file, 0)` (:187-190 of the diff). Two independent
weaknesses compound:
1. **Environment-conditional.** POSIX permission bits do not block `root` (`geteuid() == 0` bypasses
   DAC). I confirmed this run is non-root (`id -u` → `501`, `os.geteuid()` → `501`), so `open()` on
   the chmod-0 file genuinely raises `PermissionError` (an `OSError` subclass) here, and dropping the
   `OSError` arm *would* redden this case in this environment via the same crash-propagation path
   above. But under a root-running CI container (a real, common configuration, not hypothetical),
   `open()` on that file **succeeds** — the `OSError` except clause then sees zero executions for this
   fixture, and the test cannot tell.
2. **Content is inert either way.** The fixture's payload is `{}` — no `"branch"` key. Even if the
   file became readable (root, or the `OSError` arm silently removed in a permissive environment), the
   record still fails `document.get("branch") == branch` and is correctly excluded — so `d is None`
   would still hold, and the case would still print `ok`, while the `OSError` arm itself had never
   fired at all. A fixture whose content *would* claim `branch="feature/test"` if it became readable
   (so that "becomes readable" flips the verdict to an ambiguity deny) is what PRED-2 correctly
   identifies as the stronger form — the current one does not bind the `OSError` arm **on its own**,
   only in combination with the (unstated, environment-dependent) assumption that the test process is
   never root.

**Gap C: YES for 3 of 4 clauses (malformed, non-object, different-branch), CONDITIONAL for the 4th
(unreadable)** — true and discriminating in this and presumably most CI environments, but silently
untested under a root-running test process. This is a real, if narrow, coverage gap in the evidence
the c18 dispatch was scoped to close, not a production defect (production behaviour for this arm was
already ruled correct by inspection at c17, `merge-gate.py:138`).

## Fixture isolation and determinism (review point 2)

`fixture()` (`:21-42`) calls `tempfile.mkdtemp()` fresh on every invocation; every case in this diff
calls `fixture(...)` for its own root, so noise from the Gap C case cannot leak into any later case —
confirmed by reading every subsequent case in the file, each of which re-calls `fixture()`. `PRED-5`
confirmed: no inheritance.

The `os.chmod(noise_file, 0)` fixture does **not** endanger cleanup. POSIX unlink requires write+exec
permission on the *containing directory*, not on the target file's own mode bits — `noise_directory`
is created via plain `os.makedirs` (default mode), so `rm -rf`/`shutil.rmtree` by the owning user (or
root) removes it without issue. This whole file never explicitly cleans up its `tempfile.mkdtemp()`
roots (pre-existing pattern across the entire suite, not introduced by this diff) — so accumulation
across repeated runs is a pre-existing, unrelated hygiene note, not a new finding.

## code_grade

Ran the grader over the canonical range: `python3 code-grade.py --base "$(git merge-base origin/main
9fe5cf31)" --head 9fe5cf31`. 53 functions graded, 49 PASS, 4 gated at grade 2 (none grade 1, none
production-grade-3-below-bar) — **identical to every prior cycle's report for this feature**
(c0/c2/c3/c4/c6/c7/c14/c17 all report the same shape). None of the four gated records are in
`test-merge-gate.py`; none were touched by `9fe5cf31` (test-only diff, no new function definitions —
the added lines are inline top-level script statements). Reasons, unchanged from c17:
- `merge-gate.py:154 main` (cyclomatic 19/cognitive 22/ABC 45, bar 4) — pre-existing in-source
  `GRADE-2 REASON` comment: orchestration boundary, helpers own parsing/resolution/rendering, this
  function preserves the policy's ordered exits (the exact ordering Gap B's new case now verifies).
- `test-check-state.py:4621 case_t06_build_entry_invariant`, `test-hooks-install.py:396
  _run_merge_and_check`, `test-post-merge-sweep.py:885 case_t07_build_entry_receipt` — pre-existing
  fixture/assertion-driven integration-test case bodies, ABC-driven, unrelated to this cycle.

`code_grade: grade_2`.

## Findings

- **Gap C / OSError arm — environment-conditional coverage.** `severity: low`. Failure scenario: a CI
  runner that executes this suite as `root` (common in minimal containers) silently loses coverage of
  `feature_for`'s `OSError` except-arm for this case — `os.chmod(noise_file, 0)` no longer blocks
  `open()`, and the fixture's `{}` payload has no `branch` key so the verdict is unaffected either way
  — while the case still prints `ok`. Not gating: production behaviour for this arm is unaffected and
  was already ruled correct by inspection at c17; this is a verification-strength gap, not a
  behavioural one, and the budget for this feature is exhausted (no fix dispatchable this cycle).
  `should_fix` (future cycle, if reopened): make the unreadable fixture's content claim
  `branch="feature/test"` so that "readable" flips the verdict to an ambiguity deny, binding the arm
  independent of runtime UID.

## Already-ruled items — status unchanged

Q2 (verify: block names only four qualnames), Q3 (`merge_target` vs git option abbreviation), Q5
(21-name enumeration vs 26 `verify:`-gated names) — none touched by this diff; no standing change.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Gaps A and B genuinely close SC-04's evidence gaps; Gap C closes 3 of 4 noise arms robustly, the 4th (unreadable) only conditionally on a non-root runtime — real but narrow, non-gating."
  severity_max: low
  findings: 1
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  reviewed: "9fe5cf3112aed6782dfe3f1833b5e7077b31d953^..9fe5cf3112aed6782dfe3f1833b5e7077b31d953"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "Gap C's unreadable-noise fixture (content {} + chmod 0) binds the OSError arm only when the test process is non-root; confirmed non-root here (euid 501), but a root-running CI would silently drop that arm's coverage while the case still passes. Budget is exhausted this cycle — carry as backlog for a future evidence cycle if SC-04 is reopened, alongside Q2/Q3/Q5.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry/.harness/harness/features/BUG-1309-mirror-build-entry/notes/review-harness-code-reviewer-c18.md
```
