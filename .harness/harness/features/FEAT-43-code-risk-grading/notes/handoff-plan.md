# Handoff — FEAT-43, plan → build — written at 62fce05 by the main session

## Next

**Both artifacts are APPROVED. Build may start.** First step is **T-01** (`plan.yaml`) — the metric
computation and the grade, pinned by hand-derived fixtures. Nothing else can be graded until the
numbers exist and their counting rules are fixed. T-07 and T-09 depend on nothing and can run
alongside it.

**Four tasks are main-session-direct and must be routed to the main session, not a squad:** T-04
(write the skill), T-05 (wire it into the five specialists), T-08 (the cutover), T-09 (the route
check). Their paths resolve to `NOBODY` or sit in the DEC-174 enforcement layer.

**The ordering constraint is load-bearing: T-08 depends on T-05.** The squad is taught the bar
before a reviewer can fail it. Do not reorder that for convenience.

## Trust

- The A/B probe answered the feature's premise before the build: worst cognitive **8.5 with the skill against 38.0 without**, arms non-overlapping, within-arm spread 3 vs 38 — `notes/ab-probe-does-the-skill-change-the-code-2026-08-27.md` — verified-at 62fce05
- A **draft skill exists** and is what the probe graded — `notes/skill-draft-2026-08-27.md`. It is T-04's starting point, not a substitute for it — verified-at 62fce05
- The five dev specialists load **no skill mentioning complexity**; only `harness-codebase-design` and `harness-simplify` do, informally, and neither reaches them — checked in every agent's frontmatter — verified-at origin/main
- Baseline at `origin/main`: 443 production and 903 test functions, production medians cyclomatic 4 / cognitive 3 / ABC 7.8, worst function `validate-digest.py:530 validate` at cognitive 167 — verified-at 696de63
- **No coverage instrumentation and no dependency manifest exist anywhere**, which is why CRAP is out of scope — verified-at 696de63
- DEC-174 amendment 4 at `DECISIONS.md:5011` settles the lane: a squad may write the library, the cutover is main-session-direct — verified-at 62fce05

## Dead ends

- **Do NOT "fix" `.agents/**`.** The product lead's `high` finding that it does not exist and that both test-kind commands are dead is FALSE. `.agents/skills` is a symlink to `../.claude/skills`; the exact `harness.json` command runs from the repo root, 18/18 passing, exit 0 — run independently by the main session — verified-at 62fce05
- Do NOT reinstate the prediction quiz as SC-11. It measured reading comprehension, not writing behaviour, and it was replaced on the operator's instruction — `BRIEF.md` SC-11 — verified-at 62fce05
- Do NOT add coverage, CRAP, or a dependency manifest. Out of scope by operator ruling; its own feature later — `notes/grilling-code-risk-grading-2026-08-27.md` — verified-at 62fce05
- Do NOT fix the 226 functions already below the bar. Its own cleanup feature, explicitly NOT a ratchet — source: operator ruling 2026-08-27
- Do NOT refactor `validate-digest.py`. Three of the ten worst functions live there and it is enforcement-layer under DEC-174 — verified-at 696de63

## Working set

- `.harness/harness/features/FEAT-43-code-risk-grading/plan.yaml`
- `.harness/harness/features/FEAT-43-code-risk-grading/BRIEF.md`
- `.harness/notes/grilling-code-risk-grading-2026-08-27.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/ab-probe-does-the-skill-change-the-code-2026-08-27.md`
- `.harness/harness/features/FEAT-43-code-risk-grading/notes/skill-draft-2026-08-27.md`
