# Observations — harness-backend-dev — FEAT-10-software-factory

- 2026-08-09 (T-02): the three-tier root resolution is now copied THREE places
  (`check-plan-routes.py::_resolve_root`, `run-unit-tests.sh`'s header/body, and
  `factory_config.py::harness_root`). All three probe `docs/harness/SPEC.md` for the same
  deploy.sh-copies-bin-not-docs reason. If a fourth factory tool ever needs its own root
  resolution, it should import `factory_config.harness_root()` rather than growing a fourth
  copy — the plan's own T-02 intent already flags two-copies-of-a-rule as how tools end up
  looking in different directories; a third/fourth hand-rolled copy is the same defect.
- 2026-08-09 (T-02): `python3 <script>.py` run directly (as run-unit-tests.sh does) puts the
  script's own directory on `sys.path[0]` automatically, so `factory_*.py` bin scripts can
  `import factory_cli`/`import harness_yaml` with no `sys.path.insert` boilerplate — confirmed
  this matches the existing `factory_gh.py`/`test-factory-cli.py` style rather than the
  try/except `ModuleNotFoundError` fallback some older test files (`test-team-catalog.py`) use
  for the PyYAML-missing message. Don't copy the older pattern into new factory_* files unless
  the PyYAML-missing diagnostic is actually wanted.
- 2026-08-09 (T-02): `board.number` validation needs `isinstance(x, bool)` excluded explicitly —
  Python's `bool` is a subclass of `int`, so `isinstance(True, int)` is `True` and a bare
  `isinstance(number, int)` check would silently accept `board.number: true` from YAML.
- 2026-08-09 (T-06): `git branch [-r] --list <ref>` always exits 0 and answers with empty vs.
  non-empty stdout, so it is the right primitive for a "does this ref exist" probe fed through
  `run_git`'s raise-on-nonzero contract — `git rev-parse --verify` or `git show-ref --verify`
  would instead make "ref absent" a raised exception, forcing the caller to treat a normal
  branching decision as error-handling. Worth reusing in factory_land.py (T-07) if it needs a
  similar existence check.
- 2026-08-09 (T-06): I initially wrote factory_workspace.py before test-factory-workspace.py —
  caught it before running anything against real inputs, deleted the implementation, wrote the
  test, watched it fail on ModuleNotFoundError (RED), then rewrote the same implementation
  GREEN. No functional harm since nothing was executed test-last, but it's worth flagging: the
  task's own framing ("write the unit test before the implementation") is easy to read as
  advisory when the design is already clear in your head — it isn't, the Iron Law's ordering is
  about the paper trail, not just the code's correctness.
- 2026-08-09 (T-06): that same "design already clear in my head" run also shipped a fail-open
  bug the first green suite couldn't see: step 4's local-branch short-circuit (`if branch exists
  locally: checkout as-is`) skipped the intent's own qualifier ("...AND tracks the remote ref"),
  so a local branch cut from `origin/<default_branch>` by an earlier claimless run would be
  trusted as-is even when origin now carries the real claimed ref — silent divergence, surfacing
  only as a rejected push in T-07. My own test case (F) had encoded the permissive behaviour as
  correct rather than testing for the gap, because I wrote both the code and its test from the
  same mental model at the same time. Caught on advisor review, not by the suite. Lesson: when a
  task's intent contains a qualifier clause ("X, AND Y"), write the test for the case where X
  holds and Y does not BEFORE writing the implementation of the combined condition — testing
  only the happy path of a conjunction is how the conjunction's second half quietly goes
  unenforced.
- 2026-08-09 (T-04): repeated the exact same T-06 mistake — drafted factory_decompose.py before
  test-factory-decompose.py existed, purely from design work in this session (no tool calls used
  the module). Caught it before running anything, deleted the file, wrote the test, watched it
  fail on ModuleNotFoundError (RED), then rewrote from the same design GREEN. Second time in one
  feature: a large, fully-specified intent block makes the design feel "already settled" and the
  Iron Law's ordering starts to feel like paperwork rather than a discipline. It is not — worth
  a standing habit: write the test file's skeleton (imports + one fixture helper) as the very
  first file-write of any task, before any thinking-out-loud draft of the module under test.
