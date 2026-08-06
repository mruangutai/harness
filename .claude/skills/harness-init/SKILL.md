---
name: harness-init
description: Onboard a project to the harness — interview the user, write .harness/, and install the eight platform prerequisites. Use when a project has no .harness/, when check-state.sh reports "not onboarded", or when a schema_version gap calls for --upgrade.
---

# Harness: Init

The onboarding interview, run **inside a target project**. `/harness-deploy` distributes the tool and
**never touches project state**; this writes every project artifact, once. **Enroll = deploy + init.**

**Run this in the main session.** Only the main session can call `AskUserQuestion` — a subagent has no
channel to the user. Delegate the *mechanical detection* to `dev-ops`; never delegate the interview.

**The interview IS a grilling (DEC-164).** Load `harness-grilling` and run it: one question at a
time with your recommendation, facts looked up rather than asked, destination named first, and the
artifact written to `.harness/notes/`. Its answers seed `harness.json`, the domain description, and
the first `glossary.md` terms.

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

### 1. Install the eight prerequisites — HARD GATE, do this first

```bash
.claude/skills/harness/bin/merge-settings.py . \
  --template .claude/skills/harness/templates/settings.snippet.json
.claude/skills/harness/bin/merge-gitignore.sh .
.claude/skills/harness/bin/merge-settings.py . --check   # must exit 0 before step 2
python3 -c 'import yaml' 2>/dev/null && echo OK || echo MISSING   # the 7th prerequisite
```

**If that last line prints `MISSING`, STOP.** PyYAML is REQUIRED, not optional (DEC-171 am.1): there
is no line-scan fallback anywhere in `bin/`, deliberately, because a fallback leaves the hand-rolled
parser it exists to remove. Print this for the user to run, then re-check:

```
python3 -m pip install pyyaml
# if that fails with "externally-managed-environment" (PEP 668, e.g. Homebrew/Debian):
python3 -m pip install --user --break-system-packages pyyaml
```

That is the content of `harness_yaml.INSTALL_COMMAND`. **Quote it from there rather than
re-typing it** — D-07 makes the module the single source of truth, and two hand-maintained copies of
an install command is exactly the divergence class this prerequisite exists to prevent.

**This check is the LOUD EARLY warning; `check-domain.sh` is the AUTHORITATIVE one.** It runs in the
user's interactive shell, whose `PATH` is not proven identical to a hook subprocess's — so the write
hooks additionally self-report `MISSING` from inside their own environment on first invocation, which
is the same code path the one-session bootstrap escape already needs. Treat a green check here as
"probably fine", never as proof.

**Use the scripts. Do not hand-edit `.claude/settings.json`, and do not hand-replicate a script that
was denied.** All eight entries degrade *silently* — no error, no warning — and a project that already
has its own hooks is exactly where one of the eight goes missing during a hand-merge. Both scripts
preserve what is there and are safe to re-run.

**If either script cannot run, STOP HERE and tell the user what to approve.** Do not proceed to
step 2 — a half-installed init looks finished but has no domain enforcement, which is worse than a
refused one (observed in testing).

The hooks are live **immediately, in this session** — steps 4 and 8 below run *with* enforcement
on; nothing here waits on a restart (step 9 has the one real restart caveat).

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
  no-op, which is strictly worse than no gate.
- **Surface every remaining `cmd: null` to the user as a DECISION, not a footnote (DEC-163).**
  Cross-reference each against what the project actually has: a null `ui` runner in a project with
  a real UI, a null `eval` with real LLM code, a null `integration` with a real database. For each,
  `AskUserQuestion`: stand the runner up now (a dev-ops task), or accept the gap knowing SCs can
  never rest on that kind. Record the answer; an accepted gap belongs in the backlog. A null kind
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
outside the code. Then write `.harness/features/<FEAT>/BRIEF.md` from the template.

Follow the `harness-brief` skill's discipline: apply the **REQ test** (a requirement survives changing
your mind about implementation), and give **every `SC-NN` a `verify:`** — `automated` (plus an
`evidence:` kind that exists in `test_kinds`), `inspection`, or `uat`. An SC with no method is not
verifiable and blocks the goal-check later.

### 7. The approval gate — ask, then write

Summarise the brief in plain English: the goal as you understood it, how many REQs and SCs, how each
SC will be checked, and **which ones will need the user personally** (the `uat` ones). Then ask with
`AskUserQuestion`: approve, or amend?

