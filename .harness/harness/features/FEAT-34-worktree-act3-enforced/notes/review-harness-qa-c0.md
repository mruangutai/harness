# QA gate — FEAT-34, pinned at 513c4a4

**VERDICT: PASS.** `matrix_ok: true`. Full `integration` kind is green (25/25) on a clean solo
re-run; a first solo run showed one transient FAIL, reproduced as clean on immediate re-run —
treated as flaky per the panel's own rule, and reported honestly below, not hidden.

## Matrix — required kinds at the pin

`test_matrix.logic.always = [unit]`, `test_matrix.config.always = []`, `test_matrix.docs.always =
[]`. All 13 tasks are `change_type: logic` except T-05/T-13 (`config`) and T-10/T-12 (`docs`).
`logic` only obligates `unit` — but `.harness/harness.json`'s `unit.detect` glob
(`.../bin/test-*.py`) and `run-unit-tests.sh`'s explicit-list split (issue #160, `UNIT_SCRIPTS`
vs `INTEGRATION_SCRIPTS`) together route every one of this feature's new test files into
`integration` because they fork real subprocesses (git, gh stubs) — so `integration` is the kind
that actually carries this feature's coverage, and the brief's own SCs correctly cite
`evidence: integration` throughout. Nothing in the diff needed `component`, `ui`, `eval` or
`typecheck` (all `cmd: null`, none detects a touched file) — soft-skip, matches the Verification
gaps section of the brief.

| kind | state | cmd | named tests |
|---|---|---|---|
| unit | n/a (no new file routes here) | `run-unit-tests.sh --kind unit` | — |
| integration | **satisfied** | `run-unit-tests.sh --kind integration` | `test-worktree-terminal.py` (19+ cases incl. classify_all i/j/k/l), `test-post-merge-sweep.py` (a-i incl. linked-worktree case), `test-hooks-install.py` (SC-08/13/14), `test-check-state.py` (INV-29 a-f, INV-30 a-c) |
| inspection (SC-09) | **satisfied** | manual grep | all 16 `.claude/agents/harness-*.md` preload `harness-handoff`; `harness-handoff/SKILL.md:82` carries "One act is never yours... removing a worktree" — verified directly, not by re-trusting T-10's own verify string |

`--check-kinds` (the drift + cross-check detector) passes: `test-worktree-terminal.py`,
`test-post-merge-sweep.py`, `test-hooks-install.py` are all registered in both
`INTEGRATION_SCRIPTS` (`run-unit-tests.sh:19`) and `test_kinds.integration.detect`
(`.harness/harness.json`) — T-05 and T-13's registration verified directly, not by trusting their
own `verify:` string.

## Suite execution — I am sole runner, evidence below

- `ps` checked clean before every run of mine. No `run-unit-tests.sh`/`test-*.py` of ANY kind was
  live before either of my two full runs.
- Run 1: `run-unit-tests.sh --kind integration`, wall clock **236s**, **exit 1** —
  `test-validate-digest.py` case `[hook] F1.3 unquoted apostrophe must not fuse list entries`
  failed (`stderr should mention 'worst member verdict'`). This file is untouched by this
  feature's diff (`git log` shows its last touch is commit `9ad8f35`, FEAT-32, well before
  `9165162..513c4a4`) — not this feature's code surface.
- Confirmed no leftover process after the timeout/kill; ran the single test alone, clean, passed.
- Run 2: full `integration` kind again, clean `ps` before start, wall clock **235s**, **exit 0**,
  all 25 scripts PASS including the three new ones and `test-check-state.py`.
