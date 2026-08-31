# QA gate-only audit — FEAT-45-adversarial-plan-panel — pinned d0ebbe6

**matrix_ok: true. Suite green at full discovered counts. All 9 previously-unverified
`test-plan-panel.py` mutants now independently confirmed to redden correctly. SC-03's second
direction remains untested (pre-existing, confirmed finding). 24 wiring checks are
heavily string/structural-presence weighted: 3 genuinely execute runtime behaviour, 21 do not.**

## 1. Matrix resolution (re-derived from plan.yaml, not inherited)

Declared `change_type`s in this plan: `docs` (T-01,03,04), `config` (T-02,05,06,11), `logic`
(T-07,08,09,10,12). No task declares `cross_module`. I re-read T-06 and T-11's bodies directly
(not just the prior QA segment's table) — both are pure data/prose edits (frontmatter list
append + doc section; a one-line `SPAWNS` literal append) with zero new branching, so `config`
holds even though T-06 touches two files across `.omp/` and `.claude/`. Floor:
`logic.always=[unit]`, `config/docs.always=[]`. No kind is required beyond `unit`; `integration`
is not required by the floor but is exercised anyway because `test-check-state.py` (T-08) lives
in `INTEGRATION_SCRIPTS`.

| Kind | Required | cmd | Exit | Result |
|---|---|---|---|---|
| unit | yes | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | 0 | satisfied |
| integration | no (extra, above floor) | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | 0 | satisfied |
| functional/component/ui/eval/typecheck | no | n/a to this diff (no browser/frontend/AI-behavior change_type present) | — | not applicable / soft skip |

`matrix_ok: true`. No kind `missing` or `blocked`.

## 2. Discovery counts (re-derived, not trusted from the runner's exit code alone)

