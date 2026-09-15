# T-03 remote text source amendment

- Operator ruling applied from `notes/answers-2026-09-14-t03-eng.md`.
- `T-02.intent` now specifies that the existing public `load_harness_json` accepts either a filesystem path or an explicit keyword-only in-memory text source, with mutually exclusive inputs and identical strict parsing and typed-error behavior for duplicate keys at every nesting level, `NaN`, `Infinity`, `-Infinity`, mapping enforcement, and caller context. It assigns only focused accessor tests and `factory_config.product_config` remote-text consumer coverage, and forbids a second public accessor.
- `T-02.status` changed from `done` to `ready` through `plan-merge.py set-task-station`.
- `T-03.intent` now gives `factory_config.py::product_config::json_string#1` the concrete remedy of calling the existing `load_harness_json` keyword-only text mode and explicitly forbids exemption, reassignment, or a second accessor. `T-03.status` remains `ready`.
- No separate matching classification-evidence wording in `plan.yaml` named that exact row before this amendment, so no classification artifact or unrelated plan field was changed.
- The controlled task-field mutation reset `approval.status` to `pending` with `reset_reason: apply T-02, T-03`; main-session re-signature is required.
- `BRIEF.md` was left byte-for-byte unchanged because its single-accessor and strict parser/error outcomes are consistent with the ruling.
- Required check exited 0: 9 tasks and 145 anchors resolved with 0 failures against the assigned worktree.
- No production code or test file was edited. No formatter, linter, build, test suite, task verification, or other non-planning validation was run.
