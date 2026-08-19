# Observations — harness-validator-lead — FEAT-27

- 2026-08-19: qa segment, T-02/T-03 matrix gate at 2117a46. I relayed a ruling to qa saying the
  stale `integration.detect` glob "never enters T-03's obligation". That overstates it —
  `harness-qa-gate/SKILL.md:57` explicitly directs the gate to use `detect` globs to confirm a
  covering test exists, so the stale glob DOES feed the step-4 presence check. The ruling still
  holds, but the correct footing is `:96` ("a runner that silently matched nothing has told you the
  glob is wrong") keyed on the RUNNER's discovery, plus `:73` defining `satisfied` as "at least one
  named test ran, none failed" — named tests, not globs. `run-unit-tests.sh --kind integration`
  discovers and runs `test-check-expertise.py`, so neither the FAIL at `:74` nor the BLOCKED at
  `:76`/`:96` fires. Lesson: when a dispatch hands me a ruling to relay, re-derive its mechanism
  before passing it down, because the member inherits my error and cannot see past it.

- 2026-08-19: I passed qa a leading hypothesis that `agent_type: "harness-*"` would, with the
  `^harness-[a-z0-9-]+$` regex removed, glob-match a real repository-tier file and therefore bind
  the validation against regression. It is FALSE and I measured it at source:
  `inject-expertise.sh:68` is `for f in "$root"/.harness/*/expertise/"$agent.md"`, where
  `"$agent.md"` is a QUOTED expansion — bash pathname expansion does not treat characters from a
  quoted portion as glob-active, so the value's `*` stays literal and looks for a file named
  `harness-*.md`. Case 12's temp root writes `harness-qa.md` (`test-inject-expertise.py:292`), not
  that. qa independently reached the same conclusion by mutation. Cost of the error: I handed a
  member a leading question on the one item I had asked it to assess independently, so its answer
  on that sub-item is worth less as evidence than it should be. Two derivations rescued it here;
  that was luck, not design.

- 2026-08-19: The eng squad's RED proofs (both dev-ops receipts) are against pre-change baseline
  `b4659cd`. That proves the new cases discriminate the feature's ARRIVAL. It does not prove they
  pin the behavior against REGRESSION, which needs mutation of the post-change script. These are
  different claims and only the second survives an edit. Worth carrying: a receipt that says
  "proven RED first" is answering the arrival question, and a lead reading it as regression
  assurance is reading in a guarantee that was never measured. On this feature both now exist —
  eng supplied arrival, qa supplied regression — and it took two squads to get there.

- 2026-08-19: Both of qa's coverage gaps have the same shape and it is worth naming as a class:
  the shipped code is CORRECT and nothing holds it there. The `[ -r ]` guard in
  `inject-expertise.sh`'s glob loop correctly skips an unreadable repository-tier file, but no
  fixture builds that file, so a mutant removing the guard survives 18/18. Intent 1c's
  `^harness-[a-z0-9-]+$` suffix rule correctly rejects hostile agent names, but every value case 12
  tries is vacuous, so a mutant removing the regex also survives. "Verified correct at source" and
  "pinned against regression" are two findings, and only the second survives a future edit.

- 2026-08-19: T-03's `verify:` asserts `^ADVISORY ` against the LIVE `.harness/expertise/` corpus
  rather than a fixture. It is green today only because the sixteen token-carrying entries are
  still in the craft tier, and it survives T-04 only because five of those sixteen were adjudicated
  to REMAIN craft (plan D-03). A verify clause whose truth depends on corpus state that no fixture
  pins is a latent flake, and the coupling is invisible from inside either task.

- 2026-08-19: Three different numbers describe the same live corpus and none is interchangeable:
  29 ADVISORY LINES (qa, from the checker's own output at 2117a46), 19 token LINE-OCCURRENCES
  across 7 files (eng lead's pre-dispatch grep), 16 flagged ENTRIES (BRIEF). Lines, line-occurrences
  and entries are three units. Carrying any one forward as "the count" would have been a false
  claim built from true measurements.

- 2026-08-19: Process defect on my side — I attempted to send a mid-run course correction to a
  running member and had no channel for it (leads hold Read/Glob/Grep/Agent/Write; no message tool).
  I burned a spawn on a placeholder discovering this. A correction that occurs to me after dispatch
  either waits for the return or costs a send-back; there is no cheap third option, so the dispatch
  prompt has to be right at write time.

- 2026-08-19: Polling the filesystem for a member's artifact is NOT a wait — tool calls return
  instantly and buy no wall-clock time, so ~50 polls advanced the run by nothing. The only real
  yield point is the end of a turn. Waiting on an in-flight member is not something a lead can do
  by looping.
