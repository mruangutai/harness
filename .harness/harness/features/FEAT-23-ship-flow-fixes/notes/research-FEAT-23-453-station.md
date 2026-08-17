# Research — issue #453, the Plan station — and the red runs for its two clauses

**BLUF: the plan takes option (a), narrowed. The "declare a station" half is VACUOUS for harness's
own board and is deliberately not done; the whole gap is the missing writer. Option (b) as the
operator worded it is already false in the tree, and that is measured, not argued.**

The addition is two tasks — a small writer tool plus its tests, and a kickoff step in
`/harness-plan` — one decision (`D-05`), and one new decision entry folded into the existing
documentor task. No task touches `.harness/harness.json`, `fleet.yaml`, `gh_board.py` or
`gh-sync.py`.

---

## The two discriminating checks the dispatch named

### 1. #350 is CLOSED, and it does not supersede — but its ruling constrains the shape

`gh issue view 350` returns `state: CLOSED`. It closed as a **grilling ruling**, not as
implemented code, and it carries two rulings that bear directly on option (a):

- *"Harness's config gains an explicit stations map and the hardcoded literals go."*
- *"An incomplete board config becomes an error, not a mode"* — `gh_board.load_board`'s silent
  `None` becomes loud.

**No open issue implements either.** `gh issue list --state open --limit 200` was scanned for
`board|station|fleet|harness.json|config`; the closest live items are #278, #277, #262 and #206, and
none of them is that restructure.

**Consequence, and it is the reason this plan does not add a `stations:` map.** Adding one to
`harness.json` now would half-land a ruling whose other half (the literals leaving
`derive_station`, the loud failure mode) nobody is holding, and would leave a map that only one
writer reads. This plan's writer takes the station name as an argument instead, so when the #350
restructure lands there is no second declaration to reconcile. **Recorded so the choice is not read
as an oversight.**

### 2. Option (b)'s premise is FALSE in the tree

`gh-sync.py:185-197` — the parent's station write — has **no `parent_origin` check at all**. It
derives the station and calls `gh_board.set_station` on `rec["parent"]` whatever its origin. The
origin gate exists only on the **close** path, at `gh-sync.py:631` and `:681`, both reading
`if rec["parent_origin"] == "created"`.

So the boundary the tree actually enforces is:

> **The harness MOVES any card it is pointed at. It CLOSES only cards it created.**

A ruling worded "the harness does not touch tickets it did not create" would contradict the shipped
behaviour on every adopted parent. That is what removes (b)-literal — not a preference. A rewritten
(b) ("the harness moves only cards recorded in a feature's `github` block") is coherent, and is
declined for a stated cost in `D-05`: it leaves every measurement in #453 standing.

---

## The four verify-at-source items, re-derived

| Claim | Verdict at HEAD `e26e628` |
|---|---|
| `derive_station` reads task statuses alone → `Building`/`Review`/`None` | **Confirmed**, `gh_board.py:90-118`. Cause 2 stands |
| `Plan` is already a declared lifecycle value | **Confirmed.** DEC-192 prescribes the six values byte for byte; `feature-schema.json` carries `Plan` in the status enum |
| `harness.json`'s board block has no `stations:` map, by design | **Confirmed.** `harness.json` `github.board` has exactly `owner`, `number`, `station_field`. `fleet.yaml`'s map exists for FOREIGN boards |
| `mruangutai/harness` is absent from `fleet.yaml` | **Confirmed** (`fleet.yaml` header, DEC-174 am.1). Its station map does not govern board 3 |

**The net effect, checked rather than inferred:** `gh_board.set_station` (`gh_board.py:174-191`)
takes the station as a **plain string** and passes it to `factory_gh.project_field_set`, which
resolves the option **by name at runtime**. Nothing validates it against a list. And
`gh project field-list 3 --owner mruangutai` returns
`Status ['Backlog', 'Plan', 'Ready', 'Building', 'Review', 'Done']` — the option exists. Issue #453
itself renders as `projects: Harness (Plan)`, i.e. the manual move already put a card there through
the same field.

**So writing `Plan` to board 3 works today with zero configuration change.** Declaring the station
buys nothing on this board; it would only matter if the ruling were fleet-generic, and it is not —
foreign boards reach their stations through `factory_claim`, a different path, and `#453` was
measured on board 3. `fleet.yaml` therefore gets **no `plan:` key**.

## Why the writer cannot live in `gh-sync.py` — forced, not chosen

