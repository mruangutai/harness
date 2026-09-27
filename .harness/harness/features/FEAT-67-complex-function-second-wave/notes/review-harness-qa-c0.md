# FEAT-67 QA gate c0

## Verdict

PASS — T-01's required active matrix kinds are green and non-vacuous at review SHA `cf568b130bbd7d88d0ff900cd88886ae33ce622c`; both automated criteria have valid fail-first evidence.

## Matrix

`plan.yaml` declares `change_type: cross_module`; `.harness/harness.json` requires `unit` and `integration`, both active.

| kind | command | discovery | exit | result |
|---|---|---:|---:|---|
| unit | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind unit` | 42 files | 0 | satisfied |
| integration | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.py --kind integration` | 70 files | 0 | satisfied |

The runner's `pool: ... files` summaries establish discovery; both commands ran from the reviewed worktree. The integration runner's own `0 failure(s)` summary and the named-test output establish that this was not a collection/load failure.

## Automated-criterion evidence

- **SC-01:** The plan's inline grade assertion was independently run unchanged in the detached baseline checkout and exited 1 with `approval_guard`, `check`, and `parse_digest` all grade 1. The same assertion in the clean detached implementation-pin checkout `e9ed16de` exited 0: it reported all 32 retained/introduced records at grade 4+ except the permitted exact-grade-2 `_edit_introduce_limb`, `config_errors`, and `agent_file_errors`. The retained receipt is corroborated at `notes/red-first-receipts.md:31-42` and `notes/clean-pin-byte-receipts.md:45-57`.
- **SC-02:** BRIEF-approved fail-first equivalent is the baseline-versus-pin byte relation, not an impossible pre-fix RED (`BRIEF.md:18-21`). The clean detached implementation-pin receipt compares all 11 named owning suites after only checkout-root normalization and records 11/11 normalized-identical (`notes/clean-pin-byte-receipts.md:11-31`). Independently, direct base-versus-review executions of `test-check-domain.py`, `test-check-omp-port.py`, and `test-validate-digest.py` produced empty `diff` output; the final comparison applied that same ruled root substitution. This covers the three changed production boundaries, while the full 11-suite receipt supplies the required complete relation.

SC-03 and SC-04 are inspection criteria; they create no additional automated-test gap and are not goal-graded here.

## Findings

[]

## Coverage gaps

[]

## Fail-first

- `{ sc: SC-01, evidence: "notes/red-first-receipts.md:31-42; independent same-inline assertion: baseline exit 1, implementation pin e9ed16de exit 0" }`
- `{ sc: SC-02, evidence: "BRIEF.md:18-21; notes/clean-pin-byte-receipts.md:11-31; independent normalized three-boundary diff exit 0" }`

## Scope

The exact `00c7219e4026081e70614647f3f98726afb2c381..cf568b130bbd7d88d0ff900cd88886ae33ce622c` census matches the dispatch's 19 files. Build-digest advisories D-01 (seven checks), D-03 (`denied_a` removal), exact-grade-2 helpers, and R1/R2/A3 did not invalidate either required automated relation.

## Open questions

[]
