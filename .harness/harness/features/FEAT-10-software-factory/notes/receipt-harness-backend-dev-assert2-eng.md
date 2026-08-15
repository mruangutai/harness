# Receipt — harness-backend-dev — B-01, close SC-18 module-scope hole (fix cycle on assert-eng)

**Closed.** `_find_fleet_reads` in `test-factory-config.py` now scans module scope as a scope in
its own right, alongside every function/async function scope, each pruned of nested defs' bodies
so no call is double-attributed. Assertions-only; every `factory_*.py` ends byte-identical.

## The change

`test-factory-config.py`: added `_scope_body_walk(scope_node)` (13 lines) — walks a scope's
children like `ast.walk` but prunes at nested `FunctionDef`/`AsyncFunctionDef` boundaries (yields
the nested def node itself, does not descend into its body; does NOT prune `ClassDef` or
`Lambda`). Rewrote `_find_fleet_reads`: scope list is now `[("<module>", tree)] + [(n.name, n) for
n in ast.walk(tree) if isinstance(n, (FunctionDef, AsyncFunctionDef))]`, and the inner walk uses
`_scope_body_walk(func)` in place of the old `ast.walk(func)`; `args`/defaults tainting is guarded
with `getattr(func, "args", None)` since module scope has none. Tuple's second field renamed
`scope_name` (was `func.name`); shape `(file, scope, lineno, arg_src)` unchanged, so `<module>` is
what a module-scope hit reports.

Net: `_find_fleet_reads` grew from 47 lines to 52, plus the new 13-line `_scope_body_walk` helper
— +18 lines of scan logic, matching the "roughly 10 lines, not 5" pruning budget named in the
dispatch. Zero new `check()` calls.

**A pre-return review caught a real order-of-traversal bug in the first cut of
`_scope_body_walk`, fixed before this receipt was finalised** — see "Bug found and fixed" below.
The description above is the FINAL, fixed shape (`queue.pop(0)`, FIFO); the changed-line count is
unaffected (one-character diff: `stack`/`.pop()` → `queue`/`.pop(0)`).

**Prose updated** (line references are pre-edit, per dispatch): the comment block's "within the
same function" → "within the same scope", plus a sentence naming that module scope and every
function/async-function scope are both scanned; check label "(X) SC-18: exactly one function,
anywhere..." → "(X) SC-18: exactly one scope, anywhere... (module scope or any function)". Second
check label (`"that one reader is factory_config.py's load_fleet"`) was already scope-neutral, not
touched.

## Red demo (a) — module scope, the new hole

Added to `factory_land.py` (module scope, right after `TOOL = "land"`):
```
import harness_yaml
_MODULE_SCOPE_FLEET_PROBE = harness_yaml.load_file(factory_config.FLEET_PATH)
```
Red command: `python3 test-factory-config.py` → exit 1.
Red output:
```
FAIL  (X) SC-18: exactly one scope, anywhere in factory_*.py (module scope or any function), opens/parses the fleet file
        [('factory_config.py', 'load_fleet', 73, 'path'), ('factory_land.py', '<module>', 31, 'factory_config.FLEET_PATH')]
FAIL  (X) SC-18: that one reader is factory_config.py's load_fleet — no other tool bypasses it
        [('factory_config.py', 'load_fleet', 73, 'path'), ('factory_land.py', '<module>', 31, 'factory_config.FLEET_PATH')]
```
**Confirmed this passes GREEN under the OLD function-only code**, cheaply: a standalone script
(`/private/tmp/.../scratchpad/old_logic_check.py`) replicating the exact pre-change
`_find_fleet_reads` (the `isinstance(func, ast.FunctionDef)`-only walk) was run against the same
broken `factory_land.py`. Output: `OLD function-only scan hits: [('factory_config.py',
'load_fleet', 73, 'path')]` — count 1, exit 0 (green). The widening is what closes the hole; the
old scan is silent about it.

Restored `factory_land.py` (Edit reverting the two added lines); `diff` against the backup written
before any change: **exit 0**.

## Red demo (b) — function scope, the old one still works

