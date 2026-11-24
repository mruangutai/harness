# QA gate: FEAT-2489-plan-routes-split, validate c2 (r-20261124-9-validate-validator)

**VERDICT: PASS.** matrix_ok is true. I ran unit and integration once each at pin `25132b7ec29e9cdfaddfafeca7b7cd7d4c803cbd`, and every discovered file exited 0: 68 of 68 unit files and 95 of 95 integration files. Both receipts come back clean under `evidence_defects` (`[]`). The CI Plan-route gate and the Canonical-reader audit both exit 0 when parsed the way tests.yml parses them, and tests.yml is byte-identical from base to pin. The T-02 and T-04 verify blocks pass verbatim and their output is byte-equal to the c1 receipts. split-equivalence.py reports ALL PASS, and its MAP block equals equivalence-final.txt across all 164 lines. CR-2 is closed as a mutation: the pinned checker FAILs on every terminator-only case I tried, and the be0807b0 checker PASSed the same inputs. No file under bin/ or tests/ changed from be0807b0 to 25132b7e. SC-03's fail-first reds reproduce exactly. I have no new findings.

## Pin and environment

- Repository: mruangutai/harness. This is an unbound Harness feature, so the repository reviewed is the one that holds it. Base `261fdf726428bd8325fbd3d4beccad23b67e83cc` is `git merge-base 25132b7e main`.
- QA policy: `git show 25132b7e:.harness/harness.json`. unit and integration are `active`, with cmd `.agents/skills/harness/bin/run-unit-tests.py --kind <kind>`.
- Checkout: `pinned-checkout.py add --feature FEAT-2489-plan-routes-split --run-id r-20261124-9-validate-validator --persona harness-qa --sha 25132b7e…`.
  - HEAD was the pin, and `worktree-state.py --verify` exited 0 ("converged").
  - Before the runs I ran `bun install --frozen-lockfile` and `python3 -m compileall -q .claude/skills/harness/bin`.
  - `git status --porcelain` was empty before and after every run.
  - The pin was removed on return (rc=0).
- Interpreter: host python3 3.15.2. This was a host run, not a CI run.
- Environment for every run: `env -u PYTHONUNBUFFERED -u NO_COLOR -u FORCE_COLOR -u HARNESS_AGENT_TYPE -u CLAUDE_PROJECT_DIR TERM=xterm-256color HARNESS_PROJECT_DIR=<pin>`. I confirmed the result with an `env` dump: TERM=xterm-256color, and no NO_COLOR, FORCE_COLOR or PYTHONUNBUFFERED. The verify and equivalence runs also unset HARNESS_PROJECT_DIR, because the scripts scrub it themselves.

## Matrix (from the pinned harness.json; unchanged from c1)

| Task | change_type | Kinds required |
|---|---|---|
| T-01 | bugfix | integration (`fix_confined_to_tests_and_contract_docs`). `touches_runtime_code` is false, and `match_bug_class` is a placeholder |
| T-02 | scaffolding | none |
| T-03 | cross_module | unit and integration (always) |
| T-04 | config | none. The JSON change is to values only, so `touches_config_shape` is false |

| kind | state | runner command (DEC-255) | discovered / selected / exit 0 | runner exit |
|---|---|---|---|---|
| unit | satisfied | `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest <FT>/…/runs/r-20261124-9-validate-validator/qa/manifest-unit.json` | 68 / 68 / 68 | 0 (25.6s wall) |
| integration | satisfied | same, with `--kind integration` and `manifest-integration.json` | 95 / 95 / 95 | 0 (178.0s wall) |

- **Receipts.**
  - `manifest-unit.json` has sha256 a3e04665…; `manifest-integration.json` has sha256 572f8bb7….
  - In both, `tested_commit` is the pin, `runner_exit` is 0, and selected equals completed (68 and 95).
  - I ran `check-integration-shards.evidence_defects({path: doc}, pin, 1, discover_expected(pin, kind), kind)` from the pin's own module. It returns `[]` for both receipts.
- **Grading.** I graded on the per-file `----- <file> (exit N, …) -----` headers, not on `^FAIL`:
  - unit: 68 headers, all exit 0.
  - integration: 95 headers, all exit 0.
