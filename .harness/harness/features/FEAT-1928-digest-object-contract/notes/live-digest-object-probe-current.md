# FEAT-1928 live digest-object probe receipt

Written by `tests/manual/probe-digest-object-contract.py` from a real, disposable OMP RPC process. `--verify` checks transcript-derived behavior and recorded runtime identity.

- Verdict: **PASS** (18/18 checks)
- Run: 2026-10-04T19:21:24+00:00 → 2026-10-04T19:21:47+00:00
- Command: `omp --config <worktree>/.omp/providers/openai.yml --mode rpc --model openai-codex/gpt-5.6-terra --cwd <worktree>` (cwd `<worktree>`)
- OMP runtime: `omp/18.6.0`, launcher `~/.bun/bin/omp` sha256 `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`
- OMP source: `89d2610993af69427574bde17791df63906ec4e5` (release-tag metadata provenance, not binary identity)
- Harness: HEAD `98b6c38332bf270f4c88dbc89d7b9d044c7b858d` + 0 uncommitted paths; files under test are pinned by sha256 in the record
- Provider `openai`: Main `openai-codex/gpt-5.6-terra`, child `openai-codex/gpt-5.6-sol:medium` (openai-codex/gpt-5.6-sol)
- Ids: main session `01a1085d-292b-7000-9fd6-888bf0b7507c`, task call `call_DDq771eXn4fKJWFgQy3TdaRW|fc_05ad5edf478058b7016ac2a73c16e887d09cb6c1f664ef3b57`, job `DigestObjectProbe`, child session `01a1085d-5db5-7000-9d97-22ba08cba11a`
- Injected schema: executed dispatch schemaMode ['strict'], outputSchema sha256 ['efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2'] (hook bundle `efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2`); job structured output source `caller`, mode `strict`
- Null yield: `{"data": null, "error": null, "type": "result"}` → tool error by **omp-yield-tool (YieldTool.execute)**: 'This task requires structured output matching the declared schema; a last-turn result cannot satisfy it. Submit the full object: {"data":<object matching the schema>}.'
- Retry: 2 yields in child session `01a1085d-5db5-7000-9d97-22ba08cba11a` of job `DigestObjectProbe`; results ['error', 'Result submitted.']
- Completion: lifecycle ['started', 'completed'], job exit 0, structured output `valid`
- Transcript: `.harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.transcript.jsonl` sha256 `073127bf57bd74fb01d5d80934fd3661bd33e4ccb4447bc863e476036d89ad44` (43 records)

