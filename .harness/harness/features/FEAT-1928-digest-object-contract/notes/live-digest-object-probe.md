# FEAT-1928 live digest-object probe receipt

Written by `tests/manual/probe-digest-object-contract.py` from a real, disposable OMP RPC process. Every field below is re-derived from the transcript by `--verify`; hand edits fail.

- Verdict: **PASS** (18/18 checks)
- Run: 2026-09-29T22:15:13+00:00 → 2026-09-29T22:15:35+00:00
- Command: `omp --config <worktree>/.omp/providers/openai.yml --mode rpc --model openai-codex/gpt-5.6-terra --cwd <worktree>` (cwd `<worktree>`)
- OMP: `4620bb8338e0ecace7ea237da9d5088d16068617` (pin `4620bb8338e0ecace7ea237da9d5088d16068617`)
- Harness: HEAD `6512eedab9439af3df475b97aabf30db17925548` + 63 uncommitted paths; files under test are pinned by sha256 in the record
- Provider `openai`: Main `openai-codex/gpt-5.6-terra`, child `openai-codex/gpt-5.6-sol:medium` (openai-codex/gpt-5.6-sol)
- Ids: main session `01a0ef3c-7dd5-7000-a3e0-2d4c97897f26`, task call `call_i4WBZOXo3C3JqqZrpolsxDh3|fc_0e24612fa42072ea016abc387790e087d09ce9e4346db15e14`, job `DigestObjectProbe`, child session `01a0ef3c-b08d-7000-912a-f697416e03de`
- Injected schema: executed dispatch schemaMode ['strict'], outputSchema sha256 ['0053d7793ca7e68be97829392d314a48a6a41d063efcaa4ccc014df6f22ae6aa'] (hook bundle `0053d7793ca7e68be97829392d314a48a6a41d063efcaa4ccc014df6f22ae6aa`); job structured output source `caller`, mode `strict`
- Null yield: `{"data": null, "error": null, "type": null}` → tool error by **harness-hook (tool_call block, before OMP's YieldTool.execute)**: 'Harness agents must return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}}) — a string, null, list or missing `data` is not a digest.'
- Retry: 2 yields in child session `01a0ef3c-b08d-7000-912a-f697416e03de` of job `DigestObjectProbe`; results ['error', 'Result submitted.']
- Completion: lifecycle ['started', 'completed'], job exit 0, structured output `valid`
- Transcript: `.harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe.transcript.jsonl` sha256 `040974b4eef2099d1069cd8bb7faf75fcf13548e28567e8cf9f6c02d3bbf3044` (43 records)

Checks:
- PASS: the RPC session became ready
- PASS: Main dispatched exactly one harness-documentor
- PASS: no task call was refused for a dispatcher-supplied schema control
- PASS: the executed dispatch carried the hook's documentor bundle and schemaMode strict
- PASS: the dispatch declares this feature on its first line
- PASS: OMP ran the job with a caller-supplied schema in strict mode (hook injection)
- PASS: the child's system prompt carries the documentor bundle's own fields
- PASS: the first yield carried data explicitly null
- PASS: the null yield came back as a tool error
- PASS: a known component refused the null yield
- PASS: the child retried: a later yield in the same session carried the valid object
- PASS: that valid yield was accepted
- PASS: no yield between the null and the valid one was accepted
- PASS: the live bus saw the same job reject then accept a yield
- PASS: the same job settled completed
- PASS: the child session is that job's
- PASS: the job exited 0
- PASS: OMP validated the object: structured output valid and equal to it

Record:

