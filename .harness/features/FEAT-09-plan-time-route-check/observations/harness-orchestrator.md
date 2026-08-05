# Observations — harness-orchestrator — FEAT-09-plan-time-route-check

- 2026-08-05: The do-not-touch list I was handed for the concurrent feature (12 paths) was
  derived from the OTHER feature's grilling artifact, not from its PLAN. It was incomplete:
  `run-unit-tests.sh` is edited by FEAT-08 T-05 (`FEAT-08/PLAN.md:243, :250-252`) and appears on
  no list. My lead found it by opening the peer feature's PLAN.md directly. Lesson shape: with two
  features in flight, the collision surface is the peer's PLAN `files:` union, not the grilling
  artifact's prose — the artifact predates the plan by definition.

- 2026-08-05: `run-unit-tests.sh:6` is a single-line array that nearly every task's `verify:` in
  both plans rides on as a whole-suite check. A one-line shared file with N writers and a drift
  detector that `exit 2`s is a maximally bad collision surface: the failure is not local to the
  colliding task, it reddens every other task in both features.

- 2026-08-05: `cost-report.py` is project-cumulative and both concurrent orchestrators meter into
  it. The by_agent delta is contaminated at any depth where the two flows share an `agent`+`depth`
  key — here `harness-orchestrator` depth 1 and `orchestrator` depth 0. Reporting the delta as an
  upper bound with the contamination named beat inventing an attribution.

- 2026-08-05: `check-state.sh` INV-5 scans STATE.md for any `\bT-\d+\b` and compares against THIS
  feature's PLAN task ids. Writing "FEAT-08 T-05" in an open question produced a real VIOLATION on
  a factually correct sentence. Refer to a peer feature's tasks by description, never by id.

- 2026-08-05: pm found a self-reference my dispatch missed — T-01's own paths ARE granted, so a
  route checker asking only "does anyone grant this?" passes the DEC-174 carve-out task and never
  reads its `main-session-direct` declaration. A checker that resolves routes cannot validate the
  one task that deliberately deviates from its own table unless deviation is a first-class output.

- 2026-08-05 (build phase): `cost-report.py` derives the transcript dir by munging `os.getcwd()`
  (`:110-115`), so run from a git worktree it prints "no transcripts for this project" and yields
  no figure at all. The session's transcripts live under the ORIGINAL project root's munged name.
  `--project <original root>` fixes it and the call is read-only. Without knowing this, a worktree
  flow reports itself unmetered when it is merely mis-addressed — an INV-11 violation manufactured
  by the tool's own path convention.

- 2026-08-05 (build phase): The cost delta reconciled EXACTLY against the sum of the by_agent rows
  that moved, and only two rows moved. That cross-check independently PROVED no lead had spawned —
  evidence about my own dispatch history that did not come from my memory of it, which DEC-124 says
  I cannot trust. A delta that fails to reconcile means an agent moved that I have not accounted for.

- 2026-08-05 (build phase): Verifying an approved `verify:`'s EXPECTED VALUES before handing it to
  a human is cheap and is not doing the work. T-01's `verify:` asserts `.harness/harness.json`
  resolves to exactly `['harness-dev-ops']`; there is exactly one such grant
  (`team-config.yaml:196`). Had a second agent granted it, a CORRECT implementation would have
  failed an approved assertion and the round trip would have been spent diagnosing the plan.

- 2026-08-05 (build phase): `check-docs.sh`'s registry is stale-STRING markers harvested from
  DECISIONS.md, not `file:line` anchors — so an insertion that shifts every line below it cannot
  rot a citation the way a line-anchored registry would. Checking the registry's KIND settled two
  tasks' risk at once.

- 2026-08-05 (build phase): PLAN gave T-04 `depends_on: T-02` while the user's ruling put T-04 in
  the first segment. Reading what T-04's `verify:` actually DOES settled it in one read: it greps
  SKILL.md for the literal string `check-plan-routes.py` and never executes it, so the dependency
  is documentation ordering, not mechanical.

- 2026-08-05 (commit phase): A "moved, not modified" claim about a function is verifiable in one
  step and should never be taken on trust — extract the function from the base commit and from the
  working tree, dedent and strip blanks, and hash both. Here both matcher functions hashed
  identically, which is what the whole feature's one-matcher invariant rests on. A diff would have
  shown the hoist as a large change and buried the point; the hash answers the actual question.

- 2026-08-05 (commit phase): MY OWN PROBE PRODUCED A FALSE REGRESSION BEFORE THE CODE DID. An
  escaped-quote payload inside a shell echo made the hook's JSON invalid, and the hook exited 0 on
  unparseable input, which read exactly like a broken guard. Build hook payloads as FILES and pipe
  them in. When a probe contradicts a suite that just passed, suspect the probe first.

- 2026-08-05 (commit phase): `bash-write-guard.sh` denies a shell redirect to ANY path outside the
  agent's domain, including a session scratchpad. That is correct and not a bug — the fix is to
  restructure the work so no file is written (pipe the tool's stdout straight into the consuming
  process), never to hunt for a writable location.

- 2026-08-05 (parked): A TOOL YOUR MEASUREMENT DEPENDS ON CAN BE DELETED BY A CONCURRENT FEATURE.
  I spent a step chasing a 0.54 residual in a cost delta; the real cause was that the peer feature
  is `remove-cost-tracking`, had already stripped the rate table from config and staged the
  reporter for deletion. Before diagnosing a discrepancy in a tool's output, check the tool still
  exists and its config is intact. The residual was also measured across two differently-shaped
  samples of my own, which alone made it uninterpretable.

- 2026-08-05 (parked): THE 200-LINE `feature.yaml` CAP IS NOT MECHANICALLY ENFORCED HERE. A
  205-line write succeeded; none of the six registered hooks implements a state-file shape gate and
  `check-state.sh` has no such check. Prior expertise says these caps are PreToolUse BLOCKs, which
  is wrong for this tree and would have led me to trust the tool instead of counting. Count the
  lines yourself after every state write.

- 2026-08-05 (parked): WHEN A RULING CITES A GREP, RUN THE GREP. The ruling that the cost mandate
  was removed from the playbook was true in the MAIN checkout and false in my worktree — same file,
  two answers, because I sit on the far side of an unmerged seam. Verifying did not just confirm
  the ruling, it revealed which text actually governs me right now. Rulings about a shared file are
  worth re-checking in the tree you are standing in.
