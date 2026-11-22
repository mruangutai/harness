# T-01 design record — FEAT-2274 (main-session-direct)

Pre-edit baseline for fail-first evidence: `1e0b014917125bc9aae1f30a2f6fd53ed239f3bc` (worktree HEAD
after merging origin/main, before any T-01 edit). RED runs are taken against this source.

Build arrangement: Main fixes the contracts below and fans out three file-disjoint slices to plain
(ungoverned) subagents — Python broad gates, Python narrow gates, TypeScript adapter — then writes the
cross-cutting runtime suite last. No harness persona executes (DEC-174).

## C1 — Python unavailable outcome (D-01)

- One stdout line, standalone JSON: `{"decision": "unavailable", "gate": "<script stem>", "reason": "<text>"}`.
  `gate` is the script filename without `.py` (validate-digest emits `validate-digest`, though its
  stderr label stays `check-digest`). Exit status stays 0; stderr diagnostics are kept as today.
- One emitter beside `hook_guard` in `harness_boundary.py`:
  `emit_unavailable(script_path, reason)`; gate derived from `script_path`, never from the label.
- `hook_guard(main, name, fail="open", script=None)`: on an own exception with `fail="open"` and
  `script` given, call the emitter (then return 0 as before). `fail="closed"` is unchanged.
  `run_hook_body(path, ...)` passes `script=path`; validate-digest passes `script=__file__`.
- Deliberate unavailable branches in the four broad gates (missing library/schema/identity
  passthroughs that today print only a diagnostic) call the same emitter. Legitimate
  not-applicable and non-governed passthroughs do NOT emit it. A normal pass never emits it.
- Bootstrap import failure (before harness_boundary loads) prints the same JSON inline.

## C2 — Narrow gates fail closed after applicability

- gh-close-gate, branch-create-gate, plan-sign-gate: read the payload's `tool_input.command` and
  decide applicability with stdlib-only code BEFORE root resolution, repository/library/config
  loads and guard entry. Not applicable → exit 0 at once, touching nothing else.
- Applicable → the rest runs under a closed guard: any own failure (root unresolved, import,
  config, corpus, body exception) exits 2 with a named stderr refusal
  `<gate>: BLOCKED — the gate could not run (<detail>); the command it guards is refused rather
  than left unchecked.` Config-driven not-applicable (github.sync off) still exits 0.
- Applicability keeps each gate's current semantics, exemptions and protected spellings; no coarse
  substring. #2107: a flow branch plus a landed feature.json whose `github.parent` is `"²"` must
  produce a named refusal, not exit 1.

## C3 — Extension adapter (harness-hooks.ts)

- `PolicyResult` gains `unavailable?: string` (the reason). `runPolicy` parses a
  `decision: "unavailable"` line. Structured deny and exit 2 stay refusals.
- BROAD = check-domain.py, bash-write-guard.py, dispatch-guard.py, validate-digest.py: synthesize
  `unavailable` for a non-0/non-2 exit, null status or signal, failure before the Python guard
  loads, a missing gate or interpreter, and a spawnSync error or throw. Never block for these.
- NARROW = gh-close-gate.py, branch-create-gate.py, plan-sign-gate.py: exported
  `narrowGateApplies(script, command): boolean`. On an own failure (missing executable, spawn
  error/throw, non-0/non-2 exit, signal), block only when applicable; otherwise allow silently.
- Notice text, exact shape: `Harness: <gate> (<phase>) could not run; nothing was checked. <reason>`
  with `<phase>` one of pre, post, dispatch, yield. One notice per unavailable invocation, no
  session cache or dedup; several notices on one call join with "\n" into the handler's single
  `additionalContext`. The phase keeps pre/post notices distinct, because omp drops identical
  additionalContext strings across handlers. tool_call returns `additionalContext` alongside any
  `input` revision (env, rooting, schema injection) without replacing it; tool_result returns it
  alongside its content without setting `isError`.
- Every other runPolicy caller (claims, run-start, authorize, feature-root, spend) keeps its
  current posture.

## C4 — Spawn route (before_subagent_spawn)

- Registered independently of `currentAgent`: if `event.agent` matches `harness-*` and
  `event.invocationKind !== "task"`, return `{block: true, reason}` naming the `task` tool.
  Everything else returns undefined. omp 19.1.0 event: `{agent, invocationKind: "task" | "eval",
  modelRole?, patterns, spawnKey?}`.

## C5 — dispatch-guard allowlist

- Delete only the `# THE ALLOWLIST` block (`dispatch-guard.py:320-358` at the baseline) and its
  refusal guidance. No replacement allowlist, no owner-root parity check; spawns frontmatter
  unchanged. Native `assertDepthAndSpawnAllowed` is the sole authority.

## Narrow-gate classifier arrangement (the plan's build-design assignment)

Chosen: two small classifiers, each local to its runtime, with no shared dependency and no general
shell parser — the Python gate's own matcher hoisted above its bootstrap, and a TypeScript
`narrowGateApplies` consulted only when the gate process itself could not run. Agreement is
enforced by tests: the existing spelling/exemption corpora in test-gh-close-gate.py,
test-branch-create-gate.py and test-plan-sign-gate.py are exercised against both classifiers
(in test-omp-native-gate-runtime.py), including unrelated-command controls that must not match.
