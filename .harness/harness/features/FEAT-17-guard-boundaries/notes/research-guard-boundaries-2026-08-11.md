# Research — FEAT-17 guard boundaries — 2026-08-11

BLUF: all four open items from the grilling are decided on evidence; none needs an operator ruling.
The shared rule is extracted into `.claude/skills/harness/bin/harness_boundary.py`, imported lazily
by both guards; the out-of-place-worktree predicate reads the checkout's own `.git` pointer file (no
`git` subprocess, no `git worktree list`); the creation refusal covers `git worktree add|move` broadly
and refuses on an undeterminable destination; `check-state.sh` gains INV-25; the two siblings alive
today are tagged, then pruned.

Measured at `a29ad06` in `/Users/molchairuangutai/GitHub/harness` unless stated.

## D-a — how `bash-write-guard.sh` reaches the shared functions

**A new sibling module `.claude/skills/harness/bin/harness_boundary.py`, imported lazily by both
heredocs, exactly as `harness_yaml` already is.** Precedent verified: `bash-write-guard.sh:73` and
`check-domain.sh:338/502/530` both do `import harness_boundary`-shaped lazy imports of `harness_yaml`
after their manifest checks, and both files are `python3 - "$_derived" ... <<'PY'` heredocs
(`check-domain.sh:97`, and the same shape in the guard), so `sys.path` already contains `bin/`.

**Scope of the refactor, honestly.** It is not five function moves. `select_base` returns
`(base, filter_globs, target_side_test)` and the decision is finished by its CONSUMER —
`check-domain.sh domain_check()` at `:536-660`: glob filtering, base-relative `rel`, the DEC-143
worktree-prefix stripping (`_wt = re.match(r"^\.claude/worktrees/[^/]+/(.+)$", rel)`), the
`target_side_test(r)` filter over candidates, the shared-path branch, and the `Permitted for you:`
advertise list. Replicating only the five module-scope functions in the guard would recreate the
drift. So the extraction is a `classify()` that returns a structured verdict (allow / shared / deny,
plus `rel` and the advertise list) and leaves the PRINTING to each hook.

Two wrinkles that make it not a free move:

- Both guards import `harness_yaml` LAZILY on purpose (`check-domain.sh:292`,
  `bash-write-guard.sh:38`): a top-of-file import made a hook whose module is missing crash before
  the DEC-101 fail-open message. `harness_boundary` inherits that constraint, and
  `test-bash-write-guard.py`'s isolated-copy case (an absent manifest still fails OPEN) is what
  adjudicates it.
- `resolve_fleet()` and `select_base()` today PRINT `check-domain: BLOCKED ...` and `sys.exit(2)`
  themselves. Moved verbatim they would make `bash-write-guard.sh` emit a verdict naming the wrong
  hook. The module takes the label as a parameter.

## D-b — the creation refusal is BROAD, and undeterminable means refuse

Decided on the silent-failure axis the dispatch names. Narrow (`git worktree add` only) fails
silently: exit 0, normal logs, which is the #103 shape. Broad fails loudly.

Broad here means: any `git` invocation whose effect is a new checkout OF THIS REPOSITORY —
`git worktree add` and `git worktree move` — with a destination that does not resolve under
`<root>/.claude/worktrees/`. `git clone` and `git init` are deliberately NOT covered: they
materialise a DIFFERENT repository, which carries no `.harness/team-config.yaml` and no agents, so
nobody is misled into believing it is governed. That is the harm #103 records.

Three mechanics the intent must carry, all verified against `bash-write-guard.sh`:

- `git` produces no entries in `findings`, and `:320` is `if not findings: sys.exit(0)`. The
  worktree scan therefore has to run BEFORE that early exit, or it is dead code.
- `-b`, `-B`, `--reason` consume the following token, so `trailing_files()` would hand back
  `feat/x` as the destination. The scan needs its own flag handling.
- A RELATIVE destination is unresolvable — the Bash payload carries a command, and resolving against
  `root` would read `git worktree add .claude/worktrees/FEAT-99` from an unrelated cwd as legitimate.
  Refuse and say why. The paired allow uses an absolute path under `.claude/worktrees/`.

## D-c — yes, `check-state.sh` reports it, as INV-25

`check-state.sh` is the fourth DEC-174 carve-out (M-4), so the task is `main-session-direct`. The
cost objection that killed `git worktree list` for the guards does not apply: `check-state.sh` runs
once per session entry, not once per governed write. Highest live INV is INV-24
(`check-state.sh:742`, DEC-186), so the new one is INV-25.

