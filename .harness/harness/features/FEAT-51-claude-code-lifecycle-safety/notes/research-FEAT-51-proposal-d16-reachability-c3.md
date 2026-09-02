# A plan-merge.py proposal, not prose. It carries the .md name because check-domain.sh grants
# harness-pm exactly `.harness/*/features/*/notes/research-*.md` under notes/, and a proposal is
# YAML that plan-merge.py reads by path regardless of extension. Fix cycle 3, the D-16 defect.
#
# ONLY new ids: D-17 and T-09. No `approval:` mapping, no `lanes:` block and no `panel:` block,
# because none of those is a UNION_KEY and any differing value would exit 7 and refuse the whole
# apply. D-16's text, T-07's intent and T-07's verify are IMMUTABLE under the add-only merge, so
# the fix is an addition that supersedes two named clauses, following D-15's own precedent.
schema: plan/1
feature: FEAT-51-claude-code-lifecycle-safety

decisions:
  - id: D-17
    choice: T-09 owns the --dir branch of the Bash quarantine rule and T-07 does not, and this decision SUPERSEDES two clauses BY NAME which the add-only merge tool cannot edit in place. FIRST, D-16's clause reading "and T-07 is the task that implements it" no longer governs - the task that implements D-16's discard half is T-09, and a reader arriving at T-07 from D-16 must come here. SECOND, the sentence of T-07's immutable intent reading "discard is deliberately NOT covered - it removes a quarantine directory and can make nothing canonical - and list is read-only. Say so in a comment, because the omission must read as a choice." no longer governs either, so T-07 must NOT ship a comment asserting that discard is deliberately uncovered; T-09 corrects that comment if T-07 wrote it. Every other sentence of T-07's intent stands unchanged, T-07 still ships the adopt half and the three labels its own verify greps, and T-09 adds the --dir branch on top of the quarantines() rule T-07 creates. On the requirement footing, which D-16 leaves ambiguous and this decision settles - the --dir branch stands on REQ-05's SECOND sentence, that adoption and discard are BOTH explicit acts of a resumed parent and neither is a default nor a timeout, read together with REQ-04, whose remedy is that an orphan's canonical write is quarantined rather than lost. D-16's because calls REQ-05 untouched on the ground that discard makes nothing canonical, and that is true of REQ-05's FIRST sentence only; the branch does not rest on that sentence. It rests on the second one, and on issue 280's acceptance boundary that a completed child's analysis stays RECOVERABLE, which an orphan's discard destroys. T-09 therefore traces REQ-04 and REQ-05, and the decision record's DEC-209 entry already names adopt AND discard on the Bash half under D-15
    because: as the plan stood, D-16 named T-07 as its implementer while T-07's immutable intent directed the opposite comment and T-07's verify greps only three adopt-era labels, so T-07 alone would have shipped discard UNCOVERED plus a code comment asserting the omission was deliberate, D-16 would have gone undelivered, T-07's own verify would still have passed, and every gate would have stayed green over a decision the plan made and did not build; D-15 already supersedes two bullets of T-06's immutable intent by name, so this follows the file's own precedent rather than inventing a second mechanism, and an addition is the ONLY route available because plan-merge.py apply is add-only and exits 7 on any proposal that changes D-16's or T-07's existing text
    dec: DEC-209

