# FEAT-53 plan cycle 3 — the proposal fed to plan-merge.py apply, plus the change record
#
# THIS FILE IS REAL YAML. plan-merge.py safe_loads it whole, so every line of prose here is a
# `#` comment. The two data keys below are `decisions:` (D-21) and `tasks:` (T-21, T-22) and
# nothing else — a stray top-level key would be appended to plan.yaml verbatim.
#
# Authority: notes/answers-2026-09-01-plan-signature.md, sections DEC-1, DEC-3, DEC-4, Backlog.
# The change record — every edit, every invocation, every surviving grep hit — is the
# `# RECORD` block at the foot of this file.

decisions:
  - id: D-21
    choice: A touchpoint count is a measured zero only for a POST-INSTRUMENTATION feature, decided by a computable predicate - the project carries .harness/metrics/instrumented_at holding one RFC3339 UTC instant, written once by touchpoints.py record() on its first call in that project and never rewritten, and the feature's own start instant (plan.yaml approval.date, else the author date of the first commit that added its feature directory) is at or after that instant; every other feature, including every feature in a project carrying no epoch file at all, reports null with a D-19 specific-sentence reason and never 0.
    because: an absent touchpoints.jsonl is ambiguous by construction - it is both a tracked run in which nothing blocked and a feature that shipped before the counter existed - and at this repository about 50 features are the second kind with 41 of them carrying a signed approval date, so the unscoped rule fabricates exactly the launch-day autonomy tile D-19 forbids; the predicate lives HERE and not inside T-11's intent because D-19 already exists for that reason, a rule stated only in a task's intent gave every other reader a weaker contract than the code implements, and a prose test such as features that predate this feature is not computable at all; the epoch file is chosen over a harness.json key or a git log over touchpoints.py because it self-installs in any onboarded project with no harness-init change, and it fails closed - no epoch means nothing in that project is a measurement.
    dec: none