- **Conclusion on the F1.3 failure: a genuine flake, not a diff defect.** It is unrelated code,
  it failed once and passed on immediate isolated re-run and inside the full-suite re-run, and I
  am the confirmed sole runner for both attempts (no concurrent `run-unit-tests.sh` of mine or
  anyone else's). Reported rather than suppressed, per the instruction to re-run alone and say so.
- **Q15 (wall clock, prior open question): reproduces, consistently.** Two clean solo runs, no
  concurrent load either time, both land at ~235-236s against the script's own documented ~15.6s
  integration baseline — roughly the same ~15x gap the prior digest measured at ~18x. This is not
  explained by the concurrency hazard (nothing else was running during either of my measured
  runs) and is not a one-off — it is a real, reproducible property of this machine/tree today,
  not resolved by this note, but no longer merely "attributed to unrelated load and not accepted
  as fact." It should be escalated as a real perf question, separate from correctness.
- One benign observation, not an injection: mid-run I twice saw a *different* process pair
  (`bash .agents/skills/harness/bin/run-unit-tests.sh` / a child `test-*.py`) appear transiently
  in `ps`. Path prefix is `.agents/`, not this worktree's `.claude/`, so it is not one of this
  panel's runs and not this checkout — noted for completeness, not acted on, and it was gone by
  the time each of my own runs started.

## Adequacy — what the suite actually binds

**worktree_terminal.py.** `classify` — all six klass paths (`terminal`, `exempt_absent`,
`unresolved` × {out-of-segment, unresolvable default_branch, ls-tree error, ambiguous prefix,
unparseable feature.json}) each hit by a named case in `test-worktree-terminal.py` (a)-(h), with
the short-name-vs-absent discriminator (e)/(f) demonstrated failing first against a
lookup-returned-nothing stub, per the brief's own cited red proof. `classify_all` — D-10's full
5-branch posture (harness-only fails (i); absent checkout silent (j); unenumerable checkout
blocking (k), discriminated from (j) both ways; fleet-unloadable alongside-not-instead-of (l)) —
all four asserted, three with an explicit demonstrated-failing variant. **This binds past the
happy path**: every "silently stops refusing" shape the brief worries about has its own red proof
run, not just asserted.

**check-state.sh INV-29/INV-30.** `test-check-state.py` cases (a)-(f) match SC-01 through SC-05
one-for-one, asserted on the finding line's own `VIOLATION` prefix (never exit code, per the
brief's own stated trap at :1214-1218) and on the exact composed removal-command string, with the
three "must-fail" malformed-message inputs demonstrated first. INV-30 (a)-(c) match SC-12,
including the discriminating clause (b) — same fixture, only the `gh` stub's milestone-state
answer differs — which is exactly the "already proven" INV-30-keyed-on-status-alone red proof
cited in the dispatch; I did not re-run that mutation, per instruction.

**post-merge-sweep.sh and the shim.** `test-post-merge-sweep.py` covers both merge shapes (a/b),
self-exclusion with an unguarded-variant red proof (c), per-feature record assertion rather than
a total count (d, SC-11), the record-then-remove order via a gh-stub failure that leaves one
worktree standing and removes the other (e, D-04), an unresolved record left alone (f), the
CWD-outside-repo defect proof (h), and — the one I weighted heaviest — the **linked-worktree
main-checkout-vs-BIN_DIR split** (SC-16, case `case_linked_worktree_main_checkout`, ~line 665):
asserts the resolved main-checkout-root line equals R and not WT_CALLER, that R's milestone (810)
closes, that WT_CALLER's divergent milestone (811) is never called (asserted on absence of a call
naming it, not a substring), and that the correct worktree is removed. This is graded from the
printed "resolved main checkout root:" line, never from a SKIP branch, matching the brief's own
insistence that no skip is ever reached in the defect this closes.

`.claude/skills/harness/hooks/post-merge` (the shim) is exercised end-to-end by
`test-hooks-install.py`'s `case_sc14_end_to_end_and_red_proof` — a real fresh clone, the setup
step run, no hand-installed hook, a real merge, and the standing worktree actually gone — which is
the one test in the suite that would go red if the shim pointed at a path that does not exist
(SC-14's own stated red proof for SC-08 alone being insufficient).

**harness-init `core.hooksPath` step.** `case_sc08_before_and_after` (absent → reported not
installed → present and executable, two separate assertions), `case_sc13_idempotence` (run twice,
same value, both exit 0), `case_sc13_reporting_and_red_proof` (an unrelated pre-set value is
reported by content, with an explicit red-proof variant that writes unconditionally and is shown
to pass idempotence and fail reporting). All three graded, all three named.

## SCs graded for the wrong reason — none found

I looked specifically for the pattern the dispatch warns about (N-case criteria satisfied by a
file-global grep, or a green suite that would stay green if the behaviour were deleted).
- SC-05/SC-15/T-02(i-l)/T-07(f): all graded per-clause with explicit red-proof demonstrations
  already present in the suite — not a total-count or file-global assertion anywhere I found.
- SC-09 (inspection): I re-derived it myself directly against `harness-handoff/SKILL.md` and the
  16 agent frontmatter blocks rather than trusting T-10's own `verify:` (which itself is a loose
  `grep -q ... || true` loop that cannot fail on its own — a genuine finding, see below).
