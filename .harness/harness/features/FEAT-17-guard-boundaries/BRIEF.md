# BRIEF — FEAT-17 Guard boundaries

Closes #261 (P0) and #103 (P0) in one feature.

## Problem

The two write guards disagree at their edges, and both disagreements fail in the safe-looking
direction: the write lands, the exit code is 0, and the log looks normal.

Measured at `a29ad06` (grilling, `.harness/notes/grilling-guard-boundaries-2026-08-11.md`):

- **#261.** With `src/**` granted to `harness-backend-dev` and the target `<root>/src/main.py`, the
  Write route exits 2 and `echo hi > <root>/src/main.py` exits 0. An agent denied by one hook
  succeeds by switching tools — the exact evasion `bash-write-guard.sh` was added to stop.
- **#103, and only one half of it is still live.** A git worktree of this repository sitting outside
  `.claude/worktrees/` is outside the harness root and outside every workspace base, so it falls to
  the branch whose comment reads "not the repo, not deployed, not state" — true of `/tmp`, false of
  a second copy of this repository carrying the same manifest and the same agents. **From a session
  rooted in the real checkout**, three writes that exit 2 here exit 0 when aimed INTO that tree,
  including `.harness/features/X/feature.yaml`, which on that route takes DEC-150's shape caps dark
  with it. Creating one is unguarded too: `git worktree add --detach ~/GitHub/harness-SIBLING HEAD`
  returns 0 from both hooks.
- **#103's founding evidence is OVERTAKEN — recorded here so the next reader does not re-derive a
  closed hole.** FEAT-09's orchestrator wrote a 205-line `feature.yaml` and a 63-line handoff note
  from a session ROOTED in such a tree, unblocked, and reported the caps as unenforced. DEC-180 /
  issue #132 then made SHAPE independent of DOMAIN and bound it to every author, so the caps fire
  relative to whatever root the session stands in. Re-measured at `a29ad06` by rebuilding that exact
  damage from a rooted session (`notes/answers-2026-08-11-rescope.md`): a 211-line `feature.yaml`
  exits 2 and a 70-line handoff note exits 2 — identical to the real checkout — and
  `harness-documentor` writing a `bin/` script from there also exits 2. **A rooted session is fully
  governed: domain fires, shape fires.** What remains for it is that its work lands in a checkout
  nobody merges. That is a lost-work risk, not an enforcement hole, and this feature refuses that
  location on that ground alone.

The cost, on the route that is still live, is a session that believes it is governed and is not.
#103 survived since its filing because the check that was run against it was an allow-list check:
three permitted writes returned 0, and that was read as the hooks being fine.

## Goal

There are exactly two places code is written under harness's authority — `.claude/worktrees/<id>/`
for harness developing itself, and `workspace_root/<product>` for the factory working on a product.
Both are already correct and this feature does not change them. Everything that does not match that
frame gets a verdict instead of silence: an out-of-place checkout cannot be created, cannot be
written into, and — in a parser-present session, the scope recorded under
`## What the root-side rule deliberately does NOT cover` — cannot host a session that thinks it is
the main tree, with both write routes deciding it from one shared implementation, so they cannot
drift apart again.

## Requirements

- REQ-01: A write into a linked worktree of this repository that lives outside `.claude/worktrees/`
  is refused, on the Write/Edit route and on the Bash route alike, with a verdict that names where
  worktrees belong.
