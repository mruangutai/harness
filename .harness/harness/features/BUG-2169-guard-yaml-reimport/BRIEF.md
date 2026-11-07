# BRIEF — BUG-2169 Guard YAML re-import

## Problem

Operators and fleet owners with one system-wide PyYAML installation encounter dispatch refusals because the guard purges and re-imports PyYAML over its cached C extension. CI's second-install workaround hides the broken layout, and the refusal recommends a per-user installation that the isolated policy phase cannot see. The corrected cause and layout table are recorded in issue #2169 and the operator's 2026-11-07 grilling at c4e8bbc8.

## Done when — by perspective

**operator (fleet owner)** — I can start governed work with a single system-wide PyYAML, with or without its C loader, without weakening import isolation. If PyYAML is absent, the platform-specific advice can clear the refusal and plainly discloses Homebrew's risk.

**CI** — I exercise the runner image's own single PyYAML installation rather than hiding the regression behind a second copy.

**code maintainer** — I can distinguish the broken and fixed layouts with preserved fail-first evidence, retain the guard's isolation boundary, and keep the documented absent-PyYAML fallback intact.

## Success criteria

- SC-01 (operator): Bootstrap retains and reuses system-wide yaml and yaml.* modules loaded in phase 1, including yaml._yaml; only yaml modules originating in per-user site, PYTHONPATH, cwd or the bin directory are purged. Only stdlib, system-wide packages and explicitly added bin/ decide in the isolated phase. Unit preflight cases demonstrate successful starts with a single system-wide PyYAML, C loader or not, and reject distrusted-origin leakage. QA preserves named failures against c4e8bbc8 or an explicitly pinned pre-fix state and green at the fixed pin, using harness-2169-repro (ubuntu:26.04 + python3-yaml) or CI's image-owned single PyYAML, not the Mac.
  verify: automated evidence: unit
- SC-02 (operator): Refusal advice selects Debian/Ubuntu apt install python3-yaml; Homebrew python3 -m pip install --break-system-packages pyyaml without --user, plainly stating Homebrew's PEP 668 warning that omitting --user can break the Homebrew installation; otherwise python3 -m pip install pyyaml. Each recommended install targets a location visible to the isolated phase. Unit assertions cover all three branches and warning disclosure, fail against the pinned pre-fix advice and pass at the fixed pin; retain that evidence in the same single-install source as SC-01.
  verify: automated evidence: unit
- SC-03 (CI): Inspection of git show <review_sha>:.github/workflows/tests.yml confirms removal of #2168's --ignore-installed change and its misleading distro-build comment, retaining image-owned single-PyYAML coverage rather than introducing another forced installation.
  verify: inspection
- SC-04 (code maintainer): The actual guard refusal and lead start-to-return integration suites preserve expected authorizations, refusals and claim behavior after the fix, with targeted isolation regressions for distrusted yaml origins. QA preserves discriminating pre-fix failures at c4e8bbc8 or an explicitly pinned pre-fix state plus green fixed-pin results from harness-2169-repro or CI's image-owned single PyYAML; a Mac pass is not regression evidence.
  verify: automated evidence: integration
- SC-05 (code maintainer): Inspection of git show <review_sha>:.claude/skills/harness/bin/worktree_terminal.py at _read_landed_plan_yaml and its fallback confirms the documented PyYAML-absent isolated-mode fallback remains functional and accurately explained; installation advice does not claim that every machine already has visible PyYAML or remove this fallback.
  verify: inspection

## Verification gaps

No applicable null-runner kind: unit and integration are active in .harness/harness.json and discover the three named suites. SC-01, SC-02 and SC-04 require preserved pre-fix and fixed-pin evidence from harness-2169-repro (ubuntu:26.04 + python3-yaml) OR CI on the image's own single PyYAML. This Mac has two copies and no system libyaml and cannot establish the regression. No reproduction is run during intake. Platform advice branches are asserted in tests; this is not a claim that real apt/Homebrew/pip installation was exercised on every host. SC-03 and SC-05 require pinned-content inspection; no UAT criterion requires the operator personally.

## Constraints

- SUPPLIES: operator-confirmed patch grilling /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-guard-yaml-reimport-2026-11-07.md supersedes the original ticket's build diagnosis and earlier install-advice tension.
- BLOCKS: DEC-174 category rule routes this hook correction and its tests main-session-direct despite backend/devops file grants. Main implements in the assigned feature worktree; no build team.
- SUPPLIES: DEC-225 one-run intake, brief at most 120 lines, one task, no panel or goal-check; DEC-182 controlled plan writes. DEC-120 BLOCKS approval by a spawned agent.
- BLOCKS: import isolation remains intact; no pure-Python-loader forcing or two-interpreter restoration.
- SUPPLIES: PRODUCT /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-2169-guard-yaml-reimport, CLAUDE.md and AGENTS.md map actual guidance to .harness/harness/docs/SPEC.md and DECISIONS.md. Generic docs/spec.md, docs/decisions.md and docs/architecture.md are absent; no architecture authority is invented.
- Exact Homebrew warning wording/placement and handling of non-yaml compiled modules within the unchanged isolation contract are builder choices, not unresolved scope.
- No prototype: bounded noninteractive hook/import correction and refusal guidance add no interactive surface; operator may override.

## Out of scope

- Removing or weakening import isolation — explicitly retained by the operator.
- Restoring two-interpreter subprocess design — the correction stays in-process.
- Forcing the pure-Python loader — the single-install C-loader layout must work.
- Digest append #2171 and other harness_yaml behavior — separate defects outside this bounded correction.

## Approval

status: pending
approved-by:
date:
