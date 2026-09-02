# A plan-merge.py proposal, not prose. It carries the .md name because check-domain.sh grants
# harness-pm exactly `.harness/*/features/*/notes/research-*.md` under notes/, and a proposal is
# YAML that plan-merge.py reads by path regardless of extension. Applied to plan.yaml on
# 2026-09-01 with `plan-merge.py apply --file <plan.yaml> --proposal <this file>`.
#
# It carries ONLY new ids. No `approval:` mapping (plan-merge.py:537) and no `lanes:` block:
# lanes is not a UNION_KEY (plan-merge.py:98), so it falls to the every-other-key branch at
# plan-merge.py:614 and any differing value would exit 7 and refuse the whole apply.
schema: plan/1
feature: FEAT-51-claude-code-lifecycle-safety

decisions:
  - id: D-12
    choice: The Bash half of the quarantine boundary is a SECOND RULE inside the already registered plan-sign-gate.sh and plan-sign-gate.py, not a new PreToolUse Bash hook and not a check inside plan-merge.py itself
    because: it is the only candidate needing no .claude/settings.json entry and no new test-file registration, it inherits a tokenizer already hardened through five measured evasion classes, and a check inside plan-merge.py would sit inside the very tool that quarantine.py adopt delegates to under D-07, so adoption would have to be exempted from its own gate and the exemption would be the hole
    dec: DEC-174
  - id: D-13
    choice: The Bash rule bites on the four mutating plan-merge.py verbs AND on quarantine.py adopt, and it falls OPEN when the value of --file cannot be resolved to a canonical-artifact path
    because: adopt is the only other command that turns a quarantined file canonical, so REQ-05 is unreachable on this route without it, and failing open on an unresolvable value matches orphan_write's own fail-open on a missing registry and preserves the asserted control that an apply written with a shell variable as its --file value stays allowed
    dec: none
  - id: D-14
    choice: The quarantine rule reads the root plan-sign-gate.sh already resolves from its own directory through harness_boundary.resolve_root, the same root check-domain.sh resolves at its _root, and never a root derived from the command line
    because: the two routes must read ONE claims registry or an orphan quarantined at the Write gate could be allowed at the Bash gate for no reason a reader could see, and a root taken from the caller's own argument is a root the caller can choose
    dec: DEC-204

