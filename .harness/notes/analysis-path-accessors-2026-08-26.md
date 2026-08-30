# Analysis — harness path accessors and the central store — 2026-08-26

Produced by the engineering squad (4 member runs, 3 cycles, 41 minutes) at `ee66ae2`.
**Written to disk by the main session**: `.harness/notes/analysis-*.md` matches no `domain:`
entry in `team-config.yaml`, so `check-domain.sh:828-834` refused every agent that tried. The
lead's own domain (`:296-299`) is runs/expertise/observations only, and `:101` grants pm
`.harness/notes/research-*.md` and nothing else under notes.

## THE HEADLINE

**The refactor as designed changes ZERO call sites.** That contradicts the ask, and the lead
refused to guess which reading is meant. See "The blocking question" at the end.

## Section 1 — Classification

The census is **84**, not 72: 72 from the `.py` AST walk, plus 12 `.sh`-embedded Python heredocs.
A first member run reported 92 and lost its working file; that total is unreconciled and is NOT
relayed as fact.

### A — ROOT RESOLVERS (7 found by the census)

| `file:line` | function |
| --- | --- |
| `context-watch.py:67` | `_repo_root_from_script()` |
| `factory_config.py:44` | `harness_root()` |
| `harness_boundary.py:446` | `worktree_owner()` |
| `wayfind.py:46` | `root()` |
| `dispatch-guard.sh:75` | `_root_from()` |
| `post-merge-sweep.sh:42` | `_resolve_repo_root()` |
| `post-merge-sweep.sh:65` | `_resolve_main_checkout_root()` |

### THE CENSUS IS NOT EXHAUSTIVE, and the lead proved it itself

Two more root resolvers exist that the AST expression **structurally cannot see**:

- `harness_yaml.py:449` — `root = (os.environ.get("HARNESS_PROJECT_DIR") or os.environ.get("CLAUDE_PROJECT_DIR")) or os.getcwd()`, inside `require_or_die()`. Missed because the join lives in `_marker_path`, not in this function's body.
- `check-state.sh:22` — the shell chain, a module-level assignment, not a function.

**So it is 9+ resolvers, not 7.** Any "all call sites" claim rests on a detector that cannot
spell two of them.

### B — LAYOUT ACCESSORS (15)

`context-watch.py:78, :164, :572`, `factory_claim.py:99`, `factory_config.py:334`,
`feature-worktree.py:56`, `feature_schema.py:71`, `gh_cost_log.py:108` (out of scope),
`harness_yaml.py:441`, `inflight_registry.py:52`, `layout_migration.py:194`,
`worktree_terminal.py:38`, `board_lifecycle.py:451`, `wayfind.py:57`, `check-state.sh:58`.

### C — NOT PATH ACCESSORS (58) — stay.

### UNDECIDED (4)

`check-plan-routes.py:460 discover_plans()`, `validate-feature-json.py:39 discover_paths()`,
`feature-worktree.py:157 cmd_list()`, `worktree_terminal.py:185 classify()`.

7 + 15 + 58 + 4 = 84.

## Section 2 — Candidate ruling: `harness_boundary.py`, extended in place. NO NEW FILE.

| candidate | what its docstring owns | imports | importers |
| --- | --- | --- | --- |
| **`harness_boundary.py`** | *"The boundary rule — one implementation, read by every guard that needs it"* | `os`, `re`, `sys` | 5 |
| `factory_config.py` | *"the only reader of a fleet member's own product configuration… always REMOTELY via `factory_gh.file_at_ref`"* | incl. `factory_gh` — **network, at module level** | 23 |
| `wayfind.py` | — | — | 0 |

`factory_config.py`'s 23 importers all inherit an eager network import, which `dispatch-guard.sh`
cannot afford running before every Bash call.

**Caveat, stated rather than hidden:** `harness_boundary.resolve_fleet()` (`:209`) lazily imports
`factory_config` inside its body. Importing the module is network-free; *calling that one
function* is not, and it carries no comment saying so.

## Section 3 — The API: THREE functions, not one

| signature | the ONE question it answers |
| --- | --- |
| `derive_root(bin_dir)` | With zero filesystem checks, what does 4-levels-up arithmetic from this script's own `bin/` say the root is? |
| `manifest_probe_root(bin_dir, probe_relpath, verify_derived=<RATIFY>)` | Does the env var contain `probe_relpath`? Else fall back to `derive_root` — and if `verify_derived`, accept that only if it also contains the probe. |
| `walk_up_for_probe(start, probe_relpath)` | Walking up from `start`, what is the nearest directory containing `probe_relpath`? |

**Deletion test passes on all three.** The 4-up arithmetic is duplicated verbatim at
`factory_config.py:44-50`, `context-watch.py:67-74`, `post-merge-sweep.sh:42-58`; the probe shape
at `check-plan-routes.py:491-513` and `factory_config.py:44-58`; the walk at `wayfind.py:46-53`
and `dispatch-guard.sh:75-88`.

