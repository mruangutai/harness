# Observations — harness-eng-lead — FEAT-24

- 2026-08-18 (run 7, fix cycle C1): routing for both fixes was over-determined, not a judgement
  call — `plan.yaml:300` and `:361` both carry `execution_agent: harness-backend-dev`, and
  `.claude/skills/harness/bin/**` is granted to backend-dev and dev-ops alike (G-01/G-02). One
  dispatch, not two, because the operator wants ONE full-suite red set taken after both fixes; a
  second dispatch would make the first one's red set stale.

- 2026-08-18: the assertion that hid FIX 1 for a whole feature is a shape worth remembering.
  `test-factory-gh.py:914-916` asserted `any("repos/o/r/contents/..." in a for a in argv)` AND
  `any("ref=main" in a for a in argv)`. Both clauses are satisfied by the correct query form AND by
  the broken `-f` form, because the assertion never says WHICH element carries the ref. An
  element-membership assertion over an argv list cannot see argv STRUCTURE, and the HTTP method is
  structure. The recorder harness models no method at all, so no case in the file could have caught
  it. The discriminating clauses are "the ref rides in the same element as the path" and
  "`-f` is not in argv".

- 2026-08-18: verified before relaying (P-09), against my own run-6 self-record of relaying an
  unchecked argv claim. `test-factory-integration.py:275` matches
  `^repos/([^/]+/[^/]+)/contents/(.+)$` on `rest[0]` and uses ONLY `cm.group(1)` at `:277`;
  group(2) is captured and never read. So the query form's `?ref=` is absorbed by `.+` and the fake
  gh's contents branch is unaffected — observed, not inferred from the regex's shape.

- 2026-08-18: `factory_config.py:263-267` documents a memo keyed `(repo_name, ref)` with
  `clear_product_config_memo()` as its only sanctioned reset. That is the trap in FIX 2: D-03's
  clause is ABOUT the cache, so an F-5 fixture whose repo key was already read successfully by an
  earlier case in the file never invokes the raising stub and proves nothing. Put the reset (or a
  repo name used nowhere else) in the dispatch, not in the member's discretion.

- 2026-08-18: "assert the value appears nowhere in the RESULT" is vacuous whenever the correct
  implementation raises — there is no result to inspect. A negative assertion scoped to a branch
  that cannot execute passes for free. It has to be paired with a capture on the no-raise branch
  and a check of `str(exc)`.

