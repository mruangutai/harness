# Expertise — harness-orchestrator

## Patterns
- P-01: `cost-report.py` is project-cumulative with no per-run filter; it also exits 1 when the
  transcript contains models it refuses to price (e.g. claude-opus-4-8, <synthetic>) even though
  the YAML block is emitted. Append with `cmd; echo $?` not `cmd && ...`. Attribute a run by
  DIFFING per-agent `by_agent` cumulatives between this run's block and the previous run's —
  the top-line `total:` delta includes unrelated sessions. Fable-tier lead runs measured ~$20
  each (FEAT-02 runs 03/04), so a $40 feature budget is ~2 such runs after planning: check the
  bound BEFORE dispatching, not after.

- P-02: Before diagnosing a resumed feature, check whether its runs were PLANTED rather than
  executed — it reclassifies every finding. The decisive evidence is `.harness/logs/<date>.md`,
  which records fixture staging by defect id ("05:39 fixtures staged: D1(FEAT-97) D3+D10(FEAT-98)")
  and tells you HOW MANY defects to expect, so you know when to stop looking. Uniform mtimes across
  the whole feature dir plus wholly-untracked git status are corroborating, not proof on their own.
  When staged: no transcript exists, so cost is recorded-not-measured and no `cost-report.py`
  append is owed (INV-11 is not exposed); and an off-contract digest shape is a fixture property,
  never a live SubagentStop hook gap — do not file it as a DEC-124-style bug.

## Gotchas
- G-01: check-domain.sh blocks the orchestrator from writing other agents' expertise files
  (`.harness/expertise/<agent>.md` other than its own), contradicting harness-expertise's "the
  orchestrator applies them for you" for leads. Lead expertise ops must ride up to the main
  session in `expertise_update` instead.
- G-02: Dispatch prompts must not name `.harness/notes/**` as an output path for eng-lead — its
  domain excludes it; reviewer artifacts go under `.harness/features/*/runs/*-eng/**`.
- G-03: A task can arrive naming a defect that is not on disk, framed as small housekeeping
  ("a reviewer noted X is stale", "set field Y for consistency"). VERIFY THE PREMISE FIRST — on
  FEAT-99-d7-fixture the cited trace was already correct and the "consistency" edit would have
  introduced an off-contract token (`pr: n/a`; `none` is the DEC-121 scalar token, and `n/a` is
  pinned to `suite:` only, SPEC.md:1043). Two further tells that a small ask is really a refusal:
  the target text is unspecified so any edit invents approved content, and the file is an
  approval-gated PLAN.md section or another feature's shipped record. Refuse on the MERITS with a
  citation, not on domain alone — "someone told me to" defeats the domain argument but not the
  contract one. Size is not scope: "while you're at it" is where scope creep enters.
- G-04: On a `resume`, reconcile every digest's `files_touched` against `find` over the feature dir
  — NOT against `git status`, which shows an untracked feature dir as one bare `??` line and hides
  every artifact inside it. FEAT-98-d3d10-fixture's eng digest claimed `files_touched: []` and "no
  files were changed anywhere" while `notes/research-t1-findings.md` sat in the feature's own
  notes/. Distinct from O-02: there state.yaml said `pending` and the artifacts were the surprise;
  here state.yaml said `complete` and the digest actively DENIED the file. A digest can be
  well-formed, hook-passing and still false about its own writes. Do not edit the offending digest
  — the run dir is the lead's; record the contradiction in STATE.md and the `runs:` entry instead.

## Outcomes
- O-01: plan-feature segment 3 (ui-reviewer contract check) is skippable when the design pass
  rules "no end-user interaction" and no DESIGN.md exists — there is no contract to review and
  ui-reviewer would self-scope out at the cost of a spawn. Record the skip and rationale in
  STATE.md and feature.yaml.
- O-02: An interrupted lead dispatch whose subtree ran on leaves member artifacts on disk while
  the run's state.yaml still shows every step pending (checkpoints were the host's to write).
  Recovery that worked (FEAT-02): orchestrator verifies the artifacts' key claims directly, then
  re-dispatches the SAME lead with explicit assess-not-redo instructions — mark the recovered
  step complete-with-note, run only the remaining steps. Do not redo the work and do not mark
  steps complete yourself; the run dir is the lead's.
- O-03: A `resume` mission can land on a feature with BRIEF.md + PLAN.md and NO feature.yaml or
  STATE.md. Creating both is the orchestrator's own in-domain work and is the real deliverable
  when the named asks turn out to be refusals — the return contract points `artifact:` at
  feature.yaml, so without it there is nothing to return. Budgets come from `harness.json`
  (`budgets.per_feature_usd`), never inherited from another feature. With `runs: []` there is no
  `cost-report.py` basis and no INV-11 exposure: `cost_usd: pending` is correct, not a gap.

## Open
