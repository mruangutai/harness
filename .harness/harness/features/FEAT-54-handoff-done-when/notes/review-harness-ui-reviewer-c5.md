# UI/user-surface review c5 — FEAT-54 handoff Done when

## BLUF

**FAIL.** At immutable review SHA `4690f724cdbbdf03649f0cbea07efe7be3c03ce0`, the five-section author contract, refusal text, persisted-check wording, probe dry-run, SC-15 repair, and tool-disabled probe argv are coherent and actionable. No gating UI or accessibility defect remains in the 16-path implementation. The required literal repository-root SC-04 run is nevertheless not clean: it exits 1 on one unrelated INV-29 violation for the standing `BUG-1157-approval-overrule` worktree. Its complete output contains zero case-insensitive `Done when` lines. Per the acceptance rule, this reopens F-04 as a high external state-gate blocker. Raw terminal-control output in the manual probe remains the prior medium advisory SEC-F-08.

## Immutable scope and in-scope assessment

HEAD resolved exactly to `4690f724cdbbdf03649f0cbea07efe7be3c03ce0` before inspection. This is Mode B and **in scope** despite having no graphical UI: author-facing markdown, refusal messages, state findings, and CLI/model-probe output are user-facing text surfaces. All 16 required paths were inspected at that exact HEAD:

