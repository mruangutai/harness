
## Live run 2026-10-04T15:59:08+00:00

- Verdict: **FAIL** (26/28 checks)
- Command: `/Users/molchairuangutai/.bun/bin/omp --mode rpc --model openai-codex/gpt-5.6-terra --config /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.omp/providers/openai.yml --cwd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- cwd: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- OMP: `/Users/molchairuangutai/.bun/bin/omp` → runtime `/Users/molchairuangutai/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent` @ `89d2610993af69427574bde17791df63906ec4e5`
- Installed version: `18.6.0`; launcher sha256: `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`
- Release-tag source SHA above is metadata provenance only, not bundled runtime identity.
- Harness HEAD: `10a9594cae75d241185ecde8745762ec7cd3e5a5`; registered engineering run: `probe-inflight-claim-20261004T155514Z-5782-eng`
- Exercised source sha256: `{".agents/skills/harness/bin/digest_destination.py": "316d623372f227a4a379888777181595d7e1f41a74b4a3ac54967c4a8713b0e8", ".agents/skills/harness/bin/validate-digest.py": "089ec5f27ef6f8850d4c0354d971ea5d5a51ed60faecbeb36d1672412aafa650", ".omp/extensions/harness-hooks.ts": "88ee5de2442705c3a277dddb5b7574bf32b7debf91dfc68b862c06a2aac5fb7d", "tests/manual/probe-inflight-claim-lifecycle.py": "48e86d538562842e23e37504b28b71e1bb1983a13a9fb99c195bb6f92d3a65eb"}`
- Execution failure: `None`
- Session: `{"sessionId": "01a107a0-7211-7000-97d4-208cfedd386c", "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c.jsonl"}`
- Scenarios: S1-orchestrator-background, S2-wake-reclaim, S3-mixed-batch, S4-suite-preservation, S5-settled-empty
- Suite: `python3 tests/integration/test-validate-digest.py` → `{"returncode": 1, "tail": ["37/37 T-04 undeclared digest key cases passed.", "", "1 FAILING."]}`

Checks:
- PASS: omp is on PATH
- PASS: cwd is this feature worktree
- PASS: feature_root places the feature in this linked worktree
- PASS: no fixture substitution: the gates resolve their root to this worktree
- PASS: no fixture substitution: VALIDATE_DIGEST_BIN is unset
- PASS: the hook under test is this worktree's
- PASS: credentials exist for openai-codex
- PASS: the feature registry holds no rows (cutover done, nothing live)
- PASS: the RPC session became ready
- PASS: S1: a background orchestrator started under a real runtime id
- PASS: S1: its lifecycle settlement completed successfully
- PASS: S1: its settled run leaves no row
- PASS: S2: has a settled orchestrator to wake
- PASS: S2: the woken run's write landed (the hook authorizes only an exact-id claim)
- PASS: S2: a row bound to the exact woken id was sampled during the wake
- PASS: S2: the wake settled on the lifecycle bus
- PASS: S2: and leaves no row
- PASS: S3: two governed orchestrators started under real ids
- PASS: S3: a repeated name produced a suffix id (Name-2)
- PASS: S3: a nested lead held a claim under its lineage id (Nest.<id>)
- PASS: S3: no row ever carried a non-governed id or crossed personas (the nested row is the dispatched lead, under its own parent)
- FAIL: S3: every governed child completed successfully (`[{'id': 'Plain', 'agent': 'harness-orchestrator', 'parentToolCallId': 'call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565', 'detached': True, 'agentSource': 'project', 'status': 'completed', 'sessionFile': '/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Plain.jsonl', 'index': 2}, {'id': 'Nest', 'agent': 'harness-orchestrator', 'parentToolCallId': 'call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565', 'detached': True, 'agentSource': 'project', 'description': 'Run BUG-1898 live probe for nested digest results', 'status': 'completed', 'sessionFile': '/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Nest.jsonl', 'index': 1}, {'id': 'Nest.InjuredTurtle', 'agent': 'harness-eng-lead', 'parentToolCallId': 'call_zYDbU5EvoVlgIsp9f65DWK0d|fc_0d441b256fd04ef0016ac2773efe3487d08b741feb057f810b', 'detached': False, 'agentSource': 'project', 'description': 'Create probe digest artifact and return assessment object', 'status': 'failed', 'sessionFile': '/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Nest/Nest.InjuredTurtle.jsonl', 'index': 0}]`)
- PASS: S3: and none leaves a row, nested included
- FAIL: S4: the real suite run passed (`['37/37 T-04 undeclared digest key cases passed.', '', '1 FAILING.']`)
- PASS: S4: the seeded unrelated claim is byte-identical after the suite
- PASS: S4: and the suite changed no other row
- PASS: S5: every governed child observed
- PASS: S5: the feature registry is empty at probe end

Observed ids and registry snapshots:
```json
{
  "ids": {
    "S1/S2 orchestrator": "Scope",
    "S3 governed": [
      "Plain",
      "Nest"
    ],
    "lifecycle": [
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_nerZn91Pznv2CwXleb5G5Si4|fc_0bd283c779391d8e016ac276ecfeb087d097b6fbe552860995",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_nerZn91Pznv2CwXleb5G5Si4|fc_0bd283c779391d8e016ac276ecfeb087d097b6fbe552860995",
        "detached": true,
        "agentSource": "project",
        "description": "Return the BUG-1898 live probe digest object",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_nerZn91Pznv2CwXleb5G5Si4|fc_0bd283c779391d8e016ac276ecfeb087d097b6fbe552860995",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_nerZn91Pznv2CwXleb5G5Si4|fc_0bd283c779391d8e016ac276ecfeb087d097b6fbe552860995",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565",
        "detached": true,
        "agentSource": "bundled",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Nest.jsonl",
        "index": 1
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565",
        "detached": true,
        "agentSource": "bundled",
        "description": "Reply with ok",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Nest.InjuredTurtle",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_zYDbU5EvoVlgIsp9f65DWK0d|fc_0d441b256fd04ef0016ac2773efe3487d08b741feb057f810b",
        "detached": false,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Nest/Nest.InjuredTurtle.jsonl",
        "index": 0
      },
      {
        "id": "Nest.InjuredTurtle",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_zYDbU5EvoVlgIsp9f65DWK0d|fc_0d441b256fd04ef0016ac2773efe3487d08b741feb057f810b",
        "detached": false,
        "agentSource": "project",
        "description": "Create probe digest artifact and return assessment object",
        "status": "failed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Nest/Nest.InjuredTurtle.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_dGw7DHVPpzOf1HoGGPYRWs3I|fc_0839f9374fc5df52016ac27716f5c887d08967d2f27cfd2565",
        "detached": true,
        "agentSource": "project",
        "description": "Run BUG-1898 live probe for nested digest results",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T15-55-17-905Z_01a107a0-7211-7000-97d4-208cfedd386c/Nest.jsonl",
        "index": 1
      }
    ]
  },
  "sentinel": {
    "agent": "harness-qa",
    "agent_id": "Probe.Sentinel",
    "claim_id": "98084c8fbcf94082987c6c328524a40f",
    "cwd": "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract",
    "dispatcher": "probe-sentinel",
    "feature": "BUG-1898-probe-sentinel",
    "parent_agent_id": "Probe",
    "runtime": "omp",
    "started_at": 1791129488.4964101,
    "supervisor_pid": 5782,
    "supervisor_started_at": 1791129314
  },
  "before": [],
  "after": []
}
```

## Live run 2026-10-04T16:02:16+00:00

- Verdict: **FAIL** (8/9 checks)
- Command: `/Users/molchairuangutai/.bun/bin/omp --mode rpc --model openai-codex/gpt-5.6-terra --config /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.omp/providers/openai.yml --cwd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- cwd: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- OMP: `/Users/molchairuangutai/.bun/bin/omp` → runtime `/Users/molchairuangutai/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent` @ `89d2610993af69427574bde17791df63906ec4e5`
- Installed version: `18.6.0`; launcher sha256: `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`
- Release-tag source SHA above is metadata provenance only, not bundled runtime identity.
- Harness HEAD: `10a9594cae75d241185ecde8745762ec7cd3e5a5`; registered engineering run: `probe-inflight-claim-20261004T160215Z-14245-eng`
- Exercised source sha256: `{".agents/skills/harness/bin/digest_destination.py": "cf57df2ec73d8505d7c42baa8b70f8a77b7ae56ca92b09348eba11b2a717c25c", ".agents/skills/harness/bin/validate-digest.py": "089ec5f27ef6f8850d4c0354d971ea5d5a51ed60faecbeb36d1672412aafa650", ".omp/extensions/harness-hooks.ts": "88ee5de2442705c3a277dddb5b7574bf32b7debf91dfc68b862c06a2aac5fb7d", "tests/manual/probe-inflight-claim-lifecycle.py": "48e86d538562842e23e37504b28b71e1bb1983a13a9fb99c195bb6f92d3a65eb"}`
- Execution failure: `Command '['/opt/homebrew/opt/python@3.14/bin/python3.14', '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.claude/skills/harness/bin/feature-record.py', 'run-start', '--file', '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/feature.json', '--id', 'probe-inflight-claim-20261004T160215Z-14245-eng', '--squad', 'engineering', '--agent', 'harness-eng-lead']' returned non-zero exit status 2.`
- Session: `null`
- Scenarios: S1-orchestrator-background, S2-wake-reclaim, S3-mixed-batch, S4-suite-preservation, S5-settled-empty
- Suite: `python3 tests/integration/test-validate-digest.py` → `null`

