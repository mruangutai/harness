# GOAL-CHECK — FEAT-26 pr-linkage-recorded — 11/11 MET

**Verdict: GOAL MET.** Every SC-01..SC-11 is met, each on evidence I ran or read in this
worktree at HEAD `bad3244` (plus the uncommitted working tree, noted per SC). Two of the
three coverage gaps qa handed back are closed by measurement below; one remains open as a
regression-protection gap, not a delivery gap.

**Filename note:** the dispatch asked for `notes/goal-check.md`. `team-config.yaml`'s
harness-pm domain grants `.harness/*/features/*/notes/research-*.md`, so that path would be
denied. Written here instead, same directory.

## SC table

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | **MET** | `test-gh-sync.py` `record-pr writes the number when the branch has exactly one merged PR` (:1450) — asserts `pr == 501`, no `--pr` passed, and that the `gh pr list --head feat/pr-one --state merged` call was made. Suite run here: `ALL PASSED`. Live corroboration: T-06 derived 7 numbers with no `--pr`, and `gh pr view` on each (17/131/212/376/415/451/491) returns the matching branch and a merged timestamp. |
| SC-02 | **MET** (behaviour measured; see gap 1) | I ran `record-pr` on temp fixtures against a fake `gh`: zero results → `gh-sync: no merged pull request found on branch feat/x`, rc 0, `pr` still `None`; two results → `gh-sync: branch feat/x is ambiguous — merged pull requests 15, 4`, rc 0, `pr` still `None`. Both cases also bound in `test-gh-sync.py` (:1464, :1478) and the two-PR case uses the real ambiguous branch `feat/harness-native-foundation` (which `gh` confirms carries PRs 4 and 15). |
| SC-03 | **MET** | `test-gh-sync.py` `record-pr never overwrites a pr that is already an integer` (:1493) — disk holds 314, fake `gh` offers 999, and the case asserts no `pr list` call happened at all. **The `--pr` path, unbound in the suite (qa gap 1), I measured directly:** `record-pr <feat> --pr 777` on a feature whose `pr` is 314 printed `gh-sync: pr already recorded as #314 — not overwritten` and left 314 on disk. Code order confirms it: `gh-sync.py:562` gates before `pr_arg` is read at 565. |
| SC-04 | **MET, on stronger evidence than the shipped test** | The shipped case (`source_issues survives every save during a full open run`, :1365) asserts only the END state. I observed every save instead: imported `gh-sync.py`, wrapped `save_recorded` to re-read `feature.json` after each call, ran `cmd_open` on a 3-task fixture — **9 saves, all 9 carrying `[201, 202, 203]` on disk.** The "every save, not just the last" clause is therefore measured, not inferred. |
| SC-05 | **MET, with my own red proof** | `test-validate-feature-json.py` runs 5 named cases green (accept list-of-int, reject float member, reject quoted number, reject undeclared sibling naming `'source_issue'`, accept a `github` block with no `source_issues`). Red proof, run here in-memory against `feature-schema.json`: with `github.properties.source_issues.items` removed and `github.additionalProperties` set true, all three rejecting fixtures return **zero** errors — so the green is load-bearing, not vacuous. The accept case (`problems == []`) also pins the base document clean, so the reject cases cannot pass on unrelated noise. |
| SC-06 | **MET** | Four cases in `test-gh-sync.py`: exact stdout equality `"Closes #305\nCloses #101\nCloses #220\n"` on a deliberately unsorted list (a sort would go red), `stdout == ""` for empty and for absent, and `closes makes no gh call at all` asserting the fake-`gh` call log is empty while a working fake `gh` is on PATH. The absence assertion is not vacuous: other cases in the same file read that same log non-empty. Code: `cmd_closes` (`gh-sync.py:868`) is `load_recorded` + `print`, and `main` returns before the root climb and `load_config`, so no `gh` binary is reachable on that path. |
| SC-07 | **MET** | `test-check-state.py` prints the six INV-28 cases `ok`, and the presence case (`INV-28 warns on a Done feature whose pr is null`) is called FIRST in `main()` (:2270) before the four silence cases — so the line is shown to appear before it is shown to be absent. Live discriminating pair on the real tree: one INV-28 line, naming `FEAT-24-config-responsibility-split` (`Done`, `pr: null`), while **28** other `Done` features with an integer `pr` produce none. The absence assertion matches on the short token `INV-28`, which cannot wrap; a false green would need the whole block not to run, and the FEAT-24 line proves it ran. |
| SC-08 | **MET, asserted one feature id at a time** | Ran T-06's per-feature loop myself over the 23 enumerated ids: 23 ok, 0 wrong — `FEAT-01` 4, `FEAT-02` 4, `FEAT-03` 15, `FEAT-04` 15, `FEAT-05` 17, `FEAT-06` 45, `FEAT-07` 77, `FEAT-08` 131, `FEAT-09` 136, `FEAT-10` 212, `FEAT-11` 221, `FEAT-12` 259, `FEAT-13` 260, `FEAT-14` 293, `FEAT-15` 263, `FEAT-16` 311, `FEAT-17` 298, `FEAT-18` 334, `FEAT-19` `None` (`Abandoned`), `FEAT-20` 376, `FEAT-21` 415, `FEAT-22` 451, `FEAT-23` 491. Not graded only against the plan's own list: `gh pr view` independently confirms 4 = "Replace GSD with the harness (foundation)", 15 = "FEAT-04 (decisions index) + FEAT-03 backlog disposition…", and the seven derived numbers each match their feature's own branch. `git diff ffe826e..bad3244` touches exactly the 11 backfilled `feature.json` files (plus this feature's own) — the 11 already-recorded ones are untouched, which is REQ-05's second half. |
| SC-09 | **MET** | `check-state.sh` on this tree emits exactly **one** INV-28 line, and it names `FEAT-24-config-responsibility-split` — none of the 23 enumerated ids appears in any INV-28 line. `check-state.sh` exits 1, but on `VIOLATION .harness/harness/features/FEAT-34-worktree-act3-enforced/BRIEF.md is NOT approved`, not on anything from this feature; INV-28 is a `note`, so T-05's "do not change exit behaviour" holds. |
| SC-10 | **MET** | `plan.yaml` `source_issues: [492]`; `feature.json` `github.source_issues: [492]`; `python3 .claude/skills/harness/bin/gh-sync.py closes .harness/harness/features/FEAT-26-pr-linkage-recorded` prints `Closes #492`, rc 0. Caveat: this feature's `feature.json` is modified-uncommitted, so the mirrored value lives in the working tree, not at `bad3244`. |
| SC-11 | **MET** | `open on a plan with no source_issues records none and still succeeds` (:1379) — a PLAN.md-only fixture, rc 0, `source_issues == []`. Ships too: `ship records the pr and then the status` (:1518) runs on a `github` block with no `source_issues` key and reaches `pr == 55`, `status == Done`. Wider regression evidence: every pre-FEAT-26 fixture in `test-gh-sync.py` carries no `source_issues` and the whole file is `ALL PASSED`. |

