# Plan amendment — FEAT-55 build blockers F-01/F-02 — 2026-09-05

**Applied. plan.yaml now grants T-04 authority over feature-schema.json and test-gh-sync.py, carries
the two corrections in its intent, and records D-21/D-22. The signature survived: `approved`,
`molchairuangutai`, all five original rulings.** T-04 is unblocked; nothing else in the plan moved.

## Premises re-measured before writing (all true)

- `feature-schema.json` appeared nowhere in plan.yaml — no signed task held it. Confirmed by grep at
  pre-amend state; only occurrences now are the ones this amendment wrote (:172, :181, :869, :1014).
- Highest decision id was `D-20` (20 entries, `D-01`…`D-20`). Next free: D-21, D-22.
- T-04 `files:` was the single entry `.claude/skills/harness/bin/gh-sync.py`.
- Existing decision shape is `id` / `choice` / `because` / `dec` (read off D-20). Mirrored exactly.
- `approval.rulings` carried five PF ids. Unchanged.

## What changed — three `plan-merge.py` invocations, all exit 0

| verb | target | stdout |
|---|---|---|
| `amend --yaml-value` | `tasks:T-04.files` (expect `72ce13e1…`) | `AMENDED tasks:T-04.files` / `APPLIED …` |
| `amend` | `tasks:T-04.intent` (expect `ec9d73bf…`) | `AMENDED tasks:T-04.intent` / `APPLIED …` |
| `apply --proposal` | `decisions:` | `ADDED D-21` / `ADDED D-22` / `APPLIED …` |

A `--show` without `--yaml-value` on a list field exits 4 with a clear message; the flag is required
on `--show` as well as on the write.

## Measured post-state (plan.yaml, this worktree)

- T-04 `files:` :868-870, in order — `gh-sync.py`, `feature-schema.json`,
  `tests/integration/test-gh-sync.py`.
- T-04 `verify:` :871-873 unchanged, still the two-line `test-gh-issue-types.py || exit 1` /
  `test-gh-sync.py`.
- Intent: unified diff old→new is **exactly three hunks** — the preamble sentence (:877-882), the
  argv/assertion paragraph inside section 3 (:905-916), and new section 9 (:1013-1025). Every other
  line byte-identical; verified by diffing the pre-amend value against the draft before writing, and
  by `intent == draft` after.
- Decisions: 22 entries, `D-21` at :169 and `D-22` at :186, both with keys `id/choice/because/dec`.
  Folded scalars, so no G-12 `#`-truncation risk; each value's tail re-read intact.
- `approval:` — `status: approved`, `approved_by: molchairuangutai`, `date: 2026-09-05`, rulings
  `PF-bad4d518…`, `PF-17e86df9…`, `PF-f8e806d1…`, `PF-bc6cbd0c…`, `PF-e74a2da8…`. The whole-file
  `git diff -U0` matches **no** line containing `approval`/`PF-`/`rulings`/`approved_by` (grep exit 1);
  total churn 69 insertions, 3 deletions.
- Parses: `harness_yaml.load_file` succeeds on the amended file.
- `check-plan-routes.py <plan>` → `OK T-04 granted to harness-backend-dev, harness-dev-ops,
  harness-qa`, `0 violation(s) across 1 plan(s)`, exit 0. The widened list stays inside the lane.

## Cross-checks a successor should not repeat

- No other task claims `test-gh-sync.py` is *unchanged*. T-06 (:1183) says only that it "must both
  still pass" — still true after T-04 amends the one assertion, so no follow-on amendment is owed.
- Both `typed` declarations sit in T-04 alone (D-21's `because` records why): T-04 must be green
  before T-06/T-08 verify, and two tasks editing one schema file is a writer collision.

## Open questions

None blocking. F-03 (live capability-absent probe) and F-04 (budget raise) are outside this
segment's contract and untouched here.
