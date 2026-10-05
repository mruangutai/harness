# Engineering return examples

Read before preparing your first engineering return or an under-specified-task refusal. The resident
rules are in `harness-digest-dev`; persona schemas are the field authority (DEC-126, DEC-237).
Use the example for your persona and verdict, never another persona's fields.

## dev — frontend, backend, ai, data

Schema: `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/digest-schemas/harness-backend-dev.json`;
frontend, ai and data have their own `harness-<persona>.json` with the same fields.

```js
yield({data: {
  "VERDICT": "PASS",
  "DIGEST": {
    "headline": "export endpoint streams CSV and enforces the tenant filter",
    "tests_added": 3,
    "suite": "pass",
    "task": "T-03",
    "task_verify": "pass",
    "blocked_on": "none",
    "open_questions": [],
    "files_touched": ["src/export.py", "tests/unit/test_export.py"],
    "expertise_update": []
  },
  "artifact": "<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-harness-backend-dev-<runid>.md"
}})
```

## dev-ops

Schema: `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/digest-schemas/harness-dev-ops.json`.

```js
yield({data: {
  "VERDICT": "PASS",
  "DIGEST": {
    "headline": "CI runs the unit suite on every pull request",
    "change_type": "ci",
    "applied": [".github/workflows/ci.yml"],
    "suite": "pass",
    "task": "T-05",
    "task_verify": "pass",
    "test_kinds_written": ["unit: python3 -m pytest tests/unit"],
    "open_questions": [],
    "files_touched": [".github/workflows/ci.yml"],
    "expertise_update": []
  },
  "artifact": "<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-harness-dev-ops-<runid>.md"
}})
```

## Refusing an under-specified task

Dev refusal uses the backend schema above; dev-ops uses its own schema. Every field remains
required on a refusal: `VERDICT: BLOCKED`, concrete task id, `suite: n/a`, `task_verify: n/a`,
no work paths, `artifact: none`, and the missing specification named in the role's fields.

```js
yield({data: {
  "VERDICT": "BLOCKED",
  "DIGEST": {
    "headline": "task T-12 is under-specified and cannot be executed as written",
    "tests_added": 0,
    "suite": "n/a",
    "task": "T-12",
    "task_verify": "n/a",
    "blocked_on": "T-12 contains a placeholder at <location>; needs pm revision",
    "open_questions": [],
    "files_touched": [],
    "expertise_update": []
  },
  "artifact": "none"
}})
```
