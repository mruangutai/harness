# FEAT-65 pinned code review — cycle 0

## Verdict

FAIL at Stage 1 (spec compliance). Stage 2 code-quality review was not performed. The mandatory mechanical Python grade was recorded separately and does not constitute Stage 2.

## Stage 1 — spec compliance

### CR-01 — executable broad catch survives inside a scoped hook

- **SC / decision:** SC-03, SC-04, SC-06; D-01
- **Pinned site:** `.claude/skills/harness/bin/branch-create-gate.py:84` at `75a36628079ab1b37f7bd53f3100bde7305a8133`
- **Task:** T-03 owns the hook treatment; T-04 owns the census that should detect it.
- **Kind / severity:** substance / high
- **Defect:** `_CONFIG_READER` is executable Python passed to an isolated child interpreter, but it still contains `except Exception:`. The AST census parses only the carrier module, so it reports this hook as having zero broad catches while executable hook code retains one. This contradicts the typed-boundary classification for branch-create-gate's configuration load and the complete zero-catch claim.
- **Failure scenario:** a non-mapping `github` value enters `_github_config`, which invokes `_CONFIG_READER`; if an unrelated programming defect raises inside that reader (for example `json.load` is changed or injected to raise `RuntimeError`), line 84 absorbs it and returns `false -` exactly like an expected unreadable configuration. The defect therefore sails through silently rather than remaining loud, and the shipped census still reports zero.
- **Satisfying remedy:** narrow the embedded reader to the expected file/JSON/shape boundary failures, and make the census inspect executable embedded Python (or remove the embedded reader while preserving the established outcome). Add a discriminating case where an expected malformed configuration retains its result and an unrelated exception is not absorbed.

SC-01, SC-02, SC-05, SC-07, SC-08, SC-09, and SC-10 showed no independent Stage-1 mismatch in the pinned diff and five supplied evidence artifacts. CR-01 prevents SC-03, SC-04, and SC-06 from passing, so review stops before Stage 2 as required.

## Pin reconciliation

- Reviewed immutable range: `4e8c73c07e5f1f102c392fe3800616fc94a1c53d..75a36628079ab1b37f7bd53f3100bde7305a8133`.
- No `[harness:human]` commits occur in the range.
- The only worktree modification reported was the Harness-owned feature record `.harness/harness/features/FEAT-65-broad-exception-hooks/feature.json`; no tracked implementation file was dirty.
- Mandatory mechanical grade: `grade_2` because `tests/unit/test-harness-boundary.py:1017 case_hook_guard_contract` requires a grade-2 reason. This is not a Stage-2 quality judgement.

## Principles applied

None.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "Stage 1 fails: branch-create-gate ships an executable embedded `except Exception` that the zero-catch census cannot see."
  severity_max: high
  findings:
    - kind: substance
      scope: task
      severity: high
      reader: code-reviewer
      summary: "CR-01: branch-create-gate.py:84 retains an executable broad catch while the census reports zero."
      why: "An unrelated defect in the isolated config reader is silently converted to `false -`, violating SC-03/SC-04/SC-06 and D-01."
  must_fix:
    - "CR-01 (T-03/T-04): narrow or remove branch-create-gate.py:84's embedded broad catch and make the census cover executable embedded Python; retain expected config behavior while proving an unrelated exception stays loud."
  spec_violations:
    - kind: mismatch
      path: .claude/skills/harness/bin/branch-create-gate.py:84
      ref: SC-03
    - kind: mismatch
      path: .claude/skills/harness/bin/branch-create-gate.py:84
      ref: SC-04
    - kind: mismatch
      path: .claude/skills/harness/bin/branch-create-gate.py:84
      ref: SC-06
    - kind: mismatch
      path: .claude/skills/harness/bin/branch-create-gate.py:84
      ref: D-01
  code_grade: grade_2
  grade_2_reasons:
    - "tests/unit/test-harness-boundary.py:1017 case_hook_guard_contract is a cohesive contract matrix for success, open failure, closed failure, process-control escape, and the exact guarded-hook set; its ABC score reflects adjacent assertions, while cyclomatic 7 and cognitive 2 remain straightforward."
  reviewed: "4e8c73c07e5f1f102c392fe3800616fc94a1c53d..75a36628079ab1b37f7bd53f3100bde7305a8133"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-65-broad-exception-hooks/.harness/harness/features/FEAT-65-broad-exception-hooks/notes/review-harness-code-reviewer-c0.md
```