## D-d — the predicate, and why it is not the declined `git worktree list`

A linked worktree's root holds a `.git` FILE (not a directory) whose only content is a pointer.
Verified on both live worktrees:

| Checkout | `.git` content |
|---|---|
| `.../scratchpad/r6` (the mistake) | `gitdir: /Users/molchairuangutai/GitHub/harness/.git/worktrees/r6` |
| `.claude/worktrees/FEAT-13-single-issue-board-lookup` (legitimate) | `gitdir: /Users/molchairuangutai/GitHub/harness/.git/worktrees/FEAT-13-single-issue-board-lookup` |

So the rule is SELF-DESCRIBING and needs no subprocess: walk up from the path to the first `.git`
entry; if it is a file, read the pointer; the owning repository root is two levels above
`.git/worktrees/<id>`; the checkout is LEGITIMATE only if its own directory is under
`<owner root>/.claude/worktrees/`. This is identification for refusal, not the declined mapping of a
sibling onto the globs (ruling 1) — no glob is ever evaluated against the sibling.

It also covers the shape the target-side rule alone misses: when `CLAUDE_PROJECT_DIR` IS the sibling,
the sibling carries its own `.harness/team-config.yaml`, root resolves to it, every target is inside
root, and the whole session is governed as if it were `main` — the FEAT-09 incident in the grilling.
The same predicate applied to `root` at entry catches it. Both shapes are therefore claimable.

Cost: the target-side check runs only on the branch where `select_base()` returns
`(None, None, None)` — targets in neither base — so the normal governed write pays nothing. The
root-side check is one `os.path.isfile` walk per hook launch.

## D-e — the siblings alive today: tag, then prune

M-1 settled that nothing is stranded (`r6` is clean). One correction to the prune plan, measured
here: **`52d8334` is NOT an ancestor of `main`** (`git merge-base --is-ancestor` returns non-zero;
the commit is `#133 round 5: ban outer env: and container:, restore the kind-pin ruling`). Removing
the worktree makes it unreachable and gc-eligible. So the task TAGS it before removing, and captures
`git worktree list` before and after to files — untracked live state leaves no commit evidence
(G-15). The FEAT-13 worktree surviving is the paired allow.

## Lanes — every literal `files:` path, resolved with `check-domain.sh --resolve` at `a29ad06`

| Path | `--resolve` answer | Lane in this plan |
|---|---|---|
| `.claude/skills/harness/bin/harness_boundary.py` (NEW) | `harness-backend-dev`, `harness-dev-ops` | main-session-direct |
| `.claude/skills/harness/bin/check-domain.sh` | `harness-backend-dev`, `harness-dev-ops` | main-session-direct |
| `.claude/skills/harness/bin/bash-write-guard.sh` | `harness-backend-dev`, `harness-dev-ops` | main-session-direct |
| `.claude/skills/harness/bin/check-state.sh` | `harness-backend-dev`, `harness-dev-ops` | main-session-direct |
| `.claude/skills/harness/bin/test-check-domain.py` | `harness-backend-dev`, `harness-dev-ops` | main-session-direct |
| `.claude/skills/harness/bin/test-bash-write-guard.py` | `harness-backend-dev`, `harness-dev-ops` | main-session-direct |
| `.claude/skills/harness/bin/test-check-state.py` | `harness-backend-dev`, `harness-dev-ops` | main-session-direct |
| `.harness/features/FEAT-17-guard-boundaries/notes/worktree-list-before.md` | `harness-orchestrator` | main-session-direct |
| `.harness/features/FEAT-17-guard-boundaries/notes/worktree-list-after.md` | `harness-orchestrator` | main-session-direct |
| `docs/harness/DECISIONS.md` | `harness-documentor` | team |
| `docs/harness/DECISIONS-INDEX.md` | `harness-documentor` | team |

**The NEW module's path had no lane history and was resolved before it was written into `files:`.**
It answers the same pair as its siblings in `bin/`, and is nonetheless `main-session-direct`: the
enforcement rule MOVES INTO IT, so it is a DEC-174 carve-out by content. Same divergence the four
named files already carry.

## No dedicated test file for the new module

Deliberate. `run-unit-tests.sh:17-45` keeps explicit `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` arrays and
a drift detector over their union that fails the WHOLE run on an unregistered `test-*.py` (G-08).
The module is exercised BEHAVIOURALLY through both guards' existing suites, which is stronger
evidence than a unit test of the extracted functions (P-13).

## Verification-kind wrinkle — raised, not worked around

