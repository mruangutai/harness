# Checkout upgrade

The main session MUST read this procedure before `/harness-init --upgrade` (DEC-158/222).
Run it in an already-initialised Harness checkout after a newer Harness has been deployed;
for a fleet member, run it in that member's checkout and land its merged `harness.json` on
its default branch through `harness-add-repo`. This is operator-run, not a deploy side effect.

Run both commands in the target checkout:

```bash
<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/upgrade-config.py .
<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/merge-gitignore.py .
```

- `harness.json` is **merged**: new template entries are added and every project value is kept.
  Preserve `test_kinds.*.cmd` above all: dev-ops verified those by running them; re-imposing
  the template's `null` would turn a working active gate into `BLOCKED`, not a soft skip
  (DEC-187).
- `team-config.yaml` is **reported, never rewritten**. It belongs only to the control plane;
  a product repository has none to report. Reading uses a real parser (DEC-171), but
  `safe_dump` does not preserve the comments justifying every `domain` glob: round-tripping
  would delete the reasoning behind the only write-scope guarantee. `upgrade-config.py`
  prints the exact new entries and **exits 1**; the main session MUST relay them and add
  them by hand, preserving the existing globs and their comments.
- **Re-run `merge-gitignore.py .` for an existing checkout that pulls the PyYAML change**
  (the second command above). The snippet gained the `.pyyaml-bootstrap` ignore entry, and
  `merge-gitignore.py --check` reads its rule list from that snippet, so the check correctly
  goes red on already-initialised projects until the merge is re-run. The merge is idempotent
  and preserves the project's own ignore rules. Skipping it leaves the write hooks' bootstrap
  marker untracked, dirtying the tree; a dirty tree halts the next team with `BLOCKED` on
  Harness's own artifact.
- **Never touch `BRIEF.md`, `PLAN.md` or `DESIGN.md` in an upgrade**: they are the project's
  content, not its schema. First BRIEF, approval and design work route to `/harness-plan`.