## The three qa coverage gaps, restated after measurement

1. `--pr N` against an already-recorded different integer — **closed by measurement** (see SC-03).
   Still has no named test case, so it is unprotected against regression.
2. `gh-sync.py:597` — a single-element `pr list` result whose `number` is missing or not a plain
   int. Still unbound; qa's grep of all seven `PR_LIST_JSON` values stands. Not an SC clause.
3. `pr: true` — the bool exclusion in `_record_pr` (`gh-sync.py:562`) and INV-28
   (`check-state.sh:1078`) is unbound in both suites. Not an SC clause; a mutant dropping either
   guard passes both suites.

None of the three keeps an SC from being met. All three are regression-protection holes.

## Accepted costs — not exceeded

- **The Goal's "posts, edits or closes nothing" sentence binds only the renderer.** Delivered work
  matches the accepted cost exactly: SC-06's `closes makes no gh call at all` carries the posting
  clause for the renderer, and no criterion sweeps the other tasks. Nothing here posts, edits or
  closes: the only new GitHub traffic is `record-pr`'s single `gh pr list --state merged` **read**.
- **Board workflows cannot be enabled by the harness.** Untouched by this work; #673 still carries
  detection. Nothing in the diff mentions `projectV2Workflow`.

## Two things the operator should see before the PR

1. **A now-false sentence is corrected only in the working tree.** `.claude/skills/harness/SKILL.md`
   at `bad3244` still reads "the harness composes no issue-closing text into any pull request body",
   which `gh-sync.py closes` falsifies. The correction is an **uncommitted** edit (the fix to T-07's
   line-wrap false green). No SC grades documentation, so this cannot show up as an unmet criterion —
   it has to be committed deliberately, with `feature.json` and `plan.yaml`.
2. **INV-28 has already found live work.** `FEAT-24-config-responsibility-split` is `Done` with
   `pr: null`. Correctly outside this plan's enumeration (another orchestrator owned it), so it is
   not a gap here — it is REQ-04 doing its job on its first real run, and one `record-pr` closes it.

## Open question, unchanged from the build handoff

DEC-186's read-back bound lists four closed purposes and `record-pr`'s `gh pr list --state merged`
is none of them. Both readings are recorded in DEC-200. Widening the bound to five, or ruling the
mirror out of DEC-186's scope, is the operator's call — not blocking the goal-check.

**GOAL MET**
