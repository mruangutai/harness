# FEAT-1928 T-02 validator parity — baseline and object halves

Baseline recorded 2026-09-29 by the main-session-direct build (DEC-174); the object half
(`new result`, `match`) recorded 2026-09-29 against the object validator in the same
worktree, re-run under the FEAT-1928 all-required ruling. 291 rows, 14 accept/reject deltas,
every one planned; **0 unplanned mismatches**. The ruling refuses 235 rows as written; each is
compared translated and named in its `match` cell.

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

## Object half

- Object validator: `.claude/skills/harness/bin/validate-digest.py` sha256 `490e67224e0386431a4a087889db54068b903994276d75983a04f76aa28f2de9`
  under the FEAT-1928 all-required schemas (operator ruling, 2026-09-29; see below)
  (worktree HEAD `6512eedab9439af3df475b97aabf30db17925548` plus the uncommitted T-02 slice; the baseline pins above are unchanged).
- Per-row results, reasons and counterpart outcomes: `receipt-scripts/object-results.json`.

```
cd .harness/harness/features/FEAT-1928-digest-object-contract/notes/receipt-scripts
python3 parity-object.py           # re-runs every row; "291 rows, 14 accept/reject deltas, 0 unplanned"
python3 parity-object.py --table   # also fills this table's `new result` and `match` cells
```

