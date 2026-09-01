# FEAT-47 G-01 — the stale climb, and the coupling class behind it

**G-01 is closed, and it was not one occurrence.** The `T-03` climb instruction was the visible
case; three more places restated or depended on FEAT-48 internals that are being rewritten this
cycle, and one of them was about to become a red gate rather than a stale quote. All are now fixed
or de-coupled. `check-plan-routes.py` exits 0, 0 violations. `approval:` stays `pending`; no id
renumbered (tasks `T-01..T-06`, decisions `D-01..D-08`, `D-13`, `D-14`, plus a new `D-15` — the
removed `D-09..D-12` stay removed and unreused).

## The climb, verified at source rather than asserted

`plan.yaml` `T-03` said the file derives its root "four levels up while it sits in bin, two levels up
from tests/unit" and to "Repoint that climb to the two-level form". Checked against FEAT-48's plan as
it stands (`FEAT-48-parallel-safe-suite/plan.yaml` `T-03` intent, the DISCOVERY paragraph):

- The root comes from `harness_boundary.root_above`, a **pure marker walk**, wrapped in a named
  `resolve_scan_root(start)`. FEAT-48 states the choice explicitly and gives the reason: it survives
  FEAT-47's move **with no edit at all**. **There is no climb to repoint** — the instruction did not
  merely name the wrong depth, it named a mechanism that will not be on disk.
- FEAT-48 also carries a root-refusal case asserting `resolve_scan_root` returns `None` on a tree
  with no `.harness/team-config.yaml` and that `main()` exits 2 — the case that reddens **if someone
  reintroduces a depth-counting root**. The old FEAT-47 instruction was an instruction to do exactly
  that.

**So the answer to "does it need a root edit under the move" is no — but the answer to "does it need
an edit" is yes, for a different reason the old text got backwards.** It said the file "imports no
bin module". FEAT-48 has it **import `harness_boundary` from its own directory**. After the move its
own directory is `tests/unit`, so the import breaks — an `ImportError` at import time. The rewritten
instruction takes only the `sys.path` half of `T-02`'s recipe: `BIN_DIR` from `__file__`, insert,
import; the climb **locates the module only and must never become the scanned root**. That one
literal depth is unavoidable — the marker walk lives inside the module being imported, so it cannot
be called before the module is on the path — and it is stated as such rather than left to be
rediscovered.

## Verification, not assertion

- `grep` over the whole plan for `two-level form|four levels up|Repoint that climb|imports no bin
  module` → **no matches**.
- `grep` for `climb|two-level|levels up|four-level` → 8 hits, all audited: 5 are `T-02`'s own recipe
  for the 56 pre-existing `bin` tests (correct, nothing to do with FEAT-48), 3 are the new
  `sys.path` text where the literal depth is deliberate and explained.
- `yaml.safe_load` over the file: parses; `T-03` `intent` tail intact; approval and ids as above.
- `check-plan-routes.py <plan>` → `0 violation(s) across 1 plan(s)`, exit 0. The one `DEVIATION`
  (`T-06`, DECISIONS.md granted to harness-documentor) is the declared DEC-174 carve-out already in
  `lanes:`; `UNRESOLVED-GLOB` lines are informational.

## The other coupling — same class, and one half of it was a live red gate

**Two paragraphs restated FEAT-48's `D-11` watched set as fact**: "snapshots every tracked file's
size and mtime around the run" (the `run-unit-tests.sh` rewrite bullet, and the TWO INHERITED GUARDS
paragraph in `T-05`). That set is under revision in FEAT-48 this cycle — a copy here would keep
reading true while ceasing to be true, the identical failure mode as the climb. Both now cite
`D-11` as the single definition and state only what FEAT-47 depends on.

**Then the de-coupling surfaced a harder dependency underneath it, and it is not cosmetic.** FEAT-47
`T-05` must emit a concrete invocation line, so the flag's ARGUMENT is a real input, not a
quotation. Confirmed with FixFeat48C1: FEAT-48's revised `D-11` watches the bin directory, tracked
and untracked, and the argument changes from `"$ROOT"` to `"$BIN_DIR"` — `run_pool.py` watches
exactly the directory it is handed and derives nothing. FEAT-48's `T-06` verify asserts the literal
`--mutation-check "$BIN_DIR"`, so FEAT-47's quoted `"$ROOT"` **would have been a red gate, not a
stale-but-harmless quote.** Fixed: the invocation line, the CARRY bullet, and `T-05`'s own verify,
which now asserts the argument equals the directory the pool script path itself uses —
**rename-proof, and it does not depend on the variable still being called `BIN_DIR`.**

Proved by running the assertion over three lines: correct → PASS; `"$ROOT"` carried forward → RED;
flag dropped → RED with `got !missing`. It was not already-passing before the change (P-01).

**`D-15` is new**, and it is the disclosure the argument change forces. Bin-only watching means the
artifacts under test stay covered — hooks, gate scripts and the helper modules every test imports
all remain in `bin` — but the migration moves the write-beside-yourself site OUT of the watched
directory. One narrow vector is therefore newly unwatched at runtime: **a moved test mutating a file
inside `tests/` through a subprocess.** It is named rather than left implicit. Carried by the static
scan, which walks from the repository root and covers `tests/` with no escape hatch, and by every
moved fixture already being built under `tempfile.mkdtemp()`. Watching the root instead is recorded
as rejected upstream so it is not re-suggested: agents write `features/**` continuously, so a
root-wide runtime set reddens a passing suite on a sibling's note.

## Everything else checked, and clean

Each remaining FEAT-48 reference re-verified against FEAT-48's plan at its current state:

| FEAT-47 claim | FEAT-48 source | |
|---|---|---|
| pool invocation line | `T-04` step 1 | **CORRECTED** — argument was `"$ROOT"`, is now `"$BIN_DIR"` |
| `test-suite-independence.py` in `UNIT_SCRIPTS` | `T-03` REGISTRATION | matches |
| `test-run-pool.py` in `INTEGRATION_SCRIPTS` + explicit `integration.detect` path | `T-04` step 2 | matches |
| `test-run-pool.py` fixtures under `mkdtemp()` | `T-04` item 2 | matches |
| static scan, no escape hatch | `T-03` NO ESCAPE HATCH / `D-04` | matches |
| `discovered >= 50` asserted by the file's own live-tree case | `T-03` red-proof, live-tree bullet | matches — and it also asserts the printed root equals the walk's answer, now cited |
| helpers stay in `bin`, two test files migrate | `D-13` vs FEAT-48 `D-09` | matches |

**Nothing else is stale.** The residual coupling is structural, not an error: FEAT-47 must name
FEAT-48's two new test files to migrate them. That is a file-census contract, which `D-14` already
handles with floors plus a conservation law rather than fixed counts.

**The general lesson, and it is the reason this recurred twice in one pass.** An instruction that
describes the INTERNALS of a file a concurrent feature authors rots without ever reading false, so
no sweep catches it. The rule this plan now follows: cite the sibling's `D-NN` for mechanism, and
state locally only the inputs this plan itself must emit — then gate those inputs in this plan's own
verify, so a stale copy is red here rather than only in the sibling's gate.

## Open

- None blocking. `Q1` from the prior pass is answered by the operator: the `F-07` disclosure is
  accepted, automation belongs to issue #979.
