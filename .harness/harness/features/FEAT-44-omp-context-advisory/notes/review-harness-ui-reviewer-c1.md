# UI review — FEAT-44 — cycle 1 (Mode B)

## Verdict: scoped OUT (measured, not predicted)

## Census — `git diff --name-status 7ebfc9e..21e97ed`

32 files total. Zero matches for rendered-UI extensions (`html|css|scss|tsx|jsx|vue|svelte|less`).
Breakdown by category:

| category | count | files |
|---|---|---|
| TS hook implementation | 1 | `.omp/extensions/harness-hooks.ts` |
| TS test suite | 1 | `.claude/skills/harness/bin/omp-hooks.test.ts` |
| JSONL fixtures | 2 | `omp-session-anchored.fixture.jsonl`, `omp-session-anchorless.fixture.jsonl` |
| Python test/policy scripts | 8 | 3 added/modified, 5 deleted (`context-watch*`, `test-context-watch*`, `verify-context-watch-live.py`) |
| Shell | 1 | `run-unit-tests.sh` |
| JSON config | 2 | `.claude/settings.json`, `.harness/harness.json` |
| Markdown — process/skill docs | 2 | `SKILL.md` (step 5 rewrite), deleted `references/context-check.md` |
| Markdown — decision records | 2 | `DECISIONS.md`, `DECISIONS-INDEX.md` |
| Feature workspace docs (BRIEF, plan.yaml, evidence, notes, observations, feature.json) | 13 | all under `.harness/harness/features/FEAT-44-omp-context-advisory/` |

No `.tsx`/`.jsx`/`.vue`/`.svelte`/`.css`/`.scss`/`.html` anywhere in the diff.

## DESIGN.md check

`git ls-tree -r --name-only 21e97ed` finds `DESIGN.md` files for FEAT-10, FEAT-11, FEAT-19, FEAT-40 —
none are touched by this diff, and no `DESIGN.md` exists at
`.harness/harness/features/FEAT-44-omp-context-advisory/`. Confirmed absent for this feature, not
assumed. `BRIEF.md:194` states it directly: *"`component`, `ui` and `eval` are null runners; this
feature touches none of those surfaces."* — the feature's own contract asserts no UI surface, matching
the census.

## The judgement call — `contextAdvisoryText` / `contextInertText` / `contextAccessorFailureText`

Read all three at `.omp/extensions/harness-hooks.ts:527-576` (pinned content, confirmed via `git show
21e97ed:...`). They are single-line strings appended to the `content` array of a `task` tool result
(`harness-hooks.ts:826-830`), addressed to the `harness-orchestrator` agent only (REQ-02), never
`display: false`-suppressed but never rendered through any markup, spacing, colour, or theme system —
there is none in this repository (no build step, files-only; confirmed by the extension census above,
consistent with this file's own repo-tier expertise).

**Decision: agree with the lead — out of scope.** These are agent-to-agent machine notices, not a UI
surface, for two independent reasons: (1) structurally, they are plain strings in a tool-result
payload with no rendered form for this role's dimensions (fidelity, states, interaction, a11y, theme
parity) to attach to; (2) by the feature's own contract, REQ-02 restricts delivery to a single agent
tier reading its own tool output, not a human-facing display. This differs from the "CLI/hook-emitted
text surface" carve-out this role has audited before (repo-tier P-01, project-tier P-06) — that
carve-out fires when hook text is the primary human-operator-facing interface (e.g., a CLI error a
user reads directly); here the text is consumed by the agent loop and only incidentally traverses a
transcript a human may later inspect.

Read anyway for defect-class hygiene, since REQ-04 explicitly requires the "inert" and "absent" states
be told apart: `contextInertText`'s claim ("host's record shape may have changed") is reachable only
after a full-file scan finds records but no `contextSnapshot` field, which SC-03 tests as a state
distinct from the legitimate silent "no session yet" case (`resolveSessionFile` returning `absent`).
No case where the post-feature normal path would trip the inert branch was found — this is not a
repeat of the "message diagnoses the new normal as an error" defect class.

## Findings

None. No must_fix, no contract_violations, no a11y findings — none applicable, nothing to report.

```yaml
VERDICT: PASS
DIGEST:
  headline: No UI surface in this diff — 32 files, zero rendered-UI extensions, no DESIGN.md, and the injected advisory text is agent-directed tool-result content, not a human-facing surface
  mode: B
  in_scope: false
  severity_max: n/a
  findings: 0
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-44-omp-context-advisory/notes/review-harness-ui-reviewer-c1.md
```
