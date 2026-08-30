# Receipt — harness-dev-ops (StaleAnchorHazard.DevOpsProbe) — stale-anchor-write-hazard probe

## Verdict on item 6, up front

**(b): a real hole exists, and it is narrower than "enforcement does nothing."** The
mechanism that is supposed to catch this — `check-domain.sh`'s state-file shape gate,
`feature_schema.problems_for_text`'s JSON-decode check — **works correctly and reliably**
when it receives a payload shaped the way the platform's own registration and the OMP
bridge's `preDomain`/`postDomain` are documented to produce (probes 1 and 2, below: both
the named-file `PostToolUse Edit` route and the path-less `PostToolUse Bash` sweep caught
the exact damage pattern from the incident, cleanly, with the expected `not valid JSON`
message). jsonschema is importable and `validate-feature-json.py` runs (probe 4) — this is
not an environment where the checker is silently absent. The `PreToolUse Edit` exit-0 is
by design, not a bug (probe 3, item 3's own framing is correct).

The hole is at the **OMP-bridge-to-`check-domain.sh` handoff for the `edit` tool**
specifically (probe 5): `extractEditPaths(input.input)` is the ONLY thing standing between
a real `edit` `tool_result` event and `check-domain.sh --post` ever being invoked at all,
and **nothing in this repository's test suite exercises that handoff end-to-end.** The 43
passing `omp-hooks.test.ts` cases include three units for `extractEditPaths`'s string
parsing in isolation and two for `gatePath` resolution — zero cases construct a `tool_result`
event with `toolName: "edit"` and assert that `postDomain` reaches the runner with the
right `file_path`, the way the file already does for `toolName: "task"` (`:265`, `:299`).
If the live OMP host's `event.input` for an `edit` result is not shaped `{ input: "<raw
patch text>" }` — or if `input.input` ever fails the `^\[([^#\r\n]+)#[0-9A-F]{4}\]$` header
regex for any reason the format doesn't anticipate — `extractEditPaths` returns `[]`,
`postDomain` calls the runner **zero times**, and `check-domain.sh --post` never runs.
Nothing logs this: no error, no stderr, no exit code, because no process was ever spawned.
This matches the incident's own description exactly ("nothing refused it... caught only
because the next unrelated command happened to parse the file") — a silent zero, not a
suppressed report.

I cannot fully discriminate (a) vs (b) vs (c) from static analysis and offline probing
alone, because I cannot capture the real OMP host's literal `tool_result` payload for a
genuine `edit` call without live OMP telemetry. **The further probe that would close this**:
instrument `postDomain` (or wrap the `runner` it's given) for one real session, perform one
line-anchored edit against a real feature.json, and log the literal `event.input` object
the host delivered — that is the one fact this receipt cannot supply from a static tree.

---

## Item 1 — PostToolUse Edit route (named file, reads what LANDED)

Fixture: `mktemp -d`-rooted `<TMP>/.harness/harness/features/FEAT-99-probe/feature.json`,
copied verbatim from this worktree's `FEAT-44-omp-context-advisory/feature.json` (70
lines), then damaged by deleting line 33 (the closing `}` of the second review entry) —
the exact shape of a stale-anchor offset error: `sed -i '' '33d'`. Confirmed broken before
probing: `json.loads` → `Expecting ',' delimiter: line 33 column 5 (char 764)`.

Command (payload shape read from `check-domain.sh:1-80,318-336` and
`test-check-domain.py:1056-1058,1075-1078`; `--post` + `hook_event_name: PostToolUse` are
redundant-but-both-sufficient signals per `:312-319`):

```
echo "$PAYLOAD" | CLAUDE_PROJECT_DIR="$TMP" HARNESS_PROJECT_DIR="$TMP" \
  .claude/skills/harness/bin/check-domain.sh --post
```
payload: `{"agent_type":"harness-orchestrator","hook_event_name":"PostToolUse","tool_name":"Edit","tool_input":{"file_path":"<TMP>/.../feature.json","old_string":"a","new_string":"b"}}`

**Exit code: 2.**

Verbatim stderr:
```
check-domain: OVER BUDGET (already written) — .harness/harness/features/FEAT-99-probe/feature.json: feature execution-state schema.
  .harness/harness/features/FEAT-99-probe/feature.json: not valid JSON: Expecting ',' delimiter: line 33 column 5 (char 764)
```

**Finding: detection WORKS on this route, given this payload shape.** `old_string`/
`new_string` are irrelevant here — `check-domain.sh:1372-1381` reads the file back off
disk for a named-file POST target, never reconstructs the edit.

## Item 2 — PostToolUse Bash sweep route

Same damaged fixture, no `file_path`, `tool_name: Bash`, command `"true"`. `<TMP>` is not
a git repository.

**Exit code: 2.**

Verbatim stderr: identical two lines to item 1 (same `OVER BUDGET` / `not valid JSON`
message, same file).

**On `SWEEP_SKIP_CLEAN_TRACKED` and the stamp, reasoned honestly against the real
incident's case:** `SWEEP_SKIP_CLEAN_TRACKED` (`:965`) skips a candidate only when it is
**clean-tracked** — byte-identical to its committed HEAD blob (`:1444-1447`). The real
incident's `feature.json` was **modified vs. HEAD at the time** (that is what a bad edit
to an existing tracked file produces), so this skip would **not** have suppressed it — the
skip exists for `git worktree add` materializing clean copies, not for a genuinely dirty
file. The `.harness/.shape-sweep-stamp` high-water mark (`:1394-1408`) only suppresses a
candidate whose `mtime` is **older** than the last sweep; a fresh corrupting write always
postdates the stamp until a sweep actually runs and advances it, so a bad write is never
older than the mark on the very next sweep. **Neither mechanism is a plausible suppressor
of this specific incident.** The real gap, if the sweep never fired at all, is upstream of
both: `check-domain.sh --post`'s Bash-sweep branch is reached only when the OMP bridge
routes a `toolName: "bash"` `tool_result` through `postDomain` (`harness-hooks.ts:265-271`)
— if the agent's next action after the bad edit wasn't a Bash call, the sweep simply never
ran, which is consistent with (b)/item 6, not a defect in the sweep's own skip logic.

