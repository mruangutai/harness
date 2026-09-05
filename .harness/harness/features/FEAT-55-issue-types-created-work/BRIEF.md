# BRIEF — FEAT-55-issue-types-created-work — native Issue Types on work Harness creates

Source ticket: mruangutai/harness#1289. Operator intent is settled in
`.harness/notes/grilling-issue-types-2026-09-04.md` `## Settled`; this brief preserves it.

## Problem

Every issue Harness creates carries GitHub's native `Issue Type` **unset**. Work nature is encoded
only as labels: `gh-sync.py`'s `type_label()` maps `change_type` to `chore` (`CHORE_TYPES` =
config, scaffolding, infra, ci) or `bug` (`bugfix`) and leaves everything else unlabeled;
`gh-sync.py backlog` accepts `bug|chore|enhancement` and again writes labels only;
`factory_decompose.py._task_labels` repeats the same two categories; parents get only `harness`.
So project views and organisation-level reporting cannot use the canonical Bug / Feature / Task
dimension, and the labels duplicate only part of that vocabulary while competing with it.
Measured while #1289 was filed: the pinned `github.repo` `mruangutai/harness` is user-owned and
returns GraphQL `issueTypes: null` (checked at eb9d044), so capability cannot be assumed anywhere.

## Goal

Whenever the target repository exposes GitHub Issue Types, every issue Harness **creates** gets the
correct native type — defects `Bug`, user-visible capabilities and enhancements `Feature`, chores and
implementation tasks `Task`, unless that repository's configuration declares different type names.
Where the repository does not expose Issue Types, nothing changes and the operator is told once, per
command invocation, why. Issues Harness did not create are never retyped.

## Requirements

- REQ-01: Every creation route types the issue it creates — feature parent, planned task sub-issue,
  ship-review backlog issue, factory parent, factory task. No route is exempt.
- REQ-02: Native-type capability is determined per target repository/owner at run time, never
  assumed and never inherited from another repository. Type **names** are resolved to that
  repository's type identifiers through GitHub's supported API; no identifier is inferred,
  guessed or hard-coded for a particular installation.
- REQ-03: Absent configuration, defects type as `Bug`, user-visible capabilities and enhancements as
  `Feature`, and chores and implementation tasks as `Task`. Feature parents and factory parents
  default to `Feature`. A repository-specific override of these type NAMES is available for every
  one of them, declared in project configuration rather than in code.
- REQ-04: The mapping is total. Every `change_type` value the project recognises — the ten in
  `test_matrix` (ai_behavior, api, bugfix, config, cross_module, docs, feature, frontend, logic,
  scaffolding) plus `infra` and `ci`, which `CHORE_TYPES` names — and every backlog nature
  (`bug`, `chore`, `enhancement`) resolves to a type name. No value falls through to unset, and an
  unrecognised value is reported, never silently accepted.
- REQ-05: When the target repository does not expose Issue Types, today's label behaviour is
  preserved exactly and the run emits exactly **one** compatibility diagnostic per command
  invocation, whatever the number of issues created. The absence of Issue Types never fails a run.
- REQ-06: When native Issue Types are active, the competing `bug` and `chore` labels are not
  applied to issues Harness creates. The operational labels — `harness`, `feature:<FEAT>`,
  `factory:claimed`, `abandoned` — are applied exactly as they are today, in both modes.
- REQ-07: When Issue Types are available but a configured or mapped type name does not exist in the
  target repository, the run refuses **before creating any issue**, and the refusal names the
  missing type and the configuration change that repairs it.
- REQ-08: An issue is not recorded as successfully mirrored until its required native type has been
  applied. A rerun after a failure between creation and type assignment identifies the
  already-created Harness issue and classifies it — never creating a duplicate, never deleting it.
- REQ-09: The record states the new authority: DEC-138's mechanical `change_type`-to-label
  derivation and its write-only reading of the mirror are amended to cover native types and the
  capability read, and DEC-203's bounded read-back purposes admit that read.
- REQ-10: No Harness command changes the type of an issue Harness did not create. Adopted parents
  and recorded `source_issues` are left as they are.
- REQ-11: The operator can execute #1289's live acceptance against an Issue-Types-enabled
  repository without writing new code: a host-only probe exists and is registered as a runnable
  test kind, and reports either a live pass or an explicit capability-absent verdict.

## Constraints

- **DEC-138 — BLOCKS.** It states label derivation from `change_type` as mechanical and the mirror
  as write-only. Both sentences are falsified by this feature (native types replace the two labels;
  capability detection is a read). Its scoped authority must be amended with the implementation
  (REQ-09), not worked around.