- **Coverage of this change.**
  - test-broad-catch-census.py, test-structure-audit-index.py, test-checker-structure-locks.py and test-structure-audit-single-pass.py each print `PASS audit_modules_load_from_the_bin_under_test`.
  - test-check-plan-routes.py exits 0 in 49.9s. It prints 57 `PASS canonical_reader_*` lines, including `canonical_reader_audit_module_loads_from_the_bin_under_test`.
- **Full output.**
  - `notes/qa-c2-runner-unit-output.md` (sha256 53a75588…).
  - `notes/qa-c2-runner-integration-output.md` (sha256 74c0b790…).

## CI gates at the pin (exactly as tests.yml invokes them)

I extracted the step bodies with `yaml.safe_load` from the pinned tests.yml and ran them under `bash -e` from the pin, with `HARNESS_PROJECT_DIR=<pin>` standing in for `${{ github.workspace }}`.

- **Plan-route gate: step exit 0.**
  - Parse: `grep -E '^[0-9]+ violation\(s\) across [0-9]+ plan\(s\)$' | tail -1` gives `0 violation(s) across 2 plan(s)`.
  - `sed -E 's/^.* across ([0-9]+) plan\(s\)$/\1/'` gives plans=2.
  - `sed -nE 's/^examined ([0-9]+) feature dir\(s\).*$/\1/p'` gives examined=39, which is non-zero.
  - The step printed `route gate entered 39 feature dir(s), checked 2 live plan(s); checker exit 0`.
- **Canonical-reader audit: step exit 0.**
  - Parse: `sed -nE 's/^[0-9]+ unresolved reader site\(s\) across ([0-9]+) Python file\(s\)$/\1/p' | tail -1` on `0 unresolved reader site(s) across 103 Python file(s)` gives scanned=103. That is non-zero, and it is base's 101 plus the two modules.
- **Workflow unchanged.** `git diff --exit-code 261fdf72 25132b7e -- .github/workflows/tests.yml` exits 0.
- **Consolidation audit (information only).** tests.yml has no step for it. The raw `--consolidation-audit` run exits 0 with `0 consolidation finding(s) under bin/`.

## T-02 and T-04 verify, and the equivalence receipt

- I extracted both verify blocks from `plan.yaml` at the pin; the file is cmp-identical to the worktree copy.
  - T-02 sha256 9eb49eb7…; T-04 sha256 61972b16…, the same as c1.
  - I ran each from the pin root. **Both exit 0**, and each one-line output is `cmp`-identical to `notes/verify-c1-T-02.txt` and `notes/verify-c1-T-04.txt`.
- My own run of `notes/split-equivalence.py` at the pin exits 0.
  - It prints `ALL PASS` with 9 PASS lines and 0 FAIL, and `CLI perturbed:canonical … old_exit=2 new_exit=2 mapped=1`.
  - TREE head is bin `d542c641…` and tests `3f8731cd…`.
- **C2 MAP equality.** The live `^MAP ` lines are `cmp`-equal to equivalence-final.txt's, 164 lines.
  - The whole body, excluding the HEAD and PROJECTED lines, is identical (`diff` rc 0).
  - HEAD differs as it should: the receipt has d44f23e5, my run has 25132b7e, and the tree ids are equal.
  - Three PROJECTED lines differ. These are feature-record files committed since then, and the checker reads them only for projection_confined, which PASSes.

## CR-2 closure as a mutation (P-08). Temp copies in /tmp only; the tree was never touched

- Subjects:
  - pinned checker: `25132b7e:notes/split-equivalence.py`, blob `ec885c53…`;
  - pre-fix checker: `be0807b0:…`, blob `dc67649b…`, which is also the 778ea992 blob.
  - Both blob ids match `cr2-red-green.txt`.
- **My own probe.** It is independent of the fixer's, though it uses the same seam: each checker's own `cli_check → run_pair → run_entry → normalize → compare`, run on fake roots whose ENTRY writes fixed bytes. It has 15 cases.
  - **Controls.** Four must PASS: identical LF; identical CRLF on both sides; unterminated on both sides; the canonical summary with delta 2. One must FAIL: a text difference.
  - **Terminator-only cases.** Ten must FAIL:
    - stdout: trailing LF dropped; trailing LF added; CRLF; CRLF on the first line only.
    - stderr: trailing LF dropped; trailing LF added; CRLF; CRLF with empty stdout.
    - canonical summary: LF dropped; CRLF.
