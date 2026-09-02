decisions:
  - id: D-08
    choice: |
      EXTENDS D-06 and supersedes nothing in it. D-06 says the agent resolves the feature-tree
      anchor itself with one Bash command. That route is unavailable to a persona holding no
      bash, so the rule becomes: a persona that holds no shell NEVER resolves its own anchor.
      Its DISPATCHER resolves it - every such persona is spawned by a tier that does hold bash -
      and passes the absolute value into the dispatch text as a line spelled exactly
      HARNESS-FEATURE-TREE-ROOT: /absolute/path
      on a line of its own, anywhere after the first. dispatch-guard.sh, the one hook that can
      see a dispatch prompt, refuses the dispatch at exit 2 when the DISPATCHED persona grants
      no bash in its .omp/agents entry and that line is absent, or is present and names a path
      other than the one inflight_registry.feature_root resolves for the declared feature. Every
      dispatch to a persona that does hold bash is unchanged, and D-06's self-resolution route
      remains the rule for all thirteen of them.

      The predicate is the TOOL GRANT, never a list of names. Measured at HEAD it binds exactly
      three personas - harness-product-lead, harness-eng-lead, harness-validator-lead - and a
      future persona that loses bash is covered on the day it loses it, with no edit here.
    because: |
      The gap is present tense, not hypothetical. .omp/agents/harness-product-lead.md:4-9,
      harness-eng-lead.md:4-9 and harness-validator-lead.md:4-9 grant read, glob, grep, task and
      write, and no bash, by DEC-116's design: a lead holds no shell so it cannot do a member's
      work. All three WRITE into a feature directory as their normal operation - harness-team
      SKILL.md:44-47 mandates the run dir features/<feat>/runs/<date>-<seq>-<squad>/state.yaml,
      SKILL.md:49-52 and :209-210 mandate the team digest at <run_dir>/digest.md, and :249 makes
      that digest the lead's reported artifact. Those spans are inside T-06's file list and
      T-14 clause 2 names runs/ explicitly among the spans it re-anchors to the feature-tree
      prefix. So after this plan lands, three of sixteen personas are bound to a write prefix
      whose only specified resolution route they cannot execute, and the failure is silent in
      exactly the way this feature exists to prevent: a lead that guesses writes the run record
      into the wrong checkout.

      REJECTED, granting the three leads bash. DEC-116 removes the shell deliberately, and
      re-granting it to repair a path-resolution defect is the same shape of error as widening a
      domain to repair one, which D-05 already refuses on this feature. It would also buy back a
      capability whose absence is load-bearing elsewhere: DEC-116 records that a lead sets
      cost: pending_orchestrator precisely because it cannot meter its own run.

      REJECTED, a second INJECTED value. D-06's measurement stands unreversed and no narrower
      injection exists: dispatch-guard.sh:76-80 records that tool_input.prompt reaches only the
      dispatch payload, and DEC-64 fixes the SubagentStart payload at agent_type, so the hook
      cannot know which feature a spawn belongs to. Nothing about a shell-less target changes
      what the hook can see.

      REJECTED, a no-shell resolution route the persona executes by hand. One exists on paper: a
      lead could glob <root>/.git/worktrees/*/gitdir, read each pointer and prefix-match the
      basenames. That is harness_boundary.linked_worktrees:157-182 and worktree_for_feature:
      193-229 - the pointer-file convention, the prefix-not-equality rule measured at
      :203-209, the AmbiguousWorktree refusal and the realpath normalisation - reimplemented as
      prose an agent executes by hand. Two implementations of one resolver diverge silently, and
      it writes git internals into an instruction. Rejected as strictly worse than passing the
      value the dispatcher already resolved correctly.

      REJECTED, the instruction half alone - telling the leads to return VERDICT BLOCKED when
      the line is absent. Kept as the agent-side half, rejected as the whole remedy: with no
      runtime enforcement the only available criterion asserts that a rule is written down,
      which cannot go red when a dispatcher simply omits the line.

      REJECTED, having the guard REWRITE the dispatch to insert the line. Nothing in this
      repository measures whether a PreToolUse hook can mutate tool_input, and D-06's own
      standard is that a mechanism is shown rather than asserted. Refusing loudly needs no
      capability the guard has not already demonstrated at exit 2.
    dec: DEC-116

tasks:
  - id: T-18
    title: dispatch-guard refuses a shell-less dispatch that carries no resolved feature-tree root
    traces: [REQ-06]
    change_type: logic
    execution_mode: main-session-direct
    execution_reason: DEC-174 carve-out, dispatch-guard.sh is a registered PreToolUse gate and test-dispatch-guard.py is its test file
    depends_on: [T-10]
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

  - id: T-19
    title: State the shell-less anchor route in the four skills that carry the dispatch and write contracts
    traces: [REQ-02, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve reports NOBODY for every harness skill SKILL.md
    depends_on: [T-12, T-13, T-14, T-18]
    status: ready
    files:
      - .claude/skills/harness-handoff/SKILL.md
      - .claude/skills/harness-team/SKILL.md
      - .claude/skills/harness-zero-micro-management/SKILL.md
      - .claude/skills/harness/SKILL.md
    verify: |
      python3 .agents/skills/harness/bin/check-instruction-paths.py \
        && python3 -c "import sys;t='HARNESS-FEATURE-TREE-ROOT';need={'.claude/skills/harness-handoff/SKILL.md':[t,'holds no shell'],'.claude/skills/harness-team/SKILL.md':[t,'HARNESS_FEATURE_TREE_ROOT'],'.claude/skills/harness-zero-micro-management/SKILL.md':[t,'holds no shell'],'.claude/skills/harness/SKILL.md':[t]};miss=[(f,n) for f,ns in need.items() for n in ns if n not in open(f).read()];print('missing',miss);sys.exit(0 if not miss else 1)"
    intent: |
      ADDS to what T-12 and T-14 write; supersedes one clause of T-12 and nothing else. This is
      the instruction half of D-08, and it lands in four files because the rule has two sides -
      who EMITS the line and who CONSUMES it - and each side has a general home and a squad home.

      SUPERSEDES T-12's second addition bullet, the one beginning "Resolve the second yourself,
      once, before your first feature-directory write." Everything else T-12 writes stands
      unchanged, including its correction of the receipt path and its two other bullets. That
      bullet becomes two sentences instead of one: the self-resolution instruction exactly as
      T-12 states it, followed by the exception - IF YOUR PERSONA HOLDS NO SHELL, spelled with
      the literal phrase "holds no shell", you do not run that command and must not try. Your
      dispatcher resolved the value for you and it is on a line of your own dispatch spelled
      HARNESS-FEATURE-TREE-ROOT: followed by one absolute path. If that line is absent from a
      dispatch to a shell-less persona, dispatch-guard.sh refuses the spawn at exit 2, so you
      will never be running without it - and if you somehow are, return VERDICT BLOCKED rather
      than guessing a root. Today this is the three leads and nobody else.

      harness-zero-micro-management/SKILL.md, the loop all three leads preload: extend the
      dispatch paragraph at :26-36, the one already stating the HARNESS-FEATURE first line, with
      the emit duty stated as a property of the target, never as a list of names - when you
      dispatch a persona that holds no shell, your dispatch must also carry the
      HARNESS-FEATURE-TREE-ROOT line with the absolute value, and the guard refuses it without.
      Add in the same place that you yourself received that value the same way.

      harness/SKILL.md, the orchestrator playbook: the same emit duty in the delegate step at
      :30-34, which already fixes the HARNESS-FEATURE first line. The orchestrator holds bash and
      spawns all three leads, so it is where the value is actually produced. Name the producing
      command once, in one backticked span, with the control-plane prefix on the script path.

      harness-team/SKILL.md, the run-dir section: after the run-dir block at :44-47 that T-14
      clause 2 re-anchors, add one sentence saying where the feature-tree value in that path
      comes from for a conductor that holds no shell - the dispatch line, not a command. Do not
      restate the path and do not touch T-14's anchoring of it.

      PATH DISCIPLINE, because T-11's checker runs over all four of these files. Any span naming
      an agent definition must be written <HARNESS_CONTROL_PLANE_ROOT>/.omp/agents/<persona>.md,
      and any script path likewise. A bare .omp/ or .claude/ token inside a backtick span or a
      fenced block is a VIOLATION under T-11 clause 1, and this task's own verify runs that
      checker over the whole scope first.

  - id: T-20
    title: Carry the emit duty into the four agent definitions that dispatch or receive it
    traces: [REQ-02, REQ-06]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: agent definitions are deliberately unowned, team-config.yaml line 53, and check-domain resolves them to NOBODY
    depends_on: [T-13, T-18]
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
      ADDS to T-13; supersedes nothing. Each of these four files already carries the paragraph
      that fixes the HARNESS-FEATURE first line - harness-orchestrator.md:53-59,
      harness-product-lead.md:56-66, harness-eng-lead.md:76-82, harness-validator-lead.md:53-59.
      The sibling rule belongs beside it, because that is where each persona reads what its own
      dispatches must contain.

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
      remedy D-08 rejects by name. Then run sync-agent-adapters.py so the four .claude/agents
      adapters regenerate, and never hand-edit those.

      PATH DISCIPLINE as in T-19: every .omp/, .claude/ or .harness/ token inside a backtick span
      takes <HARNESS_CONTROL_PLANE_ROOT>/, and any feature-directory path takes
      <HARNESS_FEATURE_TREE_ROOT>/. T-13 has already swept these files and T-11's checker reads
      them.
