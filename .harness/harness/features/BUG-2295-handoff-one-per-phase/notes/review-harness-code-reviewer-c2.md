# Code review — BUG-2295 — c2

PASS: the consolidated c1 mixed-case bypass is closed at `7d76c1cea576822760e8bc42432f8c01fc3c8031`. No findings or must-fix; T-01 remains main-session-direct.

Reviewed `dd04e52a898109fdbe09cf5fa14e1148161734d0..7d76c1cea576822760e8bc42432f8c01fc3c8031`; prior pin `253cdf2aedf8f1b40fe712aa4e9301cdb764bf34`. Git merge-base confirms base and fix `c4c93ef1fdbcb3b047c14eabe964c6a47cd30c57` ancestry. Fix-to-pin diff over `.claude/skills/harness/bin` and `tests` is empty. Current feature.json binds the dispatched pin; its tracked modification is feature metadata only. Full commit census found one human commit: `2f8fe5f3bca8` (operator signature, rework 1 round / 45 min, main-session-direct T-01).

## Stage 1 — spec compliance

Read BRIEF, plan decisions (empty), T-01, red-first evidence and c1 validator digest before the diff. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent per intake; no substitute authority used. All executable/test changes serve SC-01/02; the only other production change is the SC-03 comment.

- SC-01/02: pinned `.claude/skills/harness/bin/check-domain.py:2296` compiles `_RE_HANDOFF_CYCLE` with `_I`; line 2315 lowercases the canonical diagnostic. Existing case-insensitive `RE_HANDOFF` at line 1486, rule dispatch at line 2407 and Edit reconstruction at lines 2632–2660 remain intact. Valid mixed-case cycle targets now reach the same refusal through Write and reconstructable Edit; cap, sections and Done when checks remain at lines 2301–2305.
- Pinned `tests/integration/test-check-domain-post.py:913–951` covers canonical build/validate/plan acceptance, cycles 1/12/305, and Build-c1/build-C1/VALIDATE-C12 through both tools. Refusal asserts exit 2, supersede guidance and the exact case-sensitive lowercase canonical path. Removing `_I` breaks mixed-case refusal; removing `.lower()` breaks exact-path assertions (static discrimination, not an executed mutant). Existing grammar, cap and Done when cases remain invoked at lines 970–978. Unchanged-file controls alone do not establish refusal; exit/message assertions do.
- SC-03 inspection: `.claude/skills/harness/bin/gh-sync.py:2586–2590` at the pin distinguishes the preventive ship prerequisite from DEC-252's shipped-feature exemption and names the shared exemption predicate.
- SC-04 inspection: `.claude/skills/harness/bin/gh-sync.py:2594–2602` at the pin retains byte-identical predicate, exemption call and diagnostics versus base dd04e52a; the complete file diff changes comments only, preserving executable side effects. No paths under FEAT-2225 or FEAT-2229 changed, including the specified historical c2/c3/c5 and c3/c4/c5 handoffs. No history migration or recorded-run ship predicate was introduced.

## Stage 2 — quality

Ran only mandated pinned `code-grade.py --base dd04e52a898109fdbe09cf5fa14e1148161734d0 --head 7d76c1cea576822760e8bc42432f8c01fc3c8031`: PASSING 4, no high or grade-2 records. Cyclomatic/cognitive/ABC: `_handoff_cycle_problems` 2/1/4.1 (grade 5); `_handoff_cycle_suffix_cases` 3/2/6.7 (5); `_record_cycle_refusal` 1/0/3.3 (5); `_handoff_cycle_refusal_case` 1/0/17.5 (4). Code grade: pass. No independent correctness or maintainability defect found.

## Principles applied

- Delete First: retained the existing shape-rule seam and broad routing; no parallel gate or history rewrite.
- Model the Domain: filename recognition and canonical guidance stay local to one rule, without new phase state or synchronized flags.

No source/test edits, tests, mutants, builds, lint or formatters run. QA owns execution of the existing gate verbatim: `set -eu` then `python3 tests/integration/test-check-domain-post.py`. Red/green counts in red-first evidence remain main-session claims, not this review's execution. Pre-existing DEC-252 commentary discrepancy is outside T-01 and not a finding. C1 artifacts preserved. Receipt-only corrections clarify explicit SC-04 path:line and human-commit identifier; no substance change.

Open questions: none.
