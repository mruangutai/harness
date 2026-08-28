# Receipt — t-02 retest — once-only refusal bound (Q1)

Task: DEBUG/MEASUREMENT under DEC-139. No fix attempted, no production code touched. Worktree
pinned at `9165162be80e6b39055cff6b989227ce1b875172`, HEAD never moved.

## Verdict on the ONE QUESTION

**Does #551 refuse MORE THAN ONCE when an agent attempts to stop repeatedly while a child is still
live? YES.** CONTRADICTED for both halves — see below. A stop refusal can and does recur for the
same still-live child, with real intervening work between attempts.

## HALF 1 — the hook's own logic (deterministic, no agents)

**Closed.** Drove `validate-digest.py --hook` directly with synthetic stdin payloads across the
2x2 (`stop_hook_active` present/absent x live children present/absent), against a throwaway fake
checkout root (`<scratch>/fakeroot/.harness/team-config.yaml`) seeded with a real
`inflight_registry.claim()` so `live_children()` returned a genuine entry — no probe state touched
the worktree.

| stop_hook_active | children live | exit |
|---|---|---|
| absent | live | **2** (refusal, `check-digest: BLOCKED - returned with children in flight`) |
| true | live | 0 (passes at `:845-846`, never reaches the children check at `:909`) |
| absent | none | 0 |
| true | none | 0 |

Then, critically: **re-ran the exact same absent/live payload a second time against the same
still-live claim (no state changed in between).** It refused again, byte-identical output, exit 2.

**Finding:** the hook has NO internal state that marks "already refused once." The `:903` comment
("Fires AT MOST ONCE per return") describes an *intended* consequence of `stop_hook_active`, not
something the hook enforces itself — `live_children()` is a pure read (it only expires stale
entries, never marks a claim as "already warned about"). Whether the bound holds is entirely a
question of whether the platform sets `stop_hook_active=true` on the retry. That is Half 2.

Confidence: high — deterministic, repeatable, read the exact code path (`:845-846` early return,
`:909-920` children check, `inflight_registry.live_children`/`.claim`/`.release_all`).

## HALF 2 — the platform half (the real question)

**Closed, by two independent pieces of evidence, both pointing the same way.**

**A. Platform's own code — a direct statement, outranks inference.** The installed CLI
(`/Users/molchairuangutai/.local/share/claude/versions/2.1.243`, a compiled binary) contains,
verbatim (via `strings`):

> `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP??8;if(Or>0&&Fr>Or)return U("tengu_stop_hook_block_count",...)`
> `"A hook blocked the turn from ending ${Fr} consecutive times — overriding and ending turn. For
> Stop/SubagentStop hooks, check stop_hook_active in the input and return success while it's true.
> Set CLAUDE_CODE_STOP_HOOK_BLOCK_CAP to raise this limit."`

`Fr` is a **consecutive** block counter, defaulting cap 8, not 1 — the platform is explicitly
designed to tolerate (and re-invoke the hook across) up to 8 consecutive blocks before it forces
the turn to end regardless. `stop_hook_active` is documented here as something the *hook itself*
must check to short-circuit — the platform does not silently suppress the hook call. Nothing in
this text says the flag persists across a stop attempt that follows genuine intervening tool use;
"consecutive" is the operative word, and genuine work between two stop attempts is exactly the
condition where a "consecutive" counter would reasonably reset.

**B. A natural transcript specimen, not the confounder.** Searched all subagent transcripts for
the literal hook output `"Stop hook feedback:"` co-occurring with `"returned with children in
flight"` (the earlier plain-phrase grep was a false-positive magnet — `inflight_registry.py`'s own
source contains the same f-string literal, so any transcript where an agent read/wrote that file
matched too; anchoring on `Stop hook feedback:` isolates genuine hook firings). Found:

`~/.claude/projects/-Users-molchairuangutai-GitHub-harness/e69cbdc1-8355-4358-b5f2-d7604a1a913b/subagents/agent-a89be3fd837d1b779.jsonl`
(agent_type in the refusal text: `harness-orchestrator` — same code path as `lead`, per
`validate-digest.py:909`'s `("lead", "orchestrator")` tuple).

- Line 378, `2026-08-24T23:00:03.161Z`: refusal lists `harness-eng-lead started
  2026-08-24T22:59:07.135172+00:00` as live.
- **Between** lines 378 and 391: a genuine turn — a Bash call, an async agent dispatch ("Async
  agent launched successfully"), more Bash calls, and text responses — spanning ~7 minutes
  (`23:00:03` to `23:06:58`).
- Line 391, `2026-08-24T23:06:58.265Z`: refusal again lists `harness-eng-lead started
  2026-08-24T22:59:07.135172+00:00` — the **identical `started_at`**, i.e. the same claim, not a
  new child. The child was still live at both attempts.

This is exactly the specimen shape the dispatch asked for and the exact confounder it warned
against does not apply here: unlike `aa4bb05730add8058`, the child had not returned between
attempts (same `started_at` proves the claim persisted), and there was real intervening work, not
an immediate identical retry.

Confidence: high on both. (A) is a direct platform statement citing the actual cap and counter
semantics. (B) is a real specimen matching the dispatch's exact validity criteria, not an adjacent
or confounded one.

## DEC-199 one-line verdict

**CONTRADICTED.** DEC-199 (near `.harness/harness/docs/DECISIONS.md:6698-6705`) states the refusal
"fires at most once" because the platform "passes through on `stop_hook_active`." The hook has no
independent enforcement of that bound (Half 1), the platform's own code documents a *consecutive*
block cap of 8 rather than 1 (Half 2A), and a real transcript shows the same live child refused
twice, ~7 minutes and substantial intervening work apart (Half 2B). The fix (ending a lead's turn
after every dispatch) will increase the rate of stop attempts made with children live, and each of
those attempts risks its own refusal, not a single one per return.

## Suite (read-only sanity check, not part of the investigation)

No production code was touched, so no new tests were needed or added. As a truthful `suite`
value to accompany `VERDICT: PASS`, ran the two existing suites that cover the exact files read
during this investigation (read-only — neither writes to the worktree):

```
$ python3 .claude/skills/harness/bin/test-validate-digest.py
...
20/20 T-09 cases passed.
...
2/2 template cases passed.
ALL PASSED.
$ echo $?
0

$ python3 .claude/skills/harness/bin/test-inflight-registry.py
...
PASS - 55/55 checks passed
$ echo $?
0
```

Both exit 0. Note `test-validate-digest.py` case 9 asserts "stop_hook_active exits 0 WITH
children still on disk" and labels it "D-09's residual... the bound is real" — that is Half 1's
claim (the hook passes through when the flag is set), which this investigation does not dispute.
It says nothing about whether the platform actually sets the flag on a stop attempt following
intervening work — that is Half 2, and it is not covered by this suite.

## Cleanup

`git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-37-lead-stop-and-wake status --porcelain`:

```
?? .harness/harness/features/FEAT-37-lead-stop-and-wake/
```

(That directory holds this run's own artifacts — this receipt plus this run's dir — nothing else.)
All probe payloads and the fake registry lived under the scratchpad
(`/private/tmp/claude-501/.../scratchpad/payload_case{1..4}.json`,
`.../scratchpad/fakeroot{,_empty}/`); the fake registry's claim was released via
`inflight_registry.release_all()` and both fake-root directories were deleted before this receipt
was written. No `validate-digest.py`, `inflight_registry.py`, or their tests were edited.
