# Grilling — the orchestrator playbook cannot survive its own loop — 2026-08-23

## Destination
`.claude/skills/harness/SKILL.md`'s delegation loop is rewritten so an orchestrator NEVER waits.
Every dispatch ends its turn; the platform wakes it with the child's completion; on waking it
checks its own context against the configured threshold and either continues or hands off to a
fresh orchestrator. Done when a real feature runs to a phase boundary with no orchestrator killed
by the 600s watchdog and no invented holding activity in its transcript.

## Settled
- THE DEFECT IS THE PLAYBOOK, not the platform. The loop tells the orchestrator to "Receive the
  team digest" (step 4) and "Loop until DONE" (step 6), and within ONE phase it sequences several
  lead round-trips: the build team, then the qa segment, then simplify, then pm's goal-check, then
  the briefing. Each round-trip is a whole team. The orchestrator therefore has to occupy itself
  for far longer than 600s, and the no-progress watchdog kills it.
- Scope is the PLAYBOOK ONLY. Operator ruling. The three domain leads run the same
  wait-for-a-member pattern through `harness-team`, and that is deliberately NOT in this feature.
- #742 stays its own ticket and was returned to Backlog. It is a real defect about the claim
  registry and the inherited cwd; it is NOT what kills the orchestrator.
- OPERATOR REQUIREMENT added mid-grilling: stop-and-wake is not enough on its own. On waking, the
  orchestrator must weigh its own context against
  `harness.json` `budgets.orchestrator_context_warn_tokens` and decide whether to hand off to a
  fresh orchestrator rather than continue the loop.
- Execution mode is MAIN-SESSION-DIRECT. **STRUCK AND CORRECTED 2026-08-23: this entry first read
  "a SQUAD RUN" and cited DEC-174 am.4 as an exact enumeration. BOTH HALVES WERE FALSE.**
  `check-domain.sh --resolve .claude/skills/harness/SKILL.md` returns NOBODY, so no agent may write
  the playbook. And am.4's own heading is "the enumeration is a list of examples, not a boundary"
  and it rules "The category governs" (DECISIONS.md:4854, :4862) — it is not an exact list. The lane
  conclusion survives on `check-domain.sh` alone, which is independent of am.4.

## Not yet specified
- HOW an orchestrator learns its OWN agent id. `context-watch.py` keys every row on an agent id,
  and the id is handed to the SPAWNER at spawn time, not to the agent itself. Without its own id
  the orchestrator cannot measure its own context, so the operator requirement has no mechanism
  yet.
- WHERE a mid-phase handoff seam is. DEC-159 makes a PHASE boundary the sanctioned termination
  point and the successor reads a capped handoff note. A context-triggered handoff can fall
  anywhere, so either the seam set widens or the note has to carry more.
- What happens to branch `chore/744-never-wait-for-a-lead` -- absorbed, superseded, or merged
  first. **CORRECTED 2026-08-23: `git show --stat f5194d2` is 1 file changed, 5 insertions, in
  `SKILL.md` ALONE.** The "142 lines of unrelated deletions" was a two-dot-diff mis-attribution:
  `git diff main..<branch>` showed `569d417`'s own +142/-16 across three files (#750) as if they
  were the branch's. The branch is clean and carries only the rule.
- Whether the watchdog fires at all while an orchestrator has a live child. Not measured; the
  probes below never needed it, because a stopped parent is woken.

## Out of scope
- The three domain leads' identical wait pattern. Already ticketed: #610 and #552 (leads hold no
  `SendMessage`).
- #744's other death -- zero assistant events, 73KB input, dead at 643s. Two candidate causes,
  one data point each, explicitly filed as a different disease.
- #742's registry collapse and the `HARNESS-FEATURE` dispatch line.
- Agent teams. Ruled out on evidence: teammates cannot spawn teammates, so a 4-tier org does not
  map, and a subagent definition's `skills:` field is NOT applied to a teammate, which is how
  rules reach all 16 agents.

## Facts I verified (so pm does not re-derive them) — at 569d417
### Measured in this session, three probes, all with unguessable UUIDs written to disk
- TWO LAYERS: a parent subagent DID receive its child's returned value. Parent reported the exact
  UUID the child wrote; parent's tool calls were `Agent`, `ToolSearch`, `Monitor`, `TaskStop` --
  no Bash, so it could not have read the file.
- THREE LAYERS (the org's real depth): C wrote `00D92E65-...`; B wrote `B_GOT:00D92E65-...`; A
  reported `A_GOT:B_GOT:00D92E65-...`. A's tool calls were `Agent` and `ToolSearch` only, and A's
  transcript CONTAINS a real `task-notification` for B.
- STOP-AND-WAKE, the decisive one. A parent dispatched a 30s child and stopped immediately with
  ONE tool call and no stalling. Timeline from its transcript: `15:17:14` final message
  `DISPATCHED_AND_STOPPED`; `15:18:05` a completion notification arrives in its context;
  `15:18:09` it emits `RESUMED_WITH:28B04340-51EC-492A-933E-1AD5603FED69`, matching disk exactly.
  **A parent that has stopped IS woken by its child. The platform pumps the loop.**
- BOTH working parents INVENTED a stall to stay alive -- one a 45s `Monitor` sleep it then killed,
  the other a "waiting for its result" turn. That is the same behaviour as the 354 `echo hold`
  calls. The model stalls because the playbook tells it to stay.
- A FALSE RESULT WAS FABRICATED. Layer B reported it first received a completion for C carrying
  UUID `91C39D91-4A48-4A69-8AAA-8DD87B9BD9DD`, wrote a wrong verdict to disk, then corrected it
  when the real notification arrived. That UUID appears ONLY in B's own assistant messages,
  never in any incoming message. B invented it. This is DEC-199's false-reporting harm shape and
  it has NO ticket yet.

### Read from the repository
- `main`'s `harness/SKILL.md` does NOT contain "NEVER WAIT". The rule exists only on branch
  `chore/744-never-wait-for-a-lead`, one commit `f5194d2`, unmerged, whose diff also removes 142
  lines across `check-domain.sh`, `feature_schema.py` and `test-validate-feature-json.py`.
- The rule as written on that branch: "NEVER WAIT FOR A LEAD. RETURN. A dispatch tells you when
  it is done; you do not poll for it. With nothing to do until a lead returns, end your turn and
  say what is in flight." Measured note in it: 354 of 450 Bash calls on `echo hold` and `sleep`,
  killed at 600s, taking its lead and its member with it.
- `budgets.orchestrator_context_warn_tokens` is `200000` in `.harness/harness.json`. DEC-198:
  crossing it ADVISES, never refuses. Its rationale records that 28 of 76 orchestrator
  transcripts peaked above it, 10 above twice it, the largest at 750837.
- `context-watch.py` is a READ-ONLY OPERATOR view. Its own docstring: "nothing here decides, the
  orchestrator does." So the threshold has a meter and a config key but no rule in the playbook.
- The playbook has NO context-threshold handoff rule today. Its only context lines are warnings
  not to hold state in context (`SKILL.md:361`, `:408`).
- DEC-159: an orchestrator's mission is exactly one phase, ending there is normal termination,
  and the successor reads a capped handoff note.
- Docs (`code.claude.com/docs/en/sub-agents.md`) state that completion notifications do NOT reach
  a parent subagent. **Our three probes contradict that.** Treat the doc as stale here and the
  measurement as authority.
- `check-state.sh` reports ONE violation, unrelated to this feature:
  `FEAT-34-worktree-act3-enforced/BRIEF.md` is not approved.
