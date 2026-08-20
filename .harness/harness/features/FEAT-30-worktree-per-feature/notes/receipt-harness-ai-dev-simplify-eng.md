# Altitude pass — FEAT-30 plan.yaml (harness-ai-dev, simplify)

**Verdict: PASS with 3 low-cost findings, all briefing-row/fold-in, none blocking.**

## The three assigned questions

**Q1 — Is the worktree-path derivation at the right home?**
`dest_for(owner_root, segment, id)` (T-01, plan.yaml:219-221) is NOT a second derivation of
`factory_config.workspace_path()` (`factory_config.py:334-339`). `workspace_path()` resolves
*which checkout* (owner_root) for a served repo, from `workspace_root` + repo name.
`dest_for()` resolves *where inside an already-resolved owner_root* a worktree lives — a
different, downstream concern, and T-01's own intent (plan.yaml:208-209) has it call
`workspace_path()` rather than re-deriving owner_root. Layered correctly, not duplicated.
**Leave.**

Residual found in passing: `dest_for()`'s join `os.path.join(owner_root, ".claude",
"worktrees", segment, id)` is a third hand-written site computing `owner_root +
WORKTREES_SEGMENT` — `harness_boundary.py:424` and `:446` already do this twice. The *string*
constant has one home (`WORKTREES_SEGMENT`, harness_boundary.py:33) and T-01 requires
`dest_for` to read it from there rather than respell it — but the join operation itself is
inlined three times now, matching existing house style (`harness_boundary.py:437` comment:
"One spelling, from the constant" — i.e. the constant, not the join, is the thing kept single).
Not a new pattern this plan introduces. **Briefing-row** — not worth a cycle; note for a future
pass if `WORKTREES_SEGMENT` ever gains a second path level, three join sites would need sync.

**Q2 — Is a rule stated in a task intent that belongs in one authority?**
T-09 (plan.yaml:997-1058) titles its intro "the same rule ... stated once each" then instructs
"Do not restate the mechanism in more than one of the three files" — read together as one
instruction they sound self-contradictory. In practice they are followable: the three numbered
sub-instructions (lines 1031-1054) assign each file a *different, non-overlapping* slice
(harness.md: invocation + branch source; orchestrator.md: addressing convention + HEAD-move
refusal; SKILL.md: full create/land/remove lifecycle + remove refusal) — no file is asked to
restate another's slice. The full path-shape formula (owner_root, WORKTREES_SEGMENT, segment,
id — lines 1025-1029) is stated once, in the plan intent itself, for the task author's benefit;
none of the three shipped files is required to spell out that formula verbatim. **The single
authority for the worktree path shape after this feature lands is code**: `dest_for()`
(feature-worktree.py) backed by `WORKTREES_SEGMENT` (harness_boundary.py:33) — not any of the
three instruction files, which reference the CLI/its output rather than restating the join.
**Briefing-row**: tighten the T-09 intro sentence (e.g. "one convention, split into three
complementary statements") so a future editor of these files doesn't read "the same rule ...
stated once each" as license to copy identical prose into all three.

**Q3 — Are the accepted residuals right to accept?**
- D-04 (plan.yaml:88-97): accepts main-session HEAD moves being unguarded; compensating control
  named explicitly — worktree isolation means a main-session branch change can no longer move
  the HEAD the orchestrator commits against. **Leave.**
- D-07 (plan.yaml:123-138): accepts bash-write-guard.sh staying fleet-unaware for worktree
  creation; compensating control named explicitly — `dest_for()` is the single destination
  constructor and "makes an illegal destination unrepresentable," so the door's blind spot has
  no reachable exploit path. **Leave.**
- D-08 (plan.yaml:139-161): accepts that the check-state.sh half of SC-09's baseline only
  catches VIOLATION lines whose text contains `FEAT-30` — verified against
  `check-state.sh:1366` (`for m in bad: print(f"  VIOLATION  {m}")`) that violation text is
  free-form and not guaranteed to name a feature id, so a code regression could in principle
  surface as an untagged VIOLATION. The compensating control is present but implicit rather
  than named as such: the suite half ("run-unit-tests.sh --kind unit and --kind integration ...
  zero FAIL/ERROR") is the hard zero that catches code-level regressions in
  `harness_boundary.py`/`check-domain.sh`, leaving the check-state half to catch only
  feature/process-state violations, which are the ones that do carry the feature id in practice.
  The two-half split is a reasoned design, not an oversight. **Leave** — the control exists, it
  is just not cross-referenced by name inside D-08's own text.

## One finding outside the three questions

`factory_config.py:334-339`, `workspace_path()`'s docstring: "This is the one place that
derivation exists — factory_workspace.py and factory_land.py both call it." T-01 adds a third
caller (feature-worktree.py, via `owner_root = factory_config.workspace_path(fleet, name)`,
plan.yaml:208-209) but T-01's file list (plan.yaml:173-175) does not touch factory_config.py, so
this caller-inventory comment goes stale the moment T-01 lands — an "authority becomes wrong
the moment a second caller arrives and nothing forces the update," matching this repo's own
Expertise gotcha (harness-ai-dev, P-02, project tier: "an inventory that is accurate only until
the second caller arrives stays wrong indefinitely"). One-line fix: append
`feature-worktree.py` to the sentence. **fold-in** — trivial, one line, directly caused by T-01;
recommend folding into T-01's intent/files rather than opening a new task or cycle.

## Scope discipline
No architecture review performed. No proposal to re-route T-03/T-04/T-05, no wording changes to
BRIEF.md requirements/criteria, no re-litigation of REQ-08/SC-08/vocabulary/open questions. All
three settled rulings respected.
