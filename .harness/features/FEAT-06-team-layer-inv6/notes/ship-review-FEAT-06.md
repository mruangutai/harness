# Ship review — FEAT-06, team layer and INV-6

**Written for Mike, 2026-08-04. Updated after your gate rulings on SC-05, `personas:` and `filter:`.**

## Where it stands

**SC-05 is closed. `personas:` and `filter:` are deleted and the plan now describes what shipped. One thing is left, and it is yours: SC-13.**

| | Status |
|---|---|
| 14 of 15 success criteria | met |
| **SC-13 (UAT)** | **you are reading `build.yaml` and `SKILL.md:40-47` — nothing else blocks** |
| BRIEF and PLAN | amended; **await your re-signature** (only the main session writes approval) |

## What you asked for, and whether you got it

Four issues closed: **#8** (the review panel had no qa step), **#9** (build step lists hand-composed at dispatch, no team definition), **#16** (INV-6 read `"none"` as truthy, so the invariant failed open), **#24** (the orchestrator's playbook never mentioned `qa` or `test_matrix`, while the spec assigned qa sequencing to it).

**Each closure is falsifiable.** The one to trust most is #24: at the pre-feature commit `SKILL.md` contained `test_matrix` **zero** times and `qa` zero times. It now contains `test_matrix` twice, and `qa`/`validator`/`loop_back` co-occur inside an 8-line window at seven positions. I measured both ends, and re-measured after every later edit.

**10 of 10 tasks passed first time. Zero build rework.**

## What your two gate rulings actually bought

You were offered the cheap path on `personas:` — shrink the list, no BRIEF change — and took the expensive one. **It was the right call, and it exposed more than the field itself.**

- **SC-07 had already started passing vacuously.** With `personas:` deleted, "its declared personas are a subset of the eng squad" is trivially true of an absent set. **SC-08 became unsatisfiable** — an absent set covers nothing. Both now assert the substance the shipped checks prove: single-squad *by construction* via the lead's squad, and the Engineering squad covering the recorded floor.
- **`EMF-2` is completed, not reversed.** The architecture review's finding was that `filter: squad == eng` named a field PLAN tasks do not carry — a fake predicate. Making it an honest token was half a fix; your point was that an honest token no runtime evaluates is a comment wearing a key.
- **T-04's signed `verify:` was red on two different keys in a row** — `KeyError: 'personas'`, then `KeyError: 'filter'`. A signed check that crashes is exactly "appears to exist, does nothing," sitting in this feature's own plan. It now runs green **and asserts their absence**, so it catches re-introduction. Strictly stronger than the original.

## What went right that you would not otherwise hear about

**Five defects caught mid-execution, each of which would have shipped green:**

1. **The widened YAML gate would have scanned nothing, forever.** Python's `glob` does not descend into dotted directories: `glob('**/*.yaml')` from the repo root matches **0** files while the tree holds 54. Fixed with `os.walk`; I re-measured it.
2. **The team-catalog checker was proven to discriminate, not assumed** — 10 of 10 failing at the pre-feature commit, 10 of 10 passing now, run against a detached worktree. This repo already contains six tests that were green on both sides of their own change.
3. **A comment broke a test by naming a constant.**
4. **The `review.yaml` comment sweep found a fifth site and created a sixth**, caught by its own closing check.
5. **T-04's verify**, above.

**One pattern is worth your attention because it recurred three times:** the site list handed down was short every time — 4 named comment sites against 6 real; 2 named `personas` sites against 5; 4 named `filter` sites against 6, with two anchors already stale. **The layer a site list forgets is the verification criterion.** My own re-grep caught the remainder each time, which is why nothing shipped wrong — but the cost of that is real.

## What is honestly NOT proven

Declared in the BRIEF, signed, and re-accepted by you at this gate:

- **`build.yaml` has never been dispatched — including by its own feature.** FEAT-06's eng-squad task list was empty: nine of ten tasks were main-session-direct and the tenth was product-squad. Your words: "we'd have to test it on an actual feature."
- **The `build` dispatch has no mechanism for selecting eng-squad task ids** — issue **#20**, the routing wall. Not this feature's business.
- **Markdown behaviour has no runner.** Four SCs assert only that files *contain* certain text.

## Cost — over by a multiple, and the reason is me

**$253 measured against the $100 build-and-validate allowance — 2.5x. The ceiling, counting every attributable row, is $403.** The lower figure counts only the models this org pins and is the defensible one. **No figure is invented.**

**My own orchestrator session is $139 of the $253 — 55%, the largest single line by far.** This is the square-of-session-length effect the design predicts, measured rather than argued: one long orchestrator re-reads its whole history every turn. Nine of ten build tasks also ran in the main session, whose spend is not separable at all, so the true total is higher.

**If you want one lever for the next feature, it is ending orchestrator sessions at phase seams instead of running one session across build, validate and ship.** That is what the design already says; this feature is the evidence.

Two things not done, neither a budget cut: **feature-close distillation** has not run because its precondition is unmet — it runs after the SCs pass, and SC-13 has not. **The three-lead parallel briefing report** was skipped because I already hold every digest and eng-lead did no build- or validate-phase work.

## Proposed backlog

Nothing here gates. On acceptance these become issues in one pass; **anything you strike dies silently**, so the list is complete.

| # | Item | Nature |
|---|---|---|
| 1 | **#36** (filed) — `run-unit-tests.sh` exits 2 with a bogus `MISCONFIGURED` error outside the repo root | bug |
| 2 | **#19** (filed) — no agent ever runs a PLAN task's `verify:` command | enhancement |
| 3 | **#37** (filed) — `adequacy_notes` is load-bearing across tiers and absent from the digest schema | bug |
| 4 | `DECISIONS.md:1634` and `:630` still show the ship-feature panel as three-wide | chore |
| 5 | **Routing wall, recurrence 7 — its own issue, not a comment on #20.** #20 is plan-time domain resolution; this is a permanent hole: `harness-qa` has no writable test surface anywhere, since all 13 test scripts live in `bin/` | enhancement |
| 6 | **AQ-2** — the panel's qa step is gate-only by *prompt only*; `harness-qa` holds `Edit`/`Write` | enhancement |
| 7 | **No gate reads team-file field content** beyond `test-team-catalog.py`'s ten named checks — the `filter:` deletion passed every gate | bug |
| 8 | **The `SubagentStop` hook does not reject a member `artifact:` pointing at a non-digest file.** Measured: `validate-digest.py` run on `PLAN.md` returns BLOCKED, so the validator catches it and the hook is not invoking it there | bug |
| 9 | `harness-code-reviewer` under-reported its own worst finding (`info` in its return, `low` in its artifact) | bug |
| 10 | Arch-review advisory 3 — T-09's line caps measure one line over | chore |
| 11 | `PLAN.md` quotes `review.yaml`'s "3× slower" as current state; now stale. Not shipped, harmless | chore |

## Where things stand

Five commits on `main`, not pushed, not merged. All ten mirror issues closed under milestone #1. Every gate green: unit 0, docs 0, state 0 violations — each re-run at my own tier rather than taken on report. Merge and PR remain yours.