- REQ-02: A session whose root IS such a worktree is refused the writes that would otherwise
  succeed there — the ones that are **in-domain relative to that worktree's OWN manifest** and so
  exit 0 today — on both write routes **in a parser-present session.** That scope is chosen and
  recorded, not an omission: under the PyYAML bootstrap grant the Bash route still refuses and the
  Write route does not, for the reasons set out below under
  `## What the root-side rule deliberately does NOT cover`.
  **Its grounds, stated narrowly, because the wider version is false at `a29ad06`.** Such a session
  is NOT ungoverned: its out-of-domain writes and its over-cap writes are already refused relative
  to its own root (DEC-180 / #132; see Problem). What is left is that everything it produces lands
  in a checkout nobody merges, and the ruling that an out-of-place worktree is a mistake rather than
  a supported shape stands. This requirement refuses the location, not an escape. The refusal is
  required on both routes — within that same parser-present scope — because SC-06's mutation proof
  is only reachable with the session root pinned inside a worktree and must flip on both routes or a
  second copy of the rule exists.
- REQ-03: Creating such a worktree is refused before it exists, at the Bash route.
- REQ-04: A path the Write route denies inside the harness checkout cannot be written by switching
  to the Bash route.
- REQ-05: Both guards decide the boundary from one shared implementation, so a change to the rule
  changes both surfaces or neither.
- REQ-06: The two legitimate locations keep exactly today's behaviour.
- REQ-07: An environment that already contains an out-of-place worktree reports it at session entry
  rather than running half-governed.
- REQ-08: The out-of-place worktrees present in this environment today are recorded, made
  recoverable, and removed.
- REQ-09: If the shared implementation cannot be loaded, both routes refuse the write and say why,
  rather than proceeding ungoverned.

## Success Criteria

Every criterion below asserts a FORBIDDEN action refused, pairs it with an allowed action from the
SAME fixture, and names the mechanism that stands the fixture up. An allow-only assertion cannot
tell a working guard from an absent one, which is how #103 stayed open.

**Why every in-root fixture path is under `.harness/`.** Inside the harness base a glob match is
accepted only when the TARGET passes `is_control_plane_target` (`check-domain.sh:277-289`, applied
unconditionally as the harness base's target-side test at `check-domain.sh:249-253`). That test
returns true for a first path segment of `.harness` or `.claude`, and otherwise only for the CLOSED
four-entry `HARNESS_CONTROL_PLANE` list at `check-domain.sh:149-154`. So a grant of `allowed/**`
cannot permit `<root>/allowed/x.txt` — it exits 2 for the same reason SC-05 asserts
`<root>/src/main.py` exits 2. Every paired allow below therefore grants `.harness/allowed/**` and
targets a path under `.harness/allowed/`. The claims are unchanged; only the fixture path is.

The same correction applies to the two ROOT-SIDE forbidden halves, and there it strengthens the
assertion rather than moving it: with `CLAUDE_PROJECT_DIR` pointed at the out-of-place checkout, a
target of `<sibling>/allowed/x.txt` would exit 2 from the ordinary glob rule even if the root-side
rule did not exist, so it could not tell a working guard from an absent one. Targeting
`<sibling>/.harness/allowed/x.txt` under a `.harness/allowed/**` grant exits 0 without the rule and
2 with it.

- SC-01: On the Write route, a write into an out-of-place worktree is refused and the verdict names
  `.claude/worktrees/`. Fixture: `test-check-domain.py` builds a tempdir root holding
  `.harness/team-config.yaml` that grants `.harness/allowed/**` to `harness-backend-dev`, creates the
  directory `<root>/.git/worktrees/sib`, and creates a sibling directory whose `.git` is a FILE
  containing `gitdir: <root>/.git/worktrees/sib` — no `git` binary is invoked. Forbidden: a Write to
  `<sibling>/allowed/x.txt` exits 2 and stderr contains `.claude/worktrees`. The sibling is outside
  root, so no grant can reach it and this half discriminates as written. Paired allow, same
  fixture: a Write to `<root>/.harness/allowed/x.txt` exits 0.
  verify: automated      evidence: integration
- SC-02: On the Bash route, the same forbidden write is refused from the same fixture shape.
  Fixture: `test-bash-write-guard.py`'s `fixture()` plus `fire()`, extended with the same
  hand-built `.git` pointer file. Forbidden: `echo hi > <sibling>/allowed/x.txt` exits 2. Paired
  allow, same fixture: `echo hi > <root>/.harness/allowed/x.txt` exits 0.
  verify: automated      evidence: integration
- SC-03: A session ROOTED in an out-of-place worktree is refused. Fixture: the same hand-built
  pointer files, with `CLAUDE_PROJECT_DIR` pointed at the sibling, which carries its own
  `.harness/team-config.yaml` granting `.harness/allowed/**`. Forbidden: a write to
  `<sibling>/.harness/allowed/x.txt` — a path that is in-domain and control-plane, so it exits 0
  unless the root-side rule refuses it — exits 2 on both routes. Paired allow, same fixture: the
  identical relative payload with `CLAUDE_PROJECT_DIR` pointed at a legitimate-shaped
  `<root>/.claude/worktrees/wt` (built by the same pointer-file mechanism and carrying its own
  manifest with the same grant), targeting `<root>/.claude/worktrees/wt/.harness/allowed/x.txt`,
  exits 0 on both routes.
  **This criterion is the sole assertion of the root-side rule's UN-MUTATED refusal, on each route
  — SC-06 proves one-implementation by mutation and cannot stand in for it.** It is scoped to a
  parser-present session: the no-PyYAML variant was cut in the 2026-08-11 re-scope, because under
  the bootstrap grant the domain check is skipped in the real checkout too, so that case adds
  nothing worse than the sanctioned escape already does. The consequence is recorded, not hidden —
  see the note below this list.
  **The root-side wording is asserted, both directions, on the forbidden half's stderr on each
  route:** it contains `.claude/worktrees`, and it does NOT contain `git worktree remove`. The
  positive half alone ships a verdict that names nowhere; the negative half alone passes for a
  verdict that says nothing. Both are needed because `git worktree remove` succeeds at exit 0 from
  inside the tree it removes (measured), so that sentence printed to a session standing in the tree
  is an instruction to delete its own cwd. The negative is scoped to the root-side verdict only —
  the target-side verdict keeps that guidance and is correct to.
  verify: automated      evidence: integration
- SC-04: Creating an out-of-place worktree is refused at the Bash route. Fixture:
  `test-bash-write-guard.py`'s `fixture()`/`fire()`. Forbidden, all exit 2: an absolute destination
  outside `.claude/worktrees/`; the same with `-b feat/x` before it, so a flag cannot hide the
  destination; a RELATIVE destination, which cannot be resolved and is therefore refused. Paired
  allows, same fixture, all exit 0: `git worktree add <root>/.claude/worktrees/FEAT-99 HEAD`,
  `git status --porcelain`, `git worktree list`, and `git commit -m x`.
  verify: automated      evidence: integration
- SC-05: The two write routes return the same verdict for the #261 shape. Fixture: a tempdir root
  whose manifest grants `src/**` and `.harness/allowed/**` to `harness-backend-dev`. Forbidden:
  `<root>/src/main.py` exits 2 on the Bash route AND on the Write route. Paired allow, same fixture:
  `<root>/.harness/allowed/x.txt` exits 0 on both.
  verify: automated      evidence: integration
- SC-06: The rule has exactly one implementation, proved by mutation rather than by grep. Fixture:
  an isolated `bin/` copy in a tempdir containing `check-domain.sh`, `bash-write-guard.sh`,
  `harness_boundary.py` and `harness_yaml.py`, plus a root manifest and the hand-built pointer files;
  `CLAUDE_PROJECT_DIR` is pinned to `<root>/.claude/worktrees/wt`, which carries its own
  `.harness/team-config.yaml` granting `.harness/allowed/**`, so the mutation is observed through the
  ROOT-SIDE check on both routes; the payload targets
  `<root>/.claude/worktrees/wt/.harness/allowed/x.txt`. The named legitimate-location constant in the
  COPIED module is then edited. Allowed-turned-forbidden: the verdict for that one identical payload
  flips from 0 to 2 on BOTH routes. Pinning the root is what makes the flip reachable — a payload
  aimed at the worktree from OUTSIDE it never reaches the rule, because the path is inside root on
  the Write route and hits the DEC-153 `.claude/worktrees/` carve-out on the Bash route. If it flips
  on one route only, a second copy of the rule exists and the criterion is not met.
  verify: automated      evidence: integration
- SC-07: The two legitimate locations are unchanged. Fixture: the same tempdir roots, whose manifest
  grants `.harness/allowed/**` and `src/**`. Allow: a write to
  `<root>/.claude/worktrees/wt/.harness/allowed/x.txt` — reached through DEC-143's worktree-prefix
  stripping, from OUTSIDE that worktree — exits 0 on both routes, and every pre-existing case in
  `test-check-domain.py` and `test-bash-write-guard.py` still passes, none deleted. Which edits that
  permits is a rule, not a list: retargeting a fixture path while PRESERVING that case's expected
  exit code is permitted, and so is adding new cases or new pairs; changing the VALUE of a
  pre-existing case's expected exit code is FORBIDDEN. Giving the Bash route the harness base's
  target-side test makes four pre-existing cases in `test-bash-write-guard.py` need the permitted
  edit — T-03 names all four by case name and fixes their direction — and flipping any of them to 2
  instead would leave each one passing under the bug it exists to guard. A fifth case is retargeted
  for a different reason and T-03 names it too: it does not turn red, so no diff of expected codes
  sees it, but once `classify` denies its first operand in its own right it stops discriminating on
  the second-segment property its name states; its expected exit stays 2. So the criterion is checked
  by diffing both test files: no pre-existing case's expected exit code changes value. Paired
  refusal, same fixture: a write to `<root>/src/main.py` exits 2 despite the `src/**` grant, so the
  allow is not an allow-all.
  verify: automated      evidence: integration
- SC-08: `check-state.sh` reports a pre-existing out-of-place worktree, fails on it, and never tells
  a session to delete its own cwd. Fixture: `test-check-state.py` creates three temp repositories
  with `git init` and one commit each, run through the file's existing `run(tmp)` helper (which sets
  `CLAUDE_PROJECT_DIR` to the directory given and runs `check-state.sh` there) — repo A with a
  worktree under `.claude/worktrees/wt`, repo B with a worktree at a sibling path outside it, repo C
  with two `git worktree add` entries — a sibling worktree that IS the run's own root and its only
  out-of-place entry, plus a legitimate one under the MAIN checkout's `.claude/worktrees/legit`.
  Every directory used as a run root carries the file's existing `make_fixture` scaffold, without
  which `check-state.sh` exits 1 as not-onboarded before any invariant runs.
  Forbidden: repo B's run prints an `INV-25` line naming the sibling path and exits non-zero, and
  repo C's run prints an `INV-25` line naming its own root path and exits non-zero — the severity is
  the same in both branches. Paired allow, same fixture: repo A prints no `INV-25` line.
  **The base-discriminating paired allow, same fixture: no `INV-25` line in repo C's output names
  `<repoC>/.claude/worktrees/legit`** — scoped by path, not by run, because repo C legitimately
  prints one `INV-25` line for its own root. This is the half that pins the legitimate location to
  the MAIN checkout rather than the session root: with the base taken from the session root, that
  correct worktree is flagged and handed `git worktree remove`. Repo A cannot detect it — there the
  run root and the main checkout are the same directory and both bases agree.
  **The remedy wording is asserted, both directions, on the single `INV-25` line naming repo C's own
  root path** — not on the whole captured run, which would redden correct code the moment any other
  invariant printed the string: that line contains `.claude/worktrees`, and it does NOT contain
  `git worktree remove`, because that command succeeds at exit 0 from inside the tree it removes
  (measured), so printing it to a session standing in that tree is an instruction to delete its own
  cwd. Paired positive for the branch, same fixture: repo B's `INV-25` line DOES contain
  `git worktree remove` — the session is not standing in that tree, so removal guidance is correct
  there, and without this half the negative is satisfiable by stripping removal guidance everywhere.
  verify: automated      evidence: integration
- SC-09 — **AMENDED 2026-08-12 by the operator, after the goal-check. The original text is kept
  below it, struck, because a criterion that quietly changes shape is how a goal-check stops
  meaning anything.**

  **As amended:** this environment holds no out-of-place worktree, and the removal is accounted
  for. Evidence: `notes/worktree-removal-receipt-2026-08-12.md`, plus T-06's verify clause, which
  asserts that `git worktree list` names only the main checkout, that `archive/worktree-r6`
  preserves `52d8334`, and that the receipt itself carries the tokens `LATE`, `archive/worktree-r6`
  and *sweep*.
  verify: inspection

  **Why it was amended rather than failed or quietly passed.** The original named two capture
  files that were never created, and could not be: the removal happened outside T-06 during the
  FEAT-13 close-out, so the before-capture was never taken and cannot be reconstructed without
  falsifying the record — and SC-09's own paired negative, the FEAT-13 worktree still appearing in
  the after-capture, was destroyed by that same close-out. `git log --all` confirms neither file
  was ever committed on any branch. **What is gone is proof the prune was TARGETED; what survives
  is evidence the END STATE is correct**, and the receipt says so on its face rather than claiming
  the stronger thing.

  ~~Original: This environment holds no out-of-place worktree, and the legitimate one survived.
  Evidence: `notes/worktree-list-before.md` and `notes/worktree-list-after.md`; the after-capture
  lists only the main checkout and paths under `.claude/worktrees/`. Paired negative: the FEAT-13
  worktree is still listed in the after-capture, and `git tag --list` contains the recovery tag for
  the removed worktree's commit `52d8334`, which is not an ancestor of `main`.~~
- SC-10: An unimportable shared module fails CLOSED rather than turning both guards off. Fixture:
  an isolated `bin/` copy carrying `check-domain.sh`, `bash-write-guard.sh` and `harness_yaml.py`
  but NOT `harness_boundary.py`, run against a root whose manifest is PRESENT. Forbidden: a governed
  write exits 2 on both routes, with a verdict naming the missing module. Paired allow, same
  isolated copy with the manifest ABSENT: the DEC-101 fail-open still prints `enforcement OFF` and
  exits 0 — the existing case at `test-check-domain.py:163-174`, which must not regress. Without the
  pairing the criterion could be met by a guard that blocks everything.
  verify: automated      evidence: integration

## What the root-side rule deliberately does NOT cover

**In a PyYAML bootstrap-grant session the two routes diverge on the root-side check, and that is a
chosen cost, not an oversight.** The Write route's check sits inside `domain_check`, which
`check-domain.sh:676` calls under `if _run_domain and not _no_parser`, so with the parser missing it
does not run. The Bash route has no `domain_check`; its check sits ahead of that route's own
`if _no_parser` exit and therefore still fires. Three reasons this is the right shape and not the
fail-quiet defect it resembles:

1. The bootstrap grant already skips the domain check in the REAL checkout, so it opens the same
   escape everywhere. A stray-worktree-plus-no-parser session is no worse off than a sanctioned one.
2. The target-side #103 refusal (SC-01) is parser-contingent on the Write route already — it is
   wired into `classify`, which only `domain_check` calls. Matching the root-side check to it is
   consistent with what this plan had already accepted, not a new weakness.
3. The rooted case is a lost-work risk, not an enforcement hole (see Problem). It does not earn a
   second assertion cluster on both routes.

The Bash route is NOT weakened to match. Moving its check below its own `_no_parser` exit to buy
symmetry would degrade a working route to the level of a deliberately weakened one.

## The new single point of failure, and what makes it loud

REQ-05 puts one module — `.claude/skills/harness/bin/harness_boundary.py` — behind both write
routes. If it cannot be imported, an unhandled `ImportError` prints a traceback and the process
exits 1, and **exit 1 is non-blocking** (`check-domain.sh:14`): the write lands, the exit code looks
benign, and enforcement is silently OFF on BOTH routes at once. That is the same failure direction
as #103 itself, installed inside its own fix. CLAUDE.md's PyYAML bootstrap escape does not cover it
— `require_or_bootstrap` runs only after `import harness_yaml` succeeds
(`check-domain.sh:502-510`).

So both governed-path import sites wrap the import and exit 2. Exit 2 is affordable here and cannot
lock the repository out of repairing itself: the import site is already gated on `_run_domain`,
which is `_governed and not _post` (`check-domain.sh:432`, `:450`, `:471`, `:493`), so the main
session never reaches it; `harness-dev-ops` is exempt before the equivalent point on the Bash route
(`bash-write-guard.sh:54-59`); and all five `bin/` surfaces are `main-session-direct` under DEC-174.
SC-10 is what proves it.

## Verification gaps

- `test-check-domain.py` and `test-bash-write-guard.py` match `harness.json`'s `unit` detect glob
  (`.claude/skills/harness/bin/test-*.py`) but live in `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS`,
  so `--kind unit` does NOT execute them. Every SC above marked `automated` — that is all of them
  except SC-09, which is `inspection` — therefore declares `evidence: integration`, whose command
  does run them. Nothing here rests on `--kind unit`. The
  mis-classification itself is out of scope and raised as an open question.
- `component`, `ui`, `eval` and `typecheck` have `cmd: null`. This feature touches none of those
  surfaces; no criterion rests on them.

## Constraints

- `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` and `check-state.sh` are DEC-174
  carve-out files. Every task touching any of them, and the new shared module the rule moves into,
  is `main-session-direct`: ordinary edits, tests run explicitly, a human reading the diff.
- Ruling: an out-of-place worktree is a mistake, not a supported shape. It is REFUSED, never
  resolved onto the globs. Consulting `git worktree list` on the governed-write path was offered
  and declined; the guards read the checkout's own `.git` pointer file instead and invoke no `git`
  subprocess.
- **Known-adjacent, deliberately not tasked.** Two findings sit next to this feature's surface and
  carry no task here; they go to the operator as backlog. (1) Both guard suites sit in
  `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS` despite matching the `unit` detect glob, so
  `--kind unit` never runs them — the same gap the verification note below records. (2) A relative
  operand on the Bash route is resolved against the harness root rather than the agent's working
  directory. Neither is a regression this feature introduces and neither blocks any criterion above.
- Out of scope, per the grilling: changing how `.claude/worktrees/` or `workspace_root/<product>`
  are governed; re-adding `mruangutai/harness` to the fleet; the `Permitted for you:` stderr line;
  `harness.json`'s `github.repo` and the factory's per-repo board (#262 / FEAT-16).
- **File-set collision with FEAT-16.** `.harness/features/FEAT-16-factory-per-repo-board/plan.yaml`
  is live and pending, **and it is being edited concurrently** — its `files:` union read 16 paths,
  then 18, then 17 across today, so any count taken from it is a snapshot. Its scope is fenced
  out of this feature, but its file set is not disjoint: re-measured at the 2026-08-11 re-scope
  against its 17-path union, this plan's union of 11 paths — unchanged by the re-scope — intersects
  it in exactly 3, the same 3 as before —
  `.claude/skills/harness/bin/test-check-domain.py`, `docs/harness/DECISIONS.md` and
  `docs/harness/DECISIONS-INDEX.md`, the same three M-3 predicted. Whichever feature lands second
  rebases onto the other's edits in those three files, and the intersection should be re-measured at
  signature rather than trusted from here.

## Approval

status: approved
approved-by: operator
date: 2026-08-11
