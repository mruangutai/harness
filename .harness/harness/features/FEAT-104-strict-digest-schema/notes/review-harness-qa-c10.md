# QA gate — FEAT-104-strict-digest-schema panel c10 @ 790023f0 (test-matrix)

**BLUF: PASS. `matrix_ok: true`.** Whole-feature floor (`logic.always=[unit]`) satisfied; `integration`
is qa-added (as at c7/c9) and satisfied. The only tracked non-feature-directory delta since the
last-passing c9 pin (`168f875f`) is `tests/integration/test-check-domain.py` (+4/-2), closing SC-08's
STEP-KEY proof gap; it ran and passed. F1/F3 stay CLOSED, F2 stays DECLINED (unchanged), Q9/CF-1/CF-3/CF-4
carried, unchanged. Nothing new.

## 0. Pin provenance (independently verified, not trusted)
- `git diff --stat 790023f0..3321bcdd` → 8 files, **all** under
  `.harness/harness/features/FEAT-104-strict-digest-schema/{STATE.md,feature.json,notes/,observations/}`.
  Claim confirmed: the worktree tip is bookkeeping-only above the pin.
- `git diff --name-only 168f875f..790023f0` → 19 files; **exactly one** outside the feature directory:
  `tests/integration/test-check-domain.py` (plus `.harness/notes/analysis-feat104-run07-review-sha-recordfix.md`,
  a harness-level note, not source/gate/config/test). Claimed +4/-2 confirmed by `git diff --numstat`.
  Diff body (verified): renames the version-2 undeclared-step-key case to
  `"schema_version 2 refuses an undeclared step key, names it and gives its route"` and adds two
  assertion clauses: `"run-state-schema.json" in strict.stderr` and `` "`evidence`" in strict.stderr ``.
- `git status --porcelain` at HEAD (`3321bcdd`) → empty. Since 790023f0..3321bcdd touches no tracked
  source/test file, running the suites at the current worktree HEAD is byte-identical to running them
  at 790023f0 for every file under test.

## 1. Change type / matrix derivation for `origin/main..790023f0` (whole feature)
Per-task `change_type` from `plan.yaml`: `logic` ×6 (T-01, T-04, T-05, T-06, T-07, T-08), `docs` ×2
(T-03, T-09), `scaffolding` ×1 (T-10). No `bugfix`/`feature`/`cross_module`/`api`/`frontend`/`ai_behavior`
task exists.
- `logic.always` = `[unit]` → **unit is the entire template floor** for this feature.
- `docs.always` = `[]`, `scaffolding.always` = `[]` → contribute nothing.
- **qa-added, beyond the floor**: `integration`. The diff rewrites `validate-digest.py`,
  `check-domain.sh`, `check-state.sh` and `run-state-schema.json` — the three gate scripts BRIEF.md's
  own "Verification gaps" section names as resting entirely on `integration` (`test_kinds` has runners
  for `unit`/`integration` only; every `verify: automated` SC above cites `evidence: integration`).
  Dropping this below the floor would leave all sixteen SCs unverified. This is the identical addition
  c7/c9 made; unchanged here.
- `functional`/`component`/`ui`/`eval`/`typecheck` → **not_applicable**: no `.ts`/`.tsx` in the diff,
  no `ai_behavior` task, no UI interaction flow, no db/external call. No `locally_run` kind's `detect`
  surface is touched.

**Resolved matrix — MEASURED this cycle** (fresh run, this session, `env -u HARNESS_AGENT_TYPE`, both
suites re-run against the current pin-identical tree — see §2):

| kind | required? | state | cmd | exit | files | provenance |
|---|---|---|---|---|---|---|
| unit | yes (template floor) | active | `run-unit-tests.sh --kind unit` | 0 | 36 | **MEASURED** |
| integration | yes (qa-added) | active | `run-unit-tests.sh --kind integration` | 0 | 70 | **MEASURED** |
| functional | no | excluded (DEC-187) | null | — | — | not_applicable |
| component | no | unresolved (cmd null) | null | — | — | not_applicable |
| ui | no | unresolved (cmd null) | null | — | — | not_applicable |
| eval | no | excluded (DEC-187) | null | — | — | not_applicable |
| typecheck | no | unresolved | null | — | — | not_applicable |

`matrix_ok: true`.

## 2. Fresh measurement (this session)
Both re-run with `env -u HARNESS_AGENT_TYPE` per instruction (avoids the known false-regression, repo
Expertise G-07).

