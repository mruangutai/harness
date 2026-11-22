# Code review — BUG-2295 — c1

FAIL: the new filename check has a case-sensitive bypass inside the existing case-insensitive handoff route. T-01 owner: main-session-direct (DEC-174).

Reviewed dd04e52a898109fdbe09cf5fa14e1148161734d0..253cdf2aedf8f1b40fe712aa4e9301cdb764bf34; sources read with git show at the pin. The only dirty tracked path was this feature's feature.json (validation bookkeeping). Human commit in scope: 2f8fe5f3, operator signature.

## Stage 1 — specification

The lowercase filename cases and retained canonical/cap/section/Done when coverage implement SC-01/02 (tests/integration/test-check-domain-post.py:909–965). No unrelated production changes or amendments found.

SC-03 inspection PASS — .claude/skills/harness/bin/gh-sync.py:2586 distinguishes the preventive ship prerequisite, DEC-252's shipped-feature exemption, and the shared DEC-174 exemption; no INV-17-at-done claim remains.

SC-04 inspection PASS — .claude/skills/harness/bin/gh-sync.py:2595 preserves the executable predicate and exemption call byte-identically: the complete base-to-pin file diff changes only the preceding comment, with diagnostics and side effects unchanged. The complete name-status diff contains no FEAT-2225 or FEAT-2229 paths, hence their specified c2/c3/c5 and c3/c4/c5 notes are untouched.

## Stage 2 — quality

F-01 — substance / high / T-01 / owner main-session-direct: .claude/skills/harness/bin/check-domain.py:2296 compiles _RE_HANDOFF_CYCLE without the existing _I flag. A valid notes/handoff-Build-c1.md reaches _rule_handoff through case-insensitive RE_HANDOFF (1486), but fails the new lowercase-only regex and therefore receives no filename refusal. The same bypass applies to reconstructable Edit (2632–2660). _norm preserves case (1405–1413). With otherwise valid content, both routes accept the cycle note instead of directing supersession. This is an inspection-proven control-flow defect, not an executed probe. Use the routing pattern's case policy in the refusal and add Write/Edit regression coverage for the alternate spelling (SC-01/02); no plan upgrade is needed.

Python risk grader, explicitly run over the pinned range: PASS; _handoff_cycle_problems grade 5 (CC 2, cognitive 1, ABC 3.5), _handoff_cycle_suffix_cases grade 3 (CC 3, cognitive 2, ABC 23.0). No gated records. Mechanical grade does not clear F-01.

No tests, builds, lint or formatter executed. QA/main owns final T-01 integration verification. Existing added assertions bind real hook output and literal canonical guidance; preserved no-mutation assertions are supplementary, not refusal proof.

## Principles applied

- Model the Domain: compare the refusal's accepted spelling domain with the existing handoff routing domain; the mismatch creates F-01.
- Delete First: retain the existing route and content checks; the remedy belongs in the new filename predicate, not another enforcement layer.

Open questions: none.
