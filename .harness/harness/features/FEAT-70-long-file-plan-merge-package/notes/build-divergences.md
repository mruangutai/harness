# FEAT-70 — build divergences (SC-02 ledger)

Every difference that survived the one normalisation (each checkout's absolute root → `<checkout>`)
in the final executions, with exact bytes and the ruling. The generated receipt prints the same
records beside their rulings; `divergence-rulings.json` is the machine copy the receipt reads.

## Behavioural ledger — 2 records, both stderr, `case_feat61_approval_reset_refuses_an_unknown_task_station` #1 and #2 (`delete-items`)
Old (baseline) / new (pin), the eight frame lines that differ (function names identical throughout):
```
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 3850, in main
+  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 298, in main
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 3521, in cmd_delete_items
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/delete.py", line 301, in cmd_delete_items
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 2602, in _locked_plan_update
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/guards.py", line 237, in _locked_plan_update
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 3518, in transform
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/delete.py", line 298, in transform
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 3476, in _deleted_bytes
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/delete.py", line 256, in _deleted_bytes
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 3497, in _reset_after_deletion
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/delete.py", line 277, in _reset_after_deletion
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 936, in _maybe_reset_approval
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/stations.py", line 166, in _maybe_reset_approval
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 884, in _resume_station
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/stations.py", line 114, in _resume_station
-  File "<checkout>/.claude/skills/harness/bin/plan-merge.py", line 860, in _task_statuses
+  File "<checkout>/.claude/skills/harness/bin/plan_merge/stations.py", line 90, in _task_statuses
```
Exit 1 both; stdout empty both; plan bytes identical; final line identical:
`artifact_accessors.FleetError: unknown station: 'Building' — known stations: backlog, plan, ready, building, review, done, abandoned, rejected`.

RULING (fable-advisor, delegated by the operator, 2026-09-28): accept. "Accepted as an irreducible
consequence of the package split — not a measurement defect and not a behavioural change. Python
tracebacks embed source coordinates, so moving cmd_delete_items byte-for-byte from plan-merge.py:3521
into plan_merge/delete.py:301 necessarily rewrites each frame's file and line, while every function
name in the eight-frame chain, the final FleetError line, exit code, stdout, and plan bytes stay
byte-identical — evidence the call chain itself is unchanged. No consumer parses frame coordinates:
known consumers read exit codes, stdout, or the last stderr line (gh-sync.py:699), and the test
asserts only returncode and the exception message. The rule stays byte-strict; add no traceback
normalization, which could mask a future relocation of the raise site. Scope: these two records'
stderr only."

## Scratch corpus — 5 records in 4 shipped plans, verb `check`
| record | stream | old | new |
|---|---|---|---|
| scratch#954 BUG-1699-lifecycle-cards | stdout | `OK T-02 2 anchor(s) resolved` … `17 anchor(s) resolved, 7 failure(s)` | `FAIL T-02 files: .claude/skills/harness/bin/plan-merge.py#_maybe_reset_approval: no definition or token '_maybe_reset_approval' in .claude/skills/harness/bin/plan-merge.py` … `16 anchor(s) resolved, 8 failure(s)` |
| scratch#2342 FEAT-1714-reject-verb | stdout | … `27 anchor(s) resolved, 7 failure(s)` | `FAIL T-03 files: …plan-merge.py#_legal_stations: no definition or token '_legal_stations' in …plan-merge.py` … `26 anchor(s) resolved, 8 failure(s)` |
| scratch#6247 FEAT-61-control-plane-consolidation | stdout | `OK T-02 14 anchor(s) resolved` … `45 anchor(s) resolved, 1 failure(s)` | `FAIL T-02 files: …plan-merge.py#_review_complete: no definition or token '_review_complete' in …plan-merge.py` … `44 anchor(s) resolved, 2 failure(s)` |
| scratch#6449 FEAT-66-complex-function-drivers | exit | `0` | `1` |
| scratch#6449 FEAT-66-complex-function-drivers | stdout | `OK T-01 17 anchor(s) resolved` … `17 anchor(s) resolved, 0 failure(s)` | `FAIL T-01 files: …plan-merge.py#apply_merge: no definition or token 'apply_merge' in …plan-merge.py` … `16 anchor(s) resolved, 1 failure(s)` |

RULING (fable-advisor, delegated by the operator, 2026-09-29): A — accept, no anchor edited. "The
four FAILs are correct tool output on changed input: both checkouts run identical `check` logic;
the pin repository simply no longer defines those symbols in plan-merge.py. DEC-232 places anchor
resolution at exactly two moments — plan exit and build entry — and these four shipped plans will
see neither again; no standing gate resolves shipped-plan symbol anchors (check-state touches none,
CI's route check is path-only via plan_anchors.path_of, check-decision-anchors grades DECISIONS.md
line anchors). The FEAT-69 precedent does not transfer: DECISIONS.md is a living document under a
mechanical rot check; a shipped plan is a closed record whose anchors were true at its own build —
BUG-1699's c1 review recorded them resolving. Re-pointing would falsify that record, reset four
approvals, and re-pin for zero consumer."

## Superseded executions (recorded because they were measured)
- Smoke ledgers over the worktree and a `/tmp/f70base` checkout before the driver was finished:
  40 differing records in `case_concurrency_real` (which of two racing writers the scheduler let win;
  `ADDED T-15` vs `ADDED T-16`) → the driver serialises consecutive `Popen` calls on both sides;
  then 18 `plan_after` records differing only in `reset_at: '<timestamp>'` → the shim freezes the
  tool's clock on both sides. Both determinism rules are the driver's, applied identically to each
  side, and are named in the generated receipt.
- First full run (2026-09-29 ~05:00Z) killed at a 3,600 s foreground clamp mid-pin; its recorder
  stored full plan bytes for all 6,518 scratch commands (1.2 GB per side, none of which differed)
  and filled the disk — replaced by sha pairs with bytes only when a command changed its plan.
  Second run failed when the baseline checkout was removed from under it by a concurrent worktree
  cleanup. The third run (13:50Z–14:51Z) is the one the receipt derives from.
