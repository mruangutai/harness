# BRIEF — FEAT-60 Preload weight

## Problem

Every harness spawn preloads its skills before it reads a single file of its own, and those
skills have grown by the same mechanism FEAT-59 measured in the process: evidence, history and
seam-specific procedure accreted into files that every wake pays for. Measured on
`feat/FEAT-59-proportional-flow` at `487aeeeb` (after the playbook was cut 504 → 182 lines):

- The universal trio — `harness-handoff` 1,416 words, `harness-expertise` 788, `harness-principles`
  778 — is **2,982 words paid by all 16 agents**, ~4k tokens on every one of the ~33 spawns a
  feature makes. ~35% of it is not a rule: `harness-handoff` spends ~255 words restating the
  DIGEST schema that `validate-digest.py` already refuses on by name, ~105 on runtime-handoff
  rules only leads act on, and a 90-word red-flags table restating the file above it.
- `harness-team` (3,374 words, all three leads): ~380 words of once-per-run seam detail
  (`steps_from:` expansion, the v2 `state.yaml` key list), ~600 of history DEC-100/120/224 already
  carry, ~140 duplicating `harness-zero-micro-management`, which the same three leads preload.
- `harness-code-risk-grading` (1,117 words, six agents): ~60% worked examples; the threshold table
  and "review semantics" restate `code_grade.py`, whose per-function output already prints
  GRADE / BAR / RESULT / SEVERITY at the moment of use.
- `harness-brief` 2,958 and `harness-spec-driven` 2,285 (pm): ~1,000 words of patch-lane, backlog
  and panel procedure used once per feature, plus ~930 of measurement forensics whose evidence is
  in DEC-129/132/163/179/182/231.
- `harness-code-review` and `harness-verification-rules` carry the #979 / DEC-169 block
  near-verbatim in both; verification-rules' DIGEST section duplicates the validator's own error
  text.

Per-agent preload today: orchestrator ~6.6k tokens, pm ~11.0k, leads ~9.8–10.5k, code-reviewer
~8.8k, each dev ~7.5k, qa ~6.2k, the four leaf readers ~4.0k. Projected after the cuts below:
roughly **40–50k tokens per feature** of preload removed, before any per-run savings.

The cause is the one DEC-158 names and FEAT-59 re-learned: a rule skill should carry the rule,
one clause of why, and a pointer. Three things violate it here — prose that restates a mechanical
gate, evidence that a decision entry already holds, and seam procedure preloaded on every wake.

## Done when — by perspective

**operator** — Every spawn is cheaper and nothing an agent must do went missing. I can read a
skill in one screen and see rules, not history.

**code maintainer** — One home per fact: a gate's contract lives in the gate and its error text;
a rule's evidence lives in its decision entry; a seam's procedure lives in a reference read at
that seam. Nothing is stated twice for the same reader, and there is a rule that keeps it so.

**agent (any of the 16)** — What I preload is what I act on at every wake. What I need at one
moment is named, with its path and its moment, and I read it then.

## KPIs

| KPI | Baseline (`487aeeeb`) | Target |
|---|---|---|
| Universal trio, words | 2,982 | ≤ 1,900 |
| Heaviest single agent preload (pm), words | 8,225 | ≤ 5,500 |
| Sum of preload across all 16 agents, words | 99,672 | ≤ 65,000 |
| Existing skill-text pins (test cases that read a SKILL.md) | all green | all green — none deleted, none weakened |
| Seam references under `references/` that are also preloaded | 0 | 0 |

## Success criteria

- SC-01 (agent): `harness-handoff/SKILL.md` ≤ 650 words; carries no field-level restatement of
  the DIGEST schema beyond the three-part shape and the VERDICT table — it names
  `validate-digest.py` as the contract; runtime-handoff and per-persona artifact paths move to
  `harness/references/runtime-handoff.md` and `artifact-paths.md`, read by leads and the
  personas they name.
  verify: automated  evidence: unit
- SC-02 (agent): `harness-team/SKILL.md` ≤ 2,100 words; `steps_from:` expansion and the v2
  `state.yaml` key contract move to `harness/references/team-run-state.md`, pointed to from the
  seed step; no rule it states is also stated in `harness-zero-micro-management`.
  verify: automated  evidence: unit
- SC-03 (agent): `harness-code-risk-grading/SKILL.md` ≤ 300 words: the bar, the blocking rule,
  the reason-required rule, and a pointer to `code-grade.py` output; worked examples move to
  `harness/references/code-risk-examples.md`.
  verify: automated  evidence: unit
