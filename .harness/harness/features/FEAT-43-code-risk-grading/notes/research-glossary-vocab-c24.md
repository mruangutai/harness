# Glossary vocabulary alignment — FEAT-43 T-10, cycle 24

**REQ-11 is now met in `.harness/glossary.md`.** The two sentences that contradicted the tool were
rewritten from source I read myself; the other five term entries are byte-unchanged. Two changed
hunks, two changed lines, one file. Send-backs spent: 0.

## What was wrong, and why

**Site 1 — `## Risk grade`, line 5, second sentence.** The old text ("Grade 1 is reported as a
high-severity finding and grade 2 as med on the existing severity ladder") ties severity to the
grade literal. The tool ties it to blocking-ness, so a grade-3 production record (bar 4) is also
`high` — which the old sentence denies.

**Site 2 — `## Driver metric`, line 13.** "The one of the three metrics" asserts a single driver.
The tool joins every tying metric with `+`.

## Re-derivation from source (read at the pin, not adopted from the receipt)

`.claude/skills/harness/bin/code-grade.py:55-62`:

```
def _blocks(grade, bar):
    return grade < bar and grade != 2


def _severity(grade, bar):
    if _blocks(grade, bar):
        return "high"
    return "med" if grade == 2 else None
```

`code-grade.py:66` — the bar: `bar = 3 if _is_test(root, grade.path) else 4`.

`.claude/skills/harness/bin/code_grade.py:42-43` — the driver:

```
    grade = min(value for _, value in metrics)
    return grade, "+".join(name for name, value in metrics if value == grade)
```

## Probe (written under `/tmp`, not in the repo)

`/tmp/feat43_probe_run.py` loads both modules from the worktree and enumerates the severity table
plus a forced three-way tie. Output, verbatim:

```
grade=1 bar=3 blocks=True severity=high
grade=1 bar=4 blocks=True severity=high
grade=2 bar=3 blocks=False severity=med
grade=2 bar=4 blocks=False severity=med
grade=3 bar=3 blocks=False severity=None
grade=3 bar=4 blocks=True severity=high
grade=4 bar=3 blocks=False severity=None
grade=4 bar=4 blocks=False severity=None
grade=5 bar=3 blocks=False severity=None
grade=5 bar=4 blocks=False severity=None
qualname=g grade=2 driver=cognitive cyc=8 cog=17 abc=9.9
tie-check: (1, 'cyclomatic+cognitive+abc')
```

Row `grade=3 bar=4 → high` is the falsifying case for the old sentence. `tie-check` is the
falsifying case for the old driver sentence.

## The two claims I wrote, and what each rests on

1. "a record below its bar and not grade 2 is reported high" — `_blocks` at `:55-56` verbatim,
   confirmed by all ten probe rows.
2. "a grade 2 record med" — `_severity` at `:62`; probe rows `grade=2 bar=3` and `grade=2 bar=4`.
3. "a record at or above its bar carries no severity" — `grade >= bar` implies `grade >= 3` (bar is
   3 or 4 at `:66`), so neither branch fires; probe rows `grade=3 bar=3`, `grade=4/5 bar=3/4`. No
   clash with clause 2: grade 2 can never reach a bar of 3 or 4.
4. "ties are reported joined by `+`, as in `cyclomatic+cognitive+abc`" — the `"+".join` at `:43`;
   probe `tie-check` emits exactly that string.

**Scope wording, deliberately weak:** I wrote "a record", not "a gated record". `_record`
(`code-grade.py:65-73`) computes severity for every record it builds, and only the diff mode's
records are the gated set (`:132-133`); the paths mode grades every function given to it. "A record"
is true in both modes; "a gated record" would have been a narrower claim than the code supports.

## The severity-ladder cross-reference is explicit, not implicit

The dispatch's proposed wording preserved "severity ladder" only implicitly, which would have
weakened the code reviewer's cited evidence that T-10 is met. I therefore opened the sentence with
"On the existing severity ladder, ..." — the phrase survives verbatim and now governs the whole
clause rather than trailing it. This is the one place I departed from the proposed text.

Second, smaller judgement: backticks appear in the file for the first time, on the two literal tool
tokens `+` and `cyclomatic+cognitive+abc`. Line 5 stays plain, matching the file's existing bare
`med`. Cheap and reversible; recorded rather than asked.

## Verification quoted in full

`git -C <worktree> diff -- .harness/glossary.md`:

```
diff --git a/.harness/glossary.md b/.harness/glossary.md
index 10626f9..b14727d 100644
--- a/.harness/glossary.md
+++ b/.harness/glossary.md
@@ -2,7 +2,7 @@
 
 ## Risk grade
 
-The integer from 1 to 5 that a function carries, determined by whichever metric produces the worst grade. Grade 1 is reported as a high-severity finding and grade 2 as med on the existing severity ladder.
+The integer from 1 to 5 that a function carries, determined by whichever metric produces the worst grade. On the existing severity ladder, severity follows blocking-ness rather than the grade literal: a record below its bar and not grade 2 is reported high, a grade 2 record med, and a record at or above its bar carries no severity.
 
 ## Gated set
 
@@ -10,7 +10,7 @@ The functions a change is responsible for: functions that are new or whose risk
 
 ## Driver metric
 
-The one of the three metrics that produced a function's risk grade.
+The metric, or metrics, that produced a function's risk grade; ties are reported joined by `+`, as in `cyclomatic+cognitive+abc`.
 
 ## ABC magnitude
 
```

Exactly two hunks, exactly two lines. `## Gated set`, `## ABC magnitude`, `## Cognitive complexity`,
`## Cyclomatic complexity`, and the first sentence of `## Risk grade` are untouched — the receipt's
CONSISTENT rows 1, 3, 5, 6, 7.

`git -C <worktree> status --porcelain`:

```
 M .claude/skills/harness-code-risk-grading/SKILL.md
 M .harness/glossary.md
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
```

`SKILL.md` is the concurrent engineering run's file; `feature.json` is the orchestrator's. I wrote
neither. My notes file is new and appears as untracked under the feature folder, which is already
untracked as a whole.

`git -C /Users/molchairuangutai/GitHub/harness status --porcelain` (main checkout):

```
?? .harness/harness/features/FEAT-43-code-risk-grading/
?? .harness/harness/features/PR-922-omp-supervision/
?? .harness/logs/2026-08-25.md
?? .harness/logs/2026-08-29.md
?? .harness/notes/analysis-path-accessors-2026-08-26.md
?? .harness/notes/analysis-pr-922-omp-supervision-2026-08-28.md
?? .harness/notes/analysis-pr-922-omp-supervision-c1-2026-08-28.md
?? .harness/notes/grilling-845-one-vocabulary-2026-08-25.md
?? .harness/notes/grilling-root-resolution-2026-08-26.md
?? .harness/notes/probe-746-foreground-dispatch-2026-08-26.md
?? .harness/notes/triage-decisions-authority-2026-08-26.md
```

**No tracked modification.** Every entry is `??` and pre-existing — none of them is
`.harness/glossary.md`. The relative-path leak from the previous run did not recur.

## Open questions

None. The tree is left uncommitted for the orchestrator.
