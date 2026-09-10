reviewed: origin/main..790023f0 (worktree tip 3321bcdd is one bookkeeping commit above the pin,
verified in-scope-only below; NOT reviewed as code)

# Verdict: PASS

Stage 1 (spec compliance) passes; Stage 2 (quality) found nothing gating. This is a re-review of a
single narrow delta over an otherwise byte-identical diff to the c9-reviewed pin: c9's Stage 1/Stage
2 findings are re-affirmed by direct git comparison (not accepted on the prior panel's word), and the
new test clauses in `tests/integration/test-check-domain.py` are independently exercised.

## Measured deltas (own verification, not the dispatch's word)

- `git diff --stat origin/main..790023f0`: 75 files, +10697/-31 — matches dispatch scope.
- `git diff --stat 168f875f..790023f0`: **19 files**, but only **one** outside the feature's own
  `notes/`/`observations/`/`STATE.md`/`feature.json` tree: `tests/integration/test-check-domain.py`.
  `git diff --numstat` on that path alone: **+4/-2**, exactly the claimed delta (case-name string
  plus two new `and` clauses in `_undeclared_cases()`). Confirmed byte-identical (zero diff) for
  `check-domain.sh`, `check-state.sh`, `validate-digest.py`, `run-state-schema.json`, and
  `tests/integration/test-validate-digest.py` between the two pins. **Claim CONFIRMED.**
- `git diff --stat 790023f0..3321bcdd`: **8 files**, all under
  `.harness/harness/features/FEAT-104-strict-digest-schema/` (`STATE.md`, `feature.json`, four
  `notes/receipt-*-simplify-sc08.md`, `notes/qa-feat104-tip-790023f0.md`,
  `observations/harness-orchestrator.md`). No source, gate, skill, agent, or DECISIONS file touched.
  **Claim CONFIRMED** — 3321bcdd is out of code-review scope by its own content, not just by policy.

## Q1 — Does the delta close SC-08 for the STEP-KEY seam?

BRIEF SC-08 (`BRIEF.md:92-95`): "names the declaration route by file and symbol —
`validate-digest.py` `SCHEMAS`/`PASSTHROUGH` for a digest key, the step-schema symbol for a step
key — asserted as a substring."

**Digest seam** (`tests/integration/test-validate-digest.py:3130-3145`,
`_t04_three_key_failures`): calls `validator.validate("harness-eng-lead", digest)` **in-process**
(a real function call on the live module, not a fixture-argued claim) and asserts the returned
message contains `"validate-digest.py"`, `"PASSTHROUGH"`, `"DOCUMENTED_OPTIONAL"`, `"SCHEMAS"` — four
distinct literal Python identifiers plus the file. **Grade: EXECUTABLE, and strong** — three named
source symbols, not one.

**Step seam** (`tests/integration/test-check-domain.py:79-89`, `_undeclared_cases`, this cycle's
delta): calls `_fire_new(...)` → `check_domain_support.fire()` → `subprocess.run([check-domain.sh,
...])`, a **real subprocess execution** of the actual hook against a real payload, and asserts
`strict.stderr` contains `"undeclared step key"`, `"rogue_step_key"`, `"run-state-schema.json"`, and
backticked `` "`evidence`" ``. **Grade: EXECUTABLE** — genuinely runs the shell script and inspects
real captured stderr, not a mock.

**Does `run-state-schema.json` (a file path) satisfy "by file and symbol" for the step seam?**
Read literally against the digest seam's bar (three *Python* symbol identifiers), no — JSON Schema
has no equivalent named construct to `SCHEMAS`/`PASSTHROUGH` at the location a new step key would be
declared (`properties.steps.items.properties`); the message names only the *file*, never a JSON
pointer or schema-node name for that location. Backticked `` `evidence` `` is a real property name in
`run-state-schema.json` (verified: `run-state-schema.json:36`, `"evidence": {...}`), and functions
as the message's one concrete "symbol" — but it is the *escape-hatch container's* name, not the
declaration location for a plain undeclared key like `rogue_step_key` used in the test itself. **This
is a materially weaker "file and symbol" citation than the digest seam's three-identifier version.**
However: `plan.yaml:454-462` (task T-06 intent) **explicitly decides** this exact route text —
"a recovery field is declared in run-state-schema.json, a per-dispatch fact goes under evidence" —
as the intended fulfillment of SC-08 for this seam, and the shipped message (`check-domain.sh:1653-
1659`) matches that decided text verbatim in substance. Since Stage 1 asks whether the code matches
what the plan *decided*, not an idealized re-reading of the BRIEF's abstract phrase, **this closes
SC-08 for the step seam as the plan defined it** — but the plan's own definition is a narrower
reading of "symbol" than the parallel digest-seam implementation delivers. Not a Stage-1 violation
(nothing here contradicts a decided value); flagged as an info-level asymmetry, not a finding,
because reopening the interpretation itself would relitigate a plan-signing decision this diff did
not touch (the message text and the schema were already byte-identical at c9; only the *test* changed
this cycle).

## Q2 — Can the new assertion set pass on an unrelated message branch?

Read `check-domain.sh:1615-1667` directly at the pin (`git show 790023f0:...`). Two producers can
mention `run-state-schema.json` under `_valid_version and isinstance(doc, dict)`:

1. **Intended** (`:1645-1659`, inside `if _schema_errors:`): head `_head("undeclared step key or
   evidence shape.")`, then `"offending key(s): {_names}. ... in ... run-state-schema.json; a
   per-dispatch fact goes under \`evidence\` ..."`.
2. **Fallback** (`:1660-1667`, `except Exception as _schema_exc:`): head `_head("run-state schema
   CANNOT be checked; the write is denied.")`, then `".claude/skills/harness/bin/run-state-schema.json
   or its jsonschema validator failed: %s: %s"`.

Branch 2 **does** contain the substring `"run-state-schema.json"` (checked: yes, in its own body
line). It does **not** contain `"undeclared step key"` (grepped the whole file: that exact phrase
occurs at exactly one site, `check-domain.sh:1653`) or the literal offending key name `rogue_step_key`
(branch 2 never enumerates `_offending`, since `_schema_errors`/`_offending` are never populated on
that path) or backticked `` `evidence` `` (branch 2's body never mentions evidence at all).

**The discriminating clause is `"undeclared step key" in strict.stderr`, already present before this
cycle's delta** — it alone rules out branch 2 and every `sys.exit(2)` site elsewhere in the file
(none of which print that phrase; confirmed by the single-hit grep). The two **new** clauses this
cycle added (`"run-state-schema.json"`, backtick `` `evidence` ``) add no *additional* branch-
discrimination power over what `"undeclared step key"` + `"rogue_step_key"` already provided — they
are automatically true whenever the intended branch fires, since both substrings sit in the same
`out.append` two lines later. Their purpose is closing the SC-08 proof gap (Q1), not tightening
branch uniqueness, which was already sound. **Conclusion: the four-clause conjunction plus
`returncode == 2` is uniquely pinned to the intended producer** in the current source; no other
present branch satisfies it, and no plausible near-future branch would either without also adopting
the literal phrase `"undeclared step key"`.

## Q3 — Is the assertion strong enough to redden?

DEC-174 forbids mutating the tracked file to prove this, and this reviewer's own role is read-only
over Bash (a prior attempt to write a disposable `/tmp` copy via shell redirect was blocked by
`bash-write-guard`, confirming the read-only grant extends to scratch files, not only tracked ones).
**This section is REASONED from the source, not mutation-executed.**

- **(a) Regression drops the route from the message entirely** (keeps `"undeclared step key"` and
  `rogue_step_key`, removes the `run-state-schema.json`/`evidence` sentence): **REDDENS.** Both new
  `in strict.stderr` clauses become false; `_report` marks the case FAIL and `run_t06_cases` returns
  a nonzero failure count.
- **(b) Regression splits the route across two separate print statements** (still both substrings
  present somewhere in the captured stderr, just not adjacent/co-located): **DOES NOT REDDEN.** Each
  `X in strict.stderr` clause is a whole-buffer substring membership test, not a check that the route
  text sits in the *same* message as the offending-key line. As long as `"run-state-schema.json"` and
  `` `evidence` `` appear *anywhere* in the accumulated stderr for this one write, the case passes.
  This is a real weakness, but it is not new to this delta — every clause in every case in this file
  (`"schema_version floor"`, `"schema_version downgrade"`, etc.) uses the identical substring-anywhere
  style, so this is the established test-writing convention here, not a regression this cycle
  introduced. Not gating; noted as a residual limitation shared by the whole suite.
- **(c) Regression emits the bare word `evidence` without backticks**: **REDDENS.** The clause is
  `"`evidence`" in strict.stderr` with literal backtick characters in the Python string; dropping the
  backticks in the shipped message removes that exact substring, and `run_t06_cases` fails.

## F1 / F3 / F2 dispositions

- **F1** (schema_version downgrade refusal, `_version_decreased` at `check-domain.sh:1766-1775`):
  byte-identical to c9 (confirmed via the zero-diff check above). **Still CLOSED.**
- **F3** (undeclared-key rejection naming `validate-digest.py`/`PASSTHROUGH`/`DOCUMENTED_OPTIONAL`/
  `SCHEMAS`, three-rogue-key case at `test-validate-digest.py:3130-3145`): byte-identical to c9.
  **Still CLOSED.**
- **F2** (`check-state.sh:1590`, `_vd_mod.validate("lead", _dtext)` in the at-rest sweep — the
  generic-persona archive-reader exemption): `check-state.sh` is byte-identical to c9; topology
  confirmed unchanged (`validate("lead", ...)` still the literal call, `_host` still unused for this
  purpose). **DECLINED disposition stands, not reopened.** Its residual (no test would catch a future
  edit substituting `_host` for the literal `"lead"`) is carried forward as CF/Q, not re-raised new.

## Carried-forward, non-gating (not re-raised)

- CF-1 (security, med — `check-state.sh` INV-16 bare-string interpolation) — carried, unchanged
  (file byte-identical to c9).
- CF-3 (code, low — `abff2a84` FEAT-56 cross-feature root commit riding this branch) — carried,
  unchanged; still present in `origin/main..790023f0` per c9's own analysis, no new commit removes it.
- CF-4 (ui, low — raw Python `None` in the downgrade-omitted-on-update edge) — carried, unchanged.
- Q7 (duplicate strict-version predicate spellings) — carried, unchanged.

## Additional Stage-2 observation (info, non-gating)

No test exists asserting the step-key seam names **multiple** offending keys "at once" in one
message (the digest seam has this at SC-07/`_t04_three_key_failures`; `plan.yaml:460` states the same
intent for steps — "names every offending key at once" — but `_undeclared_cases`/`_evidence_cases`
only ever exercise one offending key per fixture). The underlying mechanism (`_offending` is a set,
joined via `", ".join`) already supports it; this is a coverage gap, not a code defect, and predates
this cycle's delta (not introduced or worsened here).

## Code grade

`python3 .claude/skills/harness/bin/code-grade.py --base "$(git merge-base origin/main 790023f0)"
--head 790023f0` (merge-base = `78e34f06`, matching origin/main's tip — same canonical range c9
used). Result: **42 graded functions, 0 FAIL, 0 grade-2, 0 grade-1** — every one PASS against its bar
(test-code bar 3). `_undeclared_cases` itself (the delta's own function): cyclomatic 5, cognitive 1,
ABC 11.4, **grade 4**, PASS. `code_grade: pass`.

## Findings

| id | severity | gates | scenario |
|---|---|---|---|
| F-104C10-01 | info | no | The four-clause step-seam conjunction is a whole-buffer substring test, not a single-message cohesion check — a regression that split the route text and the offending-key line across two separate stderr writes for the same violation would still pass. Shared by the whole file's testing convention; not new this cycle. |
| F-104C10-02 | info | no | The step-key seam's "symbol" is a file path plus one JSON property name (`evidence`), materially thinner than the digest seam's three named Python identifiers (`SCHEMAS`/`PASSTHROUGH`/`DOCUMENTED_OPTIONAL`) for the same BRIEF clause — closes SC-08 only under the plan's own narrower decided definition (`plan.yaml:460-462`), not under a literal re-reading of "symbol". Not a violation of a decided value; worth a plan-language note if a future feature reuses this pattern. |

`severity_max: low` (carried from CF-1/CF-3; nothing new above `info`). `must_fix: []`.
