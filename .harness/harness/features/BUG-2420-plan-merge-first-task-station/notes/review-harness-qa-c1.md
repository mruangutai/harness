# BUG-2420 QA gate, validate run 2026-11-22-04-validate-validator, c1

**BLUF: PASS.** Reviewed and tested SHA `2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd`. The byte-exact oracle reddens at the pre-fix stations.py, and the c0-surviving M8 (CRLF insert) is now killed by the whole-file assertion. Unit and integration receipts are green at the pin; the literal T-01 verify exits 0. No finding.

## Delta established independently (c0 pin c0c3f1b9 -> 2b5b8b2a)
- `git diff --stat c0c3f1b9 2b5b8b2a -- . ':!.harness'`: exactly one non-feature file, `tests/unit/test-plan-merge-first-station.py` (+19/-15).
- `git diff --quiet c0c3f1b9 2b5b8b2a -- .claude tests/integration` exits 0: production `stations.py` and the integration test are byte-identical to c0. Feature-dir changes are notes plus `plan.yaml` `status: building -> review`.

## Phase 1 (BRIEF/plan only)
E1 three-row table, whole-file byte preservation on rewrite (SC-01); E2 absent task exit 3, absence wording, no write (SC-01); E3 approval block byte-identical and insert must succeed (SC-02); E4 integration `tasks: []` -> apply T-01 -> no seed -> set building -> reload (SC-03). Gaps against Phase 1: none. The c0 hole (CRLF/ordering not proven for SC-01) is the point of this cycle and is now closed.

## Kinds (serial, one at a time, from pin HEAD `2b5b8b2a...`, clean; `bun install --frozen-lockfile` ran first, 7 packages, pin stayed clean; HARNESS_AGENT_TYPE/HARNESS_PROJECT_DIR unset)
Command: `python3 <pin>/.claude/skills/harness/bin/run-unit-tests.py --kind <kind> --shard 1/1 --manifest <F>/runs/2026-11-22-04-validate-validator/qa/manifest-<kind>.json`
- unit: runner exit 0, 66 files discovered/completed, 24.18 s. Receipt `runs/2026-11-22-04-validate-validator/qa/manifest-unit.json`, tested_commit = pin. Includes `tests/unit/test-plan-merge-first-station.py`.
- integration: runner exit 0, 95 files discovered/completed, 170.39 s, `ALL PASSED`. Receipt `.../manifest-integration.json`, tested_commit = pin. Includes `tests/integration/test-plan-merge.py`.
Receipts were written by the runner; read back (tested_commit, runner_exit 0, selected counts 66/95), never edited. Counts match c0 (66/95).
Not claimed: typecheck (Python-only patch), others excluded/not touched. Matrix floor unchanged from c0 (bugfix; unit via touches_runtime_code; integration also run per BRIEF).

## Literal T-01 verify, `BUG2420_TOOL_ROOT=<pin>`, `BUG2420_BASE=d5be5392...`: exit 0
Ran verbatim. HEAD printed `2b5b8b2a...`; unit `PASS test-plan-merge-first-station.py`; integration `PASS test-plan-merge.py` incl. four `2420:` rows (apply drafts T-01, no seed, first station exit 0, reload at building); check-plan-routes `0 violation(s) across 1 plan(s)` after the known main-session-direct `DEVIATION T-01` owner-manifest line; reader audit `0 unresolved reader site(s) across 101 Python file(s)`; `passing: 12`, `BUG-2420 grades PASS: production >=4, tests >=3`.
Honest record: I first ran the block with output sent to /dev/null (silent, exit 0) by mistake, then reran it once with the output filtered to the lines above to keep the evidence; both exit 0.

