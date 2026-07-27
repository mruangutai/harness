<purpose>
Distribute the harness — skills, agents and templates — to the global location and every enrolled
project, reconciling what is installed against what the repo actually contains.

**It never writes project state.** Not `.harness/`, not `.planning/`, not `settings.json`. That is
`/harness-init`'s job. **Enroll = deploy + init**, and this split is the whole reason deploy can be
dumb enough to run unattended.

Must be run from the harness repo. What ships is the current working copy.
</purpose>

<usage>
/harness-deploy             — push to global + all registered projects
/harness-deploy <path>      — enroll a project (copies the tool, then tells you to run /harness-init)
</usage>

<process>

<step name="plan">
The mechanical work lives in a script, because it deletes things and because a copy-only deploy is
exactly how three agents this design removed stayed spawnable for months, pointing at a `.planning/`
root that no longer exists.

**Dry run is the default. Always run it first and show the user the plan verbatim.**

```bash
.claude/skills/harness/bin/deploy.sh
```

For enroll mode, pass the path:

```bash
.claude/skills/harness/bin/deploy.sh --project "<path>"
```

If the script refuses (not the harness repo, empty ship set, no flat skill dirs), stop and relay why.
Each refusal guards against a push that would prune more than it installs.
</step>

<step name="confirm">
Read the plan back in plain English, and **name the destructive parts explicitly**:

- every line marked `-` is a **deletion** — an agent removed from the design, or a directory from an
  older layout. Re-running does not undo it.
- every line marked `!` needs a human decision. The two that matter:
  - **a registered project that no longer exists** — it will be dropped from the registry.
  - **a project whose `.planning/config.json` still has `agent_skills`** pointing at paths this push
    removes. That project's injection resolves to nothing afterwards. **Deploy will not fix it** —
    that is project state. Report it and let the user decide.

Then ask whether to apply. **Do not apply without a yes** — this reaches outside the repo, into the
user's global config and other repositories on their machine.
</step>

<step name="apply">
```bash
.claude/skills/harness/bin/deploy.sh --apply
```

What it does, in order: backs up `~/.claude/agents/` if anything will be pruned · replaces each skill
dir globally · prunes global skill dirs and agents absent from the repo · migrates
`~/.gsd/harness-registry.json` to `~/.harness/registry.json` (keeping the old file as `.migrated`) ·
pushes skill dirs to each live registered project and reconciles theirs.

**Check the exit code.** A non-zero exit means it stopped partway, and a half-applied deploy is the
worst state it can produce. Re-running is safe and completes it.
</step>

<step name="report">
```
✓ Deployed — {N} skill dirs, {A} agents global; {M} project(s)
  pruned: {list}
  registry: ~/.harness/registry.json
```

Close with the two things a user gets wrong otherwise:

- **Restart Claude Code.** Agent definitions are not live-reloaded (DEC-100a), so the agents this push
  installed are not spawnable until a restart. Skills and hooks do not need one.
- **A project with no `.harness/` still needs `/harness-init`.** Deploy gave it the tool; init makes it
  a harness project. Say which projects are in that state.
</step>

</process>

<design_notes>

**Agents are global only** (DEC-113). One copy in `~/.claude/agents/` is visible from every project, so
per-project copies buy nothing and cost drift — a project holding a stale shadow silently overrides the
fixed agent, and prune cannot see it. This deviates from SPEC §3.3's "global + enrolled projects"
wording, deliberately.

**Skill dirs are replaced wholesale**, because they are harness-owned end to end. This is why a
project's team overrides must **not** live in `.claude/skills/harness/teams/` — a push would delete
them. Overrides go in `.harness/teams/`, which deploy never touches, and the runner resolves
`.harness/teams/<name>.yaml` before `.claude/skills/harness/teams/<name>.yaml`.

**The flat skill dirs are siblings of `harness/`, not children.** `cp -r .claude/skills/harness/.`
copies the router, `bin/` and `templates/` and **none** of the seven rule skills or `harness-init`, so
every agent's `skills:` list resolves to nothing — silently, because a missing skill is not an error.
The script globs `.claude/skills/harness*/` and refuses to run if it finds only `harness/`.

**What was removed from the old version, and why:**

| Removed | Reason |
|---|---|
| `manifest.json` generation | `agent_skills` injection is gone. Rules are delivered by each agent's `skills:` frontmatter (DEC-63) |
| Merging `agent_skills` into a project's `config.json` | Writing project state. That belongs to `/harness-init` |
| The `.planning/config.json` "is this a GSD project?" gate | A project needs no GSD to receive the tool. Enroll then init |
| Requiring `/gsd-new-project` first | That dependency is gone |

</design_notes>

<success_criteria>
- [ ] Dry run was shown to the user and applied only after an explicit yes
- [ ] `~/.claude/skills/` holds every `harness*/` dir in the repo, and no others
- [ ] `~/.claude/agents/` holds exactly the repo's `harness-*.md`, and no others
- [ ] `~/.harness/registry.json` exists; the old `~/.gsd/` file is kept as `.migrated`
- [ ] **No project's `.harness/`, `.planning/` or `settings.json` was touched**
- [ ] Projects needing `/harness-init` were named in the report
</success_criteria>
