# Pinned code review — FEAT-1821 — c8

**BLUF:** PASS. Both review stages pass for the T-01 c8 repair at immutable pin `0163657540ab3ad3be4ff5aa34f838dc4f1e17d8`; V7-01 and V7-02 are closed without a new substantive defect.

## Scope

Reviewed the T-01 source, test, and receipt delta in `b8f96ab8e9c8168ed8389ccf4732a958e84828fd..0163657540ab3ad3be4ff5aa34f838dc4f1e17d8`:

- `.claude/skills/harness/bin/ui_contract.py`
- `tests/unit/test-ui-verification-contract.py`
- `.harness/harness/features/FEAT-1821-ui-verification-lane/notes/receipt-main-direct-T-01-c8.md`

Excluded from code-quality scope as intervening governance/validation records: `STATE.md`, `feature.json`, `plan.yaml`, `notes/answers-validate-c7.md`, the three c7 reader notes, and `runs/validate-c7-final-validator/**`. Commit `59cee0890fdcbcdaed7423fe4fb694162c6f5aaf` is the governance-only `[harness:human]` commit in the range. Uncommitted changes are confined to `.harness/**` and do not alter the pinned bytes reviewed.

## Stage 1 — spec compliance: PASS

The repair implements the operator ruling in `notes/answers-validate-c7.md` and preserves D-04 / SC-11's complete-package rule. Literal title scanning remains authoritative when no execution record supplies a title. For manifest-driven specs, `_executed_titles` contributes only titles carried by results records with screenshot entries; the existing record, applicability, exact-title, status/error, coverage, screenshot path/size/WebP, accounting, identity, and summary checks still independently reject malformed, absent, errored, non-applicable, unevidenced, or inconsistent records. Thus those records cannot turn the overall gate green. The focused test proves the manifest-driven complete bundle passes, a title absent from both source and results is named and refused, a literal title remains accepted, and an out-of-package change does not invoke the rule.

The c8 receipt is complete and honest for the authorized repair. The repository history confirms `624eb59a` introduced T-01 (so `624eb59a^` lacks the module), `9adb6c58` is the pre-c7 T-01 completion point, `0af450c5` is the pre-c8 implementation, and the pin is the c8 commit. The receipt maps T-01's SC-05, SC-06, SC-10, and SC-11 to concrete current tests and records the later c7/c8 mutants at their own pre-fix trees. Its treatment of SC-02, SC-03, and SC-04 as runner/reporter work owned by T-03/T-06/T-13 matches the signed plan; it does not falsely claim those criteria as T-01 fail-first coverage.

## Stage 2 — code quality: PASS

No fail-open or silent-failure path was introduced. The new helper is narrow and the gate continues to accumulate all structural/evidence reasons before deciding PASS. `_executed_titles` itself does not validate evidence, but every contributed record is subsequently subjected to the existing fail-closed record and screenshot validators before the final verdict; invalid evidence can suppress a redundant “no spec carries” reason but cannot suppress the substantive refusal. The c8 Python changes grade cleanly: `_executed_titles` grade 5, the changed contract test grade 4, and its nested mutation helper grade 5.

## Scoped evidence at the pin

- Exact T-01 verify: `python3 tests/unit/test-ui-verification-contract.py` → exit 0; 24 tests, OK.
- `code-grade.py --base b8f96ab8e9c8168ed8389ccf4732a958e84828fd --head 0163657540ab3ad3be4ff5aa34f838dc4f1e17d8` → 3 changed functions, all PASS.
- Gate over committed `FEAT-1821-initial-red` evidence with a client-package change → expected exit 1 for the intentional FEAT-53 product/setup RED; no `no spec carries` refusal appeared. This closes V7-01 without reclassifying the intentional RED as a feature defect.

```yaml
VERDICT: PASS
DIGEST:
  headline: "T-01 c8 closes V7-01 and V7-02 at 01636575: manifest-driven titles pass only through independently validated execution evidence, and the fail-first receipt matches signed task ownership."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "The repository-wide pinned grade remains grade_2 only for pre-existing test helpers identified in c7; every Python function changed by c8 grades 4 or 5."
  reviewed: "b8f96ab8e9c8168ed8389ccf4732a958e84828fd..0163657540ab3ad3be4ff5aa34f838dc4f1e17d8"
  human_commits_in_scope:
    - 59cee0890fdcbcdaed7423fe4fb694162c6f5aaf
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c8.md
```
