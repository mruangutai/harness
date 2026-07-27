---
name: harness-init
description: Onboard a project to the harness — interview the user, write .harness/, and install the three platform prerequisites. Use when a project has no .harness/, when check-state.sh reports "not onboarded", or when a schema_version gap calls for --upgrade.
---

# Harness: Init

The onboarding interview, run **inside a target project**. `/harness-deploy` distributes the tool and
**never touches project state**; this writes every project artifact, once. **Enroll = deploy + init.**

**Run this in the main session.** Only the main session can call `AskUserQuestion` — a subagent has no
channel to the user. Delegate the *mechanical detection* to `dev-ops`; never delegate the interview.

## Preflight — stop if any of these fails

```bash
test -d .claude/skills/harness/templates && echo "templates ok" || echo "NO TEMPLATES"
claude --version
git rev-parse --show-toplevel 2>/dev/null || echo "NOT A GIT REPO"
```

- **No templates** → `/harness-deploy` has not run here. Stop and say so; there is nothing to instantiate.
- **CLI < 2.1.217** → below the floor for the spawn env vars. Stop; the depth setting will not take.
- **Not a git repo** → warn but continue. Commit attribution and `review_sha` pinning will not work.
- **`.harness/` already exists** → this project is initialised. Route to `--upgrade`, do not re-run fresh.

You will need permission to run the scripts in `.claude/skills/harness/bin/` and to write
`.claude/settings.json`, which many setups gate as a sensitive file. Ask for it up front rather than
discovering it at step 1 — a denial there is a **stop**, not a detour (see below).

## Fresh init

### 1. Install the three prerequisites — HARD GATE, do this first

```bash
.claude/skills/harness/bin/merge-settings.py . \
  --template .claude/skills/harness/templates/settings.snippet.json
.claude/skills/harness/bin/merge-gitignore.sh .
.claude/skills/harness/bin/merge-settings.py . --check   # must exit 0 before step 2
```

**Use the scripts. Do not hand-edit `.claude/settings.json`, and do not hand-replicate a script that
was denied.** All three entries degrade *silently* — no error, no warning — and a project that already
has its own hooks is exactly where one of the three goes missing during a hand-merge. Both scripts
preserve what is there and are safe to re-run.

**If either script cannot run, STOP HERE and tell the user what to approve.** Do not proceed to step 2.
This has already gone wrong once in testing: with the scripts denied, an init hand-wrote the `.gitignore`
half, silently skipped the settings half, and carried on through step 5 — producing a project with a
manifest, a scaffolded `.harness/`, and **no domain enforcement whatsoever**. Everything downstream looks
finished, which is precisely why a half-installed init is worse than a refused one.

The hooks take effect **immediately, in this session** — verified: a subagent spawned after this merge
had its out-of-domain write blocked by the freshly-registered hook. So steps 4 and 8 below run *with*
enforcement on, and nothing here waits on a restart.

### 2. Scaffold `.harness/` from the templates

```bash
mkdir -p .harness/expertise
cp .claude/skills/harness/templates/harness.json    .harness/harness.json
cp .claude/skills/harness/templates/team-config.yaml .harness/team-config.yaml
```

Delete the `_template` key from `.harness/harness.json` — it is a template marker, not project state.

The globs in the manifest are still placeholders at this point, and that is fine: `dev-ops` writes
only `.harness/harness.json`, which the template already grants it. **The manifest must exist before
any agent is spawned** — with no manifest `check-domain.sh` fails open and enforcement is simply off.

`PLAN.md`, `STATE.md` and `DESIGN.md` are **not** written here. A plan is written when there is
something to plan, and their owners instantiate them from the same templates.

### 3. Interview — technical

One batched `AskUserQuestion` call:

- **Project type** — web app · API/service · CLI · library · data pipeline
- **Frontend framework** (if any) and **backend framework/language**
- **Does this project have a user-facing UI?** — decides whether step 7 runs at all

### 4. Delegate detection to `dev-ops`

Spawn `harness-dev-ops` with the answers from step 3. It must:

- Determine the real test runner **for each kind** and write `test_kinds` into `.harness/harness.json`.
- **Verify every `cmd` by running it.** A command that resolves but is misconfigured is worse than one
  that is absent — `node --test src/` reports `tests 1 / fail 1` for a module-load error, which reads
  exactly like a failing suite.
- **Never invent a plausible command.** A kind with no runner keeps `cmd: null`, and its placeholder
  `_reason` is **replaced with the real one** ("no Playwright in this project", "no eval harness yet").
  `qa` treats null as a not-applicable soft skip; an invented command turns a hard gate into a silent
  no-op, which is strictly worse than no gate. A worked example from testing: this project's
  `package.json` declared `"test": "echo \"1 passing\""` — dev-ops ran it, saw it was a stub, and
  correctly refused to write it as `unit.cmd`.
- **Delete the `_reason` on any kind whose `cmd` it fills.** Every kind ships with
  `_reason: "unset — dev-ops has not run detection yet"`. Leaving that next to a command dev-ops has
  since verified states a falsehood about the project's own config.
- Keep worktree and vendor dirs in every `exclude`, or a diff scan multiplies each test file by the
  number of checkouts (measured 3× in kaya-ai).
- **Report the source layout** in its DIGEST — frontend root, backend root, prompt/agent dir, migrations
  dir, test root, docs root — for the next step. It does not write the manifest itself.
