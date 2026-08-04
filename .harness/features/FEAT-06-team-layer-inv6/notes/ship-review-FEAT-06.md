# Ship review — FEAT-06, team layer and INV-6

**Written for Mike, 2026-08-04, at `9f87c48`.**

## The decision you need to make

**The feature is built, reviewed and green. One question is genuinely yours. The other item is just one more line of work.**

| # | What | Who | Cost |
|---|---|---|---|
| 1 | **SC-05 needs one assertion line.** Handed back as segment 4, exactly like segments 1–3 | main session executes | ~1 minute |
| 2 | **SC-13 is a UAT — you read two things and rule** | **only you** | ~5 minutes |

Everything else is done. **Please answer in one pass** — segment 4 and the UAT together.

## What you asked for, and whether you got it

The feature closes four issues: **#8** (the review panel had no qa step), **#9** (build step lists were hand-composed at dispatch, with no team definition), **#16** (INV-6 read the string `"none"` as truthy, so the invariant failed open), and **#24** (the orchestrator's own playbook never mentioned `qa` or `test_matrix`, while the spec assigned qa sequencing to the orchestrator).

**All four are closed and each closure is falsifiable.** The one to trust most is #24, the re-scope's centre of gravity: at the pre-feature commit, `SKILL.md` contained `test_matrix` **zero** times and `qa` zero times. It now contains `test_matrix` twice, and the tokens `qa`, `validator`, `loop_back` co-occur inside an 8-line window at seven positions. I measured both ends myself.

**10 of 10 tasks passed on the first attempt. Zero rework during the build.**

## What went right that you would not otherwise hear about

**Four defects were caught mid-execution that would each have shipped green.** These matter more than the feature's own content, because they are precisely the failure mode the feature exists to remove:

