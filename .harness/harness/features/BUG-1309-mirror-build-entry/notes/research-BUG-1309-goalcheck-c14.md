# Goal-check at review_sha c8b23e03 — BUG-1309-mirror-build-entry (cycle 14)

**BLUF. SC-04 clause (a) is `unmet` — a BEHAVIOUR defect, not a coverage gap — so the feature does
not deliver at this pin. Everything else is met: SC-01..SC-03, SC-04b/c/d, SC-05..SC-09 `met`,
SC-10 `pending-user`.** The R-2 fix in `ac2bc0bb` rewrote `git_merge` into an ordered walk that
returns `rest[index+1]` as the branch (`merge-gate.py:60` at the pin) and gates value-taking globals
through a **closed 7-name set** (`:47-48`). Two escape classes follow, both measured, both a silent
allow with no deny, no stderr, no audit trace:

- **E1 (regression).** Any option between `merge` and the ref resolves the branch to the option
  token: `git merge --no-ff X`, `--squash X`, `--no-edit X`, `--ff-only origin/X`, `-m 'msg' X`, and
  `git -C /repo merge --no-ff X`. The pre-change parser at `de04d841` **denied** `--no-ff`/`--squash`
  (it stripped dash-tokens); the fix traded those for `-C`.
- **E2 (closed list).** `git --exec-path /usr/lib/git-core merge X` misaligns the subcommand walk and
  allows — and `--exec-path <p>` is named verbatim in the signed T-05 step 2 as an example of the
  class the plan forbade implementing as a list (`plan.yaml:1029-1033` at the pin, "VALUE-TAKING
  GLOBALS ARE A CLASS, NOT A CLOSED LIST").

Evidence: throwaway probes `/tmp/mgprobe/probe.py`, `/tmp/mgprobe/probe2.py` — synthetic PreToolUse
payloads piped into the pin's own `merge-gate.py` over a `/tmp` ROOT. Nothing written in-repo, HEAD
unmoved.

## Clause (a) — merge invocation forms an operator types

Fixture throughout: non-era feature, `github.build_entry` absent, sync true, repo pinned → the
criterion requires DENY for every form.

| # | Form | Reaches deny | Token walk that decides it |
|---|---|---|---|
| 1 | `git merge X` | YES | `rest[0]=="merge"` → branch `X` (`merge-gate.py:58-60`) |
| 2 | `git -C /repo merge X` | YES | `-C` in `takes_value` → `index+=2` (`:52-54`) |
| 3 | `git -c core.editor=true merge X` | YES | same arm |
| 4 | `git --work-tree /wt merge X` | YES | same arm |
| 5 | `git -C/repo merge X` (attached) | YES | `startswith("-")` skip-one (`:55-57`) |
| 6 | `git --git-dir=/x/.git merge X` | YES | skip-one |
| 7 | `git merge X --no-ff` (ref first) | YES | branch `X` |
| 8 | `gh pr merge 42 --squash --delete-branch` | YES | `gh_merge` (`:40-43`) |
| 9 | `gh pr merge --squash 42` | YES | first digit token |
| 10 | `git merge --no-ff X` | **no** | branch resolves to `--no-ff`; no owner; silent return (`:60`, `:147-150`) |
| 11 | `git merge --squash X` | **no** | as 10 |
| 12 | `git merge --no-edit X` | **no** | as 10 |
| 13 | `git merge -m 'merge it' X` | **no** | branch `-m` |
| 14 | `git merge --ff-only origin/X` | **no** | branch `--ff-only` |
| 15 | `git -C /repo merge --no-ff X` | **no** | global consumed, then branch `--no-ff` |
| 16 | `git --exec-path /usr/lib/git-core merge X` | **no** | `--exec-path` absent from `takes_value`; `/usr/lib/git-core` tested against `"merge"` → `return None` (`:58-59`) |

7 of 16 escape. The bed cannot see them: `tests/integration/test-merge-gate.py` at the pin contains
**zero** fixtures with an option between `merge` and the ref (`grep -- "--no-ff|--squash|--no-edit|
ff-only|merge -m"` → no match), and its three new cases only cover globals (`:171-178`).

## Per-SC grades at c8b23e03

| SC | Method | Verdict | Evidence |
|---|---|---|---|
| SC-01 | automated/integration | met | `test-gh-sync.py:3410,3431,3441,3465` — `unpinned repo records nothing` asserts `"build_entry" not in github` (key absence, `:3432`); suite exit 0, 323 ok / 0 FAIL at pin |
| SC-02 | automated/integration | met | `test-gh-sync.py:3451` partial remote write records nothing, `:3493` contract error records nothing |
| SC-03 | automated/integration | met | `test-gh-sync.py:3603,3613` (refuse, station discriminator) + new derived-command horn `:3625`; source derives via `recovery_command_for` (`gh-sync.py:1387-1396` at pin). **Discrimination re-run today** at the pin (gh-sync.py changed since c13): pre-change overlay from `6ad7233f` → exit 1, 302 ok / **21 FAIL** incl. `FAIL T-04 non-era absent refuses`, `FAIL T-04 station discriminator`, `FAIL T-04 recovery-required non-era recover-terminal horn names the derived command` |
| SC-04a | automated/integration | **unmet** | table above; forms 10–16 allow silently. `merge-gate.py:47-48,58-60` |
| SC-04b | automated/integration | met | probe2 §b: three claimants incl. era-exempt `BUG-1030-…` → deny, ids in stable sorted order, `duplicated top-level "branch"`, no re-run/receipt token, zero stderr (era gate never reached). Bed: `test-merge-gate.py:158-162` |
| SC-04c | automated/integration | met | probe2 §c/§c2: unreadable, non-object, different-branch and non-string-branch noise change neither the deny (recovery-required) nor the allow (opened); with only a noise record present the merge is ALLOWED. Bed: `test-merge-gate.py:134,147,169` |
| SC-04d | automated/integration | met | probe2 §d: `GH_BIN=/nonexistent/gh`, `gh pr merge 42` → allow, exit 0, exactly one stderr line "could not verify". Bed: `test-merge-gate.py:116` |
| SC-05 | automated/integration | met | `test-gh-sync.py:3525-3530` — exact `github.issues == {}` and exactly one `issue create` call |
| SC-06 | automated/integration | met | my run at pin: `tests/integration/test-post-merge-sweep.py` exit 0, 61 PASS / 0 FAIL, incl. `T-07 era-exempt absent build_entry is swept` and `T-07 era-exempt recovery-required keeps the worktree` (`:893-894`) |
| SC-07 | automated/integration | met | my run at pin: `test-check-state.py` exit 0, 225 ok / 0 FAIL, incl. `T-06 INV-37 fires at a done station with no task statuses` (`:4660`). Discrimination from c13 (1 FAIL under `CHECK_STATE_BIN` at the pre-change script) still valid — `git diff --stat 894adc0f c8b23e03 -- .claude tests .omp` touches 4 files, neither `check-state.sh` nor its bed |
| SC-08 | automated/integration | met | my run at pin: `test-validate-feature-json.py` ALL PASS, cases `:527-562` (legal values, illegal value, hyphen misspelling, absent key) |
| SC-09 | inspection | met | at pin: `references/github-mirror.md:41` "Build entry — immediately after the plan's signed approval, before the first task starts", `:51-54` the four values and "Ship is post-merge terminal finalization only"; `SKILL.md:141-143` build phase item 1 "**Build entry.** Immediately after signed approval and before dispatching any task". No occurrence of the mirror act "at ship" in either |
| SC-10 | uat | pending-user | `notes/uat-BUG-1309-mirror-build-entry.md`; only the operator can grade it |

## The one unmet criterion — nature and routing

SC-04a is **behaviour wrong**, not merely unproven: the deny is unreachable for forms 10–16 at the
pin. The bed's absence of those fixtures is a second, dependent finding (coverage), and it is why a
file-global green over 19 case names reads as clause (a) satisfied.

**No lane owns the remedy.** `merge-gate.py` and `tests/integration/test-merge-gate.py` are both
DEC-174 reserved to the main session (`plan.yaml:73-75` lanes rows; ruling table
`notes/rulings-2026-09-08-panel-c7.md:77-81`). This is therefore an **operator question**, not a
routable task for eng or validator. Shape of the fix, for the operator's convenience only: resolve
the branch as the first non-option token AFTER `merge`, consuming `merge`'s own value-taking options
(`-m`, `-s`, `-X`, `--into-name`), and treat value-taking globals as a class (`--exec-path`), per
signed T-05 step 2.

## Open questions

- **Q1 (blocking).** SC-04a fails at the pin on 7 of 16 enumerated operator forms. Reserved surface
  → the operator decides whether to fix `git_merge` + bed now or overrule. Nothing else in the
  delta is implicated.
- **Q2 (non-blocking).** The UAT script uses only the bare `git merge feature/uat-scratch` form
  (`notes/uat-…md:155,218,239,248,274`), so a PASS on SC-10 would not detect E1/E2. Whether to add
  one `--no-ff` step is the operator's call — I propose no SC or script edit.
- **Q3 (non-blocking).** Clause (c) noise fixtures in the bed cover only the non-object shape;
  unreadable JSON and a non-string `branch` are proven by probe, not by a standing case. Reserved
  bed, so it is an operator backlog row.

No SC edit proposed or applied. `## Approval` untouched. HEAD at `c8b23e03`; the only pre-existing
working-tree modifications (`feature.json`, `plan.yaml`) are not mine.