Checks:
- PASS: omp is on PATH
- PASS: cwd is this feature worktree
- PASS: feature_root places the feature in this linked worktree
- PASS: no fixture substitution: the gates resolve their root to this worktree
- PASS: no fixture substitution: VALIDATE_DIGEST_BIN is unset
- PASS: the hook under test is this worktree's
- PASS: credentials exist for openai-codex
- PASS: the feature registry holds no rows (cutover done, nothing live)
- FAIL: all live scenarios completed without execution failure (`"Command '['/opt/homebrew/opt/python@3.14/bin/python3.14', '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.claude/skills/harness/bin/feature-record.py', 'run-start', '--file', '/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.harness/harness/features/FEAT-1928-digest-object-contract/feature.json', '--id', 'probe-inflight-claim-20261004T160215Z-14245-eng', '--squad', 'engineering', '--agent', 'harness-eng-lead']' returned non-zero exit status 2."`)

Observed ids and registry snapshots:
```json
{
  "ids": null,
  "sentinel": null,
  "before": [],
  "after": []
}
```

## Live run 2026-10-04T16:07:22+00:00

- Verdict: **FAIL** (27/28 checks)
- Command: `/Users/molchairuangutai/.bun/bin/omp --mode rpc --model openai-codex/gpt-5.6-terra --config /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.omp/providers/openai.yml --cwd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- cwd: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- OMP: `/Users/molchairuangutai/.bun/bin/omp` → runtime `/Users/molchairuangutai/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent` @ `89d2610993af69427574bde17791df63906ec4e5`
- Installed version: `18.6.0`; launcher sha256: `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`
- Release-tag source SHA above is metadata provenance only, not bundled runtime identity.
- Harness HEAD: `10a9594cae75d241185ecde8745762ec7cd3e5a5`; registered engineering run: `probe-inflight-claim-20261004T160324Z-16199-eng`
- Exercised source sha256: `{".agents/skills/harness/bin/digest_destination.py": "cf57df2ec73d8505d7c42baa8b70f8a77b7ae56ca92b09348eba11b2a717c25c", ".agents/skills/harness/bin/validate-digest.py": "089ec5f27ef6f8850d4c0354d971ea5d5a51ed60faecbeb36d1672412aafa650", ".omp/extensions/harness-hooks.ts": "88ee5de2442705c3a277dddb5b7574bf32b7debf91dfc68b862c06a2aac5fb7d", "tests/manual/probe-inflight-claim-lifecycle.py": "4472779f620d9ecdea6fe1dc01e4392375870d5b4fc54bb175dcb0880744a825"}`
- Execution failure: `None`
- Session: `{"sessionId": "01a107a7-e9a2-7000-a5af-b414e97d8729", "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729.jsonl"}`
- Scenarios: S1-orchestrator-background, S2-wake-reclaim, S3-mixed-batch, S4-suite-preservation, S5-settled-empty
- Suite: `python3 tests/integration/test-validate-digest.py` → `{"returncode": 0, "tail": ["37/37 T-04 undeclared digest key cases passed.", "", "ALL PASSED."]}`

Checks:
- PASS: omp is on PATH
- PASS: cwd is this feature worktree
- PASS: feature_root places the feature in this linked worktree
- PASS: no fixture substitution: the gates resolve their root to this worktree
- PASS: no fixture substitution: VALIDATE_DIGEST_BIN is unset
- PASS: the hook under test is this worktree's
- PASS: credentials exist for openai-codex
- PASS: the feature registry holds no rows (cutover done, nothing live)
- PASS: the RPC session became ready
- PASS: S1: a background orchestrator started under a real runtime id
- PASS: S1: its lifecycle settlement completed successfully
- PASS: S1: its settled run leaves no row
- PASS: S2: has a settled orchestrator to wake
- PASS: S2: the woken run's write landed (the hook authorizes only an exact-id claim)
- PASS: S2: a row bound to the exact woken id was sampled during the wake
- PASS: S2: the wake settled on the lifecycle bus
- PASS: S2: and leaves no row
- PASS: S3: two governed orchestrators started under real ids
- PASS: S3: a repeated name produced a suffix id (Name-2)
- PASS: S3: a nested lead held a claim under its lineage id (Nest.<id>)
- PASS: S3: no row ever carried a non-governed id or crossed personas (the nested row is the dispatched lead, under its own parent)
- FAIL: S3: every governed child completed successfully (`[{'id': 'Nest', 'agent': 'harness-orchestrator', 'parentToolCallId': 'call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f', 'detached': True, 'agentSource': 'project', 'description': 'Run BUG-1898 nested digest object contract probe', 'status': 'completed', 'sessionFile': '/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Nest.jsonl', 'index': 1}, {'id': 'Plain', 'agent': 'harness-orchestrator', 'parentToolCallId': 'call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f', 'detached': True, 'agentSource': 'project', 'status': 'completed', 'sessionFile': '/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Plain.jsonl', 'index': 2}, {'id': 'Nest.UnableBug', 'agent': 'harness-eng-lead', 'parentToolCallId': 'call_deCfOfXejl1SQc3R6ir4JP7U|fc_04657c9d0858791f016ac2793eed3c87d0a38d7b168825ec80', 'detached': False, 'agentSource': 'project', 'description': 'Create probe digest artifact and return structured result', 'status': 'failed', 'sessionFile': '/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Nest/Nest.UnableBug.jsonl', 'index': 0}]`)
- PASS: S3: and none leaves a row, nested included
- PASS: S4: the real suite run passed
- PASS: S4: the seeded unrelated claim is byte-identical after the suite
- PASS: S4: and the suite changed no other row
- PASS: S5: every governed child observed
- PASS: S5: the feature registry is empty at probe end

Observed ids and registry snapshots:
```json
{
  "ids": {
    "S1/S2 orchestrator": "Scope",
    "S3 governed": [
      "Nest",
      "Plain"
    ],
    "lifecycle": [
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_YqKdyhjUtTvVIUbKDkT9mgNp|fc_0aaec6a48dcc3fdd016ac278e2def487d0a81e1a510159d1c0",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_YqKdyhjUtTvVIUbKDkT9mgNp|fc_0aaec6a48dcc3fdd016ac278e2def487d0a81e1a510159d1c0",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_YqKdyhjUtTvVIUbKDkT9mgNp|fc_0aaec6a48dcc3fdd016ac278e2def487d0a81e1a510159d1c0",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_YqKdyhjUtTvVIUbKDkT9mgNp|fc_0aaec6a48dcc3fdd016ac278e2def487d0a81e1a510159d1c0",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Nest.jsonl",
        "index": 1
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f",
        "detached": true,
        "agentSource": "bundled",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f",
        "detached": true,
        "agentSource": "bundled",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Nest.UnableBug",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_deCfOfXejl1SQc3R6ir4JP7U|fc_04657c9d0858791f016ac2793eed3c87d0a38d7b168825ec80",
        "detached": false,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Nest/Nest.UnableBug.jsonl",
        "index": 0
      },
      {
        "id": "Nest.UnableBug",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_deCfOfXejl1SQc3R6ir4JP7U|fc_04657c9d0858791f016ac2793eed3c87d0a38d7b168825ec80",
        "detached": false,
        "agentSource": "project",
        "description": "Create probe digest artifact and return structured result",
        "status": "failed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Nest/Nest.UnableBug.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_0NSueLpTWWD3t7eZighfiOmJ|fc_03ecc2e79366d702016ac2791adef087d0b9148457fff0eb1f",
        "detached": true,
        "agentSource": "project",
        "description": "Run BUG-1898 nested digest object contract probe",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-03-27-266Z_01a107a7-e9a2-7000-a5af-b414e97d8729/Nest.jsonl",
        "index": 1
      }
    ]
  },
  "sentinel": {
    "agent": "harness-qa",
    "agent_id": "Probe.Sentinel",
    "claim_id": "84ab04b7226746048fb0db8e05070969",
    "cwd": "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract",
    "dispatcher": "probe-sentinel",
    "feature": "BUG-1898-probe-sentinel",
    "parent_agent_id": "Probe",
    "runtime": "omp",
    "started_at": 1791129986.136209,
    "supervisor_pid": 16199,
    "supervisor_started_at": 1791129804
  },
  "before": [],
  "after": []
}
```

## Live run 2026-10-04T16:14:10+00:00

- Verdict: **PASS** (28/28 checks)
- Command: `/Users/molchairuangutai/.bun/bin/omp --mode rpc --model openai-codex/gpt-5.6-terra --config /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.omp/providers/openai.yml --cwd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- cwd: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- OMP: `/Users/molchairuangutai/.bun/bin/omp` → runtime `/Users/molchairuangutai/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent` @ `89d2610993af69427574bde17791df63906ec4e5`
- Installed version: `18.6.0`; launcher sha256: `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`
- Release-tag source SHA above is metadata provenance only, not bundled runtime identity.
- Harness HEAD: `10a9594cae75d241185ecde8745762ec7cd3e5a5`; registered engineering run: `probe-inflight-claim-20261004T161135Z-20503-eng`
- Exercised source sha256: `{".agents/skills/harness/bin/digest_destination.py": "3d321648df75239d342462b7e16cad78de8d8bc3515df16caa88ce03195aef1f", ".agents/skills/harness/bin/validate-digest.py": "089ec5f27ef6f8850d4c0354d971ea5d5a51ed60faecbeb36d1672412aafa650", ".omp/extensions/harness-hooks.ts": "88ee5de2442705c3a277dddb5b7574bf32b7debf91dfc68b862c06a2aac5fb7d", "tests/manual/probe-inflight-claim-lifecycle.py": "4472779f620d9ecdea6fe1dc01e4392375870d5b4fc54bb175dcb0880744a825"}`
- Execution failure: `None`
- Session: `{"sessionId": "01a107af-6695-7000-844a-4225cf788ea2", "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2.jsonl"}`
- Scenarios: S1-orchestrator-background, S2-wake-reclaim, S3-mixed-batch, S4-suite-preservation, S5-settled-empty
- Suite: `python3 tests/integration/test-validate-digest.py` → `{"returncode": 0, "tail": ["37/37 T-04 undeclared digest key cases passed.", "", "ALL PASSED."]}`

