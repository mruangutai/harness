# Plan-panel review — BUG-1303, cycle 1 (scope reader)

**BLUF: PASS with notes.** Traceability is clean (no orphan REQ/SC, no dangling `traces:`, the
`depends_on:` chain T-01→T-02→T-03 is a real data dependency, not theatre), and every literal string
in T-01/T-02/T-03's `intent:`/`verify:` blocks is grounded against the actual worktree source
(`validate-digest.py`, the current persona files, `SKILL.md`, `gen-decisions-index.py`) — I checked
each one directly rather than trusting the plan's own citations. No task serves a dead requirement,
and the four cycle-0 goal-check gaps are genuinely closed in this draft. Two findings on the new
guard's *own* test design; neither blocks this feature's own delivery, but one bears directly on the
guarantee REQ-04 exists to make.

## Findings

- **`plan.yaml:124-134` (T-01 step 3) vs `BRIEF.md:44-46` (REQ-04) / `BRIEF.md:82-88` (SC-05).**
  Severity: **high.** The two defensive branches that make REQ-04's completeness guarantee true —
  "print a FAIL when a registry persona has no `CONTRACT_SOURCES` entry" and "print a FAIL when a
  mapped source path is absent from disk" — are never exercised by any case the plan specifies. Step
  (5) tests `documented_contract_gaps` against synthetic `PRE_FIX_REVIEWER_BLOCK` text precisely so
  the field-gap logic is proven, not just written; step (3) has no analogous synthetic-registry or
  synthetic-CONTRACT_SOURCES case for the completeness branch, and today's real registry maps all 16
  personas, so the branch has zero live executions either. Concretely: an implementation bug in that
  branch (a stray `continue` instead of `fails += 1` + `print`, or a swallowed exception) ships
  invisibly — `tests/integration/test-validate-digest.py` still reports `ALL PASSED.` because nothing
  in this feature's own build ever calls the branch. It resurfaces only when a real 17th persona is
  added in some future feature, at which point REQ-04's exact promised behaviour ("reads as a named
  failure rather than a smaller passing count") may silently not hold — which is the identical
  "zero-discovered → zero-fails → indistinguishable-from-health" class the file's own
  `run_reviewer_severity_enum_cases` docstring (`tests/integration/test-validate-digest.py:204-218`)
  records having to fix once already (c22 send-back), and which T-01's intent explicitly tells the
  executor to model this guard after ("reuse its shape, its mechanical-discovery discipline"). The
  discipline itself — proving the zero/completeness case, not just asserting the happy path — is
  invoked in prose but not spelled out as one of T-01's seven numbered steps, so a literal execution
  of steps (1)-(7) can satisfy the text while leaving this specific guarantee unverified.

- **`plan.yaml:141-148` (T-01 step 4) vs `BRIEF.md:66-70` (SC-03).** Severity: **med.** The DEC-207
  token check for `.claude/skills/harness-code-review/SKILL.md` requires two substrings present
  anywhere in the file: `validator._PLAN_REVIEW_PREFIX` (`"plan:"`) and the `n_a` member of
  `CODE_GRADE_VALUES`. Measured directly against the current worktree file: `SKILL.md` already
  contains the literal substring `n_a` today, at `SKILL.md:112-113`, in the pre-existing "enum is an
  audit claim" passage — unrelated to the plan-phase section T-03 is about to add. So half of this
  assertion is vacuously true before T-03 lands and provides no evidence T-03's actual new content
  exists; all of the check's real discriminating power for this file comes from the `"plan:"` half.
  Concrete failure scenario: a later edit that strips T-03's new "Before there is a SHA" paragraph
  (including its own `code_grade: n_a` example) while leaving `SKILL.md:112-113` and some remnant of
  the `reviewed: plan:` line intact would still read `ok` from this case — a silent regression of the
  exact documentation SC-03 claims is "asserted to document them" individually per source.