## Fail-first (my own reproduction, natural red, at the pin's test file)
Method: no file writes were permitted to me outside the domain (bash-write-guard blocked redirect and `cp` into a scratch pin), so the stations module is served from memory by a one-shot Python wrapper that overrides `SourceFileLoader.get_code` for `plan_merge/stations.py` and then `runpy`s the pin's unit test. Source is never modified; pin `git status` was clean after. Wrapper modes: `base` (= `git show d5be5392:...stations.py`, sha256 `ceef2a6b42eb2129c0d1a7bae071404287911ad10002738fb85623bf19738b9a`, matches the pin), `m8`, `fixed` (control).
- SC-01 / base: exit 1. FAIL `a status-less task gains its first station at its field indent: the whole file is exactly the expected bytes "schema: plan/1\n...status: building\ntasks:..."` (insertion row; base rewrote verify prose instead of inserting). Controls PASS: row 2 rewrite 4/4, row 3 absent-id 4/4, `the absent-task refusal never blames a status line`. Also FAIL at base: `first station sits inside T-01's own mapping`, `T-01's verify prose keeps its own status: prose line`.
- SC-02 / base: FAIL `the first-station insert on a signed plan succeeds rc=3` and FAIL `the signed approval block is byte-identical after the insert` (the reported defect; the approval proof also needs rc 0).
- SC-03 / base: inherited from c0 (integration file and production byte-identical to c0; `git diff --quiet` above): at the base stations.py, `FAIL 2420: set-task-station gives the drafted task its first station (exit 0)` and `FAIL 2420: the written plan reloads with T-01 at building`; apply rows pass. Not re-executed this cycle, per assignment.
- M8 (the c0-surviving mutant), fixed stations.py with `lines.insert(start + 1, line + "\n")` changed to `line + "\r\n"` (exactly one occurrence asserted, 16053 bytes): exit 1. FAIL `a status-less task gains its first station ...: the whole file is exactly the expected bytes "...- id: T-01\n  status: building\r\n  title: ..."`. Every other row/check PASS, so the kill is by the insertion row's whole-file byte equality. c0 recorded this mutant green.
- Control: `fixed` mode exits 0 with all 17 rows PASS.
Tier: natural RED for SC-01/02/03 (the base module is the real pre-fix state), mutation for M8. Reds are semantic (a whole-file/expected-text mismatch and rc=3), not signature-absent.

## SC evidence
- SC-01: `tests/unit/test-plan-merge-first-station.py` ROWS table (three rows, whole expected file each) and the per-row byte-equality check; the fixture writes bytes and `plan_bytes` reads bytes with no newline translation (file header lines 74-100).
- SC-02: `case_signed_approval_survives_the_first_station` in the same file (requires rc 0 and byte-identical approval block).
- SC-03: `tests/integration/test-plan-merge.py` `case_2420_drafted_task_takes_its_first_station` (c0 line 5142; file unchanged since c0).

## Coverage gaps and observations
- None against Phase 1. Production source reasoned only for the M8 site (`stations.py:266`); code-quality judgement is the code reader's lane.
- Observation: the Q-01 write-guard discrepancy recurred. `cp` and redirects into pins were denied for harness-qa this session; the in-memory loader override was sufficient and needs no write.
- No open questions.

## Cleanup
Both pins (`...--harness-qa`, `...--harness-qa-mutants`, the latter created and unused) removed on return.

## Principles applied
- Build the Lever: the one-shot wrapper (modes base/m8/fixed) is a rerunnable proof; it is quoted by behavior above and lives in this shell run only, not committed (QA owns no script path), so a reviewer reruns by reimplementing the three `get_code` overrides described.

## Appendix: raw commands and output as recorded in the run transcript (added on request, no reruns)
Raw logs were not saved to disk: bash-write-guard denied me redirects and `cp` outside my domain, so the only durable raw record is this appendix, copied from the transcript. Lines marked `[cut]` were truncated at 330 columns by my own `cut -c1-330` filter at capture time; the full text is gone and is not reconstructed here.

### A. Pre-fix red, M8 and control: exact wrapper command
Run from the pin (`.pins/BUG-2420-plan-merge-first-task-station--2026-11-22-04-validate-validator--harness-qa`), `unset HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE`, HEAD printed `2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd`; base sha256 printed `ceef2a6b42eb2129c0d1a7bae071404287911ad10002738fb85623bf19738b9a  -`.
```sh
run() { MODE=$1 python3 -B - <<'PY'
import os, sys, subprocess, runpy
from importlib.machinery import SourceFileLoader
mode = os.environ['MODE']
fixed = open('.claude/skills/harness/bin/plan_merge/stations.py','rb').read()
if mode == 'base':
    src = subprocess.check_output(['git','show','d5be53927009df8e7848f860f9d0b4b03b89f9ad:.claude/skills/harness/bin/plan_merge/stations.py'])
elif mode == 'm8':
    old = b'lines.insert(start + 1, line + "\\n")'; new = b'lines.insert(start + 1, line + "\\r\\n")'
    assert fixed.count(old) == 1
    src = fixed.replace(old, new)
else:
    src = fixed
orig = SourceFileLoader.get_code
def get_code(self, fullname):
    if self.path.endswith('plan_merge/stations.py'):
        print(f"[override mode={mode}] stations.py served from memory, {len(src)} bytes", file=sys.stderr)
        return compile(src, self.path, 'exec')
    return orig(self, fullname)
SourceFileLoader.get_code = get_code
sys.argv = ['tests/unit/test-plan-merge-first-station.py']
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
    code = 0
except SystemExit as e:
    code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
print(f"EXIT mode={mode} status={code}")
PY
}
for m in base m8 fixed; do echo "=================== $m"; run $m 2>&1 | cut -c1-330; done
git status --porcelain
```
Final `git status --porcelain` printed nothing (pin clean).