Checks:
- PASS: omp is on PATH
- PASS: cwd is this feature worktree
- PASS: feature_root places the feature in this linked worktree
- PASS: no fixture substitution: the gates resolve their root to this worktree
- PASS: no fixture substitution: VALIDATE_DIGEST_BIN is unset
- PASS: the hook under test is this worktree's
- PASS: credentials exist for openai-codex
- PASS: the feature registry holds no rows (cutover done, nothing live)
- PASS: the RPC session became ready
- PASS: S1: a background orchestrator started under a real runtime id
- PASS: S1: its lifecycle settlement completed successfully
- PASS: S1: its settled run leaves no row
- PASS: S2: has a settled orchestrator to wake
- PASS: S2: the woken run's write landed (the hook authorizes only an exact-id claim)
- PASS: S2: a row bound to the exact woken id was sampled during the wake
- PASS: S2: the wake settled on the lifecycle bus
- PASS: S2: and leaves no row
- PASS: S3: two governed orchestrators started under real ids
- PASS: S3: a repeated name produced a suffix id (Name-2)
- PASS: S3: a nested lead held a claim under its lineage id (Nest.<id>)
- PASS: S3: no row ever carried a non-governed id or crossed personas (the nested row is the dispatched lead, under its own parent)
- PASS: S3: every governed child completed successfully
- PASS: S3: and none leaves a row, nested included
- PASS: S4: the real suite run passed
- PASS: S4: the seeded unrelated claim is byte-identical after the suite
- PASS: S4: and the suite changed no other row
- PASS: S5: every governed child observed
- PASS: S5: the feature registry is empty at probe end

