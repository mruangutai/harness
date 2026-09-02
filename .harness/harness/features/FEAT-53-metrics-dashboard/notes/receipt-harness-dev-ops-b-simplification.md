# SIMPLIFICATION angle — FEAT-53 plan review (segment B)

**BLUF:** two real findings. (1) D-19 is supposed to be the unavailability contract's authority
but T-06's intent restates it *and* silently adds normative content D-19 lacks — the authority
is already thinner than the restatement. (2) The five-literal file-mix ban (107/12/3/122/12%) is
asserted in four places but a builder can satisfy every task `verify:` in the plan while shipping
a forbidden literal in the backend Python source — no task greps `kpi.py`/`grading.py`/etc. at
all, and the one grep that exists (T-14) checks only 2 of the 5 tokens, and only `.tsx`.
Three items I went in looking for turned up clean; see CLEARED.

## Findings

### F1 — D-19 is the named authority but is missing content T-06 already depends on
- Location: D-19 (`plan.yaml:110-113`) vs T-06 intent's "THE UNAVAILABILITY CONTRACT" paragraph
  (`plan.yaml:282-285`).
- Summary: D-19's `choice` text is "null + sibling `unavailable` entry naming the reason; zero
  reserved for a measured zero." T-06's restatement adds two clauses D-19 doesn't carry: the
  reason must be **a specific sentence** ("no approval date in plan.yaml", not "no data"), and
  "never interpolate and never substitute a neighbouring feature's value." DESIGN's S-4 (`C-4`)
  is *not* a duplicate of this — it's the visual mapping (glyph/typography/fill/badge), a
  different fact, correctly separated. T-14's line ("consuming the payload's unavailable maps
  (D-19)") is a citation, not a restatement — also fine.
- Concrete cost: any task or reviewer that consults D-19 alone (the thing named as the authority)
  gets a weaker rule than the one T-06 actually implements and later tasks (T-10, T-11, T-14) are
  told to obey. If T-06's intent text is ever trimmed or T-06 is re-read cold without its intent
  paragraph, the "specific sentence" and "never substitute a neighbour" clauses have no other home
  to fall back to — D-19 does not currently say them.
- Alternative: fold the two missing clauses into D-19's `choice`/`because` text so D-19 is
  actually complete, then edit T-06's intent to cite `D-19` by id instead of re-deriving the
  contract at length.
- `changes_task_set`: no — no task added/removed, only text.
- `remedy_cost`: whole-file-recreate — the fix touches a `decisions:` list item's scalar text
  (D-19) in addition to a task's `intent:`, and I could not confirm `plan-merge.py amend` supports
  targeting a decision by id the way it does a task; flagging conservatively rather than assuming
  `amend` covers it.
- Overlaps ALTITUDE's territory (single-authority-vs-several) — reporting per dispatch, dedup is
  the lead's call.

### F2 — the file-mix literal ban is stated 4 times, enforced once, and not for the files it's stated against
- Location: DESIGN.md:13-15 and DESIGN.md:261-264 (states the ban); T-05 intent (`plan.yaml:245-246`,
  visual-designer's fixture-prototype note); T-07 intent (`plan.yaml:338-341`, "NO LITERAL of this
  repository's own mix ... may appear in **any source file**"); T-14 verify (`plan.yaml:587`,
  greps only `107` and `122` across `client/src/**/*.tsx`).
- Checked against the concrete planned values named in the dispatch: T-04's port `8971`, DESIGN's
  chart heights `280`/`320`, T-16's `2 MB` ceiling — none contains `107` or `122` as a substring,
  so the two enforced tokens don't currently false-positive against anything else in the plan.
- The real problem is under-enforcement, not over-enforcement: T-07's intent asserts the ban
  covers "any source file" (i.e. also `kpi.py`, `grading.py`, `defects.py`, `attribution.py`,
  `serve.py`), but T-07's `verify:` is just `python3 test-metrics-kpi.py` — no grep, no literal
  check of any kind, backend or frontend. T-14's grep is the *only* automated check in the whole
  plan, it only fires on `.tsx` files, and it only covers 2 of the 5 named tokens (`12`, `3`, and
  `12 percent` are asserted forbidden by DESIGN and T-05/T-07 but never grepped anywhere — likely
  because `12`/`3` are too common to grep literally without false positives, e.g. DESIGN's own
  type scale contains a bare `12`). SC-06 (`verify: automated, evidence: unit`) requires exactly
  this check to exist as a unit test reading shipped source at `review_sha`; no task in the plan
  currently produces that unit test.
