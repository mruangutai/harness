schema: plan/1
feature: FEAT-56-central-onboarding-model
decisions:
  - id: D-07
    choice: |
      Issue 206 is revised IN PLACE. No successor feature is created and no narrowed FEAT-56 is
      shipped; T-01 through T-08 stay done and nothing they delivered is reverted.
    because: |
      The operator ruled it on 2026-09-08 (notes/answers-rescope-2026-09-08.md item 1), overriding
      the advisor's SUCCEED recommendation. The engineering case agrees: the fifteen-file
      documentation inspection and the six executable-site sweep would otherwise be paid a second
      time over the same files, and a feature whose sole functional criterion is a failed uat cannot
      honestly be recorded as shipped.
    dec: none
  - id: D-08
    choice: |
      Onboarding becomes two artifacts along the seam the shipped file already carries. harness-init
      keeps its preflight, Track A and the --upgrade section and becomes only configure this harness
      checkout. A new skill harness-add-repo takes Track B minus steps 6, 7 and 8, the three-things
      opening paragraph and the one-file rule, and carries repository registration end to end with a
      preflight of its own.
    because: |
      The seam exists in the shipped file at SKILL.md:48 and :239 as of 12f74ea8, so the split reuses
      a boundary rather than cutting a new one, and the two jobs have disjoint preconditions: Track A
      runs once against an unconfigured checkout, Track B runs repeatedly against a configured one.
      Steps 6 to 8 leave entirely because they are the first BRIEF, its approval and the design pass,
      which are plan work rather than onboarding work (D-09).
    dec: DEC-220
  - id: D-09
    choice: |
      First-BRIEF, approval and design work leave onboarding altogether. A configured fleet
      repository that lacks its first BRIEF routes to /harness-plan, and neither onboarding artifact
      drafts a BRIEF, takes an approval or runs a design pass.
    because: |
      The operator ruled it (answers-rescope item 4), and the router already agrees where it was
      last corrected: commands/harness.md:14-17 sends a registered fleet member with an empty
      features directory to /harness-plan. The stale routes are elsewhere, measured at 12f74ea8:
      commands/harness-plan.md:18 and commands/harness-grilling.md:7 and :13. The approval-taking
      step inside onboarding also duplicated pm's own gate at a tier that cannot review a plan.
    dec: DEC-120
  - id: D-10
    choice: |
      harness-add-repo is a SKILL, and no command door is minted for it or for harness-init. DEC-06
      is NOT re-decided by this feature.
    because: |
      DEC-06's conclusion is that the runner is a skill rather than a command, and the new artifact
      conforms to it. DEC-06's stated premise, that harness-deploy distributes skills and agents but
      not the Claude command directory (DECISIONS.md:95-97), expired when deploy.sh and
      .claude/commands/harness-deploy.md were deleted in commit 45859123 for issue 259; no
      DECISIONS.md entry records that deletion, and DEC-113, which the earlier BRIEF cited for it,
      governs crew overrides rather than distribution. The conclusion survives on a different
      ground: a skill loads under every provider through the .agents/skills symlink today, while a
      command file is discovered by one provider's root only. So nothing signed is reversed, and the
      record of why is this entry.
    dec: DEC-06
  - id: D-11
    choice: |
      The canonical root for command doors is .omp/commands. The four doors are authored there, and
      .claude/commands holds generated adapters carrying a first-line banner naming the canonical
      file, produced and checked by bin/sync-command-adapters.py on the sync-agent-adapters.py
      pattern.
    because: |
      OMP reads slash commands from the config root's commands directory (omp://config-usage.md,
      scope-specific loading), and .omp/config.yml sets disabledProviders claude, so a door authored
      only under .claude/commands is discovered by Claude Code and by nothing else. A symlinked
      .claude/commands was considered and rejected: it cannot be shown to work here, because no test
      in this repository can exercise Claude Code's own discovery, whereas duplicated files with a
      diff-clean check are certain to work in both surfaces and their drift is caught mechanically.
      Commands carry no frontmatter, so the adapter is a copy plus a banner rather than a
      transformation.
    dec: none
