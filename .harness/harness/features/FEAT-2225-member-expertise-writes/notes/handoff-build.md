# Handoff — FEAT-2225-member-expertise-writes, build (team segment) → build (main-session-direct segments) — written at 7c2f2d48c514b93d55941eaca9499c433ea094c1, seq-4

## Next

The main session executes T-03 (`execution_mode: main-session-direct`, DEC-174) inside the feature worktree, building on 7c2f2d48; then T-04 (depends_on T-01, T-02, T-03) with its literal verify. Both are recorded as `done` in plan.yaml by the main session's `[harness:T-NN]` commits, never as runs. After T-04 lands, re-delegate the orchestrator: SIMPLIFY to harness-eng-lead (read harness-simplify first), then mark all tasks done, seam commit, pin `review_sha`, `gh-sync.py status review`, and ONE `validate` dispatch to harness-validator-lead (plan.yaml T-03, T-04; build-phase.md steps 3–5).

## Trust

- T-01 PASS, 0 cycles, commit ba3fab79; orchestrator re-ran its literal verify: unit exit 0, integration exit 0, 0 FAIL lines — runs/r-20261121-3-t01-eng/digest.md — verified-at a22c9e75
- T-02 PASS, 0 cycles, commit 7c2f2d48; orchestrator re-ran its literal verify (exit 0, empty diff) and hashed DEC-18/145/199/219/220 sections before and after: byte-identical — runs/r-20261121-4-t02-product/digest.md — verified-at 7c2f2d48c514b93d55941eaca9499c433ea094c1
- T-02's successor decision is DEC-253; DEC-86 struck with named successor — .harness/harness/docs/DECISIONS.md `## DEC-253 —` — verified-at 7c2f2d48c514b93d55941eaca9499c433ea094c1
- Both lead returns in this run arrived through the host yield gate: each digest carried its fenced record on return and `validate-digest.py <persona> <digest>` printed `digest ok` without any orchestrator append — runs/r-20261121-3-t01-eng/digest.md, runs/r-20261121-4-t02-product/digest.md — verified-at 7c2f2d48c514b93d55941eaca9499c433ea094c1
- Changed-Python code-grade and independent source review of expertise-merge.py were NOT exercised in the build run (eng-lead holds no shell) — runs/r-20261121-3-t01-eng/digest.md adequacy_notes — UNVERIFIED
- tests/integration/canonical-reader-classification.json names `expertise-merge.py::cmd_ops.transform` as a canonical-writer exemption; the T-01 rewrite may move that anchor and the classification gate may red at validate — tests/integration/canonical-reader-classification.json:626 — UNVERIFIED

## Dead ends

- T-02 was dispatched to harness-product-lead, not harness-eng-lead as the plan handoff said: harness-documentor is a product-squad persona and the build team is eng-only (DEC-118) — .harness/team-config.yaml harness-documentor block; .agents/skills/harness/teams/build.yaml note (a) — verified-at 7c2f2d48c514b93d55941eaca9499c433ea094c1
- Harness dispatches must not carry `outputSchema`/`schemaMode`; the host injects the persona schema and refuses the field — host refusal on the first T-02 dispatch attempt — source
- The ticket's `state: applied|pending` queue proposal stays superseded; T-03/T-04 document and enforce receipts, never a queue — .harness/notes/grilling-member-expertise-writes-2026-11-21.md `## Settled` — source

## Working set

- .harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml
- .harness/harness/features/FEAT-2225-member-expertise-writes/feature.json
- .harness/harness/features/FEAT-2225-member-expertise-writes/STATE.md
- .claude/skills/harness/bin/expertise-merge.py
- .harness/harness/docs/DECISIONS.md

## Done when

Scope: T-03 executed main-session-direct on 7c2f2d48 and recorded done
Authority: brief-perspective:.harness/harness/features/FEAT-2225-member-expertise-writes/BRIEF.md#orchestrator
Authority: plan-task:T-03.verify
Authority: plan-task:T-04.verify