- SC-16: graded on the printed resolved-root line and an absence-of-a-named-call assertion, not a
  substring — matches DEC-169's absence-needs-a-presence-neighbor rule (the milestone-810-closed
  assertion is the presence neighbor to milestone-811-never-called).

**One finding on T-10's own verify string** (not a code defect, a verify-command weakness):
`for a in .claude/agents/harness-*.md; do grep -q "worktree" "$a" || true; done; grep -lc
"worktree remove" ...` — the first loop's `|| true` makes it incapable of ever failing regardless
of what it finds, so T-10's own verify cannot by itself prove SC-09; SC-09 is actually proven by
my direct inspection above, not by that command. Advisory only, since the underlying behaviour
(all 16 reach the sentence via harness-handoff) is independently confirmed true.

## SC evidence map

| SC | test |
|---|---|
| SC-01 | `test-check-state.py` case (a)+(b), removal-command string |
| SC-02 | `test-check-state.py` case (c), deadlock both directions |
| SC-03 | `test-check-state.py` case (d), two clauses |
| SC-04 | `test-check-state.py` case (e); library-level in `test-worktree-terminal.py` (i) |
| SC-05 | `test-check-state.py` case (f), four sub-assertions |
| SC-06 | `test-post-merge-sweep.py` (a)+(b) |
| SC-07 | `test-post-merge-sweep.py` (c), unguarded red proof |
| SC-08 | `test-hooks-install.py` `case_sc08_before_and_after` |
| SC-09 | direct inspection (above); T-10's own verify is weak, see finding |
| SC-10 | this run: `check-state.sh` clean + full integration green (2nd run) |
| SC-11 | `test-post-merge-sweep.py` (d), per-feature |
| SC-12 | `test-check-state.py` INV-30 (a)-(c) |
| SC-13 | `test-hooks-install.py` `case_sc13_idempotence` + `case_sc13_reporting_and_red_proof` |
| SC-14 | `test-hooks-install.py` `case_sc14_end_to_end_and_red_proof` |
| SC-15 | `test-worktree-terminal.py` (j)/(k)/(l) |
| SC-16 | `test-post-merge-sweep.py` `case_linked_worktree_main_checkout` |

## Phase 1 vs Phase 2 — the delta

Reading the brief/plan cold, I expected exactly these kinds of tests: real-git fixtures for the
deadlock case, a second-repository fixture, a dirty-tree case, both merge shapes, self-exclusion,
a fresh-clone hooks fixture, and per-agent reachability. All of it exists, matching Phase 1
one-for-one — no gap between what I expected blind and what the diff actually built. The one
thing I had NOT anticipated blind was the linked-worktree BIN_DIR-vs-main-checkout split
(Amendment 3/SC-16) — that is new information the brief itself flags as a late-discovered defect,
not a coverage gap I'm reporting after the fact.

## Coverage gaps

None found against the signed matrix. `unit`/`component`/`ui`/`eval`/`typecheck` are correctly
inapplicable.

## Open questions

- Q15 (carried forward, now measured twice, not once): the ~15x integration wall-clock gap
  against the documented ~15.6s baseline reproduces on two clean solo runs with no concurrent
  load. This is a real performance question for the operator/dev-ops, not a QA-gate blocker —
  correctness is unaffected, but it changes what "the suite is slow today because of load" can be
  taken to mean going forward.