tasks:
  - id: T-09
    title: Register harness-add-repo in MAIN_SESSION_ONLY, before the skill it names exists
    traces: [REQ-07]
    change_type: config
    execution_mode: team
    execution_agent: harness-dev-ops
    depends_on: []
    status: ready
    files:
      - .claude/skills/harness/bin/check-instruction-paths.py
    verify: |
      grep -q '"harness-add-repo"' .claude/skills/harness/bin/check-instruction-paths.py &&
      python3 .claude/skills/harness/bin/check-instruction-paths.py
    intent: |
      Add "harness-add-repo" to the MAIN_SESSION_ONLY tuple in
      .claude/skills/harness/bin/check-instruction-paths.py.

      THIS TASK LANDS BEFORE THE SKILL IT NAMES EXISTS, AND THAT ORDER IS DELIBERATE. _skill_docs
      builds its scan list from os.listdir, so a tuple entry whose directory does not exist yet is a
      no-op. The reverse order is not: the moment .claude/skills/harness-add-repo/SKILL.md exists
      without this entry, the anchor rule scans it, and check-instruction-paths.py, which
      check-state.sh runs at every door and before every commit, reddens on a tree that is otherwise
      correct. Do not wait for T-10.

      Edit the tuple only. Put the entry after "harness-init" and before "harness-grilling", with a
      trailing comment in the same form the two neighbours use, saying that it runs only in the main
      session. Do NOT copy harness-init's comment: its reason is the clone-relative core.hooksPath
      value the anchor rule would rewrite, which is not this skill's reason. Amend the block comment
      above the tuple so it states both reasons rather than only harness-init's.

      Verify the prefix predicate while you are here and record the result in your receipt: the
      comprehension filters on name.startswith("harness-"), so harness-add-repo is inside the
      globbed set and the tuple entry is what removes it. The dispatch that produced this task cited
      line 29 for that predicate; at 12f74ea8 it is at line 31. Cite what you measure.

      Touch nothing else in this file. The MAIN_SESSION_ONLY rationale correction for the central
      model shipped in T-02 and is not yours to revisit. Write no new test: the file's own exit 0 is
      the assertion, and T-17 adds the permanent split test.
  - id: T-10
    title: Create the harness-add-repo skill from Track B minus steps 6 to 8, with its own preflight
    traces: [REQ-07, REQ-08]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve on .claude/skills/harness-add-repo/SKILL.md returns NOBODY at 12f74ea8, a DEC-174 carve-out
    depends_on: [T-09]
    status: ready
    files:
      - .claude/skills/harness-add-repo/SKILL.md
    verify: |
      F=.claude/skills/harness-add-repo/SKILL.md &&
      test -f "$F" &&
      grep -q '^## Preflight' "$F" &&
      ! grep -q 'claude --version' "$F" &&
      ! grep -qF 'templates/team-config.yaml' "$F" &&
      ! grep -q 'The approval gate' "$F" &&
      ! grep -q 'then the BRIEF' "$F" &&
      ! grep -q 'Design pass' "$F" &&
      ! grep -q 'harness-visual-designer' "$F" &&
      grep -qF -- '--check-product-configs' "$F" &&
      DB=$(grep -niE 'default[ _-]branch' "$F" | head -1 | cut -d: -f1) &&
      FL=$(grep -nF 'factory/fleet.yaml' "$F" | head -1 | cut -d: -f1) &&
      SG=$(grep -nF '.harness/<segment>/' "$F" | head -1 | cut -d: -f1) &&
      test "$DB" -lt "$FL" && test "$FL" -lt "$SG" &&
      python3 .claude/skills/harness/bin/check-instruction-paths.py
    intent: |
      Create .claude/skills/harness-add-repo/SKILL.md: the instruction of record for registering a
      repository into an ALREADY CONFIGURED control plane. It is a skill, never a command (D-10).
      Source the content from .claude/skills/harness-init/SKILL.md at 12f74ea8, whose Track B this
      is; do not invent a second procedure, and do not edit harness-init in this task. T-11 owns the
      removal side, so the two files carry the same prose for one commit and that is expected.

      WHAT MOVES IN, by measured anchor at 12f74ea8:
      - the three-things opening paragraph and the one-file rule, SKILL.md:8-17;
      - Track B's step 2, land harness.json then register the repository, :245-283;
      - step 3, interview technical, :284-291;
      - step 4, delegate detection to dev-ops, :292-323;
      - the GitHub Issues mirror subsection, :350-363;
      - the project board subsection, :364-407.
      Renumber the steps 1, 2, 3 in that order and repoint every internal cross-reference: the
      phrases "through step 2" and "before step 2 lands the product config" both refer to what
      becomes step 1 here.

      WHAT DOES NOT MOVE IN, and this is the operator's ruling rather than a simplification (D-09):
      step 6 interview product then the BRIEF, step 7 the approval gate, step 8 design pass. They
      are dropped from onboarding entirely. In their place write one short closing section: the
      repository is registered, and its first BRIEF, that BRIEF's approval and any design pass are
      /harness-plan's work, reached by running /harness-plan against the registered repository. Name
      no visual-designer step and take no approval.

      ITS OWN PREFLIGHT, which does not exist anywhere today and is the reason this is not a copy.
      harness-init's preflight (:30-46) checks templates, the claude CLI version and a git repo,
      which is a FRESH CHECKOUT's preflight and is also provider-specific. Write a registration
      preflight, each item with its stop-or-continue consequence:
      - this control plane is configured: .harness/harness.json exists here and
        python3 .claude/skills/harness/bin/check-state.sh runs without reporting an unconfigured
        clone. If it is unconfigured, STOP and route to harness-init: registration into an
        unconfigured control plane produces artifacts nothing reads.
      - the templates directory is readable from here, the same test harness-init makes.
      - gh is installed and authenticated against the candidate repository, because step 1 lands a
        commit on its default branch and the mirror and board questions read it. If gh is absent,
        STOP: this procedure cannot complete without it.
      - the candidate repository's default branch is known, and you have push access to it.
      - the repository is not already in .harness/factory/fleet.yaml. If it is, this is a
        re-registration; say what to check instead of adding a duplicate entry.
      Do NOT check the claude CLI version or any other provider CLI: this skill must be executable
      under any provider, which is the operator's ruling (answers-rescope item 3), and the verify
      asserts the string claude --version is absent.

      Write frontmatter with name harness-add-repo and a description that says when to load it,
      adding a repository to an already-configured fleet, and that says nothing about configuring a
      checkout. Keep the run-in-the-main-session note and the interview-is-a-grilling note: the
      technical interview still needs AskUserQuestion. Keep the ordered central-model statement
      FIRST, in the order the config lands before the fleet entry before the central tree (D-04):
      the verify compares the first line number of each of the three markers and fails if they are
      out of order.

      Take exactly the Red flags rows that belong to registration, and leave the rest for T-11. By
      measured content at :419-434 the registration rows are: the team-config copy row, the
      repo-is-in-fleet.yaml row, the dev-ops-filled-the-cmd row, the npm-test row, the
      agent-got-blocked row, and the project-has-no-evals row. The prerequisite-install, hook and
      restart rows stay with harness-init. The describing-is-not-approving row and the
      check-state-says-pending row are dropped from both files, because neither artifact takes an
      approval any more (D-09).
  - id: T-11
    title: Cut harness-init back to a fresh-checkout procedure and resolve its dangling step references
    traces: [REQ-01, REQ-02, REQ-08]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve on .claude/skills/harness-init/SKILL.md returns NOBODY at 12f74ea8, a DEC-174 carve-out
    depends_on: [T-10]
    status: ready
    files:
      - .claude/skills/harness-init/SKILL.md
    verify: |
      F=.claude/skills/harness-init/SKILL.md &&
      ! grep -q 'Track A' "$F" &&
      ! grep -q 'Track B' "$F" &&
      ! grep -q 'factory/fleet.yaml' "$F" &&
      ! grep -q 'The approval gate' "$F" &&
      ! grep -q 'then the BRIEF' "$F" &&
      ! grep -q 'Design pass' "$F" &&
      ! grep -q 'harness-visual-designer' "$F" &&
      ! grep -qE 'step 2' "$F" &&
      grep -q 'harness-add-repo' "$F" &&
      grep -qF 'git config core.hooksPath .claude/skills/harness/hooks' "$F" &&
      grep -qF 'git config --get core.hooksPath' "$F" &&
      python3 tests/integration/test-hooks-install.py &&
      python3 .claude/skills/harness/bin/check-instruction-paths.py
    intent: |
      Cut .claude/skills/harness-init/SKILL.md down to what it now is: the first-time configuration
      of a fresh Harness checkout, and nothing else. T-10 has already created
      .claude/skills/harness-add-repo/SKILL.md holding the content you delete here; delete it, never
      move it, and do not edit the new file.

      DELETE, by measured anchor at 12f74ea8: the whole of Track B, SKILL.md:239 to :418, which is
      steps 2, 3 and 4, the GitHub Issues mirror subsection, the project board subsection, and steps
      6, 7 and 8. The registration half moved to harness-add-repo (T-10) and steps 6 to 8 are
      dropped from onboarding altogether (D-09).

      KEEP: the preflight at :30-46, step 1 at :53-160, step 5 at :161-184, step 9 at :185-208, and
      the --upgrade section at :209-238. PRESERVE VERBATIM, and this is a live assertion rather than
      a courtesy, the two command strings that read
        git config --get core.hooksPath || echo "(unset)"
        git config core.hooksPath .claude/skills/harness/hooks
      exactly as they appear. tests/integration/test-hooks-install.py reads them out of this file.

      RENUMBER the three surviving steps 1, 2, 3 and drop both Track headings: with one track there
      is nothing to distinguish, and a lone Track A heading is the dangling half of a pair.

      RESOLVE EVERY DANGLING STEP REFERENCE. Four sites cite a step 2 that leaves with Track B,
      measured at 12f74ea8: :65 "must exit 0 before step 2", :83 "Never skip to step 2", :156 "step
      2", and :212 inside --upgrade, "land its merged harness.json through step 2". The first three
      refer to the hard-gate ordering inside Track A and must be repointed at the surviving step
      numbers. The fourth is the one that now points outside this file: rewrite it to say that for a
      fleet member the merged harness.json lands through the harness-add-repo skill, naming that
      skill. The verify asserts that no occurrence of "step 2" survives, so a missed site fails the
      task.

      REWRITE the opening so it describes one job. The three-things paragraph and the one-file rule
      belong to registration and move out; in their place, state that this skill configures the
      harness checkout you are standing in, that registering a repository is the harness-add-repo
      skill's job, and that a configured fleet repository which has no BRIEF yet goes to
      /harness-plan (D-09). Update the frontmatter description the same way: it must not claim to
      onboard a repository. Keep the this-harness-checkout definition and the main-session note.

      SPLIT the Red flags table at :419-434 with T-10. Keep the prerequisite-install row, the
      script-was-denied row, the they-must-restart row and the they-can-run-a-team row. T-10 takes
      the registration rows. DROP the describing-is-not-approving row and the
      check-state-says-pending row from both files: neither artifact takes an approval any more, so
      both rows would be advice about work this skill no longer does.
  - id: T-12
    title: Repoint every main-session-owned instruction surface at the right one of the two artifacts
    traces: [REQ-03, REQ-04, REQ-08]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve returns NOBODY for all twelve paths at 12f74ea8, the DEC-174 carve-out covering .claude/commands and .claude/skills outside harness/bin
    depends_on: [T-11]
    status: ready
    files:
      - .claude/commands/harness.md
      - .claude/commands/harness-plan.md
      - .claude/commands/harness-ship.md
      - .claude/commands/harness-grilling.md
      - .claude/skills/harness-grilling/SKILL.md
      - .claude/skills/harness/templates/README.md
      - .claude/skills/harness/templates/harness.json
      - .claude/skills/harness/templates/team-config.yaml
      - .claude/skills/harness/templates/BRIEF.md
      - .claude/skills/harness/templates/PLAN.md
      - .claude/skills/harness/templates/DESIGN.md
      - .claude/skills/harness/references/github-mirror.md
    verify: |
      ! grep -q 'harness-init' .claude/commands/harness-plan.md &&
      ! grep -q 'harness-init' .claude/commands/harness-grilling.md &&
      ! grep -q 'harness-init' .claude/commands/harness-ship.md &&
      grep -q 'harness-add-repo' .claude/commands/harness.md &&
      grep -q 'harness-plan' .claude/commands/harness.md &&
      ! grep -q 'harness-init' .claude/skills/harness-grilling/SKILL.md &&
      grep -q 'harness-add-repo' .claude/skills/harness/templates/README.md &&
      grep -q 'harness-add-repo' .claude/skills/harness/templates/harness.json &&
      grep -q 'harness-add-repo' .claude/skills/harness/references/github-mirror.md &&
      grep -q 'harness-init' .claude/skills/harness/templates/team-config.yaml &&
      grep -q 'harness-plan' .claude/skills/harness/templates/BRIEF.md &&
      ! grep -q 'harness-init' .claude/skills/harness/templates/BRIEF.md &&
      grep -q 'harness-plan' .claude/skills/harness/templates/PLAN.md &&
      ! grep -q 'harness-init' .claude/skills/harness/templates/PLAN.md &&
      grep -q 'harness-plan' .claude/skills/harness/templates/DESIGN.md &&
      ! grep -q 'harness-init' .claude/skills/harness/templates/DESIGN.md &&
      python3 -c "import yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))" &&
      python3 -c "import json;json.load(open('.claude/skills/harness/templates/harness.json'))" &&
      python3 .claude/skills/harness/bin/check-instruction-paths.py
    intent: |
      Every file in this task names /harness-init for a job that is now split in two. Repoint each
      one at the artifact that actually does the job it describes. This is not a search and replace:
      one of the twelve KEEPS harness-init and the verify asserts it, so a blanket substitution
      fails the task.

      THE ROUTER, and re-derive before you edit. The dispatch chain claimed the stale BRIEF-missing
      route is at commands/harness.md:12. It is NOT: at 12f74ea8, harness.md:14-17 ALREADY routes a
      registered fleet member with an empty features directory to /harness-plan. What harness.md
      routes to /harness-init is the unconfigured-clone, unregistered-repo, unreadable-harness.json
      and missing-central-tree set, and after the split only the FIRST of those four is
      harness-init's. Split that condition: "no .harness/ here" goes to harness-init; "not in
      fleet.yaml", "config unreadable at the default branch" and "no central tree" go to
      harness-add-repo. Grep every one of the four command files for harness-init and fix what you
      find. The measured stale sites are harness-plan.md:18, "write it via pm if absent, or route to
      /harness-init per the Gate check", which must become /harness-plan per D-09; and
      harness-grilling.md:7 and :13, where grilling is called onboarding's interview and step zero of
      /harness-init. Grilling remains step zero of /harness-plan and is the interview behind
      harness-add-repo's technical questions; it is no longer inside an approval path. Apply the same
      correction to the one clause in .claude/skills/harness-grilling/SKILL.md:23 and to its
      frontmatter description at :4, which says step zero of /harness-plan and of onboarding.

      THE TEMPLATES, measured sites at 12f74ea8:
      - templates/README.md:3, :9-13, :22, :26, :30, :36, the instantiated-by column. Which artifact
        instantiates which file changes: settings.snippet.json, the control plane's own harness.json,
        team-config.yaml and gitignore.snippet stay harness-init; a fleet member's own harness.json
        becomes harness-add-repo; the BRIEF.md row becomes /harness-plan, because nothing in
        onboarding drafts a BRIEF any more (D-09). The step-4 cross-reference at :30 must name
        harness-add-repo and its new step number.
      - templates/harness.json:2 and :167, the _template text and the mirror _note. The control
        plane's own copy is harness-init's; a fleet member's copy and the sync-asked-once question
        are harness-add-repo's.
      - templates/team-config.yaml:3, KEEP harness-init. It is instantiated once, as the control
        plane's own, which is exactly Track A. Changing it would be wrong and the verify asserts the
        name survives here. Do not reflow the file: it has parsed as YAML only since issue 168 was
        fixed, and the verify reloads it.
      - templates/BRIEF.md:1, templates/PLAN.md:2, templates/DESIGN.md:6, all three name
        harness-init for BRIEF, plan or design work. All three become /harness-plan.
      - references/github-mirror.md:15 and :18, "at the registration step" becomes harness-add-repo's
        registration step.

      Change no line that does not name onboarding. In particular do not touch the domain globs in
      templates/team-config.yaml or any test_kinds value in templates/harness.json.
  - id: T-13
    title: Move the four command doors to the canonical neutral root and leave generated Claude adapters
    traces: [REQ-09]
    change_type: scaffolding
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve returns NOBODY for both .claude/commands and .omp/commands at 12f74ea8, a DEC-174 carve-out
    depends_on: [T-12]
    status: ready
    files:
      - .omp/commands/harness.md
      - .omp/commands/harness-plan.md
      - .omp/commands/harness-ship.md
      - .omp/commands/harness-grilling.md
      - .claude/commands/harness.md
      - .claude/commands/harness-plan.md
      - .claude/commands/harness-ship.md
      - .claude/commands/harness-grilling.md
    verify: |
      for d in harness harness-plan harness-ship harness-grilling; do
      test -f ".omp/commands/$d.md" || exit 1
      head -1 ".claude/commands/$d.md" | grep -q 'sync-command-adapters' || exit 1
      tail -n +2 ".claude/commands/$d.md" | cmp -s - ".omp/commands/$d.md" || exit 1
      done
      python3 tests/unit/test-no-distribution.py
    intent: |
      Re-home the four Harness command doors so OMP can discover them, and leave Claude Code's copies
      behind as generated adapters (D-11).

      WHY, measured at 12f74ea8 and not to be re-litigated: .omp/config.yml sets disabledProviders
      claude, which also drops every Claude-discovered command; .omp/commands does not exist;
      .omp/extensions/harness-hooks.ts registers no slash command. So /harness, /harness-plan,
      /harness-ship and /harness-grilling resolve under Claude Code only, and under OMP they fall
      through silently as prompt text. OMP reads slash commands from its config root's commands
      directory.

      DO, for each of harness, harness-plan, harness-ship and harness-grilling:
      1. Create .omp/commands/NAME.md holding the CURRENT content of .claude/commands/NAME.md byte
         for byte, including T-12's route corrections, which are already committed.
      2. Rewrite .claude/commands/NAME.md as an adapter: ONE first line, an HTML comment saying it is
         generated from .omp/commands/NAME.md, that it must not be edited, and that the repair is
         bin/sync-command-adapters.py --apply; then the canonical content verbatim from line 2 on.
         The verify strips line 1 and byte-compares the remainder, so a reflow, a trailing-newline
         change or a stray edit fails the task.
      Change no word of any door's prose in this task. T-12 owns the routing text and its commit is
      already in; this task moves bytes and adds one banner line per adapter.

      KEEP THE INTERMEDIATE TREE GREEN, which is why this task precedes the checker rather than
      following it. tests/unit/test-no-distribution.py counts harness*.md files under
      .claude/commands and requires at least four; the adapters keep that true. Nothing else in the
      tree reads either command directory at 12f74ea8, verified across tests, bin and the workflows,
      so no gate can redden between this task and T-14. Add no test here: T-14 owns the generator and
      the parity assertion, and T-17 owns the suite reconciliation.
  - id: T-14
    title: Add the command-adapter generator and make check-omp-port fail on a Claude-only door
    traces: [REQ-09, REQ-10]
    change_type: config
    execution_mode: team
    execution_agent: harness-dev-ops
    depends_on: [T-13]
    status: ready
    files:
      - .claude/skills/harness/bin/sync-command-adapters.py
      - .claude/skills/harness/bin/check-omp-port.py
      - tests/integration/test-sync-command-adapters.py
    verify: |
      python3 .claude/skills/harness/bin/sync-command-adapters.py --check &&
      python3 .claude/skills/harness/bin/check-omp-port.py &&
      python3 tests/integration/test-sync-command-adapters.py &&
      python3 tests/integration/test-check-omp-port.py
    intent: |
      Make the command-door port mechanically enforced, so a regression to a Claude-only door turns a
      gate RED instead of failing open as prompt text (REQ-10). T-13 has already created the four
      .omp/commands door files and rewritten the four .claude/commands files as banner-prefixed
      adapters; this task adds the tool and the assertion that keep them that way.

      1. .claude/skills/harness/bin/sync-command-adapters.py, modelled on the interface of
      bin/sync-agent-adapters.py in the same directory: --root defaulting to the resolved project
      root, --check and --apply, exit 0 on success and non-zero with a message on stderr naming the
      offending file. It is a COPY plus a banner, not a transformation, because commands carry no
      frontmatter. Behaviour:
      - The canonical set is .omp/commands/harness.md plus every .omp/commands/harness-*.md.
      - The expected adapter is one banner line, an HTML comment naming the canonical file and saying
        do not edit, run this script with --apply, followed by the canonical bytes.
      - --check compares each expected adapter against the file on disk and reports every mismatch,
        not just the first.
      - A .claude/commands/harness*.md file with NO canonical counterpart is an ERROR, not an extra
        to ignore. That case is the whole point: it is exactly a door authored Claude-only, which is
        the state at 12f74ea8, and a checker that tolerates it proves nothing.
      - --apply writes the adapters and prints what it changed.
      Resolve the project root the way its sibling does; do not add a second root resolver.

      2. .claude/skills/harness/bin/check-omp-port.py: add a command-door block beside the existing
      sync-agent-adapters invocation near the end of check(). Two independent assertions, because
      either alone is satisfiable by an empty tree. FIRST, each of the four door names has a real
      file at .omp/commands/NAME.md, asserted one name at a time and never by a count, appending one
      error per missing door naming it. SECOND, run sync-command-adapters.py --check as a subprocess
      exactly as the agent-adapter check does, and append its stderr as an error on non-zero. Do not
      touch the .omp/config.yml assertions, the agent roster, the provider overlays or the
      harness-hooks required-wiring set.

      3. tests/integration/test-sync-command-adapters.py, TEST FIRST, following the conventions of
      tests/integration/test-sync-agent-adapters.py exactly: the same sys.path preamble, the same
      check/FAILS/RAN accounting, the same temp-tree fixtures. It is integration because the
      directory selects the kind (DEC-213) and it drives the script over trees. Cases, all required:
      - a well-formed temp tree with a canonical door and its banner adapter: --check exits 0.
      - the adapter's body edited: --check exits non-zero and its message names that file.
      - the banner line missing: --check exits non-zero.
      - a .claude/commands/harness-orphan.md with no canonical counterpart: --check exits non-zero.
        THIS IS THE RED-CAPABILITY CASE the criterion rests on: it reproduces the pre-T-13 state,
        where all four doors were Claude-only. Record its output in your receipt.
      - --apply on a tree with a missing adapter creates it, and a following --check exits 0.
      Never point the test at the real repository root: build every case in a temp tree, or a case
      passes for the wrong reason.

      Then re-run tests/integration/test-check-omp-port.py and fix anything your new block breaks in
      it rather than weakening the block.
  - id: T-15
    title: Correct the two agent definitions that place detection and design inside onboarding
    traces: [REQ-04, REQ-08]
    change_type: docs
    execution_mode: main-session-direct
    execution_reason: check-domain.sh --resolve returns NOBODY for .omp/agents and .claude/agents at 12f74ea8, and the two trees are distinct files kept in step by sync-agent-adapters.py
    depends_on: [T-11]
    status: ready
    files:
      - .omp/agents/harness-dev-ops.md
      - .omp/agents/harness-visual-designer.md
      - .claude/agents/harness-dev-ops.md
      - .claude/agents/harness-visual-designer.md
    verify: |
      ! grep -q 'harness-init' .omp/agents/harness-dev-ops.md &&
      grep -q 'harness-add-repo' .omp/agents/harness-dev-ops.md &&
      ! grep -q 'harness-init' .omp/agents/harness-visual-designer.md &&
      grep -q 'harness-plan' .omp/agents/harness-visual-designer.md &&
      ! grep -q 'harness-init' .claude/agents/harness-dev-ops.md &&
      ! grep -q 'harness-init' .claude/agents/harness-visual-designer.md &&
      python3 .claude/skills/harness/bin/sync-agent-adapters.py --root . --check &&
      python3 .claude/skills/harness/bin/check-omp-port.py
    intent: |
      Two agent definitions tell their agent that its work happens during /harness-init. After the
      split one of those two jobs moved and the other left onboarding altogether.

      Edit the CANONICAL files under .omp/agents only, then regenerate the .claude/agents adapters
      with python3 .claude/skills/harness/bin/sync-agent-adapters.py --root . --apply. Do not
      hand-edit the .claude/agents copies: they are generated, check-omp-port.py runs --check on
      them, and a hand-edit reappears as staleness at the next regeneration.

      Measured sites at 12f74ea8:
      - .omp/agents/harness-dev-ops.md:53, "During /harness-init you determine what this project can
        actually run and write test_kinds". That is the detection step, which now lives in the
        harness-add-repo skill for a fleet member and in harness-init for this control plane's own
        harness.json. Say both, and name the skills rather than a slash command: neither is a command
        (D-10).
      - .omp/agents/harness-visual-designer.md:42, "Established during /harness-init's design pass".
        There is no design pass in onboarding any more (D-09). The DESIGN.md contract is established
        under /harness-plan, then extended as features need it. Rewrite the clause to say so.
      Change nothing else in either file: not the frontmatter, not the model alias, not
      autoloadSkills, not the HARNESS_AGENT_ID marker, all of which check-omp-port.py asserts.
  - id: T-16
    title: Document the two-artifact split and record its decision
    traces: [REQ-04, REQ-08, REQ-09]
    change_type: docs
    execution_mode: team
    execution_agent: harness-documentor
    depends_on: [T-11]
    status: ready
    files:
      - .harness/harness/docs/DECISIONS.md
      - .harness/harness/docs/DECISIONS-INDEX.md
      - .harness/harness/docs/SPEC.md
      - .harness/harness/docs/BUILD.md
      - .harness/harness/docs/org.html
      - README.md
      - .harness/README.md
    verify: |
      grep -q 'harness-add-repo' .harness/harness/docs/DECISIONS.md &&
      grep -q 'harness-add-repo' .harness/harness/docs/DECISIONS-INDEX.md &&
      grep -q 'harness-add-repo' .harness/harness/docs/SPEC.md &&
      grep -q 'harness-add-repo' .harness/harness/docs/BUILD.md &&
      grep -q 'harness-add-repo' .harness/harness/docs/org.html &&
      grep -q 'harness-add-repo' README.md &&
      grep -q 'harness-add-repo' .harness/README.md &&
      grep -q 'omp/commands' .harness/harness/docs/DECISIONS.md &&
      python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout | diff - .harness/harness/docs/DECISIONS-INDEX.md &&
      python3 tests/integration/test-gen-decisions-index.py &&
      python3 tests/integration/test-check-decision-anchors.py
    intent: |
      Record the split in the decision log and repoint the documentation surface at two artifacts.

      1. ONE new DECISIONS.md entry, appended after the current last entry, taking the next free
      DEC-NN. DEC-220 is the highest at 12f74ea8, so DEC-221 unless another feature has taken it, in
      which case take the next free number. Use the house form: Chose, Over, Because, Record with its
      refs. It must state all four of: onboarding is two artifacts, harness-init for first-time
      configuration of a harness checkout and the harness-add-repo skill for registering a repository
      into a configured control plane; the seam, Track A plus --upgrade stays and Track B minus its
      BRIEF, approval and design steps moves; that the first BRIEF, its approval and any design pass
      are /harness-plan's work and a configured fleet member without a BRIEF routes there; and that
      the canonical root for command doors is .omp/commands with generated .claude/commands adapters,
      because a door authored only under .claude/commands is discovered by one provider. Under Over,
      record that a symlinked .claude/commands was rejected because no test here can exercise Claude
      Code's own discovery. Refs DEC-220, DEC-06, DEC-120, DEC-174. Do NOT write DEC-06 as
      overturned: its conclusion is what the new skill conforms to, and its distribution premise
      expired when deploy.sh was deleted in commit 45859123. Say that in one clause.

      2. Regenerate the index with python3 .claude/skills/harness/bin/gen-decisions-index.py, then
      hand-write the row's ruling text after the double colon: gen-decisions-index.py does not
      produce that tail, so regeneration alone leaves the row without its summary, and the verify
      greps the index for the new skill name. Keep the row inside the word cap the neighbours obey.

      3. Repoint the documentation surface. Measured sites at 12f74ea8, and grep each file yourself
      for harness-init rather than trusting this list to be complete:
      - SPEC.md:84 the DESIGN.md row establishing it during /harness-init's design pass, :134
        onboarding is handled by /harness-init, :145 the not-onboarded classification row, :152 the
        schema_version row, and :406, :420, :457, :459, :483, :1363.
      - BUILD.md:104, :200, :370, :378, :389. These are historical task records. Do NOT rewrite
        history: where a line records what task 12 delivered, leave it, and add the present-tense
        correction where the document speaks about the current system. Say which you did in your
        receipt.
      - org.html, the owner cell and the doors table.
      - README.md:192 and .harness/README.md:6, :17, :18, :85.
      In every case the test is which of the two artifacts owns the job the sentence describes:
      configuring this checkout is harness-init, registering a repository is harness-add-repo, and a
      first BRIEF or a design pass is /harness-plan. Name the skills as skills; neither is a command.
      Do not un-slash the roughly twenty /harness-init spellings elsewhere in the corpus: that chore
      is a declared non-goal of this feature.
  - id: T-17
    title: Reconcile every test whose premise was one combined onboarding skill, and assert the split
    traces: [REQ-06, REQ-08]
    change_type: cross_module
    execution_mode: team
    execution_agent: harness-qa
    depends_on: [T-13, T-15]
    status: ready
    files:
      - tests/integration/test-onboarding-split.py
      - tests/unit/test-no-distribution.py
      - tests/integration/test-hooks-install.py
      - tests/integration/test-post-merge-sweep.py
      - tests/integration/test-layout-migration.py
    verify: |
      python3 tests/integration/test-onboarding-split.py &&
      python3 tests/unit/test-no-distribution.py &&
      python3 tests/integration/test-hooks-install.py &&
      python3 tests/integration/test-post-merge-sweep.py &&
      python3 tests/integration/test-layout-migration.py
    intent: |
      One new permanent test, and four existing files whose premise was ONE combined onboarding
      skill. This task is what makes SC-14 automated rather than an inspection.

      1. tests/integration/test-onboarding-split.py, new. Follow the conventions of
      tests/integration/test-hooks-install.py in the same directory: the same sys.path and root
      resolution preamble, the same check/FAILS/RAN accounting, one named case per claim. It asserts
      PER FILE AND PER TOKEN, never with one file-global search: a single search is satisfied by the
      conformers alone and is blind to the one file that conforms to nothing. Cases:
      - .claude/skills/harness-init/SKILL.md matches none of Track A, Track B, factory/fleet.yaml,
        The approval gate, then the BRIEF, Design pass, harness-visual-designer. One assertion per
        token, each naming its token in the failure message.
      - .claude/skills/harness-add-repo/SKILL.md exists, and matches none of The approval gate, then
        the BRIEF, Design pass, harness-visual-designer.
      - .claude/skills/harness-add-repo/SKILL.md matches all three central-model markers, a
        default_branch spelling, factory/fleet.yaml, and the central-tree segment path, and their
        FIRST occurrences are in that order. Compare line numbers: presence alone cannot see the
        ordering claim.
      - .claude/commands/harness-plan.md and .claude/commands/harness-grilling.md each match no
        harness-init, asserted separately per file.
      - .claude/skills/harness-add-repo/SKILL.md has a Preflight heading and does not match the
        string claude --version: the registration procedure must be executable under any provider.
      RED-CAPABILITY, and record it in your receipt: run this file against a temp copy of the
      pre-T-11 SKILL.md, taken from this feature branch's merge-base, and report which cases fail. A
      case that cannot fail is asserting nothing.

      2. tests/unit/test-no-distribution.py: case1_presence_four_other_command_doors_survive counts
      harness*.md under .claude/commands and requires at least four. After T-13 those four are
      generated adapters and the canonical doors are under .omp/commands. Amend the case to assert
      that the canonical root holds the four doors AND that the adapter root still holds four, one
      assertion each, and correct the comment above it, which explains the count in terms of a
      distribution sweep. Its TOKEN_RE sweep is unrelated: do not touch it.

      3. tests/integration/test-hooks-install.py: case_commands_verbatim_in_skill reads
      .claude/skills/harness-init/SKILL.md. Track A stays there, so the case survives; confirm it
      passes and re-anchor any line-number or step-number citation in its comments onto the new
      numbering. Do not weaken the verbatim assertion: T-11 preserves both command strings exactly
      because this case reads them.

      4. tests/integration/test-post-merge-sweep.py around :783-785 and
      tests/integration/test-layout-migration.py around :250-254 both cite a harness-init SKILL.md
      anchor or an onboarded-product fixture premise. Re-anchor each citation onto a HEADING rather
      than a line number, so the next renumbering cannot rot it, and state in your receipt which
      citations you moved and why each remains true.

      DELETE nothing without recording the reason in your receipt, and add no test that pins prose
      wording this feature removes: that rot mode is exactly what REQ-06 forbids.