`test-check-domain.py` and `test-bash-write-guard.py` match `harness.json`'s `unit` detect glob
(`.claude/skills/harness/bin/test-*.py`) but sit in `INTEGRATION_SCRIPTS`, so
`run-unit-tests.sh --kind unit` does NOT execute them. Every SC resting on those two files therefore
declares `evidence: integration`, whose `cmd` does run them, and each task's `verify:` invokes the
test file directly. Recorded as a BRIEF verification gap and as a non-blocking open question; no
`harness.json` change is in this feature's scope.

## Collision with FEAT-16 — measured, not predicted

FEAT-16's `files:` union measured 16 paths at 09:04 and 18 at 09:08 today — the file's mtime moved
between the two reads, so it is under concurrent edit (G-01). Against the 18-path snapshot, this
plan's 11-path union intersects in exactly 3: `.claude/skills/harness/bin/test-check-domain.py`,
`docs/harness/DECISIONS.md`, `docs/harness/DECISIONS-INDEX.md`. Re-measure at signature.

---

# Cycle-1 rework — what the architecture review changed, and one thing it missed

`runs/2026-08-11-02-archreview-eng/digest.md` returned FAIL with five must_fix. All five are closed
in place; the feature, D-01, `classify()` and the task staging are untouched.

## The finding under MF-1, re-derived at source

Inside the harness base a glob match is accepted only when the TARGET passes
`is_control_plane_target` (`check-domain.sh:277-289`), wired as that base's unconditional target-side
test at `check-domain.sh:249-253`. The test passes a first path segment of `.harness` or `.claude`
(`is_control_plane_glob`, `:158-165`) and otherwise only the CLOSED four-entry
`HARNESS_CONTROL_PLANE` at `:149-154`. So `<root>/allowed/x.txt` under an `allowed/**` grant exits
**2**, and every paired allow in the original draft asserted 0. Fixed by moving the fixture path to
`.harness/allowed/`, never by weakening a claim.

## What the review got wrong: "every FORBIDDEN half stands as written" is false for three

The same rule falsifies three FORBIDDEN halves, and the review's own Secondary section makes the
argument without applying it to that side. With `CLAUDE_PROJECT_DIR` pointed at the sibling, a target
of `<sibling>/allowed/x.txt` exits 2 **from the ordinary glob rule, with the root-side rule entirely
deleted** — non-discriminating (P-01). Affected: BRIEF SC-03's forbidden half, T-02 fixture bullet 3,
T-03's sibling bullet. All three retargeted to `<sibling>/.harness/allowed/x.txt`, which exits 0
without the rule and 2 with it. This strengthens the assertions; it does not move them.

SC-01 and SC-02's forbidden halves genuinely do stand — the sibling is outside root, `select_base`
returns None, and no grant reaches it. Not touched.

## The inverted premise (MF-3), and where exit 2 is safe

Exit 1 is NON-blocking (`check-domain.sh:14`), so an unimportable `harness_boundary.py` would take
both routes silently OFF at once. Fail-closed is affordable **only at the governed import site**:
`_run_domain = _domain_phase = _governed and not _post` (`:432`, `:450`, `:471`, `:493`), so the main
session never reaches `:493`. The SECOND `import harness_yaml`, at `:529` in the shape phase, is
deliberately absorbing and is NOT gated on `_governed` — an exit 2 there would block the main
session's own shape-gated writes. T-01 now names one site and forbids the other. On the Bash route
`harness-dev-ops` returns at `bash-write-guard.sh:54-59`, before line 73. New: REQ-09, SC-10, D-06.

## MF-4 — Reading A, recorded as D-07

`rel` at `bash-write-guard.sh:400` is ROOT-relative, so every product path begins with `..`. The
`..` continue runs after `classify` but only as an outcome filter: deny on `out_of_place_worktree`,
continue on everything else. Dropping it would begin enforcing product-base domains on the Bash route
for the first time — fenced out of scope by the grilling.

## MF-5 — `--resolve`, and the divergence left standing (D-08)

`--resolve` is a second caller of the moved functions (`:357`, `:361-362`, `:399`, `:405`) and takes
the new label parameter. It exits at `:326-417`, before `_governed` is computed at `:432` and before
`domain_check` runs, and it writes nothing — so REQ-02 does not reach it and the divergence T-02
opens is recorded rather than closed. INV-25 is the loud signal instead.

## Q3 closed

`check-plan-routes.py` does NOT execute `verify:` — `BUDGETED_FIELDS` at `:285`, counted at
`:313-321`. T-06's absolute path is a portability wart only, and is left as it is.
