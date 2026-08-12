# STATE

## Current

- feature: FEAT-14-feature-json-schema · phase **build** · status Building
- branch `feat/204-feature-json-schema` · HEAD `22ec98a` · `review_sha` pinned `22ec98a`
- cycles_used **4** of 10 · runs 14 of 20
- **Segment 2 is COMPLETE — all five tasks done. T-08 is the only pending task in the plan,
  and it is the main session's.**

| task | verify at its commit |
|---|---|
| T-03 | exit 0 · `3d37762`, plan record corrected `11d9676` |
| T-11 | exit 0, `0 violation(s) across 10 plan(s)` · `cc6643f` |
| T-05 | exit 0, `--kind integration` exit 0 · `4d3f439` |
| T-09 | exit 0, three mutants each fired · `0a49250` |
| T-10 | exit 0, empty diff, 3 added / 0 deleted · `22ec98a` |

### What T-08 inherits

Its verify greps `feature.yaml` across `.claude`, `.github`, `harness.json`, `team-config.yaml` and
`docs/harness`, skips `docs/harness/DECISIONS*`, and pins only `test-harness-yaml-corpus.py` at 4.
The docs half is now clear — `SPEC.md` 14→0, `org.html` 2→0, `BUILD.md` 11→3 where the three
survivors are the dated records R-01 exempts. **What remains for T-08 is inside its own lane:**
`check-domain.sh` (6) and `test-check-domain.py` (1), both DEC-174 carve-outs, and
`check-plan-routes.py` (3) where `:238` and `:566` rename and `:405` is the dated incident record
R-01 exempts by name. `notes/baseline-check-state.txt` is 0 bytes, which makes T-08's verify demand
**zero** check-state violations after conversion, not merely no new ones.

### R-01 and R-02, applied and proven

**R-01 — the rename splits by tense.** BUILD.md's eight present-tense occurrences renamed; the
`acb8db4` marker at `:335`, the 2026-07-28 fixture record at `:353` and probe D7's definition at
`:357` stand. The narrowing is **by name, not by file and not by count** — proven, not argued:
delete one marker and add one fresh reference and the count stays 3, so a count gate passes it,
while the by-name clause fails on both the missing anchor and the new reference. I reproduced that
in memory against the real file rather than taking it on report.

**R-02 — both dead assertions repaired and each seen to fail.** Re-inserting `phase:` into §11.3
fired the phase assertion; removing `Backlog` from DEC-192's enum fired the vocabulary assertion;
appending a new `feature.yaml` line to BUILD.md fired the rename assertion. All restored
byte-identically. Before the repair neither of the first two could fail at all.

**Decisions taken: DEC-190, DEC-191, DEC-192.** DEC-189 was taken by an unrelated entry between plan
time and now. Gaps at 12 and 161 are isolated singles, not a run.

### The predicted red, unchanged and still not ours

`check-plan-routes.py` reports **35 violation(s) across 16 plan(s)**; `check-state.sh` exits 1 with
15 `has runs/ but no feature.json` violations. Both close at T-08, whose own verify asserts exactly
that. "T-11 closes the 35" is false — measured three ways.

### Q2 CLOSED by measurement — the write guard denies on unexpanded variables

The guard's out-of-repo escape (`bash-write-guard.sh:408-409`) **works**: a fully literal absolute
path outside the repo wrote successfully. The denial fires when the path contains an **unexpanded
shell variable** — the guard reported the target as the literal `$S/probe-literal.txt`, which starts
with neither `/` nor `..`, so `relpath` treats it as repo-relative and the escape never runs. This
is a false POSITIVE, the conservative direction, so it is a usability defect and not a hole. It
explains both denials seen this segment. `bash-write-guard.sh` is a DEC-174 carve-out; FEAT-17's.

## Open Questions

- Q1 non-blocking, **for the goal-check**: the plan's `D-04` cites DEC-189 and `D-08` cites DEC-190;
  both are off by one against what was taken (DEC-190 and DEC-191). Left standing under the
  operator's ruling that citation drift is a goal-check finding, not a silent edit.
- Q2 non-blocking, **for the goal-check**: `SPEC.md:1612` told the orchestrator to leave `status` at
  `in_progress` and not set `abandoned` — two values this feature's own schema rejects. The
  documentor rewrote three lines to "stays where it is / not advanced to `Done`". Kept rather than
  reverted: restoring it would ship a spec instructing an agent to write an illegal file on the same
  page that declares the enum. Reversible, and named here because T-09's intent did not name it.
- Q3 non-blocking, a real gate weakness: `DECISIONS-INDEX.md`'s `⚠ RULING PENDING` sentinel survives
  regeneration, so an index whose rulings were never written passes T-10's verify at exit 0 and
  still reports rows added. `test-gen-decisions-index.py` catches it and was run here at exit 0.
- Q4 non-blocking: the status-loop fixture at `test-check-plan-routes.py:840` writes YAML text into
  a file named `feature.json`. It parses, nothing is red, and no task owns converting it now that
  T-11 is done — the worked example of the old serialisation item 5 exists to delete.
- Q5 non-blocking, measured false three ways: `tests.yml` claims `test-check-plan-routes.py case 25`
  asserts the Plan-route step is present and unneutered. No such test exists, and T-03 added a
  second CI step with the same hole. No task's `files:` authorizes the fix.
- Q6 non-blocking, **closed by measurement**: `gh-sync.py`'s deleted `_strip_github_block` carried a
  corruption incident narrative. The deletion was directed and signed. DEC-131 does **not** preserve
  it — that entry is about orphaned spawns. It survives only in git history at `9cda973`.
- Q7 non-blocking: `check-plan-routes.py:558` still says FEAT-08 "is `awaiting_user` and stays
  checked" in the present tense; FEAT-08 reads `status: Review`. A comment no gate reads.
- Q8 non-blocking: T-11's verify runs `--kind unit`, but `test-check-plan-routes.py` — the file it
  edits — is in `INTEGRATION_SCRIPTS`, so the clause never executes the file the task changes.
- Q9 non-blocking, pre-existing: the guarded-import needle misses `except (ImportError, ...)` and
  `except ModuleNotFoundError`.
- Q10 non-blocking, carried: `validate-digest.py:182`'s orchestrator status enum still carries the
  pre-collapse vocabulary (D-13), so returns say `in_progress`, not a board column.
- Q11 non-blocking, carried: BRIEF SC-08 carries one clause twice; SC-07's prose says "exits
  non-zero" where its test asserts exactly 3.
- Q12 non-blocking: the write guard denies paths containing unexpanded shell variables — see the
  measurement above. FEAT-17-guard-boundaries' territory.
