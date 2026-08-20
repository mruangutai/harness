# Observations — harness-orchestrator — FEAT-28-ci-wiring-asserted

- 2026-08-19: The orchestrator playbook (`.claude/skills/harness/SKILL.md`, "You are a PHASE"
  section) instructs "Record your phase in `feature.json` `phase:`". The feature execution-state
  schema (`.claude/skills/harness/bin/feature-schema.json`) has `additionalProperties: false` and
  its own description says there is NO `phase` property — "`phase` and `status` collapsed into
  `status` alone under D-09/D-10; a schema that still declared `phase` would re-legalise the field
  this feature exists to delete." Writing feature.json from the playbook's instruction is blocked
  at the Write hook. The playbook instruction is stale against the schema. Raised as an
  open_question in the return, not fixed here (`.claude/skills/` is not my domain).

- 2026-08-19: `bash-write-guard.sh` blocks heredoc redirects (`cat > path <<EOF`) even for paths
  INSIDE my domain — the guard reported the target as "xxxxxxxxxxxxxxx" and routed me to the Write
  tool. So instantiating a feature dir is: `mkdir -p` via Bash (allowed), then one Write call per
  file. Batching the whole instantiation into a single heredoc script fails as a unit.

- 2026-08-19: Sequencing a plan mission while a SIBLING FEATURE BUILDS in the same checkout is
  workable but the git ban has to be pushed down verbatim into the lead dispatch, not summarised.
  The lead dispatches members who each have Bash; the constraint has to survive two hops. Naming
  the specific forbidden verbs (`commit`/`checkout`/`branch`/`stash`/`add`) and explicitly
  allowing read-only git and `gh issue view` is what keeps a member from either violating it or
  refusing to measure anything.

- 2026-08-19: Measuring the design tension BEFORE dispatching pm changed the shape of the question.
  The user framed three routes for where a new CI assertion registers; one grep of
  `run-unit-tests.sh` line 18 showed `test-check-plan-routes.py` and `test-check-domain.py` are
  ALREADY in `INTEGRATION_SCRIPTS`, and `git diff` showed FEAT-27 touches only the `UNIT_SCRIPTS`
  line. That turned "which route" from speculative into priced, and the dispatch carried the
  measurement instead of asking pm to re-derive it. Cost: two Bash calls.

- 2026-08-19: MISTAKE, and the recovery. I had **no `SendMessage` tool** in my toolset, though the
  Agent tool's own description tells me to use SendMessage to continue a running agent. Trying to
  send a mid-run correction to the in-flight product-lead therefore spawned a SECOND product-lead
  with a correction-only prompt and no feature context — two leads potentially writing the same
  `plan.yaml`. Check the toolset for `SendMessage` BEFORE dispatching, and if it is absent treat
  the first dispatch as un-amendable: front-load every constraint, because there is no channel to
  a running agent. Recovery used: verify the artifacts on disk after both return and reconcile
  there, rather than trusting either digest's account of what it wrote.

- 2026-08-19: The write ban and the domain resolver answer DIFFERENT questions, and I conflated
  them in a dispatch. `check-domain.sh --resolve .github/workflows/tests.yml` returning
  `harness-dev-ops` says the file is OWNED and therefore dispatchable in principle; it says
  nothing about whether THIS run may write it. A task-level "write only inside the feature dir"
  constraint still binds. I had told pm to red-prove an assertion by a "restored-and-byte-verified
  edit" to `tests.yml` — outside the feature dir, in a dirty tree on another feature's branch.
  A red-proof under a write ban is temp-copy-only; anything needing an in-tree mutation is a
  build-phase task with a `depends_on`, not a plan-phase measurement.
