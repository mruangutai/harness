# BRIEF — FEAT-56 Central onboarding model

## Problem

`harness-init` still tells its reader that onboarding runs *inside a product repository* and copies
`.harness/` into it (`.claude/skills/harness-init/SKILL.md:141-147` at `4b5dbb23`). That stopped
being true: `deploy.sh` is deleted (commit `45859123`, FEAT-12 for issue #259 — no `DECISIONS.md`
entry records that deletion, and DEC-113 governs crew overrides rather than distribution), nothing
distributes `bin/`, policy is read only from the control plane's own `.harness/team-config.yaml`, a
feature tree resolves to
`<control-plane>/.harness/<segment>/features` (`factory_config.features_root`), and a served
product's configuration is read from the REMOTE at its `default_branch` with no disk fallback
(`factory_config.product_config`). The cost is measurable rather than theoretical: the pilot product
carries four `.harness/` subtrees no reader ever opens — a 16.4 KB `team-config.yaml`, 14 expertise
files, three pre-migration feature dirs and an 11-file retired `codebase/` — while
`<control-plane>/.harness/kaya-ai/` does not exist at all, so its features are unreachable by every
feature reader. Fourteen executable sites and some twenty documents still assert the old model, so
an operator onboarding the next repository is instructed to produce artifacts that govern nothing,
and the first thing the factory does with a newly registered member is raise `FleetError`.

A second defect, measured at `12f74ea8` after the first rewrite shipped: onboarding conflates two
unrelated jobs, and one of its two surfaces is not reachable at all. One 434-line skill carries both
`## Track A — bootstrap this harness checkout` (`.claude/skills/harness-init/SKILL.md:48`) and
`## Track B — register a repository into this configured fleet` (`:239`), so an operator adding the
fleet's next repository reads a procedure whose first third configures a checkout they set up months
ago — and whose steps 6, 7 and 8 (`:324`, `:335`, `:408`) then make them interview for a first
BRIEF, take its approval and run a design pass before the repository is even usable. That is
`/harness-plan`'s work, sitting inside onboarding. Separately, the provider-neutral surface is a
claim rather than a fact: `.omp/config.yml` sets `disabledProviders: [claude]`, `.omp/commands/`
does not exist, and `.omp/extensions/harness-hooks.ts` registers no slash command, so all four
`/harness*` doors resolve under Claude Code only and under OMP fall through silently as prompt text
— no error, no symptom.

## Goal

Onboarding splits into TWO artifacts, each with one job. `harness-init` configures a FRESH HARNESS
CHECKOUT for the first time and does nothing else. A new provider-neutral skill, `harness-add-repo`,
registers a repository into an already-configured control plane: land exactly ONE file —
`harness.json` — on that repository's default branch where `product_config` reads it, add its
`.harness/factory/fleet.yaml` entry, create its central per-segment tree under
`<control-plane>/.harness/<segment>/`, in that order. The first BRIEF, its approval and the design
pass are NOT onboarding: a configured fleet repository that lacks its first BRIEF routes to
`/harness-plan`. And the provider-neutral surface must be REACHABLE THROUGH OMP, not neutral in
principle only — the four `/harness*` doors live at a canonical neutral root with a gate that goes
red if any of them regresses to a Claude-only path.

## Requirements

- REQ-01: The instruction of record for configuring a harness checkout — `harness-init` — contains
  no repository-registration instruction at all: no fleet entry, no product-resident
  `harness.json`, no central-tree creation for a member. It states the central model only insofar
  as it names the artifact that does own it.
- REQ-02: Installing the eight prerequisites and setting `core.hooksPath` survives as an operation
  on the CONTROL-PLANE CLONE, because `check-state.sh` INV-9 and INV-31 grade this clone against it
  on every run and a fresh clone of the control plane still needs it.
- REQ-03: No executable site — gate script, classification table or user-facing remedy — asserts
  that onboarding installs harness artifacts into a product repository, and each remedy names
  whichever of the two artifacts actually does the job it is remedying.
- REQ-04: The documentation, template and instruction surface describes onboarding as two jobs with
  two artifacts — configure a checkout, register a repository — and never as a per-product scaffold
  and never as one combined procedure.