### B. Raw output, mode base (pre-fix stations.py), `EXIT mode=base status=1`
```
[override mode=base] stations.py served from memory, 15537 bytes
PASS a status-less task gains its first station at its field indent: exit 0
FAIL a status-less task gains its first station at its field indent: the whole file is exactly the expected bytes "schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  date: '2026-11-22'\n  approved_by: Fixture Signer\n  status: approved\nstatus: building\ntasks:\n- id: T-01\n  title: Drafted without a station\n  verify: |\n  [cut]
PASS a status-less task gains its first station at its field indent: reports its outcome
PASS a status-less task gains its first station at its field indent: prints APPLIED only on success
PASS an existing status is rewritten and every other byte is unchanged: exit 0
PASS an existing status is rewritten and every other byte is unchanged: the whole file is exactly the expected bytes
PASS an existing status is rewritten and every other byte is unchanged: reports its outcome
PASS an existing status is rewritten and every other byte is unchanged: prints APPLIED only on success
PASS a genuinely absent task refuses with exit 3 and writes nothing: exit 3
PASS a genuinely absent task refuses with exit 3 and writes nothing: the whole file is exactly the expected bytes
PASS a genuinely absent task refuses with exit 3 and writes nothing: reports its outcome
PASS a genuinely absent task refuses with exit 3 and writes nothing: prints APPLIED only on success
FAIL the first station sits inside T-01's own mapping, before T-02 ['schema: plan/1', 'feature: FEAT-99-fixture', 'approval:', "  date: '2026-11-22'", '  approved_by: Fixture Signer', '  status: approved', 'status: building', 'tasks:', '- id: T-01', '  title: Drafted without a station', '  verify: |', '    status: building', '- [cut]
FAIL T-01's verify prose keeps its own `status: prose` line ['schema: plan/1', 'feature: FEAT-99-fixture', 'approval:', "  date: '2026-11-22'", '  approved_by: Fixture Signer', '  status: approved', 'status: building', 'tasks:', '- id: T-01', '  title: Drafted without a station', '  verify: |', '    status: building', '- id: T-0 [cut]
PASS the absent-task refusal never blames a status line
FAIL the first-station insert on a signed plan succeeds rc=3
FAIL the signed approval block is byte-identical after the insert schema: plan/1
feature: FEAT-99-fixture
approval:
  date: '2026-11-22'
  approved_by: Fixture Signer
  status: approved
status: building
tasks:
- id: T-01
  title: Drafted without a station
- id: T-02
  title: Already stationed
  status: ready

FAIL test-plan-merge-first-station.py
EXIT mode=base status=1
```

### C. Raw output, mode m8 (CRLF insert), `EXIT mode=m8 status=1`
```
[override mode=m8] stations.py served from memory, 16053 bytes
PASS a status-less task gains its first station at its field indent: exit 0
FAIL a status-less task gains its first station at its field indent: the whole file is exactly the expected bytes "schema: plan/1\nfeature: FEAT-99-fixture\napproval:\n  date: '2026-11-22'\n  approved_by: Fixture Signer\n  status: approved\nstatus: building\ntasks:\n- id: T-01\n  status: building\r\n  title: Drafted without a st [cut]
PASS a status-less task gains its first station at its field indent: reports its outcome
PASS a status-less task gains its first station at its field indent: prints APPLIED only on success
PASS an existing status is rewritten and every other byte is unchanged: exit 0
PASS an existing status is rewritten and every other byte is unchanged: the whole file is exactly the expected bytes
PASS an existing status is rewritten and every other byte is unchanged: reports its outcome
PASS an existing status is rewritten and every other byte is unchanged: prints APPLIED only on success
PASS a genuinely absent task refuses with exit 3 and writes nothing: exit 3
PASS a genuinely absent task refuses with exit 3 and writes nothing: the whole file is exactly the expected bytes
PASS a genuinely absent task refuses with exit 3 and writes nothing: reports its outcome
PASS a genuinely absent task refuses with exit 3 and writes nothing: prints APPLIED only on success
PASS the first station sits inside T-01's own mapping, before T-02
PASS T-01's verify prose keeps its own `status: prose` line
PASS the absent-task refusal never blames a status line
PASS the first-station insert on a signed plan succeeds
PASS the signed approval block is byte-identical after the insert
FAIL test-plan-merge-first-station.py
EXIT mode=m8 status=1
```

