# Grilling — how the harness decides which checkout it is looking at — 2026-08-26

## Destination

Every harness mechanism resolves the same root for the same agent, and that root is the
checkout the agent was assigned. One function answers it. Nothing infers it from where a
process happens to be standing.

## Settled

- **ONE resolver, used everywhere. Not the pattern copied to sixteen places** — one function
  in one module that every site imports. The operator was explicit: "one function, one source,
  centralized."
- **ONE environment variable, not four.** `HARNESS_PROJECT_DIR` is the only name. The chain
  `${HARNESS_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}` is deleted from every site.
- **The variable is an OVERRIDE, never the source.** The root is derived from the code's own
  location. An override is honoured only if it probes as a real harness, and a wrong one is
  IGNORED LOUDLY on stderr rather than obeyed.
- **The worktree is the root, always.** An agent assigned to a feature is judged inside that
  worktree.
- **Neither `harness.json` nor `fleet.yaml` can declare the root.** Both are located BY the
  root, so a declaration inside either is circular. Compared at the operator's request; the
  comparison is what settled it.
- **Worktree staleness is accepted.** No plan-time gate. The operator judges freshness case by
  case rather than a machine refusing.
- **There are TWO questions, not one**, and conflating them is what produced four names:
  *where is this harness installed* (never varies) and *where is this agent working* (varies
  per agent). Only the first is answerable from an environment variable.
- **Root resolution is OUT OF SCOPE for FEAT-37.** Operator ruling, 2026-08-26.

## Not yet specified

**Empty. All three closed on measurement, 2026-08-26.** One was closed on wrong
reasoning, retracted, and re-closed on evidence — the retraction is kept below.

- ~~How the HOOK sites learn the agent's checkout.~~ **Answered, but narrower than #742
  suggests.** Two of eight already resolve the root from payload `cwd`. Every hook payload
  carries `agent_id`, which is the input a correct answer would use. #742's dispatch field fixes
  `dispatch-guard.sh` and reaches no other hook.
- ~~Whether `install_root()` should return a non-joinable handle.~~ **CLOSED: there is no
  `install_root()`.** One function already returns both roots from one call —
  `harness_boundary.worktree_owner(path)`. Measured below. (This item was closed once on
  wrong reasoning, retracted, and is now closed on a measurement.)
- ~~Whether the main session stays exempt from the dispatch gate.~~ **It stays exempt.**
  Governing it would have caught NONE of the six collisions — measured below.

## Out of scope

- FEAT-37-lead-stop-and-wake. Its subject is the lead never-wait rule; root resolution is not
  needed there. Signed 2026-08-26 without it.
- The wider claim-registry redesign. #866 carries it.

## Facts I verified (so pm does not re-derive them)

### The four names are one value

- **`HARNESS_PROJECT_DIR` — assigned in exactly ONE file repo-wide**, `test-gh-close-gate.py:41`.
  Read by 16 files. Documented in zero: not `AGENTS.md`, not `SKILL.md`, not `SPEC.md`, not any
  command. It is a test-injection seam, never a production signal.
- **`CLAUDE_PROJECT_DIR`** — host-owned, names the project root, fixed at session start, never a
  worktree. Appears 9 times in `.claude/settings.json`, always as a command-path prefix.
- **`$(pwd)` / `os.getcwd()`** — the host RESETS the shell's working directory to the project
  root. Observed directly: `cd /tmp` returned "Shell cwd was reset to /Users/.../harness".
- **All three therefore resolve to the main checkout**, always. The fallback chain offers three
  options and one value.
- **Payload `cwd` is the only signal that ever varies**, and it varies by accident — see below.

### Claude Code does not document any of this

A `claude-code-guide` agent was asked four questions and answered NOT SPECIFIED to all four:
whether `${CLAUDE_PROJECT_DIR}` reaches a hook's environment or is only substituted into the
command string; what a hook process's working directory is; whose `cwd` the payload carries for
subagent events; and whether the value can change mid-session. **The harness built its
enforcement layer on an undocumented surface.**

### Why claims landed in two different registries

`dispatch-guard.sh:83` resolves from the DISPATCHING agent's working directory. Two claims, same
session, same mechanism:

