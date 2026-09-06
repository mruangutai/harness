# Plan fix c2 — R3, R4, R5 and both Q3 cosmetics are in the plan — BUG-1309

**All three rulings are recorded with their derivations, and the plan still routes clean.** Eight
field amendments (T-01/T-02/T-03/T-04/T-05 `intent`, T-04 `verify`, D-08 `choice` and `because`),
ONE new decision (D-09), and two BRIEF clauses. Tasks unchanged at **9**; decisions **8 → 9**.
`approval.status: pending`, BRIEF `## Approval` `pending`, REQ 10 / SC 10, no renumbering, no new
task. Writes went through `plan-merge.py amend --expect-sha256` (a changed value is exit-7 CONFLICT
under `apply`) except D-09, which is a new id and went through `apply --proposal`.

## R3 — one era rule, three refusals, one symbol

`plan.yaml` T-04's absent branch now opens with an ERA GATE ahead of any refusal: a feature whose
directory basename is in `feature_schema.BUILD_ENTRY_ERA_EXEMPT` **continues at exit 0** with one
stderr line (verbatim in the intent, opening `gh-sync: <feat> predates the build-entry receipt`),
and carries no `open` token for the same reason the `recover-terminal` refusal line carries none.
T-05 step 5 gains the same gate **before `build_entry` is read at all**: era member → ALLOW, exit 0,
one stderr line opening `merge-gate: <feat> predates the build-entry receipt`. Both intents state
that the set has exactly ONE definition — the symbol `BUILD_ENTRY_ERA_EXEMPT` in
`.claude/skills/harness/bin/feature_schema.py` (T-06) — read by all three refusals, and that a second
definition anywhere is a defect.

Tests, one PAIR per task, each intent saying that one without the other is a rejected return:
T-04 `T-04 era-exempt continues` (exit 0, stderr contains `predates`, no `REFUSED`) beside
`T-04 non-era absent refuses`; T-05 an era-named fixture ALLOWED beside a non-era fixture DENIED,
the two differing **only in the directory name**, plus an instruction that every other deny case be
staged under a non-era name or it passes vacuously.

D-08 `choice` now says the set governs EVERY refusal this change adds, not INV-37 alone; `because`
names settled bullet 7 (legacy recovery is explicit operator-approved, so a refusal that FORCES it
is not the stated policy) and the out-of-scope merge-policy clause.

**Residual risk:** BRIEF SC-03 and SC-04 still read unqualified ("Build refuses…", "a merge … is
denied"), so an era member satisfies neither literally. The third `## Verification gaps` bullet
already fences the corpus as forward-only, and the dispatch fenced BRIEF edits to SC-01, so this is
raised as Q1 rather than edited.

## R4 — `recover-terminal` adopts; only one contract error refuses

T-03's exit-2-when-milestone-and-parent-exist branch is **gone**. The intent now enumerates the four
adoption cases exhaustively (milestone+parent recorded → creates nothing remotely; milestone only;
parent only; neither), each mirroring `source_issues`, recording `recovered-terminal` and creating
ZERO task sub-issues, with `github.issues` left exactly as found and one `gh-sync: adopting recorded
…` line per adopted part. It names FEAT-55's measured shape as the reason (verified at source:
`.harness/harness/features/FEAT-55-issue-types-created-work/feature.json` → milestone 52, parent
1289, twelve issues #1391–#1402, no `build_entry`) and states that a remedy exiting 2 on the only
feature it exists for is a deadlock. Report-and-ask and `--yes` are unchanged.

**The one remaining exit 2 is a checkable condition, not a category:** `--parent <n>` passed AND
`feature.json` already records a DIFFERENT `github.parent`. The intent lists what does *not* refuse
(recorded milestone, recorded parent, non-empty `github.issues`, an existing `build_entry`).

Tests: the drafted exit-2 case is REPLACED by the FEAT-55-shape adoption case (exit 0,
`build_entry == "recovered-terminal"`, the same twelve ids asserted as a **key set**, and the count
of creating fake-`gh` invocations asserted **== 0**), plus a second-run idempotence case and the
`--parent 999` contract-error case. The pre-existing zero-sub-issue assertions are kept.

**Residual risk:** adoption trusts the local record; a `github.parent` that no longer exists on the
remote is adopted without a lookup. Deliberate — DEC-138 keeps every decision local — and visible in
the adoption line the operator reads.

## R5 — unpinned repo under enabled sync blocks Build

T-02 step 5 splits the two skips: `build_entry="not-applicable"` goes to the **sync-not-enabled skip
and to no other**; the unpinned-repo skip passes a new explicit sentinel `_NO_RECORD` and records
nothing. **The sentinel is load-bearing and step 4 changed with it:** `skip`'s default already
records `recovery-required`, so "pass nothing" could not mean "record nothing" — c1's closing clause
would have written `recovery-required` there. T-01's schema description no longer lists the unpinned
case under `not-applicable` and lists it under ABSENT. BRIEF SC-01 now asserts the blocking
behaviour and demands **key absence**, not a falsy value.

New **D-09** records the ruling with settled bullet 4 and the destination's never-silently-lose
clause, and closes with the disclosure that this was an ambiguity between bullets 4 and 5 resolved on
the operator's behalf, overturnable at signature. T-02's tests: the drafted "repo absent →
`not-applicable`" case is replaced by "sync TRUE + repo unpinned → key ABSENT", explicitly paired
with the sync-false → `not-applicable` case.

## Q3 — both cosmetics

**BRIEF `## Problem`** no longer says the late `open` "would create" anything: it states the measured
fact (FEAT-55 records milestone 52, parent 1289, twelve sub-issues #1391–#1402, created after the
work finished) and that FEAT-55 is **unreported and unterminalized rather than unmirrored**. The
neighbouring "has no mirror" clause was tensed to the merge, since it asserted the same stale claim.

**T-04's `verify:`** no longer greps stdout for `build entry`. It runs the suite (exit status is
honest — `test-gh-sync.py:702-708,3341` counts every `check` failure and exits 1), rejects any
`^FAIL` line, and requires the runner's `ok    <name>` line for three case names the intent declares
a contract. An `ok` line is printed only when the assertion HELD, so the pass depends on assertions.
Probed on synthetic stdout (`/tmp/planfix-c2/probe_verify.py`, throwaway): green only when all three
pass; non-zero when either case is missing, when a case printed but FAILed, when the suite exits 1,
and — the old failure mode — on prose-only stdout containing `build entry`. **No other task's
`verify:` was changed.**

