# Simplification angle — FEAT-38 amendment, plan surface — receipt

Scope: `plan.yaml` T-24..T-29, D-13..D-15, the rewritten `verify:` of T-18/T-19/T-20/T-21, and
`BRIEF.md`'s amendment sections (Goal, "Scope was widened", "executable-claims... DELETED",
REQ-10, SC-14..SC-18). Read-only; two findings, both advisory (PASS).

## Q1 — are six tasks (T-24..T-29) the right number?

Per-pair verdict, T-24..T-29 (T-24/T-25 excluded per dispatch — settled lane boundary):

| pair | collapse? | forbidding constraint |
|---|---|---|
| T-25/T-26 | No | `execution_agent` differs: `harness-dev-ops` (T-25, `.harness/harness.json`) vs `harness-backend-dev` (T-26, the two `bin/` files). Hard lane boundary. |
| T-26/T-27 | No | `execution_agent` differs: `harness-backend-dev` vs `harness-documentor`, **and** the dependency runs the other direction — T-26 `depends_on: [T-25, T-27]` (plan.yaml:1839), i.e. T-27 gates T-26, not the reverse. Two independent reasons, either alone forbids it. |
| T-27/T-28 | **No hard lane boundary — flagged below (F1)** | Same `execution_agent` (`harness-documentor`, plan.yaml:1901,1951) and same primary file (`DECISIONS.md`). The only real constraint is a narrower one: see F1. |
| T-28/T-29 | No | `execution_agent` differs: `harness-documentor` vs `harness-pm`. They are also not adjacent in the dependency graph at all — T-29 `depends_on: [T-26]` (plan.yaml:2015), not T-28 — so the two only look adjacent because their ids are consecutive. |

