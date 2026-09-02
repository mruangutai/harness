# Goal-check — FEAT-48 plan vs stated intent, cycle 4 at `a80d54a5`

**Does this plan deliver the operator's stated intent? Yes in design, NO at this tree — the rebase
added seven live-tree mutation sites in three files the task set does not act on, so REQ-01/REQ-02
go undelivered and two verify blocks go RED on correct work.** Not signable as drafted; the repair
is a re-plan of D-10, T-01 and T-02, not an amend.

All `plan.yaml` line numbers are the **committed** ones at `a80d54a5` (the working tree carries an
uncommitted `status:` insertion, so its numbers run +1). All figures below are my own, derived at
`a80d54a5` in this worktree.

## 1. Intent coverage — VERDICT: PASS on design, FAIL on census

Every commitment in #1053 traces to a plan element:

| #1053 commitment | Delivered by |
|---|---|
| 5.3x lever, 247s→47s at 8 workers | REQ-03/05, D-05/D-06, T-04 (`run_pool.py`), T-06 wiring, SC-06 |
| unreliable verdict TODAY, independent of parallelism | BRIEF Problem:18-19, REQ-01/02, SC-01/02/03 |
| "proven by the hazard being absent, not by the flake ceasing" (the #979 discipline) | BRIEF SC preamble:53-55, SC-02, SC-05's honest bound, T-06 intent (`plan.yaml`:906-908) |
| rejection of narrowing (no retry, no reorder, no shrinking) | T-01 intent `plan.yaml`:256 verbatim; `notes/research-parallel-safety.md`:104-105; D-08 rejects change-based selection |
| "bisecting the file set … is not done here" | Superseded, not dropped: the partner is identified by direct observation (`research-parallel-safety.md`:8-9, 52-60). No hunt task is needed, correctly |
| ruled out: self-contention, fixture paths, `gh-sync.py` writer | Consistent; the two refuted hypotheses are recorded (`research-parallel-safety.md`:83-88) |

**Nothing in the intent lacks a plan element, and no task traces to a dead REQ** — REQ-01..REQ-08
each have ≥1 task; every `traces:` names a live REQ. **#979 is out of scope by design** (FEAT-47
`plan.yaml`:4-6 re-plans it after landing); the issue names it as "Related", not as a commitment.

**The failure is not coverage of the intent, it is coverage of the tree** — see §3 F-01. The intent's
central commitment is *remove the hazard class, do not narrow it*. At `a80d54a5` seven violations in
three files sit outside the task set, so the class survives the plan as written.

**Info:** SC-06 grades 2.06x (≤120s vs 247s), not the issue's 5.3x. Deliberate and explained
(BRIEF:96-100: floor ~37s, observed 46.9-58.5s, noise margin). The real figure still reaches a human
via T-06's verbatim `pool:`/`slowest:` lines. No finding.

## 2. The FEAT-47 fold — VERDICT: SETTLED by artifact

#1053 `## Scope` says the work is "Folded into **FEAT-47**". It is not; FEAT-48 is its own feature.
**This divergence is settled, bilaterally and explicitly:**

- **FEAT-47 `plan.yaml` D-13**, `git show origin/feat/FEAT-47-tests-layout:.harness/harness/features/FEAT-47-tests-layout/plan.yaml`:187-197 — "FEAT-48 ships WHOLE and lands BEFORE this feature. Parallel safety, the worker pool and suite wall time are its scope … The D-NN numbers D-09 to D-12 and the tasks T-07 to T-09 that once held that scope are **removed, not renumbered**."
- **FEAT-47 `BRIEF.md`:87-94** — "Ordered against FEAT-48, which lands FIRST … Issue #1053 and the rejection of change-based test selection travel with FEAT-48."
- FEAT-48 side: `plan.yaml` D-09 (:115-137) and `BRIEF.md`:172-193.

The scope was carved out deliberately, in a diff, on both sides, with the vacated ids retired so no
recorded reference rebinds. **Not an unrecorded scope change; no operator ruling required.** Two
residual staleness items, both low:

- **F-06 (low)** — #1053's `## Scope` still reads "Folded into FEAT-47" and the issue has 0 comments. The authoritative intent document contradicts the settled allocation. *Consequence:* a future reader grading FEAT-48 against #1053 re-opens a closed question, exactly as this cycle had to.
- **F-07 (low)** — FEAT-48 `BRIEF.md`:213-219 still presents "FEAT-47 must shed the scope … That re-plan is in flight" as an **Open question for the operator**. It has landed (D-13 above). *Consequence:* the operator is asked at signature to rule on something already decided, which spends the scarcest attention in the factory on a no-op. Both plans remain `approval.status: pending`, so the settlement is between two unsigned drafts — sound, but it becomes binding only when both are signed.

