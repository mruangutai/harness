# BRIEF — FEAT-56 Central onboarding model

## Problem

`harness-init` still tells its reader that onboarding runs *inside a product repository* and copies
`.harness/` into it (`.claude/skills/harness-init/SKILL.md:141-147` at `4b5dbb23`). That stopped
being true: `deploy.sh` is deleted (DEC-113), nothing distributes `bin/`, policy is read only from
the control plane's own `.harness/team-config.yaml`, a feature tree resolves to
`<control-plane>/.harness/<segment>/features` (`factory_config.features_root`), and a served
product's configuration is read from the REMOTE at its `default_branch` with no disk fallback
(`factory_config.product_config`). The cost is measurable rather than theoretical: the pilot product
carries four `.harness/` subtrees no reader ever opens — a 16.4 KB `team-config.yaml`, 14 expertise
files, three pre-migration feature dirs and an 11-file retired `codebase/` — while
`<control-plane>/.harness/kaya-ai/` does not exist at all, so its features are unreachable by every
feature reader. Fourteen executable sites and some twenty documents still assert the old model, so
an operator onboarding the next repository is instructed to produce artifacts that govern nothing,
and the first thing the factory does with a newly registered member is raise `FleetError`.

## Goal

Onboarding a repository means three things and nothing else: register it in
`.harness/factory/fleet.yaml`, stand up its central per-segment tree under
`<control-plane>/.harness/<segment>/`, and land exactly ONE file — `harness.json` — on that
repository's own default branch, where `product_config` reads it. Nothing else is installed into the
product repo. `harness-init` should say that, the tree should stop asserting the old per-product
scaffold, and a member registered before its `harness.json` lands should be told so by name rather
than discovered by a mid-build exception.

## Requirements

- REQ-01: The onboarding instruction of record states the central model — fleet registration,
  central per-segment tree, one file on the product's default branch — and instructs no other write
  into a product repository. In particular it no longer instructs a copy of `team-config.yaml` into
  a product.
- REQ-02: Installing the eight prerequisites and setting `core.hooksPath` survives as an operation
  on the CONTROL-PLANE CLONE, because `check-state.sh` INV-9 and INV-31 grade this clone against it
  on every run and a fresh clone of the control plane still needs it.
- REQ-03: No executable site — gate script, classification table or user-facing remedy — asserts
  that onboarding installs harness artifacts into a product repository, or tells a user to run
  `/harness-init` to repair a product-side path.
- REQ-04: The documentation, template and command surface describes onboarding as fleet registration
  plus one product-resident file, not as a per-product scaffold.
- REQ-05: A repository registered in the fleet whose `harness.json` has not landed on its default
  branch is reported by name, with its ref and path, by a check an operator can run at onboarding
  time — before a build reaches it and turns the gap into an unattributed `FleetError`.
- REQ-06: The verification suite asserts the model the tree actually implements: no test pins
  instruction wording the rewrite removes, and every test whose premise was the per-product install
  either states the surviving premise or is deleted with its reason recorded.

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

## Success Criteria

- SC-01: `git show <review_sha>:.claude/skills/harness-init/SKILL.md` states all three elements of
  the central model — `harness.json` landing on the product's `default_branch`, registration in
  `.harness/factory/fleet.yaml`, and the central tree `<control-plane>/.harness/<segment>/` — **in
  that order**, and contains no instruction to copy `team-config.yaml` into a project, i.e. no match
  for `templates/team-config.yaml`. Order is the discriminator: D-04 makes the config land BEFORE
  fleet registration, and presence anywhere in a 370-line file cannot see that claim, so a
  keyword-compliant rewrite would pass a presence-only check. Graded by running T-01's `verify`
  block verbatim against the tree at `<review_sha>`; it compares the first `grep -n` line number of
  each marker and exits non-zero if any element is absent or out of order. RED-CAPABLE and red at
  `4b5dbb23`, where all four presence greps return zero matches and `templates/team-config.yaml`
  still matches once.
  verify: automated        evidence: integration
- SC-02: The same blob still carries the per-clone install step scoped to the control-plane clone:
  both `git config --get core.hooksPath || echo "(unset)"` and
  `git config core.hooksPath .claude/skills/harness/hooks` are present verbatim, and
  `python3 tests/integration/test-hooks-install.py` exits 0 against it.
  verify: automated        evidence: integration
