# QA gate — BUG-2241 T-01 (run 2026-11-21-02-validate-validator, pin 64fdc2dd)

**BLUF: PASS.** T-01 verify (verbatim from plan.yaml:28-29) exits 0 at review_sha in the managed pinned checkout; same SC-01 assertion fails on base 594af2a8. matrix_ok true (docs floor empty).

## Phase 1 (from BRIEF/plan only)
Expected: one automated test of SC-01 (complete rule text inside the verify literal-block section, read via `git show <sha>:path`, red on base, green on pin); SC-03 word count 1137->1181. SC-02/03 are inspection (not mine). No unit-runner coverage expected: inline assertion is not discovered by the registered runner.

## Results
- Verify at REVIEW_SHA=64fdc2dd, pinned checkout: exit 0. `PASS SC-01 content; SC-03 skill words 1181 (+44)`; check-skill-weight plain output: no VIOLATION.
- Preload measured: pm 5045 (base 5001, +44), universal 1476, eng-lead 4924, qa 3494, total 57167/16 agents. Under budgets agent 5500 / universal 1900.
- Words measured: base 1137, pin 1181 (+44).
- Source-only diff base..pin outside `.harness/`: exactly `.claude/skills/harness-spec-driven/SKILL.md`, +4/-0 lines (one paragraph, 44 words, inserted after verify literal-block paragraph, before "The panel result"). `.agents/skills` is a symlink to `.claude/skills`. No detector/runtime/UI change.
- Command cross-check: plan.yaml:28 command text and the executed command identical; line 29 check-skill-weight invoked with `.` from the pin.
- Fail-first: receipt `notes/receipts/red-base.txt` shows `AssertionError: SC-01: complete durable-state id rule absent from verify section` (assertion, not load error; semantic, not signature-only). Gap: the receipt does not record the ref/REVIEW_SHA it ran against. I therefore reproduced once myself: `REVIEW_SHA=594af2a8 <same command>` -> exit 1, same SC-01 AssertionError (it fails on the rule assertion before reaching the word count). Evidence tier: own reproduction at base; cites receipt as the retained capture.
- Named assertion: `assert rule in " ".join(section.split()), "SC-01: ..."` in T-01 verify (plan.yaml:28). Section is bound to the "literal block" heading, so the rule cannot be satisfied by an unrelated section (P-11 checked). Whitespace-normalised, so line wrapping is tolerated.

## Kinds
Docs matrix floor: empty -> `kinds: []`-equivalent; unit supplemental only. The registered unit runner does not discover this inline assertion; I did not run it (unrelated, cannot discharge SC-01).

## Gaps / notes
- Receipt red-base.txt lacks ref binding (advisory; own repro closes it).
- check-skill-weight `--json` NameError is out of scope (BUG-2239); not run.
- No source/test authoring; pin removed on return.
