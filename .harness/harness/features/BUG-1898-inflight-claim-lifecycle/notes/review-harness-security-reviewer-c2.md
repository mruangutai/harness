# Security review — BUG-1898 validate-c2

**PASS.** The pinned lifecycle change is security-sensitive, but the exact pin introduces no exploitable OWASP- or STRIDE-shaped defect. F-01 remains closed; the c2 changes resolve the security-relevant uncertainty in F-02 and F-QA-01 without widening identity, mutation, path, process, or secret-handling authority.

## Pin, range, and measured surface

- Review pin: `4942950a83c1895d85922f7cd9e9cfd41e28daf8` (`BUG-1898 fix c2: errand graded 4; suite wrapper bound to a persona-release mutant`).
- Canonical merge-base: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`; audited `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..4942950a83c1895d85922f7cd9e9cfd41e28daf8` (41 changed paths, +4293/-554).
- Focused c2 delta: `81dbd81d21b04b6fdcba2435d2e73a12ec72fd2e..4942950a83c1895d85922f7cd9e9cfd41e28daf8` (10 changed paths, +434/-30). Its shipped-code change is the extraction of `_settle_in`; the test wrapper now directs the real suite to a temporary validator through `VALIDATE_DIGEST_BIN` and applies a persona-release mutant.
- In scope: hook payload/runtime identity, root/worktree resolution, registry reads and exact mutations, parent-child settlement, recovery commands, process liveness, test-only executable override, and the credential-presence probe. The remaining changed objects are tests, feature records, decisions, and review evidence; they were included in the secrets/data-exposure census. The added UI/export/network/dependency surface is zero.

## Security result

- **Identity and authorization:** a governed run resolves a feature from its assignment or one unique exact runtime-id claim. Missing, conflicting, ambiguous, or unreadable identity refuses; mutation authorization requires agent, feature, runtime child id, and parent id. No persona/session/cwd guess was added.
- **Root and path handling:** dispatch, start, authorization, settlement, and recovery converge on `feature_root`; the no-shell declared root is required to be absolute and checked against the resolver. Recovery commands use list-built selectors and `shlex.quote`, and name an exact runtime or claim id rather than a broad persona release.
- **Strict reads, exact release, and TOCTOU:** ownership and child checks use `_read_strict`; unreadable state is not treated as empty. The c2 extraction preserves the order: strict own/child reads, child refusal, then exact `(agent, feature, agent_id)` release. Registry writes remain lock-backed; binding/authorization decisions occur inside the locked update. An actor able to replace the registry between operations already holds the filesystem capability being protected, so that does not create a privilege escalation in this diff.
- **Fail-closed lifecycle:** a dispatch-capable parent with a live child or unknowable registry cannot return success; its own claim remains. A held run can only yield `BLOCKED`, preserving an operator escape without asserting completion. Leaves do not receive a false child-denial. This confirms prior F-01 remains closed at the reviewed pin.
- **F-02:** closed for this review. `_settle_in` reduces the c2 control-flow concentration while retaining the same strict-read-before-write and child-before-own-release ordering; no security behavior was weakened.
- **F-QA-01:** closed for this review. The wrapper uses a per-process feature/runtime identity, cleans only its seeded claim ids, and the mutant changes only a temporary copied registry module. `VALIDATE_DIGEST_BIN` is a test-only override consumed by `test-validate-digest.py`; the live probe explicitly refuses to run when it is set. It grants no production execution path.
- **Secrets and data exposure:** the full-diff credential-shape census found only documentation/status text and the manual probe. The probe tests an API-key environment variable for presence or executes a parameterized read-only SQLite count; it neither reads nor prints secret values. Subprocesses use argv arrays with no shell. No token, credential, PII response, URL fetch, redirect, spreadsheet export, or new dependency was introduced.
- **SC-07:** `pending_operator_gate`. No live receipt was executed, observed, or fabricated by this review; its absence is not a panel security failure.

## STRIDE threat model

| Boundary | STRIDE | Mitigated | Basis |
|---|---|---:|---|
| Assignment/hook payload → runtime claim | S/T/E | yes | Exact feature plus runtime and parent ids; conflicts, absence, ambiguity, and unreadable registries refuse. |
| Registry read → ownership/release mutation | T/I/D | yes | Strict reads precede mutation; exact selectors and lock-backed writes prevent widened release. |
| Parent return → child lifecycle | T/E/D | yes | Exact parent-id child census blocks successful return and retains the parent claim. |
| Recovery diagnostic → operator process | T/E | yes | Exact identifiers, absolute resolved root, argv-safe rendering; no bulk recovery recommendation. |
| Test mutation override → executable selection | T/E | yes | Limited to the integration test process and temporary copy; the credentialled live probe rejects the override. |
| Credential store → manual probe output | I | yes | Parameterized read-only count or environment-key presence only; no value leaves the store. |

## Findings and disposition

- Findings: none (`severity_max: info`, because the diff was scoped in).
- Must-fix: none.
- Open questions: none.
- Scratch-worktree disposition: no scratch worktree was created. The assigned feature worktree was not removed or modified by this review; pre-existing `feature.json` modification and ignored `notes/cancelled-c1/` were left untouched.
