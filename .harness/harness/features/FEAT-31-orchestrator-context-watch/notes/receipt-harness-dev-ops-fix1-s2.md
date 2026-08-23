# Receipt — harness-dev-ops — FEAT-31 fix1/fix-s2 — independent verification

## BLUF

Independently re-derived every claim in the fix1/s1 receipt. All hold. **100 vs 105 is fully
reconciled and it is NOT a defect**: 100 measured rows + 5 unmeasured rows = 105, exactly matching
105 orchestrator sidecars recounted right now. Set difference is empty both directions — no
SC-10 gap. Acceptance bar re-run, verbatim, matches. All four requested mutants (plus one isolated
mutant I split out for a cleaner discriminator) independently reconstructed in a scratch tmpdir and
each produces a differing COUNT or VALUE from the real code. No vacuous assertion found among the
new cases. The footer's double-read costs ~0.39s of ~0.80s total (roughly half the wall clock,
measured by a disable-and-diff mutant) — real but sub-second, consistent with "not a bottleneck at
this scale," and I made no source change to fix it.

## TASK 1 — the 100 vs 105 reconciliation (measured 2026-08-22T02:52–02:53 UTC, this worktree)

- Total sidecars, 2-level glob `~/.claude/projects/*/*/subagents/agent-*.meta.json`: **2016**
  (drifted up from the operator's 2012 snapshot — expected, 30-day retention + new spawns, including
  this run's own agents).
- Orchestrator sidecars among them (`agentType: harness-orchestrator`, read via `json.load`): **105**.
- No-argument tool run: total output lines **145**; `grep -c ' feature='` = **100**;
  `grep -c ' unmeasured '` = **5**. **100 + 5 = 105 = 145's row-line total** (the other 40 lines are
  the threshold banner and the three footer lines, not additional rows).
- **Set difference of agent ids** (not totals): built the sorted id set from the tool's combined
  measured+unmeasured output and the sorted id set from the sidecar recount. `comm -23`
  (sidecar-not-in-tool) = **empty**. `comm -13` (tool-not-in-sidecar) = **empty**. Every orchestrator
  sidecar that exists right now is printed by the tool; no SC-10 gap. Hypothesis confirmed by
  measurement, not inference.

## TASK 2 — acceptance bar, verbatim

**1. No-argument scan**
```
$ python3 .claude/skills/harness/bin/context-watch.py
EXIT=1
```
100 feature rows, 5 unmeasured rows, 0 occurrences of "no orchestrators found". Exit 1 is CORRECT
per `context-watch.py:37-39` — caused by unmeasured rows being present (5 of them) and/or warnings
crossing the 200,000-token default threshold at ~105 orchestrators; both causes are live
simultaneously here, so the exit code does not isolate which one alone would suffice, but at least
one of the three documented causes fires and none is a crash or a discovery failure.

**2. Live verify — SC-01's live half**
```
$ python3 .claude/skills/harness/bin/verify-context-watch-live.py a7783f0ec41e6a8c6
tool:        current=696472 peak=696472 entries=669
independent: current=696472 peak=696472 entries=669
PASS
EXIT=0
```
All six figures agree and match BRIEF.md:43 (696,472) and the review note (669 measured steps). No
disagreement between tool and independent recomputation.

**3. Timing**
```
python3 .claude/skills/harness/bin/context-watch.py > /dev/null 2>&1
0.66s user 0.10s system 99% cpu 0.764 total
```
Confirms the fixer's ~1.1s figure as an upper bound on this machine; my measurement (0.76s) is in
the same order of magnitude, not materially different — the double-pass I/O flagged in Task 4 does
not turn this into a real bottleneck at this data volume.

**4. Suites**
```
bash .claude/skills/harness/bin/run-unit-tests.sh --kind unit         → EXIT=0, 0 MISCONFIGURED
bash .claude/skills/harness/bin/run-unit-tests.sh --kind integration  → EXIT=0, 0 MISCONFIGURED
```
`test-context-watch.py`: 76 of 76 cases passed. `test-context-watch-cli.py`: 10 of 10 cases passed.
No failing script in either kind — the pre-committed expected-FAIL set (empty) holds.

## TASK 3 — per-assertion capable-of-failing verdicts (own tmpdir mutants, independent of the
fixer's embedded red-proofs)

All four mutants built fresh in `/private/tmp/.../scratchpad/indep-mutants/`, never in the repo;
each anchor block was asserted present in the real source (byte match) before mutation, and each
mutation was asserted to change the source text.

