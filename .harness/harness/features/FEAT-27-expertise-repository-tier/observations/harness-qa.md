# Observations — harness-qa — FEAT-27

- 2026-08-19: `bash-write-guard.sh` denies `cp`/`sed -i` on ANY path under the scratchpad
  (`check-domain.sh --resolve` answers `NOBODY` there) — not just repo paths. Mutation-probe
  copies must go through the `Write` tool, never `Bash cp`, even in scratchpad. Cost me one
  self-inflicted bug: I wrote a mutated `check-expertise.sh` copy under the baseline's filename
  by re-using a mutation draft as the "baseline" — caught only because the T-03 abspath probe
  (case6) failed against what I *thought* was the unmutated baseline. Lesson: run the baseline
  probe FIRST, unconditionally, before touching any mutant file, and diff the baseline copy
  against the real file's content (not just its md5/existence) before trusting it as control.
- 2026-08-19: `run_cmd([CHECK, ...], cwd=some_tempdir)` in a probe harness needs `CHECK` to be an
  **absolute** path — `./check-expertise.sh` resolves against the harness's own cwd at spawn
  time, not the subprocess's `cwd=` override, so a relative `CHECK_EXPERTISE_BIN` silently
  breaks exactly the bare-path-invocation case (case6) it's supposed to prove.
- 2026-08-19: FEAT-27 T-02's case12 (hostile `agent_type` values against the
  `^harness-[a-z0-9-]+$` regex) is fully vacuous under mutation — removing the regex entirely
  produces empty stdout for all four hostile values (`harness-`, `harness-qa/../../etc`,
  `harness-*`, `harness-qa;id`) because none of their interpolated paths match a real file on
  disk in the case's own fixture (which only writes `harness-qa.md`). The `harness-*` value in
  particular does NOT glob-match a real `harness-qa.md` file, because it sits inside double
  quotes in the script (`"$agent.md"`), so the shell treats its `*` as a literal character, not
  a wildcard, when the surrounding word undergoes pathname expansion. The regex's actual "only
  harness-agents" filtering IS bound — but by case6 (`some-other-agent`), a value that predates
  T-02's suffix-hygiene addition and would have been rejected by the pre-change script's plain
  `case` pattern too. So 1c's specific contribution (rejecting a bad *suffix* after a valid
  `harness-` prefix) has zero test coverage in the current suite.
- 2026-08-19: Reproduced T-07's case13 mutant myself at `252fa72` (single-line delete of
  `[ -r "$f" ] || continue`, confirmed by diff, run via `INJECT_EXPERTISE_BIN`): 18/19, case13
  the only FAIL, and of its five Python `checks` entries only index 3 (`"kaya" not in ctx`) and
  index 4 (`stderr == ""`) flip — indices 0/1/2 (exit 0, repo header present, repo body present)
  stay green under this specific mutant because the script has no `set -e` (its own trailing
  `exit 0` always fires) and the harness-tier loop iteration is untouched by removing the guard
  on the kaya iteration. Full `ctx` shows the mutant actually emits a phantom
  `## Your Expertise — kaya repository (repository tier)` header with an empty body — this is
  why assertion 3 exists and is not redundant with assertion 2. Confirms the eng squad's own
  "18/19, exactly two assertions flip" claim independently rather than repeating it.
- 2026-08-19: The `stderr == ""` strength in case13 (vs. `"Traceback" not in stderr`, the weaker
  form used in case11 and shown vacuous in the census) is load-bearing, not stylistic: the
  guard-removed mutant's stderr is pure bash runtime noise (`head: ... No such file or
  directory`, `[: : integer expected`) — it never contains the literal substring "Traceback"
  (specific to uncaught Python exceptions, which this mutant does not produce). A
  `"Traceback" not in stderr` assertion in case13's place would have stayed green under the
  exact mutant it exists to catch.
- 2026-08-19: `bash-write-guard.sh` blocks Bash-tool file redirects (`>` / `cp`) into the
  scratchpad too, not just repo paths — every write for a mutation probe, including throwaway
  scratch copies, has to go through the `Write` tool. Second time this has cost a false start
  this feature; worth a durable pattern if it recurs on a third.
- 2026-08-19 (cycle 2, correction): the above `cp`-into-scratchpad-blocked claim did NOT
  reproduce this session — `cp` from Bash into the scratchpad path succeeded without a guard
  prompt or denial (used it for every mutant this round: orig.sh, n1/n2/n3/n4a/n4b, item4
  variants). Recording per rule 15 rather than silently dropping the earlier entry: either the
  guard's scratchpad behavior is path- or session-dependent, or the earlier block was specific to
  something else in that session (e.g. writing over an existing file vs. creating a new one) that
  I did not isolate at the time. Did not re-derive which — used `Write` anyway per this cycle's
  explicit instruction, so it did not block progress, but the original claim as stated ("blocks
  ... into the scratchpad too") is broader than what I could reproduce.
- 2026-08-19 (cycle 2): sent-back finding — a "could-not-fail census" swept by reading each
  case's assertion text is not sufficient; two items (N-1, N-2 in `qa-FEAT-27-matrix-final.md`)
  required tracing a data source backward through the script (an unwritten fixture variable; a
  fixture whose values happen to already sort correctly) rather than reading the assertion in
  isolation. Also corrected an overstated claim of my own from cycle 1 — "`stderr == ""` is
  load-bearing, not stylistic" for case13's T-07 mutant was not supported by my own measurement
  (`checks[3]` alone already reddens that case); the real value of `stderr == ""` is against a
  *different*, unexercised failure class. Lesson: state redundancy claims against the specific
  measured `checks` array, not against the mutant's overall pass/fail.
- 2026-08-19 (GATE-ONLY re-run at 9b929de): identity check — `git diff --stat 252fa72..9b929de`
  touches only SPEC.md, feature.json bookkeeping, and notes/observations; zero source or test
  files changed since the prior full gate. Confirmed `HEAD == 9b929de` and no uncommitted diffs
  on any graded file (working-tree `M` entries for CLAUDE.md/DECISIONS*.md belong to other
  untracked work per dispatch boundary, correctly out of scope). Re-ran both kinds fresh anyway
  per dispatch: unit exit 0 / 0 `^FAIL `, 17 registered scripts, 741+ counted case-assertions;
  integration exit 0 / 0 `^FAIL `, 12 registered scripts, 201+ counted case-assertions — both
  non-zero discovery, matching prior gate's numbers exactly (expected, since the source is
  byte-identical). Re-confirmed the standing adequacy gap independently: T-01 is `change_type:
  config` (matrix `always: []`), so the matrix itself never obligates a kind for the 16
  repository-tier grants — SC-02's only regression pin is T-01's inline one-shot `verify:` block
  (ran it directly, `ALL-GRANTS-OK`, exit 0), which is not in `run-unit-tests.sh`'s
  UNIT_SCRIPTS/INTEGRATION_SCRIPTS arrays and `test-check-domain.py` has exactly one
  case-insensitive hit on "repository" — a comment about "a product repository", zero actual
  repository-tier test cases. This is a matrix-compliant gap, not a matrix violation, and it is
  unchanged by the 252fa72..9b929de delta (T-01 was untouched in that range).