Observed ids and registry snapshots:
```json
{
  "ids": {
    "S1/S2 orchestrator": "Scope",
    "S3 governed": [
      "Nest",
      "Plain"
    ],
    "lifecycle": [
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_r0NXx6jdnDn4cLOUBw88xoQV|fc_0ecfa64802dcfce8016ac27ac036fc87d0ae0120ad4ab17988",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_r0NXx6jdnDn4cLOUBw88xoQV|fc_0ecfa64802dcfce8016ac27ac036fc87d0ae0120ad4ab17988",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_r0NXx6jdnDn4cLOUBw88xoQV|fc_0ecfa64802dcfce8016ac27ac036fc87d0ae0120ad4ab17988",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_r0NXx6jdnDn4cLOUBw88xoQV|fc_0ecfa64802dcfce8016ac27ac036fc87d0ae0120ad4ab17988",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_Limqo9nuIP7yXosuFEce9DR7|fc_0924b194b7254d99016ac27ae6edec87d0824612d4d688d87f",
        "detached": true,
        "agentSource": "bundled",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_Limqo9nuIP7yXosuFEce9DR7|fc_0924b194b7254d99016ac27ae6edec87d0824612d4d688d87f",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Nest.jsonl",
        "index": 1
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_Limqo9nuIP7yXosuFEce9DR7|fc_0924b194b7254d99016ac27ae6edec87d0824612d4d688d87f",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_Limqo9nuIP7yXosuFEce9DR7|fc_0924b194b7254d99016ac27ae6edec87d0824612d4d688d87f",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_Limqo9nuIP7yXosuFEce9DR7|fc_0924b194b7254d99016ac27ae6edec87d0824612d4d688d87f",
        "detached": true,
        "agentSource": "bundled",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Nest.CoolFlea",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_tK8eSytfhXK5zDJ5N2TjLD6n|fc_0d3693a5cfb09338016ac27afc86f487d0a6e0c958c301a2aa",
        "detached": false,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Nest/Nest.CoolFlea.jsonl",
        "index": 0
      },
      {
        "id": "Nest.CoolFlea",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_tK8eSytfhXK5zDJ5N2TjLD6n|fc_0d3693a5cfb09338016ac27afc86f487d0a6e0c958c301a2aa",
        "detached": false,
        "agentSource": "project",
        "description": "Create probe digest artifact and return assessment object",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Nest/Nest.CoolFlea.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_Limqo9nuIP7yXosuFEce9DR7|fc_0924b194b7254d99016ac27ae6edec87d0824612d4d688d87f",
        "detached": true,
        "agentSource": "project",
        "description": "Run BUG-1898 live probe for nested digest objects",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-11-38-005Z_01a107af-6695-7000-844a-4225cf788ea2/Nest.jsonl",
        "index": 1
      }
    ]
  },
  "sentinel": {
    "agent": "harness-qa",
    "agent_id": "Probe.Sentinel",
    "claim_id": "c04cff23e19e47eeb70ffded4b95025d",
    "cwd": "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract",
    "dispatcher": "probe-sentinel",
    "feature": "BUG-1898-probe-sentinel",
    "parent_agent_id": "Probe",
    "runtime": "omp",
    "started_at": 1791130394.408597,
    "supervisor_pid": 20503,
    "supervisor_started_at": 1791130295
  },
  "before": [],
  "after": []
}
```

