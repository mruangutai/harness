# T-15 verification receipt

PASS. The deliverable diff is limited to adding `### Traces` and its one-column table under `## Checks` in `.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md`; no existing directive, Checks row, inspection-evidence row, title, predicate, method, project, or ordering was changed.

The declared replayable trace ids, in order, are:

1. `C3-KEYBOARD`
2. `TBL-DESKTOP`
3. `VIS-PROTOTYPE`
4. `A11Y-AXE`

All four ids resolve to existing rows in the Checks table.

After `Feat1821Ship.BuildT16TraceCapture` reported that T-16 source editing had ended, the following exact scoped verification was run from the feature worktree root and exited 0 with no output:

```sh
python3 -c "import json,pathlib,subprocess; d=json.loads(subprocess.check_output(['python3','.claude/skills/harness/bin/ui_contract.py','check','--design','.harness/harness/features/FEAT-53-metrics-dashboard/DESIGN.md','--require-predicates','--require-inspection-evidence'],text=True)); expected=['C3-KEYBOARD','TBL-DESKTOP','VIS-PROTOTYPE','A11Y-AXE']; assert d['traced_check_ids']==expected; assert set(expected)<=set(d['listed_check_ids']); tooling='\n'.join(pathlib.Path(p).read_text() for p in ['.claude/skills/harness/bin/ui_contract.py','.claude/skills/harness/bin/dashboard/client/ui-manifest.ts','.claude/skills/harness/bin/dashboard/client/ui-reporter.ts','.claude/skills/harness/bin/dashboard/client/playwright.config.ts']); assert all(i not in tooling for i in expected)"
```

This proves exact trace membership and order, resolution to existing Checks rows, required predicates and inspection evidence, and absence of all four trace ids from the named generic tooling files.

Limitations: verification was intentionally limited to the required T-15 command. No formatter, linter, build, project-wide test, or runtime UI inspection was run.
