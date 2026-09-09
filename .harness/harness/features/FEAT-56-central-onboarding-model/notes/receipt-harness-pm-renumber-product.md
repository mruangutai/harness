# Receipt — harness-pm — FEAT-56 renumber-product — plan.yaml decision citation

**Done. One line changed: `plan.yaml:91`, `D-08.dec` `DEC-220` → `DEC-221`, via
`plan-merge.py amend` with `--expect-sha256`. `approval:` byte-unchanged, diff is exactly
1 insertion / 1 deletion, the plan still loads (20 tasks, 14 decisions), and
`check-plan-routes.py` from the worktree copy still reports the single accepted
branch-manifest DEVIATION with all twenty task rows `OK`.**

## The referent — the point of the task

`D-08.dec` pointed at the entry titled **"Onboarding is fleet registration plus one
product-resident file"**. Verified at the pre-merge tip, not assumed:
`git show 6835db61:.harness/harness/docs/DECISIONS.md | grep '^## DEC-2'` →
`## DEC-220 — Onboarding is fleet registration plus one product-resident file`. Post-merge
that same entry is `DECISIONS.md:7022` as `DEC-221`. The shift is label-only; the referent
is identical. I did **not** re-point it at `DEC-222`.

**I do judge it a probable PRE-EXISTING mis-citation, and I left it.** `D-08.choice`
(`plan.yaml:79-84`) is the two-artifact split — the subject of the entry now numbered
`DEC-222` (`DECISIONS.md:7056`), not of `DEC-221`. Two readings are live and I cannot settle
which the author meant: (a) `dec:` names the *governing* decision, in which case the
fleet-registration entry is a defensible pointer and the split got its own entry later —
`D-09.dec: DEC-120` follows exactly that loose "governing ref" habit; (b) `dec:` names the
decision this D-NN *became*, in which case the pointer should now be `DEC-222`. Correcting
it is a substantive change to a signed plan, not a mechanical renumber, so it is raised as
a non-blocking open question, not acted on.

## Scope ruling confirmed, not acted on

`plan.yaml:1923` and `:1933` sit inside **T-12's `intent:`** and were left untouched. The
ruling reads correctly to me: `:1923` is a measurement pinned to `12f74ea8` ("DEC-220 is the
highest at 12f74ea8") and was true at that SHA — rewriting it would falsify a dated
statement; `:1933` is the refs instruction to a delivered task, and the delivered entry's own
`**Record:**` already reads `refs DEC-221, …` (`DECISIONS.md:7090`). No disagreement.

## Re-measured, not trusted

`grep -n 'DEC-22[012]' plan.yaml` returns exactly three hits before and after — `:91`, `:1923`,
`:1933`. There is **no second citation** inside `decisions:`; the dispatch's claim held. No
other `dec:` or `refs:` in the decisions block names a number ≥ 220, so nothing else shifted.

## Evidence

- before `:91  dec: DEC-220` · after `:91  dec: DEC-221`; `:1923`/`:1933` byte-identical.
- `approval:` → `date: '2026-09-09'` / `approved_by: molchairuangutai` / `status: approved`,
  absent from the diff. `amend --help` takes `--key tasks|decisions` and `--id T-NN|D-NN`
  only, so the invocation has no route to `approval:` by construction.
- `git diff --stat` → `1 file changed, 1 insertion(+), 1 deletion(-)`. No reformatting.
- Loader: `harness_yaml.load_plan` (the real entry point, `harness_yaml.py:295`) → `20 tasks
  14 decisions`, `D-08 dec = ['DEC-221']`, approval mapping intact.
- `check-plan-routes.py` (worktree copy) → `1 violation(s) across 5 plan(s)`, the DEVIATION
  being `.harness/team-config.yaml differs from /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml`.
  Baseline unchanged; exit 1 is that accepted D-14 condition.

## Foreign paths left alone

Engineering squad: `tests/integration/test-check-state-records.py` (M) and
`notes/receipt-harness-dev-ops-rehome-eng.md` (??). Docs half: `.harness/README.md`,
`README.md`, `docs/BUILD.md`, `docs/DECISIONS.md`, `docs/DECISIONS-INDEX.md`, `docs/SPEC.md`,
`docs/org.html`, `observations/harness-documentor.md`, `notes/receipt-harness-documentor-renumber-product.md`.
I touched none of them. Nothing committed.
