# PASS — F-1 closed; whole-feature review passes

Reviewed `b7af829c0207522b43f978b5275a2ebdc96b3210..7b8e2e1f485db72a4a574e04738533cb0ab821ed`, including the `4a351fae..7b8e2e1f` repair. No human-tagged commits. Dirty tracked files are feature metadata only; pinned-to-live plan difference is `building` → `review`, not implementation. No source changes or full-suite execution by this reader.

## Stage 1 — spec compliance PASS

- **F-1/Q-02 closed, T-01/SC-03:** operator approval in `notes/answers-validate-c2-validator.md` requires salvage; authorized corpus.py now re-reads only strict-refused shipped records with a record path (`.claude/skills/harness/bin/check_state/corpus.py:145-164`). Existing branch normalization/collision logic consumes the recovered mapping. Active strict-refused records retain their previous behavior. INV-52 declares its new plan read (`check_state/table.py:166`).
- **SC-01 inspection:** classification and subject filtering precede artifact loads (`check_state/ctx.py:55-76,223-233`); ambiguous or unreadable status remains checked. DEC-252 governs text-line classification; Q-01 remains below.
- **SC-02 inspection:** existing preflight precedes the one-note explicit shipped exit (`check_state/runner.py:313-323`). Full/changed subjects share the context filter. Integration audit-hook assertions bind real opens, with active-read presence controls; real-corpus mode requires a nonempty shipped population.
- **SC-03 inspection:** issue claims are lazy comparison data, with unusable numbers contained and active grading preserved (`check_state/ctx.py:423-452`; `board.py:137-158,191-269`). Sparse population retains landed records and local replacement, never in-progress siblings. INV-29 remains independent of filtered subjects (`worktrees.py:317-333`). Missing/unreadable comparison JSON intentionally contributes no claim; corpus-access failure still reports CANNOT VERIFY.
- **SC-04 inspection:** INV-28/30 implementations, helpers, imports and rows are removed; numbers are retired (`table.py:240-245`). Search across `.claude` and `tests` finds no obsolete implementation callers. Fixture migrations preserve current checks rather than keeping done-only enforcement. Documentation/schema-description changes serve this cutover. No scope creep or missing criterion found; amendments serve BRIEF/DEC-252.

## Stage 2 — quality PASS; measured evidence

- Independently ran pinned `code-grade.py --base b7af829c0207522b43f978b5275a2ebdc96b3210 --head 7b8e2e1f485db72a4a574e04738533cb0ab821ed`: **PASSING: 62**, exit 0; no high or grade-2 records.
- Independently executed only `ComparisonsKeepShippedRecords.test_inv52_keeps_the_branch_of_a_shipped_record_the_strict_loader_refuses`: **1 test OK**, exit 0. Its subprocesses cover full and sparse checkouts, requiring the exact shared-branch collision and absence of shipped parse grading. Production/test bytes match the pin; no isolated reader checkout created.
- `notes/red-first.md:85-93` records baseline/c2 FAIL → repaired PASS; those red runs are retained evidence, not independently rerun here. Positive collision assertions prevent the negative parse assertion passing vacuously.
- Independently diffed `7b8e2e1f..8cdbb3620037f9fd8c86621225fcaedd9555edaa`: only feature.json review_sha/regate metadata changes. The latter's merge log ends with **146 files**, **verify-exit=0**. This establishes equivalent-code historical verification, not literal exact-pin verification; current exact-pin gates belong to QA. Known INV-26/33 station drift is not a new finding.

## Open questions

**Q-01, nonblocking:** owner should align T-01 YAML-mapping/invalid-YAML prose with adopted DEC-252 text-line classification; retain implementation behavior. Product `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` remain absent as disclosed; approved BRIEF, settled grilling and DEC-252 were used, not unrelated substitutes.

## Principles applied

- **Migrate Callers, Then Delete Legacy APIs:** retirement removes callers and old enforcement together, without aliases.
- **Model the Domain:** shipped population metadata is derived at the comparison seam; no second independently maintained status flag or per-invariant subject exemption was introduced.
