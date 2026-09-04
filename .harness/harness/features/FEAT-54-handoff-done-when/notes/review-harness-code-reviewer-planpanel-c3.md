yield# Plan-panel review (scope reader) — FEAT-54-handoff-done-when — cycle 3

## Conclusion

Both ACCEPTED rulings (PF-570b9c87, PF-918326) landed correctly and completely in the plan's
MECHANISM. No permanent (`UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS`) test case scans the real repository
tree or compares mtime/bytes of a real feature note anywhere in `plan.yaml`/`BRIEF.md`. Neither
ruling broke anything I can trace. Both REJECTED findings' subjects are untouched. **One real gap
remains, unfixed by this cycle: the plan's own `panel.findings[]` RECORD is stale** — it still
says "no operator ruling exists" for all four settled rulings, three cycles after two of them were
ruled. This corroborates the goal-check note's own Q3/F-06 exactly; I re-derived it independently
via `grep`, not from trusting that note. No must-fix; `severity_max: med`, advisory only.

## 1. The two ACCEPTED rulings — mechanism check, independent grep sweep

I swept `plan.yaml`+`BRIEF.md` myself for `mtime|byte-identical|real (repo|tree|project|corpus|
feature note)|unmodified|actual project root` (not trusting pm's or goal-check's tables) and
classified every hit:

| Site | Kind | Permanent suite member? | Verdict |
|---|---|---|---|
| `plan.yaml:522-529,542-543` T-06(g) | fixture-root scan + fixture mtime/byte check | yes (`test-check-state.py`, INTEGRATION_SCRIPTS) | **clean — fixture only, never the real tree** |
| `plan.yaml:566-573` T-07 `verify:` | runs `check-state.sh` over the real repo | **no — one-shot task verify, run once when T-07 lands, never re-run by the suite** | clean |
| `plan.yaml:610-613` T-07 intent tail | prose describing that same one-shot verify | no | clean |
| `plan.yaml:841-842` T-11 `verify:` | reads this feature's own real notes | no — same one-shot-task-verify class | clean |
| `plan.yaml:724-726` T-09 intent | "byte-identical" of two JSON keys | not a note, not a corpus scan | clean |
| `BRIEF.md:118-121` SC-08 | "left byte-identical" — comment text in gate scripts | not a note file | clean |

**No entry I found sits in `UNIT_SCRIPTS`/`INTEGRATION_SCRIPTS` and reads the real tree.** The
discriminator that makes T-07's and T-11's real-tree reads non-violating is structural, not a fact
about today's tree: they are `verify:` blocks on plan **tasks**, executed once at build time by
the executor, not test files registered in `run-unit-tests.sh`'s arrays — so they cannot redden
`test-check-state.py` when a concurrent feature writes a pre-sweep note, which is the exact failure
mode PF-570b9c87 named. **CORROBORATES** goal-check §3(a)'s table and its per-site verdicts.

**SC-04 executability.** Concrete command (`bash check-state.sh` at `review_sha` from repo root),
concrete falsifier (any reported line naming "Done when"). **Executable: yes.** Checkable that it
was executed: **partially** — SC-04 (`BRIEF.md:89-99`) says the reviewer "records in the review
record" without naming a target path. This is not a defect unique to SC-04: none of SC-07, SC-08,
or SC-11 (the BRIEF's other `inspection` criteria) pin a location either; by this repo's own
handoff convention the location is a reviewer's own `notes/review-<self>-*.md`. **CORROBORATE
goal-check Q1** as a real but non-novel, non-blocking ambiguity — info, not a finding on its own.

## 2. Did applying the rulings break anything?

- **T-06's `verify:` vs rewritten (g) and the red/green paragraph** (`plan.yaml:492-495`,
  `:545-549`): the task-level shell verify only checks `rc != 0` and greps `'done when'` in output
  — indifferent to which case fails, so (g)'s rewrite cannot desync it. The red/green paragraph
  claims (g) is green both before and after: before T-07 lands, `check-state.sh` doesn't parse
  "## Done when" at all, so it structurally cannot report a "Done when" line against (g)'s fixture,
  and the scan is read-only either way — consistent, not broken.
- **SC-04 vs REQ-07/REQ-10**: REQ-07's new-note carve-out is satisfied because T-11 lands before
  `review_sha` is pinned, so this feature's own notes already carry the section by the time SC-04's
  reviewer runs the check. REQ-10 ("deterministic checks... run in the permanent gates") is
  satisfied by `check-domain.sh`/`check-state.sh` themselves being the permanent gates (T-04, T-07);
  SC-04 is a one-time confirmatory run at review, not a substitute for that. No conflict.
