# Receipt — documentor — validate-goalcheck-c21-product

**BLUF: the vocabulary check found 4 contradictions in shipped prose, and one defect worse than a doc
nit — this feature's human commit `45328d7` changed the reviewer severity enum from `info` to `none`
and propagated it to the code-reviewer only, so the security- and ui-reviewer agent templates now
instruct a value the validator hard-rejects.** A reviewer copying its own template returns
`BLOCKED (contract violation)`, and `info` is the single most common `severity_max` in the historical
record (FEAT-06/10/11/13/16/20 all returned it). I fixed the one stale site in my domain
(`SPEC.md:1142`); the other 9 sites are outside it and are listed below as ready-to-apply patches.

Source at the pin is byte-identical to HEAD `a0ff125`: all 25 post-pin commits touch only FEAT-43
bookkeeping (`git diff --name-only <pin> HEAD` has no path outside the feature dir), so working-tree
reads are pin-accurate.

## Tool truth (derived from the tool, not from prose)

- `code-grade.py:55-56` `_blocks = grade < bar and grade != 2`; `:59-62` `_severity` → `high` if
  blocking, `med` if grade 2, else `None`; `:66` bar 3 for test files, 4 otherwise; `:138-139`
  `_result` = `PASS` iff `grade >= bar`; `:151-154` `SEVERITY:` printed only when severity is truthy,
  `REASON REQUIRED:` only when grade is 2.
- `code_grade.py:42-43` grade is `min` of three bands; **driver joins every tying metric with `+`**.
- `validate-digest.py:36` `SEV = ["none","low","med","high","critical"]`; `:194` binds all three
  reviewers; `:932` `code_grade` enum `{pass, fail, grade_2, n_a}`.
- Probed directly (`/tmp/feat43_docs_probe.py`): `grade=3 bar=4 → blocks=True severity='high'
  result=FAIL`; `_grade(9,10,21.0) → (3,'cyclomatic+cognitive+abc')`.

## Term-by-term verdict

| # | Site | Verdict |
|---|---|---|
| 1 | `glossary.md:5` "worst grade" | consistent (`code_grade.py:42` `min`) |
| 2 | `glossary.md:5` "**Grade 1** is reported as a high-severity finding and grade 2 as med" | **contradicts** — severity follows blocking-ness; grade 3 in production (bar 4) is also `high` |
| 3 | `glossary.md:9` Gated set "new or whose risk grade got worse" | consistent (`code_grade.py:392`) |
| 4 | `glossary.md:13` Driver metric "**The one** of the three metrics" | **contradicts** — `code_grade.py:43` joins ties; live output printed `DRIVER: cyclomatic+cognitive+abc` |
| 5 | `glossary.md:17` ABC magnitude "combined … size" | consistent (no numeric claim; `_round_abc` is `sqrt(a²+b²+c²)`, `:47`). Advisory: "combined" may read as a sum |
| 6 | `glossary.md:21` Cognitive "Sonar-style approximation" | consistent (`code-grade.py:70`) |
| 7 | `glossary.md:25` Cyclomatic "independent paths" | consistent |
| 8 | `harness-code-review/SKILL.md:63-65` blocking → `high` + `code_grade: fail` | consistent (`_blocks`/`_severity`, `validate-digest.py:932`) |
| 9 | `…:65-67` "not only grade 1 … grade-3 production blocks identically", `SEVERITY: high`, `RESULT: FAIL` | consistent — probe-confirmed |
| 10 | `…:67-68` "passes its bar carries no `SEVERITY:` line" | consistent (`code-grade.py:151-152`) |
| 11 | `…:68-71` grade 2 → `med`, `REASON REQUIRED`, never blocks, `code_grade: grade_2` | consistent |
| 12 | `…:58-60` grader command | consistent — **ran it verbatim, exit 0** |
| 13 | `…:93` severity ladder `` `low` / `info` `` | **contradicts** — `info` removed from `SEV` by this feature |
| 14 | `harness-code-risk-grading/SKILL.md:10` bars 4 prod / 3 test | consistent (`code-grade.py:66`) |
| 15 | `…:148-157` "worst band, never averages" + band table | consistent; gated by `check_worked_examples` (`test-code-grade.py:432`) — **ran `test-code-grade.py`: PASS** |
| 16 | `…:159-163` cognitive-driven example, Sonar caveat, shell/TS ungraded | consistent |
| 17 | `…:169` "A **grade-1** gated function is a **high** finding" | **contradicts** — same grade-literal framing; omits grade 3 in production |
| 18 | `…:174` grader command | consistent — **ran it verbatim, exit 0** |
| 19 | `…:13` heading "keep a function **under the bar**" | **contradicts** — pass is `grade >= bar`; this file uses "below the bar" for the failing side at `:164` |

