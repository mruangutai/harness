# Receipt — harness-dev-ops — T-11

**BLUF:** Added `"fable-advisor"` as the fifth entry of `SPAWNS["harness-validator-lead"]`
in `.claude/skills/harness/bin/sync-agent-adapters.py` (line ~68), preserving the four
existing entries and their order, with a comment stating the constant is inert today
(read only by `bootstrap_one()`, unreachable while `bootstrap()` refuses to overwrite
existing `.omp/agents/harness-*.md`) and exists only so it cannot silently disagree with
the shipped `spawns:` allowlist. No other file touched.

## Non-goals honored
- Did not touch `.omp/agents/harness-validator-lead.md` (T-06's file, already correct).
- Did not touch `bootstrap_one()`'s `tools` handling or `COLORS`.
- Did not add a `fable-advisor.md` definition file to the repo.

## Invariant check
`bootstrap_one()` requires the `task` tool whenever a spawns list is non-empty. Read
`.omp/agents/harness-validator-lead.md` frontmatter directly: `tools:` includes `task`.
Invariant holds; not assumed.

## Verify — run verbatim from worktree root, exit 0
```
python3 .claude/skills/harness/bin/sync-agent-adapters.py --check \
  && python3 .claude/skills/harness/bin/test-sync-agent-adapters.py \
  && python3 - <<'EOF'
import importlib.util, yaml
p = '.claude/skills/harness/bin/sync-agent-adapters.py'
s = importlib.util.spec_from_file_location('sync_probe', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)
mapped = m.SPAWNS['harness-validator-lead']
assert 'fable-advisor' in mapped, mapped
t = open('.omp/agents/harness-validator-lead.md', encoding='utf-8').read()
shipped = yaml.safe_load(t.split('---', 2)[1])['spawns']
assert 'fable-advisor' in shipped, shipped
assert sorted(shipped) == sorted(mapped), (shipped, mapped)
print('OK')
EOF
```
Output: `--check` passed silently (0), `test-sync-agent-adapters.py` reported
`18/18 cases passed`, probe printed `OK`. Combined exit status 0.

## Final list (in order)
`SPAWNS["harness-validator-lead"]` = `["harness-qa", "harness-code-reviewer",
"harness-security-reviewer", "harness-ui-reviewer", "fable-advisor"]` — matches shipped
frontmatter `spawns:` exactly (`sorted(shipped) == sorted(mapped)` held).

## git status note
`.harness/.../plan.yaml` also shows modified (`status: pending` → `building`), but that
change predates this dispatch and was not made by me — confirmed via `git diff`, the only
hunk is the status flip already noted as pre-set in the task contract. Tree left
uncommitted per instructions.
