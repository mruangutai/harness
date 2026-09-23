# FEAT-64 security review — validate c2

**PASS.** The full 67-path baseline-to-pin union is security-relevant because the production delta handles repository records, filesystem paths, subprocesses, GitHub responses, and operator-facing errors. At immutable pin `721b690e3578fbaba2b88d93774667d94ac4d8a3`, no concrete OWASP or STRIDE defect remains.

## Measured audit

- **Input validation / tampering:** The narrowed YAML/JSON, mapping-shape, filesystem, and subprocess catches preserve fail-checked or fail-closed handling for expected boundary failures while letting programming defects surface. The new plan caches are cleared at each top-level execution and key canonical plan paths; they do not let one feature's record authorize another.
- **Command execution / injection:** `factory_gh` and `post-merge-sweep` continue to use list-form `subprocess.run` with no shell interpolation. This diff adds no user-controlled shell, SQL, template, redirect, URL-fetch, or export/spreadsheet sink. `FACTORY_GH` executable selection predates this delta; its capability holder already controls the launched executable.
- **Paths / authorization:** Existing containment and worktree classification remain intact. The `harness_boundary` refactor centralizes module-load/call failures without widening the accepted path or grant set.
- **Disclosure / secrets:** The diff introduces no credential-shaped value. `GhError` retains captured streams as attributes but renders the existing bounded first-line/canonical diagnostics; converting invalid GitHub JSON to the typed error removes the prior raw exception-class rendering on that path. No new log or export exposes another user's data.
- **Availability / process control:** `KeyboardInterrupt` and `SystemExit` remain outside the ordinary-exception handlers. `hook_guard` is unwired at this pin (the only production occurrence is its definition), so its future fail-open/error-detail posture creates no current actor or capability delta.

## Prior-item regrade

- **GC-64-04 — CLOSED.** Independent object inspection found exactly three governed YAML additions between `a4a3d7f8` and evidence head `220feabb`: `plan.yaml`, `runs/validate-validator/state.yaml`, and `runs/validate-c1-validator/state.yaml`. An independent `git ls-tree` count applying the corpus test's `features/*/notes/**` exclusion gives **104 total / 100 under `.harness`**, matching both pinned `notes/build-divergences.md` §A4 and `notes/byte-evidence.md`. The evidence remedy names the real contributors and cannot conceal a fourth governed record.
- **QA-64-01 — CLOSED.** `git ls-tree` at review pin confirms `.harness/harness/features/FEAT-64-broad-exception-libs-tools/runs/build-main-direct/digest.md` is tracked and therefore independently inspectable at the immutable pin. Its absence advisory no longer applies.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The pinned parser, subprocess, path, error-rendering, and evidence changes add no exploitable security regression; GC-64-04 and QA-64-01 are closed."
  in_scope: true
  scope_reason: "The 67-path union processes repository-authored and environment/GitHub input, launches child processes, resolves paths and grants, and emits operator-visible diagnostics and validation evidence."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "repository YAML/JSON and handoff/plan records -> typed parsers and route/authority decisions", stride: T, mitigated: true }
    - { boundary: "operator configuration and GitHub responses -> list-form gh subprocess and typed diagnostics", stride: "T|I", mitigated: true }
    - { boundary: "filesystem/worktree paths -> containment, ownership, and removal decisions", stride: "T|E", mitigated: true }
    - { boundary: "exceptions and child-process output -> operator logs", stride: I, mitigated: true }
    - { boundary: "future hook main -> hook_guard verdict", stride: "T|E", mitigated: false, note: "precondition absent: hook_guard has zero callers at this pin; reassess when FEAT-65 wires it" }
    - { boundary: "validation records -> exact-byte completion proof", stride: "T|R", mitigated: true }
  open_questions: []
  files_touched: [.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-security-reviewer-c2.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-64-broad-exception-libs-tools/.harness/harness/features/FEAT-64-broad-exception-libs-tools/notes/review-harness-security-reviewer-c2.md
```
