# Ship review — FEAT-38, `DECISIONS.md` states current knowledge

**The blocker is gone and the feature is ready to land.** `origin/main` is merged, the three
conflicts are resolved, and the three amendments FEAT-44 added while this feature was abolishing the
amendment convention are folded into their entries' current truth. The full unit suite exits **0**
with zero `FAIL` lines. The blocking qa gate passes at the new pin. A targeted panel re-review of
the delta passes with **no `must_fix`**. `review_sha` is re-pinned to **`eb7e7513`**.

**One decision is yours: which of six residual findings become backlog issues.** Nothing else is
outstanding.

## What changed since the last briefing

The last briefing said FEAT-38 could not merge because FEAT-44 shipped underneath it. That is
resolved.

| Step | Result |
|---|---|
| merge `origin/main` | done, `a382827` + `141eca6`. Branch is **0 behind** `origin/main` |
| the three conflicts | resolved and independently verified — see the table below |
| the three new amendments | **folded**, `3767624`, per DEC-205 |
| SC-11 read-back on the fold | **3 of 3 PASS**, by a reader who did not write it |
| full unit suite | **exit 0**, zero `FAIL` lines, **55** scripts discovered and executed |
| blocking qa gate at the new pin | **PASS**, `matrix_ok: true`, `must_fix: []` |
| targeted panel on the delta | **PASS**, `severity_max: med`, `must_fix: []` |

**The conflict resolutions, graded rather than assumed.** No reviewer had ever seen them; they had
been verified mechanically, and mechanical agreement proves the files agree, not that the resolution
chose the right entries.

- `.harness/harness.json` — **not a union**, and correctly so. A naive union would have resurrected
  two registrations naming files FEAT-44 deleted. Reconciled entry by entry in Python: branch 29,
  main 26, union would have been 29, the pin is **27**, and the two dropped are exactly
  `test-context-watch-cli.py` and `test-context-watch-hook.py`, both confirmed absent from the tree.
  All 26 concrete registrations name a file that exists; the 27th is the glob `tests/integration/**`,
  matching nothing because the directory does not exist.
- `run-unit-tests.sh` — the same shape, and its arrays agree with `harness.json` in both directions
  today.
- `DECISIONS-INDEX.md` — **regenerated, never hand-merged**, proved by the committed file being
  byte-identical to a fresh generation. Confirmed twice independently. 188 rows against 188 live
  `## DEC-` headings, zero orphans. FEAT-44 changed zero index rulings, verified.

## A second merge landed mid-ship, and it was not foreseeable

Between the push and the merge, **FEAT-43 shipped as PR #978**, moving `origin/main` from `79e2639`
to `24af8d4` and re-conflicting the same two files. The main session merged it at **`eb7e751`** — a
HEAD move no governed agent may make, and the guard refusing it is the guard working.

**This resolution is a pure union, where the first one would have been wrong as a union.** Measured
independently twice, at the orchestrator tier and by the main session:

| array | base `79e2639` | ours | theirs | union at the pin |
|---|---|---|---|---|
| `harness.json` `test_kinds.integration.detect` | 26 | 27 | 27 | **28** |
| `run-unit-tests.sh:30` `UNIT_SCRIPTS` | 26 | 26 | 28 | **28** |
| `run-unit-tests.sh:31` `INTEGRATION_SCRIPTS` | 25 | 26 | 26 | **27** |

**Zero removals on either side** — which is exactly why a union is right here and was wrong for
FEAT-44, whose side had deleted two registered files. 27 scripts plus the inert `tests/integration/**`
glob is the 28 in `harness.json`. Every entry of all three arrays names a file that exists. The fold
survived untouched: `git diff 37676244..eb7e751` is empty for both `DECISIONS.md` and
`DECISIONS-INDEX.md`.

The blocking qa gate was re-run at `eb7e751` and passes with `must_fix: []` on a **non-vacuous**
discovery set: 55 scripts actually executed, matching 28 + 27 exactly. The reviewer panel was not
re-run, and the validation lead concurred on the member's own evidence rather than merely complying:
what that leaves unexamined is FEAT-43's shipped code, gated under its own feature, plus a union that
provably removes nothing.