`parity-object.py` executes each owning test module from its source AT THE BASELINE SHA
(`git show`), so every group rebuilds exactly the git range, claims, artifacts and stubs it
built for the baseline, while its `VALIDATE` is the object validator. Each validator call is
intercepted and its digest re-expressed as the mapping the case means: CLI stdin text becomes
the JSON object; a hook payload's `last_assistant_message` becomes `digest_object` (absent stays
absent, null stays null, a blank message becomes absent data, a bare string stays a string);
the shadow seam calls `validate(persona, mapping, ...)`. The mapping is `yaml.safe_load` of the
text from its last `^\s*VERDICT:` anchor with the two reading rules the baseline parser applied
and YAML does not: a bare top-level DIGEST key is `[]`, and VERDICT is its first token (a
retired template's `PASS | FAIL | ...` line read as PASS). Rows align to baseline.json by call
order within each group; a count mismatch fails the run.

Four baseline mechanisms no longer exist and are bridged, not skipped: the source-text red
mutants (`_bug919_red_mutant`, `_empty_red_mutant`, `_dec156_owner_root_mutant`) become the
new source plus a comment so each group still makes its real-validator call; the two retired
text templates (`run_template_cases`) are read from the baseline SHA; T-04's in-process half
reads deleted tables, so its two hook calls run through the same helper with the same
three-rogue-key digest; T-08's pre-T-04 validator fixture is deleted with the text contract, so
its three rows are replayed from their recorded fixtures against the object validator only.
Reader rows (INV-15/46/47) are no longer validator calls: SC-07 readers
take digest_record's final fenced mapping without live-schema validation, so the new result is
"record carries VERDICT, DIGEST and artifact" and, for the INV-47 notes, the VERDICT read equals
the baseline tail verdict (BLOCKED, PASS, n/a — all equal).

### The FEAT-1928 all-required ruling (2026-09-29)

The operator ruled that every property in every live schema is REQUIRED: there are no
optional fields and no null. A field that does not apply is `none` (scalar) or `[]` (list).
Conditional fields are always present with their sentinel: dev `task_verify` is `n/a` under
`task: none`, and orchestrator `judgement` is `none` unless `status: rejected`. List-entry
objects are closed and minimal. For example, a finding is `{kind, scope, severity, reader,
summary, why}`, a member is `{step, persona, verdict, headline, files_touched}` or the skipped
form, a kinds entry is `{kind, state, cmd, named_tests}` and a run is `{id, squad, verdict}`.
`must_fix` and `coverage_gaps` are lists of strings.

At the baseline these fields were optional, and omitting one was how a digest said "does not
apply". So, as written, the mapping of **235 of the 291 rows** is refused by the ruling. For
each of those rows, `object-results.json` records `ruling_spelled` together with the schema's
own error count on the untranslated mapping, and that count is non-zero for all 235. Every one
of these rows is named in the table's `match` cell as "as written refused by the FEAT-1928
ruling; translated (…)".

The translation keeps what the baseline validator read. Parity measures whether each semantic
check survived, so a row is compared as the mapping it means under the ruling:

- **Omitted fields.** 222 rows omit a field the ruling made required, and each such field is
  spelled not-applicable. The table is the same one `fixture()` in
  tests/integration/test-validate-digest.py uses: lead `sc_status`, `needs_approval`,
  `severity_max`, `matrix_ok`, `coverage_gaps`, `findings`, `readers` and `adequacy_notes`,
  plus eng-lead `amendments`; dev `task_verify: n/a`; dev-ops `test_kinds_written`; qa `kinds`
  and `sc_evidence`; reviewer `spec_violations`, `human_commits_in_scope` and
  `grade_2_reasons`; the security, UI and visual-designer scope fields; documentor
  `stale_found`; and orchestrator `judgement: none`.
- **Open entries.** 110 rows carry an entry outside the closed shapes, and each such entry is
  closed to its minimal shape. Keys the baseline never read are dropped (a member's
  `must_fix`/`severity_max`), and required keys it never read are spelled `none`/`[]` (a
  member's `headline`/`files_touched`, a finding's `scope`/`reader`/`why`, a kinds entry's
  `cmd`/`named_tests`, a ran reader's `persona`/`reason`). A bare run id becomes
  `{id, squad: none, verdict: none}`. A key the baseline did read is never added: a member
  with no verdict, and a proportionality finding with no scope, stay as written.

Translated, 225 of the 235 rows match the baseline. The other ten are deltas in the table
below. Eight of them are the SC-07 rows, which differ for their SC-07 reason and not because
of the ruling. The remaining two, P0171 and P0174, are the only rows the ruling itself turns
into deltas.

The permanent tests follow the same rule. Each fixture names only the fields its case is about,
and `fixture()` spells every omitted ruling field not-applicable. The cases that pin the
omission itself pass `complete=False`: "amendments: absent is refused", "dev/dev-ops task: none
with task_verify omitted is refused", "a lead missing needs_approval is told true, false or
`none`" and "an orchestrator missing judgement is told the mapping or `none`".

### Deltas (14 rows, all planned)

| rule | rows | baseline → object |
|---|---|---|
| SC-02: non-mapping yield data is blocked with the object instruction | P0158 (absent), P0159 (null), P0161 (string under stop_hook_active), P0169 (string, no agent_type) | accept → reject (exit 2) |
| SC-02: P0000's unreadable duplicate-key payload still fails open under hook_guard (match on the original input); its object counterpart (an extra key) is refused | P0000 | accept → accept; counterpart reject |
| SC-07: a lead's digest.md holding prose (or a block outside today's contract) is no longer refused — the validated object is appended under it | P0137, P0162, P0166, P0178, P0181 | reject → accept (exit 0, block appended) |
| SC-07: a lead artifact that does not resolve to an existing digest.md refuses the return (was DEC-156's loud fail-open) | P0168 (no feature, no run dir), P0182 (artifact is notes.md), P0188 (t09 lead naming a fixture path with no run dir) | accept → reject (exit 2) |
| FEAT-1928 ruling: `expertise_update` entries are the closed expertise-merge op shapes; the #1855 distill fixtures' `{file, ops: 3}` entry is a summary, not an op, and no op can be derived from it without inventing its entry text | P0171 (qa distill), P0174 (code-reviewer distill) | accept → reject (exit 2) |

The five SC-02 rows are the planned deltas named in the baseline half. The eight SC-07 rows
follow from the sanctioned append (BRIEF SC-07: "an unresolvable or failed artifact write
rejects the return"; the lead writes only the human part), approved by the main session on
2026-09-29 before this run. The two ruling rows follow from the operator ruling above. Their
permanent tests ("#1855: qa/code-reviewer on a distill dispatch may PASS …") now carry a real
`{op: add, target, section, entry, why}` entry and pass, so the #1855 distill gate is still
proved.

### Syntax-only rows and their object counterparts

All ten syntax-only rows were also run as the object counterpart named above; all ten are
refused: P0000 extra key; P0025 a lead object missing `steps_run` and `cycles_used`; P0136,
P0157, P0158 absent data; P0159 null data; P0161, P0169 string data; P0194, P0195 a qa
object missing `suite`. The permanent tests keep these as object cases
(tests/integration/test-validate-digest.py: "a lead return missing steps_run and cycles_used
is refused, naming both", "a null list field is refused", the `object [hook]:` absent, null,
string, blank, list and wrapped-object rows, "stop_hook_active does not pass string data",
"F6 missing agent_type with string data is refused").

## Table

| case | source | persona | baseline result | object fixture | syntax-only counterpart | new result | match |
|---|---|---|---|---|---|---|---|
| P0000 run_canonical_reader_strictness_cases#000 | cli-group:run_canonical_reader_strictness_cases | Explore | accept (exit 0) | parity-fixtures/P0000.json | syntax-only: extra | accept (exit 0); object counterpart (extra key): reject | planned delta — SC-02: the object counterpart (an extra key) is refused; the unreadable payload itself still fails open under hook_guard |
| P0001 lead, block-style members + bare empty key | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0001.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0002 amendments: the three BUG-285 recommendations are accepted eng-lead amendments | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0002.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0003 amendments: absent is legal | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0003.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0004 amendments: empty list is legal | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0004.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0005 amendments: inline mappings for all three fields | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0005.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0006 amendments: block mapping entry | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0006.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0007 amendments: unknown key is refused naming index and key | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0007.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0008 amendments: missing key is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0008.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0009 amendments: not a list is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0009.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0010 amendments: entry that is not a mapping is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0010.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0011 amendments: SC id as task is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0011.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0012 amendments: decision id as task is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0012.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0013 amendments: field outside intent/files/verify is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0013.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0014 amendments: empty reason is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0014.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0015 amendments: reason over 240 is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0015.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0016 amendments: intent with a list value is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0016.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0017 amendments: files with a string value is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0017.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0018 amendments: files with a line-number anchor is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0018.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0019 amendments: files with a bad mapping entry is refused | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0019.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0020 amendments: second entry's fault is reported at its index | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0020.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0021 amendments: a product lead may not carry the field | cli | harness-product-lead | reject (exit 1) | parity-fixtures/P0021.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0022 amendments: a validator lead may not carry the field | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0022.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[1]) |
| P0023 lead, fully inline lists | cli | harness-validator-lead | accept (exit 0) | parity-fixtures/P0023.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[0], members[1]) |
| P0024 nested must_fix must NOT satisfy the top-level one | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0024.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0025 three fields on one line loses two | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0025.json | syntax-only: missing | reject (exit 1); object counterpart (missing steps_run, cycles_used): reject | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments) |
| P0026 doer, inline — unchanged behaviour | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0026.json |  | accept (exit 0) | yes |
| P0027 main-session (DEC-174 direct build) validates as dev | cli | main-session | accept (exit 0) | parity-fixtures/P0027.json |  | accept (exit 0) | yes |
| P0028 main-session with task_verify fail and VERDICT PASS is refused like any dev | cli | main-session | reject (exit 1) | parity-fixtures/P0028.json |  | reject (exit 1) | yes |
| P0029 drifted key spelling is caught | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0029.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons, findings[0], findings[1]) |
| P0030 enum near-miss is caught, not normalized | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0030.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons, findings[0]) |
| P0031 open_questions as a count, not a list | cli | harness-qa | reject (exit 1) | parity-fixtures/P0031.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0032 bare key followed by nothing is an empty list | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0032.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0033 inline # comments are stripped, not parsed | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0033.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0034 # inside a quoted value survives | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0034.json |  | accept (exit 0) | yes |
| P0035 no VERDICT at all | cli | harness-qa | reject (exit 1) | parity-fixtures/P0035.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0036 PASS over a failing member is rejected | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0036.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0], members[1]) |
| P0037 FAIL over an escalating member is rejected | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0037.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[0], members[1]) |
| P0038 lead may report worse than its members | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0038.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0039 a members entry with no verdict is rejected | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0039.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0040 a skipped member is explicit and excluded from worst-wins | cli | harness-product-lead | accept (exit 0) | parity-fixtures/P0040.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[0]) |
| P0041 all skipped members cannot support a lead verdict | cli | harness-product-lead | reject (exit 1) | parity-fixtures/P0041.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0042 mandatory member cannot be laundered as skipped | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0042.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[0]) |
| P0043 DIGEST: with a trailing comment is still recognized | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0043.json |  | accept (exit 0) | yes |
| P0044 block-mapping member entries spanning lines are accepted | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0044.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0], members[1]) |
| P0045 a member's nested headline does not satisfy the top-level one | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0045.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0046 an int does not satisfy a str-typed field | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0046.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0047 a bare NULLABLE scalar key must not silently become an empty list | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0047.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0048 a nested open_questions count must not trip the top-level check | cli | harness-eng-lead | accept (exit 0) | parity-fixtures/P0048.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0049 drift in a UNIVERSAL field is caught, not just schema fields | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0049.json |  | reject (exit 1) | yes |
| P0050 orchestrator digest with the reconciled schema | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0050.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0], runs[1]) |
| P0051 orchestrator briefing is NULLABLE — `none` when nothing was written | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0051.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0]) |
| P0052 rejected: reject judgement with a superseding issue is accepted | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0052.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0053 rejected: superseded_by none (should not be planned) is accepted | cli | harness-orchestrator | accept (exit 0) | parity-fixtures/P0053.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0054 rejected: no judgement mapping is refused naming it | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0054.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0]) |
| P0055 rejected: kind other than reject is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0055.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0056 rejected: superseded_by zero is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0056.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0057 rejected: superseded_by negative is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0057.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0058 rejected: superseded_by boolean is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0058.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0059 rejected: empty reason is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0059.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0060 rejected: reason over 240 characters is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0060.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0061 rejected: multiline reason is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0061.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0062 rejected: a missing key is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0062.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0063 rejected: an extra key is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0063.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0064 rejected: cycles_used must be integer zero | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0064.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0065 a judgement mapping on any other status is refused | cli | harness-orchestrator | reject (exit 1) | parity-fixtures/P0065.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (runs[0]) |
| P0066 echo shadow: valid real FAIL after a template echo still validates | cli | harness-qa | accept (exit 0) | parity-fixtures/P0066.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0067 echo shadow: missing matrix_ok in the real block is not masked by the echo | cli | harness-qa | reject (exit 1) | parity-fixtures/P0067.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0068 echo shadow: lead roll-up must read the real members, not the echo | cli | harness-eng-lead | reject (exit 1) | parity-fixtures/P0068.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0], members[1]) |
| P0069 dev refusing an under-specified task can say suite: n/a | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0069.json |  | accept (exit 0) | yes |
| P0070 suite: n/a with VERDICT PASS is a fail-open and is REJECTED | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0070.json |  | reject (exit 1) | yes |
| P0071 an analysis dev -- task: none AND files_touched: [] -- may say suite: n/a with PASS | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0071.json |  | accept (exit 0) | yes |
| P0072 task: none but files WERE touched -- suite: n/a with PASS is still REJECTED, because `task: none` is a claim and the edit is the fact | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0072.json |  | reject (exit 1) | yes |
| P0073 a REAL task whose verify passed still owes a suite result -- suite: n/a with PASS is REJECTED even with nothing touched | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0073.json |  | reject (exit 1) | yes |
| P0074 qa that cannot run the suite can say matrix_ok: n/a | cli | harness-qa | accept (exit 0) | parity-fixtures/P0074.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0075 matrix_ok: n/a with VERDICT PASS is REJECTED — the gate did not run | cli | harness-qa | reject (exit 1) | parity-fixtures/P0075.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0076 reviewer scoping out of a non-UI diff may PASS with severity_max: n/a | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0076.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y) |
| P0077 visual-designer deciding no DESIGN.md is needed may say contract: n/a | cli | harness-visual-designer | accept (exit 0) | parity-fixtures/P0077.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_prototype, why, prototype) |
| P0078 pm blocked before sizing may say surface: n/a and risk: n/a | cli | harness-pm | accept (exit 0) | parity-fixtures/P0078.json |  | accept (exit 0) | yes |
| P0079 matrix_ok: mostly is STILL rejected after n/a became legal | cli | harness-qa | reject (exit 1) | parity-fixtures/P0079.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0080 severity_max: medium is STILL rejected after n/a became legal | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0080.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0081 dev-ops suite: n/a still accepted (it had the value before DEC-173) | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0081.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (test_kinds_written) |
| P0082 dev missing task_verify under a real task is rejected | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0082.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0083 dev task_verify: fail + PASS is rejected | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0083.json |  | reject (exit 1) | yes |
| P0084 dev task_verify: n/a + PASS is rejected | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0084.json |  | reject (exit 1) | yes |
| P0085 dev-ops task_verify: fail + PASS is rejected — no carve-out on this value either | cli | harness-dev-ops | reject (exit 1) | parity-fixtures/P0085.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (test_kinds_written) |
| P0086 dev-ops task_verify: n/a + PASS is rejected — no carve-out | cli | harness-dev-ops | reject (exit 1) | parity-fixtures/P0086.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (test_kinds_written) |
| P0087 dev task_verify: n/a + BLOCKED is the honest refusal, accepted | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0087.json |  | accept (exit 0) | yes |
| P0088 dev task_verify: n/a + FAIL is accepted — the same refusal, other verdict | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0088.json |  | accept (exit 0) | yes |
| P0089 dev-ops task_verify: n/a + BLOCKED is accepted — refusal, not the carve-out | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0089.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (test_kinds_written) |
| P0090 dev-ops task_verify: n/a + FAIL is accepted | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0090.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (test_kinds_written) |
| P0091 qa carries neither new field and is still accepted | cli | harness-qa | accept (exit 0) | parity-fixtures/P0091.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0092 dev task: none with task_verify omitted is accepted — D-07's escape hatch | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0092.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0093 dev-ops task: none with task_verify omitted is accepted | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0093.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify, test_kinds_written) |
| P0094 dev task: bogus is rejected — the field is constrained | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0094.json |  | reject (exit 1) | yes |
| P0095 dev omitting task entirely is rejected — the field is required | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0095.json |  | reject (exit 1) | yes |
| P0096 dev task: none + task_verify: fail is rejected as a contradiction | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0096.json |  | reject (exit 1) | yes |
| P0097 dev task: none + task_verify: n/a is accepted — the honest DEC-121 spelling | cli | harness-backend-dev | accept (exit 0) | parity-fixtures/P0097.json |  | accept (exit 0) | yes |
| P0098 dev suite: fail + PASS is rejected — the fail-value gate | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0098.json |  | reject (exit 1) | yes |
| P0099 qa suite: fail + PASS is rejected | cli | harness-qa | reject (exit 1) | parity-fixtures/P0099.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0100 qa matrix_ok: false + PASS is rejected — the BOOLEAN half | cli | harness-qa | reject (exit 1) | parity-fixtures/P0100.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0101 dev-ops suite: fail + PASS stays accepted — D-03 ruling, not a claim it is right | cli | harness-dev-ops | accept (exit 0) | parity-fixtures/P0101.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (test_kinds_written) |
| P0102 a documentor digest carries neither new field and is still accepted | cli | harness-documentor | accept (exit 0) | parity-fixtures/P0102.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (stale_found) |
| P0103 code reviewer omission of code_grade is rejected | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0103.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons) |
| P0104 code_grade's missing-field hint names the four legal values, not the list wording | cli | harness-code-reviewer | reject (exit 1) | parity-fixtures/P0104.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons) |
| P0105 task_verify's missing-field hint names its real values, not the none wording | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0105.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0106 task's missing-field hint names a task id, not the list wording | cli | harness-backend-dev | reject (exit 1) | parity-fixtures/P0106.json |  | reject (exit 1) | yes |
| P0107 FEAT-59 finding without kind is rejected, naming the entry and the enum | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0107.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0108 FEAT-59 finding with a kind outside the enum is rejected, naming the value | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0108.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0109 FEAT-59 kind: substantive (near-miss) is rejected, not normalised | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0109.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0110 FEAT-59 a bare-string finding has no kind and is rejected | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0110.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y) |
| P0111 FEAT-59 the error names the offending entry's index, not the first | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0111.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0], findings[1]) |
| P0112 FEAT-59 kind: substance is accepted (inline entry) | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0112.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0113 FEAT-59 kind: form is accepted (block-mapping entry) | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0113.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0114 FEAT-59 kind: proportionality with scope: mission is accepted | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0114.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y) |
| P0115 DEC-228 kind: proportionality with scope: task is accepted | cli | harness-ui-reviewer | accept (exit 0) | parity-fixtures/P0115.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0116 DEC-228 kind: proportionality without scope is rejected, naming both scopes | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0116.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0117 DEC-228 kind: proportionality with a scope outside task\|mission is rejected | cli | harness-ui-reviewer | reject (exit 1) | parity-fixtures/P0117.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y, findings[0]) |
| P0118 FEAT-59 findings: [] is accepted — an explicit empty list asserts you looked | cli | harness-security-reviewer | accept (exit 0) | parity-fixtures/P0118.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (in_scope, scope_reason, threat_model) |
| P0119 FEAT-59 findings as an INT count is rejected — it is a list of kinded entries | cli | harness-security-reviewer | reject (exit 1) | parity-fixtures/P0119.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (in_scope, scope_reason, threat_model) |
| P0120 FEAT-59 lead findings passthrough: kinded entries are accepted alongside readers: | cli | harness-validator-lead | accept (exit 0) | parity-fixtures/P0120.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, members[1], findings[0], readers[0]) |
| P0121 FEAT-59 lead findings passthrough: an entry without kind is rejected | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0121.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, readers, members[1], findings[0]) |
| P0122 FEAT-59 qa PASS + matrix_ok: true + fail_first: [] is REJECTED — a green suite with no fail-first evidence is not a pass | cli | harness-qa | reject (exit 1) | parity-fixtures/P0122.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0123 FEAT-59 qa PASS with populated fail_first is accepted | cli | harness-qa | accept (exit 0) | parity-fixtures/P0123.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0124 FEAT-59 qa matrix_ok: n/a with fail_first: [] is accepted — no gate ran | cli | harness-qa | accept (exit 0) | parity-fixtures/P0124.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0125 FEAT-59 qa FAIL with fail_first: [] is accepted — the gate is on PASS | cli | harness-qa | accept (exit 0) | parity-fixtures/P0125.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0126 FEAT-59 qa omitting fail_first is rejected — every field is required | cli | harness-qa | reject (exit 1) | parity-fixtures/P0126.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0127 FEAT-59 fail_first's missing-field hint names the entry shape, not `[]` | cli | harness-qa | reject (exit 1) | parity-fixtures/P0127.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0128 FEAT-59 fail_first entry without sc is rejected, naming the index | cli | harness-qa | reject (exit 1) | parity-fixtures/P0128.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0129 FEAT-59 fail_first entry with empty evidence is rejected, naming the index | cli | harness-qa | reject (exit 1) | parity-fixtures/P0129.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0130 FEAT-59 fail_first bare-string entry is rejected | cli | harness-qa | reject (exit 1) | parity-fixtures/P0130.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0131 FEAT-59 fail_first sc must be an SC-NN id | cli | harness-qa | reject (exit 1) | parity-fixtures/P0131.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0132 FEAT-59 fail_first block-mapping entries are accepted | cli | harness-qa | accept (exit 0) | parity-fixtures/P0132.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0133 #1854: a member's nested block list stays inside that member | cli | harness-validator-lead | accept (exit 0) | parity-fixtures/P0133.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0134 #1854: a nested list does not hide a member that genuinely lacks a verdict | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0134.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0135 #1854: a nested member verdict still rolls up worst-wins | cli | harness-validator-lead | reject (exit 1) | parity-fixtures/P0135.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0136 run_empty_red_case#000 | hook-group:run_empty_red_case | harness-qa | reject (exit 2) | parity-fixtures/P0136.json | syntax-only: missing | reject (exit 2); object counterpart (missing (absent data)): reject | yes |
| P0137 run_dec156_worktree_red_case#000 | hook-group:run_dec156_worktree_red_case | harness-eng-lead | reject (exit 2) | parity-fixtures/P0137.json |  | accept (exit 0) | planned delta — SC-07: the lead's digest.md held prose (or an out-of-contract block) and the validated object is appended under it instead of refused — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0138 run_bug919_qa_matrix_cases#000 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0138.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0139 run_bug919_qa_matrix_cases#001 | hook-group:run_bug919_qa_matrix_cases | harness-qa | reject (exit 2) | parity-fixtures/P0139.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0140 run_bug919_qa_matrix_cases#002 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0140.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0141 run_bug919_qa_matrix_cases#003 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0141.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0142 run_bug919_qa_matrix_cases#004 | hook-group:run_bug919_qa_matrix_cases | harness-qa | reject (exit 2) | parity-fixtures/P0142.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0143 run_bug919_qa_matrix_cases#005 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0143.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0144 run_bug919_qa_matrix_cases#006 | hook-group:run_bug919_qa_matrix_cases | harness-qa | accept (exit 0) | parity-fixtures/P0144.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence) |
| P0145 run_bug919_qa_matrix_cases#007 | hook-group:run_bug919_qa_matrix_cases | harness-qa | reject (exit 2) | parity-fixtures/P0145.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence) |
| P0146 run_joint_hint_case#000 | cli-group:run_joint_hint_case | harness-backend-dev | reject (exit 1) | parity-fixtures/P0146.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0147 run_joint_hint_case#001 | cli-group:run_joint_hint_case | harness-backend-dev | accept (exit 0) | parity-fixtures/P0147.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0148 run_joint_hint_case#002 | cli-group:run_joint_hint_case | harness-backend-dev | accept (exit 0) | parity-fixtures/P0148.json |  | accept (exit 0) | yes |
| P0149 run_code_grade_cases#000 | cli-group:run_code_grade_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0149.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope) |
| P0150 run_code_grade_cases#001 | cli-group:run_code_grade_cases | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0150.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope) |
| P0151 run_code_grade_cases#002 | cli-group:run_code_grade_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0151.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope) |
| P0152 F1.1 quoted headline text must not satisfy the verdict lookup | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0152.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0]) |
| P0153 F1.2 multi-line inline members list is followed to its close | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0153.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[0], members[1]) |
| P0154 F1.3 unquoted apostrophe must not fuse list entries | hook | harness-validator-lead | reject (exit 2) | parity-fixtures/P0154.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, members[0], members[1], members[2]) |
| P0155 F1.4 empty members against a nonzero steps_run is rejected | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0155.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments) |
| P0156 fail-open crash: list-valued enum is a reported violation, not a crash | hook | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0156.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons, findings[0], findings[1]) |
| P0157 empty-string: a present but blank final message is the persona's violation | hook | harness-qa | reject (exit 2) | parity-fixtures/P0157.json | syntax-only: missing | reject (exit 2); object counterpart (missing (absent data)): reject | yes |
| P0158 absent-key: nothing supplied to validate is OUR gap, and is said so | hook | harness-qa | accept (exit 0) | parity-fixtures/P0158.json | syntax-only: missing | reject (exit 2); object counterpart (missing (absent data)): reject | planned delta — SC-02: absent yield data is blocked with the object instruction |
| P0159 null-passthrough: an explicitly null final message is the same our-gap branch | hook | harness-qa | accept (exit 0) | parity-fixtures/P0159.json | syntax-only: missing | reject (exit 2); object counterpart (missing (null data)): reject | planned delta — SC-02: null yield data is blocked with the object instruction |
| P0160 pass-through: non-harness agent_type is not governed | hook | Explore | accept (exit 0) | parity-fixtures/P0160.json |  | accept (exit 0) | yes |
| P0161 pass-through: stop_hook_active avoids the infinite-block loop | hook | harness-qa | accept (exit 0) | parity-fixtures/P0161.json | syntax-only: wrong-type | reject (exit 2); object counterpart (wrong-type (string data)): reject | planned delta — SC-02: string data is blocked before the stop_hook_active pass-through |
| P0162 DEC-156: narrative digest.md with no contract block is exit 2 | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0162.json |  | accept (exit 0) | planned delta — SC-07: the lead's digest.md held prose (or an out-of-contract block) and the validated object is appended under it instead of refused — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0163 DEC-156: digest.md carrying the same valid block is exit 0 | hook | harness-eng-lead | accept (exit 0) | parity-fixtures/P0163.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0164 DEC-156: missing digest in a resolved run directory is refused | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0164.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0165 DEC-156: file check governs leads only — a dev's artifact is not read | hook | harness-backend-dev | accept (exit 0) | parity-fixtures/P0165.json |  | accept (exit 0) | yes |
| P0166 dec156-worktree-narrative: worktree narrative digest is rejected | hook | harness-eng-lead | reject (exit 2) | parity-fixtures/P0166.json |  | accept (exit 0) | planned delta — SC-07: the lead's digest.md held prose (or an out-of-contract block) and the validated object is appended under it instead of refused — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0167 dec156-worktree-valid: valid worktree digest passes | hook | harness-eng-lead | accept (exit 0) | parity-fixtures/P0167.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0168 dec156-worktree-nofeature: absent feature preserves fail-open fallback | hook | harness-eng-lead | accept (exit 0) | parity-fixtures/P0168.json |  | reject (exit 2) | planned delta — SC-07: a lead artifact that does not resolve to an existing digest.md now refuses the return (was DEC-156's loud fail-open) — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0169 F6 missing agent_type key is loud, not silent | hook | None | accept (exit 0) | parity-fixtures/P0169.json | syntax-only: wrong-type | reject (exit 2); object counterpart (wrong-type (string data)): reject | planned delta — SC-02: string data is blocked even with no agent_type |
| P0170 echo shadow [hook]: missing matrix_ok behind an echo is exit 2 | hook | harness-qa | reject (exit 2) | parity-fixtures/P0170.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0171 #1855: qa on a distill dispatch may PASS with suite/matrix_ok n/a | hook | harness-qa | accept (exit 0) | parity-fixtures/P0171.json |  | reject (exit 2) | planned delta — FEAT-1928 ruling: expertise_update[0] `{file, ops}` is not one of the closed expertise-merge op shapes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0172 #1855: the same qa return outside distill is still the fail-open it always was | hook | harness-qa | reject (exit 2) | parity-fixtures/P0172.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0173 #1855: qa on a distill dispatch may not decorate the return with a suite it did not run | hook | harness-qa | reject (exit 2) | parity-fixtures/P0173.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0174 #1855: code-reviewer on a distill dispatch may PASS with code_grade n_a and no range | hook | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0174.json |  | reject (exit 2) | planned delta — FEAT-1928 ruling: expertise_update[0] `{file, ops}` is not one of the closed expertise-merge op shapes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons) |
| P0175 #1855: the same reviewer return outside distill is refused at the binding | hook | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0175.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons) |
| P0176 #1855: a distill reviewer claiming a grade is refused — there is no diff to grade | hook | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0176.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons) |
| P0177 #1855: an unknown mission changes nothing | hook | harness-qa | reject (exit 2) | parity-fixtures/P0177.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0178 run_bug1305_artifact_resolution_cases#000 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0178.json |  | accept (exit 0) | planned delta — SC-07: the lead's digest.md held prose (or an out-of-contract block) and the validated object is appended under it instead of refused — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0179 run_bug1305_artifact_resolution_cases#001 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | accept (exit 0) | parity-fixtures/P0179.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0180 run_bug1305_artifact_resolution_cases#002 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0180.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0181 run_bug1305_artifact_resolution_cases#003 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0181.json |  | accept (exit 0) | planned delta — SC-07: the lead's digest.md held prose (or an out-of-contract block) and the validated object is appended under it instead of refused — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0182 run_bug1305_artifact_resolution_cases#004 | hook-group:run_bug1305_artifact_resolution_cases | harness-eng-lead | accept (exit 0) | parity-fixtures/P0182.json |  | reject (exit 2) | planned delta — SC-07: a lead artifact that does not resolve to an existing digest.md now refuses the return (was DEC-156's loud fail-open) — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0183 run_t09#000 | hook-group:run_t09 | harness-pm | accept (exit 0) | parity-fixtures/P0183.json |  | accept (exit 0) | yes |
| P0184 run_t09#001 | hook-group:run_t09 | harness-pm | reject (exit 2) | parity-fixtures/P0184.json |  | reject (exit 2) | yes |
| P0185 run_t09#002 | hook-group:run_t09 | harness-pm | accept (exit 0) | parity-fixtures/P0185.json |  | accept (exit 0) | yes |
| P0186 run_t09#003 | hook-group:run_t09 | harness-documentor | reject (exit 2) | parity-fixtures/P0186.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (stale_found) |
| P0187 run_t09#004 | hook-group:run_t09 | harness-eng-lead | reject (exit 2) | parity-fixtures/P0187.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0188 run_t09#005 | hook-group:run_t09 | harness-eng-lead | accept (exit 0) | parity-fixtures/P0188.json |  | reject (exit 2) | planned delta — SC-07: a lead artifact that does not resolve to an existing digest.md now refuses the return (was DEC-156's loud fail-open) — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0189 run_t09#006 | hook-group:run_t09 | harness-pm | accept (exit 0) | parity-fixtures/P0189.json |  | accept (exit 0) | yes |
| P0190 run_t09#007 | hook-group:run_t09 | harness-eng-lead | accept (exit 0) | parity-fixtures/P0190.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0191 run_t09#008 | hook-group:run_t09 | harness-eng-lead | reject (exit 2) | parity-fixtures/P0191.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0192 run_t51_suspension_cases#000 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0192.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0193 run_t51_suspension_cases#001 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0193.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0194 run_t51_suspension_cases#002 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0194.json | syntax-only: missing | reject (exit 2); object counterpart (missing field (suite)): reject | yes |
| P0195 run_t51_suspension_cases#003 | hook-group:run_t51_suspension_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0195.json | syntax-only: missing | reject (exit 2); object counterpart (missing field (suite)): reject | yes |
| P0196 run_bug1898_exact_release_cases#000 | hook-group:run_bug1898_exact_release_cases | harness-ai-dev | reject (exit 2) | parity-fixtures/P0196.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0197 run_bug1898_exact_release_cases#001 | hook-group:run_bug1898_exact_release_cases | harness-ai-dev | reject (exit 2) | parity-fixtures/P0197.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0198 run_bug1898_exact_release_cases#002 | hook-group:run_bug1898_exact_release_cases | harness-backend-dev | reject (exit 2) | parity-fixtures/P0198.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0199 run_bug1898_exact_release_cases#003 | hook-group:run_bug1898_exact_release_cases | harness-backend-dev | reject (exit 2) | parity-fixtures/P0199.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0200 run_bug1898_exact_release_cases#004 | hook-group:run_bug1898_exact_release_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0200.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons) |
| P0201 run_bug1898_exact_release_cases#005 | hook-group:run_bug1898_exact_release_cases | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0201.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope, grade_2_reasons) |
| P0202 run_bug1898_exact_release_cases#006 | hook-group:run_bug1898_exact_release_cases | harness-data-engineer | reject (exit 2) | parity-fixtures/P0202.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0203 run_bug1898_exact_release_cases#007 | hook-group:run_bug1898_exact_release_cases | harness-data-engineer | reject (exit 2) | parity-fixtures/P0203.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0204 run_bug1898_exact_release_cases#008 | hook-group:run_bug1898_exact_release_cases | harness-dev-ops | reject (exit 2) | parity-fixtures/P0204.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify, test_kinds_written) |
| P0205 run_bug1898_exact_release_cases#009 | hook-group:run_bug1898_exact_release_cases | harness-dev-ops | reject (exit 2) | parity-fixtures/P0205.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify, test_kinds_written) |
| P0206 run_bug1898_exact_release_cases#010 | hook-group:run_bug1898_exact_release_cases | harness-documentor | reject (exit 2) | parity-fixtures/P0206.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (stale_found) |
| P0207 run_bug1898_exact_release_cases#011 | hook-group:run_bug1898_exact_release_cases | harness-documentor | reject (exit 2) | parity-fixtures/P0207.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (stale_found) |
| P0208 run_bug1898_exact_release_cases#012 | hook-group:run_bug1898_exact_release_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0208.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments) |
| P0209 run_bug1898_exact_release_cases#013 | hook-group:run_bug1898_exact_release_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0209.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments) |
| P0210 run_bug1898_exact_release_cases#014 | hook-group:run_bug1898_exact_release_cases | harness-frontend-dev | reject (exit 2) | parity-fixtures/P0210.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0211 run_bug1898_exact_release_cases#015 | hook-group:run_bug1898_exact_release_cases | harness-frontend-dev | reject (exit 2) | parity-fixtures/P0211.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (task_verify) |
| P0212 run_bug1898_exact_release_cases#016 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0212.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (judgement) |
| P0213 run_bug1898_exact_release_cases#017 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0213.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (judgement) |
| P0214 run_bug1898_exact_release_cases#018 | hook-group:run_bug1898_exact_release_cases | harness-pm | reject (exit 2) | parity-fixtures/P0214.json |  | reject (exit 2) | yes |
| P0215 run_bug1898_exact_release_cases#019 | hook-group:run_bug1898_exact_release_cases | harness-pm | reject (exit 2) | parity-fixtures/P0215.json |  | reject (exit 2) | yes |
| P0216 run_bug1898_exact_release_cases#020 | hook-group:run_bug1898_exact_release_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0216.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0217 run_bug1898_exact_release_cases#021 | hook-group:run_bug1898_exact_release_cases | harness-product-lead | reject (exit 2) | parity-fixtures/P0217.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0218 run_bug1898_exact_release_cases#022 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0218.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0219 run_bug1898_exact_release_cases#023 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0219.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0220 run_bug1898_exact_release_cases#024 | hook-group:run_bug1898_exact_release_cases | harness-security-reviewer | reject (exit 2) | parity-fixtures/P0220.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (in_scope, scope_reason, threat_model) |
| P0221 run_bug1898_exact_release_cases#025 | hook-group:run_bug1898_exact_release_cases | harness-security-reviewer | reject (exit 2) | parity-fixtures/P0221.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (in_scope, scope_reason, threat_model) |
| P0222 run_bug1898_exact_release_cases#026 | hook-group:run_bug1898_exact_release_cases | harness-ui-reviewer | reject (exit 2) | parity-fixtures/P0222.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y) |
| P0223 run_bug1898_exact_release_cases#027 | hook-group:run_bug1898_exact_release_cases | harness-ui-reviewer | reject (exit 2) | parity-fixtures/P0223.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (mode, in_scope, states_unspecified, contract_violations, a11y) |
| P0224 run_bug1898_exact_release_cases#028 | hook-group:run_bug1898_exact_release_cases | harness-validator-lead | reject (exit 2) | parity-fixtures/P0224.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0225 run_bug1898_exact_release_cases#029 | hook-group:run_bug1898_exact_release_cases | harness-validator-lead | reject (exit 2) | parity-fixtures/P0225.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (adequacy_notes, severity_max, matrix_ok, coverage_gaps, findings, readers) |
| P0226 run_bug1898_exact_release_cases#030 | hook-group:run_bug1898_exact_release_cases | harness-visual-designer | reject (exit 2) | parity-fixtures/P0226.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_prototype, why, prototype) |
| P0227 run_bug1898_exact_release_cases#031 | hook-group:run_bug1898_exact_release_cases | harness-visual-designer | reject (exit 2) | parity-fixtures/P0227.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_prototype, why, prototype) |
| P0228 run_bug1898_exact_release_cases#032 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0228.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0229 run_bug1898_exact_release_cases#033 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0229.json |  | reject (exit 2) | yes |
| P0230 run_bug1898_exact_release_cases#034 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0230.json |  | reject (exit 2) | yes |
| P0231 run_bug1898_exact_release_cases#035 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0231.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0]) |
| P0232 run_bug1898_exact_release_cases#036 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0232.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0]) |
| P0233 run_bug1898_exact_release_cases#037 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | accept (exit 0) | parity-fixtures/P0233.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0]) |
| P0234 run_bug1898_exact_release_cases#038 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | reject (exit 2) | parity-fixtures/P0234.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0]) |
| P0235 run_bug1898_exact_release_cases#039 | hook-group:run_bug1898_exact_release_cases | harness-orchestrator | accept (exit 0) | parity-fixtures/P0235.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (judgement, runs[0]) |
| P0236 run_bug1898_exact_release_cases#040 | hook-group:run_bug1898_exact_release_cases | harness-qa | reject (exit 2) | parity-fixtures/P0236.json |  | reject (exit 2) | yes |
| P0237 run_template_cases#000 | cli-group:run_template_cases | lead | accept (exit 0) | parity-fixtures/P0237.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0238 run_template_cases#001 | cli-group:run_template_cases | lead | accept (exit 0) | parity-fixtures/P0238.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments) |
| P0239 run_t04_unknown_key_cases#000 | cli-group:run_t04_unknown_key_cases | harness-eng-lead | reject (exit 2) | parity-fixtures/P0239.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0240 run_t04_unknown_key_cases#001 | cli-group:run_t04_unknown_key_cases | harness-eng-lead | accept (exit 0) | parity-fixtures/P0240.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments, members[1]) |
| P0241 run_t08_revision_proof#000 | cli-group:run_t08_revision_proof | harness-pm | reject (exit 2) | parity-fixtures/P0241.json |  | reject (exit 1) | yes |
| P0242 run_t08_revision_proof#001 | cli-group:run_t08_revision_proof | harness-backend-dev | reject (exit 2) | parity-fixtures/P0242.json |  | reject (exit 1) | yes |
| P0243 run_t08_revision_proof#002 | cli-group:run_t08_revision_proof | harness-documentor | reject (exit 2) | parity-fixtures/P0243.json |  | reject (exit 1) | yes — as written refused by the FEAT-1928 ruling; translated (stale_found) |
| P0244 case_matrix_floor#00 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0244.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0245 case_matrix_floor#01 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0245.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0246 case_matrix_floor#02 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0246.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (kinds, sc_evidence) |
| P0247 case_matrix_floor#03 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0247.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0248 case_matrix_floor#04 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0248.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0249 case_matrix_floor#05 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0249.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence) |
| P0250 case_human_commits#00 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0250.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0251 case_human_commits#01 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0251.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0252 case_human_commits#02 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0252.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0253 case_human_commits#03 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0253.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, human_commits_in_scope) |
| P0254 case_human_commits#04 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0254.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0255 case_human_commits#05 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0255.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0256 case_dirty_tree#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0256.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0257 case_dirty_tree#01 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0257.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0258 case_dirty_tree#02 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0258.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0259 case_dirty_tree#03 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0259.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0260 case_dirty_tree#04 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0260.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0261 case_qa_kinds#00 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0261.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0], kinds[1]) |
| P0262 case_qa_kinds#01 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0262.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0], kinds[1]) |
| P0263 case_qa_kinds#02 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0263.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0264 case_qa_kinds#03 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0264.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0265 case_qa_kinds#04 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0265.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0266 case_qa_kinds#05 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0266.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0267 case_qa_kinds#06 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0267.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0268 case_qa_kinds#07 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0268.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence, kinds[0]) |
| P0269 case_receipt#00 | shadow | harness-backend-dev | reject (exit 2) | parity-fixtures/P0269.json |  | reject (exit 2) | yes |
| P0270 case_receipt#01 | shadow | harness-backend-dev | reject (exit 2) | parity-fixtures/P0270.json |  | reject (exit 2) | yes |
| P0271 case_receipt#02 | shadow | harness-backend-dev | accept (exit 0) | parity-fixtures/P0271.json |  | accept (exit 0) | yes |
| P0272 case_receipt#03 | shadow | harness-backend-dev | accept (exit 0) | parity-fixtures/P0272.json |  | accept (exit 0) | yes |
| P0273 case_inspection_citations#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0273.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0274 case_inspection_citations#01 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0274.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0275 case_inspection_citations#02 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0275.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0276 case_findings_order#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0276.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, findings[0], findings[1]) |
| P0277 case_findings_order#01 | shadow | harness-code-reviewer | accept (exit 0) | parity-fixtures/P0277.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations, findings[0], findings[1]) |
| P0278 case_grade_2_names#00 | shadow | harness-code-reviewer | reject (exit 2) | parity-fixtures/P0278.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (spec_violations) |
| P0279 case_qa_unearned_fail#00 | shadow | harness-qa | reject (exit 2) | parity-fixtures/P0279.json |  | reject (exit 2) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence) |
| P0280 case_qa_unearned_fail#01 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0280.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence) |
| P0281 case_qa_unearned_fail#02 | shadow | harness-qa | accept (exit 0) | parity-fixtures/P0281.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_evidence) |
| P0282 S1/S2/S3 orchestrator child DIGEST | claim-lifecycle | harness-orchestrator | accept (exit 0) | parity-fixtures/P0282.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (judgement) |
| P0283 S3 nested lead LEAD_DIGEST | claim-lifecycle | harness-eng-lead | accept (exit 0) | parity-fixtures/P0283.json |  | accept (exit 0) | yes — as written refused by the FEAT-1928 ruling; translated (sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings, readers, amendments) |
| P0284 INV-15/46 BUG-440 lead digest FAIL | reader | lead | accept (exit 0) | parity-fixtures/P0284.json |  | accept (exit 0) | yes |
| P0285 INV-15/46 BUG-440 lead digest PASS | reader | lead | accept (exit 0) | parity-fixtures/P0285.json |  | accept (exit 0) | yes |
| P0286 INV-15 BUG-440 run X bare 'VERDICT: FAIL' | reader | lead | reject (exit 2) | parity-fixtures/P0286.json |  | reject (exit 2) | yes |
| P0287 INV-15 feat59 _digest_run 'VERDICT: PASS' | reader | lead | reject (exit 2) | parity-fixtures/P0287.json |  | reject (exit 2) | yes |
| P0288 INV-47 _QA_BLOCKED note | reader | lead | reject (exit 2) | parity-fixtures/P0288.json |  | reject (exit 2) | yes |
| P0289 INV-47 _QA_PASS note | reader | lead | reject (exit 2) | parity-fixtures/P0289.json |  | reject (exit 2) | yes |
| P0290 INV-47 _UI_NA note | reader | lead | reject (exit 2) | parity-fixtures/P0290.json |  | reject (exit 2) | yes |
