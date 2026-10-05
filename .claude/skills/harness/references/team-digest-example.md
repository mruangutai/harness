# Team return example

Read before preparing your first lead return. Collation and field semantics live in `harness-team`;
the injected lead persona schema is the field authority (DEC-126, DEC-237).
Schema: `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/digest-schemas/harness-eng-lead.json`;
product-lead and validator-lead have their own `harness-<persona>.json` with the same fields.

```js
yield({data: {
  "VERDICT": "FAIL",
  "DIGEST": {
    "headline": "export build lands but QA found no fail-first evidence for SC-02",
    "team": "build",
    "steps_run": 3,
    "cycles_used": 1,
    "members": [
      {"step": "implement", "persona": "harness-backend-dev", "verdict": "PASS", "headline": "export endpoint streams CSV", "files_touched": ["src/export.py"]},
      {"step": "qa", "persona": "harness-qa", "verdict": "FAIL", "headline": "SC-02 lacks fail-first evidence", "files_touched": []},
      {"step": "advise", "persona": "fable-advisor", "status": "skipped", "reason": "agent not resolvable on this host"}
    ],
    "must_fix": ["record fail-first evidence for SC-02"],
    "files_touched": ["src/export.py"],
    "branch": "feat/export",
    "open_questions": [],
    "escalations": [],
    "expertise_update": [],
    "adequacy_notes": [],
    "sc_status": [],
    "needs_approval": "none",
    "severity_max": "none",
    "matrix_ok": false,
    "coverage_gaps": ["SC-02 has no fail-first evidence"],
    "findings": [],
    "readers": [],
    "amendments": []
  },
  "artifact": "<run_dir>/digest.md"
}})
```
