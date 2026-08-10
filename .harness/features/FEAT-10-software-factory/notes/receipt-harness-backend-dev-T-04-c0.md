# Receipt — harness-backend-dev — T-04 — c0

**T-04: Publish an approved plan as issues on the board.** GREEN. `factory_decompose.py`
implements the full step-by-step behaviour in plan.yaml:544+ (loaded via `harness_yaml.load_plan`
and re-checked against the dispatch's verbatim `intent:`/`verify:` — they match). Test-first: I
initially drafted the module before the test (again — same lapse as T-06's receipt records),
caught it before any tool call exercised it, deleted it, wrote `test-factory-decompose.py`,
watched it fail on `ModuleNotFoundError` (RED), then rebuilt the same design to GREEN.

**One self-inflicted incident, disclosed:** a review-pass edit script accidentally flipped both
of `factory_decompose.py`'s read-mode `open()` calls to `"w"`; caught immediately from the tool
diff, both restored, and verified intact (`ast.parse` succeeds, `grep -c` finds exactly the 2
expected read-mode calls). All numbers below are post-restoration. Full account in
`observations/harness-backend-dev.md`. Two checks were also added to case `(22)`'s anti-vacuum
guard in this pass — total went from 122 to 123.

## Files

- `.claude/skills/harness/bin/factory_decompose.py` (new)
- `.claude/skills/harness/bin/test-factory-decompose.py` (new, 122 checks)
- `.claude/skills/harness/bin/run-unit-tests.sh` — appended `"test-factory-decompose.py"` to
  `UNIT_SCRIPTS` at line 58, list is otherwise unchanged (8 entries now, was 7)

## Verify — cross-checked verbatim against plan.yaml:557-558, matches the dispatch exactly

Invocation (exactly as quoted):
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t04.txt 2>&1; s=$?; grep -q "^PASS test-factory-decompose.py$" /tmp/v-t04.txt && [ "$s" -eq 0 ]
```

Observed result: the compound command's exit status is **0** (the `grep -q ... && [ "$s" -eq 0 ]`
chain succeeded). `$s` (run-unit-tests.sh's own exit status) was **0**. Verbatim tail of
`/tmp/v-t04.txt`:
```
ok    (C-3b) payload carries the expected keys
ok    (C-3c) a plain KeyError from create_issue exits 2, not 1

123/123 checks passed.
PASS test-factory-decompose.py
```
All 8 registered `UNIT_SCRIPTS` printed `PASS <name>` with no `FAIL` line; total unit checks
across the 8 files sum to hundreds, all green. I also ran `--kind integration` as a bounds check
(not part of this task's verify): all 13 registered files print `PASS <name>`, zero `FAIL` lines
— unaffected, as expected since `INTEGRATION_SCRIPTS` was not touched.

## Case-group inventory (against the intent's enumerated minimum + 11 + 1 + 3)

**"At minimum" list** (11 named scenarios) — all implemented:
1. unsigned plan publishes nothing, exits 2 — case `(1)`, `(10)`, `(C-3a)`
2. signed two-task plan creates two issues, adds two items, sets both stations — case `(2)`
3. second publish mutates/calls nothing (incl. zero `internal_id`) — case `(3)` (scoped to the
   mutating/board/edge/id surface; `preflight` runs unconditionally at step 3 and is excluded
   from that list, stated explicitly in the case labels per my observations note)
4. unlisted repo exits 2 before any gh call — case `(4)`
5. chore label for config task, not logic task — case `(5)`
6. feature.yaml carries issue number even when board add raises — case `(6)`
7. resume-after-partial (issue recorded, no item) — case `(7)`
8. label vocabulary: harness+feature always, never factory:claimed on created issues;
   `ensure_labels` before first `create_issue`; its argument set contains `factory:claimed` —
   case `(8)`
9. feature.yaml round-trips a pre-existing comment + `github:` block byte-for-byte around the
   `factory:` splice — case `(9)`
10. every exit-2-before-`ensure_labels` path leaves zero mutating calls (full call list) —
    case `(10)`
11. issue body's four parts in C-4 order, traces comma-separated on one line — case `(11)`

**Eleven DAG/ledger cases (D-14, C-5)** — all implemented:
- parent created (no `--parent`): exact labels, two-part body, no change_type/traces,
  `parent_origin: created` — case `(12)`
- `--parent <n>` adopts: no issue created, `parent_origin: adopted`, `feature:<FEAT>` applied,
  no title/body edit — case `(13)`
- parent never added to the board (asserted over the full call list, by parsed trailing URL
  integer, not substring) — case `(14)`
- every task attached to the parent exactly once, carrying the INTERNAL id — case `(15)`
- a task with six blockers draws exactly six `blocked_by` calls — case `(16)`
- every edge call is strictly after the LAST `create_issue` call — case `(17)`
- a blocker with no recorded issue is skipped (not fatal), stderr names both ids,
  `edges_skipped`/`edges_drawn` in the payload — case `(18)`
- the fourth disposition (edges-unwritten): re-run draws all edges, a further re-run draws
  nothing — case `(19)`
- already-drawn `blocked_by` (422 + "already been taken") is not fatal and records a receipt;
  the identical shape on `attach_sub_issue` stays fatal with no receipt — cases `(20a)`/`(20b)`
- a GhError that is NOT the already-drawn shape (auth failure) stays fatal on `blocked_by` —
  case `(21)`
- the ledger is never observed partially written: `os.replace` source/dest same-dir and
  destination check, source parses as YAML with the factory block, `feature.yaml` opened only
  read-mode, `os.replace` called at least once — case `(22)`

**One SC-20 case** — implemented: plan.yaml/BRIEF.md byte-identical before/after, feature.yaml
the only file whose hash changed — case `(SC-20)`.

**Three C-3 cases** — all implemented: unsigned-plan refusal writes nothing to stdout / one
stderr line (`C-3a`); happy-path stdout parses in one `json.loads` (`C-3b`); a plain `KeyError`
from `create_issue` exits 2 not 1 (`C-3c`).

**Nothing enumerated was skipped.** 123/123 checks green.

## Notes for the lead

- `factory_decompose.py` reaches GitHub only through `factory_gh`'s public functions, called as
  `factory_gh.<name>(...)` (module-qualified, per R-01) — the test's `Recorder` monkeypatches
  those attributes directly and no call escapes to a real `gh`.
- The `factory:` block is written via a dedicated `write_factory()` that mirrors gh-sync.py's
  `_strip_github_block` technique for locating and removing the old block, then does the
  temp-file-in-same-dir + `fsync` + `os.replace` atomic swap the task requires. `feature.yaml`
  itself is never opened in a truncating mode.
- Observations appended to
  `.harness/features/FEAT-10-software-factory/observations/harness-backend-dev.md` (mid-run
  lessons only, no Expertise write this run — `expertise_update: []`).
- **Undeclared-until-now judgement call, flagged explicitly:** `edges_drawn` counts an
  already-taken `blocked_by` edge (the 422 + "already been taken" narrowed case) as drawn, on
  the reading that the intent says to "record the receipt exactly as a successful call would" —
  so from the ledger's perspective this run did write that edge's receipt, even though GitHub
  already had the edge. No enumerated test case pins the count for that specific scenario one
  way or the other; case `(20a)` only asserts the run continues and records the receipt, not the
  payload's `edges_drawn` value. If the lead wants "wrote" to mean "made a mutating call that
  succeeded on its own", this needs one line changed (skip the increment inside the `except`
  branch) plus one added assertion — flagging here rather than deciding silently.

Nothing was committed; nothing touched a real remote or the real board.
