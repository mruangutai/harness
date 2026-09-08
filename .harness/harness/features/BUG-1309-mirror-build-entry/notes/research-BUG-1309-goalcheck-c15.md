# Goal-check at review_sha e374c9a2 — BUG-1309-mirror-build-entry (cycle 15)

**BLUF. `e374c9a2` fixed the c14 regression class (E1) completely — forms 10–15 now all DENY — but
SC-04 clause (a) remains `unmet` on ONE enumerated form: form 16,
`git --exec-path /usr/lib/git-core merge <branch>`, is still a SILENT ALLOW (no deny, no stderr, no
audit line). 15 of the 16 c14 forms now deny, up from 9. Everything else is met: SC-01..SC-03,
SC-04b/c/d, SC-05..SC-09 `met`; SC-10 `pending-user`.** The residual is c14's E2 finding, untouched
by this commit: `git_merge()` still gates value-taking globals through a **closed 7-name set**
(`merge-gate.py:49-50` at the pin) that omits `--exec-path`, while the signed T-05 step 2 names
`--exec-path <p>` verbatim as an example and rules "VALUE-TAKING GLOBALS ARE A CLASS, NOT A CLOSED
LIST" (`plan.yaml:1029-1033` at the pin).

Reserved surface (DEC-174): `merge-gate.py` and its bed are main-session-direct. This is an
**operator decision**, not a routable task.

## SC-04 clause (a) — the c14 16-form enumeration, re-run verbatim

Fixture throughout, identical to c14 and to the bed's own `fixture()`: non-era feature
`FEAT-9001-fixture-non-era`, `github.build_entry` ABSENT, `sync: true`, `repo` pinned → the
criterion requires DENY for every form. Driven end-to-end through the real `merge-gate.sh` hook.

| # | Form | c14 | c15 |
|---|---|---|---|
| 1 | `git merge X` | YES | **DENY** |
| 2 | `git -C /repo merge X` | YES | **DENY** |
| 3 | `git -c core.editor=true merge X` | YES | **DENY** |
| 4 | `git --work-tree /wt merge X` | YES | **DENY** |
| 5 | `git -C/repo merge X` (attached) | YES | **DENY** |
| 6 | `git --git-dir=/x/.git merge X` | YES | **DENY** |
| 7 | `git merge X --no-ff` | YES | **DENY** |
| 8 | `gh pr merge 42 --squash --delete-branch` | YES | **DENY** |
| 9 | `gh pr merge --squash 42` | YES | **DENY** |
| 10 | `git merge --no-ff X` | no | **DENY** (fixed) |
| 11 | `git merge --squash X` | no | **DENY** (fixed) |
| 12 | `git merge --no-edit X` | no | **DENY** (fixed) |
| 13 | `git merge -m 'merge it' X` | no | **DENY** (fixed) |
| 14 | `git merge --ff-only origin/X` | no | **DENY** (fixed) |
| 15 | `git -C /repo merge --no-ff X` | no | **DENY** (fixed) |
| 16 | `git --exec-path /usr/lib/git-core merge X` | no | **ALLOW — still escaping** |

**COUNT: 15 of 16 DENY. One escapes.** Probe: `/tmp/mgprobe15/probe.py` (throwaway, `/tmp` roots
only; nothing written in-repo, HEAD unmoved).

**Reproduction for the UNMET grade** — paste from the worktree root:

```bash
env -u HARNESS_AGENT_TYPE python3 /tmp/mgprobe15/probe2.py
```

(`probe2.py` builds the same fixture and prints one `DENY`/`ALLOW` line per case.) Measured:

```
ALLOW  git --exec-path /usr/lib/git-core merge feature/test          stderr=''
DENY   git --exec-path=/usr/lib/git-core merge feature/test
ALLOW  git --attr-source HEAD merge feature/test                     stderr=''
DENY   git --config-env k=E merge feature/test
DENY   git --super-prefix p/ merge feature/test
DENY   git --namespace n merge feature/test
ALLOW  git --exec-path /usr/lib/git-core merge --no-ff feature/test  stderr=''
```

The shape: a value-taking global in its **detached** spelling that is absent from
`global_values` is skipped by one, its VALUE is then tested against `"merge"`, and `git_merge()`
returns `None` — so `main()` exits at `if not ... merge_ref(command)` (`merge-gate.py:35`) before
any receipt is read. The **attached** spelling of the same option denies, which is why the closed
set looks complete from the bed.

