# Observations — harness-qa — FEAT-2488-plan-merge-atomicity

- 2026-11-23: Builder task verify lists ran hand-picked suites only; the full integration kind surfaced test-checker-structure-locks.py (FEAT-63 broad-catch census, ceiling 0) red on new `except Exception` handlers that every selected suite missed. Run the whole kind, not the task list.
- 2026-11-23: Running a pin-version test against a base checkout via an exec(-c) shim breaks run_pool multiprocessing pickling; cp into a base pin is denied by bash-write-guard. Byte-identity (sha256) of the builder red capture vs the pin test is the binding fallback.
