# FEAT-2229 code review — c5

**PASS. T-01 / SC-02: SEC-C4-01 is closed by pinned inspection; the authorized delta introduces no identified correctness or maintainability regression. Code-grade passes with 101 passing function records.**

Reviewed `dfa52536..c163d5ea0fb17da27b3455559f317d67852981c7`, concentrating on c163d5ea's +8/-2 scanner change and +32 test lines. Read BRIEF, plan decisions/T-01 and the operator's c4 ruling before the diff; consulted PRODUCT/AGENTS.md and designated SPEC/DECISIONS/INDEX authorities. No absent product contracts invented. Full-range history has no human-tagged or foreign-feature commits. Shared tracked dirt is feature.json bookkeeping only; its live review_sha matches dispatch. Measured c163d5ea..e220cde8: feature.json only (8 insertions, 1 deletion); branch tip was not reviewed or executed.

## Stage 1 — SC-02 compliance

- **SC-02 inspection, owner T-01:** `.claude/skills/harness/bin/plan_merge/check.py:209-212,280-288,332-340` requires the complete escaped DEC identifier followed by an explicit delimiter. Letter, digit, underscore, dot and joined-hyphen continuations cannot resolve DEC-10. A wrong heading remains a section boundary but cannot supply the named decision's section. No match returns None, and `:369-383` emits the clause diagnostic rather than accepting it.
- `tests/integration/test-plan-decision-dispositions.py:386-414,679-695` adds actual-CLI M6 cases in both directions, M8 tilde/backtick-info coverage, four identifier-spoof cases and genuine-heading controls. `_spoof_and_control` at `:337-343` binds both spoof rejection and genuine-clause acceptance; `expect_fail` at `:188-192` requires exit 1 and row/DEC plus clause diagnostics. Reverting the boundary permits the spoof section and rejects the genuine control by inspection. No mutation or test execution is claimed here; independent red-first/mutation acceptance belongs to QA.
- Every delta serves SC-02 and the explicit operator ruling. No scope creep, omission or mismatch identified. SC-01/03–07 and DEC-188 retain their c4 assessments; they were not re-graded here. The following required inspection pointers carry forward from `notes/review-harness-code-reviewer-c4.md`; c163d5ea does not alter these subjects:
- **SC-04 inspection met, carried from c4:** `.claude/skills/harness/teams/plan.yaml:59-66,103-108`, `.claude/skills/harness/templates/plan.yaml:75-86` and `.claude/skills/harness/references/patch-lane.md:20-22` require the five-field block/check, independent omission and DEC-188 review, and panel-free patches.
- **SC-05 inspection met, carried from c4:** `.omp/agents/harness-pm.md:58-82`, `.claude/skills/harness/teams/validate.yaml:120-121` and `.omp/agents/harness-validator-lead.md:104-105` require individual pinned amend/strike grades, skip keep, delegate Mode 2 and preserve owning-task failure routing.
- **SC-06 inspection met, carried from c4:** `.harness/harness/docs/DECISIONS.md:5313-5336,8253-8326`, `.harness/harness/docs/DECISIONS-INDEX.md:237` and `.harness/harness/docs/SPEC.md:2009-2043,2287-2302` record DEC-254, amend DEC-188, resolve the new decision and reuse the five-field/sc_status contract without a new validate script.

## Stage 2 — quality

The shared `DEC_ID_END` lookahead changes identity matching only, without consuming the separator or changing fence state/section bounds. Space, tab, colon, opening parenthesis, em/en dash, whitespace-followed hyphen and bare line-end headings remain accepted by inspection. `_read_text` uses universal-newline text input and `_Authority` retains line endings via splitlines: CRLF becomes LF on the real file-read path, which the lookahead accepts. No extra parser, wrapper, mutable state or allocation-heavy path was added. Existing Unicode-whitespace and list-container scanner advisories remain operator-backlogged, not newly gated or claimed fixed.

Required verification ran once in the managed persona checkout, before the Python quality review:
`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/code-grade.py --base dfa52536 --head c163d5ea0fb17da27b3455559f317d67852981c7`
Result: **exit 0; PASSING: 101**, no high or grade-2 records. The four new test helpers/cases grade 5; `_heading_level` grades 4. Counts are grader-reported function records, not a claim that every changed function is listed. No tests, suites, builds, lint, formatters or runtime probes ran. Managed reviewer checkout removed successfully.

Findings/must-fix/open questions: none. C4-QA-CONTRACT, Unicode/list-container advisories, SIMPLIFY B-1/B-2 and create:true plan-check remain unchanged backlog under `notes/answers-2026-11-22-c4-ruling.md`. No production/test edits.
