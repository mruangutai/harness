# Receipt — harness-backend-dev — validate-enumfix-c22 — enum-drift-guard

**BLUF:** `severity_max` enum drift (REQ-11) closed in all four affected templates, and a
new mechanically-discovered guard (`run_reviewer_severity_enum_cases` in
`test-validate-digest.py`) now catches this class permanently — proven failing on the
pre-fix tree (naming all four offending files/values) and passing after the fix. No
edit made to `harness-validator-lead.md:102` per the eng-lead's scope ruling — measured,
not touched.

## 1. Guard: observed FAILING pre-fix, then PASSING post-fix

Guard lives in `.claude/skills/harness/bin/test-validate-digest.py`, alongside
`run_template_cases()`/`TEMPLATES` (its home, per ruling). It discovers reviewer
templates mechanically via the validator's own `norm()`/`ALIAS` (not a hardcoded file
list), and derives the expected vocabulary from the validator's own `SEV`/`NULLABLE`
(not a retyped literal).

Pre-fix output (captured before any template edit):
```
ok    [severity_max enum] .../.claude/agents/harness-code-reviewer.md
FAIL  [severity_max enum] .../.claude/agents/harness-security-reviewer.md
      | instructs ['info'] — validator REJECTS these
      | validator accepts ['none'] — template never offers these
FAIL  [severity_max enum] .../.claude/agents/harness-ui-reviewer.md
      | instructs ['info'] — validator REJECTS these
      | validator accepts ['none'] — template never offers these
ok    [severity_max enum] .../.omp/agents/harness-code-reviewer.md
FAIL  [severity_max enum] .../.omp/agents/harness-security-reviewer.md
      | instructs ['info'] — validator REJECTS these
      | validator accepts ['none'] — template never offers these
FAIL  [severity_max enum] .../.omp/agents/harness-ui-reviewer.md
      | instructs ['info'] — validator REJECTS these
      | validator accepts ['none'] — template never offers these

2/6 reviewer severity_max enum checks passed.
RESULT 4
```
(An initial regex bug — the char class excluded `/`, so `n/a` never matched — was
caught and fixed by this same run: it reported 0 checked, which is not a truthful
"failing" run, so it was fixed before use.)

Post-fix: `RESULT 0`, `6/6 reviewer severity_max enum checks passed.`

## 2. Templates corrected — byte-match `SEV`

```
$ grep -n 'severity_max' .claude/agents/harness-*-reviewer.md .omp/agents/harness-*-reviewer.md
.claude/agents/harness-code-reviewer.md:84:     severity_max: none|low|med|high|critical|n/a
.claude/agents/harness-security-reviewer.md:93: severity_max: none|low|med|high|critical|n/a
.claude/agents/harness-ui-reviewer.md:103:      severity_max: none|low|med|high|critical|n/a
.omp/agents/harness-code-reviewer.md:84:        severity_max: none|low|med|high|critical|n/a
.omp/agents/harness-security-reviewer.md:93:    severity_max: none|low|med|high|critical|n/a
.omp/agents/harness-ui-reviewer.md:103:         severity_max: none|low|med|high|critical|n/a
```
Only the enum line changed in each of the four files; surrounding `# n/a = scoped OUT …`
comments and everything else untouched.

## 3. Both directions, real validator, exit statuses

`harness-security-reviewer` digest with `severity_max: info` (old template value):
```
VERDICT: BLOCKED (contract violation)
  - severity_max='info' is not in ['critical', 'high', 'low', 'med', 'none'].
EXIT=1
```
Same digest with `severity_max: none` (corrected template value):
```
digest ok
EXIT=0
```

## 4. `harness-validator-lead.md:102` — measured, NOT edited

Fed a full, otherwise-valid `harness-validator-lead` digest (schema `lead`, no
`severity_max` key in `SCHEMAS["lead"]`) carrying `severity_max: info`:
```
digest ok
EXIT=0
```
Confirms the ruling: unknown keys are ignored by `SCHEMAS["lead"]`, so this line's
spelling drift is cosmetic guidance drift, not a shipping validator defect. No edit
made to that file, per instruction.

## 5. `.harness/harness/docs/SPEC.md:1142` — left as found

