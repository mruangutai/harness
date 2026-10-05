---
name: harness-add-repo
description: Register a repository in an already-configured Harness control plane. Use when adding a repository to an existing fleet; do not use it to configure a Harness checkout.
---

# Harness: Add repository

Registering a repository is exactly three things, in order: land that repository's own
`.harness/harness.json` on its `default_branch`; register it in
`.harness/factory/fleet.yaml`; then create its central per-segment tree at
`<control-plane>/.harness/<segment>/`. The factory reads a fleet member's config remotely at its
default branch and has no disk fallback.

**One-file rule.** The only file registration puts in a product repository is its own
`.harness/harness.json`, and it counts only after it lands on that repository's default branch.
Nothing else is installed there: no `team-config.yaml`, expertise, `.harness/products/`, `bin/`,
hooks, or settings.

**Run this in the main session.** Only the main session can call `AskUserQuestion` — a subagent has no
channel to the user. Delegate the *mechanical detection* to `dev-ops`; never delegate the interview.

**The interview IS a grilling (DEC-164).** Before interviewing, MUST read and run
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-grilling/SKILL.md`.
Record its artifact in `.harness/notes/`; the answers seed the repository's own `harness.json`.

## Preflight — stop if any of these fails

- **Configured control plane** — `.harness/harness.json` must exist here and
  `python3 .agents/skills/harness/bin/check-state.py` must not report an unconfigured clone. If it
  is unconfigured, STOP and route to `harness-init`: registration into an unconfigured control
  plane produces artifacts nothing reads.
- **Templates** — `test -d .agents/skills/harness/templates` must succeed. If the templates directory
  is not readable from here, STOP: there is nothing to instantiate.
- **Checkout prerequisites** — this checkout has run
  `.agents/skills/harness/references/checkout-prereqs.md` (ignore rules, PyYAML, jsonschema,
  relative `core.hooksPath`); `check-state.py` INV-31 reports the hook when it has not. Run it first.
- **GitHub access** — `gh` must be installed and authenticated against the candidate repository. If it
  is absent or cannot authenticate, STOP: this procedure cannot land the required default-branch
  commit or read the mirror and board state.
- **Candidate branch and access** — know the candidate repository's default branch and confirm push
  access to it before proceeding.
- **Not already registered** — inspect `.harness/factory/fleet.yaml`. If the repository is already
  present, do not add a duplicate; run `--check-product-configs --repo <owner>/<repo>` and repair the
  existing member instead.

### 1. Land `harness.json`, then register the repository

This order is load-bearing: `product_config` has no disk fallback, so registering a member before its
config lands has no symptom except an unattributed `FleetError` mid-build.

1. Instantiate `.agents/skills/harness/templates/harness.json` into a checkout of the repository.
   Delete its `_template` key; fill `test_kinds` during the technical detection below and the GitHub
   block during the mirror question below.
2. Land `.harness/harness.json` on that repository's `default_branch`. Harness has no write route
   into a product repository: `factory_workspace.py` writes no artifact into a checkout and no agent
   domain covers a product's `.harness/`. The main session asks the operator for this commit; if they
   cannot push the protected branch or lack write access, open a PR against the default branch instead.
   Registration remains incomplete until that PR merges, because `product_config` reads the default
   branch and nothing else.

   Landing this file delegates control of what the factory reads for this member to whoever can push its
   default branch. Do not register the member unless that trust is intended.
3. Only then add the member to `<control-plane>/.harness/factory/fleet.yaml` as
   `- name: <owner>/<repo>` with `default_branch: <branch>`. Nothing else goes in that file:
   `load_fleet` rejects a board at any level, and `workspace_root` is fleet-wide.
4. Prove the config is reachable:

   ```bash
   python3 .agents/skills/harness/bin/factory_config.py --check-product-configs --repo <owner>/<repo>
   ```

   It must exit 0. Exit 2 names `<repo>@<ref>:.harness/harness.json` and the reason: the config has
   not landed or does not parse. Do not proceed on exit 2. A `--repo` success proves that member,
   not the whole fleet.
5. Create the central tree the factory reads:
   `<control-plane>/.harness/<segment>/features/` and
   `<control-plane>/.harness/<segment>/expertise/`, where `segment` is the portion of the name after
   the owner (`factory_config.segment_of`). This is where the repository's `BRIEF.md`, `plan.yaml`,
   and expertise live; `factory_config.features_root` resolves the first path. A feature's own
   directory under it is written in that feature's harness PLANNING worktree, never in the main
   checkout: `feature-worktree.py create --repo <owner>/<repo>` cuts it beside the repository's
   code worktree (#2056, `.omp/commands/harness.md` §0b).

### 2. Interview — technical

One batched `AskUserQuestion` call:

- **Project type** — web app · API/service · CLI · library · data pipeline
- **Frontend framework** (if any) and **backend framework/language**
- **Does this project have a user-facing UI?**

Spawn `harness-dev-ops` with the answers. Before detection, MUST read and follow
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-init/SKILL.md`
§ "4. Delegate detection to `dev-ops`" — the complete detection contract applies.
The only difference: dev-ops writes `test_kinds` into the fleet member's own `harness.json`
in its checkout under `workspace_root`; the main session lands that file through step 1,
rather than writing the control plane's own `harness.json`.

### 3. GitHub Issues mirror and project board

Ask the user: **"Mirror features to GitHub Issues? (feature → milestone, tasks → issues, one-way
outbound after your plan approval)"**

- **Yes** → run `gh repo view --json nameWithOwner -q .nameWithOwner` in the project, show the
  result, and get explicit confirmation — **the repo is pinned under the user's eyes, never
  inferred later** (a fork or renamed remote would publish to the wrong org silently). Write
  `"github": { "sync": true, "repo": "<owner/name>" }` into the repository's own
  `.harness/harness.json`; land it on its default branch through step 1.
- **No** → write `"github": { "sync": false, "repo": null }` into that same product config — an
  explicit off, not an absence. INV-13 treats a missing block as "never asked" and nags; an explicit
  false is a decision.

The project board follows the mirror question because it needs the repo pinned. Skip it entirely when
`github.sync` is false.

Before mirror-on provisioning or auditing, MUST read and follow
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/repo-board-provisioning.md`
(DEC-158).

**Provision only USER-OWNED boards**; organization-owned boards require manual creation
and configuration, not partial provisioning. **Record a newly created project's number in
the repository's `harness.json` `github.board.number` BEFORE retrying or doing any other work**,
including when a follow-up write failed: the project exists, and retrying without its number
creates a duplicate. Land the config through step 1.
**New-board options may be replaced only on a board created in that run; existing-board
changes are additive only**, so no existing card loses its column.
**Show audit WORKFLOW findings verbatim. Registration is incomplete until all three
workflows — `Item closed`, `Auto-close issue`, `Pull request merged` — audit as enabled.**
Only the operator's clicks in the project's web UI can enable them; no API can.

## Next: plan the first feature

The repository is registered. Its first BRIEF, that BRIEF's approval, and any design pass are
`/harness-plan` work: run `/harness-plan` against the registered repository.

## Red flags

| Thought | Reality |
|---|---|
| "dev-ops filled the cmd, the `_reason` is harmless" | It says "unset — dev-ops has not run detection yet" next to a working command. Delete it |
| "`npm test` is the obvious command here" | Run it. An unverified `cmd` turns a hard gate into a silent no-op |
| "The repo is in fleet.yaml, so the factory can serve it" | Not until its `harness.json` is on its default branch. `product_config` has no fallback; run `--check-product-configs` |