Checks:
- PASS: the RPC session became ready
- PASS: Main dispatched exactly one harness-documentor
- PASS: no task call was refused for a dispatcher-supplied schema control
- PASS: the executed dispatch carried the hook's documentor bundle and schemaMode strict
- PASS: the dispatch declares this feature on its first line
- PASS: OMP ran the job with a caller-supplied schema in strict mode (hook injection)
- PASS: the child's system prompt carries the documentor bundle's own fields
- PASS: the first yield carried type result and data explicitly null
- PASS: the null yield came back as a tool error
- PASS: native OMP executed and rejected the null yield against its schema
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
      "name": "the first yield carried type result and data explicitly null",
      "ok": true
    },
    {
      "name": "the null yield came back as a tool error",
      "ok": true
    },
    {
      "name": "native OMP executed and rejected the null yield against its schema",
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
      "session_file": "~/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T19-21-25-547Z_01a1085d-292b-7000-9fd6-888bf0b7507c/DigestObjectProbe.jsonl",
      "session_id": "01a1085d-5db5-7000-9d97-22ba08cba11a"
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
          "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20261004T192124Z-product/probe-artifact.md"
        },
        "error": null,
        "mode": "strict",
        "source": "caller",
        "status": "valid"
      }
    },
    "main_session_id": "01a1085d-292b-7000-9fd6-888bf0b7507c",
    "null_rejection": {
      "native_execution_started": true,
      "rejected_by": "omp-yield-tool (YieldTool.execute)",
      "text": "This task requires structured output matching the declared schema; a last-turn result cannot satisfy it. Submit the full object: {\"data\":<object matching the schema>}."
    },
    "ready_frame": true,
    "task_calls": {
      "schema_control_refusals": 0,
      "task_calls": 1
    },
    "task_tool_call_id": "call_DDq771eXn4fKJWFgQy3TdaRW|fc_05ad5edf478058b7016ac2a73c16e887d09cb6c1f664ef3b57",
    "yields": [
      {
        "arguments": {
          "data": null,
          "error": null,
          "type": "result"
        },
        "data_key_present": true,
        "is_error": true,
        "result_text": "This task requires structured output matching the declared schema; a last-turn result cannot satisfy it. Submit the full object: {\"data\":<object matching the schema>}.",
        "tool_call_id": "call_hxtu4r6Ery9sn3wuePIOjvMN|fc_0fdab11eb5ef4e57016ac2a7455c7087d0a7ec1741280dc9ad"
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
            "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20261004T192124Z-product/probe-artifact.md"
          },
          "error": null,
          "type": null
        },
        "data_key_present": true,
        "is_error": false,
        "result_text": "Result submitted.",
        "tool_call_id": "call_pgcTDscRvYhAHzcg4FP9v8m1|fc_0fdab11eb5ef4e57016ac2a7472a6887d08ab6965d750d09dc"
      }
    ]
  },
  "exit_status": {
    "job_exit_code": 0,
    "omp_process_returncode": 0,
    "probe_exit": 0
  },
  "failed": [],
  "finished_at": "2026-10-04T19:21:47+00:00",
  "harness": {
    "head": "98b6c38332bf270f4c88dbc89d7b9d044c7b858d",
    "uncommitted_paths": 0,
    "under_test_sha256": {
      ".claude/skills/harness/bin/digest-schemas/common.json": "004ec08b92582727d30469796dc953950ddd93c18669395fbddabece53a1e735",
      ".claude/skills/harness/bin/digest-schemas/harness-documentor.json": "7917570a4357cf4402eeb97e567fd7ea26d67635fdf03b5379d2f8794fb6f9ef",
      ".claude/skills/harness/bin/digest_schema.py": "d44b6b2e4a99d534b6619b56c4bde6de35cdb81f589b404cb9762b74621208ef",
      ".claude/skills/harness/bin/validate-digest.py": "089ec5f27ef6f8850d4c0354d971ea5d5a51ed60faecbeb36d1672412aafa650",
      ".omp/extensions/digest-schema.ts": "0ed3f1813c98a748327f92c9fd6ba9f3a82098fbcc7f8de8911a370f951c9a0f",
      ".omp/extensions/harness-hooks.ts": "88ee5de2442705c3a277dddb5b7574bf32b7debf91dfc68b862c06a2aac5fb7d",
      "tests/manual/probe-digest-object-contract.py": "d5769a3aa016a6d285ab523b24ef9386b7c4ffbca79171f598173b9b3bb8df59"
    }
  },
  "ids": {
    "child_session": "01a1085d-5db5-7000-9d97-22ba08cba11a",
    "job": "DigestObjectProbe",
    "main_session": "01a1085d-292b-7000-9fd6-888bf0b7507c",
    "task_tool_call": "call_DDq771eXn4fKJWFgQy3TdaRW|fc_05ad5edf478058b7016ac2a73c16e887d09cb6c1f664ef3b57"
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
  "started_at": "2026-10-04T19:21:24+00:00",
  "transcript": {
    "path": ".harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe-current.transcript.jsonl",
    "records": 43,
    "sha256": "073127bf57bd74fb01d5d80934fd3661bd33e4ccb4447bc863e476036d89ad44"
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
    "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20261004T192124Z-product/probe-artifact.md"
  },
  "verdict": "PASS"
}
```