1. **The widened YAML gate would have scanned nothing, forever.** Python's `glob` does not descend into dotted directories, so `glob('**/*.yaml')` from the repo root matches **0** files while the tree holds 54. The gate would have passed vacuously for the rest of its life. Fixed with `os.walk`; I re-measured it independently.
2. **The new team-catalog checker was proven to discriminate, not assumed.** I ran the finished ten-check script against a detached worktree of the pre-feature commit: **10 of 10 failing there, 10 of 10 passing now.** Not one check is green-on-both-sides. This repo already contains six tests that were green before *and* after their own change, so this was worth the minutes.
3. **A comment broke a test by naming a constant** — T-01 counts occurrences of a literal, and a helpful comment took the count from 1 to 2.
4. **The `review.yaml` comment sweep found a fifth site and created a sixth.** The plan specified a general *sweep* rather than a list, because enumerated lists had already missed sites twice here. The handoff named four; my re-grep found a fifth; the sweep introduced a sixth, caught by its own closing check. A sixth enumeration would have missed it too.

## The two open items

### 1. SC-05 — one assertion line. This is work, not really a decision.

SC-05 says every YAML under `teams/` parses **and** the directory holds exactly two files, declared `verify: automated  evidence: unit`.

The parse half is genuinely asserted. **The count half is asserted nowhere.** `test-harness-yaml-corpus.py:180-181` asserts only `n > 0` per root; the `2` in its output is an f-string **label** at `:174-175`, not a comparison. No `== 2` exists anywhere under `bin/`. qa raised it, pm ruled it unmet, and I verified the premise at source twice rather than relaying it.

| | Fix it | Waive it |
|---|---|---|
| Cost | one `check()` line, main-session-direct | **a pm run plus your signature** — waiving edits an approved BRIEF, which is pm's under your approval |
| Result | the SC is met as written | an SC marked `automated` where half has no assertion |

**Fixing is both cheaper and more honest — waiving is the expensive option here, not the free one.** An unmet SC that *can* be met is a fix cycle, not a plan change. So I have handed this back as **segment 4**, and it needs no decision from you unless you want to override.

**The trap, attached to the hand-back:** the assertion belongs in **`test-harness-yaml-corpus.py`**, *not* `test-team-catalog.py`. T-07's approved `verify:` requires that second script's output to name exactly **ten** checks — an eleventh would break a verify you already signed.

### 2. SC-13 — the UAT. This one is genuinely yours.

`gates.uat` is `blocking_when_uat_criteria_exist`, and SC-13 is the only such criterion. Read two things and confirm they describe builds the way you want them dispatched:

- **`.claude/skills/harness/teams/build.yaml`** — the new build team. It is an *expansion rule*, not a step list, and it is eng-squad only by design.
- **`.claude/skills/harness/SKILL.md:40-53`** — the amended orchestrator passage naming the build team and the blocking qa gate.

These are judgements about how your org should work. No test settles them; that is why the SC exists.

## What is honestly NOT proven

Declared in the BRIEF and signed open. Restating, not reporting as new:

- **`build.yaml` is never executed by this feature.** It is a definition with a passing shape-check and no executor — the review panel's words were "prose with a passing shape-check." Its design derives from **two** recorded eng build runs on **one** feature: a floor, not a generalisation.
- **No ship run exercises the new qa segment.** The playbook now names the gate; nothing proves an orchestrator reading it actually sequences one.
- **Markdown behaviour has no runner.** Four SCs assert only that files *contain* certain text.

## Cost — over budget, and the reason is me

**$154–199 measured against the $100 build-and-validate allowance. Roughly 1.5–2x over.** The range exists because the cost reporter is cumulative over a shared transcript window: $154 counts only the models this org pins, $199 counts every attributable row. **No figure here is invented.**

Two things more useful than the number:

- **The dominant line is my own orchestrator session — about $88, or 45–57% of the total.** Not the squads. This is the square-of-session-length effect the design predicts, showing up empirically: one long orchestrator re-reads its whole history every turn. If you want one lever for the next feature, that is it.
- **Nine of the ten tasks ran in the main session**, whose spend is not separable to this feature at all. The true total is higher than any number above.

**Two things I did not do, with reasons — neither is a budget cut:**

1. **Feature-close distillation has not run because its precondition is unmet**, not to save money. It runs after the SCs pass, and they have not: SC-05 is unmet and SC-13 awaits you. Once both close, it is due. The observation logs are on disk and lose nothing by waiting.
2. **I did not spawn the three leads for parallel domain reports.** I already hold all their digests, and eng-lead did no build- or validate-phase work, so it would have returned "no activity" at real cost. Their digests are under `runs/` if you want any expanded.

## Proposed backlog

Nothing here gates. On your ship acceptance these become issues; **anything you strike dies silently**, so this list is complete on purpose.

| # | Item | Nature |
|---|---|---|
| 1 | **#36** (filed) — `run-unit-tests.sh` exits 2 with a bogus `MISCONFIGURED` error outside the repo root; `BIN_DIR` is relative, `nullglob` unset. Pre-existing, fail-closed | bug |
| 2 | `DECISIONS.md:1634` still shows the ship-feature validator panel as three-wide; `:630` quotes the old set. Historical record, but a reader of that table alone infers the old panel | chore |
| 3 | **Routing wall, recurrence 7** — `harness-qa` has no writable test surface here. `tests/` and `web/` do not exist; all 13 test scripts live in `bin/`, which qa cannot write. The qa segment's *authoring* half is structurally unavailable | enhancement (#20) |
| 4 | **AQ-2** — the panel's qa step is gate-only by *prompt only*. `harness-qa` holds `Edit`/`Write`; nothing mechanically stops it authoring | enhancement |
| 5 | Arch-review advisory 3 — T-09's line caps measure one line over | chore |
| 6 | `harness-code-reviewer` under-reported its own worst finding (`severity_max: info` in its return, `low` in its artifact) and returned a non-distillation `expertise_update`. Caught by validator-lead | bug |
| 7 | `PLAN.md:290-292` quotes `review.yaml`'s "3× slower" as current state; now stale. Not shipped, so harmless | chore |
| 8 | **#19** (filed) — no agent ever runs a PLAN task's `verify:` command | enhancement |

## Where things stand

Four commits on `main`, not pushed, not merged — `f45fd0f`, `510b7ff`, `9f87c48`, `071e313`. All ten mirror issues closed under milestone #1. Merge and PR remain yours, as always.