## SC-04 — remaining clauses, all re-run at this SHA

| Clause | Result | Evidence |
|---|---|---|
| ambiguity: ≥2 valid claimants → DENY | met | probe §ambiguity: 3 claimants incl. era-exempt `BUG-1030-…` → deny; ids `BUG-1030-stale-anchor-write-hazard, FEAT-9001-fixture-non-era, FEAT-9002-fixture-duplicate` in stable sorted order, byte-identical across two runs |
| ambiguity offers no re-run command | met | reason contains `duplicated top-level "branch"`, and neither `gh-sync.py` nor `recover-terminal`; zero stderr — the era gate is never reached |
| ambiguity reached even when a claimant IS era-exempt | met | same case; also denies through `git merge --no-ff` |
| era-exempt → ALLOW, exit 0, no permission decision | met | `BUG-1030-…` with `build_entry` absent AND with `recovery-required`, bare and `--squash` forms: exit 0, `decision is None`, `predates` on stderr |
| allowed values `opened` / `not-applicable` / `recovered-terminal` | met | 3 values × 3 forms (bare, `--no-ff`, `-m msg`) = 9 cases, all exit 0 / no decision |
| single-owner deny names feature + re-run command | met | absent and `recovery-required`, via `--no-ff`: deny naming `FEAT-9001-fixture-non-era` and `gh-sync.py` |
| one owner + ANY noise changes no verdict | met | 6 noise shapes (unreadable, empty, non-object list, non-object scalar, different-branch, non-string branch) × 3 verdicts (absent→deny, opened→allow, unclaimed-branch→allow) = 18 cases, all as required |
| `gh` unavailable → ALLOW with ONE stderr line | met | missing binary and exit-9 binary: exit 0, no decision, exactly 1 stderr line containing `could not verify` |

Total probe: 54 of 55 checks pass (`grep -cE '^(ok|FAIL)'` → 55); the single FAIL is form 16.

## Per-SC grades at e374c9a2

Delta since the c14 pin is two code/test files only
(`git diff --stat c8b23e03 e374c9a2 -- .claude tests .omp` → `merge-gate.py`,
`tests/integration/test-merge-gate.py`), so the c14 discrimination results for SC-03 (`gh-sync.py`)
and SC-07 (`check-state.sh`) stand unchanged — neither file nor its bed moved.

| SC | verify: | Verdict | Evidence |
|---|---|---|---|
| SC-01 | automated / integration | MET | `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-gh-sync.py` → exit 0, 323 ok, 0 FAIL |
| SC-02 | automated / integration | MET | same run, exit 0, 323 ok, 0 FAIL |
| SC-03 | automated / integration | MET | same run; `gh-sync.py` untouched in `c8b23e03..e374c9a2`, so c14's re-measured discrimination (pre-change overlay → 21 FAIL) is still the live measurement |
| SC-04 | automated / integration | **UNMET** | clause (a) 15/16 — form 16 allows silently. Repro above. All other clauses met. Bed: `tests/integration/test-merge-gate.py` exit 0, 27 ok, 0 FAIL, `ALL PASSED` — the bed cannot see form 16 (no `--exec-path` fixture) |
| SC-05 | automated / integration | MET | `test-gh-sync.py` exit 0, 323 ok, 0 FAIL (exact-count cases `:3525-3530`) |
| SC-06 | automated / integration | MET | `tests/integration/test-post-merge-sweep.py` → exit 0, 61 PASS, 0 FAIL; both named cases present at the pin (`:893-894`) |
| SC-07 | automated / integration | MET | `tests/integration/test-check-state.py` → exit 0, 225 ok, 0 FAIL, incl. `T-06 INV-37 fires at a done station with no task statuses` (`:4660`) |
| SC-08 | automated / integration | MET | `tests/integration/test-validate-feature-json.py` → exit 0, 78 PASS, 0 FAIL, cases `:527-562` |
| SC-09 | inspection | MET | at the pin, via `git show e374c9a2:<path>`: `references/github-mirror.md:41` "Build entry — immediately after the plan's signed approval, before the first task starts", `:51-54` the four values + "Ship is post-merge terminal finalization only"; `SKILL.md:141-143` build phase item 1 "**Build entry.** Immediately after signed approval and before dispatching any task" under `## The build phase` (`:136`). Negative grep for `at ship` / `right after the approval gate` over both blobs → no match |
| SC-10 | uat | **PENDING-USER** | `notes/uat-BUG-1309-mirror-build-entry.md`; only the operator grades it. Amended this cycle — see below |

