# Distributed templates

Canonical schemas, pushed to every project by `/harness-deploy` and instantiated by
`/harness-init`. **Deploy copies these files; it never writes project state.** That split is
what lets deploy be dumb and safe.

| Template | Instantiated to | By | When |
|---|---|---|---|
| `settings.snippet.json` | `.claude/settings.json` | `/harness-init` via `bin/merge-settings.py` | init — **merged**, never clobbered |
| `harness.json` | `.harness/harness.json` | `/harness-init`, then `dev-ops` fills `test_kinds.cmd` | init |
| `team-config.yaml` | `.harness/team-config.yaml` | `/harness-init`, seeding `# SEED` globs from detection | init |
| `BRIEF.md` | `.harness/features/<FEAT>/BRIEF.md` | `/harness-init` drafts; `harness-pm` owns thereafter | init |
| `gitignore.snippet` | `.gitignore` | `/harness-init` via `bin/merge-gitignore.sh` | init — **appended**, never overwritten |
| `PLAN.md` | `.harness/features/<FEAT>/PLAN.md` | `harness-pm` | first planning pass, not init |
| `STATE.md` | `.harness/features/<FEAT>/STATE.md` — **one per flow**, never a project-level file (DEC-120) | that feature's orchestrator | first run of that feature, not init |
| `codebase-INDEX.md` | `.harness/codebase/INDEX.md` | `documentor`, via the understand-codebase playbook | first map run, not init |
| `DESIGN.md` | `.harness/features/<FEAT>/DESIGN.md` | `harness-visual-designer` | init's optional design pass, for UI projects only |

**Everything directly in this directory is a template.** Anything that is not one lives in
`examples/` — currently `harness.kaya-ai.json`, the filled pilot config for `kaya-ai`, kept as a worked
example of what detection output looks like. Deploy copies `templates/` wholesale, so a non-template
sitting at this level would ship to every enrolled project as though it were one.

## Two conventions that carry the weight

**`# SEED`** — replaced from detection by `/harness-init`; an unseeded glob **fails closed**
(the full rule lives in team-config.yaml's header — never widen a domain to `**` to "fix" a block).

**`"cmd": null` plus a `_reason`** — an absent test runner, a not-applicable soft skip in the qa
gate. dev-ops fills it only with a command it has actually run (harness-init step 4 has the why).

## Versioning

Every template carries `schema_version`. Deploy pushes a newer template but **leaves the project's
instantiated file alone**; `bin/check-state.sh` reports the gap and the user runs
`/harness-init --upgrade`, which merges new entries while preserving per-project values —
`domain` globs and `test_kinds.*.cmd` above all. Those are never clobbered.
