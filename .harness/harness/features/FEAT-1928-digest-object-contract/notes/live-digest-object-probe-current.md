# FEAT-1928 live digest-object probe receipt

Written by `tests/manual/probe-digest-object-contract.py` from a real, disposable OMP RPC process. `--verify` checks transcript-derived behavior and recorded runtime identity.

- Verdict: **PASS** (18/18 checks)
- Run: 2026-10-04T04:48:07+00:00 → 2026-10-04T04:48:34+00:00
- Command: `omp --config <worktree>/.omp/providers/openai.yml --mode rpc --model openai-codex/gpt-5.6-terra --cwd <worktree>` (cwd `<worktree>`)
- OMP runtime: `omp/18.6.0`, launcher `~/.bun/bin/omp` sha256 `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`
- OMP source: `89d2610993af69427574bde17791df63906ec4e5` (release-tag metadata provenance, not binary identity)
- Harness: HEAD `4379809b1ce7e37e89407b2ade7912abc898fed9` + 0 uncommitted paths; files under test are pinned by sha256 in the record
- Provider `openai`: Main `openai-codex/gpt-5.6-terra`, child `openai-codex/gpt-5.6-sol:medium` (openai-codex/gpt-5.6-sol)
- Ids: main session `01a1053d-a7b7-7000-8ca6-173b16e20feb`, task call `call_4efSAeqhk0iUFr01KVdnaXyX|fc_0a15c232766301a7016ac1da902aec87d08e5ee1b3ad7f7dfe`, job `DigestObjectProbe`, child session `01a1053d-e1e8-7000-9870-e6714968c136`
- Injected schema: executed dispatch schemaMode ['strict'], outputSchema sha256 ['efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2'] (hook bundle `efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2`); job structured output source `caller`, mode `strict`
- Null yield: `{"data": null, "error": null, "type": null}` → tool error by **harness-hook (tool_call block, before OMP's YieldTool.execute)**: 'Harness agents must return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}}) — a string, null, list or missing `data` is not a digest.'
- Retry: 2 yields in child session `01a1053d-e1e8-7000-9870-e6714968c136` of job `DigestObjectProbe`; results ['error', 'Result submitted.']
- Completion: lifecycle ['started', 'completed'], job exit 0, structured output `valid`
- Transcript: `.harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.transcript.jsonl` sha256 `1c43c8c2e3cdfbab549acdaf5d7f41505507963b276d9ecd7be4c48f88669698` (43 records)

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
      "session_file": "~/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T04-48-09-143Z_01a1053d-a7b7-7000-8ca6-173b16e20feb/DigestObjectProbe.jsonl",
      "session_id": "01a1053d-e1e8-7000-9870-e6714968c136"
    },
    "dispatch": {
      "agents": [
        "harness-documentor"
      ],
      "executed_output_schema_sha256": [
        "efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2"
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
            "open_questions": [],
            "stale_found": []
          },
          "VERDICT": "PASS",
          "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20261004T044807Z-product/probe-artifact.md"
        },
        "error": null,
        "mode": "strict",
        "source": "caller",
        "status": "valid"
      }
    },
    "main_session_id": "01a1053d-a7b7-7000-8ca6-173b16e20feb",
    "null_rejection": {
      "rejected_by": "harness-hook (tool_call block, before OMP's YieldTool.execute)",
      "text": "Harness agents must return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}}) \u2014 a string, null, list or missing `data` is not a digest."
    },
    "ready_frame": true,
    "task_calls": {
      "schema_control_refusals": 0,
      "task_calls": 1
    },
    "task_tool_call_id": "call_4efSAeqhk0iUFr01KVdnaXyX|fc_0a15c232766301a7016ac1da902aec87d08e5ee1b3ad7f7dfe",
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
        "tool_call_id": "call_U017vQoD3r7TLyzjqko8pSxR|fc_050ffb8497622a40016ac1da9a9c5487d0af125706a9880c67"
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
              "stale_found": []
            },
            "VERDICT": "PASS",
            "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20261004T044807Z-product/probe-artifact.md"
          },
          "error": null,
          "type": null
        },
        "data_key_present": true,
        "is_error": false,
        "result_text": "Result submitted.",
        "tool_call_id": "call_o2J5nCvLmkBvOS5PFCUxfyHE|fc_050ffb8497622a40016ac1da9cbf2087d0ac073e8e39f3e094"
      }
    ]
  },
  "exit_status": {
    "job_exit_code": 0,
    "omp_process_returncode": 0,
    "probe_exit": 0
  },
  "failed": [],
  "finished_at": "2026-10-04T04:48:34+00:00",
  "harness": {
    "head": "4379809b1ce7e37e89407b2ade7912abc898fed9",
    "uncommitted_paths": 0,
    "under_test_sha256": {
      ".claude/skills/harness/bin/digest-schemas/common.json": "004ec08b92582727d30469796dc953950ddd93c18669395fbddabece53a1e735",
      ".claude/skills/harness/bin/digest-schemas/harness-documentor.json": "7917570a4357cf4402eeb97e567fd7ea26d67635fdf03b5379d2f8794fb6f9ef",
      ".claude/skills/harness/bin/digest_schema.py": "d44b6b2e4a99d534b6619b56c4bde6de35cdb81f589b404cb9762b74621208ef",
      ".claude/skills/harness/bin/validate-digest.py": "915dd87ee22a838d9861e7bfceda44479e2dec4ad52efa92e2e92916b0601016",
      ".omp/extensions/digest-schema.ts": "0ed3f1813c98a748327f92c9fd6ba9f3a82098fbcc7f8de8911a370f951c9a0f",
      ".omp/extensions/harness-hooks.ts": "0c91b49bf4c95a1f070d444bad1f45015f830aa2d692e3658ae885dbfbc17060",
      "tests/manual/probe-digest-object-contract.py": "70ef2074dd838846b9e57233667f50530b6d7e1b52365b2f73adaca892fd9072"
    }
  },
  "ids": {
    "child_session": "01a1053d-e1e8-7000-9870-e6714968c136",
    "job": "DigestObjectProbe",
    "main_session": "01a1053d-a7b7-7000-8ca6-173b16e20feb",
    "task_tool_call": "call_4efSAeqhk0iUFr01KVdnaXyX|fc_0a15c232766301a7016ac1da902aec87d08e5ee1b3ad7f7dfe"
  },
  "injected_bundle_sha256": "efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2",
  "main_model": "openai-codex/gpt-5.6-terra",
  "mode": "live",
  "omp": {
    "launcher": "~/.bun/bin/omp",
    "launcher_sha256": "3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72",
    "runtime": "~/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent",
    "sha": "89d2610993af69427574bde17791df63906ec4e5",
    "source_provenance": "release-tag",
    "version": "omp/18.6.0"
  },
  "persona": "harness-documentor",
  "probe": "digest-object-contract-live",
  "provider": "openai",
  "started_at": "2026-10-04T04:48:07+00:00",
  "transcript": {
    "path": ".harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.transcript.jsonl",
    "records": 43,
    "sha256": "1c43c8c2e3cdfbab549acdaf5d7f41505507963b276d9ecd7be4c48f88669698"
  },
  "valid_object": {
    "DIGEST": {
      "docs_updated": [],
      "expertise_update": [],
      "files_touched": [],
      "gaps": [],
      "headline": "FEAT-1928 live digest-object probe child settled",
      "open_questions": [],
      "stale_found": []
    },
    "VERDICT": "PASS",
    "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20261004T044807Z-product/probe-artifact.md"
  },
  "verdict": "PASS"
}
```