tasks:
  - id: T-09
    title: Add the discard branch to the Bash quarantine rule so an orphan cannot destroy a quarantined result
    traces: [REQ-04, REQ-05]
    change_type: cross_module
    execution_mode: main-session-direct
    execution_reason: plan-sign-gate.sh is a registered PreToolUse Bash gate script, held back with the other gates by DEC-174 even though resolve answers harness-backend-dev
    depends_on: [T-07]
    status: ready
    files:
      - .claude/skills/harness/bin/plan-sign-gate.py
      - .claude/skills/harness/bin/plan-sign-gate.sh
      - .claude/skills/harness/bin/test-plan-sign-gate.py
    verify: |
      grep -q 'an orphan quarantine.py discard of a quarantine directory is refused' .agents/skills/harness/bin/test-plan-sign-gate.py &&
      grep -q 'NEGATIVE CONTROL: the writer own live claim allows the quarantine.py discard' .agents/skills/harness/bin/test-plan-sign-gate.py &&
      grep -q 'NEGATIVE CONTROL: an orphan discard of a directory outside a quarantine segment is allowed' .agents/skills/harness/bin/test-plan-sign-gate.py &&
      python3 .agents/skills/harness/bin/test-plan-sign-gate.py
    intent: |
      THE ANCHORS AND THE SHA. Every line number and quoted literal below was measured from the
      MAIN checkout at ad93d43e1f232ec1ab87e08ccf70a01a08c206b7, the sha this plan's lanes block
      resolves at. The main checkout's HEAD has since moved to a7569463, the FEAT-41 ship merge,
      and git diff --stat ad93d43e a7569463 over plan-sign-gate.py, plan-sign-gate.sh,
      test-plan-sign-gate.py and inflight_registry.py is EMPTY, so every anchor below holds at
      both shas. Re-read each anchor before editing and treat the quoted literals as the
      anchors, never the numbers.

      WHY THIS TASK EXISTS, AND WHAT D-17 MOVED. D-16 chose to cover quarantine.py discard on
      the Bash route and named T-07 as its implementer, while T-07's immutable intent directs
      the OPPOSITE - a comment saying discard is deliberately not covered - and T-07's verify
      greps only the three adopt-era labels. T-07 alone therefore ships discard uncovered, with
      a comment asserting the omission is a choice, and its own verify still passes. D-17 moves
      the --dir branch here. This task runs AFTER T-07 and edits the rule T-07 creates in the
      same two files, which is what depends_on T-07 pins - the two must never be handed out as
      concurrent edits to one region.

      STEP ZERO, ONE COMMENT IN T-07'S OWN WORK. Under D-17 the sentence of T-07's intent
      directing the deliberately-not-covered comment for ADOPT_TOOL no longer governs. If T-07
      wrote that comment, CORRECT it here rather than leaving it beside a branch that
      contradicts it. The comment must say that list is read-only and therefore not covered,
      and that discard IS covered, by the --dir branch below, under this feature's decision. A
      shipped comment asserting an omission that is not an omission is the defect D-17 exists
      to close and it must not survive this task.

      STEP ONE, THE TESTS, AND THEY GO FIRST. Add ONE new group at the foot of
      test-plan-sign-gate.py, AFTER the group T-07 adds and BEFORE the summary line, which is
      the literal print(f"\n{fails} failing." - measured at :446 at ad93d43e, with the
      SystemExit at :447, and T-07's own group lands above it, so anchor on the literal and not
      on the number.

      REUSE T-07'S FIXTURE HELPERS, do not define a second pair. T-07 adds _qroot(claims), a
      throwaway root built as _root() at :36 does with .harness holding harness.json and
      team-config.yaml, and qgate(command, agent_type, session_id, root) returning
      (returncode, stderr) with HARNESS_PROJECT_DIR set to root and session_id carried in the
      payload. Use those. Do NOT modify ROOT at :54, gate() at :57, or any of the twenty-eight
      pre-existing cases - gate() builds a payload with no session_id against a fixture root
      holding no registry file, so they all fall through the new branch untouched. Confirm that
      by running them rather than assuming it: at ad93d43e the suite prints 45 ok lines, 0 FAIL
      lines and exits 0.

      Use these exact label strings. The task verify greps the first three, so a typo in any of
      them is a red verify on correct work:

        an orphan quarantine.py discard of a quarantine directory is refused
        NEGATIVE CONTROL: the writer own live claim allows the quarantine.py discard
        NEGATIVE CONTROL: an orphan discard of a directory outside a quarantine segment is allowed
        an omp-runtime writer is never quarantined on the discard branch
        a feature with no live claim allows the quarantine.py discard
        NEGATIVE CONTROL: an orphan discard whose --dir value is a shell variable is allowed
        NEGATIVE CONTROL: an orphan quarantine.py list is never denied

      The first label is the string D-16 pins verbatim; it is not yours to reword. Assert exit
      codes EXACTLY, 2 or 0. The orphan fixture is the one T-02's case 29 uses - a live claim
      for the feature held by ANOTHER persona in ANOTHER session, runtime not omp. The
      not-orphan fixture is the writer's own live claim in its own session. The omp fixture is
      T-02's case 33, runtime omp with a live supervisor pid.

      The refusing case carries TWO further assertions beyond its exit code, each its own
      check() call with its own detail string, because a combined condition is satisfied by the
      half that holds: the stderr says that discarding a quarantined result is the resumed
      parent's act and this caller is not it, AND the stderr does NOT name a quarantine path to
      write instead. The second is D-16's own wording rule - there is no path to advise when
      the refused act is a removal - and without it the branch could ship the adopt refusal
      text and read as covered.

      PROVE THE GROUP DISCRIMINATES and record the failing output. GATE at :22 reads
      PLAN_SIGN_GATE_BIN. Copy the pre-change plan-sign-gate.sh and plan-sign-gate.py to
      plan-sign-gate.pre.sh and plan-sign-gate.pre.py INSIDE .claude/skills/harness/bin - not a
      temp directory, because the wrapper resolves its root from its own location and the
      python file imports its siblings - and change the single exec line of the .pre.sh to name
      plan-sign-gate.pre.py. Here "pre-change" means the tree as T-07 left it, so the copy must
      be taken AFTER T-07 lands and BEFORE this branch is written; a copy from before T-07 would
      redden T-07's own six cases too and prove nothing about this branch. Run the suite with
      PLAN_SIGN_GATE_BIN pointing at it, record that the new cases fail and every earlier case
      passes, then DELETE both copies.

      STEP TWO, THE BRANCH, in plan-sign-gate.py, inside the quarantines(line, agent, session,
      depth=0) function T-07 adds. Do not write a second function and do not define a second
      orphan predicate - T-02's orphan_write is the one predicate both routes read, which is
      D-14, and a second one is two answers to one question.

      Beside T-07's ADOPT_TOOL = "quarantine.py" add DISCARD_VERB = "discard" and keep adopt
      where it is. Then extend quarantines() by exactly these steps, leaving T-07's --file path
      byte-identical in behaviour:

        1. In the invocation scan of T-07's step 2, where _basename(toks[i]) at :224 equals
           ADOPT_TOOL, accept the next token - past a run of SEP, skipped exactly as denies()
           skips one at :291 - being DISCARD_VERB as well as adopt. The eval and bash -c
           recursion under MAX_DEPTH at :299 is unchanged and covers this verb for free.
        2. On a discard match, read the value of --dir and NOT --file, because
           quarantine.py discard takes --dir: the token following a literal --dir, or the tail
           of a --dir=VALUE token. An absent value returns None and falls OPEN.
        3. Normalise that value to a checkout-relative POSIX path by taking the tail from its
           LAST .harness/ segment. A value with no .harness/ segment returns None and falls
           OPEN - that is D-13's posture restated for --dir, and it is what keeps the shell
           variable and command substitution controls allowed. Fail-open here is a stated blind
           spot, not an oversight, and the comment must say so in one line.
        4. Match the result against ^\.harness/[^/]+/features/([^/]+)/quarantine/[^/]+/?$ -
           D-16 pins this regex - and take the feature from group 1. No match returns None. Note
           this is a DIRECTORY pattern, so it accepts an optional trailing slash and matches no
           file inside the directory; canonical_artifact is not consulted on this branch,
           because a quarantine directory is not a canonical artifact.
        5. Return None unless _reg.orphan_write(ROOT, agent, feature, session) is True. ROOT at
           :35 is the root the wrapper resolved through harness_boundary.resolve_root from this
           script's own directory, the same root check-domain.sh resolves at its _root() on
           :154. D-04's OMP carve-out holds identically here with no extra code, because
           orphan_write itself returns False when the only live claims for the feature carry
           runtime omp - do NOT add a second runtime test, and do NOT reach into the registry
           directly.
        6. Return (rel, feature, None), the same (rel, feature, quarantine_rel) tuple shape
           T-07's rule returns, with a None third element meaning there is no path to advise.
           The refusal text at the foot of the file branches on that None and says that
           discarding a quarantined result is the resumed parent's act and this caller is not
           it, naming the refused directory as rel. It never names a quarantine path to write
           instead, and it is never REASON.

      The import of inflight_registry stays where T-07 put it, inside quarantines() and only
      after an invocation has matched, in a try that on any exception writes one stderr line
      saying the quarantine boundary was not enforced and returns None. Do not hoist it: this
      hook runs ahead of EVERY Bash call in the session. Change nothing in the sign-approval
      rule, in denies() at :256, or in the two-rule decision at the foot that T-07 writes;
      quarantine.py list stays outside every match, and a non-harness agent_type is still not
      reached by the quarantine rule.

      STEP THREE, plan-sign-gate.sh, header comment only, no code. T-07 rewrites the header to
      say this is the PreToolUse Bash gate for plan-merge.py and quarantine.py carrying TWO
      rules. Extend the quarantine rule's sentence there to name quarantine.py adopt AND
      discard, and say in one clause that list is read-only and uncovered. Keep every other
      paragraph, including the stated blind spot, the stdin reasoning and the one-python3
      reasoning. The file is NOT renamed - a rename would require a .claude/settings.json edit
      and would strand the registration of test-plan-sign-gate.py, which is the cost D-12 chose
      this home to avoid.

      RECORDED BASELINE, observed from the main checkout at a7569463 with the four gate files
      byte-identical to ad93d43e - this task's verify block run VERBATIM exits 1 with no
      output, because the first grep fails; each of the three greps individually exits 1, and
      the literal discard occurs 0 times in both test-plan-sign-gate.py and plan-sign-gate.py.
      The tail conjunct alone, python3 .agents/skills/harness/bin/test-plan-sign-gate.py, exits
      0 today printing 45 ok lines and 0 FAIL lines. The three greps are therefore the whole
      discriminator and no earlier conjunct masks them.
