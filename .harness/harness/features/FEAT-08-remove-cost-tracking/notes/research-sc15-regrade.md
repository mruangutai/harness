# SC-15 re-grade — FEAT-08

**SC-15 is `met`.** Swept at working-tree state, over every rule surface a dispatched agent receives
at spawn — not only the five files SC-15 enumerates. Nothing on that surface instructs an agent to
emit a cost figure.

## Standard applied — unchanged

`BRIEF.md:155-162`. The leading claim ("a dispatched agent reading only its rules finds nothing that
would make it emit a cost figure") binds beyond the "Specifically," list of five, exactly as ruled in
the first grade. Not relaxed, not hardened. "Cost figure" means **money**; metaphorical cost (spawns,
cycles, context, wall-clock) is a deliberate survivor and is not graded.

## Surfaces swept

1. **All 12 files under `.harness/expertise/`** — the set injected per-owner by the `SubagentStart`
   hook (`.claude/skills/harness/bin/inject-expertise.sh:49-51`).
2. `.claude/agents/` (all agent definitions)
3. `.claude/skills/` — repo copy only, `.claude/worktrees/` excluded (FEAT-09, concurrent)
4. `.harness/team-config.yaml` — **zero hits on any token**
5. `CLAUDE.md` (71 lines, repo root) — **zero hits**. Added beyond the dispatch's set: it is injected
   into every dispatched context, so the leading claim cannot be asserted without it.

Tokens, run **uniformly across all five surfaces in one pass** over `*.md`/`*.yaml`/`*.json`:
`cost`, `usd`, `spend`, `meter`, `dollar`, `price`, `budget`, `$<digit>`, `by_agent`,
`pending_orchestrator`. Concept-level, not compound-spelling only. **57 hits total; zero are money.**
The only money-shaped hit is `.claude/skills/harness/SKILL.md:241` "the note **prices** trust" —
metaphor. CLAUDE.md's two hits are `:23` "Context budget" and `:47` "budgets" in the `harness.json`
column — both non-money and both deliberate.

## The prior blocker, verified at source

`.harness/expertise/harness-orchestrator.md` is clean. The former money operating procedure at
`:5-7`, `:10`, `:62` is gone; the surviving hits at `:12`, `:17`, `:57`, `:100` are spawn/cycle cost
and `:77`, `:93` are artifact/context budgets. Read directly, not taken on report.

**Correction to the dispatch:** ten of twelve expertise files changed in the distillation round
(9 modified + `harness-ui-reviewer.md` untracked, per `git status`), not twelve.
`harness-backend-dev.md` and `harness-product-lead.md` are unmodified. All twelve were swept anyway,
so the grade is unaffected.

## The five enumerated files — re-confirmed clean

`.claude/agents/harness-orchestrator.md` (`:3`, `:44`, `:48` — cycle budget only),
`.claude/skills/harness/SKILL.md` (`:21`, `:24`, `:95-107`, `:224` — token/context and cycle budget),
`.claude/skills/harness-team/SKILL.md` (`:20`, `:108`, `:154`, `:160`, `:194`, `:254` — same class),
`teams/build.yaml` and `teams/review.yaml` — **zero hits**.

Affirmative on the named clauses: **no return template in any `.claude/skills/**/*.md` carries a
`cost:` or `cost_usd:` field**, no `max_cost_usd` key exists on the swept surface, no
actual-vs-budget reporting requirement survives.

The ship-review briefing's step-2 list is at `.claude/skills/harness/SKILL.md`, section
"## The CEO briefing (three triggers, not every completion)", step 2 "Assemble one document"
(`:258-264` at this state; anchored on the content string per P-10). Its enumeration is: each lead's
summary, open questions, resolved escalations, the goal-check result, the UAT if required, and the
proposed backlog table. **No cost line.** Read directly, not inferred from token absence.

## Every hit accounted for, by class

| Class | Ruling |
|---|---|
| Metaphorical cost/spend/budget prose (spawn, cycle, context, wall-clock) across expertise, agents, skills | Deliberate survivors. Over-removal is this feature's named dominant failure mode |
| `$1`/`$2` in `bin/*.sh` (`deploy.sh:27-31`, `check-domain.sh:61`, `branch-create-gate.sh:55`) | Shell positionals — artifact of the `\$[0-9]` pattern in the wider first pass; absent from the uniform `.md`/`.yaml`/`.json` pass |
| `cost:` duplicate-key YAML fixtures — `test-harness-yaml.py:383,418-419`, `test-harness-yaml-corpus.py:214-218`, `test-check-domain.py:203-212` | Preserved by SC-12 (`BRIEF.md:139-142`) |
| `cost` as a *tolerated* key — `check-state.sh:335`, `check-domain.sh:308`, `gen-decisions-index.py:40`, `test-check-state.py:325-363` (asserts a `cost:` block is clean) | Hook/validator internals, not rule text an agent reads. Tolerating a key is not an instruction to emit one |
| `$49` in `test-render-brief.py:47,71-72` | Markdown-renderer fixture; content arbitrary. Not a rule surface |
| `validate-digest.py:178` comment "the harness no longer meters money" | Removal marker |

## `.claude/commands/harness.md` — out of scope, on different grounds than the host's

**My ruling differs from the host's.** The host reasoned history-vs-instruction on `:49`. I do not
reach that question: the file is outside SC-15's leading claim **entirely**, so `:49` is moot rather
than answered.

SC-15 is scoped to "a **dispatched** agent reading only its rules." The main session is layer 0 and is
not dispatched (DEC-120, `docs/harness/DECISIONS-INDEX.md:140`). `grep -rn 'commands/'` across
`.claude/agents/`, `.claude/skills/` and `.harness/team-config.yaml` returns **zero** — no dispatched
agent's rule set reaches this file. It is therefore not gradable under SC-15 either way.

`:18` (a cost-vs-budget column) and `:83` (logging a cost field per return) are live money
instructions and a real defect, but an already-known one routing to the user. Recorded here as an
observation, **not** as a new SC-15 finding, to avoid double-reporting.

## Deployment gap — noted, not graded

My preloaded skill text still carries `cost: pending_orchestrator` and INV-11. The repo files contain
**zero** `pending_orchestrator` or `by_agent` hits. That is the stale global deployment at
`~/.claude/skills/` (ruled stale at panel Q2, mf2-product Q6), not an SC-15 violation. Raised as Q23.

## Open questions

- **Q23** (non-blocking): the stale `~/.claude/skills/` deployment still instructs agents to write
  `cost: pending_orchestrator`. Repo is clean; a deploy is needed before agents stop being told to
  emit the removed field.
- **Q24** (non-blocking): `.claude/commands/harness.md:18` and `:83` remain live money instructions
  in a file no agent domain covers.
