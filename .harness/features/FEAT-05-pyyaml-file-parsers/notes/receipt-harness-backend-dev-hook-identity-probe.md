# Receipt — T-09 — hook session-identity probe

**Correction, load-bearing:** an earlier version of this receipt (overwritten below) reported a
resolved-via-`CLAUDE_CODE_SESSION_ID` conclusion from 6 probe lines. Those 6 lines were produced
by running
`test-check-domain.py` with `CLAUDE_PROJECT_DIR=$(pwd)` set manually as part of my own verify
step — a synthetic subprocess invocation of the worktree's own script, not a genuine
Claude-Code-dispatched `PreToolUse` hook fire. That is not the mechanism T-09 is asking about.
Two subsequent genuine triggers (one real `Write`, one real `Edit`, both through the actual tool
— no env override) produced **zero** appends at either candidate root. This receipt reports that
corrected, reproducible result.

## What was actually observed

- **Insertion (`.claude/skills/harness/bin/check-domain.sh`, after the `:242` `sys.exit(0)`):**
  as specified, including the literal `sorted(d.keys())`.
- **Gate-safety check, immediately after insertion:** `CLAUDE_PROJECT_DIR=$(pwd) python3
  .claude/skills/harness/bin/test-check-domain.py` → `11/11 cases passed`, exit 0. The DEC-156
  duplicate-key gate was never silently disabled by the probe.
- **Forced-env test run** (same command as above, run to confirm the block's syntax was live):
  produced exactly 6 probe-format appends, one per ALLOW-branch test case in
  `test-check-domain.py` (6 of its 11 cases reach the state-shape gate; the other 5 are BLOCK
  cases that exit before reaching it). All 6 carried identical content:
  - payload keys: `['agent_type', 'tool_input', 'tool_name']`
  - `CLAUDE_*` env keys: `['CLAUDECODE', 'CLAUDE_CODE_BRIDGE_SESSION_ID',
    'CLAUDE_CODE_CHILD_SESSION', 'CLAUDE_CODE_ENTRYPOINT', 'CLAUDE_CODE_EXECPATH',
    'CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS', 'CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH',
    'CLAUDE_CODE_SESSION_ID', 'CLAUDE_EFFORT', 'CLAUDE_JOB_DIR', 'CLAUDE_PID',
    'CLAUDE_PROJECT_DIR']`
  - id value lengths: `{'CLAUDE_CODE_SESSION_ID': 36, 'CLAUDE_CODE_BRIDGE_SESSION_ID': 32}` —
    non-zero, so where this env is actually inherited it is not an empty-string false positive.
  This is real evidence that Claude Code sets non-empty `CLAUDE_CODE_SESSION_ID` /
  `CLAUDE_CODE_BRIDGE_SESSION_ID` for **subprocesses it spawns** (confirmed here via the Bash
  tool's own child-process environment) — but it is evidence about that Bash subprocess, not
  proof about the separate `PreToolUse` hook subprocess.
- **Two genuine triggers** — a real `Write` (new file) and a real `Edit` (on that file), both
  issued as ordinary tool calls with no env override — produced **zero** probe appends, checked
  at both candidate roots (this worktree's `notes/` and
  `/Users/molchairuangutai/GitHub/harness/.harness/features/FEAT-05-pyyaml-file-parsers/notes/`,
  read-only). Both attempts targeted paths inside my own domain and both attempts, per the
  earlier gate-safety check, would have been ALLOWed by `domain_check()` (consistent with the 6
  ALLOW-branch cases above reaching the same code point when run through the test harness) — so
  the difference is not that the write was denied before reaching the probe.

## Conclusion

- **RESOLVED VIA: mechanism-unknown for the real hook** — not the ESCALATE branch (I do not have
  positive proof the block executed on a genuinely-dispatched hook, so the "none of the four
  chain entries reached the hook" condition is unproven, not confirmed) and not a confirmed PASS
  either. The one thing I can state as a fact: the real, Claude-Code-dispatched `PreToolUse`
  fire for a `Write`/`Edit` in this worktree does **not** demonstrably execute this worktree's
  copy of `check-domain.sh` — two genuine tries left no trace anywhere the probe could have
  written, while a synthetic same-script invocation with a forced `CLAUDE_PROJECT_DIR` reliably
  produced 6 traces per run.
- **Which copy of `check-domain.sh` executes, for a real Write/Edit in this worktree: most
  likely the main checkout's, not this worktree's** — reversing my first-pass conclusion, which
  was drawn from the forced-env test run and did not distinguish "the script's logic works when
  invoked directly" from "Claude Code's real hook dispatch invokes this copy." This is
  consistent with PLAN Q6's finding for `validate-digest.py`: `${CLAUDE_PROJECT_DIR}` in
  `settings.json`'s hook commands appears to resolve to the main checkout for this hook too. I
  did not edit the main checkout to confirm directly (out of scope, explicitly forbidden), so
  this is the best-supported inference, not a certainty — the alternative explanation (worktree
  copy runs, but the probe's `except: pass` silently swallowed both genuine attempts for some
  other reason, e.g. a permissions or path quirk specific to real hook dispatch) cannot be ruled
  out from what I could observe without further access.
- **Extra question (`:97`'s `require_or_bootstrap` call site, no `HOOK_PAYLOAD`):** unresolved
  by this probe for the same reason — I only have env-key evidence from the forced-env path, not
  from a genuine hook fire. My working hypothesis (`CLAUDE_CODE_SESSION_ID` is an ordinary env
  var inherited by any child process regardless of `HOOK_PAYLOAD` plumbing, so `:97` likely
  resolves identity fine without a `HOOK_PAYLOAD="$payload"` addition) is **not verified** by a
  genuine hook fire and should be re-checked once the `${CLAUDE_PROJECT_DIR}` resolution question
  above is settled — flagged as `open_questions`, not asserted as fact.

## Cleanup confirmation

- Probe block removed from `.claude/skills/harness/bin/check-domain.sh` — `grep -c
  'sorted(d.keys())' .claude/skills/harness/bin/check-domain.sh` → `0`.
- `diff` against `/Users/molchairuangutai/GitHub/harness/.claude/skills/harness/bin/check-domain.sh`
  is empty (net zero change), confirmed before insertion, after the forced-env run, and after
  final removal.
- `CLAUDE_PROJECT_DIR=$(pwd) python3 .claude/skills/harness/bin/test-check-domain.py` → `11/11
  cases passed`, exit 0, checked immediately after insertion and again after removal.
- Scratch files used for the two genuine triggers
  (`receipt-harness-backend-dev-scratch-recheck.md`, `receipt-harness-backend-dev-trigger-write.md`)
  were deleted; this file is the sole `hook-identity-probe` artifact.