- REQ-05: A repository registered in the fleet whose `harness.json` has not landed on its default
  branch is reported by name, with its ref and path, by a check an operator can run at onboarding
  time — before a build reaches it and turns the gap into an unattributed `FleetError`.
- REQ-06: The verification suite asserts the model the tree actually implements: no test pins
  instruction wording the rewrite removes, and every test whose premise was ONE combined onboarding
  skill either states the surviving premise or is deleted with its reason recorded.
- REQ-07: A provider-neutral skill `harness-add-repo` exists and carries repository registration end
  to end — its own preflight, the one-file rule, the ordered three steps, the Issues mirror and
  board questions — so that an operator adding a repository reads that artifact and no other.
- REQ-08: Neither artifact contains first-BRIEF, approval or design work, and the routing surface
  sends a configured fleet member that lacks a BRIEF to `/harness-plan` rather than to onboarding.
- REQ-09: The four `/harness*` doors are reachable under OMP, from a canonical neutral root, with
  the same text Claude Code reads; no door is authored only where a single provider can discover it.
- REQ-10: A regression of any door to a Claude-only path fails a check, rather than failing open as
  prompt text.
- REQ-11: The harness declares no `cli_min_version` in any configuration file it carries or ships,
  and the CLI version band survives in `DEC-83` and `BUILD.md` as the documented compatibility
  fact a reader consults rather than as a floor any config declares. Ruled by the operator on
  2026-09-09 (D-13), after `D-12` removed the only onboarding step that read a CLI version.

## Constraints

- **DEC-174 SUPPLIES the mechanism** and is not to be overturned: a served product's configuration
  is read from its own repository at `default_branch`, with no disk fallback. Ruled binding for this
  feature by the plan-phase advisor consult
  (`features/FEAT-56-central-onboarding-model/runs/2026-09-08-01-plan-advisor-validator/digest.md`).
