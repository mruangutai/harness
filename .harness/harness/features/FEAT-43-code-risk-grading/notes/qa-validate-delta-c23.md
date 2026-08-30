# QA — validate-delta-c23 — mutation-test the enum drift guard

**PASS.** The guard binds (2a: names the offending file, fails loud, restores clean). The guard does
not pass vacuously on a starved discovery (2b: both seams fail loud, restore clean, five suites green
at the restored pin). The ungated-lead-residual claim reproduces independently. One genuine, narrow
limitation surfaced by going one step further than the dispatch's own question demanded — reported as
a non-blocking coverage gap, not a defect in this delta.

All commands run from
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading`.
Tool caveat: `read`/`edit` served a stale cached copy of `harness-security-reviewer.md` (same symptom
the sibling code-reviewer hit on `validate-digest.py`); reported via `xd://report_issue`, worked
around with `bash`/`sed`/`cmp` for every mutation and restoration in this run.

## Baseline

`python3 .claude/skills/harness/bin/test-validate-digest.py` → `18/18 reviewer severity_max enum
checks passed.`, `ALL PASSED.`, `EXIT=0`.

## Item 2a — does the guard bind? Mutate ONE template

Reintroduced `info` into `.claude/agents/harness-security-reviewer.md:93` (`severity_max:
info|none|low|med|high|critical|n/a`, byte-backed up first with `cp`):

```
FAIL  [severity_max enum] .../.claude/agents/harness-security-reviewer.md
      | instructs ['info'] — validator REJECTS these
17/18 reviewer severity_max enum checks passed.
EXIT=1
```
The guard fails and **names the exact offending file** — a guard that only reported an aggregate
count would be strictly weaker; this one does not.

Restored via `sed` (never `git`): `cmp /tmp/harness-security-reviewer.md.orig
.claude/agents/harness-security-reviewer.md` → identical (silent = match). `git status --porcelain --
.claude/agents/harness-security-reviewer.md` → empty (file no longer shows modified). Re-run:
`18/18 reviewer severity_max enum checks passed.`, `EXIT=0`.

## Item 2b — does the guard discover anything, or can it pass vacuously?

**Discovery seam** — changed the persona-match condition in `_reviewer_template_paths`
(`test-validate-digest.py:120`) from `== "reviewer"` to `== "reviewer-nonexistent"`, starving
discovery to zero real templates while the floor (`_expected_reviewer_template_paths()`, seeded before
any discovery runs) stays at 6:

```
FAIL  [severity_max enum] expected reviewer template missing: .../.claude/agents/harness-code-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.claude/agents/harness-security-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.claude/agents/harness-ui-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.omp/agents/harness-code-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.omp/agents/harness-security-reviewer.md
FAIL  [severity_max enum] expected reviewer template missing: .../.omp/agents/harness-ui-reviewer.md
0/6 reviewer severity_max enum checks passed.
EXIT=1
```
Six named failures, not a silent `0/0` pass — this is exactly the shape the c22 send-back exists to
prevent. Restored: `cmp /tmp/test-validate-digest.py.orig .claude/skills/harness/bin/test-validate-digest.py`
→ identical, `git status --porcelain -- .claude/skills/harness/bin/test-validate-digest.py` → empty.

