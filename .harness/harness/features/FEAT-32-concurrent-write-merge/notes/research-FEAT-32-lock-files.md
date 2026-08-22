# The permanent lock file dirties the tree — real, NEEDS A SIGNATURE, one line fixes it

**Verdict: needs_signature.** The harm is real and this feature creates it. The fix is one
`.gitignore` line, `.harness/**/*.lock`, carried by a widened T-11. All six measurements HELD; one
carried a wrong sub-count and one enforcer turned out narrower than the folklore.

Observed at `4673d0b` in the FEAT-32 worktree.

## The six, individually

1. **HELD, with a correction.** No rule matches a `.lock`. But the file carries **10** rules, not
   seven (`.gitignore:2,7,13,17,21,24,25,26,29,34`).
2. **HELD.** `git check-ignore -v` exits **1 (NOT IGNORED)** for all four lock paths: a feature
   `plan.yaml.lock`, `observations/harness-pm.md.lock`, `.harness/expertise/harness-pm.md.lock`,
   `.harness/.inflight-claims.json.lock`. Control: a path under `runs/` exits 0 on `.gitignore:7`,
   so the rule works and simply does not reach these.
3. **HELD.** `.harness/expertise/` is tracked and uncovered (same check, exit 1).
4. **HELD, and wider than stated.** T-11 `files:` is `.gitignore` alone, its intent ends "Change
   nothing else in the file", and its `verify:` greps `git status --porcelain
   .harness/.inflight-claims.json` — path-scoped, so the sibling `.lock` is invisible and T-11 can
   pass green while dirtying the tree. Four merge targets acquire locks, not one: T-03 `plan.yaml`,
   T-04 observations, T-05 expertise, T-06 the registry.
5. **HELD.** `expertise-merge.py:290` does `os.remove(lock_path)` in a `finally:` today, so no lock
   persists anywhere at HEAD. T-05 rewires it onto `harness_merge.py` (`:121` `path + ".lock"`,
   `:71` "the lock FILE is deliberately never removed (D-02)"), which is what introduces it.
6. **HELD.** Every merge-tool `verify:` runs in a `mktemp -d` (T-02..T-06, T-08, T-14). The five
   verifies that touch the real tree (T-01, T-10, T-13, T-15, T-17) invoke no merge tool. Real lock
   files appear only in live operation — exactly the blind spot.

## The dirty-tree halt: real for teardown, NOT for review

The enforcer is `feature-worktree.py cmd_remove` GATE 2, `:216-227`: plain `git status --porcelain`
in the worktree, **no whitelist**, every line printed as `WOULD DISCARD`, `sys.exit(4)`, and no force
flag (`REFUSE_ON_DIRTY` is a module constant, `:39-40`; SPEC.md:2308).

**It does read the distinction, in our favour.** `git status --porcelain` lists untracked (`??`) and
omits ignored — probed in a scratch repo: an untracked `sub/a.md.lock` yields `?? sub/`. So an
untracked lock trips GATE 2 and an ignored one does not. A `.gitignore` line is a complete fix.

**Partial collapse of the folklore:** the other two dirty-tree halts exempt exactly these paths.
`harness-review/SKILL.md:38` stops only on "changes outside `.harness/**`", and SPEC.md:2364 defines
the §8.6 whitelist as "`.harness/**` plus any path you have staged". `check-state.sh` contains no
dirty-tree check at all (grep -i dirty: no match). So the consequence is narrower than "the next team
run deadlocks": **ship-time worktree teardown refuses, with no force flag**, plus the standing risk
that a `git add -A` commits local flock state.

## Minimal fix, and what I rejected

**Recommend (c): one line, `.harness/**/*.lock`.** Verified in a scratch repo to match all four paths
including the one directly under `.harness/`, and to leave `poetry.lock` untouched.

- **(a) blanket `*.lock` — rejected.** Nothing is untracked by it here (`git ls-files | grep -c
  '\.lock$'` is **0**), so `.gitignore:31-34`'s objection does not bite in this repo. It bites
  downstream: `templates/gitignore.snippet` installs into consumer repos, where `*.lock` silently
  ignores `Gemfile.lock`, `poetry.lock`, `Cargo.lock`.
- **(b) four specific rules — rejected.** Precise, matches the narrow-rule convention, but a fifth
  merge target reintroduces the gap silently. The class is stable; enumerate the class.
- **(d) relocate the lock outside the repo — rejected on price, not on merit.** It is the only option
  that fixes repos whose `.gitignore` the harness does not control. Cost, honestly: re-opens signed
  D-02, discards T-02's built core and its three receipts, and needs a collision-free naming scheme
  (two checkouts of one repo must not collide; two files must not collide). A lock under `/tmp` can
  also be reaped by a tmp cleaner while a holder sleeps — a fresh acquirer then creates a new file
  and both hold, which is the create-and-delete race D-02 exists to avoid. Cost of my
  recommendation instead: the guarantee is per-repo and can be edited away.

## Carrier: widen T-11

A signature is needed either way, so prefer the task that already owns `.gitignore`,
`main-session-direct`, `change_type: config`. A second task writing one file is the hazard this
feature is about. T-11's `verify:` must also drop its path scope, or it stays green while dirty.

Not backlog: this feature's own code creates the file, and shipping it means the next teardown
refuses with no force flag.

## SCs

**None can fail.** Every automated SC runs in a temp dir or reads suite counts; a stray untracked
lock changes neither. **None passes falsely either** — but SC-13 is the only place this could have
been caught, and its six enumerated residues do not include it. **Conditional:** if the fix is NOT
carried, SC-13 needs a seventh statement naming the residue, which is itself signed-text change.

## Open questions

- **Q1 (operator):** approve the widened T-11 wording below. Blocking the fix, not the feature.
