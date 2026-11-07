# QA gate - BUG-2169 - fix c1 at 90caccaf

**FAIL (amended after code-reviewer challenge).** F-1 resolved, GC-01(a) resolved, **GC-01(b) OPEN (partially addressed)**. SC-02's literal text needs each branch and the warning to fail against pre-fix advice in the qualifying single-install source. In the image at base only `printed-not-per-user` and `printed-debian` fail on behaviour; the Homebrew branch, `other` branch and warning disclosure fail there only on the missing `install_command` helper (a missing-API red, not behaviour), and the Homebrew behavioural red exists only on the Mac, which is not regression evidence. Green suites cannot cure this. No source/test edits. Own reproduction on `harness-2169-repro` (Debian python3 3.14.4, PyYAML 6.0.3 at `/usr/lib/python3/dist-packages/yaml`, single install, libyaml `True` with `_yaml.cpython-314-aarch64-linux-gnu.so`).

## SHA relations
- `90caccaf1ae0c5bc192d13efd199d6c90971adf0` is an ancestor of worktree HEAD `2133e949`; `git diff 90caccaf HEAD -- tests .claude/skills/harness/bin` is empty. `6c896d98` is an ancestor of the tip.
- Delta 6c896d98..90caccaf in code: `tests/integration/test-check-domain-grant.py` (1 line, D-14a) and `tests/unit/test-lead-start-preflight.py` (+advice checks); no `bin/` change.
- Trees used, built on host from `git archive 90caccaf` (immutable): `/tmp/qa-c1/tip`; `/tmp/qa-c1/base` = same with `.claude/skills/harness/bin` replaced by `git archive c4e8bbc8` (differs in exactly dispatch-guard.py, harness_yaml.py, worktree_terminal.py); `/tmp/qa-c1/old` = tip + 6c896d98's grant test. Script `/tmp/qa-c1/run.sh`.

## Verify commands (all three, verbatim, in the image; per-file under 6 s)
| State | test-dispatch-guard | test-lead-start-preflight | test-lead-start-return |
|---|---|---|---|
| tip, C loader | exit 0, 135/135 | exit 0, 64/64 | exit 0, 57/57 |
| tip, `_yaml*.so` deleted (`with_libyaml` False, no CSafeLoader) | exit 0, 135/135 | exit 0, 64/64 | exit 0, 57/57 |
| base c4e8bbc8 bin, C loader | exit 1, 25 FAIL (`failed to parse YAML ... authorization cannot read writable grants`) | exit 1, 24 FAIL, same signature | exit 1, 23 FAIL, same signature |
| base, no C loader | exit 0, 135/135 | exit 1, 56/59 (3 advice FAILs only) | exit 0, 57/57 |

Base reds are semantic (the reimport defect surfaces as a refusal at start, exit 2), not invocation failures. This also confirms the receipt's point: the reimport defect is C-loader-specific; the no-C-loader start passes both at base and fixed.

## Findings
- **F-1 D-14a: RESOLVED.** Tip on image: `ok D-14a`, SC-08 lines `ok`, grant file exit 0. Old test (6c896d98) against the fixed bin on the image: `FAIL D-14a`, 26/27, exit 1 - the red is reproduced by me, and the one-line change turns it green. In this container the grant file had no other failures at tip; unrelated root/macOS-path failures did not appear.
- **GC-01(a): RESOLVED.** A single system-wide PyYAML without the C loader was executed at both base and tip (table row 2 and 4): starts succeed, 135/135, 64/64, 57/57.
- **GC-01(b): OPEN, severity high unchanged (my earlier RESOLVED was wrong).** At base (no C loader, so the only reds are advice), `advice/printed-not-per-user` and `advice/printed-debian` FAIL on the actual pre-fix `INSTALL_COMMAND` text; `advice/function` FAILs on the missing helper, and at base the missing-helper return precedes the brew/other/warning assertions, so none of those ran. Mac (Homebrew 3.15, my own run, not regression proof) reddens `printed-homebrew`. No preserved qualifying behavioural red exists for Homebrew, other, or warning disclosure in the image. Fix direction (owner T-01, tests/unit/test-lead-start-preflight.py): make those branch/warning assertions run and fail on pre-fix text without depending on the helper's existence, in the image source.
- Regressed: none.

## Matrix and SC evidence
Task T-01 change_type `bugfix`; touches runtime code (`bin/*.py`) so `unit` is required; the integration `when:` (confined to tests/docs) is false on the full diff (P-13) but integration suites exercise the same SCs and were run. `harness.json` unit cmd `run-unit-tests.py --kind unit` and integration `--kind integration` discover `tests/{unit,integration}/test-*.py` by glob; all named files are tracked, so membership holds. I did not run the full runner kinds: in a container checkout without the host's tracked layout it exits 2 (MISCONFIGURED layout, `FEAT-44 ... probe-session-accessors.ts` untracked); a harness limitation of my sandbox, not a finding. Named per-file runs above stand as the kind evidence.
- SC-01 unit: `tests/unit/test-lead-start-preflight.py` (bug2169_cases); SC-02 unit: `...preflight.py` `bug2169_advice` (printed-* checks); SC-04 integration: `test-dispatch-guard.py`, `test-lead-start-return.py`. SC-03, SC-05: `verify: inspection`, outside my gate.

## Gaps / caveats (non-blocking)
- Receipt `/tmp/bug2169-evidence/fix-c1/mac-base.txt` is empty (0 bytes), so the receipt's Mac base "56/59" claim is not supported by that file; I reproduced it myself (above). `container-base.txt` does support the image base table.
- Homebrew and `other` advice branches cannot be exercised on the image; their base-behavior red exists only on the Mac (mine); the `brew`/`debian`/`other` branch assertions through `install_command` fail at base only on the missing helper.
- Only my own evidence examined the c1 fixes after the c0 round (O-07); peers' c1 notes were not consulted.
- Accepted c0 complexity findings left untouched.