**unit** — `bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit`
- `rc=0`, `pool: 8 workers, 36 files` → **36 = 168f875f baseline, no drop, no unexplained excess.**
- Nonzero-exit file blocks: **0**. Raw `grep -c '^FAIL '` = 4, all four inside
  `----- test-factory-claim-mutation.py (exit 0, ...) -----`, which itself ends `PASS
  test-factory-claim-mutation.py`: this is repo Expertise G-08 exactly — a deliberate mutation-proof
  printing `FAIL BUG-1290 ...` tokens for 3 reddened cases inside an overall-passing script.
  **Real failing-file count: 0.**

**integration** — `bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration`
- `rc=0`, `pool: 8 workers, 70 files, 73.21s wall` → **70 = 168f875f baseline, no drop, no excess.**
- Nonzero-exit file blocks: **0**. `grep -c '^FAIL '`: **0**.

## 3. `test-check-domain.py` per-case result at this pin
Ran inside the integration pool; block: `----- test-check-domain.py (exit 0, 1.37s) -----`,
**12/12 T-06 check-domain cases passed**, `ALL PASSED`. The renamed case, quoted verbatim from this
session's own run output:
```
ok    schema_version 2 refuses an undeclared step key, names it and gives its route
```
The other 11 cases (version-1 compatibility, evidence-key identifier/space/nested cases, all-22-keys
acceptance, and the four `schema_version` floor cases including the F1 downgrade-refusal case
`schema_version floor refuses a version-2 checkpoint downgrade`) also passed — **F1 confirmed still
CLOSED** at this pin (case present, ran, passed; not vacuous — see c9's own discrimination trace,
`review-harness-qa-c9.md:68-73`, unchanged since no source line moved).

## 4. Adequacy of the c9→c10 delta — does the suite bind the two new clauses, and can it redden?
Read (not executed against, DEC-174) `.claude/skills/harness/bin/check-domain.sh:1618-1667`:
`_schema_errors`/`_offending` are populated only inside the `if _valid_version and isinstance(doc,
dict):` block reached on the undeclared-step-key/evidence-shape path; `"run-state-schema.json"` is
emitted at :1656 and backticked `` `evidence` `` at :1657, **both inside that one block**. The only
other occurrence of the literal string `"run-state-schema.json"` in the file is in the separate
`except Exception:` branch at :1660-1667 ("run-state schema CANNOT be checked"), which fires on a
*schema-load failure*, not on the undeclared-key path this test drives — so there is no coincidental
second emitter that would let the assertion pass for the wrong reason.

The new assertions (`tests/integration/test-check-domain.py:85-89`) check `strict.returncode == 2`
AND all four substrings (`"undeclared step key"`, `"rogue_step_key"`, `"run-state-schema.json"`,
`` "`evidence`" ``) in `strict.stderr` — a conjunction, so narrowing the message to drop either new
token reddens the case (each substring is independently `and`-ed, not folded into a summary count —
repo Expertise G-12 checked and does not apply here).

**Caveat — REASONED, not mutation-executed** (DEC-174 author-nothing forbids editing
`check-domain.sh` even in a disposable worktree copy under this dispatch's constraints, and this
dispatch is explicitly gate-only/author-nothing). This is the same posture the adopted note at
`notes/qa-feat104-tip-790023f0.md:40-44` and the prior c9 reviewer (`review-harness-qa-c9.md:63-66`)
took for the parent behavior — read-the-guard-condition, not flip-and-watch. Assurance here is
**reasoned**, weaker than a mutation-proven verdict (O-03).

## 5. Provenance disclosure — measured vs. adopted
- **unit, integration (§2, §3): MEASURED** — fresh run, this session, at the current pin-identical
  worktree HEAD (`3321bcdd`, verified byte-identical to `790023f0` for every tracked source/test file
  per §0).
- **Cross-checked against ADOPTED source**: `notes/qa-feat104-tip-790023f0.md`, which records
  `git rev-parse HEAD` = `790023f0c57a3d436983d935aa0948a3d99cfdf1` at the time it was written (i.e.
  graded at this exact pin, later folded into the `3321bcdd` bookkeeping commit). Its numbers (36/70,
  both exit 0, 12/12 T-06, same renamed-case text, same emitter trace) **match this session's own
  fresh measurement exactly** — independent corroboration, not just repetition of one source (O-09
  checked: both are primitive measurements against the same pin, not one summarizing the other).
