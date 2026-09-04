# UI review — FEAT-54-handoff-done-when — c2

**FAIL.** The author-facing text contract itself now holds: five ordered sections are taught consistently, blank and reversed `Scope:` shapes are refused before a write, the two feature handoffs stay within the whole-file budget, and ordinary refusals identify both the broken rule and the template. The literal SC-04 repository-root command nevertheless exits 1, so the inspection criterion remains live and cannot be waived. SC-10 remains pending operator UAT.

## Scope and immutable census

Mode B source audit at pinned `review_sha` `53e1745462b75e1c54967b43e2f4fbdfc7037e23` against `0ec44965a961d19177de871c3bb1f02b701e646b`. `HEAD` resolved to the pinned SHA, and `git diff --quiet <review_sha> -- <all 16 named paths>` exited 0, so the inspected named-set bytes match the immutable object.

I inspected every named file before scoping: `.claude/skills/harness/SKILL.md`; `bin/check-domain.sh`; `bin/check-state.sh`; `bin/handoff_done_when.py`; `templates/HANDOFF.md`; `.harness/harness.json`; `DECISIONS-INDEX.md`; the applicable DEC-159/214 text in `DECISIONS.md`; `notes/handoff-plan.md`; `notes/handoff-build.md`; `test-check-domain.py`; `test-check-state.py`; `test-run-unit-tests-kinds.py`; `probe-handoff-comprehension.py`; `test-handoff-done-when.py`; and `test-probe-handoff-comprehension.py`. I also read the BRIEF, plan task clauses, the c1 Scope-order ruling, all c0 reviewer findings, and the c0 validator digest.

The complete 78-path base-to-review diff has no CSS/SCSS/TSX/JSX/Vue/Svelte/Less file. Its sole HTML path is a generated ship-review reading view whose footer says the paired markdown is the record and the HTML must be regenerated, not edited (`notes/ship-review-2026-09-02-t05t09-eng.html`). No feature `DESIGN.md` or prototype exists. The named CLI, hook refusal, template, and handoff prose are nevertheless author-facing surfaces, so this review is in scope under the dispatch.

## Authoring experience and terminal readability

- The template has the fixed five sections in order, with `## Done when` last and exactly one example `Scope:` followed by one `Authority:`. Its instruction says the scope is the one immediate `## Next` action, not the phase or feature, and explains AND semantics and all four authority types (`templates/HANDOFF.md:18-40`). The playbook and DEC-159/214 repeat the five-section contract without a live four-section instruction (`SKILL.md:310-316`; `DECISIONS.md:3700-3722,6696-6715`).
- The real handoffs use non-empty, immediate-action labels with Scope before Authority: “re-sign the amended plan and brief” and “validate the final build against the signed success criteria” (`handoff-plan.md:53-55`; `handoff-build.md:34-37`). Newline counts are 55 and 37; both are below the 60-line cap. The template is 40 logical lines (39 newline characters because its final line has no trailing newline).
- The cap refusal keeps the whole-file threshold at 60 and names all five content categories (`check-domain.sh:1547-1559`). Focused test inspection shows 60 lines allowed and 61 refused, with no per-section cap (`test-check-domain.py:4211-4223`; `test-check-state.py:2244-2258`).
- Direct hook probes captured actual terminal bytes. A blank `Scope:` exited 2 with `Scope: value must be non-empty; follow templates/HANDOFF.md`; reversed order exited 2 with `Scope: line must appear before every Authority: line; follow templates/HANDOFF.md`. A missing section exited 2 and produced two redundant but individually actionable lines naming `## Done when` and the template. The duplication is non-gating because no approved contract prohibits it and the remedy remains unambiguous.
- Refusals are plain, linear text with a `check-domain: BLOCKED` head, indentation, explicit exit 2, and no ANSI/colour dependency. State is not conveyed by colour alone. There are no controls, focus state, motion, or theme tokens; keyboard/focus and dark/light parity are not applicable. Narrow-terminal wrapping and semantic message quality still require human eyes; SC-10 is the designated operator UAT and was not simulated.

## Prior panel F-01..F-07 reassessment