| Mutant | Fixture | Real | Mutant | Discriminates |
|---|---|---|---|---|
| M1 — flatten `discover_orchestrator_rows` to 1 level | 4-agent correct 2-level fixture | rows=**4** | rows=**0** | YES |
| Negative direction — correct code against a WRONG 1-level-shallow fixture | 1 agent at wrong depth | rows=**0** | n/a (real code only) | confirms L2 pins the negative direction genuinely, not vacuously |
| M2 — revert `_build_row` to `sizes[-1]`+0-append, `len(entries)` | last line unmeasured, 2 measured before it | current=**777**, entries=**2** | current=**0**, entries=**3** | YES (both fields) |
| M3 — same revert, isolated fixture (unmeasured line is in the MIDDLE, last line IS measured) | 3 lines, middle unmeasured | entries=**2**, current=**999** | entries=**3**, current=**999** (unchanged) | YES on entries alone — this isolates the entries-count claim from the current-value claim, which the fixer's single N1 fixture conflates (its last line is the unmeasured one, so its RED proof exercises both defects at once) |
| M4 — flatten `_find_agent_paths` in `verify-context-watch-live.py` | 1 agent at correct 2-level depth | finds path (`.../agent-agentZZZ.meta.json`, `...jsonl`) | `(None, None)` | YES |

**Verdict: all four requested mutants are capable of failing for the reason they exist**, confirmed
by an independently-built harness, not by re-running the fixer's own embedded proofs (those were
also observed to pass, but are not treated as the evidence per DEC-124).

**Permissive-implementation trap — checked, no hole found.** `L2` (test-context-watch.py) and the
`root_shallow` case inside `verify-context-watch-live.py`'s `_run_depth_self_test()` both plant a
sidecar at a genuinely WRONG one-level depth and assert it yields **0** rows / `(None, None)`. I
reran both live: `python3 test-context-watch.py` → L2 `ok`; `python3
verify-context-watch-live.py --self-test` → no `SELF-TEST FAIL` line, exit 0. A permissive
multi-depth-trying or unrestricted-recursion implementation would find the shallow-planted sidecar
and fail both checks, so the negative direction is genuinely pinned, not vacuous.

**Assertions I judge vacuous: none among the new CASE L/M/N assertions or the depth self-test.**
Every M-case (M0–M4) asserts a specific literal value (3 lines, "1 measured row", `log_retention_days=45`
with the config path, `100,000`, "excluded... 1") against a fixture built to produce exactly that
value and no other — not a floor, not a presence-only grep. `M1`/`M2`/`M3` combine `len(...) >= N`
guards with an exact-string match on the same line; the `>=` guards only prevent an IndexError before
the real (exact-match) assertion runs and are not, by themselves, the check.

## TASK 4 — architecture question, measured

Built a scratch copy of `context-watch.py` with the `_print_blind_spot_footer` call at the main
table-output call site (the one exercised by the no-argument run) commented out, and timed 3 runs of
each against the real script:

```
with footer (real):    0.80, 0.80, 0.81  (real seconds)
without footer (copy): 0.41, 0.41, 0.43  (real seconds)
```

The double-read costs **~0.39s of ~0.80s total (~49%)** — roughly half the wall clock, not the
minor rounding error "at ~1.1s it does not matter" implied. It is still sub-second in absolute
terms at this corpus size (105 orchestrators, ~2016 sidecars). I made no source change and recommend
none — narrowing the scan would break REQ-05 as the dispatch states, and the number is on the record
for whoever weighs it later. No file under `.claude/skills/harness/bin/` was touched to produce this
measurement; the timed copy lived only in the scratchpad and was deleted immediately after.

## Open questions

None blocking.

## git status — before and after

Identical at both ends of this run (byte-clean):
```
 M .claude/skills/harness/bin/context-watch.py
 M .claude/skills/harness/bin/run-unit-tests.sh
 M .claude/skills/harness/bin/test-context-watch.py
 M .harness/harness.json
 M .harness/harness/features/FEAT-31-orchestrator-context-watch/STATE.md
 M .harness/harness/features/FEAT-31-orchestrator-context-watch/feature.json
 M .harness/harness/features/FEAT-31-orchestrator-context-watch/observations/harness-backend-dev.md
 M .harness/harness/features/FEAT-31-orchestrator-context-watch/plan.yaml
?? .claude/skills/harness/bin/test-context-watch-cli.py
?? .claude/skills/harness/bin/verify-context-watch-live.py
?? .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/receipt-harness-backend-dev-*.md (six files)
?? .harness/harness/features/FEAT-31-orchestrator-context-watch/notes/receipt-harness-dev-ops-T-18-c1.md
```
This receipt is the only file this run created inside the tracked tree.
