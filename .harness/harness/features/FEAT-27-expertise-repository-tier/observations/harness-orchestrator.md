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

- 2026-08-19: A lead's digest file CHANGED between my reading it and the return notification
  arriving. I read it off disk the moment it appeared and acted on `severity_max: low` /
  `escalations: []`; the final artifact carries `severity_max: med` and an escalation routed to pm.
  I had already committed a STATE.md sentence quoting the stale value, which made the record false
  until I corrected it. The rule: a digest appearing on disk is not the return — re-read the
  artifact when the notification lands, and treat anything quoted from the early copy as unverified
  until then. The inverse of G-07, and it costs a falsified record rather than a duplicated run.

- 2026-08-19: `validate-digest.py` takes a PERSONA as its first argument, then the path. Invoked
  with the path alone it prints `VERDICT: BLOCKED (contract violation) — unknown persona
  '<the path>'`, which reads exactly like the digest being malformed and is really a usage error;
  `--help` produces the same shape. `validate-digest.py validator-lead <path>` returned `digest ok`
  on the very file the malformed call appeared to reject. Never route a contract-violation verdict
  without re-running the validator with the persona argument first.

- 2026-08-19: Writing a RECOMMENDED task's id into STATE.md tripped a real VIOLATION —
  "STATE.md references T-07, which is absent from its plan.yaml." pm had recommended a follow-up
  task and I recorded it by the id pm sketched. The invariant is right and the fix is mine: a task
  id is coined when pm authors the task under the operator's signature, not when someone recommends
  one. Describe an unapproved task by what it would do and point at the note holding the sketch;
  never give it an id in a state file. The same trap waits for any digest field that names a task.

- 2026-08-19: Routing a plan-domain escalation to pm BEFORE returning it to the operator changed
  the answer materially, and cost one spawn. qa had ranked two coverage gaps and implied both were
  simply missing tests. pm's ruling split them: one is committed at requirement level but
  operationalized by no criterion, the other is uncommitted at every level, and neither is a
  delivery gap. It also killed the framing I would have relayed — "this delays the ship" is not a
  cost when the feature is already gated on four unbuilt tasks, so both options need a signature and
  only the timing differs. An escalation relayed raw asks the operator to do the adjudication the
  owning squad exists to do.

- 2026-08-19: A green-looking suite report was RED, and the tell was where the reader stopped. The
  layer-0 executor reported `run-unit-tests.sh --kind integration` as "106/106, exit 0". The real
  run exits 1 with two FAIL lines — and the LAST line of that run is
  `106/106 checks passed. PASS test-factory-integration.py`, the final script's own internal count.
  A tail-only read of this runner reports any earlier script's failure as success. Always count
  `^FAIL ` lines and capture the runner's own exit status in a variable; never read the tail, and
  never take a piped `$?` (which returns the exit status of `tail`, not the suite — I made that
  mistake myself earlier the same session).

- 2026-08-19: The same report said "all 21 craft files OK". There are 15 craft files and 6
  repository files; 21 is their sum. The conclusion (both tiers pass) was right and the narration
  conflated the two tiers — which matters, because "21 craft files" would mean six craft files had
  been created, a real defect. Count the two tiers separately when a change's whole point is that
  they are separate.

- 2026-08-19: A hardcoded fixture that snapshots a REAL config file reddens on every legitimate
  change to that file. `test-harness-yaml.py`'s `COLLECT_FIXTURE` pins six agents' domain lists from
  the live manifest, so adding sixteen approved grants broke it — with every one of the six
  differing by exactly the expected one entry and nothing missing, which is the signature of a stale
  fixture rather than a broken change. Diagnose by diffing expected-vs-actual PER AGENT before
  routing: "extra == exactly what the task added, missing == empty" distinguishes a fixture refresh
  from a real regression in one measurement, and they route to completely different places.

- 2026-08-19: When refreshing such a fixture, the trap is regenerating it from the function under
  test — the fixture then asserts nothing and passes against a broken parser. The instruction has to
  be to re-derive it from the source data by hand. Worth saying explicitly in the dispatch, because
  pasting the actual output is the fastest way to make the suite green and looks identical in the
  diff.
