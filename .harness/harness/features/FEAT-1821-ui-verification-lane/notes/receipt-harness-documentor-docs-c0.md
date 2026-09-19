# Receipt — canonical UI lane guidance — docs-c0

VERDICT: PASS
cycles_used: 0
validated_implementation_pin: `ea4916518eea1c8f73901d372ad8e1e38595e64b`

## Canonical documents changed

- `README.md` — the project-level operator and maintainer entry point now gives the configured real-browser rerun, exact bundle location, DESIGN Checks/Traces contract, fail-closed behavior, Trace Viewer command, Mode B duties, and the intentional meaning of FEAT-53's RED example.
- `.harness/README.md` — the canonical state/artifact layout now records the committed `runs/<run-id>/ui/` exception to ordinary ignored run scratch and the generic manifest-listed trace shape. This corrects its stale blanket claim that every run directory is ephemeral.

No parallel guide or source of truth was added. Code, tests, agent policy, evidence, governance, signed feature artifacts, and FEAT-53 production were not edited.

## Scoped verification

- `python3 .claude/skills/harness/bin/ui_contract.py check --design .harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md --require-predicates --require-inspection-evidence` — exit 0; normalized the committed Checks contract, inspection evidence, generic `traced_check_ids`, and both configured projects.
- `npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list` — exit 0; resolved the configured script and listed 23 tests in 6 files without launching browsers. Because the probe omitted the two required environment variables, the reporter also wrote a default `runs/local/ui/results.json`; Main removed that generated scratch, and the canonical guidance now explicitly requires both variables even for discovery.
- `npx playwright show-trace --help` from `.claude/skills/harness/bin/dashboard/client` — exit 0; confirmed the documented Trace Viewer subcommand and ZIP argument.
- Scoped stale-claim sweep across `README.md`, `docs/`, and `.harness/` found only `.harness/harness/features/FEAT-1821-ui-verification-lane/BRIEF.md` lines containing “traces remain local and gitignored” / “traces are local-only”. Those historical signed statements were deliberately not edited: `notes/answers-validate-c8-traces.md` is the authoritative amendment and requires manifest-listed traces to be committed; the new canonical docs state that amended rule.

No formatter, linter, build, project-wide suite, or real-browser rerun was run.