- **`plan.yaml:322` (`T-04 depends_on: [T-03]`).** Severity: **low.** T-04 edits only
  `.harness/harness/docs/DECISIONS.md` / `DECISIONS-INDEX.md` and consumes no artifact T-01–T-03
  produce (unlike T-02→T-03, whose whole-suite verify genuinely needs T-02's fix landed first). The
  dependency reads as sequencing rather than a data dependency; harmless, but it serialises a
  docs-only, different-lane task behind three main-session-direct tasks with no stated reason. Not
  gating — flagging only because the assignment asked whether each link in the chain is real.

## What I checked and found clean

- **Traceability** (Stage 1, q1-3): REQ-01→T-02,T-03; REQ-02→T-01,T-02; REQ-03→T-03; REQ-04→T-01;
  REQ-05→T-04. No orphan REQ, no dangling `traces:`. SC→task mapping matches cycle-0's goal-check
  table and is unchanged by the repair except where the repair explicitly widened it (SC-04/06 now
  `verify: inspection` with named evidence; SC-05 rewritten to require registry derivation).
- **`CONTRACT_SOURCES` roster completeness**: read `ALIAS` directly (`validate-digest.py:238-248`) —
  exactly 16 keys, and the plan's 9+4+3 enumeration (`plan.yaml:97-101`) covers all 16 by name. No
  persona is silently dropped from the map as currently specified.
- **Schema-extension claim** (T-01 step 3, "for harness-code-reviewer add `code_grade` and
  `reviewed`"): confirmed against `validate-digest.py:1140-1147` — the extension fires only for the
  literal `raw_persona == "harness-code-reviewer"`, not for `harness-security-reviewer`/
  `harness-ui-reviewer` (both alias to `"reviewer"` too), exactly as the plan states.
  `SCHEMAS["reviewer"]` (`validate-digest.py:196`) supplies the base `severity_max`/`findings`/
  `must_fix` requirement independent of this feature.
  `.claude/skills/harness-digest-dev/SKILL.md` and `.claude/skills/harness-team/SKILL.md` were
  spot-checked and already document every field their respective `SCHEMAS["dev"]`/`SCHEMAS["lead"]`
  require, so T-01's guard will not go red on unrelated personas once T-02/T-03 land.
  `gen-decisions-index.py`'s row grammar (`ROW_RE`, "`:: <ruling>`") matches what T-04 instructs
  writing by hand.
- **Verify-string literal fragments**: every `grep -qF` target in T-02/T-03's `verify:` is a
  character-for-character substring of what that task's own `intent:` instructs writing (the
  `code_grade:` line, the `reviewed: plan:` line, the `features/<FEAT>/notes/review-harness-code-
  reviewer-` fragment, `DEC-207`) — checked side by side, not assumed.
  `.claude/agents/harness-code-reviewer.md` and its `.omp` twin are confirmed byte-identical from the
  `# Harness: Code Reviewer` heading onward *today*, so T-02's python body-compare check is
  well-formed from the start.
- **Predecessor-state consistency**: T-01's verify intentionally checks only the two ever-green ok
  lines (5)/(6) while the rest of the suite is red by design; T-03's whole-suite verify only needs to
  be green after both T-01 and T-02 land, which the dependency chain guarantees. No verify asserts
  content a predecessor deletes.

## Open questions

None blocking. The two `med`/`high` findings are about the new guard's own coverage of its rarer
branches, not about whether this feature's stated SCs will pass at build time — they will, under the
plan as specified. Whether to widen T-01's `intent:` to add a synthetic-registry case for the
completeness branch (mirrors step (5)'s treatment of `documented_contract_gaps`) is the operator's or
pm's call at signature, not mine to decide.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Plan traces cleanly and every literal claim checks out against the worktree; the new guard's completeness/absent-from-disk branches (REQ-04/SC-05) and one SKILL.md token check (SC-03) ship untested against their own future-regression case."
  code_grade: n_a
  findings: 3
  finding_details:
    - summary: "T-01's persona-completeness and source-missing-from-disk branches (REQ-04/SC-05's own guarantee) have no synthetic test case and zero live executions given today's fully-mapped 16-persona registry."
      severity: high
      consequence: "A bug in either branch (e.g. a swallowed FAIL) ships invisibly now and only surfaces when a real 17th persona is added later, exactly when REQ-04's promise is needed."
    - summary: "T-01 step 4's DEC-207 token check for SKILL.md tests 'n_a' as a bare substring, which SKILL.md already contains today (SKILL.md:112-113) unrelated to the plan-phase content T-03 adds."
      severity: med
      consequence: "A later edit that strips T-03's new plan-phase paragraph while leaving the unrelated pre-existing 'n_a' text and some remnant of 'reviewed: plan:' intact would still read ok, silently regressing SC-03's per-source documentation claim for this file."
    - summary: "T-04 depends_on: [T-03] but consumes no artifact T-01-T-03 produce; looks like sequencing, not a real data dependency."
      severity: low
      consequence: "Harmless serialisation of a docs-only, different-lane task behind three unrelated main-session-direct tasks; extends the critical path with no stated benefit."
  must_fix: []
  spec_violations: []
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-code-reviewer-planpanel-c1.md
```