**Regex seam** — narrowed `_SEVERITY_LINE_RE` (line 90) to exclude `/` from the character class
(`[A-Za-z0-9_]` instead of `[A-Za-z0-9_/]`), reproducing c22's original bug so no `severity_max:
...|n/a` line matches at all:

```
FAIL  [severity_max enum] .../.claude/agents/harness-code-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.claude/agents/harness-security-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.claude/agents/harness-ui-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.omp/agents/harness-code-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.omp/agents/harness-security-reviewer.md — no severity_max line found
FAIL  [severity_max enum] .../.omp/agents/harness-ui-reviewer.md — no severity_max line found
6/12 reviewer severity_max enum checks passed.
EXIT=1
```
Restored: `cmp` identical, `git status --porcelain` on the file → empty. Guard re-run green
(`18/18`, `EXIT=0`) after both restorations.

## Is the floor a genuine derivation, or a disguised hardcoded 6? Tested from a run, not just source

Added a scratch **fourth** reviewer template, `.claude/agents/harness-perf-reviewer.md` (copy of the
security reviewer's template with `severity_max` deliberately holding the rejected `info` value),
**without** touching `ALIAS` in `validate-digest.py`. Probed `validator.norm("harness-perf-reviewer")`
directly: returns `"harness-perf-reviewer"` unchanged (not `"reviewer"`) — `ALIAS` has no entry for
it. Ran the guard with the file present:

```
18/18 reviewer severity_max enum checks passed.
EXIT=0
```
No mention of `perf-reviewer` anywhere in the output — the new file, carrying a value the validator
would reject, is **completely invisible** to `_reviewer_template_paths`, because its discovery
condition (`validator.norm(fname[:-3]) == "reviewer"`) is gated by the same `ALIAS` dict the floor's
persona tuple mirrors, not by the literal filesystem. Removed the scratch file; `git status
--porcelain -- .claude/agents/harness-perf-reviewer.md` → empty (it was untracked, `rm` alone
restores state), guard re-run green.

**Judgement:** the floor is **not** a disguised hardcoded `6` in the sense the c22 send-back was
worried about — for the three ALREADY-registered personas it is a real derivation (`SEV`/`NULLABLE`
read live from the validator module, not retyped; the missing-count and has-lines checks are
mechanical over whatever `os.listdir` returns) and the mutation tests above prove it fails loudly on
both seams for the current tree. But it is **bounded by `ALIAS`, not by the filesystem** — the
sibling code-reviewer's framing ("a real fourth reviewer persona is still discovered and checked...
mechanical") is only true **conditional on that persona also being added to `ALIAS`** in the same
change. A fourth persona added as a template file with `ALIAS` left untouched — a plausible mistake,
since routing may still half-work via the file's own front-matter while the severity-vocabulary guard
silently skips it — passes vacuously exactly as measured above. This is real, narrow, and
non-blocking for THIS delta (it changes nothing about the six templates under review), but it is a
genuine coverage gap in the guard's future robustness and belongs in `coverage_gaps`, not swept under
"mechanical."

Tree-rename equivalent (`.omp`/`.claude` `agents_dir` missing) was not separately mutated — it is the
same code path already exercised by the discovery-seam test above (`FileNotFoundError` → `continue`
→ zero paths from that tree → `_report_missing_templates` names every expected path from it), so a
renamed tree fails loudly by the same mechanism just demonstrated.

## Five focused suites, run at the FINAL restored tree

All quoted after every mutation above was restored and confirmed byte-identical:

| suite | exit |
|---|---|
| `test-validate-digest.py` | `0` (`18/18 reviewer severity_max enum checks passed.`, `ALL PASSED.`) |
| `test-code-grade.py` | `0` (`PASS test-code-grade`) |
| `test-code-grade-cli.py` | `0` (`PASS test-code-grade-cli`) |
| `test-gate-policy.py` | `0` (all `ok`) |
| `test-check-plan-routes.py` | `0` (`ALL PASS`) |

Reviewer-severity-enum check count printed by the digest suite: **18/18** (6 floor-presence + 6
has-lines + 6 drift, per the six templates × three check types).

## Ungated residual — independently measured

Re-located fresh (not trusted from the receipt/review): `.claude/agents/harness-validator-lead.md:102`
and `.omp/agents/harness-validator-lead.md:106` both still read `severity_max:
info|low|med|high|critical` — confirmed by my own `grep`, same line numbers the sibling reviewer
cited. `SCHEMAS["lead"]` (`validate-digest.py:207-209`) has no `severity_max` key.

Built my own digest at `/tmp/feat43_qa_c23/digest_lead_info.md` — full, otherwise-valid `lead` schema
(`team`, `steps_run`, `cycles_used`, `members: []`, `must_fix: []`, `branch: none`, `escalations: []`,
`sc_status: []`, plus `severity_max: info`) and ran the real validator:

```
$ python3 .claude/skills/harness/bin/validate-digest.py harness-validator-lead /tmp/feat43_qa_c23/digest_lead_info.md
digest ok
EXIT=0
```
**Independently confirms the sibling reviewer's claim — no contradiction.** Control probe: the same
digest with `severity_max: totally_bogus_value_xyz` (not even a real vocabulary word) also →
`digest ok`, `EXIT=0` — confirming the key is fully unvalidated for `lead`, not merely tolerant of
`info` specifically.

## Test-matrix judgement

**Change type: `bugfix`** (closes REQ-11's enum-drift regression; no plan task ID binds this
remediation cycle directly, so inferred per the qa-gate protocol from the diff itself — four template
edits removing a drifted vocabulary word, one new regression-guard function, one docs update).
`harness.json`'s matrix requires `unit: always` plus a `__bug_class__`-matched regression test when
one applies.

- **Bug-class-specific test: satisfied.** `run_reviewer_severity_enum_cases` in
  `test-validate-digest.py` is exactly the regression guard for this bug class (persona-template vs.
  validator enum drift) — proven discriminating by my own mutation tests above (2a and both 2b seams),
  not merely present.
- **`unit` kind: not cleanly applicable at face value, and I am not going to paper over that.**
  `test-validate-digest.py` is explicitly bucketed `INTEGRATION_SCRIPTS` in
  `.agents/skills/harness/bin/run-unit-tests.sh:31` (an explicit literal-path list that overrides the
  generic `test-*.py` glob `unit` would otherwise match, per the file's own DEC-187/kind-drift
  comments) — so the one test defending this bug class runs under `--kind integration`, not `--kind
  unit`. The delta has no separate application-logic file a `unit`-kind test would apply to (four
  markdown instruction lines and a docs file are not unit-testable code). I judge `unit` **not
  applicable** for this delta specifically, with the bug-class-specific integration test carrying the
  actual defense — not a gap, since nothing unit-shaped changed, but the matrix's literal `unit:
  always` label does not map cleanly onto where the real coverage lives, and a reader should not
  assume "unit" was satisfied by an unrelated unit-classified suite (`test-code-grade.py`,
  `test-gate-policy.py`) — I ran both, but neither exercises this bug class; their presence in the
  five-suite table is confirmation the delta broke nothing else, not matrix satisfaction for `unit`.
- `docs` kind: `SPEC.md`'s matrix entry requires nothing (`"docs": {"always": []}`) — satisfied
  trivially.

**`matrix_ok: true`** — the regression class this delta exists to close has a named, empirically
discriminating test; nothing the matrix requires for `bugfix`/`docs` is missing or misconfigured.

## Adequacy — what this delta review could NOT tell you

- Whether a **future** fourth reviewer persona will actually get checked depends on a human also
  updating `ALIAS` in `validate-digest.py` in the same change — this review demonstrates that
  dependency is real (see floor judgement above) but cannot enforce it; it is a design limitation to
  flag forward, not a defect in the six templates under review today.
- The reviewer's `low` finding (`_SEVERITY_LINE_RE` breaks on an inline comment appended to the
  `severity_max:` line itself) was read, not independently reproduced by me — cheap to add but out of
  this delta's mutation set as dispatched (regex seam already covered a different break mode).
- The canonical project-wide suite and `check-state.sh` — explicitly the orchestrator's job after this
  cycle, not run here.
- `sync-agent-adapters.py --check` and `code-grade.py --base 7ccfae8d --head 6752597` — already run
  and reported by the sibling code-reviewer this cycle; not re-run here per the dispatch's
  division of labor.

## Tree state

```
$ git status --porcelain -- .claude/agents/harness-security-reviewer.md .claude/agents/harness-ui-reviewer.md .omp/agents/harness-security-reviewer.md .omp/agents/harness-ui-reviewer.md .claude/skills/harness/bin/test-validate-digest.py .harness/harness/docs/SPEC.md .claude/agents/harness-perf-reviewer.md
(empty)
```
Full `git status --porcelain` at exit shows only the same pre-existing bookkeeping present before this
run started (`feature.json` modified by an earlier agent, plus untracked notes/observations files from
sibling agents) — no delta file, and no scratch file, was left modified or added by this run. All
scratch files live under `/tmp/feat43_qa_c23/` and `/tmp/*.orig`.

```yaml
VERDICT: PASS
DIGEST:
  headline: Guard binds (2a names the offending file, fails loud, restores clean) and does not pass vacuously when starved (2b both seams fail loud with named paths, restore clean, 5/5 suites EXIT=0 at restored pin); ungated lead residual independently reproduced (severity_max:info and even a bogus value both accepted EXIT=0); floor is a genuine derivation for the 3 registered personas but is bounded by ALIAS, not the filesystem — a 4th persona template added without an ALIAS entry is proven silently invisible (non-blocking coverage gap, not a defect in this delta)
  suite: pass
  failures: 0
  matrix_ok: true
  kinds:
    - { kind: bugfix-regression, state: satisfied, cmd: "python3 .claude/skills/harness/bin/test-validate-digest.py", named_tests: 1 }
    - { kind: unit, state: not_applicable, cmd: "n/a", named_tests: 0 }
    - { kind: docs, state: satisfied, cmd: "n/a (matrix requires nothing)", named_tests: 0 }
  coverage_gaps:
    - "A reviewer persona template added to agents/ without a matching ALIAS entry in validate-digest.py is silently invisible to run_reviewer_severity_enum_cases — demonstrated live (scratch harness-perf-reviewer.md with a rejected severity_max value produced no FAIL and no mention in output, guard stayed 18/18)"
    - "_SEVERITY_LINE_RE's brittleness to an inline comment on the severity_max: line itself (sibling reviewer's low finding) was read, not independently mutation-tested this cycle"
  sc_evidence: []
  open_questions:
    - { id: Q1, question: "Should the discovery seam additionally assert that every reviewer-shaped .md file in agents/ (by filename pattern, not just ALIAS membership) is either mapped by ALIAS to \"reviewer\" or explicitly excused, so a forgotten ALIAS registration fails loudly instead of silently? Cheap given the helpers are already generic.", blocking: false }
  files_touched: [.harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-delta-c23.md]
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-delta-c23.md
```