## The fold, and what it was protecting

DEC-205 says an entry states current truth directly, a correction rewrites the entry it corrects, and
**a claim the tree has falsified survives as one clause of that truth so it cannot be re-proposed as
new.** The last part is the whole point: an entry whose falsified claim was simply deleted passes
every automated assertion.

| Entry | What was believed | What falsified it | Verdict |
|---|---|---|---|
| DEC-159 | the in-flight warning is a Claude PostToolUse hook, `context-watch-hook.py` | FEAT-44 deleted the file and the registration; delivery is now the OMP `tool_result` injection | PASS |
| DEC-198 | the `200000` default is sourced to `context-watch.py` | that file is retired; the default is re-homed to `.omp/extensions/harness-hooks.ts` | PASS |
| DEC-201 | the orchestrator identifies itself with a nonce and a second grep of the Claude sidecars | retired with the sidecar mechanism; `ctx.sessionManager.getSessionFile()` replaces it | PASS |

**DEC-201 was the one at risk, and it held.** Its amendment carried measured evidence with stated
limits, and the failure mode was a fold that keeps the finding and loses the bounds. All six bounds
survive: one OMP build measured twice on one machine, the committed probe path, the version-floor
risk, that `probe-omp-session-accessor.py` fails rather than skips, that the check is **MANUAL and
not a CI gate**, and that this is one build's observed behaviour rather than a property of the OMP
API. The retired nonce scheme is recorded as **correct-but-inapplicable rather than wrong** — a
distinction that matters, because flattening it would have let the scheme be re-proposed as a fresh
idea.

Three corroborating details of retired mechanisms were dropped. Each was judged defensible on the
record rather than silently: `notes/readback-fold-merge.md`.

## Three handed-down premises proved false, and all three were caught by re-measurement

Worth saying plainly, because it is now the third feature in a row where the sender was wrong and the
receiver caught it.

1. **"`test_kinds` went 28 → 27."** No consistent counting method yields that pair; it understates a
   drop of two as a drop of one. The truth is 29 → 27. **The resolution's substance is correct**; only
   the numeral was wrong, and it reached no durable record — it appears only in the notes that refute it.
2. **"`.claude/settings.json` is absent from this tree."** It is present, and still registers a
   PostToolUse hook on the `Write|Edit|Bash` matcher — `check-domain.sh --post`, not the retired
   watchdog. DEC-159's folded clause is scoped "no Claude hook is registered *for this*", so it is
   true as written.
3. **"DEC-159's amendment ends with a stray `---`."** It was DEC-201's. Both were handled.

A fourth, smaller: the goal-check digest's headline says *"sixteen live criteria"*, but its own table
carries **17 rows** — SC-01 through SC-18 less the retired SC-09 tombstone. The table is right and the
headline is an arithmetic slip. With SC-13 since answered by you, **17 of 17 live criteria are met**,
which is what the previous briefing said.

## How this briefing was assembled

**No report round was spawned** — that buys a re-narration of files already on disk (DEC-69). Read
directly: `runs/fold-merge-product/digest.md`, `runs/readback-fold-validator/digest.md`,
`runs/regate-pin-validator/digest.md`, `runs/goalcheck-ship-product/digest.md`,
`notes/research-FEAT-38-goalcheck-635cd3b.md`, `notes/uat-FEAT-38.md`, this feature's `STATE.md`, and
the two prior ship reviews (`ship-review-2026-08-30-ship-close.md`, `ship-review-2026-08-29-18.md`),
which themselves name the plan, build, simplify and panel digests they assembled from.

## Proposed backlog — strike any row you do not want filed

**Anything you strike dies silently, so all seven are listed.** None gates anything. B-25, B-26 and
B-39 are carried unchanged from the last briefing.

