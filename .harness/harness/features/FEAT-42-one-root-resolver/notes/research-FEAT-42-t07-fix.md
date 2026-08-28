# T-07 fixed to match the amended SC-01 — FEAT-42 — 2026-08-26

**All three edits are on disk. SC-01 and the dispatch agree, so no BLOCKED on that axis.** One new
finding, measured, needs the orchestrator: `bash-write-guard.sh` denies T-07's mutation proof — and
denied the version already in the plan, before I touched it.

## The three edits (`plan.yaml`, T-07 only)

1. **`depends_on`** now ends `..., T-18, T-20`. `T-20.depends_on` is `[T-10, T-11, T-14, T-16, T-17]`,
   re-read after the edit — no cycle.
2. **`intent`, absence half** — scan root is now every tracked source file in the repository via
   `git -C ROOT ls-files`, dropping basenames starting `test-`, excluding `harness_boundary.py` and
   excluding every `*.md`. Baseline **21 occurrences across 17 files at sha 3952814**. The
   DO-NOT-ENUMERATE-A-FILE-LIST rule survives with its justification extended by "and so that a site
   outside `.claude/skills/harness/bin/` is caught at all". The comment-the-exclusions instruction
   survives, now covering three exclusions. The DEC-169 presence half is byte-unchanged and still
   scoped to `harness_boundary.py` and its importers.
3. **Mutation target moved out of the old scan root** — see below. The intent's closing paragraph,
   which described the old target by name, was updated with it; leaving it would have contradicted
   `verify:` and tripped the member's verbatim cross-check.

Cross-checked against `BRIEF.md:77-91`: exclusions and the 21/17 baseline at sha `3952814` match the
dispatch word for word.

## The mutation target: `docs/invalid-states-audit.html`

Against the five hard constraints: tracked (`git ls-files docs/` returns it), basename does not start
`test-`, not `harness_boundary.py`, not `*.md`, and not under `.claude/skills/harness/bin/`.

Safe to append-and-restore: it is a static 45KB audit page, referenced by **zero** `.py/.sh/.yaml/
.yml/.json` files in the tree (grep, worktree HEAD), so no hook, gate or test loads it — a momentary
mutation cannot break the run that observes it. It currently contains 0 occurrences of
`HARNESS_PROJECT_DIR`, so the pre-mutation green run is real. It is also the only tracked non-`.md`
file under `docs/`. The mutant is an HTML comment plus one inert line; restore is `cp` from backup.

The two load-bearing lines, verbatim:

```
printf '\n<!-- mutant -->\nroot="${HARNESS_PROJECT_DIR:-x}"\n' >> docs/invalid-states-audit.html
grep -q "invalid-states-audit.html" /tmp/f42-t07-mut.txt || { echo "failed for the wrong reason"; exit 1; }
```

All four discipline parts survive: mutation-applied assertion, failure-names-the-file grep (updated
to the new filename), `cp` restore from `/tmp/f42-t07-restore.html`, re-run green. `verify:` is still
a `|` literal block and `bash -n` parses it clean.

**Why this discriminates and the old one did not:** planted outside `.claude/skills/harness/bin/`,
the mutant is invisible to the directory-scoped scan root and visible only to the repo-wide one. The
old `$B/gh-close-gate.sh` target went red under both, so it could not prove the widening.

## Open question — the write guard denies this proof, and already denied the old one

Measured against `.claude/skills/harness/bin/bash-write-guard.sh` with
`agent_type=harness-backend-dev`, `CLAUDE_PROJECT_DIR` = the main checkout:

| redirect target | verdict |
|---|---|
| `docs/invalid-states-audit.html` (new) | **BLOCKED** — outside your domain |
| `$B/gh-close-gate.sh` (the version already in the plan) | **BLOCKED** — takes `$B/...` literally |
| absolute path under `.claude/worktrees/.../docs/...` | **allowed** (DEC-153 carve-out, guard :687) |

Root cause: the guard resolves a relative Bash path against `root` (:232, `CLAUDE_PROJECT_DIR`), not
the agent's cwd, so the `^\.claude/worktrees/` perturbation carve-out at :687 never fires for a
relative path or an unexpanded variable — even though DEC-153 sanctions exactly this proof in a
worktree. It is not a defect my edit introduced; the shipped form fails identically. A portable
literal absolute path cannot be written into a plan, and reaching for a form the guard cannot parse
would be evasion (DEC-151), so I did neither. Resolution is the orchestrator's: route T-07
main-session-direct like its eleven enforcement-layer siblings, or fix the guard's cwd resolution.

## Untouched, confirmed after editing

20 tasks; 14 `main-session-direct` / 6 `team`; `T-07.status: pending`; `approval.status: pending`
with `approved_by: null`; D-05 and D-12 as they were. `check-plan-routes.py` exits 0 (its 12
DEVIATION lines are the pre-existing DEC-174 lanes).
