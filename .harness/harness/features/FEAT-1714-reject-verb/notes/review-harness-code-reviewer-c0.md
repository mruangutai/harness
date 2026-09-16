# Pinned code review — FEAT-1714 c0

## BLUF

FAIL over `origin/main...82bdef1a6f7cd89005f661a06296725f5b1ad9b1` (46 assigned paths). Stage 1 fails SC-03/T-02/T-05 because `gh-sync.py reject` reports remote mutation failures as success and can either record `rejected` after an incomplete disposition or invite the orchestrator to record it on the `none` path. Per protocol, Stage 2 was not opened after that spec failure. The independently required Python risk audit also returns `code_grade: fail` with three high records and two grade-2 records.

## Stage 1 — spec compliance: FAIL

All three BRIEF perspectives, SC-01..SC-05, D-01/D-02, T-01..T-05, the handoffs, signed answers, and every existing receipt were assessed against the pinned diff.

### F-01 — high · substance · T-02/T-05 · fail-open reject lifecycle

**Failure scenario:** GitHub accepts the parent close but rejects the comment, `superseded` label, or milestone close. `cmd_reject` prints an error but returns success; on the numeric path it still writes station `rejected`, and on the `none` path the orchestration contract interprets command success as permission to write `rejected`. The local record therefore claims a completed rejection while SC-03's required parent disposition is incomplete. A parent-close failure likewise returns exit 0; the `none` orchestration can then mark a still-open parent rejected.

**Evidence:** `.claude/skills/harness/bin/gh-sync.py:1869-1900` returns normally on close failure and treats comment/label/milestone failures as stderr-only before the numeric station write; `.claude/skills/harness/SKILL.md:58-67` says the `none` station write occurs only after the command succeeds; `plan.yaml:193,264` requires the complete disposition and the successful-path write; `tests/integration/test-gh-sync-abandon.py:648-697` covers only green reject mutations and has no rejection-failure case. This is the project's recurrent fail-open defect class.

**Required:** make reject expose mutation failure as failure and never permit either station writer until every required disposition mutation succeeds; add discriminating numeric and `none` failure cases.

### Spec violations

- `mismatch` — `.claude/skills/harness/bin/gh-sync.py`, SC-03 / T-02 / T-05: an incomplete GitHub disposition is reported as a successful reject.

## Stage 2 — code quality: NOT RUN

Stage 1 did not pass, so the conditional quality read was not performed. The mandatory mechanical Python grade was run independently and is recorded below; it is not a substitute for Stage 2.

## Code-risk audit: fail

- **F-02 — high · substance · T-01:** `.claude/skills/harness/bin/validate-digest.py:388`, `_reject_judgement_errors`: cyclomatic 22, cognitive 24, ABC 50.2, grade 1 (driver cyclomatic+ABC; production bar 4).
- **F-03 — high · substance · T-03:** `.claude/skills/harness/bin/worktree_terminal.py:383`, `_landed_station_record`: cyclomatic 8, cognitive 10, ABC 20.5, grade 3 (driver cognitive+ABC; production bar 4).
- **F-04 — high · substance · T-03:** `tests/integration/test-check-state-feat59.py:454`, `case_inv44`: cyclomatic 11, cognitive 9, ABC 74.4, grade 1 (driver ABC; test bar 3).
- **F-05 — med · substance · T-02:** `.claude/skills/harness/bin/gh-sync.py:1851`, `cmd_reject`: cyclomatic 11, cognitive 14, ABC 31.6, grade 2. Reason required: it owns one ordered lifecycle, but its many remote-failure branches obscure the station-write invariant; F-01 is the concrete resulting failure.
- **F-06 — med · substance · T-03:** `tests/integration/test-worktree-terminal.py:821`, `case_plan_station_is_the_landed_authority`: cyclomatic 8, cognitive 12, ABC 31.7, grade 2. Reason required: it is one authority scenario spanning several landed-station variants, but the combined setup/assertion shape exceeds the test bar.

## Assessed and dismissed

- **Shared vocabulary cutover:** dismissed. `TERMINAL_STATIONS = ("abandoned", "rejected")` is the sole terminal set and the old singular name is deleted; the inspected consumers use the shared tuple (`factory_config.py:24-28`; D-01/SC-05).
- **`superseded_by: none` performs no station write in `gh-sync.py`:** dismissed as intentional. T-02 assigns that sole write to the orchestrator after confirmed lifecycle success (`plan.yaml:193,264`).
- **INV-44 number collision:** dismissed. The pin consistently uses INV-44; INV-43 remains assigned to BUG-1723 (`check-state.py:2987`; signed answers).
- **TERMINAL_MARKER deletion:** dismissed as intentional clean cutover, not scope creep (D-01/T-03).
- **DEC-230/index drift:** dismissed. DEC-230 states six exhaustive kinds, reject semantics and INV-44, and the index points to the moved entry (`DECISIONS.md:7425-7449`; `DECISIONS-INDEX.md:217`).
- **Preload pressure:** dismissed as non-diff debt where applicable. Universal preload is represented as within its stated bound; harness-eng-lead's overage predates this feature per dispatch evidence.
- **Foreign/human commit:** dismissed. The full pinned commit walk contains no `[harness:human]` commit.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Reject lifecycle failures fail open, and the mandatory Python grade has three high records."
  severity_max: high
  findings:
    - { id: F-01, kind: substance, scope: task, severity: high, reader: code-reviewer, task: T-02/T-05, summary: "gh-sync reject reports incomplete GitHub disposition as success and can permit a rejected station write." }
    - { id: F-02, kind: substance, scope: task, severity: high, reader: code-reviewer, task: T-01, summary: "_reject_judgement_errors is production grade 1 (22/24/50.2; cyclomatic+ABC)." }
    - { id: F-03, kind: substance, scope: task, severity: high, reader: code-reviewer, task: T-03, summary: "_landed_station_record is production grade 3 (8/10/20.5; cognitive+ABC)." }
    - { id: F-04, kind: substance, scope: task, severity: high, reader: code-reviewer, task: T-03, summary: "case_inv44 is test grade 1 (11/9/74.4; ABC)." }
    - { id: F-05, kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-02, summary: "cmd_reject is grade 2; its branch shape obscures the station-write invariant." }
    - { id: F-06, kind: substance, scope: task, severity: med, reader: code-reviewer, task: T-03, summary: "case_plan_station_is_the_landed_authority is test grade 2." }
  must_fix:
    - "Fail reject when any required GitHub mutation fails and prevent both numeric and none station writes after incomplete disposition."
    - "Resolve the three high code-grade records."
  spec_violations:
    - { kind: mismatch, path: .claude/skills/harness/bin/gh-sync.py, ref: SC-03 }
  stage1: fail
  stage2: not_run_stage1_failed
  code_grade: fail
  reviewed: "origin/main...82bdef1a6f7cd89005f661a06296725f5b1ad9b1"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-c0.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1714-reject-verb/.harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-code-reviewer-c0.md
```