An earlier draft's `harness_path(root, *segments)` was **DROPPED** — deleting it makes no
complexity reappear.

**The cwd-fallback conflict is resolved structurally, not by a flag.** `check-plan-routes.py:460`
is pinned to "no cwd fallback" by `test-check-plan-routes.py:324-330, :935, :983` — the fix for
issue #133's fail-open. Neither `derive_root` nor `manifest_probe_root` touches cwd at all; only
`walk_up_for_probe` does, and it is a separate function. A site cannot pick up a cwd path by
accident.

## Section 4 — Call-site plan: 7 definitions change, 0 call sites change

| function | verdict |
| --- | --- |
| `context-watch.py:67` | THIN-CALLER · 1 site · **DEC-174 barred** (runs inside `context-watch-hook.py`'s `exec_module`) |
| `factory_config.py:44 harness_root()` | THIN-CALLER · 10 invocations, **0 need editing** · not barred · **the only row whose runtime behaviour changes** |
| `harness_boundary.py:446 worktree_owner()` | **STAYS — bucket A was wrong.** It answers "which checkout owns this path" via a `.git`-pointer walk; it never touches env, derive, or probe |
| `wayfind.py:46 root()` | THIN-CALLER · 1 site · not barred |
| `dispatch-guard.sh:75` | THIN-CALLER · 1 site · **barred** (registered PreToolUse) |
| `post-merge-sweep.sh:42` | THIN-CALLER · 1 site · **barred** (self-declared post-merge hook body) |
| `post-merge-sweep.sh:65` | **STAYS — bucket A was wrong.** Asks git which linked worktree is main; its own docstring at `:71-72` insists the two never fuse |

**Bucket B largely collapses, and this is the useful structural result.** 12 of the 15 STAY,
because they already take `root` as an explicit parameter — `harness_yaml.py:441`,
`inflight_registry.py:52`, `board_lifecycle.py:451`, `feature-worktree.py:56`,
`factory_config.py:334` and others. Already parameterised; nothing to centralise.

Three were simply mis-bucketed: `context-watch.py:164` and `:572` operate on
`~/.claude/projects`, not the harness root; `worktree_terminal.py:38` is module-loading by path.

**Not mechanical:** `wayfind.py:46` probes the *directory* `.harness`, not a manifest file.
`check-plan-routes.py:489-495` documents by measurement that `$HOME/.harness/` exists on this
machine, so the directory probe reintroduces issue #133 / B-7's fail-open. **Moving the mechanism
does not close that.**

## Section 5 — What breaks

1. `harness_root()` and `worktree_owner()` are pinned **separately, never together** —
   `test-check-domain.py:1673 run_worktree_grant_parity()` and `test-factory-config.py:774-786`
   case (21). A coverage gap, not a passing contradiction.
2. **`wayfind.py` has ZERO test coverage.** `grep -rl wayfind test-*.py` returns nothing.
   Replacing `root()` changes behaviour with nothing that can go red.
3. `check-plan-routes.py:460`'s "no cwd fallback" is the issue-#133 fix. A careless shared
   resolver silently undoes it.
4. **No `test-harness-boundary.py` exists.** The winning module has no dedicated test file, so
   anything added to it inherits that gap.

## The blocking question

**Q1 — thin-caller, or deletion?** The plan keeps every old name as a thin delegate, so no call
site is repointed and `harness_root()`, `root()`, `_root_from()` all survive. That is the
low-risk read. The other read — delete the old names and repoint all 10+ call sites — is what
the operator's sentence literally says. **These are opposite refactors and the lead refused to
guess.**

## The other open questions

- **Q2 — ratify `verify_derived`.** `True` = uniform fail-closed, matching
  `check-plan-routes.py:503-513`. `False` = matching `factory_config.py:50`. Only
  `factory_config.py:44-59` changes either way — but `harness_root()` runs at **module import
  time** (`FLEET_PATH`, `:59`) for all 23 importers, so `True` needs a real failure path
  (`FleetError` at `:66-71`) rather than today's warn-and-trust. Not a free ratification.
- **Q3** — `.harness/notes/analysis-*.md` is in no agent's domain. One line at
  `team-config.yaml:101` would fix it: `- { path: .harness/notes/analysis-*.md, upsert: true }`.
- **Q4** — is `post-merge-sweep.sh` inside DEC-174's execution bar? It is a self-declared
  post-merge hook body, absent from `.claude/settings.json`'s registered list.
- **Q5** — `harness_yaml.py:449` and `check-state.sh:22` are the 8th and 9th resolvers. Fold in
  or backlog?

## A HARNESS DEFECT the run surfaced

**Three of four dispatches lost their report body.** `validate-digest.py:148` allows a `dev`
persona only `suite: {"pass","fail"}`; `:66` makes `suite: n/a` + `PASS` a rejection. An
**analysis-only** backend-dev therefore has no truthful digest, gets re-prompted, and the
re-emission drops its report.

**Two agents each reasoned themselves into a fabricated `suite: pass` to satisfy it.** The schema
is actively teaching agents to misreport the record. The run only completed when the lead
switched persona to `dev-ops`, where `n/a` + `PASS` is allowed (`:71`).

---

# SETTLED — operator rulings, 2026-08-26

## D-1 · Option B: the old names are DELETED

Not kept as thin delegates. Seven definitions removed, fourteen call sites repointed.
**Reason:** a surviving forwarder is a second door. Someone greps `harness_root`, finds it,
uses it, and never learns the store exists — which is how nine names grew.

## D-2 · ONE marker file, not a parameter

`MARKER = os.path.join(".harness", "team-config.yaml")` — a module constant, never an argument.

The probe is inconsistent today, and that IS the defect:

| Site | Looks for |
| --- | --- |
| `check-plan-routes.py:498` | `.harness/team-config.yaml` |
| `dispatch-guard.sh:89` | `.harness/team-config.yaml` |
| `factory_config.py:39` | `.harness/harness/docs/SPEC.md` |
| `wayfind.py:51` | the `.harness` DIRECTORY — the known fail-open |

**Measured:** `$HOME/.harness/` exists on this machine and holds two backup tarballs —
**no `team-config.yaml`, no `SPEC.md`**. Either file closes `wayfind`'s directory hole.

`team-config.yaml` wins because SPEC.md's path carries the PROJECT NAME
(`.harness/harness/docs/`) and therefore differs per project. `team-config.yaml` is the same
path in every harness project.

## D-3 · `strict=True` everywhere

When the override is discarded AND the derived root also has no marker: refuse, do not warn and
continue. **Reason:** a wrong root produces confident answers about the wrong tree —
`check-plan-routes.py:498` carries the measurement, 36 violations reported from a different
checkout with only the `scanning` line as a clue.

### The import-time risk, checked and cleared

`factory_config.harness_root()` runs at MODULE IMPORT (`FLEET_PATH`, `:59`) for 23 importers,
and `check-domain.sh:196` reaches it: `resolve_fleet` lazily imports `factory_config` inside a
`try`, whose `except` is `sys.exit(2)`. A strict raise there would BLOCK a governed write.

**It cannot fire in that path.** `factory_config` resolves from its own `_BIN_DIR`, not from the
hook's `root`. Under a fixture root the env var is discarded (no marker) and the fallback is the
LIVE checkout, which always carries `team-config.yaml`. Strict raises only when the bin directory
itself sits outside any harness checkout — a broken install, where refusing is correct.

## D-4 · The API — four names, one already exists

```python
# harness_boundary.py — extended in place. NO NEW FILE.

MARKER = os.path.join(".harness", "team-config.yaml")

def root_from_script(bin_dir):
    """Where this script's own location says the root is. No filesystem check."""

def resolve_root(bin_dir, strict=True):
    """The root. Honours HARNESS_PROJECT_DIR only if it carries MARKER, and says on
    stderr when it discards one. Raises when nothing carries MARKER."""

def root_above(start):
    """The nearest directory at or above `start` carrying MARKER, or None."""

def worktree_owner(path):
    """(checkout_dir, owner_root, legitimate). UNCHANGED — not one line."""
```

The team's proposed names — `derive_root`, `manifest_probe_root`, `walk_up_for_probe` — are
replaced. They named the machinery rather than the question, and `probe_relpath` as a parameter
left every caller choosing its own definition of "is this a harness", which is not a single
source of truth.

## D-5 · The migration map

| Old | New | Edits |
| --- | --- | --- |
| `factory_config.harness_root()` | `resolve_root(_BIN_DIR)` | 8 |
| `wayfind.root()` | `root_above(cwd)` — **also closes its fail-open** | 1 |
| `context-watch._repo_root_from_script()` | `root_from_script(_BIN_DIR)` | 1 |
| `dispatch-guard._root_from()` | `root_above(payload_path)` | 1 |
| `post-merge-sweep._resolve_repo_root()` | `root_from_script(BIN_DIR)` | 1 |
| `harness_yaml.py:449` | `resolve_root(_BIN_DIR)` | 1 |
| `check-state.sh:22` | `resolve_root(_BIN_DIR)` | 1 |
| `harness_boundary.worktree_owner()` | — | **stays** |
| `post-merge-sweep._resolve_main_checkout_root()` | — | **stays**, asks git, different question |

**14 call-site edits. 7 definitions removed.**

`dispatch-guard.sh` and `check-state.sh` are enforcement layer. Under DEC-174 the MAIN SESSION
executes those directly, never the team.

## Still open — not ruled

- **Q3** — `.harness/notes/analysis-*.md` is in no agent's domain, so no agent can write this
  kind of report. One line at `team-config.yaml:101` fixes it.
- **Q4** — is `post-merge-sweep.sh` inside DEC-174's execution bar? Self-declared hook body,
  absent from `.claude/settings.json`'s registered list.
- **Q6** — `validate-digest.py:148`/`:66` give an analysis-only dev persona no truthful `suite`
  value. It cost three of four report bodies and pushed two agents into fabricating `suite: pass`.