## Changed in my domain (1 line)

`.harness/harness/docs/SPEC.md:1142` — `severity_max: info|…` → `none|…`. It mirrors the base
`reviewer` schema (`validate-digest.py:194`) exactly, so `info` was its only error; the per-persona
extras it omits (`code_grade`, `reviewed`) were already omitted by design. Proven rejected before the
fix: `severity_max='info' is not in ['critical','high','low','med','none']` → `BLOCKED`.

## Not applied — outside my domain, ready to apply

**A. Hard-blocking (4 files, identical edit).** `severity_max: info|low|med|high|critical|n/a` →
`severity_max: none|low|med|high|critical|n/a`, at `.claude/agents/harness-security-reviewer.md:93`,
`.omp/agents/harness-security-reviewer.md:93`, `.claude/agents/harness-ui-reviewer.md:103`,
`.omp/agents/harness-ui-reviewer.md:103`. *Why:* `SEV` (`validate-digest.py:36`) no longer contains
`info`, and `test-validate-digest.py` now asserts "info severity must be rejected"; these templates
tell two reviewers to emit it.

**B. Rollup vocabulary (advisory — `lead` schema does not validate this field, `:207-209`).**
`Add to the DIGEST: \`severity_max: info|low|med|high|critical\` and` →
`… \`severity_max: none|low|med|high|critical\` and`, at
`.claude/agents/harness-validator-lead.md:102` and `.omp/agents/harness-validator-lead.md:106`.

**C. Glossary (`harness-pm` owns).**
- `:13` current `The one of the three metrics that produced a function's risk grade.` → proposed
  `The metric, or metrics, that produced a function's risk grade; ties are reported joined by \`+\`, as in \`cyclomatic+cognitive+abc\`.`
- `:5` current second sentence `Grade 1 is reported as a high-severity finding and grade 2 as med on the existing severity ladder.`
  → proposed `Severity follows blocking-ness, not the grade literal: a gated record below its bar and not grade 2 is \`high\`, a gated grade 2 is \`med\`, and a record at or above its bar carries no severity.`

**D. Risk-grading skill (`.claude/skills/**`, nobody in this segment owns).**
- `:169` current `A grade-1 gated function is a **high** finding and fails review under the existing review rule. A`
  → proposed `A gated function below its bar and not grade 2 — grade 1 anywhere, or grade 3 in production — is a **high** finding and fails review under the existing review rule. A`
- `:13` current `## Habits that keep a function under the bar` → proposed
  `## Habits that keep a function at or above the bar`

**E. Ladder bottom rung — needs a vocabulary ruling, not a rename.** `harness-code-review/SKILL.md:93`,
`harness-security-reviewer.md:80` (both trees), `harness-team/SKILL.md:175`. `none` means "nothing
found", so it is not a drop-in for `info` as a *finding* label. Either drop the `info` rung (such
findings report `low`) or keep `info` as a finding label and state that `severity_max` bottoms at
`none`. Raised as Q1.

## `docs/**` and READMEs

- `docs/**` — the directory does not exist in this repository; nothing to be wrong.
- `README.md`, `.harness/README.md` — no mention of code grading, severity or the review vocabulary
  (grepped for `code_grade|code-grade|risk grade|severity|cyclomatic|driver metric|gated set`).
- `.harness/harness/docs/**` — only `SPEC.md:1142` was falsified (fixed). `DECISIONS.md`/`SPEC.md`
  severity mentions are the `severity_max >= high → FAIL` policy (DEC-31), which this feature reuses
  unchanged and does not falsify. Historical `severity_max: info` in feature notes is left untouched
  as record (principle 15).

## Tree state

```
$ git -C <worktree> status --porcelain
 M .harness/harness/docs/SPEC.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-documentor-validate-goalcheck-c21-product.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/research-goalcheck-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/uat-sc11-c21.md
?? .harness/harness/features/FEAT-43-code-risk-grading/observations/harness-documentor.md
```

The two `research-`/`uat-` untracked files are the sibling pm agents', not mine; the receipt and the
observations log are mine. `SPEC.md` is my one
tracked edit; nothing else differs from the pin. An edit of mine briefly landed in the **main**
checkout (relative path resolved against my cwd, not the worktree) and was reverted byte-identically —
`git -C /Users/molchairuangutai/GitHub/harness status --porcelain` reports no tracked modification.
