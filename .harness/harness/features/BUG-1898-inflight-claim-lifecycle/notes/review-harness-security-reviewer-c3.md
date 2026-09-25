# Security review — BUG-1898 validate-c3

**PASS.** This diff is security-sensitive because untrusted hook/runtime identity crosses registry ownership and release boundaries, and because the c3 mutation oracle guards against a future persona-wide release of another run's claim. The exact pinned c3 delta fails closed and introduces no exploitable OWASP- or STRIDE-shaped regression. F-01 remains closed and F-QA-01 is repaired.

## Pin, range, and measured self-scope

- Review pin: `6bfc21e3ccdf78eb86cdd0eb250067348d887096`; `feature.json` binds that exact `review_sha`.
- Canonical merge-base: `a4d72e7fc91d0cf7a568d9e2a5225465a422170e`; reviewed `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..6bfc21e3ccdf78eb86cdd0eb250067348d887096` (47 paths, +4658/-554).
- Focused c3 comparison: `4942950a83c1895d85922f7cd9e9cfd41e28daf8..6bfc21e3ccdf78eb86cdd0eb250067348d887096` (9 paths, +372/-7); the c3 commit itself changes only `tests/integration/test-suite-claim-preservation.py` (+13/-4), while the other focused-range paths are c2 evidence/state records.
- In scope: hook payload/runtime identity, feature-root selection, strict registry reads, exact claim release, parent/child lifecycle, recovery command/process/path boundaries, the test-only executable override, credential handling, and the permanent mutation oracle. The focused c3 code adds no production input, network, dependency, credential, export, or data-response surface; it strengthens the existing tampering detector for the registry authorization boundary. This surface was security-reviewed in c2 and was remeasured rather than inherited.

## Result

- **Exact oracle is fail closed.** `EXACT_RELEASE_FAIL` includes the trailing space, and the parser collects the complete set of labels from every line beginning exactly `FAIL  [bug1898] `. Acceptance requires both nonzero child exit and set equality with `{after the child settles the identical yield passes, and releases only the parent}`. Consequently a singleton containing either required label is unequal and rejected; replacing either label with any other `[bug1898]` label is unequal and rejected; extra `[bug1898]` labels also reject. Set semantics appropriately ignore duplicate emissions of the same required label without allowing a missing or substituted identity.
- **Incidental failures cannot satisfy or spoil it.** The four relocated-copy schema failures are emitted by the generic CLI runner as `FAIL  <name>` (`test-validate-digest.py:1667-1697`), while only `_b1898_check` emits `FAIL  [bug1898] <name>` (`:5674-5676`, `:5892-5896`). Thus `drifted key spelling is caught`, `enum near-miss is caught, not normalized`, `code reviewer omission of code_grade is rejected`, and `code_grade's missing-field hint names the four legal values, not the list wording` never enter `reddened`: they neither satisfy a missing target nor add an unexpected target.
- **Measured identity proof.** Running `python3 tests/integration/test-suite-claim-preservation.py` at the source-identical pin exited 0: one sentinel per governed persona was seeded, the pinned validator suite passed, every unrelated live claim remained byte-identical, and the persona-wide-release mutant reddened exactly the two parent-settlement checks. This discriminates the exact identity/release failure rather than merely rerunning a green suite.
- **F-01 remains closed.** C3 changes no production registry, validator, hook, root, command, or release code. The canonical pin retains strict own/child reads before the held-child refusal and exact parent release; unreadable identity/registry state cannot become absence, and no persona-wide or bulk recovery path was added.
- **Secrets/data/process/path review.** The canonical changed-code credential-shape scan returned no matches. The c3 parser consumes captured child text only, starts no additional process, performs no path resolution, and changes no subprocess argv or environment authority. Its existing temporary copied validator is removed in `finally`; `VALIDATE_DIGEST_BIN` remains confined to the child integration suite. No secrets, PII, URLs, redirects, spreadsheet output, or dependencies are introduced.
- **SC-07:** remains `pending_operator_gate`. No live OMP was run and no receipt is claimed or fabricated; this is not a panel failure.

## STRIDE threat model

| Boundary | STRIDE | Mitigated | Basis |
|---|---|---:|---|
| Hook/runtime identity → claim ownership | S/T/E | yes | Exact feature, runtime, parent, and claim identity remain required; c3 changes no production route. |
| Registry read → release mutation | T/I/D | yes | Strict reads and exact-id release remain unchanged; the repaired mutant oracle now detects persona-wide release by exact failure identity. |
| Child suite output → mutation-oracle verdict | T/R | yes | Complete exact-set equality plus nonzero exit rejects missing, substituted, and additional BUG-1898 labels; unrelated failures are outside the prefix namespace. |
| Test override/temp copy → validator execution | T/E | yes | Override is child-process-local, points to a temporary copied validator, and cleanup is in `finally`. |
| Credential store → review/test output | I | yes | C3 adds no credential access; the canonical scan found no credential-shaped changed-code match. |

## Findings and cleanup

- Findings: none (`severity_max: info`; the diff was scoped in).
- Must-fix: none. F-QA-01 is closed under T-03/T-04; F-01 remains closed under T-03.
- Open questions: none.
- Scratch cleanup: no scratch checkout/worktree was created. The focused test's temporary validator copy was removed by its `finally`; no `BUG-1898-suite-sentinel-*` row remained in `.harness/.inflight-claims.json`. The assigned feature worktree was not removed, source was not modified, and `notes/cancelled-c1/` was untouched.
