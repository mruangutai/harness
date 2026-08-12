# Review — harness-code-reviewer — FEAT-17-guard-boundaries (adversarial panel, S1)

**SHA discipline.** `git rev-parse HEAD` = `c6a28bdee6efabe0f7b2a116defaa819ecd88cbd` — matches the
pinned `review_sha` (`c6a28bd`). Reviewed via `git show c6a28bd:<path>` and
`git diff main...c6a28bd` throughout; the working tree's `harness_boundary.py` is byte-identical to
the SHA's blob (`diff` confirmed empty), so probe fixtures imported it directly per the panel's
explicit permission.

`git status --porcelain` START: ` M .harness/features/FEAT-17-guard-boundaries/feature.json` (only).
`git status --porcelain` END: identical, ` M .harness/features/FEAT-17-guard-boundaries/feature.json`
(only) — not mine, present before I touched anything, unrelated to this diff's source files. All
scratch fixtures (`rootA/`, `rootB/`, `workspaceB/`, `noperm/`) were created under the scratchpad via
`python3 -c` file I/O (not shell redirection, which the write guard denies outright for this role) and
removed before this artifact was written; `ls` of the scratchpad shows no residue.

`git log --format='%h %s' main..c6a28bd` — 13 commits, none marked `[harness:human]`; all 13 are
FEAT-17's own T-01..T-07 plus goal-check/grilling/state-sync commits. No hand edit is in scope beyond
what the plan already covers.

`git diff --name-only main...c6a28bd` (18 files, full list, for the "no UI surface" claim):
```
.claude/skills/harness/bin/bash-write-guard.sh
.claude/skills/harness/bin/check-domain.sh
.claude/skills/harness/bin/check-state.sh
.claude/skills/harness/bin/harness_boundary.py
.claude/skills/harness/bin/test-bash-write-guard.py
.claude/skills/harness/bin/test-check-domain.py
.claude/skills/harness/bin/test-check-state.py
.harness/features/FEAT-17-guard-boundaries/BRIEF.md
.harness/features/FEAT-17-guard-boundaries/STATE.md
.harness/features/FEAT-17-guard-boundaries/feature.json
.harness/features/FEAT-17-guard-boundaries/notes/handoff-build.md
.harness/features/FEAT-17-guard-boundaries/notes/receipt-harness-documentor-2026-08-12-07-t07-product.md
.harness/features/FEAT-17-guard-boundaries/notes/research-FEAT-17-goalcheck.md
.harness/features/FEAT-17-guard-boundaries/notes/worktree-removal-receipt-2026-08-12.md
.harness/features/FEAT-17-guard-boundaries/plan.yaml
.harness/notes/grilling-central-product-config-2026-08-12.md
docs/harness/DECISIONS-INDEX.md
docs/harness/DECISIONS.md
```
No UI surface touched. Confirms the scope. `.harness/notes/grilling-central-product-config-2026-08-12.md`
sits outside per-feature `notes/` and outside anything I traced to a REQ/D — flagged below as an open
question, not a finding (low confidence it's this feature's).

---

## Ranked findings

### FINDING 1 — HIGH. `check-state.sh`'s INV-25 silently disables itself, and untested, exactly
where REQ-07's promise matters most

`check-state.sh:967-971` (at c6a28bd):
```python
try:
    import harness_boundary as _hb
    _wt_seg = _hb.WORKTREES_SEGMENT
except Exception:
    _wt_seg = None
```
Every check under INV-25 is gated at `check-state.sh:973`, `if _wt_seg:`. If the import fails,
`_wt_seg` is `None` and the **entire INV-25 block is skipped — no `bad.append`, no `warn.append`,
nothing printed.** Final exit is `sys.exit(1 if bad else 0)` (`check-state.sh:1079`): a run with an
existing out-of-place worktree, but a broken/missing `harness_boundary.py`, prints
`"all state invariants hold."` and **exits 0.**

This is the fourth import site the panel asked me to look for — not enumerated by D-06 (rightly: D-06
scopes itself to "a path that can produce a [write] verdict," and INV-25 is diagnostic, not a write
gate) — but its failure mode is **worse** than the two guards' exit-1-traceback concern: it is not a
crash, it is a silent, deliberate `except Exception: pass`-shaped absorb with zero signal. REQ-07 says
plainly: "An environment that already contains an out-of-place worktree reports it at session entry
**rather than running half-governed**." A broken `harness_boundary.py` is exactly "half-governed" —
by D-06/SC-10 it *also* takes both write guards down (they exit 2 loudly) — and in that same
environment, `check-state.sh` reports clean.

