---
name: harness-init
description: Configure a fresh Harness checkout. Use when this checkout has no `.harness/`, when check-state reports it unconfigured, or when a schema_version gap calls for --upgrade. To register a repository in a configured fleet, use harness-add-repo.
---

# Harness: Init

This skill configures the Harness checkout you are standing in. It does not register a repository:
use `harness-add-repo` for that. A configured fleet repository that has no first BRIEF yet goes to
`/harness-plan`.

**This harness checkout** is the working copy of the Harness repository you are standing in and running
this skill from. It is not an instruction to clone or install Harness.

**Run this in the main session.** Only the main session can call `AskUserQuestion` — a subagent has no
channel to the user. Delegate the *mechanical detection* to `dev-ops`; never delegate the interview.

**The interview IS a grilling (DEC-164).** Before interviewing, MUST read and run
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-grilling/SKILL.md`.
Record its artifact in `.harness/notes/`; the answers seed the control plane's domain
description and first `.harness/glossary.md` terms.

## Preflight — stop if any of these fails

```bash
test -d .agents/skills/harness/templates && echo "templates ok" || echo "NO TEMPLATES"
git rev-parse --show-toplevel 2>/dev/null || echo "NOT A GIT REPO"
```

- **No templates** → the harness templates directory is not readable from here. Stop and say so;
  there is nothing to instantiate.
- **Not a git repo** → warn but continue. Commit attribution and `review_sha` pinning will not work.
- **`.harness/` already exists** → this harness checkout is initialised. Route to `--upgrade`, do not re-run fresh.

You will need permission to run the scripts in `.agents/skills/harness/bin/`. Ask for it up front
rather than discovering it at step 1 — a denial there is a **stop**, not a detour.

### 1. Checkout prerequisites — HARD GATE, do this first

Run `.agents/skills/harness/references/checkout-prereqs.md` first: the ignore rules, PyYAML,
jsonschema, and a relative `core.hooksPath`. Every checkout needs it, a re-clone of an onboarded
repository included, and a `MISSING` you cannot clear is a **stop**. Enforcement is live the
moment it passes — steps 4 and 5 run *with* it on, and only step 6's restart caveat is real.

### 2. Instantiate this checkout's own config

For the control plane itself, instantiate its own `.harness/harness.json` and
`.harness/team-config.yaml` from the templates — this harness checkout is the only place a
`team-config.yaml` is instantiated.

### 3. Interview — technical

One batched `AskUserQuestion` call:

- **Project type** — web app · API/service · CLI · library · data pipeline
- **Frontend framework** (if any) and **backend framework/language**
- **Does this project have a user-facing UI?** — dev-ops needs this to judge a null `ui` runner
  against a project that has a real UI.

### 4. Delegate detection to `dev-ops`

Spawn `harness-dev-ops` with the answers from step 3. It must:

- Determine the real test runner **for each kind** and write `test_kinds` into the control plane's
  `.harness/harness.json`. `dev-ops` never writes `fleet.yaml` or pushes a product config directly
  to a remote.
- **Verify every `cmd` by running it.** A command that resolves but is misconfigured is worse than one
  that is absent — `node --test src/` reports `tests 1 / fail 1` for a module-load error, which reads
  exactly like a failing suite.
- **Never invent a plausible command.** A kind with no runner keeps `cmd: null`, and its placeholder
  `_reason` is **replaced with the real one** ("no Playwright in this project", "no eval harness yet").
  `qa` treats an active kind with null or unrunnable `cmd` as `BLOCKED`, never a skip
  (DEC-187); an invented command turns a hard gate into a silent no-op.
- **Surface every remaining `cmd: null` to the user as a DECISION, not a footnote (DEC-163).**
  Cross-reference each against what the project actually has: a null `ui` runner in a project with a
  real UI, a null `eval` with real LLM code, a null `integration` with a real database. For each,
  `AskUserQuestion`: stand the runner up now (a dev-ops task), or accept the gap knowing SCs can
  never rest on that kind. Record the answer; an accepted gap belongs in the backlog and
  skips only with explicit `status: excluded`, `excluded_because`, and `signed` naming a
  decision that resolves in the project's decisions file (DEC-187). Retain the kind's key;
  unresolved kinds block, and active kinds require a command run and seen pass. A null kind
  that reaches the first feature unspoken becomes a permanent blind spot nobody chose.
- **Delete the `_reason` on any kind whose `cmd` it fills.** Every kind ships with
  `_reason: "unset — dev-ops has not run detection yet"`. Leaving that next to a command dev-ops has
  since verified states a falsehood about the project's own config.
- Keep worktree and vendor dirs in every `exclude`, or a diff scan multiplies each test file per
  checkout.
- **Report the source layout** in its DIGEST — frontend root, backend root, prompt/agent dir, migrations
  dir, test root, docs root — for the next step. It does not write the manifest itself.
- Check the team conventions: is `@astryxdesign/core` present, is Supabase linked? Report, do not
  silently install.
### 5. Seed the control-plane manifest

Replace every glob marked `# SEED` in this control plane's `.harness/team-config.yaml` with the real
path from dev-ops's report. **You** write this file — it is not in any agent's domain.

