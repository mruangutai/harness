# Templates

Canonical schemas. `harness-init` instantiates control-plane templates; `harness-add-repo` lands
exactly one file in a product repository — that repository's own harness.json, on its default branch.

| Template | Instantiated to | By | When |
|---|---|---|---|
| `harness.json` | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json` for the control plane; a fleet member's own copy on its default branch | `harness-init` for the control plane; `harness-add-repo` for a fleet member, then `dev-ops` fills `test_kinds.cmd` | configure or register |
| `team-config.yaml` | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/team-config.yaml` only; a product repository never carries one | `harness-init`, seeding `# SEED` globs from detection | configure |
| `BRIEF.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/BRIEF.md` | `/harness-plan` drafts; `harness-pm` owns thereafter | plan |
| `gitignore.snippet` | `.gitignore` | `harness-init` via `bin/merge-gitignore.py` | init — **appended**, never overwritten |
| `plan.yaml` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/plan.yaml` | `harness-pm` | first planning pass, not init |
| `PLAN.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/PLAN.md` | `harness-pm` | **superseded by `plan.yaml` (DEC-182)** — never instantiated for a new feature; kept because features planned before DEC-182 keep their `PLAN.md` until they ship |
| `STATE.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/STATE.md` — **one per flow**, never a project-level file (DEC-120) | that feature's orchestrator | first run of that feature, not init |
| `DESIGN.md` | `<HARNESS_FEATURE_TREE_ROOT>/.harness/<segment>/features/<FEAT>/DESIGN.md` | `harness-visual-designer` | `/harness-plan` for UI projects only |
| `MAP.md` | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/efforts/<slug>/MAP.md` in local mode; no Markdown shadow in tracker mode | main-session `harness-wayfinding` | multi-session discovery |
| `GRILLING.md` | `<HARNESS_CONTROL_PLANE_ROOT>/.harness/notes/grilling-<slug>-<date>.md` | main-session `harness-grilling` | before a user-confirmed hand-off |

Artifact templates load at their owning skill's named seam; they are not all instantiated at init.

## Two conventions that carry the weight

**`# SEED`** — replaced from control-plane detection by `harness-init`; an unseeded glob **fails closed**
(the full rule lives in team-config.yaml's header — never widen a domain to `**` to "fix" a block).

**`"cmd": null` plus a `_reason`** — an honest absent-runner record, not permission to skip.
Required unresolved/null runners are `BLOCKED`; only an explicit excluded kind with a resolving
signed decision soft-skips (DEC-187). dev-ops fills commands only after running them successfully.

## Versioning

Versioned control-plane templates (`harness.json`, `team-config.yaml`) carry `schema_version`.
`bin/check-state.py` reports a gap against an instantiated copy; `/harness-init --upgrade`
merges new entries while preserving project values, especially `domain` globs and verified
`test_kinds.*.cmd`. Artifact templates are not all versioned or upgraded by that procedure.