**Concrete scenario.** `harness_boundary.py` is deleted, syntax-broken, or unreachable via PYTHONPATH
(the same state SC-10 tests for the two guards). A pre-existing sibling worktree sits outside
`.claude/worktrees/`. An operator or orchestrator runs `check-state.sh` at session entry, gets "all
state invariants hold," and proceeds believing the environment is clean while the write guards are
simultaneously blocking every governed write with "module could not be imported." The one gate that
should have surfaced *why* — an out-of-place worktree is present — says nothing.

**Confirmed zero test coverage.** `test-check-state.py`'s `case_u` (SC-08's fixture) calls `run()`,
which invokes the *real* `check-state.sh` against the real `bin/` directory — `harness_boundary.py`
is always importable in every SC-08 case. SC-10's isolated-copy-missing-the-module fixture (BRIEF:
"an isolated `bin/` copy carrying `check-domain.sh`, `bash-write-guard.sh` and `harness_yaml.py` but
NOT `harness_boundary.py`") does not include `check-state.sh` at all. No test in this feature's SC
list exercises this path.

**This gates.** Realistic input (a broken shared module — the exact state this feature's own D-06
anticipates and tests for on the write-guard side), wrong outcome (the loudest gate goes silent).

---

### FINDING 2 — HIGH. D-07/DEC-193's "product paths keep exactly today's Bash-route behaviour" is
false for two operand shapes the ruling didn't consider — verified by direct execution, not inference

`bash-write-guard.sh:546` calls `harness_boundary.classify(ap, root, mine, shared, "bash-write-guard")`
**unconditionally, for every finding**, before the outside-repo `..` filter at `bash-write-guard.sh:565-566`
is ever reached (`if rel.startswith(".."): continue`). `classify()` (`harness_boundary.py:232`) calls
`resolve_fleet()` **first thing**, unconditionally, at `harness_boundary.py:261`, and `resolve_fleet`
(defined `:125`) `sys.exit(2)`s internally at `harness_boundary.py:166` if `.harness/factory/fleet.yaml`
exists but does not parse. `select_base` (called `harness_boundary.py:263-264`, defined `:169`)
similarly `sys.exit(2)`s internally at `harness_boundary.py:213` for a target under `workspace_root`
matching no declared repository — reached via `classify`'s `if base is None:` branch at `:265`, which
also calls `worktree_owner(real(abs_target))` at `:271` before falling through to
`not_a_domain_question` at `:283`. All of this happens **inside `classify()`, before it can return a
verdict for the outer `..` filter to discard.**

D-07's claim, verbatim: *"the .. continue runs after classify but only when the outcome is not
out_of_place_worktree, so paths under workspace_root and a product name keep exactly today's
Bash-route behaviour."* DEC-193 repeats it: *"its outside-repo pass-through is preserved, narrowed to
a filter on the verdict rather than removed."* Both are **true only for a genuine product-base path
when `fleet.yaml` parses.** I verified the following before/after table by direct execution — `main`'s
`bash-write-guard.sh` had no `harness_boundary` dependency at all and ran the `..` continue before any
matching (`git show main:.claude/skills/harness/bin/bash-write-guard.sh:406-409`); at `c6a28bd` I
imported `harness_boundary` directly (working-tree copy, byte-identical to the SHA) against hand-built
fixtures and called `classify()` with the exact arguments the guard passes:

