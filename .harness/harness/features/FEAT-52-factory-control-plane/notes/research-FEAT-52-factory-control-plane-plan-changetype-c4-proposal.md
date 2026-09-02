schema: plan/1
feature: FEAT-52-factory-control-plane
status: plan
source_issues: [356]

lanes:
  resolved_at: e8e1b78be3379d4a669aa7e28aef8f76eb942471
  rows:
    - surface: .claude/skills/harness/bin/inject-expertise.sh
      lane: main-session-direct
      reason: DEC-174 carve-out, a registered SubagentStart hook and its test file
    - surface: .claude/skills/harness/bin/check-instruction-paths.py
      lane: main-session-direct
      reason: DEC-174 carve-out, a gate script joins the category on the day it becomes a gate
    - surface: .claude/skills/harness/bin/run-unit-tests.sh
      lane: main-session-direct
      reason: registering a gate test file is part of the same enforcement-layer edit
    - surface: .claude/skills/harness-handoff/SKILL.md
      lane: main-session-direct
      reason: check-domain resolves every harness skill SKILL.md to NOBODY
    - surface: .omp/agents/**
      lane: main-session-direct
      reason: agent definitions are deliberately unowned, team-config.yaml line 53
    - surface: .claude/agents/**
      lane: main-session-direct
      reason: generated compatibility output, equally unowned
    - surface: .github/workflows/tests.yml
      lane: main-session-direct
      reason: DEC-183, a gate cannot be wired into its own required job by a guarded run
    - surface: .harness/harness/docs/DECISIONS.md
      lane: team
      agent: harness-documentor

decisions:
  - id: D-01
    choice: "The Harness control-plane root reaches an agent as one line of the preamble that inject-expertise.sh injects through hookSpecificOutput.additionalContext, and it is the only value this feature injects."
    because: "It is the only registered SubagentStart hook, it already resolves the root from its own directory via harness_boundary.resolve_root, and DEC-100 measured that SubagentStart fires for nested spawns."
    rejected:
      - "An environment variable: CLAUDE_PROJECT_DIR is session-scoped and was measured UNSET in an agent tool shell, so an agent cannot anchor its own paths with it."
      - "Deriving the root from the working directory: a factory worker's cwd is the product checkout, which is the defect itself."
    dec: DEC-100
  - id: D-02
    choice: "The injected line is spelled HARNESS_CONTROL_PLANE_ROOT then a colon then the absolute path, and an instruction cites one of exactly two angle-bracket placeholder tokens followed by a slash - HARNESS_CONTROL_PLANE_ROOT for a read of a Harness-owned file and HARNESS_FEATURE_TREE_ROOT for a write into a feature directory."
    because: "Angle-bracket placeholders are the convention these same files already use for FEAT and for the agent name, so no new grammar is introduced, and one injected key plus one resolved key keeps the injected value and the cited tokens describing the same two directions."
    rejected:
      - "A dollar sigil: it would read as a shell variable that provably does not exist in the agent's shell."
    dec: none
  - id: D-03
    choice: "The lint is a standalone checker, check-instruction-paths.py, wired as a step of the required integration CI job rather than as an invariant inside check-state.sh."
    because: "check-state.sh audits per-feature state while this is a repo-wide instruction lint with its own scope list, a standalone script is runnable verbatim as a task verify command, and DEC-183 set the precedent for promoting a checker to a required CI step."
    rejected: []
    dec: DEC-183
  - id: D-04
    choice: "The spawn-time assertion lives inside inject-expertise.sh but signals through the injected text and stderr, never through the exit code, which stays 0 on every branch."
    because: "DECISIONS.md line 1503 and the script's own header fix its contract at always exits 0 so it can never block a spawn, and all seventeen existing cases assert exit 0, so the refusal happens one tier up at the agent, which is told to return VERDICT BLOCKED when the block says UNRESOLVED."
    rejected:
      - "Exiting non-zero on an unresolved root or on drift: it contradicts a signed contract and would let a hook block a spawn."
    dec: none
  - id: D-05
    choice: "Read-only access to Harness-owned skills needs no new grant in team-config.yaml, so the feature anchors the path and records the policy instead of widening any domain."
    because: "settings.json registers PreToolUse hooks only for Write and Edit, for Bash, and for Task and Agent, so no hook matches Read and nothing was denying the read - the only thing preventing it was that the relative path did not resolve."
    rejected:
      - "Widening a domain in team-config.yaml: it would widen WRITE permission as a side effect of fixing a resolution defect."
    dec: none
  - id: D-06
    choice: "Instruction paths carry TWO anchors: HARNESS_CONTROL_PLANE_ROOT, injected by inject-expertise.sh, prefixes every READ of a Harness-owned skill, rule, reference, decision or config, and HARNESS_FEATURE_TREE_ROOT, never injected, prefixes every WRITE into a feature directory and resolves to the checkout that HOLDS that feature's directory as inflight_registry.feature_root returns worktree_for_feature(owner_root, feature) or owner_root."
    because: "One value cannot serve both directions - measured at sha e8e1b78be3379d4a669aa7e28aef8f76eb942471, settings.json registers the MAIN checkout copy of inject-expertise.sh and harness_boundary.resolve_root is script-directory-relative, so the injected root is the main checkout whatever the agent's cwd and the FEAT-52 feature directory does not exist there at all, which sends a write anchored to it off the reviewed branch and invisible at review_sha, while leaving the write relative sends a factory worker's records into a disposable product workspace the next claim force-resets, which issue 356 comment 1 ruled against."
    rejected:
      - "Injecting a SECOND resolved value from inject-expertise.sh: the hook cannot identify the spawning agent's feature, because dispatch-guard.sh:76-80 records that tool_input.prompt exists only on the dispatch payload and DEC-64 fixes the SubagentStart payload's contract at agent_type, so it would have to scan the inflight registry of the control plane and of every linked worktree for a claim keyed on persona alone - ambiguous whenever two spawns of one non-single-flight persona run on different features at once - plus an unmeasured dependency on PreToolUse:Task firing before SubagentStart."
      - "Anchoring writes to the control-plane root: the feature tree is the one description true both for a Harness self-development run, where it is the feature worktree, and for a factory run, where the resolver collapses to the control plane because the product feature has no Harness worktree."
    dec: DEC-204
  - id: D-07
    choice: "The spawn-time assertion asserts the PATH CONTRACT rather than merely that a root resolved: inject-expertise.sh invokes check-instruction-paths.py over the four instruction files every harness agent receives - its own .omp/agents/<agent_type>.md and the three always-preloaded skills harness-handoff, harness-expertise and harness-principles - and reports the finding count plus up to five file:line pointers as a HARNESS_PATH_DRIFT line in the injected block, at exit 0 on every branch."
    because: "Root resolution cannot go red when a new relative path is introduced, which is the entire failure class a second mechanism is wanted against, and the hook already knows agent_type so that instruction set is knowable at spawn with no payload field the SubagentStart contract does not promise; the accepted cost is one extra subprocess per spawn on top of the interpreter-startup floor the hook already pays."
    rejected:
      - "Exiting non-zero on drift: it contradicts DECISIONS.md:1503 and the seventeen existing exit-0 cases, so the refusal stays the agent's."
      - "Re-implementing the lint's rule inside the hook: it would give the factory two rules free to drift apart, so the hook invokes the checker instead."
    dec: none
  - id: D-08
    choice: "The feature-tree anchor is resolved by whoever holds a shell: a persona whose .omp/agents entry grants bash resolves its own with inflight_registry.py feature-root --feature FEAT-NN-slug, and a persona that grants none never resolves its own but receives it from its dispatcher on a line of the dispatch text spelled HARNESS-FEATURE-TREE-ROOT then a colon then one absolute path, which dispatch-guard.sh refuses the dispatch without at exit 2, the predicate being the TOOL GRANT and never a list of names."
    because: "The gap is present tense - .omp/agents/harness-product-lead.md:4-9, harness-eng-lead.md:4-9 and harness-validator-lead.md:4-9 grant read, glob, grep, task and write and no bash by DEC-116's design, while all three WRITE into a feature directory as normal operation (harness-team SKILL.md:44-47 mandates the run dir, :49-52 and :209-210 the team digest, :249 makes that digest the lead's reported artifact), so three of sixteen personas would otherwise be bound to a write prefix whose only specified resolution route they cannot execute, and a lead that guesses writes the run record into the wrong checkout."
    rejected:
      - "Granting the three leads bash: DEC-116 removes the shell deliberately so a lead cannot do a member's work, and re-granting it to repair a path-resolution defect is the error shape D-05 already refuses; DEC-116 also records that a lead sets cost pending_orchestrator precisely because it cannot meter its own run."
      - "A second INJECTED value: nothing about a shell-less target changes what SubagentStart can see, and D-06's measurement stands unreversed."
      - "A no-shell resolution route the persona executes by hand: globbing the .git/worktrees pointer files and prefix-matching is harness_boundary.linked_worktrees:157-182 and worktree_for_feature:193-229 - the pointer convention, the prefix-not-equality rule at :203-209, the AmbiguousWorktree refusal and the realpath normalisation - reimplemented as prose, so two implementations of one resolver diverge silently."
      - "The instruction half alone, telling the leads to return VERDICT BLOCKED when the line is absent: kept as the agent-side half but rejected as the whole remedy, because with no runtime enforcement the only available criterion asserts that a rule is written down, which cannot go red when a dispatcher simply omits the line."
      - "Having the guard REWRITE the dispatch to insert the line: nothing in this repository measures whether a PreToolUse hook can mutate tool_input, and refusing loudly needs no capability the guard has not already demonstrated at exit 2."
    dec: DEC-116

tasks:
  - id: T-01
    title: Add the feature-root resolver verb the write anchor is defined by
    traces: [REQ-06]
    change_type: logic
    execution_mode: main-session-direct
    execution_reason: DEC-174 carve-out, inflight_registry.py is imported by dispatch-guard.sh, a registered PreToolUse hook
    depends_on: []
    status: ready
    files:
      - .claude/skills/harness/bin/inflight_registry.py
      - .claude/skills/harness/bin/test-inflight-registry.py
    verify: |
      python3 .agents/skills/harness/bin/test-inflight-registry.py
    intent: |
      The feature-tree write anchor is the checkout that HOLDS a feature's directory. That
      resolution already exists and is already used: inflight_registry.feature_root(owner_root,
      feature) at inflight_registry.py:260-266 returns worktree_for_feature(owner_root, feature)
      or owner_root, and dispatch-guard.sh:115-126 resolves a dispatch's checkout by the identical
      rule. What is missing is a way for an AGENT to ask.

      1. Add one verb to inflight_registry.py main(), beside list, attach, release, release-all and
         reconcile, in their exact shape:
           feature-root --feature FEAT-NN-slug
         Resolve the owner root through the existing _resolve_root, which honours --root and
         otherwise calls harness_boundary.resolve_root against this script's own directory. Print
         feature_root(root, feature) on one line and return 0. A missing --feature is the same
         one-line stderr message and return 1 the sibling verbs use, with nothing on stdout. Add
         the verb name to the usage string at the top of main(): a verb absent from usage is a verb
         nobody finds.

      2. Add cases to test-inflight-registry.py:
         - a temporary owner root carrying a linked worktree whose basename is FEAT-90-alpha: the
           verb prints that worktree's absolute path, and the case asserts the printed value
           DIFFERS from the owner root. That is the discriminating assertion, the one that goes
           red if the resolver ever answers with the control plane for a feature held elsewhere;
         - the same root with --feature FEAT-91-beta, for which no worktree exists: it prints the
           owner root, exit 0;
         - the short-form case worktree_for_feature already supports: a worktree named FEAT-90
           resolves --feature FEAT-90-alpha, because both spellings are legal input;
         - no --feature: return 1, a message naming the missing option, nothing on stdout.

      Do NOT register the test file anywhere new. test-inflight-registry.py is already in
      run-unit-tests.sh's INTEGRATION_SCRIPTS and already named in harness.json's
      test_kinds.integration.detect; adding it again trips the KIND-DRIFT cross-check.

  - id: T-02
    title: Add the check-instruction-paths.py lint over inline spans and fenced blocks, with a red-proving fixture
    traces: [REQ-04, REQ-06]
    change_type: logic
    execution_mode: main-session-direct
    execution_reason: DEC-174 carve-out, a new gate script and its test file are enforcement layer the moment the gate is wired
    depends_on: []
    status: ready
    files:
      - .claude/skills/harness/bin/check-instruction-paths.py
      - .claude/skills/harness/bin/test-check-instruction-paths.py
      - .claude/skills/harness/bin/run-unit-tests.sh
    verify: |
      python3 .agents/skills/harness/bin/test-check-instruction-paths.py
    intent: |
      Write a new checker and its test. The checker resolves its root the way every sibling does:
      harness_boundary.resolve_root against its own directory, never cwd, never the environment.

      SCOPE, computed by the checker, printed by --list-scope, one path per line, sorted:
        - every .omp/agents/*.md
        - every .claude/agents/*.md
        - every .claude/skills/harness-*/SKILL.md
        - .claude/skills/harness/SKILL.md and every .claude/skills/harness/references/*.md
        - every .claude/skills/harness/templates/*.md
      minus a module-level MAIN_SESSION_ONLY tuple, each entry carrying a one-clause reason as a
      comment: harness-init, harness-grilling, harness-wayfinding. Those three are run by the main
      session only and are never dispatched into a workspace. The templates directory is NOT
      exempt: templates/PLAN.md:9 and templates/README.md:8-16 carry relative control-plane paths
      and both reach harness-pm, which IS dispatched into a workspace.

      THE RULE. A violation is a path token matching ^\.(harness|claude|agents|omp)/ that appears
      EITHER inside a backtick-delimited inline span OR on any line inside a fenced code block, and
      that is not immediately preceded by <HARNESS_CONTROL_PLANE_ROOT>/ or by
      <HARNESS_FEATURE_TREE_ROOT>/. A fenced block opens on a line whose first non-space characters
      are three or more backticks or three or more tildes, with an optional info string, and closes
      on a line of at least as many of the SAME character. Inside a fence a token is delimited by
      whitespace, by a quote, or by the start or end of the line - never by backticks, which do not
      delimit anything there. A rule that saw only inline spans would be blind to
      harness-expertise/SKILL.md:36-37, which carries the observations write path inside a fence.

      THE SECOND VIOLATION CLASS, which is the enforcement half of D-06. A span or fenced token
      beginning with <HARNESS_CONTROL_PLANE_ROOT>/.harness/ then any segment then /features/ is
      ALSO a violation, reported as
        VIOLATION <path>:<lineno>: feature-directory path anchored to the control plane
      followed by the span. A feature directory belongs to the checkout that holds it, and
      anchoring it to the control plane sends a Harness self-development agent's receipt and
      observations off its own branch.

      REPORTING AND EXIT. One line per violation, VIOLATION <path>:<lineno>: <the span>. Exit 1
      when any violation is found, 0 when none. Exit 2 when the root cannot be resolved or the
      scope is EMPTY - an empty scan is indistinguishable from a clean tree and must never pass.

      ARGUMENTS. --list-scope prints the scope and exits 0. --root <dir> overrides the resolved
      root, for tests. Bare positional arguments, when given, restrict the scan: a FILE argument
      must itself be in the scope, and a DIRECTORY argument selects every scope file underneath it.
      An argument that selects nothing in the scope is exit 2 naming it, never a silent clean run.
      No arguments means the whole scope.

      Always print a final summary line "scanned N file(s), M violation(s)" so a caller can tell a
      broken scan from a clean one, the same reason check-plan-routes.py prints its count.

      TEST FILE, test-check-instruction-paths.py, following the sibling test scripts' plain-python
      case style and exiting non-zero on any failure:
        - RED PROOF, on BOTH shapes the rule must see: materialise a temp root whose scope file
          holds exactly TWO relative .harness/ instruction paths on two known lines, one inside a
          backtick-delimited inline span and one inside a fenced code block opened by three
          backticks. Assert exit status 1, assert stdout names that file AND EACH of the two line
          numbers separately, and assert the summary reports 2 violations. A fixture exercising
          only the inline shape leaves the fenced blind spot untested and green.
        - GREEN: the same fixture with both paths prefixed by <HARNESS_CONTROL_PLANE_ROOT>/ exits 0
          with 0 violations.
        - THE SECOND CLASS, two cases against a temp root: one scope file holding a single
          <HARNESS_CONTROL_PLANE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-<agent>.md
          span exits 1 and stdout names that file AND that line; the same fixture with
          <HARNESS_FEATURE_TREE_ROOT>/ in its place exits 0 with 0 violations.
        - EMPTY SCOPE: a temp root with no scope files exits 2, not 0.
        - SCOPE COMPLETENESS, five separate assertions against the real repository root, one per
          canonical site of BRIEF.md's S1 to S5 list and no substitution: --list-scope output
          contains each of
            .claude/skills/harness-qa-gate/SKILL.md
            .claude/skills/harness-expertise/SKILL.md
            .claude/skills/harness-handoff/SKILL.md
            .omp/agents/harness-backend-dev.md
            .claude/skills/harness/templates/PLAN.md
          Assert them individually, never by count.
        - EXEMPTIONS: --list-scope contains no path under harness-init, harness-grilling or
          harness-wayfinding.
        - A positional path outside the scope exits 2.

      REGISTRATION. Append "test-check-instruction-paths.py" to UNIT_SCRIPTS in run-unit-tests.sh.
      Do NOT add it to test_kinds.integration.detect in harness.json: the KIND-DRIFT cross-check
      fails when a UNIT_SCRIPTS name appears there, and unit.detect's glob
      .claude/skills/harness/bin/test-*.py already matches it.

      Do not run the checker over the live tree as part of this task's verify. It stays red until
      the anchoring work lands, and a verify asserting a by-construction red is unsatisfiable the
      moment that work is done; the whole-scope run is verified once, later, by the task that wires
      the CI step.

  - id: T-03
    title: Inject the control-plane root and the path-drift assertion into every harness agent's preamble
    traces: [REQ-01, REQ-04, REQ-05]
    change_type: logic
    execution_mode: main-session-direct
    execution_reason: DEC-174 carve-out, inject-expertise.sh is a registered SubagentStart hook and its test file is enforcement layer
    depends_on: [T-02]
    status: ready
    files:
      - .claude/skills/harness/bin/inject-expertise.sh
      - .claude/skills/harness/bin/test-inject-expertise.py
    verify: |
      python3 .agents/skills/harness/bin/test-inject-expertise.py
    intent: |
      inject-expertise.sh resolves the harness root today (variable `root`, from
      harness_boundary.resolve_root against the script's own bin directory) and uses it only to
      locate Expertise files. Carry that value to the AGENT, and assert the path contract while you
      are there.

      1. Emit a control-plane block as the FIRST thing in the body that is piped to `emit`, before
         any Expertise tier. Exactly this shape, three lines then a blank line:

             ## Harness control plane

             HARNESS_CONTROL_PLANE_ROOT: <the absolute resolved root>

             Every Harness-owned path in your instructions is written as
             <HARNESS_CONTROL_PLANE_ROOT>/... . Substitute the value above. It is absolute and it is
             NOT your working directory.

      2. Emit it UNCONDITIONALLY. `emit` currently drops an empty body, and an agent with no
         Expertise file at any of the three tiers therefore receives nothing at all. The block must
         arrive for that agent too, so the body is never empty for a matched harness agent.

      3. The unresolved branch. Where the script currently prints
         "no harness root resolved from ..." to stderr and exits 0, KEEP the stderr line, KEEP
         exit 0, and additionally emit a block reading:

             ## Harness control plane

             HARNESS_CONTROL_PLANE_ROOT: UNRESOLVED

             The control plane could not be located from this spawn. Do not guess a path and do not
             fall back to your working directory. Return VERDICT: BLOCKED naming the unresolved
             control-plane root.

         DO NOT make this branch exit non-zero. DECISIONS.md:1503 records this hook's contract as
         "always exits 0 so it can never block a spawn"; the refusal belongs to the agent, not to
         the hook. This is D-04.

      4. The non-harness agent filter at the `grep -Eq '^harness-[a-z0-9-]+$'` guard is unchanged:
         a non-matching agent_type still gets no injection and no error.

      5. THE PATH-DRIFT ASSERTION (D-07). After emitting the control-plane block and before any
         Expertise tier, scan the four instruction files every harness agent receives, resolved
         from the injected root and from agent_type so that no payload field beyond agent_type is
         needed:
           <root>/.omp/agents/<agent_type>.md
           <root>/.claude/skills/harness-handoff/SKILL.md
           <root>/.claude/skills/harness-expertise/SKILL.md
           <root>/.claude/skills/harness-principles/SKILL.md
         Apply the lint's OWN rule by INVOKING it, never by re-implementing it:
           python3 <root>/.claude/skills/harness/bin/check-instruction-paths.py <those four paths>
         A missing agent file is zero findings for that file, not a failure: a legitimately named
         but non-dispatchable agent has none.

         Emit into the injected block, immediately after the HARNESS_CONTROL_PLANE_ROOT line,
         either
           HARNESS_PATH_DRIFT: none
         or
           HARNESS_PATH_DRIFT: <n> unanchored path(s)
         followed by at most five lines, each two spaces then <file>:<line>, taken from the
         checker's VIOLATION lines, then one line telling the agent to treat an anchored-looking
         path in those files as unreliable and to say so in its DIGEST.

         EXIT STATUS STAYS 0 ON EVERY BRANCH, including a checker that exits 1, exits 2, or is
         absent. A checker that could not run emits HARNESS_PATH_DRIFT: unknown and nothing else.

      6. In test-inject-expertise.py add these cases, keeping every existing case passing:
         - a spawn with NO Expertise file at any tier still receives the block, and its first
           content line is `HARNESS_CONTROL_PLANE_ROOT: ` followed by an absolute path that is an
           existing directory. Run this case with the subprocess cwd set to a temporary directory
           that is NOT the resolved root, and assert BOTH that the injected value is an existing
           absolute directory AND that it DIFFERS from the cwd the hook was invoked in. A case in
           which the two coincide cannot fail for the reason this feature exists;
         - a spawn WITH a project-tier Expertise file receives the block BEFORE the Expertise
           heading (assert the byte offset of the control-plane heading is lower);
         - the unresolved branch: invoke a copy of the script placed where resolve_root cannot
           find a marker, assert exit status 0, assert stdout carries
           `HARNESS_CONTROL_PLANE_ROOT: UNRESOLVED`, and assert the string `VERDICT: BLOCKED`
           is present in the injected block;
         - a non-harness agent_type still produces no stdout and exit 0;
         - a fixture root whose .omp/agents/<agent>.md holds no relative Harness-owned path yields
           HARNESS_PATH_DRIFT: none, exit 0;
         - the SAME fixture with exactly one relative .harness/ span added at a known line yields
           HARNESS_PATH_DRIFT: 1 unanchored path(s) AND a line naming that file AND that exact
           line number, exit 0. This pair is the RED path, observed rather than assumed;
         - a fixture root with no check-instruction-paths.py yields HARNESS_PATH_DRIFT: unknown,
           exit 0.

  - id: T-04
    title: Anchor the four path families across the agent definitions and the four squad skills, by direction
    traces: [REQ-02, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: agent definitions and harness skill files both resolve to NOBODY under check-domain.sh
    depends_on: [T-02]
    status: ready
    files:
      - .omp/agents/**
      - .claude/agents/**
      - .claude/skills/harness-expertise/SKILL.md
      - .claude/skills/harness-qa-gate/SKILL.md
      - .claude/skills/harness-verification-rules/SKILL.md
      - .claude/skills/harness-tdd-enforcement/SKILL.md
    verify: |
      python3 .agents/skills/harness/bin/check-instruction-paths.py .omp/agents .claude/agents .claude/skills/harness-expertise/SKILL.md .claude/skills/harness-qa-gate/SKILL.md .claude/skills/harness-verification-rules/SKILL.md .claude/skills/harness-tdd-enforcement/SKILL.md \
        && python3 .agents/skills/harness/bin/sync-agent-adapters.py --check \
        && python3 -c "import sys;a='HARNESS_FEATURE_TREE_ROOT';pos=['.claude/skills/harness-expertise/SKILL.md','.claude/skills/harness-tdd-enforcement/SKILL.md','.omp/agents/harness-backend-dev.md'];miss=[f for f in pos if a not in open(f).read()];print('missing',miss);sys.exit(0 if not miss else 1)"
    intent: |
      Rewrite every backticked relative Harness-owned path in these files so it carries the anchor
      its DIRECTION requires. Change the PATH only. Do not reword the surrounding prose, do not
      renumber, do not restructure a table.

      THE DIRECTION RULE, which is D-06 and is not negotiable per family. A READ of a Harness-owned
      file takes <HARNESS_CONTROL_PLANE_ROOT>/. A WRITE into a feature directory - any path under
      .harness/<repo>/features/ - takes <HARNESS_FEATURE_TREE_ROOT>/, because measured at sha
      e8e1b78be3379d4a669aa7e28aef8f76eb942471 the SubagentStart hook is registered as the MAIN
      checkout's copy of the script, so the injected root is the main checkout even for an agent
      standing in a feature worktree, and that checkout does not hold the feature directory at all.
      Anchoring a write there sends it off the reviewed branch, invisible at review_sha.

      The four families, from issue 356 comment 2, with their direction and their known sites at
      that sha:
        F1 READ, .harness/harness.json - harness-qa-gate/SKILL.md lines 45 and 94,
           harness-verification-rules/SKILL.md line 28, harness-tdd-enforcement/SKILL.md line 106,
           and the agent files harness-ai-dev, harness-backend-dev, harness-data-engineer,
           harness-frontend-dev, harness-dev-ops. Becomes
           <HARNESS_CONTROL_PLANE_ROOT>/.harness/harness.json.
        F2 READ, .harness/expertise/<agent>.md - harness-expertise/SKILL.md lines 17 and 72, and
           the Expertise sentence in ALL 16 agent files. Becomes
           <HARNESS_CONTROL_PLANE_ROOT>/.harness/expertise/<agent>.md. The Expertise file is NOT
           inside a feature directory, so it keeps the control-plane anchor even though it is
           written under a distillation dispatch.
        F3 WRITE, the observations log. Becomes
           <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/observations/<agent>.md
           at harness-expertise/SKILL.md lines 16 and 37 and in every agent file that repeats it.
           Line 37 is INSIDE A FENCED BLOCK; anchor it by hand like any other occurrence.
        F4 WRITE, the receipt. Becomes
           <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-<agent>-<runid>.md
           at harness-tdd-enforcement/SKILL.md line 121 and anywhere else a file in this list
           spells it. The harness-handoff instance is not in this task's file list.

      Line numbers are an aid for that sha, not the definition. The DEFINITION is the checker's
      rule: after this task, no backticked span and no fenced token in these files begins with
      .harness/, .claude/, .agents/ or .omp/ unless it starts with one of the two placeholders, and
      no span anchors a feature-directory path to the control plane. Sweep with the checker rather
      than by the list, because the list came from a hand sweep and issue 356 records one instance
      introduced by an ordinary edit the same day. The debugging-skill read in the agent files is
      one of the spans the checker's rule matches, so it is anchored here too.

      The observations-merge invocation inside the fenced block becomes, on one line:
      python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/observations-merge.py apply --file <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/observations/<agent>.md
      Two anchors on one command line is the point, not a mistake: the SCRIPT is a read from the
      control plane and the --file argument is a write into the feature tree. Any plan-merge.py
      invocation in these files takes the same shape.

      Add ONE sentence to harness-expertise/SKILL.md, immediately after its first use of the
      feature-tree placeholder: that the value is resolved from the FEAT id on the first line of
      the dispatch, as harness-handoff states. Do not restate the resolving command here; one
      statement, one home.

      Edit .omp/agents/*.md and then regenerate the compatibility copies with
      `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/sync-agent-adapters.py --apply`.
      Do not hand-edit .claude/agents/*.md; they are generated output and the --check in the verify
      will catch a divergence.

  - id: T-05
    title: Give the silent fifth family its own treatment - skill reads from a product clone
    traces: [REQ-02, REQ-03]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: the five doer agent files, harness-eng-lead and the harness references are all NOBODY under check-domain.sh
    depends_on: [T-02, T-04]
    status: ready
    files:
      - .omp/agents/harness-ai-dev.md
      - .omp/agents/harness-backend-dev.md
      - .omp/agents/harness-data-engineer.md
      - .omp/agents/harness-frontend-dev.md
      - .omp/agents/harness-eng-lead.md
      - .claude/skills/harness/references/debug-mission.md
      - .claude/skills/harness-expertise/SKILL.md
      - .claude/skills/harness/bin/test-check-instruction-paths.py
    verify: |
      python3 .agents/skills/harness/bin/test-check-instruction-paths.py \
        && python3 .agents/skills/harness/bin/check-instruction-paths.py .omp/agents .claude/skills/harness/references/debug-mission.md .claude/skills/harness-expertise/SKILL.md \
        && python3 .agents/skills/harness/bin/sync-agent-adapters.py --check
    intent: |
      The fifth family fails DIFFERENTLY from the other four and needs a different answer. A doer
      dispatched into a product clone is told to read
      `.agents/skills/harness-systematic-debugging/SKILL.md`. FEAT-12 ended skill distribution, so
      products carry no harness skills: the file is simply absent, the read returns nothing, and the
      protocol never loads. No denial, no error, no transcript entry. The agent debugs without the
      discipline it was told to use.

      Anchoring alone is not the fix; anchoring PLUS an explicit read-through is. Do both.

      1. ANCHOR. In the five agent files at .omp/agents/harness-ai-dev.md,
         harness-backend-dev.md, harness-data-engineer.md, harness-frontend-dev.md and
         harness-eng-lead.md, and in .claude/skills/harness/references/debug-mission.md, the
         instruction must read
         <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness-systematic-debugging/SKILL.md.
         Same for harness-expertise/SKILL.md's pointer to
         .agents/skills/harness-distill/SKILL.md, which is the same shape - a skill read a product
         clone cannot satisfy. Regenerate with
         `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/sync-agent-adapters.py --apply`.

      2. STATE THE READ. Immediately after the anchored instruction in each of the five agent files,
         add one sentence: "That path is under the control-plane root, not your checkout. Reading it
         is permitted and read-only; your write grants are unchanged." The permission is settled -
         no hook matches Read in .claude/settings.json, so the read was never denied, only
         unresolvable. Do NOT add any grant to .harness/team-config.yaml. Widening a domain to fix a
         path-resolution defect would widen WRITE permission as a side effect, which is out of
         scope.

      3. PROVE THE READ. Add one case to test-check-instruction-paths.py named for this family:
         create a temp directory shaped like a product checkout, containing NO .agents and NO
         .claude directory, chdir into it, take the anchored instruction path as written in
         .omp/agents/harness-backend-dev.md, substitute the real repository root for
         <HARNESS_CONTROL_PLANE_ROOT>, and assert the resulting file opens and its first 200 bytes
         contain "harness-systematic-debugging". Then assert that the SAME instruction path with the
         placeholder stripped - the pre-change spelling - does NOT exist relative to that temp cwd.
         Both halves are required: the second is what makes the first discriminating.

  - id: T-06
    title: Sweep the remaining factory-reachable skills and the orchestrator playbook, by direction
    traces: [REQ-02, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: every harness skill file resolves to NOBODY under check-domain.sh
    depends_on: [T-02]
    status: ready
    files:
      - .claude/skills/harness/SKILL.md
      - .claude/skills/harness-brief/SKILL.md
      - .claude/skills/harness-code-review/SKILL.md
      - .claude/skills/harness-curate/SKILL.md
      - .claude/skills/harness-digest-dev/SKILL.md
      - .claude/skills/harness-distill/SKILL.md
      - .claude/skills/harness-principles/SKILL.md
      - .claude/skills/harness-review/SKILL.md
      - .claude/skills/harness-spec-driven/SKILL.md
      - .claude/skills/harness-team/SKILL.md
      - .claude/skills/harness-uat/SKILL.md
      - .claude/skills/harness-zero-micro-management/SKILL.md
    verify: |
      python3 .agents/skills/harness/bin/check-instruction-paths.py .claude/skills/harness/SKILL.md .claude/skills/harness-brief/SKILL.md .claude/skills/harness-code-review/SKILL.md .claude/skills/harness-curate/SKILL.md .claude/skills/harness-digest-dev/SKILL.md .claude/skills/harness-distill/SKILL.md .claude/skills/harness-principles/SKILL.md .claude/skills/harness-review/SKILL.md .claude/skills/harness-spec-driven/SKILL.md .claude/skills/harness-team/SKILL.md .claude/skills/harness-uat/SKILL.md .claude/skills/harness-zero-micro-management/SKILL.md \
        && python3 -c "import sys;a='HARNESS_FEATURE_TREE_ROOT';pos=['.claude/skills/harness/SKILL.md','.claude/skills/harness-team/SKILL.md','.claude/skills/harness-uat/SKILL.md','.claude/skills/harness-review/SKILL.md'];miss=[f for f in pos if a not in open(f).read()];print('missing',miss);sys.exit(0 if not miss else 1)"
    intent: |
      These are the scope files the agent-definition sweep and the fifth-family task do not cover.
      Each is preloaded into, or read on demand by, an agent the factory can dispatch: the
      orchestrator playbook, the product manager's two planning skills, the reviewers' and leads'
      rules, the distillation pair, and the universal principles rule.

      Change the PATH only, never the prose around it and never a table's structure. Every
      backticked span and every fenced token beginning .harness/, .claude/, .agents/ or .omp/ takes
      an anchor, and WHICH anchor is decided by direction (D-06):

      - A READ of a Harness-owned file takes <HARNESS_CONTROL_PLANE_ROOT>/. That is team-config.yaml,
        harness.json, the teams yaml files, the bin scripts, the templates directory, and every
        skill, rule and reference path.
      - A path naming anything inside a feature directory is a WRITE target and takes
        <HARNESS_FEATURE_TREE_ROOT>/: notes/, observations/, runs/, BRIEF.md, plan.yaml, STATE.md,
        DESIGN.md, uat-*.md, review-*.md, receipt-*.md, research-*.md and the feature directory
        itself. Anchoring one of those to the control plane is a violation the checker reports in
        its own right, because the injected root is the main checkout even for an agent standing in
        a feature worktree, so a write anchored there lands off the reviewed branch.

      Known counts of matching spans at sha e8e1b78be3379d4a669aa7e28aef8f76eb942471, as an aid and
      not as the definition: harness/SKILL.md 12 (of which 3 are feature-directory writes),
      harness-brief 6, harness-distill 4, harness-spec-driven 3, harness-team 3 (1 write),
      harness-code-review 2, harness-curate 2, harness-review 2 (1 write), harness-uat 2 (2
      writes), harness-digest-dev 1, harness-principles 1, harness-zero-micro-management 1. Sweep
      with the checker, not by the counts.

      Do NOT touch harness-init, harness-grilling or harness-wayfinding. They are run by the main
      session only, they are never dispatched into a workspace, and they are the checker's declared
      exemptions for that reason. Anchoring them would make the exemption list look decorative and
      would invite a later author to delete it.

      This task's verify runs the checker over exactly these twelve files and asserts that four of
      them carry a feature-tree anchor, which is the positive control: a sweep that anchored
      everything to the control plane would pass an absence check and fail this one.

  - id: T-07
    title: Anchor the seven templates, with the eight README spans pinned by direction
    traces: [REQ-02, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: templates resolve to NOBODY under check-domain.sh
    depends_on: [T-02]
    status: ready
    files:
      - .claude/skills/harness/templates/README.md
      - .claude/skills/harness/templates/PLAN.md
      - .claude/skills/harness/templates/BRIEF.md
      - .claude/skills/harness/templates/STATE.md
      - .claude/skills/harness/templates/DESIGN.md
      - .claude/skills/harness/templates/HANDOFF.md
      - .claude/skills/harness/templates/MAP.md
    verify: |
      python3 .agents/skills/harness/bin/check-instruction-paths.py .claude/skills/harness/templates \
        && python3 -c "import re,sys;r=open('.claude/skills/harness/templates/README.md').read();p=open('.claude/skills/harness/templates/PLAN.md').read();cp='<HARNESS_CONTROL_PLANE_ROOT>/';ft='<HARNESS_FEATURE_TREE_ROOT>/';reads=['.claude/settings.json','.harness/harness.json','.harness/team-config.yaml'];writes=['.harness/features/<FEAT>/BRIEF.md','.harness/features/<FEAT>/plan.yaml','.harness/features/<FEAT>/PLAN.md','.harness/features/<FEAT>/STATE.md','.harness/features/<FEAT>/DESIGN.md'];miss=[x for x in reads if cp+x not in r]+[x for x in writes if ft+x not in r];print('missing',miss);sys.exit(0 if not miss and cp+'.harness/team-config.yaml' in p else 1)"
    intent: |
      The templates are factory-reachable and were the one directory the first scope draft omitted:
      templates/PLAN.md:9 backticks .harness/team-config.yaml and templates/README.md:8-16 backticks
      eight paths the checker's rule matches, and harness-pm reads both. Anchor every backticked
      Harness-owned path in all seven template .md files, changing the PATH only and never the prose
      or a table's structure. At sha e8e1b78be3379d4a669aa7e28aef8f76eb942471 the other five files
      carry no matching span; the checker confirms that rather than your reading.

      Measured at that sha, README rows 8 to 16 carry EIGHT matching spans, not nine: the ninth
      backticked path on those rows is .gitignore, which the rule does not match because it is a
      file name and not a directory prefix. The direction split of the eight is pinned here so no
      one has to infer it.

      READS, taking <HARNESS_CONTROL_PLANE_ROOT>/:
        .claude/settings.json
        .harness/harness.json
        .harness/team-config.yaml

      FEATURE-DIRECTORY WRITES, taking <HARNESS_FEATURE_TREE_ROOT>/:
        .harness/features/<FEAT>/BRIEF.md
        .harness/features/<FEAT>/plan.yaml
        .harness/features/<FEAT>/PLAN.md
        .harness/features/<FEAT>/STATE.md
        .harness/features/<FEAT>/DESIGN.md

      Bare names with no directory component - settings.snippet.json, harness.json,
      team-config.yaml, BRIEF.md, plan.yaml, PLAN.md, STATE.md, DESIGN.md, gitignore.snippet,
      .gitignore, bin/merge-settings.py, bin/merge-gitignore.sh - are template FILENAMES in the
      left-hand column, not paths the rule matches. Leave them exactly as they are; prefixing a
      column of template names would make the table say something false.

      In templates/PLAN.md the only span the rule matches is .harness/team-config.yaml at line 9, a
      READ. Where its prose points at a file inside a feature directory, that pointer takes the
      feature-tree prefix.

  - id: T-08
    title: State both anchors, the read-only policy and the shell-less exception in harness-handoff
    traces: [REQ-02, REQ-03, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve reports NOBODY for every harness skill SKILL.md
    depends_on: [T-01, T-02, T-03]
    status: ready
    files:
      - .claude/skills/harness-handoff/SKILL.md
    verify: |
      python3 .agents/skills/harness/bin/check-instruction-paths.py .claude/skills/harness-handoff/SKILL.md \
        && python3 -c "import sys;s=open('.claude/skills/harness-handoff/SKILL.md').read();need=['HARNESS_CONTROL_PLANE_ROOT','HARNESS_FEATURE_TREE_ROOT','inflight_registry.py feature-root','read-only','holds no shell','HARNESS-FEATURE-TREE-ROOT'];miss=[n for n in need if n not in s];print('missing',miss);sys.exit(0 if not miss else 1)"
    intent: |
      harness-handoff/SKILL.md is preloaded into all 16 agents, so it is where the path contract has
      to live to bind everyone. Add ONE short section, and change nothing else about the skill's
      existing rules.

      Section title: "Harness-owned paths — anchored, never relative". Its content, as rules:

      - Your starting context carries a line `HARNESS_CONTROL_PLANE_ROOT: <absolute path>`. That
        directory is the Harness control plane. It is NOT your working directory, and in a factory
        dispatch it is a different repository from the one you are standing in. If that line says
        UNRESOLVED, return VERDICT: BLOCKED. Do not guess.
      - There are TWO anchors and they are not interchangeable. <HARNESS_CONTROL_PLANE_ROOT> is the
        control plane, injected into your starting context, and prefixes every READ of a
        Harness-owned skill, rule, reference, decision or config, written
        `<HARNESS_CONTROL_PLANE_ROOT>/.harness/...` or `<HARNESS_CONTROL_PLANE_ROOT>/.claude/...`.
        <HARNESS_FEATURE_TREE_ROOT> is the checkout that HOLDS your feature's directory, and
        prefixes every WRITE into it - your receipt, your observations log, your notes. Substitute
        the value before you read or write.
      - You MAY read anything under the control-plane root - skills, rules, references, decisions -
        read-only. Your WRITE grants are unchanged and are still resolved by check-domain.sh; the
        read permission widens nothing.
      - Resolve the second anchor yourself, once, before your first feature-directory write. Your
        FEAT id is the first line of your own dispatch (DEC-204) and the command is, in one
        backticked span:
        `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/inflight_registry.py feature-root --feature <FEAT>`
        It prints one absolute path. In a Harness self-development run that is your feature's
        worktree; in a factory run, where the feature has no Harness worktree, it is the control
        plane itself - correct, because a factory workspace is disposable and the next claim
        force-resets it.
      - THE EXCEPTION, and it is stated with the literal phrase "holds no shell": if your persona
        holds no shell you do not run that command and must not try. Your dispatcher resolved the
        value for you and it is on a line of your own dispatch spelled
        `HARNESS-FEATURE-TREE-ROOT: ` followed by one absolute path. dispatch-guard.sh refuses a
        dispatch to a shell-less persona without that line at exit 2, so you will never be running
        without it - and if you somehow are, return VERDICT BLOCKED rather than guessing a root.
        Today this is the three leads and nobody else.
      - The two values are OFTEN EQUAL, which is not a licence to use either. They differ exactly
        when the feature has its own checkout, which is when getting it wrong costs you the branch.
      - Never write a bare relative Harness-owned path into an instruction.
        check-instruction-paths.py rejects it, and in a product checkout it resolves against the
        product.

      Then fix this file's own paths. The receipt path, currently relative at line 80, becomes in
      one backticked span
      <HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md
      - a WRITE, so the feature-tree anchor, never the control-plane one. Apply the same treatment
      to every other feature-directory path this file spells, and the control-plane anchor to every
      read path in it. After this task the checker must exit 0 over this file, which means zero
      unanchored spans AND zero feature-directory paths anchored to the control plane.

  - id: T-09
    title: dispatch-guard refuses a shell-less dispatch that carries no resolved feature-tree root
    traces: [REQ-06]
    change_type: logic
    execution_mode: main-session-direct
    execution_reason: DEC-174 carve-out, dispatch-guard.sh is a registered PreToolUse gate and test-dispatch-guard.py is its test file
    depends_on: [T-01]
    status: ready
    files:
      - .claude/skills/harness/bin/dispatch-guard.sh
      - .claude/skills/harness/bin/test-dispatch-guard.py
    verify: |
      python3 .agents/skills/harness/bin/test-dispatch-guard.py
    intent: |
      This is the runtime half of D-08. It adds ONE block to dispatch-guard.sh and four cases to
      its test file. Nothing existing in either file is edited.

      WHERE. Immediately after the "if not root:" pass-through that ends at dispatch-guard.sh:138
      and before the runtime/supervisor_pid block that begins at :140, so it runs on every
      governed dispatch regardless of host runtime, and after both hb and reg are imported.

      WHAT IT DOES, in order, using the owner_root that hb.resolve_root already returns inside
      _root_for - resolve it once more the same way rather than reusing the worktree-specific
      root, because the agent definitions are authoritative in the control plane:

      1. Read the dispatched persona's tool grant from the file
         os.path.join(owner_root, ".omp", "agents", dispatched + ".md"). Parse only the YAML
         frontmatter list under the tools: key. If the file is missing, unreadable, or carries no
         tools: key, print one stderr line saying the tool grant for that persona could not be
         read and PASS THROUGH at the current exit path. That is the file's standing posture:
         only the missing-feature-line branch fails closed on our own failure.
      2. If the grant CONTAINS bash, do nothing further in this block. Thirteen of the sixteen
         personas take this path and their dispatches are byte-for-byte unaffected.
      3. If the grant does NOT contain bash, the dispatch must carry the anchor. Scan the prompt
         lines for the first whose text, stripped of surrounding whitespace, begins with the
         literal prefix "HARNESS-FEATURE-TREE-ROOT: ". The remainder is the declared root.
         - No such line: exit 2, with stderr saying that the dispatched persona holds no shell
           and therefore cannot resolve its own feature-tree write anchor, naming the persona,
           naming the required line spelled exactly, and naming the command that produces the
           value - inflight_registry.py feature-root --feature <the declared feature>.
         - A line whose value is not an absolute path: the same exit 2, saying the value must be
           absolute and quoting what was given.
      4. With a value present, compare it to the truth. Call reg.feature_root(owner_root,
         declared) inside try/except; on ANY exception print one stderr line and pass through -
         AmbiguousWorktree is a refusal the resolver owns, not one this block should convert.
         Compare os.path.realpath of both sides. Equal: continue to the existing runtime block.
         Different: exit 2, with stderr naming BOTH paths and saying the dispatch declared a
         feature-tree root the resolver does not agree with, which is a dispatcher that guessed.

      Use no apostrophe anywhere inside this block. The whole python program is one
      single-quoted shell argument and the file says so at :58-60.

      FOUR NEW CASES in test-dispatch-guard.py, each on its own throwaway root built by
      _checkout() and then given a .omp/agents/ directory, because _checkout() has none and the
      lookup would otherwise fail open and prove nothing. Materialise two minimal agent files in
      it: harness-product-lead.md whose frontmatter tools list is read, glob, grep, task, write,
      and harness-backend-dev.md whose list also carries bash. Both cases below dispatch from
      harness-orchestrator.

      - REFUSED: subagent_type harness-product-lead, prompt carrying the feature line and no
        tree-root line. Assert exit 2, assert stderr names harness-product-lead AND the literal
        HARNESS-FEATURE-TREE-ROOT. A bare non-zero is not the assertion - a crash on the way in
        is also non-zero.
      - ALLOWED: the same payload with a second line reading HARNESS-FEATURE-TREE-ROOT: followed
        by the value reg.feature_root returns for that root and feature. Assert exit 0.
      - DISCRIMINATION IN THE OTHER DIRECTION: subagent_type harness-backend-dev, the identical
        prompt with NO tree-root line. Assert exit 0. Without this case a guard that refuses
        every dispatch passes the first one.
      - MISMATCH REFUSED: harness-product-lead with a tree-root line naming an absolute path that
        is not the resolved root. Assert exit 2 and assert stderr contains BOTH the declared
        value and the resolved one.

      Register nothing new in run-unit-tests.sh: test-dispatch-guard.py is already in
      INTEGRATION_SCRIPTS, so the kind cross-check and the file-presence check both stay green.

  - id: T-10
    title: State the emit duty and the shell-less route in the playbook, the lead loop and the team skill
    traces: [REQ-02, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve reports NOBODY for every harness skill SKILL.md
    depends_on: [T-06, T-08, T-09]
    status: ready
    files:
      - .claude/skills/harness/SKILL.md
      - .claude/skills/harness-team/SKILL.md
      - .claude/skills/harness-zero-micro-management/SKILL.md
    verify: |
      python3 .agents/skills/harness/bin/check-instruction-paths.py .claude/skills/harness/SKILL.md .claude/skills/harness-team/SKILL.md .claude/skills/harness-zero-micro-management/SKILL.md \
        && python3 -c "import sys;t='HARNESS-FEATURE-TREE-ROOT';need={'.claude/skills/harness-team/SKILL.md':[t,'HARNESS_FEATURE_TREE_ROOT'],'.claude/skills/harness-zero-micro-management/SKILL.md':[t,'holds no shell'],'.claude/skills/harness/SKILL.md':[t,'feature-root']};miss=[(f,n) for f,ns in need.items() for n in ns if n not in open(f).read()];print('missing',miss);sys.exit(0 if not miss else 1)"
    intent: |
      This is the dispatcher-side half of D-08, and it lands in three files because the rule has
      two sides - who EMITS the resolved feature-tree value and who CONSUMES it - and each side has
      a general home and a squad home. The agent-facing statement for a shell-less persona already
      lives in harness-handoff; do not restate it here beyond what each file needs.

      harness-zero-micro-management/SKILL.md, the loop all three leads preload: extend the dispatch
      paragraph at :26-36, the one already stating the HARNESS-FEATURE first line, with the emit
      duty stated as a property of the TARGET and never as a list of names - when you dispatch a
      persona that holds no shell, your dispatch must also carry a line spelled
      `HARNESS-FEATURE-TREE-ROOT: ` followed by the absolute value, and dispatch-guard.sh refuses
      the dispatch at exit 2 without it. Add in the same place that you yourself hold no shell and
      received that value the same way, on a line of your own dispatch, and that an absent line is
      VERDICT BLOCKED rather than a guessed root.

      harness/SKILL.md, the orchestrator playbook: the same emit duty in the delegate step at
      :30-34, which already fixes the HARNESS-FEATURE first line. The orchestrator holds bash and
      spawns all three leads, so it is where the value is actually produced. Name the producing
      command once, in one backticked span, with the control-plane prefix on the script path:
      `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/inflight_registry.py feature-root --feature <FEAT>`
      Resolve it once per feature, not once per dispatch.

      harness-team/SKILL.md, the run-dir section: after the run-dir block at :44-47, add one
      sentence saying where the feature-tree value in that path comes from for a conductor that
      holds no shell - the dispatch line, not a command. Do not restate the path and do not change
      how it is anchored.

      PATH DISCIPLINE, because the checker runs over all three of these files in this task's own
      verify. Any span naming an agent definition is written
      <HARNESS_CONTROL_PLANE_ROOT>/.omp/agents/<persona>.md, any script path likewise, and any
      feature-directory path takes <HARNESS_FEATURE_TREE_ROOT>/. A bare .omp/, .claude/ or
      .harness/ token inside a backtick span or a fenced block is a violation.

  - id: T-11
    title: Carry the emit duty into the four agent definitions that dispatch or receive it
    traces: [REQ-02, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: agent definitions are deliberately unowned, team-config.yaml line 53, and check-domain resolves them to NOBODY
    depends_on: [T-04, T-09]
    status: ready
    files:
      - .omp/agents/harness-orchestrator.md
      - .omp/agents/harness-product-lead.md
      - .omp/agents/harness-eng-lead.md
      - .omp/agents/harness-validator-lead.md
      - .claude/agents/**
    verify: |
      python3 .agents/skills/harness/bin/sync-agent-adapters.py --check \
        && python3 -c "import sys;t='HARNESS-FEATURE-TREE-ROOT';n=['harness-orchestrator','harness-product-lead','harness-eng-lead','harness-validator-lead'];f=['.omp/agents/%s.md'%x for x in n]+['.claude/agents/%s.md'%x for x in n];miss=[p for p in f if t not in open(p).read()];print('missing',miss);sys.exit(0 if not miss else 1)"
    intent: |
      Each of these four files already carries the paragraph that fixes the HARNESS-FEATURE first
      line - harness-orchestrator.md:53-59, harness-product-lead.md:56-66,
      harness-eng-lead.md:76-82, harness-validator-lead.md:53-59. The sibling rule belongs beside
      it, because that is where each persona reads what its own dispatches must contain.

      In harness-orchestrator.md: you hold bash and every lead you spawn does not, so every
      dispatch you make to a lead carries a second line, HARNESS-FEATURE-TREE-ROOT: followed by
      the absolute path that
      `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/inflight_registry.py feature-root --feature <FEAT>`
      prints. Resolve it once per feature, not once per dispatch. dispatch-guard.sh refuses a
      dispatch to a shell-less persona without it at exit 2.

      In each of the three lead files: you hold no shell, so you never resolve that value
      yourself. It arrives on that line of your own dispatch and it is the prefix for every write
      you make into the feature directory, your run dir and your team digest included. If it is
      absent, return VERDICT BLOCKED; do not guess a root, because a run record written into the
      wrong checkout is invisible at review_sha. State the same emit duty for any persona YOU
      dispatch that holds no shell.

      One paragraph per file, placed immediately after the existing HARNESS-FEATURE paragraph.
      Change no frontmatter: this task grants no tool to anyone, and granting a lead bash is the
      remedy D-08 rejects by name. Then run
      `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/sync-agent-adapters.py --apply`
      so the four .claude/agents adapters regenerate, and never hand-edit those.

      PATH DISCIPLINE: every .omp/, .claude/ or .harness/ token inside a backtick span or a fenced
      block takes <HARNESS_CONTROL_PLANE_ROOT>/, and any feature-directory path takes
      <HARNESS_FEATURE_TREE_ROOT>/. These four files have already been swept once; do not
      reintroduce a relative span in the paragraph you add.

  - id: T-12
    title: Make the instruction lint a required CI check, with the wiring assertion proven red
    traces: [REQ-04]
    change_type: config
    execution_mode: main-session-direct
    execution_reason: DEC-183, a gate cannot be wired into the job that must protect it by a run that job guards
    depends_on: [T-04, T-05, T-06, T-07, T-08, T-10, T-11]
    status: ready
    files:
      - .github/workflows/tests.yml
      - .claude/skills/harness/bin/test-check-instruction-paths.py
    verify: |
      python3 .agents/skills/harness/bin/test-check-instruction-paths.py \
        && python3 .agents/skills/harness/bin/check-instruction-paths.py
    intent: |
      Add a step to the `integration` job in .github/workflows/tests.yml, immediately after the
      existing check-plan-routes.py step and written in its style, that runs
      `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/check-instruction-paths.py`
      - spelled in the workflow as the repository-relative path the other steps use, since a CI
      job runs at the repository root - and fails the job on a non-zero exit.

      Two failure modes must be distinguished in the step, exactly as the route-check step
      distinguishes them:
        - exit 1 means violations were found. Echo them as a GitHub error annotation and fail.
        - exit 2 means the checker COULD NOT RUN - unresolvable root, or an empty scope. Fail with a
          distinct annotation saying the scan did not happen, because an empty scan is
          indistinguishable from a clean tree and would pass forever.
      Also assert the summary line is present: if the step sees no `scanned N file(s)` line, it
      fails, because a checker that printed nothing cannot be read as clean.

      Then the committed assertion that the step exists, AND the proof that assertion can report
      RED. Write ONE function in test-check-instruction-paths.py taking a workflow-file PATH and
      returning the list of failures it found, checking three things separately: that the file
      contains the invocation check-instruction-paths.py, that the invocation appears inside the
      `integration:` job block and not another job, and that the block containing it also contains
      a non-zero-exit failure branch. Then:
        - call it on the real .github/workflows/tests.yml and assert it returns no failures;
        - materialise into a temp path a copy of that workflow with the check-instruction-paths.py
          step DELETED, call the function on it, and assert it returns a failure naming the missing
          invocation;
        - materialise a second copy with the step PRESENT but its non-zero-exit failure branch
          removed, call the function on it, and assert it returns a failure naming the missing
          failure branch.
      Two mutants, because the two halves fail independently: a deleted step and a step that runs
      the checker and ignores its exit code are different defects, and one mutant proves only one
      of them. An assertion never shown red is not evidence that the job can fail. The real
      workflow is read from the working tree; the mutants are temp files this test writes and
      removes. This is the precedent test-check-plan-routes.py case 25 set, plus the red proof it
      lacks.

      This task's verify is also the plan's whole-scope run: the checker with no arguments over the
      entire declared scope, which is green only once every anchoring task has landed. A non-zero
      exit here names the file and line of whatever was missed - read the VIOLATION lines rather
      than re-sweeping by hand.

  - id: T-13
    title: Record the two-anchor path contract as a decision
    traces: [REQ-01, REQ-02, REQ-03, REQ-06]
    change_type: docs
    execution_mode: team
    execution_agent: harness-documentor
    depends_on: [T-12]
    status: ready
    files:
      - .harness/harness/docs/DECISIONS.md
      - .harness/harness/docs/DECISIONS-INDEX.md
    verify: |
      python3 .agents/skills/harness/bin/gen-decisions-index.py --check \
        && python3 .agents/skills/harness/bin/test-gen-decisions-index.py
    intent: |
      Append ONE decision entry to DECISIONS.md - one entry, not two - taking the next free DEC
      number by reading the highest existing one, and write its index row in the SAME commit.

      THE RULING to record is TWO anchors, because one value cannot serve both directions:
        - the control-plane placeholder <HARNESS_CONTROL_PLANE_ROOT> is injected into every harness
          agent's preamble by the SubagentStart hook as the line
          `HARNESS_CONTROL_PLANE_ROOT: <absolute path>`, and prefixes every READ of a Harness-owned
          skill, rule, reference, decision or config;
        - the feature-tree placeholder <HARNESS_FEATURE_TREE_ROOT> is NOT injected, and prefixes
          every WRITE into a feature directory. A persona that holds a shell resolves it from the
          FEAT id on the first line of its own dispatch (DEC-204) with
          inflight_registry.py feature-root --feature FEAT-NN-slug, which returns
          worktree_for_feature(owner_root, feature) or owner_root: the checkout that HOLDS the
          feature directory. A persona that holds NO shell never resolves it - its dispatcher does,
          and passes it on a HARNESS-FEATURE-TREE-ROOT line of the dispatch, which dispatch-guard.sh
          refuses the dispatch without at exit 2. The predicate is the tool grant, never a name
          list, so a persona that loses its shell is covered on the day it loses it;
        - reading anything under the control-plane root is permitted and read-only, and no write
          grant is widened by it;
        - check-instruction-paths.py enforces both spellings over inline spans AND fenced code
          blocks, as a required step of the integration CI job, and reports a feature-directory path
          anchored to the control plane as a violation in its own right.

      THE REASONING, in four or five sentences and no more:
        - the defect: a relative path in prose resolves against the AGENT's working directory, and
          until the factory that was always the harness checkout;
        - why two anchors: measured at sha e8e1b78be3379d4a669aa7e28aef8f76eb942471, settings.json
          registers the MAIN checkout's copy of inject-expertise.sh and
          harness_boundary.resolve_root is script-directory-relative, so the injected root is the
          main checkout even for an agent standing in a feature worktree - anchoring writes there
          sends a Harness self-development agent's receipt and observations off the reviewed branch,
          while leaving them relative sends a factory worker's into a disposable product workspace
          the next claim force-resets, which issue 356 comment 1 ruled against;
        - why not an environment variable: CLAUDE_PROJECT_DIR is session-scoped and was measured
          UNSET in an agent's own tool shell, so an agent cannot anchor its own paths with it;
        - why the hook signals through text and not an exit code: its contract at
          DECISIONS.md:1503 is that it always exits 0 so it can never block a spawn, so the refusal
          is the agent's, which returns VERDICT: BLOCKED when the injected value reads UNRESOLVED;
        - the three severities the defect produced: a denied write is loud, a wrong read is silent
          and dangerous, and a missing skill read has no signal at all.

      Record the REJECTED alternatives and why, because a future scan will re-suggest both:
        - injecting a SECOND resolved value from inject-expertise.sh. The hook cannot identify the
          spawning agent's feature - dispatch-guard.sh:76-80 records that tool_input.prompt exists
          only on the dispatch payload and reaches no other hook, and DEC-64 fixes the
          SubagentStart payload's contract at agent_type - so it would have to scan the inflight
          registry of the control plane and of every linked worktree for a claim keyed on persona
          alone, ambiguous whenever two spawns of one non-single-flight persona run on different
          features at once;
        - granting the three shell-less leads bash. DEC-116 removes the shell deliberately so a
          lead cannot do a member's work, and re-granting it to repair a path-resolution defect
          would widen a capability to fix a resolution defect.

      Also record the spawn-time assertion in one sentence: the hook invokes the same checker over
      the four instruction files every agent receives - its own .omp/agents/<agent_type>.md and the
      three always-preloaded skills - and reports HARNESS_PATH_DRIFT in the injected block, still
      exiting 0 on every branch.

      Cite issue 356 and its five path families, and note that issue 357, the bin to src source
      location question, is neither upstream nor downstream of this.

      Write the index row's text after the ` :: ` yourself. gen-decisions-index.py regenerates the
      generated part of the row but never produces that ruling text, so regeneration alone will not
      satisfy the check. Run the generator after appending, so every later row's line anchor is
      corrected.
  - id: T-14
    title: Assert the shipped hook holds no non-zero exit, with a positive control
    traces: [REQ-05]
    change_type: logic
    execution_mode: main-session-direct
    execution_reason: DEC-174 carve-out, inject-expertise.sh is a registered SubagentStart hook and test-inject-expertise.py is its test file
    depends_on: [T-03]
    status: ready
    files:
      - .claude/skills/harness/bin/test-inject-expertise.py
    verify: |
      python3 .agents/skills/harness/bin/test-inject-expertise.py
    intent: |
      Add ONE case to test-inject-expertise.py that proves, by TEXT SCAN, that the shipped
      inject-expertise.sh contains no non-zero exit on any branch. This is the second clause of
      SC-02, and D-04 is the ruling it defends: the hook signals through injected text and stderr,
      never through the exit code, because DECISIONS.md:1503 fixes its contract at always exits 0
      so it can never block a spawn.

      1. THE PATTERN, exactly, as a POSIX extended regular expression:
           ^[[:space:]]*exit [1-9]
         Use it by invoking grep -E in a subprocess, which is where [[:space:]] is a valid POSIX
         character class. DO NOT hand this literal string to Python's re.compile: there
         [[:space:]] is a character set of the seven characters : s p a c e and [, so the pattern
         compiles cleanly and can never match the text it was written for - a pattern that cannot
         fail is the same defect class this case exists to catch. If you implement the scan in
         Python instead of grep, the translation is ^[ \t]*exit [1-9], and the positive control in
         step 3 is what proves the translation live rather than assumed.

      2. THE FILE, and the count. Scan the SHIPPED script, resolved from the repository the test
         itself lives in: the sibling of the test file's own directory, i.e.
         Path(__file__).resolve().parent / "inject-expertise.sh". Never a copy, never a fixture,
         never a path built from the process working directory. Assert the number of matching
         lines equals ZERO, as an integer count compared to 0 - not as a truthiness check on the
         output string, and not as "the output is empty". Distinguish an ERROR from an ABSENCE:
         grep exits 0 when it matched, 1 when it did not, and 2 or above when it could not read
         the file. Treat any status above 1 as a FAILURE of this case, never as zero matches.

      3. THE POSITIVE CONTROL, asserted in the SAME case. Materialise a temporary file whose
         ENTIRE content is the single line
           exit 2
         and run the SAME pattern through the SAME invocation shape against it. Assert it reports
         exactly ONE match. Remove the temp file afterwards. Without this half, a grep that
         errored, or a pattern that compiled to something unmatchable, is indistinguishable from a
         clean script - the absence reads as proof. This whole feature is about a check that must
         be able to report red, and it is the same defect class SC-05 exists to prevent on the
         lint.

      4. WHAT THIS CASE MUST NOT DO. It must not execute the hook: this is a text scan of the
         script's source, not a behavioural run, and running it proves nothing about branches that
         did not fire. It must not edit inject-expertise.sh. And it must not register the test file
         anywhere new - test-inject-expertise.py is already registered in run-unit-tests.sh and
         already named in harness.json's test_kinds detect, so adding it again trips the KIND-DRIFT
         cross-check. Keep every existing case in the file passing.