### F1 — T-27/T-28 share a lane; the split is not forced by `execution_agent`, only by a narrow downstream dependency
- **Lines:** T-26 `depends_on: [T-25, T-27]` (plan.yaml:1839); T-27 (plan.yaml:1896-1944); T-28 (plan.yaml:1946-2007), `depends_on: [T-27]` (plan.yaml:1952).
- **Problem:** T-27 (delete the 11 claim markers) and T-28 (delete DEC-205's item 2, repair its heading/intro/closing sentences, regenerate the index) are the same `execution_agent` editing the same file in strict sequence, with no other task's `execution_agent` sitting between them. T-28's own intent explains why the *index regeneration* happens once, after both edits (plan.yaml:2002-2007) — but that reasoning argues for one regeneration, not for two tasks; a single task doing edit-1, edit-2, then regenerating once would satisfy the same intent. The one real reason for the split is narrower than a lane boundary: T-26 depends on **T-27 specifically**, not on T-28 (plan.yaml:1839) — T-26 only needs the claim markers gone, not the DEC-205 text repair or the index regen. Merging T-27+T-28 would force T-26 to wait on unrelated work.
- **Concrete cost:** as written, this is two tasks where one lane boundary check (`execution_agent`) doesn't apply, and the actual justification lives in a fine-grained dependency-graph argument that a reader has to reconstruct from T-28's intent prose rather than from the task boundary itself.
- **Recommendation:** advisory only, not a required change. Either (a) leave as-is and have T-27's intent state the T-26 dependency as the explicit reason for the split (T-28's intent gives the index-regen reason; T-27's does not give the task-boundary reason), or (b) merge T-27+T-28 into one `harness-documentor` task and move `T-26`'s dependency to point at the merged task, accepting the added serialization on T-26. Not a required fix before signature — flagging so pm can pick one deliberately rather than by omission.

## Q2 — any task doing two lanes' work?

No. Checked every new task's `files:` against its `execution_agent`:

| task | execution_agent | files | in-lane? |
|---|---|---|---|
| T-24 | harness-backend-dev | `run-unit-tests.sh` | yes — matches T-19's (done) lane for the same file |
| T-25 | harness-dev-ops | `.harness/harness.json` | yes — matches T-18's (done) lane for the same file |
| T-26 | harness-backend-dev | `check-decision-claims.py`, `test-check-decision-claims.py` | yes — matches T-20's (done) lane for the same files |
| T-27 | harness-documentor | `DECISIONS.md` | yes — matches T-21's (done) lane |
| T-28 | harness-documentor | `DECISIONS.md`, `DECISIONS-INDEX.md` | yes — both docs surfaces |
| T-29 | harness-pm | `notes/research-FEAT-38-bin-argv-class-audit.md` | yes — a `notes/research-*` path is pm's per the standard convention; the 72-file sweep is a read-only classification judgement over `bin/`, not a write into that directory, so it does not cross into backend-dev's or dev-ops's write lane |

## Q3 — verify clause inventory, T-24..T-29

| task | clause | category |
|---|---|---|
| T-24 | claims-name absent from `INTEGRATION_SCRIPTS` | own work |
| | anchors-name present in `INTEGRATION_SCRIPTS` | positive control (sibling untouched) |
| | no `^KIND-DRIFT:` on `--kind integration` | own work (the ordering claim this task is built on) |
| | anchor test's `PASS` line present | positive control |
| T-25 | claims-name absent from `detect` | own work |
| | anchors-name present in `detect` | positive control |
| | `--check-kinds` exits 0 | own work (cross-check both registration sides agree) |
| T-26 | both files absent from index (`git ls-files --error-unmatch`) | own work |
| | both files absent from disk (`test -e`) | own work |
| | `check-decision-anchors.py` still present | positive control |
| | unscoped `git grep -l check-decision-claims` sweep (3 pathspecs excluded) | cross-task — this is the one clause in the set that is neither purely "this task's own work" nor a simple positive control: it grades T-24, T-25, T-26 and T-27 together as a class. The plan's own intent (plan.yaml:1877-1894) names this explicitly and gives the reason (it is the only proof no sixth reference site exists) and the reason it is safe (T-26 `depends_on: [T-27]` makes the sweep run only after both doc-side deletions have landed). Not flagged as excess — it is deliberate and already justified in-line, and DEC-14/SC-14 both rely on exactly this sweep existing somewhere. |
| T-27 | pre-state marker count == 11 at `48bbe7e` | positive control (baseline) |
| | markers absent from current file | own work |
| | `check-decision-claims` name absent from current file | own work |
| | all six DEC headings still present | positive control (over-deletion guard) |
| T-28 | stale "two checks" phrasing absent (heading+intro+closing, one OR-pattern) | own work |
| | stale item-2 phrasing absent | own work |
| | heading now says "one mechanical check" | own work (mirrors the adjacent absence clause — matches the presence+absence pairing this checkout's Expertise P-08 calls out; not redundant) |
| | rule 1 (anchor rot) unchanged | positive control |
| | no second numbered item | own work |
| | generated index diffs clean | own work |
| T-29 | candidate count floor >= 60 | positive control (guards against a silently-empty enumeration) |
| | every candidate has a verdict row | own work |
| | enumeration command literally quoted in the note | own work |

No task's `verify:` is more elaborate than the claim it defends — every clause above is either this task's own assertion or an explicitly-justified control/cross-check. No finding here.

## Q4 — same fact asserted twice through different spellings

### F2 — the claims-test-absence assertion is independently spelled in four places, two of them "done" tasks
- **Lines:** `.harness/harness.json` absence — T-18 (plan.yaml:1362-1369, `done`) and T-25 (plan.yaml:1799-1809). `run-unit-tests.sh` absence — T-19 (plan.yaml:1423, `done`) and T-24 (plan.yaml:1746).
- **Problem:** T-18's rewritten verify and T-25's verify both independently re-derive and assert `test-check-decision-claims.py` (as a literal string) is absent from `.harness/harness.json`'s integration `detect`; T-19's rewritten verify and T-24's verify both independently assert the same literal string is absent from `run-unit-tests.sh`'s `INTEGRATION_SCRIPTS`. That is the same fact, twice per file, in four separately-maintained literal-string spellings. The duplication is deliberately explained in T-18/T-19's intent (the runner cross-checks both registration sides and exits 2 on disagreement, so the already-landed tasks need to keep re-asserting the absence at final state, not just at their own original landing) — it is not a defect in isolation.
- **Concrete cost:** if the literal filename ever needs to change again (renamed, moved), an editor must find and update all four spellings in lockstep. The two "done" tasks are the likeliest to be missed, precisely because their status reads as already landed and closed.
- **Recommendation:** advisory only. No fix is required before signature — removing either T-18/T-19's re-assertion or T-24/T-25's would weaken a gate the qa pass has already accepted (the apply-side rule in `harness-simplify` forbids exactly that trade). Cheapest mitigation, if pm wants one: have T-18 and T-19's verify comments cite T-24/T-25 by id (`# duplicate of T-24/T-25's absence check, kept as the cross-registration control`) so a future editor searching for the literal string finds all four sites from any one of them.

## Q5 — dead references to a deleted shape

Checked (grep over the whole amended `plan.yaml` and `BRIEF.md`):

- `REQ-08` — 6 mentions in plan.yaml (lines 231, 240, 1383, 1451, 1520, 1598), 2 in BRIEF.md (171, 174). All are the tombstone itself or explicit "no longer traces it" statements. None treat REQ-08 as live, and no task's `traces:` list still names it (T-20/T-21 both carry `traces: []` post-amendment). No finding.
- `SC-09` — 2 mentions, both in the tombstone paragraph (BRIEF.md:257-262). No finding.
- The rejected `contains`/`max_lines` declarative redesign — searched for both tokens; the only hits are unrelated English usage ("DECISIONS.md contains...", grep patterns, "output contains the expected substring"). No trace of the rejected redesign shape anywhere. No finding.
- `check-decision-claims`/`test-check-decision-claims` — every one of the ~24 mentions in plan.yaml falls inside T-18, T-19, T-20, T-21, T-24, T-25, T-26 or T-27 (the removal machinery and the corrected historical record of the deleted mechanism itself). None sit in an untouched, stale task. No finding.
- "DEC-205 rule 6b" — appears twice (T-27 intent, plan.yaml:1942; T-28 title, plan.yaml:1947). **Verified against T-03's corrected intent (plan.yaml:394-432), which numbers DEC-205's six top-level rules explicitly and states "the sixth names one mechanical check where it once named two."** "Rule 6b" is that rule 6's second sub-item (the now-deleted "executable claims" half); it is a real, precise internal shorthand consistent with the entry's own structure, not a dead reference to a vocabulary that no longer exists. Checked and cleared, not a finding.

## Verdict

PASS. Two advisory findings (F1, F2), neither blocks signature — both are pre-existing tradeoffs the amendment's own intent text already partially defends; the value here is naming them explicitly for pm rather than leaving them implicit.
