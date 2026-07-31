# Handoff — FEAT-03-subissue-mirror, plan → plan-fix (then build) — written at af2159e, seq-1

## Next

**Route eng-lead's six must_fix to product-lead as ONE fix cycle** (`cycles_used` 0 → 1), inputs:
`.harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-02-eng/digest.md` (the failing report,
`feed: [self]`), plus BRIEF.md and PLAN.md. Two of the six touch BRIEF, not just PLAN: MF-1 rewords
**SC-06**, MF-5 narrows **REQ-09**. **Do not dispatch until Q7 is answered** — the user's budget /
task-count decision may change the decomposition the fixes apply to. After the fix cycle returns
PASS, the artifacts go back up `pending`; the plan phase still ends at the user's signature.

## Trust

- BRIEF.md (171 lines, 9 REQ, 12 SC, `## Verification gaps`, `## Out of scope`) and PLAN.md
  (288 lines, D-01..D-06, T-01..T-08) exist and both `## Approval` are `status: pending` —
  `.harness/features/FEAT-03-subissue-mirror/{BRIEF,PLAN}.md` — verified-at af2159e
- `test-gh-sync.py` passes today (exit 0, ALL PASSED) and two of its passing assertions encode the
  contract this feature reverses (`close-task closes issue + 2 absorbed`, `absorbed #12 #14 closed`)
  — ran it directly — verified-at af2159e
- `test_kinds.unit.detect` matches **zero** files in this repo (`tests/unit/` absent; both bin test
  scripts are hyphenated so `test_*.py` misses them) — `find` over the tree + `.harness/harness.json`
  — verified-at af2159e
- `deploy.sh` copies `bin/` as a whole directory (`safe_replace_dir`, deploy.sh:85-93), so a new
  shared module ships automatically — eng-lead digest, question 2 — verified-at af2159e
- MF-6 is real and worse than filed: **one `.pyc` is already tracked** —
  `.claude/skills/harness/bin/__pycache__/validate-digest.cpython-314.pyc` (`git ls-files`) — and
  neither `.gitignore` nor `templates/gitignore.snippet` has any pycache rule (grep: no match), and
  `dirty_tree_whitelist` covers only `.harness/**` and `.claude/worktrees/**` — verified-at af2159e
- `check-docs.sh` exits 0 at this sha (45 patterns, 68 files) — ran it — verified-at af2159e
- `github.sync: false` / `repo: null` in this repo, so every mirror invariant is provable only
  against the fake `gh`; the live API path is carried by DEC-168's measured probe — verified-at af2159e
- Cost is ~$44 against `max_cost_usd: 40`, spent entirely in the plan phase — per-agent snapshot
  deltas appended to both runs' `state.yaml` (P-01 method) — verified-at af2159e, approximate

## Dead ends

- **Feature B, both halves of the razor** — extracting the `blocked_by` write and the parent read is
  IN; `gh-sync.py` *calling* either is OUT (a READ, and DEC-138 makes the mirror write-only) —
  BRIEF.md `## Out of scope`:141-152, pinned by SC-06 — source: grilling `## Settled`
- **Re-probing closure semantics** — measured and recorded; no task may re-derive them —
  DEC-168 — source: grilling `## Facts I verified`
- **Asserting on `sub_issues_summary` immediately after a write** — eventually consistent
  (`total: 1` corrected to `total: 2` seconds later) — DEC-168 — source: same
- **Retrofitting FEAT-01/FEAT-02/kaya's FEAT-03** — new features only — BRIEF `## Constraints`:132
- **Renaming the feature id** — BRIEF, PLAN, STATE, feature.yaml and two run dirs reference
  `FEAT-03-subissue-mirror`; pm's narrower-slug preference rides as Q6 — source: orchestrator decision
- **Dispatching visual-designer or ui-reviewer** — no visual surface, no DESIGN.md —
  `feature.yaml skipped_segments` — source: Expertise O-01, extended

## Working set

- `.harness/features/FEAT-03-subissue-mirror/BRIEF.md`
- `.harness/features/FEAT-03-subissue-mirror/PLAN.md`
- `.harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-02-eng/digest.md`
- `.harness/notes/grilling-subissue-mirror-2026-07-31.md`
- `.claude/skills/harness/bin/{gh-sync.py,wayfind.py,test-gh-sync.py}`
