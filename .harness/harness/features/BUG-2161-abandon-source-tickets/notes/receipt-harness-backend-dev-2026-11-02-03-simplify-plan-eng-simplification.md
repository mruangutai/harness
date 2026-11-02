# Receipt — BUG-2161 plan SIMPLIFICATION angle (read-only)

BLUF: 2 low findings, 1 info; no deletion-test failure in the design (source disposal folds into existing `_abandon_plan`/`_apply_abandon_plan`; no new module/command). Checks executed: none.

## Findings
1. [low] plan.yaml:81,106 + BRIEF.md:21 — D-02 / "must not rewrite that station" restates behaviour that already holds.
   Cost: `_record_station` -> `plan_merge/stations.py:293-303` replaces `status:` in place, so a same-station write is byte-identical; `_prune_abandoned_runs` already returns when runs/ is absent (gh-sync.py:1783-1784) and prunes when retained. Prescribing "no rewrite" and a signed decision for it invites a new `if station == abandoned` branch plus a station read, and a decision (DEC-238) that records no new choice. The only new fact is "do not refuse at abandoned", which falls out of removing the early skip.
   Alternative: state the observable (plan.yaml bytes unchanged, runs/ pruned) in T-01/SC-04; call `_record_station` unconditionally; drop D-02 or reduce to one clause under D-01.
2. [low] plan.yaml:83,105,128 + BRIEF.md:17,37 — "exact parent reason, no wording" and "no corpus check" are spelled in D-03, T-01 (x2-3), T-02, SC-02, Constraints.
   Cost: same rule in ~5 places that can drift in a revision.
   Alternative: T-01/T-02 intents cite D-01/D-03 and SC ids instead of restating.
3. [info] plan.yaml:104,108 + BRIEF.md:23 — dead references: "false default for existing direct callers" (cmd_abandon's only caller is gh-sync.py:2511; no test calls it; `yes=False` already the pattern) and "No corpus-lookup detector ... required" (the detector shape was removed by the resolved panel finding).
   Alternative: delete both sentences.

VERDICT: PASS (advisory findings above; route to harness-pm).
