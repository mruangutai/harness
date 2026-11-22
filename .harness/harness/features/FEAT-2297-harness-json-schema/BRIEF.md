# BRIEF — FEAT-2297 One validated harness.json contract

## Problem

Harness readers currently interpret harness.json independently: malformed or missing configuration can silently disable close, branch and merge policies, while shape changes break consumers despite green unit checks. Maintainers also pay for duplicated validation and scattered fixtures; Kaya still carries schema_version 2 and status-less test_kinds. The settled intake is /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-harness-json-schema-2026-11-22.md; its thirteen choices remain binding.

## Done when — by perspective

**operator** — I can rely on invalid or missing configuration refusing work with a useful diagnosis, without losing the ability to repair it. Harness and Kaya accept the current contract after a deliberate upgrade, and Kaya's change reaches main only through my approved PR.

**code maintainer** — I have one configuration contract and read boundary rather than reader-specific interpretations. I can change valid test setup in one place, and the affected test code is smaller without losing meaningful policy coverage.

**reader** — I can trace enforcement, exceptions, migration, and test reduction to falsifiable evidence, including both unit and integration checks and a pinned migration/reduction record.

## Success criteria

- SC-01 (operator): The loader accepts documented absent-key defaults and current version-3 shapes, rejects present invalid values, unknown non-prose keys, status-less test_kinds, version 2, duplicate keys, non-finite JSON, non-object roots and missing files; errors retain source context, key path and violated rule, with an upgrade instruction for version 2. Qa demonstrates new assertions failing against the pinned pre-change implementation before production edits.
  verify: automated        evidence: unit
- SC-02 (operator): Every actual Python harness.json reader, including remote product_config, refuses invalid/missing input before a governed action and retains the loader diagnosis; check-state records a configuration violation rather than grading with substitute defaults. Absent optional keys still default; explicit valid sync-off and null-board behavior and unrelated transport/advisory policies remain unchanged. Integration cases demonstrate the fail-open baseline first.
  verify: automated        evidence: integration
- SC-03 (operator): The repair path reads legacy input without schema validation, migrates 2 to 3, gives every status-less kind a truthful status, preserves project commands, reasons, detection/exclusion globs and era values, validates before atomic replacement, and preserves the original when migration fails. Control-plane and template configs validate. Missing/unparseable source remains a diagnosed repair problem, not a fabricated replacement. Qa proves the migration assertions fail first.
  verify: automated        evidence: integration
- SC-04 (code maintainer): One schema-valid fixture builder supplies every harness.json fixture, shared and inline, including checked-in builder-generated TypeScript budget fixtures whose freshness is checked against that builder; Bun tests do not invoke Python at runtime. check_state_support.py, f58_sparse_fixture.py and gh_sync_support.py delegate rather than author separate configuration shapes. Deliberately invalid cases start with that valid base and visibly corrupt it (or explicitly remove its file); non-config artifacts and already-validated in-memory domain stubs are not misclassified. A fixture census exercises detection of a bypass before accepting the completed migration.
  verify: automated        evidence: integration
- SC-05 (code maintainer): Every REMOVABLE inventory row is deleted or retained with a specific policy-coverage reason; every UPDATE-BEHAVIOR row is rewritten for refusal on invalid/missing input or for the signed absent-key defaults where absence is valid. Net physical test lines across the union of affected existing and new test/helper files, generated budget fixtures and feature-only reduction/control tooling decrease against c1724230c4d931ad46d433c8ba93df8cf312f898. A receipt records the exhaustive row dispositions, both refs, per-file counts and negative total delta; its bounded feature checker must fail on an undisposed row, old fail-open assertion, or nonnegative delta. Qa runs this explicit offline integration evidence command in addition to the configured integration runner; it is not installed as an evergreen fixed-base test.
  verify: automated        evidence: integration
- SC-06 (reader): All changed/new JSON/YAML reader sites are represented in tests/integration/canonical-reader-classification.json; every ordinary harness.json entry names artifact_accessors.load_harness_json. Named repair/report routes and the advisory TypeScript budgets-only exception are explicit, and digest schemas, run identities and shipped feature comparison data no longer receive harness-config validation. Reader inventory and non-config regression cases fail first when the wrong route remains.
  verify: automated        evidence: integration
- SC-07 (reader): At review_sha, git show <review_sha>:<path> for .harness/harness/docs/DECISIONS.md, SPEC.md, .claude/skills/harness/templates/README.md and the feature change receipt agrees on defaults, conditional requirements, failure behavior, version-3 upgrade, closed vocabularies and exceptions. Every amend/strike disposition has landed and the decision index is regenerated; no document claims that #2293 condition evaluation shipped.
  verify: inspection
- SC-08 (operator): I review the dedicated mruangutai/kaya migration PR and authorize its merge to main. The durable receipt names the PR, my authorization and merge commit, and records a validated remote-main config containing version 3 and explicit statuses, with Kaya's unresolved/null commands still honestly unresolved.
  verify: uat
- SC-09 (reader): Unit-kind regression evidence covers the loader, strict non-config access, board normalization, review evaluation and existing TypeScript advisory fallback; integration-kind evidence covers real CLI/gate refusal, the check-state report, upgrade preservation and remote-authority/no-mutation boundaries. Qa maps both kinds to the live feature/runtime and config-shape floors and records fail-first evidence for new behavior, not merely a schema file's existence.
  verify: automated        evidence: unit
