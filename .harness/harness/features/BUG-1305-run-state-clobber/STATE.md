# STATE

## Current

- feature: BUG-1305-run-state-clobber
- run: .harness/harness/features/BUG-1305-run-state-clobber/runs/brief-amend-c16-product/state.yaml
- squad: product
- status: in-flight
- station: review; cycles 16/18; production code byte-identical to 154ff2a0
- ruling (AdviseBug1305Sc07Conflict): AMEND SC-07, do not ship unmet. SC-07's carve-out was signed before the cycle-13 ruling that mandated the reconstruction-None fail-closed class in service of SC-01(a); the same delegated authority signed both and the later ruling controls. As written the criterion could only be greened by demoting a true disclosure out of the note BLUF, which is the under-reporting SC-07 exists to prevent; the goal-checker's refusal to launder it is recorded as correct. The handoff PRE permit is REQUIRED, not advisory. Cap through cycle 17, cycle 18 reserved solely for mechanical fixes to the amendment wording or the new test.
- cycle 16 landed: SC-07 amended to the Advisor's exact wording (product lane); one handoff valid-reconstructable PRE-Edit permit case added and the regression note refreshed (main-session lane, DEC-174).

## Open Questions

- Cycle 17 is the last graded one: scoped re-review of the test-plus-brief-plus-note diff, then an SC-07-only re-grade. All other criteria carry without re-grade because .claude/skills is byte-unchanged since the reviewed pin.
- SEC-01 remains an accepted residual tracked at #1376; briefing rows B-1 to B-16 in notes/ship-review-2026-09-05-validate-c2.md are unstruck, and B-1 is superseded by the cycle-13 fix.
- Harness defect, fifth occurrence: persona-keyed worktree claims refused a lead its own BUG-1305 run-directory digest write three times in one run; the collated report had to be delivered inline. Remedy named by a blocked lead: inflight_registry.py release for the stale BUG-1308 harness-product-lead claim, which is another flow's registry and the main session's act.