- **DEC-203 — BLOCKS.** Its read-back bound admits exactly seven purposes, and "which native issue
  types a repository declares" is not among them. Capability detection needs that bound widened in
  as many words, in the same amendment.
- **DEC-187 — BLOCKS.** Every kind named in the test matrix must be `active` or `excluded`, and a
  null `cmd` is BLOCKED rather than an inferred skip. The probe kind REQ-11 needs must therefore be
  registered with a real `cmd`, in the shape `omp_session_accessor` and `handoff_comprehension`
  already use (`status: locally_run`).
- **DEC-163 — SUPPLIES.** It licenses `locally_run` as the honest home for a host-only probe and
  requires the `## Verification gaps` block below.
- **DEC-174 — SUPPLIES the routing.** `.claude/skills/harness/references/**`,
  `.claude/skills/harness/SKILL.md`, `.claude/skills/harness/templates/**` and `docs/SPEC.md` are
  main-session-direct; the harness plans this work but does not dispatch a squad to it.
- **DEC-202 — SUPPLIES the spelling.** `.claude/skills/` is the one authored skill tree;
  `.agents/skills/` is a link to it. Every path written here uses the `.claude/skills/` spelling,
  and the two spellings are one file.
- `gh-sync.py`'s exit-code contract is unchanged: environmental problems (no `gh`, `sync: false`,
  unpinned repo) print `SKIP` and exit 0 — the mirror never gates — while caller and configuration
  errors exit non-zero. REQ-05 is the environmental path; REQ-07 is a configuration error.
- The mapping and recovery semantics in `## Settled` of the grilling note are user-settled. They are
  preserved as written, not re-derived.
- No new configuration surface: repository configuration already lives in `.harness/harness.json`'s
  `github` block.

## Out of scope

Recorded verbatim from the grilling note's `## Out of scope`:

- Changing adopted/source issues.
- Enabling or bootstrapping GitHub Issue Types for repositories that do not expose them.

## Success Criteria

- SC-01: With a `gh` that reports Issue Types available, `gh-sync.py open` and `gh-sync.py backlog`
  set a native type on the feature parent, on every task sub-issue, and on every backlog issue —
  asserted per created issue against the recorded call log, not as a total count.
  verify: automated        evidence: integration
- SC-02: With Issue Types available, `factory_decompose.py` sets a native type on the factory parent
  and on every factory task issue it publishes, asserted per issue.
  verify: automated        evidence: integration
- SC-03: Against a fake `gh` whose capability query returns `issueTypes: null`, every creation route
  produces byte-identical labels to today's behaviour and the run prints exactly one compatibility
  diagnostic for a fixture creating three or more issues. The blind spot this fixture must not have:
  a fake that never returns a GraphQL null cannot prove detection, so the null-returning fake is
  the case, and a populated-types fake is its positive control.
  verify: automated        evidence: integration
- SC-04: No type identifier is hard-coded or derived from a string pattern: at the reviewed sha,
  every type identifier used in a create or type-assignment call is traceable to a value returned by
  that repository's own capability response. Read with `git show <review_sha>:<path>`.
  verify: inspection
- SC-05: A table-driven test enumerates all twelve `change_type` values and all three backlog
  natures and asserts each resolves to a non-empty type name, one assertion per value; an
  unrecognised value resolves to a reported error rather than to unset. The test must be shown to
  fail before the mapping exists.
  verify: automated        evidence: unit
- SC-06: A configuration declaring different type names for defect, capability and chore work
  causes the outward type-assignment calls to carry the declared names and not the defaults, for
  both a task sub-issue and a parent.
  verify: automated        evidence: integration
- SC-07: With Issue Types active, no created issue carries a `bug` or `chore` label on any of the
  five routes, and `harness`, `feature:<FEAT>` and `factory:claimed` are still present exactly where
  they are today; in compatibility mode `bug` and `chore` reappear unchanged.
  verify: automated        evidence: integration
- SC-08: With Issue Types available and a mapped type name absent from the repository, each of the
  three creation commands separately — `gh-sync.py open`, `gh-sync.py backlog` and
  `factory_decompose.py` — refuses before creating anything: zero `issue create` calls reach the
  fake `gh`, zero type-assignment calls are made, the exit status is non-zero, and the message
  names both the missing type name and the configuration key to repair. Asserted per command, in
  that command's own test file; a refusal proven on one command never discharges this criterion
  for another.
  verify: automated        evidence: integration