- **Whole-feature `matrix_ok` derivation (§1) and F1/F2/F3 dispositions: largely ADOPTED** from
  `review-harness-qa-c9.md` (§4-§6 there), since `validate-digest.py`, `check-domain.sh`,
  `check-state.sh`, `run-state-schema.json` and `test-validate-digest.py` are byte-unchanged between
  `168f875f` and `790023f0` (§0) — re-deriving matrix predicates or re-tracing F2's topology from
  scratch would reproduce c9's own reasoning over an unchanged tree. Spot-checked, not re-derived
  wholesale: this session independently re-ran `test-validate-digest.py` (55/55 T-01, 34/34 T-04,
  10/10 T-08, `ALL PASSED`, exit 0, within the same 70-file integration pool) and independently located
  `_t04_three_key_failures` (F3's case, `test-validate-digest.py:3130-3146`) and the F1 case
  (`test-check-domain.py`, §3) in source — both present, unchanged, passing.

## 6. Carried forward, unchanged, not re-litigated
- **F1** (schema_version downgrade refusal) — CLOSED, confirmed still passing at this pin (§3).
- **F3** (three-rogue-key single-rejection message) — CLOSED, case present and passing at this pin
  (`_t04_three_key_failures`, within 34/34 T-04, §5); disposition not reopened.
- **F2** (generic-`lead` exemption in `check-state.sh`'s at-rest sweep) — DECLINED, disposition
  STANDS per dispatch; not re-litigated. Topology (at-rest sweep vs. SubagentStop hook validating the
  true raw persona) unchanged since c9, not re-traced.
- **Q9 / F-QA-2**: REQ-08's generic-lead archive exemption has no test able to redden it — still open,
  non-gating. Carried.
- **CF-1** (security, med — `check-state.sh` INV-16 bare-string interpolation) — carried, unchanged;
  no source line in scope moved.
- **CF-3** (code, low — `abff2a84` cross-feature root commit) — carried, unchanged.
- **CF-4** (ui, low — raw `None` in the `schema_version` downgrade omitted-on-update edge) — carried,
  unchanged.
- **Q7** (duplicate strict-version predicate spellings) — carried, unchanged.

## 7. Findings
None new. All items above are carried and previously dispositioned; none gate this pin.

## Final tree state
`git status --porcelain` at session start and end: empty (worktree HEAD `3321bcdd`). Zero files
authored, edited, or touched by this dispatch besides this note.

## VERDICT

```yaml
VERDICT: PASS
DIGEST:
  headline: "matrix_ok=true at 790023f0: whole-feature floor is logic.always=[unit], satisfied; integration is qa-added and satisfied. Both suites MEASURED fresh this session (unit 36/36 files exit 0, integration 70/70 files exit 0, matching 168f875f baseline exactly) and cross-checked against the same-pin ADOPTED note notes/qa-feat104-tip-790023f0.md (numbers match exactly). The sole c9->c10 delta, test-check-domain.py's renamed undeclared-step-key case with two new stderr-substring clauses, ran and passed (12/12 T-06); its discrimination is REASONED (DEC-174 forbids mutation) via a single-emitter trace in check-domain.sh:1618-1667, not mutation-proven. F1/F3 CLOSED confirmed still passing; F2 DECLINED disposition stands, not reopened."
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: unit, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit", named_tests: 36 }
    - { kind: integration, state: satisfied, cmd: "env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration", named_tests: 70 }
    - { kind: functional, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: component, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: ui, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: eval, state: not_applicable, cmd: null, named_tests: 0 }
    - { kind: typecheck, state: not_applicable, cmd: null, named_tests: 0 }
  coverage_gaps: []
  sc_evidence:
    - { id: SC-08, test: "tests/integration/test-check-domain.py:83-90 (case: schema_version 2 refuses an undeclared step key, names it and gives its route)" }
    - { id: SC-01, test: "tests/integration/test-validate-digest.py T-04 cases (34/34), _t04_canonical_failures" }
    - { id: SC-02, test: "tests/integration/test-validate-digest.py T-01 cases (55/55), per-persona documented-contract" }
    - { id: SC-03, test: "tests/integration/test-check-domain.py (12/12 T-06 cases)" }
    - { id: SC-07, test: "tests/integration/test-validate-digest.py:3130-3146 _t04_three_key_failures" }
    - { id: SC-15, test: "tests/integration/test-check-domain.py schema_version floor cases (4 of the 12)" }
  findings:
    - { id: F1, severity: n_a, gates: false, scenario: "carried CLOSED from c9; schema_version downgrade refusal, re-confirmed passing this session, not reopened" }
    - { id: F3, severity: n_a, gates: false, scenario: "carried CLOSED from c9; three-rogue-key single-rejection message, re-confirmed present and passing this session, not reopened" }
    - { id: F2, severity: n_a, gates: false, scenario: "carried DECLINED from c9, disposition stands per dispatch; generic-lead at-rest sweep exemption, not reopened" }
    - { id: Q9, severity: med, gates: false, scenario: "REQ-08's generic-lead archive exemption at validate-digest.py has no standing test able to redden it; a future narrowing of the raw_persona != 'lead' guard could silently break lead-digest at-rest reads with nothing catching it — carried, non-gating" }
  must_fix: []
  severity_max: med
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-104-strict-digest-schema/notes/review-harness-qa-c10.md
```
