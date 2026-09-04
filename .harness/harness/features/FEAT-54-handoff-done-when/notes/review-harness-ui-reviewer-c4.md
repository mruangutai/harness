# UI/user-surface review — FEAT-54 handoff Done when — c4

**PASS.** At immutable candidate `f05e1e6cd74c7d91580dd6ef565a00432faac1ad`, the author-facing template, playbook guidance, hook refusals, state findings, real handoffs, and manual-probe dry-run are coherent and actionable. Exact repository-root SC-04 exits 0 with zero `Done when` findings. One previously reported terminal-control advisory remains medium and therefore does not gate under the configured `advisory_unless_high` review policy.

## Immutable 16-path census

HEAD resolved exactly to `f05e1e6cd74c7d91580dd6ef565a00432faac1ad`; a path-restricted `git diff --quiet` confirmed all 16 reviewed paths match that object. Census: 7 Python, 2 shell, 1 JSON, 6 Markdown; **0 HTML/CSS/SCSS/TSX/JSX/Vue/Svelte/Less**. No `DESIGN.md` or prototype exists for this feature. There is no rendered visual UI, but the CLI/hook/template/probe text is an author/operator-facing surface, so this review is in scope.

**Direct author/operator surfaces (8, in scope):**

1. `.claude/skills/harness/bin/handoff_done_when.py`
2. `.claude/skills/harness/bin/check-domain.sh`
3. `.claude/skills/harness/bin/check-state.sh`
4. `.claude/skills/harness/templates/HANDOFF.md`
5. `.claude/skills/harness/SKILL.md`
6. `tests/manual/probe-handoff-comprehension.py`
7. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md`
8. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md`

**Supporting contract/config surfaces (3, inspected; not rendered UI):**

9. `.harness/harness.json`
10. `.harness/harness/docs/DECISIONS.md`
11. `.harness/harness/docs/DECISIONS-INDEX.md`

**Test-only evidence (5, inspected; out of direct user-surface scope):**

12. `tests/unit/test-handoff-done-when.py`
13. `tests/unit/test-probe-handoff-comprehension.py`
14. `tests/integration/test-check-domain.py`
15. `tests/integration/test-check-state.py`
16. `tests/integration/test-run-unit-tests-kinds.py`

## Surface audit

- **Contract clarity and consistency:** `templates/HANDOFF.md:1-39`, `SKILL.md:310-316`, DEC-159, DEC-214, and both real handoffs consistently define five sections; `Done when` is last, describes the one immediate action in `Next`, has exactly one non-empty `Scope:` followed by one-to-four `Authority:` lines, uses AND semantics, and resolves targets only at write time. The two real scopes are concise immediate actions and the notes are 55 and 37 lines, below the unchanged 60-line cap.
- **Refusal quality:** `check-domain.sh:1546-1569` produces uncoloured, linear text under `check-domain: BLOCKED`, names the broken rule, and points to `templates/HANDOFF.md`. A direct malformed-write probe exited 2 with `## Done when Scope: value must be non-empty; follow templates/HANDOFF.md`; no file was created. The duplicate missing-section explanation is redundant but gives the same remedy and violates no approved contract.
- **State findings:** `check-state.sh:1069-1070,1188-1264` distinguishes missing narrative headings, the baseline-conditioned fifth heading, block-shape/grammar failures, and the whole-file cap without re-resolving targets. Messages identify the feature/note and remedy. No ANSI or colour-only encoding appears in the reviewed terminal paths.
- **Parser safety and states:** `handoff_done_when.py:24-35,57-101,154-174,187-216,272-288` rejects duplicate H2 sections, nested prose, blank/reordered Scope, unsafe authority paths, and non-ATX approval lookalikes; echoed pointers and unexpected lines use escaped representations. The inspected unit and both gate test surfaces independently cover missing, valid, malformed, unresolved, unsafe, duplicate/nested, 60/61-line, edit-refusal, and persisted-target-rot states.
- **Probe clarity:** the actual dry-run against `handoff-build.md` exited 0, clearly labeled `DRY RUN`, model, both arms, four questions, the note, and `planned model calls: 2 (not executed)`. The locally-run registration and normal-suite exclusion agree across `.harness/harness.json` and `test-run-unit-tests-kinds.py`.

