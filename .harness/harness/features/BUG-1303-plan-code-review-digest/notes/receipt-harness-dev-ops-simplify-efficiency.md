# EFFICIENCY — BUG-1303 (`63404ef0..b724a0f4`)

**BLUF: nothing-found.** The new `run_documented_contract_cases` section costs ~18.5ms of a
measured 19.0s suite (~0.10%) — every candidate waste it contains (redundant file reads, an
extra module load) is under 1ms in absolute terms. This is a one-shot CI/build gate
(`INTEGRATION_SCRIPTS` in `run-unit-tests.sh`), not a per-session or per-write hook, so even a
generous 10x safety margin on the measurement leaves nothing worth an edit. The three markdown
subjects carry no runtime cost at all.

## Measured cost of the new section

Method: loaded `test-validate-digest.py` via the same `importlib.util.spec_from_file_location`
mechanism the suite itself uses, redirected stdout, and timed a direct call to
`run_documented_contract_cases()` in isolation (not via a full suite re-run). Result: **18.5ms**
wall, `fails=0`. Against the orchestrator's pinned 19.0s total, that's **0.097%** of the suite —
not re-derived, only the numerator is new here.

Decomposed (throwaway probe in `/tmp`, never inside the worktree):
- **16.7ms** — the function's own independent `importlib` load of `validate-digest.py`
  (a fresh module object under the name `_validator_contract_guard`, separate from
  `run_code_grade_cases`'s own `_validator_under_test` load at line 3971). This dominates the
  section's cost. It is not incidental sloppiness: the file's established convention
  (`_fresh_validator()`, `:2918`) deliberately re-imports per check group so one case's
  monkeypatch can't bleed into another — the same reason `run_code_grade_cases` does its own
  load. Sharing the module across both would save ~16.7ms once — not worth breaking the
  isolation convention for.
- **~0.3ms total** for all 16 `CONTRACT_SOURCES` persona→path reads (11 distinct files, 5
  duplicate entries: `harness-digest-dev/SKILL.md` read 4x, `harness-team/SKILL.md` read 3x).
  Proportional cost of just the 5 redundant reads: **~0.09ms**.
- **~0.15ms** for `_reviewer_plan_mode_results`'s 3 re-reads of files already read once by
  `documented_contract_results` (`.claude/agents/harness-code-reviewer.md` is new to this call,
  but `.omp/agents/harness-code-reviewer.md` and the code-review `SKILL.md` overlap with
  `CONTRACT_SOURCES`'s own `.omp/agents/harness-code-reviewer.md` entry — 1 of the 3 is a true
  second read).

## Leads, answered

- **Suite fraction, method named:** 18.5ms / 19.0s ≈ 0.10%. Method: isolated
  `run_documented_contract_cases()` call, stdout-suppressed, timed directly — not a fraction
  inferred from source reading.
- **Redundant `CONTRACT_SOURCES`/`_reviewer_plan_mode_results` reads — does it matter at this
  size?** No. Total redundant-read cost across both call sites is **under 0.5ms** combined — a
  memoized reader would save a fraction of a millisecond in a 19-second suite. Declining to flag
  this, per the skill's own worked example, is the correct outcome here.
- **Lifecycle placement:** one-shot CI/build gate. `test-validate-digest.py` is registered in
  `INTEGRATION_SCRIPTS` in `.claude/skills/harness/bin/run-unit-tests.sh` (confirmed by grep
  against prior review receipts in this feature's own notes tree, e.g.
  `review-harness-qa-c1.md:43-44`, `qa-test-matrix-c1.md:51-52` — both read the array directly,
  not the `detect` glob). It runs under `--kind integration`, invoked by the qa test-matrix gate
  at a build boundary — not on every session start or every write. `.harness/harness.json` (this
  checkout) carries no hook wiring to this script; nothing under `.claude/settings*.json` or
  `.github/workflows` invokes it per-session either (grepped, no matches).
- **Is the deliberate full-suite run at this boundary itself waste?** No — it is the evidence
  the boundary exists to produce (qa's test-matrix gate already PASSed on this diff, per the
  dispatch's own pinned numbers: 156 ok lines, zero `^FAIL`, 19.0s). Flagging a one-shot CI gate
  for taking 19 seconds would be optimizing a cost nobody pays repeatedly.

## Non-runtime subjects (one line each, per dispatch)

`.claude/agents/harness-code-reviewer.md`, `.omp/agents/harness-code-reviewer.md`,
`.claude/skills/harness-code-review/SKILL.md`, `.harness/harness/docs/DECISIONS*.md` — prose/config,
no execution path, no runtime cost to measure.

## Out of scope by construction

`.claude/skills/harness/bin/validate-digest.py` — byte-unchanged (BRIEF SC-04); any remedy
touching it is excluded regardless of merit. None found there anyway.

## Verification

`git status --porcelain` at both start and end of this pass, unfiltered:
```
 M .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json
 M .harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml
```
Identical at both checkpoints — pre-existing, not caused by this pass, and outside the diff's
changed-file set assigned to this angle. No file in `63404ef0..b724a0f4`'s diff was touched.
All timing done via a throwaway script in `/tmp`, never written inside the worktree.
