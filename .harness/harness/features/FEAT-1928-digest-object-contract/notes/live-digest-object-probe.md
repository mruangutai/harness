# FEAT-1928 live digest-object probe receipt

Written by `tests/manual/probe-digest-object-contract.py` from a real, disposable OMP RPC process. Every field below is re-derived from the transcript by `--verify`; hand edits fail.

- Verdict: **PASS** (18/18 checks)
- Run: 2026-09-30T00:08:03+00:00 → 2026-09-30T00:08:29+00:00
- Command: `omp --config <worktree>/.omp/providers/openai.yml --mode rpc --model openai-codex/gpt-5.6-terra --cwd <worktree>` (cwd `<worktree>`)
- OMP: `4620bb8338e0ecace7ea237da9d5088d16068617` (pin `4620bb8338e0ecace7ea237da9d5088d16068617`)
- Harness: HEAD `45292dee30b110d7b68b1547aa98fdfc1313648f` + 0 uncommitted paths; files under test are pinned by sha256 in the record
- Provider `openai`: Main `openai-codex/gpt-5.6-terra`, child `openai-codex/gpt-5.6-sol:medium` (openai-codex/gpt-5.6-sol)
- Ids: main session `01a0efa3-cdd3-7000-a7ca-07f47d97b6ec`, task call `call_RCf3O8fIt5M8KPelouzxIRxG|fc_0da80f091dacb218016abc52eb71f087d0ab3f96adb36adc4f`, job `DigestObjectProbe`, child session `01a0efa4-0875-7000-b185-32df1fad7a45`
- Injected schema: executed dispatch schemaMode ['strict'], outputSchema sha256 ['efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2'] (hook bundle `efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2`); job structured output source `caller`, mode `strict`
- Null yield: `{"data": null, "error": null, "type": null}` → tool error by **harness-hook (tool_call block, before OMP's YieldTool.execute)**: 'Harness agents must return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}}) — a string, null, list or missing `data` is not a digest.'
- Retry: 2 yields in child session `01a0efa4-0875-7000-b185-32df1fad7a45` of job `DigestObjectProbe`; results ['error', 'Result submitted.']
- Completion: lifecycle ['started', 'completed'], job exit 0, structured output `valid`
- Transcript: `.harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe.transcript.jsonl` sha256 `88d62e1edfeeb85414957d61322d77e817568f2b4908147fdfceceb6ba400279` (43 records)

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
      "session_file": "~/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-09-30T00-08-04-819Z_01a0efa3-cdd3-7000-a7ca-07f47d97b6ec/DigestObjectProbe.jsonl",
      "session_id": "01a0efa4-0875-7000-b185-32df1fad7a45"
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
          "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20260930T000803Z-product/probe-artifact.md"
        },
        "error": null,
        "mode": "strict",
        "source": "caller",
        "status": "valid"
      }
    },
    "main_session_id": "01a0efa3-cdd3-7000-a7ca-07f47d97b6ec",
    "null_rejection": {
      "rejected_by": "harness-hook (tool_call block, before OMP's YieldTool.execute)",
      "text": "Harness agents must return the digest as an object: yield({data: {VERDICT, DIGEST, artifact}}) \u2014 a string, null, list or missing `data` is not a digest."
    },
    "ready_frame": true,
    "task_calls": {
      "schema_control_refusals": 0,
      "task_calls": 1
    },
    "task_tool_call_id": "call_RCf3O8fIt5M8KPelouzxIRxG|fc_0da80f091dacb218016abc52eb71f087d0ab3f96adb36adc4f",
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
        "tool_call_id": "call_yXoXgFJPfVXaTExGeFFbjlHf|fc_031387b53b341bec016abc52f630f487d0bd5fca90bcc1ba07"
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
            "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20260930T000803Z-product/probe-artifact.md"
          },
          "error": null,
          "type": null
        },
        "data_key_present": true,
        "is_error": false,
        "result_text": "Result submitted.",
        "tool_call_id": "call_CJlOrDdAaMyM67g4cgd8PU2p|fc_031387b53b341bec016abc52f9585c87d096fe436895d0c485"
      }
    ]
  },
  "exit_status": {
    "job_exit_code": 0,
    "omp_process_returncode": 0,
    "probe_exit": 0
  },
  "failed": [],
  "finished_at": "2026-09-30T00:08:29+00:00",
  "harness": {
    "head": "45292dee30b110d7b68b1547aa98fdfc1313648f",
    "uncommitted_paths": 0,
    "under_test_sha256": {
      ".claude/skills/harness/bin/digest-schemas/common.json": "363da9fd13f84a20d5eeb403a14ccdace0ac8caffa376beb1eea3d6454806d77",
      ".claude/skills/harness/bin/digest-schemas/harness-documentor.json": "7917570a4357cf4402eeb97e567fd7ea26d67635fdf03b5379d2f8794fb6f9ef",
      ".claude/skills/harness/bin/digest_schema.py": "d44b6b2e4a99d534b6619b56c4bde6de35cdb81f589b404cb9762b74621208ef",
      ".claude/skills/harness/bin/validate-digest.py": "490e67224e0386431a4a087889db54068b903994276d75983a04f76aa28f2de9",
      ".omp/extensions/digest-schema.ts": "0ed3f1813c98a748327f92c9fd6ba9f3a82098fbcc7f8de8911a370f951c9a0f",
      ".omp/extensions/harness-hooks.ts": "be6e8ff3b6b739ae148ea265e0383f8505dcfc6648040c75eb08d1456851c1d2",
      "tests/manual/probe-digest-object-contract.py": "fbdd0e9405d3ad46e379696990b701761b4198048a69b060b20bcb20f8ad0b9f"
    }
  },
  "ids": {
    "child_session": "01a0efa4-0875-7000-b185-32df1fad7a45",
    "job": "DigestObjectProbe",
    "main_session": "01a0efa3-cdd3-7000-a7ca-07f47d97b6ec",
    "task_tool_call": "call_RCf3O8fIt5M8KPelouzxIRxG|fc_0da80f091dacb218016abc52eb71f087d0ab3f96adb36adc4f"
  },
  "injected_bundle_sha256": "efb2e75f9f2781722b6422a31acf01a43a78830ec2caaf36427d9851543da6d2",
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
  "started_at": "2026-09-30T00:08:03+00:00",
  "transcript": {
    "path": ".harness/harness/features/FEAT-1928-digest-object-contract/notes/live-digest-object-probe.transcript.jsonl",
    "records": 43,
    "sha256": "88d62e1edfeeb85414957d61322d77e817568f2b4908147fdfceceb6ba400279"
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
    "artifact": ".harness/harness/features/FEAT-1928-digest-object-contract/runs/probe-digest-object-20260930T000803Z-product/probe-artifact.md"
  },
  "verdict": "PASS"
}
```

## Operator note: Anthropic run (not part of the verified record)

The same probe at the same HEAD (`45292dee30b110d7b68b1547aa98fdfc1313648f`, clean tree) was
also run live with `--provider anthropic`: `omp --config <worktree>/.omp/providers/anthropic.yml
--mode rpc --model anthropic/claude-sonnet-5 --cwd <worktree>`, 2026-09-30T00:08:40Z → 00:08:58Z,
job `PoisedBarracuda`, child session `01a0efa4-7d06-7000-9f81-54edad83f84e`, child model
`anthropic/claude-opus-5:medium`, transcript sha256
`b054484087119ed25b9ff40f0c179306cbfb1677d9ab61ae9bf0a5108b3589b3` (not kept). It scored 17/18:
every check passed except "the first yield carried data explicitly null". claude-opus-5 sent
`{"data": "null"}`, the four-character string, even though it was told to send the bare JSON
token. This matches three earlier Anthropic runs. OMP does not put `yield` on the Anthropic
strict-tool allowlist (`packages/ai/src/providers/anthropic.ts:5393`), so no grammar makes this
model emit a JSON null. The hook still refused the string with the same RETURN_THE_OBJECT
message, and the same job then completed with exit 0 and structured output `valid` (source
`caller`, mode `strict`). Before either the hook or `YieldTool.execute` runs, OMP's
`validateToolArguments` removes both an optional `data: null` and an optional `data: "null"`
(`packages/ai/src/utils/validation.ts:825-839`), so on both providers the hook sees `data`
absent. The receipt above is the OpenAI run, where the model sent a real JSON null.
