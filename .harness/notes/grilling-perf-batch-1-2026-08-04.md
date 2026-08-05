# Grilling — performance levers, batch 1 (issues #18, #19, #22) — 2026-08-04

## Destination

Three rule-surface changes land, from `.harness/notes/perf-review-agent-workflow-2026-08-04.md`
rows 1, 2 and 5. Reaching the end looks like: a dev cannot return `PASS` without running its
task's declared `verify:`; the user's change requests at the signature gate go out as one
consolidated fix rather than one dispatch per request; and a bounded runtime-environment question
is probed before any claim about it is relayed to the user. Zero quality degradation is the
binding constraint — the user's ruling, not an inference.

## Settled

- **#19 — teeth: prose, or an enforced field?** → **Enforced digest field.** Add
  `task_verify: pass|fail|n/a` to the dev return schema in the canonical
  `harness-digest-dev/SKILL.md` (DEC-126) **and** to `validate-digest.py`. Prose alone is the
  "relied on being pointed at" pattern DEC-125 names, and it is what left `verify:` unrun across
  five features.
- **#19 — how the dev obtains the command?** → **Both.** The lead's dispatch prompt carries the
  task id **and** the `verify:` command verbatim (the DEC-158 pattern, where the dispatch quotes
  what the member is not preloaded with); the dev cross-checks against `PLAN.md`, which it can
  read, and returns `BLOCKED` on mismatch between dispatch and PLAN.
- **#19 — what does `task_verify: fail` mean?** → **`fail` (or `n/a`) alongside `VERDICT: PASS`
  is rejected by the validator**, exactly mirroring `suite` under DEC-173. The dev fixes until the
  verify passes, or returns `FAIL` / `BLOCKED` honestly.
- **#19 — does dev-ops inherit `suite`'s `n/a` + `PASS` carve-out
  (`validate-digest.py:66`)?** → **No.** `suite` is about tests, which dev-ops work genuinely
  lacks; `verify:` is a command PLAN mandates on **every** task with no placeholders. For
  `task_verify`, `n/a` means refused-or-blocked only, for all five specialists.
- **#18 — which surface batches the rulings?** → **The main session's signature gate**
  (`.claude/commands/harness.md` §2), NOT the orchestrator playbook as the issue proposed. On
  presenting BRIEF/PLAN, all of the user's change requests are collected in one review pass and
  dispatched as exactly one consolidated fix. The user accepted the cost: reviewing to exhaustion
  before the first fix goes out.
- **#22 — where does the probe-don't-infer rule live?** → **`.claude/commands/harness.md` and
  `harness/SKILL.md` only** — the two tiers that relay claims to the user and the two that
  over-claimed. Explicitly NOT `harness-handoff`, whose lines are paid by all 16 agents at every
  spawn; perf-doc row 9 is separately trying to shrink that preload.
- **Build shape** → **mixed, and PLAN must declare the split up front** (FEAT-06's shape), not
  discover it mid-build. `docs/**` is member-executable by `harness-documentor`
  (`team-config.yaml:116`) and `.claude/skills/harness/bin/**` by backend-dev (`:155`) or dev-ops
  (`:197`). Only `.claude/skills/harness-*/SKILL.md`, `.claude/skills/harness/SKILL.md`,
  `.claude/commands/harness.md` and `.claude/agents/*.md` have no owner and become declared
  main-session steps. Asserting "direct end to end" would be the inverse of the routing wall —
  planning main-session steps for work a member owns.

## Not yet specified

- Whether the batched-fix rule at the signature gate needs any recorded escape for a change request
  that is genuinely urgent and independent of the rest of the review. Nobody has hit that case yet,
  so the shape of the escape cannot be stated sharply.

## Out of scope

- **#20** (routing wall — plan-time route resolution) and **#21** (qa phase 1 concurrent with the
  build): the user's scoping ruling. #21 additionally collides with open issues #40, #41 and #42,
  which contest qa's write permissions and the review panel's membership.
- **Perf-doc row 10** (count and budget runs, not just cycles): not a filed ticket. Consequence
  accepted and recorded here — after this feature there is still no instrumented way to say which
  lever paid.
- Row 5's sourcing slip in the perf doc (below). Left as-is by the user's ruling.

## Facts I verified (so pm does not re-derive them)

All at `3bfedc9`.