## Live run 2026-10-04T16:47:55+00:00

- Verdict: **PASS** (28/28 checks)
- Command: `/Users/molchairuangutai/.bun/bin/omp --mode rpc --model openai-codex/gpt-5.6-terra --config /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.omp/providers/openai.yml --cwd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- cwd: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- OMP: `/Users/molchairuangutai/.bun/bin/omp` → runtime `/Users/molchairuangutai/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent` @ `89d2610993af69427574bde17791df63906ec4e5`
- Installed version: `18.6.0`; launcher sha256: `3fdbf0d27eb43682b26a4bb487c34516b74d1dc12e373177ae3ecc37053cfd72`
- Release-tag source SHA above is metadata provenance only, not bundled runtime identity.
- Harness HEAD: `7af3e03c24c3389698fa3c8df32a6ca5d4909f0e`; registered engineering run: `probe-inflight-claim-20261004T164505Z-64038-eng`
- Exercised source sha256: `{".agents/skills/harness/bin/digest_destination.py": "e386daf6b0d85a3cb71c0c6a3965da65b703ae97104736c2d14dd29800690996", ".agents/skills/harness/bin/validate-digest.py": "089ec5f27ef6f8850d4c0354d971ea5d5a51ed60faecbeb36d1672412aafa650", ".omp/extensions/harness-hooks.ts": "88ee5de2442705c3a277dddb5b7574bf32b7debf91dfc68b862c06a2aac5fb7d", "tests/manual/probe-inflight-claim-lifecycle.py": "b968b4726f18a9a4cf28bfb00a22948eff5e13c9c68ebd72e186cf34db534ccb"}`
- Execution failure: `None`
- Session: `{"sessionId": "01a107ce-15e2-7000-9d7a-a74cb97d3272", "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272.jsonl"}`
- Scenarios: S1-orchestrator-background, S2-wake-reclaim, S3-mixed-batch, S4-suite-preservation, S5-settled-empty
- Suite: `python3 tests/integration/test-validate-digest.py` → `{"returncode": 0, "tail": ["37/37 T-04 undeclared digest key cases passed.", "", "ALL PASSED."]}`

Checks:
- PASS: omp is on PATH
- PASS: cwd is this feature worktree
- PASS: feature_root places the feature in this linked worktree
- PASS: no fixture substitution: the gates resolve their root to this worktree
- PASS: no fixture substitution: VALIDATE_DIGEST_BIN is unset
- PASS: the hook under test is this worktree's
- PASS: credentials exist for openai-codex
- PASS: the feature registry holds no rows (cutover done, nothing live)
- PASS: the RPC session became ready
- PASS: S1: a background orchestrator started under a real runtime id
- PASS: S1: its lifecycle settlement completed successfully
- PASS: S1: its settled run leaves no row
- PASS: S2: has a settled orchestrator to wake
- PASS: S2: the woken run's write landed (the hook authorizes only an exact-id claim)
- PASS: S2: a row bound to the exact woken id was sampled during the wake
- PASS: S2: the wake settled on the lifecycle bus
- PASS: S2: and leaves no row
- PASS: S3: two governed orchestrators started under real ids
- PASS: S3: a repeated name produced a suffix id (Name-2)
- PASS: S3: a nested lead held a claim under its lineage id (Nest.<id>)
- PASS: S3: no row ever carried a non-governed id or crossed personas (the nested row is the dispatched lead, under its own parent)
- PASS: S3: every governed child completed successfully
- PASS: S3: and none leaves a row, nested included
- PASS: S4: the real suite run passed
- PASS: S4: the seeded unrelated claim is byte-identical after the suite
- PASS: S4: and the suite changed no other row
- PASS: S5: every governed child observed
- PASS: S5: the feature registry is empty at probe end

Observed ids and registry snapshots:
```json
{
  "ids": {
    "S1/S2 orchestrator": "Scope",
    "S3 governed": [
      "Plain",
      "Nest"
    ],
    "lifecycle": [
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_yfkn1o792ENRCl3fuDNPyH9d|fc_09c5c5ce1e6af1a0016ac2829e853c87d098037480208ce5b8",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_yfkn1o792ENRCl3fuDNPyH9d|fc_09c5c5ce1e6af1a0016ac2829e853c87d098037480208ce5b8",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_yfkn1o792ENRCl3fuDNPyH9d|fc_09c5c5ce1e6af1a0016ac2829e853c87d098037480208ce5b8",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_yfkn1o792ENRCl3fuDNPyH9d|fc_09c5c5ce1e6af1a0016ac2829e853c87d098037480208ce5b8",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_rhHX6T2V5GUHhHh5TNfqque8|fc_0ad50f53a87407df016ac282c7280087d0af873ad1a810821b",
        "detached": true,
        "agentSource": "bundled",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_rhHX6T2V5GUHhHh5TNfqque8|fc_0ad50f53a87407df016ac282c7280087d0af873ad1a810821b",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_rhHX6T2V5GUHhHh5TNfqque8|fc_0ad50f53a87407df016ac282c7280087d0af873ad1a810821b",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Nest.jsonl",
        "index": 1
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_rhHX6T2V5GUHhHh5TNfqque8|fc_0ad50f53a87407df016ac282c7280087d0af873ad1a810821b",
        "detached": true,
        "agentSource": "bundled",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_rhHX6T2V5GUHhHh5TNfqque8|fc_0ad50f53a87407df016ac282c7280087d0af873ad1a810821b",
        "detached": true,
        "agentSource": "project",
        "description": "Return the BUG-1898 live probe result object",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Nest.VastCephalopod",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_KGLizeRjuU0aJq25RbsQmrkT|fc_0ce7cfe90b8b0642016ac282ec243c87d09cdc304a5a708c86",
        "detached": false,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Nest/Nest.VastCephalopod.jsonl",
        "index": 0
      },
      {
        "id": "Nest.VastCephalopod",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_KGLizeRjuU0aJq25RbsQmrkT|fc_0ce7cfe90b8b0642016ac282ec243c87d09cdc304a5a708c86",
        "detached": false,
        "agentSource": "project",
        "description": "Create probe digest artifact and return structured verdict",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Nest/Nest.VastCephalopod.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_rhHX6T2V5GUHhHh5TNfqque8|fc_0ad50f53a87407df016ac282c7280087d0af873ad1a810821b",
        "detached": true,
        "agentSource": "project",
        "description": "Run BUG-1898 nested lead digest contract probe",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T16-45-08-962Z_01a107ce-15e2-7000-9d7a-a74cb97d3272/Nest.jsonl",
        "index": 1
      }
    ]
  },
  "sentinel": {
    "agent": "harness-qa",
    "agent_id": "Probe.Sentinel",
    "claim_id": "e3603dac37974e9d9033f8d354956270",
    "cwd": "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract",
    "dispatcher": "probe-sentinel",
    "feature": "BUG-1898-probe-sentinel",
    "parent_agent_id": "Probe",
    "runtime": "omp",
    "started_at": 1791132419.619354,
    "supervisor_pid": 64038,
    "supervisor_started_at": 1791132305
  },
  "before": [],
  "after": []
}
```

## Live run 2026-10-04T22:14:13+00:00

- Verdict: **PASS** (28/28 checks)
- Command: `/Users/molchairuangutai/.bun/bin/omp --mode rpc --model openai-codex/gpt-5.6-terra --config /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract/.omp/providers/openai.yml --cwd /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- cwd: `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract`
- OMP: `/Users/molchairuangutai/.bun/bin/omp` → runtime `/Users/molchairuangutai/.bun/install/global/node_modules/@oh-my-pi/pi-coding-agent` @ `2a2c6dcbbb558c0f8145f67f28b3370984f2bf60`
- Installed version: `18.6.1`; launcher sha256: `348d0987f05eab2f56b6f543933ca6bbb964d8d069cca9a55be3a5efffad041a`
- Release-tag source SHA above is metadata provenance only, not bundled runtime identity.
- Harness HEAD: `c81a57b6c7d62a63b52614e4bcb64a07f7d9fa47`; registered engineering run: `probe-inflight-claim-20261004T221050Z-2292-eng`
- Exercised source sha256: `{".agents/skills/harness/bin/digest_destination.py": "e386daf6b0d85a3cb71c0c6a3965da65b703ae97104736c2d14dd29800690996", ".agents/skills/harness/bin/validate-digest.py": "089ec5f27ef6f8850d4c0354d971ea5d5a51ed60faecbeb36d1672412aafa650", ".omp/extensions/harness-hooks.ts": "456c9af765b8c25351e1a473076a9b2253594671863c2a7e60199090ca850436", "tests/manual/probe-inflight-claim-lifecycle.py": "b968b4726f18a9a4cf28bfb00a22948eff5e13c9c68ebd72e186cf34db534ccb"}`
- Execution failure: `None`
- Session: `{"sessionId": "01a108f8-5282-7000-ac2e-57580c51b770", "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770.jsonl"}`
- Scenarios: S1-orchestrator-background, S2-wake-reclaim, S3-mixed-batch, S4-suite-preservation, S5-settled-empty
- Suite: `python3 tests/integration/test-validate-digest.py` → `{"returncode": 0, "tail": ["37/37 T-04 undeclared digest key cases passed.", "", "ALL PASSED."]}`