Every suite invoked as `env -u HARNESS_AGENT_TYPE python3 <path>` from the worktree root. No
formatter, no linter, no project-wide suite run.

## Is the goal delivered at this SHA?

**Not fully.** Modulo the user-gated SC-10, nine of ten criteria are met and the goal's substance —
mirror at Build entry, durable local receipt, Build refusing without one, recovery without
historical task issues, terminal-state invariant — is delivered. The one gap is inside the goal's
own sentence "a merge is refused while that receipt says recovery is still owed": one merge
invocation form an operator can type still reaches no refusal. It is a narrow residual (one option
spelling class) but it is a real, current, reproducible silent allow, and the plan's signed T-05
step 2 forbids exactly the closed-list implementation that leaves it open.

## Emergent criteria

**None.** The `--attr-source HEAD` and detached-`--exec-path` behaviour is not a new criterion: it is
the same class SC-04 clause (a) already quantifies over, and c14 already recorded it as E2. Nothing
outside the BRIEF's ten criteria surfaced this cycle. No SC edit proposed or applied.

## The UAT amendment — WRITTEN INTO the script

The script previously issued only the bare `git merge feature/uat-scratch` form, so an operator PASS
could not detect a post-subcommand-flag escape. **I wrote the amendment into
`notes/uat-BUG-1309-mirror-build-entry.md`** (my own `notes/uat-*` path, not reserved surface):

- **lines 179–206** — new `## Step 3b — The refusal survives the flags you actually type`.
- **lines 250–253** — Step 6 gains the `--no-ff` allow-side counterpart (guards over-refusal).
- **lines 256–261** — Step 6's Observe/PASS/FAIL updated for two invocations.
- **lines 337–339** — the verdict now requires Step 3b to PASS.

Step 3b, verbatim as the operator types it:

```bash
python3 /tmp/bug1309-uat-fixture.py $UAT_CHECKOUT recovery-required

printf '{"tool_input":{"command":"git merge --no-ff feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh

printf '{"tool_input":{"command":"git merge --squash feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh

printf '{"tool_input":{"command":"git merge -m message feature/uat-scratch"}}' \
  | HARNESS_PROJECT_DIR=$UAT_ROOT bash $UAT_CHECKOUT/.claude/skills/harness/bin/merge-gate.sh
```

Expected: THREE `deny` JSON lines, each naming `FEAT-9001-uat-scratch` and
`github.build_entry=recovery-required`. **Executed verbatim at this SHA and observed** — three
identical denies. Step 6's amended pair (bare + `--no-ff`, after `open` records `opened`) printed
`exit=0` twice with no JSON, also observed. The fixture builder was extracted from the note's own
Step 1 block (83 lines) to `/tmp/bug1309-uat-fixture.py`; `/tmp/bug1309-uat` is throwaway and the
operator's Step 1 rebuilds it.

I did NOT add a `--exec-path` step: a hand test whose expected output encodes a known defect would
have to be rewritten the moment the operator decides on form 16. That decision comes first.

## Open questions

- **Q1 (blocking).** SC-04 clause (a) fails on 1 of 16 enumerated forms:
  `git --exec-path /usr/lib/git-core merge <branch>` is a silent allow, and the same holds for any
  detached-value git global outside the closed 7-name set (`--attr-source` measured). Reserved
  surface (DEC-174) → the operator decides: replace the closed set with the class the signed T-05
  step 2 mandates (skip-two for any `--opt value` global whose value does not lex as the subcommand,
  or fail closed when the subcommand cannot be identified), or overrule SC-04 clause (a) for form
  16 with a recorded ruling. Nothing else in the criteria is implicated.
- **Q2 (non-blocking).** The bed still has no fixture for form 16's class; a ruling that fixes the
  parser should add one, and a ruling that overrules should record why the bed omits it. Reserved
  bed → operator backlog row.
- **Q3 (non-blocking).** Clause (c) noise fixtures in the bed cover only the non-object shape;
  unreadable JSON, empty file and non-string `branch` are proven by probe, not by a standing case.
  Carried forward from c14 unchanged. Reserved bed → operator backlog row.

`## Approval` untouched. BRIEF.md, plan.yaml, feature.json and STATE.md untouched. HEAD at
`e374c9a2`; the one pre-existing working-tree modification (`feature.json`) is not mine.