Already modified in the working tree (documentor's approved in-domain fix). Not
touched, not reverted, not duplicated by me.

## 6. Suites and adapter sync

- `sync-agent-adapters.py --check` → EXIT=0 (`.claude`/`.omp` in step)
- `test-code-grade.py` → `PASS test-code-grade`, EXIT=0
- `test-code-grade-cli.py` → `PASS test-code-grade-cli`, EXIT=0
- `test-gate-policy.py` → all `ok`, EXIT=0
- `test-check-plan-routes.py` → `ALL PASS`, EXIT=0
- `test-validate-digest.py` → `ALL PASSED.`, EXIT=0 (this is where the new guard landed)

## 7. `code-grade.py` on every changed file

- `test-validate-digest.py` (only Python touched): the guard was split into 5 small
  helpers (`_reviewer_severity_expected`, `_reviewer_template_paths`,
  `_severity_line_values`, `_report_severity_drift`, `run_reviewer_severity_enum_cases`)
  after the first draft graded 1/5 (cognitive 38, bar 3, high severity). Post-split
  grades: 5, 3, 5, 4, 4 — all `RESULT: PASS`, bar 3. No qualname graded 2 or below.
  CR-01 stays closed.
- The four `.md` template files: `code-grade.py` is a Python-AST tool and reports
  `PARSE ERROR … UNGRADED` on markdown — expected, nothing Python to grade there.

## 8. Tree state

`git rev-parse HEAD` → `a0ff125caeb571e49a3bff86c3802cab9b596127` (unmoved).
`git status --porcelain` shows only the six tracked-file edits above (plus files from
other agents' prior runs, not mine) — no scratch files added by this run, nothing
committed.

## Open item

None outstanding from this task's scope. `harness-validator-lead.md:102` spelling
drift remains as measured — cosmetic, ungated, ruled not to be touched.

---

# Cycle 2 — send-back: close the guard's zero-coverage fail-open

**BLUF:** `run_reviewer_severity_enum_cases()` used to read `checked == 0` as a pass — the exact
state this cycle's own regex bug produced in cycle 1, caught only because that run was deliberately
watched for a FAIL. Fixed: `checked` now starts at a floor (the 3 reviewer personas × 2 trees = 6
expected templates) so it can never reach zero, and both live discovery seams — the regex missing a
template's line, and `_reviewer_template_paths` finding fewer templates than expected — are asserted
explicitly and FAIL loudly, naming the offending file. Both seams demonstrated broken and restored
below. Templates and CR-01's helper split are untouched, confirmed by grep and `code-grade.py`.

## 1. Only lines 103-226 changed

`_SEVERITY_LINE_RE` (line 90) and `_reviewer_severity_expected` (93-100) are byte-identical to
cycle 1. Changed/added: `_reviewer_template_paths` (now catches a missing `agents_dir` via
`FileNotFoundError` instead of raising — deliberate: it now contributes empty discovery, which the
new floor check below turns into a loud, named failure rather than an uncaught crash),
`_expected_reviewer_template_paths` + `_EXPECTED_REVIEWER_PERSONAS` (new — the floor, derived from
the 3 shipped personas × 2 trees, not a bare `6`), `_report_missing_templates` (new — FAILs, naming
the path, for every expected template discovery didn't find), `_report_template_has_lines` (new —
FAILs, naming the path, if a discovered template yielded zero `severity_max` lines),
`_severity_line_values`/`_report_severity_drift` unchanged, `run_reviewer_severity_enum_cases`
rewritten to wire all of the above and seed `checked` from the floor so it is never 0.

## 2. Both discovery seams demonstrated broken, FAIL loudly, then restored

**a. Regex seam** — narrowed `_SEVERITY_LINE_RE`'s char class to exclude `/` (cycle 1's actual bug,
which never matches `n/a`):
```
FAIL  [severity_max enum] .../.claude/agents/harness-code-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.claude/agents/harness-security-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.claude/agents/harness-ui-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.omp/agents/harness-code-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.omp/agents/harness-security-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.omp/agents/harness-ui-reviewer.md — no severity_max line found

6/12 reviewer severity_max enum checks passed.
RESULT 6
```
Before this fix, the same bug produced `no reviewer severity_max template lines found.` / `RESULT 0`
— a pass. Restored `_SEVERITY_LINE_RE` to the correct char class (including `/`) immediately after
capturing this output; the file diffed byte-identical to before the demonstration on that line.

**b. Discovery seam** — changed the persona-match condition in `_reviewer_template_paths` from
`== "reviewer"` to `== "reviewer-nonexistent"` so it resolves nothing:
```
FAIL  [severity_max enum] expected reviewer template missing: .../.claude/agents/harness-code-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.claude/agents/harness-security-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.claude/agents/harness-ui-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.omp/agents/harness-code-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.omp/agents/harness-security-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.omp/agents/harness-ui-reviewer.md

0/6 reviewer severity_max enum checks passed.
RESULT 6
```
Restored the persona-match line to `== "reviewer"` immediately after capturing this output; the file
diffed byte-identical to before the demonstration on that line.

Both restorations done with `edit`, never `git restore`/`git checkout --`.

## 3. Guard passes on the corrected tree

`test-validate-digest.py` → `18/18 reviewer severity_max enum checks passed.` (6 floor-presence + 6
has-lines + 6 drift), `ALL PASSED.`, `EXIT=0`.

## 4. Templates untouched — byte-match cycle 1

```
$ grep -n 'severity_max' .claude/agents/harness-*-reviewer.md .omp/agents/harness-*-reviewer.md
.claude/agents/harness-code-reviewer.md:84: severity_max: none|low|med|high|critical|n/a
.claude/agents/harness-security-reviewer.md:93: severity_max: none|low|med|high|critical|n/a
.claude/agents/harness-ui-reviewer.md:103: severity_max: none|low|med|high|critical|n/a
.omp/agents/harness-code-reviewer.md:84: severity_max: none|low|med|high|critical|n/a
.omp/agents/harness-security-reviewer.md:93: severity_max: none|low|med|high|critical|n/a
.omp/agents/harness-ui-reviewer.md:103: severity_max: none|low|med|high|critical|n/a
```
(Also matched, unrelated prose lines `severity_max >= high` in all six files — not instructed-line
syntax, not matched by `_SEVERITY_LINE_RE`, unmodified since cycle 1.)

## 5. Adapter sync and the five focused suites

- `sync-agent-adapters.py --check` → EXIT=0
- `test-code-grade.py` → `PASS test-code-grade`, EXIT=0
- `test-code-grade-cli.py` → `PASS test-code-grade-cli`, EXIT=0
- `test-gate-policy.py` → all `ok`, EXIT=0
- `test-check-plan-routes.py` → `ALL PASS`, EXIT=0
- `test-validate-digest.py` → `ALL PASSED.`, EXIT=0

## 6. `code-grade.py` on every added/changed qualname

```
_reviewer_template_paths            GRADE 3  (cyclomatic 6, cognitive 12, abc 10.8)  PASS
_expected_reviewer_template_paths   GRADE 5  (cyclomatic 3, cognitive 0,  abc 2.2)   PASS
_report_missing_templates           GRADE 5  (cyclomatic 3, cognitive 3,  abc 4.7)   PASS
_severity_line_values               GRADE 5  (cyclomatic 3, cognitive 0,  abc 7.7)   PASS  [unchanged]
_report_template_has_lines          GRADE 5  (cyclomatic 2, cognitive 1,  abc 1.4)   PASS
_report_severity_drift              GRADE 4  (cyclomatic 5, cognitive 5,  abc 8.1)   PASS  [unchanged]
run_reviewer_severity_enum_cases    GRADE 3  (cyclomatic 4, cognitive 3,  abc 21.5)  PASS
```
All at or above bar 3; none graded 2 or below. CR-01 stays closed. (Other `FAIL`/lower-grade
qualnames reported by `code-grade.py` on this large file belong to unrelated pre-existing test
functions, not touched this cycle.)

## 7. Tree state

`git rev-parse HEAD` → `a0ff125caeb571e49a3bff86c3802cab9b596127` (unmoved, matches cycle 1).
`git status --porcelain`: same six tracked-file edits as cycle 1 (only `test-validate-digest.py` is
mine), plus untracked notes/observations files from other agents' runs in this multi-agent session —
no scratch files added by this cycle, nothing committed.

## Open item

None outstanding. `harness-validator-lead.md:102` spelling drift remains as measured in cycle 1 —
cosmetic, ungated, still not touched.