- 2026-08-09 (T-04): `factory_gh.project_item_add(owner, number, url)` takes the item's GitHub
  URL, not the issue number — a substring check like `str(n) in url` is a real trap once issue
  numbers can be prefixes of each other (`/issues/1` is a substring of `/issues/17`). Assert on
  the parsed trailing integer of the URL instead. This is exactly the shape the "parent never on
  the board" case needs to be honest.
- 2026-08-09 (T-04): the four-disposition sort (full / partial / new / edges-unwritten) is keyed
  on three independent maps — issues, items, edges — never on issues alone, and the edges
  check itself must recompute per-task from `edges.parent` membership plus the *unsatisfied*
  subset of `depends_on` against `edges.blocked_by`, not from any single boolean already stored
  anywhere. Worth reusing this exact shape (`_owes_edges`) if a later factory tool ever needs to
  resume a partially-drawn DAG.
- 2026-08-09 (T-04): `factory_gh.preflight()` runs unconditionally at step 3, before any
  disposition is sorted — so a "second publish makes zero calls" test case cannot assert an
  empty call list; scope it to the mutating/board/edge/id surface and say so in the assertion's
  own label, or a reviewer re-reading the test will (correctly) wonder why preflight is missing
  from an "everything" claim.
- 2026-08-09 (T-04): a review-pass smoke-test corrupted a live, untracked production file. I ran
  a python heredoc to flip one `open()` call to `"w"` mode (to confirm case (22)'s truncation
  detector actually fires red) using `str.replace(old, new)` — plain `str.replace` replaces
  EVERY occurrence, not the first, and `factory_decompose.py` had two call sites sharing the
  same snippet text (`extract_brief`'s BRIEF.md read and `write_factory`'s feature.yaml read), so
  both flipped. My immediate follow-up `git checkout -- <path>` did nothing and printed no error,
  because the file is new and untracked — there is no committed blob to restore from, and
  `git checkout` on an untracked path is a silent no-op, not a failure. Caught only because the
  harness surfaces a tool-result diff back to me; without that channel the corruption would have
  shipped. Two lessons: (1) never use `str.replace` for a targeted single-site edit when the
  file might contain the same snippet twice — use `.replace(old, new, 1)` or, better, don't hand-
  edit via python heredoc when the Edit tool's uniqueness check exists for exactly this; (2) for
  an UNTRACKED file, `git checkout --` is not a safety net — the only backstop is having read the
  file's current content immediately beforehand (which I had) so a manual restore is possible.
  The mutation-test step itself (temporarily break code to confirm a test goes red) also turned
  out to buy nothing here: the anti-vacuum assertion added in the same pass already proved the
  patched `open` was being intercepted, which was the only fact the mutation would have added.
  Skip the "break it to prove the test fires" step when a cheaper structural proof already covers
  the same claim.
- 2026-08-09 (T-05): wrote test-factory-claim.py in full BEFORE any line of factory_claim.py —
  ran it once to confirm ModuleNotFoundError (RED), then wrote the implementation once and it
  passed all 68 checks on the first run. Breaking from the T-04/T-06 pattern (draft first,
  delete, restart) mattered here specifically because the intent block already fully specifies
  every branch and skip-reason string, so writing the recorder + fixtures first forced me to
  pin the exact stderr strings and call-order assertions before any code existed to bias them.
- 2026-08-09 (T-05): the blocker gate's cost model is "cache the YAML files (plan.yaml,
  feature.yaml), never the issue_view results" — DESIGN.md C-2 amendment states this explicitly
  ("the plan's cache holds the YAML files, not issue_view results, so T-12's six blockers cost
  six reads"). A cache keyed on blocker issue number instead would silently violate this: it
  reads correctly on a first poll but hides the intended "recheck every blocker on every poll"
  behavior a later poll needs to see a blocker close.
- 2026-08-09 (T-05): MIXED BLOCKER SET (three depends_on entries in different open/closed
  states) requires scanning ALL entries every time and keeping the LAST one found still open —
  not the first. A `return as soon as you find one open` implementation passes every other case
  in the suite (all-open or all-closed per candidate) and only fails this one, which is exactly
  why the plan calls it out as the case that "falsifies a partially correct tool."
- 2026-08-09 (T-05): FEATURES_ROOT must be read as a bare module global inside the function body
  (`os.path.join(FEATURES_ROOT, ...)`), never bound as a function default-argument value — a
  default is evaluated once at def-time, at import, and a test's post-import monkeypatch of the
  module attribute would then silently not take effect for any call.
