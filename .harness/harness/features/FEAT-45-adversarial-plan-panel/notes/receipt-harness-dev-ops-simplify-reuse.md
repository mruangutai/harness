# REUSE angle — FEAT-45 plan surface — receipt

**BLUF: empty return.** Checked all four seeded candidates plus every `verify:` block and the
T-08/T-10 fixture-reuse claims; the plan reuses what the tree already has in every case examined.
No finding meets the "concrete cost" bar (part 4 of the finding format). Read-only throughout;
plan.yaml, BRIEF.md and everything under `.claude/` are unmodified (verified below).

## The four seeded candidates

1. **T-02 vs `review.yaml` (`.claude/skills/harness/teams/review.yaml`).** T-02's intent (plan.yaml:278-336)
   explicitly instructs "read review.yaml first and match its key vocabulary and comment discipline
   exactly," and the step vocabulary it lists — `id, persona, depends_on, inputs, outputs,
   mutates_repo, prompt, on_fail, max_cycles, then, feed` — is exactly `review.yaml`'s and
   `build.yaml`'s own vocabulary (`build.yaml:72-89`), not a divergent spelling. No drift found.

2. **`on_fail`/`loop_back`/`max_cycles`/`then:`/`feed:` restated by D-11 and T-02.** This is
   configuration, not re-implementation, and the plan is not inventing that framing itself:
   `build.yaml:86-89` already carries the identical self-aware comment — *"Restates eng-lead's
   existing build fix-loop rule; it does not invent a new one"* — for the same runner contract
   (`harness-team/SKILL.md` §3f, "Apply `on_fail`," lines 145-165). D-11 and T-02 do the same thing
   build.yaml already does correctly. No finding.

3. **T-06 vs `harness-validator-lead.md`'s existing gate.** The lead already computes
   `must_fix`/`severity_max` and gates at `severity_max >= high` (`.omp/agents/harness-validator-lead.md:90`).
   T-06's intent (plan.yaml:521-556) adds only the transcription/identity contract (SHAPE vs
   CONTENT, unrated-as-high) and never touches or restates the gate threshold itself. This is the
   REQ-06 case the BRIEF frames as "existing mechanism reaching the signature" — agreement, not
   duplication. No finding.

4. **T-09's `panel_findings.py` sha256 helper.** Grepped `.claude/skills/harness/bin/` for
   `sha256|hashlib|content.hash|finding_id`: the only hit is `test-factory-decompose.py:14,904`,
   a directory-tree-diff file-hasher for an unrelated purpose (detecting incidental file changes
   during a decompose run), not an id/identity helper. `observations-merge.py:91-98` has a
   `normalize()` used for markdown-record dedup (whitespace-collapse only, no lowercasing, no
   hashing) — same idiom, different domain and different behavior (case-sensitive), not a
   candidate for reuse by a content-hash identity function. **No existing id/hash helper exists.**
   T-09 is the real answer: build it.

## `verify:` blocks — no hand-rolled re-checks of an existing gate

Read every task's `verify:` against `check-state.sh`, `check-plan-routes.py`, `check-domain.sh
--resolve`, `run-unit-tests.sh`, `gen-decisions-index.py`, `sync-agent-adapters.py`,
`test-team-catalog.py`. Each verify block calls the existing script it needs rather than
re-implementing its check:
- T-01 runs `gen-decisions-index.py` + its own test, greps only the prose it authored.
- T-02/T-03 pipe through `check-domain.sh --resolve` for routing, exactly the tool's purpose.
- T-03 also runs the pre-existing `test-orchestrator-playbook.py`.
- T-06 runs `sync-agent-adapters.py` + `test-sync-agent-adapters.py`, diffs the generated file.
- T-07 calls `check-plan-routes.py`'s own `live_invariant_numbers()` (confirmed at
  `check-plan-routes.py:658`) instead of re-scanning `check-state.sh` for invariant numbers by hand.
- T-08/T-09/T-10 run the test files they add cases to, plus `run-unit-tests.sh --kind unit`.

None of these re-greps what a registered gate already asserts. No finding.

## T-08 / T-10 fixture-reuse claims — verified, not just asserted

- **T-08** ("use the fixture helpers that file already has... do not build a second fixture
  mechanism") is grounded: `test-check-state.py` already has `make_fixture`/`_root_env`
  (lines 47-86), a ready-made approved-`plan.yaml` fixture (`PLAN_YAML_OK`, lines 789-806) built
  and consumed exactly this way by `case_q` (lines 809-861), and the exact marker-bracketed-mutant
  idiom T-08 is told to "follow exactly" already exists twice (`case_t14_red`/`T14_MARKER`,
  lines 2080-2134; `case_t10_red`/`T10_MARKER`, lines 2215-2269). The helpers exist and are
  directly reusable for panel/rulings fixtures.
- **T-10** ("read `test-team-catalog.py` first and match its shape exactly") is grounded: that
  file's `check(name, ok, detail)` helper, `REPO` resolution from `HARNESS_PROJECT_DIR`/
  `CLAUDE_PROJECT_DIR` falling back to cwd, and counted-not-frozen `ran`/`fails` totals
  (`test-team-catalog.py:41-61`) are exactly the shape described and directly copyable.

Both reuse instructions are accurate, not aspirational. No finding.

## Verification that the domain guard held

```
$ git status --porcelain
 M .harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json
```
Only `feature.json` shows as modified (pre-existing state from run bookkeeping, not touched by
this review). `plan.yaml`, `BRIEF.md`, and every path under `.claude/` are unmodified — confirmed
by `git diff --stat HEAD` carrying no entry for any of them.