Restored file re-confirmed byte-identical (diff exit 0) before applying this demo in isolation.
Re-ran the `assert-eng` function-scope demo: inside `factory_land.py:_main`, right after
`args = parser.parse_args()`, added:
```
import harness_yaml
harness_yaml.load_file(args.fleet)
```
Red command: `python3 test-factory-config.py` → exit 1.
Red output:
```
FAIL  (X) SC-18: exactly one scope, anywhere in factory_*.py (module scope or any function), opens/parses the fleet file
        [('factory_config.py', 'load_fleet', 73, 'path'), ('factory_land.py', '_main', 47, 'args.fleet')]
FAIL  (X) SC-18: that one reader is factory_config.py's load_fleet — no other tool bypasses it
        [('factory_config.py', 'load_fleet', 73, 'path'), ('factory_land.py', '_main', 47, 'args.fleet')]
```
Hit list is **two** hits, not three — the pruning works: `_main`'s own body is not also counted
inside `<module>`'s walk. Restored; `diff` against the backup: **exit 0**.

## Bug found and fixed — traversal order broke the assign→call taint chain

My first cut of `_scope_body_walk` used a `stack`/`.pop()` (LIFO), unlike `ast.walk`'s FIFO/BFS
order. Because `tainted` is built incrementally *during* the walk, LIFO can visit a `Call` node
before the `Assign` that feeds it (e.g. body `[Assign, Expr(Call)]` — pushing then popping in LIFO
order visits the `Call`'s parent `Expr` before the sibling `Assign`, since `Assign` was pushed
first and popped last). Consequence: a bypass shaped as `p = factory_config.FLEET_PATH; ...
harness_yaml.load_file(p)`, in ANY scope including function scopes that worked correctly before
this dispatch, went undetected — a fail-open regression, not merely an unclosed module-scope gap.

**Demo (c) — the discriminating case.** Inside `factory_land.py:_main`, after
`args = parser.parse_args()`:
```
import harness_yaml
_p = factory_config.FLEET_PATH
harness_yaml.load_file(_p)
```
`_p` is fleet-bearing only through the assign chain (`"fleet" in "_p"` is false,
`_is_fleet_default(Name('_p'))` is false).

- **Before the fix** (`stack.pop()`, LIFO): `python3 test-factory-config.py` → **GREEN, 56/56,
  exit 0** — the regression, confirmed empirically.
- **Fix**: `stack.pop()` → `queue.pop(0)` (and `stack` renamed `queue`, purely cosmetic), restoring
  `ast.walk`'s FIFO order with the prune intact. One line changed.
- **After the fix**: `python3 test-factory-config.py` → **RED, exit 1**, hit list
  `[('factory_config.py', 'load_fleet', 73, 'path'), ('factory_land.py', '_main', 48, '_p')]` — two
  hits, as expected.

Restored `factory_land.py`; `diff` against the backup: **exit 0**.

**Demos (a) and (b) re-run once, post-fix, to confirm nothing else moved:**
- (a) module scope: RED, exit 1, same two hits as originally reported (`<module>`/`factory_land.py`
  line 31). Restored; `diff` exit 0.
- (b) function scope (`args.fleet`): RED, exit 1, still exactly **two** hits (`_main` line 47,
  not three) — pruning intact after the fix. Restored; `diff` exit 0.

## FLEET_PATH false-positive check

`factory_config.py:50`'s `FLEET_PATH = os.path.join(...)` module-scope assignment is a path
computation, never an argument to `open(`/`load_file(`, so it never appears in `_fleet_reads`.
Confirmed in every green run below: enumeration returns **exactly one** hit,
`('factory_config.py', 'load_fleet', 73, 'path')`.

## No git safety net — restore by copy, verified

