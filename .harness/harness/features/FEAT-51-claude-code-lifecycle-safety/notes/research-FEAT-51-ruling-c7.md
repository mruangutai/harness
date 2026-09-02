# Research — FEAT-51 — operator F-1 ruling applied (cycle 7)

**The conservative clean scope landed.** `plan.yaml` is now 9 tasks / 16 decisions, `D-16`, `D-17`
and `T-09` are gone, `D-18` records the ruling as a choice, and no surviving claim in either file
says an orphan cannot destroy a quarantined result. Both files still carry `pending` approval.

## What changed

- `plan.yaml` — 1096 lines, written by the remove-then-single-shot recreate route. `T-01..T-08`,
  `T-10`; `D-01..D-15`, `D-18`. No `approval:` key at any nesting level.
- `BRIEF.md` — `SC-12` withdrawn (no renumber: `SC-13` keeps its id), one `## Verification gaps`
  bullet records the withdrawal and the backlog referral, the signability constraint re-measured.
- `D-15` named `D-16` in exactly ONE place — clause (b), `and on quarantine.py adopt and discard
  per D-16`. Struck to `and on quarantine.py adopt,`. Nothing else in `D-15` touched.
- `T-07`'s intent gained two things and nothing else: the `ADOPT_TOOL` comment must now cite `D-18`
  and its `rm -rf` reason, and a ninth exact label — `NEGATIVE CONTROL: an orphan apply whose
  --file value is a shell variable is allowed` — under the live-orphan fixture at exit 0, which is
  `D-13`'s `--file` fail-open and the only home left for `PF-7f73167a` after `T-09` went.
- `T-06` now `depends_on` `T-07` and its `verify:` gained two region-sliced greps ahead of the
  existing three conjuncts, all of which survive.

## The T-09 residue, classified

Every surviving `T-09`/`t09` hit, by class:

| Where | Class |
|---|---|
| `panel.findings` summaries L38, L65, L71 | frozen finding text, byte-identical by contract — historical, not a live reference |
| `T-01` intent L241–255 (`_t09_root`, `_t09_fire`, `t09`, `run_t09`) | FEAT-41-era code anchors, **verified on disk** at `test-validate-digest.py:1227/1241/1249/1283` — keep |
| `T-03` intent L389, L392 (`T-09 group`, `t09 at :2495`) | FEAT-41-era code anchors, **verified on disk** at `test-check-domain.py:2495` — keep |

`test-plan-sign-gate.py` carries no `t09` at all, so `T-10`'s `AFTER the T-09 group` was dangling
and now reads `AFTER the T-07 group`. `T-10`'s other three references were repointed to `T-07`, and
the label count corrected **21 → 15**: `T-03` contributes 6 exact labels, `T-07` 8 + the new one =
9, `T-09`'s 7 are gone.

## Measurements taken, not copied

At `0bc57c88`, worktree checkout (`/tmp/feat51-measure-d.py`, re-runnable):

- `plan-merge.py apply`, proposal carrying `approval:` onto an absent base → **exit 8**
  (control: the same proposal without `approval:` → exit 0, `APPLIED`).
- `plan-merge.py sign-approval` on a plan carrying no `approval:` mapping → **exit 5**.
- `check-domain.sh` on a `Write` **and** an `Edit` of `plan.yaml` → **exit 2** for `main`,
  `harness-pm` and `harness-product-lead`; the FEAT-41 route-denial text for the first two.

All three match what the dispatch stated. The header comment block now carries these three.

## `T-06`'s new verify — and why it does not hardcode `DEC-209`

`DEC-209` is **already taken at `0bc57c88`** by a shipped entry, *Mechanical code-grade state is
computed by the digest gate*. It was free at `ad93d43e`, so this is drift that landed on main
between the two shas. A verify grepping `^## DEC-209` would therefore slice the wrong entry and be
red on correct work, so the two new conjuncts slice the **last** `## DEC-` region — the entry
`T-06` appends, whatever number it takes under its own next-free-number clause.

Discrimination proven (`/tmp/feat51-verify-proof.py`), each conjunct separately:

| Tree | `plan-sign-gate.sh` | `plan-merge.py` |
|---|---|---|
| current | red (1) | red (1) |
| entry naming both halves appended | **green (0)** | **green (0)** |
| entry naming only `check-domain.sh` (the `PF-e050d4` defect) | red (1) | red (1) |

Runs in ~0.1s. The new `T-07` grep is likewise red today (exit 1).

## Open question, and it is not mine to settle

`DEC-209` being taken invalidates every `dec: DEC-209` pointer in the decisions block, `T-06`'s
"no DEC-209 token occurs anywhere in the file" premise, `T-08`'s `QUARANTINE_DEC` constant and
`SC-09`. `T-06`'s intent already carries the next-free-number fallback, so the build is not
blocked — but the pointers will read wrong. Raised as `Q1`; renumbering is outside this dispatch.

## Verified

`safe_load` clean; 9 tasks all `status: ready` with all ten required fields; `T-06.depends_on ==
[T-01..T-05, T-07]`; `T-10.depends_on == [T-03, T-07]`; seven panel ids intact with the seven
rulings applied and `PF-e380f685` left `open`; `readers`/`last_run`/`cycle` untouched.
`check-plan-routes.py` → **0 violations**, exit 0 (five `DEVIATION` lines are the expected DEC-174
carve-out). Every task `files:` entry is already a `lanes.rows` surface — **no lanes row added**.
`diff` and `cmp` of the written `plan.yaml` against `/tmp/feat51-plan-proposal.yaml` both exit 0.
`BRIEF.md`: `REQ-01..REQ-07` byte-identical to baseline, no `SC-12` criterion, `SC-13` present,
`## Approval` still `status: pending`.
