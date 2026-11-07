# QA gate - BUG-2169 - fix c2 at a48a725e

**PASS.** GC-01(b) CLOSED, F-1 CLOSED (no regression), GC-01(a) CLOSED (no regression). All three T-01 verify commands exit 0 at the fixed tip in the image, with the C loader and without it, in ~9 s total. At baseline `c4e8bbc8` bin, the current tests fail on behaviour for SC-01 (reimport refusal) and for all five advice cases (printed pre-fix text), on the image with the C loader removed, where the advice is the ONLY red. No source or test edits by me.

## Source and layout certification (verified, not from the receipt)
- `a48a725e16321d3a3f9ef142a0b95e2e19a4de5e` is an ancestor of worktree HEAD `6cbd668e`; `git diff a48a725e HEAD -- tests .claude/skills/harness/bin` is empty. Delta `90caccaf..a48a725e` touches code only in `tests/unit/test-lead-start-preflight.py` (+bin: none); the rest is feature notes/records.
- Trees (host `git archive`, immutable; container `git checkout` on the worktree mount avoided): `/tmp/qa-c2/tip` = `a48a725e`; `/tmp/qa-c2/base` = tip archive overlaid with `git archive c4e8bbc8 .claude/skills/harness/bin` (bin file count 119 = 119; differs from tip in exactly `dispatch-guard.py`, `harness_yaml.py`, `worktree_terminal.py`; base `harness_yaml.py` byte-identical to `git show c4e8bbc8:` blob, sha256 `471f596c...`; tip's is `0c416893...`); `/tmp/qa-c2/pre` = whole `c4e8bbc8` archive (used only for the non-root runner comparison). Tip `tests/unit/test-lead-start-preflight.py` is byte-identical to the `a48a725e` blob.
- Base = current (tip) tests against pre-fix production bin; the tests do not need `install_command`, so nothing is a missing-helper red.

## Environment (identical for all receipts; `out/<state>/env.txt`)
Image `harness-2169-repro` (Debian-family, ubuntu 26.04 + `python3-yaml`), `/usr/bin/python3` 3.14.4, one PyYAML only: `/usr/lib/python3/dist-packages/yaml`, 6.0.3 (`find` shows no other `yaml` dir under any `*packages*`). C loader state: `with_libyaml True`, `CSafeLoader True`, one `_yaml*.so`. "noC" = `rm /usr/lib/python3/dist-packages/yaml/_yaml*.so` in the disposable container: `with_libyaml False`, `CSafeLoader False`, 0 `.so`. Mac not used.

## Verify commands, verbatim chain (3 files; `out/<state>/*.out|.err`)
| State | test-dispatch-guard | test-lead-start-preflight | test-lead-start-return | grant (D-14a/SC-08) |
|---|---|---|---|---|
| **tip, C loader** | exit 0, 135/135 | exit 0, 61/61 (0 FAIL) | exit 0, 57/57 | exit 0, 82 ok, 0 FAIL |
| **tip, no C loader** | exit 0, 135/135 | exit 0, 61/61 | exit 0, 57/57 | exit 0, 82 ok |
| base, C loader | exit 1, 110/135, 25 FAIL | exit 1, 35/61, 26 FAIL | exit 1, 13/36, 23 FAIL | n/a (see note) |
| base, no C loader | exit 0, 135/135 | **exit 1, 56/61, 5 FAIL (exactly the 5 advice cases)** | exit 0, 57/57 | n/a |

Timing at tip (`out/timing/{C,noC}/times.txt`, per file): C loader dispatch-guard 2.8 s, preflight 1.8 s, start-return 4.7 s, chain 9.2 s; no C loader 3.0 / 1.9 / 4.8 s, chain 9.7 s. Under 60 s. Discovered counts nonzero (135, 61, 57 cases).
Grant note: at base the grant test dies on `AttributeError: harness_yaml has no attribute install_command` (the D-14a line calls the helper the fix adds), so base grant is not a regression signal and I do not use it; the 12 cases before the crash print ok.

## Fail-first (behavioural, base bin + current tests, on the image)
- **SC-01** (reimport defect, C loader): base-C reds are the reimport refusal, not invocation failure: 20/19/21 `FAIL` lines carry `authorization cannot read writable grants: failed to parse YAML ... could not determine a constructor for the tag None`, exit 2 at start (e.g. `SC-02/product/plan-approved`, `SC-01/eng/one`). Green at tip C and noC. Evidence: `out/base-C/test-lead-start-preflight.out`, `test-dispatch-guard.out`, `test-lead-start-return.out`. The defect is C-loader specific: base-noC starts pass (consistent with c1).
- **SC-02 literal** (qualifying single-install image, advice is the only red): `out/base-noC/test-lead-start-preflight.out` lines 57-77, exit 1, 56/61, five FAIL, each printing the actual pre-fix `INSTALL_COMMAND` (`python3 -m pip install pyyaml` + `# ... PEP 668 ...` + `python3 -m pip install --user --break-system-packages pyyaml`):
  `BUG-2169/advice/debian` FAIL; `advice/homebrew` FAIL; `advice/homebrew-warning` FAIL; `advice/other` FAIL; `advice/precedence` FAIL. All five PASS at tip C and noC (11 `BUG-2169/` PASS lines include the cases). The probe `_printed_advice` runs a child python that sets `sys.prefix` / `/etc/debian_version` before importing `harness_yaml` and prints `INSTALL_COMMAND`; the reds are assertion failures on the printed text (`--user` present, no `apt install`, no `PEP 668`+`break the Homebrew` disclosure), not helper/invocation failures. This answers GC-01(b): Homebrew, generic (`other`) and warning each fail on behaviour at baseline in the image, same single-install source as SC-01. (The Mac is not involved.)
- **SC-04**: base-C: `test-dispatch-guard` 25 FAIL, `test-lead-start-return` 23 FAIL, same refusal signature; tip: both 0 FAIL, C and noC.

## Dispositions
- **F-1 (D-14a advice expectation): CLOSED, no regression.** `ok D-14a: the block SAYS WHY and carries the install command` and all SC-08 lines `ok` at tip, C and noC; `tests/integration/test-check-domain-grant.py` exit 0, 82/82 ok; earlier refusal/claim assertions (pair cases (a)-(i), regex parity) still `ok`.
- **GC-01(a) (non-C-loader fixed single-install starts): CLOSED, no regression.** Tip noC: 135/135, 61/61, 57/57, all exit 0.
- **GC-01(b): CLOSED.** See SC-02 literal above. Independent of the c2 receipt: `/tmp/bug2169-evidence/fix-c2/` was not used; I re-derived from archives. Receipt's base "35/61" reproduces for base-C (26 FAIL, 35 pass); the five advice reds reproduce on base-noC (cleaner isolation, 56/61).
- Regressed: none.

## Matrix and kinds (T-01 `bugfix`; P-13 resolved on the FULL feature diff)
`bugfix` floor `always: []`; `unit` when `touches_runtime_code` TRUE (bin/*.py); `integration` when `fix_confined_to_tests_and_contract_docs` FALSE, but integration suites exercise SC-04 and were run. `matrix_ok: true`. Per-kind, in the image on a committed tip archive (`git init` + commit so the layout check passes), runner `--kind`:
- **unit** (`run-unit-tests.py --kind unit`, `env -u HARNESS_AGENT_TYPE`, 57 files): as root exit 1; as non-root exit 1; the only failing file is `test-omp-hooks.py` (`bun: command not found` in `subprocess.run(["bun","test",...])`, traceback in `out/nonroot-tip/runner-unit.out`), identical at the **pre-fix `c4e8bbc8` tree** (pre also reddens `test-lead-start-preflight.py`, the defect). Image lacks `bun`; an environment limit unrelated to BUG-2169. `test-lead-start-preflight.py` PASS.
- **integration** (84 files): as root exit 1 (6 files fail: `check-domain-post`, `check-plan-routes`, `feature-worktree`, `harness-yaml`, `layout-migration`, plus one; they are unreadable-file/write-failure cases that root bypasses; C and noC identical, `out/timing/*/runner-integration.out`); **as non-root: exit 0, ALL PASSED, 84 files, 48 s** (`out/nonroot-tip/`). The pre-fix tree as non-root exits 1 with `test-dispatch-guard.py` and `test-lead-start-return.py` FAIL, which is the SC-04 fail-first at kind level. `test-check-domain-grant.py`, `test-dispatch-guard.py`, `test-lead-start-return.py`, `test-harness-yaml.py` PASS.
Named planned suites (the 3-file chain) are distinct from full kind coverage; full integration kind green (non-root), full unit kind green except the unrelated `bun`-less `test-omp-hooks.py` (not a finding for this diff; same at baseline).

## SC evidence (`sc_evidence`)
- SC-01: `tests/unit/test-lead-start-preflight.py` `bug2169_cases` (startup cases `BUG-2169/*`).
- SC-02: `tests/unit/test-lead-start-preflight.py` `bug2169_advice` (`advice/debian|homebrew|homebrew-warning|other|precedence`).
- SC-04: `tests/integration/test-dispatch-guard.py`, `tests/integration/test-lead-start-return.py`.
- SC-03, SC-05: `verify: inspection`, outside this gate.
Fail-first: SC-01, SC-02, SC-04 per the table above, evidence `out/base-C/`, `out/base-noC/`, `out/nonroot-pre/` under `/tmp/qa-c2/` (session-local, not durable; key lines excerpted above).

## Gaps / caveats (non-blocking)
- Raw evidence lives in `/tmp/qa-c2/out/` (tip/base outputs, env, timing, runner logs); it is session-local, so this note carries the excerpts. Peer code-reader asked for preservation: excerpts above are the durable copy.
- Container root hides unreadable-file cases; I ran the integration kind as non-root to attribute them (all green).
- Only my own evidence has examined the c2 fix after c1 (O-07); the c2 receipt's evidence dir was not used.
- Accepted c0 complexity findings untouched.

---
# CORRECTION (adequacy send-back) - unit kind with Bun supplied

**Correction to the section above (history retained unchanged).** My original return marked `unit` satisfied and PASS while the full unit-kind command had returned **exit 1** (`test-omp-hooks.py`, `bun: command not found`). That was an environment/prerequisite failure on an active kind, not a satisfied kind; calling it an "unrelated baseline nuisance" was not a pass. The original exit 1 stands as recorded (`out/nonroot-tip/runner-unit.out`). The feature-specific red/green proof above is unchanged and still accepted.

**Corrected run (separately named: `unit-with-bun`).** Same pinned archive `a48a725e` (`/tmp/qa-c2/tip`, committed in the container for the layout check), same image `harness-2169-repro` (single system PyYAML 6.0.3 at `/usr/lib/python3/dist-packages/yaml`, python 3.14.4), **non-root uid 1000**, no product/config/source change, PyYAML untouched (C loader present). Bun supplied only as a mounted read-only Linux binary: official `bun-linux-aarch64.zip` from the oven-sh release `latest` (CI precedent: `.github/workflows/tests.yml` installs Bun via `oven-sh/setup-bun@v2`, unpinned), **Bun 1.4.4**, on PATH via `/opt/bun`.
- Command: `env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/run-unit-tests.py --kind unit`
- Result: **exit 0**, `pool: 8 workers, 57 files, 13.56 s wall`; no `FAIL test-*` runner lines; `PASS test-omp-hooks.py` and `PASS test-lead-start-preflight.py`. (Run twice, both exit 0; the saved run is the second.) Evidence: `/tmp/qa-c2/out/nonroot-tip-bun/{exit.txt,bun-version.txt,runner-unit.out}` (session-local). Bare `FAIL BUG-1290 5a/5b/5c` lines in the output are test-factory-claim-mutation's deliberate mutation-proof prints (repo G-09), and one `ERROR could not resolve scan root` is a test-internal negative case; the runner exit code is the grade. The PASS-line count (59) exceeds 57 files because nested PASS prints are not one per file (repo G-04); discovered file count is 57.
- Not a Mac run; unit-kind failure at tip is therefore **resolved**: unit = satisfied with the required runtime present. Integration (non-root, 84 files, exit 0) unchanged from above.
- Residual caveat: Bun is a host-fetched latest binary, not a version pinned by repo; the CI itself is unpinned, so no version precedent exists to match.

**Corrected classification:** unit `satisfied` (named tests ran with the runtime prerequisite, none failed), integration `satisfied`, `matrix_ok: true`, `coverage_gaps: []`, PASS.
