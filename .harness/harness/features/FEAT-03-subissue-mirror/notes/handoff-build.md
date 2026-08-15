# Handoff — FEAT-03-subissue-mirror, build → validate — written at e68ba00, seq-5 (supersedes seq-4)

## Next

**Dispatch pm's goal-check through product-lead, scoped SC-01..SC-12 with SC-13 CARVED OUT.** The
panel already PASSed (`runs/2026-07-31-12-validator/digest.md`, `must_fix: []`, `matrix_ok: true`,
`severity_max: low`), so validate's exit predicate is met and only the goal-check stands between here
and the briefing. SC-13 is excluded on the `PLAN ## Preconditions and hand-offs` citation, not waived:
it is a main-session edit to `.claude/skills/harness/SKILL.md:137,144` that no agent domain covers, and
handing it to pm returns it unmet, FAILs the roll-up, and demands a fix cycle routable to no lead.

## Trust

- **Build is complete and committed: `4d00dbc..e68ba00`, three commits** (`2897b09` T-01, `ae728e8`
  T-02..T-07, `e68ba00` T-08); `git log --oneline 4d00dbc..HEAD` shows exactly those three and nothing
  else rode in — verified-at e68ba00
- **Every discriminating receipt was re-run by the orchestrator, not taken from a digest:**
  `run-unit-tests.sh` exit 0 over three scripts; all four SC-06 payload/lookup absences clean in
  `wayfind.py` while both carve-out list GETs still count **1** each; `parent_args|blocked_by_args` in
  `gh-sync.py` = **0**; `absorbed #12 #14 NOT closed` and `close-task closes exactly one issue` both
  present — verified-at e68ba00
- **There are SEVEN `evidence: unit` SCs, not eight** — SC-01, 02, 03, 04, 05, 08, 12; the other six
  (SC-06, 07, 09, 10, 11, 13) are `verify: inspection`. The dispatch brief said eight; qa and PLAN:149
  say seven and the BRIEF parse confirms it. **pm must use seven** — verified-at e68ba00
- **Q18 (empty `sub_issue_id` receipt window) DOES NOT EXIST as built** — `gh()`'s `skip()` is
  `sys.exit(0)`, making the attach path act-then-receipt at `gh-sync.py:296-300`; validator-lead
  corrected eng-lead's raise — verified-at e68ba00
- **SC-10's false positive is pre-empted:** this feature's own `feature.yaml` is in the diff (phase,
  cycles, cost, runs) but its `github:` block is untouched — `parent: none` / `milestone: none` /
  `issues: {}` — and no other feature's `feature.yaml` is in the range — verified-at e68ba00
- **Cost ~$269 of $120 (2.2x) and `cycles_used: 6` of 10.** Cost never gates (DEC-134); four cycles
  remain and the panel spent none — verified-at e68ba00
- The live GitHub API path is proven by nothing here: `github.sync` false, `github.repo` null, so all
  three mirror sync points SKIP and every assertion runs against the fake `gh` — UNVERIFIED by design

## Dead ends

- **Reopening `ship`/`abandon`'s origin symmetry, the `absorbs:` inversion, or SC-06's payload-scoping**
  — settled across three fix cycles and re-verified post-build; a path-level grep for SC-06 is
  self-voiding — source: user at 4d00dbc; run 12 digest
- **Editing `.claude/skills/harness/SKILL.md`** (SC-13, main session's) or re-anchoring the
  `observed @f929d44` receipts / PLAN:20-24's `1ce886a` pin — source: PLAN Preconditions; Q13
- **Widening `post_body_path`'s `except OSError`** (validator F1) — PLAN:432 specifies `OSError`
  literally and PLAN is approval-gated, so it is a backlog item, not an in-flight fix — run 12 Q3
- **Dispatching `ui`, visual-designer, or a ship-refresh** — no visual surface, no `DESIGN.md`, and no
  `INDEX.md`/map exists anywhere in the repo — source: orchestrator, this run; `skipped_segments`

## Working set

- `.harness/features/FEAT-03-subissue-mirror/{STATE.md,feature.yaml}` and `BRIEF.md ## Success Criteria`
- `runs/2026-07-31-12-validator/digest.md` (panel + qa receipts, F1..F4 backlog candidates with natures)
- `notes/{qa-FEAT-03-c0.md,review-harness-code-reviewer-c0.md,review-harness-security-reviewer-c0.md}`
- `.claude/skills/harness/bin/{gh-sync.py,gh_issues.py,test-gh-sync.py,run-unit-tests.sh}`