Every backup was written with `Write` (per prior run's finding: `cp` into the scratchpad is
blocked by `bash-write-guard`) at
`/private/tmp/claude-501/-Users-molchairuangutai-GitHub-harness/cd83b531-197f-4da6-a4a5-9bb0ec5fcaa5/scratchpad/factory_land.py.bak`
before any change this run. That backup was itself first diffed against the working file
(exit 0 — the prior run's own backup, still present, already matched). Both restores this run
(demo a, demo b) were verified `diff` **exit 0**. Final state: `factory_land.py` untouched from
before this dispatch.

## No commit, no stage

Nothing was staged or committed. `git status` for `factory_land.py` and `test-factory-config.py`
left exactly as `git status` shows for the working tree (both untracked, as before).

## Suites — exit codes and counts

| Suite | Baseline | Result | Exit |
|---|---|---|---|
| `test-factory-claim.py` | 77/77 | **77/77** | 0 |
| `test-factory-config.py` | 56/56 | **56/56** — unchanged, no new check | 0 |
| `test-factory-integration.py` | 97/97 | **97/97** | 0 |

`test-factory-config.py` stayed exactly 56/56: this widens an existing enumeration and adds no
check, as required.

`bash .claude/skills/harness/bin/run-unit-tests.sh` → exit 0 (87 `PASS ` lines total in the
combined run). File-level gate counts unchanged from the receipt this fixes: `--kind unit` →
**10/10** unit-registered `.py` files PASS; `--kind integration` → **14/14** registered
integration-script files PASS (counting `PASS test-*` lines only, excluding per-case sub-checks
inside `test-check-plan-routes.py`), including `test-factory-integration.py`. No file was added to
or removed from either registry by this change.

## check-docs.sh

Receipt written first. Then ran:
`.claude/skills/harness/bin/check-docs.sh` → **exit 0**.

---

## Cycle 1 — self-test the scan, without a 57th check

**Closed.** Folded a throwaway-fixture self-test of `_find_fleet_reads` into the existing
positive-control `check()` at what was `:402-406` (now `:438-444`). Check count stayed **56**;
`_find_fleet_reads`/`_scope_body_walk` were called through their existing signatures, not
refactored.

### The change

Added `_SELFTEST_SRC` (a small string literal, no separate file on disk beyond a throwaway temp
dir) containing three shapes in one fixture module `factory_selftest.py`:
1. module-scope: `_MODULE_PROBE = harness_yaml.load_file(factory_config.FLEET_PATH)`
2. negative: `_IGNORED_PATH = os.path.join('some', 'fleet.yaml')` — never passed to
   `open`/`load_file`, must not be reported
3. function-scope assign-chain, inside `def _reader():` — `_p = factory_config.FLEET_PATH` then
   `harness_yaml.load_file(_p)`, where `"fleet" in "_p"` is False

Wrote the fixture to `tempfile.mkdtemp()`, called `_find_fleet_reads(_selftest_dir,
["factory_selftest.py"])` (existing signature, unmodified), asserted `len(hits) == 2` and
`sorted(scope for hit in hits) == ["<module>", "_reader"]` — scope names asserted, not just
count; the `== 2` clause is what pins the negative `os.path.join` shape (it must not add a third
hit). `shutil.rmtree` cleans up in a `finally`. This boolean (`_selftest_ok`) was ANDed into the
condition of the existing `(X) sanity: ...` `check()` and its label extended to say "...and
reports nothing else (the negative os.path.join shape is not a hit)" — so the label is not
narrower than the condition it now covers. `import shutil` added to the top-of-file import block
(alphabetical). Net: check count unchanged at 56; two new module-level blocks (fixture source +
self-test invocation), no new `check()` call, no change to `_find_fleet_reads`'s or
`_scope_body_walk`'s signature or body.

### Mutation demo (a) — scope list narrowed back to `FunctionDef`-only

Reverted `scopes = [("<module>", tree)] + [...]` to drop the `[("<module>", tree)]` term (edit
made directly on `test-factory-config.py`, this run's own domain file). `python3
test-factory-config.py` → **RED, exit 1**. Failing label, verbatim:
```
FAIL  (X) sanity: factory_*.py enumeration is non-empty and includes factory_config.py, and _find_fleet_reads self-test finds both the module-scope read and the function-scope assign-chain read in a throwaway fixture
        (['factory_claim.py', 'factory_cli.py', 'factory_config.py', 'factory_decompose.py', 'factory_gh.py', 'factory_land.py', 'factory_workspace.py'], [('factory_selftest.py', '_reader', 12, '_p')])
```
(label shown pre-cycle-1's later wording fix; the assertion tripped is the same one)
`1 of 56 FAILING`, i.e. suite count held at 56 while the assertion tripped. Reverted with `Edit`.

**Restore verification, corrected:** a `diff` immediately after this restore against a
`.postfold` reference is a tautology if that reference was itself written by reading the
just-restored file — which is what the first pass of this receipt did, and its "written before
either mutation demo" claim was **false**; retracted here. The reference that genuinely predates
both mutations is the pre-cycle-1 `.bak` copy (written before any cycle-1 edit at all). After
*all* cycle-1 edits landed (fold + the label wording fix below), `diff .bak
<final test-factory-config.py>` → **exit 1** (expected — the fold is a real, intentional change),
with exactly three hunks: the `import shutil` line, the `_SELFTEST_SRC`/self-test-invocation
block, and the `(X) sanity` check's condition+label. **No hunk touches `_scope_body_walk`'s
`queue.pop(0)` line or the `scopes = [("<module>", tree)] + [` line** — i.e. the hunk audit
confirms zero residue from either mutation demo, which is the actual load-bearing claim.

### Mutation demo (b) — `queue.pop(0)` reverted to `queue.pop()` (LIFO)

Edited `_scope_body_walk`'s `queue.pop(0)` → `queue.pop()`. `python3 test-factory-config.py` →
**RED, exit 1**. Failing label, verbatim:
```
FAIL  (X) sanity: factory_*.py enumeration is non-empty and includes factory_config.py, and _find_fleet_reads self-test finds both the module-scope read and the function-scope assign-chain read in a throwaway fixture
        (['factory_claim.py', 'factory_cli.py', 'factory_config.py', 'factory_decompose.py', 'factory_gh.py', 'factory_land.py', 'factory_workspace.py'], [('factory_selftest.py', '<module>', 5, 'factory_config.FLEET_PATH')])
```
The function-scope `_reader` hit vanished under LIFO (only the module-scope hit survived) — the
exact fail-open the assign-chain fixture shape was built to catch. `1 of 56 FAILING`. Reverted
with `Edit`; diffed the whole file against a `.postfold` reference (written to the scratchpad
*after* demo (a)'s restore and *before* demo (b)'s mutation — genuinely predates demo (b), unlike
the retracted framing above) — **exit 0** (byte-identical restore, this diff is not a tautology).

**On the pre-cycle-1 GREEN claim:** neither mutation was re-run against the pre-cycle-1 file this
cycle. It is not directly measured here — it follows from the fact that before this cycle's fold,
no assertion in the suite inspected fixture/self-test behaviour at all, so nothing in the suite
could have tripped on either mutation; that is the premise the send-back stated and this cycle
did not re-verify it by running it. Flagging this rather than asserting it as a fresh measurement.

### Suites and gate, post-restore

| Suite | Result | Exit |
|---|---|---|
| `test-factory-config.py` | **56/56** | 0 |
| `test-factory-claim.py` | **77/77** | 0 |
| `test-factory-integration.py` | **97/97** | 0 |

`bash .claude/skills/harness/bin/run-unit-tests.sh` → **exit 0**; 87 `PASS ` lines in the combined
run (unchanged from cycle 0's count — no file added to or removed from either registry).

### No git safety net, no commit, no stage

Both mutation demos were applied directly to `test-factory-config.py` (this run's own domain
file) and reverted with `Edit`. Demo (b)'s restore was verified against a genuine pre-mutation
`.postfold` reference (diff exit 0). Demo (a)'s restore was verified by (1) a full `Read` of the
file confirming `scopes = [("<module>", tree)] + [` was intact, and (2) the post-cycle `.bak`
hunk audit above confirming no hunk touches either mutation's line. Final state was re-confirmed
green (56/56, exit 0) after the label wording fix. Nothing staged, nothing committed; `git status`
for `test-factory-config.py` unchanged (still untracked).

### check-docs.sh (cycle 1)

Receipt updated first, then ran `.claude/skills/harness/bin/check-docs.sh` → **exit 0**
(`checked 62 superseded pattern(s) across 306 file(s). no stale statements found.`).