## Exact SC-04 measurement

From the repository root I ran exactly:

```sh
bash .claude/skills/harness/bin/check-state.sh
```

Result: **exit 0**; tagged `VIOLATION` lines: **0**; output lines containing case-sensitive `Done when`: **0**. Thus c3 F-04 is closed at this pin: the repaired external FEAT-51 state no longer prevents the required clean repository-state result.

## Prior-finding reassessment at the current pin

| Finding | c4 disposition | Independent current-pin basis |
|---|---|---|
| F-01 — authority containment/fail closed | **CLOSED** | Shared bounded regular-file reader rejects absolute, traversal, control-bearing, symlink-escape, special, oversized, unreadable, and resolver-exception cases; approval and finding paths use it independently. |
| F-02 — probe admission before model calls | **CLOSED** | `validate_note`/`read_regular_file` admit only contained `handoff-*.md` regular files; inspected focused tests require zero calls for outside/traversal/symlink/directory/wrong-name/oversize and two calls for valid input. |
| F-03 — invalid/unreadable Edit mutates before refusal | **CLOSED** | PreToolUse reconstructs protected Edit candidates and refuses invalid/non-UTF-8 candidates before mutation; the integration cases assert byte identity. |
| F-04 — literal SC-04 | **CLOSED** | Exact root command exits 0 with 0 tagged violations and 0 `Done when` findings. |
| F-05 — blank Scope | **CLOSED** | `_scope_problems` requires a non-empty value; direct real-hook refusal reproduced the actionable message. |
| F-06 — Scope ordering | **CLOSED** | `_order_problems` requires Scope before every Authority, with unit/write/state cases covering reversal. |
| F-07 — complexity grades | **CLOSED for this lens** | No current-pin user-surface regression follows from the prior complexity concern; mechanical complexity grading remains the code-reviewer lane and was not rerun by this UI assignment. |
| F-08 — nested/duplicate heading truncation | **CLOSED** | `_body` stops only at a strict H2, nested prose remains visible as invalid, and `_done_when_indices` rejects duplicate H2 sections; all three enforcement layers carry cases. |
| F-09 — non-Markdown approval heading | **CLOSED** | `_atx_heading_text` requires one-to-six hashes plus whitespace; valid ATX remains the positive control while no-space/seven-hash forms are refused. |
| SEC-F-08 — raw terminal control bytes | **SURVIVES — MED advisory** | `probe-handoff-comprehension.py:86-98,157-197` still prints repository/model-controlled paths, facts, errors, and answers without terminal neutralization. |

## Ranked findings

1. **SEC-F-08 — med, advisory — raw control bytes can alter probe evidence.** A repository Scope value or model answer containing ESC/OSC sequences reaches `print()` unchanged and can clear the terminal, change its title, or visually forge the following coverage/result lines. Owner lane: **harness-dev-ops via harness-eng-lead**. This is substantive but non-gating under `.harness/harness.json` `gates.review: advisory_unless_high`.

No high/critical, unrated, or must-fix user-surface issue remains.

## Accessibility, theme parity, and adequacy limits

The changed surface has no controls, focus state, hit targets, motion, colour tokens, or colour-only meaning. Keyboard/focus accessibility and dark/light parity are therefore not applicable; the terminal output is plain linear text in both terminal themes. SEC-F-08 is an output-integrity/readability risk, not a theme or contrast claim.

This is a source-and-terminal audit, not rendered-pixel inspection. Narrow-terminal wrapping and the operator's judgment of message actionability/value against the 60-line budget require human eyes. I did not run the credentialled model arm, SC-10 UAT, PM goal-check, formatters, linters, builds, or unrelated suites; SC-10 remains intentionally pending outside this assignment.

```yaml
VERDICT: PASS
DIGEST:
  headline: "At f05e1e6cd74c7d91580dd6ef565a00432faac1ad the author-facing contract is green and exact SC-04 exits 0; only medium advisory SEC-F-08 remains."
  mode: B
  in_scope: true
  severity_max: med
  findings: 1
  must_fix: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c4.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c4.md
```
