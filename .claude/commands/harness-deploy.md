<purpose>
Deploy harness skills and agents from the harness repo to global locations and all registered projects, or enroll an existing project for the first time.

Must be run from the harness repo. What you deploy is the current working copy — skills from `.claude/skills/harness/` and agents from `.claude/agents/harness-*.md`.
</purpose>

<usage>
/harness-deploy             — push updated skills to all registered projects
/harness-deploy <path>      — enroll an existing project for the first time
</usage>

<process>

<step name="validate">
Confirm running from the harness repo:

```bash
ls .claude/skills/harness/SKILL.md 2>/dev/null && echo "ok" || echo "not harness repo"
```

If not found: "harness-deploy must be run from the harness repo." Stop.
</step>

<step name="update-global">
Copy harness skills to the global distribution point:

```bash
mkdir -p ~/.claude/skills/harness
cp -r .claude/skills/harness/. ~/.claude/skills/harness/
```

Write `~/.claude/skills/harness/manifest.json` from the current `agent_skills` block in `.planning/config.json`:

Read `.planning/config.json`, extract the `agent_skills` object, write it as:
```json
{
  "agent_skills": { ... }
}
```

to `~/.claude/skills/harness/manifest.json`.

Copy harness agents to the global agents directory:

```bash
cp .claude/agents/harness-*.md ~/.claude/agents/
```

Agents are global — they are not pushed per-project.
</step>

<step name="route">
Check for a path argument.

- No argument → **push mode**
- Path provided → **enroll mode**
</step>

<step name="push-mode">
**Push mode — update all registered projects**

Read `~/.gsd/harness-registry.json`.

If the file is missing or `projects` array is empty:
```
No registered projects. Use /harness-deploy <path> to enroll a project first.
```
Stop.

For each project path in the registry:

```bash
test -f "{path}/.planning/config.json" && echo "exists" || echo "missing"
```

If exists:
```bash
cp -r ~/.claude/skills/harness/. "{path}/.claude/skills/harness/"
```
Report: `✓ {path}`

If missing:
Report: `✗ {path} — project not found (remove from registry?)`

Final summary:
```
Deployed to {N}/{total} projects.
```
</step>

<step name="enroll-mode">
**Enroll mode — first-time setup for an existing project**

Resolve the provided path to an absolute path.

Verify the project is a GSD project:
```bash
test -f "{absolute-path}/.planning/config.json" && echo "ok" || echo "not a gsd project"
```

If not a GSD project: "No `.planning/config.json` found at {path}. Initialize GSD first with /gsd-new-project." Stop.

Copy skills to the project:
```bash
mkdir -p "{absolute-path}/.claude/skills/harness"
cp -r ~/.claude/skills/harness/. "{absolute-path}/.claude/skills/harness/"
```

Merge agent_skills into the project's config.json:
- Read `{absolute-path}/.planning/config.json`
- Read `~/.claude/skills/harness/manifest.json` for the entries to add
- Merge: if `agent_skills` key already exists, add only the missing entries (do not overwrite existing entries for other agent types)
- If `agent_skills` key is absent, add it with the full manifest entries
- Write the updated config.json back

Register the project:
- Read `~/.gsd/harness-registry.json` (create as `{"projects":[]}` if missing)
- If the absolute path is not already in the `projects` array, append it
- Write back

Report:
```
✓ Harness enrolled in {absolute-path}
  — skills copied to .claude/skills/harness/
  — agent_skills added to .planning/config.json
  — registered in ~/.gsd/harness-registry.json
```
</step>

</process>

<success_criteria>
- [ ] Global `~/.claude/skills/harness/` matches harness repo's `.claude/skills/harness/`
- [ ] `~/.claude/skills/harness/manifest.json` reflects current `agent_skills` from config.json
- [ ] Global `~/.claude/agents/harness-*.md` matches harness repo's `.claude/agents/harness-*.md`
- [ ] Push mode: all reachable registered projects have updated skills
- [ ] Enroll mode: project has skills, config.json agent_skills entries, and is in registry
</success_criteria>
