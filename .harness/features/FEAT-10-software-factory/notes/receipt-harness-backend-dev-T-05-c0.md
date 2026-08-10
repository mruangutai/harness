# Receipt — harness-backend-dev — T-05 — Claim the next board item atomically

## Task and files

`T-05` in `.harness/features/FEAT-10-software-factory/plan.yaml` (starts at the `- id: T-05` line
in the `tasks:` list). Files touched:

- `.claude/skills/harness/bin/factory_claim.py` (new)
- `.claude/skills/harness/bin/test-factory-claim.py` (new)
- `.claude/skills/harness/bin/run-unit-tests.sh` (appended `"test-factory-claim.py"` to the end
  of `UNIT_SCRIPTS` at line 58, no other change)

## Verify — cross-checked verbatim against plan.yaml, exact match

Dispatch form:
```
.claude/skills/harness/bin/run-unit-tests.sh --kind unit > /tmp/v-t05.txt 2>&1; s=$?; grep -q "^PASS test-factory-claim.py$" /tmp/v-t05.txt && [ "$s" -eq 0 ]
```
This is byte-identical to plan.yaml's T-05 `verify:` block (confirmed with `awk` against
plan.yaml directly, not from memory).

**Observed result: exit 0.** Ran the command exactly as above. `$?` (verify_result) = `0`,
`$s` (run-unit-tests.sh's own exit) = `0`. Tail of `/tmp/v-t05.txt`:

```
...
70/70 checks passed.
PASS test-factory-claim.py
```

Full unit run: **9/9 `PASS` lines** (`test-harness-yaml-corpus.py`, `test-render-brief.py`,
`test-team-catalog.py`, `test-factory-cli.py`, `test-factory-gh.py`, `test-factory-config.py`,
`test-factory-workspace.py`, `test-factory-decompose.py`, `test-factory-claim.py`), suite exit 0.
Baseline recorded at task start: `--kind unit` exit 0 over 8 files — this run adds exactly one
new `PASS` line and changes nothing else. `--kind integration` re-run after the change: still
13 files, 76 `PASS`/`ok` lines, exit 0 — unaffected, as expected (`run-unit-tests.sh`'s only
change is the `UNIT_SCRIPTS` append).

## TDD

`test-factory-claim.py` was written and run to completion (`ModuleNotFoundError: No module named
'factory_claim'`, confirmed RED) before `factory_claim.py` existed. The implementation was then
written once against that already-complete test file and passed all 68 checks on the first run —
no code was written test-last, no test was adjusted to match the implementation afterward. A
review pass (advisor) then added one further case, `(B5-bis)`, for edge (i) — see the blocker-gate
inventory below — bringing the total to 70/70; that case was added and run before this receipt
was finalized, so it is still pre-return, not a post-hoc patch.

## Case-group inventory

**"At minimum" list (8 groups, all implemented):**
- M1 empty ready column exits 1 — `(M1)` x2
- M2 item in a repo absent from the fleet is not a candidate — `(M2)` x2
- M3 real board-item shape (repository=URL, content.repository=owner/name), selected despite
  the URL-form repository key — folded into the happy-path fixture, `(M3/M6)` x2 (every fixture
  in the file uses this real shape; nothing uses a same-form repository key)
- M4 lowest issue number wins among three claimable — `(M4)` x1
- M5 station option missing from recorder's field options exits 2 BEFORE any board read,
  naming the option, the field and the fleet file — `(M5)` x3, third check asserts all three
- M6 happy path sets station to building exactly once, JSON branch = factory/issue-<n> —
  `(M6)` x2
- M7 feature key equals label value w/ prefix stripped; harness-only label claims normally with
  feature null — `(M7)` x3
- M8 project_items called with a query naming the ready option — `(M8)` x1

**REQ-03 (5 groups, all implemented):**
- R1 create_ref True on first candidate → payload+exit0; label/assign/field_set all AFTER
  create_ref, asserted from call-index order — `(R1)` x2
- R2 EXHAUSTION, both routes — route one (create_ref False x3) and route two (pre-filter
  rejects x3: closed / already-labelled / already-assigned) — both exit 1, stdout empty, zero
  mutating calls; stderr says "no claimable work" and never "no work available"; route1 asserts
  each of the 3 issue numbers + "already exists" (count == 3); route1 stderr != route2 stderr —
  `(R2 route1)` x5, `(R2 route2)` x5, `(R2)` x1 (not-equal)
- R3 lowest-numbered candidate unclaimable, once per reason (closed, already-labelled,
  already-assigned, ref-refused) — still claims the next and exits 0 — `(R3 <reason>)` x4
- R4 `--issue` create_ref False on a foreign login exits 3, zero mutations; `--issue` on a
  self-owned issue exits 0 and re-emits WITHOUT calling create_ref; the same issue in poll mode
  is skipped (exit 1), not re-emitted — `(R4)` x6 across three sub-cases
- R5 create_ref RAISING GhError (not returning False) exits 2, never 3, loop stops (second
  candidate's issue_view never called) — `(R5)` x2

**Blocker gate, SC-22 (7 groups, all implemented):**
- B1 SKIP AND CONTINUE — create_ref called exactly once, with the clear candidate's issue
  number never the blocked one's; blocked candidate's skip reason on stderr, distinct from
  already-labelled/already-assigned — `(B1)` x3
- B2 EVERY CANDIDATE BLOCKED — exit 1, zero mutating calls including create_ref, "no claimable
  work" present and "no work available" absent — `(B2)` x3
- B3 ALL BLOCKERS CLOSED — the previously blocked candidate IS now claimed — `(B3)` x1
- B4 MIXED BLOCKER SET (3 deps: closed, closed, open) — skipped, create_ref called once with
  the clear candidate, stderr names the LAST (open) blocker's T-NN and issue number; same
  fixture with the last blocker also closed — candidate IS now claimed — `(B4)` x3
- B5 UNRESOLVABLE BLOCKER — skipped, not claimed, distinct stderr reason naming the dangling
  T-NN — `(B5)` x2
- (beyond the enumerated seven) EDGE (i), lost task identity — a `feature:` label that resolves
  but whose title yields no matching plan task is BLOCKED, not clear: create_ref called exactly
  once, with the clear candidate's issue number, and the reason text is asserted distinct from
  both blocker-still-open and unresolvable-blocker — `(B5-bis)` x2. Not one of the seven
  enumerated blocker-gate cases; added because DESIGN.md C-2's amendment and the intent both
  name edge (i) explicitly and the receipt's distinct-skip-reason audit requires this reason be
  evidenced, not argued from the code's template shape alone — see the audit table below.
- B6 FEATURE NULL IS UNGATED — claimed normally with feature null; `harness_yaml.load_plan`
  monkeypatched to a recording wrapper and asserted never called for this issue — `(B6)` x2
- B7 `--ISSUE` ON A BLOCKED ISSUE — not owned: exit 2 (never 3, never 0), zero mutating calls,
  no create_ref call, stderr names the blocking T-NN; owned (self-ownership): exit 0, re-emits
  the payload, proving the gate sits after self-ownership — `(B7)` x4 across two sub-cases

**C-3 stream-split (3 groups, all implemented):**
- C1 empty-column path — stdout EMPTY, "no work available" on stderr, exit 1 — `(C1)` x3
- C2 happy path — whole stdout parses in ONE `json.loads`, exit 0 — `(C2)` x2
- C3 monkeypatched `preflight` raising GhError — exit 2 not 1, stdout empty, exactly one stderr
  line naming a concrete value — `(C3)` x4

Total: **70/70 checks pass.** No enumerated case from the intent was dropped; one case
(`B5-bis`) was added beyond the enumerated seven, for edge (i).

## Distinct-skip-reason audit

Every one of the seven reasons the intent requires to be mutually distinct, with its exact
emitted string (from `factory_claim.py`, all printed to stderr, `factory: claim: skip #<n> — `
prefix omitted below for brevity — the full line is `f"factory: {TOOL}: skip #{num} — {reason}"`
except where noted):

| Reason | Exact text |
|---|---|
| already-closed | `issue is not open` |
| already-labelled | `already carries factory:claimed` |
| already-assigned | `already assigned` |
| ref-already-exists | `refs/heads/factory/issue-<n> already exists` |
| blocker-still-open | `issue #<n> is blocked by <T-NN> (issue #<blocker>), which is still open` |
| unresolvable-blocker | `issue #<n> depends_on <T-NN>, which has no recorded issue in feature.yaml (unresolvable blocker)` |
| edge (i) lost-task-identity | `issue #<n> carries a feature: label that resolves, but its title yields no matching plan task (edge (i), lost task identity)` |

All seven strings are textually distinct from one another (no shared reason substring beyond
`"issue"`/`"#<n>"`, which every reason legitimately carries). Pairs the test asserts distinct
directly:
- `(B1)`: blocked candidate's reason vs. already-labelled/already-assigned — asserted by
  checking `"already carries factory:claimed" not in err` and `"already assigned" not in err`
  alongside the blocker reason's presence.
- `(R2)`: route1 (all ref-already-exists, ×3) vs. route2 (already-closed, already-labelled,
  already-assigned, one each) — asserted `err1 != err2` directly, plus route1's own assertion
  that it names all three issue numbers with `"already exists"` exactly 3 times (so route1's
  stderr cannot be confused with a `no work available` empty-column report either).
- `no claimable work` vs. `no work available` — asserted as a positive/negative pair on
  `(R2 route1)`, `(R2 route2)`, `(B2)`: the former string present, the latter absent, in every
  exhaustion/all-blocked case; `(C1)` separately asserts `no work available` for the genuinely
  empty column.
- `(B5)` unresolvable vs. `(B1)`/`(B4)` blocker-still-open — different fixture, different
  candidate, both asserted independently by substring (`"T-99"` for B5, `"T-02"`/`"T-04"` +
  issue numbers for B1/B4); not asserted not-equal against each other directly, but their
  emitted templates are structurally distinct (see table) so no run in this suite could conflate
  them.
- `(B5-bis)` edge (i) vs. blocker-still-open and unresolvable-blocker — asserted directly:
  `"no matching plan task" in err and "still open" not in err and "unresolvable blocker" not in
  err`. This is the case that falsifies a `_blocker_gate` that returns "clear" (instead of the
  edge-(i) tuple) when the task lookup misses — that mutant would call `create_ref` on issue
  #711 and fail `(B5-bis)`'s call-list assertion.

No enumerated case from the intent is left unevidenced; the edge (i) reason, the one row of the
audit table this receipt would otherwise argue only from the code's template shape, is now backed
by `(B5-bis)` and not just cited by name.

## Open questions

None. (Edge (i) was raised as a gap during review and closed with `(B5-bis)` before this
receipt was finalized — see the case-group inventory above — rather than left as an open
question.)

## Notable implementation decisions (cheap, reversible, recorded here not asked)

- The board query strings are my own construction (`f'{station_field}:"{ready_option}" is:open'`
  for poll mode, `"is:open"` for `--issue` mode) since the intent specifies only what the query
  must *contain*, not gh's exact filter syntax; `project_items` is monkeypatched in every test so
  the real syntax is untested here regardless (unchanged from T-04's own stance on this seam).
- MIXED BLOCKER SET's "last blocker" is resolved by scanning every `depends_on` entry in order
  and keeping the last one whose issue is still open (not the first found) — this is what the
  intent's own worked example requires and is exercised directly by `(B4)`.
