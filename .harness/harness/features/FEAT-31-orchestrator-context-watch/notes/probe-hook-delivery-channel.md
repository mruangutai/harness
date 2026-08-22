# Finding — which hook event delivers text into a RUNNING agent's own context without refusing it

Measured 2026-08-21 in the FEAT-31 worktree at 6f651f1, by reading shipped production code in this
repository. No probe spawn, no settings.json change, no measurement of a hypothetical.

## Why this needed settling before the plan is signed

REQ-08 and SC-13 require that an orchestrator crossing the threshold "is told so in its own context,
while it is running". The operator has ruled that the warning **advises and does not refuse**, so
`PreToolUse` + exit 2 is excluded by the ruling: in PRE, exit 2 is the refusal. That left the delivery
channel unnamed, and the BRIEF's prerequisite probe settled *identity* (`session_id` + `agent_id`), not
*delivery*. A plan resting on an unnamed channel is a plan whose central mechanism is unverified.

## The answer, and it is already in production here

`PostToolUse` + exit 2. The tool has already run, so nothing is blocked, and the hook's stderr reaches
the agent. `check-domain.sh` states both halves in its own comments and has shipped on that basis:

- `check-domain.sh:571-573` — the mode table: PostToolUse on Write, Edit and Bash reads what landed on
  disk and exits 2, "whose stderr reaches the agent. Detection, not prevention".
- `check-domain.sh:648-653` — a review finding recorded in place: "In POST it already LANDED — exit 2
  there only carries stderr back to the agent". The consequence drawn there is that the message must
  not say BLOCKED, because the write did happen; `VERB` is set to
  `OVER BUDGET (already written)` in post mode for exactly that reason.

`settings.json` already registers `check-domain.sh --post` on `PostToolUse` for `Write|Edit|Bash`, so
this is an in-service path in this repository, not an inference from documentation.

## What follows for the plan

- SC-13's hook registers on **`PostToolUse`**, not `PreToolUse`, and warns by exiting 2 with the text on
  stderr. That satisfies "in its own context" and "advises, does not refuse" simultaneously, with no
  new mechanism.
- The registration in `.claude/settings.json` is still `main-session-direct` — that path resolves to
  NOBODY under `check-domain.sh --resolve`, and DEC-174 puts the cutover in the operator's hands
  regardless.
- The warning's wording carries the same obligation `VERB` records: it must not claim anything was
  stopped. It states the current size, the threshold and the nearest seam, and the orchestrator decides.
- `PostToolUse` fires on `Write|Edit|Bash` in the current registration. Which matcher the context
  warning needs is a plan decision, not settled here. An orchestrator's most frequent tool is not
  necessarily one of those three, and a matcher that never fires for an orchestrator is the
  green-and-incapable-of-red shape in hook form. **This is the one thing the plan must still check
  rather than assume.**

## Not verified here

That the stderr text is visible to the model as *context* rather than only as a tool-result error
string. The two comments above assert it reaches the agent and the shipped code depends on it, which is
strong evidence; it is not a direct observation of a subagent transcript. Marked so nobody promotes it
to a measurement it is not.

# Finding 2 — which source names the FEATURE an orchestrator is on

Measured 2026-08-21 across every orchestrator sidecar and transcript on this machine. SC-10 fails if
the operator cannot answer "which feature each is on", and that source was never named.

| source | reliability, measured | verdict |
|---|---|---|
| first FEAT-NN in the agent transcript's first four entries | 89 of 89 | USE THIS |
| sidecar description | 66 of 94 | 70 percent, not a contract |
| sidecar worktreePath | absent on the FEAT-31 orchestrator's own sidecar | unavailable |
| transcript entry cwd | present on every entry, but it is the SPAWN cwd | wrong value |
| transcript entry gitBranch | present on every entry | ACTIVELY LIES, see below |

**gitBranch is a trap, demonstrated on this run.** The FEAT-31 planning orchestrator's own transcript
first entry reads cwd /Users/molchairuangutai/GitHub/harness and gitBranch
feat/FEAT-30-worktree-per-feature. Both name the checkout it was SPAWNED from, not the worktree it was
dispatched to work in. An instrument deriving the feature from gitBranch would today report the FEAT-31
orchestrator as working on FEAT-30 — a number that exists, looks plausible and is wrong, which is the
exact failure class this feature exists to end.

**REQ-07's unmeasured case occurs naturally.** 94 orchestrator sidecars, 89 with a matching .jsonl: five
have no transcript. The unmeasured branch is exercised by real data, not only by the SC-11 fixture.

Method: the sidecars were enumerated by agentType, and each transcript's first four entries were
searched for a FEAT-NN with a regex. Counts are from that run and grow with every spawn.

# Finding 3 — the corrected method runs against a LIVE orchestrator, and the field path is fixed

