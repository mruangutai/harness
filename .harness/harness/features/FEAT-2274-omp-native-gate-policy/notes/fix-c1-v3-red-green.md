# Fix c1 — V3: unavailable notice lost beside a pre refusal

Finding V3 (med, SC-01/SC-07): the `tool_call` handler in `.omp/extensions/harness-hooks.ts`
returned `{ block: true, reason }` without the notices it had already collected. Whenever one
gate denied, a sibling gate's "could not run" notice was dropped. The unit test at
`tests/unit/omp-hooks.test.ts` (~2196) asserted that loss.

## What omp 19.1.0 supports alongside `block: true`

- Installed omp: `~/.bun/bin/omp` (`omp/19.1.0`). It is a Bun-compiled single binary, not a
  node_modules install. No 19.x package source exists on disk; the bun cache only has
  `@oh-my-pi/pi-coding-agent` 18.5.1–18.14.1.
- Type (18.14.1 source, `~/.bun/install/cache/@oh-my-pi/pi-coding-agent@18.14.1@@@1/src/extensibility/shared-events.ts:331`):
  `interface ToolCallEventResult { block?: boolean; reason?: string; input?: Record<string, unknown>; additionalContext?: string }`.
  The doc on `additionalContext` says: "ignored when this or a later handler blocks the call".
  On `accumulateToolCallResult`: "A `block` result short-circuits the caller, discarding
  everything collected so far."
- The 19.1.0 binary was checked with `strings -n 8 $(readlink -f ~/.bun/bin/omp)`. Its embedded
  JS has the same behaviour:
  - `ExtensionRunner.emitToolCall`: `if (c.block) { return c; }` comes before the
    additionalContext accumulator (`jie`).
  - The tool wrapper does `if (r?.block) { const T = r.reason || "Tool execution was blocked by an extension"; throw new Error(T); }`,
    and the agent-loop prep returns `{ block: true, reason: T.reason || ... }`. Neither reads
    `additionalContext` on a block.
- Conclusion: a blocking result cannot carry additionalContext. Only `reason` reaches the model.
  So the notices go in `reason`, after the denial reason.

## Change

- `.omp/extensions/harness-hooks.ts` (tool_call handler, end):
  `if (reason) return { block: true, reason: [reason, ...notices].join("\n") };`
  The call stays blocked and the denying gate's reason comes first. Each notice keeps the
  `Harness: <gate> (<phase>) could not run; nothing was checked. <reason>` form. With no
  notices, the reason is unchanged, so every other refusal assertion holds as-is.
- `tests/unit/omp-hooks.test.ts`, test "FEAT-2274: an explicit deny stays a refusal and a normal
  pass stays silent beside an unavailable gate". The pre assertion encoded the OLD contract
  (notice dropped), which the panel named as wrong. I migrated it to require
  `reason: ["a/denied.ts is outside your domain", notice("check-domain", "pre")].join("\n")`
  with `block: true`. The other assertions in that test (post refusal + notice, clean pass
  silent) are unchanged.

## RED

```
$ cd W && bun test tests/unit/omp-hooks.test.ts -t "explicit deny stays a refusal"
error: expect(received).toEqual(expected)
    "block": true,
-   "reason":
- "a/denied.ts is outside your domain
- Harness: check-domain (pre) could not run; nothing was checked. crashed (RuntimeError: boom)"
- ,
+   "reason": "a/denied.ts is outside your domain",
(fail) OMP task lifecycle adapter > FEAT-2274: an explicit deny stays a refusal and a normal pass stays silent beside an unavailable gate
 0 pass / 1 fail
```

## GREEN

```
$ cd W && bun test tests/unit/omp-hooks.test.ts -t "explicit deny stays a refusal"
 1 pass / 0 fail / 4 expect() calls
$ cd W && bun test tests/unit/omp-hooks.test.ts
 179 pass / 0 fail / 1143 expect() calls
```
