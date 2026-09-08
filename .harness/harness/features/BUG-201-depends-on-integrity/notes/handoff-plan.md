# Handoff — BUG-201-depends-on-integrity, plan → build — written at b44005a8, seq-1

<!-- BACKFILLED 2026-09-08, not written at the seam. The seam write was refused at the time
     by check-domain.sh's handoff shape rel, which discarded the worktree root and looked for
     every Authority pointer in the main checkout, where an unmerged feature dir does not
     exist. That defect was BUG-1480, shipped in PR #1497; this note is written from the
     worktree the moment the fix made it possible. The record says so rather than pretending
     the note existed. -->

## Next

Dispatch the `build` team to `harness-eng-lead` with tasks T-01..T-06 in plan order, T-01
first: the failing unit test for the `depends_on` reference rule precedes the rule itself
(plan-task:T-01.verify, and the Iron Law). T-03 carries the rule inside `validate_plan_doc`;
T-05/T-06 carry the two swallowing consumers. Input paths in Working set.

## Trust

- Approval is signed on both fragments, so build may start — `plan.yaml:3` `approval:` and
  `BRIEF.md:153` `## Approval` — verified-at b44005a8
- The rule has exactly one home, `validate_plan_doc`'s call tree; a second implementation is
  an SC-04 violation, not a convenience — `BRIEF.md:89` — verified-at b44005a8
- The plan panel ran and its findings are transcribed with dispositions — `plan.yaml:117-123`
  three readers `status: ran` — verified-at b44005a8
- The operator settled the D-05 consumer posture in writing — `notes/answers-plan-c0.md`
  Q-A — verified-at b44005a8

## Dead ends

- Do not add a second validation site for the rule to catch it earlier in any consumer:
  SC-04 pins one implementation and a panel finding already turned on it —
  `BRIEF.md:89` — verified-at b44005a8
- Do not widen `unit`-kind or `integration`-kind detect globs to reach the new test:
  SC-06/SC-07 require today's consumers to behave unchanged on their own terms —
  `BRIEF.md:105,111` — verified-at b44005a8

## Working set

- .harness/harness/features/BUG-201-depends-on-integrity/plan.yaml
- .harness/harness/features/BUG-201-depends-on-integrity/BRIEF.md
- .harness/harness/features/BUG-201-depends-on-integrity/notes/answers-plan-c0.md
- .claude/skills/harness/bin/plan-merge.py
- .harness/harness/features/BUG-201-depends-on-integrity/notes/research-BUG-201-depends-on-integrity-replan-c1.md

## Done when

Scope: T-01..T-06 built test-first, the depends_on rule live in validate_plan_doc
Authority: brief-sc:SC-01
Authority: brief-sc:SC-04
Authority: brief-sc:SC-05
