# SIMPLIFICATION angle — plan.yaml / BRIEF.md — BUG-1286-test-tree-enforcement

**BLUF: one real finding.** T-05's DECISIONS.md-amendment intent (plan.yaml:316-333) hand-copies
D-01/D-02/D-03/D-04's clauses verbatim into prose instead of pointing at the decisions block; if pm
revises any of those decisions after T-05's text is drafted, the amendment ships the stale wording.
Everything else checked — dead-reference citations, SC bundling, task files/traces/change_type —
comes back clean.

## Check 1 — same fact asserted twice through different spellings

D-01's vocabulary (`test-*`/`test_*`/`*_test.*`/`*.test.*`/`probe-*`, extensions `.py .sh .ts .tsx
.js .mjs .cjs`) is spelled out in D-01 (plan.yaml:36-39), as the `NAME_PATTERNS`/`SOURCE_EXTENSIONS`
code constants in T-01 (plan.yaml:115-116), and again in prose in T-05's amendment bullet 1
(plan.yaml:316-319). D-03's three-part activation condition (`.git` entry, toplevel == root, index
carries `suite_layout.py`) is spelled out in D-03 (plan.yaml:58-60), decomposed across T-01's three
separate implementation steps (plan.yaml:135, 129-131, 139-141), cross-referenced by attribution in
T-02 ("the predicate requires this to enforce repository-wide, per T-01", plan.yaml:204), and
restated in full in T-05's amendment bullet 3 (plan.yaml:323-326).

- T-01's copy is **load-bearing and must stay**: it is the actual code spec a different reader
  (the implementer) needs to act on — decomposing D-03's condition into three concrete steps is not
  duplication, it is translation from decision to implementation.
- T-02's copy is a one-clause attribution, not a restatement — it does not carry the predicate's
  wording, only points at T-01. No finding.
- T-05's copies of D-01 and D-03 are the one pair that can drift and has no attribution back to the
  decisions block — see Check 2, which covers the fix for both.

**finding** (folded into Check 2 to avoid double-reporting the same fix).

## Check 2 — a rule restated in two places that can drift

**finding.** T-05's intent (plan.yaml:310-335) hand-transcribes D-01, D-02, D-03 and D-04 clause by
clause into the DECISIONS.md amendment paragraph, rather than instructing the documentor to read the
decisions block at write time. D-01 is the authoritative source (plan draft, still open to revision
by pm before signature); T-05's copy is derived. If any of D-01 through D-04 is revised after T-05's
intent text is drafted — plausible, since three other angle-reviewers are running against this same
draft right now — the documentor executes T-05's stale clause-by-clause text into a signed
DECISIONS.md paragraph, and nothing catches the mismatch: T-05's verify only greps for the "Amended
by" marker line and diffs the regenerated index, neither of which checks the amendment's prose
against the current decisions.

Concrete cost: a governing record (DEC-213) that describes a decision as it read at plan-draft time,
not as pm actually signed it — exactly the staleness REQ-07 exists to prevent.

Replacement wording for plan.yaml:316-333 (T-05 intent), weakest statement that keeps the amendment
correct without re-stating each clause:

```
Append an amendment paragraph to DEC-213, in the house style used at DECISIONS.md lines 4908, 5296
and 6174, opening with
"**Amended by BUG-1286-test-tree-enforcement — the predicate's reach, not its principle.**"
and stating, as the current contract, what decisions D-01 (vocabulary), D-02 (exception registry),
D-03 (tracked-set activation) and D-04 (bin clause retention) read in THIS PLAN'S DECISIONS BLOCK AT
THE TIME YOU WRITE THIS TASK — restate their current wording, not any wording captured elsewhere,
since a later revision to any of D-01 through D-04 supersedes this paragraph's draft rather than the
other way around. Also state that the paragraph beginning "What this does not do" still holds for
bin support modules such as layout_fixtures.py, which is not test-shaped and needs no exception.
```

## Check 3 — dead references to a shape that no longer exists

**no finding.** Every citation checked against the pinned SHA tree lands exactly where claimed:
- BRIEF.md's `suite_layout.py:20-33` (Problem section) — lines 20-28 are the `tests/` clause and
  29-33 the bin clause, matching "only looks in two places."
- D-05's `tests/manual/probe-omp-session-accessor.py` lines 54-55 — exactly the `PROBE = (...)`
  path assignment the decision describes.
- T-05's DECISIONS.md house-style exemplars at lines 4908, 5296, 6174 — all three open with
  `**Amended by <feature> — <clause>.**`, matching the wording T-05 is told to follow.
- `suite-census.py`'s `baseline()` helper and `add_*_parser` table — pre-verified by the
  orchestrator at the pinned SHA; not re-derived here per dispatch.

## Check 4 — carrying weight it does not need

Read hardest: SC-05, SC-06, SC-11, SC-12.

**finding — SC-05** (BRIEF.md:72-75). Bundles two independent claims: (a) a fixture with valid
`tests/unit/**`/`tests/integration/**`/`tests/manual/**` files produces no violations, and (b) no
`active` entry in `.harness/harness.json` `test_kinds` matches `tests/manual`. Claim (b) is already
asserted by the Constraints section's "Unchanged surfaces, committed: `.harness/harness.json`
`test_kinds`" (BRIEF.md:53). If (a) passes and (b) fails (or vice versa), SC-05 reports one failure
that conflates a code-behavior regression with a static-config regression — unreportable which one
broke. Split:

```
SC-05: A fixture holding valid `tests/unit/**`, `tests/integration/**` and `tests/manual/**` files
produces no violations.
verify: automated        evidence: unit
```
Drop the `test_kinds` clause from SC-05 — it is redundant with the Constraints line and, since
nothing in this feature's `files:` lists touches `harness.json`, is already covered by "unchanged
surfaces" rather than needing its own SC.

**finding — SC-06** (BRIEF.md:76-78). Bundles (a) the real repository root produces no violations,
and (b) `layout_fixtures.py` stays present and unmoved. These are independent: a violations-count
regression and a file-relocation regression are different failure classes, and a reviewer reading
"SC-06 failed" cannot tell which without opening the evidence. Split:

```
SC-06a: The real repository root produces no violations at the reviewed revision.
verify: automated        evidence: unit
SC-06b: `.claude/skills/harness/bin/layout_fixtures.py` remains present and unmoved.
verify: automated        evidence: unit
```

**finding — SC-11** (BRIEF.md:97-100). Bundles three independent claims: (a) `git diff` at
`review_sha` changes neither `.harness/harness.json` nor the mutation-snapshot scope, (b) the
predicate's repository-wide clause is inert on a root that doesn't track `suite_layout.py` itself.
(a) is a diff-inspection claim over two unrelated files; (b) is a behavior claim already covered by
T-01 test case 5. Bundling triples the failure surface into one unreportable criterion. Split:

```
SC-11a: `git diff` at `review_sha` changes neither `.harness/harness.json` nor the mutation
snapshot's scope.
verify: inspection
SC-11b: The predicate's repository-wide clause is inert on a root that does not track
`suite_layout.py` itself, so a product checkout's own test discovery is untouched.
verify: automated        evidence: unit
```

**no finding — SC-12** (BRIEF.md:101-104). Its two clauses ("directory and bin clauses still report
their violations" and "the repository-wide clause contributes nothing") are one coherent behavior —
T-01 test case 5 exercises both with a single fixture (`legal_tree()`) precisely because they are the
same claim ("the new clause does not interfere with the existing non-git path"), not two independent
subsystems. Splitting would separate two assertions of one invariant for no gain.

## Check 5 — files/traces/change_type carrying an unneeded entry

**no finding.** Every task's `traces:` maps to intent content actually present: T-01's REQ-08 trace
is justified by its "if `suite_layout.py` is not in the tracked set... do not report a violation.
This is what keeps a product checkout unaffected" clause (plan.yaml:139-141); T-01's REQ-04/REQ-05
traces are justified by its legitimate-files and registry-self-policing clauses. Every task's
`files:` list matches exactly the surfaces its intent instructs writing to, and the sum across all
five tasks' `files:` (7 paths) matches the `lanes.rows` list one-for-one — no extra grant, no
missing one.

## Skip note

Per Check 1's resolution: T-01's decomposition of D-03 and T-02's attributed cross-reference are
deliberate anchors for a different reader (the implementer), not complexity to trim — noted rather
than flagged.
