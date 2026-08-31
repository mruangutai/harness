# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: `2026-08-30-fold-ship-orchestrator` — fold the merged amendments, re-pin, re-gate, ship
- status: **Done**, PR **#996**, branch **0 behind `origin/main`**
- review_sha: **`eb7e7513`** — re-pinned twice this run

**EVERY GATE IS GREEN AT THE PIN THAT SHIPS.** Full unit suite **exit 0**, zero `FAIL` lines, **55**
scripts executed (28 unit + 27 integration, a non-vacuous discovery set). Blocking qa gate **PASS**,
`matrix_ok: true`, `must_fix: []`. Targeted delta panel **PASS**, `severity_max: med`, `must_fix: []`.
SC-11 read-back **3 of 3 PASS**. 17 of 17 live success criteria met.

**The fold, per DEC-205, at `3767624`.** DEC-159 (the in-flight warning moved off the Claude hook onto
the OMP `tool_result` injection), DEC-198 (the 200000 default re-homed to
`.omp/extensions/harness-hooks.ts`) and DEC-201 (self-identification replaced by
`ctx.sessionManager.getSessionFile()`). Each states current truth in the present tense; each falsified
claim survives as one clause so it cannot be re-proposed as new; each amendment block is deleted with
the stray `---` that closed DEC-201's. DEC-201's six evidence bounds survive item for item, and its
retired nonce scheme is recorded as correct-but-inapplicable rather than wrong. Zero `**Amendment`
constructs remain; `DECISIONS.md` is 6305 lines with 188 entries, down from 7414 at base `7ebfc9e`.

**The read-back was run by a reader who did not write the fold**, per SC-11's own method, with the
governing belief and its falsifier pointed to by line. `notes/readback-fold-merge.md`.

**TWO MERGES, TWO RE-PINS, AND THE SECOND WAS NOT FORESEEABLE.** `635cd3ba` → `37676244` → `eb7e7513`.
FEAT-44 shipped under this feature and was merged at `a382827`/`141eca6`; the fold and the first
re-gate followed. Then **FEAT-43 shipped as PR #978 between the push and the merge**, moving
`origin/main` to `24af8d4` and re-conflicting the same two files. The main session merged it at
`eb7e751` — a HEAD move no governed agent may make, correctly refused.

**The second resolution is a PURE UNION, unlike the first.** Measured independently twice:
`harness.json` `test_kinds.integration.detect` base 26 / ours 27 / theirs 27 / **union 28**;
`UNIT_SCRIPTS` 26 / 26 / 28 / **28**; `INTEGRATION_SCRIPTS` 25 / 26 / 26 / **27**. **Zero removals on
either side**, so the union is correct here — where in the FIRST merge it would have been wrong,
because FEAT-44 had deleted two registered files. 27 scripts plus the inert `tests/integration/**`
glob is the 28 in `harness.json`; the glob matches nothing because the directory is absent. Every
entry of all three arrays names a file that exists. The fold survived untouched:
`37676244..eb7e751` is empty for both `DECISIONS.md` and `DECISIONS-INDEX.md`.

**PR #996 deliberately carries two FEAT-46 commits**, `16f86e3` (grilling note) and `7a23d74` (the
operator's hold entry). They touch only `.harness/logs/2026-08-30.md` and a note under FEAT-46 — no
source — and splitting them out needs a history rewrite that moves HEAD and voids the pin. Recorded
so it is not silent. The `test-validate-feature-json.py` substring fix (`79e2639`, PR #997) is
`main`'s work, here by merge, not FEAT-38's.

**FIVE handed-down premises proved FALSE this run, every one caught by a receiver re-measuring.**
(1) "`test_kinds` 28 → 27" — the truth was 29 → 27; the numeral reached no durable record.
(2) "`.claude/settings.json` is absent" — it is present and still registers a PostToolUse hook on
`Write|Edit|Bash`, `check-domain.sh --post`, not the retired watchdog; DEC-159's clause is scoped
"for this" and is true as written. (3) "DEC-159's amendment ends with a stray `---`" — it was
DEC-201's. (4) The goal-check digest's headline says "sixteen live criteria" while its own table
carries 17 rows; the table is right. (5) **This orchestrator's own "61 scripts reporting PASS" was
wrong — the true figure is 55.** Four scripts print their own `PASS <script>` line in a format
byte-identical to the runner's, so a log tally over-counts. Recorded as an error of this run's,
not smoothed.

**Budget: cycles 16 of 30; runs 38 of an informational 20.** No rework — all four squad runs this
phase returned PASS first pass with zero send-backs, so `cycles_used` did not move. The run count is
informational (DEC-157) and stops nothing.

**Feature-close distillation has NOT run.** It runs at merge on a distill mission the main session
dispatches, and is not a ship step.

## Open Questions

None blocking. Seven residual findings are carried to the operator as proposed backlog in
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
  DEC-141). A sibling construct to the abolished amendment, present at the original base `7ebfc9e`
  and outside this feature's approved scope. FEAT-46's triage is the natural home.
- **B-42** — `run-unit-tests.sh --check-kinds` asserts only one direction and would NOT have caught
  the naive-union defect it was cited as guarding. Pre-existing; ranked first on irreversibility.
- **B-43** — four test scripts print their own `PASS <script>` line byte-identically to the runner's
  own marker, so any log-based tally over-counts. It produced a false "61" in this run's reporting.