- **Issue #206 item 2 is NOT to be built.** Its literal instruction — create
  `.harness/products/<name>/` — matches no resolver in the tree and would overturn DEC-174. The
  operator struck that placement on 2026-08-18 (#336 body, on #493).
- **DEC-182 SUPPLIES** the plan artifact: a new feature gets `plan.yaml`, never `PLAN.md`.
- **DEC-188 BLOCKS** editing historical `features/**` plans and notes: they are record.
- **`tests/fixtures/prior-check-domain.sh.fixture` must not be touched** — it is a frozen prior copy
  of `check-domain.sh` and editing it defeats the fixture.
- `.agents/skills` is a symlink to `.claude/skills`; the pair that genuinely desynchronizes is
  `.omp/agents/**` against `.claude/agents/**`, kept in step by `bin/sync-agent-adapters.py` and
  asserted by `bin/check-omp-port.py`.
- The "human clones a repo and runs `/harness` inside it, outside the factory workspace" case has no
  mechanism (`deploy.sh` deleted, nothing distributes `bin/`) and is not a subject of this feature.
- **Issues #203 and #206 are reconciled IN FAVOUR OF REWRITE.** #206 asked for #203 — which scoped
  the deletion of `harness-init` — to be reconciled before either was picked up. #203 is closed, the
  `deploy.sh` premise it was scoped around is absent from `.claude/skills/harness/bin/`, and
  `.claude/skills/harness-init/SKILL.md` still exists and is still the only onboarding instruction
  of record. So this feature rewrites the skill to the central model and no task deletes it (D-06).
- **The operator's ruling of 2026-09-08 BINDS the shape** and is not to be re-litigated
  (`features/FEAT-56-central-onboarding-model/notes/answers-rescope-2026-09-08.md`): issue #206 is
  revised in place; `harness-add-repo` is a SKILL, provider-neutral; the OMP command-door port
  ships in THIS feature; first-BRIEF, approval and design leave onboarding for `/harness-plan`.
- **DEC-06 SUPPLIES, and is not re-decided.** Its conclusion — the runner is a skill, not a command
  — is what `harness-add-repo` conforms to. Its stated premise, that `/harness-deploy` distributes
  skills but not `.claude/commands/` (`DECISIONS.md:95-97`), expired when `deploy.sh` and
  `.claude/commands/harness-deploy.md` were deleted; the conclusion survives on the neutrality
  ground instead, which is why nothing here reverses a signed decision.
- **T-01..T-08 are delivered and stay `done`.** The operator rejected the SHAPE, not the work:
  DEC-220, `product_config_report()`, `--check-product-configs` with its 18-case suite, the
  six corrected `bin/` sites and the repaired `templates/team-config.yaml` are the substrate this
  revision splits, and nothing in it is reverted.

## Non-goals

- **Migrating or deleting the pilot product's four stale `.harness/` subtrees.** Removing them is a
  write into a product repository that no agent domain grants, and `.harness/team-config.yaml` is
  `harness_boundary.MARKER`, which `root_above` reads to decide which checkout a path belongs to —
  deleting it from a default branch is not reversible by a later cycle. The rewritten skill must
  STOP PRODUCING those artifacts; removing already-committed ones is separate, operator-gated work.
- **Per-repo domain isolation.** `harness_boundary.glob_to_re` supports only `**`, `*`, `?` and
  literals, so `.harness/${repo}/**` is inexpressible; the live grants are repo-agnostic globs and
  `team-config.yaml` is forced-global. That work is #495 and is unbuilt.
- **Reviving the codebase-map tier.** #206's row 8 is void: the tier, both doors, its invariants, its
  spawn injection and its renderer were retired 2026-08-24 (`BUILD.md:208`). Nothing here re-homes
  a map, and `.harness/<segment>/codebase/` has no resolver.
- **Creating `.harness/products/` in any form**, centrally or in a product repo. It matches no
  resolver; see Constraints.
- **Creating a successor feature or a narrowed FEAT-56.** The operator ruled the revision happens in
  place, on issue #206 (D-07).
- **Re-deciding DEC-06.** `harness-add-repo` is a skill, which is DEC-06's own conclusion; the
  expiry of its distribution premise is recorded (D-10) and nothing is reversed.
- **Adding a `/harness-add-repo` or `/harness-init` command door.** Both are skills, loadable under
  every provider today; minting a command file for either would re-commit the shape the operator
  rejected. The door port covers the four doors that already exist and adds none.
- **Un-slashing the ~20 documents that spell `/harness-init` as if it were a command.** The spelling
  predates this feature and resolves in neither surface; it is a separate chore, recorded here so it
  is not mistaken for delivered work.

## Success Criteria

Five criteria were graded MET against the delivered T-01..T-08 work at `12f74ea8`: SC-02, SC-05,
SC-06, SC-07 and SC-10. **No grade is carried forward, and every one of the five is re-taken at
`<review_sha>`.** Four of them have a subject this revision rewrites — SC-02's blob by T-11,
SC-10's file by T-12, SC-06's unit suite by T-17, SC-07's integration suites by T-14 and T-17 — so
a `12f74ea8` grade would be a statement about a different artifact. SC-05's subject is genuinely
untouched (no task's `files:` names `factory_config.py` or `test-fleet-product-config.py`), and it
is still re-taken, because a grade observed at another pin is not evidence about this one. The
per-SC paragraphs below say the same thing; if a later goal-check finds this preamble and a
paragraph disagreeing, the paragraph is wrong and both must be fixed before the grade is taken.
**SC-09 is STRUCK** — it graded the operator reading `harness-init` as the
procedure they would run to onboard the next repository, which the split makes false by
construction; no grade of it is carried, and SC-11 and SC-12 replace it, one per resulting artifact.

- SC-01: `git show <review_sha>:.claude/skills/harness-add-repo/SKILL.md` states all three elements
  of the central model — `harness.json` landing on the product's `default_branch`, registration in
  `.harness/factory/fleet.yaml`, and the central tree `<control-plane>/.harness/<segment>/` — **in
  that order**, and contains no instruction to instantiate or to copy a `team-config.yaml` — not
  into a project and not for the control plane, whose own instantiation instruction stays in
  `harness-init` (T-11). Order is the
  discriminator: D-04 makes the config land BEFORE fleet registration, and presence anywhere in a
  long file cannot see that claim. Graded by running T-10's `verify` block verbatim at
  `<review_sha>`. RED at `12f74ea8`: the file does not exist.
  verify: automated        evidence: integration
- SC-02: `git show <review_sha>:.claude/skills/harness-init/SKILL.md` still carries the per-clone
  install step scoped to the control-plane clone — both `git config --get core.hooksPath || echo
  "(unset)"` and `git config core.hooksPath .claude/skills/harness/hooks` present verbatim — and
  `python3 tests/integration/test-hooks-install.py` exits 0 against it. Graded ONLY at
  `<review_sha>`: T-11 rewrites this blob, renumbers the steps around those two commands and now
  also keeps three sections inside it, so no `12f74ea8` grade is retained.
  verify: automated        evidence: integration
- SC-03: Each of the six named executable sites states the central model AND names the artifact that
  owns the job its remedy describes, checked one file at a time, never by one file-global search:
  `bin/check-instruction-paths.py` (`MAIN_SESSION_ONLY`, which must list `harness-add-repo`),
  `bin/check-state.sh` (its four `/harness-init` remedies — each must be a checkout-configuration
  or `--upgrade` condition, never a registration one), `bin/check-domain.sh` (the fail-open
  message), `bin/upgrade-config.py` (docstring plus two remedies), `bin/gh-sync.py` (the
  `github.repo` skip message), `bin/layout_migration.py` (the `MARKER` applicability rationale). A
  reviewer cites one `file:line` per file, six citations, read at `<review_sha>`.
  verify: inspection
- SC-04: Every main-session-owned instruction file and every document naming onboarding names the
  RIGHT one of the two artifacts, cited one `file:line` per file at `<review_sha>`. The set, and it
  is the union of what the tasks touch: `.claude/commands/harness.md`, `harness-plan.md`,
  `harness-ship.md`, `harness-grilling.md`; `.claude/skills/harness-grilling/SKILL.md`;
  `.claude/skills/harness/templates/README.md`, `harness.json`, `team-config.yaml`, `BRIEF.md`,
  `PLAN.md`, `DESIGN.md`; `.claude/skills/harness/references/github-mirror.md`;
  `.harness/harness/docs/SPEC.md`, `BUILD.md`, `DECISIONS.md` (the new entry), `DECISIONS-INDEX.md`,
  `org.html`; `README.md`; `.harness/README.md`; `.omp/agents/harness-dev-ops.md` and
  `harness-visual-designer.md` with their two `.claude/agents/` adapters.
  verify: inspection
- SC-05: `factory_config`'s product-config report names an unreachable member: with a stub whose
  read fails for one declared repository and succeeds for another, the report marks exactly that
  repository not-ok with a detail naming `<repo>@<ref>:.harness/harness.json`, and the CLI exits 2;
  with a stub that succeeds for both, it exits 0 and its ok count equals the declared count.
  Graded at `<review_sha>` by re-running `tests/unit/test-fleet-product-config.py` (18/18 at
  `12f74ea8`, issue-free). No task in this revision touches `factory_config.py`, so the re-take is
  expected to reproduce that result — but the grade of record is the one taken at the new pin.
  verify: automated        evidence: unit
- SC-06: `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` exits 0 at `<review_sha>`.
  Graded at `<review_sha>` only: T-17 rewrites `tests/unit/test-no-distribution.py`, so this is the
  standing gate over the revision's own diff and no earlier grade is retained.
  verify: automated        evidence: unit
- SC-07: `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` exits 0 at
  `<review_sha>`, with no case reporting a skip for a missing skill anchor. Graded at
  `<review_sha>` only: T-14 and T-17 add and rewrite integration suites, so this is the standing
  gate over the revision's own diff and no earlier grade is retained.
  verify: automated        evidence: integration
- SC-08: With the new skill present, `python3 .claude/skills/harness/bin/check-instruction-paths.py`
  exits 0 with zero violations, and `python3 .claude/skills/harness/bin/check-omp-port.py` prints
  `OMP port surface: ok` and exits 0 — the second now including the command-door assertion SC-13
  names, so a green here can no longer mean "the doors were never looked at".
  verify: automated        evidence: integration
- SC-10: The shipped template `.claude/skills/harness/templates/team-config.yaml` loads as YAML:
  `python3 -c "import yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))"`
  exits 0 at `<review_sha>`. Graded at `<review_sha>` only: T-12 edits that file's comment header,
  so the `12f74ea8` grade (issue #168) is about a different blob and is not retained.
  verify: automated        evidence: integration
- SC-11: The operator runs `harness-init` as a FRESH-CHECKOUT procedure and it works as one. About
  ten minutes, from the UAT script: they read the skill top to bottom against a scratch clone of
  this repository and confirm that every step is about the checkout in front of them, that nothing
  asks them to register a repository, write a BRIEF, take an approval or run a design pass, and that
  the `--upgrade` section no longer points at a step that has left the file. They write PASS or FAIL
  with a one-line reason.
  verify: uat
- SC-12: The operator runs `harness-add-repo` as a REGISTRATION procedure and it works as one. About
  ten minutes: with the control plane already configured, they follow the skill for one real
  candidate repository up to the point of the fleet entry, and confirm its preflight catches the
  unconfigured-control-plane and missing-`gh` cases, that the three steps are in the order the
  config-first rule requires, and that it ends with `--check-product-configs` rather than with a
  BRIEF. They write PASS or FAIL with a one-line reason.
  verify: uat
- SC-13: The four doors are reachable through OMP, and a regression to Claude-only goes RED
  mechanically rather than by inspection. Four assertions, each its own: `python3
  .claude/skills/harness/bin/sync-command-adapters.py --check` exits 0; `.omp/commands/harness.md`,
  `harness-plan.md`, `harness-ship.md` and `harness-grilling.md` each exist at `<review_sha>`,
  asserted one file at a time and never by a count;
  `python3 tests/integration/test-sync-command-adapters.py` exits 0, one of its cases building a
  temp tree in which a door exists ONLY under `.claude/commands/` — today's exact state — and
  asserting the check reports it non-zero; and `python3
  tests/integration/test-check-omp-port.py` exits 0 carrying a case that deletes one
  `.omp/commands/` door from an otherwise-valid temp root and asserts `check()` names it. The last
  two clauses are the criterion's teeth: without them the first two are satisfied by a check that
  looks at nothing, and `check-omp-port.py` could be left unedited while the verify still passed.
  verify: automated        evidence: integration
- SC-14: Neither artifact carries first-BRIEF, approval or design work, and the routing surface
  sends a BRIEF-less fleet member to `/harness-plan`. `python3
  tests/integration/test-onboarding-split.py` exits 0, asserting per file and per token at
  `<review_sha>`: `harness-init/SKILL.md` matches none of `Track B`, `factory/fleet.yaml`,
  `The approval gate`, `then the BRIEF`, `Design pass`, `harness-visual-designer`,
  `claude --version`, `2.1.217`; `harness-add-repo/SKILL.md` matches none of
  `The approval gate`, `then the BRIEF`, `Design pass`, `harness-visual-designer`; and neither
  `.claude/commands/harness-plan.md` nor `.claude/commands/harness-grilling.md` matches
  `harness-init`. RED at `12f74ea8`: the file does not exist, and `harness-init/SKILL.md`
  matches `Track B` twice, `factory/fleet.yaml` twice, `claude --version` once and `2.1.217`
  once.
  verify: automated        evidence: integration
- SC-15: The operator opens an OMP session in this repository and confirms that `/harness-plan`
  resolves from `.omp/commands/`. About a minute, and only they can run it: in the session they
  type `/harness-plan` and observe what the session does with it. PASS only if the door is
  RECOGNISED as a command and its instruction runs. It FAILS in either of two ways, and the
  operator records WHICH: (a) it does not resolve at all — the text comes back as an ordinary
  prompt or as an unknown command, which is the original bug this feature exists to fix; or (b) it
  resolves, but from some root other than `.omp/commands/`. The two are told apart in one step:
  before opening the session, add a marker line to `.omp/commands/harness-plan.md` (for example
  `<!-- OMP-ROOT-PROBE -->` plus an instruction to echo it first); if the door runs and the marker
  is honoured, the session read that file and it is a PASS; if the door runs but the marker is
  absent, it resolved from another root and it is FAIL (b). Revert the marker afterwards. They
  write PASS or FAIL with the failure letter or a one-line reason; nobody else may set it.
  verify: uat
- SC-16: No configuration file declares `cli_min_version`, checked ONE FILE AT A TIME and never by
  one file-global search — four conforming sites satisfy a global grep and are blind to the fifth.
  For each of `.harness/harness.json`, `.claude/skills/harness/templates/harness.json` and
  `.claude/skills/harness/templates/examples/harness.kaya-ai.json`, `git show
  <review_sha>:<path>` parses with `json.load` and the loaded mapping lacks the key; for each of
  `.harness/team-config.yaml` and `.claude/skills/harness/templates/team-config.yaml` it parses
  with `yaml.safe_load`, the loaded mapping lacks the key, and the blob matches neither
  `cli_min_version` nor the trailing comment `floor for the spawn env vars`. And the amendment
  landed: `git show <review_sha>:.harness/harness/docs/BUILD.md` matches `cli_min_version`
  nowhere, while `git show <review_sha>:.harness/harness/docs/DECISIONS.md` matches both
  `cli_min_version` — DEC-83 names the key it no longer declares — and the band row `2.1.172`,
  which must survive the amendment. RED at `97fe447f`: all five configs carry the key
  (`.harness/harness.json:3`, `.harness/team-config.yaml:11`,
  `.claude/skills/harness/templates/harness.json:4`,
  `.claude/skills/harness/templates/team-config.yaml:22`,
  `.claude/skills/harness/templates/examples/harness.kaya-ai.json:4`), `BUILD.md:426` carries it
  in its key enumeration, and `DECISIONS.md` matches it nowhere.
  verify: automated        evidence: integration

## Verification gaps

- `component`, `ui` and `typecheck` have no runner here (`cmd: null`), and `functional` and `eval`
  are `excluded` under DEC-187. This feature touches none of those surfaces, so nothing rests on
  them. The two ACTIVE kinds are `unit` and `integration`, and every `automated` criterion above
  names one of them.
- **No runner grades an instruction being FOLLOWED.** Both skills are prose executed by a model and
  an operator. What the suite proves of them is structural: that the ordered central-model statement
  MOVED to `harness-add-repo` and left `harness-init` (SC-01, SC-14), that the two command strings a
  test reads out of Track A survive (SC-02), and that the gates around them stay green (SC-06,
  SC-07, SC-08). Whether either procedure actually onboards anything is carried by SC-11 and SC-12
  (uat) and by nothing else. A dry run against a real new repository is not in scope and is
  therefore not proven.
- **The struck SC-09 is not replaced by an automated criterion, and could not be.** It was an
  operator judgement about a procedure's fitness. SC-11 and SC-12 are the same kind of judgement,
  split per artifact, and remain `not_met` until the operator executes each script.
- **SC-01, SC-02, SC-10, SC-16 and SC-13's first two clauses name an exact command, not a file the
  runner discovers.** Their `evidence: integration` label is the nearest ACTIVE kind, but the
  assertions live in a task `verify:` block or a one-line interpreter call, so running the
  integration suite alone does not grade them. Each is graded by executing the command the
  criterion names, at `<review_sha>`. SC-13's third clause and SC-14 are the exception: they are
  permanent test files the integration suite discovers and runs.
- **No AUTOMATED gate proves a door is DISCOVERED by a provider.** SC-13 proves the four doors exist
  at the neutral root with identical text and that a Claude-only door reddens the check. Whether an
  OMP session actually resolves `/harness-plan` from `.omp/commands/` is observed by the operator in
  a live session — gated by SC-15 (`uat`), which is required and blocks the ship decision, but which
  no runner can take over: `.omp/config.yml` cannot be exercised by a test in this repository.
- **`check-state.sh` deliberately makes no network call**, so no every-run invariant can grade a
  fleet member's remote `harness.json`. REQ-05 is discharged by an operator-run check (SC-05), which
  means a member whose config is deleted after onboarding stays invisible until the next build.

## Approval

status: pending
approved-by:
date:
