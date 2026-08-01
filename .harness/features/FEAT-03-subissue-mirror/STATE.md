# STATE

## Current

- feature: FEAT-03-subissue-mirror
- run: .harness/features/FEAT-03-subissue-mirror/runs/2026-07-31-11-product/state.yaml (last complete)
- squad: validation (next)
- status: in-progress
- phase: **validate** (was build). Build EXITED on its disk-checkable predicate (DEC-148): T-01..T-08
  all carry PASS runs in `feature.yaml`. Validate exits at panel PASS with `must_fix` resolved.
- note: **BUILD IS DONE AND COMMITTED — three commits, `4d00dbc..e68ba00`.** `2897b09` T-01,
  `ae728e8` T-02..T-07, `e68ba00` T-08. `review_sha` re-pinned from the plan baseline `1ce886a` to
  `e68ba00` (INV-6). Tree carries only the held dirt `.harness/logs/2026-07-31.md`, never staged.
  **Every discriminating receipt was re-verified by the orchestrator, not taken from a digest.**
  `run-unit-tests.sh` exits 0 naming three scripts. All four SC-06 payload/lookup absences are clean
  in `wayfind.py` while BOTH carve-out list GETs remain (`sub_issues", "--paginate"` = 1,
  `dependencies/blocked_by",$` = 1 — 0 would have meant a wrongly extracted GET). No bare `"gh"`
  literal remains. `parent_args|blocked_by_args` in `gh-sync.py` = 0, the standing guard intact. The
  suite now prints `close-task closes exactly one issue` and `absorbed #12 #14 NOT closed` — the
  inversion D-02 demanded, not a deleted assertion. All four leave-open fixtures assert absence in
  BOTH close forms (`issue close 40` AND a regex over any `issues/40` call), so the MF-1 class did not
  recur. `ship closes the milestone regardless of parent origin` is emitted inside the ADOPTED fixture
  at `test-gh-sync.py:583` — the only placement catching one `if origin == "created":` wrapped around
  both the parent close and the milestone PATCH. `check-docs.sh` exit 0 (45 patterns / 73 files, "no
  stale statements found") and `check-state.sh` exit 0 with no INV-10 line, both after DEC-138 am.7
  landed at `DECISIONS.md:4299-4374` with NO staleness marker declared — the deliberate choice that
  keeps the checker green (SC-11) and leaves SC-13 to the main session.
  **Two things the plan did not anticipate, both execution-time adjustments:** (1) `review.yaml` has
  only `code`, `security`, `ui` and **no `qa` step**, yet `harness.json` sets `qa_gate: blocking` —
  running it as written would exit validate with the blocking gate never run. `harness-qa` is a
  Validation member (`team-config.yaml:207`), so validator-lead gets the `review` team **plus an added
  `qa` step**. (2) The `ui` step is skipped on the rationale already in `skipped_segments` — no visual
  surface, no DESIGN.md; ui-reviewer would self-scope out at the cost of a spawn.
  **Ship-refresh is SKIPPED: there is no map.** No `INDEX.md` anywhere in the repo and no map dir
  under `.harness/`, so there is no provenance to update and no stale role section to rewrite.
  **Goal-check is scoped SC-01..SC-12, SC-13 carved out** on the `PLAN ## Preconditions` citation —
  not a waiver; a fix cycle for SC-13 is routable to no lead (Q13). SC-06, SC-07, SC-09, SC-10, SC-11
  are `verify: inspection` and are NOT spoken to by the green suite. One pre-empted false positive:
  this feature's own `feature.yaml` IS in the diff (phase, cycles, cost, runs), so a loose SC-10 read
  flags it — the discriminating check is the `github:` block, still `parent: none` / `milestone: none`
  / `issues: {}`, unchanged, and no other feature's `feature.yaml` is in the range.
  **Budgets, flagged up rather than absorbed.** `cycles_used: 6 of 10`, correct per DEC-157
  (lead-reported send-backs count even when prose-only: 3 plan fix cycles, 1 in run 09, 2 in run 10) —
  four left, panel not yet run. `cost_usd` ~239 of 120, **2.0x**; run 10 alone ~$54 against
  `per_run_usd: 15.0`. Cost never gates (DEC-134); both ride up as non-blocking open questions,
  because raising either bound is the user's decision and should reach them before exhaustion.

## Open Questions

- **Q13 (for the user, PRE-SHIP) — SC-13 is a criterion only the main session can satisfy.** Its
  subject `.claude/skills/harness/SKILL.md:137,144` is covered by no agent domain. Verified still open
  at `e68ba00`: `grep -c 'closes its issue and everything it absorbs' SKILL.md` is **1** and `:144`'s
  ship row still names only the milestone. Fix cycle 3 raised the bar — the row must name the parent
  **and** name it conditional on recorded origin; a row asserting an unconditional close does not
  satisfy SC-13. Nothing mechanical detects this: `check-docs.sh` is silent **by design**, because a
  staleness marker for still-live wording turns the checker red and gates every `/harness` entry on an
  edit no agent may make. T-08 therefore declared no marker. Returned as a named pre-ship step.
- Q18 (eng-lead, run 10) — `cmd_open`'s attach receipt is written after a `gh()` internal-id lookup;
  a lookup returning exit 0 with EMPTY stdout would POST an empty `sub_issue_id` and still be
  receipted, so no re-run repairs it. Window is narrow (a real `gh api` failure exits non-zero, which
  `gh()` turns into SKIP exit 0 before the POST) and PLAN specifies no guard, so the member correctly
  declined to add one. Accept, or add an empty-id guard as a follow-up.
- Q19 (eng-lead, run 10) — `wayfind.py` is exercised by NO test in `run-unit-tests.sh`, yet T-02 made
  it import-dependent on `gh_issues.py`. Its runtime path rests on one ad-hoc import probe. Low risk
  given dry-run-by-default, but unproven by the gate rather than proven by it.
- Q20 (eng-lead, run 10, harness defect) — `validate-digest.py`'s dev-ops `change_type` enum is
  `{config, scaffolding, infra, ci}` and lacks `logic`, the value PLAN:576 scopes T-07 with. Two
  vocabularies, one field name; t07 reported `infra` and flagged it rather than working around it.
- Q9 (eng-lead, harness gap — CONFIRMED, WIDER THAN FILED) — no `build` team yaml exists, worked
  around in all three build runs with inline step lists; **and** `review.yaml` lacks the `qa` step the
  blocking `qa_gate` needs. Both reach every future feature.
- Q14 (orchestrator, harness defect) — `bash-write-guard.sh` reads any `>` in a bash command string,
  including quoted and heredoc CONTENT, as a redirect. Five hit classes now, two new this run: an
  arrow inside a read-only `python3 -c` print argument, and an HTML comment marker in heredoc prose.
  Workarounds: `git commit -F <file>`, and the Write tool for prose with angle brackets.
- Q11 (orchestrator, harness defect) — the playbook's `cost-report.py --yaml >>` append makes a
  duplicate top-level `cost:` that `check-state.sh` rejects (DEC-156); renaming the placeholder is
  also rejected since `CHECKPOINT_KEYS` admits only `cost`. Hand-nested as `cost.run_usd` in all
  eleven run dirs. Also: the script is project-cumulative with no per-run filter and exits 1 on
  unpriceable models while still emitting, so attribution is by diffing `by_agent` run to run.
- Q17 / Q16b (cosmetic, non-blocking) — PLAN cites `feature.yaml:41` for `parent: none` at four sites
  and the line keeps moving (now `:73`); documentor cited `:73` in the amendment rather than edit the
  approval-gated PLAN. And PLAN:644 / PLAN:649 / BRIEF:174-177 baseline `check-docs.sh` at 69 files
  and `check-state.sh` at exit 1, observed 73 files and exit 0. No SC asserts any of these literals,
  so nothing is falsified. Cite fields, not lines.
- Q10 (orchestrator, harness defect) — `check-state.sh` infers a cycle from any FAIL run, firing a
  VIOLATION on the "FAIL held at the user gate" state DEC-157 defines as zero cycles. Symptom retired
  at signature; the over-approximation stands, as does the asymmetry (pending PLAN is a note, pending
  BRIEF a violation — yet a plan mission ends with both pending).
- Q1 / Q2 / Q3 / Q4 / Q5 / Q6 (pm, from planning) — unowned-domain prose (`SKILL.md`,
  `harness-brief/SKILL.md`), the frozen adopted-parent body, the prototype gate judged not required,
  the `attached:` receipt schema addition (landed; suite asserts both survival cases), and the slug
  judged narrower than the feature (immutable under DEC-133). Unchanged this run.
- Q8 (eng-lead) — CLOSED IN EXECUTION: T-08 routed to product-lead as run 11 (DEC-118), PASS, zero
  send-backs.