| Claim | Dispatcher | Recorded cwd |
| --- | --- | --- |
| `harness-pm` | the triage product-lead, which had no worktree | main checkout |
| `harness-product-lead` | FEAT-37's orchestrator, working in its worktree | the worktree |

**An agent's dispatch prompt names its worktree. Its process working directory does not follow.**
The path is prose. The cwd stays inherited from the spawning session until the agent happens to
run `cd` in an unrelated Bash call. FEAT-41 confirms the negative case: its worktree registry is
empty and its claims went to main, from the same dispatch shape.

### The correct pattern already exists, in one file

`factory_config.py:44-56` derives from `_BIN_DIR`, accepts an override only if it probes, prints
`IGNORING it and using {derived}` on a bad one, and always returns a usable root. Fifteen other
sites roll their own chain with no derivation, no probe and no complaint.

**Measured: it resolves a worktree correctly when run from the worktree's own copy.**

```
main copy:     /Users/.../GitHub/harness
worktree copy: /Users/.../worktrees/harness/FEAT-37-lead-stop-and-wake
```

### The sixteen sites split 7 hooks / 9 scripts

Hooks (always run MAIN's copy): `bash-write-guard.sh`, `branch-create-gate.sh`,
`check-domain.sh`, `context-watch-hook.py`, `dispatch-guard.sh`, `gh-close-gate.sh`,
`inject-expertise.sh`, `validate-digest.py`.

Scripts (invoked by path, so the copy that runs decides): `check-plan-routes.py`,
`check-state.sh`, `factory_config.py`, `gen-decisions-index.py`, `harness_yaml.py`,
`inflight_registry.py`, `run-unit-tests.sh`, `validate-feature-json.py`, `wayfind.py`.

### One function is deliverable — none of these is really bash

Every `.sh` site already runs `python3`, and **four already import a shared harness module**:
`bash-write-guard.sh`, `check-domain.sh`, `check-state.sh`, `post-merge-sweep.sh`. The precedent
for a shared import exists; it was simply not used for this.

### The problem has already been hit and patched privately

`check-domain.sh:885-890`, verbatim: *"a live agent worktree held 38 files matching these globs
and the sweep reached NONE of them, because the globs are joined to `root` and a worktree is a
separate checkout underneath it."* It fixed this for itself with its own
`harness_boundary.linked_worktrees` enumeration. **One site solved the shared problem privately;
the other fifteen got no benefit.** That is the copy/paste the operator ruled against.

### What the platform will and will not give

- **The Agent tool has NO `cwd` parameter.** Five params: `description`, `prompt`,
  `subagent_type`, `model`, `isolation`. `isolation: "worktree"` creates a fresh temporary
  worktree, not a named feature's.
- **`.claude/settings.json` CAN set environment variables session-wide, and already does** —
  `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "3"` enforces the four-tier org. But the value is fixed
  at session start, so it cannot vary per agent.
- **`inject-expertise.sh` can inject `additionalContext`** into every `harness-*` spawn. That is
  machine-generated prose, not a mechanism.
- **`dispatch-guard.sh` receives `tool_input`** — the dispatch prompt itself — and blocks with
  `sys.exit(2)`. It is exempt for the main session (`:38`).
- **`feature-worktree.py path --repo <r> --id <i>`** already turns a feature id into an absolute
  worktree path, with no inference.
- **The staleness check runs at SHIP only.** `grep` finds `feature-worktree.py behind` in
  `harness-ship.md` alone. FEAT-37's plan was written 62 commits behind main; merged current at
  `dbbddc9` on operator ruling.

## Workaround in use until this ships

Dispatch prompts now instruct the agent to `cd` into its worktree before its first dispatch.
Machine-generated prose, not a mechanism, and it works today.

## Closing facts — 2026-08-26, at `ee66ae2`

### The hook answer already exists, in two of eight sites

The hook payload carries `cwd`. `research-FEAT-32-hook-payloads.md` measured it on a governed
dispatch: `agent_type=harness-orchestrator`, `cwd=` the FEAT-32 worktree. So a hook is told where
the calling agent stands, even though the hook process itself runs the main checkout's copy.

| Hook | Resolves root from payload `cwd`? |
| --- | --- |
| `dispatch-guard.sh` | **yes** — `:83`, then walks up to `.harness/team-config.yaml` |
| `validate-digest.py` | **yes** — `:872`, same walk, cwd first |
| `context-watch-hook.py` | reads `cwd` at `:58`, but passes it to `warn_for_agent` — not root resolution |
| `bash-write-guard.sh` | no — env chain only |
| `branch-create-gate.sh` | no |
| `check-domain.sh` | no |
| `gh-close-gate.sh` | no |
| `inject-expertise.sh` | no |

**Two sites solved the shared problem privately and rolled their own walk.** That is the same
shape as `check-domain.sh`'s `linked_worktrees` patch: a real answer, unshared.

### But payload `cwd` is the wrong input, and #742 already ruled the right one

`cwd` reports where the calling agent *stands*. Nothing *sets* where an agent stands — the Agent
tool has no `cwd` parameter, `cd` does not persist between Bash calls, and `bash-write-guard.sh`
refuses it. So `cwd` stays inherited from the spawning session and varies by accident.

**#742 (2026-08-23) carries the ruling**: every governed dispatch opens with a machine-readable
`HARNESS-FEATURE: <flow-id>` line, and a dispatch without it is refused at exit 2. That deletes
`cwd` from the chain rather than reading it more carefully. It is the mechanical answer the
operator asked for, and it was already ruled three days before this grilling.

**#866 is the same defect, re-filed.** Its "carry the feature's root down the dispatch chain
rather than letting `cwd` decide it" is #742's ruling in different words. #866 adds six measured
occurrences and three adjacent defects (stranded claim on a killed holder, a dangerous
`release-all` remedy at a non-existent path, and the `#551` miscitation that should be `#628`).

### The dispatch field reaches exactly one site — a RETRACTION

An earlier cut of this file claimed that once the dispatch declares the feature, no site can
reach the wrong root. **That was inferred, not measured, and it is false.** The measurement that
refutes it was already in this repository, from 2026-08-20.

`FEAT-31/notes/probe-hook-payload-identity.md` captured a real PreToolUse Bash payload from
inside a subagent. **Eleven keys, and `tool_input.prompt` is not among them:**

```
agent_id, agent_type, cwd, hook_event_name, permission_mode, prompt_id,
session_id, tool_input, tool_name, tool_use_id, transcript_path
```

`tool_input` on a Bash payload is the COMMAND — `gh-close-gate.py:25` reads
`tool_input["command"]`. On a Write payload it is the file path and content. **The
`HARNESS-FEATURE:` line lives in `tool_input.prompt` of the DISPATCH payload only, which is a
different tool call at a different moment.** So #742's field is visible to `dispatch-guard.sh`
and to nothing else. Seven hooks and nine scripts never see it.

**A join is possible but unbuilt, and it is three hops.** `agent_id` IS on every hook payload,
and the sidecar `{session_id}/subagents/agent-{agent_id}.jsonl` records the `toolUseId` that
spawned the agent. `dispatch-guard.sh` holds `tool_use_id` at the dispatch. So a later hook could
read its own `agent_id`, read the sidecar, and join back to the recorded feature. That is a real
route. It is not built, it rests on an undocumented sidecar format, and it is not what #742 ruled.

### So the root question splits THREE ways, not two

The Settled section says there are two questions. The measurements say three, because the three
site classes are handed three different inputs:

| Site class | Count | What it is handed | The answer |
| --- | --- | --- | --- |
| Scripts invoked by path | 9 | argv and env | derive from code location — `factory_config.py:44-56` is already correct |
| Hooks | 8 | `agent_id`, `agent_type`, `cwd` | `cwd` today, and it is accidental; the `agent_id` join is unbuilt |
| The dispatch moment | 1 | `tool_input.prompt` | #742's `HARNESS-FEATURE:` field |

**One function serves all three, and it is `worktree_owner` — see below.** The caller passes the
path it has: a target, or `__file__`. #742 alone does NOT fix the other fifteen sites, and an
earlier cut of this file said it did.

### Governing the main session would have caught nothing

`inflight_registry.py:32` — `SINGLE_FLIGHT_AGENTS = ("harness-pm",)`. Only `harness-pm` is ever
refused; every other persona is recorded and waved through. Of the six collisions, **every `pm`
was dispatched by a `harness-orchestrator`, which `dispatch-guard.sh` already governs.** The gate
saw all six and refused none, because the claims landed in different registries. The main session
dispatched orchestrators and leads — neither is single-flight, so a claim there would never have
been refused. The exemption at `dispatch-guard.sh:38` is not the defect. `cwd` is.

### THE SINGLE SOURCE OF TRUTH: `harness_boundary.worktree_owner(path)`

**It already exists, and it returns BOTH roots from one call.** Measured 2026-08-26 at `ee66ae2`:

| Input | `checkout_dir` | `owner_root` |
| --- | --- | --- |
| a bin file in MAIN | the main checkout | the main checkout |
| the SAME bin file in a WORKTREE's own copy | that worktree | **the main checkout** |
| a doc in another worktree | that worktree | **the main checkout** |

Two questions, one call, no ambiguity:

- **"Which checkout is this path in?"** → `checkout_dir`. This is what a guard judging a write
  needs, and it is EXACT, not accidental — the path itself carries the answer.
- **"Where is this harness installed?"** → `owner_root`. Correct **even when the calling code is
  a worktree's own copy**, which is the case every other resolver gets wrong.

It walks up to the first `.git` entry and reads it. A DIRECTORY is the main checkout; a FILE is a
worktree pointer naming its owner. **No git subprocess.** Cost measured at 0.023 ms per write
against a guard that already reads files.

### The two modules are different domains, and neither owns root resolution

| | `factory_config.py` (356 lines) | `harness_boundary.py` (537 lines) |
| --- | --- | --- |
| Owns | the FLEET — `.harness/factory/fleet.yaml`, plus each member repo's `harness.json` read REMOTELY at its default branch | the BOUNDARY — which checkout a path stands in, and whether a write is legal there |
| Scope | many repositories | one repository, many checkouts |
| Imports | `factory_cli`, `factory_gh`, `harness_yaml` — network code | `os`, `re`, `sys` only |

They do not overlap. Root resolution is a THIRD concern that both happen to need, and each grew
its own. **A hook must not import `factory_config`** — it would pull GitHub client code into a
`PreToolUse` path that runs before every Bash call. So the one resolver belongs in
`harness_boundary.py`, which is already light and already imported by the guards.

### `harness_root()`'s JOB is right. Its MECHANISM is measurably broken.

Its stated value, from the module docstring, is real: *"factory_workspace.py and factory_land.py
... operate a CHECKOUT OF ANOTHER REPOSITORY: run from inside it, a relative fleet.yaml path
would resolve against the target repo, not the factory's own."* It must not read cwd. Correct.

**But it derives from `_BIN_DIR`, so a worktree's own copy returns the worktree — and the SPEC.md
probe cannot catch that, because every worktree has SPEC.md.** Verified: all seven.

**Measured harm, today, 2026-08-26.** `gh_cost_log.py:111` calls `harness_root()`. The cost log
for today is SPLIT:

| Checkout | `gh-cost-2026-08-26.jsonl` |
| --- | --- |
| main | **absent** |
| FEAT-41 worktree | 1,213 lines |
| FEAT-37 worktree | 36 lines |

`.gitignore:34` ignores `gh-cost-*.jsonl`, so these never merge back. The record of today's spend
exists in two worktrees and nowhere else. `worktree_owner(__file__)` returns the MAIN checkout in
all three cases. Relevant to #676, which carries the review-and-disable of this log.

The same mechanism reaches `factory_claim.py:45` (`FEATURES_ROOT`) and
`factory_config.py:59` (`FLEET_PATH`). `fleet.yaml` is byte-identical across all eight checkouts
today (md5 `1d3fa204a5ca6f98ace619c52cfced9c`), so `FLEET_PATH` is harmless BY LUCK, not by
design. A per-worktree claim registry defeats the point of a claim.

**What `harness_root()` hands over and what is dropped:** the probed `HARNESS_PROJECT_DIR`
override moves into the one resolver — it is the test-injection seam and tests need it. The
`_BIN_DIR` derivation is dropped; `worktree_owner` replaces it. The SPEC.md probe stays as the
override's validity test, since `.git` alone does not prove a harness checkout.

### So `install_root()` is deleted before it is written

A second function would be a third name for something that already has two, and the harness
already recorded that trap — `worktree_terminal.py:112-113`: *"Matched by SEGMENT NAME, never by
comparing `owner_root` against `factory_config.harness_root()`. That comparison is the CWD trap:
`harness_root()` derives from the calling script's own file."*

The non-joinable-handle idea existed to stop a site joining feature globs to the wrong root. With
`worktree_owner` the wrong root is not returned at all, so there is nothing to defend against.
**Removing the hazard beats naming it.**

### `factory_config.harness_root()` becomes a caller, not a second source

It has 8 production consumers — `feature-worktree.py:67`, `board_lifecycle.py` (×6),
`factory_claim.py:45`, `gh_cost_log.py:111`, and `factory_config.FLEET_PATH:59`. All want the
INSTALL root. **Run from a worktree's own copy it returns the WORKTREE**, because it derives from
`_BIN_DIR/../../../..`. `worktree_owner` returns the true owner in that same case.

Whether those eight are actually wrong today, or per-checkout by intent, is a BUILD-TIME check —
not a claim this file makes. What is settled is that they read from one source afterwards.

**What `harness_root()` keeps and hands over:** the probed `HARNESS_PROJECT_DIR` override that is
IGNORED LOUDLY on stderr when it does not probe (`factory_config.py:44-56`). That behaviour moves
into the single resolver. The variable stays a test-injection seam — assigned repo-wide in exactly
one file, `test-gh-close-gate.py:41`.

### The seven non-dispatch hooks are answered too

The earlier retraction left them with no decided input. They have one: **the target of the
operation**, passed to the same function.

- `check-domain.sh` (Write/Edit) — `tool_input.file_path`. Its own header already says the named
  route works: *"The named-target route already handled this via `_norm`; the sweep did not."*
- `bash-write-guard.sh` — the paths it already parses out of the command.
- `validate-digest.py` — the digest path.
- The four with NO target — `check-domain.sh --post` (a blind sweep), `inject-expertise.sh`,
  `branch-create-gate.sh`, `gh-close-gate.sh` — pass `__file__` and take `owner_root`.

**Measured that this is safe for the target-less four:** expertise files are byte-identical across
all seven worktrees (`diff -rq` returns nothing), and `harness.json`'s `github` block reads
`sync=True repo=mruangutai/harness` in all eight checkouts. The sweep additionally needs
`linked_worktrees(owner_root)`, which `check-domain.sh` already has and no other site can reach.

## What this grilling hands over

**Two pieces. #742's ruling is one of them and is not sufficient on its own.**

1. `HARNESS-FEATURE: <flow-id>` becomes mandatory on every governed dispatch (#742). This fixes
   `dispatch-guard.sh`, which is where every measured collision landed. It fixes nothing else,
   because no other payload carries the dispatch prompt.
2. **`harness_boundary.worktree_owner(path)` becomes the ONE root resolver**, gaining the probed
   `HARNESS_PROJECT_DIR` override from `factory_config.py:44-56`. Callers pass the target they
   are operating on, or `__file__` when they have no target, and read `checkout_dir` or
   `owner_root`. `factory_config.harness_root()` becomes a thin caller of it.
3. All sixteen sites import it. The chain `${HARNESS_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}`
   is deleted, and so is every private re-derivation.
4. **Payload `cwd` is deleted as a root input.** `dispatch-guard.sh:83` and
   `validate-digest.py:872` both read it today, and it is accidental — it is the SPAWNING
   session's directory, not the agent's assignment. The path being operated on replaces it.
5. `#866`'s three adjacent defects ride along, because they live in the same two files.

**Constraint:** `dispatch-guard.sh` and `inflight_registry.py` are inside DEC-174's enumeration.
The main session executes this directly. It must not be built while another feature's build is
live — changing the dispatch gate hits every in-flight agent mid-run.

**Status: CLOSED.** Frontier empty.