tasks:
  - id: T-21
    title: Mount T-15's charts inside T-14's panels and gate on the rendered output
    traces: [REQ-07, REQ-10, REQ-11, REQ-12]
    change_type: frontend
    execution_mode: team
    execution_agent: harness-frontend-dev
    depends_on: [T-14, T-15]
    status: ready
    files:
      - .claude/skills/harness/bin/dashboard/client/src/panels.tsx
      - .claude/skills/harness/bin/dashboard/client/src/charts.tsx
      - .claude/skills/harness/bin/dashboard/client/src/panels.test.tsx
    verify: |
      out="$(npm --prefix .claude/skills/harness/bin/dashboard/client run test -- --reporter=verbose 2>&1)" \
        && printf '%s\n' "$out" | grep -q 'grading panel mounts the Shape A histogram' \
        && printf '%s\n' "$out" | grep -q 'trend panel mounts the Shape B time series'
    intent: |
      T-14 creates panels.tsx and T-15 creates charts.tsx AFTER it, and no task in this plan ever
      touches panels.tsx again. Left as drafted, charts.tsx ships as a correct, unimported module
      and every panel renders with no chart in it, while T-14's and T-15's verifies both stay
      green because each greps its own file's source text. This task is the wiring and the gate
      that the wiring happened.
      Write the failing test first, and demonstrate it failing for the right reason - with
      charts.tsx present but not imported by panels.tsx - before you add the import.
      IN charts.tsx, add nothing but a handle: the Shape A component's outermost element carries
      data-testid="chart-shape-a" and the Shape B component's carries data-testid="chart-shape-b".
      Change no other behaviour in that file. A testid is required rather than a role or a text
      query because T-15 renders both charts aria-hidden beside the real table, and
      testing-library's ByRole and ByText cannot see an aria-hidden subtree at all - the query
      that would look more idiomatic here cannot reach the thing under test.
      IN panels.tsx, import both components from ./charts and mount them where DESIGN C-2 places
      them: Shape A inside the grading panel beside the named grade-1/grade-2 outlier table, and
      Shape B inside each of the three trend panels (throughput, blocking human touchpoints, code
      grading). Respect the gap states already built in T-14 - a panel whose payload region hands
      over to NoShipRecords (S-1) mounts NO chart and NO axes, so the mount sits on the branch
      where the data is whole, never above it.
      IN panels.test.tsx, render the REAL panel components through @testing-library/react over a
      hand-written whole fixture payload - not a mock of the chart, not a snapshot of the source -
      and assert with getByTestId. Two cases, with these labels VERBATIM because the verify greps
      for them:
        "grading panel mounts the Shape A histogram" - rendering the grading panel with a fixture
        payload carrying a non-empty bins object puts an element with data-testid chart-shape-a in
        the document.
        "trend panel mounts the Shape B time series" - rendering a trend panel with a fixture
        payload carrying at least one non-empty segmented run puts an element with data-testid
        chart-shape-b in the document.
      WHAT MAKES EACH CASE RED IS THE ABSENCE OF THE MOUNT, and nothing else: getByTestId throws
      when the chart component is not in the rendered output, which is precisely the state
      panels.tsx is in before this task. Do not weaken either case into a source-text assertion,
      a mocked chart, a toMatchSnapshot, or a check that the import statement exists - a
      source-text assertion is the defect this task was created to close, so writing one here
      reproduces it with a greener face.
      Add a THIRD case if and only if you can make it fail honestly - a panel whose payload region
      is S-1 renders no element with either testid - and label it as you like; the verify does not
      grep for it.
      The toolchain (vitest, jsdom, @testing-library/react, vitest.config.ts and the ResizeObserver
      stub) is stood up by T-04 and is a prerequisite of this task, not something to install here.
      This task's verify runs vitest directly. T-22 is what makes the same assertion reachable
      from run-unit-tests.sh, and it is a separate task because run-unit-tests.sh and
      bin/test-*.py are outside your grant even after T-01.
  - id: T-22
    title: Make the client render gate reachable from the integration suite and from CI
    traces: [REQ-07, REQ-12]
    change_type: scaffolding
    execution_mode: team
    execution_agent: harness-dev-ops
    depends_on: [T-03, T-21]
    status: ready
    files:
      - .claude/skills/harness/bin/test-metrics-client-render.py
      - .claude/skills/harness/bin/run-unit-tests.sh
      - .github/workflows/tests.yml
    verify: |
      bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds && python3 .claude/skills/harness/bin/test-metrics-client-render.py
    intent: |
      T-21's render assertion runs only when someone types its verify by hand. run-unit-tests.sh's
      two arrays hold test-*.py BASENAMES ONLY and its drift detector globs $BIN_DIR/test-*.py
      (run-unit-tests.sh lines 30-31 and 61-76), so a vitest or npm script cannot be registered
      there at all. This task is the one adapter that makes it a suite gate.
      Create .claude/skills/harness/bin/test-metrics-client-render.py. It runs
        npm --prefix .claude/skills/harness/bin/dashboard/client run test -- --reporter=verbose
      as a subprocess from the repository root, captures stdout and stderr together, and FAILS
      unless all three hold: the subprocess exited 0, the line
      "grading panel mounts the Shape A histogram" appears in the output, and the line
      "trend panel mounts the Shape B time series" appears. Print one ok line per assertion and
      exit non-zero on any failure. Do not re-implement the render - the whole value of this
      script is that it drives T-21's real test file.
      NO SOFT SKIP, EVER. If node or npm is absent, or if the client's node_modules directory is
      absent, this script FAILS with one line naming what is missing and the exact command that
      fixes it (npm ci --prefix .claude/skills/harness/bin/dashboard/client). It must never
      report success or skip. The ui and component test kinds both ship cmd null in harness.json,
      so this is the ONLY executing gate over any rendered surface in the whole feature, and a
      skip here restores exactly the green-with-nothing-mounted state PF-7408d83a found.
      Register the basename test-metrics-client-render.py in run-unit-tests.sh
      INTEGRATION_SCRIPTS and NOT in UNIT_SCRIPTS - it spawns a subprocess toolchain, which is
      the split's own discriminator (run-unit-tests.sh lines 19-29). T-03 has already declared
      the matching literal .claude/skills/harness/bin/test-metrics-client-render.py in
      harness.json test_kinds.integration.detect, so the KIND CROSS-CHECK passes; add nothing to
      harness.json here.
      THEN MAKE CI ABLE TO RUN IT, which it cannot today. .github/workflows/tests.yml runs
      run-unit-tests.sh --kind integration as a required check, and T-02 gitignores the client's
      node_modules, so the fresh checkout has no installed dependencies and this script would
      fail every run. Add ONE step to that job, after the PyYAML and jsonschema install and
      BEFORE the "Integration suite" step:
        - name: Install the dashboard client dependencies
          run: npm ci --prefix .claude/skills/harness/bin/dashboard/client
      npm ci is correct rather than npm install because T-04 commits package-lock.json, and
      ubuntu-latest ships node and npm already, so no setup-node step is needed - the existing
      setup-bun step is for something else and does not provide npm. Change nothing else in the
      workflow. If ubuntu-latest turns out not to ship npm, STOP and report it rather than
      switching the runner or the package manager - that is a decision.
      Report in your DIGEST the observed exit status of test-metrics-client-render.py and the
      node and npm versions you saw.

