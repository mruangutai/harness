# Distributed templates

Canonical schemas, pushed to every project by `/harness-deploy` and instantiated by
`/harness-init`. **Deploy copies these files; it never writes project state.** That split is
what lets deploy be dumb and safe.

| Template | Instantiated to | By | When |
|---|---|---|---|
| `settings.snippet.json` | `.claude/settings.json` | `/harness-init` via `bin/merge-settings.py` | init — **merged**, never clobbered |
| `harness.json` | `.harness/harness.json` | `/harness-init`, then `dev-ops` fills `test_kinds.cmd` | init |
| `team-config.yaml` | `.harness/team-config.yaml` | `/harness-init`, seeding `# SEED` globs from detection | init |
| `BRIEF.md` | `.harness/BRIEF.md` | `/harness-init` drafts; `harness-pm` owns thereafter | init |
| `gitignore.snippet` | `.gitignore` | `/harness-init` via `bin/merge-gitignore.sh` | init — **appended**, never overwritten |
| `PLAN.md` | `.harness/PLAN.md` | `harness-pm` | first planning pass, not init |
| `STATE.md` | `.harness/features/<FEAT>/STATE.md` — **one per flow**, never a project-level file (DEC-120) | that feature's orchestrator | first run of that feature, not init |
| `DESIGN.md` | `.harness/DESIGN.md` | `harness-visual-designer` | init's optional design pass, for UI projects only |

**Everything directly in this directory is a template.** Anything that is not one lives in
`examples/` — currently `harness.kaya-ai.json`, the filled pilot config for `kaya-ai`, kept as a worked
example of what detection output looks like. Deploy copies `templates/` wholesale, so a non-template
sitting at this level would ship to every enrolled project as though it were one.

## Two conventions that carry the weight

**`# SEED`** marks a value that differs per project. `/harness-init` replaces it from detection.
An unseeded glob **fails closed** — the agent gets blocked with an actionable message naming its
permitted paths. That is the safe direction, and it is why widening a domain to `**` to "fix" a
block is never the answer.

**`"cmd": null` plus a `_reason`** is how an absent test runner is recorded. `dev-ops` replaces a
`null` only with a command it has actually **run**. Never write a plausible command you have not
executed: a `cmd` that resolves but is misconfigured reads exactly like a failing suite, and an
invented one turns a hard gate into a silent no-op — strictly worse than no gate at all. A `null`
`cmd` is a not-applicable soft skip in the qa gate.

## Versioning

Every template carries `schema_version`. Deploy pushes a newer template but **leaves the project's
instantiated file alone**; `bin/check-state.sh` reports the gap and the user runs
`/harness-init --upgrade`, which merges new entries while preserving per-project values —
`domain` globs and `test_kinds.*.cmd` above all. Those are never clobbered.
