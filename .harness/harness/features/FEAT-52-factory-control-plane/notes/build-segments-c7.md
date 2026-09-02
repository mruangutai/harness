# FEAT-52 build — the executable segment list

**Both approvals are signed** (plan.yaml:3-6, BRIEF.md:221-225, both `approved`/mruangutai/2026-09-01),
and the GitHub mirror is now open: **milestone #41, parent #1220, fifteen sub-issues #1221–#1235**,
one per T-NN, `open` run by me this session.

**Nothing here is dispatchable to a squad.** 14 of the 15 tasks are `execution_mode:
main-session-direct`; the only `team` task, T-13, depends on T-12 and so sits at the very end. That
is why this note exists instead of a run digest. `fable-advisor` was consulted per the operator's
standing instruction and ruled **NO** on an orchestrator executing them
(`runs/2026-09-02-01-validator/digest.md`); `.claude/skills/harness/references/github-mirror.md:32-34`
excludes the orchestrator from the mode by name.

Worktree for every command below:
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-52-factory-control-plane`

## Ownership, by segment

| seg | tasks | issues | lane | owner | depends |
|---|---|---|---|---|---|
| 1 | T-01, T-02 | #1221, #1222 | main-session-direct | **Main** | — |
| 2 | T-03, T-04, T-06, T-07, T-09 | #1223, #1224, #1226, #1227, #1229 | main-session-direct | **Main** | T-01/T-02 |
| 3 | T-05, T-08, T-11, T-14 | #1225, #1228, #1231, #1234 | main-session-direct | **Main** | seg 2 |
| 4 | T-10 | #1230 | main-session-direct | **Main** | T-06, T-08, T-09 |
| 5 | T-12 | #1232 | main-session-direct | **Main** | T-04..T-08, T-10, T-11 |
| 6 | T-15 | #1235 | main-session-direct | **Main** | T-12 |
| 6 | T-13 | #1233 | team (`harness-documentor`) | **me** | T-12 |

**T-13 and T-15 are concurrent** — T-13 writes `DECISIONS.md`, which is not in the lint's scope, so
it cannot move T-15's whole-scope result. **Message me the moment T-12 is committed** and I will run
T-13 through `harness-product-lead` while you run T-15.

Waves recomputed from the plan's own `depends_on` this session, not inherited. Note T-11 is free as
soon as T-04 and T-09 land, which is one wave earlier than the Advisor's answer placed it.

## Per-task bookkeeping Main owns (mirror reference, `start-task` row)

For each `main-session-direct` task, in this order:

1. `python3 .agents/skills/harness/bin/plan-merge.py set-task-station --file .harness/harness/features/FEAT-52-factory-control-plane/plan.yaml --task T-NN --station building`
2. `python3 .agents/skills/harness/bin/gh-sync.py start-task .harness/harness/features/FEAT-52-factory-control-plane T-NN`
3. build test-first, run the task's `verify:` **verbatim** — read it from the plan, not from this note
4. commit with `[harness:t-NN]` in the message, then `set-task-station … --station done`. **Close
   nothing** — D-23: sub-issues stay open until `ship`.

`plan.yaml` has exactly one write route, `plan-merge.py`. `Edit`, `Write` and a shell redirect are
all denied on it.

**Two acts at the signature seam are yours and are still outstanding:**
`python3 .agents/skills/harness/bin/plan-merge.py set-feature-station --file .harness/harness/features/FEAT-52-factory-control-plane/plan.yaml --station ready`
and
`python3 .agents/skills/harness/bin/gh-sync.py status .harness/harness/features/FEAT-52-factory-control-plane ready`.
The `ready` row belongs to the signature, and the cards did not exist when you signed. It is
idempotent and moves the sub-issues only, never the parent (D-18); `start-task` overwrites each card
anyway, so running it is for an honest board rather than for correctness.

## The task table

Read each task's full `intent:` verbatim before editing — it is the specification, and several carry
line anchors measured at `e8e1b78b` that are hints, not addresses:

```
python3 -c "import yaml;d=yaml.safe_load(open('.harness/harness/features/FEAT-52-factory-control-plane/plan.yaml'));print([t for t in d['tasks'] if t['id']=='T-01'][0]['intent'])"
```

| task | change_type → matrix | traces | the shape, in one line |
|---|---|---|---|
| T-01 | `logic` → unit | REQ-06 | `inflight_registry.py` gains a `feature-root --feature FEAT-NN-slug` verb; the discriminating case asserts the printed path DIFFERS from the owner root |
| T-02 | `logic` → unit | REQ-04, REQ-06 | new `check-instruction-paths.py`; **three** violation classes sharing ONE `^\.harness/([^/]+/)?features/` predicate; empty scope is exit 2, never 0 |
| T-03 | `logic` → unit | REQ-01, REQ-04, REQ-05 | `inject-expertise.sh` emits the control-plane block unconditionally and a `HARNESS_PATH_DRIFT` line; **exit stays 0 on every branch** (D-04) |
| T-04 | `docs` | REQ-02, REQ-06 | anchor families F1–F4 across `.omp/agents/**` and four squad skills, then `sync-agent-adapters.py --apply` |
| T-05 | `docs` | REQ-02, REQ-03 | the fifth family — the systematic-debugging read a product clone cannot satisfy: anchor it AND state the read is permitted |
| T-06 | `docs` | REQ-02, REQ-06 | twelve remaining factory-reachable skills, by direction. Do **not** touch harness-init/grilling/wayfinding |
| T-07 | `docs` | REQ-02, REQ-06 | seven templates; README's eight spans split 3 READ / 5 WRITE. Bare filenames in the left column stay bare |
| T-08 | `docs` | REQ-02, REQ-03, REQ-06 | one new section in `harness-handoff/SKILL.md` stating both anchors, the read-only policy and the literal phrase "holds no shell" |
| T-09 | `logic` → unit | REQ-06 | `dispatch-guard.sh` refuses a shell-less dispatch with no `HARNESS-FEATURE-TREE-ROOT:` line at exit 2; predicate is the **tool grant**, never a name list. No apostrophe anywhere in the block |
| T-10 | `docs` | REQ-02, REQ-06 | the emit duty in the playbook, the lead loop and the team skill |
| T-11 | `docs` | REQ-02, REQ-06 | the emit duty in the four agent definitions that dispatch or receive it; change no frontmatter |
| T-12 | `config` | REQ-04 | wire the lint into the `integration` job, exit 1 and exit 2 distinguished; **two mutants** prove the assertion can go red. Its verify is also the plan's whole-scope run |
| T-13 | `docs` | REQ-01..REQ-03, REQ-06 | **squad, mine** — one DEC entry recording the two-anchor contract, index row in the same commit |
| T-14 | `logic` → unit | REQ-05 | text-scan `^[[:space:]]*exit [1-9]` over the shipped hook = 0 matches, **with a positive control** proving the pattern can match |
| T-15 | `logic` → unit | REQ-02, REQ-04, REQ-06 | six per-site direction rows read from `git show <ref>:<path>`; two fixtures per row, three for row 6. Registers in `UNIT_SCRIPTS`, **not** in `harness.json` detect |

## Three traps the plan states and a reader will still hit

1. **T-02's checker must stay RED until T-12.** Its own verify runs only the test file, deliberately —
   a verify asserting a by-construction red is unsatisfiable the moment the anchoring lands.
2. **Registration is asymmetric.** `test-check-instruction-paths.py` and `test-anchor-directions.py`
   go in `UNIT_SCRIPTS` in `run-unit-tests.sh` and **nowhere else**; adding either to
   `harness.json`'s `test_kinds.integration.detect` trips the KIND-DRIFT cross-check. The three
   already-registered test files get no new registration at all.
3. **Never hand-edit `.claude/agents/*.md`** — generated output; `sync-agent-adapters.py --check` in
   four separate verifies will catch it.

## What I do next

On your message that T-12 is committed I dispatch **T-13** to `harness-product-lead` →
`harness-documentor`, then qa → simplify → `review_sha` pin → `gh-sync.py status … review` → panel →
goal-check → briefing. `cycles_used` is 7 of 10; `runs` is 16 of an informational 20. Segment work
that passes first time adds no cycle.