Measured 2026-08-21 by the FEAT-31 planning orchestrator against its OWN transcript while running.

    entries=110  requests carrying iterations=31
    naive peak     = 113,845
    corrected peak = 113,845
    current        = 113,845

**The field path, which the plan needs as a literal.** Per entry, the usage mapping is at
message.usage. Size is input_tokens plus cache_read_input_tokens plus cache_creation_input_tokens.
Where message.usage.iterations is a non-empty list, the corrected size is the MAX of that same sum
computed per iteration; where it is absent, the top-level sum is already the size. Peak is the max over
entries; current is the last entry's value.

**SC-01's live half is demonstrable and was demonstrated here** — a running orchestrator's own peak and
current were both read from disk while it ran, so nothing about the mechanism needs a finished run.

**A caution the plan must carry into its fixtures.** On this transcript naive equals corrected exactly,
across all 31 requests that carry iterations: none of them had a sub-call larger than the top-level sum.
So a test whose only input is a transcript like this one CANNOT distinguish the corrected method from
the naive one, and would pass either way. That is precisely why SC-02 mandates a fixture keeping the two
values distinct, and it is not a formality — a fixture drawn from an ordinary transcript reproduces this
coincidence and the test goes green against the defect it exists to catch.

# Finding 4 — the BRIEF names three enforcement surfaces; there are at least four

Resolved 2026-08-21 with check-domain.sh --resolve from the FEAT-31 worktree root.

| surface | resolves to | lane | named in BRIEF |
|---|---|---|---|
| .claude/skills/harness/bin/check-domain.sh | backend-dev, dev-ops | main-session-direct, DEC-174 | yes |
| .claude/settings.json | NOBODY | main-session-direct, forced | yes |
| .claude/skills/harness/bin/check-state.sh | backend-dev, dev-ops | main-session-direct, DEC-174 | yes |
| .claude/skills/harness/bin/test-check-state.py | backend-dev, dev-ops | main-session-direct, DEC-174 am.4 | no |
| .claude/skills/harness/templates/harness.json | NOBODY | main-session-direct, forced | NO |
| .claude/skills/harness/bin/run-unit-tests.sh | backend-dev, dev-ops | judgement call | no |

**The template is the one that was missed.** REQ-03 puts the threshold in .harness/harness.json, which
resolves to harness-dev-ops and is team-writable. Its TEMPLATE resolves to NOBODY, and under DEC-160 the
general path for a config-schema addition is /harness-init --upgrade with the template as its source. So
a squad can add the key to this project and cannot add it to the template, and a project initialised
tomorrow would never receive it.

**A second DEC-160 obligation nothing covers.** DEC-160 states that a decision adding a harness.json key
must say so. SC-09 only corrects DEC-159's watchdog clause. No criterion requires the new budgets key to
be declared in a decision, so the plan must carry that as a task and say which decision entry does it,
or the feature ships a config key no decision declares.

**upgrade-config.py enumerates no budget keys** — grepped for budgets and max_total_cycles, zero hits —
so whether a new key propagates through it at all is unestablished and the plan must check rather than
assume.

# Finding 5 — the BRIEF's Verification gaps paragraph is wrong, and it does not bite here

Raised by harness-product-lead in its send-back criteria, verified independently 2026-08-21 against
.harness/harness.json in this worktree.

The BRIEF says five null-cmd kinds are a DEC-163 soft skip. **DEC-187 supersedes that half.** A soft skip
requires status `excluded` AND a signed decision id. Measured statuses: `unit` and `integration` are
active; `functional` is excluded with `signed: DEC-187` and is the ONLY soft skip; `component`, `ui`,
`eval` and `typecheck` are `unresolved`, which the qa gate treats as BLOCKED, never as a skip.

**Where it would bite, read from test_matrix:**

| change_type | always | verdict |
|---|---|---|
| frontend | unit, component | component is unresolved, so it BLOCKS |
| ai_behavior | eval | eval is unresolved, so it BLOCKS |
| feature | unit, integration | safe here; the ui row is conditional on has_interaction_flow |
| logic, api, cross_module, bugfix, config, scaffolding, docs | active kinds or none | safe |

**It does not bite this feature.** Nothing in FEAT-31 is frontend or ai_behavior: the work is a Python
CLI, a hook module, a schema module, a config key, a gate table and a decision entry. Every change_type
those need is in the safe set, and the feature has no interaction flow so the conditional ui row never
fires. So the BRIEF's conclusion — that no criterion rests on a null kind — is CORRECT, and only its
stated reason is wrong.

**What the operator should know:** the BRIEF is approved and one paragraph in it is false. It is a
reasoning error with no consequence for this feature, so the recommendation is to leave the approved
artifact alone and let this note carry the correction, rather than reopening an approved BRIEF for a
statement that changes no task. Recorded rather than silently absorbed, per PRINCIPLES rule 15.