```json
{
  "checks": [
    {
      "name": "the RPC session became ready",
      "ok": true
    },
    {
      "name": "Main dispatched exactly one harness-documentor",
      "ok": true
    },
    {
      "name": "no task call was refused for a dispatcher-supplied schema control",
      "ok": true
    },
    {
      "name": "the executed dispatch carried the hook's documentor bundle and schemaMode strict",
      "ok": true
    },
    {
      "name": "the dispatch declares this feature on its first line",
      "ok": true
    },
    {
      "name": "OMP ran the job with a caller-supplied schema in strict mode (hook injection)",
      "ok": true
    },
    {
      "name": "the child's system prompt carries the documentor bundle's own fields",
      "ok": true
    },
    {
      "name": "the first yield carried data explicitly null",
      "ok": true
    },
    {
      "name": "the null yield came back as a tool error",
      "ok": true
    },
    {
      "name": "a known component refused the null yield",
      "ok": true
    },
    {
      "name": "the child retried: a later yield in the same session carried the valid object",
      "ok": true
    },
    {
      "name": "that valid yield was accepted",
      "ok": true
    },
    {
      "name": "no yield between the null and the valid one was accepted",
      "ok": true
    },
    {
      "name": "the live bus saw the same job reject then accept a yield",
      "ok": true
    },
    {
      "name": "the same job settled completed",
      "ok": true
    },
    {
      "name": "the child session is that job's",
      "ok": true
    },
    {
      "name": "the job exited 0",
      "ok": true
    },
    {
      "name": "OMP validated the object: structured output valid and equal to it",
      "ok": true
    }
  ],
  "child_model": "openai-codex/gpt-5.6-sol:medium",
  "command": "omp --config <worktree>/.omp/providers/openai.yml --mode rpc --model openai-codex/gpt-5.6-terra --cwd <worktree>",
  "cwd": "<worktree>",
  "dry_run": false,
  "evidence": {
    "bus_yield_results": [
      true,
      false
    ],
    "child_session": {
      "agent": "harness-documentor",
      "persona_schema_lines": [
        "\"docs_updated\": [\"README.md\"],",
        "\"stale_found\": [\"docs/cli.md\"],"
      ],
      "providers_models": [
        "openai-codex/gpt-5.6-sol"
      ],
      "session_file": "~/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-09-29T22-15-14-133Z_01a0ef3c-7dd5-7000-a3e0-2d4c97897f26/DigestObjectProbe.jsonl",
      "session_id": "01a0ef3c-b08d-7000-912a-f697416e03de"
    },
    "dispatch": {
      "agents": [
        "harness-documentor"
      ],
      "executed_output_schema_sha256": [
        "0053d7793ca7e68be97829392d314a48a6a41d063efcaa4ccc014df6f22ae6aa"
      ],
      "executed_schema_modes": [
        "strict"
      ],
      "task_first_line": "HARNESS-FEATURE: FEAT-1928-digest-object-contract",
      "top_level_schema_controls": []
    },
    "job": {
      "agent": "harness-documentor",
      "exit_code": 0,
      "id": "DigestObjectProbe",
      "lifecycle": [
        "started",
        "completed"
      ],
      "resolved_model": "openai-codex/gpt-5.6-sol:medium",
      "structured_output": {
        "data": {
          "DIGEST": {
            "docs_updated": [],
            "expertise_update": [],
            "files_touched": [],
            "gaps": [],
            "headline": "FEAT-1928 live digest-object probe child settled",
            "open_questions": []
          },
          "VERDICT": "PASS",
          "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20260929T221513Z-product/probe-artifact.md"
        },
        "error": null,
        "mode": "strict",
        "source": "caller",
        "status": "valid"
      }
    },
    "main_session_id": "01a0ef3c-7dd5-7000-a3e0-2d4c97897f26",
    "null_rejection": {
      "rejected_by": "harness-hook (tool_call block, before OMP's YieldTool.execute)",
      "text": "Harness agents must return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}}) \u2014 a string, null, list or missing `data` is not a digest."
    },
    "ready_frame": true,
    "task_calls": {
      "schema_control_refusals": 0,
      "task_calls": 1
    },
    "task_tool_call_id": "call_i4WBZOXo3C3JqqZrpolsxDh3|fc_0e24612fa42072ea016abc387790e087d09ce9e4346db15e14",
    "yields": [
      {
        "arguments": {
          "data": null,
          "error": null,
          "type": null
        },
        "data_key_present": true,
        "is_error": true,
        "result_text": "Harness agents must return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}}) \u2014 a string, null, list or missing `data` is not a digest.",
        "tool_call_id": "call_wwmZXhoOX8ZPovj497ejPni8|fc_0d05a4a7188fe0ef016abc38813a6887d08cd95eeea0e44b66"
      },
      {
        "arguments": {
          "data": {
            "DIGEST": {
              "docs_updated": [],
              "expertise_update": [],
              "files_touched": [],
              "gaps": [],
              "headline": "FEAT-1928 live digest-object probe child settled",
              "open_questions": [],
              "stale_found": null
            },
            "VERDICT": "PASS",
            "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20260929T221513Z-product/probe-artifact.md"
          },
          "error": null,
          "type": null
        },
        "data_key_present": true,
        "is_error": false,
        "result_text": "Result submitted.",
        "tool_call_id": "call_90hUnO4oVR8qwYWyb1yP7Y37|fc_0d05a4a7188fe0ef016abc3883ed8087d08406d301d2b211eb"
      }
    ]
  },
  "exit_status": {
    "job_exit_code": 0,
    "omp_process_returncode": 0,
    "probe_exit": 0
  },
  "failed": [],
  "finished_at": "2026-09-29T22:15:35+00:00",
  "harness": {
    "head": "6512eedab9439af3df475b97aabf30db17925548",
    "uncommitted_paths": 63,
    "under_test_sha256": {
      ".claude/skills/harness/bin/digest-schemas/common.json": "4e7f4ddb6657d206f44c772116b7fdf426cf122d0c25b26256e276a83755c29a",
      ".claude/skills/harness/bin/digest-schemas/harness-documentor.json": "5c541c8a1b302fad78d236cc61f8ce39c025904a7c5aab03b638bdc66a724ad8",
      ".claude/skills/harness/bin/digest_schema.py": "d44b6b2e4a99d534b6619b56c4bde6de35cdb81f589b404cb9762b74621208ef",
      ".claude/skills/harness/bin/validate-digest.py": "0b1734da50990f1a61b8c07a1148fdfcab70df331ba782f11892b7ddfede24af",
      ".omp/extensions/digest-schema.ts": "0ed3f1813c98a748327f92c9fd6ba9f3a82098fbcc7f8de8911a370f951c9a0f",
      ".omp/extensions/harness-hooks.ts": "8eecb7905eeee9a573df5c1de29e01f0b09b16671b4c872bdbf707610ae522a9"
    }
  },
  "ids": {
    "child_session": "01a0ef3c-b08d-7000-912a-f697416e03de",
    "job": "DigestObjectProbe",
    "main_session": "01a0ef3c-7dd5-7000-a3e0-2d4c97897f26",
    "task_tool_call": "call_i4WBZOXo3C3JqqZrpolsxDh3|fc_0e24612fa42072ea016abc387790e087d09ce9e4346db15e14"
  },
  "injected_bundle_sha256": "0053d7793ca7e68be97829392d314a48a6a41d063efcaa4ccc014df6f22ae6aa",
  "main_model": "openai-codex/gpt-5.6-terra",
  "mode": "live",
  "omp": {
    "launcher": "~/.bun/bin/omp",
    "pin": "4620bb8338e0ecace7ea237da9d5088d16068617",
    "runtime": "~/.local/share/omp-upstream/omp-18.4.2",
    "sha": "4620bb8338e0ecace7ea237da9d5088d16068617"
  },
  "persona": "harness-documentor",
  "probe": "digest-object-contract-live",
  "provider": "openai",
  "started_at": "2026-09-29T22:15:13+00:00",
  "transcript": {
    "path": ".harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe.transcript.jsonl",
    "records": 43,
    "sha256": "040974b4eef2099d1069cd8bb7faf75fcf13548e28567e8cf9f6c02d3bbf3044"
  },
  "valid_object": {
    "DIGEST": {
      "docs_updated": [],
      "expertise_update": [],
      "files_touched": [],
      "gaps": [],
      "headline": "FEAT-1928 live digest-object probe child settled",
      "open_questions": []
    },
    "VERDICT": "PASS",
    "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20260929T221513Z-product/probe-artifact.md"
  },
  "verdict": "PASS"
}
```
