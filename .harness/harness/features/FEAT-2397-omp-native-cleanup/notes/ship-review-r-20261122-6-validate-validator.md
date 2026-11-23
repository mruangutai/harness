# Ship briefing — FEAT-2397-omp-native-cleanup (#2397) — 2026-11-22

**Bottom line: ready to ship.** Validate c2 (`r-20261122-6-validate-validator`) PASSed at review_sha
`eda06a68`, with must_fix empty and severity_max none.

That took one rework round. c0 ESCALATE was ruled by AdvisorC10Escalations. c1 FAILed on a
form-only SC-04 finding and was ruled by AdvisorC11C1Close; c2 was a goalcheck-only re-gate. Spend:
6 runs, 88 wall-clock minutes, rework 1 round and 35 of the budgeted 90 minutes.

## What shipped (audit findings #9–#12)

| Finding | Change |
|---|---|
| #9 Expertise internals | One `{"context": …}` decode carried on PolicyResult; single-pass `_capped_body`; in-process DEC-214 drift check |
| #10 Claude leftovers | Removed: dispatch-guard's `claude` default and its `subagent_type`/`prompt` aliases, `stop_hook_active`, the `CLAUDE_CODE_*` identity arms, and `CLAUDE_PROJECT_DIR` in CI and helpers (renamed to `HARNESS_PROJECT_DIR`). The redundant test env is removed too. The internal Python ABI is kept and documented in DEC-233 |
| #11 Model policy | Native `task.perCallModel: "off"` replaces the dispatch-guard model refusal and `taskModelOverride`. The escalation route lives in `.omp/rules` |
| #12 Context usage | `ctx.getContextUsage()` replaces the JSONL reader, with no fallback. Floor omp ≥18.0.11, observed on real omp 19.1.0, 7/7 (#2194 closed) |
| Doctrine | 23 decision rows rewritten in place. DEC-111 struck. SPEC, the harness command, org.html and the index regenerated |

## Disclosed and carried

- **GC-03 / #2387:** the owner-manifest DEVIATION from the team-config provision rewording appears
  only in a linked worktree. Clone and CI runs are green.
- **Host-environmental unit failures on this machine:** `test-omp-hooks.py` FEAT-2225 ×5,
  `test-factory-config.py` (21), and the BUG-1290 lines. They are identical at the review base in a
  clean clone. QA's managed run was 67/67.
- **T-01's verify pool:** gate-runtime takes about 41 s against a 45 s per-script timeout, a tight
  margin.

## Decisions for ship (delegated authority)

1. Ship and merge.
2. Re-examine #1248 and #612 (sign-off backlog condition).
3. Distill or skip.
4. New backlog rows, if any.
