# Handoff — FEAT-06-team-layer-inv6, validate → ship — RECONSTRUCTED 2026-08-13, seq-1

**READ THIS FIRST. This is not the artifact INV-17 wants.** It was written on 2026-08-13 by the main
session, from records on disk, **after** the feature shipped in PR #45 — not by the agent that
crossed the validate seam on 2026-08-04. No handoff was written at the crossing. Every line is
sourced to a file that already existed; nothing is recalled and nothing is inferred. Treat it as a
reconstruction of what the successor needed, not as evidence the seam was handed off properly.

## Next

**Nothing.** The ship decision was taken and executed: PR #45 merged, four issues closed — **#8**
(the review panel had no qa step), **#9** (build step lists hand-composed at dispatch, no team
definition), **#16** (INV-6 read `"none"` as truthy, so the invariant failed open), **#24** (the
orchestrator's playbook never mentioned `qa` or `test_matrix` while the spec assigned qa sequencing
to it). This handoff exists to close a record gap, not to hand work forward.

## Trust

- **14 of 15 SCs met at the validate crossing; SC-13 was UAT and the operator's alone** —
  `notes/ship-review-FEAT-06.md`
- **10 of 10 tasks passed first time. Zero build rework.** The five recorded cycles were all
  plan-and-review rework, before build — `feature.json` runs list, `notes/ship-review-FEAT-06.md`
- Panel PASS, qa PASS — `notes/review-harness-code-reviewer-c0.md`,
  `notes/review-harness-security-reviewer-c0.md`, `notes/qa-c0.md`
- **The goal-check FAILED and two amend runs followed**, the first escalating. The BRIEF and PLAN were
  amended and required the operator's **re-signature** — `feature.json` runs list,
  `notes/answers-ship-gate.md`
- **#24's closure is the falsifiable one:** at the pre-feature commit `SKILL.md` contained
  `test_matrix` **zero** times and `qa` zero times; after, `test_matrix` twice and
  `qa`/`validator`/`loop_back` co-occurring inside an 8-line window at seven positions. Both ends
  measured — `notes/ship-review-FEAT-06.md`
- **The operator's two gate rulings exposed more than the fields they were about.** With `personas:`
  deleted, SC-07 had already begun passing **vacuously** and SC-08 became **unsatisfiable**; both were
  rewritten to assert the substance the shipped checks prove — `notes/ship-review-FEAT-06.md`

## Dead ends

- **The widened YAML gate would have scanned nothing, forever.** Python's `glob` does not descend into
  dotted directories: `glob('**/*.yaml')` from the repo root matched **0** files while the tree held
  54. Fixed with `os.walk` — `notes/ship-review-FEAT-06.md`
- **A signed `verify:` crashed on two different keys in a row** — `KeyError: 'personas'`, then
  `KeyError: 'filter'`. A signed check that crashes is "appears to exist, does nothing", sitting in
  this feature's own plan. It now asserts their **absence**, so it catches re-introduction —
  `notes/ship-review-FEAT-06.md`
- **`filter: squad == eng` named a field PLAN tasks do not carry** — a fake predicate. Making it an
  honest token was half a fix; an honest token no runtime evaluates is a comment wearing a key. Do not
  reintroduce either — `notes/ship-review-FEAT-06.md`
- **The site list handed down was short EVERY time, three times running** — 4 named comment sites
  against 6 real, 2 named `personas` sites against 5, 4 named `filter` sites against 6 with two
  anchors already stale. **The layer a site list forgets is the verification criterion.** Re-grep
  rather than trust a list — `notes/ship-review-FEAT-06.md`

## Working set

- `.harness/features/FEAT-06-team-layer-inv6/notes/ship-review-FEAT-06.md` — the whole picture
- `.harness/features/FEAT-06-team-layer-inv6/notes/answers-ship-gate.md` — the operator's two rulings
- `.harness/features/FEAT-06-team-layer-inv6/notes/qa-c0.md`
- `.harness/features/FEAT-06-team-layer-inv6/notes/research-FEAT-06-goal-check.md`
