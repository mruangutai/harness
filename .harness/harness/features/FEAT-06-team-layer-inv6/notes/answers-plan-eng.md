# User answers — FEAT-06 plan gate, run `plan-eng` — 2026-08-04

Taken by the main session from the user directly. All four blocking questions answered, plus a
re-scope instruction that supersedes EQ-1.

## THE HEADLINE: EQ-1 is not an accept-or-widen choice. The feature is re-scoped.

**The user's instruction: STOP AND RE-PLAN AROUND THE UNOWNED QA GATE.**

While gating EQ-1 the main session verified something neither squad reported, and it changes what
this feature is about:

- `.claude/skills/harness/SKILL.md` — the orchestrator playbook, preloaded by
  `harness-orchestrator` (`.claude/agents/harness-orchestrator.md:8-12`) — contains **zero**
  occurrences of `qa` and **zero** of `test_matrix`. Verified by `grep -c -i`.
- `docs/harness/SPEC.md:1978` assigns the job anyway: qa sits in the ship sequence and
  "**the orchestrator sequences the squad segments**… qa gates (`test_matrix` hard gate) →
  `loop_back` → dev."
- SPEC is not preloaded by the orchestrator. So the obligation exists only where its owner never
  reads it.
- The gate has nonetheless run on all three shipped features — **because a lead added the step by
  hand each time**: FEAT-03 `feature.yaml:62` "panel + **added qa step**"; FEAT-04
  `feature.yaml:144` "ui step SKIPPED, **qa step ADDED** to cover the blocking gate"; FEAT-05
  `notes/qa-c0.md` + `qa-c1.md`.

**Consequence for the plan as written.** `build.yaml` covering 7 of 8 is now understood as
**correctly bounded, not a shortfall** — qa was never `build.yaml`'s job, because DEC-118 puts qa
in the validator squad and the orchestrator owns the cross-squad sequencing. Do NOT reword an SC to
apologize for 7-of-8, and do NOT widen `build.yaml` to reach qa. Both were the wrong repair.

**What to re-plan around instead.** The unowned qa gate is the more important defect and the user
wants the feature scoped around it. It is filed as **issue #24** with the evidence above. Its
relationship to the three tickets already in scope:

- **#8** (`review.yaml` omits the qa step) is the same hole from the team-file side. Adding the
  step to `review.yaml` fixes the panel path and does NOT fix ship sequencing, which is where SPEC
  assigns the job. #8 remains necessary and is no longer sufficient.
- `docs/harness/SPEC.md:1980`'s review row reads `{code ∥ qa ∥ security ∥ ui}` — qa **in the
  panel** — which the shipped `review.yaml` does not have. That is a **third** description of
  where qa runs. Three descriptions, no two agreeing. Reconciling them is now in scope.
- The through-line the grilling artifact named — "a definition or check that appears to exist but
  does nothing" — now has a fifth instance, and it is the one guarding the only blocking gate.

pm re-scopes; the budget question comes back to the user if the re-scope needs more than $120.

## The other three, answered

### Q8 — `steps_from:` KEPT (the rule, not a literal list)

The user chose the expansion rule. Reasoning given back to them in plain terms and accepted: a
literal `steps:` list is wrong the moment a feature's task set differs, so it gets rewritten every
feature — which is the hand-written list of issue #9 wearing a filename.

**Therefore EMF-1, EMF-2 and EMF-3 are LIVE and must be fixed** — they are defects inside a schema
form that now definitely exists. They were only ever moot on the other branch.

**T-09 stays load-bearing.** Without teaching `harness-team/SKILL.md` the expansion form,
`build.yaml` is prose only (PLAN D-03's own note at `PLAN.md:66-70`).

### Q5 — pm's DEC-174 carve-out extension KEPT; the three `bin/` test files are main-session-direct

`bin/test-check-state.py`, `bin/run-unit-tests.sh` and the new `bin/test-team-catalog.py` are
**not** routed to backend-dev, despite backend-dev holding `bin/**`.

Reason the user accepted: a test *for* `check-state.sh` is part of what makes that gate green, and
the carve-out exists because green gates cannot vouch for the code that produces them — which is
verbatim the 2026-08-03 failure (four gates green while four `.harness` YAML files did not parse
and the validator rejected its own normative template).

Cost accepted: more of the build sits in main-session context with no lead assessing it.

### Q3 — `gate-probe.yaml` DELETED, not quoted

The main session verified before asking: `gate-probe`'s only references outside its own file are
`docs/harness/DECISIONS.md:2307-2325`, which record it as the historical proof of loop-back
semantics. Nothing executes it. Deleting orphans no live consumer and the decision record keeps
the story.

**Consequences pm must carry:** pm's D-02 is overridden. T-03 drops. The widened YAML-validity
gate (T-05) then covers **2** files, not 3 — and its success criterion must be reworded to match,
or it asserts a count that cannot be met.

## Q10 — acknowledged, not actioned here

The domain routing wall at six recurrences is a harness-level problem and correctly not this
feature's business. It is already filed as **issue #20** with the FEAT-03/04/05 evidence, and the
two new instances found this feature (visual-designer has no legal path for a design ruling;
PLAN Q4) should be added there rather than absorbed into FEAT-06.

## Also filed while this gate was open — not FEAT-06 work

Issues **#18–#23** from the 2026-08-04 performance review
(`.harness/notes/perf-review-agent-workflow-2026-08-04.md`). Two touch this feature's surfaces and
pm should read them before re-planning, but neither is in scope:

- **#19** — every PLAN task declares a `verify:` command and no agent ever runs it. FEAT-06's own
  PLAN carries `verify:` lines that nothing will execute.
- **#21** — qa phase 1 needs no source access yet is sequenced after the whole build. Moot while
  nothing schedules qa at all (#24), which is why #24 comes first.

Note for pm on #19: the user was told the `verify:` gap exists. Do not re-derive it.
