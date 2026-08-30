# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: `2026-08-30-fold-ship-orchestrator` — fold the merged amendments, re-pin, re-gate, ship
- status: **Done**, PR **#996**, branch **0 behind `origin/main`**
- review_sha: **`37676244`** — re-pinned this run

**THE MERGE BLOCKER IS GONE, THE FOLD IS DONE, AND EVERY GATE IS GREEN AT THE NEW PIN.**
`origin/main` is merged (`a382827`, re-merged at `141eca6`), the three conflicts are resolved, and
the three amendments FEAT-44 brought in are folded at `3767624`. Full unit suite **exit 0**, zero
`FAIL` lines. Blocking qa gate **PASS** (`matrix_ok: true`, `must_fix: []`). Targeted delta panel
**PASS** (`severity_max: med`, `must_fix: []`). SC-11 read-back **3 of 3 PASS**.

**The fold, per DEC-205.** DEC-159 (the in-flight warning moved off the Claude hook onto the OMP
`tool_result` injection), DEC-198 (the 200000 default re-homed to `.omp/extensions/harness-hooks.ts`)
and DEC-201 (self-identification replaced by `ctx.sessionManager.getSessionFile()`). Each entry
states current truth in the present tense; each falsified claim survives as one clause so it cannot
be re-proposed as new; each amendment block is deleted, with the stray `---` that closed DEC-201's.
DEC-201's six evidence bounds survive item for item — one OMP build measured twice on one machine,
the committed probe path, the version-floor risk, that `probe-omp-session-accessor.py` fails rather
than skips, that the check is MANUAL and not a CI gate, and that this is one build's observed
behaviour rather than a property of the OMP API — and its retired nonce scheme is recorded as
correct-but-inapplicable rather than wrong.

**The read-back was run by a reader who did not write the fold**, per SC-11's own method, with the
governing belief and its falsifier pointed to by line for each entry. `notes/readback-fold-merge.md`;
the reviewer's own note is `notes/review-harness-code-reviewer-readback-fold.md`. Three corroborating
details of retired mechanisms were dropped and each was judged defensible on the record.

**The conflict resolutions were GRADED, not assumed** — no reviewer had seen them before this run.
`harness.json` is not a union: branch 29, main 26, union would have been 29, the pin is 27, and the
two dropped are exactly the files FEAT-44 deleted. All 26 concrete registrations name a file that
exists. `DECISIONS-INDEX.md` is byte-identical to a fresh regeneration, proving it was regenerated
and not hand-merged; 188 rows, 188 live headings, zero orphans.

**WHY `review_sha` MOVED, and it had to.** The prior pin was **`635cd3ba`**. It described a tree in
which `origin/main` had never been merged. The merge changed source under it — `harness.json`,
`run-unit-tests.sh` and the generated index — and the fold then changed the authority itself. A pin
that no longer contains the work under review returns PASS on nothing. `37676244` is the fold commit
and contains every source change this feature ships.

**PR #996 deliberately carries two FEAT-46 commits**, `16f86e3` (grilling note) and `7a23d74` (the
operator's hold entry). They touch only `.harness/logs/2026-08-30.md` and a note under FEAT-46 — no
source — and splitting them out would need a history rewrite that moves HEAD and voids the pin.
Recorded so it is not silent. The `test-validate-feature-json.py` substring fix (`79e2639`, PR #997)
is `main`'s work, here by merge, and is not FEAT-38's.

**Three handed-down premises proved FALSE this run, all caught by re-measurement.** (1) "`test_kinds`
28 → 27" — no counting method yields that pair; the truth is 29 → 27, and the numeral reached no
durable record. (2) "`.claude/settings.json` is absent" — it is present and still registers a
PostToolUse hook on `Write|Edit|Bash`, `check-domain.sh --post`, not the retired watchdog; DEC-159's
clause is scoped "for this" and is true as written. (3) "DEC-159's amendment ends with a stray `---`"
— it was DEC-201's. A fourth, smaller: the goal-check digest's headline says "sixteen live criteria"
while its own table carries 17 rows; the table is right, and with SC-13 answered it is **17 of 17**.

**Budget: cycles 16 of 30; runs 37 of an informational 20.** No rework this run — all three squad runs
returned PASS first pass with zero send-backs, so `cycles_used` did not move. The run count is
informational (DEC-157) and stops nothing; each run here closed a named gate.

**Feature-close distillation has NOT run.** It runs at merge on a distill mission the main session
dispatches, and is not a ship step.

## Open Questions

None blocking. Six residual findings are carried to the operator as proposed backlog in
`notes/ship-review-2026-08-30-fold-ship.md`; anything not accepted there dies silently.

- **B-25** — `bash-write-guard.sh` cannot expand shell variables and does not track `cd`; it resolves
  targets against the session root, so `cd <dir> && sed -i '' … plan.yaml` was denied while the same
  command with a literal absolute path was allowed, and `check-domain.sh --resolve` grants that path.
- **B-26** — `/usr/bin/grep` is `pi-uu-grep 0.2.0`, in which `^+` matches EVERY line. Four false
  readings across this feature; every affected measurement was redone in Python.
- **B-39** — a run-directory slug collision destroyed a record. `runs/` is gitignored, so it was
  unrecoverable, and nothing in the contract stops a lead reusing a slug.
- **B-40** — `DEC-159` still says the handoff shape gate denies at >40 lines while the same entry
  records the cap raised to ~60 at DEC-160. Un-amended remainder; reported, not edited.
- **B-41** — three `### DEC-NNN addendum` sub-headings survive in `DECISIONS.md` (DEC-124, DEC-125,
  DEC-141). A sibling construct to the abolished amendment, present at the feature's original base
  `7ebfc9e` and outside its approved scope. FEAT-46's triage is the natural home.
- **B-42** — `run-unit-tests.sh --check-kinds` asserts only one direction and would NOT have caught
  the naive-union defect it was cited as guarding. Correct today only because qa measured file
  existence directly. Pre-existing; the panel ranked it first on irreversibility.
