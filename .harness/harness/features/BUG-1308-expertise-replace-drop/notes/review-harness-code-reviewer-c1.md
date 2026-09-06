# Code review — BUG-1308 expertise-replace-drop — cycle 1

**Graded at `4c76f0f51a7e8eddc871f5a721d92602762ac103`** (HEAD b4fc4d42 differs only by a
`.harness/harness/features/...` bookkeeping line — confirmed empty diff outside that path).
`git status --porcelain` before my session: clean. After: two untracked sibling artifacts
(`notes/qa-mutation-c1.md`, `notes/review-harness-ui-reviewer-c1.md`) appeared mid-review from
concurrent panel members — not written by me; I made zero commits, stages, or edits.

## VERDICT: FAIL — severity_max: high

Stage 1 (spec compliance) passes cleanly: every REQ/SC is delivered, no scope creep, no omission.
Stage 2 (code quality) fails on two independently sufficient grounds: two test functions T-02 added
are **grade 1** (mechanically below the grade-3 test bar and not grade 2, which the risk-grading
protocol makes an automatic high finding), and a genuine fail-open in the new `add` verb's
resolution that D-03/REQ-05 do not exempt.

## Stage 1 — spec compliance

Per-file record (all seven read via `git show 4c76f0f5:<path>`, never the working tree):

| File | What it yielded |
|---|---|
| `.claude/skills/harness/bin/expertise-merge.py` | The `ops` subcommand, `resolve_ops` and its Step A–E helpers (`:153-536`). Diff vs `origin/main` is **269 pure `+` lines, zero `-`** — confirms REQ-07(a) verbatim. |
| `tests/unit/test-expertise-ops.py` | u1..u16 (no u4, by design). All exist, all PASS when run. |
| `tests/integration/test-expertise-merge.py` | case11..case20 present and PASS; case18 is the concurrency case, verified against production `harness_merge.acquire`. |
| `.claude/skills/harness-distill/SKILL.md` | Ops vocabulary line, refusal token table and the merge-rewrite phrases realigned exactly to what shipped (`:112-143`). T-03's own verify script re-run clean. |
| `.harness/harness/docs/SPEC.md` §5.3 | New paragraphs (`+41` lines) describing the `ops` mechanism accurately, with one citation defect (F-04 below). |
| `.harness/harness/docs/DECISIONS.md` | `DEC-219` entry present, all four labels (`Chose/Over/Because/Tradeoff accepted`), refs DEC-66/95/145. |
| `.harness/harness/docs/DECISIONS-INDEX.md` | `DEC-219` row carries `replace and drop through the ops subcommand` verbatim; `test-gen-decisions-index.py` passes. |

### REQ/SC table

| Req/SC | Status | Evidence (file:line, verified at pin) |
|---|---|---|
| REQ-01/02 replace, drop | delivered | `_rebuild_section` expertise-merge.py:269-283; case11/case12 PASS |
| REQ-03 caps preserved | delivered | `_check_caps` :310-317, once on final state (D-07); u1/u8/u9 PASS |
| REQ-04 missing target | delivered | `_resolve_replace_or_drop` :203-212 → exit 10; u3, case13 PASS |
| REQ-05 ambiguous target | **delivered for replace/drop, NOT for `add`** — see F-03 | `_resolve_replace_or_drop` :213-219, `_check_proposal_ambiguity` :240-252; u5/u6/case14 PASS but no case exercises `add` against an already-duplicated base id |
| REQ-06 byte-identity on refusal | delivered | case13/case15/case20 sha256 before==after PASS |
| REQ-07(a) apply unchanged | delivered | diff is 269 pure additions, 0 removed lines; case16 PASS |
| REQ-07(b) concurrency, deterministic, no bypass | delivered | `case_concurrent_writers` (test-expertise-merge.py:811-895) takes `harness_merge.acquire(<file>.lock)` itself (:829), polls both `Popen` children every 0.05s for 2.0s (:838-846), asserts neither exits, then waits 20s each, checks id census + P-07 marker. No env var/sleep/flag/edit anywhere in the case. Ran it live: PASS. Code quality of this function is a separate Stage-2 finding (F-01). |
| REQ-08 contract/mechanism agree | delivered | `case17`'s `contract_drift` mechanised probe (:696-806) PASS on real SKILL.md and reddens correctly on all three drift copies |
| REQ-09 regression coverage | delivered | u1..u16 + case11..case20 cover every named shape |
| SC-01..SC-12 | all delivered | ran both suites live: unit 0 FAIL/28 files (project-wide), integration 0 FAIL/46 files; `test-expertise-ops.py` and `test-expertise-merge.py` both individually PASS with every named case id present |

No scope creep found: the diff touches exactly the seven files the plan names, nothing else.

## Stage 2 — code quality

### F-01 — HIGH — `case_concurrent_writers` is grade 1 (code_grade: fail)
`tests/integration/test-expertise-merge.py:811`. `code-grade.py --base $(git merge-base origin/main
4c76f0f5) --head 4c76f0f5`: cyclomatic 9, cognitive 12, ABC 47.0 → **GRADE 1**, `RESULT: FAIL`,
`SEVERITY: high`. Test-code bar is grade 3 (harness-code-risk-grading); grade 1 anywhere is an
automatic high finding per that skill's review semantics, no reasoned waiver possible. No receipt in
`notes/` (qa's two T-02 notes, backend-dev's T-01 receipt) discusses code grading at all — this
was never run before now.

