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

## Station

One of the eight names a feature or task carries through its life: `backlog`, `plan`, `ready`, `building`, `review`, `done`, `abandoned`, `rejected`. Declared once, as rows of `factory_config.STATION_ROWS`; every other station fact is derived from that table. The first six have a board column (`MANDATED_STATIONS`); `abandoned` and `rejected` do not (`TERMINAL_STATIONS`).

## Lifecycle bucket

The second axis of the station table: which of three groups a station belongs to — `not_started`, `active` or `finished`. The three buckets partition the eight names, so every station is in exactly one. Call sites ask `factory_config.is_active(name)` or `is_finished(name)` rather than spelling a subset; both raise on a name the table does not declare.

## not_started

The bucket holding `backlog` alone: recorded, nothing yet decided or built.

## active

The bucket holding `plan`, `ready`, `building` and `review` (`ACTIVE_STATIONS`): work is in progress and the feature or task can still move forward.

## finished

The bucket holding `done`, `abandoned` and `rejected` (`FINISHED_STATIONS`): nothing executable remains. Finished is not evidence that work started — `abandoned` can happen before execution and `rejected` happens at intake — which is why `plan-merge.py`'s `_work_started` remains its own historical predicate over `building`, `review` and `done` and is not derived from this bucket.
