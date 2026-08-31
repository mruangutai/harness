# Code review — FEAT-45-adversarial-plan-panel — c0

Reviewed `1d3e5db..d0ebbe6` at pinned `d0ebbe6`. Worktree HEAD is `57f196d` (one commit ahead,
pinning-only: `git diff d0ebbe6 HEAD --stat` touches only `feature.json`), so every other cited
file was read directly from the working tree, verified byte-identical to the pin. No
`[harness:human]` commits since the pin.

## Verdict: FAIL (Stage 1 omission, Stage 2 fail-open, Stage 2 code-grade — all `must_fix`)

## Stage 1 — spec compliance

Verified at source, not accepted from the BRIEF/plan text alone:

- **REQ-02/REQ-05 independent-MODEL claim — TRUE, mechanism verified, not merely independent
  CONTEXT.** `dispatch-guard.sh:33-35` blocks a **harness-prefixed caller** from passing `model:`
  (exit 2) but never touches the target's own frontmatter; `dispatch-guard.sh:56-65` separately
  exits 0 with no claim recorded whenever the **dispatched** persona is not `harness-`-prefixed.
  `plan-panel.yaml`'s `should-not-exist` step carries no `model:` key, so a dispatch built from it
  runs `fable-advisor` on its own frontmatter pin (`model: anthropic/claude-fable-5`, per D-14,
  unread in this repo — outside scope, correctly). Mechanism present in both the team file and
  `.omp/agents/harness-validator-lead.md`'s `spawns:` (confirmed) — real, not aspirational.
- **REQ-14/SC-17 absent-persona skip — TRUE, warn not fail, verified live.** `check-state.sh:227-237`:
  a reader whose `status` isn't `ran`/`skipped` is a hard `bad.append` (blocks); a `skipped` reader
  missing persona/reason is also `bad`; a **complete** skip record goes to `warn.append` only —
  never blocks. Ran `test-check-state.py` live: `ok - INV-32 plan panel fixtures, including
  inv32-red`, and its case 8 (`reader-skipped`) asserts no `VIOLATION` line for the skip. Confirmed.
- **DEC-206 "unrated fails closed" — the executable branch exists** (`check-state.sh:214`,
  `severity in {"high", "critical", "unrated"}`) and both `.omp/` and `.claude/` copies of
  `harness-validator-lead.md` carry "Transcribe `unrated` unchanged and treat it as
  gating-equivalent to high" — not prose-only. **But see Stage 2 finding 1: the branch does not
  actually deliver the "omitted severity fails closed" half DEC-206 also promises.**
