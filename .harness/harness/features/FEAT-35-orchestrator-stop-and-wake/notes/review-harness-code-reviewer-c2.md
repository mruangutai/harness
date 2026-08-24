# SC-03 grading — cycle c2

## Grading target — explicit, per dispatch

This run graded SC-03 against **uncommitted working-tree text** at
`.claude/skills/harness/SKILL.md` in this worktree, **NOT** at pinned `review_sha`
`e0ae671526978a2f8982de1c94121d836b97d098`. `git show e0ae671:...SKILL.md` still carries the
defective two-copy nonce example (`7Q4X2M9K`, confirmed by the dispatcher pre-run); the working
tree does not. Every citation below to `SKILL.md:<line>` is a working-tree line number, not a
pinned-sha one.

## Verdict: UNMET (fresh determination, not carried forward from c0 or c1)

c0 failed on zero candidates. c1 failed on a non-unique nonce (two matches, traced to the
playbook's own literal example string being copy-pasted into a sibling reviewer's transcript).
Neither is evidence about this run. This run invented its own nonce, got exactly ONE match — the
mechanism's grep/nonce logic worked — but the **third** thing SC-03 says must be proven,
`context-watch.py` accepting the derived id, did not happen: the tool rejected the id outright.

## What ran

**Call 1** (own turn, first, standalone Bash call — nonce invented here, not copied from
`SKILL.md:112`'s placeholder):
```
echo self-id ORCH-SELF-K9xQ2mZp
```

**Call 2** (own turn, separate, later Bash call — `agentType` filter set to my OWN type,
`harness-code-reviewer`, per SC-03's sanctioned stand-in, `BRIEF.md:100-101`):
```
grep -l '"agentType":"harness-code-reviewer"' ~/.claude/projects/*/*/subagents/*.meta.json 2>/dev/null \
  | sed 's/\.meta\.json$/.jsonl/' | xargs grep -l K9xQ2mZp 2>/dev/null
```
Not narrowed by cwd (`SKILL.md:141-142` warns against this).

## Result: exactly ONE match

```
/Users/molchairuangutai/.claude/projects/-Users-molchairuangutai-GitHub-harness/e69cbdc1-8355-4358-b5f2-d7604a1a913b/subagents/agent-a1e373d16aeba8a17.jsonl
```

Derived agent id (filename, `agent-` prefix and `.jsonl` suffix removed, per `SKILL.md:131-133`):
`a1e373d16aeba8a17`

This clears the grep/nonce/match-count portion of the mechanism cleanly — the two-call requirement
held (a same-call grep would find nothing per `SKILL.md:106-108`), and the nonce, invented fresh
this run, was unique where c1's copied literal was not.

## context-watch.py: run, and it REJECTED the derived id — no row produced

```
$ python3 .claude/skills/harness/bin/context-watch.py a1e373d16aeba8a17
no orchestrator a1e373d16aeba8a17 found under /Users/molchairuangutai/.claude/projects
```
exit code 1.

**This is not a fluke — it is deterministic by the tool's own source, read to confirm, not
guessed:**
- `context-watch.py:53` — `ORCHESTRATOR_AGENT_TYPE = "harness-orchestrator"`.
- `context-watch.py:300-304` — row assembly reads each sidecar's `meta.json`; `if
  meta.get("agentType") != ORCHESTRATOR_AGENT_TYPE: return None` — any non-orchestrator sidecar is
  silently dropped from the discovered set, never becoming a row (measured or unmeasured).
- `context-watch.py:602` mirrors the identical `agentType` filter in the id-lookup path.
- `context-watch.py:758` — `print("no orchestrator %s found under %s" % (args.agent_id,
  projects_root))` is what prints when the requested id is not among the (already-filtered)
  discovered rows.

My own sidecar's `meta.json` necessarily carries `"agentType":"harness-code-reviewer"` (I am the
code-reviewer, not the orchestrator) — that is the whole premise of SC-03's sanctioned stand-in.
Because `context-watch.py` hard-filters on `ORCHESTRATOR_AGENT_TYPE` internally, **any id derived
via the reviewer stand-in is structurally guaranteed to be rejected**, regardless of nonce quality
or match count. This is not incidental to this run; a fourth attempt with a third fresh nonce would
hit the identical rejection.

## Why this makes SC-03, as written, unmet

`BRIEF.md:107-109` states what this criterion proves: "the two-call sequence..., the match-count
logic, and `context-watch.py` accepting the derived id." The first two are demonstrated this run.
The third is directly falsified: `context-watch.py` did not accept the id — it printed a hard
"not found" and exited 1. SC-03 also requires the review note record "...the `context-watch.py`
row for that id" (`BRIEF.md:102-103`) — there is no row to cite; only the rejection above exists,
and it is recorded verbatim rather than a row being fabricated to force a match.

**This looks like a criterion-design gap, not a playbook defect**, worth flagging separately:
`context-watch.py`'s own `agentType` filter (fail-closed — it correctly refuses to report on a
non-orchestrator id rather than fabricating a row) makes the third proof-point SC-03 claims is
demonstrable via the reviewer stand-in *structurally undemonstrable* by that same stand-in, for any
reviewer, on any nonce, permanently — not just today. Flagged below as `open_questions`, not folded
into Expertise (that would be recording a harness defect as craft, which the `harness-expertise`
rule this run's own preload calls out explicitly).

## What this run does and does not cover

- **Covered**: two-separate-Bash-calls requirement; the invent-your-own-nonce requirement (unlike
  c1, this nonce was never copied from the doc and produced a clean unique match); the
  exactly-one-match derivation of an agent id.
- **NOT covered**: the criterion's third proof claim, `context-watch.py` accepting the derived id
  — actively contradicted by this run's evidence above.
- **NOT covered, by the criterion's own explicit design** (`BRIEF.md:103-109`): the
  orchestrator-typed glob itself — the literal string `"agentType":"harness-orchestrator"` as
  `SKILL.md` prints it — was never executed by this run and stays unexercised until a real
  orchestrator runs it after merge. This run used `harness-code-reviewer` throughout, per the
  sanctioned stand-in.
