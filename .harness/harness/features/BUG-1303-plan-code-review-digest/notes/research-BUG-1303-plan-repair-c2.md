# Plan repair, cycle 2 — BUG-1303 panel findings closed

**BLUF: all eight dispositions applied; the HIGH finding is closed by fixing, not accepting.**
T-01's per-persona grading is now a pure helper taking roster, source map, required-field map and a
source reader as ARGUMENTS, and a synthetic-registry case (T-01 step 7b) reddens each of its four
defensive branches inside one suite run. Case (6) is gone, T-01's steps renumber 1-8 contiguously,
T-02 now edits the canonical `.omp` source and regenerates, and SC-08 is graded by the existing
`sync-agent-adapters.py --check` gate rather than by a third copy of it. `approval.status` stays
`pending`. Files touched: `plan.yaml` (via `plan-merge.py` verbs only), `BRIEF.md`, this note.

## Acceptance evidence

`python3 -c "import yaml,sys;yaml.safe_load(...)" plan.yaml` → `YAML OK approval= {'status': 'pending'}`.

`python3 .claude/skills/harness/bin/check-plan-routes.py plan.yaml`:

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
DEVIATION T-01 tests/integration/test-validate-digest.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-02: declared main-session-direct (.claude/agents/harness-code-reviewer.md, .omp/agents/harness-code-reviewer.md ungranted)
OK T-03: declared main-session-direct (.claude/skills/harness-code-review/SKILL.md ungranted)
OK T-04 granted to harness-documentor
0 violation(s) across 1 plan(s)
```

The `DEVIATION` line is the expected DEC-174 carve-out; only `VIOLATION` gates, and there are none.

Verify/intent literal identity checked mechanically: both ok-line literals T-01's `verify:` greps
occur character-identically in T-01's own `intent:`, and neither `verify:` nor `intent:` still
mentions `[reviewer persona copies]`.

## Demonstrated failing directions — every new or changed T-01 assertion

1. Unmapped persona (step 4, branch 1) — synthetic roster persona absent from the synthetic map
   yields a failure line naming that persona (step 7b, assertion 1).
2. Mapped source absent from disk (step 4) — synthetic `read_source` returning `None` yields a
   failure line naming that path (step 7b, assertion 2).
3. Documented block not locatable (step 4, new under A-3) — synthetic source with no locatable block
   yields a failure line naming that path (step 7b, assertion 3).
4. Block-scoped gap detection (steps 1+2, new under A-3) — synthetic source carrying the required
   field only in prose ABOVE its block is reported as a gap, which whole-file search would have
   passed (step 7b, assertion 4).
5. Fully-mapped control (step 4) — reports no failure at all (step 7b, assertion 5); without it the
   four above could pass by always failing.
6. Composite `reviewed: ` + `_PLAN_REVIEW_PREFIX` (step 6) — red at the end of T-01 for all three
   contract sources, green only once T-02/T-03 land.
7. Field-paired `code_grade:` line carrying `n_a` (step 6) — red at the end of T-01 for all three
   sources; the bare form was vacuous for `SKILL.md` today, the paired form is not.
8. Artifact-path fragment `features/<FEAT>/notes/review-harness-code-reviewer-` (step 6, new under
   A-2) — red at the end of T-01 for both agent copies, green after T-02.

Items 6-8's red state is real, observed in T-01's own run, and T-01's receipt must quote it.

## Per-finding disposition

- **S-1 (HIGH), fixed.** T-01 step 4 is now `documented_contract_results(roster, sources,
  required_by_persona, read_source)` — pure, no module globals; step 5 does the real wiring with
  `sorted(validator.ALIAS)` and `CONTRACT_SOURCES`, so the derivation rule is unchanged. Step 7b is
  the synthetic-registry case; its ok literal is
  `ok    [documented contract completeness] unmapped persona, absent source, unlocatable block and out-of-block field each reported by name`,
  greped verbatim by T-01's `verify:`. SC-05 in `BRIEF.md` now requires the demonstration.
- **A-1 (med), duplicate dropped.** Case (6) deleted; steps renumbered 1-8. T-01's `verify:` now
  greps the two synthetic ok lines of step 7. SC-08 re-declared `verify: inspection`, evidence named:
  T-02's `verify:` (`--check` rc 0 plus the body-compare) and the standing `check-omp-port.py:156-166`
  wiring.
- **Q2 / T-02 workflow (med), respecified.** T-02 makes all four edits in
  `.omp/agents/harness-code-reviewer.md` then runs `sync-agent-adapters.py --apply`; both paths stay
  in `files:`; `verify:` leads with `--check` and keeps all content greps against both copies plus
  the body-compare. `lanes:` untouched. Recorded as **D-07**.
- **A-2 (med), applied.** Artifact-fragment assertion added to T-01 step 6 for the two agent copies,
  with its failing direction named (a source lacking the fragment reddens by name). SC-03 widened.
- **S-2 + A-4 (med/info), one edit.** T-01 step 6 asserts the composite `reviewed: ` +
  `_PLAN_REVIEW_PREFIX` and a line whose first token is `code_grade:` carrying `n_a` — both tokens
  still taken from the validator module. SC-03 now claims the composite. T-03's intent was amended
  minimally to require the literal `code_grade: n_a`, without which the composite could not go green.
- **A-3 (low), scoped; premise settled.** `documented_contract_gaps` now grades only the documented
  block, located by `documented_block(source_text, source_path)` (fenced `DIGEST:` block for a shared
  SKILL, `## Output` section for an agent file); an unlocatable block is a named failure.
  **Premise, restated as measured** at HEAD `c369fb1f` in this worktree: no required field name occurs
  outside the digest block in either shared SKILL — `harness-digest-dev/SKILL.md` matches only at
  lines 18-27, `harness-team/SKILL.md` only at lines 240-253, all inside the single fenced block. The
  defect is latent, not live; scoped anyway, because whole-file search is the wrong shape either way.
- **S-3 (low), transcribed.** `T-04 depends_on: [T-01]`, with the record-integrity reason written into
  T-04's intent: the entry's claim "checked mechanically by tests/integration/test-validate-digest.py"
  is true only once T-01 lands.

## Independent check I ran (not required, load-bearing)

Block scoping could have created reds nobody planned for. I ran the block extractor plus the gap check
over all 16 registry personas at HEAD: the only gap is `code_grade` for `harness-code-reviewer` in both
agent copies, every documented block is locatable, and block-scoped results equal whole-file results
everywhere. So T-01's expected-red list — reviewer `code_grade` ×2 plus step 6's plan-mode assertions —
is still exactly right after the A-3 change.

## Open questions

None. `approval.status` stays `pending`; the plan is the operator's to sign.