| Prior finding | c2 disposition | Evidence |
|---|---|---|
| F-01 — authority containment and fail-closed resolver | **CLOSED** | `_unsafe_rel_path`, `_read_target`, and `_resolution_problems` reject absolute/traversal/control, root escape, symlink escape, non-regular/oversized/unreadable targets and unexpected resolver exceptions (`handoff_done_when.py:45-99,234-247`). Unit and real-gate cases cover both grammar modes and fail-closed injection (`test-handoff-done-when.py:76-101,139-159`; `test-check-domain.py:4088-4110,4168-4189`). |
| F-02 — comprehension probe local-file disclosure | **CLOSED** | `validate_note` admits only repository-contained `handoff-*.md` regular UTF-8 files, refuses links and oversize input before `run`, and `note_paths` returns only validated notes (`probe-handoff-comprehension.py:54-113`). Six focused tests assert zero calls for every rejected shape and exactly two calls for a valid note (`test-probe-handoff-comprehension.py:49-101`); the current c2 QA execution record reports all six passing. |
| F-03 — invalid Edit mutates before refusal | **CLOSED** | PreToolUse reconstructs handoff Edit candidates, sends them through shape validation, and exits 2 on unreadable/non-UTF-8 existing bytes before mutation (`check-domain.sh:1825-1887`). The integration cases compare before/after bytes for an invalid candidate and invalid UTF-8 bytes (`test-check-domain.py:4114-4166`). |
| F-04 — literal SC-04 root check | **LIVE — HIGH** | The exact root command exited **1**. A case-insensitive census over its captured output found **0** lines naming `Done when`, but the output includes the unrelated FEAT-51 missing `handoff-validate.md` violation plus five c2 run-digest contract violations. None is waived or replaced with a fixture. See live finding below. |
| F-05 — blank/whitespace-only Scope | **CLOSED** | `_scope_problems` requires a non-empty trimmed value (`handoff_done_when.py:177-183`); unit, write-gate, and state-gate cases each pin it (`test-handoff-done-when.py:68-74`; `test-check-domain.py:4043-4058`; `test-check-state.py:2178-2219`). The direct hook probe exited 2 with the actionable message. The prior UI c0 F-01 is this panel finding and is closed by the same evidence. |
| F-06 — Scope after Authority | **CLOSED** | The c1 product ruling makes BRIEF REQ-02 controlling. `_order_problems` rejects any first Authority before Scope (`handoff_done_when.py:200-207`), and unit/write/state cases pin the order (`test-handoff-done-when.py:68-74`; `test-check-domain.py:4047-4049`; `test-check-state.py:2217-2219`). The direct hook probe exited 2 and named the required order. |
| F-07 — changed-function risk grades | **CLOSED** | The current c2 post-simplify QA record reports an exact 62-pair census: 20 production functions at grade 4+ and 42 test functions at grade 3+, with identity/length discrimination; the changed `measure_note` is grade 4 (`notes/qa-validation-post-simplify-c2.md:25-55`). The whole-file grade exit 1 is explicitly attributed there to unchanged legacy records and is not substituted for the scoped gate. |

### Live F-04 — HIGH — literal SC-04 remains red

**Failure scenario.** An operator reaches review and runs the exact BRIEF-prescribed root command expecting the review-time clean-state evidence. It exits 1, so the operator cannot truthfully record the required clean exit or treat SC-04 as satisfied; doing so would turn an unrelated repository violation into a silent waiver.

**Actual.** From the repository root, `bash .claude/skills/harness/bin/check-state.sh` exited 1. Its captured output had zero case-insensitive `Done when` matches, but did report FEAT-51's missing validate handoff and five c2 digest-contract violations.

**Specified.** BRIEF SC-04 requires the literal root check and preservation of its actual exit; the c0 validator already ruled that exit 1 remains a failure even when no line names `Done when` (`runs/2026-09-02-review-c0-validator/digest.md`).

**Owner lane.** Main direct repository-state/bookkeeping reconciliation. This reviewer does not repair, waive, or replace the command.

## Commands and evidence

- `git rev-parse HEAD` → `53e1745462b75e1c54967b43e2f4fbdfc7037e23`; both review/base objects resolved as commits.
- Full diff census → 78 paths; UI-extension census → one generated HTML, zero authored rendered-UI paths.
- Named-set `git diff --quiet <review_sha> -- <16 paths>` → exit 0.
- Literal SC-04 command → exit 1; captured-output `Done when` census → 0 matches.
- Direct blank-Scope hook probe → exit 2; direct reversed-Scope hook probe → exit 2; direct missing-section probe → exit 2.
- SC-10 credentialled/operator run: **not run; pending UAT**.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "The author-facing five-section/refusal contract now holds, including blank and reversed Scope closure, but literal SC-04 still exits 1 and cannot be waived; SC-10 remains pending operator UAT."
  mode: B
  in_scope: true
  severity_max: high
  findings: 1
  must_fix:
    - "F-04: reconcile repository state/bookkeeping so the literal root SC-04 command exits 0; this review recorded exit 1 without waiving FEAT-51 or substituting a fixture."
  contract_violations:
    - { path: ".claude/skills/harness/bin/check-state.sh", actual: "literal root command exit 1; zero Done-when output matches", specified: "BRIEF SC-04 clean review-time root check" }
  a11y: []
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c2.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-ui-reviewer-c2.md
```