`gh-sync.py`'s `main()` reads `cmd, feat_dir = argv[0], argv[1]` and then
`if not os.path.isdir(feat_dir): die(...)` **before any subcommand dispatch**, and derives the
harness root by walking up from that directory. At `/harness-plan` kickoff there is no feature
directory at all — that is the same fact that makes `gh-sync open` unrunnable this early. A
`station` subcommand would have to special-case the one positional the whole file is built around.

Hence a new bin, `.claude/skills/harness/bin/board-station.py`. The cost is a **second
board-writing entry point** (`set_station` today has one caller module) and one more call site to
update when #350's restructure lands. Named in `D-05` rather than smoothed over.

## Collisions, adjudicated rather than assumed

| Surface | Tasks | Verdict |
|---|---|---|
| `.claude/commands/harness-plan.md` | T-03 EDIT 2 **and** T-06 | **REAL.** T-03's clause greps `squad plans,.*simplif.*eng-lead reviews architecture` on that file. Ordered `T-06 depends_on [T-03, T-05]`, and T-06's own verify re-asserts T-03's regex so a collision reddens T-06 rather than passing silently |
| `.claude/skills/harness/bin/gh-sync.py` | T-01 only | **NOT a collision.** The #453 writer is a new file; `gh-sync.py` is untouched by T-05 and T-06 |
| `.harness/harness.json` | none | **NOT a collision.** Resolved anyway (below) because the dispatch asked; the plan writes nothing there |
| `.harness/harness/docs/DECISIONS.md` | T-04 only | Both decisions land in the **same** documentor task, so one entry-and-regenerate pass, no race |
| `run-unit-tests.sh` | T-05 only | Registration of the new test file is in the SAME task as the file (G-08) |

## Which bucket the new test goes in — decided by the DETECT globs, not by taste (P-02)

`test-board-station.py` goes in **`UNIT_SCRIPTS`**, and `SC-10`'s evidence kind is `unit`.

`test_kinds.integration.detect` in `harness.json` is an **explicit four-file allowlist**, not a glob;
`test_kinds.unit.detect` carries `.claude/skills/harness/bin/test-*.py`, which matches the new file
automatically. Put the file in the integration bucket and the qa matrix would detect it as `unit`,
run `--kind unit`, and **never execute it** — a gate that proves nothing, and closing that would
require an edit to `.harness/harness.json`. The unit bucket already holds tests that fork the real
script (`test-validate-feature-json.py`, 5 `subprocess` uses; `test-branch-create-gate.py`, 3), so
this is precedent rather than an exception. Detection and execution agree with zero config change,
and T-05's `--kind unit` conjunct then actually executes the new cases as well as proving
registration.

## Lane resolution, run at `b7ae135`

`check-domain.sh --resolve` was run at the working tree. **That resolve is valid at `b7ae135`:**
`git diff --stat b7ae135 HEAD -- .claude/skills/harness/bin/check-domain.sh .harness/team-config.yaml
.harness/factory/fleet.yaml` is **empty** — the resolver and both its inputs are byte-identical
across the range.

| path | `--resolve` said |
|---|---|
| `.claude/skills/harness/bin/board-station.py` | `harness-backend-dev` / `harness-dev-ops` |
| `.claude/skills/harness/bin/test-board-station.py` | `harness-backend-dev` / `harness-dev-ops` |
| `.claude/skills/harness/bin/run-unit-tests.sh` | `harness-backend-dev` / `harness-dev-ops` |
| `.claude/commands/harness-plan.md` | `NOBODY` → `main-session-direct` |
| `.harness/harness.json` | `harness-dev-ops` — **resolved, then ruled out of scope**, not assumed |
| `.harness/factory/fleet.yaml` | `NOBODY` — **resolved, then ruled out of scope** |
| `.claude/skills/harness/bin/gh_board.py` | `harness-backend-dev` / `harness-dev-ops` — resolved; no task writes it |

None of the four DEC-174 files is touched.

---

# Red runs — every new clause EXECUTED, none narrated

## T-05 — conjunct 1, the tool does not exist

**Failing state:** the pre-change tree.

```
T-05: .claude/skills/harness/bin/board-station.py does not exist
exit=1
```

## T-05 — conjunct 2, the registration grep, proved SEPARATELY

Conjunct 1 exits first, so this was run on its own against the real `run-unit-tests.sh`:

```
$ grep -qF "test-board-station.py" .claude/skills/harness/bin/run-unit-tests.sh
RED: not registered (exit 1 path taken)
```

