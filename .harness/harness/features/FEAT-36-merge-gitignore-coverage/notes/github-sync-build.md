# GitHub sync evidence — build

After `plan.yaml` recorded T-01 as `done` and `feature.json` recorded status `Building`, the orchestrator ran exactly once:

```text
python3 .agents/skills/harness/bin/gh-sync.py status .harness/harness/features/FEAT-36-merge-gitignore-coverage Building
```

Observed output and exit:

```text
gh-sync: feature.json status -> Building
exit 0
```

No station write is defined for `status Building`; T-01 remains open under D-23. No `close-task`, `status Review`, or retry was run.
