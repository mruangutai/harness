# Plan panel — BUG-1303, cycle 3 — scope reader

**BLUF: PASS, zero findings.** All three cycle-3 remedies (S-4, A-6, A-7) verified CLOSED against
the plan text itself, not the repair note's claim. Re-running the standing scope questions
(orphan REQ, dangling `traces:`, `depends_on:` topology, verify/intent literal identity) against
the changed text found nothing new. No new finding this pass.

## S-4 — CLOSED

`PF-87f1837ea32b6a51a980a10d527431fc` was mine at cycle 2: a `CONTRACT_SOURCES` entry present but
mapped to an EMPTY list looped zero times and emitted no line — neither pass nor named failure.

Checked myself, this cycle:
- `plan.yaml:257-259` — step (4)'s grading spec now states explicitly: an entry "PRESENT but whose
  list of sources is EMPTY takes this same branch and is reported by name the same way: an empty
  mapping is an unmapped persona, never a zero-iteration silent pass."
- `plan.yaml:345-346` — step (7b)'s six-assertion list (not five, as cycle 2 recorded before the
  repair) now carries, as its own numbered bullet: "a roster persona whose entry in the synthetic
  map is an EMPTY list yields that same failure line NAMING that persona, never zero lines." This is
  a genuine synthetic-input assertion inside `run_documented_contract_cases`'s one call to
  `documented_contract_results` — demonstrated, not merely described, matching every other branch in
  (7b).
- `plan.yaml:355` (intent quote) vs `plan.yaml:192` (T-01 `verify:` grep target) — I extracted both
  strings programmatically and diffed them: byte-identical, `'ok    [documented contract
  completeness] unmapped persona, absent source, unlocatable block and out-of-block field each
  reported by name'`. The line was deliberately left unchanged rather than reworded for six
  assertions (`plan.yaml:356-358` states this explicitly); I judge it still reads truthfully — it
  names failure *categories* ("unmapped persona"), and the empty-list case is the same category as
  the missing-entry case, not a seventh category the line fails to disclose. No overclaim.

## A-6 — CLOSED

`PF-9c43910b2d2e6e14595b28a0c264a7f9`: T-01 step (5) hand-mirrors `validate()`'s inline
`code_grade`/`reviewed` schema extension; T-04's decision entry had to scope "checked mechanically"
correctly and name the mirror site.

Checked: T-04 intent (`plan.yaml` T-04 body) now reads verbatim — "what is checked is the required
fields of validate-digest.py's SCHEMAS for each persona PLUS the reviewer's known inline per-persona
extension, code_grade and reviewed... The entry must NAME the guard's own `required_by_persona`
construction in `run_documented_contract_cases`... as the hand-written mirror of that inline
extension, so any future inline schema extension in validate() must update that site or the guard
silently under-checks the persona it extends." This is the exact scoping and naming the dispatch
asked me to confirm — present, word for word in intent. T-04's `verify:` (`grep -qF "documented
output block" ... && gen-decisions-index.py --stdout | diff -q -`) is consistent with what the
intent now requires it to write: the mechanical-scoping sentence and the `required_by_persona`
citation are prose content graded by SC-06 at `verify: inspection` (BRIEF.md), not by a second
literal grep — correctly, since their exact wording is deliberately left to the documentor's voice
("Chose-and-why voice... under twenty-five lines") while only the required phrase `"documented
output block"` is pinned mechanically. No mismatch between verify and intent.

## A-7 — CLOSED, no traceability defect from the shrink

`PF-49abc17456e3e70e647d1f831bf115d3`: nine `.claude/agents/<persona>.md` duplicate mappings
dropped from `CONTRACT_SOURCES` (step 3, `plan.yaml:234-246`), each of those nine personas now maps
to exactly ONE source, the canonical `.omp/agents/<persona>.md`.

Checked for traceability fallout:
- No REQ or SC loses a task. `REQ-01`→T-02,T-03; `REQ-02`→T-01,T-02; `REQ-03`→T-03; `REQ-04`→T-01;
  `REQ-05`→T-04 — every REQ-01..05 traced, none orphaned, none doubled without cause.
- SC-05 (per-persona completeness, `CONTRACT_SOURCES` gaps reported by name) is unaffected: the
  shrink removes a *redundant* second mapping, not a persona's only mapping — all sixteen registry
  personas (`sorted(validator.ALIAS)`) still resolve to at least one real source.
- T-01's `verify:` (case 6, plan-mode composites) still asserts the three reviewer-specific sources
  — `.claude/agents/harness-code-reviewer.md`, `.omp/agents/harness-code-reviewer.md`,
  `.claude/skills/harness-code-review/SKILL.md` — independently of `CONTRACT_SOURCES`; the intent
  states plainly "step (6)'s three reviewer sources are not CONTRACT_SOURCES and are unchanged"
  (`plan.yaml:241`). So dropping the `.claude` duplicate from the generic completeness map does not
  touch the D-06 artifact-fragment guard on both copies (the fix for cycle-2's `[A-5]`, confirmed
  present at T-02's `verify:` — both `! grep -qF` absence clauses against the old path, on both
  files).
- The structural argument for the shrink (`D-07`: `sync-agent-adapters.py --check` compares bodies
  full-file across all 16 pairs and is already wired into `check-omp-port.py:156-166`) is an
  orchestrator-measured fact I did not re-derive; I did re-run `sync-agent-adapters.py --check`
  myself in this worktree and got rc 0, consistent with it.

## Standing scope questions, re-run — nothing new

- Orphan REQ: none (see REQ trace list above).
- Dangling `traces:`: none — every task's `traces:` cites an existing `REQ-NN`.
- `depends_on:` topology: `T-01:[]`, `T-02:[T-01]`, `T-03:[T-01,T-02]`, `T-04:[T-01]` — a valid
  topological order; `T-04`'s prior `depends_on: T-03` (cycle-2 `[S-d37f710e]`) is now `[T-01]` only,
  correctly, since T-04 is a record-integrity dependency on T-01 alone.
- `verify:` asserting a literal a predecessor deletes: none found — T-02/T-03 only add content T-01's
  guard checks for; nothing removes text another task's verify depends on.
- Tasks serving no live requirement: none — all four tasks trace to a REQ none of which is
  duplicated elsewhere.

## Anomaly

The known host hazard (worktree PWD defaulting to the main checkout) did not manifest for me this
pass — I `cd`'d to the worktree root explicitly before every read and command, and my structured
`yield` below reports `reviewed: plan:<abs worktree path>`. Recording per instructions in case the
host still refuses it downstream.
