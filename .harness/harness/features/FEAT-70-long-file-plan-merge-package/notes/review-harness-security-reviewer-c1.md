# Security review — FEAT-70 cycle 1

**PASS.** Review SHA `01af5a511f356d76ee91ced8922e2d53e71479e3`, measured against feature baseline `9e531b34fc04f752cedf51586dc13c460580901a`, has a security surface but no exploitable regression. `git diff --name-status` reports 47 paths: the `plan-merge.py` entry, 11 `plan_merge/` package files, feature records/receipts, receipt executables, and integration fixtures. The immutable implementation pin remains `73ba9dceee11253bbf57b7ca1b36323c81d83891`.

## Scope and assessment

The delta is scoped **in** because the CLI consumes operator/agent argv, paths, YAML, digests, and anchors; mutates signed plans and ledgers; and emits receipts interpreted by automation and humans. OWASP/STRIDE review covered authentication/approval identity, secrets, command and path injection, input validation, symlink/worktree safety, subprocess/archive handling, and output/data exposure.

No findings. The package carve retains the resolved destination boundary (`plan_merge/guards.py:20-45`), duplicate-safe/schema-checked YAML and reload verification (`guards.py:123-220`), governed-agent approval refusal (`guards.py:222-230`), shared locked update (`guards.py:233-238`), and same-directory atomic rollback (`guards.py:241-268`). The census adds no dependency, network request, SQL, shell, redirect, template, CSV, or spreadsheet-export surface, and the credential-shaped-string sweep found no committed credential.

Cycle-0 closure VAL-02 broadens only test-fixture assembly: `test-hooks-install.py:63-68,119-132` copies each trusted sibling Python package (directory with `__init__.py`) into a throwaway repository; `test-post-merge-sweep.py:96-101,146-152` symlinks those trusted packages into an isolated fixture. A contributor able to replace/add a source package already has repository-code execution; enumeration grants no lesser actor a new write or execution primitive. The sweep suite additionally proves every exercised runtime root is inside its fixture and never the real checkout. The copied-package change does not alter shipped runtime behavior.

Dismissed candidate: following package-directory symlinks could copy/link unexpected content, but the only source is the reviewed checkout's trusted bin directory and the destinations are disposable test fixtures. There is no untrusted path parameter and no privilege delta. The accepted seven-record ruling remains exact-record only: two traceback-coordinate stderr records and five relocated-symbol anchor records; it does not normalize or suppress arbitrary output, secrets, exit status, or plan bytes.

## Threat model

- **Untrusted plan/proposal/digest → plan or feature ledger (T/I/E): mitigated.** Resolved destination, safe parse/schema checks, approval identity guard, lock, reload, and atomic replacement remain intact.
- **CLI path/anchor → filesystem (T/I): mitigated.** Destination validation applies after resolution; anchor validation remains on the established reader.
- **Trusted checkout packages → throwaway fixture (T/D/E): mitigated.** Source capability is not lower-trust than execution, destination is isolated, and root-containment assertions pass.
- **Tool streams/receipts → human or automation (I/R): mitigated.** Exact-byte comparison remains fail-closed outside the seven accepted records; no spreadsheet-interpreted export exists.
- **Secrets/credentials → committed output (I): mitigated.** No credential-shaped addition or new logging channel was found.

## Evidence

- Full pinned census: 47 files, 6,151 insertions, 3,639 deletions.
- Cycle-0-to-cycle-1 census: 13 paths, including exactly the two fixture files above, receipt/grade corrections, and review records.
- `python3 tests/integration/test-hooks-install.py` → exit 0; all package-aware clone/hook and real-checkout exclusion assertions pass.
- `python3 tests/integration/test-post-merge-sweep.py` → exit 0; all isolation, self-exclusion, record-before-remove, linked-worktree, and fixture-root safety assertions pass.
- `feat70-grade-assert.py 73ba9dce… 9e531b34…` → GREEN; 237 functions, 106 grade 5 and 131 grade 4; `bodies` is grade 4, closing VAL-01.
- SC-01, SC-02, and SC-03 remain supported by the pinned clean-byte and red-first receipts; this audit does not re-litigate the signed seven-record ruling.

Open questions: none.
