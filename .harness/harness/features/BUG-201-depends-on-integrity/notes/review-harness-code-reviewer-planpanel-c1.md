# Plan-panel scope review — BUG-201-depends-on-integrity — c1

**BLUF: one MED finding, everywhere else clean.** T-06's fix to `gh-sync.py` `_projected_for`
(the site D-05/SC-09 pin) changes a function with **three call sites**, but T-05/T-06/SC-09 test
**exactly one** of them (`start-task`). A second, live, reachable call site —
`cmd_status`'s `ready` bulk-placement loop (gh-sync.py, inside `if station == "ready":`, the
`_projected = _projected_for(feat_dir, rec)` loop over `numbers`) — gets the same new `refuse()`
with zero test coverage, and it silently converts a documented best-effort bulk write ("a bulk
write must not stop at the first failure", written a few lines below this exact loop for its
`BoardError` sibling) into a hard `exit(2)` mid-loop. This is a *different* defect from the
advisor's settled Q-ADV-3 ruling (which I did not re-argue): Q-ADV-3 says exit-2-on-malformed-plan
is DEC-138-consistent *as a posture*; this finding says the posture, once wired into a shared
helper, reaches an untested caller with a materially different existing contract. The advisor's own
adequacy note flagged `_apply_parent_rule`'s internal call (`:302`) as unmeasured — I traced that one
and it is actually **dead** for this scenario (`cmd_start_task`'s own earlier direct call to
`_projected_for` already exits first, so `_apply_parent_rule`'s call is never reached with a
malformed plan). The live gap is the *other* site the advisor didn't name: `cmd_status`'s `ready`
loop. All ten c0 findings' claimed c1 repairs verified as real against the artifact — none is a
restatement, and none of the ten repairs itself introduced a new defect. `code_grade: n_a` (DEC-207).

## H1 — DAG / verify integrity

Full re-check across all six tasks (T-01..T-06; T-05/T-06 are new since c0's scope pass, which only
covered T-01..T-04):

- **REQ tracing**: REQ-01→T-01,T-03 · REQ-02→T-01,T-03 · REQ-03→T-02,T-03 · REQ-04→T-03,T-04,T-06 ·
  REQ-05→T-05,T-06. No orphan `traces:`, no untraced REQ.
- **DAG**: T-01:[] · T-02:[] · T-03:[T-01,T-02] · T-04:[T-03] · T-05:[T-03] · T-06:[T-05]. Valid
  topological order, no dangling edge, no cycle. `check-plan-routes.py` already confirms this
  mechanically (given: 0 violations, exit 0).