## Item 3 — PreToolUse Edit route

Confirmed by reading (`check-domain.sh:1361-1370`) and by running: `Edit` (any content) at
`PreToolUse` exits 0 with no output. Verified twice — once ungoverned (no `agent_type`),
once as `harness-orchestrator` against this worktree's real `.harness/team-config.yaml`
copied into the fixture, to isolate "domain phase passes/is skipped" from "shape phase
runs" — both exited 0.

```
$ echo "$PAYLOAD_PRE_EDIT" | CLAUDE_PROJECT_DIR="$TMP" HARNESS_PROJECT_DIR="$TMP" check-domain.sh
EXIT=0
```

No stderr either run. Matches the file's own comment exactly: "Only `Write` carries a
whole-file `content` to measure, so only `Write` can be blocked before the fact."

## Item 4 — jsonschema importability

```
$ python3 .claude/skills/harness/bin/validate-feature-json.py
scanning <worktree>/.harness/*/features/*/feature.{json,yaml,yml} — 40 file(s)
EXIT=0

$ python3 -c 'import jsonschema; print(jsonschema.__version__)'
4.26.0
EXIT=0
```

**Not exit 3. jsonschema is present and the checker runs in this environment**
(`/opt/homebrew/bin/python3`, Python 3.14.5). This rules out "the checker cannot run at
all here" as an explanation for the incident, and is consistent with probes 1/2 both
succeeding cleanly.

## Item 5 — OMP bridge coverage

Runner used: `bun test` (present at `/opt/homebrew/bin/bun`; this repo's own suite is run
this way — filename filter requires the explicit relative path, not a bare `bun test
<path>` glob-mismatch first attempt).

```
$ bun test ./.claude/skills/harness/bin/omp-hooks.test.ts
 43 pass
 0 fail
 72 expect() calls
Ran 43 tests across 1 file. [21.00ms]
```

**All 43 pass.** But — from source, not the test file — the routing for an `edit` result:

`harness-hooks.ts:577-578`:
```
const toolName = text(event.toolName);
const input = (event.input && typeof event.input === "object" ? event.input : {}) as Dict;
```
`event.input` becomes the routed `Dict` verbatim if the host supplies an object, else `{}`.

