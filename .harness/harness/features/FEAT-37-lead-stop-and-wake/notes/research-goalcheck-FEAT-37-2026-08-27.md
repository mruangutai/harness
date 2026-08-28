# Goal-check — FEAT-37 lead stop-and-wake — 2026-08-27

**Pin `4e652f9`.** Diff `4e652f9..5056f57` touches only `STATE.md`, `feature.json`, `notes/` and
`observations/` — no graded surface moved, so working-tree runs grade the pinned content.

## BLUF

**Seven of eight criteria are met; SC-08 is the declared post-merge deferral and is NOT graded here.**
Every REQ-01 through REQ-07 traces to a done task. The feature delivered what it was signed for. Three
findings and two operator judgements below; none of them unmakes a verdict.

## Verdicts

| SC | Verdict | Method | Evidence |
|---|---|---|---|
| SC-01 | met | automated (unit) | `--group playbook` cases 0-3, my own run, exit 0 |
| SC-02 | met | automated (unit) | same run, cases 4-6 (refusal expected / stop again / recurs) |
| SC-03 | met | automated (unit) | `--self-check` exit 0; A,C,D,E,F expected_pass=False got False; B True/True |
| SC-04 | met | inspection | `.claude/skills/harness-team/SKILL.md:119-120` — panel digest `runs/panel-2026-08-27-validator/digest.md:22`; code reviewer cites `:118-120` |
| SC-05 | met | inspection | same panel, `digest.md:23`; anchors `:81`, `:126`, `:196` graded, non-vacuous sweep proven against `c5e59aa^:.claude/skills/harness/SKILL.md:45-46` |
| SC-06 | met | automated (unit) | `--group coverage` 3/3 PASS; `gen-decisions-index.py --stdout \| diff -` exit 0, my own run |
| SC-07 | met | automated (unit) | `--group bound` 6/6 PASS, **both floor cases fired** (`case_floor_DECISIONS.md`, `case_floor_inflight_registry.py`) |
| SC-08 | **not_met — declared deferral, not graded** | uat | none, by design (BRIEF.md:219-233, D-13) |

**REQ coverage:** REQ-01..04 → T-02; REQ-05 → T-05; REQ-06 → T-04 and T-06; REQ-07 → T-01. Nothing dropped.
T-09 carries `traces: [REQ-01..04]` but its work was the DEC-70 narrowing — an enabling change no REQ owns.

## SC-08 — the only criterion measuring conduct, and it ships unmet

A spawned agent loads its skills from the **main checkout**, so every lead in this build read the
unedited playbook. First-hand proof from this run: the stop guard refused the orchestrator repeatedly
saying *"this refusal fires ONCE"* — the outer copy, verified at
`/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/inflight_registry.py:274`, while the
branch's corrected text at `4e652f9:...:339` reads *"at most once per consecutive stop sequence"*.
**Nothing in this build is evidence for the shipped text.** Conduct is unverified until the operator
runs SC-08 from `main` post-merge. Not softened, not partial.

## Findings

**F-01 — SC-05's line citations in BRIEF.md are stale.** Measured at the pin: `:112` is blank and the
"Collect returns" text is at `:126`; `:181` reads "the rule." and the turn-boundaries sentence is at
`:196`. `:81` is still correct. Graded against the **text**, and both readers reached the same three
anchors independently. BRIEF.md is approval-gated and was **not** edited. Cause: `c5e59aa`-era drift
plus the feature's own insertion at `:116-131`.

**F-02 — SC-07 enumerates two once-only sites; a third existed.** `SPEC.md` carried *"Enforcement is
exactly one rejection deep"* (`4e652f9^:SPEC.md:1176`); the T-09 docs sweep corrected it in place
(`4e652f9:SPEC.md:1176`). **SC-07 does not grade `SPEC.md`**, so that falsified sentence would have
shipped standing with every criterion green. This is a gap in the criterion's own enumeration, not in
the work — the correction landed by a sweep's diligence, not by any gate.

**F-03 — T-09's signed `verify:` block can never grade green.** `gen-decisions-index.py --check` is a
flag that has never existed; the docstring says so explicitly and it exits **2** (confirmed at the pin).
The property T-09 meant to gate is gated by SC-06, which names `--stdout | diff -` and exits 0.

## Two recommendations — for the operator, not adopted here

**R-01 — the emergent criterion is genuinely NEW, and I recommend adding it as a blocking backlog row
rather than to this BRIEF.** DEC-70's narrowing landed in `DECISIONS.md`, `DECISIONS-INDEX.md` and
`SPEC.md` — none of which an agent preloads when classifying a change. Verified unqualified at the pin:
`.claude/skills/harness-qa-gate/SKILL.md:40` (`ai_behavior | prompts, model calls, agent definitions,
tool definitions`), `.claude/agents/harness-ai-dev.md:38,41`, and `.harness/harness.json` `test_matrix.ai_behavior.always: ["eval"]`.
**New-vs-covered:** REQ-05's subject is the never-wait rule in the decision record; REQ-06's is the
refusal bound; SC-06 and SC-07 grade DEC-201 and the once-only sites. Nothing here has DEC-70's
classification surfaces as its subject, so folding it into any existing REQ would silently widen that
REQ's subject — the exact move the BRIEF rejected for REQ-08. It is new, therefore it changes what
"done" means, therefore it is the operator's call. **The case is stronger than REQ-08's** because this
feature *created* the inconsistency: the next qa spawn classifying a playbook edit reads the gate skill,
not DEC-70, and reproduces the blockage T-09 existed to remove.

**R-02 — amend T-09's `verify:` clause to the `--stdout | diff -` form.** Not applied in this run. The
plan records a done task behind a clause that can only ever exit 2; leaving it is a falsified record of
how the task was gated.

## Not re-litigated
`check-plan-routes.py` / `harness.json gates` → #910. Orchestrator-tier regression → #903 (strikes D-14/D-16,
replacement D-17; T-03/T-07/T-08 gaps deliberate). INV-26 clear. The panel's `feature.json` diff-base idea
needs a schema change first — the validator refuses an undeclared key; noted, not attempted.