**On an explicit yes, write `## Approval` yourself** — `status: approved`, their name, today's
date. Not self-approval: init runs at the tier with the user channel (SPEC §2.3), and until it says
`approved`, `check-state.sh` halts everything downstream. An init that leaves a pending brief has
not finished onboarding.

**If the user amends or defers, leave it pending** — and tell them plainly that the harness is blocked
until they approve, and that `/harness` will keep saying so. A pending brief is a correct state; a
brief you approved on their behalf is not.

### Map the codebase — runs AS PART OF INIT, not as a remembered follow-up (DEC-140)

If the project has **existing source code**, the last act of init is spawning
`harness-orchestrator` with **mission map** (DEC-137) — the org's structural knowledge is built
before the first feature ever plans, so nothing downstream runs unmapped.

- **Existing code** (dev-ops detection found source beyond scaffolding) → spawn mission map now,
  in the background; tell the user it is running and that `codebase/map.html` lands when done.
- **Greenfield** (no meaningful source) → skip, and say so — the map builds naturally as ships
  refresh it. INV-14 will start nagging the moment real code exists without a map.

### GitHub Issues mirror — ask ONCE, here, so it is never forgotten (DEC-138)

Ask the user: **"Mirror features to GitHub Issues? (feature → milestone, tasks → issues, one-way
outbound after your plan approval)"**

- **Yes** → run `gh repo view --json nameWithOwner -q .nameWithOwner` in the project, show the
  result, and get explicit confirmation — **the repo is pinned under the user's eyes, never
  inferred later** (a fork or renamed remote would publish to the wrong org silently). Write
  `"github": { "sync": true, "repo": "<owner/name>" }` into `.harness/harness.json`.
- **No** → write `"github": { "sync": false, "repo": null }` — an explicit off, not an absence.
  INV-13 treats a missing block as "never asked" and nags; an explicit false is a decision.

### 8. Design pass — UI projects only

If step 3 said there is a UI, offer it: `harness-visual-designer` establishes `.harness/features/<FEAT>/DESIGN.md`
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

> **Restart Claude Code before running a team.** Agent definitions are not live-reloaded (DEC-100a), so
> agents installed in this session are not spawnable yet. Without a restart the first team fails with
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
- `team-config.yaml` is **reported, never rewritten.** It is now READ with a real parser (DEC-171), but
  writing it stays refused for a reason a parser does not fix: `safe_dump` does not preserve comments,
  and the manifest is more comment than data — every `domain` glob is justified in prose beside it.
  Round-tripping it would silently delete the reasoning that makes the harness's only write-scope
  guarantee auditable. `upgrade-config.py` prints the exact new entries and **exits 1** — relay them and
  add them by hand.
- **An existing checkout that pulls the PyYAML change must re-run `merge-gitignore.sh .`** (it is in the
  block above). The snippet gained `.harness/.pyyaml-bootstrap`, and `merge-gitignore.sh --check` reads
  its rule list from that snippet — so `--check` correctly goes **red on every already-initialised
  project** until it is re-run. The script is idempotent and preserves the project's own rules. Skipping
  it means the write hooks' bootstrap marker lands untracked, dirtying the tree, and a dirty tree halts
  the next team run with `BLOCKED` on the harness's own artifact.
- **`BRIEF.md`, `PLAN.md` and `DESIGN.md` are never touched by an upgrade.** They are the project's
  content, not its schema.

## Red flags

| Thought | Reality |
|---|---|
| "I'll just add the hook to settings.json myself" | That is how one of the eight goes missing. Run the script; it preserves the project's own hooks |
| "The script was denied, I'll replicate what it does" | Stop instead. A half-installed init looks finished and has no domain enforcement — observed in testing |
| "dev-ops filled the cmd, the `_reason` is harmless" | It says "unset — dev-ops has not run detection yet" next to a working command. Delete it |
| "They must restart before anything works" | The hooks are live now. Only newly-written agent files need the restart |
| "The project has no `evals/`, I'll point ai-dev at `src/**`" | Now two devs share a writable path. Drop the glob instead |
| "`npm test` is the obvious command here" | Run it. An unverified `cmd` turns a hard gate into a silent no-op |
| "The agent got blocked, I'll widen its domain" | Fail-closed is the design working. Fix the glob to the real path, never to `**` |
| "They described the goal to me, so it's approved" | Describing is not approving. Ask, then write what they answered |
| "check-state says pending — close enough" | Nothing downstream may run against an unapproved brief. Onboarding is not done |
| "I'll copy the new team-config over theirs" | Their `domain` globs are real and the template's are placeholders. Merge by hand |
| "They can run a team now" | Not until they restart. Agent definitions are not live-reloaded |
