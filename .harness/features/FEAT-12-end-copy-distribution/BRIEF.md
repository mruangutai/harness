# BRIEF — FEAT-12 End copy-based distribution

Issue: mruangutai/harness#203. Grilling: `.harness/notes/grilling-end-distribution-2026-08-10.md`.

## Problem

Harness tooling exists in three places at once, and the copies rot silently. `deploy.sh` pushes 21
skill directories and 8 slash commands out of this repo into a global install *and* into every
enrolled project, plus 16 agent files into the global install **only** — `deploy.sh:18` states
"AGENTS GO GLOBAL ONLY (DEC-113)" and the copy loop at `deploy.sh:232` writes them to
`~/.claude/agents/` and nowhere else. That asymmetry is load-bearing for what follows: the 16 agent
files sitting in `kaya-ai` were never put there by a project copy and were never committed.
On 2026-08-10 the global copy was found to be **stale, not merely
redundant**: `harness-wayfinding` and `harness-grilling` were last written on Jul 31 while this repo
rewrote them on 2026-08-09 in `c5597be`. The global text lacked the one-door-per-job framing for ten
days and nobody noticed until someone diffed it. `kaya-ai` still carries the same frozen fork —
55 skill files and 8 command files tracked on `master`, 16 untracked agent files, and a further
153 skill files tracked on three of its feature branches — and `check-state.sh`,
`validate-digest.py` and every other gate run in kaya run **from that copy, not from here**. A gate
that is a stale fork of the real gate is worse than no gate: it reports green about rules that no
longer exist.

The global install was already deleted by hand on 2026-08-10 ahead of this work (backups at
`~/.harness/global-harness-*-backup-2026-08-10.tgz`). What is left is the machinery that would
recreate it, the copy still sitting in kaya, and roughly forty live references telling humans and
agents to use a distribution step.

## Goal

End copy-based distribution. `deploy.sh`, its slash command and its registry are deleted; the copy
of the tooling in kaya-ai's own three tooling directories — the ones a session opened at that
repo's root reads from — is removed, and the removal is committed to `master`; kaya-ai is onboarded
to `fleet.yaml` so the factory can still reach it by name; and no live instruction, docstring or
user-facing message in this repo points at a distribution step any more. After this, a product repo
reaches harness tooling by being checked out by the factory, not by holding a copy of it. The only
copy this feature leaves behind is branch-local rather than repo-level: three of kaya-ai's six git
worktrees still carry the tooling on their own feature branches, and each of the three loses it the
next time that branch takes `master` (see `## Constraints`). No copy survives on `master`, which is
what the factory clones.

## Requirements

- REQ-01: This repository contains no mechanism that copies harness tooling anywhere else.
- REQ-02: `~/.harness/registry.json` and its writer are both gone, and nothing that reads project
  roots regresses as a result.
- REQ-03: `kaya-ai`'s three top-level tooling directories hold no harness tooling — no `harness*`
  entries under `.claude/skills/`, no `harness*.md` under `.claude/commands/`, no `harness-*.md`
  under `.claude/agents/` — so a session opened at `kaya-ai`'s root has no harness capability,
  which is the intended end state. **The three directories are the scope, deliberately.** Copies
  inside three of `kaya-ai`'s six git worktrees under `.claude/worktrees/` are a declared deferral
  (see `## Constraints`) — a **transient** one, because those copies are tracked on their own
  feature branches and each branch drops them the next time it takes `master`. This requirement is
  worded to match what the work delivers rather than to promise past it.
- REQ-04: `kaya-ai`'s own accumulated state under its `.harness/` is untouched by this work, in
  full, including the entries the operator ruling did not name.
- REQ-05: `kaya-ai` is reachable to the factory by name once the registry is gone.
- REQ-06: A factory checkout of `kaya-ai` runs without a dangling-hook error caused by this removal.
- REQ-07: No live instruction, docstring, comment or user-facing string in this repo directs anyone
  to a distribution step that no longer exists.
- REQ-08: The decision record states that copy-based distribution is retired, and the strike leaves
  no surviving citation of the struck ruling in the design docs. Corrected at `835b297`: the
  original wording rested the second half on the propagation checker, which no longer exists. Both
  halves are asserted by T-14's own `verify:` in `plan.yaml` (`DEC-12` struck, exactly one
  surviving `DEC-113` section retaining its override-precedence rule, no `DEC-12` citation left in
  `DECISIONS.md`, `DECISIONS-INDEX.md`, `BUILD.md` or `SPEC.md`, and the matching index rows), with
  that same `verify:`'s first clause sweeping the four falsified phrases out of `docs/`,
  `README.md`, `.harness/README.md`, `.claude/skills` and `.claude/commands`. T-13 case 4
  re-asserts the strike half independently under SC-08.

