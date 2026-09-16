# QA matrix gate — BUG-1129 validate c1

```yaml
VERDICT: FAIL
DIGEST:
  headline: "All c0 QA coverage and fail-first gaps are closed at 499eaf0, but the mandated isolated-pin integration matrix exits 1 on six unrelated manifest-parity assertions."
  suite: fail
  failures: 6
  matrix_ok: false
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit", named_tests: 41 }
    - { kind: integration, state: failed, cmd: "python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration", named_tests: 72 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-01, test: "tests/integration/test-gh-sync-ship.py:476-494" }
    - { id: SC-02, test: "tests/integration/test-post-merge-sweep.py:577-608" }
    - { id: SC-03, test: "tests/unit/test-handoff-policy.py:43-80; tests/integration/test-gh-sync-ship.py:496-512" }
    - { id: SC-04, test: "tests/integration/test-gh-sync-ship.py:514-526" }
  fail_first:
    - { sc: SC-01, evidence: "notes/receipt-main-session-T-01-fail-first.md:6-9" }
    - { sc: SC-02, evidence: "notes/receipt-main-session-T-01-fail-first.md:11-13" }
    - { sc: SC-03, evidence: "notes/receipt-main-session-T-01-fail-first.md:28-48 (Arm 5 fail-open mutation)" }
    - { sc: SC-04, evidence: "notes/receipt-main-session-T-01-fail-first.md:20-26 (Arm 4 pre-migration)" }
  open_questions:
    - { id: Q1, question: "The isolated-pin integration runner fails test-check-plan-routes.py because qa-c1-pin/.harness/team-config.yaml differs from the owner manifest, producing six assertion failures; this is unrelated to T-01 but leaves the required integration gate red. Isolated-worktree matrix support needs resolution before a PASS gate can be issued.", blocking: true }
  files_touched: [".harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-qa-c1.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1129-validate-handoff-sweep/.harness/harness/features/BUG-1129-validate-handoff-sweep/notes/review-harness-qa-c1.md
```

## Scope and matrix

Reviewed immutable SHA `499eaf0b9c1eb04e0f51dcfec47fab9ea50abd54` in detached `qa-c1-pin`. T-01 is `bugfix`; its full feature diff touches runtime code and integration tests, requiring unit and integration. The exact mandated commands were invoked with `python3`, not through a symlink or bare-script invocation:

- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit` — exit 0; PASS (41 scripts).
- `python3 .claude/skills/harness/bin/run-unit-tests.py --kind integration` — exit 1; FAIL (72 scripts). `test-check-plan-routes.py` has six named assertion failures (`case_04`, `case_05`, `case_15`, `case_17`, `case_19d`, `case_19d2`): its fixture detects the isolated worktree's `.harness/team-config.yaml` differs from the owner manifest. This is a genuine named-test assertion failure, not a load/import/collection error, so the integration kind is failed and the matrix cannot pass.

The isolated `qa-c1-pin` worktree was removed. Final registered `.claude/worktrees/qa-*-pin` count: **0**.

## Phase 1 expectations and c0 closure

Phase 1 required: SC-01 refusal diagnostics, complete GitHub-write boundary and exact pre/post plan preservation; SC-02 sweep retention/no write/no SKIP; SC-03 unit plus ship-path coverage for the one all-direct predicate and every invalid/unreadable shape with a red mutation proof; and SC-04 fixture-default note creation plus explicit refusal omission with a pre-migration red proof.

- c0 QA / code-review Q1 (SC-01 wording, exact station, and full write boundary): **closed**. `test-gh-sync-ship.py:476-494` binds exit 1, `validation incomplete`, note path, no SKIP, byte-identical plan/station, and an empty logged GitHub-write set other than `auth` while exercising `--body-file`.
- c0 QA Q2 / goal-check GC-03 (SC-03 negative shipping and fail-first): **closed**. `test-handoff-policy.py:43-80` covers the sole exempt shape and absent, parse, mapping, empty, malformed-task, missing-mode, team, mixed, and unreadable inputs; `test-gh-sync-ship.py:496-512` binds unparsable-plan refusal/no-write through ship. Receipt Arm 5 records both surfaces red under the fail-open mutant.
- c0 QA Q3 / goal-check GC-04 (SC-04 fixture contract and fail-first): **closed**. `test-gh-sync-ship.py:514-526` asserts default `stage_ship` creates the note with every required handoff section; receipt Arm 4 records this assertion red before fixture migration.
- c0 goal-check GC-02 (complete no-write boundary): **closed** by the Q1 whole-boundary assertion above; the `--body-file` path proves comment posting is inside the guarded boundary.
- c0 security and UI reviews had no findings; no carry-forward item.

The new unit file is `tests/unit/test-handoff-policy.py`; it was in the passing unit matrix. The changed assertions bind their executed subjects and supplied failure modes: receipt Arm 5 is the SC-03 fail-open mutant and Arm 4 is the SC-04 pre-migration subject. No c0 coverage or fail-first gap survives; the only blocking result is the observed mandated integration-matrix failure.