`check-domain.py` reads only the control plane's manifest. The live grants are repo-agnostic globs,
and per-repository isolation is unbuilt (issue 495): `harness_boundary.glob_to_re` supports only
`**`, `*`, `?`, and literals, so a per-repository glob is inexpressible today.

Two rules that carry the write-scope guarantee:

- **Two devs must never share a writable path.** If frontend and backend genuinely live in one tree,
  split by subdirectory; if they cannot be split, say so and let the user decide. Overlapping domains
  void the parallel-safety claim silently.
- **Never widen a domain to `**` to make a block go away.** An unseeded glob fails *closed* — the agent
  is blocked with a message naming its permitted paths. That is the loud, safe direction.

Drop a `# SEED` glob entirely if the project has no such directory (no `evals/`, no `migrations/`).
A glob matching nothing is better than a glob matching everything.

**One overlap is deliberate: qa's colocated-test glob.** `**/*.test.*` sits inside the devs' source
roots on purpose — both qa and a dev legitimately write tests, and they never run concurrently on the
same file. **Keep it if the project colocates tests**; drop it only if the project keeps all tests under
a separate root. It is the one exception to the disjointness rule above, and it is not an oversight.
### 6. Verify, then warn about the restart

```bash
python3 .agents/skills/harness/bin/check-state.py                 # this harness checkout
python3 .agents/skills/harness/bin/check-omp-port.py              # OMP hook wiring and roster
python3 .agents/skills/harness/bin/factory_config.py --check-product-configs
```

All three must exit 0. The fleet check reads every declared member. These are real failures, not
noise to talk past.

Then say this, explicitly, as the last thing — **but only if agent definitions were installed or
updated during this same session:**

> **Restart the OMP session before running a team.** Agent definitions are loaded at session start
> (DEC-100a), so agents installed in this session are not spawnable yet. Without a restart the first
> team fails with "Agent type not found" and no explanation.

**Do not overstate this.** Hooks and skills are live immediately; agents that were installed before
this session started are spawnable now. The restart is about **newly written agent files**, nothing
else. Telling a user their harness is inert when it is not is its own kind of wrong.

## `--upgrade`

Before `--upgrade`, MUST read and follow
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/checkout-upgrade.md`
(DEC-158/222). Run in the already-initialised checkout; for a fleet member, land the merged
`harness.json` on its default branch through `harness-add-repo`.

**Preserve every project value, especially verified `test_kinds.*.cmd`.** Resetting a working
active runner to null makes it `BLOCKED`, not a soft skip (DEC-187).
**`team-config.yaml` is report-only, never rewritten**: it belongs only to the control plane,
and `safe_dump` cannot preserve the comments justifying its write-scope globs (DEC-171).
Relay reported new entries and add them by hand, preserving the globs and comments.
**Never change `BRIEF.md`, `PLAN.md` or `DESIGN.md` in an upgrade**: they are content, not
schema. First BRIEF, approval and design work route to `/harness-plan`.

## Red flags

| Thought | Reality |
|---|---|
| "I'll wire a hook into a settings file myself" | Enforcement is `harness-hooks.ts`, loaded with the OMP session and graded by `check-omp-port.py`; there is no settings file to edit |
| "The package install was denied, I'll work around it" | Stop instead. A half-installed init looks finished and has no domain enforcement — observed in testing |
| "They must restart before anything works" | The hooks are live now. Only newly-written agent files need the restart |
| "The project has no `evals/`, I'll point ai-dev at `src/**`" | Now two devs share a writable path. Drop the glob instead |
| "The agent got blocked, I'll widen its domain" | Fail-closed is the design working. Fix the glob to the real path, never to `**` |
| "I'll copy the new team-config over theirs" | Their `domain` globs are real and the template's are placeholders. Merge by hand |
| "They can run a team now" | If agent definitions were installed or updated this session, restart first: definitions are not live-reloaded. Definitions installed before session start are spawnable now |