### F-02 — HIGH — `case_malformed_ops_cli` is grade 1 (code_grade: fail)
`tests/integration/test-expertise-merge.py:943`. Same tool, same base: cyclomatic 2, cognitive 0,
ABC 60.8 → **GRADE 1**. A flat sequence of three sub-cases (a/b/c), each doing
`write_ops`/`run_ops`/`hashlib.sha256`/`check` — low branching, but ABC alone drives it below grade
2. Same automatic-high rule as F-01.

`code_grade: fail` for this range (two grade-1 records block the build regardless of the med-grade-2
ones below).

### F-03 — HIGH — `add` silently resolves against an ambiguous base id instead of refusing it
`_resolve_add`, `expertise-merge.py:221-237`. D-03 states its ambiguity taxonomy is "two conditions,
no third," condition (a) being *"a target id appearing more than once inside one section of the base
file."* `check-expertise.sh` does not forbid duplicate ids in a section (grepped: no such check
exists), and `case14(b)`/`u5` construct exactly this base shape and treat it as a legitimate fixture
the tool must correctly refuse — but both of those tests exercise it only with `op: replace`, never
`op: add`.

Confirmed live against the pinned module: base `Patterns = [P-01, P-04("four-a"), P-04("four-b")]`
(the same duplicate-id shape `case14b` builds).
- `add P-04 entry="four-b"` (matches the *last* occurrence) → **no exception, outcome PRESERVED** —
  reported as a clean success.
- `add P-04 entry="four-c NEW"` → **exit 7 CONFLICT** naming only the last occurrence's text, never
  mentioning the base file itself is ambiguous.

Root cause: `_resolve_add` does `existing = dict(base_sections.get(section, []))`, which silently
collapses a duplicate id to whichever occurrence is last in file order — the same "guessing which of
two entries was meant" DEC-66 forbids outright, and the one behaviour `_resolve_replace_or_drop`
correctly refuses for the other two verbs on the identical base shape. REQ-05's blanket guarantee
("An operation whose target is ambiguous is refused... and nothing is written") does not hold for
`add`. No case in u1..u16/case11..case20 exercises `add` against a duplicated base id, so this gap
is untested as well as unfixed.

### F-04 — low — SPEC.md's exit-12 citation range excludes one of the four causes it lists
`.harness/harness/docs/SPEC.md` (new table row): *"The payload is not a JSON list, or an op omits a
required key, carries a forbidden one, or names an unknown verb"* cites `expertise-merge.py:153-200`.
That range covers `_malformed`/`_validate_verb`/`_validate_target_section`/`_validate_entry_and_keys`/
`_parse_op` — three of the four causes — but the payload-is-not-a-list check is actually at
`resolve_ops:339` (confirmed via `grep -n "MergeRefusal(1[012]"`), well outside the cited range. A
maintainer following the citation to find that branch will not find it there.

### F-05 (confirms qa's VL-1) — low, non-gating
`u5`/`u6` (unit, AMBIGUOUS TARGET / exit 11) assert only `e.code == 11` — no check of the
section/id/reason wording. That wording contract is fully asserted only at integration,
`case14b`/`case14c` (test-expertise-merge.py:541-548, 561-567): token `AMBIGUOUS TARGET`, the id, the
section name, and `reason=`, plus sha256 byte-identity. Since SC-04's own evidence field is
`unit, integration` (a joint claim, not a per-layer duplication requirement) and the integration half
fully discharges the wording assertion, this placement is adequate for REQ-04/REQ-05 as written.
Confirmed accurate, not gating.

### Grade-2 (med) records, non-gating by themselves
`case_missing_target` (ABC 27.5), `case_ambiguous_target` (ABC 41.6), `case_multi_op_composition`
(ABC 27.2), `case_contract_drift` (ABC 41.6) — all grade 2 in `test-expertise-merge.py`. Per protocol
these need a written reason naming the function; none exists in any T-02 receipt. Not gating alone
(grade 2 never blocks the build), but recorded so a future pass doesn't have to re-derive them.

## What I did not find
No dead refusal branches (D-03/D-04/D-05's three exit codes are each reachable and reached by a real
test); no copy-paste divergence between the unit and integration halves beyond what the plan itself
calls out (u11's reversal vs. case19's non-repeated reversal, by design per D-15/cycle-2 rank 7); no
stale doc phrasing beyond F-04. `merge` correctly stays an authoring-only concept in both the tool and
the contract text (u7, case17 PASS).

## code_grade
`fail` — two grade-1 records in the `merge-base(origin/main, 4c76f0f5)..4c76f0f5` range
(F-01, F-02), both in `tests/integration/test-expertise-merge.py`.

```yaml
VERDICT: FAIL
DIGEST:
  headline: Stage 1 spec compliance is clean, but two new test functions grade 1 and the new add-verb resolution silently mis-resolves an already-ambiguous base id instead of refusing it.
  severity_max: high
  findings: 5
  must_fix:
    - "F-01: tests/integration/test-expertise-merge.py:811 case_concurrent_writers is grade 1 (cyclomatic 9, cognitive 12, ABC 47.0) — below the grade-3 test bar, not grade 2, automatic high finding"
    - "F-02: tests/integration/test-expertise-merge.py:943 case_malformed_ops_cli is grade 1 (cyclomatic 2, cognitive 0, ABC 60.8) — same rule"
    - "F-03: expertise-merge.py:221-237 _resolve_add silently PRESERVEs or wrongly reports CONFLICT(7) against an already-duplicated base id instead of AMBIGUOUS TARGET(11), violating REQ-05/D-03 for the add verb only; confirmed live against the pinned module"
  spec_violations: []
  code_grade: fail
  reviewed: "base..4c76f0f51a7e8eddc871f5a721d92602762ac103"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1308-expertise-replace-drop/.harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-code-reviewer-c1.md
```
