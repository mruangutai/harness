# Plan-panel c3 scope read — BUG-285-yaml-loader-pin

**Verdict: the enlarged five-task plan is the right shape for the folded-in scope, but the
signature package resting on it is broken in two places that matter more than its size.** One is
mechanical and certain (a target file the plan repeatedly names no longer exists at that path).
The other is procedural (the goal-check the panel is relying on never looked at the fold-in half of
the plan at all). Neither is in the already-open/ruled-state list handed to me. A third, narrower
gap (duplicate-key parity) is a real but lower-stakes omission. All anchors below were re-verified
at source in this worktree at `6cb113f4`, not trusted from any note.

## Job A — findings

### 1. `severity: critical` — the T-01/T-04/T-05 target file does not exist at the path the plan names

**Summary:** `tests/integration/test-gh-sync.py` — named 12 times in `plan.yaml` and 5 times in
`BRIEF.md` (T-01's `files:`, T-01/T-04/T-05's `verify:` blocks, SC-01/02/04/05) — was deleted by
`[harness:human]` commit `efcebe2d` ("split the three integration-suite pole files (#1527)",
2026-09-09) into five files: `test-gh-sync-abandon.py`, `test-gh-sync-open.py`,
`test-gh-sync-record.py`, `test-gh-sync-ship.py`, `test-gh-sync-start-task.py`. That commit reached
this feature branch through the `6cb113f4` merge of `main` this cycle is reviewing against — it is
exactly the class of hand-edit the review protocol says "inherits no earlier review and is in scope
for you now." The 318-case count the split commit records matches the 318-`ok` baseline plan.yaml
cites for T-01/SC-04, confirming this is the same suite, relocated, not a different one.

**Verified at source, not inferred:** `git log --oneline -- tests/integration/test-gh-sync.py`
shows `efcebe2d` as the last touch, and the path is absent from a directory listing of
`tests/integration/`. The exact anchors T-01's intent gives — the check named
`"T-06C: a feature.json with no github: block returns the default, does not raise"` and the
comment `"---------- fix1 Part B: three states must stay distinct"` — now live in
`tests/integration/test-gh-sync-open.py` at lines 396 and 401, not in any file at the path T-01
names. T-01's insertion instruction ("immediately after ... line 1442 ... before ... line 1444")
cannot be followed literally because the file holding those lines does not exist.

**Consequence:** every verify command written as `python3 tests/integration/test-gh-sync.py`
(T-01, T-04, T-05) fails immediately with `No such file or directory` — certain, not probabilistic,
breakage, and it fails loud rather than open. Worse than the crash itself: an executing agent
handed T-01 cannot follow the dispatch as written at all. It must either (a) silently invent a
sixth pole file at the named-but-wrong path, quietly reintroducing the monolith the human split
existed to remove, or (b) independently figure out which of the five real files carries the T-06C /
fix1-Part-B block and re-derive the insertion point itself — exactly the placement judgment a fully
specified dispatch exists to remove. T-04 and T-05's verify blocks are affected the same way; SC-01,
SC-02, SC-04 and SC-05 all cite the same non-existent path as their evidence location.

### 2. `severity: high` — the goal-check note handed to this cycle graded a different, smaller plan

**Summary:** `notes/research-BUG-285-goalcheck-plan-c3.md` was authored by commit `bdb958d5`
("goal-check the amended plan and record the third panel reader"). At that commit, `plan.yaml`
carried only `T-01`, `T-02`, `T-03` and `D-01`–`D-05` — verified directly:
`git show bdb958d5:.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml` lists exactly those
seven ids and no others. The note's own "seven checks" section names only `T-01`, `T-02`, `T-03`
and traces only `REQ-01` through `REQ-08`. `T-04`, `T-05`, `D-06` through `D-11`, `REQ-09`–`REQ-11`,
and every `SC` from `SC-09` on (bar the ones the note happens not to number) are absent from it —
it never examines the gh-sync.py half of the fix (the uncaught `UnicodeDecodeError` traceback,
arguably the more urgent of the two defects) or the parity test (`T-05`/`SC-14`) that BRIEF's own
Goal section calls "the point of the feature." `feature.json`'s `runs` list corroborates this from
the other side: the last recorded run is `2026-09-11-04-goalcheck-product` (`PASS`) — the same
commit — and no goal-check run appears after it, i.e. after the Q7 fold-in added `T-04`/`T-05`.

