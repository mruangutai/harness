# Handoff — FEAT-45-adversarial-plan-panel, build → build (main-session segment) — written at 5178bb1, seq-3

Supersedes handoff-plan.md, whose `## Next` was STOP-pending-signature. That precondition is
discharged: both approval fragments read `approved`, signed 2026-08-30.

## Next

NOT a lead dispatch — the next seven tasks are `main-session-direct` and no lead may run them.
The main session executes T-02, T-03, T-04, T-05, T-06 (paths resolve to NOBODY), then T-07 and
T-08 (DEC-174 enforcement layer). Order: T-02, T-03, T-04, T-05 are mutually independent;
T-06 before T-11; T-07 before T-08. Each carries its own `verify:` in plan.yaml — run it verbatim.
Only then do T-11 (`harness-eng-lead` → `harness-dev-ops`) and T-10 (same lane, last) become
dispatchable, and only then is the QA gate and SIMPLIFY meaningful.

## Trust

- T-01 and T-09 are DONE, committed, and each task's `verify:` re-run verbatim by the orchestrator
  itself at exit 0 — commits 2d7cbac and 5178bb1, tree clean after each — verified-at 5178bb1
- The unit suite is green read CORRECTLY: `grep -c '^FAIL '` = 0 with the runner's own exit status
  captured at 0. A tail read would have reported the last script's `N/N checks passed` — verified-at 5178bb1
- `test-panel-findings.py` can report RED: five single-defect mutants each reddened their expected
  discriminator, so no case is vacuous — `runs/2026-08-31-01-eng/digest.md` — verified-at 5178bb1
- `main` (ba338d8) holds a DIFFERENT DEC-205 from PR #1032, invisible from this branch. FEAT-45's
  entries are DEC-206/DEC-207 and the 205 gap is deliberate; the index sorts by number and asserts
  no contiguity — `bin/gen-decisions-index.py:141,193` — verified-at 2d7cbac
- T-11 is genuinely blocked on T-06: its verify asserts `'fable-advisor' in shipped` and the shipped
  `spawns:` list is four harness entries, zero advisor matches — `.omp/agents/harness-validator-lead.md` — verified-at 5178bb1
- T-10 is genuinely blocked on T-02/T-03/T-04: `plan-panel.yaml` is ABSENT and `plan-panel` greps 0
  in both `.claude/skills/harness/SKILL.md` and `.claude/commands/harness-plan.md` — verified-at 5178bb1
- Routing was measured, not read: `check-domain.sh --resolve` returns NOBODY for the five ungranted
  paths and `check-plan-routes.py` exits 0 with 0 violations and the 2 expected DEC-174 deviations — verified-at 5178bb1

## Dead ends

- Do NOT dispatch T-07 or T-08 to any lead. DEC-174 enumerates `check-state.sh` and **the test file
  of each** gate, and rules such a change is made directly, never through a team run whose gates are
  the thing being changed — `DECISIONS.md:4303,4326` — verified-at 5178bb1
- Do NOT run the QA gate or SIMPLIFY yet. SIMPLIFY is defined as the LAST build step before
  `review_sha` pins; a matrix verdict at 2 of 11 tasks is invalidated by the seven that follow —
  DEC-195 — verified-at 5178bb1
- Do NOT re-pin `review_sha` during build. It stays 1d3e5db; pinning is a validate-entry act (INV-6),
  and the plan-phase readers genuinely reviewed that sha — `notes/answers-2026-08-30-plan.md` Q1
- Do NOT use `plan-merge.py` to flip a task `status:` — it is ADD-ONLY and exits 7 on any differing
  id. Anchor a surgical edit on the task's own `- id:` block — pm measured across all three cycles
- Do NOT add `fable-advisor.md` to this repository. Agent distribution is out of scope and its
  absence is exactly what REQ-14 exists to handle — Q1 ruling — verified-at b8777df

## Working set

- `.harness/harness/features/FEAT-45-adversarial-plan-panel/plan.yaml` — T-02..T-08 `intent:`/`verify:`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/STATE.md`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/feature.json`
- `.harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-31-01-eng/digest.md`
