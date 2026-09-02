# FEAT-47-tests-layout — handback to the main session

**FEAT-47 cannot be built by the harness. Every one of its seven tasks is `main-session-direct`, and the
signed plan says so on every task individually.** The orchestrator dispatched to ship it holds no route to
a single implementation surface. This document is the handback: the order to execute in, what is stale in
the plan's own premises, and where each task's operative text lives.

Nothing here changes the approved definition of done. BRIEF.md SC-01..SC-10 stand unedited, and the plan is
unedited except for its station fields.

## The blocker, measured not inferred

| Evidence | What it says |
|---|---|
| `plan.yaml` tasks T-01..T-07, key `execution_mode` | all seven are `main-session-direct`, each with its own `execution_reason` citing DEC-174 |
| live `PreToolUse` probe: `Write` to `.claude/skills/harness/bin/.orch-probe.tmp` | `check-domain: BLOCKED — harness-orchestrator may not write …`; permitted globs are feature-directory paths only. The file was never created |
| `check-domain.sh --resolve tests/unit/x.py` | `NOBODY` |
| `check-domain.sh --resolve .harness/team-config.yaml` | `NOBODY` |
| `check-state.sh` INV-17, unprompted | *"FEAT-47-tests-layout: exempt from handoff notes — every task in its plan.yaml is execution_mode main-session-direct (DEC-174), so no squad ran and no seam was crossed"* |

The harness's own state checker classifies this feature as one no squad runs. That is mechanical
corroboration of the plan's declaration, arrived at independently of it.

## The advisor's ruling

Run `runs/2026-09-02-01-advisor-validator/`, `fable-advisor` via `harness-validator-lead`. Verbatim verdict:

> No legitimate squad-executable route exists for FEAT-47: every mechanically-open surface is either closed
> today (`tests/**` and `team-config.yaml` resolve to NOBODY), normatively closed by DEC-174 (gates and gate
> tests are inside the line, and the orchestrator's dispatch/write path runs through the very gates T-01 and
> T-05 change), or opens only AFTER a main-session task lands.

Three points it was asked to settle:

1. **A layer-1 orchestrator dispatching layer-2/3 squads is INSIDE DEC-174's "team run".** The carve-out
   pairs *"directly — ordinary edits, tests run explicitly, a human reading the diff"* against *"dispatched
   through a team run whose gates are the thing being changed"*. Orchestrator dispatch is refereed by
   `dispatch-guard.sh` and squad writes by the domain hook — both on DEC-174's enumerated gate list — and
   T-01 rewrites `harness_boundary.py`, the module every domain decision resolves through. Only the main
   session holds the user channel (DEC-120), so only it satisfies *"a human reading the diff"*.
2. **No task decomposes into a squad-written library plus a main-session cutover.** DEC-174's library
   paragraph requires the cutover prove *the gate's violation set is identical before and after*; FEAT-47
   exists to change gate behaviour, so that proof is unavailable by construction. T-04 is the one
   technically-open route once T-01 lands, and it is a single `git mv` plus a compile check — legal,
   pointless, not worth splitting the pass.
3. **The segment handback is the correct shape**, with the corrections recorded below.

## Execute in this order — ONE pass

```
T-01 → T-02 → T-03 → T-04 → T-05 → T-07 → T-06
```

**T-07 precedes T-06.** The plan's file order inverts them. `T-06 depends_on: [T-05, T-07]`, and T-06's
verify runs the residue census, which reads red against an Expertise corpus T-07 has not yet repaired.

Run each task's own `verify:` block before starting the next. Three of the joints re-derive premises rather
than merely check work: **after T-01**, **after T-03**, **after T-05**.

## Global preamble — what has moved since the plan was signed

- **`lanes.resolved_at` is `ea6f51f`. `origin/main` is now `e74e088`.** Every census the plan quotes was
  measured before that. D-14 and D-19 already require build-time derivation; this is why.
- **FEAT-48 has merged.** `run_pool.py` and `test-suite-independence.py` are tracked at `origin/main`. The
  build's cross-feature precondition holds, and the panel's standing caveat — *"every cross-feature claim
  binds FEAT-48's plan text, not its code"* — is now resolvable against real code.
- **63 `test-*.py` are tracked under `.claude/skills/harness/bin/` at `e74e088`**, against the plan's
  enumerated 58 + 2. T-02's floor of 39 and T-03's floor of 20 are floors, not counts, and stay valid; the
  enumerations behind them are short and must be re-derived, not trusted. SC-10's floor of 58 also holds.
- **`feat/FEAT-47-tests-layout` at `dafd8e8` carries plan artifacts only.** No implementation exists.
- **`tests/**` and `.harness/team-config.yaml` resolve to NOBODY until T-01 lands.**

## Per-task build-time derivations