- SC-04 (agent): `harness-brief/SKILL.md` ≤ 1,900 words and `harness-spec-driven/SKILL.md`
  ≤ 1,150 words; patch-lane, backlog-intake and panel-recording procedure move to references
  named from the step that needs them; every measurement paragraph is one clause plus a DEC
  pointer.
  verify: automated  evidence: unit
- SC-05 (code maintainer): the #979 / DEC-169 block exists in exactly one file; `harness-review`
  and `harness-verification-rules` point to it. `harness-verification-rules` carries no DIGEST
  field text the validator's error messages already carry.
  verify: inspection
- SC-06 (code maintainer): `harness-principles` and `harness-expertise` keep every rule; each
  rationale is one clause with a pointer to `docs/PRINCIPLES.md` or the DEC; combined ≤ 1,250
  words.
  verify: automated  evidence: unit
- SC-07 (code maintainer): every word cut as "why" is either already in the cited decision entry
  or is added to it in the same commit — nothing is deleted from the record, only moved from the
  spawn path. `gen-decisions-index.py` and `check-decision-anchors.py` exit 0.
  verify: inspection
- SC-08 (code maintainer): a preload-weight check exists — `check-skill-weight.py` reading
  each agent's `autoloadSkills` and the word count of each file — and `check-state.sh` NOTES (never
  fails) when the universal trio or any single agent's preload exceeds `budgets.preload_warn_words`
  in harness.json. The numeral lives in harness.json only.
  verify: automated  evidence: unit
- SC-09 (code maintainer): `harness-distill/SKILL.md` and `harness-curate/SKILL.md` carry the
  three-part rule for skill text — *if a gate refuses on it, name the gate; if a decision holds
  it, point; if one seam needs it, reference it* — so a future distillation cannot put the weight
  back.
  verify: inspection
- SC-10 (operator): every test that reads a SKILL.md today (`test-orchestrator-playbook.py`,
  `test-team-catalog.py`, `test-lead-stop-and-wake.py`, `test-check-state-plans.py`,
  `test-validate-digest.py`'s documented-contract cases, `test-sync-agent-adapters.py`,
  `test-check-omp-port.py`) passes unchanged in what it asserts; a pin that must move with the
  text moves to the text's new home, never to a weaker predicate.
  verify: automated  evidence: unit
- SC-11 (agent): no file under `harness/references/` is named in any agent's `autoloadSkills`,
  and every reference is pointed to from the skill that owns its seam with the moment to read it.
  verify: automated  evidence: unit

## Verification gaps

- SC-05, SC-07 and SC-09 are text judgements graded by inspection against the diff; the word
  counts (SC-01–04, 06) are the mechanical half.
- No live-flow acceptance: this feature changes what agents read, not what they do. The first
  feature run after merge is observed for a `BLOCKED` or `open_questions` that names a rule an
  agent could not find — that is the failure mode, and it is recorded here if it happens.

## Constraints

- Built direct under DEC-174, all eleven SCs, on the operator's call at signature. The
  deliverable is the text every agent in a normal-path run preloads; spawning leads and devs off a
  worktree whose `harness-handoff` and `harness-team` are half-cut by the previous task executes
  the change through the path being changed, and any resulting `BLOCKED` could not be attributed
  to FEAT-59's lanes versus these cuts. SC-08 would be DEC-174 direct regardless. The first
  SC-23/SC-24 run of FEAT-59's lanes is the next feature that does not touch agent text.
- Cuts land against the FEAT-59 text: FEAT-59 merged to `main` at `97599fd8`; this branch is
  rebased onto it and its PR targets `main`.
- DEC-158 (rule + one clause + pointer) and DEC-150 (read by pointer, never a sweep) supply the
  rule; DEC-205 (the record states current truth) governs the decision edits in SC-07.
- The playbook split that already landed in FEAT-59 (`harness/SKILL.md` → `references/`) is the
  pattern and is out of scope here; its references are not re-cut.

## Out of scope

- Agent frontmatter bodies (`.omp/agents/*.md`) — measured 343–1,204 words each, not the driver.
- Expertise files and their injection budget — a separate mechanism (DEC-125).
- Rewriting a rule's substance; this feature moves and cuts, it does not change what agents must do.
- The post-merge sweep keys on a landed `feature.json`, which a DEC-174 direct build never
  produces, so it skipped FEAT-59 and will skip FEAT-60. Backlog: the sweep verb needs a
  direct-build path; not fixed here.

## Approval

status: approved
date: 2026-09-13
by: operator, main session (direct work under DEC-174, all SCs; see Constraints)
