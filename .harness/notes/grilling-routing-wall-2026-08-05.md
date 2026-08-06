# Grilling — the routing wall, plan-time route resolution (issue #20) — 2026-08-05

## Destination

No PLAN reaches signature with a task whose target paths no agent may write and nobody noticed.
Every task's route is resolved **at plan time** against `.harness/team-config.yaml`, mechanically —
either it names the agent that may write those paths, or it is a declared main-session step. The
build phase never discovers routing again.

## Settled

- **Enforcement is MECHANICAL, not prose.** A checker runs every PLAN task's `files:` through domain
  resolution and fails on a task that resolves to neither a granted agent nor a declared
  main-session step.
- **ONE matcher, reused — not duplicated.** `check-domain.sh` gains a resolve mode (shape:
  `--resolve <path>` answering *which agent may write this, or nobody*), and the plan-time checker
  calls it. The alternative of extracting the matcher into a shared module was considered and
  rejected: it rewrites the guard rather than adding a mode to it, for the same outcome.
- **DEC-174 therefore applies to the `check-domain.sh` half** — direct execution, tests run
  explicitly, a human reading the diff, never a team run. Same shape as FEAT-07's T-01.
- **Prose-only was rejected**, and for the reason the user gave on FEAT-07's #19: it is the
  "relied on being pointed at" pattern DEC-125 names. pm produced the artifact twice unprompted,
  so prose adds little that is not already happening.
- **Concurrency:** planned and built alongside FEAT-08 (issue #58, cost removal). #20 was chosen for
  this specifically because it has **zero file overlap** with #58 — see `## Facts`.

## Not yet specified

- Whether the checker is a new script, a mode of an existing one, or an invariant inside
  `check-state.sh`. It depends on when it must fire — at PLAN write, at the approval gate, or on
  every `check-state.sh` sweep — and that timing question is not yet sharp.
- What a task with a glob in `files:` (`docs/**`) should resolve to when the glob spans two agents'
  domains. Nobody has hit it; the shape of the answer cannot be stated.
- Whether the `## Lanes` table stays a human-readable artifact once the check is mechanical, or
  becomes generated output.

## Out of scope

- **Rows 8, 9 and 10 of the performance review** — trimming the orchestrator and universal preloads,
  and counting runs. All three collide with FEAT-08 on shared files and are deliberately queued
  behind it. Row 10 is filed as issue **#79**.
- **#21** (qa phase 1 concurrent with the build). It collides with open issues #40/#41/#42 on qa's
  permissions and the review panel's shape, and needs a companion clause to DEC-159's build-exit
  predicate.
- **Row 7**, the hook-fire multiplier. Highest risk row in the review's own ranking and the only one
  where getting it wrong weakens enforcement rather than costing time.
- Changing any agent's domain grants. This feature makes the existing grants *legible at plan time*;
  it does not re-draw them.

## Facts I verified (so pm does not re-derive them)

All at `ae2443d`.

- **`execution_mode:` and the `## Lanes` table exist in NO template and NO skill.**
  `grep -n 'execution_mode\|lane'` over `templates/PLAN.md` and `harness-spec-driven/SKILL.md`
  returns nothing. They are FEAT-06 house style, copied by FEAT-07 — invented ad hoc twice, which is
  the evidence that the need is real and the codification is missing.
- **The proven artifact to codify is `FEAT-07/PLAN.md:3-15`** — a `## Lanes` table mapping surface →
  lane → the `team-config.yaml` line that grants it, plus per-task `execution_mode:` with a reason.
- **`templates/PLAN.md:10` already carries the adjacent rule** — a deviation from a `team-config.yaml`
  convention must appear in `## Decisions`. What is missing is the *resolution*, not the disclosure.
- **The matcher is INLINE in `check-domain.sh:215`, `def matches(path, pat)`**, with deliberately
  custom semantics: its comment at `:193` records that `fnmatch` is wrong here because its `*`
  matches `/`, so `web/*/x` would match too much. Any second implementation is a drift risk of
  exactly the DEC-126 kind.
- **Domain resolution needs `check-domain.sh` only** — the grants live in `team-config.yaml` and are
  read there.
- **THE COLLISION CHECK THAT PUT #20 IN THIS SLOT.** FEAT-08 (#58) touches `harness/SKILL.md`,
  `harness-team/SKILL.md`, `harness-orchestrator.md`, `teams/*.yaml`, `harness.json`,
  `check-state.sh`, `validate-digest.py`, `cost-report.py` and `docs/**`. #20 touches
  `check-domain.sh`, `templates/PLAN.md`, `harness-spec-driven/SKILL.md`, `harness-pm.md` and a new
  checker. **The intersection is empty.** Rows 8/9/10 do NOT have this property — row 8's first
  required rider is *"move the ORCHESTRATOR-ONLY `cost-report.py` paragraph or INV-11's metering
  instruction is lost"*, and FEAT-08 deletes both `cost-report.py` and INV-11, so the two plans
  would contradict each other.
- **Three recurrences, named as such in the record:** `FEAT-05/feature.yaml:78-81` calls it the
  "ROUTING WALL, third recurrence" — dev-ops granted neither `.gitignore` nor `templates/**` nor
  `harness-init/SKILL.md`. FEAT-04 T-09/T-10 and FEAT-03 Q13 are the same wall. It cost a real
  ESCALATE at FEAT-04 run 10, $16, with the lead attributing it to its own dispatch error.
- **Gates green at `ae2443d`:** `run-unit-tests.sh` exit 0, `check-docs.sh` exit 0,
  `check-state.sh` zero violations.
