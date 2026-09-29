# FEAT-1928 T-02 validator parity — baseline half

Baseline recorded 2026-09-29 by the main-session-direct build (DEC-174). The `new result`
and `match` columns are left blank for the object-validator run.

## Immutable pins

- Baseline SHA (worktree HEAD, branch feat/FEAT-1928-digest-object-contract): `70c3377679b0c28aa969044453e3454a33c059cb`
- `.claude/skills/harness/bin/validate-digest.py` sha256 at baseline: `9fbec17bedd7e570c5431239a5ac8d9bdff3b1331bd139d1b4b5cc31999860a6`
- Machine-readable results: `receipt-scripts/baseline.json`; per-case input text, object mapping and baseline reasons: `receipt-scripts/parity-fixtures/P####.json`.

## Commands

```
cd .harness/harness/features/FEAT-1928-digest-object-contract/notes/receipt-scripts
python3 parity-baseline.py           # writes parity-fixtures/, baseline.json, parity-table.md
python3 parity-baseline.py --check   # re-runs every case; result: "291 cases, 0 drift"
```

The harness loads each owning test module and runs its groups unchanged, wrapping
`subprocess.run` so every call to the baseline `validate-digest.py` (CLI `<persona>` or
`--hook`) is recorded with its stdin and exit code; the shadow suite is observed through its
`_errors` seam (in-process `validate()`); the claim-lifecycle probe's two digest constants
are run through the CLI with the persona the probe dispatches (the live probe needs OMP and a
provider); readers run `validate('lead', text)` (ctx.lead_digest, INV-15/46) plus
`check_state.run_state._inv15_digest_verdict` (INV-46/47 tail VERDICT). Calls to other
binaries (mutants, vendored prior-revision fixtures) are not baseline cases and are excluded.
Accept = exit 0; hook mode rejects with exit 2, CLI with exit 1. Object mapping =
`yaml.safe_load` of the text from the last `^\s*VERDICT:` anchor.

## Counts per source

| source | cases | accept | reject | owning file |
|---|---|---|---|---|
| cli (CASES, run_cli_cases) | 135 | 50 | 85 | tests/integration/test-validate-digest.py |
| hook (HOOK_CASES, run_hook_cases) | 26 | 11 | 15 | tests/integration/test-validate-digest.py |
| hook-group (empty_red 1, dec156_worktree_red 1, bug919 qa matrix 8, bug1305 5, t09 9, t51 4, bug1898 41) | 69 | 14 | 55 | tests/integration/test-validate-digest.py |
| cli-group (canonical_reader 1, joint_hint 3, code_grade 3, template 2, t04_unknown_key 2, t08_revision_proof 3) | 14 | 7 | 7 | tests/integration/test-validate-digest.py |
| shadow (38 validate() calls behind 36 named checks) | 38 | 20 | 18 | tests/integration/test-validate-digest-shadows.py |
| claim-lifecycle | 2 | 2 | 0 | tests/manual/probe-inflight-claim-lifecycle.py |
| reader (INV-15/46/47) | 7 | 2 | 5 | tests/integration/test-check-state-records.py, test-check-state-feat59.py |
| **total** | **291** | 106 | 185 | |

CLI count confirms the plan's 135 named CLI cases (`len(CASES) == 135`, asserted by the
harness). Groups other than CASES/HOOK_CASES carry no per-call name, so their rows are named
`<group>#<call index>`; the shadow rows are `<case function>#<call index>`. Reader rows for
the INV-47 notes are rejected by `validate('lead')` by design (member notes are not lead
digests); their baseline value that INV-47 consumes is the tail verdict stored in the fixture
(`BLOCKED`, `PASS`, `n/a`).

## Syntax-only cases (no object equivalent) and their object-level counterpart

| id | case | baseline | why no object | counterpart |
|---|---|---|---|---|
| P0000 | run_canonical_reader_strictness_cases#000 | accept (hook fails open on duplicate `agent_type` JSON key) | payload not a digest (`not governed` string) | extra (duplicate key) |
| P0025 | three fields on one line loses two | reject | YAML error: fields jammed on one line | missing (`steps_run`, `cycles_used`) |
| P0136 | run_empty_red_case#000 | reject | blank message | missing |
| P0157 | empty-string blank final message | reject | blank message | missing |
| P0158 | absent-key last_assistant_message | accept (fail-open "our gap") | no text | missing (absent data must now be blocked) |
| P0159 | null-passthrough | accept (fail-open) | null text | missing (null data must now be blocked) |
| P0161 | stop_hook_active pass-through | accept | bare string `done` | wrong-type (string data) |
| P0169 | F6 missing agent_type | accept (pass-through) | bare string `whatever` | wrong-type (string data) |
| P0194 | run_t51_suspension_cases#002 | reject (children in flight) | no text | missing |
| P0195 | run_t51_suspension_cases#003 | reject (children in flight) | no text | missing |

Every other row (281) has a mapping fixture. Expect intentional divergence on P0000, P0158,
P0159, P0161, P0169: baseline fails open, while the T-02 object contract requires string,
null, absent, or malformed data to be blocked. Record these as planned deltas, not mismatches.
Shadow, hook-group, and reader results also depend on the fixture checkout or registry state
the owning test builds (git range, claims, artifacts). A fixture pins the digest and object
only, so the new-result run has to rebuild that state through the same test groups.