## 3. Post-rebase staleness — VERDICT: FAIL, 5 findings

Method: I reimplemented T-03's written rule (`plan.yaml`:520-553) and ran it over `git show` copies
at four shas. It reproduces the plan's own pinned numbers exactly, which is what licenses its other
outputs: **ea6f51f, three files, with the content-read exclusion → exactly the ten named sites,
`1482 1489 / 2112 2114 2133 2248 2250 2269 / 584 605`; without it → 25.** Both **HOLD**, and T-03's
`want` set is correct. Those pins are `git show ea6f51f` reads, so they are rebase-immune by
construction, as is SC-03's historical half.

- **`13 hazard sites in live files` (`plan.yaml`:617-618) — STALE. Current value: 20, over 59 files.** Reproduced 13 at both `ccf674a` and `d5c23a0` (58 files) and 20 at `405a12a8` and `a80d54a5` (59) — so the claim was right when written and the **rebase broke it**. The three named sites moved: `:3077 :3079 :3088` → `:3293 :3295 :3304`.
- **F-01 — HIGH, GATING. Seven new live-tree mutation sites, three site groups, no task owns them.** From `0bc57c88..38dd3622` (FEAT-50 `7505b873` and siblings):
  - `test-bash-write-guard.py:899` `open` + `:901` `os.chmod` — writes `.feat50-bash-write-guard-<pid>.sh` into live `bin/` (`:898`). **This file is in no task's `files:` list.**
  - `test-check-domain.py:3286` `open` + `:3288` `os.chmod` — `.feat50-check-domain-<pid>.sh` (`:3285`). In T-01's `files:`, but T-01's intent addresses only `run_schema` case 3.
  - `test-check-state.py:3598` `open`, `:3600` `copymode`, `:3613` `os.unlink` — a **second** mutant, `.check-state-inv32-era-mutant.sh` (`:3591`), distinct from the `.check-state-inv32-mutant.sh` basename T-02 names.

  *Consequence, for the builder and then the operator:* D-10's census says four sites; the tree holds seven groups. A doer who executes T-01 and T-02 exactly as written finishes correct work and then **T-02's verify exits 1** (its `appeared` poll runs `test-check-state.py`, which still creates the era-mutant in live `bin/`) and **T-03's verify exits 1** (`live.returncode == 0` is unreachable with 7 violations). **SC-03's live-tree zero is unmeetable as drafted**, and REQ-01/REQ-02 are not delivered. Carried by **D-10** (`plan.yaml`:139-155, the census), **T-02** (`files:` :337-339 and intent :374-381) and **T-01** (intent). *Repair size:* larger than a single-field amend — a re-derived D-10, a new path in T-02's `files:`, and new intent text in two tasks.
- **F-02 — MED. All three `test-check-state.py` anchors in T-02's intent are stale.** `plan.yaml`:376-378 cites `2109-2133`, `2245-2269`, `3066-3088`; at `a80d54a5` the blocks are **`2237-2264`, `2373-2400`, `3282-3304`** (`mutant`/`mpath` lines 2240, 2376, 3286). Drift is +131, +128, +216 — **not only the INV-32 one**; the shared hypothesis flagged just the third. `test-feature-worktree.py:583-607` **HOLDS** (`:583` at ea6f51f, ccf674a and the tip alike). Graded med, not high, because `plan.yaml`:380-381 already instructs "Re-derive the line numbers before you edit … The basenames are the durable identifier" — the plan anticipates its own rot. *Consequence:* a doer who trusts the anchors edits unrelated code.
- **F-03 — LOW. Discovered count 58 (`plan.yaml`:499-500) — STALE. My walk: 59.** D-03 prune set exactly (`.git`, `.claude/worktrees`, `node_modules`, `.venv`); all 59 under `.claude/skills/harness/bin/`; `git ls-tree` corroborates **56 at ea6f51f, 58 at ccf674a, 59 at 0bc57c88 / 38dd3622 / 405a12a8 / a80d54a5**. **My finding differs from the shared hypothesis**, which held 58 was already wrong pre-rebase: at `ccf674a`, the sha the plan cites, 58 is *correct*. It became 59 on the rebase. **SC-03's floor of 50 is unaffected** — the margin absorbed it, as D-03 intended. *Consequence:* a stated measurement is wrong; no gate misfires.
- **F-05 — LOW. `plan.yaml`:972 — "190 of 190 existing headings at ccf674a, last DEC-207" — STALE. Current: 192 of 192 em-dash headings, last DEC-209** (DEC-208 and DEC-209 arrived on the rebase). *Consequence:* none mechanical — T-05's instruction reads the last heading at authoring time and pins no number (`plan.yaml`:968-969), so the mechanism is sound; only the parenthetical is false. Single-field amend.
- Also re-derived and **HOLDING**: `run-unit-tests.sh` serial loop at **147-157** exactly (`for s in "${SCRIPTS[@]}"` at 148, `done` at 157); the literal `"${SCRIPTS[@]}"` occurs **exactly once**; drift detector `for s in` at **64**. The rebase did not touch this file.