- **be0807b0 result: missed=10 of 15.** All ten terminator cases PASS, which is the CR-2 hole. All five controls behave as required.
- **Pin result: missed=0 of 15.** All ten FAIL, with details `stdout differs after mapping`, `stderr differs` and `summary line terminator differs`, and the five controls still hold. The controls show the probe discriminates; it does not simply fail everything.
- **The fixer's probe re-run.** I extracted it verbatim from `cr2-red-green.txt` and got the same verdicts: be0807b0 PASSes 7 of 7 terminator cases, and the pin FAILs 7 of 7 with its 3 controls PASS. This matches the receipt line for line.
- **One boundary beyond the class (P-11).**
  - A bare CR (`x\ry\n` against `x\ny\n`) PASSes at be0807b0, because `splitlines()` also splits on `\r`, and FAILs at the pin. The fix closes this member too.
  - Undecodable bytes raise UnicodeDecodeError in both versions. `run_check` catches a check's own exception as that check's FAIL (`split-equivalence.py` run_check), so the result is fail-closed and is not a finding.

## Delta be0807b0..25132b7e

- `git diff --name-only be0807b0 25132b7e` lists 26 paths, all under `.harness/harness/features/FEAT-2489-plan-routes-split/`. The count of paths outside that directory is 0, so nothing under `.claude/skills/harness/bin/` or `tests/` changed.
- plan.yaml's only change is `status: building` → `review`.
- Tree hashes:
  - `25132b7e:.claude/skills/harness/bin` = `d542c641c93f20a5a5f3567aa52d0171c625f201`, and `25132b7e:tests` = `3f8731cd34fe2a850bc9e4a00054eba89f684eb9`.
  - These equal be0807b0's, 778ea992's and the seam receipt's recorded values. The claim that production and test code are unchanged is therefore verified, not taken on trust.

## SC evidence and fail-first

SC-03 is the only `verify: automated` SC; SC-01, SC-02, SC-04 and SC-05 are `inspection`.

- **Test.** `tests/integration/test-check-plan-routes.py` runs the canonical cases by default. The code is unchanged since c1, which cited `_check_live_inventory_named_plans` at :1961 and `case_canonical_reader_named_plan_contract` at :1983. In this run all 57 `canonical_reader_*` checks PASS.
- **Fail-first: natural red and semantic. I reproduced both today on `git archive` trees.**
  - `notes/red-t01-canonical-self-test.txt`. On base 261fdf72, `--canonical-reader-self-test` exits 1 with exactly `canonical_reader_live_inventory_names_no_plan` and `canonical_reader_audit_holds_without_a_feature_corpus`, as recorded.
  - `notes/red-t03-stale-inventory.txt` (HEAD 3b6f2a42, an ancestor of the pin).
    - The default run exits 1. Its 9 FAILs, all `canonical_reader_*`, are set-identical to the receipt (`diff` rc 0).
    - `--canonical-reader-audit` exits 2. Its 5 CLASSIFICATION lines name only the scanned-file manifest, the two moved rows and canonical_reader_audit.py.

## Findings

None new. The already-ruled items (ESC-1, CR-2, SEC-1, C6, QA-F1) were not re-raised: no code under them changed, and CR-2's closure is confirmed above.

## Coverage gaps (Phase 1 expectations with no test; carried from c1, unchanged)

- No test asserts the failure shape of a bin missing either module (C4, accepted). Only case 19b's copy list touches this.
- SC-02's fifth item and the sixth item's seam-straddle class have no automated check. They rest on inspection and on the manual seam receipt, which C1 ruled out of split-equivalence.py.
- The three integration audit files are never run against a copied bin. Only the two unit files are (T-04 verify re-ran them green).

## Principles applied

- **Build the Lever** (leaf read this run): its test needs a lever file in the diff. My CR-2 probe and the step and verify extractions live only in /tmp, because QA holds no write grant there, so I do not claim this principle. The probe's cases are listed above so the work can be reproduced.
