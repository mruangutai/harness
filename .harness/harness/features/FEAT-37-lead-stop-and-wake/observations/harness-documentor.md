# Observations - harness-documentor

- 2026-08-27 (T-05): a dispatch's "expected green" list named `test-lead-stop-and-wake.py --check-kinds`; that flag does not exist (argparse rc=2, usage lists only `--self-check | --group`). Running the named command beat trusting the expectation.
- 2026-08-27 (T-05): the task intent asserted the platform nudge text "appears nowhere under .claude/, .harness/ or docs/"; grep found four matches (the rule's own denial, the guard test, BRIEF, plan.yaml). Wrote the constraint without the falsifiable grep claim rather than transcribing a signed-but-untrue sentence.
- 2026-08-27: FEAT-37 T-06 — a task intent named two sites for a "states the same bound" pointer; one (`.claude/skills/harness/SKILL.md`) had been emptied by an earlier commit and the plan's OWN decision block (D-11) already recorded that, while the task intent still asserted it. Grepping the plan against itself, not just the code, found the contradiction in one command.
