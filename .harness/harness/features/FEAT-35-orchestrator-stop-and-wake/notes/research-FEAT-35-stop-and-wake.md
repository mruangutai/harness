# Research — FEAT-35 stop-and-wake — harness-pm — 2026-08-23

**BLUF.** The operator requirement has a mechanism, measured working today with no new code, and
two facts in the grilling note are wrong. Nothing in this feature is blocked on an unknown.

## 1. An orchestrator CAN learn its own agent id (the "no mechanism" gap closes)

Measured from inside a running subagent turn at `569d417`:

- Sidecar layout is `~/.claude/projects/<project-slug>/<session-id>/subagents/agent-<id>.jsonl`
  with a sibling `agent-<id>` metadata file carrying `agentType`, `description`, `parentAgentId`
  and `spawnDepth`. `context-watch.py:discover_orchestrator_rows` walks exactly that shape.
- **Nonce grep identifies self.** Emit a fixed literal nonce in a Bash command, then in a LATER
  Bash call grep the orchestrator-typed sidecars for it. Exactly one file matched — my own —
  in **1.14s** over 114 orchestrator sidecars (993M of sidecar data; an unfiltered root-wide grep
  over 1.2G took 8.05s, so filtering by `agentType` first is worth keeping).
- **TWO CALLS ARE REQUIRED, and the nonce must be a literal.** A single call that generated a
  nonce and grepped for it within the same command found NOTHING (rc=1): the assistant message
  carrying the command is not yet in the sidecar when that command runs. A generated nonce also
  cannot be re-grepped in a later call. This is the one detail that separates a working
  instruction from one that silently reports "no row".
- **End-to-end proof.** This feature's live orchestrator resolved to `af05a0d5a321741b6`
  (`agentType: harness-orchestrator`, `spawnDepth: 1`), and
  `context-watch.py af05a0d5a321741b6` printed
  `current=75,467 peak=75,467 entries=56 headroom=124,533` against the configured 200000.

**Do not narrow the grep by cwd slug.** `context-watch.py --resolve-dir "$PWD"` in this worktree
returns `-Users-...-harness--claude-worktrees-harness-FEAT-35-orchestrator-stop-and-wake`, but the
live transcripts sit under `-Users-molchairuangutai-GitHub-harness` — the slug follows the SESSION's
cwd, not the agent's. Slug narrowing finds nothing and reads as "no row".

## 2. CORRECTION — branch `chore/744-never-wait-for-a-lead` removes NOTHING

The grilling note records "142 lines removed across `check-domain.sh`, `feature_schema.py` and
`test-validate-feature-json.py`". Measured: `git show --stat f5194d2` is
**`1 file changed, 5 insertions(+)`**, SKILL.md only. Its merge-base with `main` is `3df18d3`;
`main` is now `569d417` (PR #750, the feature-schema fix). A two-dot `git diff main..branch`
attributes main's own newer commit to the branch as deletions. `git diff main...branch` is 5
insertions. **The branch is clean;** the ruling turns on other grounds (plan D-03).

## 3. CORRECTION — execution mode is main-session-direct, not a squad run

`check-domain.sh --resolve .claude/skills/harness/SKILL.md` -> `NOBODY` at `569d417`.
`check-plan-routes.py:363` makes every task touching it a VIOLATION unless it declares
`main-session-direct`. DEC-174 am.4 permits the WORK (the playbook is not on the enumerated
enforcement layer); the domain grant decides the LANE, and they are independent questions.

## 4. The `phase:` finding is a DEC-192 leftover, not a schema bug

`SKILL.md:343-344` says "Record your phase in `feature.json` `phase:`". DEC-192 **deleted** the
`phase` field: one `status` field, six board-column values. The feature schema's properties are
`feature_id, branch, pr, status, review_sha, cycles_used, max_total_cycles, runs, max_total_runs,
github, factory` with `additionalProperties: false`. So the playbook instructs a write the tree
refuses, in the exact file this feature scopes. Ruled INTO the plan (T-03) — no user call needed,
because DEC-192 already decided the content.

## 5. The 600s-with-a-live-child question — why no synthetic probe

I could not run it: my own sidecar metadata reads `spawnDepth: 3`, the cap (DEC-120), so the
platform withholds the spawn tool and I cannot create a parent/child pair. A synthetic >600s child
is also confounded — the child's own no-progress exposure is indistinguishable from the parent's. A
real lead round-trip routinely exceeds 600s (a whole team, DEC-118), so the honest measurement is a
real run: SC-05, `verify: uat`. **This is the feature's load-bearing unknown.** If a stopped parent
is killed at ~600s, stop-and-wake does not fix the death — it only removes the invented stalling.

## 6. Verification reality

`test_kinds.eval` has `cmd: null`, and the three playbook tasks are `change_type: ai_behavior`
(the matrix requires `eval`), so that requirement soft-skips. Nothing can execute a markdown
playbook, so the text assertions in T-05 plus SC-05's real run are what actually carry conformance.
A new `bin/test-*.py` must be registered in `run-unit-tests.sh`'s explicit script list or its drift
detector exits 2 for the whole suite — which is why T-05 is one task over two files.