## T-05 — conjunct 3, the drift detector, proved by MUTATION

The clause ends with `bash run-unit-tests.sh --kind unit`. Green-by-default is the FEAT-22 failure
shape, so it was mutated rather than assumed. The detector runs over the **union** of both buckets
(`run-unit-tests.sh:36-39`), so `--kind unit` catches an unregistered integration file too — and
`--kind unit` costs **2.8s measured**, against 52.5s for the integration bucket.

```
unmutated                                              rc=0
one on-disk test file removed from the arrays          rc=2
  MISCONFIGURED: .claude/skills/harness/bin/test-gh-board.py is not in
  run-unit-tests.sh's explicit script list
```

Mutation applied by piping the real script through `sed` while `BIN_DIR` still pointed at the real
bin directory, so the run is the real detector over the real tree, not a mirror of it (P-11).
This is the exact shape an unregistered `test-board-station.py` would create: it fails the WHOLE
run and would redden every other task's verify (G-08).

## T-05 — conjunct 4, the case labels, proved to redden AND to pass

The label strings match `test-gh-board.py`'s `check()` output format exactly — `PASS` followed by
**two** spaces (`test-gh-board.py:28-33`, output confirmed by running it). Note `test-gh-sync.py`
uses a different format (`ok` + four spaces); the two coexist in the tree, so the format is pinned
in T-05's intent rather than left to the author.

```
green suite output          -> T-05 label conjuncts GREEN            exit=0
case FAILs                  -> the station-write case did not pass   exit=1
case silently deleted       -> the station-write case did not pass   exit=1
```

## T-06 — all conjuncts, proved across FOUR states

The marker conjunct is red on the pre-change tree:

```
T-06: the marker <KICKOFF: the source ticket moves to Plan> occurs 0 times in
      .claude/commands/harness-plan.md, expected exactly 1
exit=1
```

The later conjuncts cannot be reached on that tree, so the whole clause was run against a simulated
post-edit file and three mutants of it:

```
post-edit (T-03 then T-06)   -> T-06 GREEN                                        exit=0
T-03's simplify clause gone  -> T-03's plan-surface simplify clause no longer
                                matches - the two edits collided                  exit=1
kickoff marker reworded      -> the marker occurs 0 times, expected exactly 1     exit=1
current tree                 -> the marker occurs 0 times, expected exactly 1     exit=1
```

**Both halves are therefore proved** — the clause can pass on the prescribed edit and reddens on
each of the three failure shapes it exists to catch, including the T-03 collision. The ordering
conjunct compares the marker's line number against the plan-sequence line and both anchors are
asserted to occur exactly once (G-04).

**Probe artefact, not a clause defect:** an earlier probe run used `grep -cF ... <(printf ...)`
under this session's **zsh**, where the count came back empty. The shipped clause greps a real file
path under bash, so the quirk does not reach it; the probe was rerun with pipes (O-03).

## T-04 — the added DEC-196 conjunct

```
$ grep -qE "^## DEC-196 " .harness/harness/docs/DECISIONS.md
RED: no DEC-196 entry (exit 1 path taken)
```

and the index-row conjunct, run separately because the heading conjunct exits before it:

```
$ grep -qE "^- DEC-196 @[0-9]+ " .harness/harness/docs/DECISIONS-INDEX.md
RED: no DEC-196 row in the index (exit 1 path taken)
```

The index-drift conjunct between them was already proved by mutation in
`research-FEAT-23-verify-red-runs.md`; adding a second entry does not change what it detects.

## Where `absorbs` sits, and why it is on ONE task

`absorbs` is consumed by `gh-sync.py`: it is written into the sub-issue body at `:536-537` and, at
`close-task`, prints *"T-NN absorbs #N — left open for the ship briefing"* (`:595-597`). **It does
not auto-close the issue**, so a duplicate would not close #453 early — it would point a watcher at
two sub-issues for one item. It therefore sits on **T-06 alone**, the task that delivers the outcome
the issue asks for, exactly as #430 sits on T-03 and not on T-02 which builds the skill T-03 wires.

---

## Open, non-blocking

**#350's two rulings are closed and unticketed.** The stations map, the removal of
`derive_station`'s hardcoded literals, and `load_board`'s silent `None` becoming loud are all
ruled and none is scheduled. This feature deliberately does not start that work. Worth a backlog
item; it is not FEAT-23's scope.