tasks:
  - id: T-07
    title: Close the Bash route by adding the quarantine rule to plan-sign-gate.sh and plan-sign-gate.py
    traces: [REQ-04, REQ-05]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: plan-sign-gate.sh is a registered PreToolUse Bash gate script, held back with the other gates by DEC-174 even though resolve answers harness-backend-dev
    depends_on: [T-02]
    status: ready
    files:
      - .claude/skills/harness/bin/plan-sign-gate.py
      - .claude/skills/harness/bin/plan-sign-gate.sh
      - .claude/skills/harness/bin/test-plan-sign-gate.py
    verify: |
      grep -q 'an orphan agent plan-merge apply on plan.yaml is quarantined' .agents/skills/harness/bin/test-plan-sign-gate.py &&
      grep -q 'an omp-runtime writer is never quarantined on the Bash route' .agents/skills/harness/bin/test-plan-sign-gate.py &&
      grep -q 'an orphan quarantine.py adopt onto a canonical plan.yaml is quarantined' .agents/skills/harness/bin/test-plan-sign-gate.py &&
      python3 .agents/skills/harness/bin/test-plan-sign-gate.py
    intent: |
      WHY THIS TASK EXISTS, in one measurement taken at
      ad93d43e1f232ec1ab87e08ccf70a01a08c206b7: .claude/settings.json registers
      check-domain.sh on PreToolUse for Write and Edit ONLY, at the matcher on :19. The
      PreToolUse Bash matcher on :27 runs branch-create-gate.sh, bash-write-guard.sh,
      gh-close-gate.sh and plan-sign-gate.sh, and check-domain.sh --post on :62 is a POST
      sweep. Since FEAT-41 reversed DEC-182, plan.yaml has exactly one writer,
      plan-merge.py, and it is invoked through Bash. So T-03's quarantine branch, which
      lives in check-domain.sh, covers BRIEF.md, feature.json and STATE.md and cannot reach
      plan.yaml at all. Issue 551's first measured occurrence is a fourteen-task plan.yaml
      replaced sixty-three seconds later by a one-task file, which is a plan.yaml write.
      This task puts the boundary on the route that write travels.

      WHAT FEAT-41 ALREADY BUYS, AND NOT MORE: plan-merge.py's locked union merge prevents
      the DELETION half, so an orphan can no longer shrink a fourteen-task plan to one. It
      does nothing for REQ-05. An orphaned child can still land NEW canonical plan content
      with no parent, no wake and no adoption, and apply prints APPLIED and exits 0.

      Every line number below was measured at ad93d43e. Re-read each anchor before editing
      and treat the quoted literals as the anchors.

      STEP ONE, THE TESTS, AND THEY GO FIRST. Add ONE new group at the foot of
      test-plan-sign-gate.py, after the HIGH-2 group that ends at :443 and BEFORE the
      summary print at :446. Do NOT modify ROOT at :54 or gate() at :57: gate() builds a
      payload with no session_id against a fixture root holding no registry file, so all
      twenty-eight existing cases fall through the new rule untouched. Confirm that by
      running them rather than assuming it. Add instead:

        _qroot(claims) - a throwaway root built exactly as _root() at :36 does, .harness
        holding harness.json and team-config.yaml, since resolve_root honours
        HARNESS_PROJECT_DIR only when .harness/team-config.yaml is readable underneath it.
        Then write each requested claim with inflight_registry.claim_with_receipt, imported
        from the bin directory the way test-inflight-registry.py already imports it.

        qgate(command, agent_type, session_id, root) - subprocess.run(["bash", GATE], ...)
        with HARNESS_PROJECT_DIR set to root and session_id carried in the payload.
        Returns (returncode, stderr), like gate().

      Use these exact label strings, because the task verify greps three of them:

        an orphan agent plan-merge apply on plan.yaml is quarantined
        an orphan set-task-station on plan.yaml is quarantined
        the writer own live claim allows the plan-merge apply
        a feature with no live claim allows the plan-merge apply
        an omp-runtime writer is never quarantined on the Bash route
        an orphan quarantine.py adopt onto a canonical plan.yaml is quarantined
        NEGATIVE CONTROL: an orphan apply on a non-canonical file path is allowed
        NEGATIVE CONTROL: a non-harness agent_type is not governed by the quarantine rule

      Assert exit codes EXACTLY, 2 or 0, and for each deny also assert the stderr names the
      quarantine path. The orphan fixture is the one T-02's case 29 uses: a live claim for
      the feature held by ANOTHER persona in ANOTHER session, runtime not omp. The
      not-orphan fixture is the writer's own live claim in its own session.

      PROVE THE GROUP DISCRIMINATES, and record the failing output in your receipt. GATE at
      :22 reads PLAN_SIGN_GATE_BIN. Copy the pre-change plan-sign-gate.sh and
      plan-sign-gate.py to plan-sign-gate.pre.sh and plan-sign-gate.pre.py INSIDE
      .claude/skills/harness/bin - not a temp directory, because the wrapper resolves its
      root from its own location and the python file imports its siblings - and change the
      single exec line of the .pre.sh to name plan-sign-gate.pre.py. Run the suite with
      PLAN_SIGN_GATE_BIN pointing at it, record that the new cases fail and the twenty-eight
      existing ones pass, then DELETE both copies.

      STEP TWO, THE RULE, in plan-sign-gate.py. Leave the sign-approval rule and every
      constant, helper and comment it owns behaviour-identical: VERB at :32, TOOL at :33,
      REASON at :50, the payload read at :64, the main-session exemption at :73, and OPS,
      SEP, MAX_DEPTH, RAW_SIGN, words(), is_tool(), as_bash_reads_it(), the INDIRECT rule
      and denies() at :256. Add beside them:

        MUTATING_VERBS = ("apply", "add-tasks", "set-task-station", "set-feature-station"),
        the four non-signing verbs of plan-merge.py's VERBS table at :932 of plan-merge.py,
        re-measured at ad93d43e. sign-approval is deliberately absent: it is already refused
        for every agent by the existing rule.

        ADOPT_TOOL = "quarantine.py", with the single verb adopt. discard is deliberately
        NOT covered - it removes a quarantine directory and can make nothing canonical - and
        list is read-only. Say so in a comment, because the omission must read as a choice.

        quarantines(line, agent, session, depth=0) -> a (rel, feature, quarantine_rel) tuple
        or None, mirroring denies()'s shape so the two rules read as siblings:

          1. line = as_bash_reads_it(line); toks = words(line). On None, meaning the line
             will not lex, RETURN None and fall open. State in a comment why there is no
             raw-text fallback here: this rule needs the VALUE of --file, and the text
             fallback cannot read an argument value through quoting. It is the same stated
             blind spot the module docstring already records for a tool name produced only
             by shell expansion, and the same posture as D-13.
          2. Find an invocation: an index i where _basename(toks[i]) at :224 equals TOOL and
             the next token, past a run of SEP exactly as denies() skips one at :291, is in
             MUTATING_VERBS; or _basename(toks[i]) equals ADOPT_TOOL and that next token is
             adopt. No match, and no eval or bash -c token to recurse into under MAX_DEPTH
             the way denies() does at :299, returns None.
          3. Read the value of --file from the tokens after i: the token following a literal
             --file, or the tail of a --file=VALUE token. Absent returns None.
          4. Normalise that value to a checkout-relative POSIX path by taking the tail from
             its LAST .harness/ segment. A value with no .harness/ segment returns None, and
             that is what keeps the existing controls at :150, :320 and :366 allowed - a bare
             --file p, a --file whose value is a shell variable, and a --file whose value is
             a command substitution. Those three are why the rule fails open here rather
             than closed.
          5. For a plan-merge.py verb, call _reg.canonical_artifact(rel); None returns None,
             otherwise the feature is its first element. For quarantine.py adopt the path
             points INTO the quarantine directory, which canonical_artifact returns None for
             by design, so match rel against
             ^\.harness/[^/]+/features/([^/]+)/quarantine/[^/]+/(.+)$ and require the
             trailing basename to be in _reg.CANONICAL_ARTIFACTS; anything else returns None,
             because T-04's adopt already exits 2 on an illegal basename.
          6. Return None unless _reg.orphan_write(ROOT, agent, feature, session) is True.
             ROOT at :35 is the root the wrapper resolved through
             harness_boundary.resolve_root from this script's own directory, which is the
             same root check-domain.sh resolves at its _root() on :154. That is D-14, and the
             reason both routes read one registry.

        Import inflight_registry INSIDE quarantines() and only AFTER step 2 has matched, in a
        try that on any exception writes one stderr line saying the quarantine boundary was
        not enforced and returns None. Two reasons, both load-bearing: failing OPEN on our
        own gap is the precedent every branch of check-domain.sh sets, and this hook runs
        ahead of EVERY Bash call in the session, so an unconditional import and registry read
        would be paid by every git status in the harness.

      Then, at the foot of the file, replace the single decision at :304 with two, the
      sign-approval rule FIRST:

        if denies(cmd): stderr REASON, exit 2, unchanged.
        else: _q = quarantines(cmd, agent, session); if _q is not None, stderr the quarantine
        refusal and exit 2.
        else: exit 0.

      agent is the agent_type already read at :73; the quarantine rule applies only when
      agent.startswith("harness-"), the same _governed test check-domain.sh states at :310,
      because registry personas are harness-*. A non-harness agent_type keeps its existing
      sign-approval refusal and is not reached by this rule. session is a NEW payload read,
      payload.get("session_id") on the payload parsed at :65. The order of the two rules is
      not observable, since sign-approval is not in MUTATING_VERBS, and is fixed so it cannot
      become so.

      The quarantine refusal is its own text, never REASON, and names four things: the
      canonical path refused, spelled as the checkout-relative rel; that this writer holds no
      live claim for that feature, so its parent is gone and a replacement may already be
      writing; the EXACT path from _reg.quarantine_rel(rel, agent, session) to write instead,
      or for an adopt call that adoption is the resumed parent's act and this caller is not
      it; and that a quarantined result becomes canonical only when a resumed parent runs
      quarantine.py adopt. Do not touch the registry, do not kill anything, and refuse
      nothing else.

      STEP THREE, plan-sign-gate.sh. Its header comment at :2 says this hook refuses one
      verb, and :16 says IT REFUSES ONE VERB, NOT THE TOOL. Both stop being true. Rewrite the
      header to state that this is the PreToolUse Bash gate for plan-merge.py and
      quarantine.py, carrying TWO rules - the unconditional sign-approval refusal under
      DEC-120, and the quarantine boundary for an orphaned governed writer under this
      feature's decision - and keep every other paragraph, including the stated blind spot,
      the stdin reasoning and the one-python3 reasoning. Change no code in the wrapper: it
      already resolves the root and already execs the .py with it. The file is NOT renamed:
      renaming it would require a .claude/settings.json edit and would strand the
      registration of test-plan-sign-gate.py, which is the whole cost D-12 chose this home to
      avoid.
