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

**The interview IS a grilling (DEC-164).** Load `harness-grilling` and run it: one question at a
time with your recommendation, facts looked up rather than asked, destination named first, and the
artifact written to `.harness/notes/`. Its answers seed the repository's own `harness.json`.

## Preflight — stop if any of these fails

- **Configured control plane** — `.harness/harness.json` must exist here and
  `python3 .claude/skills/harness/bin/check-state.sh` must not report an unconfigured clone. If it
  is unconfigured, STOP and route to `harness-init`: registration into an unconfigured control
  plane produces artifacts nothing reads.
- **Templates** — `test -d .agents/skills/harness/templates` must succeed. If the templates directory
  is not readable from here, STOP: there is nothing to instantiate.
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

1. Instantiate `.claude/skills/harness/templates/harness.json` into a checkout of the repository.
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
   python3 .claude/skills/harness/bin/factory_config.py --check-product-configs --repo <owner>/<repo>
   ```

   It must exit 0. Exit 2 names `<repo>@<ref>:.harness/harness.json` and the reason: the config has
   not landed or does not parse. Do not proceed on exit 2. A `--repo` success proves that member,
   not the whole fleet.
5. Create the central tree the factory reads:
   `<control-plane>/.harness/<segment>/features/` and
   `<control-plane>/.harness/<segment>/expertise/`, where `segment` is the portion of the name after
   the owner (`factory_config.segment_of`). This is where the repository's `BRIEF.md`, `plan.yaml`,
   and expertise live; `factory_config.features_root` resolves the first path.

No `team-config.yaml` exists anywhere but the control plane; no `.harness/expertise/`,
`.harness/products/`, `bin/`, hooks, or settings are written in a product repository.

### 2. Interview — technical

One batched `AskUserQuestion` call:

- **Project type** — web app · API/service · CLI · library · data pipeline
- **Frontend framework** (if any) and **backend framework/language**
- **Does this project have a user-facing UI?**

Spawn `harness-dev-ops` with the answers. It follows the same dev-ops contract as harness-init's
“Delegate detection to dev-ops” section — verify every cmd, never invent
one, surface every null as a DECISION, keep worktree/vendor dirs excluded, report source layout —
with one difference: it writes test_kinds into the fleet member's own harness.json in its checkout
under workspace_root; the main session lands that file through step 1, rather than the control
plane's own harness.json.

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

- `python3 .agents/skills/harness/bin/board_lifecycle.py provision` — **read the exit code.**
  `0` provisioned or already correct. `2` the declaration is unusable and the message names the
  key — **nothing was written**. `3` a NEW project was created, linked, AND its Status field
  made to carry every declared station — one run, not two — and its number must be written
  into that project's `harness.json` `github.board.number` **before anything else runs**.
  `4` a project was created but a follow-up write FAILED — either the link, or the Status field
  after a successful link: **the project exists.** Record the number the message names before
  retrying, or the retry creates a second board.
- **On a NEW board, `provision` DELETES GitHub's default columns — when your `station_field` is
  the one GitHub already made.** A brand-new Projects v2 project ships a `Status` single-select
  carrying `Todo`, `In Progress` and `Done` (measured 2026-08-23 on project 7). Declare
  `station_field: "Status"`, as every board here does, and `provision` replaces that option set
  with exactly your declared stations and prints which options it removed. Declare any other
  name — `"Station"`, say — and there is nothing to replace: `provision` CREATES that field and
  GitHub's own `Status` field survives untouched, still carrying `Todo` and `In Progress`, as a
  column the board does not use. Neither behaviour is a bug; the difference is worth knowing
  before you pick a field name.
  Either way it touches only a board created in that same run — no items exist yet, so no card
  can lose its column. On an EXISTING board it only ever ADDS the missing stations and never
  removes a column.
- **Provisioning works only for a USER-OWNED board.** Every primitive queries `user(login:)`, and
  an organization-owned project is refused with "organization-owned board not supported". Create
  and configure that by hand; `provision` exits 2 saying so rather than doing something partial.
  Both repositories in the fleet today happen to be user-owned, so nothing else would surface this.
- `python3 .agents/skills/harness/bin/board_lifecycle.py audit` — show the operator the WORKFLOW
  findings **verbatim**.

**The three workflows are a HARD GATE you cannot automate.** `Item closed`, `Auto-close issue` and
`Pull request merged` cannot be enabled by any API: all 31 ProjectV2 mutations include
`deleteProjectV2Workflow` and none that creates or enables one, and `ProjectV2Workflow` exposes
neither its trigger nor its action. **Only a click in the project's web UI turns them on.** Ask the
operator to do it, then re-run the audit. Registration is not finished until it reports all three
enabled.

**Accepted cost, ruled by the operator:** this check runs ONCE, here, and never in
`check-state.sh` — that gate runs at every `/harness` door and before every commit, so a network
call there would fire dozens of times per build. The consequence is real: a workflow switched off
after registration is invisible until the next registration run.

## Next: plan the first feature

The repository is registered. Its first BRIEF, that BRIEF's approval, and any design pass are
`/harness-plan` work: run `/harness-plan` against the registered repository.

## Red flags

| Thought | Reality |
|---|---|
| "dev-ops filled the cmd, the `_reason` is harmless" | It says "unset — dev-ops has not run detection yet" next to a working command. Delete it |
| "`npm test` is the obvious command here" | Run it. An unverified `cmd` turns a hard gate into a silent no-op |
| "The repo is in fleet.yaml, so the factory can serve it" | Not until its `harness.json` is on its default branch. `product_config` has no fallback; run `--check-product-configs` |
