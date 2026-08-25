# Security review — T-01

**PASS.** The pinned delta is security-relevant enough to inspect because it adds a subprocess-driving test with an executable environment override and filesystem writes, but it introduces no exploitable trust-boundary failure.

## Pinned scope

- Base: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`
- Review SHA: `ce29a059e37af5133ae5b4f87df6f622ed966a92`
- Changed-file census:
  - `.agents/skills/harness/bin/test-merge-gitignore.py` — in scope: new subprocess, environment, temporary-filesystem, and captured-output behavior.
  - `.agents/skills/harness/bin/run-unit-tests.sh` — inspected: only registers the new test in `INTEGRATION_SCRIPTS` (`:17`); no new input or privilege logic.
  - `.harness/harness.json` — inspected: only adds the exact test path to integration detection (`:119`); no secrets or runtime authorization change.
- Relevant unchanged utility: `.agents/skills/harness/bin/merge-gitignore.sh` — inspected to trace the process and filesystem contract; the pinned diff does not modify it.
- Authority inspected: `BRIEF.md` REQ-01–REQ-05 / SC-01–SC-06 and `plan.yaml` T-01, D-01, D-02.

## OWASP/STRIDE assessment

- **Subprocess and injection (Tampering / Elevation):** `MERGE_GITIGNORE_BIN` selects an executable only for this standalone test (`test-merge-gitignore.py:9`). Invocation uses list-form argv with no shell (`:18-22`), so project paths and `--check` are not shell-interpreted. The override is explicitly approved for reviewer-controlled mutants (`plan.yaml:61-65`). An actor able to set the test process environment is already selecting test execution context; no lower-trust input route or privilege gain is introduced.
- **Filesystem boundary (Tampering / DoS):** every new case authors its own project beneath `tempfile.TemporaryDirectory` (`test-merge-gitignore.py:34-126`), passes that project explicitly, and the caller-cwd case verifies separation. No user project, arbitrary deletion, traversal-derived path, or persistent artifact is introduced.
- **Input validation:** the new program has no CLI/user payload. Its rule set is repository-authored from the canonical snippet (`test-merge-gitignore.py:10-15`), and its project paths are internally authored. The unchanged utility validates the root as a directory and quotes root/target uses (`merge-gitignore.sh:13-26,32-43`).
- **Secrets, auth, dependencies, SSRF:** no credential material, authentication/authorization path, network request, redirect, parser dependency, or package change exists in the delta.
- **Data exposure (Information Disclosure / Repudiation):** subprocess output is captured rather than streamed (`test-merge-gitignore.py:22`); normal test output contains case names and counts only (`:133-147`). Failure details can contain canonical rules or randomized temporary paths, not secrets or project data. There is no export surface.

## Assessed and dismissed

The unchanged utility appends through the target path and therefore retains its pre-existing behavior for a project-supplied `.gitignore` symlink; it also performs shell-side rule reporting. The new suite invokes that utility only against test-authored temporary regular files and does not add a production call path, so the pinned delta neither creates nor newly exposes those behaviors.

## Findings

None. Severity maximum: `info`. No must-fix items or open questions. Per assignment, no tests or validation commands were run.