**Consequence:** the panel is being asked to weigh a goal-check verdict that answers "does the
three-task plan deliver the operator's pre-fold-in intent," not "does the five-task plan deliver
the intent as amended by the fold-in" — which is this cycle's actual governing question. A
`PASS` computed against a strict subset of the current plan is not evidence for the superset; it is
silent on whether `T-04`/`T-05` serve a real requirement, whether their `depends_on` shape is sound,
or whether the parity test achieves what BRIEF's Goal promises. This is not one of the ruled-state
items in scope context (those concern `PF-142f3a`'s reproduction and the T-03/BRIEF SC-11 letter
conflict, both unrelated).

### 3. `severity: med` — the parity fixture set omits the one input BRIEF names as its own second axis of disagreement

**Summary:** BRIEF's Problem section states the two loaders disagree "in both directions," and
names, in the JSON-accepts/YAML-rejects direction, exactly one case: **a duplicate key** —
`json.loads('{"a":1,"a":2}')` returns `{'a': 2}` (confirmed: last-wins, no error) while
`harness_yaml.load_str` on the same text raises `DuplicateKeyError`. `T-05`'s six-input shared set
and `SC-14` do not include a duplicate-key input; BRIEF's Constraints/Risk sections mention it only
as prose ("nothing may emit a duplicate key, which JSON accepts silently"), asserted nowhere.

**Consequence:** post-fix both readers parse with plain `json.loads`, so they most likely converge
on this input by construction (both silently take the last value) — but nothing in this plan
verifies that convergence. A future change that adds duplicate-key detection to only one reader
(a plausible defensive hardening, e.g. an `object_pairs_hook`) would silently reintroduce precisely
the class of two-readers-disagree divergence this feature exists to close, and no gate in this plan
would catch it — `SC-14`'s six inputs are the only standing parity gate, and none of them is a
duplicate key.

### 4. `severity: info` — the dead `except` member's deletion is, by construction, unobservable to any dynamic test in the plan

**Summary:** the `UnicodeDecodeError` member T-04 deletes from the parse guard is provably dead
(`json.loads` on a `str` cannot raise it — confirmed by the same measurement the plan itself cites).
Because it is dead code, no input can ever reach that branch, so no test in `T-05`/`SC-14` — or any
test that could ever be written — can distinguish a tree with the deletion from one without it by
running anything. What stops a later editor re-adding it is `SC-13`, a one-time inspection at the
pinned sha, plus the corrected docstring (`SC-15`/`D-06`); neither is a standing, re-runnable gate.

**Consequence:** this is not a defect in the plan's design — dead-code removal is inherently
unverifiable dynamically, and the plan's chosen substitute (inspection + docstring) is a reasonable
answer, not a gap the plan failed to consider. Recorded as advisory only; not gating.

### Other Job-A questions checked, no finding

- **Orphan REQ/SC or task `traces:` to a nonexistent REQ:** none. `REQ-01`–`REQ-11` are each traced
  by exactly one or two tasks (`T-01`→01-04, `T-02`→05-06, `T-03`→07-08, `T-04`→09-11, `T-05`→09,11);
  every `SC-01`–`SC-15` maps to a task's file or verify block. No orphans either direction.
- **File collisions across tasks:** none, given finding 1 is corrected. `T-02`↔`factory_decompose.py`
  only, `T-03`↔a new unit file, `T-04`↔`gh-sync.py` only, `T-05`↔a new unit file; `T-01`'s real
  target (`test-gh-sync-open.py`, once named correctly) is touched by no other task.
  `depends_on` shape (`T-05`→[`T-02`,`T-04`], `T-01`/`T-03` independent) is a valid topological
  order and no task's `verify:` reads something a predecessor deletes or a successor hasn't made yet.
- **Would a BRIEF-only reader understand the deliverable is two readers agreeing, not two fixes
  shipping together?** Yes — BRIEF's Goal section states it explicitly ("the point of the
  feature" language), unprompted by this cycle's framing.
