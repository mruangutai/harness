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
- **Run records checklist (BUG-2399): the ignore merge in an existing checkout.** Harness
  once shipped a broad `runs/**` ignore. Run records other than `runs/*/ui/` are retained
  evidence (DEC-238) and are tracked now, so `merge-gitignore.py` replaces that rule with
  `.harness/*/features/*/runs/*/ui/**`. Any historical evidence it was hiding becomes
  untracked the moment the rule narrows, and both `merge-gate.py merge-distill` and
  `feature-worktree.py remove` refuse a tree carrying it. The operator runs this once per
  checkout:
  1. Pause teams, distill and worktree removal in this checkout. Commit, or set aside, any
     staged or unrelated edits first (`git status` is clean), so the review below sees only
     the migration.
  2. Before narrowing, see what the old rule hides. Both layouts appear, namespaced
     (`.harness/<segment>/features/<id>/runs/<run>/`) and legacy (`.harness/features/<id>/runs/<run>/`):

     ```bash
     git ls-files --others --ignored --exclude-standard -z -- .harness | tr '\0' '\n'
     ```

  3. Narrow the rule:

     ```bash
     <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/merge-gitignore.py .
     ```

  4. Review `git diff -- .gitignore` and `git status --untracked-files=all`. The exposed
     run files are the evidence. Run UI and `*.lock` files stay ignored. If a project ignore
     still hides a reviewed record, resolve that with the project owner; do not force-add it.
  5. Stage `.gitignore` and the reviewed non-UI run files by explicit path. Use literal
     pathspecs, so names with spaces or glob characters stage exactly. Never use `git add -A`
     or `-f`, and never delete evidence:

     ```bash
     git --literal-pathspecs add -- .gitignore '<reviewed run path>' ...
     git diff --cached --name-only
     ```

  6. Confirm that the staged list is exactly `.gitignore` plus the reviewed records, then
     commit it as its own commit (`git commit -m "harness: track run records (BUG-2399)"`).
     With no historical evidence, stage `.gitignore` alone. Resume teams only after that commit.

  From then on, nothing is ever force-added. The orchestrator's feature-directory commit
  carries each run's records. A distill run's records are committed and pushed before
  `merge-distill`, and an aborted run's untracked records refuse removal rather than vanish.
- **Re-run the checklist above for an existing checkout that pulls a snippet change** (the
  PyYAML `.pyyaml-bootstrap` entry, or the BUG-2399 run-UI rule). `merge-gitignore.py --check`
  reads its rule list from the snippet and reports obsolete Harness rules, so the check
  correctly goes red on already-initialised projects until the merge is re-run. The merge is
  idempotent and preserves the project's own ignore rules.
- **Never touch `BRIEF.md`, `PLAN.md` or `DESIGN.md` in an upgrade**: they are the project's
  content, not its schema. First BRIEF, approval and design work route to `/harness-plan`.
