# Checkout upgrade

The main session MUST read this procedure before `/harness-init --upgrade` (DEC-158/222).
Run it in an already-initialised Harness checkout after a newer Harness has been deployed;
for a fleet member, run it in that member's checkout and land its merged `harness.json` on
its default branch through `harness-add-repo`. This is operator-run, not a deploy side effect.

Run the config upgrade in the target checkout:

```bash
<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/upgrade-config.py .
```

Then merge the ignore rules through the run-records checklist below. Never run
`merge-gitignore.py` on its own in an existing checkout.

A fleet member's product checkout carries neither the templates nor a `team-config.yaml`, so
replace the first command there with:

```bash
<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/upgrade-config.py . --config-only \
  --templates <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/templates
```

Version 3 is a breaking upgrade (DEC-256): until a member's upgraded `harness.json` lands on
its default branch, every Harness reader refuses that member.

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
- **Working files checklist (DEC-260): the ignore merge in an existing checkout.** Each
  feature's `notes/`, `runs/` and `observations/` and the project `.harness/notes/` are local
  working files, never committed. The operator runs this once per checkout:
  1. Pause teams, distill and worktree removal in this checkout.
  2. Run the merge:

     ```bash
     <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/merge-gitignore.py .
     ```

  3. Review `git diff -- .gitignore`.
  4. Untrack the working files:

     ```bash
     git rm -r --cached --sparse --ignore-unmatch -- \
       ':(glob).harness/*/features/*/notes/**' ':(glob).harness/*/features/*/runs/**' \
       ':(glob).harness/*/features/*/observations/**' ':(glob).harness/notes/**'
     ```

  5. Commit `.gitignore` and the untracking as their own commit. History is not rewritten and
     the files stay on disk.

  An in-flight branch that still tracks its own working files turns
  `tests/unit/test-working-files-untracked.py` red once it merges main; its repair is the same
  `git rm -r --cached --sparse` command run on that branch and committed alone (DEC-260).
- **Re-run the checklist above for an existing checkout that pulls a snippet change** (the
  PyYAML `.pyyaml-bootstrap` entry, or the DEC-260 working-file rules). `merge-gitignore.py --check`
  reads its rule list from the snippet and reports obsolete Harness rules, so the check
  correctly goes red on already-initialised projects until the merge is re-run. The merge is
  idempotent and preserves the project's own ignore rules.
- **Never touch `BRIEF.md`, `PLAN.md` or `DESIGN.md` in an upgrade**: they are the project's
  content, not its schema. First BRIEF, approval and design work route to `/harness-plan`.
