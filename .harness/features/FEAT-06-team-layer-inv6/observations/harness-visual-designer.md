# Observations — harness-visual-designer — FEAT-06-team-layer-inv6

> **Path note.** The dispatch named
> `.harness/features/FEAT-06-team-layer-inv6/notes/design-pass-visual-designer.md` as my artifact.
> `check-domain.sh` BLOCKED it: `team-config.yaml:104-110` grants me `DESIGN.md`,
> `notes/mockups/**`, `notes/prototypes/**`, my Expertise and this observations log — and nothing
> else under `notes/`. `DESIGN.md` is explicitly forbidden by the dispatch and would assert a
> contract that does not exist. So the ruling lives here, the only durable path that is mine.
> Raised as Q1 in my DIGEST — a routing gap, not a workaround.

---

# Design pass — FEAT-06 team layer and INV-6

**Ruling: `needs_prototype: false`. No design contract is created or changed (`contract: n/a`).**
Nothing in this feature is operated by a person. The ui-reviewer segment can be skipped.

## The change set, against the interaction test

Every `files:` entry in PLAN.md's nine tasks is one of: a YAML data file read by an agent
(`teams/review.yaml`, `teams/gate-probe.yaml`, new `teams/build.yaml`), a shell invariant
(`bin/check-state.sh`), a Python constant and its two consumers (`bin/harness_yaml.py`,
`bin/validate-digest.py`), gate tests and the runner (`bin/test-check-state.py`,
`bin/test-harness-yaml-corpus.py`, new `bin/test-team-catalog.py`, `bin/run-unit-tests.sh`),
agent-preloaded markdown (`harness/SKILL.md`, `harness-team/SKILL.md`), and one docs row
(`docs/harness/SPEC.md` §13). No screen, no control, no flow.

Pre-empting the obvious challenge: the repo does hold a rendered visual artifact,
`docs/harness/org.html` (21KB). **No task touches it** — T-08's `files:` block is
`docs/harness/SPEC.md` alone, and it is the only `docs/**` task in the plan.

## SC-13 (`verify: uat`) — tested, does not flip the ruling

SC-13 is *"the user reads the new `build.yaml` and agrees it describes a build the way they want
builds dispatched."*

1. **It is already routed to a different gate.** The `harness-uat` skill turns each `verify: uat`
   criterion into a hand-test script and blocks the ship decision on the user's result. SC-13 is
   gated, not orphaned; absorbing it into the prototype gate would double-gate one criterion.
2. **A prototype of `build.yaml` would be `build.yaml`.** The prototype gate exists where the built
   thing is expensive and the experience must be judged before it is paid for. Here the artifact is
   a short YAML file — final fidelity is the cheapest fidelity. There is nothing to stand in for.

So SC-13 is **ordinary artifact approval**, of the same kind as PLAN sign-off, not end-user
interaction in the sense the prototype gate means.

## `build.yaml` legibility — checked, no finding

D-03's `steps_from:` expansion rule is a new schema form whose only reader is a lead agent reading
it as prose (`harness-team/SKILL.md:9`). I judge agent-facing prose ergonomics to be engineering
legibility, not a design surface I own — but I checked it rather than declining. T-04 already
specifies a header comment block carrying the three things a reader needs: (a) eng-squad-only by
DEC-118, (b) it is an expansion rule and not a DAG, and why, (c) provenance and n. That is adequate.
**No finding.** Reported as checked so silence is not mistaken for omission.

## Why the ui-reviewer skip is safe, on evidence rather than opinion

- **Mode B** would self-scope out anyway. `.claude/skills/harness/teams/review.yaml`'s `ui` step
  prompt already reads: *"Self-scope out if the diff touches no user-facing surface: write a
  one-line note saying so and return PASS."* The pre-emptive skip and the runtime self-scope
  converge on the same result.
- **Mode A** (grade `DESIGN.md` before anything is built) is inapplicable: **no `DESIGN.md` exists
  anywhere in this repo** — verified, `docs/harness/` holds BUILD.md, DECISIONS.md,
  DECISIONS-INDEX.md, SPEC.md and `org.html` only, and no feature folder carries one. This feature
  creates none.

## Open questions

None on the ruling. The user can demand a prototype at the approval gate; that is the mechanism
working, not a question I raise. The only open item is the path/domain gap noted at the top.
