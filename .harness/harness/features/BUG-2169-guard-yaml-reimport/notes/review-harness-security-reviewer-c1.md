# PASS — no security regression in the fixed delta

Reviewed `6c896d981ed17d2bae528818ecffa56400ae2666..90caccaf1ae0c5bc192d13efd199d6c90971adf0`, original base `c4e8bbc87e858bb2a0320efd766c7036cbcebb8b`, against BRIEF SC-01–05, SPEC §13 and DEC-174/225. No prior security findings existed (`review-harness-security-reviewer-c0.md`); none are open or regressed.

## Measured scope and security assessment

Complete pinned census: **10 paths, +263/-7**: two test files, seven Markdown review/evidence notes, and feature.json. In scope: changed security-adjacent assertions and interpreted evidence; **no new production security surface**. The earlier cycle reviewed the production import boundary. This delta changes no hook, authorization policy, isolation roots, dependency, subprocess invocation or runtime fallback.

- `tests/integration/test-check-domain-grant.py:359–362`: D-14a replaces pip-only wording with a member of the existing concrete install-command set. The adjacent SC-09 assertion still requires the different-session invocation to exit **2** (`:348–350`); the diagnostic assertion still requires nonempty stderr and “EARLIER session.” It cannot turn an allowed write into a passing refusal assertion. Platform-branch correctness remains separately asserted in preflight.
- `tests/unit/test-lead-start-preflight.py:502–526`: printed INSTALL_COMMAND is examined before the missing-helper return, using independently read platform facts; the added Homebrew assertion requires both command and risk warning. Existing explicit branch/warning checks and real start/claim plus four hostile-origin controls remain. No removal or weakening of the isolation assertions appears in the pinned diff.
- All eight record/note paths were inspected: historical blocked/refused outcomes remain recorded, not replaced with success. Full-diff credential sweep found no credential material (token matches were accounting and security-review prose).

## Existing must-fix reconciliation — not new security findings

- **F-1, substance, unrated: resolved by inspection.** D-14a now accepts apt as well as pip; receipt and container.txt record `ok D-14a` and SC-08. No whole-file grant pass is claimed; known root/path failures are outside this assertion.
- **GC-01(a), substance, unrated: evidence supplied, runtime closure belongs to QA.** Fix receipt records single-system non-C-loader starts and container-base.txt records the corresponding base behavior; no loader policy changes occurred.
- **GC-01(b), substance, unrated: early-return defect resolved by inspection.** container-base.txt records actual printed-not-per-user/printed-debian behavioral failures, rather than only a missing helper. This is not independent certification of every platform's qualifying fail-first evidence.
- Two accepted med grade-2 findings remain code-review matters, not newly raised blockers.

Evidence caveat: container.txt includes failed container git checkout attempts and mislabeled green “base” rows; those rows are **not base proof**. container-base.txt supplies corrected base failures. QA/lead were notified; they own source/pin identity and final gate sufficiency. Mac output is not used here as regression proof.

Threat boundaries assessed: hook refusal/exit status → security assertions (Tampering), install advice → operator (Tampering). No exploitable weakening found by inspection. No gates, builds, linters, formatters or mutations executed by this reviewer. Source/tests unchanged; only this note written. Findings/must-fix: none. Open security questions: none.
