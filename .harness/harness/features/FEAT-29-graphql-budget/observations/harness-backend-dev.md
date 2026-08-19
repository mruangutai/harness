# Observations — harness-backend-dev — FEAT-29-graphql-budget

- 2026-08-19 (T-01): a two-condition fixture (a shared totalCount plus a mixed stationed/null-station
  node list) can make an intentionally-isolated mutation (drop null-station items) trip an
  UNRELATED guard (the truncation raise) as a side effect, smearing the redness across every check
  that shares the fixture. Fix was to give the property under test (presence-not-dropped) its own
  fixture with a `totalCount` chosen so neither the correct output nor the mutated output crosses
  the truncation threshold — not a general pattern yet, but worth checking for on any function that
  layers a count-based guard over a per-node mapping loop.
- 2026-08-19 (T-01): repeated the G-13 mistake live — used `git checkout -- <path>` to restore
  after a mutation cycle, which reset to HEAD (pre-feature baseline) rather than the prior cycle's
  fix, wiping the whole implementation. Caught by `git diff --stat` and a grep for the function
  name immediately after, recovered from a saved `git apply` patch, hash-verified. The gotcha
  already says not to do this; doing it once "by reflex" mid-task before catching it is the real
  lesson — the muscle memory of `git checkout --` as "undo my last edit" is strong enough to
  override having just read the rule.
- 2026-08-19 (T-02): a defensive `x = d.get("k") or {}` guard against a caller passing None can be a
  literal no-op if the upstream contract already normalizes that None to `{}` before the caller ever
  sees it — mutating the `or {}` away here did NOT redden the null-content test, because
  `factory_gh.project_item_stations` already turns a null `content` node into `content_out = {}`
  before returning. The mutation that actually exercised the guard was downstream: switching
  `content.get("repository")` to `content["repository"]` (bracket access), which raises `KeyError`
  against the already-normalized `{}`. Lesson: when a mutation produces zero red checks, that is not
  "the code is dead" — check whether the upstream contract already forecloses the input shape the
  mutation targets, and mutate the actual access pattern instead.
- 2026-08-19 (T-02): fixture isolation for a null/empty-content case came for free here — the
  content-null fixture's node fails the repository-equality check before the station lookup ever
  runs, so a mutation to the station-drop logic (mutation 1) never touched it, and a mutation to the
  content-access logic (mutation 2) never touched the other three checks (their content dicts are
  real, non-empty, so `.get` vs `[...]` behaves identically for them). No T-01-style shared-fixture
  spread this time; still split into two `with tempfile.TemporaryDirectory()` blocks up front rather
  than relying on that being true, per the T-01 lesson above.
- 2026-08-19 (T-04): a mutation that removes a MODULE-WIDE detection guard inside a shared function
  (`run_gh`) is not scopeable to the two new tests written to prove it — every pre-existing test in
  the file that queues exactly one `Result` for a non-zero-exit case now collides with the mutated
  code's attempt at a second subprocess call, and the recorder's `AssertionError` crashes the whole
  suite via an EARLIER, unrelated test before the two new checks are even reached. This is not the
  P-04/fixture-isolation failure mode (no shared state leaking between tests) — it is inherent
  blast radius from mutating a function every other test in the file also calls through. Ran a
  scoped standalone probe (own `Result`/`recorder`, imports `factory_gh` directly) containing only
  the two target checks to get a clean per-mutation redness signal instead of the full-suite crash;
  recorded both outcomes in the receipt. Worth carrying forward: for any mutation to a shared
  helper called by dozens of existing single-Result tests, plan for a scoped probe from the start
  rather than discovering the full-suite crash first.