- SC-10 (reader): Integration-kind regression evidence independently covers the cross-process/config-shape contract and preserves unrelated feature-record, transport failure, valid sync-off/null-board and matrix semantic cases while the fixture migration reduces code. No matrix condition evaluator or plan-time reconciliation is introduced.
  verify: automated        evidence: integration

## Verification gaps

- Unit and integration are active with runnable commands in /Users/molchairuangutai/GitHub/harness/.harness/harness.json; their detect globs include the planned tests. They carry SC-01–SC-06 and SC-09–SC-10. The config-shape integration floor and the feature unit-plus-integration floor both apply; unit alone is insufficient.
- typecheck has cmd null/status unresolved. This feature preserves the TypeScript runtime budgets exception and changes only its test fixture construction; no typecheck result is claimed. Existing unit-kind TypeScript tests carry the unchanged fallback behavior (SC-09), and pinned inspection carries the documented exception (SC-07). This standing runner gap is not resolved by this feature.
- component and ui have null/unresolved runners, but there is no browser/component or interaction-flow change; no SC rests on them. functional and eval are excluded by DEC-187, not substitutes for unit/integration.
- issue_types_live is locally_run, not CI evidence. The manual probe's configuration-read refusal is covered offline by integration (SC-02); this feature neither changes nor claims verification of GitHub's live Issue Types service.
- SC-08 requires the operator personally; a prepared payload or green local suite is not proof of Kaya main landing. Kaya's own seven null runners remain unresolved, not excluded or invented.
- Local cumulative proof and configured unit/integration evidence precede Kaya PR publication and merge; they never wait for SC-08. SC-08 remains a mandatory independent ship gate.
- The operator's 2026-11-22 superseding OQ-SMOKE ruling authorizes removing only mruangutai/harness-factory-smoke from .harness/factory/fleet.yaml in T-03. Its remote main has an incompatible stations object; removal avoids retaining that transient member in the validated fleet. The smoke repository remains untouched; Kaya remains subject to migration and validation. Do not suppress any remaining fleet validation failure.
- Requested product guidance /Users/molchairuangutai/GitHub/harness/docs/spec.md, docs/decisions.md and docs/architecture.md is absent. AGENTS.md explicitly identifies .harness/harness/docs/SPEC.md and DECISIONS.md as Harness authority; those were consulted independently, not asserted to be the missing files. No architecture guidance is invented.

## Constraints

- SUPPLIES: DEC-03 state backbone, DEC-35 named matrix predicates, DEC-187 status/exclusion semantics, DEC-212 config-shape integration evidence, DEC-217 surface-sensitive floors, DEC-221 remote default-branch authority, DEC-202 authored .claude/skills tree and .agents discovery, and DEC-254 decision dispositions.
- BLOCKS: DEC-174 requires every task main-session-direct; the main session orchestrates and dispatches only product and validator leads, never harness-eng-lead. DEC-160 requires explicit decisions for configuration contract additions. DEC-13 keeps upgrade user-triggered; do not silently edit another project's state.
- Preserve all thirteen settled intake choices: full-reader migration; fail closed; Kaya rather than transient smoke as design constraint; absent-key defaults/current present shapes; closed unknown keys with unchecked underscore-prefixed prose; fixed enums; version 3 and 2-to-3 upgrade; config-schemas/harness.json on the existing jsonschema/referencing stack; budgets-only TypeScript exception; direct execution; plan mission; missing-file refusal; one fixture builder; measured test reduction.
- plan.yaml decisions propose the remaining defaults/API/conditional-key contract for signature. The operator, not a developer, approves those choices. Ordinary board absence defaults null; factory board-required operations still refuse a null board as their domain precondition.
- Keep only the named schema-validation bypasses: upgrade-config repair input and check-state's diagnostic report. Strict decoding is still shared; neither bypass authorizes a governed action with invalid configuration. Bash gates first apply their existing config-independent governed-command recognizers: unrelated/repair-only commands pass that gate without a config read, while every matched action validates and refuses invalid/missing input before consulting sync. Compound repair-plus-action commands receive no exemption; no repair-command allowlist is added. TypeScript resolveBudgetNumber remains advisory and budgets-only under DEC-198.
- Shared execution, authority, fixture and verification rules are defined once in notes/research-apply-plan-c1.md under Shared task contract. Every task intent must read that contract alongside this BRIEF and D-01–D-08 before execution; future dispatches must carry that reference and the task's literal verify block.

## Out of scope

- #2293: evaluating matrix conditions and reconciling SC evidence kinds at plan time. It is next; this feature only fixes the condition names.
- Changes to the harness-factory-smoke repository itself. Only removal of its mruangutai/harness-factory-smoke entry from .harness/factory/fleet.yaml is in scope under the superseding operator ruling.
- Schemas for team-config.yaml or fleet.yaml.
- Content validation of underscore-prefixed prose keys. The operational _matrix_provenance key is not prose and retains its declared current shape.

## Approval

status: approved
approved-by: Mike Ruangutai
date: 2026-11-22