`harness-hooks.ts:258-263` (`postDomain`, `edit` branch):
```
if (toolName === "edit") {
  return extractEditPaths(input.input).map((filePath) => runner(cwd, "check-domain.sh", ["--post"], {
    ...base,
    tool_name: "Edit",
    tool_input: { file_path: filePath },
  }));
}
```
`input.input` — the **nested `.input` property of `event.input`** — is what
`extractEditPaths` parses. This presumes the host's `edit` `tool_result` event's `input`
object literally carries an `input: "<raw patch text>"` field (mirroring this very `edit`
tool's own `{i, input}` call signature) and that the raw text still contains the
`[PATH#TAG]` header lines verbatim by the time it reaches this hook.

`extractEditPaths` (`:69-83`) matches **only** `^\[([^#\r\n]+)#[0-9A-F]{4}\]$` header lines
and `^MV (.+)$` lines, line-anchored (`m` flag). A stale `#TAG` (any 4 hex chars) still
matches — the regex never validates the tag against the file's real state — so a
stale-anchor edit's header alone would not defeat extraction. But **any other shape
mismatch does defeat it silently**: a wrapped/truncated patch body, a host that hands the
hook a parsed/structured edit object instead of the raw text, or `event.input.input` being
absent, all yield `[]` from `extractEditPaths`, `[]` from `postDomain`, `undefined` from
`firstBlock([])` (`:275-276`) — no denial, no `isError`, nothing.

**No test in `omp-hooks.test.ts` constructs a `tool_result` event with `toolName: "edit"`
and asserts `postDomain`/the runner is invoked.** Grepped the file directly (`toolName:
"write"`, `toolName: "bash"`, `toolName: "edit"`, `check-domain`) — the only `toolName`
literal test-fired through the handlers is `"task"` (`:265-268`, `:299-302`) and one
`tool_call`-side `"bash"` case at `:242` unrelated to `postDomain`. `extractEditPaths` is
tested only as a pure string function (`:39-53`), never through the event pipeline. **This
absence is the finding**, per the dispatch's own framing: the coverage gap it names.

## Remedy — INSIDE the DEC-174 boundary; main session must execute

None of the files that would need editing to close the item-5 gap or add positive coverage
are on the DEC-174 off-limits list — `omp-hooks.test.ts` and `harness-hooks.ts` are not
named there, and are also not under `.claude/skills/harness/bin/` in a way that collides
with BackendMergeHelper's grant (that grant is scoped to `.claude/skills/harness/bin/**`
and this file *is* under that path — `.claude/skills/harness/bin/omp-hooks.test.ts` — so it
is **BackendMergeHelper's domain this run, not mine to write**, per the dispatch's own
domain split). Recording the spec here rather than writing it:

- **File:** `.claude/skills/harness/bin/omp-hooks.test.ts`
- **Behavior:** add a case that constructs a `tool_result` event with
  `toolName: "edit"`, `input: { input: "[a.ts#A1B2]\nPUT 1.=1:\n+x\n" }` (or the real
  patch-language shape this repo's `_edit` tool emits) fired through
  `registerHarnessHooks`'s `tool_result` handler with a fake `runner`, and asserts the fake
  runner recorded exactly one call with `script: "check-domain.sh"`, `args` including
  `"--post"`, and `payload.tool_input.file_path === "a.ts"` — mirroring the existing
  `"task"`-toolName integration cases at `:265-268`/`:299-302`, which is the established
  pattern for this exact kind of assertion in this file.
- **Test that would prove it:** the new case itself, run via `bun test
  ./.claude/skills/harness/bin/omp-hooks.test.ts`, going from 43 to 44 passing.

This closes the *test-coverage* gap, not the *live-host-shape* uncertainty named in the
verdict above — that uncertainty needs a live probe (a wrapped `runner`, one real session,
one real edit), which is out of reach from a static-tree dispatch and is recorded as the
open question below.

## files_touched

Only this receipt. The scratch fixture (`mktemp -d` tree) was deleted immediately after
probing; `git status --porcelain` confirmed clean before and after. No observations log
entry was appended (nothing here rises above a per-feature finding — it belongs in
`open_questions`, not craft).