Checks:
- PASS: omp is on PATH
- PASS: cwd is this feature worktree
- PASS: feature_root places the feature in this linked worktree
- PASS: no fixture substitution: the gates resolve their root to this worktree
- PASS: no fixture substitution: VALIDATE_DIGEST_BIN is unset
- PASS: the hook under test is this worktree's
- PASS: credentials exist for openai-codex
- PASS: the feature registry holds no rows (cutover done, nothing live)
- PASS: the RPC session became ready
- PASS: S1: a background orchestrator started under a real runtime id
- PASS: S1: its lifecycle settlement completed successfully
- PASS: S1: its settled run leaves no row
- PASS: S2: has a settled orchestrator to wake
- PASS: S2: the woken run's write landed (the hook authorizes only an exact-id claim)
- PASS: S2: a row bound to the exact woken id was sampled during the wake
- PASS: S2: the wake settled on the lifecycle bus
- PASS: S2: and leaves no row
- PASS: S3: two governed orchestrators started under real ids
- PASS: S3: a repeated name produced a suffix id (Name-2)
- PASS: S3: a nested lead held a claim under its lineage id (Nest.<id>)
- PASS: S3: no row ever carried a non-governed id or crossed personas (the nested row is the dispatched lead, under its own parent)
- PASS: S3: every governed child completed successfully
- PASS: S3: and none leaves a row, nested included
- PASS: S4: the real suite run passed
- PASS: S4: the seeded unrelated claim is byte-identical after the suite
- PASS: S4: and the suite changed no other row
- PASS: S5: every governed child observed
- PASS: S5: the feature registry is empty at probe end

