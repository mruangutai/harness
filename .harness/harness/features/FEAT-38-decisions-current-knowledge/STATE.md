# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: `2026-08-30-uat-repoint-product` — PASS, SC-13's UAT script repointed at the live pin
- squad: product (`harness-pm`, via `harness-product-lead`)
- status: **Review**, and **AWAITING THE OPERATOR**. No PR, no merge, no ship.

**All 28 planned tasks read `done`**, landed in `depends_on` order and each verified by the
orchestrator running the task's own `verify:` extracted from the signed `plan.yaml` with
`harness_yaml.load_plan` rather than retyped: T-27 (`0a94d91`), T-24 (`8c879f5`), T-28 and T-29
(`70690ea`), T-25 (`8a7c75c`), then qa evidence and the SIMPLIFY apply (`635cd3b`).

**`review_sha` is `635cd3ba`**, pinned at the tip that CONTAINS the build, after SIMPLIFY so no
apply commit could move the tip under the panel. The stale `48bbe7e` pin is gone.

**Both gates that can be closed here are closed.** The blocking qa gate PASSES — `matrix_ok: true`,
`must_fix: []`, suite exit 0, ZERO `FAIL ` lines, all **55** registered scripts actually run, so the
green is not a gate discovering nothing. The review panel PASSES at the pin with `severity_max: low`
and no `must_fix`; `gates.review` is `advisory_unless_high`, so it does not gate.

**THE SHIP IS BLOCKED ON ONE THING: SC-13, and it is UNRUN, not failed.**

**CORRECTION — the previous `## Current` asserted "SC-13 STANDS and does not return to the
operator". THAT WAS WRONG, and it was the orchestrator's error.** It restated the dispatch's premise
instead of checking it. `harness-pm`'s goal-check checked the file and found `notes/uat-FEAT-38.md`
reads `status: ready` with all four `result:` fields BLANK. Verified at source: no operator
judgement has ever been recorded. Operator ruling 6 (`notes/answers-2026-08-29-24.md:20-23`) rules
that SC-13 "STANDS and is not re-run" — but that is a ruling about not RE-RUNNING a judgement, and
the record contains none to stand on. `gates.uat` is `blocking_when_uat_criteria_exist`.

**The goal-check grades 15 of 16 live criteria MET at the pin**; SC-13 is the sixteenth.

**What T-27 did to SC-13's subject was measured, not argued.** Ruling 6 voids its own assumption if
T-27 touched prose. It did not: at `0a94d91` the prose line sequences are IDENTICAL either side
(5067 lines each; 20 removed = 11 markers + 9 blanks; zero insertions). Across the pin gap
`48bbe7e..635cd3ba`, **DEC-138 (128 lines) and DEC-174 (122 lines) are BYTE-IDENTICAL**, and
**DEC-181 went 51 → 46 lines by losing exactly 3 claim markers and 2 blanks — zero prose, zero
additions.** So the operator's reading, if it was ever made, transfers intact.

**Ruling 2 asserted directly, never inferred from a green suite.** `check-decision-anchors.py` and
`test-check-decision-anchors.py` are byte-identical to `git show 99bb52c:` (sha256 `adb9a648…`,
`7a4e0ba1…`) and named by BOTH registration sides. Re-asserted after the SIMPLIFY apply. The
retained checker also demonstrably still reports RED: on a `/tmp` copy it exits 0 over 20 anchors
and exits 1 with one fabricated anchor planted, so the tree was never perturbed.

**Budget: cycles 16 of 30; runs 34 of an informational 20.** Two rework cycles: the panel's SC-11
seam send-back, and this UAT repoint. Every other run returned PASS first-pass. `len(runs)` passed
`max_total_runs` long ago; INV-22 will say so, the count is informational and stops nothing, and
these runs earn their place — they closed the whole remaining build, both gates and the goal-check.

## Open Questions

**Blocking — the operator alone can close it:**

- **SC-13 must be run, or its judgement recorded.** The script is repointed at `635cd3ba`, correct
  and operator-ready (~15 minutes). If the operator did read those three entries and simply never
  wrote it down, saying so is enough and it gets recorded. Nobody else may set `status:` or fill a
  `result:` field, and no agent may mark an SC met.

**Not blocking, carried to the operator in the ship briefing:**

- **A run-directory collision destroyed a record.** The T-27 lead wrote into
  `runs/2026-08-29-01-product`, already the panel-revision run's directory, overwriting its
  `digest.md` and `state.yaml`. `runs/` is gitignored, so it was never in git and is unrecoverable.
  Artifacts were relocated to `runs/t27-product/` and a tombstone left. Nothing in the run-directory
  contract stops a lead choosing a slug that already exists.
- **Bare relative paths resolve against the OUTER checkout, not the assigned worktree.** Measured
  three times in one panel; two review artifacts were written into the main checkout and are still
  stray, untracked, there. Byte-identical copies were recovered into this tree; removing the
  originals is the operator's, as the orchestrator does not touch that checkout.
- **`bash-write-guard.sh` cannot expand shell variables and does not track `cd`.** It resolves
  targets against the session root, so `cd <dir> && sed -i '' … plan.yaml` and `sed -i '' … "$P"`
  were both denied "outside your domain" while the identical command with a literal absolute path
  was allowed — and `check-domain.sh --resolve` grants `plan.yaml` to `harness-orchestrator`, so the
  two surfaces disagree.
- **`/usr/bin/grep` is `pi-uu-grep 0.2.0`, in which `^+` matches EVERY line.** It produced four
  false readings across this phase, including an apparent 83 insertions against a true `--numstat`
  of zero. Every affected measurement was redone in Python.
- **A stale prose reference SC-18 forbids fixing**: `check-decision-anchors.py`'s docstring still
  calls the snippet problem "the executable-claims checker's job (a different tool)". Pre-existing,
  not introduced, and SC-18 pins that file byte-identical to `99bb52c`.
- **DEC-205 names two refused rot detectors but not what compensates today** — the answer lives only
  in `BRIEF.md`. The remedy would add positive content to DEC-205, which the ruling forbids.
- **The `bin/` argv class is NOT empty**: 11 of 70 scripts build argv from a parsed value, recorded
  as remaining work in two risk groups. Backlog under REQ-10's reconciliation, not this feature's
  destination.
- **SC-04's pinned baseline `37` for `am.N` does not reproduce** (34 occurrences / 31 lines) while
  its `30` and `24` reproduce exactly. Every pattern is 0 at the pin, so intent is met.
- Non-blocking Q6..Q10 from the plan phase remain open and gate nothing. REQ-08 and SC-09 are
  retired tombstones, graded by nobody.