| Row (Bash-route operand) | fleet.yaml **absent** | fleet.yaml **valid** | fleet.yaml **broken** |
|---|---|---|---|
| product-base path (under a declared repo) | 0 → 0, unchanged (`not_a_domain_question`, discarded by the outer `..` continue) | 0 → 0, unchanged (verified: `classify()` returns e.g. `{'outcome': 'deny', ...}` without exiting; the outer continue still discards it) | 0 → **2, CHANGED, fail-closed** (`resolve_fleet` exits before the target is even examined) |
| path under `workspace_root`, no declared repo | N/A — no workspace declared | 0 → **2, CHANGED, fail-closed, no SC covers it** (verified: `classify()` raises `SystemExit(2)` from `select_base`'s internal exit, message "belongs to no repository declared") | 0 → **2, CHANGED** (`resolve_fleet` exits first, same as above) |
| outside everything (e.g. `/tmp/x.py`) | 0 → 0, unchanged | 0 → 0, unchanged (verified: `classify()` returns `not_a_domain_question`, no exit) | 0 → **2, CHANGED, broadest blast radius** (verified: `resolve_fleet` exits even for a target with nothing to do with any product or workspace) |
| inside an out-of-place worktree | 0 (the #103 bug) → 2 | 0 → 2 | 0 → 2 |

(The last row's 0→2 in all three columns is the deliberate REQ-01/SC-01 fix and is expected — not part
of this finding.)

Three cells the decision text does not account for all move **fail-closed**, which the panel dispatch
correctly anticipates is still "the finding D-07 asserts does not exist." The most consequential is the
broken-fleet column: **a `.harness/factory/fleet.yaml` that exists but is transiently malformed —
plausible mid-edit, since the main session owns and can be actively editing it — now blocks every
Bash-route write outside the harness root, for every governed agent, including writes that have
nothing to do with products or the workspace** (a scratch file in `/tmp`, for instance). Before this
feature, such writes were never gated on `fleet.yaml`'s validity at all on the Bash route. This is new,
unruled, untested behaviour, and the error message it prints ("the fleet declaration does not load, so
no product path can be identified") names a file with zero connection to the write being attempted.

The valid-fleet "path under workspace_root, no declared repo" cell is arguably *correct* enforcement
(closing a real, related gap) but it is still an **undocumented** verdict change with **no SC covering
it** — D-07 and DEC-193 both assert nothing changes outside the out-of-place-worktree case, and this
row shows something does.

**Why this is HIGH and not the "low, fail-closed" precedent `factory_config.py:140-153` sets for its
own inversion.** That precedent rates a fail-closed inversion low because the direction of the
runtime failure is the only thing wrong. That is not what is being rated here: the gating basis is
that **a signed decision (D-07) and its durable record (DEC-193) assert, in prose the operator
approved, a narrower scope of change than the code delivers, and the deviation is verified by direct
execution rather than inferred.** A decision record that is wrong about what its own code does is a
correctness defect in the record regardless of which direction the runtime behaviour moved — Expertise
P-03/P-06: verify a durable record against the code it names, report a deviation regardless of whether
any individual cell is beneficial. The fail-closed direction is additionally an availability concern
(Finding 2's own broken-fleet cell), not a pure mitigating fact.

**This gates.**

---

### FINDING 3 — MED (structural, not proven live). `domain_check()` is invoked with no wrapping
try/except; every governed exit path elsewhere in this file is deliberately shaped, this one is not

`check-domain.sh:535`: `domain_check()` is called bare, no `try`/`except` around the call, even though
the function (`:392-525`) calls `harness_boundary.worktree_owner` (`:420`) and `harness_boundary.classify`
(`:479`) — both post-import, unguarded call sites, exactly the shape A1's "sharper" question asks
about ("an exception raised AFTER a successful import").

**I could not construct a concrete input that reaches an uncaught exception through this path**, and I
tried the specific candidates the dispatch named:
- `PermissionError`/`OSError` from `os.path.realpath` on an unreadable intermediate directory —
  falsified empirically: `os.path.realpath()` on Python 3.14.5 (the interpreter this repo runs)
  does not raise on a permission-denied path component; it stops resolving that segment and returns
  the normalized path (verified with a `chmod 000` fixture).
- `AttributeError` from a partially-shadowed `harness_boundary` module — not reachable: both guards
  prepend `_selfdir` (the real `bin/` directory) to `PYTHONPATH` *first*, so a same-named module later
  on the path cannot shadow it, and the module is imported once per process (the `--resolve` and main
  paths are mutually exclusive within one invocation, so no double-import race).
- `ValueError` from `os.path.commonpath`/`os.path.relpath` mixing incompatible paths — every
  `commonpath` call in `harness_boundary.py` is already wrapped in `except ValueError` (`:186`,
  `:401`, and `check-state.sh:1013`); the unwrapped `relpath` calls in `classify()` only ever compare
  two `real()`-resolved absolute POSIX paths, which cannot raise `ValueError` for a drive mismatch on
  this platform.
- `RecursionError`/infinite loop in `worktree_owner`'s upward directory walk — the loop has an explicit
  cycle-break (`parent == cur or parent == seen_root`) and terminates normally.

I'm reporting this as a structural gap (defense-in-depth is absent where every documented import site
in the same file has it) rather than a proven exploit, per the epistemic-honesty rule against
presenting a guess as a conclusion. Downgrading it below `med` felt wrong given how deliberately every
*other* exit in this file is shaped to fail closed — but I have no live input, so it does not gate on
its own.

---

### D-06 shape-phase exclusion — RE-VERIFIED, HOLDS

Confirmed at `c6a28bd`, not taken on the plan's word: `check-domain.sh:631` (`_norm`'s worktree-strip
regex, `re.match(r"^\.claude/worktrees/[^/]+/(.+)$", rel)`) and `check-domain.sh:589` (`SWEEP_GLOBS`,
`os.path.join(".claude", "worktrees", "*", _p)`) are both hardcoded literals — neither reads
`harness_boundary.WORKTREES_SEGMENT` or any other attribute of the module. The shape phase carries
zero import of `harness_boundary` anywhere in the file (only two lazy imports exist, both fail-closed,
both under `_run_domain`/`--resolve`, confirmed by full-file grep). D-06's exclusion claim is
factually correct at this SHA.

### D-06 import-site enumeration — RE-VERIFIED, HOLDS (3 sites, all fail-closed)

- `check-domain.sh:167-176`, `--resolve` branch, import at `:168`, `except Exception` → `sys.exit(2)` at `:176`.
- `check-domain.sh:349-358`, main hook path under `if _run_domain:`, import at `:350`, exit 2 at `:358`.
- `bash-write-guard.sh:82-90`, import at `:83`, exit 2 at `:90`.

All three re-derived directly from the SHA (not the plan's stale `:493`/`:357`/`:73` citations, which
have drifted as the panel dispatch itself warned).

### SC-09 (verify: inspection) — INSPECTED, HOLDS

Amended text requires: `notes/worktree-removal-receipt-2026-08-12.md` carries `LATE`,
`archive/worktree-r6` and *sweep*; `git worktree list` names only the main checkout; `archive/worktree-r6`
preserves `52d8334`. All confirmed:
- `notes/worktree-removal-receipt-2026-08-12.md:15` — `"2. \`git tag archive/worktree-r6 52d8334\` before removal | **LATE** — applied 2026-08-12, after removal"`.
- `notes/worktree-removal-receipt-2026-08-12.md:37` — `"the honest characterisation is that this WAS a sweep, not a targeted prune."`
- `notes/worktree-removal-receipt-2026-08-12.md:47` — `"Tags: \`archive/worktree-r6\` -> \`52d8334\`, \`archive/worktree-wt140\` -> \`ffbdbfa\`."`
- `git worktree list` (run against the live checkout at `c6a28bd`) prints exactly one entry, the main
  checkout — no out-of-place worktree present.
- `git rev-parse archive/worktree-r6` → `52d8334862c9b47144b953ce686033385b813fc7`, matching the receipt.

### A2 cross-check (secondary; security-reviewer leads) — no additional caller-side finding

All three `worktree_owner()` call sites — `check-domain.sh:420` (root-side), the internal call inside
`classify()` at `harness_boundary.py:271` (target-side, `_wt_owner`), and `bash-write-guard.sh:128`
(root-side) — treat `None` uniformly as not-a-worktree (`if _wt_owner is not None and not _wt_owner[2]:`
/ `if _root_wt is not None and not _root_wt[2]:`). I found no caller-specific None-handling divergence
a parser-side reading would miss; this is the same fail-open direction the security reviewer is
already tasked with and I have nothing to add beyond confirming the pattern is uniform across all
three call sites.

---

## Spec compliance (Stage 1, lower priority per dispatch)

REQ-01 through REQ-09 and SC-01 through SC-10 were checked against the diff at a `file:line` level
for the specific claims the panel dispatch asked about (D-06, D-07, D-09, SC-08/INV-25, SC-09). I did
not run the full test suite (out of scope for this role — read-only, no Bash execution of the test
files themselves beyond direct `harness_boundary` import against hand-built fixtures) and defer overall
green/red status to qa's own run. No scope creep found in `harness_boundary.py`,
`check-domain.sh`, or `bash-write-guard.sh` beyond what REQ-01..09 and D-01..09 call for.
`.harness/notes/grilling-central-product-config-2026-08-12.md` sits outside any per-feature `notes/`
path and I could not trace it to a REQ/D in this feature's plan — flagged as an open question, not a
finding, since I did not read it in full and it may legitimately belong to FEAT-16's concurrent edit
(BRIEF's own "File-set collision with FEAT-16" section) rather than being this feature's scope creep.

---

## What I could not falsify

Nothing. Every claim I set out to test (A1 completeness, A1's sharper exception-after-import question,
D-06's shape-phase exclusion, A3's verdict table, SC-09's inspection, A2's caller uniformity) was
either confirmed true, confirmed false with a reproducible fixture, or explicitly downgraded to
"attempted and could not reach" (Finding 3) rather than silently dropped. No `open_questions` are
blocking.