## Success Criteria

- SC-01: `.claude/skills/harness/bin/deploy.sh` and `.claude/commands/harness-deploy.md` do not
  exist, and the full test suite still reports ALL PASS — the deletion breaks nothing that ran
  before it.
  verify: automated      evidence: unit
- SC-02: `test-check-plan-routes.py` still passes every case after the registry is deleted —
  including case 20, whose `$HOME`-shaped trap builds its **own** synthetic `registry.json` in a
  temp directory and therefore must not have depended on the real one. That script is in
  `INTEGRATION_SCRIPTS`, so `run-unit-tests.sh --kind integration` is the command that runs it.
  verify: automated      evidence: integration
- SC-02b: `~/.harness/registry.json` does not exist, while the two `global-harness-*-backup-2026-08-10.tgz`
  archives beside it do. No test kind may assert this — a test that reads `$HOME` is machine-dependent
  and would be a worse artifact than the claim it proves — so it rests on T-09's verify output as the
  cited evidence.
  verify: inspection
- SC-03: `.harness/factory/fleet.yaml` loads with `safe_load` and its `repos:` list contains
  `mruangutai/kaya-ai` with `default_branch: master` alongside `mruangutai/harness`, and
  `factory_config.py` accepts the file without raising.
  verify: automated      evidence: unit