- **`files:` vs same-file conflicts**: T-01/T-04 share `tests/unit/test-plan-depends-on.py`, but
  T-04 transitively depends on T-01 via T-03 — correct sequential ownership (already confirmed at
  c0). No other file is shared by two tasks with no dependency between them (T-05's test files
  and T-06's production files are different paths; T-06 correctly `depends_on: [T-05]`).
- **The specific ask — T-03/T-06 both run `test-factory-claim.py`/`test-gh-sync.py`, T-05 edits
  them**: traced concretely. T-03 (`depends_on:[T-01,T-02]`, before T-05 ever runs) executes those
  two suites in their **pre-T-05** state — a pure regression check, since T-03 touches only
  `harness_yaml.py` and changes neither file's behavior. T-05 (`depends_on:[T-03]`) is the
  designed-red half: its own `verify:` is expected to FAIL at landing (T-03's rule now makes
  `load_plan` raise on the fixture, but `factory_claim.py`/`gh-sync.py` are still unfixed) — this
  matches the intent's explicit "Both commands FAIL until T-06 lands... record the literal FAIL
  lines you observe," the same TDD shape c0 already accepted for T-01/T-02. T-06
  (`depends_on:[T-05]`) then runs the **post-T-05** versions of those two suites, after fixing the
  production files, and all 8 named suites should be green. **The ordering the verify overlap
  implies IS fully expressed in the DAG; every task's `verify:` can pass (or is designed to fail)
  exactly when the DAG says it lands.** No defect. (Minor, non-gating: T-03's and T-06's 8-suite
  `&&` chains mean an unrelated failure in an early suite masks whether later suites in the same
  chain would have passed — a generic chained-verify property already present pre-c1, not
  reported as a finding.)
- No `verify:` names a file no predecessor creates; no `verify:` asserts something a predecessor
  deletes.

**H1 finding count: 0.**

## H2 — SC-01..SC-09 wording, graded in isolation

| SC | grade | why |
|---|---|---|
| SC-01 | clean | Names mechanism (`validate_plan_doc`), exception class, and both ids exactly. Read in total isolation from T-01's own suite, a hard-coded special case for literally `T-02`/`T-99` would satisfy SC-01's one example — but that gap is closed by T-01's paired-allow and mixed-type cases living in the same evidence file; not a wording defect on its own. `info`. |
| SC-02 | clean | Exit EXACTLY 5 + `ILLEGAL PLAN` + `T-99` + sha256-unchanged, AND the paired allow at exit 0, AND exit 9 explicitly excluded — closes both the deny-everything loophole and the unresolved-`--file` loophole PF-6dda61 found at c0. Verified genuinely repaired (see H3). |
| SC-03 | admits a narrow misgrade of a correct build | The floor (`>= 67`) is a *point-in-time measurement of the ambient corpus*, not a property of this feature's code. If the repo's committed-feature-plan count ever drops below 67 for reasons unrelated to this feature (archival, cleanup), a structurally correct depends_on-integrity implementation reads as failing SC-03 purely on corpus size. Distinct from c0's PF-7beea1 (which was about floor-vs-equality, already fixed). `low`, non-blocking — a future staleness risk, not a defect in this build. |
| SC-04 | under-specified for its own `verify: inspection` | "a reviewer greps the reviewed tree for the check and finds it once" never names what string/symbol to grep for. Read in isolation (the explicit ask for SC-04/SC-05) an inspector cannot execute this without importing T-03's intent, which does name the helper (`_validate_plan_depends_on`) — a reader with only SC-04's sentence has no discriminating search term. `low`. |
| SC-05 | reasonably concrete | Enumerates exact case numbers (T-01 cases 1,3,5,6c) an inspector can check against the recorded run's FAIL lines; closes PF-cc2bcf's "any cause" gap for real (see H3). One residual, generic risk: the *exact*-match requirement means an unrelated flaky extra failure in the same run would misgrade an otherwise-correct build as not satisfying SC-05 — inherent to any exact-enumeration criterion, not specific to this wording. `info`. |
| SC-06 | clean | All three named `unit` suites verified present, by literal grep, in both T-03's and T-06's `verify:` blocks. |
| SC-07 | clean | All four named `integration` suites verified present, by literal grep, in both T-03's and T-06's `verify:` blocks. |
| SC-08 | clean | Cross-checked against live source: `_blocker_reason_text`'s `no_plan` branch DOES literally contain the substring "no plan could be read" today (`factory_claim.py`, both the root-missing and the directory/file-unparseable variants) — so SC-08's "does NOT contain 'no plan could be read'" is a real, currently-failing (pre-T-06), post-T-06-required discriminator, not a phrase invented by the BRIEF. Confirmed at source, not assumed. |
| SC-09 | wording undercounts the mechanism it pins — the one MED finding | "reports the real cause at both of its sites" is true only for the two invocations T-05/T-06 actually test (`start-task`→`_projected_for`, `status Ready`→`_status_plan_doc`). `_projected_for` has a **third, live, untested call site**: inside `cmd_status`'s `ready` branch (the bulk placement loop over `numbers`, gh-sync.py — separate from the `_status_plan_doc`-gated approval check a few lines earlier in the same function). An **approved** plan that later carries a dangling `depends_on` (issue #201's own motivating scenario — a hand-edit or a revision typo surviving signature) passes `ready`'s approval guard, reaches this loop, and after T-06's fix hits the new `refuse()` mid-loop — turning a documented "a bulk write must not stop at the first failure" contract (stated in this same function for its `BoardError` sibling) into a hard process exit that aborts placement for every *other*, unrelated sub-issue in the same transition. Neither T-05's nor T-06's case list (a–g) exercises `status Ready` with **multiple** recorded sub-issues, nor `cmd_status`'s `ready` branch specifically (only the earlier approval-guard exit, which SC-09 itself already correctly excludes as insufficient for a different reason). I separately traced the advisor's own flagged site, `_apply_parent_rule`'s internal call (`:302`) — it is **not** live for this scenario: `cmd_start_task`'s own direct call to `_projected_for` (used to place the task's own card) already exits first on a malformed plan, so `_apply_parent_rule`'s later internal call is dead code on this path. The live gap is the `ready`-loop site, not the one the advisor's adequacy note named. **This is not a re-argument of Q-ADV-3** (whether exit-2-on-malformed is DEC-138-consistent, settled) — it is that the fix, applied once to a shared helper, silently reaches a caller whose pre-existing contract SC-09/T-06 never examined. `med`. |

## H3 — c0 finding repair verification (verbatim disposition claims from the goal-check note, checked against the artifact)

| id | c1 claim | my verification | verdict |
|---|---|---|---|
| PF-d26198 (Q-A) | delivered | `BRIEF.md` REQ-05 names all three sites with `af859ee8` line citations; `plan.yaml` D-05 gives each site its own posture; T-05/T-06 implement it. Source-verified: the cited `factory_claim.py`/`gh-sync.py` lines match the live code exactly (I read them directly). | REAL, delivered |
| PF-6dda61 (SC-02) | repaired | `BRIEF.md` SC-02 now requires exit EXACTLY 5 + `ILLEGAL PLAN` + `T-99` + sha256-unchanged + the paired allow at exit 0, and explicitly excludes exit 9 — closes both the deny-everything and the unresolved-`--file` readings the c0 finding named. | REAL repair |
| PF-cc2bcf (SC-05) | repaired | `BRIEF.md` SC-05 now requires import success, paired-allows passing in the same run, and names the exact FAIL set (cases 1,3,5,6c) — an "any cause" FAIL no longer satisfies it. | REAL repair |
| PF-e9eff4 (REQ-04 2nd half) | repaired | `plan.yaml` T-03's `verify:` block (8 lines, `&&`-chained) and T-06's `verify:` block (8 lines) both literally include `test-check-plan-routes.py`, `test-gh-sync.py`, `test-factory-claim.py`, `test-harness-yaml.py`, `test-plan-merge.py` — read directly, not assumed. `BRIEF.md` SC-06/SC-07 bind them by name. | REAL repair |
| PF-4e8683 (D-03 lane) | repaired, then SETTLED by advisor ruling | Advisor Q-ADV-2 (2026-09-07) ruled T-03/T-06 both stay `team`; binding, not re-argued here. | SETTLED, not re-opened |
| PF-4f9180 (exit-2 surface, info) | unchanged-deliberately | No artifact edit was needed for an info-severity, non-blocking observation; correctly left as-is. | Acknowledged, appropriately not "fixed" |
| PF-092cbd (self-dep sentence, info) | repaired | T-03's intent carries the verbatim "NON-NORMATIVE NOTE... NOT a behaviour to implement... Write no branch, no special case and no test for it" block — read directly in `plan.yaml`. | REAL repair |
| PF-7beea1 (SC-03 count) | repaired | `BRIEF.md` SC-03 is now a floor-with-provenance (67 committed at `af859ee8`, 68 in this worktree, "never an equality... a corpus that has grown does not [fail]"). | REAL repair (see also SC-03's *new*, narrower staleness note in H2 above — not the same gap PF-7beea1 named) |
| PF-3116cd (T-01 case 6, low) | repaired | T-01 case 6 in `plan.yaml` is the full a/b/c mixed-type structure plus the explanatory "THE VARIANT THIS CASE CATCHES" paragraph naming the one-side-coercion defect — read directly, matches the c0 ask verbatim. | REAL repair |
| PF-e159de (non-list widening, info) | unchanged in plan, strengthened in BRIEF | `BRIEF.md` `## Constraints` carries the "ONE DECLARED WIDENING... Measured in this worktree on 2026-09-07: zero of the 68 live `plan.yaml` files..." paragraph — read directly. `plan.yaml` T-01 case 5 / T-03 unchanged, as claimed. | REAL addition, correctly scoped |

**All ten claimed c1 dispositions verified against the artifact — none is a restatement, and none of
the ten repairs itself introduced a new defect.** The one new item I found (SC-09/`_projected_for`'s
third call site) predates this repair cycle; it is a gap in the original T-06/SC-09 design that
neither c0 nor the c1 rewrite touched, surfaced by the advisor's own adequacy note and confirmed
concrete here.

## Findings

1. **[med]** `gh-sync.py` `_projected_for`'s fix (T-06) reaches an untested, live call site —
   `cmd_status`'s `ready` bulk-placement loop — where the new `refuse()`/exit(2) silently overrides
   a documented best-effort bulk-write contract. Failure scenario: an already-**approved** plan
   whose `depends_on` is later corrupted (hand-edit, or a pre-signature typo that predates this
   feature) reaches `gh-sync status <feat> Ready` with multiple recorded sub-issues; today every
   card that CAN be placed gets placed and the rest print "no station follows" and continue; after
   T-06, the loop hard-exits at the first malformed read and every subsequent sub-issue's card in
   that same `ready` transition goes unplaced with no diagnostic for them. No SC or task exercises
   this branch. See SC-09 row in H2 for the full trace (including why the advisor's own named site,
   `_apply_parent_rule:302`, is *not* actually live for this scenario).

No other findings. H1 is clean; SC-01/02/06/07/08 are clean; SC-03/04/05 carry only `info`/`low`
wording notes that do not admit a materially wrong implementation or misgrade a correct one in any
way that changes the shipped behavior.

## Open questions

None from this lens — the one substantive gap above is reported as a finding, not a question, since
it is independently checkable and I did check it.

```yaml
VERDICT: PASS
DIGEST:
  headline: One MED finding — T-06's _projected_for fix reaches an untested third call site (cmd_status's ready bulk loop) that silently converts a documented best-effort bulk write into a hard exit; all ten c0 repairs verified real; H1 DAG/verify integrity and SC-01/02/06/07/08 clean.
  severity_max: med
  findings: 1
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity/.harness/harness/features/BUG-201-depends-on-integrity/plan.yaml"
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity/.harness/harness/features/BUG-201-depends-on-integrity/notes/review-harness-code-reviewer-planpanel-c1.md
```
