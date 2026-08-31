# DAG-ordering audit — FEAT-38 plan.yaml — cycle 1 send-back

**F-1 was one instance of a class with ten members. Nine more were found; all are fixed.** The
mechanism that hid them: every verify block was discrimination-tested against the pre-change tree and
every one exited non-zero, so it looked sound — but an *earlier* conjunct exits first, so the
generator and suite invocations at the end of nine blocks were never executed at all. Their green was
assumed, never observed.

Audited: **23 tasks, 64 verify-referenced artifacts** (files read, files asserted on, executables
run), each checked against `git ls-tree 7ebfc9e` or against the task's **transitive** `depends_on`
closure. Four referenced artifacts do not exist at `7ebfc9e`: `check-decision-anchors.py`,
`test-check-decision-anchors.py` (T-17), `check-decision-claims.py`, `test-check-decision-claims.py`
(T-20). Everything else is in the tree.

## The ten instances and their resolutions

| # | Task | The defect | Resolution |
|---|---|---|---|
| F-1 | T-16 | `check-decision-anchors.py` is T-17's; T-17 not in closure | **edge**: `depends_on: [T-08, T-17]` |
| 1 | T-04 | `gen-decisions-index.py --stdout \|\| exit 1` **cannot** exit 0 after its own deletion — the stale index row is an ORPHAN, a hard error. T-11 regenerates but transitively depends on T-04, so no edge exists | assertion reshaped: ORPHAN line for DEC-140 as positive control, no non-ORPHAN stderr line |
| 2 | T-05 | same, six ids | same shape, six ids |
| 3 | T-07 | same, eight ids | same shape, eight ids |
| 4 | T-08 | same, all fifteen ids already deleted in its closure | same shape, fifteen ids |
| 5 | T-06 | its own change makes two suite cases red by construction; T-11 owns green and depends on T-06 (cycle) | exclude exactly those two case names; assert the regeneration case **is** red as positive control; drop `exit $rc` |
| 6 | T-10 | same two cases, plus the generator now exits 1 on orphans | same |
| 7 | T-19 | gates on the **whole** integration suite, whose green state belongs to T-11 outside T-19's closure and unorderable against it | narrowed to what T-19 owns: no `KIND-DRIFT`, plus `PASS <script>` for each of the two new checkers |
| 8 | T-12 | `grep -r` over `bin/` matches `gen-decisions-index.py` `am.1` (lines 89, 90, 217), removed only by T-10 — not in closure. Also matches gitignored `__pycache__/*.pyc` bytecode | **edge**: `+T-10`; and `--exclude-dir=__pycache__` |
| 9 | T-16, T-21 | both write `DECISIONS.md` but neither is ordered before T-11, which regenerates the index. Nothing restores freshness | **edges**: T-11 `depends_on: [T-09, T-10, T-16, T-21]`, making T-11 the last writer; T-21's generator call becomes orphan-tolerant |

## Evidence (reproducible probes under `/tmp/feat38probe/`)

- **Orphan hazard, instances 1–4, 9.** Sandbox copy of the tree, DEC-140's entry deleted, index
  untouched: baseline `exit 0` → after deletion `exit 1`,
  `ORPHAN: DEC-140 'STRUCK 2026-08-24 with DEC-137 …' has a ruling in the index but no live heading`.
  Mechanism is `gen-decisions-index.py:302-316` — non-sentinel ruling + no live heading = `return None`
  → `sys.exit(1)`. All fifteen deleted ids have own rows with non-sentinel rulings, so all fifteen
  orphan.
- **Instance 5/6, second case.** Removing the strip-before-cap helper pushes three committed rulings
  past the 30-word cap: DEC-37 at 33, DEC-102 at 34, DEC-92 at 36. Recorded in T-06's intent so the
  doer is not surprised.
- **Instance 5/6, first case.** The committed index carries 9 `SUPERSEDED BY` occurrences — 8 row
  suffixes plus the HEADER line at `DECISIONS-INDEX.md:19` — all of which T-06 stops emitting, so
  `test_committed_index_matches_a_fresh_regeneration` fails deterministically.
- **Instance 9.** Inserting two claim markers into DEC-181's body changes **24 index rows**:
  DEC-181's tags go `budget,state,domain,expertise` → `budget,domain,state,skills` (tags are scored
  from the raw body, `compute_tags:248-256`), and every later row's `@<line>` anchor shifts.
- **Added conjuncts proved, not assumed.** Each added conjunct was executed on a tree where the
  earlier conjuncts pass: T-04's tail green with DEC-140 deleted, red when DEC-140 is present, red
  when the generator emits a non-ORPHAN line; the T-06/T-10 exclusion ladder green on the two allowed
  failures, red on a third failure, red when the positive control is absent, red when the new case is
  not `ok`.

## State of the artifact

`plan.yaml` parses; 23 tasks / 12 decisions / 18 lane rows **unchanged**; `approval.status: pending`;
every `verify:` a literal block; every `files:` entry a plain string; `traces:` REQ-NN only; no
`.agents/skills`, no `TBD`. `check-plan-routes.py` on the plan: **exit 0, 0 violations** (the two
T-22/T-23 DEVIATIONs are pre-existing and justified in their `execution_reason`). No dangling
`depends_on` id; the DAG is **acyclic** — topological order:

```
T-01 T-02 T-03 T-04 T-06 T-05 T-07 T-08 T-09 T-10 T-12 T-13 T-14 T-15
T-17 T-16 T-20 T-18 T-19 T-21 T-11 T-22 T-23
```

All 23 blocks pass `bash -n`; all 22 executable blocks still exit non-zero on the pre-change tree, so
discrimination is preserved. The three couplings the cycle-1 author flagged as load-bearing — T-01
before every deletion, T-05/T-07 after T-06, T-08 after T-05 and T-07 — are untouched. `BRIEF.md`
was not edited.

## Open questions

- **Q1 (non-blocking).** T-23's `verify:` runs `gh issue view 448`, so it needs an authenticated `gh`
  and network. That is an external precondition no task in this plan supplies; it was excluded from
  the discrimination run for that reason.
- **Q2 (non-blocking).** T-12's `verify:` greps all of `bin/`, but T-17 and T-20 add new scripts there
  outside T-12's closure. Harmless as specified — neither new script has any reason to cite a deleted
  id — but if one did, T-12 would red on a file its `files:` list does not grant it to edit.