### D. Raw output, mode fixed (control), `EXIT mode=fixed status=0`
Recorded: `[override mode=fixed] stations.py served from memory, 16051 bytes`, then all 17 rows PASS (the same 17 row names as sections B/C, now including "the whole file is exactly the expected bytes" for row 1 and the three post-row checks), then `PASS test-plan-merge-first-station.py` and `EXIT mode=fixed status=0`. Rows are condensed here to this sentence; the transcript form is identical to section C with row 1's whole-file line PASS.

### E. Runner invocations as recorded
```sh
unset HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE
python3 $P/.claude/skills/harness/bin/run-unit-tests.py --kind unit --shard 1/1 --manifest $F/runs/2026-11-22-04-validate-validator/qa/manifest-unit.json 2>&1 | tail -25
# tail: "pool: 8 workers, 66 files, 24.18s wall"; RUNNER_EXIT=0
python3 $P/.claude/skills/harness/bin/run-unit-tests.py --kind integration --shard 1/1 --manifest $F/runs/2026-11-22-04-validate-validator/qa/manifest-integration.json 2>&1 | tail -8
# tail: "ALL PASSED.", "PASS test-validate-digest.py", "pool: 8 workers, 95 files, 170.39s wall"; RUNNER_EXIT=0
```
Receipt read-back printed `unit 2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd 0 66 [...]` and `integration 2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd 0 95 [...]` (tested_commit, runner_exit, selected count); pin `git status --porcelain` empty afterwards. The runs were serial (integration started after unit returned).

### F. Literal T-01 verify: both executions as recorded
Both used `cd /tmp; export BUG2420_TOOL_ROOT=<pin> BUG2420_BASE=d5be53927009df8e7848f860f9d0b4b03b89f9ad`, then the plan's block verbatim inside a `( ... )` subshell (`set -eu`, `cd "$BUG2420_TOOL_ROOT"`, `unset HARNESS_PROJECT_DIR HARNESS_AGENT_TYPE`, `git rev-parse HEAD`, unit script, integration script, check-plan-routes on plan.yaml, `--canonical-reader-audit`, the code-grade Python heredoc).
- Execution 1 (MISTAKE, silent): the subshell's output was redirected `> /dev/null 2>&1` by me. Only `first-pass-silent exit=0` was printed. It carried exit status 0, but I have no output from it and cite no evidence from it.
- Execution 2 (evidence): same block, output piped through `grep -E` / `cut -c1-200` / `head -50`; `verify_exit=${PIPESTATUS[0]}` printed `verify_exit=0`. Recorded filtered output:
```
2b5b8b2aa7f411d515641ef0c73c0e6f7a7e07cd
PASS test-plan-merge-first-station.py
PASS  set-key runs the lanes validator rather than bypassing it
PASS  2420: apply drafts T-01 into an inline-empty tasks list (exit 0)
PASS  2420: apply does not seed a station on the drafted task
PASS  2420: set-task-station gives the drafted task its first station (exit 0)
PASS  2420: the written plan reloads with T-01 at building
PASS test-plan-merge.py
DEVIATION T-01 .claude/skills/harness/bin/plan_merge/stations.py, tests/integration/test-plan-merge.py, tests/unit/test-plan-merge-first-station.py granted to harness-backend-dev, harness-dev-ops, har [cut]
0 violation(s) across 1 plan(s)
0 unresolved reader site(s) across 101 Python file(s)
{"passing": 12, "records": [{"abc": 11.9, "bar": 4, "cognitive": 2, "cognitive_method": "Sonar-style approximation", "cyclomatic": 3, "driver": "abc", "grade": 4, "line": 193, "path": ".claude/skills/ [cut]
BUG-2420 grades PASS: production >=4, tests >=3
verify_exit=0
```
Unmatched lines (for example the ~700 integration PASS rows) were filtered out and are not preserved; the exit status 0 of the whole `set -eu` block is the full-block result.