Each task's operative text — `files`, `depends_on`, the full `verify:` block and the numbered steps of
`intent` — is in `plan.yaml` at the line anchors below. **Read it there, not from a restatement.** This
document deliberately does not copy ~75 KB of plan text into a second file: a duplicated payload is a
second source of truth that can drift from the signed one, and the main session can open the plan directly.
What follows is only what the plan cannot tell you, because it was true after the plan was written.

| Task | `plan.yaml` | Derive at build time, before editing |
|---|---|---|
| T-01 | line 350 | Re-locate every cited anchor **by content, not by line number** (`harness_boundary.py` 234-242, 370-381; `team-config.yaml` 170/211/231; `test-check-domain.py` 1749-1757). Bracket the premise: `check-domain.sh --resolve tests/unit/x.py` returns `NOBODY` before and exactly `harness-qa`, `harness-backend-dev`, `harness-dev-ops` after. Tests first — write the `is_control_plane_target` / `is_control_plane_glob` cases, watch them fail, then edit |
| T-02 | line 431 | Derive the integration set from `git ls-files -- '.claude/skills/harness/bin/test-*.py'` at current HEAD and run the plan's own `comm -23` reconciliation before moving anything. Assert the floor **and** the per-file rename record; never a count |
| T-03 | line 578 | Derive the unit set as the tracked remainder after T-02's moves, plus the bun suite and its two `.jsonl` fixtures. Anchor recipe is T-02's, verbatim |
| T-04 | line 684 | None. One `git mv` plus header repair |
| T-05 | line 716 | Capture the **current** contents of the two bash arrays in `run-unit-tests.sh` before deleting them, and derive D-16's line-exemption census by running `suite-census.py`. Write both test files first and watch them fail |
| T-07 | line 1262 | Re-run the two-glob token sweep at build time — the 28-file snapshot in the plan is not the set, and the cycle-2 panel's `critical` was exactly this enumeration going stale. Run **after** T-05 |
| T-06 | line 1110 | Read `DECISIONS.md`'s last heading for the next free number; no number is pinned anywhere in the plan. Backfill the `dec: pending-T-06` fields, regenerate the index, re-run the residue census |

**One nuance to preserve, not correct:** T-05's `execution_reason` calls `.harness/harness.json` a file *"no
squad may take under DEC-174"*. It in fact resolves mechanically to `harness-dev-ops`. The bar there is
normative, not a NOBODY. Leave the wording as signed.

## Residual, non-gating

| ID | Item | Nature |
|---|---|---|
| B-1 | `PF-264325dc9f79813daf80d9eecb567380` (`med`, open): `suite-census.py`, the sole instrument for SC-01/02/07/09/10, has no test of its own subcommands | enhancement |
| B-2 | `PF-0ee4b2ee83a7a0ddb1818deb201d6bcf` (`med`, open): T-07's verify passes on a content-gutted stub entry | bug |
| B-3 | `PF-d9cfc106d7adaf9e9ad1824b39c39a1b` (`low`, open): `suite-census.py residue`'s claimed standing life has no standing invoker post-merge | chore |
| B-4 | `check-domain.sh:1216` refuses any Write to an existing run digest that is not a prefix-extension, and a lead holds no `Edit` — so a lead physically cannot *prepend* a contract block to its own digest. Repaired by appending here; `validate-digest.py` tail-anchors on the last `VERDICT:`, so it reads correctly. Should the guard admit a prepend that preserves prior bytes? | bug |

## Bookkeeping reconciled this run

- `feature.json`: illegal `status` key removed (the schema declares `additionalProperties: false`); the two
  validator runs recorded with `code_grade: n_a` (DEC-207 / BUG-1080); `cycles_used: 2`, derived from
  `panel.cycle: 2` and the three plan-panel review artifacts `c0`/`c1`/`c2`; `max_total_runs` recorded.
- `plan.yaml`: feature station and all seven task stations written to `ready` through `plan-merge.py`. They
  read `pending`, which is not in the FEAT-41 vocabulary, and the shape gate was flagging it.
- GitHub mirror opened (INV-26): milestone #42, parent #1236, sub-issues #1237-#1243 for T-01..T-07.
- `runs/2026-08-31-01-validator/digest.md` repaired to the lead contract by its own squad, transcription
  only, prose byte-identical. `validate-digest.py lead` returns `digest ok` on both run digests.
- `check-state.sh` now reports **zero** FEAT-47 violations. The three that remain in the tree belong to
  FEAT-51 and BUG-1187 and are the main session's (worktree removal, a missing handoff note).

## What is still the main session's, beyond the build

- `gh-sync.py status <feature-dir> ready` — the Ready station write belongs to the signature, and every
  phase of this feature is main-session-held because every task is `main-session-direct`.
- `gh-sync.py start-task <feature-dir> T-NN` per task, after recording `building` in `plan.yaml`.
- The pin of `review_sha` and the validation panel, once the build lands.
