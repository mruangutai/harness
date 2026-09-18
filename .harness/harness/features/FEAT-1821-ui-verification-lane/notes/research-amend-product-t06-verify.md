# T-06 verify-field amendment

```yaml
VERDICT: PASS
DIGEST:
  headline: T-06 verification matches the implemented UI results contract
  feasibility: clear
  surface: S
  flags: []
  recommend: proceed
  tasks: 1
  decisions: 0
  needs_approval: false
  risk: low
  sc_status: []
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-1821-ui-verification-lane/plan.yaml
    - .harness/harness/features/FEAT-1821-ui-verification-lane/feature.json
    - .harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t06-verify.md
  expertise_update: []
  amendments:
    - task: T-06
      field: verify
      was: |
        sh -c 'HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=FEAT-1821-initial-red npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui; rc=$?; test "$rc" -ne 0' && python3 -c "import json,pathlib; p=pathlib.Path('.harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json'); d=json.loads(p.read_text()); named={'C1-HEADER-GEOMETRY','DIR-KPI-IDENTITY','DIR-STATUS-LABEL','TBL-DESKTOP'}; byid={x['check_id'] for x in d['checks']}; shots=[pathlib.Path(s['path']) for x in d['checks'] for s in x['screenshot_evidence']]; assert d['schema']=='harness-ui-results/1' and d['summary']['status']=='fail' and named<=byid and not d['missing_check_ids'] and shots and all(x.stat().st_size>12 and x.read_bytes()[8:12]==b'WEBP' for x in shots)"
      now: |
        sh -c 'HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=FEAT-1821-initial-red npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui; rc=$?; test "$rc" -ne 0' && python3 -c "import json,pathlib; p=pathlib.Path('.harness/harness/features/FEAT-53-metrics-dashboard/runs/FEAT-1821-initial-red/ui/results.json'); d=json.loads(p.read_text()); named={'C1-HEADER-GEOMETRY','DIR-KPI-IDENTITY','DIR-STATUS-LABEL','TBL-DESKTOP'}; byid={x['check_id'] for x in d['checks']}; shots=[pathlib.Path(s['path']) for x in d['checks'] for s in x['screenshots']]; assert d['schema']=='harness-ui-results/1' and d['summary']['status']=='failed' and named<=byid and not d['missing_check_ids'] and shots and all(x.stat().st_size>12 and x.read_bytes()[8:12]==b'WEBP' for x in shots)"
      reason: "contract drift. Main's full discarded run confirmed the implemented T-01 gate and T-03 reporter form uses per-record screenshots and summary status failed."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/research-amend-product-t06-verify.md
```

## Evidence

- Before mutation, T-06.verify matched the complete command in the lead-owned task input byte for byte, including its trailing newline.
- The sole mutation route was the control-plane plan-merge.py record-amendments command; it emitted AMENDED T-06.verify judgement=amendment and applied only plan.yaml and feature.json.
- Focused byte inspection reversed x['screenshots'] to x['screenshot_evidence'] and d['summary']['status']=='failed' to d['summary']['status']=='fail' within T-06, then reproduced the exact pre-amendment plan SHA-256. This proves those two specified tokens are the only plan-byte changes.
- T-06.verify equals the task-input command with exactly the two enumerated substitutions. No task field besides T-06.verify changed.
- feature.json gained exactly one final judgement for T-06.verify with by harness-orchestrator, kind amendment, and the exact contract-drift reason. Its prior 15 judgements and every non-ledger field are unchanged.
- Approval remains approved by operator on 2026-09-18.
- The scoped plan check exited 0 with 13 tasks, 27 anchors resolved, and 0 failures. The pre-existing T-03/T-08 playwright.config.ts overlap remained advisory.
- Files touched are plan.yaml, feature.json, and this research artifact. No code, schema, execution metadata, task status, dependencies, traces, feature state, formatter, linter, broad validation, or project-wide test changed or ran.
- The amendment used 0 retry cycles.