Read `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays directly out of `run-unit-tests.sh` at the
pinned tree: **29 unit + 27 integration = 56 total**, matching the claimed pre-panel baseline
exactly (no shrinkage). Cross-checked against actual run output: unit run produced 429 `PASS `
lines with `0 FAIL`; integration run produced 31 `PASS test-*.py` lines collapsing to 27 unique
scripts (4 scripts print their own internal `PASS <name>` plus the runner's final `PASS <name>`,
double-counted in the raw grep, not a discovery defect) with `0 FAIL`. Both runs `rc=0`.

## 3. Test-first / falsifiability audit — `test-check-state.py`'s INV-32 fixture (T-07/T-08)

Read `case_inv32()` directly (`test-check-state.py:2982-3047`). All nine directions the task
intent names (no-panel, high-open, high-overruled, high-resolved, ruling-unattributed,
stale-ruling, reader-missing, reader-skipped, inv32-red) are distinct boolean checks in a list,
each asserting on OUTPUT CONTENT (finding ids, literal words "reworded"/"asked again"/"never
ran"), not just exit code — satisfies P-07. They are collapsed into ONE printed `ok/FAIL` line
by design (`all(checks)`), but the `verify:` block's token sweep targets the SOURCE, not runtime
output, so this is not vacuous: a failing sub-check prints the full `checks` list for diagnosis.
The `inv32-red` mutant (lines 3017-3043) strips the marker-bracketed region into a sibling file
(never the fixture tmpdir, correctly avoiding the import-death trap), runs both real and mutant
over two fixtures, and requires `rc in (0,1)` + no traceback on the mutant — crash-vs-caught
discrimination is present. I did not re-execute this one (read only); the prior QA segment did
execute it live and it ran green in both suite invocations above. **Reading only, corroborated
by a live green run this session** — not independently re-executed by me.

## 4. Mutant re-verification — `test-plan-panel.py`'s 16 claimed mutants (T-10)

Baseline: `receipt-harness-dev-ops-T10.md` §3 claims 16 mutants, one per case-representative
check. `notes/qa-feat45-c0.md` (build-time QA) independently re-verified 7 of these:
1a, 1b, 2(scope-output resolve), 3(outputs), 4a, 8a, 8b — leaving **9 author-reported only**:
1c, 2(goalcheck), 3(playbook), 4c, 5, 6(halt), 6(loop_back), 7b, 7c.

I mutated fresh copies of `test-plan-panel.py` in `/tmp` (never the tracked file — confirmed
`git status --porcelain` clean before and after) for all 9, run with `PYTHONPATH` pointed at the
real `bin/` dir and `HARNESS_PROJECT_DIR` pointed at the real worktree so every file resolution
target stays the real doctrine tree.

**First pass on 1c falsely read as vacuous** — my initial `str.replace` hit the check's `name`
label (first `check()` arg), not the boolean expression (second arg, same literal string
appears twice on the source line), so the mutant left the assertion itself untouched and
(correctly) still passed 24/24. Re-targeted the replacement to the unique boolean-expression
occurrence; corrected mutant reddens as expected. Recording this because it is exactly the
kind of self-inflicted false-vacuity error P-09 warns about — the first result was my probe
error, not a defect in the test.

| case | mutation | result |
|---|---|---|
| 1c | SKILL.md needle swapped in the boolean expression only | RED, only (1c) |
| 2 (goalcheck) | `"harness-pm" in names` → nonexistent persona | RED, only (2) goalcheck |
| 3 (playbook) | `"c<cycle>" in skill_text` → absent token | RED, only (3) playbook |
| 4c | `_agrees(scope["persona"], m)` → bogus persona | RED, only (4c) |
| 5 | `len(omp_files) == 16` → `== 999` | RED, only (5) omp count |
| 6 (halt) | inverted `not in` → `in` | RED, only (6) halt |
| 6 (loop_back) | `"escalate"` → bogus value | RED, both loop_back steps (documented as shared line, not a false positive — matches receipt's own note) |
| 7b | `"plan-panel" in slice_text` → absent token | RED, only (7b) |
| 7c | `"simplify" in slice_text` → absent token | RED, only (7c) |

All 9: exit code non-zero, `FAIL` lines named exactly the targeted check(s), no traceback, no
other check affected. **All 9 of the 9 previously-unverified mutants independently confirmed
this session** (measured, not reasoned) — combined with the prior 7, **16/16 of the claimed
mutants for `test-plan-panel.py` are now independently verified**, none vacuous, none crashed.

## 5. SC-03's second direction — confirmed still unbound

Read BRIEF.md's SC-03 verbatim: *"Every panel step and playbook-named artifact that can re-run
resolves `{{cycle}}` in its output path (DEC-117), **and the run-scoped record of a superseded
run survives the re-run**. Falsified by one re-runnable writer with a cycle-free path, **or by a
second run overwriting the first's record**."* Two independent falsification directions.

Read `test-plan-panel.py`'s only SC-03-tagged check (`(3) ... loop_back outputs are empty or
carry the literal {{cycle}}`, lines 161-181): it is a static string-presence check over the
declared `outputs:` templates and `SKILL.md` prose (`"c<cycle>" in skill_text`). Nothing in the
file simulates two consecutive panel cycles writing real files and asserts the first survives
the second. **A real behavioural test would have to**: run (or fake) cycle 0's write to its
resolved path, run cycle 1's write to *its* resolved path, and assert cycle 0's file still
exists unmodified afterward — proving distinct cycle numbers actually prevent overwrite, not
just that the token is textually present. This is the same gap the prior QA segment logged;
confirmed still open at the pinned SHA, not narrowed by anything in this diff.

## 6. Executable-behaviour vs. string-presence ratio across the 24 wiring checks

Read every check in `test-plan-panel.py` (lines 108-292) and classified by what it actually
exercises:

- **Genuinely executes runtime behaviour (3 of 24):** the two `(2) ... resolves to persona ...`
  checks (scope output + goalcheck path) each shell out to the real `check-domain.sh --resolve`
  and assert on its actual stdout/rc; `(8b)` `importlib`-loads the real
  `sync-agent-adapters.py` module and inspects its live `SPAWNS` dict — the structure the sync
  tooling itself consumes at bootstrap time.
- **String/structural presence only (21 of 24):** `(1a)`, `(1b)`, `(1c)` — literal needle in a
  YAML field or markdown prose; `(2)` should-not-exist's trivial empty-outputs pass; `(3)` ×2
  loop_back + `(3)` playbook — `{{cycle}}`/`c<cycle>` token presence; `(4a)` persona absent from
  a directory listing; `(4b)` empty-list check; `(4c)`/`(4d)` persona-in-set membership read
  from `team-config.yaml`; `(5)` ×3 — directory-listing counts and set equality; `(6)` `then:
  halt` absence + `(6)` ×2 field-presence; `(7a)` regex-slice presence, `(7b)`/`(7c)` — needle
  presence in the sliced text; `(8a)` — persona-in-list membership parsed from frontmatter YAML.

**Adequacy claim: 3/24 (12.5%) bind live executable behaviour; 21/24 (87.5%) assert presence or
absence of a token/entry in static markdown, YAML, or a directory listing.** This is consistent
with the file's own stated scope (its docstring: "asserts nothing about finding quality" — it
grades wiring, not runtime panel behaviour) and is not itself a defect, but the ratio is the
adequacy fact the dispatch asked for: most of these 24 "wiring checks" would not catch a defect
in *how* the panel behaves at runtime, only in whether the doctrine files that wire it together
still say the right things.

## 7. DEC-206 compensating control — presence check

DEC-206's SIGNED trade needs its named compensating control shipped. Grepped both
`.omp/agents/harness-validator-lead.md` and `.claude/agents/harness-validator-lead.md` at the
pinned SHA directly (`git show d0ebbe6:<path>`) for all five tokens T-06's own `verify:` block
checks (`unrated`, `plan-panel`, `never CONTENT`, `findings`, `status skipped`): **present in
both files.** Confirms the compensating control DEC-206 names is shipped in both the canonical
and generated agent definitions, not just in one.

## Findings

| # | Severity | File:line | Finding | Failure scenario |
|---|---|---|---|---|
| F1 | med | `.claude/skills/harness/bin/test-plan-panel.py:161-181` | SC-03's second falsification direction ("a second run overwriting the first's record") has no test; only a `{{cycle}}` token-presence proxy exists. | If a future refactor changes how `{{cycle}}` resolves (e.g., a template bug that renders the same literal string for two different cycle numbers), every check in this file stays green because none of them ever run two cycles and diff the filesystem — the operator would only discover the collision live, the first time a panel actually re-runs and silently clobbers cycle 0's review record. |
| F2 | info | `.claude/skills/harness/bin/test-plan-panel.py` (whole file) | 21 of 24 wiring checks assert string/structural presence in static doctrine files rather than exercising runtime panel behaviour (3/24 do). | Not a defect by itself — matches the file's declared scope — but a reviewer citing "24/24 wiring checks pass" as strong assurance of correct panel *behaviour* would be overstating what most of these checks can catch; a doctrine file that says the right words but is wired to the wrong step would pass most of these 21 unchanged. |

No `high`/`critical` findings — this is a gate-only audit and every measured signal (matrix
resolution, discovery counts, suite green, all 16 `test-plan-panel.py` mutants, DEC-206 control
presence) came back clean and reproducible.
