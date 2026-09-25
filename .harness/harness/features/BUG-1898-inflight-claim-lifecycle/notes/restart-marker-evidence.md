# Restart and revival: where a run's feature comes from (T-02)

**BLUF.** A governed OMP run resolves its feature at `before_agent_start`, in this order, and
nowhere else:

1. The feature this session already runs, if it is still loaded. This is a wake by message.
2. The one `HARNESS-FEATURE` value in the run's prompt, which is the assignment on a first run.
3. The one live claim bound to this exact runtime id. This covers a restart or revival that
   carries no marker. The search covers the owner-checkout registry plus the registry of every
   registered linked worktree.

If none of these yields exactly one answer, the run is held. Every tool is refused and only a
BLOCKED yield passes. The feature is never guessed from persona, dispatch name, cwd, or session.

## The measured premise

- **DEC-204** (`DECISIONS.md:6360-6364`): the role marker comes from the system prompt, but the
  feature marker does not. OMP places the assignment in the first user message. Reading only
  `before_agent_start.systemPrompt` "was measured losing the feature and falsely treating
  concurrent features as one parent-child tree".
- **Same text, read earlier.** The pinned runtime (`harness-runtime-lineage-v2` @ d0d1f810) emits
  `before_agent_start` from `AgentSession.#prepareAgentStart(message, prompt, …)`
  (`session/agent-session.ts:6765-6787`). `prompt` there is the text of the user message that
  starts the run. On a first run, that is the text DEC-204 captured from `message_end`.
  - Run start happens before the first tool call.
  - Refusal can inject its reason into the same event (`BeforeAgentStartEventResult.message`).
- **The assignment is not the prompt's first line.** A task child's first prompt is rendered
  through `prompts/system/subagent-user-prompt.md` ("Complete assignment thoroughly:" and then
  the assignment). So the hook applies DEC-204's grammar across the whole prompt: one
  `HARNESS-FEATURE` value, and two different values are refused as `feature-conflict`.
  dispatch-guard still enforces the first-line rule on the task text it is given.
- **A revival carries no assignment.** After an OMP restart or a revival, the extension instance
  is fresh and the prompt is the wake message. Case 3 above covers that path.

## Search scope for the markerless lookup

`inflight_registry.find_run_claim(owner_root, agent_id)` (T-01). The hook calls it as
`find-run --agent-id <ctx.agentId> --root <ctx.cwd>`.

- Registries read:
  - the owner checkout (`<root>/.harness/.inflight-claims.json`);
  - every checkout `harness_boundary.linked_worktrees(root)` enumerates from
    `.git/worktrees/*/gitdir`, the same enumeration `feature_root` uses.
- A match is a live claim whose `agent_id` equals the runtime id exactly. A parent id, persona,
  dispatch name or prefix never matches.
- Answers:

  | Condition | Answer |
  |---|---|
  | exactly one match | `{ok, feature, root}` |
  | zero matches | `not-found` |
  | two or more matches | `ambiguous` |
  | any registry unreadable, even with a match elsewhere | `unreadable` |

  Every refusal is non-retryable, and the lookup is read-only.

## Unit receipts

Recorded at this build:

- `bun test tests/unit/omp-hooks.test.ts`: 98 pass, 0 fail.
- `python3 tests/integration/test-inflight-registry.py`: 161/161.

Hook cases, in `describe("BUG-1898 run-start claims on the real registry")`, which runs the real
registry against a temporary checkout:

- **Unique recovery:** "a markerless revival recovers its feature from its one exact live claim".
  The write is authorized and yield validation receives the recovered feature.
- **Zero matches:** "a markerless revival with no exact claim is held: only a BLOCKED yield
  passes". A write, read, bash, task and PASS yield are refused with `not-found`. A BLOCKED yield
  passes, and the registry is untouched.
- **Multiple matches:** "a markerless revival bound in two registries is held as ambiguous". The
  same id is in the owner registry and in a registered linked worktree.
- **Unreadable registry:** "an unreadable registry holds the run, non-retryable, and is left as
  found". The corrupt file's bytes are unchanged afterwards. This is also why startup
  `reconcile` now runs only after a successful run start: its locked writer reads a corrupt
  registry as empty and would rewrite it.

Registry cases in `tests/integration/test-inflight-registry.py`:

- `case_40a_find_run_places_a_unique_match` (owner root and linked worktree).
- `case_40b_find_run_refuses_missing_and_ambiguous`, including the CLI exiting 2.
- `case_40c_find_run_refuses_any_unreadable_registry`.

This note records proof of the settled lookup rule. It does not defer identity selection to a
later live observation. T-04's live probe exercises the same path end to end.
