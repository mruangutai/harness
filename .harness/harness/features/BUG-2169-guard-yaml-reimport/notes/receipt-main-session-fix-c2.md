# Fix receipt - BUG-2169 - c2 (main-session-direct, DEC-174)

Round 2 under the operator's raise (`notes/operator-rework-raise-2026-11-07.md`, 2 rounds /
90 min). Open finding from fix c1: GC-01(b) - Homebrew, generic and warning advice lacked
behavioural red at base on the qualifying image. F-1 and GC-01(a) were resolved in c1.
Raw output: `/tmp/bug2169-evidence/fix-c2/` (session); base tree built on the host (working
files, `bin/` from `c4e8bbc8`, `harness_yaml.py` verified byte-identical).

## Change (test only, `tests/unit/test-lead-start-preflight.py`)

`bug2169_advice` no longer calls `install_command` or checks the host. `_printed_advice` runs a
child python3 that sets `sys.prefix` and the `/etc/debian_version` answer BEFORE importing
`harness_yaml`, then prints `INSTALL_COMMAND`. Each branch is judged on the advice the module
actually prints for a simulated Homebrew, Homebrew-on-Debian, Debian-system and other python3.
`INSTALL_COMMAND` exists at base, so every case executes there. The early return on the
missing helper and the c1 host-conditional `printed-*` checks are gone.

## Evidence

| Case | Image base | Image fixed | Mac base | Mac fixed |
|---|---|---|---|---|
| advice/debian | FAIL | PASS | FAIL | PASS |
| advice/homebrew | FAIL | PASS | FAIL | PASS |
| advice/homebrew-warning | FAIL | PASS | FAIL | PASS |
| advice/other | FAIL | PASS | FAIL | PASS |
| advice/precedence | FAIL | PASS | FAIL | PASS |
| preflight total | exit 1, 35/61 | exit 0, 61/61 | exit 1, 56/61 | exit 0, 61/61 |

Image fixed also: dispatch-guard 135/135, start-return 57/57. Image is `harness-2169-repro`
(Debian PyYAML 6.0.3, C loader). Grader: `_printed_advice` grade 5; `bug2169_cases` and
`bug2169_advice` remain grade 2 under the accepted written reasons.