- 2026-08-19 (T-04, cycle 2): made the in-repo discriminator check itself observably red under
  mutation 1 (`test-factory-gh.py`'s "run_gh: message carries the captured stderr", line ~217),
  by queueing a second `Result` on that fixture's `recorder` — the mutant's extra `gh api
  rate_limit` call consumes it; unmutated code never makes that call so the spare item is simply
  never consumed (`recorder` only raises when it runs out). Fixing that one fixture uncovered two
  MORE single-Result recorders in the same file (`preflight`'s auth-login test, and
  `ensure_labels`'s stop-at-failing-label test) that crash the same way under the same mutation —
  fixed those too, since without them the suite crashes before reaching any further checks and
  "every other check that also reddened" can't be observed at all. Stopped after a THIRD crash
  further down (`ensure_labels: passes repo verbatim`, a bare `ValueError` from
  `.index("--repo")` on the leaked rate_limit-query call, not a clean check redness) rather than
  chasing every one of the file's ~30 `run_gh`-backed fixtures — the dispatch itself already
  conceded the blast radius is inherent and unsatisfiable to fully contain, and patching the whole
  file crosses from "queue a second Result for the named recorder" into rewriting fixture
  robustness project-wide, out of a narrow-scope cycle. Lesson: when a mutation to a shared helper
  is proven capable of reddening the ONE named discriminator, that is sufficient — do not treat an
  unrelated downstream crash as evidence the fix is incomplete; name it and stop.
- 2026-08-19 (T-04, cycle 3): mutating the MARKER LIST instead of the guard (append a text marker
  matching the discriminator fixture's own stderr) is what finally reddened the actual named
  discriminator ("run_gh: unrelated failure never contains the GraphQL budget headline") in-repo,
  with a blast radius of exactly two checks in the whole 198-check file — the discriminator itself
  plus its sibling text-preservation check. Cycles 1-2 mutated the guard
  (`_looks_like_rate_limit`/`_is_rate_limit_query`), which routes EVERY non-zero exit in the module
  through the budget path and detonates ~30 unrelated single-Result fixtures before the target
  check is even reached — a structurally different, much larger blast radius from a structurally
  similar-looking mutation. Lesson: "mutate the detection guard" and "mutate the detection data"
  are not interchangeable ways to test the same discriminator — the guard is shared by every
  caller, the marker list only misroutes calls whose text happens to match, so scoping the mutation
  to the data is what keeps the blast radius to the one fixture the check is actually about.
- 2026-08-19 (T-04, cycle 3): the spare `Result` needed for the misrouted discriminator call is
  itself a subtler choice than "add any second Result" — it must be a SUCCESS (exit 0, the real
  `_RATE_LIMIT_JSON` fixture), not another failure. A second Result that also fails routes
  `_rate_limit_budget_error` down its OWN except branch (`GhError` catching `GhError`), producing
  the "...budget could not be read" message, which does NOT contain "GraphQL budget exhausted" —
  so the target check (which asserts that exact headline is absent) stays green even though the
  call was misrouted, and only the "preserves original text" sibling check reddens. Confirmed live:
  ran the mutation once with a failing spare (target check stayed green, only a different, unnamed
  check reddened) before switching the spare to success and re-running, which is what finally
  reddened the named discriminator itself.
- 2026-08-19 (T-03): wrote full gh_cost_log.py before writing test-gh-cost-log.py — caught it
  myself before running anything, deleted the production file, and restarted test-first. The
  Iron Law violation happened even with the rule fully in context at spawn time; the trigger was
  reading a long, detailed intent block and mentally "designing the module" while reading it,
  which slid straight into writing it. Worth watching for on any task whose intent paragraph
  reads like a spec — the more complete the spec in the dispatch, the stronger the pull to
  transcribe it directly into the implementation file first.
- 2026-08-19 (T-03): my own test's first mutation attempt (an early return in record() on
  non-zero rc) produced a bare FileNotFoundError traceback that killed the whole suite before
  reaching the two later checks that depended on the same read_lines() call, not a clean FAIL —
  the P-04 pattern, but self-inflicted this time rather than found in someone else's fixture.
  read_lines() had no try/except and every block indexed lines[0]/lines[N] unguarded. Fixed by
  making read_lines() itself never raise (returns [] on OSError/JSONDecodeError) and switching
  every subsequent index into a guarded `non_cov[0] if non_cov else {}` plus `.get()` reads, then
  re-ran the same mutation and got a clean named FAIL with a trailing "N of M FAILING." line.
  Lesson for next time: build the crash-proofing into read helpers in test files from the start,
  not after the first mutation already proves the suite is fragile to it.
- 2026-08-19 (T-03): confirmed live that HARNESS_GH_COST_LOG defaulting ON, wired into
  factory_gh.run_gh, causes PRE-EXISTING unit tests outside my file list (test-board-station.py,
  test-gh-board.py — both reach run_gh for real, one via a forked subprocess, one in-process)
  to write a real .harness/logs/gh-cost-<date>.jsonl into the ACTUAL checkout, not a tmp root —
  because factory_config.harness_root() silently falls back to the real checkout root whenever
  CLAUDE_PROJECT_DIR is unset (it is, in this shell), and neither of those two test files sets
  it to a tmp path. Reproduced twice (unit and integration runs each recreate/append to the
  file). I could not clean it up myself — bash-write-guard correctly blocked my own `rm` on that
  path as outside my domain, which is itself confirmation this is a real domain boundary, not a
  false alarm. Raised as a blocking open_question rather than silently patched (no file in scope
  can fix it without either changing factory_config.py's fallback or the two test files, both
  out of my file list).
- 2026-08-19 (T-03, second pass, amendment 5 — REQ-03/SC-05 flip to opt-in default OFF):
  the c1 open_question (Q1) resolved itself as a side effect of the operator's amendment rather
  than my own file-list options — flipping the default to OFF means the pre-existing unit and
  integration suites no longer write into the real `.harness/logs/` at all when
  `HARNESS_GH_COST_LOG` is unset, which is the normal case for every suite invocation. Verified
  live: `.harness/logs/gh-cost-2026-08-19.jsonl` stayed byte-identical (39504 bytes) across a
  full `--kind unit` and a full `--kind integration` run, both before and after. Worth noting for
  future amendments: a scope change can retroactively answer an open_question raised under the
  prior scope without anyone touching the file the question was about.
- 2026-08-19 (T-03, second pass): the mutation probe (`_enabled()` -> `return True`, ignoring the
  env var entirely) reddened FIVE checks, not four — the new SC-05 pair (2 cases x 2 assertions)
  plus the pre-existing `HARNESS_GH_COST_LOG=0 writes no line` case, because that case's own
  correctness now depends on `_enabled()` actually reading the var rather than being a `!= "0"`
  check with a note in the docstring. A mutation that reddens an existing check outside the new
  ones you added is not automatically a scope violation — check whether the existing check was
  always coupled to the same function before treating the extra redness as unexpected.
- 2026-08-19 (T-03, fix cycle 3): the required proof shape for a coverage-hole fix (not a code
  defect) is mutation testing on the EXISTING correct production code, not a RED/GREEN cycle on
  new production code — TDD's Iron Law governs production-code order, and there was none to add
  here. Three named-check mutations (delete each `with` block, remove `not _enabled() or`)
  reddened exactly the checks predicted, none aborted; that is the applicable evidence when the
  fix is entirely test-side.
- 2026-08-19 (T-03, fix cycle 3): closing a "the interface is never driven, only the sink
  underneath it is called directly" vacuous-pass gap needs a call-COUNT assertion, not just a
  write assertion — the write-suppressing guard (record()'s own check) and the interface-level
  guard (measured()'s own check) are separate code paths that can each mask the other's removal.
  Proved live: deleting `not _enabled() or` from measured()'s guard left the OFF write absent
  (record()'s guard still fires) but tripled the subprocess call count; only the count assertion
  caught it.
- 2026-08-19 (T-03, fix cycle 3): twice during this cycle, a stale "file changed on disk since
  last read" tool signal showed a production file back in an already-reverted mutated state,
  immediately contradicted by a fresh `sha256sum`/`git diff` check showing the correct state. Not
  a real regression either time — re-verify with an independent command before treating that
  signal as ground truth, especially right after a rapid mutate/revert/verify sequence on the
  same file.