- **`verify:` reaches no executor.** It appears in exactly two places outside the perf doc:
  `.claude/skills/harness/templates/PLAN.md:33` and `:47`. `grep -n verify` over
  `.claude/agents/harness-eng-lead.md` and
  `.claude/skills/harness-zero-micro-management/SKILL.md` returns nothing — the lead is never told
  to pass it down.
- **The dev digest schema is enforced in code**, so #19 cannot be done in prose alone:
  `.claude/skills/harness/bin/validate-digest.py:81` — `"dev": {"tests_added": int, "suite":
  {"pass","fail"}, "blocked_on": str}` — with `GATE_FIELDS` at `:73` and the dev-ops carve-out
  documented at `:66`.
- **Devs hold repo-wide read**, so the PLAN cross-check is available to them:
  `.harness/team-config.yaml:147,161,174,187,202` each carry `{ path: ".", read: true }`.
- **Route resolution, done here so the build does not discover it.** `team-config.yaml` grants
  `docs/**` to `harness-documentor` (`:116`) and `.claude/skills/harness/bin/**` to backend-dev
  (`:155`) and dev-ops (`:197`). Nothing grants `.claude/skills/harness-*/SKILL.md`,
  `.claude/skills/harness/SKILL.md`, `.claude/commands/harness.md`, or `.claude/agents/*.md` —
  those are the main-session steps.
- **`task_verify` has three propagation sites beyond the two canonical files**, found by
  `grep -rn -e tests_added -e blocked_on docs/ .claude/`. The doc checker cannot catch these — it
  is literal-superseded-string class with DECISIONS.md as its registry (DEC-104), which is exactly
  how perf-doc row 11 (`SPEC.md:1980` vs `review.yaml`) got through. Each needs a PLAN task:
  - `docs/harness/SPEC.md:1054-1055` — restates the eng-dev digest fields. → documentor
  - `.claude/skills/harness/bin/test-validate-digest.py` — seven dev-digest fixtures at `:191`,
    `:294`, `:562`, `:586`, `:721`, `:943`, each of which gains a required field. → backend-dev
    or dev-ops
  - `.claude/skills/harness-tdd-enforcement/SKILL.md:70-72` — a refusal-shaped dev digest.
    → main session
- **The validator already has a registered test**, so DEC-174's "tests run explicitly" is
  satisfiable: `.claude/skills/harness/bin/test-validate-digest.py` exists and is first in
  `run-unit-tests.sh:6`'s `SCRIPTS` list. A new gated field with no new test case would be the
  2026-08-03 shape — four green gates over a validator that rejected its own template — so the
  test case is part of the task, not optional. Run the suite from the repo root; issue #36 makes
  it abort from anywhere else.
- **Three DECISIONS entries are implied** — the gated `task_verify` field, the signature-gate
  batching rule, and the probe rule — each with its `DECISIONS-INDEX.md` row written in the same
  commit (`DECISIONS-INDEX.md:14`).
- **Only #19 admits a mechanical success criterion.** #18 and #22 are prose rules on the main
  session and orchestrator surfaces; their SCs are `verify: inspection` (the rule is present and
  says X). Neither can be shown to have changed behavior until the next feature runs.
- **`validate-digest.py` is inside the DEC-174 carve-out**, so the #19 schema edit is made
  directly with its tests run explicitly and a human reading the diff — never dispatched through a
  team run. This is consistent with the build shape above, not an exception to it.
- **#18's own proposed surface is contradicted by the record it cites.** The FEAT-03 rulings were
  not answers to the orchestrator's questions; they were new change requests raised while reading
  BRIEF/PLAN for signature — `.harness/logs/2026-07-31.md:4` ("User NOT ready to sign") and `:5`
  ("User approved; still not signing"). The orchestrator never held a partially-answered question
  set. Cost: seven serialized runs, ~$95, ~5h wall clock (`:2` 10:15 → `:6` 15:08).
- **The over-claim in #22's evidence was the main session's own.**
  `.harness/logs/2026-08-03.md:14` reads "CORRECTED MY OWN EARLIER OVER-CLAIM to the user".
  Note for pm: the perf doc's row 5 cites `:17` as retracting the orchestrator's identical
  over-claim; read at `3bfedc9`, `:17` records the DEC-174 user ruling instead. The finding stands;
  only that one citation is loose. Left uncorrected by the user's scoping ruling.
- **`bin/check-state.sh` exits 0** at `3bfedc9` — the only output is the known `note` class from
  issue #23 (pruned FEAT-05 run dirs) plus one FEAT-06 pruned run dir.
