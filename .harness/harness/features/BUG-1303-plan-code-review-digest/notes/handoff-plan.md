# Handoff — BUG-1303-plan-code-review-digest, plan → signature gate — written at c369fb1f, seq-2

## Next

Present BRIEF.md and plan.yaml to the operator for a plain signature. `plan-merge.py sign-approval`
with NO `--overrule`: `panel.findings` carries 11 findings and ZERO at `disposition: open`, so no
risk acceptance is required of anyone. Nothing is dispatchable until the signature lands — T-01 is
the DAG root (`depends_on: []`) and every other task descends from it. On signing, the first dispatch
is T-01 (main-session-direct, DEC-174 carve-out).

## Trust

- The defect is doctrine-only, both directions measured: a plan-mode digest with `code_grade: n_a`
  and `reviewed: plan:<abs plan.yaml>` returns `digest ok` rc 0, while the same digest carrying the
  artifact path the persona documents is BLOCKED rc 1 — orchestrator probe — verified-at c369fb1f
- `validate-digest.py` is untouched by every task: the full file set is the test, the two persona
  copies, the code-review SKILL, DECISIONS.md and DECISIONS-INDEX.md — orchestrator enumerated
  `files:` across all four tasks — verified-at c369fb1f
- `.omp/agents/**` is canonical, `.claude/agents/**` are GENERATED, so T-02 edits the OMP source then
  runs `--apply` — `sync-agent-adapters.py` docstring lines 3-5 — verified-at c369fb1f
- `tests/integration/test-validate-digest.py` is green at the branch point: exit 0, zero `^FAIL `,
  `ALL PASSED.` — orchestrator run, 18.9s — verified-at c369fb1f
- T-02's `verify:` greps BOTH persona copies and returns rc 1 on the unmodified tree, so it can
  report red — orchestrator ran the verbatim verify string — verified-at c369fb1f
- `check-plan-routes.py`: 0 violations; the lone T-01 DEVIATION is the expected DEC-174 carve-out —
  orchestrator run — verified-at c369fb1f
- Panel cycle 3 PASSED at `severity_max: none` with both readers `ran` and zero new findings —
  `runs/2026-09-05-08-validator/digest.md` — verified-at c369fb1f

## Dead ends

- Do not edit `validate-digest.py` to close this bug — SC-04 asserts the review range names no file
  under `.claude/skills/harness/bin/`, and the positive control proves the validator already accepts
  the correct form — `BRIEF.md` SC-04 — verified-at c369fb1f
- Do not hand-edit `.claude/agents/harness-code-reviewer.md` — the next `--apply` overwrites it and
  the fix silently reverts — `plan.yaml` D-07 — verified-at c369fb1f
- Do not re-add a persona-copy body-identity case or a second agent copy to CONTRACT_SOURCES —
  `sync-agent-adapters.py --check` already compares all 16 pairs byte-for-byte and
  `check-omp-port.py:156-166` runs it — `plan.yaml` panel findings A-1 and A-7 — verified-at c369fb1f
- Do not assert bare `n_a` or bare `plan:` as evidence of documentation — `n_a` already occurs at
  `harness-code-review/SKILL.md:112-113` and is vacuous — `plan.yaml` panel finding S-2 —
  verified-at c369fb1f

## Working set

- .harness/harness/features/BUG-1303-plan-code-review-digest/BRIEF.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/plan.yaml
- .harness/harness/features/BUG-1303-plan-code-review-digest/runs/2026-09-05-08-validator/digest.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/notes/research-BUG-1303-goalcheck-plan-c0.md
- .harness/harness/features/BUG-1303-plan-code-review-digest/feature.json

## Done when

Scope: operator signs BRIEF.md and plan.yaml with no overrule
Authority: approval:.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/BRIEF.md#Approval