- **T-09's verify vs the real `test_kinds` shape** — read directly at
  `.harness/harness.json:105-159` (not trusted from the plan): 8 existing kinds, every one carrying
  `exclude`; `omp_session_accessor.exclude == ".claude/worktrees/**"` exactly, byte-for-byte the
  literal T-09's verify asserts (`plan.yaml:688`). **CONFIRMED at source, matches goal-check §3(b).**
- **D-10's amended `because` vs D-01, D-03, T-07**: D-10's tail (`plan.yaml:177`, verified whole and
  unbroken by `grep`, not visually truncated on disk) adds only a record clause — no new mechanism.
  D-01 (`plan.yaml`, amended at c2c) already defers to D-10 and says "GRAMMAR... never target
  resolution," consistent with D-10's new "stable contract" clause. D-03 fixes the four types and
  their grammar; D-10's new clause only states that a future rename/narrow is a new decision, which
  doesn't touch D-03 as written. T-07's intent explicitly keeps grammar-only checks in the persisted
  pass "because a typed prefix consults no target and so cannot rot" — the identical rationale D-10
  now records. No contradiction anywhere I can trace.

## 3. Record honesty — one real, non-novel gap

**`plan.yaml:50-52` (PF-570b9c87) and `:60-62` (PF-918326)** still read verbatim: *"disposition:
open - no operator ruling exists for this finding; both c2 readers... independently re-derived it
as STANDING against the revised plan..."* — this is now **false**: the shared context confirms both
were ACCEPTED, and their mechanism (T-06(g), T-09's `exclude`) is implemented in this same file.
**`plan.yaml:69-71` (PF-d0ea19ff)** and **`:93-96` (PF-bd92960a)** carry the same stale "open"
framing for their REJECTED rulings. Contrast with `plan.yaml:29-32` and `:40-42`
(PF-4205e7e2, PF-1e45eb3a), whose dispositions WERE updated at c2 to say "ACCEPTED by the
operator..." / "REJECTED by the operator...". The same repair was not applied to the four c3
rulings. **CORROBORATES goal-check §6 F-06 and Q3 exactly** — I re-derived this myself via
`grep 'disposition:'` before reading goal-check's own table, so this is independent confirmation,
not inheritance. Concrete failure scenario: the operator reads `panel:` at the signature gate,
sees four "open — no ruling exists" lines for rulings they already made in this same session, and
either re-adjudicates work already done or loses confidence the ruling landed, delaying signature.
Not a re-raise of any of the four settled rulings themselves — only their disposition transcription
is stale. Per the dispatch's constraint I have no write access to `panel:`; this is advisory to
whoever holds that pen (pm, main-session), and both pm's own note and goal-check already flagged it
as deferred. Severity: **med** (consistent with the precedent set at c2, where the same defect
class against PF-4205e7e2 alone was rated med).

**Q2 corroboration**: `plan.yaml:3-4` `approval:` is exactly `{status: pending}` — no `rulings:`
key exists anywhere in the schema. Confirms goal-check Q2's premise; nothing to add.

## 4. Anything new

Nothing at any severity beyond §3. `depends_on` is acyclic and unchanged from c2 (delta touched
only T-06, T-09, D-10, SC-04 per the object-diff both pm and goal-check report); all 10 REQ ids are
traced by at least one task; no task's `traces:` cites a nonexistent REQ.

## Clearances, and what each rests on

- **No permanent suite case reads the real tree or compares real-note mtime/bytes** — STRUCTURAL:
  rests on the task-verify-vs-registered-test-file distinction (§1), not on today's tree state.
- **SC-04 is executable** — STRUCTURAL: a concrete command and a concrete falsifier, independent of
  what the corpus currently contains.
- **T-09's `exclude` literal matches convention** — TODAY'S-TREE fact: I read
  `.harness/harness.json:105-159` directly. If a future edit to that file changes
  `omp_session_accessor.exclude`, T-09's own hardcoded assert (`plan.yaml:688`) is unaffected — it
  does not read the sibling kind at runtime — so this clearance's functional half is structural;
  only the plan's stated RATIONALE ("exactly the value omp_session_accessor carries") depends on
  today's config.
- **D-01/D-03/D-10/T-07 consistency** — STRUCTURAL: read from the decision and task texts
  themselves, not from repo state.
- **REQ traceability (10/10) and `depends_on` acyclicity** — STRUCTURAL, unchanged since c2.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Both ACCEPTED rulings landed correctly and completely in mechanism, with no permanent test case scanning the real tree; neither ruling broke anything traced; the plan's panel.findings record is still stale on all four settled rulings' dispositions, corroborating goal-check Q3/F-06 independently — advisory, not gating."
  severity_max: med
  findings: 2
  must_fix: []
  spec_violations: []
  reviewed: "plan:/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/plan.yaml"
  code_grade: n_a
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-54-handoff-done-when/.harness/harness/features/FEAT-54-handoff-done-when/notes/review-harness-code-reviewer-planpanel-c3.md
```
