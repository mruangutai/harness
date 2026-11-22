# T-03 decision dispositions — FEAT-2274

DEC-205 forbids amendment sub-sections in `DECISIONS.md` ("a correction rewrites the entry it
corrects"), so each change below is a present-tense rewrite of the affected clause, and this note —
not the decision file — is the disposition record SC-08 asks for. Reviewers compare with
`git show <review_sha>:.harness/harness/docs/DECISIONS.md` against the pre-edit pin `1e0b0149`.

| Decision | Disposition | Clause rewritten | Why |
|---|---|---|---|
| DEC-100 | amended | §4, "Only `exit 2` blocks …" | Own failures are now a third outcome. The broad gates (check-domain, bash-write-guard, dispatch-guard, validate-digest) stay fail-open but visibly unavailable (D-01's stdout JSON, extension synthesis, passive notice per occurrence, deny precedence). The narrow command gates (gh-close, branch-create, plan-sign) fail closed after matching their command. The run-start claim backstop is kept and is no longer a reason to hide the failure. Not reversed: failing the broad gates closed stays refused. |
| DEC-118 | amended | "the `spawns:` list is enforced …" paragraph | Its claim that `dispatch-guard.py` reads `spawns:` became false at T-01. omp's native `assertDepthAndSpawnAllowed` is the sole allowlist on task, eval `agent()` and workpool; dispatch-guard keeps the `name:` refusal. The ruling (one squad per team) stands. |
| DEC-127 | amended | item 2, "fail OPEN, LOUDLY" | The guard now also prints the unavailable line, so the failure reaches the agent instead of only stderr. |
| DEC-204 | amended | "Main … remains outside persona policy" | Main stays outside persona policy but not target policy: `harness-*` targets spawn through `task` only, Main included (`before_subagent_spawn`). Lineage, liveness and ledger rules unchanged. |
| DEC-208 | amended | rule 1, "Presence, not truthiness" | The `last_assistant_message` absence pass was the retired text contract; the live `digest_object` contract (DEC-237) refuses absent, null or non-object data at exit 2. Own gaps (identity, schema, registry) are visibly unavailable. No absent-digest pass is restored. |
| DEC-234 | amended | the **Chose:** paragraph | The three narrow gates run a stdlib applicability check before the copied prologue; the prologue is unchanged and stays copied; merge-gate and run-unit-tests run it first, as before. |
| DEC-174 | retained | — | This feature was planned by the harness and executed main-session-direct, exactly as DEC-174 requires for changes to its own hooks, gates and their tests. |
| DEC-233 | retained | — | OMP remains the only host; nothing here reintroduces a Claude adapter. |
| DEC-237 | retained | — | The YieldTool object contract and hook-injected strict schemas are unchanged; DEC-208's rewrite now names DEC-237 as the current digest contract. |

DEC-118 was not in the plan's list; T-03's intent requires amending any other consulted decision
whose claim the implementation changed, rather than leaving it silently superseded.

## Builder-side prose corrections outside T-03's `files:`

T-01 made two skill sentences false; both now name omp as the authority that refuses a target
outside `spawns:`:

- `.claude/skills/harness-zero-micro-management/SKILL.md` — "`dispatch-guard` refuses anything
  outside it" → "omp refuses anything outside it".
- `.claude/skills/harness/SKILL.md` — "`dispatch-guard` refuses a target outside your `spawns:` …
  and any `name:` parameter" → omp refuses the target; dispatch-guard still refuses `name:`.

## SC-04 evidence pointers

- At `review_sha`: `git show <review_sha>:.claude/skills/harness/bin/dispatch-guard.py` (no
  allowlist block, no owner-root frontmatter lookup) and the three
  `git show <review_sha>:.omp/agents/harness-{product,eng,validator}-lead.md` "Outside your squad →
  escalate" paragraphs; their frontmatter matches `git show 1e0b0149:` byte for byte.
- External, owner-checkout evidence (not content at `review_sha`): the published omp 19.1.0
  `runStructuredSubagent` and `assertDepthAndSpawnAllowed` facts in
  `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-omp-native-enforcement-a-2026-11-21.md`,
  section "Facts I verified (so pm does not re-derive them)".