## Table

| case | source | persona | baseline result | object fixture | syntax-only counterpart | new result | match |
|---|---|---|---|---|---|---|---|
| P0000 run_canonical_reader_strictness_cases#000 | cli-group:run_canonical_reader_strictness_cases | Explore | accept (exit 0) | parity-fixtures/P0000.json | syntax-only: extra |  |  |
| P0001 lead, block-style members + bare empty key | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0001.json |  |  |  |
| P0002 amendments: the three BUG-285 recommendations are accepted eng-lead amendments | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0002.json |  |  |  |
| P0003 amendments: absent is legal | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0003.json |  |  |  |
| P0004 amendments: empty list is legal | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0004.json |  |  |  |
| P0005 amendments: inline mappings for all three fields | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0005.json |  |  |  |
| P0006 amendments: block mapping entry | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0006.json |  |  |  |
| P0007 amendments: unknown key is refused naming index and key | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0007.json |  |  |  |
| P0008 amendments: missing key is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0008.json |  |  |  |
| P0009 amendments: not a list is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0009.json |  |  |  |
| P0010 amendments: entry that is not a mapping is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0010.json |  |  |  |
| P0011 amendments: SC id as task is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0011.json |  |  |  |
| P0012 amendments: decision id as task is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0012.json |  |  |  |
| P0013 amendments: field outside intent/files/verify is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0013.json |  |  |  |
| P0014 amendments: empty reason is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0014.json |  |  |  |
| P0015 amendments: reason over 240 is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0015.json |  |  |  |
| P0016 amendments: intent with a list value is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0016.json |  |  |  |
| P0017 amendments: files with a string value is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0017.json |  |  |  |
| P0018 amendments: files with a line-number anchor is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0018.json |  |  |  |
| P0019 amendments: files with a bad mapping entry is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0019.json |  |  |  |
| P0020 amendments: second entry's fault is reported at its index | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0020.json |  |  |  |
| P0021 amendments: a product lead may not carry the field | cli | harness-product-lead | reject (exit 1) | parity-fixtures/P0021.json |  |  |  |
| P0022 amendments: a validator lead may not carry the field | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0022.json |  |  |  |
| P0023 lead, fully inline lists | cli | harness-validator-lead | accept (exit 0) | parity-fixtures/P0023.json |  |  |  |
| P0024 nested must_fix must NOT satisfy the top-level one | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0024.json |  |  |  |
| P0025 three fields on one line loses two | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0025.json | syntax-only: missing |  |  |
| P0026 doer, inline — unchanged behaviour | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0026.json |  |  |  |
| P0027 main-session (DEC-174 direct build) validates as dev | cli | main-session | accept (exit 0) | parity-fixtures/P0027.json |  |  |  |
| P0028 main-session with task_verify fail and VERDICT PASS is refused like any dev | cli | main-session | reject (exit 1) | parity-fixtures/P0028.json |  |  |  |
| P0029 drifted key spelling is caught | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0029.json |  |  |  |
| P0030 enum near-miss is caught, not normalized | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0030.json |  |  |  |
| P0031 open_questions as a count, not a list | cli | harness-qa | reject (exit 1) | parity-fixtures/P0031.json |  |  |  |
| P0032 bare key followed by nothing is an empty list | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0032.json |  |  |  |
| P0033 inline # comments are stripped, not parsed | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0033.json |  |  |  |
| P0034 # inside a quoted value survives | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0034.json |  |  |  |
| P0035 no VERDICT at all | cli | harness-qa | reject (exit 1) | parity-fixtures/P0035.json |  |  |  |
| P0036 PASS over a failing member is rejected | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0036.json |  |  |  |
| P0037 FAIL over an escalating member is rejected | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0037.json |  |  |  |
| P0038 lead may report worse than its members | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0038.json |  |  |  |
| P0039 a members entry with no verdict is rejected | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0039.json |  |  |  |
| P0040 a skipped member is explicit and excluded from worst-wins | cli | harness-product-lead | accept (exit 0) | parity-fixtures/P0040.json |  |  |  |
| P0041 all skipped members cannot support a lead verdict | cli | harness-product-lead | reject (exit 1) | parity-fixtures/P0041.json |  |  |  |
| P0042 mandatory member cannot be laundered as skipped | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0042.json |  |  |  |
| P0043 DIGEST: with a trailing comment is still recognized | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0043.json |  |  |  |
| P0044 block-mapping member entries spanning lines are accepted | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0044.json |  |  |  |
| P0045 a member's nested headline does not satisfy the top-level one | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0045.json |  |  |  |
| P0046 an int does not satisfy a str-typed field | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0046.json |  |  |  |
| P0047 a bare NULLABLE scalar key must not silently become an empty list | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0047.json |  |  |  |
| P0048 a nested open_questions count must not trip the top-level check | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0048.json |  |  |  |
| P0049 drift in a UNIVERSAL field is caught, not just schema fields | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0049.json |  |  |  |
| P0050 orchestrator digest with the reconciled schema | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0050.json |  |  |  |
| P0051 orchestrator briefing is NULLABLE — `none` when nothing was written | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0051.json |  |  |  |
| P0052 rejected: reject judgement with a superseding issue is accepted | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0052.json |  |  |  |
| P0053 rejected: superseded_by none (should not be planned) is accepted | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0053.json |  |  |  |
| P0054 rejected: no judgement mapping is refused naming it | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0054.json |  |  |  |
| P0055 rejected: kind other than reject is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0055.json |  |  |  |
| P0056 rejected: superseded_by zero is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0056.json |  |  |  |
| P0057 rejected: superseded_by negative is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0057.json |  |  |  |
| P0058 rejected: superseded_by boolean is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0058.json |  |  |  |
| P0059 rejected: empty reason is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0059.json |  |  |  |
| P0060 rejected: reason over 240 characters is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0060.json |  |  |  |
| P0061 rejected: multiline reason is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0061.json |  |  |  |
| P0062 rejected: a missing key is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0062.json |  |  |  |
| P0063 rejected: an extra key is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0063.json |  |  |  |
| P0064 rejected: cycles_used must be integer zero | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0064.json |  |  |  |
| P0065 a judgement mapping on any other status is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0065.json |  |  |  |
| P0066 echo shadow: valid real FAIL after a template echo still validates | cli | harness-qa | accept (exit 0) | parity-fixtures/P0066.json |  |  |  |
| P0067 echo shadow: missing matrix_ok in the real block is not masked by the echo | cli | harness-qa | reject (exit 1) | parity-fixtures/P0067.json |  |  |  |
| P0068 echo shadow: lead roll-up must read the real members, not the echo | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0068.json |  |  |  |
| P0069 dev refusing an under-specified task can say suite: n/a | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0069.json |  |  |  |
| P0070 suite: n/a with VERDICT PASS is a fail-open and is REJECTED | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0070.json |  |  |  |
| P0071 an analysis dev -- task: none AND files_touched: [] -- may say suite: n/a with PASS | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0071.json |  |  |  |
| P0072 task: none but files WERE touched -- suite: n/a with PASS is still REJECTED, because `task: none` is a claim and the edit is the fact | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0072.json |  |  |  |
| P0073 a REAL task whose verify passed still owes a suite result -- suite: n/a with PASS is REJECTED even with nothing touched | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0073.json |  |  |  |
| P0074 qa that cannot run the suite can say matrix_ok: n/a | cli | harness-qa | accept (exit 0) | parity-fixtures/P0074.json |  |  |  |
| P0075 matrix_ok: n/a with VERDICT PASS is REJECTED — the gate did not run | cli | harness-qa | reject (exit 1) | parity-fixtures/P0075.json |  |  |  |
| P0076 reviewer scoping out of a non-UI diff may PASS with severity_max: n/a | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0076.json |  |  |  |
| P0077 visual-designer deciding no DESIGN.md is needed may say contract: n/a | cli | harness-visual-designer | accept (exit 0) | parity-fixtures/P0077.json |  |  |  |
| P0078 pm blocked before sizing may say surface: n/a and risk: n/a | cli | harness-pm | accept (exit 0) | parity-fixtures/P0078.json |  |  |  |
| P0079 matrix_ok: mostly is STILL rejected after n/a became legal | cli | harness-qa | reject (exit 1) | parity-fixtures/P0079.json |  |  |  |
| P0080 severity_max: medium is STILL rejected after n/a became legal | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0080.json |  |  |  |
| P0081 dev-ops suite: n/a still accepted (it had the value before DEC-173) | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0081.json |  |  |  |
| P0082 dev missing task_verify under a real task is rejected | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0082.json |  |  |  |
| P0083 dev task_verify: fail + PASS is rejected | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0083.json |  |  |  |
| P0084 dev task_verify: n/a + PASS is rejected | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0084.json |  |  |  |
| P0085 dev-ops task_verify: fail + PASS is rejected — no carve-out on this value either | cli | harness-dev-ops | reject (exit 1) | parity-fixtures/P0085.json |  |  |  |
| P0086 dev-ops task_verify: n/a + PASS is rejected — no carve-out | cli | harness-dev-ops | reject (exit 1) | parity-fixtures/P0086.json |  |  |  |
| P0087 dev task_verify: n/a + BLOCKED is the honest refusal, accepted | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0087.json |  |  |  |
| P0088 dev task_verify: n/a + FAIL is accepted — the same refusal, other verdict | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0088.json |  |  |  |
| P0089 dev-ops task_verify: n/a + BLOCKED is accepted — refusal, not the carve-out | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0089.json |  |  |  |
| P0090 dev-ops task_verify: n/a + FAIL is accepted | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0090.json |  |  |  |
| P0091 qa carries neither new field and is still accepted | cli | harness-qa | accept (exit 0) | parity-fixtures/P0091.json |  |  |  |
| P0092 dev task: none with task_verify omitted is accepted — D-07's escape hatch | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0092.json |  |  |  |
| P0093 dev-ops task: none with task_verify omitted is accepted | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0093.json |  |  |  |
| P0094 dev task: bogus is rejected — the field is constrained | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0094.json |  |  |  |
| P0095 dev omitting task entirely is rejected — the field is required | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0095.json |  |  |  |
| P0096 dev task: none + task_verify: fail is rejected as a contradiction | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0096.json |  |  |  |
| P0097 dev task: none + task_verify: n/a is accepted — the honest DEC-121 spelling | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0097.json |  |  |  |
| P0098 dev suite: fail + PASS is rejected — the fail-value gate | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0098.json |  |  |  |
| P0099 qa suite: fail + PASS is rejected | cli | harness-qa | reject (exit 1) | parity-fixtures/P0099.json |  |  |  |
| P0100 qa matrix_ok: false + PASS is rejected — the BOOLEAN half | cli | harness-qa | reject (exit 1) | parity-fixtures/P0100.json |  |  |  |
| P0101 dev-ops suite: fail + PASS stays accepted — D-03 ruling, not a claim it is right | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0101.json |  |  |  |
| P0102 a documentor digest carries neither new field and is still accepted | cli | harness-documentor | accept (exit 0) | parity-fixtures/P0102.json |  |  |  |
| P0103 code reviewer omission of code_grade is rejected | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0103.json |  |  |  |
| P0104 code_grade's missing-field hint names the four legal values, not the list wording | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0104.json |  |  |  |
| P0105 task_verify's missing-field hint names its real values, not the none wording | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0105.json |  |  |  |
| P0106 task's missing-field hint names a task id, not the list wording | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0106.json |  |  |  |
| P0107 FEAT-59 finding without kind is rejected, naming the entry and the enum | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0107.json |  |  |  |
| P0108 FEAT-59 finding with a kind outside the enum is rejected, naming the value | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0108.json |  |  |  |
| P0109 FEAT-59 kind: substantive (near-miss) is rejected, not normalised | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0109.json |  |  |  |
| P0110 FEAT-59 a bare-string finding has no kind and is rejected | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0110.json |  |  |  |
| P0111 FEAT-59 the error names the offending entry's index, not the first | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0111.json |  |  |  |
| P0112 FEAT-59 kind: substance is accepted (inline entry) | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0112.json |  |  |  |
| P0113 FEAT-59 kind: form is accepted (block-mapping entry) | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0113.json |  |  |  |
| P0114 FEAT-59 kind: proportionality with scope: mission is accepted | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0114.json |  |  |  |
| P0115 DEC-228 kind: proportionality with scope: task is accepted | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0115.json |  |  |  |
| P0116 DEC-228 kind: proportionality without scope is rejected, naming both scopes | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0116.json |  |  |  |
| P0117 DEC-228 kind: proportionality with a scope outside task\|mission is rejected | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0117.json |  |  |  |
| P0118 FEAT-59 findings: [] is accepted — an explicit empty list asserts you looked | cli | harness-security-reviewer | accept (exit 0) | parity-fixtures/P0118.json |  |  |  |
| P0119 FEAT-59 findings as an INT count is rejected — it is a list of kinded entries | cli | harness-security-reviewer | reject (exit 1) | parity-fixtures/P0119.json |  |  |  |
| P0120 FEAT-59 lead findings passthrough: kinded entries are accepted alongside readers: | cli | harness-validator-lead | accept (exit 0) | parity-fixtures/P0120.json |  |  |  |
| P0121 FEAT-59 lead findings passthrough: an entry without kind is rejected | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0121.json |  |  |  |
| P0122 FEAT-59 qa PASS + matrix_ok: true + fail_first: [] is REJECTED — a green suite with no fail-first evidence is not a pass | cli | harness-qa | reject (exit 1) | parity-fixtures/P0122.json |  |  |  |
| P0123 FEAT-59 qa PASS with populated fail_first is accepted | cli | harness-qa | accept (exit 0) | parity-fixtures/P0123.json |  |  |  |
| P0124 FEAT-59 qa matrix_ok: n/a with fail_first: [] is accepted — no gate ran | cli | harness-qa | accept (exit 0) | parity-fixtures/P0124.json |  |  |  |
| P0125 FEAT-59 qa FAIL with fail_first: [] is accepted — the gate is on PASS | cli | harness-qa | accept (exit 0) | parity-fixtures/P0125.json |  |  |  |
| P0126 FEAT-59 qa omitting fail_first is rejected — every field is required | cli | harness-qa | reject (exit 1) | parity-fixtures/P0126.json |  |  |  |
| P0127 FEAT-59 fail_first's missing-field hint names the entry shape, not `[]` | cli | harness-qa | reject (exit 1) | parity-fixtures/P0127.json |  |  |  |
| P0128 FEAT-59 fail_first entry without sc is rejected, naming the index | cli | harness-qa | reject (exit 1) | parity-fixtures/P0128.json |  |  |  |
| P0129 FEAT-59 fail_first entry with empty evidence is rejected, naming the index | cli | harness-qa | reject (exit 1) | parity-fixtures/P0129.json |  |  |  |
| P0130 FEAT-59 fail_first bare-string entry is rejected | cli | harness-qa | reject (exit 1) | parity-fixtures/P0130.json |  |  |  |
| P0131 FEAT-59 fail_first sc must be an SC-NN id | cli | harness-qa | reject (exit 1) | parity-fixtures/P0131.json |  |  |  |
| P0132 FEAT-59 fail_first block-mapping entries are accepted | cli | harness-qa | accept (exit 0) | parity-fixtures/P0132.json |  |  |  |
| P0133 #1854: a member's nested block list stays inside that member | cli | harness-validator-lead | accept (exit 0) | parity-fixtures/P0133.json |  |  |  |
| P0134 #1854: a nested list does not hide a member that genuinely lacks a verdict | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0134.json |  |  |  |
| P0135 #1854: a nested member verdict still rolls up worst-wins | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0135.json |  |  |  |
| P0136 run_empty_red_case#000 | hook-group:run_empty_red_case | harness-qa | reject (exit 2) | parity-fixtures/P0136.json | syntax-only: missing |  |  |
| P0137 run_dec156_worktree_red_case#000 | hook-group:run_dec156_worktree_red_case | harness-eng-lead | reject (exit 2) | parity-fixtures/P0137.json |  |  |  |
| P0138 run_bug919_qa_matrix_cases#000 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0138.json |  |  |  |
| P0139 run_bug919_qa_matrix_cases#001 | hook-group:run_bug919_qa_matrix_cases | harness-qa | reject (exit 2) | parity-fixtures/P0139.json |  |  |  |
| P0140 run_bug919_qa_matrix_cases#002 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0140.json |  |  |  |
| P0141 run_bug919_qa_matrix_cases#003 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0141.json |  |  |  |
| P0142 run_bug919_qa_matrix_cases#004 | hook-group:run_bug919_qa_matrix_cases | harness-qa | reject (exit 2) | parity-fixtures/P0142.json |  |  |  |
| P0143 run_bug919_qa_matrix_cases#005 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0143.json |  |  |  |
| P0144 run_bug919_qa_matrix_cases#006 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0144.json |  |  |  |
| P0145 run_bug919_qa_matrix_cases#007 | hook-group:run_bug919_qa_matrix_cases | harness-qa | reject (exit 2) | parity-fixtures/P0145.json |  |  |  |
| P0146 run_joint_hint_case#000 | cli-group:run_joint_hint_case | harness-backend-dev | reject (exit 1) | parity-fixtures/P0146.json |  |  |  |
| P0147 run_joint_hint_case#001 | cli-group:run_joint_hint_case | harness-backend-dev | accept (exit 0) | parity-fixtures/P0147.json |  |  |  |
| P0148 run_joint_hint_case#002 | cli-group:run_joint_hint_case | harness-backend-dev | accept (exit 0) | parity-fixtures/P0148.json |  |  |  |
| P0149 run_code_grade_cases#000 | cli-group:run_code_grade_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0149.json |  |  |  |
| P0150 run_code_grade_cases#001 | cli-group:run_code_grade_cases | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0150.json |  |  |  |
| P0151 run_code_grade_cases#002 | cli-group:run_code_grade_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0151.json |  |  |  |
| P0152 F1.1 quoted headline text must not satisfy the verdict lookup | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0152.json |  |  |  |
| P0153 F1.2 multi-line inline members list is followed to its close | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0153.json |  |  |  |
| P0154 F1.3 unquoted apostrophe must not fuse list entries | hook | harness-validator-lead | reject (exit 2) | parity-fixtures/P0154.json |  |  |  |
| P0155 F1.4 empty members against a nonzero steps_run is rejected | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0155.json |  |  |  |
| P0156 fail-open crash: list-valued enum is a reported violation, not a crash | hook | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0156.json |  |  |  |
| P0157 empty-string: a present but blank final message is the persona's violation | hook | harness-qa | reject (exit 2) | parity-fixtures/P0157.json | syntax-only: missing |  |  |
| P0158 absent-key: nothing supplied to validate is OUR gap, and is said so | hook | harness-qa | accept (exit 0) | parity-fixtures/P0158.json | syntax-only: missing |  |  |
| P0159 null-passthrough: an explicitly null final message is the same our-gap branch | hook | harness-qa | accept (exit 0) | parity-fixtures/P0159.json | syntax-only: missing |  |  |
| P0160 pass-through: non-harness agent_type is not governed | hook | Explore | accept (exit 0) | parity-fixtures/P0160.json |  |  |  |
| P0161 pass-through: stop_hook_active avoids the infinite-block loop | hook | harness-qa | accept (exit 0) | parity-fixtures/P0161.json | syntax-only: wrong-type |  |  |
| P0162 DEC-156: narrative digest.md with no contract block is exit 2 | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0162.json |  |  |  |
| P0163 DEC-156: digest.md carrying the same valid block is exit 0 | hook | harness-eng-lead | accept (exit 0) | parity-fixtures/P0163.json |  |  |  |
| P0164 DEC-156: missing digest in a resolved run directory is refused | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0164.json |  |  |  |
| P0165 DEC-156: file check governs leads only — a dev's artifact is not read | hook | harness-backend-dev | accept (exit 0) | parity-fixtures/P0165.json |  |  |  |
| P0166 dec156-worktree-narrative: worktree narrative digest is rejected | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0166.json |  |  |  |
| P0167 dec156-worktree-valid: valid worktree digest passes | hook | harness-eng-lead | accept (exit 0) | parity-fixtures/P0167.json |  |  |  |
| P0168 dec156-worktree-nofeature: absent feature preserves fail-open fallback | hook | harness-eng-lead | accept (exit 0) | parity-fixtures/P0168.json |  |  |  |
| P0169 F6 missing agent_type key is loud, not silent | hook | None | accept (exit 0) | parity-fixtures/P0169.json | syntax-only: wrong-type |  |  |
| P0170 echo shadow [hook]: missing matrix_ok behind an echo is exit 2 | hook | harness-qa | reject (exit 2) | parity-fixtures/P0170.json |  |  |  |
| P0171 #1855: qa on a distill dispatch may PASS with suite/matrix_ok n/a | hook | harness-qa | accept (exit 0) | parity-fixtures/P0171.json |  |  |  |
| P0172 #1855: the same qa return outside distill is still the fail-open it always was | hook | harness-qa | reject (exit 2) | parity-fixtures/P0172.json |  |  |  |
| P0173 #1855: qa on a distill dispatch may not decorate the return with a suite it did not run | hook | harness-qa | reject (exit 2) | parity-fixtures/P0173.json |  |  |  |
| P0174 #1855: code-reviewer on a distill dispatch may PASS with code_grade n_a and no range | hook | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0174.json |  |  |  |
| P0175 #1855: the same reviewer return outside distill is refused at the binding | hook | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0175.json |  |  |  |
| P0176 #1855: a distill reviewer claiming a grade is refused — there is no diff to grade | hook | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0176.json |  |  |  |
| P0177 #1855: an unknown mission changes nothing | hook | harness-qa | reject (exit 2) | parity-fixtures/P0177.json |  |  |  |
| P0178 run_bug1305_artifact_resolution_cases#000 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0178.json |  |  |  |
| P0179 run_bug1305_artifact_resolution_cases#001 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | accept (exit 0) | parity-fixtures/P0179.json |  |  |  |
| P0180 run_bug1305_artifact_resolution_cases#002 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0180.json |  |  |  |
| P0181 run_bug1305_artifact_resolution_cases#003 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0181.json |  |  |  |
| P0182 run_bug1305_artifact_resolution_cases#004 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | accept (exit 0) | parity-fixtures/P0182.json |  |  |  |
| P0183 run_t09#000 | hook-group:run_t09 | harness-pm | accept (exit 0) | parity-fixtures/P0183.json |  |  |  |
| P0184 run_t09#001 | hook-group:run_t09 | harness-pm | reject (exit 2) | parity-fixtures/P0184.json |  |  |  |
| P0185 run_t09#002 | hook-group:run_t09 | harness-pm | accept (exit 0) | parity-fixtures/P0185.json |  |  |  |
| P0186 run_t09#003 | hook-group:run_t09 | harness-documentor | reject (exit 2) | parity-fixtures/P0186.json |  |  |  |
| P0187 run_t09#004 | hook-group:run_t09 | harness-eng-lead | reject (exit 2) | parity-fixtures/P0187.json |  |  |  |
| P0188 run_t09#005 | hook-group:run_t09 | harness-eng-lead | accept (exit 0) | parity-fixtures/P0188.json |  |  |  |
| P0189 run_t09#006 | hook-group:run_t09 | harness-pm | accept (exit 0) | parity-fixtures/P0189.json |  |  |  |
| P0190 run_t09#007 | hook-group:run_t09 | harness-eng-lead | accept (exit 0) | parity-fixtures/P0190.json |  |  |  |
| P0191 run_t09#008 | hook-group:run_t09 | harness-eng-lead | reject (exit 2) | parity-fixtures/P0191.json |  |  |  |
| P0192 run_t51_suspension_cases#000 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0192.json |  |  |  |
| P0193 run_t51_suspension_cases#001 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0193.json |  |  |  |
| P0194 run_t51_suspension_cases#002 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0194.json | syntax-only: missing |  |  |
| P0195 run_t51_suspension_cases#003 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0195.json | syntax-only: missing |  |  |
| P0196 run_bug1898_exact_release_cases#000 | hook-group:run_bug1898_exact_release_cases | harness-ai-dev | reject (exit 2) | parity-fixtures/P0196.json |  |  |  |
| P0197 run_bug1898_exact_release_cases#001 | hook-group:run_bug1898_exact_release_cases | harness-ai-dev | reject (exit 2) | parity-fixtures/P0197.json |  |  |  |
| P0198 run_bug1898_exact_release_cases#002 | hook-group:run_bug1898_exact_release_cases | harness-backend-dev | reject (exit 2) | parity-fixtures/P0198.json |  |  |  |
| P0199 run_bug1898_exact_release_cases#003 | hook-group:run_bug1898_exact_release_cases | harness-backend-dev | reject (exit 2) | parity-fixtures/P0199.json |  |  |  |
| P0200 run_bug1898_exact_release_cases#004 | hook-group:run_bug1898_exact_release_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0200.json |  |  |  |
| P0201 run_bug1898_exact_release_cases#005 | hook-group:run_bug1898_exact_release_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0201.json |  |  |  |
| P0202 run_bug1898_exact_release_cases#006 | hook-group:run_bug1898_exact_release_cases | harness-data-engineer | reject (exit 2) | parity-fixtures/P0202.json |  |  |  |
| P0203 run_bug1898_exact_release_cases#007 | hook-group:run_bug1898_exact_release_cases | harness-data-engineer | reject (exit 2) | parity-fixtures/P0203.json |  |  |  |
| P0204 run_bug1898_exact_release_cases#008 | hook-group:run_bug1898_exact_release_cases | harness-dev-ops | reject (exit 2) | parity-fixtures/P0204.json |  |  |  |
| P0205 run_bug1898_exact_release_cases#009 | hook-group:run_bug1898_exact_release_cases | harness-dev-ops | reject (exit 2) | parity-fixtures/P0205.json |  |  |  |
| P0206 run_bug1898_exact_release_cases#010 | hook-group:run_bug1898_exact_release_cases | harness-documentor | reject (exit 2) | parity-fixtures/P0206.json |  |  |  |
| P0207 run_bug1898_exact_release_cases#011 | hook-group:run_bug1898_exact_release_cases | harness-documentor | reject (exit 2) | parity-fixtures/P0207.json |  |  |  |
| P0208 run_bug1898_exact_release_cases#012 | hook-group:run_bug1898_exact_release_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0208.json |  |  |  |
| P0209 run_bug1898_exact_release_cases#013 | hook-group:run_bug1898_exact_release_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0209.json |  |  |  |
| P0210 run_bug1898_exact_release_cases#014 | hook-group:run_bug1898_exact_release_cases | harness-frontend-dev | reject (exit 2) | parity-fixtures/P0210.json |  |  |  |
| P0211 run_bug1898_exact_release_cases#015 | hook-group:run_bug1898_exact_release_cases | harness-frontend-dev | reject (exit 2) | parity-fixtures/P0211.json |  |  |  |
| P0212 run_bug1898_exact_release_cases#016 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0212.json |  |  |  |
| P0213 run_bug1898_exact_release_cases#017 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0213.json |  |  |  |
| P0214 run_bug1898_exact_release_cases#018 | hook-group:run_bug1898_exact_release_cases | harness-pm | reject (exit 2) | parity-fixtures/P0214.json |  |  |  |
| P0215 run_bug1898_exact_release_cases#019 | hook-group:run_bug1898_exact_release_cases | harness-pm | reject (exit 2) | parity-fixtures/P0215.json |  |  |  |
| P0216 run_bug1898_exact_release_cases#020 | hook-group:run_bug1898_exact_release_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0216.json |  |  |  |
| P0217 run_bug1898_exact_release_cases#021 | hook-group:run_bug1898_exact_release_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0217.json |  |  |  |
| P0218 run_bug1898_exact_release_cases#022 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0218.json |  |  |  |
| P0219 run_bug1898_exact_release_cases#023 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0219.json |  |  |  |
| P0220 run_bug1898_exact_release_cases#024 | hook-group:run_bug1898_exact_release_cases | harness-security-reviewer | reject (exit 2) | parity-fixtures/P0220.json |  |  |  |
| P0221 run_bug1898_exact_release_cases#025 | hook-group:run_bug1898_exact_release_cases | harness-security-reviewer | reject (exit 2) | parity-fixtures/P0221.json |  |  |  |
| P0222 run_bug1898_exact_release_cases#026 | hook-group:run_bug1898_exact_release_cases | harness-ui-reviewer | reject (exit 2) | parity-fixtures/P0222.json |  |  |  |
| P0223 run_bug1898_exact_release_cases#027 | hook-group:run_bug1898_exact_release_cases | harness-ui-reviewer | reject (exit 2) | parity-fixtures/P0223.json |  |  |  |
| P0224 run_bug1898_exact_release_cases#028 | hook-group:run_bug1898_exact_release_cases | harness-validator-lead | reject (exit 2) | parity-fixtures/P0224.json |  |  |  |
| P0225 run_bug1898_exact_release_cases#029 | hook-group:run_bug1898_exact_release_cases | harness-validator-lead | reject (exit 2) | parity-fixtures/P0225.json |  |  |  |
| P0226 run_bug1898_exact_release_cases#030 | hook-group:run_bug1898_exact_release_cases | harness-visual-designer | reject (exit 2) | parity-fixtures/P0226.json |  |  |  |
| P0227 run_bug1898_exact_release_cases#031 | hook-group:run_bug1898_exact_release_cases | harness-visual-designer | reject (exit 2) | parity-fixtures/P0227.json |  |  |  |
| P0228 run_bug1898_exact_release_cases#032 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0228.json |  |  |  |
| P0229 run_bug1898_exact_release_cases#033 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0229.json |  |  |  |
| P0230 run_bug1898_exact_release_cases#034 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0230.json |  |  |  |
| P0231 run_bug1898_exact_release_cases#035 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0231.json |  |  |  |
| P0232 run_bug1898_exact_release_cases#036 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0232.json |  |  |  |
| P0233 run_bug1898_exact_release_cases#037 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | accept (exit 0) | parity-fixtures/P0233.json |  |  |  |
| P0234 run_bug1898_exact_release_cases#038 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0234.json |  |  |  |
| P0235 run_bug1898_exact_release_cases#039 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | accept (exit 0) | parity-fixtures/P0235.json |  |  |  |
| P0236 run_bug1898_exact_release_cases#040 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0236.json |  |  |  |
| P0237 run_template_cases#000 | cli-group:run_template_cases | lead | accept (exit 0) | parity-fixtures/P0237.json |  |  |  |
| P0238 run_template_cases#001 | cli-group:run_template_cases | lead | accept (exit 0) | parity-fixtures/P0238.json |  |  |  |
| P0239 run_t04_unknown_key_cases#000 | cli-group:run_t04_unknown_key_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0239.json |  |  |  |
| P0240 run_t04_unknown_key_cases#001 | cli-group:run_t04_unknown_key_cases | harness-eng-lead | accept (exit 0) | parity-fixtures/P0240.json |  |  |  |
| P0241 run_t08_revision_proof#000 | cli-group:run_t08_revision_proof | harness-pm | reject (exit 2) | parity-fixtures/P0241.json |  |  |  |
| P0242 run_t08_revision_proof#001 | cli-group:run_t08_revision_proof | harness-backend-dev | reject (exit 2) | parity-fixtures/P0242.json |  |  |  |
| P0243 run_t08_revision_proof#002 | cli-group:run_t08_revision_proof | harness-documentor | reject (exit 2) | parity-fixtures/P0243.json |  |  |  |
| P0244 case_matrix_floor#00 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0244.json |  |  |  |
| P0245 case_matrix_floor#01 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0245.json |  |  |  |
| P0246 case_matrix_floor#02 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0246.json |  |  |  |
| P0247 case_matrix_floor#03 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0247.json |  |  |  |
| P0248 case_matrix_floor#04 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0248.json |  |  |  |
| P0249 case_matrix_floor#05 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0249.json |  |  |  |
| P0250 case_human_commits#00 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0250.json |  |  |  |
| P0251 case_human_commits#01 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0251.json |  |  |  |
| P0252 case_human_commits#02 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0252.json |  |  |  |
| P0253 case_human_commits#03 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0253.json |  |  |  |
| P0254 case_human_commits#04 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0254.json |  |  |  |
| P0255 case_human_commits#05 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0255.json |  |  |  |
| P0256 case_dirty_tree#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0256.json |  |  |  |
| P0257 case_dirty_tree#01 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0257.json |  |  |  |
| P0258 case_dirty_tree#02 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0258.json |  |  |  |
| P0259 case_dirty_tree#03 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0259.json |  |  |  |
| P0260 case_dirty_tree#04 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0260.json |  |  |  |
| P0261 case_qa_kinds#00 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0261.json |  |  |  |
| P0262 case_qa_kinds#01 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0262.json |  |  |  |
| P0263 case_qa_kinds#02 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0263.json |  |  |  |
| P0264 case_qa_kinds#03 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0264.json |  |  |  |
| P0265 case_qa_kinds#04 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0265.json |  |  |  |
| P0266 case_qa_kinds#05 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0266.json |  |  |  |
| P0267 case_qa_kinds#06 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0267.json |  |  |  |
| P0268 case_qa_kinds#07 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0268.json |  |  |  |
| P0269 case_receipt#00 | shadow | harness-backend-dev | reject (exit 2) | parity-fixtures/P0269.json |  |  |  |
| P0270 case_receipt#01 | shadow | harness-backend-dev | reject (exit 2) | parity-fixtures/P0270.json |  |  |  |
| P0271 case_receipt#02 | shadow | harness-backend-dev | accept (exit 0) | parity-fixtures/P0271.json |  |  |  |
| P0272 case_receipt#03 | shadow | harness-backend-dev | accept (exit 0) | parity-fixtures/P0272.json |  |  |  |
| P0273 case_inspection_citations#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0273.json |  |  |  |
| P0274 case_inspection_citations#01 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0274.json |  |  |  |
| P0275 case_inspection_citations#02 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0275.json |  |  |  |
| P0276 case_findings_order#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0276.json |  |  |  |
| P0277 case_findings_order#01 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0277.json |  |  |  |
| P0278 case_grade_2_names#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0278.json |  |  |  |
| P0279 case_qa_unearned_fail#00 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0279.json |  |  |  |
| P0280 case_qa_unearned_fail#01 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0280.json |  |  |  |
| P0281 case_qa_unearned_fail#02 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0281.json |  |  |  |
| P0282 S1/S2/S3 orchestrator child DIGEST | claim-lifecycle | harness-orchestrator | accept (exit 0) | parity-fixtures/P0282.json |  |  |  |
| P0283 S3 nested lead LEAD_DIGEST | claim-lifecycle | harness-eng-lead | accept (exit 0) | parity-fixtures/P0283.json |  |  |  |
| P0284 INV-15/46 BUG-440 lead digest FAIL | reader | lead | accept (exit 0) | parity-fixtures/P0284.json |  |  |  |
| P0285 INV-15/46 BUG-440 lead digest PASS | reader | lead | accept (exit 0) | parity-fixtures/P0285.json |  |  |  |
| P0286 INV-15 BUG-440 run X bare 'VERDICT: FAIL' | reader | lead | reject (exit 2) | parity-fixtures/P0286.json |  |  |  |
| P0287 INV-15 feat59 _digest_run 'VERDICT: PASS' | reader | lead | reject (exit 2) | parity-fixtures/P0287.json |  |  |  |
| P0288 INV-47 _QA_BLOCKED note | reader | lead | reject (exit 2) | parity-fixtures/P0288.json |  |  |  |
| P0289 INV-47 _QA_PASS note | reader | lead | reject (exit 2) | parity-fixtures/P0289.json |  |  |  |
| P0290 INV-47 _UI_NA note | reader | lead | reject (exit 2) | parity-fixtures/P0290.json |  |  |  |
