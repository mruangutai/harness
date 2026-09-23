# GC-64-02 — evidence-kind alignment

## Finding

A unit-only verifier for SC-03 skipped the eight tool-family integration assertions, while an integration-only verifier for SC-06 skipped the handoff-authority unit assertion. Each carrying assertion now belongs to a criterion declaring the test kind that executes it.

## Exact before / after

- Before SC-03 (code maintainer; unit): “Boundary tests demonstrated failing first and then prove that the scoped consumers catch exported typed errors or the documented `OSError`, `UnicodeError`, `json.JSONDecodeError`, `ValueError`, and subprocess error classes, while unrelated programming exceptions propagate; `harness_boundary.hook_guard` catches `Exception` but not `BaseException`, explicitly lets `KeyboardInterrupt` and `SystemExit` escape, preserves a successful `main` result, and is not called by a hook.”
- After SC-03 (code maintainer; unit): “Boundary tests demonstrated failing first and then prove that the scoped shared-library consumers catch exported typed errors or the documented `OSError`, `UnicodeError`, `json.JSONDecodeError`, `ValueError`, and subprocess error classes, while unrelated programming exceptions propagate; `harness_boundary.hook_guard` catches `Exception` but not `BaseException`, explicitly lets `KeyboardInterrupt` and `SystemExit` escape, preserves a successful `main` result, and is not called by a hook.”
- New SC-07 (code maintainer; integration): “Boundary tests demonstrated failing first and then prove that the scoped tool consumers `board-station.py`, `check-omp-port.py`, `check-plan-routes.py`, `check-skill-weight.py`, `gh-sync.py`, `post-merge-sweep.py`, `run-unit-tests.py`, and `upgrade-config.py` catch exported typed errors or the documented `OSError`, `UnicodeError`, `json.JSONDecodeError`, `ValueError`, and subprocess error classes, while unrelated programming exceptions propagate.”
- Before SC-06 (reader; integration): “Red-first tests prove that a scoped path cannot reparse a feature, plan, manifest, or config source already parsed and reported in the same execution, and the final implementation consumes the existing parsed value without adding a second shared loader or a second parse diagnostic.”
- After SC-06 (reader; integration): “Red-first tests prove that the scoped route-discovery path cannot reparse a plan, manifest, or config source already parsed and reported in the same execution, and the final implementation consumes the existing parsed value without adding a second shared loader or a second parse diagnostic.”
- New SC-08 (reader; unit): “Red-first tests prove that the scoped handoff-authority path cannot reparse a feature or plan source already parsed and reported in the same execution, and the final implementation consumes the existing parsed value without adding a second shared loader or a second parse diagnostic.”
- No exception class, propagation behavior, hook-guard behavior, source category, existing-value consumption, loader prohibition, or diagnostic prohibition was removed.

## Trace additions for the main session

- Add SC-07 to T-02 and T-03 `traces:`.
- Add SC-08 to T-01 and T-03 `traces:`.
- Approval must be revoked and re-signed by the main session.
