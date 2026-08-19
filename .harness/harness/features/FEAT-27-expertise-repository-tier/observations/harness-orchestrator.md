# Observations — harness-orchestrator — FEAT-27-expertise-repository-tier

- 2026-08-19: Pre-change baseline of `inject-expertise.sh`, captured at `253287f` BEFORE T-02 edits
  it, because T-02 changes what the hook DISCOVERS and after that the exit code stops being evidence
  (P-09). Per agent, `context_lines` from `hookSpecificOutput.additionalContext`:
  `harness-qa` 134, `harness-orchestrator` 149, `harness-dev-ops` 35, `harness-frontend-dev` 0,
  `some-other-agent` 0. Exactly one header emitted — `## Your Expertise — this codebase (project
  tier, authoritative on conflict)`. No global tier ($HOME/.harness absent) and no codebase-map block
  (`.harness/codebase/` does not exist in this repo).
  The discriminator this buys: after T-02 and BEFORE T-04, every one of those line counts must be
  UNCHANGED and only the header wording may move, because no repository tier exists on disk yet. A
  count that moves at T-02 means the hook is emitting something it should not.

- 2026-08-19: The baseline paid off and cost about four minutes. Post-T-02 the five counts were
  identical (134/149/35/0/0), the header had moved to `this checkout's craft (project tier)`, and the
  precedence line was correctly ABSENT because no repository tier exists on disk yet. None of the
  twelve new test cases can see this: they all build temp roots, so the only thing that exercises the
  hook against the REAL corpus is an orchestrator running it by hand. Worth doing on any hook change.

- 2026-08-19: `harness-frontend-dev` returning 0 lines is the live state T-02's case 10 is written
  against — it holds a craft GRANT in `team-config.yaml` but has no craft file on disk. Confirmed by
  running the hook, not by reading the manifest. 15 craft files, 16 grants.

- 2026-08-19: A feature whose deliverable is a spawn-time hook can be verified END TO END by the
  orchestrator before any reviewer sees it, because the hook is a plain script with a documented
  stdin/stdout contract. Building a temp root with three tiers (craft + two repository segments) and
  invoking it took one bash call and proved the precedence line appears exactly once, before the
  first repository block; segments sort; both bodies inject; and the 40- and 150-line truncation
  notices each name their own budget. That is SC-01, SC-09 and SC-10 measured rather than argued —
  and it means a panel finding against them starts from a rebuttable measurement.

- 2026-08-19: This feature's plan puts 3 of 6 tasks in the `main-session-direct` lane, so the build
  cannot run as one orchestrator session. The packing that minimises round trips is: run the
  dependency-free TEAM tasks first (T-02, T-03), which unblocks ALL THREE layer-0 tasks at once
  (T-04 needs T-01+T-03, T-06 needs T-03+T-04), so they hand over as a single ordered batch instead
  of three separate relays. Ordering the segments by lane rather than by task number turned 3
  round trips into 2.

- 2026-08-19: The layer-0 handover note deliberately does NOT copy each task's `intent:` and
  `verify:` out of `plan.yaml` — it ships the `yaml.safe_load` extraction command instead. A copy of
  an approved artifact is a copy that can drift from the signature; an extraction command cannot.
  The intents here run to 40+ lines with byte-exact assertion strings in them, so the drift risk was
  not theoretical.

- 2026-08-19: A concurrent session branched this SHARED checkout mid-run, so `git checkout -b` had
  put me on the wrong branch and my signed-artifacts commit landed on a chore branch (#433's
  foreign-pen shape). Repair that worked without disturbing a live subagent: `git stash push --
  <feature-dir>`, checkout the real branch, `git cherry-pick <the commit>`, `git stash pop` — run as
  ONE bash invocation so the window where tracked files are absent from the tree is sub-second. The
  tell to check first: `git diff --name-only <target-branch> HEAD` — if it lists only files no live
  subagent touches, the switch is safe.

- 2026-08-19: Do not verify a branch-repair claim from the reporting agent's summary. The coordinator
  reported the amendment commit was "already on main"; local `main` did not contain it and was one
  commit behind — the content was on `origin/main` under a different sha from a squash merge. The
  conclusion (do not cherry-pick it) was right, the stated reason was checkable and only half true,
  and `git branch -a --contains <sha>` plus `git log origin/main` settled it in one call.

- 2026-08-19: I nearly counted another PHASE's rework into my own budget. The plan run's `state.yaml`
  records per-step `cycles:` summing to 3, and I wrote `cycles_used: 3` reasoning that the counter is
  feature-wide. It is not that simple: DEC-157 counts rework THIS orchestrator routes or that a lead
  reports from inside a run THIS orchestrator dispatched. Those cycles were reported to the
  plan-phase orchestrator, which recorded 0. Two tells that it was wrong: I was summing a field on a
  step still reading `status: running`, and I had spent 30% of the only budget with teeth before
  dispatching anything. An inflated count can force a BLOCKED return with nothing wrong, which is
  the exact failure DEC-157 exists to prevent — so the error is not conservative, it is dangerous.

- 2026-08-19: A run dir is not automatically a run. `runs/2026-08-18-1-eng/` held an architecture
  review with no `state.yaml` and no `digest.md`; it was a STEP inside the product run (recorded
  there as S-04), hosted by a second lead, which created its own dir. Recording it in `feature.json`
  `runs:` would have double-counted it AND forced me to invent a verdict, since the schema's run
  entry has no field in which to say "inherited from another run's step record". Leaving it out costs
  one `check-state.sh` NOTE about an unrecorded dir; that note is the honest outcome.

- 2026-08-19: A stale `detect` glob in `harness.json` looked like it would fail the blocking gate on
  a correct task, and one command disproved it. `test_kinds.integration.detect` does not name
  `test-check-expertise.py`, and the qa-gate skill turns "detect found nothing" into FAIL/BLOCKED —
  but the configured `cmd` is what discharges the obligation, and `run-unit-tests.sh --kind
  integration` executes the file (it is in `INTEGRATION_SCRIPTS`, and the run prints `PASS
  test-check-expertise.py`). Rule of thumb: when config metadata and a runner disagree about what
  runs, RUN IT — the runner is the authority, and the metadata becomes a backlog row, not a gate.
