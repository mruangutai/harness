# Typecheck plan — draft receipt

Four ordered, main-session-direct tasks cover all operator-settled constraints; approval remains pending. No implementation or production typecheck was performed.

## Contract and coverage

- Goal: [source #2257](https://github.com/mruangutai/harness/issues/2257); operator scope and baseline observations remain the grilling artifact at /Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-typescript-typecheck-2026-11-22.md, observed at 120b131f. Those observations were not rerun.
- BRIEF.md defines operator, code maintainer and reader perspectives; 12 SCs use three automated criteria (existing active integration/unit kinds) and nine inspections. None needs user-executed UAT or rests on unresolved typecheck.
- T-01: exact dev-only compiler/Bun type pins, manifest/lock/config, ignored node_modules, full tracked-source inclusion and maintainer/upgrade documentation (SC-01/02/04/10/11/12).
- T-02, after T-01: real compiler red-first, all eight fixture errors repaired without weakening assertions or production typing, existing Bun suite non-regression (SC-01/09/10/12).
- T-03, after T-02: frozen installation in checks and compiler-dependent integration shards; unconditional PR compiler step carried by required integration; weekly root bun Dependabot entry (SC-03/05/06/10/12).
- T-04, after all predecessors: independently enumerate tracked sources, execute the real compiler and independently poison every source, then activate only after an actual recorded pass; remove _reason, preserve detect/exclude and leave test_matrix/_matrix_provenance unedited (SC-01/02/04/07/08/09/10/12). Final validation binds compiler/unit/integration and CI receipts to the review and merge trees.
- pi/ctx:any real-OMP typing, other JS dependencies, linters and formatters remain excluded (SC-10). The runtime suite is honestly identified as preservation evidence, not invented fail-first evidence.

## Decisions and routing

- Ten exact keep rows cover nine governing DECs: 35, 98, 174, 179, 183 (required context and accepted workflow limitation separately), 187, 212, 213 and 217. No adopted ruling is amended/struck; no new choice passes DEC-149's three-part D-NN threshold. The operator already settled the toolchain and enforcement choices.
- At 0bdcabbfc585a9357554817684d1b8a19d69038a, check-domain --resolve was run for each of the ten planned files, all exit 0. package.json, bun.lock, tsconfig.json and .gitignore resolve NOBODY. Hook tests, CI and activation/regression are direct under DEC-174; README/Dependabot accompany their respective direct cutovers. Shared files have one owning task each.
- Product paths docs/spec.md, docs/decisions.md and docs/architecture.md are absent. Question resolved from README.md Canonical surfaces: Harness explicitly locates its guidance at .harness/harness/docs/{SPEC,DECISIONS,BUILD}. SPEC section 9, relevant DEC entries and BUILD's opening relationship statement were consulted; each actual task intent carries checkout identity and guidance pointers. No absent guidance was invented.

## Checks actually performed

- Backlog intake: gh issue list --repo mruangutai/harness --state open --limit 100 and gh issue view 2257; no additional source issue absorbed.
- Root resolved with control-plane inflight_registry.py feature-root; all file routes queried with control-plane check-domain.py --resolve, exit 0.
- Plan created only through control-plane plan-merge.py apply; stdout captured/printed. Initial YAML indentation failed before creation. First plan check then rejected a multiline DEC-183 quote whose indentation was not verbatim; corrected via set-key to an exact one-line clause.
- Final command: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2257-typescript-typecheck/.harness/harness/features/FEAT-2257-typescript-typecheck/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2257-typescript-typecheck
- Observed exit 0: 4 tasks, 10 anchors resolved, 0 failures. No overlap reported. No APPROVAL-RESET receipt, so no gh-sync status call.
- The writer's automatic changed-state output reports unsigned BRIEF/pending approval and missing Build-entry receipt; those are recorded, not bypassed by approval or opening build tickets during draft. No build, test, lint, formatting or smoke command was run by this planning assignment.

## Principles applied

- Experience First: maintainer setup, reviewed upgrades and required-PR failure behavior are first-class perspective outcomes, not implementation conveniences.
- Redesign From First Principles: one compiler command connects local use, coverage proof, CI and honest QA activation instead of parallel commands with drifting coverage.

## Remaining handoff

The host product lead owns the independent reader wave and four separate harness-simplify readers before signature; that pass was requested, not claimed executed here. All planned implementation verification remains future work. Open product questions: none.