- Concrete cost: a builder can satisfy every task `verify:` in this plan (T-06 through T-16) while
  shipping a literal `107` or `122` inside `kpi.py` or `grading.py` — nothing greps backend
  source — and SC-06 would only be caught later by whichever gate re-derives it from scratch (or
  not at all, since no unit test currently exists for it). That is exactly the SC-06 automated/unit
  evidence the coverage table promises and the plan does not currently deliver.
- Alternative: add a grep-style assertion to T-07's `verify:` (mirroring T-14's pattern) that
  scans every tracked `.py` file under `dashboard/` via `git ls-files` for the literal forms `107`
  and `122` (the two tokens that are actually grep-safe; leave `12`/`3`/`12 percent` to code
  review since a literal grep for them is unworkable), so SC-06's unit evidence has one concrete
  home covering both frontend and backend.
- `changes_task_set`: no — this amends T-07's `verify:` text; no new task is strictly required.
- `remedy_cost`: amend — `verify:` is a scalar block string.

## CLEARED (checked, ruled out)

- **T-13/T-14/T-15 restating DESIGN C-1/C-2/C-3/C-4 at length** — genuinely a duplicate of prose,
  but every one of this plan's 17 task intents follows the same convention (T-06 quotes D-19 at
  length, T-07 quotes D-12, T-12 quotes D-03/D-05/D-17): each task is deliberately self-contained
  so a builder needs one document, not two. Rejecting that convention only for T-13/14/15 would be
  inconsistent, and per this plan's own tooling a future DESIGN change reaching into an intent is a
  cheap scalar `amend`, not a structural rewrite — so the drift cost the restatement risks is
  already cheap to repair. Recommendation: **leave as-is.**
- **Dead references to `PLAN.md`, `web/src/**`, `deploy.sh`, `/harness-deploy`, the deleted FEAT-51
  worktree, `registry.json`.** None of `PLAN.md`, `/harness-deploy`, `registry.json`, or the FEAT-51
  path appear anywhere in plan.yaml/DESIGN.md/BRIEF.md. `deploy.sh` appears once, in D-01's
  `because` clause, explicitly stating it "is gone" — correct, not a dead live-reference. `web/src/**`
  appears in D-01 (naming it as the rejected home) and in T-01's intent ("add one entry immediately
  after the existing `web/src/**` entry") — confirmed live: `team-config.yaml:171` currently carries
  exactly that entry for `harness-frontend-dev`, so T-01's instruction points at something real.
- **DESIGN open questions Q1–Q3 presented as open** (DESIGN.md has no Q4–Q6). Q1 (Astryx version) is
  genuinely still open — T-04, which resolves it, is `status: ready`, not yet run. Q2 (CAP-08 shape)
  is explicitly deferred to T-15's probe at build time — plan text matches. Q3 (window tokens) is
  already adopted as the working value throughout the plan while explicitly held open for the
  user to overrule at the approval gate — that's the intended non-blocking shape, not staleness.
  None is dead.
- **Redundant `run-unit-tests.sh --check-kinds &&` conjunct.** Checked all four occurrences (T-03,
  T-06, T-10, T-12) against each task's `files:` list: T-06, T-10 and T-12 all list
  `run-unit-tests.sh` itself among their files (they add array entries), and T-03 edits
  `harness.json`'s `test_kinds.integration.detect` string that `--check-kinds` cross-checks against
  those same arrays. Tasks that touch neither file (T-07, T-08, T-09, T-11) correctly omit the
  conjunct. Read `run-unit-tests.sh`'s own `--check-kinds` implementation: it asserts every
  `INTEGRATION_SCRIPTS` name is declared in `detect` and no `UNIT_SCRIPTS` name is — exactly the
  drift class each of these four tasks could introduce. Load-bearing everywhere it appears; matches
  this checkout's own gotcha (repo Expertise G-10). **Cleared, not flagged.**
