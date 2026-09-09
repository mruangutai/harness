# Templates

Canonical schemas. `harness-init` instantiates control-plane templates; `harness-add-repo` lands
exactly one file in a product repository — that repository's own harness.json, on its default branch.

| Template | Instantiated to | By | When |
|---|---|---|---|
| `settings.snippet.json` | `<HARNESS_CONTROL_PLANE_ROOT>/.claude/settings.json` | `harness-init` via `bin/merge-settings.py` | init — **merged**, never clobbered |
| `harness.json` | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json` for the control plane; a fleet member's own copy on its default branch | `harness-init` for the control plane; `harness-add-repo` for a fleet member, then `dev-ops` fills `test_kinds.cmd` | configure or register |
| `team-config.yaml` | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/team-config.yaml` only; a product repository never carries one | `harness-init`, seeding `# SEED` globs from detection | configure |
| `BRIEF.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/BRIEF.md` | `/harness-plan` drafts; `harness-pm` owns thereafter | plan |
| `gitignore.snippet` | `.gitignore` | `harness-init` via `bin/merge-gitignore.sh` | init — **appended**, never overwritten |
| `plan.yaml` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/plan.yaml` | `harness-pm` | first planning pass, not init |
| `PLAN.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/PLAN.md` | `harness-pm` | **superseded by `plan.yaml` (DEC-182)** — never instantiated for a new feature; kept because features planned before DEC-182 keep their `PLAN.md` until they ship |
| `STATE.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/STATE.md` — **one per flow**, never a project-level file (DEC-120) | that feature's orchestrator | first run of that feature, not init |
| `DESIGN.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/DESIGN.md` | `harness-visual-designer` | `/harness-plan` for UI projects only |

**Everything directly in this directory is a template.** Anything that is not one lives in
`examples/` — currently `harness.kaya-ai.json`, the filled pilot config for `kaya-ai`, kept as a worked
example of what detection output looks like. Everything at this level is read as a template by
`harness-init` or `harness-add-repo` as applicable.

## Two conventions that carry the weight

**`# SEED`** — replaced from control-plane detection by `harness-init`; an unseeded glob **fails closed**
(the full rule lives in team-config.yaml's header — never widen a domain to `**` to "fix" a block).

**`"cmd": null` plus a `_reason`** — an absent test runner, a not-applicable soft skip in the qa
gate. dev-ops fills it only with a command it has actually run (the relevant onboarding skill has the why).

## Versioning

Every template carries `schema_version`. The template in this repository moves ahead while an
instantiated file stays where it is; `bin/check-state.sh` reports the gap and the operator runs
`/harness-init --upgrade` against the clone that holds it, which merges new entries while preserving
per-project values — `domain` globs and `test_kinds.*.cmd` above all. Those are never clobbered.
