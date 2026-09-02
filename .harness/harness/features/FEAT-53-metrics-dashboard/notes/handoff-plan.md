# Handoff — FEAT-53, plan → plan (pass 5) — written at bdba1c61, seq-4

## Next

Wait for the operator's pass-4 ruling on `notes/ship-review-2026-09-02-plan-c4.md`, which arrives as
`notes/answers-<runid>.md`. **Two answers are expected, and the budget one is load-bearing.**

1. **`max_total_cycles`.** 9 of a hard 10 are spent, all in the plan phase. If they raise it, write
   the new value with
   `feature-json-merge.py set-key <feature.json> max_total_cycles <n>` — it is a user decision and
   only they may authorise it (DEC-157).
2. **`B-19`..`B-25`** (panel findings `C4-01`..`C4-07`, all `disposition: open` in `plan.yaml`'s
   `panel` key, each carrying a `remedy_size` clause). None gates — the cycle-4 panel returned PASS,
   `severity_max: med`, `must_fix: []`.

If they fix any: ONE consolidated `harness-product-lead` → `harness-pm` pass, then the `plan-panel`
team at cycle 5, then pm transcribes the panel key — the same three-run shape this pass used.
`B-19` is a `T-19` test case, `B-20` a `T-10` clause, `B-21` four fields across `D-08`/`D-20`/BRIEF
`## Constraints`/DESIGN C-2, `B-22` a filing clause, `B-23` `SC-13`, `B-24` two artifacts, `B-25`
`T-05`. If they fix nothing, the plan goes straight to signature; **only the main session signs**,
and it must fill BRIEF `## Approval`'s `date:` as well as `status` and `approved-by`, because `date`
is load-bearing for cycle time under D-14.

## Trust

- Every pass-3 ruling is applied and the cycle-4 panel gates nothing — `runs/2026-09-02-05-validator/digest.md`, both readers `ran` — verified-at bdba1c61
- `plan.yaml` at HEAD: `status: plan`, `approval.status: pending`, 22 tasks, 22 decisions, `panel` cycle 4 with 25 findings — `load_plan` over `git show HEAD:<path>` — verified-at bdba1c61
- The task graph is sound: 22 tasks, every `depends_on` id resolves, acyclic, all 15 REQs traced by at least one task — I re-derived it mechanically myself, not adopted from a reader — verified-at bdba1c61
- `cycles_used` is 9 of a hard 10; `runs` is 18 of an informational 20; `review_sha` is `none` and correctly so, nothing is built — `feature.json` at HEAD — verified-at bdba1c61
- The accuracy / handoff-eval KPI is absent from `BRIEF.md`, `DESIGN.md` and `plan.yaml` — regex over all three, mine and pm's independently — verified-at bdba1c61
- Two of this pass's cycles were send-backs caused by MY under-specification, counted as rework anyway per DEC-157 — `runs/2026-09-02-04-product/digest.md` — verified-at bdba1c61

## Dead ends

- The accuracy / handoff-eval KPI: OUT OF SCOPE for FEAT-53 by operator ruling, becoming FEAT-54 — `notes/answers-2026-09-02-plan-signature-c3.md` — do not add it anywhere, in any form
- DEC-5 / the visual prototype: CLOSED after two browser reviews — `notes/answers-2026-09-01-plan-signature-c2.md` — do not reopen. `B-25` is about `T-05`'s contract, not about the gate
- `B-6`: struck as redundant — same answers file
- `B-12`/`B-13`/`B-14` and the stale spliced `#` comment block: accepted backlog, not fixable by any sanctioned verb today — same answers file
- Spending cycle 10 on the seven advisory findings without the operator saying so: they ruled explicitly that further findings come back to them rather than into another unilateral cycle — `notes/answers-2026-09-02-plan-signature-c3.md` budget note
- Narrowing a fix dispatch to the paths a finding names: doing that to `D-22` is what produced `V-1` in the first place — `notes/ship-review-2026-09-02-plan-c3.md` §1
- The worktree's vendored `.claude/skills/harness/bin/plan-merge.py`: stale, predates `set-panel` and `--yaml-value`. Run the MAIN checkout's binary at `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py` against the worktree plan by absolute `--file`
- `git diff --stat` as a dispatch acceptance criterion inside a live feature dir: it grades the tree, not the change, and is unmeetable while earlier edits sit uncommitted

## Working set

- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/ship-review-2026-09-02-plan-c4.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml`
- `.harness/harness/features/FEAT-53-metrics-dashboard/runs/2026-09-02-05-validator/digest.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/research-FEAT-53-goalcheck-plan-c4.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/feature.json`
