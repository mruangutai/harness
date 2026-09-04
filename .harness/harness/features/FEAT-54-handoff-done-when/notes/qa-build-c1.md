# FEAT-54 build QA gate — c1

## Verdict

**FAIL.** Both configured matrix commands pass at `d32df480271390e3bfdfc8e3ca921f0c9b695ed4`, and the executor's same-session transcription is acceptable TDD evidence without an operator waiver. Three c0 assertion gaps are closed. SC-02 remains under-bound: the five-Authority case checks the bare substring `"5"` across all stderr, while every refusal already contains the header `DEC-159`; that case stays green if the count is omitted or wrong.

## Matrix evidence

| Kind | Exact configured command | Result | Discovery |
|---|---|---|---|
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 0 | 24 files; `test-handoff-done-when.py` discovered; 32 named cases passed |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0 | 44 files; zero failed scripts; `test-check-state.py` discovered and passed |

`HARNESS_AGENT_TYPE` was unset around both invocations because the repository environment otherwise contaminates the suite; command arguments and selection were unchanged. The full integration runner's captured output did not retain `test-check-domain.py`'s very large successful output, so its discovery is established by the runner's `tests/integration/test-*.py` glob (`run-unit-tests.sh:25-27`) and a separate direct run: `python3 tests/integration/test-check-domain.py` exited 0 with all 22 FEAT-54 handoff cases named. A separate direct `python3 tests/integration/test-check-state.py` exited 0 with all 11 FEAT-54 cases named.

## Corrective assertion assessment

- **SC-01 closed:** the real Write-hook fixture requires exit 2 and both `## Done when` and `templates/HANDOFF.md` in captured stderr (`tests/integration/test-check-domain.py:4022-4031`). The passing sibling fixture requires exit 0 (`:4032`). Both observable details are live.
- **SC-02 still open:** zero/two Scope and zero Authority bind their labels and expected digits, but five Authority uses `("Authority", "5")` over whole stderr (`tests/integration/test-check-domain.py:3996-4001,4033-4043`). The common refusal header is `handoff shape (DEC-159).` (`check-domain.sh:1569`), so `"5"` is present independently of the reported count. Removing or corrupting the five-count detail would not redden this case. This is a concrete non-vacuity failure, not a stylistic concern.
- **SC-13 closed:** each of the unknown-prefix and bare-source-location fixtures invokes the real Write hook and requires exit 2 plus all four distinct prefixes (`tests/integration/test-check-domain.py:4022-4026,4058-4062`). Omitting any prefix reddens its case.
- **SC-15 c0 count gap closed:** the baselined and non-baselined malformed fixtures each require `Scope` and `2` on the same path-specific report line (`tests/integration/test-check-state.py:2164-2172,2180-2197`). The well-formed absent-target controls remain unreported, keeping the persisted no-re-resolution half live.

## TDD evidence

Accepted without waiver. `notes/tdd-executor-record.md:3-18` is an executor-authored transcription of command results actually observed in the same build session, explicitly says no RED was recreated, records the T-01 import failure before module creation, records the literal T-03 and T-06 RED verifies succeeding before their production changes, and records subsequent GREEN outcomes. The signed plan requires those RED/GREEN executions and ordering; it does not require that the receipt itself be written before GREEN. After-the-fact same-session transcription is therefore weaker than raw logs but adequate primary execution evidence, not a recreated RED.

## Ranked must-fix

1. **SC-02:** make each malformed-count assertion bind the count as a count-bearing message fragment (for example `"has 5 Authority: lines"`) or a structured/path-specific line, rather than an unscoped digit. Re-run the full configured integration command.

No blocking open question remains; the repair is local and specified by the signed observable contract.