1. `.claude/skills/harness/bin/handoff_done_when.py` — parser and actionable problem text.
2. `tests/unit/test-handoff-done-when.py` — direct message/grammar evidence.
3. `tests/unit/test-probe-handoff-comprehension.py` — admission and argv evidence.
4. `tests/integration/test-check-domain.py` — real write/Edit refusal evidence.
5. `.claude/skills/harness/bin/check-domain.sh` — author-facing write gate.
6. `.harness/harness.json` — baseline, locally-run registration, and gate policy.
7. `tests/integration/test-check-state.py` — persisted messages and repaired no-rot proof.
8. `.claude/skills/harness/bin/check-state.sh` — operator-facing state gate.
9. `.claude/skills/harness/templates/HANDOFF.md` — primary authoring surface.
10. `.claude/skills/harness/SKILL.md` — orchestrator/successor guidance.
11. `tests/manual/probe-handoff-comprehension.py` — CLI/model-probe surface.
12. `.harness/harness/docs/DECISIONS.md` — DEC-159/DEC-214 wording.
13. `.harness/harness/docs/DECISIONS-INDEX.md` — decision routing/parity.
14. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-plan.md` — real authored note.
15. `.harness/harness/features/FEAT-54-handoff-done-when/notes/handoff-build.md` — real authored note.
16. `tests/integration/test-run-unit-tests-kinds.py` — probe discoverability/isolation evidence.

The approved `BRIEF.md`, `plan.yaml`, all c4 reviewer notes, and `runs/2026-09-03-sec-f10-c5-eng/digest.md` were also consulted as authority/prior evidence. This review independently checked current bytes and executions rather than inheriting their verdicts.

## Surface audit

- **Guidance fidelity and parity:** `templates/HANDOFF.md`, `SKILL.md:309-316`, DEC-159, DEC-214, both gates, and both real FEAT-54 handoffs consistently say five sections; `Done when` is last, describes the one immediate action in `Next`, has one non-empty `Scope:` followed by one-to-four typed `Authority:` lines, uses AND semantics, and resolves targets only at write time. The two real handoffs are within the 60-line cap and their scopes match their immediate next actions.
- **Refusal/actionability:** `handoff_done_when.py` names the broken count, ordering, pointer, or unexpected line and always points authors to `templates/HANDOFF.md`. `check-domain.sh:1547-1569` retains the clear `check-domain: BLOCKED` hierarchy and refuses validator exceptions explicitly. The focused real-hook file passed all 41 FEAT-54 cases, including missing/valid, blank/reordered Scope, all pointer kinds, unsafe targets, pre-mutation Edit refusal, 60/61 lines, and fail-closed exceptions.
- **Persisted output:** `check-state.sh:1211-1264` identifies the feature and note, distinguishes missing/empty/cap/Done-when problems, and uses plain linear text. The SC-15 repair changes no operator wording but makes the stability claim falsifiable: both absent-target cases now reject every output line naming `handoff-plan.md`, and the caller mutant reports `real=0, mutant=1`. The full selected state test passed.
- **Probe clarity and safety:** the actual dry-run against `handoff-build.md` exited 0 and clearly printed `DRY RUN`, model, both arm labels, four questions, the selected note, and `planned model calls: 2 (not executed)`. `ask()` now passes exactly one `--no-tools` and no `--auto-approve`; the focused behavioral test captured that argv and all 7 methods passed. SEC-F-10 is closed.
- **Accessibility/readability:** the reviewed messages use labels and words rather than colour alone; no ANSI styling, controls, focus state, hit targets, motion, or colour tokens are part of the authored interface. Keyboard/focus and light/dark-theme parity are therefore not applicable. SEC-F-08 remains because repository/model-controlled paths, facts, errors, and answers still reach raw `print()` sinks; a source grep found no ANSI/control neutralization (`ansi`, `escape`, `neutral`, `sanitize`, `unicode_escape`, `repr`, `isatty`, C0/C1 or ESC handling).

## Literal SC-04 evidence — blocking

From the repository root, exactly:

```sh
bash .claude/skills/harness/bin/check-state.sh
```

Result at the pinned SHA: **exit 1**. The complete 812-line capture contains **one** tagged `VIOLATION` and **zero** case-insensitive `Done when` lines. The sole violation is INV-29: the standing worktree `.claude/worktrees/harness/BUG-1157-approval-overrule` has no landed `feature.json`, so terminal status cannot be determined. The message is itself actionable: it names the worktree, the missing landed record, and the exact removal command. It is external to the 16-path FEAT-54 implementation, but acceptance requires a clean literal SC-04 run, so the review cannot pass.

**Concrete user-facing failure scenario:** a reviewer or operator runs the mandated root state check at the immutable pin and receives a hard violation/exit 1, so they cannot truthfully record a clean SC-04 result even though no output line names `Done when`. **Owner lane:** harness-orchestrator/Main repository-state and worktree-lifecycle lane; this read-only review must not remove another feature's worktree.

## Prior-finding dispositions at c5

| Finding | Disposition | Current-pin basis |
|---|---|---|
| F-01 — authority containment/fail closed | **CLOSED** | Shared bounded reader and current 54-case unit run reject unsafe, escaped, special, and unresolved targets with actionable text. |
| F-02 — probe admission before model calls | **CLOSED** | Validated-note admission precedes calls; focused 7-method run retains zero-call refusals and a two-call valid control. |
| F-03 — invalid/unreadable Edit mutates before refusal | **CLOSED** | PreToolUse reconstruction refuses invalid/non-UTF-8 candidates; selected real-hook cases passed byte-identity checks. |
| F-04 — literal SC-04 | **REOPENED — HIGH** | Exact command exits 1 on the external INV-29 worktree violation; zero `Done when` lines. |
| F-05 — blank Scope | **CLOSED** | Shared parser, unit, write, and state surfaces refuse it with `value must be non-empty`. |
| F-06 — Scope ordering | **CLOSED** | All three enforcement layers refuse Authority-before-Scope with the required-order message. |
| F-07 — changed-function complexity | **CLOSED for UI lens** | No user-surface recurrence; mechanical grading remains the code-reviewer lane. |
| F-08 — nested/duplicate heading truncation | **CLOSED** | Shared parser and selected gate tests reject nested stray prose and duplicate Done-when H2s. |
| F-09 — false approval heading | **CLOSED** | Strict ATX parsing and current tests reject no-space/seven-hash lookalikes beside valid controls. |
| F-10 — SC-15 assertion subject mismatch | **CLOSED** | Empty needle tuples bind both absent-target cases to every line naming the handoff; executable caller mutant passes only at `real=0, mutant=1`. |
| SEC-F-08 — raw terminal controls | **SURVIVES — MED advisory** | Raw path/fact/provider/model strings remain printable without terminal neutralization. Owner: harness-dev-ops via harness-eng-lead. |
| SEC-F-10 — tool-enabled auto-approved probe | **CLOSED** | Current argv has exactly one `--no-tools`, omits `--auto-approve`, and is pinned by the passing focused test. |

## Verification and limits

Executed only selected evidence: parser unit script (54 named passes), probe unit file (7 tests, OK), complete required domain integration file (41 FEAT-54 outcomes pass), complete required state integration file (including `real=0, mutant=1`), probe dry-run (exit 0), and literal SC-04 (exit 1 as above). No formatter, linter, project-wide build/suite, credentialled model run, SC-10 UAT, or PM goal-check ran.

This is a source-and-terminal audit, not rendered-pixel inspection. Narrow-terminal wrapping and the operator's subjective judgment of the section's value/actionability against the 60-line budget require human/SC-10 UAT; no confident visual claim is made for those dimensions.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The 16-path text UI is coherent and both c4 high repairs close, but literal SC-04 exits 1 on an external INV-29 worktree violation, so c5 cannot pass."
  mode: B
  in_scope: true
  severity_max: high
  findings: 2
  must_fix:
    - "F-04: obtain a pin/environment where the exact repository-root SC-04 command exits 0; current failure is INV-29 for standing BUG-1157-approval-overrule with missing landed feature.json. Owner: harness-orchestrator/Main repository-state and worktree-lifecycle lane."
  contract_violations:
    - { path: ".claude/skills/harness/bin/check-state.sh", actual: "literal root command exit 1; one INV-29 BUG-1157 worktree violation; zero Done when lines", specified: "BRIEF SC-04 and c5 acceptance require a clean literal repository-root state check" }
  a11y: []
  open_questions:
    - { id: Q1, question: "The dispatch requested notes/review-ui-c5.md, but check-domain permits this persona only notes/review-harness-ui-reviewer-*.md; should the dispatch generator adopt the canonical persona-qualified filename?", blocking: false }
  files_touched: [.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c5.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c5.md
```
