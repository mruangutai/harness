# T-05 probe: the generated frontmatter binds a child's yield on OMP 19.2.1

Measured 2026-11-27 by the main session (DEC-174), after T-04 landed at `84e3b617`, in a throwaway project outside every checkout.

## Result

omp_version: 19.2.1
model: claude-opus-5-5
agent_file: .omp/agents/harness-documentor.md
agent_blob: 96f4332cea14e629fca682433197fee6aa96f893
task_item_keys: agent, name, solutionSpace, task
off_schema_yield: rejected
conforming_yield: accepted

Also observed: the child's saved `session_init` carries an `outputSchema` structurally equal to `digest_projection.provider_bundle("harness-documentor")` and `outputSchemaMode: permissive`. Frontmatter cannot set strict mode, as the grilling measured, so the Harness yield hook remains the barrier (T-02).

## Method

The checkout's `.omp/config.yml` was copied verbatim. This copy leaves `task.structured` unset, so OMP's default (off) applies. The probe agent's `structured` and `output` lines are byte-identical to `.omp/agents/harness-documentor.md` at HEAD (checked with `diff`). The run was `omp -p --no-extensions --no-skills --no-rules --no-context-files --no-title --no-lsp --auto-approve`.

Agent `.omp/agents/probe-documentor.md` (output block abbreviated here; full copy in the throwaway project, identical to the agent file at the blob above):
```markdown
---
name: probe-documentor
description: Probe of the generated harness-documentor digest output for BUG-2565 T-05.
tools: [read]
spawns: []
blocking: true
structured: true
output:
  … (the generated harness-documentor output, unchanged)
---
You are a probe. First call yield with data {"wrong": true}. When that is rejected, call yield with exactly this data object:
{"VERDICT": "PASS", "DIGEST": {"headline": "probe", "open_questions": [], "files_touched": [], "expertise_update": [], "docs_updated": [], "gaps": [], "stale_found": []}, "artifact": "none"}
```

The conforming object passed `digest_schema.validate_object("harness-documentor", obj) == []` before it was used.

Parent prompt: This is a tooling experiment. Step 1: print, verbatim, the property names of one task item in your task tool parameter schema exactly as your tool definition gives them (comma separated), and say whether outputSchema or schemaMode appear. Step 2: dispatch the task tool once with agent "probe-documentor" and task "Run your probe steps." Step 3: report the task result status, any data, and any warnings verbatim.

## Evidence

Parent's step 1, verbatim:

> **Step 1:** The properties of a task item are `agent, name, solutionSpace, task`. Neither `outputSchema` nor `schemaMode` appears anywhere in the task tool's parameter schema.

Child transcript, both yields and their results:

- call `yield` with `{"data": "{\"wrong\": true}"}`
  - result (error): "Output does not match schema: VERDICT: is required; DIGEST: is required; artifact: is required; wrong: must not be present. Send `data` as the decoded value, not a JSON string. Call yield again with the corrected shape — 2 retry attempt(s) remain before the schema constraint is dropped."
- call `yield` with `{"data": "{\"VERDICT\": \"PASS\", \"DIGEST\": {\"headline\": \"probe\", \"open_questions\": [], \"files_touched\": [], \"expertise_update\": [], \"docs_updated\": [], \"gaps\": [], \"stale_found\": []}, \"artifact\": \"none\"}"}`
  - result (ok): "Result submitted."

Parent task result, verbatim:
```
<task-result id="IntegralPigeon" agent="probe-documentor" status="completed" duration="4.2s">

<output>
{
  "VERDICT": "PASS",
  "DIGEST": {
    "headline": "probe",
    "open_questions": [],
    "files_touched": [],
    "expertise_update": [],
    "docs_updated": [],
    "gaps": [],
    "stale_found": []
  },
  "artifact": "none"
}
</output>
</task-result>
```
