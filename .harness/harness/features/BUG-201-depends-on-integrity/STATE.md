# STATE

## Current

- feature: BUG-201-depends-on-integrity
- mission: plan — COMPLETE. Both signable artifacts exist, the panel has run and is recorded.
- status: awaiting_user — the operator's signature is the only remaining act of this phase
- station: plan (plan.yaml `status: plan`)
- source ticket: issue #201 · intake `.harness/notes/grilling-depends-on-integrity-2026-09-06.md`
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-201-depends-on-integrity
- branch `feat/BUG-201-depends-on-integrity`, base sha af859ee8. `review_sha` stays `none`: a
  plan-phase panel grades a specification, not code (DEC-207), so INV-6 demands no pin.
- budget: cycles_used 0 / 10 (no rework: every segment passed first time), runs 3 / 20
- runs: `2026-09-06-01-product` (draft), `2026-09-06-01-validator` (panel, code_grade n_a),
  `2026-09-06-02-product` (panel transcription). The plan-panel step-1 goal-check produced its
  note and NO run dir, so it is deliberately absent from `runs:` — recording it would leave an
  INV-8 dangling reference. The count is a floor, as DEC-157 says.

**HANDOFF (this is the seam note — `notes/handoff-plan.md` could NOT be written; see the defect
below).**

- NEXT: nothing is dispatchable until the operator signs. The main session runs ONE batched
  signature review over the ten `panel.findings` (DEC-176) and signs BOTH fragments —
  `BRIEF.md ## Approval` and `plan.yaml approval:` — through `plan-merge.py sign-approval`.
  Then build opens by dispatching T-01 and T-02 together to `harness-eng-lead` via the `build`
  team: both carry `depends_on: []`, touch different files, and are the test-first pair T-03
  depends on. T-03 next, T-04 last. All four are `execution_mode: team` / `harness-backend-dev`.
- TRUST, each with its evidence:
  - both approval fragments read `pending` and no agent wrote either — plan.yaml `approval`,
    BRIEF.md `## Approval` — verified at af859ee8
  - the whole plan corpus carries ZERO dangling `depends_on`, so the rule breaks nothing on
    disk — my own walk of every `.harness/harness/features/*/plan.yaml` — verified at af859ee8
  - `validate_plan_doc` is the one home shared by `load_plan` and `plan-merge.py`'s pre-write
    check, so one edit covers both routes — `def validate_plan_doc` docstring in
    `.claude/skills/harness/bin/harness_yaml.py` (FEAT-41 HIGH-1) — verified at af859ee8
  - nothing in the panel gates: `severity_max: med`, no high, critical or unrated finding —
    `runs/2026-09-06-01-validator/digest.md` — verified at af859ee8
  - the corpus is 68 plans once BUG-201's own is counted, not the 67 SC-03 pins (finding
    PF-7beea12eb) — UNVERIFIED by me; re-count before grading SC-03
- DEAD ENDS for the next phase:
  - do not validate self-dependencies, cycles or ordering — the operator excluded them —
    intake `## Out of scope` — verified at af859ee8
  - do not add a second checker beside `check-plan-routes.py` — it covers the read route only
    and leaves `plan-merge.py apply` free to write the dangling edge — plan.yaml D-01
  - do not "fix" `check-plan-routes.py`'s exit 2 — finding PF-4f91801bd grades it as already
    satisfying the intent
- WORKING SET: `plan.yaml`, `BRIEF.md`,
  `notes/research-BUG-201-depends-on-integrity-goalcheck-plan-c0.md`,
  `runs/2026-09-06-01-validator/digest.md`, `.claude/skills/harness/bin/harness_yaml.py`

**HARNESS DEFECT, measured not inferred.** `notes/handoff-plan.md` cannot be written for a NEW
feature from a worktree. `check-domain.sh:1747` calls `handoff_done_when.problems(rel, ...)` with
the worktree-STRIPPED rel path but the MAIN checkout root, so `_feature_dir` resolves to
`<main>/.harness/harness/features/BUG-201-depends-on-integrity`, which cannot exist until the
branch merges. Measured both ways with the identical note body: worktree root -> `[]`, main root
-> both Authority pointers unresolved. Every legal authority type (`plan-task:`, `brief-sc:`,
`approval:`, `finding:`) resolves through that same base, so no pointer can pass. DEC-143 strips
the worktree prefix from the path and not from the base. Raised as an open question, not worked
around.

## Open Questions

- Q-A (BLOCKING, operator only): should BUG-201 also make the two swallowing consumers report a
  dangling plan loudly — `factory_claim.py:108-109`, `gh-sync.py:1155/:1265` — or is "not
  consumed, diagnosed as unreadable" the accepted landing? The grilling excluded DAG policy, not
  consumer diagnosis, so this is unruled scope.
- Q-B: SC-02's literal wording is passable by a write route that refuses every apply; tightening
  it is a BRIEF amendment (finding PF-6dda61c31).
- Q1: D-03's team lane rests on DEC-174's "a module a gate imports is not itself a gate". If the
  operator reads the following sentence as absolute, T-03 flips to main-session-direct — one
  field, at signature (finding PF-4e8683223).
- Q-C: SC-03 pins 67 plans; the corpus is 68 with BUG-201's own (finding PF-7beea12eb).
- Q-D: the handoff-note defect above — whose fix is a harness change, not a BUG-201 change.