## 4. `verify:` satisfiability at the tip — VERDICT: FAIL, sweep yield 2

Six blocks swept. **Yield: two newly unsatisfiable, both rebase-induced** (c3's pre-rebase sweep
found zero; that sweep is now void, as the dispatch anticipated).

| Block | Verdict |
|---|---|
| T-01 | **satisfiable.** `"CRASHING schema module DENIES"` occurs exactly once at the tip and `"never written"` zero times, so both `len(...)==1` legs are reachable. Whole-file `returncode == 0` is not statically decidable |
| T-02 | **UNSATISFIABLE.** `appeared` cannot be empty: `test-check-state.py:3598` creates `.check-state-inv32-era-mutant.sh` in live `bin/` and no task removes it (F-01) |
| T-03 | **UNSATISFIABLE.** `live.returncode == 0` requires zero live findings; 7 survive (F-01). Its other legs hold: `disc[0] >= 50` → 59; the ten-site `want` set reproduces exactly |
| T-04 | **not statically decidable** — drives unbuilt `run_pool.py` over its own tempdir fixtures. No dependency on any rebase-touched path |
| T-06 | **not statically decidable**, and its static legs HOLD: the one-occurrence `"${SCRIPTS[@]}"` assertion and the `--mutation-check "$BIN_DIR"` substring are both reachable at the tip. The ten-run leg is a false-gate *risk* only: the three new mutants are created and unlinked **within** one run, and `--mutation-check` compares before/after, so they are invisible to it — a leak on a crash path would redden it |
| T-05 | **satisfiable.** `--stdout` drift comparison and the 300-word floor are unaffected by the rebase |

## 5. Cycle-3 advisory closure — VERDICT: PASS, 3 of 3 FIXED

`runs/2026-08-31-04-validator/` holds two files, `digest.md` and `state.yaml` — one digest.
Graded at source at the tip, not from `a80d54a5`'s message (which moved 5 files, `plan.yaml` +30/-4):

- **F2 (med) — FIXED.** The fourth blind spot (a target derived from a tainted file's *content*) is stated in D-11 at `plan.yaml`:185-193 and required of the decision entry at T-05 intent `plan.yaml`:1006-1012.
- **SNE-01 (low) — FIXED.** D-03 carries the accepted consequence of the repo-wide walk at `plan.yaml`:61-69, naming the four prunes, the walked `.harness/**`, the reddened PR and the rename recovery.
- **F1 (low) — FIXED.** `BRIEF.md` REQ-02 is now qualified: "for a write whose target is derived from the test's own path, or whose target is inside the shared code directory the runtime check watches … this requirement does not claim them" (`BRIEF.md`:33-37). The unqualified overclaim is gone.

Fix ordering the digest asked for (F2 before F1) is respected: REQ-02's qualification cites D-11.

## Findings

| id | sev | gating | summary |
|---|---|---|---|
| F-01 | **high** | **GATING** | 7 unowned live-tree mutation sites; D-10 census stale at 4; SC-03 unmeetable; T-02+T-03 verify RED on correct work |
| F-02 | med | no | all three `test-check-state.py` anchors in T-02 stale (+131/+128/+216) |
| F-03 | low | no | discovered count 58 → 59; SC-03 floor of 50 unaffected |
| F-05 | low | no | T-05's "190 headings, last DEC-207" → 192, last DEC-209 |
| F-06 | low | no | #1053 `## Scope` still says "Folded into FEAT-47" |
| F-07 | low | no | BRIEF's operator open-question is already answered by FEAT-47 D-13 |

## Open questions

- **Q1 (not blocking).** F-01's repair changes D-10's census and two tasks' intent. Does the operator want the three new FEAT-50/BUG-1071 sites fixed **inside FEAT-48** (consistent with D-10's "fixed here rather than allowlisted", and required for SC-03's zero), or is a narrower SC-03 preferred? Recommend the former: an allowlist for three sites is the invariant D-04 refuses.
- **Q2 (not blocking).** Nothing settles whether FEAT-50's mutant idiom will keep re-appearing. The invariant T-03 adds is exactly the mechanism that stops it, which is an argument for shipping FEAT-48 sooner, not for widening it.

## Plan integrity

`plan.yaml` **byte-unchanged by this dispatch**; `approval.status: pending`. Recorded at entry and
re-confirmed at exit — see the DIGEST for the `status --porcelain` / `diff --stat` result. The
pre-existing uncommitted diff (7 insertions, 6 deletions: `status: plan` and six `pending`→`plan`
station values) was present **before** this run and is not mine.