- SC-04: `kaya-ai` at the state this feature leaves it in contains zero `harness*` entries under
  `.claude/skills/`, zero `harness*.md` under `.claude/commands/`, and zero `harness-*.md` under
  `.claude/agents/` — and still contains `.claude/commands/review-team.md`, which is not harness
  tooling and must survive. The presence half is not optional: an all-absent result would also be
  produced by deleting the wrong directory outright, so all three parent directories must still
  exist. **The three clauses are graded against two different things, and this is deliberate.** The
  skills and commands clauses are graded against `origin/master`, because those files are tracked
  and their removal is a commit (T-05's verify). **The agents clause is graded against kaya's
  working tree only** — zero `harness-*.md` are tracked on `master`, so their deletion produces no
  commit content and the remote never carried them; grading it against the remote would pass
  vacuously on a target that never existed. Its evidence is the pair T-02 produces: the recorded
  pre-deletion count in `notes/kaya-agents-count-before.txt`, which must be greater than zero, and
  the post-deletion count of zero.
  verify: inspection
- SC-05: `kaya-ai/.harness/` is byte-identical across the removal. The same seven top-level entries
  (`artifacts`, `codebase`, `expertise`, `features`, `harness.json`, `notes`, `team-config.yaml`),
  the same total file count, and the same per-file sha256, captured before the first deletion and
  re-captured after the last one, differ in nothing.
  verify: inspection
- SC-06: A fresh factory checkout of `kaya-ai` at `master` executes a Bash call, a Write and a Task
  spawn with no missing-hook error. This is the criterion that proves the fleet entry ships live
  rather than inert.
  verify: uat
- SC-07: Across this repo's live surfaces — every file except `docs/harness/DECISIONS.md`,
  `.harness/logs/**`, `.harness/notes/**` and `.harness/features/**`, which are history and stay
  true as written — the tokens `harness-deploy`, `deploy.sh`, `harness-registry` and
  `registry.json` appear only at
  sites on an explicit allow-list, and that allow-list is named in the test rather than derived from
  what happens to be there. The search pattern is deliberately wider than the sweep that produced
  the task list, so a site nobody surveyed still fails.
  verify: automated      evidence: unit
- SC-08: `DEC-12` is struck from `docs/harness/DECISIONS.md` in full, `DEC-113` retains only its
  override-precedence ruling, no citation of `DEC-12` survives anywhere in `docs/`, and
  `DECISIONS-INDEX.md` carries a `DEC-113` row and no `DEC-12` row. The presence half is what keeps the
  strike from overreaching: `DEC-113`'s surviving section must still state that project-owned
  overrides resolve first, because `harness-team/SKILL.md` obeys that rule.
  verify: automated      evidence: unit
- SC-09: `docs/harness/SPEC.md` no longer carries a section presenting distribution as a live
  operation, and the text that replaces it names the factory checkout as the way a product repo
  reaches harness tooling. Anchored on content, not line number: the section currently opens with
  the heading text containing the words Distribution and `/harness-init`.
  verify: inspection
- SC-10: `upgrade-config.py` emits no message instructing the user to run a distribution step, and
  `test-upgrade-config.py` asserts the replacement wording rather than merely not asserting the old
  wording.
  verify: automated      evidence: integration

## Verification gaps

- No test kind in this repo can observe another repository. `component`, `ui`, `eval` and
  `typecheck` all have `cmd: null`, and none of the four would help here anyway: nothing in
  `test_kinds` reaches outside `CLAUDE_PROJECT_DIR`. Every claim about `kaya-ai` — SC-04, SC-05,
  SC-06 — therefore rests on inspection of a captured manifest or on the operator running it,
  never on a runner. What carries SC-05 is the before/after sha256 manifest, which is a real
  artifact a reviewer can re-diff; what carries SC-06 is the operator.
- `functional` is `excluded` under DEC-187 and is not used here.

## Constraints

- **Out of scope, and this is a ruling rather than an oversight: `.claude/skills/harness/templates/`
  is NOT deleted.** Issue #203's first comment widened scope to deleting those 14 files. The
  grilling did not settle that widening, so it does not enter this feature. The directory stays.
  **What this feature does edit inside it is three sites in two files**, all of them sweep
  targets in T-11: one *sentence* in `templates/README.md` (the pushed-to-every-project
  clause), and two trailing *comments* in `templates/team-config.yaml`
  (the `teams` and `team_overrides` entries, whose `DEC-113` citation and resolved-first ruling
  both survive). Nothing else in `templates/` is touched.
- Out of scope: anything `harness-init` does beyond neutralising its distribution references. The
  rewrite of that skill is #206, which lands after this.
- Out of scope: moving `kaya-ai`'s `expertise/`, `codebase/`, `features/`, `artifacts/` or `notes/`
  anywhere. Deferred by operator ruling; the central-store migration is separate work.
- Out of scope: `factory_gh.py` and `.harness/features/FEAT-11-graphql-field-resolve/`, which are
  being planned concurrently against issue #211.
- Untouchable under DEC-174: `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py` and
  `check-state.sh` — **four, not five.** `check-docs.sh` was the fifth; it no longer exists.
  Issue #202 deleted it under DEC-188 and its absence from the tree is confirmed at `687fd3e`.
  It is not recreated by this feature. All four survivors were grepped for `deploy` and `registry`
  at `c1d1617` and every hit is incidental prose, so no enforcement-file edit is implied by this
  work. That is what keeps this feature inside a team run.
- `.claude/commands/review-team.md` in `kaya-ai` is not harness tooling and is not deleted.
- **Out of scope, and declared rather than omitted: `kaya-ai`'s `.claude/settings.json.harness-bak`
  stays.** It is tracked on `origin/master`, it is `merge-settings.py`'s backup of the settings
  file, and it registers six harness scripts — so after this feature `master` still ships one
  tracked file naming scripts that no longer exist. It is left because it is inert and because it
  is not harness tooling: `merge-settings.py` only ever *writes* it (`merge-settings.py:326`,
  `shutil.copyfile(path, path + ".harness-bak")`) and never reads it back, Claude Code does not
  load a `.harness-bak` file, so it cannot produce the dangling-hook failure SC-06 tests for; and
  `merge-settings.py:325` says the backup exists because harness is editing a file *the project
  owns and harness does not*. Bringing it in would need a requirement this brief does not have.
  Recorded as `D-06` in `plan.yaml`, with the reversal cost: one path on T-03, one entry on T-05's
  pathspec.
- **Out of scope and DEFERRED — but transient, not permanent: the harness copies inside `kaya-ai`'s
  git worktrees.** Measured on 2026-08-10 against kaya `master` at `b6aaab9`, all six worktrees
  enumerated rather than sampled. **Three of the six carry a copy** — `333-env-test`
  (`feat/333-env-test`, tip `ab92578`, 55 files), `feat02-statements` (`feat/120-statements-page`,
  tip `d09289c`, 48 files) and `feat03-live-review-loop` (`feat/48-live-review-loop`, tip `c7b2208`,
  50 files): 153 files across 56 `.claude/skills/harness*` directories. The other three worktree
  branches do not contain the path at all. **An earlier draft of this bullet called the copies
  "untracked and gitignored". That was wrong and was never measured.** Every one of the 153 is
  **tracked content of its own branch** (`git -C <worktree> ls-files '.claude/skills/harness*'`).
  What is gitignored is only the container, in the *main* tree: `.gitignore:23` lists
  `.claude/worktrees/`, which is why the copies never appear in kaya's root `git status` and why
  `git ls-files '.claude/worktrees*'` on `master` returns zero — **a factory clone of `master`
  carries no worktrees at all**, so this deferral cannot reach SC-06.
  **The factory cannot reach the residue either, and that is measured rather than assumed.** After
  T-05 the two diverged branches would hold 48 and 50 harness skill files with no upstream — a
  stale fork of the gates, which the Problem section calls worse than no gate. But
  `factory_workspace.py:118` fixes the working branch to `factory/issue-<N>` and `:103` cuts it
  from `origin/<default_branch>`; the only other checkout targets are `default_branch` itself
  (`:129-130`) and a pre-existing `factory/issue-<N>` ref, itself cut the same way. No code path
  checks out a `feat/*` branch, so no factory run can ever execute against those stale copies.
  **The consequence for the operator: the deferral clears itself.** No branch has modified those
  paths since its merge-base (branch-side diff of `.claude/skills/harness*` from merge-base is 0
  files for all three), so T-05's deletion commit merges cleanly. The next time each of the three
  branches merges or rebases `master`, the deletion applies and its copy goes — no conflict, no
  further work. Until then a session opened *inside* one of those three worktrees still finds
  harness tooling, which is narrower than REQ-03's "a session opened directly in `kaya-ai` has no
  harness capability". That is the intended end state arriving late per branch, not a regression,
  and it is why REQ-03 is scoped to the three top-level directories. Nothing in this feature reaches
  the worktrees: they are outside all three of T-02's globs and SC-04 is worded against
  `.claude/skills/`, which they are not under.
- **Pre-existing red suite, not this feature's.** Observed at `c4fea5d` on 2026-08-10 with the
  operator's #202 change staged: `run-unit-tests.sh --kind unit` exits 0, but `--kind integration`
  exits 1 on `test-gen-decisions-index.py`, with two failures —
  `test_row_per_distinct_dec_matches_authority` (expected one fence-guarded `DEC-83` duplicate,
  found none, because `DEC-83` was struck) and `test_committed_index_is_complete_and_within_budget`
  (`DEC-188`'s row summary is 37 words against a 30-word cap). Separately,
  `gen-decisions-index.py --stdout` emits nothing and reports `ORPHAN: DEC-104`. All three are the
  in-flight #202 strike, not FEAT-12. Three task verifies here call `run-unit-tests.sh` and cannot
  pass until #202's index regeneration lands. Repairing them is #202's work and is out of scope.
  **SUPERSEDED at `835b297`.** The observation above is what was measured at `c4fea5d` and stays on
  the record, but it no longer describes the tree. #202 landed as
  `835b297 [harness:human] #202: the propagation checker is struck, not deprecated`, and at that
  commit the operator re-measured: `run-unit-tests.sh` exits 0 with 85 distinct test files passing
  and none failing; `test-gen-decisions-index.py` reports all 8 cases `ok`, including the two
  recorded failing above; and `gen-decisions-index.py --stdout` emits the index normally, starting
  `<!-- index-contract v1 -->`, with no ORPHAN. **There is no red-suite dependency left. Nothing in
  this feature is waiting on #202.**
- **The propagation checker is gone, and the plan is written around that.** At `c1d1617` the
  mechanism was a `<!-- stale: ... -->` marker declared in the invalidated decision, enforced by
  `check-docs.sh` as `check-state.sh`'s INV-10. Issue #202 landed during this planning run:
  `check-docs.sh` is **deleted, committed at `835b297`** (`[harness:human] #202: the propagation
  checker is struck, not deprecated`), and its absence is re-confirmed at `687fd3e`. It is not
  staged and not pending a possible revert. **DEC-188 is the standing rule** and states it in the
  record's own words: a decision the tree flatly contradicts is **struck from the record and
  removed from every gate** — not marked stale, not amended, not left standing with a marker
  beside it. DEC-188 also records what was already done under it: `check-docs.sh` deleted, the
  INV-10 block out of `check-state.sh`, and the 66 stale-wording markers and 14 escape comments
  gone from the live docs. `DEC-103`, `DEC-104`, `DEC-83` and `DEC-181` were each deleted
  outright. Nothing in this feature runs a propagation checker and nothing substitutes for one.
  This feature therefore strikes rather
  than marks, and nothing mechanical now checks that a falsified doc statement was actually
  removed. What replaces it is two checks, not one, and they cover different things: T-14's
  `verify:` sweeps the four falsified **phrases** out of `docs/`, `README.md`,
  `.harness/README.md`, `.claude/skills` and `.claude/commands`, and SC-07's test (T-13 case 2)
  sweeps the **tokens** `harness-deploy|deploy\.sh|harness-registry|registry\.json` across
  every tracked file bar four historical trees. Neither one subsumes the other.
- **Five items below, in two groups — corrected at `835b297`, where the earlier "four" miscounted
  its own list.** They are quoted so a reviewer can re-run the sweep. The first four are prose
  phrases and are covered **only** by T-14's verify, over the five path roots
  named above. The fifth, `~/.gsd/harness-registry.json`, is not a prose phrase but a token, and is
  covered by SC-07 / T-13 case 2's `harness-registry` pattern instead. The five strings below were
  previously each followed by an inline ok-stale escape comment; those escapes were
  `check-docs.sh`'s syntax, the checker is deleted, and nothing reads them, so they are removed
  rather than left as dead syntax in a document the operator signs. The strings themselves are
  quoted verbatim on purpose, so a reviewer can re-run the sweep from this list. This file is safe
  to quote them in: it lives under `.harness/features/`, which is on T-13 case 2's exclusion list
  and outside T-14's verify pathspec, so the quotations cannot redden either sweep — checked, not
  assumed.
  `Enroll = deploy + init`
  `never touches project state`
  `distributes the tool and never`
  `replaced wholesale on every`
  `~/.gsd/harness-registry.json`

## Settled rulings

- **Q1 — SETTLED by the operator on 2026-08-10: commit and push, path-scoped.** The question was
  whether removing `kaya-ai`'s copy becomes a commit pushed to `kaya-ai`'s `master` or stops at that
  machine's working tree. 55 skill files and all 8 command files are tracked on `master`, and
  `factory_workspace.py:125` materialises a workspace by `git clone https://github.com/<repo>.git` —
  from the **remote**, not from the local checkout — so a working-tree-only deletion is undone by
  the very next factory checkout and the goal is never reached. **The ruling authorizes a push to
  `mruangutai/kaya-ai` `master` for the deletion commit only.** It authorizes nothing in this
  repository: "do not push, do not open a PR" was ruled for **this** repo, still binds here in full,
  and was silent on kaya. Path-scoping is part of the ruling, not a style note — kaya's working tree
  carries 63 uncommitted entries that are not this feature's, so staging is by explicit pathspec and
  never `-a`, `-A` or `git add .`. `T-05` is unconditional as a result.
- **The agent files and the local skill modifications, measured rather than assumed.** An earlier
  draft of Q1 claimed "the 16 agent files and the 21 uncommitted skill modifications are untracked
  and are unaffected either way." **The second half was false.** Measured in `kaya-ai` on
  2026-08-10: 34 of the modified files under `.claude/skills/harness*` and `.claude/commands/harness*`
  are **tracked**, and committing their deletion discards those local modifications permanently.
  The conclusion is unchanged but the reason is different: **nothing unique is lost because all 34
  are reproducible from this repository** — 28 are byte-identical to this repo's copy at `365a8a9`,
  and the remaining 6 are present in this repo's object database, confirmed by hashing kaya's copy
  and running `git cat-file -e` on the hash here. That is also the authorization for `git rm -f`,
  which `T-02` needs because `git rm` refuses a locally-modified tracked file without it. The agent
  files genuinely are untracked — zero of them are on `master` — so their deletion produces no
  commit content and the remote never carried them.

## Open questions

- None blocking. The two declared deferrals — `.claude/settings.json.harness-bak` and `kaya-ai`'s
  worktree copies — are recorded in `## Constraints` above, where they are out-of-scope rulings the
  operator signs rather than questions awaiting an answer. Both are measured: the first is inert
  (written, never read back), the second is transient (tracked per branch, cleared when that branch
  next takes `master`).

## Approval

status: approved
approved_by: operator
date: 2026-08-10

**Ruling that rides with this signature — D-06 is REVERSED.** The plan deferred
`.claude/settings.json.harness-bak` because it is inert: `merge-settings.py` writes it and never
reads it back. Remove it anyway. It is TRACKED on kaya's `origin/master` and names six harness
scripts this feature deletes, so leaving it means kaya's master permanently carries a tracked file
pointing at paths that do not exist. The plan states the cost itself: one path on T-03, one entry on
T-05's pathspec. Fold it into those tasks — it is not a new task.

**Ratified by this signature, not re-asked:** REQ-03's narrowing to kaya's three top-level tooling
directories (the worktree copies are gitignored, untracked on master, and `git log master..<branch>`
returns 0 commits on those paths for all three, so they clear on the next merge rather than
conflicting); and the corrected cost of the push — 34 TRACKED files have their local modifications
permanently discarded by the deletion commit, all 34 reproducible from this repo.

