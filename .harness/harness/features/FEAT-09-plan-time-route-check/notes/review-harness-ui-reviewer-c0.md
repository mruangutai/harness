# UI review — FEAT-09 (plan-time route check) — cycle 0 — Mode B

## Scoping verdict: no rendered-UI surface; adjacent CLI-output legibility contract judged in-remit and checked

**Diff scope:** `git diff 47ed11f..4918d06` (base measured via `git merge-base main HEAD`), 19 files
changed, 1679 insertions / 41 deletions.

### 1. Rendered-UI surface: absent, measured not inferred

- File-extension census across the full diff for `html|css|scss|less|tsx|jsx|vue|svelte`: zero
  matches (`git diff --name-only 47ed11f..4918d06 | grep -Ei ...` → exit 1, no output).
- No `web/` or `src/` directory exists in the worktree at any depth ≤2.
- `DESIGN.md` for this feature confirmed absent at the diff base via direct object check:
  `git cat-file -e 47ed11f:.harness/features/FEAT-09-plan-time-route-check/DESIGN.md` → exit 128,
  "does not exist in '47ed11f'". No design contract exists to audit against.
- Standard Mode B dimensions (fidelity, states, interaction, a11y, theme parity, regression) have
  no object to apply to. `in_scope: false` for those dimensions is a measured finding, not an
  inference.

### 2. CLI-output legibility (the one adjacent surface the dispatch flagged) — judged in-remit, checked, compliant

`check-plan-routes.py` prints `VIOLATION`, `DEVIATION`, `UNRESOLVED-GLOB` findings to a human
reader (the planner). `BRIEF.md:26-27` REQ-03 requires the rejection to name the offending task
AND path. I judged this within my remit (it is a legibility contract on machine-to-human output,
directly analogous to an error-state message spec) and checked message construction against the
requirement and against the feature's own documentation:

- `VIOLATION {tid}: {path} ungranted (NOBODY); execution_mode is {declared} — legal tokens:
  {LEGAL_TOKENS}` (`check-plan-routes.py:116-117`) — names both task id and path. Satisfies REQ-03.
- `VIOLATION {tid}: no files: line` (`:79`) — names the task, no path applicable (there is none).
- `DEVIATION {tid} {paths} granted to {agents} but declared main-session-direct` (`:123-125`) —
  names task, paths, and the resolved agents needed to fix it.
- `UNRESOLVED-GLOB {tid} {entry}` (`:91`) — names task and the unresolved glob entry.
- `LEGAL_TOKENS` (`:42`) is a plain string literal (`"team, main-session-direct"`), not a
  set/dict — no non-deterministic repr ordering across runs. Checked directly, not assumed.

**Summary-line undercount is intentional, not a defect.** The final line
(`f"{total_violations} violation(s) across {len(paths)} plan(s)"`, `:161`) counts only
`VIOLATION` — a reader scanning just that line would miss printed `DEVIATION`/`UNRESOLVED-GLOB`
lines above it. I checked whether this is a gap against the contract: `PLAN.md:183` (D-03) and
`PLAN.md:186` (D-04) explicitly document `DEVIATION` and `UNRESOLVED-GLOB` as non-failing and
excluded from the violation count, and both behaviors are asserted in
`test-check-plan-routes.py` (case 6, case 14). Documented-contract vs. actual-behavior match —
no divergence. Not a finding.

- `SKILL.md` (+24 lines) and `PLAN.md` template (+20 lines) were read in full diff: both document
  `execution_mode:`, the two legal tokens, and the plan-time checker consistently with the
  implementation. No documented-vs-actual drift found.

### Known limit

I read source (Python format strings, markdown), not rendered/executed terminal output — actual
line-wrapping, ANSI handling, or a real multi-violation run's visual scan-ability at a real
terminal width is not verifiable from source. If a human has run this checker against a plan with
several violation types mixed together and found the output hard to scan, that observation would
override this source-level assessment.

## Verdict

No must-fix items. No a11y surface exists in this diff. PASS.