| ID | Nature | Finding |
|---|---|---|
| B-25 | bug | `bash-write-guard.sh` cannot expand shell variables and does not track `cd`. It resolves targets against the session root, so `cd <dir> && sed -i '' … plan.yaml` and `sed -i '' … "$P"` are denied "outside your domain" while the identical command with a literal absolute path is allowed — and `check-domain.sh --resolve` grants that same path. Two enforcement surfaces disagree |
| B-26 | bug | `/usr/bin/grep` on this machine is `pi-uu-grep 0.2.0`, in which a line-leading `+` matches every line. Four false readings in this feature. Every affected measurement was redone in Python |
| B-39 | bug | A run-directory slug collision let one lead overwrite another run's `digest.md` and `state.yaml`. `runs/` is gitignored, so the record was unrecoverable. Nothing in the contract stops a lead reusing a slug |
| B-40 | chore | `DEC-159` still says the handoff shape gate denies a note at >40 lines, while the same entry records the cap raised to ~60 at DEC-160. In the un-amended remainder; found during the fold and reported rather than edited, because re-auditing the remainder was an explicit non-goal |
| B-41 | chore | Three `### DEC-NNN addendum` level-3 sub-headings survive in `DECISIONS.md` (under DEC-124, DEC-125, DEC-141). They are a sibling construct to the amendment this feature abolished, nothing mechanical bans them, and they predate the feature — present at its original base `7ebfc9e`. Outside its approved scope. **FEAT-46's triage is the natural home** |
| B-42 | bug | `run-unit-tests.sh --check-kinds` asserts only one direction. It does **not** assert that every declared `test_kinds.integration` entry appears in the script arrays, so it would not have caught the naive-union defect it was cited as guarding. Correct today only because qa measured file existence directly; nothing automated holds it. Pre-existing, ranked first by the panel on irreversibility — the failure mode is silent |
| B-43 | chore | Four test scripts (`test-feature-worktree.py`, `test-expertise-merge.py`, `test-plan-merge.py`, `test-observations-merge.py`) print their own `PASS <script>` line in a format byte-identical to the runner's own marker, so any log-based tally over-counts. It produced a false "61 scripts" in this run's own reporting before qa re-measured it at 55 |

## Open, recorded, not proposed as backlog

- **PR #996 carries two FEAT-46 commits** — `16f86e3` (the FEAT-46 grilling note) and `7a23d74` (the
  operator's hold entry). They were flagged in the last briefing as a deliberate decision. They touch
  only `.harness/logs/2026-08-30.md` and a grilling note — no source, no FEAT-46 implementation — and
  splitting them out now would need a history rewrite that would move HEAD and void the pin. They
  land with the merge, said here so it is not silent.
- **Nobody mutated `harness.json` to prove the runner CAN fail.** Exit 0 plus 26 of 26 registrations
  existing is a strong positive measurement, but it does not discriminate fail-closed from fail-open.
  The index regeneration check IS falsification-grade — a hand-merge would have differed.
- The four items the last briefing left open are unchanged: bare relative paths resolving against the
  outer checkout, DEC-205 naming two refused rot detectors without naming what compensates, the stale
  docstring SC-18 forbids fixing, and the 11-of-70 `bin/` argv class.

## Budget

**Cycles 16 of 30** — a hard bound, not crossed, and it did not move this run. All three squad runs
returned PASS on the first pass and reported zero send-backs, so there was no rework to count.

**Runs 38 of an informational 20.** That budget notices a long feature; it never stops one, and this
is not an apology. The four runs added here each closed a named gate — the fold, its independent
read-back, the re-gate at the fold pin, and the re-gate at the merge pin — and none was rework. Asked the three questions INV-22
exists to ask: each run was efficient, each resolved its issue, and each advanced a success criterion.
The count is a floor anyway; orchestrator-held segments are not runs and never appear in it.

## What happens next

1. Merge #996. `main` requires one status check, `integration`.
2. `gh-sync.py ship` lands the board: 28 sub-issues, three `source_issues` (#615, #78, #686), then
   parent #935, then milestone 31 — which closes only if no child is open.
3. **The worktree is safe to remove once the merge lands**, and removal is yours or the `post-merge`
   hook's, never an agent's from inside it. Every terminal artifact is committed in the PR, so it is
   on the default branch the moment the merge completes.
4. **Feature-close distillation has not run.** It runs at merge, on a distill mission you dispatch —
   not as part of shipping.
5. FEAT-46 comes off hold, and inherits both the scoped SC-13 note from the last briefing and B-41.