- SC-09: In a fixture where creation succeeds and type assignment then fails, the issue is not
  recorded as mirrored; rerunning the same command makes no second `issue create` call, no delete or
  close call, and applies the type to the already-created issue.
  verify: automated        evidence: integration
- SC-10: `tests/manual/probe-issue-types.py` exists, is registered in `.harness/harness.json`
  `test_kinds` as a `locally_run` kind with a non-null `cmd`, and when run against the pinned
  `github.repo`, or against a repository the operator names explicitly through the probe's create
  opt-in, reports exactly one of three verdicts: a live pass naming the native types it
  observed on issues it created in the repository the opt-in named, reachable only under that
  explicit create opt-in and counting whether or not that repository is the configured one; a
  capability-present verdict naming the repository and the type names it declares while creating
  nothing, which is what the read-only default invocation reports against an Issue-Types-enabled
  repository; or an explicit capability-absent verdict naming the repository. It never
  reports a pass derived from a fixture. **An environmental skip is not a verdict and never
  satisfies this criterion**: no `gh` on PATH, `github.sync` false, an unpinned repo, or a failed
  capability query all make the probe report nothing about the repository, so they are outside
  the three verdicts and are never read as a pass — SC-10 stays unmet until one of the three is
  recorded.
  **This is the criterion that carries #1289's
  enabled-repository acceptance** — see `## Verification gaps`.
  verify: automated        evidence: issue_types_live
- SC-11: At the reviewed sha, `.harness/harness/docs/DECISIONS.md` states the amended authority for
  both DEC-138 (native types supersede the two derived labels; the capability read is authorised)
  and DEC-203 (the read-back bound admits the native-type read), and `DECISIONS-INDEX.md` matches
  the regenerated index. Read with `git show <review_sha>:<path>`.
  verify: inspection
- SC-12: An issue Harness did not create is never typed — not on the run that adopts it, and not on
  any later run. With Issue Types available and an adopted parent supplied by `--parent`, zero
  type-assignment calls carry that issue's node id on the adopting run or on a rerun without the
  flag, the provenance record reads `adopted` on both, and no type-assignment call carries a node id
  derived from any recorded `source_issues` number. Where a record's provenance is absent — a
  `feature.json` or `factory.yaml` written before this feature ships — zero type-assignment calls
  carry either recorded number on the first run or on a rerun, and no provenance entry is written for
  them. Asserted per recorded issue against the call log, on both the gh-sync and the factory route,
  and the red-check gate for each test file must name those cases individually so that omitting one
  fails as loudly as failing one. This is REQ-10's only falsifiable grading.
  verify: automated        evidence: integration

## Verification gaps

- **#1289's acceptance sentence "Against an Issue-Types-enabled repository …" is NOT executable in
  this environment.** The pinned `github.repo` `mruangutai/harness` is user-owned and returns
  GraphQL `issueTypes: null` (recorded in #1289, checked at eb9d044), and no Issue-Types-enabled
  repository is available here. SC-10 carries that acceptance, by method (ii): a `tests/manual/`
  probe registered as a `locally_run` kind. Run here, that probe can only return its
  capability-absent verdict; the live pass is available to the operator the first time the probe is
  pointed at an enabled repository. **No fixtured criterion above may be reported as a
  live-repository pass** — SC-01, SC-02, SC-03, SC-06, SC-07, SC-08 and SC-09 all run against the
  bash fake `gh` that `tests/integration/test-gh-sync.py` already installs via `GH_SYNC_GH` /
  `FACTORY_GH`.
- **The probe's live pass requires a real write, and it is opt-in.** The default invocation the
  registered kind runs creates nothing (D-19); SC-10's live pass is reachable only when the
  operator passes the probe's explicit create opt-in naming the target repository, and that mode
  **creates a real issue in the repository the flag names**, then reports the issue it created
  and the command that removes it.
- **What the fake cannot prove.** It dispatches on the argument string and returns canned payloads,
  so it validates nothing about GitHub's real field names, endpoint or acceptance of the
  type-assignment call: a wrong-but-consistent API shape passes every fixtured criterion. That risk
  is carried by SC-10 alone.
- **Registering the kind is implementation work** in `.harness/harness.json` (lane team, dev-ops),
  and a `locally_run` kind **does not run in CI** — so SC-10 is never green automatically; it is
  green only when the operator runs it and records the verdict.
- `component`, `ui`, `eval` and `typecheck` carry `cmd: null` in `test_kinds`. No criterion above
  rests on any of them, and this feature touches none of their surfaces.

## Approval

status: pending
approved-by:
date:
