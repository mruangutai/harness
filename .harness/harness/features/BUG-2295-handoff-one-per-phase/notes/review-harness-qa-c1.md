# QA gate — BUG-2295 T-01 — pin 253cdf2a vs base dd04e52a (run qa-c1)

BLUF: matrix_ok true. Fail-first for SC-01 and SC-02 reproduced by me: pinned tests over baseline check-domain.py went RED with exactly 6 assertion FAILs, then GREEN at the pin. Phase 1 (BRIEF+plan only) expectation: refusal of suffixed names for several phases and multi-digit cycles via Write and Edit, canonical accepted, existing checks retained. All covered; no gaps.

## Matrix
change_type bugfix -> always []; when unit if touches_runtime_code, integration if fix_confined_to_tests_and_contract_docs. Diff touches check-domain.py and gh-sync.py (runtime scripts), so unit is triggered; integration is the task verify and the BRIEF-required kind. Both run.

## Per-kind results (env -u HARNESS_AGENT_TYPE, exit codes captured)
- integration T-01 verify `python3 tests/integration/test-check-domain-post.py` at pin: rc=0, 96 ok, 0 FAIL lines.
- unit `run-unit-tests.py --kind unit` at pin: rc=0, 63 files, "Ran 131 tests ... OK". Per-file: every file PASS (test-feature-record.py slowest, 22.6s). The printed 'FAIL BUG-1290 5a/5b/5c' and 'ERROR could not resolve scan root' lines are deliberate captured diagnostics from a mutation-proof/negative fixture, not suite failures (G-09); the runner exit code governs.
- integration `run-unit-tests.py --kind integration` at pin: rc=0, 91 files, every file PASS ("OK").
- component/ui/typecheck: null runners, not gaps. eval/functional excluded (DEC-187). locally_run kinds: handoff_comprehension probe not touched (note contents unchanged), not_applicable.
- Note: integration is the kind this change binds; unit kind ran green but no unit test directly exercises check-domain handoff rule — the binding evidence is the integration file (P-04). Reported as satisfied for integration; unit reported locally_run-equivalent "ran green, no named test for this change".

## fail_first (SC-01, SC-02; natural RED, tier: baseline production + pinned tests)
Isolation: second pinned checkout of 253cdf2a (key harness-qa-base) with only .claude/skills/harness/bin/check-domain.py restored to dd04e52a via `git checkout dd04e52a -- <file>`; product tree untouched. Command: `python3 tests/integration/test-check-domain-post.py`.
RED rc=1, 90 ok, 6 FAIL (assertion failures, "exit 0" where exit 2 wanted — semantic, not setup):
  handoff build-c1 Write refused / Edit refused; validate-c12 Write refused / Edit refused; plan-c305 Write refused / Edit refused.
Controls ok at baseline: canonical build/validate/plan accepted; the three "refused Edit leaves file unchanged" rows (a pre-hook never writes, so they are not discriminating).
GREEN at pin rc=0, 96 ok, 0 FAIL; all 12 new rows ok.
Raw logs: /tmp/qa-red.out (102 lines), /tmp/qa-green.out (102 lines); matches notes/red-first-T-01.md claim.
SC-01: tests at tests/integration/test-check-domain-post.py `_handoff_cycle_suffix_cases` (Write rows, needles notes/handoff-<phase>.md and "supersede").
SC-02: same function Edit rows with existing suffixed target; retained cap/missing-section/Done-when rows (ok in green: "SWEEP reaches and enforces handoff cap", "handoff Done when missing", "handoff edit without Done when").

## Assurance limits
- Discrimination shown for the filename rule only through the six reds; the canonical-accept and unchanged-file rows are baseline-green (discrimination unshown, not useless).
- Only three phases/cycles (1, 12, 305) sampled; leg for names like handoff-x-c without digits or `-c1a` is not tested (no BRIEF requirement).
- SC-03/SC-04 are inspections, not graded by me.
- Raw logs live in /tmp; this note is the durable record.
