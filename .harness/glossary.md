# Glossary

## Risk grade

The integer from 1 to 5 that a function carries, determined by whichever metric produces the worst grade. On the existing severity ladder, severity follows blocking-ness rather than the grade literal: a record below its bar and not grade 2 is reported high, a grade 2 record med, and a record at or above its bar carries no severity.

## Gated set

The functions a change is responsible for: functions that are new or whose risk grade got worse.

## Driver metric

The metric, or metrics, that produced a function's risk grade; ties are reported joined by `+`, as in `cyclomatic+cognitive+abc`.

## ABC magnitude

The combined assignment, branch, and condition size of a function.

## Cognitive complexity

A Sonar-style approximation of how hard a function is to follow, not SonarSource's algorithm.

## Cyclomatic complexity

The number of independent paths through a function.
