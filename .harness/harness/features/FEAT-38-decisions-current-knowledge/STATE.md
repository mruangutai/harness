# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: `2026-08-30-ship-close-orchestrator` — the ship closing sequence
- squad: none. Orchestrator-held; no lead was dispatched in this run
- status: **Review**, PR **#996** OPEN and **CONFLICTING**. **NOT merged. NOT shipped.**

**THE CLOSING SEQUENCE STOPPED AT THE MERGE, AND THE REASON IS INTEGRATION, NOT QUALITY.** Every
gate this feature owns is green and SC-13 is answered. PR #996 cannot merge because the branch
conflicts with `origin/main` in three files. No board card was moved, the milestone was NOT closed,
and `gh-sync.py ship` was deliberately NOT run — writing `Done` for work that did not merge would
falsify the record.

**THE PREMISE "0 COMMITS BEHIND MAIN" WAS MEASURED AGAINST A STALE, DIVERGENT LOCAL `main`.** That
is the single fact that inverted this run's outcome:

- `main...HEAD` → `0 52`. True, and misleading: the branch merged LOCAL `main` at `d04be92`.
- `main...origin/main` → **`2 19`**. Local `main` is 2 ahead and **19 behind** the remote.
- `origin/main...HEAD` → **`19 55`**. The real merge-base is `7ebfc9e`, the feature's ORIGINAL base,
  not `7a23d74`.

**The 19 upstream commits are FEAT-44** (OMP-native context advisory, PRs #982 and #995), which
shipped while FEAT-38 was in flight and touched three of the same files.

**The three conflicts, measured with `git merge-tree --write-tree origin/main HEAD`:**

- `.claude/skills/harness/bin/run-unit-tests.sh` — both features registered new test scripts
- `.harness/harness.json` — both edited `test_kinds`
- `.harness/harness/docs/DECISIONS-INDEX.md` — a GENERATED file; FEAT-44's `57333d0` regenerated it
  after amending DEC-198, DEC-201 and DEC-159

`.harness/harness/docs/DECISIONS.md` itself **auto-merges cleanly**. The feature's own subject
matter is not in conflict.

**The two local-only `main` commits are `16f86e3` (grill FEAT-46) and `7a23d74` (hold FEAT-46 until
FEAT-38 ships).** They are unpushed, and because the branch merged local `main`, **PR #996 carries
them**. Nobody intended FEAT-46 material to ride this PR; it is stated so the resolution decides it
deliberately.

**Resolution is NOT this orchestrator's to perform.** It needs `origin/main` merged into the branch
— a HEAD move that `bash-write-guard.sh` refuses for every governed agent, correctly. It also
changes source files under the pin, so `review_sha` `635cd3ba` would no longer describe the merged
tree and the qa gate would need re-running against the resolved tree. That is a validate cycle, not
a closing step.

**SC-13 IS ANSWERED — that blocker is genuinely gone.** `notes/uat-FEAT-38.md` reads
`status: passed`, answered by the operator on 2026-08-30 on their own reading of DEC-138, DEC-174
and DEC-181, each marked `pass. true today`, with the cross-cutting question answered `pass —
nothing considered settled has disappeared`. The file keeps the verdict history rather than
overwriting it: an initial `failed` instruction was reversed by the operator after reading the
entries. **The pass is scoped** — it asked only whether each entry reads as current truth, never
whether an entry is a decision at all or is in clause form. FEAT-46 sets that standard and all three
entries are in scope for its triage; this pass must never be cited to exempt them.

**Everything else was already closed and none of it was re-run here.** Goal-check 17 of 17 live
criteria met. The blocking qa gate PASSES (`matrix_ok: true`, `must_fix: []`, suite exit 0, all 55
registered scripts run). The four-reviewer panel PASSES at the pin, `severity_max: low`, no
`must_fix`.

**`review_sha` `635cd3ba` was still valid against the branch tip and was NOT re-pinned.** Of the 16
files changed between the pin and `d04be92`, 13 are under this feature's own directory and the other
three are two `.harness/logs/` entries and a grilling note. Zero source files. **This validity
statement is about the branch as it stands; a conflict resolution against `origin/main` voids it.**

**What this run did do.** Pushed the branch (it had never been pushed — `d04be92..6be4e0b` now on
the remote). Opened PR #996. Recorded `pr: 996` through `gh-sync.py record-pr` rather than by hand.
Wrote the handoff and the ship review. Set `status: Done` in anticipation of the merge and
**reverted it to `Review` when the merge proved impossible.**

**Budget: cycles 16 of 30; runs 34 of an informational 20.** Neither moved in this run — no rework,
and an orchestrator-held segment is not a squad run. The count is informational and stops nothing.

## Open Questions

**BLOCKING — the main session's or the operator's, not any squad's:**

- **PR #996 conflicts with `origin/main` in three files and cannot merge.** Someone with the
  authority to move HEAD must merge `origin/main` into the branch and resolve
  `run-unit-tests.sh`, `harness.json` and the generated `DECISIONS-INDEX.md` — the last is
  regenerated, not hand-merged. Then re-run the blocking qa gate and re-pin `review_sha`, because
  the resolution changes source files the panel graded.
- **Decide whether PR #996 should carry the two FEAT-46 commits** it inherited from the local
  `main` merge, or whether they are split out first.
- **Local `main` is 2 ahead / 19 behind `origin/main`.** Independent of this feature, and it is what
  made a stale measurement look authoritative.

**Carried to the operator as proposed backlog** in `notes/ship-review-2026-08-30-ship-close.md`,
which also carries the non-backlog residuals. Anything not accepted there dies silently:

- **B-25 — `bash-write-guard.sh` cannot expand shell variables and does not track `cd`.** It
  resolves targets against the session root, so `cd <dir> && sed -i '' … plan.yaml` and
  `sed -i '' … "$P"` were denied "outside your domain" while the identical command with a literal
  absolute path was allowed — and `check-domain.sh --resolve` grants that path. Two surfaces
  disagree.
- **B-26 — `/usr/bin/grep` is `pi-uu-grep 0.2.0`, in which `^+` matches EVERY line.** Four false
  readings across this feature, including an apparent 83 insertions against a true `--numstat` of
  zero. Every affected measurement was redone in Python.
- **B-39 — a run-directory slug collision destroyed a record.** The T-27 lead wrote into
  `runs/2026-08-29-01-product`, already the panel-revision run's directory, overwriting its
  `digest.md` and `state.yaml`. `runs/` is gitignored, so it was unrecoverable. Nothing in the
  run-directory contract stops a lead choosing a slug that already exists.