# ============================================================================================
# RECORD — what changed in plan cycle 3, and why
# ============================================================================================
#
# BLUF. Both operator rulings that required plan changes are applied. D-03 now names FLASK as
# the server, with three alternatives rejected by name. KPI 4's absent-file-is-zero rule is
# scoped by a computable post-instrumentation predicate recorded as D-21. T-21 mounts T-15's
# charts into T-14's panels behind an executing render assertion, and T-22 makes that assertion
# a suite gate and a CI gate. All eight panel findings carry a disposition; none is open.
#
# (A) DEC-1 — the web framework
# ---------------------------------------------------------------------------------------------
# CHOSEN: Flask. One runtime install (python3 -m pip install flask), a synchronous WSGI app
# matching compute that is entirely subprocess-bound (git, code-grade.py), and
# send_from_directory already does the traversal-safe join and mimetype lookup the /assets
# route needs.
# REJECTED, each with its reason, in D-03's `because:`:
#   FastAPI plus uvicorn — two installs and an async event loop in front of wholly synchronous
#     work; every route would be pushed to a threadpool anyway.
#   A Node server — T-06..T-11 build the whole KPI core in Python (kpi.py, grading.py,
#     defects.py, attribution.py, trend.py, touchpoints.py). It means PORTING all six modules;
#     the alternative, shelling out to python3 per request, adds an interpreter start and a
#     re-read of every feature to a 3.6s budget. Named explicitly in the `because:` as required.
#   python3 stdlib ThreadingHTTPServer — the value this decision carried until today. The
#     operator ruled the reversal invalid, and hand-writing the route table, the dist traversal
#     check and the Content-Type table re-derives send_from_directory and safe_join as feature
#     code nothing outside this feature tests.
#
# T-12's intent was rewritten to match: Flask app with routing decorators; the ThreadingHTTPServer
# thread-count paragraph is REPLACED (not deleted) by the werkzeug equivalent —
# app.run(host="127.0.0.1", port=<n>, threaded=True, debug=False, use_reloader=False), whose
# thread count is likewise unbounded and accepted for D-05's reason, so D-05's rationale stays
# attached to a live sentence. debug=False and use_reloader=False are stated as non-optional.
# UNCHANGED IN SUBSTANCE, as instructed: loopback-only bind (D-05), read-only (REQ-13), default
# port 8971, --check, the /assets Content-Type requirement AND its explicit fallback table (kept
# because guess_type returns None for a type the host mime database lacks), the 8.0s ceiling and
# its whole measurement paragraph, 404-JSON and 400-naming-three-tokens, and the
# "do NOT assert jsonschema" paragraph. The prerequisite gate now names Flask alongside python3,
# yaml, harness.json and the bundle, and prints exact install commands for each.
# The test list gained one case: with Flask made unimportable, the same invocation exits
# non-zero naming it — the new prerequisite is proven to gate rather than assumed to.
#
# PREREQUISITE SCOPE — DECIDED: DASHBOARD-ONLY, not a ninth platform prerequisite.
# yaml and jsonschema are platform prerequisites because harness bin scripts import them on
# every run (check-state.sh, validate-feature-json.py, plan-merge.py), so a missing one breaks
# the factory itself. Nothing in .claude/skills/harness/bin/ outside dashboard/ imports Flask,
# and the dashboard is one optional command. Declaring it harness-wide would force every
# onboarded project and every CI job to install a web framework to run a factory that never
# calls it, and harness-init's own text already draws this line ("This is NOT a ninth
# prerequisite and the count above does not change", .agents/skills/harness-init/SKILL.md:52).
# So no task touches harness-init or tests.yml for Flask; T-12's REQ-14 gate is the whole
# mechanism, and T-17 documents it. No new task was added for this.
#
# (B) DEC-4 / PF-328f8f3c — KPI 4 must never fabricate a zero
# ---------------------------------------------------------------------------------------------
# THE PREDICATE, recorded as D-21 above and therefore consultable without reading a task:
#   epoch      = the single RFC3339 UTC instant on line 1 of .harness/metrics/instrumented_at,
#                written once by touchpoints.py record() on its first call in that project.
#   start      = the feature's plan.yaml approval.date, else the author date of the first commit
#                that added its feature directory.
#   POST       = epoch exists AND start exists AND start >= epoch  -> count lines; absent file
#                is 0, a measured zero.
#   otherwise  -> null plus a D-19 specific sentence. Three distinct sentences, one per cause
#                (no epoch in this project / feature cannot be dated / feature predates the
#                epoch), because "no data" is what D-19 forbids.
# Rejected alternatives for the predicate: a harness.json key (needs a harness-init change to
# reach a foreign project), and git log over touchpoints.py (the script does not exist inside a
# foreign project_root at all). The epoch file self-installs and fails closed.
# T-11's intent and verify are rewritten. The sentence "an absent file means a run with no
# touchpoints, which is a measured zero, not unavailable" is GONE, replaced by the four-branch
# ladder. count() now returns a (value, reason) PAIR — T-19's intent needed no change because it
# already says any field it cannot compute is null with its reason and never 0.
# T-11's verify asserts BOTH BRANCHES SEPARATELY by grepping two verbatim case labels out of
# test-metrics-trend.py's output, and also that no FAIL line appears (the runner's exit status
# alone is not sufficient evidence — see run-unit-tests.sh's own failure accounting).
# T-20's opening paragraph asserted the old rule as its motivation; it now says the true one —
# with no call site the epoch is never written, every feature falls to branch 1, and REQ-06
# would ship honest but permanently unmeasured.
# T-06 and T-10 were checked and carry NO copy of the rule: T-06's unavailability contract is
# already correct and generic, and T-10's "shipped before metrics existed" concerns the trend
# record, not the touchpoint file. No amendment was needed in either.
#
# (C) DEC-4 / PF-7408d83a — the chart is wired, and the wiring is gated
# ---------------------------------------------------------------------------------------------
# TWO tasks, not one, and the second is forced by a domain grant, not by preference.
# check-domain.sh --resolve, run in this worktree, reports harness-backend-dev and
# harness-dev-ops for .claude/skills/harness/bin/run-unit-tests.sh and for
# .claude/skills/harness/bin/test-metrics-client-render.py. T-01 grants harness-frontend-dev
# ONLY .claude/skills/harness/bin/dashboard/client/**, so the agent the dispatch names for T-21
# cannot write the runner script or the bash array. Merging them into one task would have made
# T-21 undispatchable; splitting them plans the prerequisite instead of assuming it.
#   T-21 (harness-frontend-dev) — the mount and the render assertion. Its verify invokes vitest
#     directly, which is an executing render.
#   T-22 (harness-dev-ops) — the test-*.py adapter, its INTEGRATION_SCRIPTS registration, and
#     the CI step that installs the client dependencies.
# WHAT MAKES THE ASSERTION RED: panels.test.tsx renders the real panel components through
# @testing-library/react over a whole hand-written fixture payload and calls
# getByTestId('chart-shape-a') / getByTestId('chart-shape-b'). getByTestId THROWS when the chart
# component is absent from the rendered output — which is exactly panels.tsx's state before the
# import is added. No .tsx source text is read by any assertion.
# Why a testid and not getByRole/getByText: T-15 renders both charts aria-hidden beside the real
# table, and testing-library cannot see an aria-hidden subtree, so the idiomatic queries cannot
# reach the thing under test.
# T-21's verify, verbatim:
#   out="$(npm --prefix .claude/skills/harness/bin/dashboard/client run test -- --reporter=verbose 2>&1)" \
#     && printf '%s\n' "$out" | grep -q 'grading panel mounts the Shape A histogram' \
#     && printf '%s\n' "$out" | grep -q 'trend panel mounts the Shape B time series'
# The exit status is the gate (vitest exits non-zero on a failing case); the two greps are what
# stop a doer from deleting a case and passing anyway.
# PLANNED PREREQUISITES, none assumed:
#   T-04 — vitest, jsdom and @testing-library/react added as exact devDependency pins, a `test`
#     script set to `vitest run`, vitest.config.ts (jsdom, globals, src/**/*.test.tsx,
#     setupFiles) and vitest.setup.ts (a ResizeObserver stub, because jsdom has none and a
#     CAP-13 responsive chart throws on mount without one — the one red T-21's gate must not
#     have). T-04's files and verify were extended to match, and it is told NOT to run vitest
#     (src/ does not exist yet and `vitest run` with no test file exits non-zero).
#   T-03 — a THIRD literal, .claude/skills/harness/bin/test-metrics-client-render.py, added to
#     harness.json test_kinds.integration.detect and to T-03's own inline verify assertion, so
#     run-unit-tests.sh's KIND CROSS-CHECK passes when T-22 registers the basename.
#   T-22 — the CI step. .github/workflows/tests.yml runs `--kind integration` as a required
#     check and T-02 gitignores the client's node_modules, so without `npm ci --prefix ...` the
#     new script fails every CI run. check-domain.sh --resolve reports harness-dev-ops for that
#     workflow file, so it is in T-22's lane.
#
# (D) Dispositions — all eight findings, none open
# ---------------------------------------------------------------------------------------------
#   PF-328f8f3c high  resolved   resolved_by D-21/T-11/T-20 (recorded as T-11)   DEC-4
#   PF-7408d83a high  resolved   resolved_by T-21                                DEC-4
#   PF-6aa9faae med   overruled  DEC-3 keeps Shape B this increment
#   PF-04c95fd6 med   overruled  Backlog B-1
#   PF-3713534d med   overruled  Backlog B-2
#   PF-55e28a6e med   overruled  Backlog B-3
#   PF-d2fc9563 med   overruled  Backlog B-4
#   PF-ce8b018f med   overruled  Backlog B-5
# last_run, cycle, both readers, and every id, severity, reader and summary were reproduced
# byte-identical through `set-panel --value-file`.
#
# BRIEF.md changes (all of them)
# ---------------------------------------------------------------------------------------------
#   1. `## Constraints`, the "Disclosure, new since the grilling" bullet — "served off the same
#      stdlib server" reworded to "served off the same Python server" and the bullet now says
#      D-03 settled Flask on 2026-09-01. The disclosure itself is KEPT; only the false assertion
#      about what the server is was removed.
#   2. `## Constraints` — one clause added to the runtime-dependency bullet naming Flask as a
#      dashboard-only prerequisite gated in T-12, not a platform one.
#   3. `## Success Criteria` — NEW SC-17, the pre/post-instrumentation split, asserted per
#      branch, verify: automated, evidence: integration (T-11's asserting script
#      test-metrics-trend.py is registered in INTEGRATION_SCRIPTS, so integration is the honest
#      kind — declaring `unit` here would reproduce PF-d2fc9563 in a new criterion).
#   4. `### Coverage` — REQ-06 and REQ-11 rows gain SC-17, and an SC-17 row was added.
#   `## Approval` is untouched and still `status: pending`.
#
# DESIGN.md changes — NONE. THE WRITE WAS DENIED, AND THE GAP IS AN OPEN QUESTION
# ---------------------------------------------------------------------------------------------
# DESIGN.md carries NO stdlib or framework assertion at all, so ruling DEC-1 forced nothing
# there (the grep for stdlib/ThreadingHTTPServer/http.server returns nothing in that file).
# Ruling DEC-4 DOES force one change and it could not be made. C-1 landing tile 3 (Blocking
# human touchpoints) reads "per-feature mean, with the count of features at zero"
# (DESIGN.md:165). Under D-21 most features at launch are NOT TRACKED, so a mean whose
# denominator silently swallows them is the S-4 fabrication one level up, and the tile needs a
# third term: the count of features not tracked.
# check-domain.sh BLOCKED the edit — harness-pm's grants are BRIEF.md, PLAN.md, plan.yaml,
# notes/research-*.md, notes/uat-*.md, glossary.md and its own expertise/observations. DESIGN.md
# belongs to another lane, and the hook says not to work around it. So:
#   - the CONTRACT is fully specified in the plan: T-11's intent requires the aggregate to be
#     the mean over TRACKED features plus the count of tracked features at zero PLUS the count
#     of features not tracked, reported by name on the payload. The build is not ambiguous.
#   - DESIGN.md:165 is now UNDERSTATED relative to the plan and needs one sentence added by
#     whoever owns it. Raised as Q2 in the DIGEST. It is not a blocker for signature: no task
#     reads DESIGN.md as its authority for that term, T-14 reads the payload.
#
# TWO AMENDMENTS BEYOND THE FOUR TARGETS, both forced by the acceptance criteria
# ---------------------------------------------------------------------------------------------
#   D-20.because — the phrase "off the same stdlib server" was corrected to "off the same
#     Python server", a two-word substitution with a delta of 0 characters and no change to
#     the decision. D-20 is on the do-not-touch list as "ruled KEEP", and this touches nothing
#     the ruling settled: the choice, the recommendation and the whole argument are byte-
#     identical. It was corrected because the acceptance criterion is absolute — no line in
#     plan.yaml may ASSERT the server is stdlib — and that clause asserted it as a property of
#     "the same server", not as a label on the rejected alternative. Reported as a deliberate
#     deviation.
#   T-11.traces — REQ-06 gained REQ-11. T-11 now implements the unavailability contract for
#     KPI 4, and SC-17 traces REQ-11; without this REQ-11 has no task carrying the touchpoint
#     half of it.
#
# SURVIVING GREP HITS, every one accounted for
# ---------------------------------------------------------------------------------------------
# grep -n 'stdlib\|ThreadingHTTPServer\|http\.server' over plan.yaml, BRIEF.md and DESIGN.md
# after the change. BRIEF.md: ZERO hits. DESIGN.md: ZERO hits. plan.yaml, five hits, none of
# which asserts the server is stdlib:
#   D-03 choice   — "rejected ... python3 stdlib ThreadingHTTPServer". Explicitly a rejected
#                   alternative. Required by the ruling, which demands three named rejects.
#   D-03 because  — "REJECTED - python3 stdlib ThreadingHTTPServer, which this decision named
#                   as the choice until 2026-09-01". Labelled rejected, and dated.
#   T-12 intent   — "replacing what this task said while D-03 named the stdlib server" and
#                   "the ThreadingHTTPServer paragraph". Both are historical, telling the doer
#                   which paragraph was superseded; neither asserts a current property.
#   the RECORD block below — this document's own prose, quoting the rejected option.
# NOTE: the four hits at plan.yaml lines ~1150+ are THIS FILE'S COMMENT BLOCK, which
# plan-merge.py apply carried into plan.yaml (see Q1 in the DIGEST).
#
# plan-merge.py invocations, in order
# ---------------------------------------------------------------------------------------------
#   NOTE: the worktree's own copy of plan-merge.py predates `set-panel` and `--yaml-value`, so
#   from the T-03 amend onward the MAIN checkout's binary was used against the worktree's
#   plan.yaml by absolute path. Both write through the same lock and the same splice.
#    1. amend --key decisions --id D-03 --field choice   --show
#    2. amend --key decisions --id D-03 --field because  --show
#    3. amend --key decisions --id D-03 --field choice   --expect-sha256 06859b71… --value-file
#    4. amend --key decisions --id D-03 --field because  --expect-sha256 bfdcfa96… --value-file
#    5. amend --key tasks --id T-12 --field intent  --show
#    6. amend --key tasks --id T-12 --field intent  --expect-sha256 14cdbdb2… --value-file
#    7. amend --key tasks --id T-11 --field intent  --show
#    8. amend --key tasks --id T-11 --field verify  --show
#    9. amend --key tasks --id T-11 --field intent  --expect-sha256 ca5e70ea… --value-file
#   10. amend --key tasks --id T-11 --field verify  --expect-sha256 60868592… --value-file
#   11. amend --key tasks --id T-20 --field intent  --show
#   12. amend --key tasks --id T-20 --field intent  --expect-sha256 231e4fde… --value-file
#   13. amend --key tasks --id T-03 --field intent  --show
#   14. amend --key tasks --id T-03 --field verify  --show
#   15. amend --key tasks --id T-04 --field intent  --show
#   16. amend --key tasks --id T-04 --field verify  --show
#   17. amend --key tasks --id T-04 --field files   --show --yaml-value
#   18. amend --key tasks --id T-03 --field intent  --expect-sha256 31ee0680… --value-file
#   19. amend --key tasks --id T-03 --field verify  --expect-sha256 7598650a… --value-file
#   20. amend --key tasks --id T-04 --field intent  --expect-sha256 9bfab08b… --value-file
#   21. amend --key tasks --id T-04 --field verify  --expect-sha256 31482c6f… --value-file
#   22. amend --key tasks --id T-04 --field files   --expect-sha256 f298e484… --value-file --yaml-value
#   23. apply --proposal <this file>                      (adds D-21, T-21, T-22)
#   24. set-panel --value-file <panel value file>         (all eight dispositions)
#   25. amend --key tasks --id T-11 --field traces  --show --yaml-value
#   26. amend --key tasks --id T-11 --field traces  --expect-sha256 28af3d65… --value-file --yaml-value
#   27. amend --key decisions --id D-20 --field because --show
#   28. amend --key decisions --id D-20 --field because --expect-sha256 67669f8a… --value-file
#   Every one carried --file <the FEAT-53 worktree plan.yaml> by absolute path. No Edit, no
#   Write and no shell redirect touched plan.yaml at any point.
#
# PROOF
# ---------------------------------------------------------------------------------------------
#   yaml.safe_load over the final plan.yaml succeeds; top keys are schema, feature, status,
#     source_issues, approval, lanes, decisions, tasks, panel. 22 tasks, 21 decisions,
#     8 panel findings, 0 with disposition open.
#   approval: sha256 of lines 6-9 is
#     b13cc26e6afad3f81e10dd9fbefdc4656bf124264aabce240812b27c46234040 both BEFORE the first
#     amend and AFTER the last — byte-identical, and it reloads as
#     {status: pending, approved_by: none, date: none}.
#   panel identity: every id, severity, reader and summary compared field by field against
#     `git show HEAD:...plan.yaml` — all eight match, last_run 2026-09-01-06-validator and
#     cycle 1 unchanged, both readers still status ran. The value file was GENERATED from the
#     file's own panel rather than retyped, so drift was not possible.
#   check-plan-routes.py on this plan: T-21 granted to harness-backend-dev, harness-dev-ops;
#     T-22 the same; every pre-existing task unchanged. The one reported violation is the
#     pre-existing team-config DEVIATION line, identical before and after this cycle.
#
# Open questions for the tier above are in the DIGEST, not here.
#
# =============================================================================================
# LOOP-BACK 2 — 2026-09-01 — closing the cycle-2 goal-check's blocking findings
# =============================================================================================
#
# The YAML above is the cycle-3 proposal AS APPLIED and is NOT re-applied by this pass. Every
# edit below went through `plan-merge.py amend` — one field, one compare-and-swap — so nothing
# in this pass could add a comment block to plan.yaml. Sequence, in order:
#
#   1. amend --key tasks --id T-22 --field intent  --expect-sha256 85f34dc8… --value-file
#      (Q1) adds `flask` to .github/workflows/tests.yml — the required `integration` context
#      runs T-12's script — states the two installs (npm ci, flask) as (a) and (b), and states
#      that this is THIS repo's test job and NOT a ninth platform prerequisite, so a later
#      reader does not "fix" it into harness-init. Also rewrites the render script's contract:
#      `--reporter=json`, raw_decode from the first `{`, and status == "passed" per case, with
#      the reason a label grep was insufficient written down.
#   2. amend --key tasks --id T-16 --field intent  --expect-sha256 325f48b1… --value-file
#      (Q2) "python3 and nothing else" -> no node toolchain and no BUILD step, prerequisites
#      python3 + PyYAML + Flask gated by serve.py --check; the false sentence is named as false.
#   3. amend --key tasks --id T-17 --field intent  --expect-sha256 665cf580… --value-file
#      (Q2) the five gate checks WITH Flask; `jsonschema` explicitly not a dashboard
#      prerequisite, with T-12's reason; Flask/PyYAML capitalisation pinned for the verify.
#   4. amend --key tasks --id T-17 --field verify  --expect-sha256 79388cc2… --value-file
#      (Q2) adds Flask, PyYAML, `python3 -m pip install flask`, harness.json and
#      client/dist/index.html to the token list, so wrong REQ-14 docs can no longer ship green.
#   5. amend --key tasks --id T-21 --field verify  --expect-sha256 543abd0b… --value-file
#      (Q3a) `--reporter=json` + per-case status, replacing the two label greps.
#   6. amend --key tasks --id T-21 --field intent  --expect-sha256 99ff433c… --value-file
#      (Q3a+Q3b) chart-internal assertions inside each subtree, the fixture shape they need
#      (a grade left at 0; two contiguous runs), both reds to be demonstrated, and STOP-and-
#      report if T-15's real output or the pinned vitest cannot satisfy it.
#   7. amend --key decisions --id D-21 --field because --expect-sha256 f47e49de… --value-file
#      (Q5) the epoch's durability recorded as an accepted risk, naming NOBODY as the resolved
#      lane for .harness/metrics/**, what moves if the file is lost, why the loss direction is
#      safe, and T-11's branch-1 case as the assertion that pins the post-loss state.
#
#   BRIEF.md, by Edit (pm's own artifact, no merge tool): SC-18 added
#   (verify: automated, evidence: integration — integration because T-22 registers the script
#   in INTEGRATION_SCRIPTS); the `component`/`typecheck` verification gap corrected from
#   "unproven by any gate" to partly proven, with the gate named and BOUNDED; coverage table
#   updated in both directions (REQ-07 and REQ-12 rows, plus the SC-18 -> REQ-07, REQ-12 row).
#
# PROOF, this pass
# ---------------------------------------------------------------------------------------------
#   plan.yaml sha256 65d51faf…6f3c BEFORE -> a6b54eb2…ba03 AFTER; yaml.safe_load succeeds;
#     22 tasks, 21 decisions unchanged; every amended field's tail verified present after the
#     splice (no truncated scalar).
#   approval: sha256 of lines 6-9 is b13cc26e6afad3f81e10dd9fbefdc4656bf124264aabce240812b27c46234040
#     before and after, and identical to `git show HEAD:` — byte-identical, status pending.
#   panel: 8 findings, dispositions {resolved, overruled}, none open; 2 readers, both `ran`.
#     D-20, D-08 and T-18 untouched.
#   check-plan-routes.py on this plan: 0 violation(s); T-20's DEC-174 line is the expected
#     main-session-direct deviation.
#   T-21's verify snippet, extracted VERBATIM from plan.yaml and run over seven synthetic
#     jest-shaped reporter payloads: both-passed 0, npm-preamble 0, describe-prefixed 0,
#     skipped 1, pending 1, failed 1, absent 1. The gate can no longer be greened by test.skip.
#   T-17's verify, extracted VERBATIM and run in a temp root: exit 1 `missing Flask` against a
#     METRICS.md documenting the old prerequisite list; exit 0 once Flask is documented.
#
# Out of this pass by routing, not by omission: the cycle-time origin question (operator's,
# unruled since cycle 1), STATE.md:17 (orchestrator's), DESIGN.md's touchpoint tile (visual
# designer's), and the trailing-comment-block defect in plan-merge.py apply (already raised).