- Check the team conventions: is `@astryxdesign/core` present, is Supabase linked? Report, do not
  silently install.

### 5. Seed the manifest

Replace every glob marked `# SEED` in `.harness/team-config.yaml` with the real path from dev-ops's
report. **You** write this file — it is not in any agent's domain.

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

### 6. Interview — product, then the BRIEF

Second `AskUserQuestion` round: the goal, requirements, constraints, and what "done" looks like from
outside the code. Then write `.harness/BRIEF.md` from the template.

Follow the `harness-brief` skill's discipline: apply the **REQ test** (a requirement survives changing
your mind about implementation), and give **every `SC-NN` a `verify:`** — `automated` (plus an
`evidence:` kind that exists in `test_kinds`), `inspection`, or `uat`. An SC with no method is not
verifiable and blocks the goal-check later.

### 7. The approval gate — ask, then write

Summarise the brief in plain English: the goal as you understood it, how many REQs and SCs, how each
SC will be checked, and **which ones will need the user personally** (the `uat` ones). Then ask with
`AskUserQuestion`: approve, or amend?

**On an explicit yes, write `## Approval` yourself** — `status: approved`, their name, today's date.
This is not self-approval and it is not a shortcut:

- `## Approval` is **orchestrator-written by design** (SPEC §2.3). pm never touches it because pm has
  no user channel; init runs at the orchestrator tier and does.
- Until it says `approved`, `check-state.sh` reports `BRIEF.md is NOT approved — halt` and **nothing
  downstream may run.** An init that leaves a pending brief has not finished onboarding the project.

**If the user amends or defers, leave it pending** — and tell them plainly that the harness is blocked
until they approve, and that `/harness` will keep saying so. A pending brief is a correct state; a
brief you approved on their behalf is not.

### 8. Design pass — UI projects only

If step 3 said there is a UI, offer it: `harness-visual-designer` establishes `.harness/DESIGN.md`
(palette in **both** themes, type scale, spacing, component direction), then `harness-ui-reviewer` in
**mode A** judges whether that contract is sound before anything is built against it.

Skip it entirely for a project with no user-facing surface. An empty `DESIGN.md` is worse than none —
it reads as though the decisions were made.

### 9. Verify, then warn about the restart

```bash
.claude/skills/harness/bin/check-state.sh
.claude/skills/harness/bin/merge-settings.py . --check
```

`check-state.sh` must exit 0. It will not if the brief is pending (step 7) or the settings merge was
skipped — both are real failures, not noise to talk past.

Then say this, explicitly, as the last thing — **but only if `/harness-deploy` installed or updated
agent definitions during this same session:**

> **Restart Claude Code before running a crew.** Agent definitions are not live-reloaded (DEC-100a), so
> agents installed in this session are not spawnable yet. Without a restart the first crew fails with
> "Agent type not found" and no explanation.

**Do not overstate this.** The hooks written in step 1 *are* live immediately — verified — and agents
that deploy installed before this session started are spawnable now, which is why steps 4 and 8 work.
The restart is about **newly written agent files**, nothing else. Telling a user their harness is inert
when it is not is its own kind of wrong.

## `--upgrade`

For a project that is already initialised, after a newer harness has been deployed.

```bash
.claude/skills/harness/bin/upgrade-config.py .
.claude/skills/harness/bin/merge-settings.py . \
  --template .claude/skills/harness/templates/settings.snippet.json
.claude/skills/harness/bin/merge-gitignore.sh .
```

- `harness.json` is **merged** — new template entries added, every project value kept. `test_kinds.*.cmd`
  above all: dev-ops verified those by running them, and re-imposing the template's `null` would turn a
  working gate back into a soft skip.
- `team-config.yaml` is **reported, never rewritten.** These scripts carry no YAML library by design, and
  putting the manifest's `domain` globs behind a line-based regex writer is not a trade worth making.
  `upgrade-config.py` prints the exact new entries and **exits 1** — relay them and add them by hand.
- **`BRIEF.md`, `PLAN.md` and `DESIGN.md` are never touched by an upgrade.** They are the project's
  content, not its schema.

## Red flags

| Thought | Reality |
|---|---|
| "I'll just add the hook to settings.json myself" | That is how one of the three goes missing. Run the script; it preserves the project's own hooks |
| "The script was denied, I'll replicate what it does" | Stop instead. A half-installed init looks finished and has no domain enforcement — observed in testing |
| "dev-ops filled the cmd, the `_reason` is harmless" | It says "unset — dev-ops has not run detection yet" next to a working command. Delete it |
| "They must restart before anything works" | The hooks are live now. Only newly-written agent files need the restart |
| "The project has no `evals/`, I'll point ai-dev at `src/**`" | Now two devs share a writable path. Drop the glob instead |
| "`npm test` is the obvious command here" | Run it. An unverified `cmd` turns a hard gate into a silent no-op |
| "The agent got blocked, I'll widen its domain" | Fail-closed is the design working. Fix the glob to the real path, never to `**` |
| "They described the goal to me, so it's approved" | Describing is not approving. Ask, then write what they answered |
| "check-state says pending — close enough" | Nothing downstream may run against an unapproved brief. Onboarding is not done |
| "I'll copy the new team-config over theirs" | Their `domain` globs are real and the template's are placeholders. Merge by hand |
| "They can run a crew now" | Not until they restart. Agent definitions are not live-reloaded |