Observed ids and registry snapshots:
```json
{
  "ids": {
    "S1/S2 orchestrator": "Scope",
    "S3 governed": [
      "Plain",
      "Nest"
    ],
    "lifecycle": [
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_xkc2zFY8TtwHFCup6MiWMvRT|fc_021498b6794dfc69016ac2cef4cc6c87d0ac64dc7aa1f040c1",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_xkc2zFY8TtwHFCup6MiWMvRT|fc_021498b6794dfc69016ac2cef4cc6c87d0ac64dc7aa1f040c1",
        "detached": true,
        "agentSource": "project",
        "description": "Return the BUG-1898 live probe digest object",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_xkc2zFY8TtwHFCup6MiWMvRT|fc_021498b6794dfc69016ac2cef4cc6c87d0ac64dc7aa1f040c1",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Scope",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_xkc2zFY8TtwHFCup6MiWMvRT|fc_021498b6794dfc69016ac2cef4cc6c87d0ac64dc7aa1f040c1",
        "detached": true,
        "agentSource": "project",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Scope.jsonl",
        "index": 0
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_ptjslXpjfh7X1AFc00hdDSxW|fc_02204057945533de016ac2cf267c0887d09303d1b41c100698",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_ptjslXpjfh7X1AFc00hdDSxW|fc_02204057945533de016ac2cf267c0887d09303d1b41c100698",
        "detached": true,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Nest.jsonl",
        "index": 1
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_ptjslXpjfh7X1AFc00hdDSxW|fc_02204057945533de016ac2cf267c0887d09303d1b41c100698",
        "detached": true,
        "agentSource": "bundled",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Scope-2",
        "agent": "scout",
        "parentToolCallId": "call_ptjslXpjfh7X1AFc00hdDSxW|fc_02204057945533de016ac2cf267c0887d09303d1b41c100698",
        "detached": true,
        "agentSource": "bundled",
        "description": "Reply with ok",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Scope-2.jsonl",
        "index": 0
      },
      {
        "id": "Plain",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_ptjslXpjfh7X1AFc00hdDSxW|fc_02204057945533de016ac2cf267c0887d09303d1b41c100698",
        "detached": true,
        "agentSource": "project",
        "description": "Return the BUG-1898 live probe digest object",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Plain.jsonl",
        "index": 2
      },
      {
        "id": "Nest.FoolishShrew",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_ytrhzIQAWpxMsQDqaz9S88Wa|fc_0b930250daeca0d4016ac2cf4f596887d090109f88a8fcba6b",
        "detached": false,
        "agentSource": "project",
        "status": "started",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Nest/Nest.FoolishShrew.jsonl",
        "index": 0
      },
      {
        "id": "Nest.FoolishShrew",
        "agent": "harness-eng-lead",
        "parentToolCallId": "call_ytrhzIQAWpxMsQDqaz9S88Wa|fc_0b930250daeca0d4016ac2cf4f596887d090109f88a8fcba6b",
        "detached": false,
        "agentSource": "project",
        "description": "Create probe digest and return structured assessment",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Nest/Nest.FoolishShrew.jsonl",
        "index": 0
      },
      {
        "id": "Nest",
        "agent": "harness-orchestrator",
        "parentToolCallId": "call_ptjslXpjfh7X1AFc00hdDSxW|fc_02204057945533de016ac2cf267c0887d09303d1b41c100698",
        "detached": true,
        "agentSource": "project",
        "description": "Run BUG-1898 nested digest object contract probe",
        "status": "completed",
        "sessionFile": "/Users/molchairuangutai/.omp/agent/sessions/-GitHub-harness-.claude-worktrees-harness-FEAT-1928-digest-object-contract/2026-10-04T22-10-54-210Z_01a108f8-5282-7000-ac2e-57580c51b770/Nest.jsonl",
        "index": 1
      }
    ]
  },
  "sentinel": {
    "agent": "harness-qa",
    "agent_id": "Probe.Sentinel",
    "claim_id": "0b56283f9e9b4acab1a6aa1a606e4811",
    "cwd": "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1928-digest-object-contract",
    "dispatcher": "probe-sentinel",
    "feature": "BUG-1898-probe-sentinel",
    "parent_agent_id": "Probe",
    "runtime": "omp",
    "started_at": 1791151975.688565,
    "supervisor_pid": 2292,
    "supervisor_started_at": 1791151850
  },
  "before": [],
  "after": []
}
```
