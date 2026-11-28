# T-01 fail-first record (BUG-2582)

Built by the main session, main-session-direct (DEC-174), on 2026-11-27. Base: `e6960865`.

## RED: the new tests against the unchanged tree

Command: `env -u HARNESS_AGENT_TYPE python3 tests/unit/test-plan-merge-station-convert.py`. Exit 1.

- **FAIL `bug2582-convert-apply`**, **`bug2582-convert-add-tasks`** and **`bug2582-convert-keeps-base-approval-and-stamp`**, each with "MergeRefusal code 5: ILLEGAL PLAN … `station_only:` may only be `true` on a record with an EMPTY `tasks:` list". This is the BUG-2565 repro.
- **FAIL `bug2582-inv34-remedy-line`**: remedy present, conversion sentence absent.
- **PASS** (guards that hold at base): `bug2582-marker-in-proposal-refused`, `bug2582-finished-{done,abandoned,rejected}`, `bug2582-empty-proposal-stays-station-only` and `bug2582-loader-pair-unchanged`.

## GREEN

The T-01 literal verify exits 0:
- the unit file is all PASS;
- `harness_yaml.py` is unchanged against `e6960865` (`git diff --quiet`);
- the red proof against the base `union.py` and the base check-state prints "red-first ok";
- `test-plan-merge.py`, `test-harness-yaml.py` and `test-check-state-plans.py` all pass.

## Deviations from the task text, both test-fixture corrections

1. **The finished-station cases.** The plan's fixture changed only the base `status:` to `done`, `abandoned` or `rejected`. The proposal still said `status: plan`, so the plain-key merge refused with CONFLICT, code 7, before conversion was ever reached, and the case would have pinned the status conflict rather than "a finished record is not converted". The proposal now carries the same finished station. Both base and fix refuse with 5 through the loader pair, as SC-02 states.
2. **The checker archive for `CHECK_STATE_REV`.** The plan modelled this on `test-check-state-inv35.py`, which archives only `bin/`. The checker reads its sibling `schemas/harness.json` at startup, so an archived `bin/` alone dies before INV-34 runs ("remedy absent"). The case now archives `.claude/skills/harness`, the parent of `bin/`.
