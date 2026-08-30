# Fixture provenance — `omp-session-*.fixture.jsonl`

Written for T-01. Records where the two committed fixtures came from, at what nesting depth, and
exactly what was scrubbed before staging.

## Source

| | |
|---|---|
| Captured | 2026-08-30 |
| Writer | omp 18.0.10, `anthropic/claude-sonnet-5` parent dispatching a `sonic` subagent |
| Source path | `2026-08-30T00-26-49-983Z_01a0500f-d4ff-7401-a3c1-5f7539918812/PrimaryTiglon.jsonl` |
| **Nesting depth** | **1 — a dispatched subagent, not the main session** |

**The path shape is what establishes the depth**, and it is the reason this capture is valid:

```
<ts>_<session-id>.jsonl              <- main session          (NOT used)
<ts>_<parent-id>/<DispatchLabel>.jsonl  <- subagent, depth 1  (used: PrimaryTiglon.jsonl)
```

The two shapes are distinguished by measurement in `../evidence/README.md:26-27`. The orchestrator
this feature advises always runs as a dispatched subagent, never as the main session, so a
main-session capture would have left the suite green while never exercising the nested case the
feature exists for — issue #923's own failure shape one layer out.

## Why a synthetic-task capture rather than an excerpt of real work

The plan requires a **captured** record shape rather than a hand-authored one, so that the fixture
does not share an author with the reader — the same principle that justified the old SC-01 verifier
("sharing that code would compare a function to itself"). It does **not** require the *content* to be
real work, and content is where the irreversible risk lives: a pushed blob cannot be un-shipped.

So the session was generated deliberately: a parent was asked to dispatch one `sonic` subagent whose
whole task was to run `echo alpha` and reply `done`. **omp wrote every record**, so the schema,
field names, ordering and nesting are host-produced and unmodified. Every payload string was already
trivial before scrubbing. This satisfies the no-shared-author requirement while reducing the
disclosure surface to approximately nothing.

The full scrub below was applied anyway, so the fixtures are provably clean rather than clean by
luck.

## Scrub actions

| field class | action | records affected |
|---|---|---|
| `credential_pin` records (`{type,id,parentId,timestamp,provider,hash}`) | **dropped entirely** | 1 |
| `session.cwd` | replaced with `/tmp/fixture` | 1 |
| `session_init.systemPrompt` | replaced with `fixture system prompt` — this was the **only** field in the capture carrying the local username or absolute paths | 1 |
| `session_init.task` | replaced with `fixture task` | 1 |
| `message.content[].text` and `.thinking` | replaced with `fixture text` | 6 |
| `toolCall.arguments` on assistant records | replaced with `{"command":"echo fixture"}` | 2 |
| `custom.data.args` / `.intent` | replaced with synthetic equivalents | 2 |
| `message.contextSnapshot` | **untouched** — the only structure under test | 2 |

Verified absent from both files after scrubbing, each check run over the concatenated blob:
local username, `/Users` paths, the `/tmp/fx44` capture path, `credential_pin`, `-----BEGIN`,
`AKIA[0-9A-Z]{16}`, and `(sk|ghp|gho|github_pat|xox[abp])[-_][A-Za-z0-9]{8}`.

Then **every line of both files was read by eye** before `git add`, as the task requires. The
automated sweeps in T-01's verify block are a floor, not a substitute for that read.

## Shape of the committed files

| file | records | anchors | notes |
|---|---|---|---|
| `omp-session-anchored.fixture.jsonl` | 13 | 2 | `promptTokens` 28514 then **28614** |
| `omp-session-anchorless.fixture.jsonl` | 11 | 0 | same source, every `contextSnapshot`-bearing record removed |

The newest anchor is **28614**. It differs from the older anchor (28514), from
`DEFAULT_CONTEXT_WARN_TOKENS` (200000), from the `resolveContextWarnTokens` test value (150000), and
from the `contextAdvisoryText` test value (223029) — so a hardcoded return cannot pass any assertion
that reads it.

Neither file carries a comment line; both are pure JSONL, because the reader parses every line.
