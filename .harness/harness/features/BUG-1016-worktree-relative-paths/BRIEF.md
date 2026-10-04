# BRIEF — BUG-1016 Scope worktree relative paths

## Problem

Governed OMP agents inherit the parent checkout as cwd. Relative file-tool calls therefore read a different version from the assigned feature worktree, or create feature files in the main checkout: #1016 and #1570 observed differing read/Bash contents, and FEAT-43 B22 observed a stray feature directory. Repeating the read does not repair this checkout mismatch.

## Done when — by perspective

**operator** — I can rely on a governed agent's relative file-tool calls reaching its assigned feature worktree, including omitted-path searches and multi-file edits. Explicit destinations remain explicit, uncertain assignments refuse rather than guess, and my main-session tools behave as before.

**code maintainer** — I can find one documented adapter contract and regression cases covering every supported tool shape, without introducing a second worktree resolver or changing another host.

## Success criteria

- SC-01 (operator): For governed OMP calls to read, grep, glob, write, ast_grep and ast_edit, every nonempty relative filesystem path and every relative entry in a semicolon-separated path list is rooted in the unique assigned feature worktree. Non-path input and tool-specific selectors remain intact. Demonstrate new cases failing before production changes.
  verify: automated        evidence: unit
- SC-02 (operator): Each relative edit hashline section header and MV destination resolves in that worktree, including multiple sections and quoted destinations with spaces; hashes, operation lines, content and line endings remain intact. Both pre-write and post-write domain checks see the same effective file destinations the host executes. Demonstrate new cases failing first.
  verify: automated        evidence: unit
- SC-03 (operator): An absent or null path for grep, glob and ast_grep becomes the assigned worktree root; explicit empty or whitespace-only strings and list entries remain byte-for-byte unchanged, with separators preserved. Required path arguments on other tools are not invented. Demonstrate new omitted/null default-path cases failing first and retain explicit-blank passthrough controls.
  verify: automated        evidence: unit
- SC-04 (operator): Rewriting uses the governed run's existing HARNESS-FEATURE identity and the feature-root command backed by harness_boundary.worktree_for_feature, never a checkout path from dispatch prose, environment overrides or tool input. No matching worktree leaves input unchanged; ambiguous resolution refuses the call, as do resolver errors or unusable output. Existing claim-readiness and mutation authorization are not bypassed. Demonstrate new resolution/refusal cases failing first; preserve existing claim controls.
  verify: automated        evidence: unit
- SC-05 (operator): Absolute filesystem paths, leading-tilde paths and leading scheme:// destinations stay byte-for-byte unchanged. After rewriting, BUG-2003's write/edit URI policy still permits only agent:// and exactly xd://report_issue; other schemes/devices refuse by name, pre and post, and an allowed URI never exempts another target in a mixed edit. File-domain checks judge rewritten ordinary files and preserve refusals. Demonstrate a mixed relative-file/URI case failing first and retain existing URI regressions.
  verify: automated        evidence: unit
- SC-06 (operator): Successful rewriting is silent: no additional tool-result advisory or notification. Main-session and non-governed calls retain their inputs and default-path behavior; Bash retains its command, cwd and existing environment revision, with no feature-root rewrite lookup. Preserve existing controls and demonstrate the new governed rewrite path failing first.
  verify: automated        evidence: unit
- SC-07 (code maintainer): At the pinned review_sha, a new adapter decision in DECISIONS.md and its DECISIONS-INDEX.md row describe all seven tools, default paths, list entries, hashline/MV rewriting, the exact relative-filesystem predicate, silent behavior, claim/resolver authority, absent/ambiguous outcomes, URI policy, and unchanged main-session/Claude Code/Bash behavior. The production adapter and tests agree with that contract. Inspect git show <review_sha>:.harness/harness/docs/DECISIONS.md, git show <review_sha>:.harness/harness/docs/DECISIONS-INDEX.md, git show <review_sha>:.omp/extensions/harness-hooks.ts (registerHarnessHooks) and git show <review_sha>:tests/unit/omp-hooks.test.ts (OMP task lifecycle adapter).
  verify: inspection

## Verification gaps

- typecheck has no runner for TypeScript. The active unit runner discovers tests/unit/omp-hooks.test.ts through tests/unit/test-omp-hooks.py and executes the adapter behavior with Bun; review inspects the pinned TypeScript. This feature does not establish a typecheck runner. No criterion relies on a null test kind or requires operator UAT.

## Constraints

- DEC-174 BLOCKS team execution of enforcement changes: the OMP adapter and its co-changed tests are main-session-direct. All implementation edits stay in this feature worktree.
- DEC-250 SUPPLIES the existing exact runtime claim/lineage authority; an assignment identifies the feature but its checkout-path prose cannot authorize or select a destination.
- DEC-233 BLOCKS reintroducing Claude Code hosting: it does not host Harness agents, and this feature changes neither that host nor OMP itself.
- Existing harness_boundary.worktree_for_feature through inflight_registry.py feature-root SUPPLIES discovery. Reuse its short-name prefix matching and ambiguity refusal; do not create a second resolver.
- The existing tool_call revised-input channel SUPPLIES execution of the effective paths. Rewrite before file-domain policy, not just in its payload.
- Relative filesystem predicate: classify each path-list entry independently, judging the entry after trimming surrounding whitespace and removing one surrounding pair of double quotes (amended 2026-10-04 by the operator, validate R1). That target is relative when it is nonblank, node:path.isAbsolute is false, its first character is not ~, and it has no leading [A-Za-z][A-Za-z0-9+.-]*:// scheme. A rooted entry keeps its surrounding whitespace and quotes. Preserve explicit excluded entries verbatim, including empty/whitespace-only entries; preserve separator order and tool selector text. Only genuinely omitted/undefined/null paths default to the worktree root, and only for grep, glob and ast_grep.
- Rewriting is silent and lexical: no existence probe, symlink remapping, new traversal restriction or absolute-path relocation. Existing write guards still decide destination permission.
- A validated successful feature-root answer may be cached within its governed run only, isolated by run/feature/root authority and cleared at run boundaries. Failures and inferred roots are never cached; caching cannot introduce fallback or bypass claim-readiness, authorization or resolver refusal.
- BUG-2003's URI classification remains downstream of rewriting and unchanged, including its named refusals and mixed-target enforcement.

## Out of scope

- Bash cwd: agents already cd or use absolute paths; rewriting shell text is much riskier.
- Absolute-path remapping between checkouts.
- Changing OMP itself (a subagent inherits the parent cwd; src/task/executor.ts effectiveCwd = worktree ?? cwd).

## Approval

status: approved
approved-by: molchairuangutai
date: 2026-10-04
