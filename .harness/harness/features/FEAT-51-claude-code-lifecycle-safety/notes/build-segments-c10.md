# FEAT-51 build — the executable segment list

**The build phase is open.** `plan.yaml` `status: building`, milestone #38, parent #1135, nine
sub-issues #1136–#1144 (one per T-NN, `open` run by me). Nothing is dispatchable to a squad until
**T-02 lands**: every remaining task depends on T-01 or T-02, and both are `main-session-direct`
under DEC-174. That is why this note exists instead of a run digest.

Worktree for every command below:
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-51-claude-code-lifecycle-safety`

## Ownership, by segment

| seg | tasks | issue | lane | owner | depends |
|---|---|---|---|---|---|
| 1 | T-01, T-02 | #1136, #1137 | main-session-direct | **Main** | — |
| 2 | T-03, T-07 | #1138, #1142 | main-session-direct | **Main** | T-02 |
| 3 | T-04 | #1139 | team (`harness-dev-ops`) | **me** | T-02 |
| 4 | T-05 | #1140 | main-session-direct | **Main** | T-01, T-04 |
| 5 | T-10 | #1144 | main-session-direct | **Main** | T-03, T-07 |
| 6 | T-06 | #1141 | team (`harness-documentor`) | **me** | T-01..T-05, T-07 |
| 7 | T-08 | #1143 | team (`harness-dev-ops`) | **me** | T-06 |

Segments 2 and 3 are concurrent once T-02 lands — they share no files. **Message me the moment T-02
is committed** and I will run segment 3 while you run segment 2.

## Per-task bookkeeping Main owns (mirror reference, `start-task` row)

For each `main-session-direct` task, in this order:

1. `python3 .agents/skills/harness/bin/plan-merge.py set-task-station --file .harness/harness/features/FEAT-51-claude-code-lifecycle-safety/plan.yaml --task T-NN --station building`
2. `python3 .agents/skills/harness/bin/gh-sync.py start-task .harness/harness/features/FEAT-51-claude-code-lifecycle-safety T-NN`
3. build test-first, run the task's `verify:` verbatim
4. commit with `[harness:t-NN]` in the message, then `set-task-station … --station done`. **Close
   nothing** — D-23: sub-issues stay open until `ship`.

`plan.yaml` has exactly one write route, `plan-merge.py`. `Edit`, `Write` and a shell redirect are
all denied on it.

**One mirror act was missed at signature and is yours:** the sub-issues were created after you
signed, so
`python3 .agents/skills/harness/bin/gh-sync.py status .harness/harness/features/FEAT-51-claude-code-lifecycle-safety ready`
never had cards to move. It is idempotent and the `ready` row is the signature's; run it once before
segment 1 if you want the board honest, or skip it — `start-task` overwrites each card anyway.

## SEGMENT 1 — run this now

Read each task's full `intent:` verbatim before editing; it is the specification, and both carry
re-measured line anchors that are hints, not addresses:

```
python3 -c "import yaml;d=yaml.safe_load(open('.harness/harness/features/FEAT-51-claude-code-lifecycle-safety/plan.yaml'));print([t for t in d['tasks'] if t['id']=='T-01'][0]['intent'])"
```

### T-01 — `validate-digest.py` gains a nonterminal SUSPENDED answer (issue #1136)

- **traces** REQ-02, REQ-06 · **change_type** `api` → test matrix requires **unit**
- **files** `.claude/skills/harness/bin/validate-digest.py`,
  `.claude/skills/harness/bin/test-validate-digest.py`
- **shape** In `hook_mode()` only, split the single live-children refusal into three answers:
  (1) `VERDICT: SUSPENDED` from a lead/orchestrator with non-empty `live_children` and a DIGEST
  `awaiting` list whose personas **set-equal** `live_children` → exit 0, one stderr line, **and the
  claim is NOT released**; (2) a terminal verdict with live children → unchanged refusal, exit 2;
  (3) no live children → fall through, where `SUSPENDED` is rejected as an unknown verdict.
  `SUSPENDED` is **not** added to `VERDICTS` and no persona schema gains a suspension shape.
- **the subtle half** STEP ONE's `_reg.release(...)` fires on every return today. It must not fire
  on the accepted-suspension branch, and every other path stays behaviour-identical, including the
  failure swallowing.
- **do not** use the `case()` helper — it cannot carry a registry. Use the T-09 fixture builders
  (`_t09_root`, `_reg_module`, `_t09_fire`, `t09`), a new group function beside `run_t09`,
  registered in `main()` next to `fails += run_t09()`.
- **RED first, six labels, verbatim** — write them, run against a pre-change copy of
  `validate-digest.py` placed **inside** `.claude/skills/harness/bin` (a `/tmp` copy cannot import
  its siblings) via `VALIDATE_DIGEST_BIN`, record all six failing, delete the copy:
  `a SUSPENDED return with a live child is accepted` (expect exit 0, gets 2) ·
  `a terminal PASS with a live child is refused` (this one may already pass — it pins the
  unchanged branch) · `a SUSPENDED return with no live child is refused` ·
  `a SUSPENDED return omitting a live child is refused` ·
  `a SUSPENDED return from a member persona is refused` ·
  `a SUSPENDED return leaves the parent claim live` (read the claim back off disk with the
  `claims()` reader, never from the exit code).
- **verify** (verbatim from the plan):
  ```
  grep -q 'a SUSPENDED return with a live child is accepted' .agents/skills/harness/bin/test-validate-digest.py &&
  grep -q 'a SUSPENDED return leaves the parent claim live' .agents/skills/harness/bin/test-validate-digest.py &&
  python3 .agents/skills/harness/bin/test-validate-digest.py
  ```

### T-02 — orphan-write predicate and quarantine path rule (issue #1137)

- **traces** REQ-04, REQ-07 · **change_type** `logic` → test matrix requires **unit**
- **files** `.claude/skills/harness/bin/inflight_registry.py`,
  `.claude/skills/harness/bin/test-inflight-registry.py`
- **three new public names**, built on `_update_registry`, `_expire_where`, `_matches`, `_visible` —
  no new primitives: `CANONICAL_ARTIFACTS`; `canonical_artifact(rel)`; `quarantine_rel(rel, agent,
  session)` (pure string work, no filesystem); `orphan_write(root, agent, feature, session,
  now=None)`. Expiry stays **query-scoped** — pass `feature` into the `_expire_where` predicate, as
  `live_children` does. Change no existing signature, TTL or constant.
- **the second half, and it is why occurrence 7 shipped a false verdict**: the LAST line
  `children_refusal_lines` appends today coaches "an immediate second identical return ships".
  **Replace that line and only it**; keep the issue-551 line above it byte-unchanged. The
  replacement names SUSPENDED-with-an-awaiting-list as the legal turn-end and must not say a
  repeated return ships. Do not add a second line beside the old one.
- **RED first** — cases 29–33 in the file's `def case_NN_name` style, each registered in `main()`
  or it never runs: 29 `case_29_orphan_write` (another persona, another session → orphan) ·
  30 own live claim in own session → not orphan · 31 no live claim at all → not orphan (the
  fail-open) · 32 claim with absent session key → visible to any session, not orphan ·
  33 `case_33_orphan_write_omp_runtime_is_never_orphaned` (needs a **real child process** for the
  supervisor pid). Plus the refusal-text assertion labelled exactly
  `the children refusal names SUSPENDED and never says a repeated return ships`, asserting both
  halves separately: `SUSPENDED` occurs, `identical return ships` does not.
- **verify** (verbatim):
  ```
  grep -q 'def case_29_orphan_write' .agents/skills/harness/bin/test-inflight-registry.py &&
  grep -q 'def case_33_orphan_write_omp_runtime_is_never_orphaned' .agents/skills/harness/bin/test-inflight-registry.py &&
  grep -q 'the children refusal names SUSPENDED and never says a repeated return ships' .agents/skills/harness/bin/test-inflight-registry.py &&
  python3 .agents/skills/harness/bin/test-inflight-registry.py
  ```

**Order inside segment 1 is free** — `depends_on: []` on both, disjoint files. T-01 is the riskier
one (its target moved +270/-158 since the plan's original anchor sha); a failure there wastes none
of T-02, and **T-02 is the one that unblocks five tasks**, so land it first if you want segment 3
running in parallel sooner.

## SEGMENT 2 — after T-02 (Main)

- **T-03** (#1138, `cross_module` → unit **and integration**): the quarantine branch in
  `check-domain.sh`'s Python heredoc, placed **after** the FEAT-41 plan.yaml route denial and
  **before** the `if not _post:` mode split — that position is load-bearing three ways. Fails
  **open** on any import failure. Grade the canonical case on **`BRIEF.md`, not `plan.yaml`** (a
  `plan.yaml` editor write is already refused for every author, so it cannot discriminate), plus one
  case pinning that an orphan `Write` of `plan.yaml` still exits 2 with the FEAT-41 text. One
  `.harness/team-config.yaml` shared-list entry: `{ path: .harness/*/features/*/quarantine/** }`.
  Six labels, `an orphan canonical write is quarantined` and
  `an omp-runtime writer is never quarantined` are the two the verify greps.
- **T-07** (#1142, `cross_module` → unit **and integration**): `MUTATING_VERBS`, `ADOPT_TOOL` and
  `quarantines()` in `plan-sign-gate.py`, a rewritten header in `plan-sign-gate.sh`, nine labelled
  cases including the `--file`-is-a-shell-variable **negative control that must run under the live
  orphan fixture** or it proves nothing. `sign-approval` stays out of `MUTATING_VERBS`; `discard`
  is deliberately uncovered and the comment must say why, citing D-18.

Both carry full anchor-by-anchor `intent:` in `plan.yaml`. Read it; do not work from this summary.

## What I do next

On your message that T-02 is committed I dispatch **segment 3 (T-04)** to `harness-eng-lead` →
`harness-dev-ops`, then hold for segments 4 and 5, then run 6 and 7, then qa → simplify →
`review_sha` pin → panel → goal-check → briefing. `cycles_used` is 9 of 20; segment work that
passes first time adds none.