- SC-03: Each of the six named executable sites states the central model, checked one file at a
  time, not by one file-global search: `bin/check-instruction-paths.py` (`MAIN_SESSION_ONLY`'s
  rationale), `bin/check-state.sh` (its four `/harness-init` remedies), `bin/check-domain.sh` (the
  fail-open message), `bin/upgrade-config.py` (docstring plus two remedies), `bin/gh-sync.py` (the
  `github.repo` skip message), `bin/layout_migration.py` (the `MARKER` applicability rationale). A
  reviewer cites one `file:line` per file, six citations, read at `<review_sha>`.
  verify: inspection
- SC-04: Each of the fifteen named documentation, template and instruction files states onboarding
  as fleet registration plus one product-resident file:
  `.harness/harness/docs/SPEC.md`, `BUILD.md`, `DECISIONS.md` (the new entry),
  `DECISIONS-INDEX.md`, `org.html`, `README.md`, `.harness/README.md`,
  `.claude/skills/harness/templates/README.md`, `templates/harness.json`,
  `templates/team-config.yaml`, `templates/BRIEF.md`,
  `.claude/skills/harness/references/github-mirror.md`, `.claude/commands/harness.md`,
  `.claude/commands/harness-plan.md` and `.claude/commands/harness-grilling.md`. A reviewer cites
  one `file:line` per file, fifteen citations, read at `<review_sha>`.
  verify: inspection
- SC-05: `factory_config`'s product-config report names an unreachable member: with a stub whose
  read fails for one declared repository and succeeds for another, the report marks exactly that
  repository not-ok with a detail naming `<repo>@<ref>:.harness/harness.json`, and the CLI exits 2;
  with a stub that succeeds for both, it exits 0 and its ok count equals the declared count. Both
  directions assert in one suite run, and the failing direction must be shown to redden before the
  exit-code line exists.
  verify: automated        evidence: unit
- SC-06: `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` exits 0 at `<review_sha>`.
  verify: automated        evidence: unit
- SC-07: `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` exits 0 at
  `<review_sha>`, with no case reporting a skip for a missing skill anchor.
  verify: automated        evidence: integration
- SC-08: `python3 .claude/skills/harness/bin/check-omp-port.py` prints `OMP port surface: ok` and
  exits 0 after the dev-ops agent definition changes, and
  `python3 .claude/skills/harness/bin/check-instruction-paths.py` exits 0 with zero violations.
  verify: automated        evidence: integration
- SC-09: The operator reads the rewritten `harness-init` and confirms it is the procedure they would
  actually run to onboard the next repository — that nothing in it asks them to write a file the
  factory does not read, and that the step order tells them what to do between fleet registration
  and the product's first `harness.json` commit.
  verify: uat
- SC-10: The shipped template `.claude/skills/harness/templates/team-config.yaml` loads as YAML:
  `python3 -c "import yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))"`
  exits 0. The criterion is graded by running that exact command against the tree at
  `<review_sha>`. It is RED-CAPABLE and red today: at `4b5dbb23` it exits 1 with
  `yaml.parser.ParserError: while parsing a flow sequence ... expected ',' or ']', but got
  '<scalar>'`, the sequence opening at line 28 column 11, because the inline `## Approval` text
  inside the unquoted `main_session.writes:` flow sequence reads as a YAML comment and leaves the
  sequence unterminated. It turns green only once every entry of that sequence is a quoted scalar.
  verify: automated        evidence: integration

## Verification gaps

- `component`, `ui` and `typecheck` have no runner here (`cmd: null`), and `functional` and `eval`
  are excluded. This feature touches none of those surfaces, so nothing rests on them.
- **No runner grades an instruction being FOLLOWED.** `harness-init` is prose executed by a model
  and an operator. What the suite can prove of it is now three things, not two: the ordered
  statement of the central model and the absence of the struck copy instruction (SC-01), the
  command strings a test reads out of it (SC-02, `tests/integration/test-hooks-install.py`), and
  that the gates around it stay green (SC-06, SC-07, SC-08). Whether the rewritten procedure
  actually onboards a repository is still carried by SC-09 (uat) and by nothing else. A dry run
  against a real new repository is not in scope and is therefore not proven.
- **SC-01, SC-08 and SC-10 name an exact command, not a file the runner discovers.** Their
  `evidence: integration` label is the nearest ACTIVE kind (`--kind integration`, non-null `cmd`),
  but the assertions themselves live in a task `verify:` block or a one-line interpreter call, so
  running the integration suite alone does not grade them. Each is graded by executing the command
  the criterion names, at `<review_sha>`.
- **`check-state.sh` deliberately makes no network call**, so no every-run invariant can grade a
  fleet member's remote `harness.json`. REQ-05 is discharged by an operator-run check (SC-05), which
  means a member whose config is deleted after onboarding stays invisible until the next build.

## Approval

status: approved
approved-by: molchairuangutai
date: 2026-09-08