- **INV-32 discovery-vs-clean distinction — TRUE, and demonstrably not vacuous.** `expected_readers
  = {"should-not-exist", "scope", "goalcheck"}` is a fixed 3-name enumeration checked per-name
  (`check-state.sh:222-237`), so an empty `readers:` list cannot pass — it fails all three as
  "never ran." `test-check-state.py`'s case 7 (`reader-missing`) pins exactly this, and case
  `inv32-red` (D-13's marker-anchored mutant) proves the no-panel and reader-missing assertions
  are falsifiable: ran it live, `ok`. Genuinely non-vacuous.
- **SC-01, per-reader, enumerated separately, not file-global:** `should-not-exist`'s prompt →
  "what here should not be built at all" (REQ-02, `plan-panel.yaml:19-20`, checked at
  `test-plan-panel.py` case 1a). `scope`'s prompt → "which tasks serve no live requirement"
  (REQ-04, `plan-panel.yaml:41-42`, case 1b). `SKILL.md:93` → "does this plan deliver the
  operator's stated intent" (REQ-03, case 1c). Ran `test-plan-panel.py` live: **24/24 pass**, all
  three checked independently.
- **SC-15, both places, both real:** `fable-advisor` is in `.omp/agents/harness-validator-lead.md`'s
  `spawns:` (confirmed by read) and in `SPAWNS["harness-validator-lead"]` in
  `sync-agent-adapters.py:71` (confirmed by read, and by `test-plan-panel.py` cases 8a/8b, live
  green). `.claude/agents/harness-validator-lead.md`'s generated frontmatter correctly carries no
  `spawns:` key at all (claude_adapter emits `tools/color/model/effort/skills` only) — consistent
  with D-14's explicit "no assertion is made about `.claude/agents/**`."
- **SC-06 roster stays at 16/16**, verified by direct count (`find .omp/agents -maxdepth 1 -name
  'harness-*.md' | wc -l` → 16, same for `.claude/agents`) and by `test-plan-panel.py` case 5, live.
- **SC-08 registration:** `test-panel-findings.py` and `test-plan-panel.py` are both in
  `run-unit-tests.sh`'s `UNIT_SCRIPTS` (confirmed via `:raw` read, not the truncated display); ran
  both live, 9/9 and 24/24. Neither name appears in `harness.json`'s `integration.detect` explicit
  list, so the KIND-DRIFT self-check stays clean. `D-15`'s `TEAMS_EXPECTED = 3` bump is present and
  correctly commented as the FEAT-06 SC-05 point-in-time exception, not a re-signature.
- **SC-09/SC-10 (inspection):** DEC-206 and DEC-207 both present in `DECISIONS.md` with matching
  `DECISIONS-INDEX.md` rows (`@7416`, `@7445`). `harness-plan.md`'s Target-state bullet and
  `SKILL.md`'s new "The plan phase" section both name `plan-panel`, `DEC-176`, and the batched-pass
  language; no separate pre-signature fix dispatch introduced.

**Finding S1 — `must_fix`, `med`.** `plan.yaml:991-993` (T-08's own intent) explicitly requires:
*"Add ONE more assertion inside the high-open case: a finding with severity unrated and disposition
open is reported exactly as a high one is."* T-08 is marked `status: done`. The shipped
`test-check-state.py` contains **zero** occurrences of the string `unrated` (grepped the whole
file) — `case_inv32`'s `open_finding` fixture (`test-check-state.py:2986-2987`) hardcodes
`"severity": "high"` only; no fixture anywhere constructs `severity: unrated`. T-08's own `verify:`
block (`plan.yaml:911-917`) never greps for `unrated` either, so the gap is invisible to the task's
own gate. This is an omission against the task's own written intent, not a hypothetical: DEC-206
names this exact sentinel as its sole compensating control, and it now has no regression test
distinguishing it from `high`.

## Stage 2 — code quality

**Finding 1 — `must_fix`, `high`, fail-open.** `check-state.sh:212`: `severity =
str(item.get("severity", "")).strip().lower()`. `disposition`'s sibling default
(`check-state.sh:213`) correctly fails **closed** — an omitted/malformed disposition stays
`!= "resolved"` and still gates. `severity`'s default does the opposite: a finding whose `severity`
key is **absent entirely**, or present with YAML `null` (a bare `severity:` with no value — both
legal YAML pm or the lead could plausibly emit during transcription), evaluates to `""` or
`"none"` — **neither is in `{"high", "critical", "unrated"}`**, so
`check-state.sh:214`'s gate does not fire and the finding sails through unrated *and*
un-vetted, with no operator ruling required. This directly contradicts DEC-206's stated guarantee,
`.harness/harness/docs/DECISIONS.md:7441`: *"An omitted severity fails closed... A reader that
declines to rate, or **a normalization that loses a rating**, therefore withholds rather than
passes."* The code only fails closed for the literal string `unrated`; a normalization or
transcription slip that drops the key or leaves it null is exactly the "normalization that loses a
rating" DEC-206 names as the risk, and it is not caught. Concrete scenario: `harness-validator-lead`
(an LLM, not code) transcribes the reader's fenced-YAML return into its digest; if one finding's
`severity` key is dropped in that transcription (nothing validates the reader's raw return — DEC-206
says so explicitly), or `harness-pm`'s own transcription into `plan.yaml` drops it, `INV-32` reports
nothing, the plan proceeds to signature, and the operator is never shown the finding needed a
ruling. No test in `test-check-state.py` constructs a missing- or null-severity fixture (confirmed:
same file, no such case among the nine directions), so this is currently un-guarded in both code and
test. Fix: gate on absence of an allow-listed low value (`severity not in {"info","low","med"}`) or
explicitly add `"" `/`"none"` to the gating set, whichever direction the operator prefers, plus a
fixture pinning it.

**Finding 2 — `must_fix`, `high`, code-grade.** Ran `code-grade.py --base 1d3e5db --head d0ebbe6`
live (tool resolved from the main checkout, not present in this worktree's own `bin/`, per the
review skill's invocation). One gated function fails outright:

```
PATH: .claude/skills/harness/bin/test-check-state.py
LINE: 2982
QUALNAME: case_inv32
CYCLOMATIC: 28   COGNITIVE: 14   ABC: 95.1
GRADE: 1   DRIVER: cyclomatic+abc   BAR: 3
RESULT: FAIL
```

`case_inv32` (the same function carrying Finding S1's fixture gap) is grade 1 against a grade-3 test
code bar — cyclomatic 28 is nearly 3x the grade-3 ceiling (10) and ABC 95.1 is over 3.5x it (26).
The tool's overall run exits 1. 22 other changed functions across `test-panel-findings.py` and
`test-plan-panel.py` all pass at grade 4-5; this is the one gated record blocking the build. The
function is doing exactly the "nine directions in one function" job D-13's own comment describes,
and would benefit from being split one case-per-helper (the file's own `check()` accumulator
pattern already supports that shape) — not asked to relitigate the fixture-reuse rationale D-13
gives for keeping the mutant-comparison logic together, but the nine `_inv32_run` call sites plus
the mutant block are separable without touching that rationale.

**Finding 3 — `low`, ambiguity, not a proven defect.** `SKILL.md`'s "The record" step and
`harness-spec-driven/SKILL.md`'s "The panel result" subsection both say pm transcribes "every
[named] reader" from "the validator lead's digest," but the validator lead's digest only ever names
two readers (`should-not-exist`, `scope`) — the third expected reader, `goalcheck`, is pm's own
product-segment work, done under a different orchestrator dispatch entirely. Neither doctrine file
states in so many words that pm must also write a `reader: goalcheck, status: ran` entry for its own
step. `check-state.sh:216-229` hard-requires all three by name (`bad`, not `warn`), so if a first
implementer reads "transcribe the validator lead's digest" narrowly, every live plan blocks at
signature until fixed. Failure direction is fail-**closed** (annoying, not dangerous), and the
template's own enum comment (`templates/plan.yaml:59`, `reader: should-not-exist | scope |
goalcheck`) is a strong hint toward the correct reading, so I am not raising this to `must_fix` —
noting it because SC-16's first live `/harness-plan` is exactly where this would surface.

No other fail-open branches found in `panel_findings.py` (identity hashing only, no gating logic),
`sync-agent-adapters.py` (7-line additive diff, dead code path per its own comment, confirmed by
diff), `run-unit-tests.sh` (registration only, confirmed both new files present via `:raw` read),
or `test-harness-yaml-corpus.py` (comment + constant change matches D-15 exactly). `panel_findings.py`
CLI hard-fails (exit 2) on empty reader / whitespace-only summary — correctly fail-closed.

## Not re-litigated

DEC-206's signed trade (reader structurally unvalidated) — accepted per instructions. Weighed all
three named residuals; found no evidence they are better or worse than stated. SC-03's `{{cycle}}`
proxy and the 9/16 author-reported mutants were not independently re-derived.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "check-state.sh's INV-32 fails OPEN on a missing/null severity (only the literal string 'unrated' gates, contradicting DEC-206), test-check-state.py shipped without T-08's own mandated unrated regression case, and case_inv32 is a grade-1 function against a grade-3 test-code bar (cyclomatic 28, ABC 95.1)."
  severity_max: high
  findings: 3
  must_fix:
    - "check-state.sh:212-214 — a panel finding with an absent or null `severity` key does not gate (only the literal string 'unrated' does), contradicting DEC-206's 'omitted severity fails closed' compensating control. Add it to the gating set (or invert to an allow-list) plus a fixture."
    - "plan.yaml:991-993 (T-08 intent) required an assertion pinning severity: unrated as gating-equivalent to high inside test-check-state.py's high-open case; test-check-state.py contains zero occurrences of 'unrated' — the task shipped without its own stated deliverable, and T-08's verify block never checks for it either."
    - "test-check-state.py:2982 case_inv32 is GRADE 1 (cyclomatic 28, cognitive 14, ABC 95.1) against the grade-3 test-code bar; code-grade.py exits 1. Split the nine fixture directions into named helpers."
  spec_violations:
    - { kind: omission, path: ".claude/skills/harness/bin/test-check-state.py", ref: "D-06/T-08" }
  code_grade: fail
  reviewed: "1d3e5db..d0ebbe6"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-45-adversarial-plan-panel/notes/review-harness-code-reviewer-c0.md
```