## Verifications

`yaml.safe_load` clean: 9 tasks, 9 decisions, `approval: {status: pending}`, all 9 `verify:` values
still literal `|` blocks, every decision scalar's tail intact (D-09's `because` ends
"…overturn it at signature."). `BUILD_ENTRY_ERA_EXEMPT` is named in T-04, T-05 and T-06 and defined
in exactly one module in all three.

`depends_on` graph — T-01[] → T-02, T-06; T-02 → T-03, T-05; T-03 → T-04, T-07; T-06 → T-04, T-05;
T-04..T-08 → T-09 — walked with a DFS carrying a recursion stack: **acyclic**. Each amended
`verify:`'s inputs were mapped to that graph: T-04's needs the era set (T-06 ✓ dependency) and the
`recover-terminal` cases (T-03 ✓); T-05's needs `feature_schema` (T-06 ✓); T-02's needs the schema
(T-01 ✓). **No `verify:` requires an artifact a later task creates.**

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
DEVIATION T-04 .claude/skills/harness/bin/gh-sync.py, tests/integration/test-gh-sync.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-05: declared main-session-direct (.claude/settings.json, .claude/skills/harness/templates/settings.snippet.json, .omp/extensions/harness-hooks.ts ungranted)
DEVIATION T-06 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/feature_schema.py, tests/integration/test-check-state.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
DEVIATION T-07 .claude/skills/harness/bin/post-merge-sweep.sh, tests/integration/test-post-merge-sweep.py granted to harness-backend-dev, harness-dev-ops, harness-qa but declared main-session-direct
OK T-08: declared main-session-direct (.claude/skills/harness/references/github-mirror.md, .claude/skills/harness/SKILL.md ungranted)
OK T-09 granted to harness-documentor
0 violation(s) across 1 plan(s)
```

Exit 0. Same three DEVIATION rows as c1 — the expected DEC-174 carve-out shape.

## Open questions

- **Q1 (non-blocking).** SC-03 and SC-04 quantify over all features while R3 exempts the era corpus.
  Out of this dispatch's BRIEF scope; the `## Verification gaps` bullet carries the boundary today.
- **Q2 (non-blocking).** T-02, T-03 and T-07 still grep the suite's stdout for a token. Only T-04's
  `verify:` was in scope; the same substitution fits all three if the operator wants it.
- **Not re-graded here.** A separate fresh-context goal-check follows; the c0 and c1 notes are
  unmodified.