- **Over-specification / droppable-without-failing-the-goal:** none found beyond the three items
  already open and out of scope for me to re-raise. `T-05` itself, which a hasty read might call
  foldable into `T-01`/`T-04`, is not droppable — it is the parity test BRIEF's Goal names as the
  deliverable, not incidental verification. Decisions (`D-10`, `D-11`) pin implementation choices
  while their matching `SC`s (`SC-06`, `SC-13`) explicitly grade coverage rather than spelling —
  correctly free where free is warranted.

## Job B — measurement, verbatim

**Invocation** (from the worktree root, `HARNESS_AGENT_TYPE` unset):

```
$ cd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-yaml-loader-pin
$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-plan-routes.py \
    .harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml
```

**Output:**

```
MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-02 granted to harness-backend-dev, harness-dev-ops
OK T-03 granted to harness-backend-dev, harness-dev-ops, harness-qa
OK T-04 granted to harness-backend-dev, harness-dev-ops
OK T-05 granted to harness-backend-dev, harness-dev-ops
0 violation(s) across 1 plan(s)
```

**Exit code:** `0`. **Violation count:** `0`. This settles `PF-142f3a51c…`'s disposition in the
direction `notes/research-BUG-285-foldq7.md` already reported: run from inside this worktree today,
`check-plan-routes.py` does not reproduce the earlier worktree-side DEVIATION.

## Disposition

Two of the four findings gate: the missing target file (critical — three tasks' `files:`/`verify:`
and four `SC`s point at a path that does not exist) and the stale goal-check (high — the cycle's
central "is the enlarged plan still right" question has not actually been graded against the
enlarged plan). Both must be closed before this draft is fit to present for signature: T-01/T-04/T-05
need their file references corrected to the real split file(s), and a goal-check needs to run again
against the current five-task, eleven-decision, fifteen-criterion plan. The duplicate-key gap
(med) and the dead-member observability note (info) do not gate but should travel with the plan to
whoever re-runs the goal-check.

```yaml
VERDICT: FAIL
DIGEST:
  headline: "T-01/T-04/T-05 target a test file main's merge deleted (split into 5 pole files), and the cycle-3 goal-check note grades only the pre-fold-in 3-task plan — both must close before signature; a duplicate-key parity gap is a real but non-gating third item"
  severity_max: critical
  findings: 4
  must_fix:
    - "tests/integration/test-gh-sync.py no longer exists (split by [harness:human] efcebe2d into 5 pole files); correct T-01's files:/intent insertion point and T-01/T-04/T-05's verify: commands to the real file (test-gh-sync-open.py for T-01's anchors) before dispatch"
    - "re-run the goal-check against the current 5-task/11-decision/15-criterion plan.yaml — the handed note (research-BUG-285-goalcheck-plan-c3.md, authored at bdb958d5) graded only the pre-fold-in 3-task/5-decision plan and never examined T-04, T-05, D-06-D-11, REQ-09-11 or SC-09/11-15"
  spec_violations:
    - { kind: omission, path: "tests/unit/test-feature-json-readers.py (T-05 intent; BRIEF SC-14)", ref: D-08 }
  code_grade: n_a
  reviewed: "plan:.harness/harness/features/BUG-285-yaml-loader-pin/plan.yaml"
  human_commits_in_scope: [efcebe2d1a68bba93df42e99759b2238a76fc126]
  open_questions:
    - { id: Q1, question: "Once T-01's target file is corrected, should T-04's and T-05's verify: blocks each name test-gh-sync-open.py explicitly, or should they keep 'the gh-sync integration suite' generic and let the dispatch resolve it against whichever pole file(s) currently hold the relevant checks?", blocking: true }
    - { id: Q2, question: "Should the duplicate-key input be added as a seventh case to T-05's shared set (and an eighth to SC-14), or is convergence-by-construction (both readers now on plain json.loads) an acceptable non-gated answer the operator should simply be told about at signature?", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-285-yaml-loader-pin/.harness/harness/features/BUG-285-yaml-loader-pin/notes/review-harness-code-reviewer-planpanel-c3.md
```