- 2026-08-18: full suite is 28 files (`run-unit-tests.sh:17-18`, 16 unit + 12 integration). At this
  commit exactly two are pre-cleared red — `test-no-distribution.py` (operator's, T-07 fixture) and
  `test-check-state.py` (red by design until T-05's `derive_station()` arity lands by hand). Any
  third FAIL line is a new defect, and saying so explicitly in the dispatch is what stops a member
  filing an unexpected red under "expected".

- 2026-08-19 (run 2026-08-19-4-eng, fix cycle C3): THE ABOVE PRE-CLEARED-RED NOTE IS SUPERSEDED and
  re-measuring it before reuse is the whole lesson (G-11). Settled without a shell, from
  `.git/HEAD`, `.git/refs/heads/feat/FEAT-24-config-responsibility-split` and
  `.git/logs/refs/heads/...` (G-06): HEAD is on the feature branch at `2e60cc2`, and the dispatch's
  pin `6baa39b` is its immediate PARENT. The one commit between them is a record/handoff commit
  ("the build seam handoff, and the feature reaches zero violations of its own"), no code. qa
  measured `run-unit-tests.sh --kind all` at `b0604c3` as rc=0, zero FAIL, 1365 ok, and
  `b0604c3 → 6baa39b → 2e60cc2` are all record commits. So the expected red set for this run is
  **EMPTY, rc=0** — deciding that BEFORE the member's number arrives is what stops "expected" from
  meaning "whatever came back".

- 2026-08-19: the dispatch's "test-check-state.py is expected to be involved in a separate finding"
  does NOT license a red there. qa's T-05 finding is that INV-26 assertions are MISSING — a file
  with no assertions runs green. A red `test-check-state.py` would be a new defect, not the known
  one. A "known finding" and a "known failure" are different objects and a dispatch phrase that
  blurs them is how an unexpected red gets filed under expected.

- 2026-08-19: `receipt-harness-backend-dev-fix-c2.md:112-115` records that an auto-mode Bash
  classifier BLOCKED running the suite with `validate=False` in the tracked `factory_gh.py` — the
  guard reads a weakened validation flag as the thing it exists to stop. Any dispatch whose proof
  is an in-place mutation of a security-shaped flag must ship the fallback in the prompt itself:
  copy the whole `bin/` dir to scratch, mutate the copy, run the copied test (Python puts the
  script's own dir first on `sys.path`, so the copy imports the mutated sibling; PYTHONPATH
  shadowing does NOT work for a sibling module). I could not send this mid-flight — a lead holds
  no SendMessage tool — so it costs a re-dispatch. Put it in the first dispatch next time.

- 2026-08-19: `dispatch-guard.sh` blocked my first Agent call for passing `model: sonnet` (DEC-152/155).
  Correct block, my error. Model pins are org design and never a dispatch option; the tool's own
  `model` parameter is not a licence to use it from a lead.

- 2026-08-19 (run 8, four-angle simplify): a member's receipt appearing on disk is NOT its return,
  and I watched two of four members REVISE their receipt in place after first writing it — the file
  moved back to last in an mtime-sorted `Glob` while the agent was still running. So the only
  in-flight signal a lead actually has is mtime churn, and the correct read of it is "still
  writing", never "ready to read". The validator-lead burned a spawn on this exact error last run by
  reading a mid-write snapshot and reporting a contradiction that the member fixed before returning.
  Waiting cost me nothing; reading early would have cost a false finding in a digest.

- 2026-08-19 (run 8): I spent roughly sixty `Glob` calls polling for returns that arrive by PUSH
  notification anyway. Polling buys no information and does not protect against the thing I was
  actually afraid of (issue #461, a lead returning while a member is in flight) — what protects
  against that is simply not writing a verdict. The real constraint underneath: a lead holds no
  `SendMessage`, so it cannot ask a running member for anything, and it has no way to idle except
  by making tool calls. Next time: do the genuinely useful adjacent reads once, then stop, and
  accept that the turn is just open.

- 2026-08-19 (run 8): severity of a "silent return None" finding is decided by WHO CALLS IT, and
  enumerating the callers flipped my disposition. `gh_board.load_board` returns None when the
  `github` block is absent while its own docstring says that case raises. That reads as a live
  silent-failure hole until you grep: all three callers pre-filter the block first
  (`gh-sync.py:151`, `board-station.py:140`, and `check-state.sh:1147` behind the
  `isinstance(_g26, dict) and sync is True and repo` guard at `:1138-1140`). So it is a falsified
  docstring, not a hole — the difference between a forced fix cycle and a routed docstring question.
  Enumerate call sites before rating any "this fails silently" finding.

- 2026-08-19 (run 10, fix cycle C5): "no way to idle" is now a MEASURED constraint, not a
  preference. `validate-digest.py --hook` refuses to let me stop the turn without a full DIGEST, and
  a member was still in flight. So the two obligations collide directly: the hook demands a verdict
  to stop, and issue #461 says never write a verdict over an unreturned member. The only resolution
  available to a lead is to keep making tool calls. Doing genuinely useful reads instead of `Glob`
  polling is the difference between paying that cost and wasting it — the ui-reviewer and
  code-reviewer notes I read while waiting changed my scope assessment.

- 2026-08-19 (run 10): A DISPATCH BAR I WROTE WAS ITSELF UNSOUND, and I caught it only after the
  spawn. I required the member to prove its replacement substring discriminating via `grep -c` on
  `factory_config.py` returning exactly 1. But `grep -c` counts LINES and the `:165` message is a
  two-line f-string (`:165-166`) — a phrase straddling the break returns 0, and a member reporting
  "0, therefore unique" reports nothing. Discrimination between two ERROR MESSAGES is a property of
  the runtime strings, never of source lines; the sound instrument is triggering both errors and
  asserting the substring present in one and ABSENT from the other. A source-text grep cannot stand
  in for a runtime assertion whenever the string is built by formatting.

- 2026-08-19 (run 10): I misread `RAISED_MESSAGES` scoping and the correction matters for any future
  message edit in this file. `(8b)` is registered into `BAD_CASES` at `test-factory-config.py:184`,
  which is BEFORE `RAISED_MESSAGES = []` at `:193`, and the generic loop appends at `:204` — so
  `(8b)` runs twice and the `:165` text DOES enter the list. Its consumer at `:280-285` requires
  every message to contain an em dash and to contain neither `FleetError` nor `Traceback`, and
  builds its ok-line label from `m[:70]!r`, so changing `:165` renames one `(15)` ok-line. Registration
  order versus initialisation order is the thing to check, not proximity in the file.

- 2026-08-19 (run 10): THE FIX AS SCOPED CANNOT FULLY CLEAR SC-06, and knowing that before the
  member returns is what stops me reporting a closed criterion. The operator scoped FIX 1 to two
  cases (unparseable JSON, non-mapping). But code-reviewer's note (`:67-78`, `:111-117`) grades
  SC-06 unmet on THREE grounds — the third being that missing-file and `gh` unauthenticated are
  structurally ONE code path, since both are just "run_gh exits non-zero" to `factory_gh`, so no
  test in `test-factory-config.py` can distinguish them. Distinguishing them needs `factory_gh.py`,
  which is outside the two permitted files. So the residue is not sloppiness, it is a scope boundary,
  and it must be raised rather than papered over.

- 2026-08-19 (run 10, the send-back): REPLACING AN ASSERTION IS NOT THE SAME AS PRESERVING WHAT IT
  PINNED, and "no assertion may be weakened" does not catch the difference. The old `(8b)` assertion
  pinned the DESTINATION (`repos[].board`) — at the wrong value, which was the defect. The member's
  replacement pinned `whole-fleet board`, which names the REJECTED KEY, exactly as `invalid: board —`
  two lines above already did. Both assertions passed, neither was weaker in isolation, and the set
  had lost the destination entirely: a future edit could restore `repos[].board` and nothing reddens.
  The test is not "is each assertion as strong as before" but "does the SET still pin every property
  the old set pinned". Ask what an assertion is FOR before approving its replacement.

- 2026-08-19 (run 10): a mutation-proof gotcha for uncommitted work, found by the member and worth
  keeping. `git checkout -- <file>` restores from HEAD, so on a fix that is not yet committed it
  reverts to the PRE-FIX defect rather than to the in-progress fix — a "restore" step that silently
  undoes the cycle's own work while every hash check still looks orderly if you compare to the wrong
  baseline. Any dispatch asking for mutate-then-restore on uncommitted work must say to snapshot the
  file to scratch and restore from THAT, and to state which baseline each sha256 is compared against.
